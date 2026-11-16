"""Bước 6: phổ JWST / HST đã công bố của các hành tinh bị tranh cãi, tự kiểm tra lại bằng thống kê đơn giản.

Các hệ bị tranh cãi (docs/khi-quyen-va-tuong-lai.md, mục 3) phần lớn không có dữ liệu Kepler, nên không chạy được
bước 1–5. Bước này lấy thẳng số liệu phổ đã công bố trên NASA Exoplanet Archive và làm 4 việc:

    1. Tải điểm phổ truyền qua (bảng transitspec) và phổ nhật thực phụ (bảng emissionspec) qua TAP.
       Ghi chú: bảng mới `spectra` có thêm các phổ JWST 2023–2026 (K2-18 b, TRAPPIST-1 e/f, LHS 1140 b, 55 Cnc e,
       GJ 1132 b), nhưng file số liệu của nó chỉ tải được qua nút "Download All Checked Spectra" trên web, không qua TAP.
       Script vẫn liệt kê các phổ đó (metadata) để biết còn thiếu gì.
    2. Phép thử "đường phẳng": nếu hành tinh là đá trần hoặc mây che kín thì phổ truyền qua phẳng. Tính χ² của dữ liệu
       so với một đường thẳng nằm ngang (độ sâu trung bình có trọng số) → xác suất p → quy ra σ.
       p nhỏ (σ lớn) = phổ có cấu trúc thật SỰ khác phẳng (do khí quyển, HOẶC do vết trên sao, HOẶC sai số bị đánh giá thấp).
    3. So sánh các bộ phổ của cùng một hành tinh (khác nhóm phân tích, khác pipeline, khác lần quan sát): gộp bin chung
       0.1 μm trên vùng bước sóng chồng nhau, bỏ chênh lệch mức trung bình, rồi tính χ² của hiệu số. p nhỏ = 2 bộ phổ
       KHÔNG khớp nhau, tức kết luận phụ thuộc cách xử lý dữ liệu.
    4. Biên độ đặc trưng dự kiến cho khí quyển H/He, hơi nước, CO₂ (2 độ cao thang, như bước 5) so với độ chính xác
       của phổ: loại khí quyển nào đã đủ dữ liệu để loại trừ.

Không cần chạy bước 1–5. Cách chạy:
    .venv/Scripts/python scripts/06_disputed_spectra.py                 # mọi hành tinh trong DEFAULT_PLANETS
    .venv/Scripts/python scripts/06_disputed_spectra.py "K2-18 b"       # một hành tinh

Kết quả (thư mục outputs/disputed/):
    <hành tinh>_spectra.png         phổ đã công bố + vạch phân tử + biên độ dự kiến
    disputed_spectra_summary.png    phép thử đường phẳng của mọi bộ phổ, đơn vị σ
    disputed_spectra.md             báo cáo
    data/csv/disputed/<hành tinh>_spectra.csv   số liệu đã tải, mở được bằng Google Sheets
"""

import argparse
import html
import math
import re
import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import requests
from scipy import stats

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "disputed"
CSV_DIR = ROOT / "data" / "csv" / "disputed"
ARCHIVE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

DEFAULT_PLANETS = ["K2-18 b", "GJ 1132 b", "GJ 486 b", "55 Cnc e", "TRAPPIST-1 e", "TRAPPIST-1 f", "LHS 1140 b"]

K_B = 1.380649e-23
M_H = 1.6735e-27
G = 6.674e-11
R_EARTH, M_EARTH, R_SUN = 6.371e6, 5.972e24, 6.957e8
SCALE_HEIGHTS = 2
ATMOSPHERES = [("H/He (μ = 2.3)", 2.3, "#2ca02c"), ("hơi nước (μ = 18)", 18.0, "#1f77b4"), ("CO₂ (μ = 44)", 44.0, "#9467bd")]
BIN_WIDTH = 0.1  # μm, bin chung khi so 2 bộ phổ
MOLECULE_BANDS = [  # (tên, bước sóng μm): các dải hấp thụ mạnh, chỉ để định hướng khi nhìn hình
    ("H₂O", 1.15), ("H₂O", 1.4), ("H₂O", 1.9), ("H₂O", 2.7), ("CH₄", 1.7), ("CH₄", 2.3), ("CH₄", 3.3),
    ("CO₂", 4.3), ("CO", 4.6), ("SO₂", 7.3), ("CO₂", 15.0),
]


