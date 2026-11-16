"""Vẽ các hình minh họa cho docs/khi-quyen-va-tuong-lai.md (lưu vào docs/img/gen/).

Cách chạy:
    .venv/Scripts/python docs/img/make_illustrations.py

Mọi hình là sơ đồ tự vẽ bằng matplotlib. Hình nào "không theo tỉ lệ" đều ghi rõ trên hình;
riêng đồ thị vận tốc tàu buồm laser là kết quả tính số từ công thức (mục 4.3 của tài liệu).
Các hình disputed_*.png (mục 3.5) là mô phỏng/minh họa, ghi rõ "không phải dữ liệu thật" trên hình;
riêng disputed_timeline.png là năm công bố/bị bác lấy từ các bài báo trong mục 3.5.
"""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Wedge
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định không in được tiếng Việt
OUT = Path(__file__).resolve().parent / "gen"
OUT.mkdir(exist_ok=True)
C = 2.99792458e8
G0 = 9.80665
plt.rcParams.update({"font.size": 10, "axes.titlesize": 11})


def save(fig, name):
    fig.savefig(OUT / name, dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("đã vẽ", name)


# ------------------------------------------------------------------ 1. Phổ truyền qua
def transmission_geometry():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), gridspec_kw={"width_ratios": [1, 1.3, 1.1]})
    fig.patch.set_facecolor("white")
    # (a) nhìn từ Trái Đất
    ax = axes[0]
    ax.add_patch(Circle((0, 0), 1, color="#ffcf6e"))
    ax.add_patch(Circle((0.35, 0.1), 0.2 + 0.06, color="#7fb3ff", alpha=0.55))
    ax.add_patch(Circle((0.35, 0.1), 0.2, color="#222222"))
    ax.annotate("lớp khí quyển\n(phóng đại ~50 lần)", (0.35 + 0.18, 0.1 + 0.18), (0.75, 0.85), fontsize=9,
                arrowprops=dict(arrowstyle="->"))
    ax.annotate("hành tinh\n(phần đặc)", (0.35, 0.1), (-0.9, -0.85), fontsize=9, arrowprops=dict(arrowstyle="->"))
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("(a) Nhìn từ Trái Đất lúc transit")
    # (b) mặt cắt ngang: tia sáng xuyên qua khí quyển
    ax = axes[1]
    ax.add_patch(Circle((0, 0), 1.0, color="#222222"))
    for i, (r, a) in enumerate([(1.06, 0.35), (1.12, 0.22), (1.18, 0.12), (1.24, 0.06)]):
        ax.add_patch(Circle((0, 0), r, fill=False, color="#1f77b4", lw=6, alpha=a))
    for y, absorbed in [(1.03, True), (1.10, True), (1.2, False), (1.5, False)]:
        ax.annotate("", (2.4, y), (-2.4, y), arrowprops=dict(arrowstyle="->", color="#d62728" if absorbed else "#e8a400", lw=1.6))
    ax.text(-2.35, 1.6, "ánh sáng sao →", fontsize=9)
    ax.text(1.35, 0.15, "tia đi sát bề mặt: khí dày,\nbị hấp thụ ở bước sóng\ncủa phân tử (H₂O, CH₄, CO₂…)", fontsize=8.5, color="#d62728")
    ax.text(1.35, 1.65, "tia đi cao: khí loãng,\nlọt qua", fontsize=8.5, color="#b07a00")
    ax.annotate("", (0, 1.24), (0, 1.0), arrowprops=dict(arrowstyle="<->", color="black"))
    ax.text(0.05, 1.08, "vài H", fontsize=9)
    ax.text(-0.35, -0.1, "hành tinh", color="white", fontsize=9)
    ax.text(-2.4, -1.5, "Mật độ khí giảm e lần sau mỗi độ cao thang H = kT / (μ m_H g)", fontsize=9)
    ax.set_xlim(-2.5, 3.2); ax.set_ylim(-1.7, 2.0); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("(b) Mặt cắt: tia sáng xuyên qua rìa khí quyển (không theo tỉ lệ)")
    # (c) phổ minh họa
    ax = axes[2]
    wl = np.linspace(0.6, 5.2, 600)
    base = 1.00
    bands = [(1.15, 0.05, 0.6), (1.4, 0.07, 1.0), (1.85, 0.08, 1.0), (2.3, 0.1, 0.8), (3.3, 0.12, 1.2), (4.3, 0.08, 1.6)]
    feat = sum(h * np.exp(-0.5 * ((wl - c) / w) ** 2) for c, w, h in bands)
    for mu, color, label in [(2.3, "#2ca02c", "khí quyển H/He nhẹ (μ = 2.3)"), (18, "#1f77b4", "khí quyển hơi nước (μ = 18)")]:
        ax.plot(wl, base + feat * 2.3 / mu * 0.05, color=color, label=label)
    ax.axhline(base, color="black", ls="--", lw=1, label="không có khí quyển (đá trần)")
    ax.set_xlabel("Bước sóng (μm)")
    ax.set_ylabel("Độ sâu transit (tương đối)")
    for c, name in [(1.4, "H₂O"), (1.85, "H₂O"), (3.3, "CH₄"), (4.3, "CO₂")]:
        peak = sum(h * math.exp(-0.5 * ((c - cc) / w) ** 2) for cc, w, h in bands)
        ax.text(c, base + peak * 0.05 + 0.002, name, ha="center", fontsize=9)
    ax.legend(fontsize=8, loc="upper left")
    ax.set_title("(c) Phổ truyền qua minh họa: khí càng nặng, biên độ càng nhỏ")
    save(fig, "transmission_geometry.png")


