"""Bước 4: tìm vệ tinh (exomoon) quanh từng hành tinh có transit.

Light curve Kepler gần như không bao giờ "thấy" trực tiếp được vệ tinh, nhưng đặt được GIỚI HẠN TRÊN:
    1. Vùng vệ tinh có thể tồn tại: giữa giới hạn Roche (gần quá bị xé vụn) và ~0.49 bán kính Hill
       (xa quá bị sao mẹ giật mất).
    2. TTV (Transit Timing Variation): hành tinh và vệ tinh cùng quay quanh tâm khối chung, nên hành tinh
       lúc đến sớm lúc đến muộn. Đo thời điểm từng transit → độ lệch O−C → giới hạn khối lượng vệ tinh.
    3. OSE (Orbital Sampling Effect): cộng mọi transit lại thì vệ tinh tạo một "vai" trũng rất nông
       hai bên transit hành tinh. Đo độ trũng ở vùng vai → giới hạn bán kính vệ tinh.

Cần chạy 02_analyze.py trước. Cách chạy:
    .venv/Scripts/python scripts/04_moons.py "Kepler-10"

Kết quả:
    data/csv/<sao>_<hành tinh>_transit_times.csv   thời điểm từng transit + O−C, cho Google Sheets
    data/csv/<sao>_<hành tinh>_ose_profile.csv     transit gấp pha gộp bin trong vùng vệ tinh, cho Google Sheets
    outputs/<sao>_moons.png                        O−C và vùng vai của từng hành tinh
    outputs/<sao>_moons.md                         báo cáo

Công thức xem docs/kien-thuc-exoplanet.md, mục 7.9.
"""

import argparse
import importlib
import json
import math
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from astropy.timeseries import LombScargle
from scipy.stats import chi2 as chi2_dist

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
analyze = importlib.import_module("02_analyze")  # tên file bắt đầu bằng số nên không import thường được

G, AU, DAY = analyze.G, analyze.AU, analyze.DAY
R_SUN, M_SUN, R_EARTH, M_EARTH = analyze.R_SUN, analyze.M_SUN, analyze.R_EARTH, analyze.M_EARTH
EXPOSURE = analyze.EXPOSURE
CSV_DIR, OUT_DIR = analyze.CSV_DIR, analyze.OUT_DIR

HILL_STABLE = 0.4895  # vệ tinh quay cùng chiều bền vững tới ~0.49 bán kính Hill (Domingos et al. 2006)
MOON_DENSITY = 3000.0  # kg/m³, giả định vệ tinh đá (Mặt Trăng 3.34, Io 3.53, Ganymede 1.94 g/cm³)
M_MOON = 7.342e22  # khối lượng Mặt Trăng (kg)
REFERENCE_MOONS = [("Mặt Trăng", 0.273), ("Titan", 0.404), ("Ganymede", 0.413), ("Sao Hỏa", 0.532), ("Trái Đất", 1.0)]


def moon_zone(planet, star):
    """Vùng vệ tinh có thể tồn tại và các đại lượng quỹ đạo liên quan."""
    mass_measured = planet["mass_earth"] is not None
    mp = (planet["mass_earth"] if mass_measured else planet["mass_estimate_earth"]) * M_EARTH
    ms = star["mass_msun"] * M_SUN
    rp = planet["radius_earth"] * R_EARTH
    a = planet["a_au"] * AU
    hill = a * (mp / (3 * ms)) ** (1 / 3)
    a_max = HILL_STABLE * hill
    rho_p = mp / (4 / 3 * math.pi * rp**3)
    roche = 2.44 * rp * (rho_p / MOON_DENSITY) ** (1 / 3)  # giới hạn Roche cho vệ tinh "lỏng" (bị thủy triều kéo dãn)
    v_p = 2 * math.pi * a / (planet["period_days"] * DAY)
    return {
        "mp": mp, "mass_measured": mass_measured, "rp": rp, "hill": hill, "a_max": a_max, "roche": roche,
        "possible": a_max > roche,
        "p_moon_max": 2 * math.pi * math.sqrt(a_max**3 / (G * mp)) / DAY,
        "v_p": v_p,
        "dt_max": a_max / v_p / DAY,  # vệ tinh lệch trước/sau hành tinh tối đa bao nhiêu thời gian (ngày)
    }


