"""Bước 7: sơ đồ hệ cho các hệ bị tranh cãi (docs/khi-quyen-va-tuong-lai.md, mục 3), kể cả hành tinh đã bị bác.

Các hệ này phần lớn không có dữ liệu Kepler nên không chạy được bước 1–2 để tạo <sao>_system.json. Bước này dựng
system.json từ NASA Exoplanet Archive (bảng pscomppars: các hành tinh đã xác nhận) rồi THÊM các hành tinh từng được
công bố nhưng đã bị bác ("refuted", vẽ xám chấm chấm, dấu ✗) hoặc còn là ứng viên ("candidate", dấu ?), lấy thông số
từ chính bài báo đã công bố chúng. Sau đó vẽ bằng hàm draw_diagram của bước 3, nên hình cùng kiểu với các hệ Kepler.

Bán kính hành tinh chỉ có khối lượng (đo bằng vận tốc xuyên tâm) được ước tính từ khối lượng (Chen & Kipping 2017,
dạng rút gọn) và vẽ mờ, ghi "(ước tính)". Vị trí trên quỹ đạo của hành tinh không có transit là tùy ý.

Không cần chạy bước nào trước. Cách chạy:
    .venv/Scripts/python scripts/07_disputed_systems.py                  # mọi hệ trong SYSTEMS
    .venv/Scripts/python scripts/07_disputed_systems.py "GJ 581"         # một hệ
    thêm --date 2026-11-16 để cố định ngày vẽ vị trí hành tinh

Kết quả: outputs/disputed/<hệ>_diagram.png, outputs/disputed/<hệ>_system.json, outputs/disputed/disputed_systems.md
"""

import argparse
import importlib
import json
import math
import sys
from pathlib import Path

import requests
from astropy.time import Time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
diagram = importlib.import_module("03_diagram")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "disputed"
ARCHIVE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
BKJD_OFFSET = 2454833.0
ALBEDO = 0.3