# ------------------------------------------------------------------ 2. Transit và nhật thực phụ
def eclipse_geometry():
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={"width_ratios": [1, 1.5]})
    ax = axes[0]
    ax.add_patch(Circle((0, 0), 0.5, color="#ffcf6e"))
    ax.add_patch(Circle((0, 0), 2.2, fill=False, ls="--", color="gray"))
    for ang, label, color in [(-90, "TRANSIT\n(hành tinh che sao)", "#222222"), (90, "NHẬT THỰC PHỤ\n(sao che hành tinh)", "#555555"),
                              (0, "pha 0.25", "#b05a2a"), (180, "pha 0.75", "#b05a2a")]:
        x, y = 2.2 * math.cos(math.radians(ang)), 2.2 * math.sin(math.radians(ang))
        ax.add_patch(Circle((x, y), 0.22, color="#b05a2a"))
        ax.add_patch(Wedge((x, y), 0.22, ang + 90, ang + 270, color="#3b1d0e"))  # phía đêm (quay lưng với sao)
        ax.text(x * 1.32, y * 1.27 - (0.15 if ang == -90 else 0), label, ha="center", va="center", fontsize=8.5)
    ax.annotate("", (0, -3.6), (0, -2.8), arrowprops=dict(arrowstyle="<-", lw=1.5))
    ax.text(0.1, -3.5, "về phía Trái Đất", fontsize=9)
    ax.set_xlim(-3.6, 3.6); ax.set_ylim(-3.8, 3.4); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Nhìn từ trên xuống quỹ đạo (phần tối = phía đêm)")
    ax = axes[1]
    ph = np.linspace(-0.1, 1.1, 3000)
    flux = np.ones_like(ph)
    d_tr, d_ecl, amp = 0.010, 0.0012, 0.0005
    phase_curve = amp * (1 - np.cos(2 * np.pi * ph)) / 2
    flux += phase_curve
    for c, d in [(0.0, d_tr), (1.0, d_tr)]:
        flux[np.abs(ph - c) < 0.02] -= d
    ecl = np.abs(ph - 0.5) < 0.02
    flux[ecl] -= phase_curve[ecl]
    ax.plot(ph, (flux - 1) * 1e6, color="black")
    ax.set_ylim(-1500, 900)
    ax.annotate("transit: sâu ~ (Rp/Rs)²", (0.0, -d_tr * 1e6 * 0.13), (0.06, -1250), fontsize=9, arrowprops=dict(arrowstyle="->"))
    ax.annotate("nhật thực phụ: mất đúng phần ánh sáng\ncủa hành tinh (phản xạ + phát nhiệt)", (0.5, 380), (0.18, 700), fontsize=9,
                arrowprops=dict(arrowstyle="->"))
    ax.annotate("đường cong pha: thấy dần phía ngày", (0.3, 220), (0.62, -500), fontsize=9, arrowprops=dict(arrowstyle="->"))
    ax.text(0.62, -1350, "Độ sâu đã phóng đại để dễ thấy.\nKepler-6b thật: transit ~8.800 ppm,\nnhật thực phụ ~19 ppm (tự đo).", fontsize=8.5)
    ax.set_xlabel("Pha quỹ đạo")
    ax.set_ylabel("Độ sáng tổng (ppm)")
    ax.set_title("Đường cong ánh sáng qua một vòng quỹ đạo")
    save(fig, "eclipse_geometry.png")


# ------------------------------------------------------------------ 3. Độ tin cậy thống kê
def significance():
    fig, axes = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    x = np.linspace(-6, 6, 2000)
    y = np.exp(-x**2 / 2) / math.sqrt(2 * math.pi)
    ax.plot(x, y, color="black")
    for s, color in [(3, "#ff7f0e"), (5, "#d62728")]:
        m = x >= s
        ax.fill_between(x[m], 0, y[m] * (40 if s == 5 else 1), color=color, alpha=0.5)
        ax.axvline(s, color=color, ls="--")
    ax.text(3.05, 0.30, "3σ: nhiễu ngẫu nhiên vượt\nngưỡng này 1 lần\ntrong ~740 (một phía)", color="#c45f00", fontsize=9)
    ax.text(5.05, 0.18, "5σ: 1 lần\ntrong ~3,5\ntriệu", color="#d62728", fontsize=9)
    ax.set_xlabel("Độ lệch so với 'không có gì' (đơn vị σ)")
    ax.set_yticks([])
    ax.set_title("σ nghĩa là gì: xác suất nhiễu tạo ra tín hiệu mạnh như vậy")
    ax = axes[1]
    claims = [
        ("2023: CH₄ (Madhusudhan et al.)", 5.0, "#2ca02c"),
        ("2023: CO₂ (Madhusudhan et al.)", 3.0, "#2ca02c"),
        ("2023: DMS 'tạm thời'", 1.0, "#ff7f0e"),
        ("4/2025: DMS/DMDS, MIRI\n(\"bằng chứng mạnh nhất\")", 3.0, "#d62728"),
        ("2025–2026: phân tích lại\nđộc lập, DMS", 0.5, "#7f7f7f"),
    ]
    for i, (label, s, color) in enumerate(claims):
        ax.barh(i, s, color=color, alpha=0.8)
        ax.text(s + 0.1, i, f"~{s:g}σ" if s >= 1 else "không đáng kể", va="center", fontsize=9)
    ax.set_yticks(range(len(claims)), [c[0] for c in claims], fontsize=8.5)
    ax.axvline(5, color="#d62728", ls="--")
    ax.text(5.05, len(claims) - 0.6, "chuẩn 'phát hiện'\ntrong vật lý", fontsize=8, color="#d62728")
    ax.invert_yaxis()
    ax.set_xlim(0, 7)
    ax.set_xlabel("Độ tin cậy công bố (σ, xấp xỉ)")
    ax.set_title("K2-18b: các tuyên bố và độ tin cậy")
    save(fig, "significance_k2-18b.png")