def transit_template(planet):
    """Mô hình transit của hành tinh (đã khớp ở bước 2) trên lưới dày, để nội suy cho nhanh."""
    span = planet["t14_days"] * 1.5 + 0.1
    grid = np.linspace(-span, span, 4001)
    a_rs = planet["a_rs"]
    flux = analyze.batman_model(grid, planet["period_days"], 0.0, planet["rp_rs"], a_rs, planet["impact_b"])
    return grid, flux


def cadence_alias(period, ls_period, epochs, cadence):
    """Chu kỳ "TTV" có trùng một họa âm của chu kỳ phách giữa chu kỳ hành tinh và nhịp đo 29.4 phút không?

    Mỗi vòng, tâm transit rơi vào một vị trí khác trong khoảng 29.4 phút giữa 2 lần đo (lệch đi frac(P/cadence)).
    Phép định thời hơi thiên lệch theo vị trí đó (nhất là khi ingress ngắn hơn 29.4 phút), nên O−C dao động theo
    chu kỳ phách 1/frac và các họa âm của nó. Đây là lỗi đo, KHÔNG phải TTV thật. Trả về bậc họa âm k nếu trùng."""
    if ls_period is None:
        return None
    beat = (period / cadence) % 1
    beat = min(beat, 1 - beat)  # số chu kỳ phách mỗi vòng
    tolerance = 1 / (epochs.max() - epochs.min())  # 1 phần tử phân giải của periodogram
    if tolerance > 0.005:
        return None  # quá ít vòng: các họa âm chồng lên nhau, không phân biệt được
    for k in range(1, 16):
        alias = (k * beat) % 1
        alias = min(alias, 1 - alias)  # tần số > 0.5 vòng⁻¹ bị gập lại (lấy mẫu mỗi vòng 1 lần)
        if abs(alias - 1 / ls_period) < tolerance:
            return k
    return None


def cadence_phase_test(tc, oc, t_ref, cadence, bins=5):
    """Kiểm tra trực tiếp: O−C trung bình có đổi theo vị trí tâm transit trong khoảng 29.4 phút giữa 2 lần đo không?
    Chia thành 5 nhóm theo vị trí đó, so trung bình các nhóm (sai số lấy từ độ tán xạ thật). Trả về p-value:
    nhỏ (< 0.001) nghĩa là định thời bị thiên lệch theo lưới đo."""
    phase = ((tc - t_ref) / cadence) % 1
    idx = np.minimum((phase * bins).astype(int), bins - 1)
    scatter = np.std(oc)
    chi2, used = 0.0, 0
    for i in range(bins):
        m = idx == i
        if m.sum() >= 5:
            chi2 += ((np.mean(oc[m]) - np.mean(oc)) / (scatter / math.sqrt(m.sum()))) ** 2
            used += 1
    return float(chi2_dist.sf(chi2, used - 1)) if used >= 3 else None


