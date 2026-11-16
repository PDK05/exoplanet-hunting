# Exoplanet Hunting

Tự săn hành tinh ngoài Hệ Mặt Trời từ dữ liệu thô của kính thiên văn Kepler: tải đường cong ánh sáng, tự tìm các lần transit, tính thông số từng hành tinh, đối chiếu với NASA, vẽ sơ đồ hệ và đặt giới hạn cho vệ tinh (exomoon).

## Các hệ đã phân tích

| Hệ | Khoảng cách (Gaia DR3) | Kết quả |
|---|---|---|
| Kepler-6 | ≈ 1 906 năm ánh sáng | 1 hành tinh (Kepler-6b), tự tìm thấy bằng transit |
| Kepler-10 | ≈ 607 năm ánh sáng | 3 hành tinh: b, c tự tìm thấy; d bổ sung từ NASA (chỉ phát hiện bằng vận tốc xuyên tâm, không có transit) |
| Kepler-186 | ≈ 579 năm ánh sáng | 5 hành tinh: b–e tự tìm thấy; f tín hiệu yếu, BLS không tự tìm ra nên kiểm chứng bằng chu kỳ của NASA |
| Kepler-452 | ≈ 1 807 năm ánh sáng | 1 hành tinh (Kepler-452b), tín hiệu yếu, kiểm chứng bằng chu kỳ của NASA |
| Kepler-1625 | ≈ 8 000 năm ánh sáng (sai số ~9%) | **Hệ bị tranh cãi** (ứng viên vệ tinh Kepler-1625 b-i). 1 hành tinh, 3 transit, transit dài 19 giờ vượt lưới BLS nên kiểm chứng bằng chu kỳ NASA |
| Kepler-1708 | ≈ 5 700 năm ánh sáng | **Hệ bị tranh cãi** (ứng viên vệ tinh Kepler-1708 b-i). 1 hành tinh, chỉ 2 transit; NASA thiếu T0 nên tự đo thời điểm transit trong light curve |

Không phát hiện vệ tinh nào; với mỗi hành tinh chỉ đặt được giới hạn trên về khối lượng và bán kính vệ tinh. Hai tín hiệu TTV trông như có chu kỳ (Kepler-10b, Kepler-186b) đều được xác định là lỗi đo hoặc nhiễu. Với 2 ứng viên vệ tinh nổi tiếng (Kepler-1625 b-i, Kepler-1708 b-i), chỉ riêng dữ liệu Kepler qua pipeline này **không đủ để xác nhận hay bác bỏ**: giới hạn đặt được xấp xỉ đúng cỡ vệ tinh được tuyên bố (xem mục 3.5 của `docs/khi-quyen-va-tuong-lai.md`).

Báo cáo đầy đủ: `outputs/<hệ>_report.md` và `outputs/<hệ>_moons.md`.

## Quy trình

| Bước | Script | Làm gì | Kết quả |
|---|---|---|---|
| 1 | `scripts/01_download.py` | Tải đường cong ánh sáng Kepler (long cadence, mọi quý) từ MAST, ghép và làm phẳng | `data/raw/` (FITS), `data/csv/<hệ>_*_raw.csv`, `_all_flat.csv`, `_star_header.csv` |
| 2 | `scripts/02_analyze.py` | Tìm lặp mọi hành tinh có transit bằng BLS, khớp mô hình transit (batman), tính thông số vật lý và thành phần, đối chiếu NASA Exoplanet Archive và Gaia | `outputs/<hệ>_lightcurve.png`, `_periodogram.png`, `_folded.png`, `_report.md`, `_system.json` |
| 3 | `scripts/03_diagram.py` | Vẽ sơ đồ hệ: quỹ đạo nhìn từ trên xuống (vị trí hành tinh theo ngày), so sánh kích thước, khoảng cách so với Hệ Mặt Trời; thang log | `outputs/<hệ>_diagram.png` |
| 4 | `scripts/04_moons.py` | Tìm vệ tinh qua TTV (lệch thời điểm transit) và OSE (vai trũng quanh transit) | `outputs/<hệ>_moons.png`, `_moons.md`, `data/csv/<hệ>_*_transit_times.csv`, `_ose_profile.csv` |
| 5 | `scripts/05_atmosphere.py` | Khí quyển: tự đo nhật thực phụ trong dữ liệu Kepler (albedo), lấy phổ HST/Spitzer/JWST đã công bố, độ cao thang, chỉ số TSM/ESM cho JWST | `outputs/<hệ>_atmosphere.png`, `_atmosphere.md`, `data/csv/<hệ>_*_eclipse.csv` |
| 6 | `scripts/06_disputed_spectra.py` | Hành tinh **bị tranh cãi** (không cần dữ liệu Kepler): tải phổ JWST/HST/Spitzer đã công bố qua TAP, phép thử "đường phẳng" χ², so các nhóm/pipeline với nhau, biên độ dự kiến cho khí quyển H/He, hơi nước, CO₂ | `outputs/disputed/<hành tinh>_spectra.png`, `_coverage.png` (mọi phổ JWST/HST đã công bố), `disputed_spectra_summary.png`, `disputed_spectra.md`, `data/csv/disputed/` |
| 7 | `scripts/07_disputed_systems.py` | Sơ đồ 15 hệ bị tranh cãi (Gliese 581, Kapteyn, Barnard, Proxima, α Cen A/B, Fomalhaut, K2-18, TRAPPIST-1, LHS 1140, GJ 1132, GJ 486, 55 Cnc, Kepler-1625, Kepler-1708): hành tinh xác nhận từ NASA + hành tinh **bị bác (✗)** và **ứng viên (?)** từ bài đã công bố, vẽ bằng hàm của bước 3 | `outputs/disputed/<hệ>_diagram.png`, `_system.json`, `disputed_systems.md` |