# ------------------------------------------------------------------ 4. Thấu kính hấp dẫn Mặt Trời
def sgl_side():
    fig, ax = plt.subplots(figsize=(16, 5.5))
    ax.set_facecolor("#0b0f1a"); fig.patch.set_facecolor("#0b0f1a")
    ax.add_patch(Circle((0, 0), 0.35, color="#ffd34d", zorder=5))
    ax.text(0, -0.75, "Mặt Trời", color="white", ha="center")
    ax.add_patch(Circle((-8.5, 0), 0.25, color="#4f8fd8"))
    ax.text(-8.5, -0.7, "hành tinh cần chụp\n(cách hàng chục năm ánh sáng)", color="white", ha="center", fontsize=9)
    focus = 5.0
    for b, color in [(0.36, "#ffe08a"), (0.5, "#ffc35c"), (0.7, "#ff9d4d")]:
        for sign in (1, -1):
            xs = [-8.2, 0, 13]
            ys = [sign * b, sign * b, sign * b - sign * b / (focus * (b / 0.36) ** 2) * 13]
            ax.plot(xs, ys, color=color, lw=1.2)
    ax.plot([focus, 13], [0, 0], color="#7fdbff", lw=3, alpha=0.8)
    ax.text(focus, 0.25, "đường tiêu cự bắt đầu ~548 AU", color="#7fdbff", fontsize=9)
    ax.plot([8.5], [0], marker="s", color="white", ms=8)
    ax.text(8.5, -0.55, "kính thiên văn\n~650–900 AU", color="white", ha="center", fontsize=9)
    ax.annotate("", (0.0, 0.55), (-2.0, 0.55), arrowprops=dict(arrowstyle="->", color="white"))
    ax.text(-3.4, 0.75, "tia sượt qua mép Mặt Trời (b ≈ R☉)\nbị bẻ cong góc θ = 4GM☉/(c²b) ≈ 1,75″", color="white", fontsize=9)
    ax.text(1.0, -1.85, "tia đi xa hơn (b lớn) bị bẻ ít hơn → hội tụ xa hơn: không có 'tiêu điểm' mà là một ĐƯỜNG tiêu cự",
            color="#cccccc", fontsize=9)
    ax.text(-8.6, 1.75, "Sơ đồ không theo tỉ lệ (góc bẻ thật chỉ ~0,0005°)", color="#ff8080", fontsize=9)
    ax.set_xlim(-9.5, 13); ax.set_ylim(-2.1, 2.1); ax.axis("off")
    ax.set_title("Thấu kính hấp dẫn Mặt Trời: nhìn ngang", color="white")
    save(fig, "sgl_side.png")


def sgl_ring_view():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))
    fig.patch.set_facecolor("#05070d")
    for ax, (offset, title) in zip(axes, [(0.0, "Kính nằm ĐÚNG trên trục:\nvòng Einstein trọn vẹn"),
                                          (0.35, "Kính lệch khỏi trục:\nvòng vỡ thành 2 cung"),
                                          (None, "Thực tế: vầng nhật hoa sáng\nhơn vòng ~10⁷ lần")]):
        ax.set_facecolor("#05070d")
        n = 400
        yy, xx = np.mgrid[-1.6:1.6:n * 1j, -1.6:1.6:n * 1j]
        r = np.hypot(xx, yy)
        corona = np.where(r > 1, (r ** -4) * (1.0 if offset is None else 0.08), 0)
        img = np.zeros((n, n, 3))
        img[..., 0] += corona * 1.0; img[..., 1] += corona * 0.85; img[..., 2] += corona * 0.6
        ring_r = 1.03
        if offset is not None:
            theta = np.arctan2(yy, xx)
            if offset:  # lệch trục: 2 ảnh ở 2 phía đối diện, ảnh phía gần sáng hơn
                weight = np.exp(-(theta / 0.45) ** 2) + 0.55 * np.exp(-((np.abs(theta) - np.pi) / 0.35) ** 2)
            else:
                weight = np.ones_like(theta)
            ring = np.exp(-((r - ring_r) / 0.012) ** 2) * weight / weight.max()
            img[..., 0] += ring * 0.6; img[..., 1] += ring * 0.85; img[..., 2] += ring * 1.0
        else:
            ring = np.exp(-((r - ring_r) / 0.012) ** 2) * 1e-3
            img[..., 2] += ring
        img[r <= 1] = 0
        ax.imshow(np.clip(img, 0, 1), extent=[-1.6, 1.6, -1.6, 1.6])
        ax.add_patch(Circle((0, 0), 1, color="#202020"))
        ax.text(0, 0, "che bằng\ncoronagraph", color="white", ha="center", va="center", fontsize=9)
        ax.set_title(title, color="white", fontsize=10)
        ax.axis("off")
    fig.suptitle("Nhìn từ kính thiên văn về phía Mặt Trời: ảnh hành tinh hiện thành vòng Einstein sát mép đĩa Mặt Trời",
                 color="white", fontsize=11)
    save(fig, "sgl_view_from_telescope.png")