def time_transits(t, flux, err, planet, cadence):
    """Đo thời điểm từng transit: dịch mô hình cố định hình dạng, chọn độ dịch cho χ² nhỏ nhất.
    Sai số lấy theo quy tắc Δχ² = 1 quanh cực tiểu."""
    period, t0, t14 = planet["period_days"], planet["t0_bkjd"], planet["t14_days"]
    grid, template = transit_template(planet)
    search = max(0.5 * t14, 3 * EXPOSURE)
    shifts = np.linspace(-search, search, 401)
    expected = t14 / EXPOSURE
    epochs = np.round((t - t0) / period).astype(int)
    rows = []
    for n in np.unique(epochs):
        mid = t0 + n * period
        win = np.abs(t - mid) < t14 + search
        dt = t[win] - mid
        left = np.sum((dt > -t14 / 2) & (dt < -t14 / 6))
        right = np.sum((dt < t14 / 2) & (dt > t14 / 6))
        if np.sum(np.abs(dt) < t14 / 2) < max(0.6 * expected, 3) or min(left, right) < max(0.15 * expected, 1):
            continue  # transit rơi vào khoảng trống dữ liệu, thiếu ingress hoặc egress
        # Độ nhiễu thật quanh transit này (sai số pipeline thường nhỏ hơn thực tế → sai số thời điểm bị đánh giá thấp)
        outside = np.abs(dt) > t14 / 2 + EXPOSURE
        noise = np.std(flux[win][outside]) if outside.sum() >= 5 else np.median(err[win])
        noise = max(noise, np.median(err[win]))
        model = np.interp(dt[None, :] - shifts[:, None], grid, template, left=1, right=1)
        chi2 = np.sum(((flux[win][None, :] - model) / noise) ** 2, axis=1)
        best = int(np.argmin(chi2))
        if best in (0, len(shifts) - 1):
            continue  # cực tiểu nằm ở mép: tín hiệu quá yếu để định thời
        around = chi2 <= chi2[best] + 1
        sigma = (shifts[around].max() - shifts[around].min()) / 2
        sigma = max(sigma, (shifts[1] - shifts[0]) / 2)
        rows.append((n, mid + shifts[best], sigma))
    if len(rows) < 3:
        return None
    n, tc, sig = (np.array(col) for col in zip(*rows))
    # Khớp lại chu kỳ tuyến tính (trọng số 1/σ²) rồi tính O − C. Transit định thời hỏng (rơi sát khoảng trống,
    # tia vũ trụ...) lệch hàng chục phút sẽ kéo lệch cả đường thẳng, nên loại các điểm lệch > 5 lần MAD rồi khớp lại.
    used = np.ones_like(n, dtype=bool)
    for _ in range(5):
        w = 1 / sig[used] ** 2
        A = np.vstack([np.ones(used.sum()), n[used]]).T * np.sqrt(w)[:, None]
        (c0, c1), *_ = np.linalg.lstsq(A, tc[used] * np.sqrt(w), rcond=None)
        oc = tc - (c0 + c1 * n)
        mad = 1.4826 * np.median(np.abs(oc[used] - np.median(oc[used])))
        new_used = np.abs(oc) <= np.maximum(5 * mad, 3 * sig)
        if np.array_equal(new_used, used) or new_used.sum() < 3:
            break
        used = new_used
    chi2 = float(np.sum((oc[used] / sig[used]) ** 2))
    dof = int(used.sum()) - 2
    # Kiểm định TTV bằng periodogram Lomb–Scargle của O−C: TTV do vệ tinh (bị lấy mẫu thưa nên hiện ra như một
    # chu kỳ "ảo") hay do hành tinh khác đều có tính chu kỳ. Độ mạnh LS không đổi khi nhân mọi sai số với cùng
    # một hệ số, nên không bị lừa khi sai số thời điểm bị đánh giá thấp (như χ²).
    fap, ls_period = None, None
    if used.sum() >= 8:
        ls = LombScargle(n[used], oc[used], sig[used])
        span = n[used].max() - n[used].min()
        freq = np.linspace(1 / span, 0.5, max(200, 10 * int(span)))
        power = ls.power(freq)
        best = int(np.argmax(power))
        fap = float(ls.false_alarm_probability(power[best], minimum_frequency=freq[0], maximum_frequency=freq[-1]))
        ls_period = 1 / freq[best]
    # Phép thử chia đôi: tín hiệu thật (vệ tinh, hành tinh khác) phải có mặt ở CẢ hai nửa dữ liệu.
    # Mỗi nửa tìm đỉnh mạnh nhất riêng; nếu cả hai trùng chu kỳ của toàn bộ dữ liệu thì tín hiệu "ổn định".
    halves_agree = None
    if used.sum() >= 16:
        nu, ocu, sgu = n[used], oc[used], sig[used]
        middle = np.median(nu)
        halves_agree = True
        for part in (nu < middle, nu >= middle):
            half_power = LombScargle(nu[part], ocu[part], sgu[part]).power(freq)
            half_period = 1 / freq[int(np.argmax(half_power))]
            halves_agree = halves_agree and bool(abs(half_period - ls_period) / ls_period < 0.05)
    return {
        "epoch": n, "tc": tc, "sigma": sig, "oc": oc, "used": used, "period": c1, "t0": c0,
        "n_used": int(used.sum()), "n_clipped": int((~used).sum()),
        "chi2_red": chi2 / max(dof, 1),
        "fap": fap, "ls_period": ls_period, "cadence_alias": cadence_alias(c1, ls_period, n[used], cadence),
        "cadence_p": cadence_phase_test(tc[used], oc[used], t.min(), cadence) if used.sum() >= 15 else None,
        "halves_agree": halves_agree,
        "rms": float(np.sqrt(np.mean(oc[used] ** 2))), "sigma_mean": float(np.sqrt(np.mean(sig[used] ** 2))),
    }


