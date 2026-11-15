"""Bước 2: tìm TẤT CẢ hành tinh có transit, tính thông số + thành phần từng hành tinh, so với NASA.

Quy trình:
    1. BLS lặp: tìm tín hiệu mạnh nhất → che transit của nó → tìm tiếp, tới khi chỉ còn nhiễu
    2. Mỗi hành tinh: gấp pha → khớp hình thang (giá trị khởi đầu) → khớp mô hình batman
       (có tối rìa + nhòe phơi sáng) → hình học quỹ đạo
    3. Kết hợp thông tin sao (header KIC, Gaia) → thông số vật lý, khoảng cách
    4. Khối lượng (RV đã công bố / ước tính) → mật độ → thành phần
    5. Bổ sung hành tinh không có transit (chỉ phát hiện bằng RV) từ NASA Exoplanet Archive

Cần chạy 01_download.py trước. Cách chạy:
    .venv/Scripts/python scripts/02_analyze.py "Kepler-10"

Kết quả:
    data/csv/<sao>_<hành tinh>_folded.csv   transit gấp pha của từng hành tinh, cho Google Sheets
    outputs/<sao>_*.png                      light curve, periodogram, transit gấp pha
    outputs/<sao>_report.md                  báo cáo đầy đủ
    outputs/<sao>_system.json                số liệu cả hệ, dùng cho 03_diagram.py

Công thức xem docs/kien-thuc-exoplanet.md, mục 7.
"""

import argparse
import json
import math
import sys
import time
import warnings
from pathlib import Path

import batman
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import requests
from astropy.timeseries import BoxLeastSquares
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "data" / "csv"
OUT_DIR = ROOT / "outputs"

# Hằng số vật lý (SI)
G = 6.674e-11
R_SUN = 6.957e8
M_SUN = 1.989e30
T_SUN = 5772.0
R_EARTH = 6.371e6
M_EARTH = 5.972e24
R_JUP = 7.1492e7
M_JUP = 1.898e27
AU = 1.496e11
DAY = 86400.0
PC_TO_LY = 3.2616  # 1 parsec = 3.26 năm ánh sáng
BKJD_OFFSET = 2454833.0  # BKJD = BJD − 2454833

ARCHIVE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
GAIA_URL = "https://gea.esac.esa.int/tap-server/tap/sync"
ARCHIVE_COLS = (
    "pl_name,discoverymethod,tran_flag,pl_orbper,pl_tranmid,pl_trandur,pl_trandep,pl_ratror,pl_rade,pl_radj,"
    "pl_bmasse,pl_bmassj,pl_bmassprov,pl_dens,pl_orbsmax,pl_orbeccen,pl_orbincl,pl_imppar,pl_ratdor,pl_eqt,"
    "pl_insol,pl_rvamp,st_teff,st_rad,st_mass,st_met,st_logg,st_dens,st_age,sy_dist,sy_plx"
)

EXPOSURE = 29.4 / 1440  # mỗi điểm long cadence là ánh sáng cộng dồn trong 29.4 phút (ngày)
# Hệ số tối rìa bậc hai (u1, u2) cho sao loại G trong bộ lọc Kepler, giá trị gần đúng
LIMB_DARKENING = [0.40, 0.26]

# Ngưỡng chấp nhận một tín hiệu BLS là transit thật (xem mục 7.6 trong sổ tay)
MIN_SDE = 9.0  # đỉnh periodogram phải nổi bật hơn hẳn phần còn lại
MIN_SNR = 10.0  # độ sâu / sai số độ sâu
MIN_TRANSITS = 3  # phải thấy lặp lại ít nhất 3 lần
MAX_PLANETS = 8
# Hành tinh chu kỳ dài có transit dài (Kepler-452b ~10.6 giờ = 0.44 ngày) nên cần cả 0.5, 0.6.
# BLS chỉ nhận thời lượng < chu kỳ nhỏ nhất, nên các giá trị quá dài sẽ bị lọc theo --min-period.
BLS_DURATIONS = [0.03, 0.05, 0.07, 0.1, 0.14, 0.2, 0.28, 0.4, 0.5, 0.6]


# ---------------------------------------------------------------- mô hình transit

def trapezoid(t, depth, t14, t12, t0):
    """Mô hình transit đơn giản hình thang: t14 = tổng thời gian, t12 = thời gian ingress (đi vào)."""
    t12 = np.clip(t12, 1e-4, t14 / 2)
    x = np.abs(t - t0)
    flux = np.ones_like(t)
    bottom = x <= t14 / 2 - t12
    slope = (x > t14 / 2 - t12) & (x < t14 / 2)
    flux[bottom] = 1 - depth
    flux[slope] = 1 - depth * (t14 / 2 - x[slope]) / t12
    return flux


def observed_trapezoid(t, depth, t14, t12, t0):
    """Hình thang sau khi bị "nhòe" do phơi sáng 29.4 phút: lấy trung bình mô hình trong khoảng phơi sáng.
    Bỏ qua bước này thì ingress trông dài hơn thật, làm sai b và a/Rs."""
    offsets = np.linspace(-EXPOSURE / 2, EXPOSURE / 2, 15)
    return np.mean([trapezoid(t + o, depth, t14, t12, t0) for o in offsets], axis=0)


def batman_model(t, period, dt0, k, a_rs, b):
    params = batman.TransitParams()
    params.t0, params.per, params.rp, params.a = dt0, period, k, a_rs
    params.inc = math.degrees(math.acos(min(b / a_rs, 1)))
    params.ecc, params.w = 0.0, 90.0
    params.limb_dark, params.u = "quadratic", LIMB_DARKENING
    return batman.TransitModel(params, t, supersample_factor=7, exp_time=EXPOSURE).light_curve(params)


def phase_fold(t, period, t0):
    """Thời gian tính từ tâm transit gần nhất (ngày), trong khoảng [-P/2, P/2)."""
    return (t - t0 + period / 2) % period - period / 2


# ---------------------------------------------------------------- tìm hành tinh