def sgl_3d():
    fig = plt.figure(figsize=(16, 6.5))
    fig.patch.set_facecolor("white")
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, v = np.mgrid[0:2 * np.pi:30j, 0:np.pi:15j]
    ax.plot_surface(0.6 * np.cos(u) * np.sin(v), 0.6 * np.sin(u) * np.sin(v), 0.6 * np.cos(v), color="#ffd34d", alpha=0.9)
    ax.plot([0, 14], [0, 0], [0, 0], color="#1f77b4", lw=2)
    ax.plot([-10, 0], [0, 0], [0, 0], color="gray", ls=":")
    ax.scatter([-10], [0], [0], color="#4f8fd8", s=80)
    ax.text(-10, 0, 0.8, "hành tinh", fontsize=9)
    z = 9
    th = np.linspace(0, 2 * np.pi, 60)
    ax.plot(np.full_like(th, z), 1.2 * np.cos(th), 1.2 * np.sin(th), color="#d62728")
    ax.text(z, 0, 1.6, "ảnh hành tinh: hình tròn\nđường kính ~1,3 km", fontsize=9, color="#d62728")
    ax.scatter([z], [0.5], [0.4], color="black", s=30, marker="s")
    ax.text(z + 0.5, 0.5, -0.9, "kính 1 m", fontsize=9)
    for b in [0.6, 0.8]:
        for t in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            ax.plot([-10, 0, 14], [0, b * np.cos(t), b * np.cos(t) - b * np.cos(t) / 6 * 14 * (0.6 / b) ** 2],
                    [0, b * np.sin(t), b * np.sin(t) - b * np.sin(t) / 6 * 14 * (0.6 / b) ** 2], color="orange", lw=0.5, alpha=0.6)
    ax.set_axis_off()
    ax.view_init(elev=18, azim=-60)
    ax.set_title("Góc nhìn 3D: các tia quanh mép Mặt Trời hội tụ về đường tiêu cự (không theo tỉ lệ)")
    ax2 = fig.add_subplot(1, 2, 2)
    n = 128
    yy, xx = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]
    r = np.hypot(xx, yy)
    lon = np.arctan2(yy, np.sqrt(np.clip(1 - r**2, 0, 1)))
    planet = np.zeros((n, n, 3))
    land = (np.sin(5 * xx + 2 * np.cos(4 * yy)) + np.cos(6 * yy - xx)) > 0.6
    planet[...] = [0.15, 0.35, 0.75]
    planet[land] = [0.35, 0.55, 0.25]
    clouds = (np.sin(9 * xx * yy + 3 * yy) > 0.85)
    planet[clouds] = [0.95, 0.95, 0.95]
    planet[r > 1] = 1
    ax2.imshow(planet, extent=[-0.65, 0.65, -0.65, 0.65])
    for gx in np.linspace(-0.65, 0.65, 11):
        ax2.axvline(gx, color="black", lw=0.3, alpha=0.5)
        ax2.axhline(gx, color="black", lw=0.3, alpha=0.5)
    path_x = np.repeat(np.linspace(-0.6, 0.6, 6), 2)
    path_y = np.tile([-0.6, 0.6], 6)
    path_y[2::4], path_y[3::4] = 0.6, -0.6
    ax2.plot(path_x, path_y, color="#d62728", lw=1.5, marker="s", ms=3)
    ax2.set_xlabel("km trên mặt phẳng ảnh (ở ~650 AU)")
    ax2.set_ylabel("km")
    ax2.set_title("Mặt phẳng ảnh: kính di chuyển quét từng 'điểm ảnh'\n(mỗi vị trí đo 1 điểm; 1000×1000 điểm cần ~1 năm, Turyshev & Toth 2022)", fontsize=10)
    save(fig, "sgl_3d_and_image_plane.png")