def ttv_mass_limit(timing, zone):
    """Giới hạn trên khối lượng vệ tinh từ TTV.

    Hành tinh lệch khỏi tâm khối một đoạn a_v·M_v/M_p, chạy với vận tốc v_p nên đến sớm/muộn tối đa
    a_v·M_v/(M_p·v_p); trung bình bình phương của dao động hình sin = biên độ/√2.
    → M_v = √2 · σ_TTV · v_p · M_p / a_v. Lấy a_v = a_max (vệ tinh xa nhất cho tín hiệu lớn nhất, giới hạn chặt nhất).
    σ_TTV lấy bằng chính độ tán xạ O−C đo được (rms): tín hiệu vệ tinh không thể lớn hơn tổng tán xạ thấy được.
    Cách này thận trọng (giới hạn hơi lỏng) nhưng không phụ thuộc việc sai số thời điểm có bị đánh giá thấp hay không."""
    sigma_lim = timing["rms"] * DAY
    return sigma_lim, math.sqrt(2) * sigma_lim * zone["v_p"] * zone["mp"] / zone["a_max"]


def ose_limit(t, flux, planet, zone, star, timing, others_mask):
    """Giới hạn bán kính vệ tinh từ hiệu ứng lấy mẫu quỹ đạo (OSE).

    Mỗi transit, vệ tinh nằm ở một chỗ khác nhau quanh hành tinh (trong khoảng ±Δt_max). Cộng hàng trăm
    transit thì các chỗ trũng nhỏ của vệ tinh "nhòe" thành một vai nông ở hai bên transit hành tinh.
    Tổng diện tích trũng mỗi transit ≈ δ_v·T14, trải trên bề rộng ~2Δt_max + T14
    → độ trũng trung bình vùng vai ≈ δ_v · T14 / (2Δt_max + T14)."""
    period = timing["period"] if timing else planet["period_days"]
    t0 = timing["t0"] if timing else planet["t0_bkjd"]
    t14, dt_max = planet["t14_days"], zone["dt_max"]
    inner = 0.6 * t14 + EXPOSURE  # bỏ phần transit hành tinh (kể cả nhòe phơi sáng)
    outer = dt_max + t14 / 2
    if outer <= inner + EXPOSURE:
        return None  # vùng vệ tinh nằm gọn trong transit hành tinh: OSE không tách ra được
    base_in = outer + t14 / 2
    base_out = min(base_in + max(2 * dt_max, 1.0), period / 2)
    if base_out <= base_in + EXPOSURE:
        return None
    phase = analyze.phase_fold(t, period, t0)
    use = ~others_mask
    ap = np.abs(phase)
    moon = use & (ap > inner) & (ap < outer)
    base = use & (ap > base_in) & (ap < base_out)
    if moon.sum() < 10 or base.sum() < 10:
        return None
    deficit = np.mean(flux[base]) - np.mean(flux[moon])
    sigma = np.std(flux[base]) * math.sqrt(1 / moon.sum() + 1 / base.sum())
    depth_lim = (max(deficit, 0) + 2 * sigma) * (2 * dt_max + t14) / t14
    r_lim = math.sqrt(depth_lim) * star["radius_rsun"] * R_SUN / R_EARTH
    # Biên dạng gộp bin để vẽ / xuất CSV cho Google Sheets
    span = base_out
    near = use & (ap < span)
    edges = np.linspace(-span, span, 121)
    idx = np.digitize(phase[near], edges)
    profile = [
        ((edges[i - 1] + edges[i]) / 2 * 24, float(np.mean(flux[near][idx == i])), int(np.sum(idx == i)))
        for i in range(1, len(edges)) if np.sum(idx == i) >= 5
    ]
    return {
        "deficit": deficit, "sigma": sigma, "depth_lim": depth_lim, "r_lim": r_lim,
        "inner": inner, "outer": outer, "base_in": base_in, "base_out": base_out,
        "n_moon": int(moon.sum()), "n_base": int(base.sum()), "profile": profile,
    }