def tap(query):
    try:
        return requests.get(ARCHIVE_URL, params={"query": query, "format": "json"}, timeout=120).json()
    except Exception as exc:
        print(f"Không truy vấn được NASA Exoplanet Archive: {exc}")
        return []


def ref_parts(link):
    """Bảng NASA lưu tài liệu tham khảo dạng thẻ <a>: trả về (tên, url)."""
    if not link:
        return "không rõ nguồn", ""
    url = re.search(r"href=(\S+)", link)
    return html.unescape(re.sub(r"<[^>]+>", "", link)).strip(), (url.group(1) if url else "")


def short_facility(facility, instrument):
    f = (facility or "").lower()
    if "james webb" in f or "jwst" in f:
        tel = "JWST"
    elif "hubble" in f:
        tel = "HST"
    elif "spitzer" in f:
        tel = "Spitzer"
    elif "kepler" in f:
        tel = "Kepler"
    elif "tess" in f:
        tel = "TESS"
    else:
        tel = "mặt đất"
    inst = (instrument or "").replace("Near Infrared Spectrograph", "NIRSpec").replace("Wide Field Camera 3", "WFC3")
    inst = inst.replace("Infrared Array Camera", "IRAC").replace("Mid-Infrared Instrument", "MIRI")
    inst = inst.replace("Near Infrared Imager and Slitless Spectrograph", "NIRISS").replace("Near Infrared Camera", "NIRCam")
    inst = re.sub(r"\s*\((NIRSpec|WFC3|IRAC|MIRI|NIRISS|NIRCam)\)", "", inst)
    if inst.startswith(tel + " "):  # "Kepler Kepler CCD camera" → "Kepler CCD camera"
        inst = inst[len(tel) + 1:]
    return tel, inst


TEL_COLORS = {"JWST": "#d62728", "HST": "#1f77b4", "Spitzer": "#ff7f0e", "Kepler": "#8c564b", "TESS": "#8c564b", "mặt đất": "#7f7f7f"}


def load_datasets(planet):
    """Gom điểm phổ thành từng bộ: (loại phổ, nguồn, thiết bị). Độ sâu đổi từ % sang ppm."""
    datasets = {}
    for kind, table, dep, ref_col in [("transit", "transitspec", "plntransdep", "plntranreflink"),
                                      ("eclipse", "emissionspec", "especlipdep", "plntreflink")]:
        rows = tap(f"select centralwavelng,bandwidth,{dep},{dep}err1,{dep}err2,{dep}lim,facility,instrument,{ref_col} "
                   f"from {table} where plntname='{planet}'")
        for r in rows:
            if r.get(dep) is None or r.get(f"{dep}lim") or r.get(f"{dep}err1") is None:
                continue  # bỏ giới hạn trên/dưới và điểm không có sai số
            ref, url = ref_parts(r.get(ref_col))
            tel, inst = short_facility(r["facility"], r["instrument"])
            key = (kind, ref, tel, inst)
            ds = datasets.setdefault(key, {"kind": kind, "ref": ref, "url": url, "tel": tel, "inst": inst, "wl": [], "d": [], "e": []})
            ds["wl"].append(r["centralwavelng"])
            ds["d"].append(r[dep] * 1e4)
            ds["e"].append((abs(r[f"{dep}err1"]) + abs(r[f"{dep}err2"] or r[f"{dep}err1"])) / 2 * 1e4)
    out = []
    for ds in datasets.values():
        order = np.argsort(ds["wl"])
        for k in ("wl", "d", "e"):
            ds[k] = np.asarray(ds[k], dtype=float)[order]
        out.append(ds)
    return sorted(out, key=lambda d: (d["kind"], d["tel"], d["ref"], d["inst"]))


def flat_test(wl, depth, err):
    """χ² so với đường nằm ngang. Trả về (mức trung bình, χ²_red, p, σ tương đương)."""
    w = 1 / err**2
    mean = np.sum(w * depth) / np.sum(w)
    chi2 = float(np.sum(((depth - mean) / err) ** 2))
    dof = len(depth) - 1
    if dof < 1:
        return mean, None, None, None
    p = float(stats.chi2.sf(chi2, dof))
    sigma = float(stats.norm.isf(p)) if p > 0 else 40.0  # một phía; p = 0 do tràn số → coi như > 40σ
    return mean, chi2 / dof, p, max(sigma, 0.0)