# ------------------------------------------------------------------ 5. Tàu buồm laser
def lightsail_scene():
    fig = plt.figure(figsize=(17, 6))
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    gx, gy = np.meshgrid(np.linspace(-1.5, 1.5, 9), np.linspace(-1.5, 1.5, 9))
    ax.scatter(gx, gy, np.zeros_like(gx), color="#d62728", s=8)
    ax.text(-1.5, -2.3, 0, "mảng laser ghép pha\n(~1 km², hàng triệu nguồn 10 kW)", fontsize=8)
    sail_z = 10
    sx = np.array([-0.6, 0.6, 0.6, -0.6]); sy = np.array([-0.6, -0.6, 0.6, 0.6])
    ax.add_collection3d(Poly3DCollection([list(zip(sx, sy, [sail_z] * 4))], color="#cfd8e3", alpha=0.9, edgecolor="black"))
    ax.scatter([0], [0], [sail_z + 0.05], color="black", s=25)
    ax.text(0.8, 0.8, sail_z, "cánh buồm 4 m × 4 m\n+ chip vài gam", fontsize=8)
    for x0 in [-1.5, 1.5]:
        for y0 in [-1.5, 1.5]:
            ax.plot([x0, x0 * 0.4], [y0, y0 * 0.4], [0, sail_z], color="#ff6b6b", alpha=0.5)
    ax.set_zlim(0, 11); ax.set_axis_off()
    ax.view_init(elev=15, azim=-55)
    ax.set_title("(a) Góc 3D: chùm laser đẩy cánh buồm")
    ax = fig.add_subplot(1, 3, 2)
    xs = np.linspace(-2, 2, 200)
    ax.plot(0.08 * xs**2, xs, color="#4a5a70", lw=4)
    for y in [-1.4, -0.7, 0, 0.7, 1.4]:
        ax.annotate("", (0.08 * y**2 - 0.05, y), (-2.5, y), arrowprops=dict(arrowstyle="->", color="#d62728"))
        ax.annotate("", (-1.6, y + 0.25), (0.08 * y**2 - 0.05, y + 0.08), arrowprops=dict(arrowstyle="->", color="#ff9d9d", ls="--"))
    ax.annotate("", (2.2, 0), (0.6, 0), arrowprops=dict(arrowstyle="-|>", color="black", lw=2.5))
    ax.text(0.7, 0.25, "lực F = 2P/c\n(phản xạ toàn phần)", fontsize=9)
    ax.text(-2.5, 1.85, "photon tới: động lượng hν/c", color="#d62728", fontsize=9)
    ax.text(-2.5, -2.2, "photon dội lại: thêm hν/c nữa", color="#d07070", fontsize=9)
    ax.text(0.3, -1.5, "màng mỏng ~100 nm\n(khối lượng < 1 g)", fontsize=8.5)
    ax.set_xlim(-2.7, 2.6); ax.set_ylim(-2.4, 2.2); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("(b) Mặt cắt ngang: vì sao ánh sáng đẩy được")
    ax = fig.add_subplot(1, 3, 3)
    ax.add_patch(Rectangle((-2, -2), 4, 4, color="#cfd8e3", ec="black"))
    ax.add_patch(Rectangle((-0.12, -0.12), 0.24, 0.24, color="black"))
    ax.text(0.2, -0.45, "StarChip (~1 cm, vài gam):\ncamera, máy tính, laser liên lạc,\npin hạt nhân 150 mg", fontsize=8.5)
    for xx in np.linspace(-2, 2, 9):
        ax.plot([xx, xx], [-2, 2], color="white", lw=0.5)
        ax.plot([-2, 2], [xx, xx], color="white", lw=0.5)
    ax.text(-2, 2.2, "4 m", fontsize=9)
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("(c) Mặt trước cánh buồm (không theo tỉ lệ chip)")
    save(fig, "lightsail_views.png")


def lightsail_acceleration():
    """Tích phân số chuyển động tàu buồm: lực = 2P/c · (1−β)/(1+β) (Doppler, hệ quy chiếu mặt đất),
    công suất bắt được giảm khi vết chùm (đường kính 2,44 λ L / D) to hơn cánh buồm."""
    P, lam, d_sail, mass = 100e9, 1.064e-6, 4.0, 2e-3
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for d_array, color in [(1000, "#1f77b4"), (3000, "#2ca02c"), (10000, "#d62728")]:
        t, x, p = 0.0, 0.0, 0.0  # p = động lượng tương đối tính
        dt = 0.05
        ts, vs, xs = [0], [0], [0]
        while t < 1800:
            gamma = math.sqrt(1 + (p / (mass * C)) ** 2)
            beta = p / (gamma * mass * C)
            spot = 2.44 * lam * x / d_array
            frac = 1.0 if spot <= d_sail else (d_sail / spot) ** 2
            force = 2 * P / C * frac * (1 - beta) / (1 + beta)
            p += force * dt
            x += beta * C * dt
            t += dt
            if int(t / dt) % 20 == 0:
                ts.append(t); vs.append(beta); xs.append(x)
        axes[0].plot(np.array(ts) / 60, vs, color=color, label=f"mảng laser {d_array / 1000:g} km")
        axes[1].plot(np.array(xs) / 1.496e11, vs, color=color, label=f"mảng laser {d_array / 1000:g} km")
    for ax in axes:
        ax.axhline(0.2, color="black", ls="--", lw=0.8)
        ax.set_ylabel("Vận tốc (phần của c)")
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
    axes[0].set_xlabel("Thời gian (phút)")
    axes[1].set_xlabel("Quãng đường (AU)")
    axes[1].set_xscale("log")
    axes[0].set_title("Tính số: P = 100 GW, λ = 1,064 μm, cánh 4 m, tổng khối lượng 2 g")
    axes[1].set_title("Hết tăng tốc khi vết chùm laser to hơn cánh buồm")
    save(fig, "lightsail_acceleration.png")


def interstellar_scale():
    fig, ax = plt.subplots(figsize=(15, 3.6))
    items = [("Trái Đất", 1, "#4f8fd8"), ("Sao Mộc", 5.2, "#c99a6b"), ("Sao Hải Vương", 30, "#5b7fd6"),
             ("Voyager 1 (2026)", 170, "#999999"), ("thấu kính Mặt Trời\nbắt đầu", 548, "#d62728"),
             ("tàu SGL làm việc", 650, "#d62728"), ("Alpha Centauri\n4,37 năm ánh sáng", 276000, "#ffb000")]
    for name, au, color in items:
        ax.scatter(au, 0, s=80, color=color, zorder=3)
        ax.text(au, 0.25 if items.index((name, au, color)) % 2 else -0.45, name, ha="center", fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.5, 1e6)
    ax.set_ylim(-0.8, 0.7)
    ax.set_yticks([])
    ax.set_xlabel("Khoảng cách từ Mặt Trời (AU, thang log)")
    ax.text(1, -0.75, "Voyager 1 bay 49 năm mới được ~170 AU (~3,6 AU/năm). Tàu SGL cần ~20–30 AU/năm; tàu buồm laser 0,2c ≈ 12.600 AU/năm.",
            fontsize=9)
    ax.set_title("Thang khoảng cách: vì sao cần cách đẩy mới")
    save(fig, "distance_scale.png")