def period_grid(pmin: float, pmax: float, baseline: float) -> np.ndarray:
    """Lưới chu kỳ cho BLS. Bước nhảy tỉ lệ với thời lượng transit dự kiến (dài dần theo P^(1/3))
    chia cho độ dài dữ liệu: đủ mịn để không bỏ sót, không thừa để chạy nhanh."""
    periods = [pmin]
    while periods[-1] < pmax:
        p = periods[-1]
        expected_duration = 0.05 * (p / 0.5) ** (1 / 3)
        periods.append(p * (1 + 0.5 * expected_duration / baseline))
    return np.array(periods)


def search_planets(t, flux, err, pmin, pmax):
    """BLS lặp: mỗi vòng lấy tín hiệu mạnh nhất, nếu đạt ngưỡng thì che transit của nó rồi tìm tiếp."""
    baseline = t.max() - t.min()
    periods = period_grid(pmin, min(pmax, baseline / MIN_TRANSITS), baseline)
    durations = [d for d in BLS_DURATIONS if d < pmin]
    print(f"BLS: thử {len(periods)} chu kỳ từ {periods[0]:.2f} đến {periods[-1]:.1f} ngày (mỗi vòng ~1 phút)")
    keep = np.ones_like(t, dtype=bool)
    found, periodograms = [], []
    for round_no in range(1, MAX_PLANETS + 2):
        started = time.time()
        bls = BoxLeastSquares(t[keep], flux[keep], err[keep])
        result = bls.power(periods, durations, objective="snr")
        best = int(np.argmax(result.power))
        sde = (result.power[best] - np.mean(result.power)) / np.std(result.power)
        period = result.period[best]
        t0 = result.transit_time[best]
        duration = result.duration[best]
        stats = bls.compute_stats(period, duration, t0)
        n_transits = int(np.sum(stats["per_transit_count"] > 0))
        snr = result.depth_snr[best]
        ok = sde >= MIN_SDE and snr >= MIN_SNR and n_transits >= MIN_TRANSITS
        print(
            f"  Vòng {round_no}: P = {period:.5f} ngày, độ sâu = {result.depth[best] * 1e6:.0f} ppm, "
            f"SNR = {snr:.0f}, SDE = {sde:.1f}, {n_transits} transit → {'HÀNH TINH' if ok else 'nhiễu, dừng'} "
            f"({time.time() - started:.0f}s)"
        )
        periodograms.append((result.period, result.power, ok))
        if not ok:
            break
        # Tinh chỉnh chu kỳ bằng lưới rất mịn quanh đỉnh: sai 0.00004 ngày sau ~450 vòng đã lệch ~26 phút,
        # đủ làm nhòe transit gấp pha và sai a/Rs
        fine = bls.power(np.linspace(period * 0.9995, period * 1.0005, 3000), durations, objective="snr")
        best = int(np.argmax(fine.power))
        period, t0, duration = fine.period[best], fine.transit_time[best], fine.duration[best]
        found.append({"period": period, "t0": t0, "duration": duration, "snr": snr, "sde": sde, "n_transits": n_transits})
        keep &= ~bls.transit_mask(t, period, duration * 1.5, t0)
        if len(found) >= MAX_PLANETS:
            break
    return found, periodograms


def check_ephemeris(t, flux, err, period, t0, duration, trials=3000, seed=1):
    """Chế độ kiểm chứng: dùng P, T0 đã công bố thay vì tự tìm (cho tín hiệu quá yếu, BLS mù không thấy).

    Kèm phép thử báo động giả: chọn ngẫu nhiên P (±30%) và T0, đếm bao nhiêu % trường hợp cho SNR
    cao bằng tín hiệu thật. Tỉ lệ này càng nhỏ thì tín hiệu càng khó là do nhiễu ngẫu nhiên."""
    bls = BoxLeastSquares(t, flux, err)
    stats = bls.compute_stats(period, duration, t0)
    depth, depth_err = stats["depth"]
    snr = depth / depth_err
    n_transits = int(np.sum(stats["per_transit_count"] > 0))
    rng = np.random.default_rng(seed)
    fake = []
    for _ in range(trials):
        p = period * rng.uniform(0.7, 1.3)
        try:
            s = bls.compute_stats(p, duration, t.min() + rng.uniform(0, p))
        except ValueError:  # mọi transit giả đều rơi vào khoảng trống dữ liệu
            continue
        if np.sum(s["per_transit_count"] > 0) >= min(n_transits, MIN_TRANSITS):
            fake.append(s["depth"][0] / s["depth"][1])
    fake = np.array(fake)
    false_alarm = float(np.mean(fake >= snr)) if len(fake) else None
    print(
        f"  Kiểm chứng P = {period:.4f} ngày: độ sâu = {depth * 1e6:.0f} ± {depth_err * 1e6:.0f} ppm, SNR = {snr:.1f}, "
        f"{n_transits} transit; {false_alarm * 100:.2f}% trong {len(fake)} lần chọn bừa P, T0 cho SNR cao bằng"
    )
    return {
        "period": period, "t0": t0, "duration": duration, "snr": snr, "sde": None, "n_transits": n_transits,
        "source": "verify", "false_alarm": false_alarm, "fake_trials": len(fake), "fake_snr": fake,
    }