def bin_spectrum(wl, depth, err, edges):
    idx = np.digitize(wl, edges) - 1
    bd, be = np.full(len(edges) - 1, np.nan), np.full(len(edges) - 1, np.nan)
    for i in range(len(edges) - 1):
        m = idx == i
        if m.any():
            w = 1 / err[m] ** 2
            bd[i] = np.sum(w * depth[m]) / np.sum(w)
            be[i] = 1 / math.sqrt(np.sum(w))
    return bd, be


def compare(a, b):
    """So 2 bộ phổ trên vùng chồng nhau, sau khi bỏ chênh lệch mức trung bình. None nếu chồng nhau quá ít."""
    lo, hi = max(a["wl"].min(), b["wl"].min()), min(a["wl"].max(), b["wl"].max())
    if hi - lo < 3 * BIN_WIDTH:
        return None
    edges = np.arange(lo, hi + BIN_WIDTH / 2, BIN_WIDTH)
    da, ea = bin_spectrum(a["wl"], a["d"], a["e"], edges)
    db, eb = bin_spectrum(b["wl"], b["d"], b["e"], edges)
    ok = ~(np.isnan(da) | np.isnan(db))
    if ok.sum() < 3:
        return None
    diff, var = da[ok] - db[ok], ea[ok] ** 2 + eb[ok] ** 2
    offset = np.sum(diff / var) / np.sum(1 / var)
    chi2 = float(np.sum((diff - offset) ** 2 / var))
    dof = int(ok.sum()) - 1
    p = float(stats.chi2.sf(chi2, dof))
    return {"range": (lo, hi), "bins": int(ok.sum()), "offset": offset, "chi2_red": chi2 / dof, "p": p,
            "sigma": max(float(stats.norm.isf(p)) if p > 0 else 40.0, 0.0)}


def feature_amplitudes(params):
    """Biên độ đặc trưng phổ truyền qua (ppm) = 2·n·H·Rp/Rs², H = kT/(μ m_H g)."""
    rp, mp, rs, teq = (params.get(k) for k in ("pl_rade", "pl_bmasse", "st_rad", "pl_eqt"))
    if not (rp and mp and rs and teq):
        return {}
    g = G * mp * M_EARTH / (rp * R_EARTH) ** 2
    out = {}
    for label, mu, _ in ATMOSPHERES:
        h = K_B * teq / (mu * M_H * g)
        out[label] = 2 * SCALE_HEIGHTS * h * rp * R_EARTH / (rs * R_SUN) ** 2 * 1e6
    return out


def expected_dchi2(amplitude, err):
    """Nếu có đặc trưng cao `amplitude` (đỉnh–đáy) phủ dải bước sóng, coi như dao động hình sin biên độ A/2:
    bình phương trung bình (A/2)²/2 → tổng χ² tăng thêm Σ (A/2)²/2/σᵢ². ≥ 9 nghĩa là bộ phổ sẽ lệch phẳng ≥ 3σ."""
    return float(np.sum((amplitude / 2) ** 2 / 2 / err**2))


def slug(planet):
    return planet.replace(" ", "").replace("-", "")