# ------------------------------------------------------------------ 7. Các hệ bị tranh cãi (mục 3.5)
STATUS_COLORS = {
    "bác bỏ": "#d62728",
    "đang tranh cãi": "#ff7f0e",
    "ứng viên, chờ kiểm tra": "#1f77b4",
    "xác nhận (hành tinh khác)": "#2ca02c",
}


def disputed_timeline():
    """Dòng thời gian: năm công bố → năm bị bác / tình trạng tới 11/2026."""
    now = 2026.9
    rows = [  # (tên, năm công bố, năm kết luận hoặc None nếu còn treo, tình trạng, ghi chú)
        ("Gliese 581 d", 2007, 2014, "bác bỏ", "hoạt động sao (P_rot/2)"),
        ("Gliese 581 g", 2010, 2014, "bác bỏ", "hoạt động sao"),
        ("Alpha Centauri Bb", 2012, 2016, "bác bỏ", "do lịch quan sát"),
        ("Kapteyn b", 2014, 2021, "bác bỏ", "hoạt động sao"),
        ("Sao Barnard b (233 ngày)", 2018, 2021, "bác bỏ", "hoạt động sao + alias 1 năm"),
        ("Sao Barnard b, c, d, e", 2024, 2025, "xác nhận (hành tinh khác)", "4 hành tinh nhỏ, nóng"),
        ("Fomalhaut b", 2008, 2020, "bác bỏ", "đám bụi đang tan"),
        ("Proxima Centauri c", 2020, None, "ứng viên, chờ kiểm tra", "RV yếu, chu kỳ dài"),
        ("Alpha Centauri A 'S1'", 2025, None, "ứng viên, chờ kiểm tra", "mới thấy 1 lần"),
        ("GJ 1132 b: khí quyển", 2021, 2025, "bác bỏ", "nghiêng về đá trần"),
        ("GJ 486 b: hơi nước", 2023, None, "đang tranh cãi", "hành tinh hay vết sao?"),
        ("55 Cancri e: khí quyển", 2024, None, "ứng viên, chờ kiểm tra", "mạnh nhất, nhưng dung nham"),
        ("K2-18b: DMS 'sự sống'", 2023, None, "đang tranh cãi", "phân tích lại: không đủ"),
        ("Kepler-1625 b-i (vệ tinh)", 2018, None, "đang tranh cãi", ""),
        ("Kepler-1708 b-i (vệ tinh)", 2022, None, "đang tranh cãi", ""),
        ("Phosphine Sao Kim", 2020, None, "đang tranh cãi", "(Hệ Mặt Trời, để so sánh)"),
        ("Sao Tabby 'cấu trúc ngoài hành tinh'", 2015, 2018, "bác bỏ", "bụi"),
    ]
    fig, ax = plt.subplots(figsize=(15, 8))
    for i, (name, y0, y1, status, note) in enumerate(rows):
        color = STATUS_COLORS[status]
        end = y1 if y1 is not None else now
        ax.plot([y0, end], [i, i], color=color, lw=6, alpha=0.35, solid_capstyle="butt")
        ax.scatter(y0, i, s=70, color=color, zorder=3, marker="o")
        if y1 is not None:
            ax.scatter(y1, i, s=90, color=color, zorder=3, marker="X" if status == "bác bỏ" else "*")
        else:
            ax.annotate("", xy=(now + 0.35, i), xytext=(now - 0.05, i),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.5))
        if note:
            ax.text(end + 0.5, i, note, va="center", fontsize=8.5, color="#444444")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(2006, 2032.5)
    ax.set_xticks(range(2006, 2027, 2))
    ax.axvline(now, color="#999999", ls=":", lw=1)
    ax.text(now + 0.1, len(rows) - 0.4, "11/2026", ha="left", fontsize=8, color="#666666")
    ax.grid(axis="x", alpha=0.3)
    handles = [plt.Line2D([], [], color=c, lw=6, alpha=0.6, label=s) for s, c in STATUS_COLORS.items()]
    handles += [plt.Line2D([], [], color="black", marker="o", ls="", label="năm công bố"),
                plt.Line2D([], [], color="black", marker="X", ls="", label="năm bị bác"),
                plt.Line2D([], [], color="black", marker=r"$\rightarrow$", ls="", ms=12, label="vẫn còn treo")]
    ax.legend(handles=handles, loc="lower left", fontsize=8.5, ncol=2, framealpha=0.95)
    ax.set_title("Các tuyên bố từng gây tranh cãi: công bố năm nào, bị bác hay vẫn còn treo (tới 11/2026)")
    save(fig, "disputed_timeline.png")