def verdict_ttv(timing):
    if timing is None:
        return "Không định thời được (tín hiệu quá yếu hoặc quá ít transit)"
    if timing["fap"] is None:
        return f"Quá ít transit ({timing['n_used']}) để kiểm định tính chu kỳ; chỉ đặt được giới hạn trên"
    phase_biased = timing["cadence_p"] is not None and timing["cadence_p"] < 0.001
    if timing["fap"] < 0.001 and (timing["cadence_alias"] or phase_biased):
        why = (f"trùng họa âm bậc {timing['cadence_alias']} của chu kỳ phách giữa chu kỳ hành tinh và nhịp đo 29.4 phút"
               if timing["cadence_alias"] else "")
        if phase_biased:
            why += ("; " if why else "") + f"O−C đổi theo vị trí tâm transit trong lưới đo (p = {timing['cadence_p']:.1e})"
        return f"O−C có chu kỳ ~{timing['ls_period']:.1f} vòng (FAP = {timing['fap']:.1e}) nhưng {why} → **lỗi đo, không phải TTV**"
    if timing["fap"] < 0.001 and timing["halves_agree"] is False:
        return (
            f"O−C có chu kỳ ~{timing['ls_period']:.1f} vòng (FAP = {timing['fap']:.1e}) nhưng **không lặp lại ở cả hai nửa "
            "dữ liệu** → nhiều khả năng là nhiễu (nhiễu đỏ, vết đen sao), không phải TTV"
        )
    if timing["fap"] < 0.001:
        return (
            f"⚠️ O−C có chu kỳ ~{timing['ls_period']:.1f} vòng (FAP = {timing['fap']:.1e}), có ở cả hai nửa dữ liệu, không giải "
            "thích được bằng lưới đo: cần loại trừ hành tinh khác, vết đen sao trước khi nghĩ tới vệ tinh"
        )
    return f"Không thấy TTV có chu kỳ (FAP = {timing['fap']:.2f})"


