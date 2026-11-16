"""Bước 5: khí quyển hành tinh: dữ liệu Kepler + phổ đã công bố (HST, Spitzer, JWST) + khả năng quan sát bằng JWST.

Kepler chỉ có 1 dải màu (~0.42–0.9 μm), nên không tự đo được phổ. Bước này làm 4 việc:
    1. Nhật thực phụ (secondary eclipse) trong dữ liệu Kepler: khi hành tinh khuất SAU sao, độ sáng giảm đúng
       bằng phần ánh sáng hành tinh phản xạ + phát nhiệt → albedo hình học Ag.
    2. Lấy phổ đã công bố trên NASA Exoplanet Archive (bảng transitspec, emissionspec, spectra): độ sâu transit
       theo bước sóng (phổ truyền qua) và độ sâu nhật thực phụ theo bước sóng (phổ phát xạ).
    3. Độ cao thang (scale height) H = kT/(μ m_H g) → biên độ đặc trưng phổ truyền qua cho khí quyển H/He, hơi nước,
       CO₂; so với độ chính xác của phổ đã có để biết loại khí quyển nào bị loại.
    4. Chỉ số TSM, ESM (Kempton et al. 2018): hành tinh có đáng để JWST chụp phổ không.

Cần chạy 02_analyze.py trước. Cách chạy:
    .venv/Scripts/python scripts/05_atmosphere.py "Kepler-6"

Kết quả:
    outputs/<sao>_atmosphere.png                     nhật thực phụ Kepler + phổ của từng hành tinh
    outputs/<sao>_atmosphere.md                      báo cáo
    data/csv/<sao>_<hành tinh>_eclipse.csv           nhật thực phụ gấp pha gộp bin, cho Google Sheets

Công thức xem docs/kien-thuc-exoplanet.md, mục 7.10.
"""

import argparse
import html
import importlib
import json
import math
import re
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import requests

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
analyze = importlib.import_module("02_analyze")

G, AU, DAY = analyze.G, analyze.AU, analyze.DAY
R_SUN, R_EARTH, M_EARTH = analyze.R_SUN, analyze.R_EARTH, analyze.M_EARTH
EXPOSURE = analyze.EXPOSURE
CSV_DIR, OUT_DIR, ARCHIVE_URL = analyze.CSV_DIR, analyze.OUT_DIR, analyze.ARCHIVE_URL

K_B = 1.380649e-23
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
M_H = 1.6735e-27  # khối lượng nguyên tử hydro (kg)
KEPLER_WAVELENGTH = 0.64  # μm, bước sóng hiệu dụng của dải Kepler (0.42–0.90 μm)
SCALE_HEIGHTS = 2  # đặc trưng phổ truyền qua thường cao cỡ 2 độ cao thang (quy ước thô, Kempton et al. 2018)
ATMOSPHERES = [("H/He (μ = 2.3)", 2.3), ("hơi nước (μ = 18)", 18.0), ("CO₂ (μ = 44)", 44.0)]


def planck(wavelength_um, temperature):
    lam = wavelength_um * 1e-6
    return 2 * H_PLANCK * C_LIGHT**2 / lam**5 / math.expm1(H_PLANCK * C_LIGHT / (lam * K_B * temperature))


def brightness_temperature(depth, k, wavelength_um, t_star):
    """Giải ngược Planck: độ sâu nhật thực phụ = k² · B(λ, T_hành tinh) / B(λ, T_sao). Coi sao là vật đen."""
    ratio = depth / k**2 * planck(wavelength_um, t_star)
    if ratio <= 0:
        return None
    lam = wavelength_um * 1e-6
    return H_PLANCK * C_LIGHT / (lam * K_B) / math.log1p(2 * H_PLANCK * C_LIGHT**2 / (lam**5 * ratio))


def tsm_scale(r_earth):
    """Hệ số chuẩn hóa của TSM theo nhóm bán kính (Kempton et al. 2018, bảng 1)."""
    if r_earth < 1.5:
        return 0.190
    if r_earth < 2.75:
        return 1.26
    if r_earth < 4.0:
        return 1.28
    return 1.15  # 4–10 R⊕; với khí khổng lồ > 10 R⊕ Kempton không cho hệ số, dùng tạm giá trị này