def disputed_rv_activity():
    """Mô phỏng: vết trên sao (quay 130 ngày) tạo ra 'hành tinh' giả trong dữ liệu vận tốc xuyên tâm."""
    from astropy.timeseries import LombScargle

    rng = np.random.default_rng(581)
    p_rot = 130.0
    # Lịch quan sát thật thường có dạng này: ~7 tháng/năm sao lên được, mỗi mùa vài chục đêm ngẫu nhiên
    t = np.sort(np.concatenate([
        365.25 * yr + rng.uniform(0, 210, 45) for yr in range(7)
    ]))
    # Chỉ số hoạt động (vd. vạch Hα): vết sao quay theo sao + vết sinh/tan dần (biên độ, pha trôi chậm)
    amp = 1 + 0.4 * np.sin(2 * np.pi * t / 900)
    phase = 0.6 * np.sin(2 * np.pi * t / 1400)
    activity = amp * (np.sin(2 * np.pi * t / p_rot + phase) + 0.7 * np.sin(4 * np.pi * t / p_rot + 2 * phase + 1.0))
    halpha = activity + rng.normal(0, 0.15, t.size)
    rv = 1.6 * activity + rng.normal(0, 0.8, t.size)  # m/s: RV đi theo hoạt động sao, KHÔNG có hành tinh nào

    freq = np.linspace(1 / 400, 1 / 10, 6000)
    pow_rv = LombScargle(t, rv).power(freq)
    k = np.polyfit(halpha, rv, 1)
    resid = rv - np.polyval(k, halpha)
    pow_res = LombScargle(t, resid).power(freq)

    fig, axes = plt.subplots(2, 2, figsize=(15, 8.5))
    ax = axes[0, 0]
    ax.scatter(t, rv, s=10, color="#1f77b4")
    ax.set_xlabel("Thời gian (ngày)")
    ax.set_ylabel("Vận tốc xuyên tâm (m/s)")
    ax.set_title("(a) Dữ liệu RV: các khoảng trống theo mùa, KHÔNG có hành tinh nào")
    ax = axes[0, 1]
    ax.plot(1 / freq, pow_rv, color="#1f77b4")
    for p, label, ha in [(p_rot, " chu kỳ tự quay\n 130 ngày", "left"),
                         (p_rot / 2, "P_rot/2 ≈ 65 ngày \n(≈ 'Gliese 581 d' \n66,6 ngày) ", "right")]:
        ax.axvline(p, color="#d62728", ls="--", lw=1)
        ax.text(p, pow_rv.max() * 0.92, label, fontsize=8.5, color="#d62728", va="top", ha=ha)
    ax.text(20, pow_rv.max() * 0.5, "các đỉnh phụ quanh đỉnh chính:\nalias do lịch quan sát theo mùa", fontsize=8.5, color="#555555")
    ax.set_xscale("log")
    ax.set_xlabel("Chu kỳ (ngày, thang log)")
    ax.set_ylabel("Công suất Lomb–Scargle")
    ax.set_title("(b) Periodogram: đỉnh rất rõ, trông như có 'hành tinh'")
    ax = axes[1, 0]
    ax.scatter(halpha, rv, s=10, color="#ff7f0e")
    xs = np.linspace(halpha.min(), halpha.max(), 10)
    ax.plot(xs, np.polyval(k, xs), color="black")
    r = np.corrcoef(halpha, rv)[0, 1]
    ax.text(0.03, 0.93, f"hệ số tương quan r = {r:.2f}", transform=ax.transAxes, fontsize=9)
    ax.set_xlabel("Chỉ số hoạt động của sao (vd. vạch Hα)")
    ax.set_ylabel("Vận tốc xuyên tâm (m/s)")
    ax.set_title("(c) Phép thử: RV đi theo chỉ số hoạt động sao, hành tinh thật thì không")
    ax = axes[1, 1]
    ax.plot(1 / freq, pow_rv, color="#1f77b4", alpha=0.3, label="trước khi hiệu chỉnh")
    ax.plot(1 / freq, pow_res, color="#2ca02c", label="sau khi trừ phần tương quan với Hα")
    ax.set_xscale("log")
    ax.set_ylim(0, pow_rv.max() * 1.05)
    ax.set_xlabel("Chu kỳ (ngày, thang log)")
    ax.set_ylabel("Công suất Lomb–Scargle")
    ax.legend(fontsize=9)
    ax.set_title("(d) Trừ hoạt động sao: các 'hành tinh' biến mất")
    fig.suptitle("Mô phỏng (không phải dữ liệu thật): vết trên sao giả làm hành tinh trong dữ liệu vận tốc xuyên tâm, "
                 "như Gliese 581 d/g, Kapteyn b, Barnard b (2018)", fontsize=11)
    fig.tight_layout()
    save(fig, "disputed_rv_activity.png")


def disputed_fomalhaut():
    """Minh họa: hành tinh thật và đám bụi khác nhau thế nào qua nhiều năm chụp ảnh (Fomalhaut b)."""
    epochs = [2004, 2006, 2010, 2012, 2014]
    fig, axes = plt.subplots(2, len(epochs), figsize=(15, 6.2), facecolor="white")
    yy, xx = np.mgrid[-1:1:200j, -1:1:200j]
    for j, yr in enumerate(epochs):
        dt = yr - 2004
        x0 = -0.5 + 0.09 * dt  # cả hai cùng di chuyển trên quỹ đạo
        for i, kind in enumerate(["planet", "dust"]):
            ax = axes[i, j]
            if kind == "planet":
                sigma, peak = 0.05, 1.0
            else:
                sigma, peak = 0.05 + 0.035 * dt, 1.0 * (0.05 / (0.05 + 0.035 * dt)) ** 1.3
            img = peak * np.exp(-((xx - x0) ** 2 + yy ** 2) / (2 * sigma ** 2))
            ax.imshow(img, cmap="inferno", vmin=0, vmax=1, origin="lower", extent=[-1, 1, -1, 1])
            ax.set_xticks([])
            ax.set_yticks([])
            if i == 0:
                ax.set_title(str(yr))
        axes[0, 0].set_ylabel("Nếu là hành tinh:\nchấm sáng giữ\nnguyên cỡ, độ sáng", fontsize=9)
        axes[1, 0].set_ylabel("Fomalhaut b thực tế:\nnở to, mờ dần\n→ đám bụi", fontsize=9)
    fig.suptitle("Minh họa (không phải ảnh thật): Fomalhaut b qua các lần chụp HST 2004–2014. "
                 "Hành tinh tự phát nhiệt/phản xạ ổn định; đám bụi từ va chạm thì loãng dần (Gáspár & Rieke 2020)",
                 fontsize=10.5)
    fig.tight_layout()
    save(fig, "disputed_fomalhaut.png")