def fit_planet(t, flux, det):
    """Khớp hình thang rồi batman cho một hành tinh (các hành tinh khác đã bị che khỏi t, flux)."""
    period = det["period"]
    phase = phase_fold(t, period, det["t0"])
    near = np.abs(phase) < max(3 * det["duration"], 0.3)
    guess = [max(1 - np.median(flux[np.abs(phase) < det["duration"] / 4]), 1e-5), det["duration"], det["duration"] / 8, 0.0]
    try:
        popt, _ = curve_fit(observed_trapezoid, phase[near], flux[near], p0=guess)
        trap_depth, trap_t14, _, trap_dt0 = popt
    except RuntimeError:
        trap_depth, trap_t14, trap_dt0 = guess[0], guess[1], 0.0
    trap_depth, trap_t14 = abs(trap_depth), abs(trap_t14)
    # Tín hiệu yếu có thể làm hình thang trôi đi xa; kéo giá trị khởi đầu về trong giới hạn cho batman
    if not 0.5 * det["duration"] < trap_t14 < 2 * det["duration"]:
        trap_t14 = det["duration"]
    trap_dt0 = float(np.clip(trap_dt0, -0.04, 0.04))

    fit_win = np.abs(phase) < max(1.5 * trap_t14, 0.15)
    k0 = math.sqrt(trap_depth)
    a0 = min(max(period / (math.pi * trap_t14), 2.0), 900)  # xấp xỉ khi b = 0

    def model(tt, dt0, k, a_rs, b):
        return batman_model(tt, period, dt0, k, a_rs, b)

    popt, pcov = curve_fit(
        model, phase[fit_win], flux[fit_win],
        p0=[trap_dt0, k0, a0, 0.3],
        bounds=([-0.05, 0.3 * k0, 1.5, 0.0], [0.05, 2 * k0, 1000, 1.0]),
        max_nfev=5000,  # tín hiệu yếu (vd. Kepler-452b) cần nhiều vòng lặp hơn mặc định
    )
    dt0, k, a_rs, b = popt
    a_rs_err = math.sqrt(pcov[2, 2]) if np.isfinite(pcov[2, 2]) else float("inf")
    incl = math.degrees(math.acos(b / a_rs))
    t14 = period / math.pi * math.asin(min(math.sqrt((1 + k) ** 2 - b**2) / (a_rs * math.sin(math.radians(incl))), 1))
    depth = 1 - model(np.array([dt0]), *popt)[0]
    return {
        "t0": det["t0"] + dt0,
        "k": k,
        "a_rs": a_rs,
        "a_rs_err": a_rs_err,
        "b": b,
        "incl": incl,
        "t14": t14,
        "depth": depth,
        "rho_star": 3 * math.pi / (G * (period * DAY) ** 2) * a_rs**3,  # kg/m^3
        "phase": phase,
        "fit_params": popt,
    }


# ---------------------------------------------------------------- dữ liệu ngoài

def tap_query(url: str, query: str):
    try:
        r = requests.get(url, params={"query": query, "format": "json"}, timeout=60)
        return r.json()
    except Exception as exc:
        print(f"Không truy vấn được {url}: {exc}")
        return []


def fetch_archive_planets(host: str):
    """Tất cả hành tinh đã xác nhận quanh sao này (bảng pscomppars), kể cả hành tinh không có transit."""
    rows = tap_query(ARCHIVE_URL, f"select {ARCHIVE_COLS} from pscomppars where hostname='{host}'")
    return sorted((row for row in rows if row.get("pl_orbper")), key=lambda row: row["pl_orbper"])


def fetch_kois(kepid: int):
    """Các KOI (ứng viên Kepler) của sao, bảng Q1–Q17 DR25."""
    query = (
        "select kepoi_name,kepler_name,koi_disposition,koi_period,koi_prad,koi_depth,koi_model_snr "
        f"from q1_q17_dr25_koi where kepid={kepid}"
    )
    return sorted(tap_query(ARCHIVE_URL, query), key=lambda row: row["kepoi_name"])


def fetch_gaia(ra: float, dec: float, mag: float):
    """Tìm sao trong Gaia DR3 trong bán kính 5" quanh tọa độ, độ sáng gần với cấp sao Kepler (tránh nhầm sao bên cạnh)."""
    query = (
        "SELECT TOP 5 source_id, parallax, parallax_error, phot_g_mean_mag, ruwe, "
        f"DISTANCE(POINT(ra, dec), POINT({ra}, {dec})) * 3600 AS sep "
        "FROM gaiadr3.gaia_source "
        f"WHERE CONTAINS(POINT(ra, dec), CIRCLE({ra}, {dec}, {5 / 3600})) = 1 ORDER BY sep"
    )
    try:
        r = requests.get(
            GAIA_URL, params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "json", "QUERY": query}, timeout=60
        )
        data = r.json()
    except Exception as exc:
        print(f"Không lấy được dữ liệu Gaia: {exc}")
        return None
    names = [col["name"] for col in data["metadata"]]
    rows = [dict(zip(names, row)) for row in data["data"]]
    rows = [row for row in rows if row["parallax"] and abs(row["phot_g_mean_mag"] - mag) < 1.5]
    return rows[0] if rows else None


def read_header(name: str) -> dict:
    header = {}
    with open(CSV_DIR / f"{name}_star_header.csv", encoding="utf-8") as f:
        next(f)
        for line in f:
            key, value = line.strip().split(",", 1)
            try:
                header[key] = float(value)
            except ValueError:
                header[key] = value
    return header


# ---------------------------------------------------------------- vật lý hành tinh

def spectral_type(teff: float) -> str:
    for limit, name in [(30000, "O"), (10000, "B"), (7500, "A"), (6000, "F"), (5200, "G"), (3700, "K")]:
        if teff >= limit:
            return name
    return "M"


def planet_class(r_earth: float) -> str:
    if r_earth < 1.6:
        return "Hành tinh đá"
    if r_earth < 4:
        return "Sub-Neptune"
    if r_earth < 10:
        return "Giống Sao Hải Vương"
    return "Khí khổng lồ"


def mass_from_radius(r_earth: float) -> float:
    """Ước tính khối lượng từ bán kính theo quan hệ thực nghiệm Chen & Kipping (2017), dạng R = C·M^S.
    Với khí khổng lồ (R > ~12 R⊕) bán kính gần như không đổi theo khối lượng nên ước tính rất kém."""
    if r_earth < 1.23:  # hành tinh đá: R = 1.008 M^0.279
        return (r_earth / 1.008) ** (1 / 0.279)
    return (r_earth / 0.808) ** (1 / 0.589)  # kiểu Neptune: R = 0.808 M^0.589


def radius_from_mass(m_earth: float) -> float:
    """Chiều ngược lại của mass_from_radius, dùng cho hành tinh không có transit (không đo được bán kính)."""
    if m_earth < 2.04:
        return 1.008 * m_earth**0.279
    if m_earth < 131.6:
        return 0.808 * m_earth**0.589
    return 14.3 * (m_earth / 131.6) ** -0.044  # khí khổng lồ: bán kính gần như không đổi