# Mỗi hệ: tên trên NASA (None nếu NASA không có hành tinh xác nhận nào), thông số sao tự nhập khi NASA không có,
# hành tinh thêm vào (bị bác / ứng viên) và ghi chú hiện ở chân hình. Thông số hành tinh thêm vào lấy từ bài công bố:
# a (AU), P (ngày), khối lượng tối thiểu M sin i (M⊕) hoặc bán kính ước tính (R⊕).
SYSTEMS = {
    "GJ 581": {
        "host": "GJ 581",
        "extra": [
            {"name": "GJ 581 g", "status": "refuted", "a_au": 0.146, "period_days": 36.6, "mass_earth": 3.1},
            {"name": "GJ 581 d", "status": "refuted", "a_au": 0.218, "period_days": 66.6, "mass_earth": 6.1},
            {"name": "GJ 581 f", "status": "refuted", "a_au": 0.758, "period_days": 433, "mass_earth": 7.0},
        ],
        "notes": ["✗ d (Udry 2007), g, f (Vogt 2010): Robertson et al. 2014 cho thấy d và g là tín hiệu do hoạt động của sao "
                  "(sao tự quay 130 ngày; d ≈ P_rot/2); f không được dữ liệu HARPS xác nhận. b, c, e vẫn là hành tinh thật."],
    },
    "Kapteyn's star": {
        "host": "Kapteyn",
        "refute": {"Kapteyn c": "refuted"},
        "extra": [{"name": "Kapteyn b", "status": "refuted", "a_au": 0.168, "period_days": 48.6, "mass_earth": 4.8}],
        "notes": ["✗ b (trong vùng có thể sống) và c (Anglada-Escudé et al. 2014): Robertson et al. 2015 và Bortle et al. 2021 "
                  "cho thấy cả hai là tín hiệu do hoạt động của sao. NASA vẫn còn liệt kê Kapteyn c."],
    },
    "Barnard's star": {
        "host": "Barnard's star",
        "extra": [{"name": "Barnard b (2018)", "label": "b 2018", "status": "refuted", "a_au": 0.404, "period_days": 232.8, "mass_earth": 3.2}],
        "notes": ["✗ 'b 2018' (Ribas et al. 2018, siêu Trái Đất lạnh 233 ngày): Lubin et al. 2021, do hoạt động sao + alias 1 năm.",
                  "b, c, d, e (González Hernández et al. 2024; Basant et al. 2025): 4 hành tinh rất nhỏ, quá nóng, đã xác nhận."],
    },
    "Proxima Centauri": {
        "host": "Proxima Cen",
        "extra": [{"name": "Proxima Cen c", "status": "candidate", "a_au": 1.49, "period_days": 1928, "mass_earth": 7.0}],
        "notes": ["? c (Damasso et al. 2020, chu kỳ ~5 năm): tín hiệu RV yếu, chu kỳ gần bằng thời gian quan sát, chưa được nhóm độc lập xác nhận."],
    },
    "Alpha Centauri A": {
        "host": None,
        "star": {"teff": 5790, "radius_rsun": 1.22, "lum_lsun": 1.52, "distance_pc": 1.347},
        "extra": [{"name": "α Cen A S1", "label": "S1", "status": "candidate", "a_au": 1.6, "period_days": 900, "radius_earth": 11.2}],
        "notes": ["? S1 (Sanghi, Beichman et al. 2025): chấm sáng JWST MIRI 8/2024, chưa thấy lại (2/2025, 4/2025). "
                  "Quỹ đạo e ≈ 0,4, chu kỳ 2–3 năm, cỡ khí khổng lồ: a và bán kính ở đây là giá trị minh họa trong khoảng bài báo đưa ra."],
    },
    "Alpha Centauri B": {
        "host": None,
        "star": {"teff": 5260, "radius_rsun": 0.863, "lum_lsun": 0.50, "distance_pc": 1.347},
        "extra": [{"name": "α Cen Bb", "label": "Bb", "status": "refuted", "a_au": 0.04, "period_days": 3.236, "mass_earth": 1.13}],
        "notes": ["✗ Bb (Dumusque et al. 2012, Nature): Rajpaul et al. 2016 cho thấy tín hiệu sinh ra từ lịch quan sát (window function). "
                  "Hiện không có hành tinh nào được xác nhận quanh α Cen B."],
    },
    "Fomalhaut": {
        "host": None,
        "star": {"teff": 8590, "radius_rsun": 1.84, "lum_lsun": 16.6, "distance_pc": 7.70},
        "extra": [{"name": "Fomalhaut b", "status": "refuted", "a_au": 177, "period_days": 1700 * 365.25, "radius_earth": 11.2}],
        "notes": ["✗ b (Kalas et al. 2008, ảnh HST): Gáspár & Rieke 2020: chấm sáng nở to và mờ dần, là đám bụi từ va chạm, không phải hành tinh. "
                  "Vùng có thể sống tính theo công thức cho sao ≤ 7200 K nên chỉ là gần đúng (Fomalhaut 8590 K)."],
    },
    "K2-18": {
        "host": "K2-18",
        "notes": ["b: sub-Neptune 8,6–8,9 M⊕ trong vùng có thể sống. CH₄, CO₂ (JWST 2023) khá vững; DMS/DMDS 'dấu hiệu sự sống' "
                  "(~3σ, 2025) bị nhiều phân tích độc lập bác là không đủ bằng chứng. Phổ: outputs/disputed/K218b_spectra.png."],
    },
    "TRAPPIST-1": {
        "host": "TRAPPIST-1",
        "notes": ["e, f (vùng có thể sống): JWST loại khí quyển giàu H₂ (e: 2025, f: 2026); khí quyển N₂ kiểu Trái Đất hay đá trần "
                  "vẫn chưa phân biệt được. Chương trình JWST 15 transit của e: tới 11/2026 chưa công bố kết quả."],
    },
    "LHS 1140": {
        "host": "LHS 1140",
        "notes": ["b: siêu Trái Đất trong vùng có thể sống. JWST 2024 (Cadieux et al.) loại khí quyển H₂ dày, gợi ý tạm thời có N₂; chưa xác nhận."],
    },
    "GJ 1132": {
        "host": "GJ 1132",
        "notes": ["b: HST 2021 (Swain et al.) tuyên bố khí quyển núi lửa; nhóm khác cùng dữ liệu ra phổ phẳng; JWST 2023: 2 lần transit "
                  "cho 2 kết quả khác nhau; 2025: nhiều khả năng đá trần. Phổ: outputs/disputed/GJ1132b_spectra.png."],
    },
    "GJ 486": {
        "host": "GJ 486",
        "notes": ["b: JWST 2023 (Moran et al.) thấy tín hiệu hơi nước, nhưng có thể do vết lạnh trên sao. Phổ: outputs/disputed/GJ486b_spectra.png."],
    },
    "55 Cancri": {
        "host": "55 Cnc",
        "notes": ["e: hành tinh dung nham ~2.000 °C. JWST 2024 (Hu et al.) có dấu hiệu khí quyển thứ cấp CO/CO₂; độ sâu nhật thực thay đổi "
                  "giữa các lần đo. Hoàn toàn không thể có sự sống. Phổ: outputs/disputed/55Cnce_spectra.png."],
    },
    "Kepler-1625": {
        "host": "Kepler-1625",
        "notes": ["b: ứng viên vệ tinh cỡ Sao Hải Vương Kepler-1625 b-i (Teachey & Kipping 2018), đang tranh cãi (Heller & Hippke 2024). "
                  "Pipeline repo: outputs/Kepler1625_report.md, _moons.md."],
    },
    "Kepler-1708": {
        "host": "Kepler-1708",
        "notes": ["b: ứng viên vệ tinh ~2,6 R⊕ Kepler-1708 b-i (Kipping et al. 2022), đang tranh cãi. Pipeline repo: outputs/Kepler1708_report.md, _moons.md."],
    },
}