def disputed_single_epoch():
    """Bẫy 'chỉ thấy 1 lần': GJ 1132 b (2 lần transit khác nhau) và Alpha Cen A S1 (1 lần chụp)."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [1.25, 1]})

    ax = axes[0]
    rng = np.random.default_rng(1132)
    wl = np.linspace(2.9, 5.1, 28)
    err = 14
    visit1 = 60 * np.exp(-((wl - 3.6) / 0.25) ** 2) + 45 * np.exp(-((wl - 4.4) / 0.2) ** 2) + rng.normal(0, err, wl.size)
    visit2 = rng.normal(0, err, wl.size)
    combined = (visit1 + visit2) / 2
    ax.errorbar(wl - 0.012, visit1, yerr=err, fmt="o-", ms=4, lw=0.8, color="#d62728", alpha=0.85, label="lần transit 1: có 'đặc trưng'")
    ax.errorbar(wl + 0.012, visit2, yerr=err, fmt="o-", ms=4, lw=0.8, color="#1f77b4", alpha=0.85, label="lần transit 2: phẳng")
    ax.plot(wl, combined, color="black", lw=2, label="gộp 2 lần: đặc trưng yếu đi một nửa")
    ax.axhline(0, color="#2ca02c", ls="--", label="đá trần: phổ phẳng")
    ax.set_xlabel("Bước sóng (μm)")
    ax.set_ylabel("Độ sâu transit trừ trung bình (ppm)")
    ax.set_title("(a) GJ 1132 b: 2 lần quan sát JWST cho 2 kết quả khác nhau")
    ax.legend(fontsize=8.5, loc="upper right")
    ax.text(0.01, 0.02, "Mô phỏng minh họa, không phải dữ liệu thật (May et al. 2023; Bennett et al. 2025)",
            transform=ax.transAxes, fontsize=8, color="#666666")

    ax = axes[1]
    ax.set_facecolor("#0b0b1a")
    period, ecc, t_peri = 2.4, 0.4, 2025.2

    def pos(tt):
        m = 2 * np.pi * (tt - t_peri) / period
        e_anom = m
        for _ in range(30):
            e_anom = e_anom - (e_anom - ecc * np.sin(e_anom) - m) / (1 - ecc * np.cos(e_anom))
        x = np.cos(e_anom) - ecc
        y = math.sqrt(1 - ecc ** 2) * np.sin(e_anom)
        return x, 0.45 * y  # nghiêng quỹ đạo: trục y bị ép lại khi nhìn từ Trái Đất

    tt = np.linspace(t_peri, t_peri + period, 400)
    ox, oy = zip(*[pos(v) for v in tt])
    ax.plot(ox, oy, color="#888888", ls=":", lw=1)
    mask_r = 0.75
    ax.add_patch(Circle((0, 0), mask_r, color="#333344", zorder=2))
    ax.text(0, -0.42, "vùng bị che bởi\ncoronagraph và\nánh chói của sao", ha="center", color="#bbbbbb", fontsize=7.5, zorder=4)
    ax.scatter(0, 0, s=160, color="#ffd27f", zorder=5)
    ax.text(0, 0.1, "α Cen A", ha="center", color="#ffd27f", fontsize=9, zorder=5)
    for when, label, color, seen in [(2024.6, "8/2024: THẤY", "#2ca02c", True),
                                     (2025.12, "2/2025: không thấy", "#d62728", False),
                                     (2025.29, "4/2025: không thấy", "#d62728", False),
                                     (2026.6, "8/2026: dự đoán\nsẽ hiện lại", "#1f77b4", False)]:
        x, y = pos(when)
        ax.scatter(x, y, s=90 if seen else 60, color=color, zorder=6,
                   marker="o" if seen else ("x" if color == "#d62728" else "D"))
        ax.annotate(label, (x, y), xytext=(8, 10 if y >= 0 else -18), textcoords="offset points",
                    color=color, fontsize=8.5, zorder=7)
    ax.set_xlim(-1.75, 1.0)
    ax.set_ylim(-0.95, 0.95)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("(b) Alpha Centauri A 'S1': mới thấy 1 lần, 2 lần sau bị khuất")
    ax.text(0.01, 0.02, "Minh họa, không theo tỉ lệ; quỹ đạo e ≈ 0,4, chu kỳ 2–3 năm (Sanghi et al. 2025)",
            transform=ax.transAxes, fontsize=8, color="#bbbbbb")
    fig.suptitle("Bẫy 'chỉ thấy 1 lần': kết quả phải lặp lại được mới tính là phát hiện", fontsize=11)
    fig.tight_layout()
    save(fig, "disputed_single_epoch.png")


if __name__ == "__main__":
    transmission_geometry()
    eclipse_geometry()
    significance()
    sgl_side()
    sgl_ring_view()
    sgl_3d()
    lightsail_scene()
    lightsail_acceleration()
    interstellar_scale()
    disputed_timeline()
    disputed_rv_activity()
    disputed_fomalhaut()
    disputed_single_epoch()