def composition(m_earth, r_earth, insol, age_gyr):
    """Suy đoán thành phần từ khối lượng + bán kính. Trả về (tóm tắt ngắn, giải thích chi tiết).

    - Hành tinh nhỏ: so với đường cong lý thuyết R = (1.07 − 0.21·CMF)·M^0.27 (Zeng et al. 2016),
      CMF = tỉ lệ khối lượng lõi sắt (sắt nguyên chất CMF = 1, đá nguyên chất CMF = 0, Trái Đất 0.325).
    - Có lớp khí: tỉ lệ khí H/He theo công thức của Lopez & Fortney (2014).
    - Khí khổng lồ: khối lượng nguyên tố nặng theo Thorngren et al. (2016).
    """
    if m_earth is None:
        return planet_class(r_earth) + " (chỉ theo bán kính)", "Chưa có khối lượng nên chỉ phân loại được theo bán kính."
    density = m_earth * M_EARTH / (4 / 3 * math.pi * (r_earth * R_EARTH) ** 3) / 1000
    if m_earth > 50 or r_earth > 8:
        m_jup = m_earth * M_EARTH / M_JUP
        m_heavy = 57.9 * m_jup**0.61
        z = min(m_heavy / m_earth, 1)
        text = (
            f"Khí khổng lồ, mật độ {density:.2f} g/cm³. Chủ yếu là hydro + heli; nguyên tố nặng (đá, băng, kim loại) "
            f"ước tính ~{m_heavy:.0f} M⊕ (~{z * 100:.0f}% khối lượng)."
        )
        if density < 0.69:
            text += " Xốp hơn Sao Thổ: hành tinh bị **phồng** (hay gặp ở hot Jupiter bị sao mẹ sưởi nóng)."
        return f"Khí khổng lồ H/He, ~{z * 100:.0f}% nguyên tố nặng", text

    scale = m_earth**0.27
    r_iron, r_rock, r_water = 0.86 * scale, 1.07 * scale, 1.24 * scale
    if r_earth < r_iron:
        return "Đặc bất thường", (
            f"Bán kính {r_earth:.2f} R⊕ nhỏ hơn cả quả cầu sắt nguyên chất cùng khối lượng ({r_iron:.2f} R⊕): "
            "nhiều khả năng sai số khối lượng/bán kính còn lớn."
        )
    if r_earth <= r_rock:
        cmf = (1.07 - r_earth / scale) / 0.21
        return f"Đá + sắt, lõi sắt ~{cmf * 100:.0f}%", (
            f"Mật độ {density:.2f} g/cm³, nằm giữa đường 'sắt nguyên chất' ({r_iron:.2f} R⊕) và 'đá nguyên chất' "
            f"({r_rock:.2f} R⊕). Lõi sắt chiếm ~{cmf * 100:.0f}% khối lượng (Trái Đất: 32.5%). Không có khí quyển dày."
        )

    # Lớn hơn hành tinh đá thuần: phải có chất nhẹ. Thử giải thích bằng lớp khí H/He bọc lõi giống Trái Đất.
    r_core = m_earth**0.25
    r_env = r_earth - r_core
    norm = 2.06 * m_earth**-0.21 * insol**0.044 * (age_gyr / 5) ** -0.11
    f_env = 0.05 * (r_env / norm) ** (1 / 0.59) if r_env > 0 else 0.0
    if r_earth <= r_water:
        return "Đá + nhiều nước/băng HOẶC khí mỏng", (
            f"Mật độ {density:.2f} g/cm³: quá nhẹ để là đá thuần ({r_rock:.2f} R⊕) nhưng chưa vượt đường "
            f"'50% nước' ({r_water:.2f} R⊕). Hai khả năng không phân biệt được: (a) thế giới nước, nước/băng chiếm "
            f"tới ~50% khối lượng; (b) lõi đá + lớp khí H/He mỏng ~{f_env * 100:.1f}% khối lượng."
        )
    return f"Lõi đá + lớp khí H/He ~{f_env * 100:.1f}%", (
        f"Mật độ {density:.2f} g/cm³, lớn hơn cả mô hình 50% nước ({r_water:.2f} R⊕) nên phải có lớp khí H/He. "
        f"Với lõi giống Trái Đất, lớp khí chiếm ~{f_env * 100:.1f}% khối lượng nhưng làm bán kính phồng thêm "
        f"{r_env:.1f} R⊕."
    )


def match_archive(period: float, archive_planets):
    for row in archive_planets:
        if abs(row["pl_orbper"] - period) / row["pl_orbper"] < 0.01:
            return row
    return None


def mass_from_rv(k_rv, period_days, ms_kg, incl_deg):
    """Mp·sin i = K · (P / 2πG)^(1/3) · Ms^(2/3)   (khi Mp << Ms). Trả về kg."""
    return k_rv * ((period_days * DAY) / (2 * math.pi * G)) ** (1 / 3) * ms_kg ** (2 / 3) / math.sin(math.radians(incl_deg))


def fmt(value, spec):
    return "—" if value is None else format(value, spec)


