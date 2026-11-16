# Exoplanet Hunting

Tự săn hành tinh ngoài Hệ Mặt Trời từ dữ liệu thô của kính thiên văn Kepler: tải đường cong ánh sáng, tự tìm các lần transit, tính thông số từng hành tinh, đối chiếu với NASA, vẽ sơ đồ hệ và đặt giới hạn cho vệ tinh (exomoon).

## Các hệ đã phân tích

| Hệ | Khoảng cách (Gaia DR3) | Kết quả |
|---|---|---|
| Kepler-6 | ≈ 1 906 năm ánh sáng | 1 hành tinh (Kepler-6b), tự tìm thấy bằng transit |
| Kepler-10 | ≈ 607 năm ánh sáng | 3 hành tinh: b, c tự tìm thấy; d bổ sung từ NASA (chỉ phát hiện bằng vận tốc xuyên tâm, không có transit) |
| Kepler-186 | ≈ 579 năm ánh sáng | 5 hành tinh: b–e tự tìm thấy; f tín hiệu yếu, BLS không tự tìm ra nên kiểm chứng bằng chu kỳ của NASA |
| Kepler-452 | ≈ 1 807 năm ánh sáng | 1 hành tinh (Kepler-452b), tín hiệu yếu, kiểm chứng bằng chu kỳ của NASA |

Không phát hiện vệ tinh nào; với mỗi hành tinh chỉ đặt được giới hạn trên về khối lượng và bán kính vệ tinh. Hai tín hiệu TTV trông như có chu kỳ (Kepler-10b, Kepler-186b) đều được xác định là lỗi đo hoặc nhiễu.

Báo cáo đầy đủ: `outputs/<hệ>_report.md` và `outputs/<hệ>_moons.md`.

## Quy trình

| Bước | Script | Làm gì | Kết quả |
|---|---|---|---|
| 1 | `scripts/01_download.py` | Tải đường cong ánh sáng Kepler (long cadence, mọi quý) từ MAST, ghép và làm phẳng | `data/raw/` (FITS), `data/csv/<hệ>_*_raw.csv`, `_all_flat.csv`, `_star_header.csv` |
| 2 | `scripts/02_analyze.py` | Tìm lặp mọi hành tinh có transit bằng BLS, khớp mô hình transit (batman), tính thông số vật lý và thành phần, đối chiếu NASA Exoplanet Archive và Gaia | `outputs/<hệ>_lightcurve.png`, `_periodogram.png`, `_folded.png`, `_report.md`, `_system.json` |
| 3 | `scripts/03_diagram.py` | Vẽ sơ đồ hệ: quỹ đạo nhìn từ trên xuống (vị trí hành tinh theo ngày), so sánh kích thước, khoảng cách so với Hệ Mặt Trời; thang log | `outputs/<hệ>_diagram.png` |
| 4 | `scripts/04_moons.py` | Tìm vệ tinh qua TTV (lệch thời điểm transit) và OSE (vai trũng quanh transit) | `outputs/<hệ>_moons.png`, `_moons.md`, `data/csv/<hệ>_*_transit_times.csv`, `_ose_profile.csv` |

Hành tinh có tín hiệu yếu (Kepler-186f, Kepler-452b) có thêm ảnh từng lần transit riêng lẻ (`outputs/<hệ>_<hành tinh>_transits.png`) kèm phép thử báo động giả.

## Cài đặt và chạy

Cần Python 3.12 và kết nối mạng (tải dữ liệu, truy vấn NASA và Gaia).

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt     # Linux/macOS: .venv/bin/pip

.venv/Scripts/python scripts/01_download.py "Kepler-10"
.venv/Scripts/python scripts/02_analyze.py  "Kepler-10"
.venv/Scripts/python scripts/03_diagram.py  "Kepler-10"                    # thêm --date 2027-01-01 để xem ngày khác
.venv/Scripts/python scripts/04_moons.py    "Kepler-10"
```

Tên hệ nhận dạng tên sao hoặc mã KIC (vd. `"KIC 11904151"`). Chỉ dùng được cho sao có dữ liệu Kepler nhiệm vụ chính (2009–2013), không dùng được cho dữ liệu K2 hoặc TESS. Mới chạy thử với 4 hệ ở trên; với hệ khác có thể cần chỉnh ngưỡng trong `02_analyze.py`.

`03_diagram.py` vẽ vị trí hành tinh theo ngày chạy, nên chạy lại sẽ ra sơ đồ khác ảnh đang có trong `outputs/` (vẽ ngày 26/10/2026).

## Làm bằng Google Sheets

Mọi bước đều xuất CSV vừa đủ nhỏ để mở bằng Google Sheets, nên có thể làm lại toàn bộ phân tích không cần code. Hướng dẫn từng bước trong phần 6 của `docs/kepler-186.md` và `docs/kepler-452.md`.

## Tài liệu

- `docs/kien-thuc-exoplanet.md`: sổ tay kiến thức nền (Kepler, định dạng FITS, bảng KOI, công thức tính từ transit, tìm vệ tinh, thuật ngữ).
- `docs/kepler-186.md`, `docs/kepler-452.md`: tài liệu đầy đủ cho từng hệ: nguồn dữ liệu kèm link, cách làm bằng Python và Google Sheets, đối chiếu NASA, tài liệu tham khảo.

## Nguồn dữ liệu

- Đường cong ánh sáng: [Kepler, MAST](https://archive.stsci.edu/missions-and-data/kepler), tải qua [Lightkurve](https://lightkurve.github.io/lightkurve/).
- Thông số hành tinh và ứng viên KOI: [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) (bảng `pscomppars`, `q1_q17_dr25_koi`).
- Khoảng cách: [Gaia DR3](https://www.cosmos.esa.int/web/gaia/dr3) (ESA).

## Cấu trúc thư mục

```
data/raw/       FITS gốc tải từ MAST (65 file, 4 hệ)
data/csv/       CSV trung gian, mở được bằng Google Sheets
outputs/        ảnh, báo cáo .md và số liệu .json của từng hệ
scripts/        4 bước xử lý
docs/           tài liệu kiến thức và hướng dẫn
```
