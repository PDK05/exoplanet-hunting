"""Bước 3: vẽ sơ đồ hệ hành tinh với kích thước và khoảng cách theo thang LOGARIT.

Vì sao dùng log? Trong hệ Kepler-10, sao mẹ to gấp ~80 lần hành tinh b, còn quỹ đạo d xa gấp ~30 lần quỹ đạo b.
Vẽ đúng tỉ lệ thường thì hành tinh nhỏ hơn 1 pixel. Thang log biến "gấp 10 lần" thành "thêm 1 bậc"
nên mọi thứ cùng hiện lên được, đổi lại khoảng cách trên hình không còn tỉ lệ thuận với thực tế.

Cần chạy 02_analyze.py trước. Cách chạy:
    .venv/Scripts/python scripts/03_diagram.py "Kepler-10"
    .venv/Scripts/python scripts/03_diagram.py "Kepler-10" --date 2027-01-01   # vị trí hành tinh vào ngày khác

Kết quả: outputs/<sao>_diagram.png
"""

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from matplotlib.patches import Circle

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs"

R_SUN_AU = 0.00465  # bán kính Mặt Trời tính bằng AU
R_SUN_EARTH = 109.1  # bán kính Mặt Trời tính bằng bán kính Trái Đất
BKJD_OFFSET = 2454833.0  # BKJD = BJD − 2454833

# Hệ Mặt Trời để so sánh: (tên, bán trục lớn AU, bán kính R⊕)
SOLAR_SYSTEM = [
    ("Sao Thủy", 0.387, 0.383),
    ("Sao Kim", 0.723, 0.949),
    ("Trái Đất", 1.0, 1.0),
    ("Sao Hỏa", 1.524, 0.532),
    ("Sao Mộc", 5.203, 11.21),
]
REFERENCE_SIZES = [("Trái Đất", 1.0), ("Sao Hải Vương", 3.88), ("Sao Mộc", 11.21), ("Mặt Trời", R_SUN_EARTH)]

PLANET_COLORS = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22"]


def star_color(teff: float) -> str:
    if teff >= 7500:
        return "#cad8ff"
    if teff >= 6000:
        return "#f8f7ff"
    if teff >= 5200:
        return "#fff4c2"
    if teff >= 3700:
        return "#ffd29b"
    return "#ffb07a"


def log_size(r_earth: float) -> float:
    """Đường kính trên hình theo thang log: 1 R⊕ → 1, 10 R⊕ → 2, 100 R⊕ → 3."""
    return 1 + math.log10(max(r_earth, 0.1))


# Ngưỡng bức xạ của vùng có thể sống bảo thủ (Kopparapu et al. 2013): S = S☉ + a·T + b·T² + c·T³ + d·T⁴,
# T = Teff − 5780. Sao lạnh phát nhiều hồng ngoại, nước và CO₂ hấp thụ tốt hơn, nên ngưỡng thấp hơn sao giống Mặt Trời.
HZ_INNER = (1.0385, 1.2456e-4, 1.4612e-8, -7.6345e-12, -1.7511e-15)  # hiệu ứng nhà kính mất kiểm soát
HZ_OUTER = (0.3507, 5.9578e-5, 1.6707e-9, -3.0058e-12, -5.1925e-16)  # hiệu ứng nhà kính CO₂ cực đại