def tap(query):
    try:
        return requests.get(ARCHIVE_URL, params={"query": query, "format": "json"}, timeout=90).json()
    except Exception as exc:
        print(f"Không truy vấn được NASA Exoplanet Archive: {exc}")
        return []


def ref_text(link):
    """Bảng NASA lưu tài liệu tham khảo dạng thẻ <a>: lấy tên tác giả và đường dẫn."""
    if not link:
        return ""
    url = re.search(r"href=(\S+)", link)
    name = html.unescape(re.sub(r"<[^>]+>", "", link)).strip()
    return f"[{name}]({url.group(1)})" if url else name


def kepler_eclipse(t, flux, planet, others_mask):
    """Đo nhật thực phụ ở pha 0.5 (giả định quỹ đạo tròn) bằng hiệu trung bình ngoài và trong nhật thực."""
    period, t0, t14, k = planet["period_days"], planet["t0_bkjd"], planet["t14_days"], planet["rp_rs"]
    t23 = t14 * (1 - k) / (1 + k)  # phần đáy phẳng (hành tinh khuất hẳn sau sao), xấp xỉ khi b nhỏ
    phase = analyze.phase_fold(t, period, t0 + period / 2)
    use = ~others_mask
    ap = np.abs(phase)
    inside = use & (ap < t23 / 2)
    outer = min(t14 / 2 + max(t14, 0.1), period / 4)
    outside = use & (ap > t14 / 2 + EXPOSURE) & (ap < outer)
    if inside.sum() < 20 or outside.sum() < 20:
        return None
    depth = float(np.mean(flux[outside]) - np.mean(flux[inside]))
    sigma = float(np.std(flux[outside]) * math.sqrt(1 / inside.sum() + 1 / outside.sum()))
    span = outer
    near = use & (ap < span)
    edges = np.linspace(-span, span, 41)
    idx = np.digitize(phase[near], edges)
    profile = [
        ((edges[i - 1] + edges[i]) / 2 * 24, float(np.mean(flux[near][idx == i])), int(np.sum(idx == i)))
        for i in range(1, len(edges)) if np.sum(idx == i) >= 5
    ]
    return {"depth": depth, "sigma": sigma, "n_in": int(inside.sum()), "n_out": int(outside.sum()),
            "t23": t23, "profile": profile}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='Tên đã dùng ở bước 1–2, ví dụ "Kepler-6"')
    parser.add_argument("--host", help="Tên sao trên NASA Exoplanet Archive (mặc định = target)")
    args = parser.parse_args()

    name = analyze.slug(args.target)
    host = args.host or args.target
    system = json.loads((OUT_DIR / f"{name}_system.json").read_text(encoding="utf-8"))
    star = system["star"]
    t_star, rs = star["teff"], star["radius_rsun"] * R_SUN
    data = np.loadtxt(CSV_DIR / f"{name}_all_flat.csv", delimiter=",", skiprows=1)
    t, flux = data[:, 0], data[:, 1]
    planets = [p for p in system["planets"] if p.get("rp_rs") and p.get("t14_days")]
    if not planets:
        raise SystemExit("Không có hành tinh nào có transit đã khớp mô hình. Chạy 02_analyze.py trước.")

    mags = tap(f"select sy_jmag,sy_kmag from pscomppars where hostname='{host}'")
    j_mag = next((m["sy_jmag"] for m in mags if m.get("sy_jmag")), None)
    k_mag = next((m["sy_kmag"] for m in mags if m.get("sy_kmag")), None)
    names = ",".join(f"'{p['name']}'" for p in planets)
    trans = tap(
        "select plntname,centralwavelng,plntransdep,plntransdeperr1,plntransdeperr2,facility,instrument,plntranreflink "
        f"from transitspec where plntname in ({names})"
    )
    emis = tap(
        "select plntname,centralwavelng,especlipdep,especlipdeperr1,especlipdeperr2,espbritemp,espbritemperr1,"
        f"facility,instrument,plntreflink from emissionspec where plntname in ({names})"
    )
    spectra = tap(f"select pl_name,spec_type,authors,num_datapoints,facility,instrument,minwavelng,maxwavelng,bibcode "
                  f"from spectra where pl_name in ({names})")

    results = []
    for p in planets:
        print(f"{p['name']}:")
        others = np.zeros_like(t, dtype=bool)
        for q in planets:
            if q is not p:
                for centre in (0.0, 0.5):  # che cả transit lẫn nhật thực phụ của hành tinh khác
                    others |= np.abs(analyze.phase_fold(t, q["period_days"], q["t0_bkjd"] + centre * q["period_days"])) < q["t14_days"] * 0.75
        k, a_rs = p["rp_rs"], p["a_rs"]
        rp = p["radius_earth"] * R_EARTH
        mass_measured = p["mass_earth"] is not None
        mp = (p["mass_earth"] if mass_measured else p["mass_estimate_earth"]) * M_EARTH
        a = p["a_au"] * AU
        # Nhiệt độ cân bằng kiểu Kempton: albedo 0, nhiệt phân bố đều cả hành tinh; phía ngày nóng hơn ~10%
        t_eq0 = t_star * math.sqrt(rs / a) * 0.25**0.25
        t_day = 1.10 * t_eq0
        g = G * mp / rp**2
        heights = [(label, K_B * t_eq0 / (mu * M_H * g)) for label, mu in ATMOSPHERES]
        features = [(label, 2 * SCALE_HEIGHTS * h * rp / rs**2) for label, h in heights]
        r_e, m_e = rp / R_EARTH, mp / M_EARTH
        tsm = tsm_scale(r_e) * r_e**3 * t_eq0 / (m_e * star["radius_rsun"] ** 2) * 10 ** (-j_mag / 5) if j_mag else None
        tsm_cut = 10 if r_e < 1.5 else 90
        esm = (4.29e6 * planck(7.5, t_day) / planck(7.5, t_star) * k**2 * 10 ** (-k_mag / 5)) if k_mag else None

        eclipse = kepler_eclipse(t, flux, p, others)
        thermal_kepler = k**2 * planck(KEPLER_WAVELENGTH, t_day) / planck(KEPLER_WAVELENGTH, t_star)
        if eclipse:
            eclipse["albedo"] = eclipse["depth"] * (a_rs / k) ** 2
            eclipse["albedo_err"] = eclipse["sigma"] * (a_rs / k) ** 2
            eclipse["albedo_reflect"] = (eclipse["depth"] - thermal_kepler) * (a_rs / k) ** 2
            print(f"  Nhật thực phụ Kepler: {eclipse['depth'] * 1e6:.1f} ± {eclipse['sigma'] * 1e6:.1f} ppm → Ag = "
                  f"{eclipse['albedo']:.2f} ± {eclipse['albedo_err']:.2f}")
            with open(CSV_DIR / f"{name}_{analyze.slug(p['name'])}_eclipse.csv", "w", encoding="utf-8") as f:
                f.write("hours_from_mid_eclipse,flux_binned,n_points\n")
                for h, fl, cnt in eclipse["profile"]:
                    f.write(f"{h:.4f},{fl:.7f},{cnt}\n")

        # Phổ truyền qua: điểm Kepler tự đo (k², không có tối rìa) + các điểm đã công bố (đơn vị % → tỉ lệ)
        t_points = [(KEPLER_WAVELENGTH, k**2, None, "Kepler (tự đo, k²)", "")]
        for row in trans:
            if row["plntname"] == p["name"] and row.get("plntransdep") is not None:
                err = max(abs(row.get("plntransdeperr1") or 0), abs(row.get("plntransdeperr2") or 0)) / 100
                t_points.append((row["centralwavelng"], row["plntransdep"] / 100, err or None,
                                 row.get("facility", ""), ref_text(row.get("plntranreflink"))))
        e_points = []
        for row in emis:
            if row["plntname"] == p["name"] and row.get("especlipdep") is not None:
                err = max(abs(row.get("especlipdeperr1") or 0), abs(row.get("especlipdeperr2") or 0)) / 100
                depth = row["especlipdep"] / 100
                e_points.append({
                    "wl": row["centralwavelng"], "depth": depth, "err": err, "facility": row.get("facility", ""),
                    "ref": ref_text(row.get("plntreflink")), "tb_pub": row.get("espbritemp"),
                    "tb_pub_err": row.get("espbritemperr1"), "tb_self": brightness_temperature(depth, k, row["centralwavelng"], t_star),
                })
        # So sánh độ sâu transit giữa các bước sóng: mỗi điểm đã công bố so với điểm Kepler tự đo
        comparisons = []
        for wl, depth, err, facility, ref in t_points[1:]:
            if err and wl > 1:
                diff = depth - k**2
                verdicts = []
                for label, amp in features:
                    verdicts.append((label, amp, amp / err))
                comparisons.append({"wl": wl, "diff": diff, "err": err, "facility": facility, "ref": ref, "verdicts": verdicts})

        results.append({
            "p": p, "k": k, "t_eq0": t_eq0, "t_day": t_day, "g": g, "heights": heights, "features": features,
            "mass_measured": mass_measured, "tsm": tsm, "tsm_cut": tsm_cut, "esm": esm, "eclipse": eclipse,
            "thermal_kepler": thermal_kepler, "t_points": t_points, "e_points": e_points, "comparisons": comparisons,
            "spectra": [s for s in spectra if s["pl_name"] == p["name"]],
        })
        print(f"  H(H/He) = {heights[0][1] / 1e3:.0f} km, đặc trưng phổ ~{features[0][1] * 1e6:.1f} ppm, "
              f"TSM = {tsm if tsm is None else round(tsm, 1)}, ESM = {esm if esm is None else round(esm, 1)}")

    # ---- Biểu đồ: mỗi hành tinh 1 hàng; trái: nhật thực phụ Kepler, phải: phổ ----
    fig, axes = plt.subplots(len(results), 2, figsize=(13, 3.8 * len(results)), squeeze=False)
    for r, (ax_e, ax_s) in zip(results, axes):
        p, ecl = r["p"], r["eclipse"]
        if ecl:
            h, fl, _ = zip(*ecl["profile"])
            ax_e.scatter(h, (1 - np.array(fl)) * 1e6, s=10, color="black")
            ax_e.axhline(0, color="gray", lw=0.6)
            ax_e.axvspan(-ecl["t23"] * 12, ecl["t23"] * 12, color="#ff7f0e", alpha=0.15, label="trong nhật thực")
            ax_e.axhline(ecl["depth"] * 1e6, color="crimson", lw=1, ls="--",
                         label=f"đo được {ecl['depth'] * 1e6:.1f} ± {ecl['sigma'] * 1e6:.1f} ppm")
            ax_e.invert_yaxis()
            ax_e.legend(fontsize=8)
        else:
            ax_e.text(0.5, 0.5, "Không đủ dữ liệu quanh pha 0.5", ha="center", transform=ax_e.transAxes)
        ax_e.set_title(f"{p['name']}: nhật thực phụ trong dải Kepler", fontsize=10)
        ax_e.set_xlabel("Giờ tính từ tâm nhật thực phụ")
        ax_e.set_ylabel("Độ trũng (ppm)")

        if r["e_points"]:
            wl = np.array([e["wl"] for e in r["e_points"]])
            ax_s.errorbar(wl, [e["depth"] * 1e6 for e in r["e_points"]], yerr=[e["err"] * 1e6 for e in r["e_points"]],
                          fmt="o", color="black", label="Spitzer (đã công bố)")
            if ecl:
                ax_s.errorbar([KEPLER_WAVELENGTH], [ecl["depth"] * 1e6], yerr=[ecl["sigma"] * 1e6], fmt="s",
                              color="crimson", label="Kepler (tự đo)")
            grid = np.linspace(0.4, 6, 200)
            # (8/3)^(1/4) ≈ 1.28: phía ngày khi nhiệt không lan sang phía đêm chút nào (Cowan & Agol 2011)
            for temp, color, what in [(r["t_eq0"], "#1f77b4", "nhiệt chia đều"), (r["t_day"], "#ff7f0e", "phía ngày, Kempton"),
                                      ((8 / 3) ** 0.25 * r["t_eq0"], "#d62728", "không lan sang phía đêm")]:
                model = [r["k"] ** 2 * planck(x, temp) / planck(x, t_star) * 1e6 for x in grid]
                ax_s.plot(grid, model, color=color, lw=1, label=f"vật đen {temp:.0f} K ({what})")
            ax_s.set_ylabel("Độ sâu nhật thực phụ (ppm)")
            ax_s.set_title("Phổ phát xạ (phía ngày của hành tinh)", fontsize=10)
            ax_s.legend(fontsize=7)
        elif len(r["t_points"]) > 1:
            pts = r["t_points"]
            ax_s.errorbar([x[0] for x in pts[1:]], [x[1] * 1e6 for x in pts[1:]], yerr=[x[2] * 1e6 for x in pts[1:]],
                          fmt="o", color="black", label="đã công bố")
            ax_s.scatter([pts[0][0]], [pts[0][1] * 1e6], marker="s", color="crimson", zorder=3, label="Kepler (tự đo, k²)")
            for (label, amp), color in zip(r["features"], ["#2ca02c", "#1f77b4", "#9467bd"]):
                ax_s.axhspan((pts[0][1] - amp) * 1e6, (pts[0][1] + amp) * 1e6, color=color, alpha=0.15,
                             label=f"khí quyển {label}: ±{amp * 1e6:.0f} ppm")
            ax_s.set_ylabel("Độ sâu transit (ppm)")
            ax_s.set_title("Phổ truyền qua", fontsize=10)
            ax_s.legend(fontsize=7)
        else:
            lines = [f"Chưa có phổ HST / Spitzer / JWST nào được công bố.",
                     f"Biên độ phổ truyền qua dự kiến (2 độ cao thang):"]
            lines += [f"  {label}: {amp * 1e6:.1f} ppm" for label, amp in r["features"]]
            if r["tsm"] is not None:
                lines.append(f"TSM = {r['tsm']:.1f} (ngưỡng JWST {r['tsm_cut']})")
            if r["esm"] is not None:
                lines.append(f"ESM = {r['esm']:.1f} (ngưỡng 7.5)")
            ax_s.text(0.03, 0.95, "\n".join(lines), va="top", ha="left", fontsize=9, transform=ax_s.transAxes)
            ax_s.set_axis_off()
        ax_s.set_xlabel("Bước sóng (μm)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"{name}_atmosphere.png", dpi=110)
    plt.close()

    # ---- Báo cáo ----
    lines = [f"# Khí quyển các hành tinh của {args.target}", "",
             f"![Nhật thực phụ trong dải Kepler (trái) và phổ của từng hành tinh (phải)]({name}_atmosphere.png)", ""]
    lines.append(
        f"Sao mẹ: Teff = {t_star:.0f} K, Rs = {star['radius_rsun']:.3f} R☉, cấp sao J = {j_mag}, K = {k_mag}. "
        "Kepler chỉ có 1 dải màu nên **không tự đo được phổ**; phổ theo bước sóng lấy từ các bài báo đã công bố "
        "(NASA Exoplanet Archive, bảng `transitspec`, `emissionspec`, `spectra`)."
    )
    lines += ["", "| Thông số | " + " | ".join(r["p"]["name"] for r in results) + " |", "|---|" + "---|" * len(results)]

    def row(label, getter):
        cells = []
        for r in results:
            try:
                cells.append(getter(r))
            except (TypeError, KeyError, ValueError):
                cells.append("—")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    row("Bán kính / khối lượng dùng", lambda r: f"{r['p']['radius_earth']:.2f} R⊕ / "
        f"{(r['p']['mass_earth'] if r['mass_measured'] else r['p']['mass_estimate_earth']):.1f} M⊕"
        + ("" if r["mass_measured"] else " (ước tính)"))
    row("Nhiệt độ cân bằng (albedo 0) / phía ngày (K)", lambda r: f"{r['t_eq0']:.0f} / {r['t_day']:.0f}")
    row("Trọng lực bề mặt (m/s²)", lambda r: f"{r['g']:.1f}")
    for i, (label, _) in enumerate(ATMOSPHERES):
        row(f"Độ cao thang H, {label} (km)", lambda r, i=i: f"{r['heights'][i][1] / 1e3:.0f}")
    for i, (label, _) in enumerate(ATMOSPHERES):
        row(f"Biên độ phổ truyền qua, {label} (ppm)", lambda r, i=i: f"{r['features'][i][1] * 1e6:.1f}")
    row("**TSM** (JWST, phổ truyền qua)", lambda r: f"{r['tsm']:.1f} (ngưỡng {r['tsm_cut']}) " + ("✅" if r["tsm"] >= r["tsm_cut"] else "❌"))
    row("**ESM** (JWST, phổ phát xạ 7.5 μm)", lambda r: f"{r['esm']:.1f} (ngưỡng 7.5) " + ("✅" if r["esm"] >= 7.5 else "❌"))
    row("Nhật thực phụ Kepler (ppm)", lambda r: f"{r['eclipse']['depth'] * 1e6:.1f} ± {r['eclipse']['sigma'] * 1e6:.1f} "
        f"({r['eclipse']['depth'] / r['eclipse']['sigma']:.1f}σ)")
    row("Phần phát nhiệt dự kiến trong dải Kepler (ppm)", lambda r: f"{r['thermal_kepler'] * 1e6:.2f}")
    row("Albedo hình học Ag (cả độ sâu / trừ phần nhiệt)", lambda r: f"{r['eclipse']['albedo']:.2f} ± {r['eclipse']['albedo_err']:.2f} / "
        f"{r['eclipse']['albedo_reflect']:.2f}")
    row("Phổ đã công bố trên NASA", lambda r: str(len(r["spectra"])) + " bộ" if r["spectra"] else "chưa có")

    for r in results:
        p = r["p"]
        lines += ["", f"## {p['name']}", ""]
        if r["spectra"]:
            lines += ["**Phổ đã công bố** (bảng `spectra`):", "", "| Loại | Kính / thiết bị | Bước sóng (μm) | Số điểm | Tác giả | bibcode |", "|---|---|---|---|---|---|"]
            for s in r["spectra"]:
                lines.append(f"| {s['spec_type']} | {s['facility']} / {s['instrument']} | {s['minwavelng']}–{s['maxwavelng']} | "
                             f"{s['num_datapoints']} | {html.unescape(s['authors'])} | {s['bibcode']} |")
            lines.append("")
        else:
            lines += ["Chưa có phổ HST, Spitzer hay JWST nào được công bố cho hành tinh này.", ""]
        if r["e_points"]:
            lines += ["**Phổ phát xạ** (độ sâu nhật thực phụ theo bước sóng). Nhiệt độ độ sáng tự tính coi sao là vật đen nên "
                      "lệch chút so với bài báo (dùng mô hình phổ sao):", "",
                      "| Bước sóng (μm) | Độ sâu (ppm) | T độ sáng tự tính (K) | T độ sáng công bố (K) | Nguồn |", "|---|---|---|---|---|"]
            for e in r["e_points"]:
                tb = f"{e['tb_self']:.0f}" if e["tb_self"] else "—"
                pub = f"{e['tb_pub']:.0f} ± {e['tb_pub_err']:.0f}" if e["tb_pub"] else "—"
                lines.append(f"| {e['wl']} | {e['depth'] * 1e6:.0f} ± {e['err'] * 1e6:.0f} | {tb} | {pub} | {e['ref']} |")
            lines += ["", f"So sánh: nhiệt độ cân bằng (albedo 0, phân bố đều) {r['t_eq0']:.0f} K; phía ngày không phân bố lại nhiệt "
                      f"có thể tới ~{(8 / 3) ** 0.25 * r['t_eq0']:.0f} K. Nhiệt độ độ sáng cao hơn nhiệt độ cân bằng nghĩa là nhiệt "
                      "**không kịp lan sang phía đêm** hoặc albedo rất thấp.", ""]
        if r["comparisons"]:
            lines += ["**Phổ truyền qua** (so độ sâu transit đã công bố với k² tự đo trong dải Kepler):", "",
                      "| Bước sóng (μm) | Chênh độ sâu so với Kepler (ppm) | " + " | ".join(f"Khí quyển {lbl}: biên độ / sai số" for lbl, _ in ATMOSPHERES) + " | Nguồn |",
                      "|---|---|" + "---|" * len(ATMOSPHERES) + "---|"]
            for c in r["comparisons"]:
                cells = [f"{amp * 1e6:.0f} ppm / {ratio:.2f}σ" for _, amp, ratio in c["verdicts"]]
                lines.append(f"| {c['wl']} | {c['diff'] * 1e6:+.0f} ± {c['err'] * 1e6:.0f} | " + " | ".join(cells) + f" | {c['ref']} |")
            best = max(c["verdicts"][0][2] for c in r["comparisons"])
            lines += ["", ("Biên độ khí quyển H/He chỉ bằng "
                           f"{best:.2f} lần sai số đo: **dữ liệu hiện có không phân biệt được** có khí quyển hay không. "
                           if best < 3 else
                           "Biên độ khí quyển H/He lớn hơn 3 lần sai số: nếu chênh độ sâu nhỏ thì khí quyển H/He trong suốt bị loại "
                           "(hoặc có mây che). ") + "Cần độ chính xác cỡ vài ppm, chỉ JWST mới đạt.", ""]
        if r["eclipse"]:
            e = r["eclipse"]
            snr = e["depth"] / e["sigma"]
            lines.append(
                f"**Nhật thực phụ Kepler**: {e['depth'] * 1e6:.1f} ± {e['sigma'] * 1e6:.1f} ppm ({snr:.1f}σ, {e['n_in']} điểm trong, "
                f"{e['n_out']} điểm ngoài). " + (
                    f"Albedo hình học Ag = {e['albedo']:.2f} ± {e['albedo_err']:.2f}; trừ phần phát nhiệt dự kiến "
                    f"({r['thermal_kepler'] * 1e6:.1f} ppm) còn {e['albedo_reflect']:.2f}."
                    if snr >= 3 else
                    f"Chưa phát hiện (dưới 3σ): albedo hình học Ag < {(max(e['depth'], 0) + 3 * e['sigma']) * (p['a_rs'] / r['k']) ** 2:.2f} (giới hạn 3σ)."
                )
            )
    lines += [
        "",
        "Ghi chú:",
        "- **TSM / ESM** (Kempton et al. 2018): tín hiệu dự kiến khi chụp bằng JWST NIRISS (truyền qua) và MIRI 7.5 μm "
        "(phát xạ) trong 10 giờ. Ngưỡng đáng ưu tiên: TSM > 10 với hành tinh < 1.5 R⊕, > 90 với hành tinh lớn hơn; ESM > 7.5.",
        "- Biên độ phổ truyền qua tính bằng 2 độ cao thang, khí quyển trong suốt không mây. Mây hoặc sương mù làm phổ phẳng đi.",
        "- Nhật thực phụ giả định quỹ đạo tròn (pha 0.5). Quỹ đạo lệch tâm làm nhật thực lệch khỏi pha 0.5.",
        "- Bước làm phẳng light curve (cửa sổ ~18 ngày) không ảnh hưởng nhật thực dài vài giờ, nhưng xóa mất biến thiên "
        "theo pha quỹ đạo (phase curve).",
    ]
    report = "\n".join(lines) + "\n"
    (OUT_DIR / f"{name}_atmosphere.md").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"Biểu đồ: {OUT_DIR / f'{name}_atmosphere.png'}")


if __name__ == "__main__":
    main()