Hệ số tối rìa của sao lấy riêng cho từng sao từ bảng KOI DR25 (Claret, theo Teff, logg, [Fe/H]). Báo cáo `outputs/<hệ>_report.md` có mục **Hình ảnh** chèn mọi ảnh của hệ.

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
.venv/Scripts/python scripts/05_atmosphere.py "Kepler-10"

.venv/Scripts/python scripts/06_disputed_spectra.py                        # các hành tinh bị tranh cãi, hoặc thêm tên vd. "K2-18 b"
.venv/Scripts/python scripts/07_disputed_systems.py --date 2026-11-16      # sơ đồ các hệ bị tranh cãi
```

Cờ đã dùng cho từng hệ: Kepler-186 `01_download.py --flatten-window 101 --mask-known`, `02_analyze.py --max-period 150 --verify-archive`; Kepler-452 `01_download.py --sheet-quarter 3`, `02_analyze.py --min-period 300 --max-period 450 --verify-archive`. Kepler-6, Kepler-10 dùng mặc định. Kepler-1625 `01_download.py --mask-known`, `02_analyze.py --min-period 200 --max-period 450 --verify-archive`; Kepler-1708 `01_download.py --mask-known --ephemeris 737.1131 772.205 19`, `02_analyze.py --min-period 200 --max-period 480 --verify-archive --ephemeris 737.1131 772.205 19` (`--ephemeris P T0_BKJD T14_giờ` dùng khi NASA thiếu T0/T14).

Tên hệ nhận dạng tên sao hoặc mã KIC (vd. `"KIC 11904151"`). Chỉ dùng được cho sao có dữ liệu Kepler nhiệm vụ chính (2009–2013), không dùng được cho dữ liệu K2 hoặc TESS. Đã chạy với 6 hệ ở trên; với hệ khác có thể cần chỉnh ngưỡng trong `02_analyze.py`. Bước 6 thì ngược lại: chỉ cần tên hành tinh trên NASA, không cần dữ liệu Kepler; nhưng chỉ tải được điểm phổ có trong bảng `transitspec`/`emissionspec`. Các phổ JWST mới (K2-18 b 2023/2025, TRAPPIST-1 e/f, LHS 1140 b, 55 Cnc e, GJ 1132 b) chỉ có trong bảng `spectra`, phải tải bằng nút "Download All Checked Spectra" trên web nên chưa được kiểm tra.

`03_diagram.py` vẽ vị trí hành tinh theo ngày chạy, nên chạy lại sẽ ra sơ đồ khác ảnh đang có trong `outputs/` (vẽ ngày 26/10/2026).

## Làm bằng Google Sheets

Mọi bước đều xuất CSV vừa đủ nhỏ để mở bằng Google Sheets, nên có thể làm lại toàn bộ phân tích không cần code. Hướng dẫn từng bước trong phần 6 của `docs/kepler-186.md` và `docs/kepler-452.md`.

## Tài liệu

- `docs/kien-thuc-exoplanet.md`: sổ tay kiến thức nền (Kepler, định dạng FITS, bảng KOI, công thức tính từ transit, tìm vệ tinh, tối rìa, khí quyển, thuật ngữ) và mục 9 mô tả chi tiết code xử lý từng bước.
- `docs/kepler-6.md`, `docs/kepler-10.md`, `docs/kepler-186.md`, `docs/kepler-452.md`: tài liệu đầy đủ cho từng hệ: nguồn dữ liệu kèm link, cách làm bằng Python và Google Sheets, đối chiếu NASA, vệ tinh, khí quyển, hình ảnh.
- `docs/khi-quyen-va-tuong-lai.md`: phổ khí quyển ngoại hành tinh; các tuyên bố "phát hiện sự sống" gần đây (K2-18b, TRAPPIST-1e, LHS 1140 b) và các hệ từng bị tranh cãi hoặc bác bỏ (Gliese 581g, Alpha Cen Bb, Barnard b, GJ 1132 b, Kepler-1625b-i…), độ tin cậy thống kê và cách báo chí đưa tin; thấu kính hấp dẫn Mặt Trời và tàu buồm laser, có công thức và hình minh họa nhiều góc nhìn.
- `docs/img/`: ảnh minh họa; `web/` lấy từ Wikimedia Commons (giấy phép tự do, ghi nguồn), `gen/` tự vẽ bằng `docs/img/make_illustrations.py`.

## Nguồn dữ liệu

- Đường cong ánh sáng: [Kepler, MAST](https://archive.stsci.edu/missions-and-data/kepler), tải qua [Lightkurve](https://lightkurve.github.io/lightkurve/).
- Thông số hành tinh và ứng viên KOI: [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) (bảng `pscomppars`, `q1_q17_dr25_koi`).
- Khoảng cách: [Gaia DR3](https://www.cosmos.esa.int/web/gaia/dr3) (ESA).
- Phổ khí quyển đã công bố: NASA Exoplanet Archive (bảng `transitspec`, `emissionspec`, `spectra`); cấp sao J, K từ `pscomppars`.

## Cấu trúc thư mục

```
data/raw/       FITS gốc tải từ MAST (93 file, 6 hệ)
data/csv/       CSV trung gian, mở được bằng Google Sheets
outputs/        ảnh, báo cáo .md và số liệu .json của từng hệ
scripts/        7 bước xử lý
docs/           tài liệu kiến thức và hướng dẫn
```