def tap(query):
    try:
        return requests.get(ARCHIVE_URL, params={"query": query, "format": "json"}, timeout=120).json()
    except Exception as exc:
        print(f"Không truy vấn được NASA Exoplanet Archive: {exc}")
        return []


def radius_from_mass(m_earth):
    """Chen & Kipping 2017 rút gọn: hành tinh đá R ∝ M^0.28 (M < 2 M⊕), sau đó R ∝ M^0.59 (tới cỡ Sao Thổ)."""
    if m_earth < 2:
        return m_earth ** 0.279
    return 2 ** 0.279 * (m_earth / 2) ** 0.589 if m_earth < 130 else 11.2


def teq(star, a_au):
    return star["teff"] * math.sqrt(star["radius_rsun"] * 0.00465 / (2 * a_au)) * (1 - ALBEDO) ** 0.25


def build_system(title, cfg):
    planets, star = [], cfg.get("star")
    if cfg.get("host"):
        rows = tap("select pl_name,pl_orbper,pl_orbsmax,pl_rade,pl_bmasse,tran_flag,pl_tranmid,st_teff,st_rad,st_lum,sy_dist "
                   f"from pscomppars where hostname='{cfg['host'].replace(chr(39), chr(39) * 2)}' order by pl_orbper")
        if not rows:
            raise SystemExit(f"NASA không có hệ {cfg['host']}")
        r0 = rows[0]
        star = star or {"teff": r0["st_teff"], "radius_rsun": r0["st_rad"], "lum_lsun": 10 ** r0["st_lum"], "distance_pc": r0["sy_dist"]}
        for r in rows:
            transiting = bool(r["tran_flag"])
            p = {"name": r["pl_name"], "a_au": r["pl_orbsmax"], "period_days": r["pl_orbper"], "transiting": transiting,
                 "radius_earth": r["pl_rade"], "radius_measured": transiting,
                 "t0_bkjd": (r["pl_tranmid"] - BKJD_OFFSET) if transiting and r["pl_tranmid"] else None}
            if cfg.get("refute", {}).get(r["pl_name"]):
                p["status"] = cfg["refute"][r["pl_name"]]
            planets.append(p)
    for e in cfg.get("extra", []):
        p = dict(e, transiting=False, t0_bkjd=None, radius_measured=False)
        p["radius_earth"] = e.get("radius_earth") or radius_from_mass(e["mass_earth"])
        planets.append(p)
    for p in planets:
        p["teq_k"] = teq(star, p["a_au"])
    planets.sort(key=lambda p: p["a_au"])
    return {"target": title, "star": star, "planets": planets, "notes": cfg.get("notes", []), "source": "NASA pscomppars + bài báo (bước 7)"}


def slug(name):
    return "".join(ch for ch in name.replace("Alpha Centauri", "AlphaCen") if ch.isalnum())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("systems", nargs="*", default=list(SYSTEMS), help="Tên hệ trong SYSTEMS")
    parser.add_argument("--date", help="Ngày vẽ vị trí hành tinh (YYYY-MM-DD), mặc định hôm nay")
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    when = Time(args.date) if args.date else Time.now()

    lines = ["# Sơ đồ các hệ bị tranh cãi", "",
             "Tạo bởi `scripts/07_disputed_systems.py` (dùng hàm vẽ của bước 3). Hành tinh đã xác nhận lấy từ NASA Exoplanet Archive "
             "(`pscomppars`); hành tinh **bị bác (✗, xám chấm chấm)** và **ứng viên (?, gạch chấm)** lấy thông số từ bài đã công bố chúng. "
             "Bán kính của hành tinh chỉ có khối lượng là ước tính (vẽ mờ). Bối cảnh: `docs/khi-quyen-va-tuong-lai.md`, mục 3.5. "
             f"Vị trí hành tinh vẽ cho ngày {when.datetime.strftime('%d/%m/%Y')}.", ""]
    for title in args.systems:
        cfg = SYSTEMS[title]
        system = build_system(title, cfg)
        name = slug(title)
        (OUT_DIR / f"{name}_system.json").write_text(json.dumps(system, ensure_ascii=False, indent=1), encoding="utf-8")
        out = diagram.draw_diagram(system, OUT_DIR / f"{name}_diagram.png", when)
        n_ref = sum(p.get("status") == "refuted" for p in system["planets"])
        n_cand = sum(p.get("status") == "candidate" for p in system["planets"])
        print(f"{title}: {len(system['planets'])} hành tinh ({n_ref} bị bác, {n_cand} ứng viên) → {out.name}")
        lines += [f"## {title}", "", *[f"- {n}" for n in system["notes"]], "", f"![{title}]({out.name})", ""]
    if len(args.systems) == len(SYSTEMS):
        (OUT_DIR / "disputed_systems.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"Báo cáo: {OUT_DIR / 'disputed_systems.md'}")


if __name__ == "__main__":
    main()