# ---------------------------------------------------------------- chương trình chính

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='Tên đã dùng ở bước 1, ví dụ "Kepler-10"')
    parser.add_argument("--host", help="Tên sao trên NASA Exoplanet Archive (mặc định = target)")
    parser.add_argument("--min-period", type=float, default=0.5)
    parser.add_argument("--max-period", type=float, default=100.0)
    parser.add_argument(
        "--verify-archive", action="store_true",
        help="Hành tinh có transit trên NASA mà BLS không tự tìm ra: dùng P, T0 của NASA để gấp pha + khớp mô hình",
    )
    args = parser.parse_args()

    name = slug(args.target)
    OUT_DIR.mkdir(exist_ok=True)
    data = np.loadtxt(CSV_DIR / f"{name}_all_flat.csv", delimiter=",", skiprows=1)
    t, flux, err = data[:, 0], data[:, 1], data[:, 2]
    header = read_header(name)
    baseline = t.max() - t.min()
    print(f"Light curve: {len(t)} điểm, dài {baseline:.0f} ngày")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(t, flux, s=0.3, color="black")
    ax.set_xlabel("Thời gian (BKJD)")
    ax.set_ylabel("Độ sáng chuẩn hóa")
    ax.set_title(f"{args.target}: light curve đã làm phẳng")
    plt.savefig(OUT_DIR / f"{name}_lightcurve.png", dpi=120)
    plt.close()

    # ---- 1. Tìm hành tinh ----
    detections, periodograms = search_planets(t, flux, err, args.min_period, args.max_period)
    fig, axes = plt.subplots(len(periodograms), 1, figsize=(10, 2.6 * len(periodograms)), squeeze=False)
    for ax, (periods, power, ok), round_no in zip(axes[:, 0], periodograms, range(1, 99)):
        ax.plot(periods, power, lw=0.5, color="black" if ok else "gray")
        ax.set_xscale("log")
        ax.set_ylabel("SNR")
        ax.set_title(f"Vòng {round_no}: {'tìm thấy hành tinh' if ok else 'chỉ còn nhiễu'}", fontsize=10)
    axes[-1, 0].set_xlabel("Chu kỳ (ngày)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"{name}_periodogram.png", dpi=120)
    plt.close()

    # ---- 2. Sao mẹ ----
    teff, rs, logg, feh = header["TEFF"], header["RADIUS"], header["LOGG"], header.get("FEH")
    lum = rs**2 * (teff / T_SUN) ** 4
    ms_logg = (10**logg / 100) * (rs * R_SUN) ** 2 / G / M_SUN  # M = g R^2 / G
    archive_planets = fetch_archive_planets(args.host or args.target)
    kois = fetch_kois(int(header["KEPLERID"]))
    age = next((row["st_age"] for row in archive_planets if row.get("st_age")), None)

    if args.verify_archive:
        for arc in archive_planets:
            if not arc.get("tran_flag") or any(abs(d["period"] - arc["pl_orbper"]) / arc["pl_orbper"] < 0.01 for d in detections):
                continue
            print(f"BLS không tự tìm ra {arc['pl_name']} → kiểm chứng bằng P, T0 của NASA")
            detections.append(check_ephemeris(
                t, flux, err, arc["pl_orbper"], arc["pl_tranmid"] - BKJD_OFFSET, arc["pl_trandur"] / 24,
            ))

    # ---- 3. Khớp mô hình từng hành tinh (che transit của các hành tinh khác) ----
    planets = []
    for i, det in enumerate(detections):
        others = np.zeros_like(t, dtype=bool)
        for j, other in enumerate(detections):
            if j != i:
                others |= np.abs(phase_fold(t, other["period"], other["t0"])) < other["duration"] * 0.75
        fit = fit_planet(t[~others], flux[~others], det)
        fit.update(det | {"t0": fit["t0"]})
        fit["mask"] = ~others
        fit["archive"] = match_archive(det["period"], archive_planets)
        planets.append(fit)

    # Khối lượng sao tự tính: mỗi hành tinh cho một giá trị mật độ sao ρ* → Ms = ρ*·thể tích.
    # Lấy trung bình có trọng số theo sai số (σ_Ms / Ms = 3·σ_(a/Rs) / (a/Rs)): hành tinh nhỏ có ingress
    # quá ngắn so với 29.4 phút phơi sáng thì a/Rs gần như không đo được, trọng số sẽ rất thấp.
    estimates = []
    for p in planets:
        m = p["rho_star"] * 4 / 3 * math.pi * (rs * R_SUN) ** 3 / M_SUN
        sigma = 3 * m * p["a_rs_err"] / p["a_rs"]
        p["ms_transit"], p["ms_transit_err"] = m, sigma
        if 0.1 < m < 5 and 0 < sigma < m:
            estimates.append((m, sigma))
    if estimates:
        weights = [1 / s**2 for _, s in estimates]
        ms = sum(m * w for (m, _), w in zip(estimates, weights)) / sum(weights)
        ms_err = 1 / math.sqrt(sum(weights))
    else:  # không có ước tính đáng tin (vd. quỹ đạo lệch tâm, tín hiệu yếu) → dùng logg
        ms, ms_err = ms_logg, None

    for idx, p in enumerate(planets):
        arc = p["archive"]
        p["name"] = arc["pl_name"] if arc else f"Ứng viên {idx + 1}"
        p["transiting"] = True
        p["rp"] = p["k"] * rs * R_SUN
        p["a"] = ((G * ms * M_SUN * (p["period"] * DAY) ** 2) / (4 * math.pi**2)) ** (1 / 3)  # Kepler 3
        p["teq"] = teff * math.sqrt(rs * R_SUN / (2 * p["a"])) * (1 - 0.3) ** 0.25  # albedo 0.3
        p["insol"] = lum / (p["a"] / AU) ** 2
        p["v_orb"] = 2 * math.pi * p["a"] / (p["period"] * DAY)
        p["prob"] = rs * R_SUN / p["a"]
        if arc and arc.get("pl_rvamp"):
            p["mass"] = mass_from_rv(arc["pl_rvamp"], p["period"], ms * M_SUN, p["incl"]) / M_EARTH
            p["mass_source"] = f"RV (K = {arc['pl_rvamp']} m/s đã công bố, Ms và i tự tính)"
        elif arc and arc.get("pl_bmasse") and arc.get("pl_bmassprov") == "Mass":
            p["mass"] = arc["pl_bmasse"]
            p["mass_source"] = "Đã công bố (NASA)"
        else:
            p["mass"] = None
            p["mass_source"] = f"Chưa đo; ước tính từ bán kính ~{mass_from_radius(p['rp'] / R_EARTH):.1f} M⊕"
        p["mass_estimate"] = mass_from_radius(p["rp"] / R_EARTH)

    # ---- 4. Hành tinh không có transit (chỉ phát hiện bằng RV...) ----
    matched = {p["archive"]["pl_name"] for p in planets if p["archive"]}
    for arc in archive_planets:
        if arc["pl_name"] in matched:
            continue
        p = {"name": arc["pl_name"], "period": arc["pl_orbper"], "transiting": bool(arc.get("tran_flag")), "archive": arc}
        p["a"] = ((G * ms * M_SUN * (p["period"] * DAY) ** 2) / (4 * math.pi**2)) ** (1 / 3)
        p["teq"] = teff * math.sqrt(rs * R_SUN / (2 * p["a"])) * (1 - 0.3) ** 0.25
        p["insol"] = lum / (p["a"] / AU) ** 2
        p["v_orb"] = 2 * math.pi * p["a"] / (p["period"] * DAY)
        p["prob"] = rs * R_SUN / p["a"]
        if arc.get("pl_rvamp"):
            p["mass"] = mass_from_rv(arc["pl_rvamp"], p["period"], ms * M_SUN, 90) / M_EARTH
            p["mass_source"] = f"Khối lượng TỐI THIỂU Mp·sin i từ RV (K = {arc['pl_rvamp']} m/s)"
        else:
            p["mass"] = arc.get("pl_bmasse")
            p["mass_source"] = f"Đã công bố ({arc.get('pl_bmassprov')})"
        p["rp"] = radius_from_mass(p["mass"]) * R_EARTH if p["mass"] else None
        p["note"] = (
            f"Phát hiện bằng {arc.get('discoverymethod')}, không có transit trong dữ liệu Kepler → không đo được "
            "bán kính, độ nghiêng; bán kính bên dưới chỉ là ước tính từ khối lượng."
        )
        planets.append(p)
    planets.sort(key=lambda p: p["period"])

    for p in planets:
        r_e = p["rp"] / R_EARTH if p.get("rp") else None
        if r_e and p["transiting"] and "k" in p:
            p["comp_short"], p["comp_text"] = composition(p["mass"], r_e, p["insol"], age or 5.0)
        else:
            p["comp_short"], p["comp_text"] = "Không xác định", "Không có bán kính đo được (không transit) nên không suy ra được mật độ và thành phần."

    # ---- 5. Biểu đồ + CSV gấp pha cho từng hành tinh có transit ----
    fitted = [p for p in planets if "k" in p]
    if fitted:
        fig, axes = plt.subplots(1, len(fitted), figsize=(6 * len(fitted), 4.5), squeeze=False)
        for ax, p in zip(axes[0], fitted):
            tt, ff = t[p["mask"]], flux[p["mask"]]
            phase = phase_fold(tt, p["period"], p["t0"])
            span = max(p["t14"] * 1.5, 0.1)
            near = np.abs(phase) < span
            bins = np.linspace(-span, span, 61)
            idx = np.digitize(phase[near], bins)
            centres = np.array([(bins[i - 1] + bins[i]) / 2 for i in range(1, len(bins)) if (idx == i).sum() >= 3])
            binned = np.array([np.median(ff[near][idx == i]) for i in range(1, len(bins)) if (idx == i).sum() >= 3])
            dt0 = p["fit_params"][0]
            models = batman_model(centres + dt0, p["period"], dt0, *p["fit_params"][1:])
            with open(CSV_DIR / f"{name}_{slug(p['name'])}_folded.csv", "w", encoding="utf-8") as f:
                f.write("hours_from_mid_transit,flux_binned,model\n")
                for c, fl, m in zip(centres, binned, models):
                    f.write(f"{c * 24:.4f},{fl:.6f},{m:.6f}\n")
            ax.scatter(phase[near] * 24, ff[near], s=0.5, alpha=0.2, color="gray")
            ax.scatter(centres * 24, binned, s=10, color="black", label="gộp bin")
            curve = np.linspace(-span, span, 1000)
            ax.plot(curve * 24, batman_model(curve + dt0, p["period"], dt0, *p["fit_params"][1:]), color="crimson", label="mô hình batman")
            ax.set_ylim(1 - p["depth"] * 2.5, 1 + p["depth"] * 1.2)
            ax.set_xlabel("Giờ tính từ tâm transit")
            ax.set_title(f"{p['name']}: P = {p['period']:.4f} ngày, sâu {p['depth'] * 1e6:.0f} ppm", fontsize=10)
            ax.legend(fontsize=8)
        axes[0, 0].set_ylabel("Độ sáng chuẩn hóa")
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"{name}_folded.png", dpi=120)
        plt.close()

    # Hành tinh kiểm chứng (tín hiệu yếu): xem riêng từng transit + phép thử báo động giả.
    # CSV từng transit (±1.5 ngày) đủ nhỏ để làm toàn bộ trên Google Sheets.
    for p in [p for p in fitted if p.get("source") == "verify"]:
        epochs = np.unique(np.round((t - p["t0"]) / p["period"]).astype(int))
        epochs = [n for n in epochs if np.any(np.abs(t - (p["t0"] + n * p["period"])) < p["t14"] / 2)]
        fig, axes = plt.subplots(1, len(epochs) + 1, figsize=(4 * (len(epochs) + 1), 3.8), squeeze=False)
        with open(CSV_DIR / f"{name}_{slug(p['name'])}_transits.csv", "w", encoding="utf-8") as f:
            f.write("transit_no,time_bkjd,hours_from_mid_transit,flux\n")
            for ax, n in zip(axes[0], epochs):
                mid = p["t0"] + n * p["period"]
                win = np.abs(t - mid) < 1.5
                for tt, ff in zip(t[win], flux[win]):
                    f.write(f"{n},{tt:.6f},{(tt - mid) * 24:.4f},{ff:.6f}\n")
                inside = np.abs(t - mid) < p["t14"] / 2
                ax.scatter((t[win] - mid) * 24, flux[win], s=4, color="black")
                ax.axvspan(-p["t14"] * 12, p["t14"] * 12, color="crimson", alpha=0.1)
                ax.axhline(1 - p["depth"], color="crimson", lw=0.8, ls="--")
                ax.set_title(f"Transit {n} (BKJD {mid:.1f}): sâu {(1 - np.mean(flux[inside])) * 1e6:.0f} ppm", fontsize=9)
                ax.set_xlabel("Giờ tính từ tâm transit")
                ax.set_ylim(1 - 6 * p["depth"], 1 + 4 * p["depth"])
        ax = axes[0, -1]
        ax.hist(p["fake_snr"], bins=50, color="gray")
        ax.axvline(p["snr"], color="crimson", label=f"tín hiệu thật, SNR {p['snr']:.1f}")
        ax.set_title(f"SNR khi chọn bừa P, T0 ({p['fake_trials']} lần)", fontsize=9)
        ax.set_xlabel("SNR")
        ax.legend(fontsize=8)
        axes[0, 0].set_ylabel("Độ sáng chuẩn hóa")
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"{name}_{slug(p['name'])}_transits.png", dpi=120)
        plt.close()

    # ---- 6. Khoảng cách ----
    gaia = fetch_gaia(header["RA_OBJ"], header["DEC_OBJ"], header["KEPMAG"])
    abs_mag = 4.74 - 2.5 * math.log10(lum)
    d_phot = 10 ** ((header["KEPMAG"] - abs_mag + 5) / 5)
    d_pc = 1000 / gaia["parallax"] if gaia else d_phot

    # ---- 7. Báo cáo ----
    n_transit = sum(1 for p in planets if "k" in p)
    n_verify = sum(1 for p in planets if p.get("source") == "verify")
    lines = [f"# Hệ hành tinh {args.target}", ""]
    lines.append(
        f"Dữ liệu: {len(t)} điểm Kepler long cadence, dài {baseline:.0f} ngày. "
        f"**Tổng cộng {len(planets)} hành tinh**: {n_transit - n_verify} tự tìm thấy bằng transit"
        + (f", {n_verify} BLS không tự tìm ra, kiểm chứng bằng P, T0 của NASA" if n_verify else "")
        + (f", {len(planets) - n_transit} bổ sung từ NASA Exoplanet Archive (không có transit)." if len(planets) > n_transit else ".")
    )
    for p in planets:
        if p.get("source") == "verify":
            lines += ["", (
                f"⚠️ **{p['name']}** quá yếu để BLS tự tìm (đỉnh periodogram mạnh nhất là nhiễu). Khi gấp pha đúng "
                f"P, T0 đã công bố: SNR = {p['snr']:.1f}, {p['n_transits']} transit. Phép thử báo động giả: "
                f"**{p['false_alarm'] * 100:.2f}%** trong {p['fake_trials']} lần chọn bừa P, T0 cũng cho SNR cao bằng. "
                f"Xem `{name}_{slug(p['name'])}_transits.png`."
            )]

    lines += ["", "## Sao mẹ", "", "| Thông số | Giá trị | NASA |", "|---|---|---|"]
    arc0 = archive_planets[0] if archive_planets else {}
    star_rows = [
        ("Nhiệt độ bề mặt Teff (KIC)", f"{teff:.0f} K", arc0.get("st_teff")),
        ("Loại phổ (suy từ Teff)", spectral_type(teff), None),
        ("Bán kính Rs (KIC)", f"{rs:.3f} R☉", arc0.get("st_rad")),
        ("Khối lượng từ logg (KIC)", f"{ms_logg:.3f} M☉", arc0.get("st_mass")),
        ("Khối lượng dùng cho tính toán", f"{ms:.3f}" + (f" ± {ms_err:.3f} M☉ (từ mật độ transit)" if ms_err else " M☉ (từ logg)"), arc0.get("st_mass")),
        ("Độ sáng L", f"{lum:.2f} L☉", None),
        ("Độ kim loại [Fe/H] (KIC)", f"{feh} dex" + (f" (kim loại gấp ~{10 ** float(feh):.1f} lần Mặt Trời)" if feh not in (None, "None") else ""), arc0.get("st_met")),
        ("Tuổi", f"{age} tỷ năm (NASA)" if age else "—", None),
    ]
    for label, value, ref_value in star_rows:
        lines.append(f"| {label} | {value} | {'' if ref_value is None else ref_value} |")

    lines += ["", "## Khoảng cách từ Trái Đất", ""]
    if gaia:
        d_err = d_pc * gaia["parallax_error"] / gaia["parallax"]
        lines.append(
            f"- **Thị sai Gaia DR3** (nguồn {gaia['source_id']}): {gaia['parallax']:.4f} ± {gaia['parallax_error']:.4f} mas, "
            f"RUWE = {gaia['ruwe']:.2f} (< 1.4 là đáng tin) → **{d_pc:.1f} ± {d_err:.1f} pc ≈ {d_pc * PC_TO_LY:.0f} năm ánh sáng**"
        )
    lines.append(f"- Ước tính bằng độ sáng (M = {abs_mag:.2f}, Kp = {header['KEPMAG']:.2f}): ~{d_phot:.0f} pc (thô, không tính bụi)")
    if arc0.get("sy_dist"):
        lines.append(f"- NASA Exoplanet Archive: {arc0['sy_dist']:.0f} pc")
    lines.append(
        f"- Khoảng cách tới từng hành tinh = khoảng cách tới sao ± a. Quỹ đạo rộng nhất ({max(p['a'] for p in planets) / AU:.3f} AU) "
        f"chỉ bằng {max(p['a'] for p in planets) / AU / (d_pc * 206265):.1e} lần khoảng cách nên coi như **bằng nhau**."
        if planets else "- Chưa có hành tinh."
    )

    if planets:
        lines += ["", "## Thông số các hành tinh", ""]
        lines.append("| Thông số | " + " | ".join(p["name"] for p in planets) + " |")
        lines.append("|---|" + "---|" * len(planets))

        def row(label, getter):
            cells = []
            for p in planets:
                try:
                    cells.append(getter(p))
                except (KeyError, TypeError):
                    cells.append("—")
            lines.append(f"| {label} | " + " | ".join(cells) + " |")

        def ref(p, col, spec):
            arc = p.get("archive")
            return f" ({format(arc[col], spec)})" if arc and arc.get(col) is not None else ""

        lines.append("| *Số trong ngoặc: giá trị NASA* |" + " |" * len(planets))
        row("Phát hiện bằng", lambda p: (
            ("Transit (kiểm chứng theo P, T0 NASA)" if p.get("source") == "verify" else "Transit (tự tìm)")
            if "k" in p else p["archive"].get("discoverymethod", "?")
        ))
        row("Chu kỳ P (ngày)", lambda p: f"{p['period']:.5f}" + ref(p, "pl_orbper", ".5f"))
        row("SNR / số transit thấy được", lambda p: f"{p['snr']:.0f} / {p['n_transits']}")
        row("Độ sâu transit (ppm)", lambda p: f"{p['depth'] * 1e6:.0f}")
        row("Thời lượng T14 (giờ)", lambda p: f"{p['t14'] * 24:.2f}" + ref(p, "pl_trandur", ".2f"))
        row("Rp / Rs", lambda p: f"{p['k']:.4f}" + ref(p, "pl_ratror", ".4f"))
        row("Tham số va chạm b", lambda p: f"{p['b']:.2f}" + ref(p, "pl_imppar", ".2f"))
        row("a / Rs", lambda p: f"{p['a_rs']:.2f} ± {p['a_rs_err']:.2f}" + ref(p, "pl_ratdor", ".2f"))
        row("Khối lượng sao suy từ transit (M☉)", lambda p: f"{p['ms_transit']:.2f} ± {p['ms_transit_err']:.2f}")
        row("Độ nghiêng i (độ)", lambda p: f"{p['incl']:.2f}" + ref(p, "pl_orbincl", ".2f"))
        row("Bán kính (R⊕)", lambda p: (f"{p['rp'] / R_EARTH:.2f}" if "k" in p else f"~{p['rp'] / R_EARTH:.1f} (ước tính)") + ref(p, "pl_rade", ".2f"))
        row("Bán kính (R♃)", lambda p: f"{p['rp'] / R_JUP:.3f}" + ref(p, "pl_radj", ".3f"))
        row("Khối lượng (M⊕)", lambda p: fmt(p["mass"], ".1f") + ref(p, "pl_bmasse", ".1f"))
        row("Khối lượng (M♃)", lambda p: fmt(p["mass"] * M_EARTH / M_JUP, ".4f"))
        row("Nguồn khối lượng", lambda p: p["mass_source"])
        row("Mật độ (g/cm³)", lambda p: fmt(p["mass"] * M_EARTH / (4 / 3 * math.pi * p["rp"] ** 3) / 1000, ".2f") if "k" in p else "—")
        row("Trọng lực bề mặt (× Trái Đất)", lambda p: fmt(G * p["mass"] * M_EARTH / p["rp"] ** 2 / 9.81, ".2f") if "k" in p else "—")
        row("Bán trục lớn a (AU)", lambda p: f"{p['a'] / AU:.4f}" + ref(p, "pl_orbsmax", ".4f"))
        row("Độ lệch tâm e", lambda p: "giả định 0" + ref(p, "pl_orbeccen", ".2f"))
        row("Vận tốc quỹ đạo (km/s)", lambda p: f"{p['v_orb'] / 1000:.0f}")
        row("Nhiệt độ cân bằng Teq (K)", lambda p: f"{p['teq']:.0f}" + ref(p, "pl_eqt", ".0f"))
        row("Bức xạ nhận được (× Trái Đất)", lambda p: f"{p['insol']:.0f}" + ref(p, "pl_insol", ".0f"))
        row("Xác suất có transit Rs/a (%)", lambda p: f"{p['prob'] * 100:.1f}")
        row("Loại theo bán kính", lambda p: planet_class(p["rp"] / R_EARTH))
        row("**Thành phần**", lambda p: p["comp_short"])

        lines += ["", "## Thành phần từng hành tinh", ""]
        for p in planets:
            lines.append(f"- **{p['name']}**: {p['comp_text']}" + (f" {p['note']}" if p.get("note") else ""))
        lines += [
            "",
            "Thành phần ở đây là **suy đoán từ mật độ** (khối lượng / thể tích) so với mô hình lý thuyết. "
            "Muốn biết thành phần khí quyển thật (H₂O, CO₂, CH₄...) phải chụp phổ truyền qua bằng JWST/HST.",
        ]

    if kois:
        lines += ["", "## Đối chiếu với danh sách ứng viên Kepler (KOI DR25)", ""]
        lines.append("| KOI | Tên | Kết luận | Chu kỳ (ngày) | Bán kính (R⊕) | Script tìm thấy? |")
        lines.append("|---|---|---|---|---|---|")
        for koi in kois:
            hits = [p for p in planets if "k" in p and abs(p["period"] - koi["koi_period"]) / koi["koi_period"] < 0.01]
            found = "❌" if not hits else "🔍 chỉ kiểm chứng" if hits[0].get("source") == "verify" else "✅"
            lines.append(
                f"| {koi['kepoi_name']} | {koi.get('kepler_name') or ''} | {koi['koi_disposition']} | "
                f"{koi['koi_period']:.4f} | {koi.get('koi_prad')} | {found} |"
            )

    report = "\n".join(lines) + "\n"
    (OUT_DIR / f"{name}_report.md").write_text(report, encoding="utf-8")

    # ---- 8. JSON cho sơ đồ ----
    system = {
        "target": args.target,
        "star": {"teff": teff, "radius_rsun": rs, "mass_msun": ms, "lum_lsun": lum, "distance_pc": d_pc},
        "planets": [
            {
                "name": p["name"],
                "period_days": p["period"],
                "t0_bkjd": p.get("t0"),
                "a_au": p["a"] / AU,
                "radius_earth": p["rp"] / R_EARTH if p.get("rp") else None,
                "radius_measured": "k" in p,
                "mass_earth": p["mass"],
                # Các trường dưới đây dùng cho bước tìm vệ tinh (04_moons.py)
                "mass_estimate_earth": p.get("mass_estimate"),
                "t14_days": p.get("t14"),
                "rp_rs": p.get("k"),
                "a_rs": p.get("a_rs"),
                "impact_b": p.get("b"),
                "depth": p.get("depth"),
                "detection": p.get("source", "bls") if "k" in p else None,
                "transiting": p["transiting"],
                "teq_k": p["teq"],
                "composition": p["comp_short"],
            }
            for p in planets
        ],
    }
    (OUT_DIR / f"{name}_system.json").write_text(json.dumps(system, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + report)
    print(f"Biểu đồ, báo cáo, JSON: {OUT_DIR}")
    print(f'Vẽ sơ đồ hệ: .venv/Scripts/python scripts/03_diagram.py "{args.target}"')


def slug(name: str) -> str:
    return name.replace(" ", "").replace("-", "")


if __name__ == "__main__":
    main()