def habitable_zone(lum: float, teff: float):
    """Vùng có thể sống (nước lỏng trên bề mặt) tính bằng AU: khoảng cách = √(L / S_ngưỡng)."""
    t = min(max(teff, 2600), 7200) - 5780  # công thức chỉ dùng được cho Teff 2600–7200 K
    s_in, s_out = (sum(c * t**i for i, c in enumerate(coef)) for coef in (HZ_INNER, HZ_OUTER))
    return math.sqrt(lum / s_in), math.sqrt(lum / s_out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='Tên đã dùng ở bước 1, ví dụ "Kepler-10"')
    parser.add_argument("--date", help="Ngày để mô phỏng vị trí hành tinh (YYYY-MM-DD), mặc định hôm nay")
    args = parser.parse_args()

    name = args.target.replace(" ", "").replace("-", "")
    system = json.loads((OUT_DIR / f"{name}_system.json").read_text(encoding="utf-8"))
    star, planets = system["star"], system["planets"]
    rs_au = star["radius_rsun"] * R_SUN_AU
    rs_earth = star["radius_rsun"] * R_SUN_EARTH
    hz_in, hz_out = habitable_zone(star["lum_lsun"], star["teff"])
    when = Time(args.date) if args.date else Time.now()
    now_bkjd = when.jd - BKJD_OFFSET

    fig = plt.figure(figsize=(16, 10))
    grid = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], height_ratios=[1, 1])
    ax_orbit = fig.add_subplot(grid[:, 0])
    ax_size = fig.add_subplot(grid[0, 1])
    ax_dist = fig.add_subplot(grid[1, 1])
    fig.suptitle(
        f"Hệ {system['target']}: cách Trái Đất {star['distance_pc']:.0f} pc ≈ "
        f"{star['distance_pc'] * 3.2616:.0f} năm ánh sáng · {len(planets)} hành tinh",
        fontsize=15, fontweight="bold",
    )

    # ---- A. Nhìn từ trên xuống, bán kính quỹ đạo theo log ----
    # Tọa độ bán kính ρ = 1 + log10(a / Rs): bề mặt sao ở ρ = 1, mỗi vòng xa hơn = xa gấp 10 lần.
    def rho(a_au):
        return 1 + math.log10(a_au / rs_au)

    outer = max([rho(p["a_au"]) for p in planets] + [rho(hz_out)]) + 0.4
    ax_orbit.add_patch(Circle((0, 0), rho(hz_out), color="#2ca02c", alpha=0.12, lw=0))
    ax_orbit.add_patch(Circle((0, 0), rho(hz_in), color="white", lw=0))
    ax_orbit.add_patch(Circle((0, 0), 1, color=star_color(star["teff"]), ec="#e0a000", lw=1.5, zorder=3))
    ax_orbit.text(0, 0, "Sao\nmẹ", ha="center", va="center", fontsize=9, zorder=4)
    for a_ref in [0.01, 0.1, 1, 10]:
        if 1 < rho(a_ref) < outer:
            ax_orbit.add_patch(Circle((0, 0), rho(a_ref), fill=False, ls=":", color="gray", lw=0.8))
            ax_orbit.text(rho(a_ref) * 0.707, -rho(a_ref) * 0.707, f"{a_ref} AU", fontsize=8, color="gray")
    ax_orbit.text(0, -(rho(hz_in) + rho(hz_out)) / 2, "vùng có thể sống", ha="center", fontsize=8, color="#2ca02c")

    for i, p in enumerate(planets):
        color = PLANET_COLORS[i % len(PLANET_COLORS)]
        r = rho(p["a_au"])
        ax_orbit.add_patch(Circle((0, 0), r, fill=False, color=color, lw=1.2, ls="-" if p["transiting"] else "--"))
        if p["t0_bkjd"] is not None:
            # Lúc transit hành tinh nằm giữa sao và Trái Đất; Trái Đất ở phía dưới hình (góc −90°)
            angle = -math.pi / 2 + 2 * math.pi * ((now_bkjd - p["t0_bkjd"]) / p["period_days"] % 1)
        else:
            angle = math.pi / 4 + i * 0.5  # không biết thời điểm: đặt tùy ý
        x, y = r * math.cos(angle), r * math.sin(angle)
        size = 0.09 * log_size(p["radius_earth"] or 1)
        ax_orbit.add_patch(Circle((x, y), size, color=color, zorder=5, alpha=1 if p["radius_measured"] else 0.5))
        ax_orbit.annotate(p["name"].split()[-1], (x, y), xytext=(6, 6), textcoords="offset points", fontsize=11, fontweight="bold", color=color)
    ax_orbit.annotate("", xy=(0, -outer), xytext=(0, -outer + 0.5), arrowprops=dict(arrowstyle="->", color="black"))
    ax_orbit.text(0.05, -outer + 0.1, "hướng về Trái Đất", fontsize=8)
    ax_orbit.set_xlim(-outer, outer)
    ax_orbit.set_ylim(-outer, outer)
    ax_orbit.set_aspect("equal")
    ax_orbit.axis("off")
    ax_orbit.set_title(
        f"Quỹ đạo nhìn từ trên xuống, ngày {when.datetime.strftime('%d/%m/%Y')}\n"
        "bán kính theo log: mỗi vòng chấm = xa gấp 10 lần · nét đứt = không có transit",
        fontsize=10,
    )

    # ---- B. So sánh kích thước, đường kính theo log ----
    bodies = [(f"Sao mẹ\n{rs_earth:.0f} R⊕", rs_earth, star_color(star["teff"]), True)]
    bodies += [
        (f"{p['name'].split()[-1]}\n{p['radius_earth']:.2f} R⊕" + ("" if p["radius_measured"] else "\n(ước tính)"),
         p["radius_earth"], PLANET_COLORS[i % len(PLANET_COLORS)], p["radius_measured"])
        for i, p in enumerate(planets) if p["radius_earth"]
    ]
    bodies += [(f"{n}\n{r:g} R⊕", r, "#dddddd", True) for n, r in REFERENCE_SIZES]
    x = 0.0
    for label, r, color, measured in bodies:
        d = log_size(r)
        x += d / 2
        ax_size.add_patch(Circle((x, d / 2), d / 2, color=color, ec="black", lw=0.6, alpha=1 if measured else 0.5))
        ax_size.text(x, -0.25, label, ha="center", va="top", fontsize=7.5)
        x += d / 2 + 0.7
    ax_size.set_xlim(-0.2, x)
    ax_size.set_ylim(-1.3, 3.6)
    ax_size.set_aspect("equal")
    ax_size.axis("off")
    ax_size.set_title("Kích thước, đường kính theo log (1 R⊕ → 1, 10 R⊕ → 2, 100 R⊕ → 3); màu xám = để so sánh", fontsize=10)

    # ---- C. Khoảng cách tới sao trên trục log, so với Hệ Mặt Trời ----
    ax_dist.axvspan(hz_in, hz_out, ymin=0.5, ymax=1, color="#2ca02c", alpha=0.15, label="vùng có thể sống")
    ax_dist.axvspan(1e-4, rs_au, color=star_color(star["teff"]), ec="#e0a000", label="bên trong sao mẹ")
    for i, p in enumerate(planets):
        ax_dist.scatter(p["a_au"], 1, s=60 * log_size(p["radius_earth"] or 1) ** 2, color=PLANET_COLORS[i % len(PLANET_COLORS)], zorder=3)
        ax_dist.annotate(
            f"{p['name'].split()[-1]}\n{p['a_au']:.3f} AU\n{p['teq_k']:.0f} K",
            # Nhãn so le trên/dưới để hai hành tinh gần nhau không đè chữ lên nhau
            (p["a_au"], 1), xytext=(0, 14 if i % 2 == 0 else -14), textcoords="offset points",
            ha="center", va="bottom" if i % 2 == 0 else "top", fontsize=8,
        )
    ax_dist.axvspan(0.95, 1.67, ymin=0, ymax=0.5, color="#2ca02c", alpha=0.15)
    for j, (n, a, r) in enumerate(SOLAR_SYSTEM):
        ax_dist.scatter(a, 0, s=60 * log_size(r) ** 2, color="#bbbbbb", zorder=3)
        ax_dist.annotate(
            n, (a, 0), xytext=(0, 10 if j % 2 else -12), textcoords="offset points",
            ha="center", va="bottom" if j % 2 else "top", fontsize=8, color="gray",
        )
    ax_dist.axhline(0.5, color="gray", lw=0.5)
    ax_dist.set_xscale("log")
    ax_dist.set_xlim(rs_au * 0.5, max(6, max(p["a_au"] for p in planets) * 3))
    ax_dist.set_ylim(-0.8, 1.8)
    ax_dist.set_yticks([0, 1], ["Hệ Mặt Trời", system["target"]])
    ax_dist.set_xlabel("Khoảng cách tới sao (AU, thang log)")
    ax_dist.legend(loc="upper right", fontsize=8)
    ax_dist.set_title("Khoảng cách tới sao mẹ so với Hệ Mặt Trời (kích thước chấm theo log bán kính)", fontsize=10)
    ax_dist.grid(axis="x", which="major", alpha=0.3)

    plt.tight_layout()
    out = OUT_DIR / f"{name}_diagram.png"
    plt.savefig(out, dpi=130)
    print(f"Sơ đồ: {out}")


if __name__ == "__main__":
    main()