def compare_moons(r_earth):
    """Đặt giới hạn cạnh các vật quen thuộc: vật to hơn giới hạn đã bị loại, vật nhỏ hơn thì chưa."""
    ruled_out = [name for name, r in REFERENCE_MOONS if r > r_earth]
    allowed = [name for name, r in REFERENCE_MOONS if r <= r_earth]
    parts = []
    if ruled_out:
        parts.append(f"đã loại vật cỡ {ruled_out[0]} trở lên")
    if allowed:
        parts.append(f"chưa loại được vật cỡ {allowed[-1]}")
    return "; ".join(parts) if parts else "không loại được vật cỡ nào trong danh sách"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='Tên đã dùng ở bước 1–2, ví dụ "Kepler-10"')
    args = parser.parse_args()

    name = analyze.slug(args.target)
    system = json.loads((OUT_DIR / f"{name}_system.json").read_text(encoding="utf-8"))
    star = system["star"]
    data = np.loadtxt(CSV_DIR / f"{name}_all_flat.csv", delimiter=",", skiprows=1)
    t, flux, err = data[:, 0], data[:, 1], data[:, 2]
    cadence = float(np.median(np.diff(t)))  # nhịp đo thật: 29.4244 phút (khác một chút so với thời gian phơi sáng)
    planets = [p for p in system["planets"] if p.get("rp_rs") and p.get("t14_days")]
    if not planets:
        raise SystemExit("Không có hành tinh nào có transit đã khớp mô hình. Chạy lại 02_analyze.py (bản mới).")

    results = []
    for p in planets:
        print(f"{p['name']}:")
        others = np.zeros_like(t, dtype=bool)
        for q in planets:
            if q is not p:
                others |= np.abs(analyze.phase_fold(t, q["period_days"], q["t0_bkjd"])) < q["t14_days"] * 0.75
        zone = moon_zone(p, star)
        timing = time_transits(t[~others], flux[~others], err[~others], p, cadence)
        ttv = ttv_mass_limit(timing, zone) if timing else None
        ose = ose_limit(t, flux, p, zone, star, timing, others)
        results.append((p, zone, timing, ttv, ose))
        print(
            f"  Vùng vệ tinh: Roche {zone['roche'] / 1e3:,.0f} km → {zone['a_max'] / 1e3:,.0f} km (0.49 R_Hill)"
            + ("" if zone["possible"] else " → KHÔNG có quỹ đạo vệ tinh bền")
        )
        if timing:
            print(
                f"  TTV: {timing['n_used']} transit (loại {timing['n_clipped']} ngoại lai), sai số mỗi lần {timing['sigma_mean'] * 1440:.1f} phút, "
                f"O−C rms {timing['rms'] * 1440:.1f} phút, χ²_red {timing['chi2_red']:.2f}"
            )
        if ose:
            print(f"  OSE: vai trũng {ose['deficit'] * 1e6:.1f} ± {ose['sigma'] * 1e6:.1f} ppm → R_vệ tinh < {ose['r_lim']:.2f} R⊕")

        slug_p = analyze.slug(p["name"])
        if timing:
            with open(CSV_DIR / f"{name}_{slug_p}_transit_times.csv", "w", encoding="utf-8") as f:
                f.write("epoch,tc_bkjd,sigma_min,oc_min,used\n")  # used = 0: transit ngoại lai bị loại
                for row in zip(timing["epoch"], timing["tc"], timing["sigma"], timing["oc"], timing["used"]):
                    f.write(f"{row[0]},{row[1]:.6f},{row[2] * 1440:.3f},{row[3] * 1440:.3f},{int(row[4])}\n")
        if ose:
            with open(CSV_DIR / f"{name}_{slug_p}_ose_profile.csv", "w", encoding="utf-8") as f:
                f.write("hours_from_mid_transit,flux_binned,n_points\n")
                for h, fl, cnt in ose["profile"]:
                    f.write(f"{h:.4f},{fl:.7f},{cnt}\n")

    # ---- Biểu đồ: mỗi hành tinh 1 hàng, trái O−C, phải vùng vai OSE ----
    fig, axes = plt.subplots(len(results), 2, figsize=(13, 3.6 * len(results)), squeeze=False)
    for (p, zone, timing, ttv, ose), (ax_ttv, ax_ose) in zip(results, axes):
        if timing:
            used = timing["used"]
            ax_ttv.errorbar(timing["epoch"][used], timing["oc"][used] * 1440, yerr=timing["sigma"][used] * 1440, fmt="o",
                            ms=3, color="black", ecolor="gray", alpha=0.7 if used.sum() < 200 else 0.25)
            if (~used).any():
                ax_ttv.scatter(timing["epoch"][~used], timing["oc"][~used] * 1440, marker="x", color="crimson",
                               label="ngoại lai, đã loại")
                ax_ttv.legend(fontsize=8)
            spread = 6 * max(timing["rms"], timing["sigma_mean"]) * 1440
            ax_ttv.set_ylim(-spread, spread)
            ax_ttv.axhline(0, color="crimson", lw=0.8)
            ax_ttv.set_title(f"{p['name']}: O−C (χ²_red = {timing['chi2_red']:.2f})", fontsize=10)
        else:
            ax_ttv.text(0.5, 0.5, "Không định thời được từng transit", ha="center", transform=ax_ttv.transAxes)
            ax_ttv.set_title(p["name"], fontsize=10)
        ax_ttv.set_xlabel("Số thứ tự transit")
        ax_ttv.set_ylabel("O − C (phút)")
        if ose:
            h, fl, _ = zip(*ose["profile"])
            h, dip = np.array(h), (1 - np.array(fl)) * 1e6
            ax_ose.scatter(h, dip, s=8, color="black")
            # Trục dọc co theo phần ngoài transit hành tinh; đáy transit hành tinh tràn khỏi khung là bình thường
            outside = dip[np.abs(h) > ose["inner"] * 24]
            pad = 0.2 * (outside.max() - outside.min())
            ax_ose.set_ylim(outside.min() - pad, outside.max() + pad)
            for lo, hi, color in [(ose["inner"], ose["outer"], "#2ca02c"), (ose["base_in"], ose["base_out"], "#999999")]:
                for sign in (-1, 1):
                    ax_ose.axvspan(sign * lo * 24, sign * hi * 24, color=color, alpha=0.15)
            ax_ose.invert_yaxis()
            ax_ose.set_title(f"Vai vệ tinh (xanh) so với nền (xám): R_vệ tinh < {ose['r_lim']:.2f} R⊕", fontsize=10)
        else:
            ax_ose.text(0.5, 0.5, "Vùng vệ tinh nằm gọn trong transit hành tinh\n→ OSE không tách ra được",
                        ha="center", va="center", transform=ax_ose.transAxes)
            ax_ose.set_axis_off()
        ax_ose.set_xlabel("Giờ tính từ tâm transit")
        ax_ose.set_ylabel("Độ trũng (ppm)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"{name}_moons.png", dpi=110)
    plt.close()

    # ---- Báo cáo ----
    lines = [f"# Tìm vệ tinh quanh các hành tinh của {args.target}", ""]
    lines.append(
        "Light curve Kepler chỉ đặt được **giới hạn trên**: vệ tinh lớn/nặng hơn mức này đã bị loại. "
        "Giả định vệ tinh đá (mật độ 3 g/cm³), quỹ đạo tròn, cùng chiều; giới hạn tính cho vệ tinh ở xa nhất "
        "có thể (0.49 bán kính Hill), nơi tín hiệu lớn nhất."
    )
    lines += ["", "| Thông số | " + " | ".join(p["name"] for p, *_ in results) + " |", "|---|" + "---|" * len(results)]

    def row(label, getter):
        cells = []
        for item in results:
            try:
                cells.append(getter(*item))
            except (TypeError, KeyError):
                cells.append("—")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    row("Khối lượng hành tinh dùng (M⊕)", lambda p, z, *_: f"{z['mp'] / M_EARTH:.1f}" + ("" if z["mass_measured"] else " (ước tính từ bán kính)"))
    row("Bán kính Hill (km)", lambda p, z, *_: f"{z['hill'] / 1e3:,.0f}")
    row("Quỹ đạo vệ tinh xa nhất bền vững, 0.49 R_Hill (km)", lambda p, z, *_: f"{z['a_max'] / 1e3:,.0f}")
    row("Giới hạn Roche (km)", lambda p, z, *_: f"{z['roche'] / 1e3:,.0f}")
    row("**Vệ tinh có thể tồn tại?**", lambda p, z, *_: "✅ có" if z["possible"] else "❌ không (vùng bền nằm trong giới hạn Roche)")
    row("Chu kỳ vệ tinh dài nhất (ngày)", lambda p, z, *_: f"{z['p_moon_max']:.2f}")
    row("Vệ tinh lệch trước/sau hành tinh tối đa (giờ)", lambda p, z, *_: f"{z['dt_max'] * 24:.2f}")
    row("Số transit định thời được", lambda p, z, tm, *_: f"{tm['n_used']}" + (f" (loại {tm['n_clipped']} ngoại lai)" if tm['n_clipped'] else ""))
    row("Sai số thời điểm mỗi transit (phút)", lambda p, z, tm, *_: f"{tm['sigma_mean'] * 1440:.1f}")
    row("O−C rms (phút)", lambda p, z, tm, *_: f"{tm['rms'] * 1440:.1f}")
    row("χ²_red của O−C (≈ 1 nếu sai số đúng)", lambda p, z, tm, *_: f"{tm['chi2_red']:.2f}")
    row("Periodogram O−C: chu kỳ mạnh nhất (vòng) / FAP", lambda p, z, tm, *_: f"{tm['ls_period']:.1f} / {tm['fap']:.2g}")
    row("O−C phụ thuộc vị trí trong lưới đo 29.4 phút? (p)", lambda p, z, tm, *_: f"{tm['cadence_p']:.2g}" + (" ⚠️" if tm['cadence_p'] < 0.001 else ""))
    row("Chu kỳ O−C lặp lại ở cả 2 nửa dữ liệu?", lambda p, z, tm, *_: {True: "có", False: "không"}[tm['halves_agree']])
    row("Kết luận TTV", lambda p, z, tm, *_: verdict_ttv(tm))
    row("Giới hạn TTV rms = O−C rms (phút)", lambda p, z, tm, ttv, _: f"{ttv[0] / 60:.1f}")
    row("**Khối lượng vệ tinh tối đa (từ TTV)**", lambda p, z, tm, ttv, _: f"{ttv[1] / M_EARTH:.3g} M⊕ = {ttv[1] / M_MOON:.3g} lần Mặt Trăng")
    row("Vai trũng OSE (ppm)", lambda p, z, tm, ttv, o: f"{o['deficit'] * 1e6:.1f} ± {o['sigma'] * 1e6:.1f}")
    row("**Bán kính vệ tinh tối đa (từ OSE)**", lambda p, z, tm, ttv, o: f"{o['r_lim']:.2f} R⊕: {compare_moons(o['r_lim'])}")
    lines += [
        "",
        "Ghi chú:",
        "- **TTV** ở đây là độ lệch thời điểm so với chu kỳ đều. TTV đáng kể có thể do hành tinh khác kéo, vết đen "
        "trên sao, nhiễu đỏ... chứ không nhất thiết là vệ tinh.",
        "- Vệ tinh gần hành tinh hơn a_max thì TTV nhỏ hơn (tỉ lệ với khoảng cách), nên giới hạn khối lượng yếu đi tương ứng.",
        "- **OSE** giả định nhiễu trắng; nhiễu đỏ làm giới hạn thực tế kém hơn. Một tín hiệu \"vai\" dương cũng có thể là do "
        "bước làm phẳng light curve.",
        "- Hành tinh quá gần sao: bán kính Hill nhỏ, vệ tinh còn bị thủy triều kéo dần vào hành tinh hoặc văng ra trong "
        "thời gian ngắn hơn tuổi hệ (Barnes & O'Brien 2002), nên khó tồn tại kể cả khi nằm trong vùng bền.",
    ]
    report = "\n".join(lines) + "\n"
    (OUT_DIR / f"{name}_moons.md").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"Biểu đồ: {OUT_DIR / f'{name}_moons.png'}")


if __name__ == "__main__":
    main()