def plot_planet(planet, datasets, amps, catalog):
    kinds = [k for k in ("transit", "eclipse") if any(d["kind"] == k for d in datasets)]
    if not kinds:
        return None
    fig, axes = plt.subplots(len(kinds), 1, figsize=(13, 4.8 * len(kinds)), squeeze=False)
    for ax, kind in zip(axes[:, 0], kinds):
        group = [d for d in datasets if d["kind"] == kind]
        markers = "osD^vP*X"
        for i, d in enumerate(group):
            label = f"{d['tel']} {d['inst']}: {d['ref']}"
            ax.errorbar(d["wl"] * (1 + 0.004 * (i - len(group) / 2)), d["d"], yerr=d["e"], fmt=markers[i % len(markers)],
                        ms=4, lw=0.8, alpha=0.8, color=TEL_COLORS[d["tel"]] if len(group) <= 2 else None, label=label)
        if kind == "transit" and amps:
            ref = max(group, key=lambda d: np.sum(1 / d["e"] ** 2))  # bộ chính xác nhất làm mốc
            mean = np.sum(ref["d"] / ref["e"] ** 2) / np.sum(1 / ref["e"] ** 2)
            for label, mu, color in ATMOSPHERES:
                a = amps[label]
                ax.axhspan(mean - a / 2, mean + a / 2, color=color, alpha=0.08)
                ax.axhline(mean + a / 2, color=color, ls=":", lw=1)
                ax.axhline(mean - a / 2, color=color, ls=":", lw=1,
                           label=f"dải ±{a / 2:.0f} ppm: đặc trưng nếu khí quyển {label}")
            ax.axhline(mean, color="black", lw=0.8, ls="--", label="đường phẳng (đá trần / mây dày)")
        lo = min(d["wl"].min() for d in group)
        hi = max(d["wl"].max() for d in group)
        for name, w in MOLECULE_BANDS:
            if lo * 0.9 <= w <= hi * 1.1:
                ax.axvline(w, color="#bbbbbb", lw=0.8, zorder=0)
                ax.text(w, 1.01, name, transform=ax.get_xaxis_transform(), ha="center", fontsize=8, color="#666666")
        ax.set_xscale("log")
        ticks = [t for t in (0.5, 0.7, 1, 1.5, 2, 3, 4, 5, 7, 10, 15) if lo * 0.85 <= t <= hi * 1.15]
        ax.set_xticks(ticks, [f"{t:g}" for t in ticks])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel("Bước sóng (μm)")
        ax.set_ylabel("Độ sâu transit (ppm)" if kind == "transit" else "Độ sâu nhật thực phụ (ppm)")
        ax.set_title(f"{planet}: {'phổ truyền qua' if kind == 'transit' else 'phổ phát xạ (nhật thực phụ)'}", pad=16)
        ax.legend(fontsize=7.5, loc="best")
    missing = [s for s in catalog if s["facility_short"] in ("JWST", "HST")]
    if missing:
        fig.text(0.01, -0.01, f"Bảng 'spectra' của NASA còn {len(missing)} bộ phổ JWST/HST cho hành tinh này không tải được "
                 "qua TAP (xem báo cáo).", fontsize=8, color="#666666")
    fig.tight_layout()
    path = OUT_DIR / f"{slug(planet)}_spectra.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_summary(rows):
    rows = [r for r in rows if r["sigma"] is not None]
    if not rows:
        return None
    fig, ax = plt.subplots(figsize=(13, 0.42 * len(rows) + 1.6))
    for i, r in enumerate(rows):
        s = min(r["sigma"], 12)
        ax.barh(i, s, color=TEL_COLORS[r["tel"]], alpha=0.8)
        ax.text(s + 0.1, i, f"{r['sigma']:.1f}σ" + (" (cắt ở 12)" if r["sigma"] > 12 else "") + f"  χ²_red = {r['chi2_red']:.2f}",
                va="center", fontsize=8)
    ax.set_yticks(range(len(rows)), [f"{r['planet']} | {r['tel']} {r['inst']} | {r['ref']}" for r in rows], fontsize=8)
    ax.invert_yaxis()
    for s, c, t in [(3, "#ff7f0e", "3σ: 'bằng chứng'"), (5, "#d62728", "5σ: 'phát hiện'")]:
        ax.axvline(s, color=c, ls="--")
        ax.text(s + 0.1, len(rows) - 0.5, t, color=c, fontsize=8.5, va="bottom")
    ax.set_xlim(0, 15)
    ax.set_xlabel("Phổ khác một đường phẳng bao nhiêu σ (phép thử χ²; giả định sai số công bố là đúng)")
    ax.set_title("Phép thử đường phẳng cho mọi bộ phổ tải được\ncao = có cấu trúc (khí quyển, vết trên sao, hoặc sai số bị đánh giá thấp)", fontsize=11)
    present = [t for t in TEL_COLORS if any(r["tel"] == t for r in rows)]
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=TEL_COLORS[t], alpha=0.8) for t in present], present, fontsize=8, loc="center right")
    path = OUT_DIR / "disputed_spectra_summary.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_coverage(planet, cat, datasets):
    """Mọi phổ JWST/HST/... đã công bố (bảng `spectra`): dải bước sóng, kính, tác giả; tô đậm bộ đã tải và kiểm tra được."""
    if not cat:
        return None
    used = {(d["tel"], d["ref"].split(" ")[0]) for d in datasets}
    rows = sorted(cat, key=lambda s: (s["bibcode"][:4], s["facility_short"], s["minwavelng"]))
    # gộp các bộ giống hệt nhau (nhiều lần quan sát cùng bài, cùng thiết bị) thành 1 dòng "×n"
    merged = {}
    for s in rows:
        key = (s["spec_type"], s["facility_short"], s["inst_short"], s["authors"], round(s["minwavelng"], 1), round(s["maxwavelng"], 1))
        merged.setdefault(key, [s, 0])[1] += 1
    items = list(merged.values())
    fig, ax = plt.subplots(figsize=(13, 0.38 * len(items) + 1.8))
    for i, (s, n) in enumerate(items):
        tel = s["facility_short"]
        ok = (tel, (s["authors"] or "").split(" ")[0]) in used
        lo, hi = s["minwavelng"], max(s["maxwavelng"], s["minwavelng"] * 1.03)  # điểm đơn (vd. Spitzer) vẽ thành vạch hẹp
        ax.barh(i, hi - lo, left=lo, color=TEL_COLORS[tel], alpha=0.9 if ok else 0.35, edgecolor="black" if ok else "none")
        kind = "truyền qua" if s["spec_type"] == "Transmission" else "nhật thực phụ" if s["spec_type"] == "Eclipse" else s["spec_type"]
        ax.text(hi * 1.03, i, f"{s['authors']} ({kind}, {s['num_datapoints']} điểm{', ×' + str(n) + ' bộ' if n > 1 else ''})"
                + ("  [đã kiểm tra]" if ok else ""), va="center", fontsize=8)
    ax.set_yticks(range(len(items)), [f"{s['facility_short']} {s['inst_short']}"[:38] for s, _ in items], fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ticks = [0.5, 0.7, 1, 1.5, 2, 3, 5, 8, 12, 20]
    ax.set_xticks(ticks, [f"{t:g}" for t in ticks])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlim(0.4, 150)
    for name, w in MOLECULE_BANDS:
        ax.axvline(w, color="#cccccc", lw=0.8, zorder=0)
        ax.text(w, 1.0, name, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=7.5, color="#777777")
    ax.set_xlabel("Bước sóng (μm)")
    present = [t for t in TEL_COLORS if any(s["facility_short"] == t for s, _ in items)]
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=TEL_COLORS[t]) for t in present], present, fontsize=8, loc="lower right")
    ax.set_title(f"{planet}: mọi phổ đã công bố trên NASA Exoplanet Archive (đậm, viền đen = số liệu tải được và đã kiểm tra ở bước 6)", pad=18)
    path = OUT_DIR / f"{slug(planet)}_coverage.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("planets", nargs="*", default=DEFAULT_PLANETS, help='Tên hành tinh trên NASA, vd. "K2-18 b"')
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    names = ",".join(f"'{p}'" for p in args.planets)
    params = {r["pl_name"]: r for r in tap(f"select pl_name,pl_rade,pl_bmasse,pl_eqt,st_rad,st_teff,sy_dist from pscomppars where pl_name in ({names})")}
    catalog = tap(f"select pl_name,spec_type,facility,instrument,num_datapoints,minwavelng,maxwavelng,authors,bibcode "
                  f"from spectra where pl_name in ({names})")
    for s in catalog:
        s["facility_short"], s["inst_short"] = short_facility(s["facility"], s["instrument"])

    summary, report = [], []
    for planet in args.planets:
        print(f"=== {planet}")
        datasets = load_datasets(planet)
        par = params.get(planet, {})
        amps = feature_amplitudes(par)
        cat = [s for s in catalog if s["pl_name"] == planet]
        with open(CSV_DIR / f"{slug(planet)}_spectra.csv", "w", encoding="utf-8") as f:
            f.write("loai,kinh,thiet_bi,nguon,buoc_song_um,do_sau_ppm,sai_so_ppm\n")
            for d in datasets:
                for w, dep, e in zip(d["wl"], d["d"], d["e"]):
                    f.write(f"{d['kind']},{d['tel']},\"{d['inst']}\",\"{d['ref']}\",{w:.4f},{dep:.2f},{e:.2f}\n")
        fig_path = plot_planet(planet, datasets, amps, cat)

        report += ["", f"## {planet}", ""]
        if par:
            report.append(f"Bán kính {par.get('pl_rade') or '?'} R⊕, khối lượng {par.get('pl_bmasse') or '?'} M⊕, "
                          f"Teq {par.get('pl_eqt') or '?'} K, sao {par.get('st_rad') or '?'} R☉ / {par.get('st_teff') or '?'} K, "
                          f"cách {par.get('sy_dist') or '?'} pc (NASA `pscomppars`).")
        if amps:
            report += ["", "Biên độ đặc trưng phổ truyền qua dự kiến (2 độ cao thang, khí quyển trong không mây): "
                       + ", ".join(f"{k} **{v:.0f} ppm**" for k, v in amps.items()) + "."]
        if fig_path:
            report += ["", f"![{planet}]({fig_path.name})"]
        cov_path = plot_coverage(planet, cat, datasets)
        if cov_path:
            report += ["", f"![{planet}: các phổ đã công bố]({cov_path.name})"]

        if datasets:
            report += ["", "**Phép thử đường phẳng** (từng bộ phổ tải được qua TAP):", "",
                       "| Loại | Kính / thiết bị | Nguồn | Số điểm | Bước sóng (μm) | Sai số trung vị (ppm) | χ²_red | p | Khác phẳng | So với biên độ dự kiến |",
                       "|---|---|---|---|---|---|---|---|---|---|"]
            for d in datasets:
                mean, chi2_red, p, sigma = flat_test(d["wl"], d["d"], d["e"])
                med_err = float(np.median(d["e"]))
                verdict = ""
                if d["kind"] == "transit" and amps and len(d["wl"]) >= 5:
                    parts = []
                    for k, v in amps.items():
                        dchi2 = expected_dchi2(v, d["e"])
                        name_k = k.split(" (")[0]
                        if dchi2 < 9:
                            parts.append(f"{name_k}: không đủ nhạy")
                        elif sigma is not None and sigma < 3:
                            parts.append(f"{name_k}: **loại** (nếu không mây)")
                        else:
                            parts.append(f"{name_k}: khớp được")
                    verdict = "; ".join(parts)
                sig_txt = "—" if sigma is None else (f"**{sigma:.1f}σ**" if sigma >= 3 else f"{sigma:.1f}σ")
                report.append(
                    f"| {'truyền qua' if d['kind'] == 'transit' else 'nhật thực phụ'} | {d['tel']} {d['inst']} | "
                    f"[{d['ref']}]({d['url']}) | {len(d['wl'])} | {d['wl'].min():.2f}–{d['wl'].max():.2f} | {med_err:.0f} | "
                    f"{'—' if chi2_red is None else f'{chi2_red:.2f}'} | {'—' if p is None else f'{p:.2g}'} | {sig_txt} | {verdict} |")
                summary.append({"planet": planet, "tel": d["tel"], "inst": d["inst"], "ref": d["ref"], "sigma": sigma, "chi2_red": chi2_red})

            pairs = []
            trans = [d for d in datasets if d["kind"] == "transit"]
            for i in range(len(trans)):
                for j in range(i + 1, len(trans)):
                    c = compare(trans[i], trans[j])
                    if c:
                        pairs.append((trans[i], trans[j], c))
            if pairs:
                report += ["", "**Các bộ phổ có khớp nhau không?** (bin chung 0.1 μm trên vùng chồng nhau, đã bỏ chênh lệch mức trung bình):", "",
                           "| Bộ A | Bộ B | Vùng chồng (μm) | Số bin | Chênh mức trung bình (ppm) | χ²_red | p | Kết luận |",
                           "|---|---|---|---|---|---|---|---|"]
                for a, b, c in pairs:
                    verdict = "**không khớp** (> 3σ)" if c["sigma"] >= 3 else "khớp trong sai số"
                    report.append(f"| {a['tel']} {a['inst']}, {a['ref']} | {b['tel']} {b['inst']}, {b['ref']} | "
                                  f"{c['range'][0]:.2f}–{c['range'][1]:.2f} | {c['bins']} | {c['offset']:+.0f} | {c['chi2_red']:.2f} | "
                                  f"{c['p']:.2g} | {verdict} ({c['sigma']:.1f}σ) |")
        else:
            report += ["", "Không có điểm phổ nào tải được qua TAP (bảng `transitspec`, `emissionspec`)."]

        if cat:
            report += ["", "**Mọi phổ đã công bố trong bảng `spectra` của NASA** (✅ = có số liệu tải được qua TAP và đã dùng ở trên):", "",
                       "| Loại | Kính / thiết bị | Bước sóng (μm) | Số điểm | Tác giả | bibcode | Dùng? |", "|---|---|---|---|---|---|---|"]
            used = {(d["tel"], d["ref"].split(" et al")[0].split(" ")[0]) for d in datasets}
            for s in sorted(cat, key=lambda s: (s["bibcode"], s["instrument"])):
                first_author = (s["authors"] or "").split(" et al")[0].split(" ")[0]
                mark = "✅" if (s["facility_short"], first_author) in used else "—"
                report.append(f"| {s['spec_type']} | {s['facility_short']} {s['inst_short']} | {s['minwavelng']:.2f}–{s['maxwavelng']:.2f} | "
                              f"{s['num_datapoints']} | {s['authors']} | [{s['bibcode']}](https://ui.adsabs.harvard.edu/abs/{s['bibcode']}) | {mark} |")
        print(f"  {len(datasets)} bộ phổ tải được, {len(cat)} bộ trong bảng spectra")

    sum_path = plot_summary(summary)
    head = [
        "# Phổ JWST / HST của các hành tinh bị tranh cãi: tự kiểm tra lại",
        "",
        "Tạo bởi `scripts/06_disputed_spectra.py`. Số liệu: NASA Exoplanet Archive, bảng `transitspec`, `emissionspec` "
        "(điểm phổ, tải qua TAP) và `spectra` (danh mục mọi phổ đã công bố). Bối cảnh từng hệ: `docs/khi-quyen-va-tuong-lai.md`, mục 3.",
        "",
        "**Đọc kết quả thế nào:**",
        "- *Khác phẳng bao nhiêu σ*: phép thử χ² so với đường nằm ngang. Đá trần hoặc mây dày cho phổ phẳng (≈ 0σ). "
        "Số σ cao chỉ nói phổ **có cấu trúc**, không nói cấu trúc đó do khí quyển: vết trên sao, lỗi hệ thống của pipeline, "
        "hoặc sai số công bố bị đánh giá thấp đều làm σ tăng. Ngược lại χ²_red < 1 rõ rệt nghĩa là sai số công bố có thể bị đánh giá cao.",
        "- *So với biên độ dự kiến*: nếu hành tinh có khí quyển loại đó (trong, không mây), bộ phổ lẽ ra phải lệch phẳng ≥ 3σ "
        "(ước tính: đặc trưng cao 2 độ cao thang, coi như dao động hình sin phủ dải bước sóng). "
        "\"Không đủ nhạy\" = sai số quá lớn để nói gì. \"Loại\" = đủ nhạy mà phổ vẫn phẳng, nên khí quyển trong loại đó bị loại "
        "(mây dày vẫn có thể giấu nó). \"Khớp được\" = đủ nhạy và phổ có cấu trúc, nhưng chưa chắc cấu trúc do khí quyển.",
        "- *Các bộ phổ có khớp nhau không*: cùng một hành tinh mà 2 nhóm / 2 pipeline / 2 lần quan sát cho kết quả lệch nhau "
        "quá sai số thì mọi kết luận dựa trên chỉ một bộ đều đáng ngờ.",
        "",
        "**Giới hạn:** các phổ JWST mới nhất của K2-18 b (2023, 2025), TRAPPIST-1 e/f, LHS 1140 b, 55 Cnc e, GJ 1132 b "
        "có trong danh mục `spectra` nhưng số liệu không tải được qua TAP, nên chưa được kiểm tra ở đây (đánh dấu — trong bảng danh mục). "
        "Ứng viên vệ tinh Kepler-1625 b-i dựa trên 1 transit HST năm 2017 (quang trắc, không phải phổ), không nằm trong các bảng này.",
    ]
    if sum_path:
        head += ["", f"![Tổng hợp phép thử đường phẳng]({sum_path.name})"]
    (OUT_DIR / "disputed_spectra.md").write_text("\n".join(head + report) + "\n", encoding="utf-8")
    print(f"Báo cáo: {OUT_DIR / 'disputed_spectra.md'}")


if __name__ == "__main__":
    main()
