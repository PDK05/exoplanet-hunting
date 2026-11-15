# Hệ Kepler-452: săn "người anh họ của Trái Đất" từ A tới Z

Tài liệu tự đủ: gom toàn bộ kiến thức nền (vốn nằm rải rác trong [`kien-thuc-exoplanet.md`](kien-thuc-exoplanet.md)) cộng phần riêng của Kepler-452. Mọi nguồn dữ liệu đều có **link cụ thể**. Có **2 cách làm**: viết code Python (phần 5) hoặc chỉ dùng Google Sheets (phần 6). Kết quả đối chiếu với NASA ở phần 7. Phần 9 là phương án tìm vệ tinh quanh hành tinh (cả Python lẫn Sheets).

Số liệu trong tài liệu được tính thật từ dữ liệu Kepler ngày 26/10/2026.

## Mục lục

0. [Tóm tắt: cần tải gì, ở đâu](#0-tóm-tắt-cần-tải-gì-ở-đâu)
1. [Kiến thức nền: Kepler và phương pháp transit](#1-kiến-thức-nền-kepler-và-phương-pháp-transit)
2. [Kiến thức nền: dữ liệu Kepler và file FITS](#2-kiến-thức-nền-dữ-liệu-kepler-và-file-fits)
3. [Kiến thức nền: từ transit tính ra được gì, công thức](#3-kiến-thức-nền-từ-transit-tính-ra-được-gì-công-thức)
4. [Hệ Kepler-452: lý lịch và tranh cãi](#4-hệ-kepler-452-lý-lịch-và-tranh-cãi)
5. [Phương án A: chơi bằng code Python](#5-phương-án-a-chơi-bằng-code-python)
6. [Phương án B: chỉ dùng Google Sheets](#6-phương-án-b-chỉ-dùng-google-sheets)
7. [Kết quả và so sánh với NASA](#7-kết-quả-và-so-sánh-với-nasa)
8. [Những bài học riêng từ Kepler-452](#8-những-bài-học-riêng-từ-kepler-452)
9. [Tìm vệ tinh quanh Kepler-452b](#9-tìm-vệ-tinh-quanh-kepler-452b)
10. [Bảng thuật ngữ](#10-bảng-thuật-ngữ)
11. [Tài liệu tham khảo](#11-tài-liệu-tham-khảo)

---

## 0. Tóm tắt: cần tải gì, ở đâu

### 0.1. Thẻ căn cước của hệ

| | Giá trị |
|---|---|
| Tên sao | **Kepler-452** = **KIC 8311864** = KOI-7016 = Gaia DR3 2079597124345617280 |
| Tọa độ | RA 296.003679°, Dec +44.27756° (chòm Thiên Nga) |
| Cấp sao Kepler | Kp = 13.43 (khá mờ: mờ hơn Kepler-10 khoảng 12 lần) |
| Hành tinh | **Kepler-452 b** (KOI K07016.01), chu kỳ **384.8 ngày**, chỉ có **4 transit** trong 4 năm Kepler |
| Transit sâu | chỉ **~160–190 ppm** (0.016–0.019%), nhỏ hơn cả độ nhiễu của một điểm đo (~120 ppm) |

### 0.2. Có cần tải hết dữ liệu không?

| Mục đích | Cần những file nào |
|---|---|
| **Tự tìm chu kỳ từ đầu** (không biết trước đáp án) | **Cả 18 file** Q0–Q17. ⚠️ Nhưng làm vậy sẽ **thất bại** với hành tinh này (xem mục 5.3, 8.1). |
| **Kiểm chứng + tính thông số** khi đã biết P, T0 của NASA | **Chỉ 4 file**: Q3, Q7, Q11, Q15 (mỗi file chứa đúng 1 transit). Đây là đường ngắn nhất, cả Python lẫn Sheets. |
| Thông tin sao mẹ (KIC) | Có sẵn trong header của **bất kỳ** file FITS nào ở trên |
| Đáp án NASA | 3 link truy vấn ở mục 0.4 (trả về CSV, mở thẳng được) |
| Khoảng cách | 1 link truy vấn Gaia ở mục 0.5 |

### 0.3. Light curve: link tải từng file

Thư mục gốc chứa đủ 18 file (MAST, miễn phí, không cần tài khoản):
**https://archive.stsci.edu/missions/kepler/lightcurves/0083/008311864/**

> Quy tắc đường dẫn: `.../lightcurves/<4 chữ số đầu của KIC 9 chữ số>/<KIC 9 chữ số>/`. KIC 8311864 → `008311864` → thư mục `0083/008311864/`.

**4 file chứa transit** (tải từng file bằng cách bấm link):

| Transit | Thời điểm giữa transit (BKJD) | Ngày (UTC) | Quý | File |
|---|---|---|---|---|
| 0 | 314.985 | 12/11/2009 | **Q3** | [kplr008311864-2009350155506_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0083/008311864/kplr008311864-2009350155506_llc.fits) |
| 1 | 699.828 | 02/12/2010 | **Q7** | [kplr008311864-2010355172524_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0083/008311864/kplr008311864-2010355172524_llc.fits) |
| 2 | 1084.671 | 22/12/2011 | **Q11** | [kplr008311864-2012004120508_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0083/008311864/kplr008311864-2012004120508_llc.fits) |
| 3 | 1469.514 | 10/01/2013 | **Q15** | [kplr008311864-2013011073258_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0083/008311864/kplr008311864-2013011073258_llc.fits) |

<details open>
<summary>Danh sách đủ 18 file (bấm để mở)</summary>

| Quý | File | Khoảng thời gian (BKJD) |
|---|---|---|
| Q0 | kplr008311864-2009131105131_llc.fits | 120.5 – 130.2 |
| Q1 | kplr008311864-2009166043257_llc.fits | 131.5 – 165.0 |
| Q2 | kplr008311864-2009259160929_llc.fits | 169.5 – 258.5 |
| **Q3** | kplr008311864-2009350155506_llc.fits | 260.2 – 349.5 |
| Q4 | kplr008311864-2010078095331_llc.fits | 352.4 – 442.2 |
| Q5 | kplr008311864-2010174085026_llc.fits | 443.5 – 538.2 |
| Q6 | kplr008311864-2010265121752_llc.fits | 539.4 – 629.3 |
| **Q7** | kplr008311864-2010355172524_llc.fits | 630.2 – 719.5 |
| Q8 | kplr008311864-2011073133259_llc.fits | 735.4 – 802.3 |
| Q9 | kplr008311864-2011177032512_llc.fits | 808.5 – 905.9 |
| Q10 | kplr008311864-2011271113734_llc.fits | 906.8 – 1000.3 |
| **Q11** | kplr008311864-2012004120508_llc.fits | 1001.2 – 1098.3 |
| Q12 | kplr008311864-2012088054726_llc.fits | 1099.4 – 1182.0 |
| Q13 | kplr008311864-2012179063303_llc.fits | 1182.7 – 1273.1 |
| Q14 | kplr008311864-2012277125453_llc.fits | 1274.1 – 1371.3 |
| **Q15** | kplr008311864-2013011073258_llc.fits | 1373.5 – 1471.1 |
| Q16 | kplr008311864-2013098041711_llc.fits | 1472.1 – 1558.0 |
| Q17 | kplr008311864-2013131215648_llc.fits | 1559.2 – 1591.0 |

Mỗi file 75–500 KB, tổng ~7.5 MB. Mọi file đều là *long cadence* (29.4 phút/điểm).
</details>

Cách khác để tới cùng dữ liệu:
- **MAST Portal** (giao diện web, tìm theo tên): https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html → gõ `Kepler-452` → lọc *Mission = Kepler*, *Product type = timeseries* → tải các file `_llc.fits`.
- **Python `lightkurve`**: `lk.search_lightcurve("Kepler-452", author="Kepler", cadence="long")` (script `01_download.py` làm việc này).
- **CSV đã chuyển sẵn trong repo** (`data/csv/`, xem mục 5.4): dùng thẳng cho Google Sheets, khỏi phải xử lý FITS.

### 0.4. Dữ liệu NASA: lấy ở đâu, lấy cái gì

**NASA Exoplanet Archive** (Caltech/IPAC) là nơi chứa "đáp án". Có 2 cách xem:

**a) Trang tổng quan (xem bằng mắt):** https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-452
Trang này liệt kê **mọi bộ thông số đã công bố** cho Kepler-452 b, mỗi bộ một nguồn (bài báo hoặc bảng KOI). Có 6 bộ, chênh nhau khá nhiều (xem mục 7.3).

**b) Truy vấn TAP (trả về CSV, dán vào trình duyệt là tải được, hoặc dùng `IMPORTDATA` trong Sheets):**

| Bảng | Là gì | Link truy vấn |
|---|---|---|
| `pscomppars` | **Planetary Systems Composite**: mỗi hành tinh 1 dòng, ghép từ nhiều nguồn để đủ cột. Tiện nhưng **lẫn nguồn** (mục 8.4) | [link](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,pl_orbper,pl_tranmid,pl_trandur,pl_trandep,pl_ratror,pl_rade,pl_bmasse,pl_bmassprov,pl_orbsmax,pl_orbincl,pl_imppar,pl_ratdor,pl_eqt,pl_insol,st_teff,st_rad,st_mass,st_met,st_logg,st_age,sy_dist,sy_plx,pl_controv_flag+from+pscomppars+where+hostname='Kepler-452'&format=csv) |
| `ps` | **Planetary Systems**: mỗi bộ thông số đã công bố là 1 dòng; dòng `default_flag = 1` là bộ "chuẩn" (Jenkins et al. 2015) | [link](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,default_flag,pl_refname,pl_orbper,pl_tranmid,pl_trandur,pl_ratror,pl_ratdor,pl_imppar,pl_rade,pl_orbsmax,pl_eqt,pl_insol,st_rad,st_mass,st_teff,st_logg,st_met+from+ps+where+hostname='Kepler-452'&format=csv) |
| `q1_q17_dr25_koi` | **Bảng KOI DR25**: kết quả pipeline Kepler (bản cuối) | [link](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+kepoi_name,kepler_name,koi_disposition,koi_pdisposition,koi_score,koi_period,koi_time0bk,koi_duration,koi_depth,koi_prad,koi_ror,koi_dor,koi_impact,koi_model_snr,koi_max_mult_ev,koi_num_transits,koi_steff,koi_srad,koi_smass,koi_slogg+from+q1_q17_dr25_koi+where+kepid=8311864&format=csv) |

Giao diện bảng (lọc/tải bằng chuột, không cần viết truy vấn):
- Composite: https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PSCompPars
- KOI DR25: https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=q1_q17_dr25_koi
- Giải thích từng cột: https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html (bảng PS) và https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html (bảng KOI)

**Các cột cần dùng và giá trị thực tế của Kepler-452 b:**

| Cột | Ý nghĩa | pscomppars | KOI DR25 |
|---|---|---|---|
| `pl_orbper` / `koi_period` | Chu kỳ (ngày) | 384.843 | 384.847556 |
| `pl_tranmid` / `koi_time0bk` | Thời điểm giữa transit đầu (BJD / BKJD) | 2455147.985 (= BKJD 314.985) | 314.97 |
| `pl_trandur` / `koi_duration` | Thời lượng T14 (giờ) | 10.63 | 9.969 |
| `pl_trandep` / `koi_depth` | Độ sâu (**pscomppars tính bằng %**, KOI bằng ppm) | 0.0199% = 199 ppm | 189.9 ppm |
| `pl_ratror` / `koi_ror` | Rp/Rs | 0.0128 | 0.012491 |
| `pl_imppar` / `koi_impact` | Tham số va chạm b | 0.69 | 0.059 |
| `pl_ratdor` / `koi_dor` | a/Rs | 281.6 ⚠️ | 298.1 |
| `pl_rade` / `koi_prad` | Bán kính hành tinh (R⊕) | **1.63** | **1.09** |
| `pl_bmasse`, `pl_bmassprov` | Khối lượng (M⊕) và cách có được | 3.29, *M-R relationship* (ước tính, **không đo**) | — |
| `pl_orbsmax` | Bán trục lớn (AU) | 1.046 | — |
| `pl_eqt` / `koi_teq` | Nhiệt độ cân bằng (K) | 265 | 220 |
| `pl_insol` / `koi_insol` | Bức xạ nhận (× Trái Đất) | 1.10 | 0.56 |
| `st_rad` / `koi_srad` | Bán kính sao (R☉) | **1.11** | **0.798** |
| `st_mass` / `koi_smass` | Khối lượng sao (M☉) | 1.037 | 0.892 |
| `st_teff` / `koi_steff` | Nhiệt độ sao (K) | 5757 | 5579 |
| `st_met` | [Fe/H] | +0.21 | — |
| `st_age` | Tuổi sao (tỷ năm) | 6.0 | — |
| `sy_dist`, `sy_plx` | Khoảng cách (pc), thị sai (mas) | 551.7 pc, 1.784 mas | — |
| `pl_controv_flag` | **Cờ tranh cãi** (1 = sự tồn tại đang bị nghi ngờ) | **1** | — |
| `koi_disposition` | Kết luận | — | CONFIRMED |
| `koi_score` | Độ tin của bộ lọc tự động Robovetter (0–1) | — | 0.771 |
| `koi_model_snr` | SNR của mô hình transit | — | 12.3 |
| `koi_max_mult_ev` | **MES**: độ mạnh tín hiệu khi cộng mọi transit (ngưỡng phát hiện Kepler = 7.1) | — | **7.6** |
| `koi_num_transits` | Số transit | — | 4 |

> Hai cột "NASA" chênh nhau **gấp rưỡi** về bán kính hành tinh. Không phải lỗi: chúng dùng 2 bộ thông số sao khác nhau. Đây là bài học lớn nhất của Kepler-452 (mục 8.2).

### 0.5. Khoảng cách: Gaia DR3

- Truy vấn (CSV): [link](https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=SELECT+source_id,parallax,parallax_error,ruwe,phot_g_mean_mag+FROM+gaiadr3.gaia_source+WHERE+source_id=2079597124345617280)
- Kết quả: thị sai **1.8053 ± 0.0103 mas**, RUWE 1.01, G = 13.39.
- Giao diện web: Gaia Archive https://gea.esac.esa.int/archive/ → *Search* → nhập tọa độ RA/Dec ở mục 0.1, bán kính 5″.

---

## 1. Kiến thức nền: Kepler và phương pháp transit

### 1.1. Kepler làm gì?

Kepler là kính thiên văn không gian của NASA, hoạt động 2009–2013. Kính **nhìn cố định vào một vùng trời** (chòm Thiên Nga – Thiên Cầm) và đo **độ sáng của khoảng 150.000 ngôi sao** liên tục, khoảng 30 phút một lần, trong 4 năm.

Phương pháp **transit (quá cảnh)**: khi hành tinh đi ngang trước mặt ngôi sao, sao **tối đi một chút** rồi sáng lại, và lặp lại **theo chu kỳ**.

```
Độ sáng
  1.000 ─────────┐     ┌──────────────┐     ┌──────
                 │     │              │     │
  0.999          └─────┘              └─────┘
                 ← transit →
                 |←──── chu kỳ (period) ────→|
```

"Săn exoplanet" thực chất là **tìm những chỗ trũng nhỏ, lặp lại đều đặn trong chuỗi độ sáng theo thời gian**.

### 1.2. Lịch sử: Kepler, K2, TESS

| | Kepler | K2 | TESS |
|---|---|---|---|
| Thời gian | 2009–2013 | 2014–2018 | 2018–nay |
| Vùng trời | 1 vùng cố định | ~20 vùng dọc hoàng đạo (mỗi vùng là 1 *campaign* ~80 ngày) | Gần toàn bầu trời |
| Thời gian quan sát mỗi sao | ~4 năm | ~80 ngày | ~27 ngày (có vùng lâu hơn) |
| Mã sao | **KIC** | **EPIC** | **TIC** |
| Tên file | `kplr<KIC>-..._llc.fits` | `ktwo<EPIC>-c<campaign>_llc.fits` | `tess..._lc.fits` |

Tháng 5/2013 Kepler hỏng bánh xe giữ hướng thứ 2 nên kết thúc nhiệm vụ chính; K2 dùng lại con tàu nhưng dữ liệu tách riêng. Dữ liệu Kepler gốc **vẫn public, miễn phí, ở bản cuối cùng DR25** (Data Release 25, xử lý lại toàn bộ Q1–Q17).

**Vì sao Kepler-452b chỉ Kepler mới bắt được?** Chu kỳ 385 ngày nên cần quan sát **liên tục hơn 3 năm** mới thấy ≥ 3 transit. K2 (80 ngày) và TESS (27 ngày/vùng) không đủ dài.

### 1.3. Độ lớn của tín hiệu

$$\text{Độ sâu} \approx \left(\frac{R_{\text{hành tinh}}}{R_{\text{sao}}}\right)^2$$

- Sao Mộc đi qua Mặt Trời: ~1% (10.000 ppm). Kepler-6b (hot Jupiter): ~1%.
- **Trái Đất đi qua Mặt Trời: ~84 ppm.**
- **Kepler-452b: ~160–190 ppm**, tức chỉ gấp đôi "Trái Đất qua Mặt Trời".

### 1.4. False positive (tín hiệu giả)

Tín hiệu trông giống transit nhưng không phải hành tinh: **sao đôi che khuất nhau** (eclipsing binary), ánh sáng **sao khác ở gần** lọt vào, hoặc (quan trọng với Kepler-452b) **nhiễu hệ thống của thiết bị** tạo ra chỗ trũng giả. Phần lớn công sức thực sự nằm ở việc loại bỏ những trường hợp này.

---

## 2. Kiến thức nền: dữ liệu Kepler và file FITS

### 2.1. Các loại dữ liệu

| Loại | Là gì | Dùng khi nào |
|---|---|---|
| **Light curve** (`*_llc.fits`, `*_slc.fits`) | Bảng độ sáng theo thời gian của 1 ngôi sao | **Bắt đầu từ đây** |
| Target Pixel File (`*_lpd-targ.fits`) | Ảnh pixel thô quanh sao ở từng thời điểm | Nâng cao: tự đo sáng, soi nhiễu |
| **KOI table** | Bảng ứng viên hành tinh NASA đã phân tích | Lấy "đáp án" để kiểm tra |
| **KIC** | Danh mục thông tin các sao | Tra kích thước, nhiệt độ sao |

### 2.2. Mổ xẻ tên file và cấu trúc FITS

FITS là định dạng chuẩn của thiên văn. Một file gồm nhiều **HDU** (Header + Data Unit), giống nhiều "tab":

```
kplr008311864-2009350155506_llc.fits
 │     │           │          │
 │     │           │          └─ llc = long cadence light curve (29.4 phút/điểm)
 │     │           └─ thời điểm tạo file (năm 2009, ngày thứ 350, ...)
 │     └─ KIC ID 9 chữ số: Kepler-452
 └─ kplr = Kepler

HDU 0  PRIMARY     → chỉ có header: thông tin ngôi sao
HDU 1  LIGHTCURVE  → bảng dữ liệu chính
HDU 2  APERTURE    → các pixel được cộng lại để đo sáng
```

⚠️ Google Sheets/Excel **không đọc được FITS**. Phải chuyển sang CSV trước (bằng Python, hoặc phần mềm TOPCAT ở mục 6.1).

### 2.3. Header (HDU 0): thông tin sao. Giá trị thật của Kepler-452

| Khóa | Ý nghĩa | Kepler-452 |
|---|---|---|
| `KEPLERID` | Mã KIC | 8311864 |
| `RA_OBJ`, `DEC_OBJ` | Xích kinh / xích vĩ (độ) | 296.003679, 44.27756 |
| `KEPMAG` | Cấp sao (⚠️ số càng nhỏ càng sáng) | 13.426 |
| `TEFF` | Nhiệt độ bề mặt (K); Mặt Trời 5772 | 5578 |
| `LOGG` | Log gia tốc trọng trường (cgs): sao lùn ~4.4, khổng lồ ~2–3 | 4.578 |
| `FEH` | Độ kim loại [Fe/H] | −0.24 |
| `RADIUS` | Bán kính sao (R☉) | **0.794** ⚠️ (phổ học cho 1.11, xem mục 8.2) |
| `QUARTER` | Quý (Q0–Q17, mỗi quý ~90 ngày, mỗi quý một file) | |

Các giá trị KIC này được đo bằng **ảnh chụp qua vài kính lọc màu** (trắc quang) trước khi phóng Kepler, nên khá thô.

### 2.4. Bảng dữ liệu (HDU 1)

| Cột | Ý nghĩa | Ghi chú |
|---|---|---|
| `TIME` | Thời điểm đo, đơn vị **BKJD** = BJD − 2454833 (ngày) | BJD là thời gian đã quy về tâm Hệ Mặt Trời |
| `SAP_FLUX` | Độ sáng **thô** (e⁻/s) | Còn nhiễu thiết bị |
| `PDCSAP_FLUX` | Độ sáng **đã làm sạch** nhiễu hệ thống | ✅ **Dùng cột này** |
| `PDCSAP_FLUX_ERR` | Sai số | |
| `SAP_QUALITY` | **Cờ chất lượng**: 0 = tốt | Bỏ các dòng khác 0 |
| `MOM_CENTR1/2` | Vị trí tâm sáng trên cảm biến | Phát hiện sao nhiễu lân cận |

Dữ liệu có nhiều **NaN** (lần đo hỏng), phải lọc bỏ. Với Kepler-452: mỗi quý ~3.700–4.400 dòng tốt; độ nhiễu mỗi điểm ~**120 ppm**.

### 2.5. Quy trình chuẩn xử lý một light curve

1. **Lọc**: bỏ dòng `SAP_QUALITY ≠ 0` và NaN.
2. **Chuẩn hóa**: chia mỗi quý cho trung vị của quý đó (độ sáng tuyệt đối mỗi quý lệch nhau vì sao rơi vào cảm biến khác).
3. **Làm phẳng (flatten / detrend)**: chia cho đường xu hướng chậm (trung bình trượt vài ngày) để loại biến thiên của sao và thiết bị. Cửa sổ phải **dài hơn ≥ 3 lần thời lượng transit** để không "là phẳng" luôn transit; Kepler-452b dài 10.6 giờ → cửa sổ ≥ 1.5 ngày (script dùng 901 điểm ≈ 18 ngày).
4. **Tìm chu kỳ** bằng **BLS** (Box Least Squares): thử hàng nghìn chu kỳ, mỗi chu kỳ đo xem gấp dữ liệu lại có "hộp trũng" nào không.
5. **Gấp pha (phase fold)**: chồng các transit lên nhau theo chu kỳ, cộng tín hiệu lại.
6. **Khớp mô hình** transit (có tối rìa + nhòe phơi sáng) để ra Rp/Rs, b, a/Rs.
7. Kết hợp thông số sao → thông số vật lý. So với NASA.

---

## 3. Kiến thức nền: từ transit tính ra được gì, công thức

### 3.1. Mỗi thông số lấy từ đâu

| Thông số | Nguồn | Với Kepler-452b |
|---|---|---|
| Chu kỳ P, thời điểm T0 | ✅ Light curve | Chỉ 4 transit, tín hiệu yếu → phải dùng P, T0 của NASA |
| Độ sâu, thời lượng T14 | ✅ Light curve | Đo được, sai số ~10% |
| Rp/Rs | ✅ √độ sâu | Đo được |
| b, a/Rs, độ nghiêng i | ✅ Hình dạng transit | ❌ Tín hiệu quá yếu, **không xác định được** |
| Mật độ sao ρ* | ✅ Từ a/Rs và P | ❌ (vì a/Rs không xác định) |
| Rs, Teff, logg sao | 📚 KIC (thô) hoặc **quang phổ** | KIC 0.794 R☉ vs phổ 1.11 R☉ |
| Khối lượng sao Ms | 🔀 g·R²/G, hoặc mô hình tiến hóa sao | 0.87 (KIC) / 1.037 (phổ) |
| Bán kính hành tinh Rp | 🔀 (Rp/Rs) × Rs | **Sai số Rs truyền thẳng vào Rp** |
| Bán trục lớn a | 🔀 Định luật Kepler 3 | |
| Teq, bức xạ | 🔀 Teff, Rs, a | |
| Khoảng cách | 🛰️ Thị sai Gaia | |
| **Khối lượng hành tinh** | ❌ Cần RV hoặc TTV | ❌ **Chưa ai đo được**, chỉ ước tính |
| Độ lệch tâm e | ❌ Gần như không đo được | Giả định e = 0 |
| Thành phần | 🔀 Cần cả Mp lẫn Rp | Chỉ đoán theo bán kính |

### 3.2. Công thức

**Hình học transit** (quỹ đạo tròn):
- $k = R_p/R_s \approx \sqrt{\text{độ sâu}}$ (tối rìa làm transit sâu hơn $k^2$ một chút)
- $\cos i = b/(a/R_s)$
- $T_{14} = \dfrac{P}{\pi}\arcsin\left(\dfrac{\sqrt{(1+k)^2-b^2}}{(a/R_s)\sin i}\right)$

**Mật độ sao từ transit:** $\rho_* = \dfrac{3\pi}{GP^2}\left(\dfrac{a}{R_s}\right)^3$

**Khối lượng sao:** $M_s = gR_s^2/G$ với $g = 10^{\log g}$ (cgs, chia 100 để ra m/s²); hoặc $M_s = \rho_*\cdot\tfrac43\pi R_s^3$.

**Định luật Kepler 3:** $a = \left(\dfrac{GM_sP^2}{4\pi^2}\right)^{1/3}$, dạng tiện tay: $a\,[\text{AU}] = \left(M_s[M_☉]\cdot P[\text{năm}]^2\right)^{1/3}$.

**Năng lượng và nhiệt độ:**
- Độ sáng sao: $L/L_☉ = (R_s/R_☉)^2(T_{eff}/5772)^4$
- Bức xạ nhận: $S/S_⊕ = (L/L_☉)/(a/\text{AU})^2$
- Nhiệt độ cân bằng: $T_{eq} = T_{eff}\sqrt{R_s/(2a)}\,(1-A)^{1/4}$, A = albedo (lấy 0.3 như Trái Đất)

**Vùng có thể sống** (habitable zone, xấp xỉ Kopparapu et al. 2013): mép trong $\sqrt{L/1.06}$ AU, mép ngoài $\sqrt{L/0.36}$ AU. Bản "lạc quan" nới mép trong tới $S \approx 1.78\,S_⊕$ (mức Sao Kim thời trẻ có thể còn nước). Các ngưỡng 1.06 / 0.36 là của sao giống Mặt Trời; thực ra ngưỡng **phụ thuộc nhiệt độ sao** (với Kepler-452, 5757 K: 1.036 / 0.348, gần như nhau; với sao lùn M như Kepler-186 thì khác hẳn, xem [`kepler-186.md`](kepler-186.md) mục 3.2). Script vẽ sơ đồ dùng công thức theo nhiệt độ.

**Xác suất một hành tinh có transit nhìn thấy:** $\approx R_s/a$.

**Khoảng cách từ thị sai:** $d\,[\text{pc}] = 1000/\varpi\,[\text{mas}]$; 1 pc = 3.2616 năm ánh sáng. Tin được khi RUWE < 1.4 và sai số thị sai < 10–20%.

**Khoảng cách thô bằng độ sáng:** $M = 4.74 - 2.5\log_{10}(L/L_☉)$; $d = 10^{(m-M+5)/5}$ pc (bỏ qua bụi nên lệch ±10–20% hoặc hơn).

**Vận tốc xuyên tâm (RV)** sao bị hành tinh kéo:
$$K = \left(\frac{2\pi G}{P}\right)^{1/3}\frac{M_p\sin i}{M_s^{2/3}} \;\approx\; 28.4\,\text{m/s}\cdot\frac{M_p}{M_♃}\left(\frac{P}{1\,\text{năm}}\right)^{-1/3}\left(\frac{M_s}{M_☉}\right)^{-2/3}$$

**Ước tính khối lượng từ bán kính** (Chen & Kipping 2017, dạng R = C·M^S):

| Loại | Khối lượng | Công thức (R⊕, M⊕) | Đảo ngược |
|---|---|---|---|
| Đá | < 2 M⊕ (R < 1.23) | $R = 1.008\,M^{0.279}$ | $M = (R/1.008)^{3.584}$ |
| Kiểu Neptune | 2–130 M⊕ | $R = 0.808\,M^{0.589}$ | $M = (R/0.808)^{1.698}$ |

**Mật độ hành tinh:** $\rho_p = 5.51\,\text{g/cm}^3 \cdot (M/M_⊕)/(R/R_⊕)^3$. **Trọng lực bề mặt:** $g/g_⊕ = (M/M_⊕)/(R/R_⊕)^2$.

**Phân loại theo bán kính:** < 1.6 R⊕ đá; 1.6–4 sub-Neptune (lõi đá + khí H/He hoặc nhiều nước); 4–10 giống Hải Vương; > 10 khí khổng lồ. Ranh giới 1.6 R⊕ quan trọng với Kepler-452b vì nó nằm **đúng sát ranh giới**.

### 3.3. Ba cái bẫy khi khớp hình dạng transit (rút ra từ Kepler-6, Kepler-10)

1. **Nhòe phơi sáng:** mỗi điểm cộng dồn 29.4 phút nên sườn transit bị kéo dài, trông như b lớn. Sửa: lấy trung bình mô hình trong khoảng phơi sáng (*supersampling*).
2. **Tối rìa:** đáy transit cong, không phẳng. Sửa: mô hình vật lý `batman` với hệ số tối rìa bậc hai.
3. **Lưới chu kỳ phải đủ mịn:** sai chu kỳ một chút nhân với nhiều vòng thì transit gấp pha bị nhòe. (Kepler-452b chỉ 3 vòng nên không bị bẫy này, nhưng có bẫy khác: mục 8.1.)

Thêm: hành tinh nhỏ có ingress ngắn hơn rất nhiều so với 29.4 phút thì **b và a/Rs gần như không đo được**. Kepler-452b còn tệ hơn: tín hiệu quá yếu.

---

## 4. Hệ Kepler-452: lý lịch và tranh cãi

### 4.1. Vì sao nổi tiếng

Ngày **23/7/2015**, NASA công bố Kepler-452b (Jenkins et al. 2015) với biệt danh **"Earth 2.0" / "người anh họ lớn tuổi hơn của Trái Đất"**:
- Là hành tinh **gần kích thước Trái Đất đầu tiên** (1.6 R⊕) quay quanh **một sao giống Mặt Trời** (loại G2), trong **vùng có thể sống**.
- Chu kỳ 385 ngày, chỉ dài hơn năm Trái Đất 5%. Nhận bức xạ hơn Trái Đất ~10%.
- Sao mẹ ~6 tỷ năm tuổi, già hơn Mặt Trời ~1.5 tỷ năm, sáng hơn Mặt Trời ~20%.

### 4.2. Vì sao bị tranh cãi (`pl_controv_flag = 1`)

- Tín hiệu **sát ngưỡng phát hiện**: MES = 7.6, trong khi ngưỡng của Kepler là 7.1. Chỉ có 4 transit.
- Hành tinh được "xác nhận" bằng **thống kê** (*validation*: tính xác suất tín hiệu là sao đôi hay sao nền thấp hơn nhiều so với là hành tinh), **không** bằng RV hay quan sát độc lập (sao quá mờ, tín hiệu RV dự kiến chỉ ~0.3 m/s).
- Sau khi Kepler xử lý lại dữ liệu (DR25) và đo được **tỉ lệ tín hiệu giả do nhiễu thiết bị** ở vùng chu kỳ dài + tín hiệu yếu, Mullally et al. (2018) chỉ ra xác suất Kepler-452b là tín hiệu giả **không còn nhỏ đến mức "xác nhận"** được. Hành tinh vẫn nằm trong danh sách confirmed nhưng gắn cờ tranh cãi.
- Bản thân phần 5.3 dưới đây cho thấy điều đó: **BLS mù không tìm ra nó**, có nhiều chỗ trũng giả sâu hơn transit thật.

### 4.3. Hai bộ thông số sao khác nhau

| | KIC (trắc quang, trước 2009) | Jenkins 2015 (quang phổ Keck + mô hình tiến hóa) |
|---|---|---|
| Teff | 5578 K | 5757 K |
| logg | 4.578 | 4.32 |
| Rs | 0.794 R☉ | **1.11 R☉** |
| Ms | 0.87 M☉ | 1.037 M☉ |
| [Fe/H] | −0.24 | +0.21 |
| Tuổi | — | ~6 tỷ năm |

Bảng KOI DR25 (`koi_srad = 0.798`) vẫn dựa trên kiểu thông số KIC, nên ra Rp = 1.09 R⊕. Jenkins dùng Rs = 1.11 nên Rp = 1.63 R⊕. Gaia DR2 sau này (Berger et al. 2018) đo lại Rs = 1.108 R☉, **ủng hộ Jenkins**.

---

## 5. Phương án A: chơi bằng code Python

### 5.1. Cài đặt (1 lần)

Cần Python 3.12. Thư viện: `lightkurve` (tải + đọc FITS), `batman-package` (mô hình transit), `matplotlib`, `requests`, `setuptools` (xem `requirements.txt`).

```bash
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

### 5.2. Chạy 4 bước

```bash
# Bước 1: tải 18 file FITS từ MAST + xuất CSV (thêm --sheet-quarter 3 để CSV thô là quý có transit đầu tiên)
.venv/Scripts/python scripts/01_download.py "Kepler-452" --sheet-quarter 3

# Bước 2: tìm hành tinh trong khoảng chu kỳ 300–450 ngày; nếu BLS không tự tìm ra thì
#         kiểm chứng bằng P, T0 của NASA (--verify-archive) + phép thử báo động giả (~1 phút)
.venv/Scripts/python scripts/02_analyze.py "Kepler-452" --min-period 300 --max-period 450 --verify-archive

# Bước 3: sơ đồ hệ theo thang log
.venv/Scripts/python scripts/03_diagram.py "Kepler-452"

# Bước 4: tìm vệ tinh quanh hành tinh (mục 9)
.venv/Scripts/python scripts/04_moons.py "Kepler-452"
```

Bước 1 tự gọi MAST qua `lightkurve`: `lk.search_lightcurve("Kepler-452", author="Kepler", cadence="long")`, tức **đúng 18 file ở mục 0.3**. Bước 2 tự gọi NASA Exoplanet Archive (bảng `pscomppars`, `q1_q17_dr25_koi`) và Gaia DR3 qua các link TAP ở mục 0.4, 0.5.

**Vì sao `--min-period 300 --max-period 450`?** Thử mọi chu kỳ từ 0.5 tới 450 ngày mất rất lâu (hàng trăm nghìn chu kỳ × 10 thời lượng) mà kết quả cũng không khá hơn. Khoảng 300–450 ngày đủ để minh họa. Chu kỳ tối đa còn bị giới hạn bởi độ dài dữ liệu/3 = 1470/3 = 490 ngày (phải thấy ≥ 3 transit).

**Đã sửa gì trong script để chạy được hệ này?**
- Thêm thời lượng 0.5, 0.6 ngày cho BLS (transit Kepler-452b dài ~0.44 ngày; trước chỉ thử tới 0.4).
- Thêm chế độ `--verify-archive` và phép thử báo động giả (hàm `check_ephemeris`).
- Tăng số vòng lặp khi khớp mô hình (tín hiệu yếu hội tụ chậm).

### 5.3. Chuyện gì xảy ra khi chạy

```
Light curve: 65156 điểm, dài 1470 ngày
BLS: thử 2647 chu kỳ từ 300.00 đến 450.1 ngày
  Vòng 1: P = 433.14288 ngày, độ sâu = 520 ppm, SNR = 25, SDE = 4.4, 1 transit → nhiễu, dừng
BLS không tự tìm ra Kepler-452 b → kiểm chứng bằng P, T0 của NASA
  Kiểm chứng P = 384.8430 ngày: độ sâu = 139 ± 13 ppm, SNR = 11.0, 4 transit;
  0.40% trong 2783 lần chọn bừa P, T0 cho SNR cao bằng
```

1. **BLS mù thất bại.** Đỉnh mạnh nhất (P = 433 ngày) chỉ là **một chỗ trũng giả duy nhất** sâu 520 ppm ở BKJD ~297, do nhiễu thiết bị. Chu kỳ thật 384.85 ngày chỉ **xếp hạng ~800** trong periodogram. Đã thử thêm cửa sổ làm phẳng 2–18 ngày, đổi hàm mục tiêu BLS, chia trọng số theo nhiễu cục bộ: không cách nào đưa nó lên đầu. Pipeline của NASA dùng bộ lọc "làm trắng nhiễu" tinh vi hơn nhiều mà cũng chỉ đạt MES 7.6.
2. **Kiểm chứng thành công.** Gấp pha đúng P, T0 của NASA thì thấy rõ transit với SNR 11 (NASA: 12.3), cả 4 transit đều có mặt.
3. **Phép thử báo động giả:** chọn bừa ~2.800 cặp (P, T0) gần đó, chỉ **0.4%** cho SNR cao bằng. Tức là nếu chỉ thử *một* chu kỳ thì tín hiệu khó là ngẫu nhiên; nhưng khi tìm mù qua hàng nghìn chu kỳ thì 0.4% × hàng nghìn = **hàng chục tín hiệu giả mạnh ngang**. Đây chính là lý do tranh cãi.

### 5.4. File tạo ra

| File | Nội dung | Dùng cho |
|---|---|---|
| `data/raw/mastDownload/Kepler/kplr008311864_lc_Q111111111111111111/` | 18 file FITS gốc (không đưa lên git) | |
| `data/csv/Kepler452_star_header.csv` | Header sao (KIC) | Sheets + Python |
| `data/csv/Kepler452_Q3_raw.csv` | Quý 3 thô (3.736 dòng, có transit 0 ở BKJD 315) | Sheets |
| `data/csv/Kepler452_all_flat.csv` | 18 quý đã ghép + làm phẳng (65.156 dòng) | Python bước 2 |
| `data/csv/Kepler452_Kepler452b_transits.csv` | **4 cửa sổ ±1.5 ngày quanh 4 transit** (581 dòng, đã làm phẳng) | ⭐ **Sheets** |
| `data/csv/Kepler452_Kepler452b_folded.csv` | Transit gấp pha, gộp bin + mô hình | Sheets |
| `outputs/Kepler452_report.md` | Báo cáo đầy đủ | |
| `outputs/Kepler452_lightcurve.png` | Light curve 4 năm | |
| `outputs/Kepler452_periodogram.png` | Periodogram BLS (đỉnh là nhiễu) | |
| `outputs/Kepler452_Kepler452b_transits.png` | **Từng transit riêng + histogram phép thử báo động giả** | |
| `outputs/Kepler452_folded.png` | Transit gấp pha + mô hình batman | |
| `outputs/Kepler452_diagram.png` | Sơ đồ hệ (thang log) | |
| `outputs/Kepler452_system.json` | Số liệu cả hệ | Bước 3, 4 |
| `outputs/Kepler452_moons.md`, `Kepler452_moons.png` | Bước 4: tìm vệ tinh | |
| `data/csv/Kepler452_Kepler452b_transit_times.csv` | Thời điểm 4 transit + O − C | Sheets (mục 9.4) |
| `data/csv/Kepler452_Kepler452b_ose_profile.csv` | Transit gấp pha gộp bin trong vùng vệ tinh | Sheets (mục 9.4) |

### 5.5. Đọc kết quả Python

Script dùng **thông số sao KIC** (header FITS) để tính, nên ra Rp = **1.03 R⊕**, a = 0.989 AU, Teq = 220 K. Để so công bằng với NASA (Jenkins), nhân lại bằng thông số sao phổ học (mục 7.1, cột "Python + sao NASA"). Cần nhớ:
- **a/Rs = 287 ± 1415** và **b = 0.20**: sai số lớn gấp 5 lần giá trị, nghĩa là **không đo được**. Khối lượng sao suy từ transit (1.07 ± 15.9 M☉) cũng vô nghĩa, nên script tự quay về dùng logg.
- Độ sâu 169 ppm (mô hình batman, tại tâm) và 139 ppm (hộp BLS, trung bình cả thời lượng) đo hai thứ khác nhau; Rp/Rs = 0.0118 mới là số đáng so.

---

## 6. Phương án B: chỉ dùng Google Sheets

Sheets không chạy được BLS hay khớp mô hình có tối rìa, nhưng **đủ để làm hết phần tính toán** khi đã biết P, T0 (chính là cách hành tinh này phải làm). Kết quả gần như trùng Python (mục 7.1).

> ⚠️ **Dấu phân cách công thức:** Sheets đặt vùng *Việt Nam* thì dùng **dấu chấm phẩy `;`** giữa các đối số và **dấu phẩy** cho số thập phân. Các công thức dưới đây viết theo vùng *United States* (dấu `,` và `.`). Đổi tại **File → Settings → Locale → United States** để dán y nguyên, hoặc tự thay `,` → `;`.

### 6.1. Lấy dữ liệu vào Sheets: 3 lối

**Lối 1 (nhanh nhất): dùng CSV có sẵn trong repo.** Mở `data/csv/Kepler452_Kepler452b_transits.csv` (581 dòng, 4 transit). Bỏ qua 6.2, nhảy thẳng tới 6.3.

**Lối 2 (tự làm từ FITS, không viết code): dùng TOPCAT.**
1. Tải 4 file FITS ở **mục 0.3** (Q3, Q7, Q11, Q15).
2. Cài **TOPCAT** (miễn phí, cần Java): https://www.star.bris.ac.uk/~mbt/topcat/ → tải `topcat-full.jar`, chạy bằng cách nhấp đúp.
3. TOPCAT → **File → Load Table** → chọn file FITS. TOPCAT tự mở HDU 1 (bảng LIGHTCURVE).
4. (Tùy chọn) **Views → Columns Info**, bỏ tick các cột thừa, chỉ giữ `TIME`, `PDCSAP_FLUX`, `PDCSAP_FLUX_ERR`, `SAP_QUALITY` (cột bị ẩn sẽ không được lưu). Rồi **File → Save Table** → Output format **csv**.
5. Làm lại cho 3 file còn lại → 4 file CSV (~3.700–4.400 dòng mỗi file).

**Lối 3 (nửa chừng):** chạy riêng bước 1 Python (`01_download.py`) chỉ để có CSV, phần tính toán làm hết trong Sheets.

### 6.2. Xử lý 1 quý thô trong Sheets (Lối 2, ví dụ transit 0 trong Q3)

Import CSV vào tab `Q3` (**File → Import → Upload → Insert new sheet**). Giả sử A = `TIME`, B = `PDCSAP_FLUX`, C = `PDCSAP_FLUX_ERR`, D = `SAP_QUALITY`.

1. **Lọc dữ liệu tốt** sang tab mới `Q3_good`, ô A1:
   ```
   =FILTER(Q3!A2:B, Q3!D2:D=0, Q3!B2:B<>"", Q3!A2:A<>"")
   ```
2. **Giờ tính từ tâm transit** (tâm transit 0 = BKJD **314.985**; các transit khác: 699.828, 1084.671, 1469.514), ô C1, kéo xuống:
   ```
   =(A1-314.985)*24
   ```
3. **Đường xu hướng** (trung vị trượt 145 điểm ≈ 3 ngày), ô D1, kéo xuống:
   ```
   =MEDIAN(INDEX(B:B, MAX(1, ROW()-72)):INDEX(B:B, MIN(COUNT(B:B), ROW()+72)))
   ```
4. **Độ sáng đã làm phẳng**, ô E1: `=B1/D1`.
5. **Trung bình trượt 21 điểm (~10 giờ)** để "nhìn" được transit, ô F1: `=AVERAGE(INDEX(E:E, MAX(1, ROW()-10)):INDEX(E:E, ROW()+10))`.
6. Vẽ: chọn cột A và F → **Insert → Chart → Scatter**. Trục dọc min 0.9996, max 1.0003.

**Bạn sẽ thấy gì?** Ở BKJD 315 có chỗ trũng ~130–180 ppm, nhưng trong cùng quý còn **4 chỗ trũng khác sâu hơn** (BKJD ~297, 336, 325, 349) là nhiễu thiết bị. Nếu không biết trước đáp án, nhìn bằng mắt sẽ **chọn sai**. Đó chính là bài học của hệ này.

Ghép 4 quý: chép cột C (giờ) và E (độ sáng phẳng) của các dòng có |C| ≤ 36 từ cả 4 tab vào một tab chung, thêm cột số thứ tự transit. Kết quả tương đương file `Kepler452_Kepler452b_transits.csv`.

### 6.3. Tính độ sâu và SNR

Import `Kepler452_Kepler452b_transits.csv` vào tab `transits`: A = `transit_no`, B = `time_bkjd`, C = `hours_from_mid_transit`, D = `flux`.

Tạo tab `calc`. Quy ước: **trong transit** = |giờ| ≤ 4.8 (phần giữa, ±0.2 ngày, tránh sườn); **ngoài transit** = |giờ| ≥ 12.

| Ô | Nội dung | Công thức | Kết quả |
|---|---|---|---|
| B1 | Trung bình trong transit | `=AVERAGE(FILTER(transits!D2:D, ABS(transits!C2:C)<=4.8, transits!D2:D<>""))` | 0.999845 |
| B2 | Trung bình ngoài transit | `=AVERAGE(FILTER(transits!D2:D, ABS(transits!C2:C)>=12, transits!D2:D<>""))` | 1.000010 |
| B3 | **Độ sâu (tỉ lệ)** | `=(B2-B1)/B2` | 0.000167 |
| B4 | Độ sâu (ppm) | `=B3*1E6` | **167** |
| B5 | Số điểm trong transit | `=COUNTIFS(transits!C2:C, ">=-4.8", transits!C2:C, "<=4.8")` | 79 |
| B6 | Số điểm ngoài transit | `=COUNTIFS(transits!C2:C, ">=12")+COUNTIFS(transits!C2:C, "<=-12")` | 387 |
| B7 | Độ nhiễu 1 điểm | `=STDEV(FILTER(transits!D2:D, ABS(transits!C2:C)>=12, transits!D2:D<>""))` | 0.000129 |
| B8 | **SNR** | `=B3/(B7*SQRT(1/B5+1/B6))` | **10.4** |

Độ sâu từng transit: thêm điều kiện `transits!A2:A=0` (rồi 1, 2, 3) vào FILTER của B1, B2. Kết quả: **188, 154, 159, 165 ppm**. Bốn transit gần bằng nhau (chênh nằm trong sai số ~30 ppm mỗi transit) là một dấu hiệu tốt; sao đôi thường cho transit chẵn/lẻ sâu khác nhau.

(Nếu làm theo Lối 2 từ FITS thô với tâm |giờ| ≤ 4.8 và nền 12–36 giờ, sẽ ra ~159 ppm.)

### 6.4. Vẽ transit gấp pha

- **Từng transit chồng lên nhau:** tab `transits`, chọn cột C và D → Scatter. Mọi transit đã chồng tại 0 giờ (vì cột C tính từ tâm từng transit). Trục dọc 0.9994 – 1.0004.
- **Gộp bin cho dễ nhìn:** tab `bins`, A2 = −36, A3 = `=A2+1.5`, kéo tới 36 (bin 1.5 giờ). B2:
  ```
  =IFERROR(AVERAGEIFS(transits!D:D, transits!C:C, ">="&A2, transits!C:C, "<"&A2+1.5), "")
  ```
  Vẽ Scatter A–B: thấy rõ "lòng chảo" rộng ~10 giờ, sâu ~170 ppm.
- **Bản Python đã gộp sẵn + mô hình:** import `Kepler452_Kepler452b_folded.csv` → chọn 3 cột → Scatter; Customize → Series → `model` → chuyển thành Line.
- **Tự gấp pha từ dữ liệu chưa tách transit** (ví dụ cột thời gian A của `Kepler452_all_flat.csv`), với `H1 = 384.843` (P), `H2 = 314.985` (T0):
  ```
  =(MOD(A2 - $H$2 + $H$1/2, $H$1) - $H$1/2) * 24
  ```

### 6.5. Tính thông số vật lý

Tab `params`. Nhập đầu vào (lấy sao NASA vì đáng tin hơn; cột KIC để so sánh):

| Ô | Đầu vào | Sao NASA (Jenkins 2015) | Sao KIC (header FITS) |
|---|---|---|---|
| B1 | Độ sâu (tỉ lệ) | `=calc!B3` | `=calc!B3` |
| B2 | P (ngày) | 384.843 | 384.843 |
| B3 | Rs (R☉) | 1.11 | 0.794 |
| B4 | Ms (M☉) | 1.037 | 0.870 |
| B5 | Teff (K) | 5757 | 5578 |
| B6 | Thị sai Gaia (mas) | 1.8053 | 1.8053 |

Đặt ở cột C cho bộ KIC (cùng công thức, đổi B→C). Có thể lấy thẳng số NASA vào Sheets bằng
`=IMPORTDATA("https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_orbper,pl_tranmid,st_rad,st_mass,st_teff+from+pscomppars+where+hostname='Kepler-452'&format=csv")`.

| Ô | Thông số | Công thức | NASA-sao | KIC-sao |
|---|---|---|---|---|
| B8 | Rp/Rs | `=SQRT(B1)` | 0.0129 | 0.0129 |
| B9 | **Rp (R⊕)** | `=B8*B3*109.1` | **1.56** | 1.12 |
| B10 | **a (AU)** | `=(B4*(B2/365.25)^2)^(1/3)` | **1.048** | 0.989 |
| B11 | Độ sáng sao L (L☉) | `=B3^2*(B5/5772)^4` | 1.22 | 0.55 |
| B12 | **Bức xạ S (× Trái Đất)** | `=B11/B10^2` | **1.11** | 0.56 |
| B13 | **Teq (K), albedo 0.3** | `=B5*SQRT(B3*0.00465/(2*B10))*0.7^0.25` | **261** | 220 |
| B14 | Vùng sống, mép trong (AU) | `=SQRT(B11/1.06)` | 1.07 | 0.72 |
| B15 | Vùng sống, mép ngoài (AU) | `=SQRT(B11/0.36)` | 1.84 | 1.24 |
| B16 | Mép trong "lạc quan" (AU) | `=SQRT(B11/1.78)` | 0.83 | 0.56 |
| B17 | Khối lượng ước tính (M⊕) | `=IF(B9<1.23, (B9/1.008)^3.584, (B9/0.808)^1.698)` | ~3.1 | ~1.4 |
| B18 | Mật độ ước tính (g/cm³) | `=5.51*B17/B9^3` | ~4.4 | — |
| B19 | Trọng lực bề mặt (× Trái Đất) | `=B17/B9^2` | ~1.3 | — |
| B20 | Vận tốc quỹ đạo (km/s) | `=2*PI()*B10*1.496E8/(B2*86400)` | 29.6 | 28.0 |
| B21 | Xác suất có transit (%) | `=B3*0.00465/B10*100` | 0.49 | 0.37 |
| B22 | RV dự kiến K (m/s) | `=28.4*(B17/317.8)*(B2/365.25)^(-1/3)*B4^(-2/3)` | ~0.27 | — |
| B23 | **Khoảng cách (pc)** | `=1000/B6` | **553.9** | |
| B24 | Khoảng cách (năm ánh sáng) | `=B23*3.2616` | **1.807** | |
| B25 | Khoảng cách thô bằng độ sáng (pc) | `=10^((13.426-(4.74-2.5*LOG10(B11))+5)/5)` | ~603 | ~405 |
| B26 | Phân loại | `=IF(B9<1.6,"Đá",IF(B9<4,"Sub-Neptune",IF(B9<10,"Giống Hải Vương","Khí khổng lồ")))` | Đá (sát ranh giới) | Đá |

Lưu ý: B13 dùng 0.00465 = bán kính Mặt Trời tính bằng AU; B20 dùng 1.496E8 km/AU.

### 6.6. Dự đoán transit tiếp theo

Ô `T0_BJD = 2455147.985`, `P = 384.843`. Transit thứ n: `=T0_BJD + n*P`. Đổi BJD sang ngày thường: `=T0_BJD + n*P - 2415018.5` rồi định dạng ô là **Date time** (Sheets đếm ngày từ 30/12/1899 = JD 2415018.5).

| n | BJD | Ngày (UTC) |
|---|---|---|
| 16 | 2461305.47 | 21/09/2026 |
| 17 | 2461690.32 | **11/10/2027** |
| 18 | 2462075.16 | 30/10/2028 |

Sai số chu kỳ ±0.01 ngày nhân 17 vòng → dự đoán lệch được vài giờ. (Không kính nào hiện nay đo nổi transit 170 ppm của một sao Kp 13.4 từ mặt đất; tương lai có thể là PLATO của ESA.)

### 6.7. Giới hạn của Sheets

Sheets **không** tự tìm được chu kỳ (BLS), không khớp được mô hình có tối rìa (nên không ra b, a/Rs, độ nghiêng), không chạy được phép thử báo động giả hàng nghìn lần. Với Kepler-452b thì Python cũng không làm được mấy việc đó một cách đáng tin, nên **khoảng cách giữa 2 phương án nhỏ hơn mọi hệ khác**.

---

## 7. Kết quả và so sánh với NASA

### 7.1. Bảng tổng hợp

"Python + sao NASA" = Rp/Rs do Python đo nhân với Rs, Ms, Teff của Jenkins 2015 (tính tay theo công thức mục 3.2).

| Thông số | Python (sao KIC) | Python + sao NASA | Sheets (sao NASA) | NASA KOI DR25 | NASA chuẩn (Jenkins 2015) |
|---|---|---|---|---|---|
| Chu kỳ P (ngày) | 384.843 (lấy của NASA) | | 384.843 | 384.8476 | 384.843 |
| Tìm được bằng BLS mù? | ❌ (xếp hạng ~800) | | ❌ | ✅ MES 7.6 | ✅ |
| Số transit | 4 | | 4 | 4 | 4 |
| SNR | 11.0 | | 10.4 | 12.3 | |
| Độ sâu (ppm) | 169 (tâm, mô hình) | | 167 | 189.9 | 199 |
| T14 (giờ) | 10.16 | | — | 9.97 | 10.63 |
| Rp/Rs | 0.0118 | 0.0118 | 0.0129 | 0.0125 | 0.0128 |
| b | 0.20 (không xác định) | | — | 0.059 | 0.69 |
| a/Rs | 287 ± 1415 (không xác định) | | — | 298.1 | 281.6* |
| Rs (R☉) | 0.794 | 1.11 | 1.11 | 0.798 | 1.11 |
| Ms (M☉) | 0.870 (logg KIC) | 1.037 | 1.037 | 0.892 | 1.037 |
| **Rp (R⊕)** | 1.03 | **1.43** | **1.56** | 1.09 | **1.63** |
| **a (AU)** | 0.989 | 1.048 | 1.048 | — | 1.046 |
| **Bức xạ (× Trái Đất)** | 0.56 | 1.11 | 1.11 | 0.56 | 1.10 |
| **Teq (K)** | 220 | 261 | 261 | 220 | 265 |
| Khối lượng | ~1.1 M⊕ (ước tính) | ~2.6 M⊕ (ước tính) | ~3.1 M⊕ (ước tính) | — | 3.29 M⊕ (*ước tính* M-R) |
| Mật độ (g/cm³) | — | | ~4.4 | — | 4.17 (cũng từ ước tính) |
| Khoảng cách | Gaia DR3: **553.9 ± 3.2 pc ≈ 1.807 năm ánh sáng** | | 553.9 pc | — | 551.7 pc |

\* a/Rs = 281.6 trong bảng composite lấy từ **KOI DR24** (dùng sao KIC), không khớp với Rs = 1.11 của Jenkins. Tính lại cho khớp: a/Rs = 1.046 AU / (1.11 × 0.00465 AU) ≈ **203** (mục 8.4).

### 7.2. Đọc bảng

- **Phần "chỉ cần light curve"** (Rp/Rs, độ sâu, T14, SNR): Python và Sheets khớp NASA trong khoảng 5–15%, hợp lý với tín hiệu SNR ~11. Độ sâu của mình thấp hơn NASA ~10%, một phần do bước làm phẳng ăn bớt tín hiệu và do cách đo khác nhau (trung bình phần giữa vs. mô hình đầy đủ).
- **Phần "cần biết sao"** (Rp, a, S, Teq): lệch **hoàn toàn do bộ thông số sao**. Cùng một Rp/Rs, dùng sao KIC ra hành tinh 1.1 R⊕ nhận 56% bức xạ Trái Đất (lạnh hơn sao Hỏa một chút); dùng sao phổ học ra 1.6 R⊕ nhận 110% (ấm hơn Trái Đất). Hai "hành tinh" khác hẳn nhau.
- **Phần "không đo được"** (b, a/Rs, khối lượng): cả mình lẫn NASA đều không có số thật. Khối lượng 3.29 M⊕ trên NASA chỉ là ước tính từ bán kính (`pl_bmassprov = M-R relationship`), chính là công thức Chen & Kipping ở mục 3.2.
- **Khoảng cách:** Jenkins 2015 ước tính 430 pc (~1.400 năm ánh sáng, con số báo chí hay dùng). Gaia đo thị sai trực tiếp cho **~554 pc ≈ 1.800 năm ánh sáng**, xa hơn 30%. Ước tính bằng độ sáng với sao KIC chỉ ra ~405 pc, vì sao KIC bị đánh giá quá nhỏ và mờ.

### 7.3. Sáu bộ thông số trên NASA cho cùng một hành tinh

Lấy từ bảng `ps` (link ở mục 0.4):

| Nguồn | Rs (R☉) | Rp (R⊕) | S (× Trái Đất) |
|---|---|---|---|
| KOI DR24 | 0.794 | 1.13 | 0.56 |
| KOI DR25 | 0.798 | 1.09 | 0.56 |
| **Jenkins et al. 2015** (mặc định) | **1.11** | **1.63** | **1.10** |
| KOI DR25 Supplemental | 1.119 | — | — |
| Berger et al. 2018 (Gaia DR2) | 1.108 | 1.51 | 1.09 |
| Morton et al. 2016 | 1.06 | 1.50 | — |

Các nguồn dùng thông số sao hiện đại (Jenkins, Berger, Morton) đều cho **Rp ≈ 1.5–1.6 R⊕**, khớp với kết quả Sheets 1.56 R⊕.

### 7.4. Vậy Kepler-452b là hành tinh thế nào?

- **Kích thước:** ~1.5–1.6 R⊕, ngay **ranh giới đá / sub-Neptune** (1.6 R⊕). Thống kê cho thấy hành tinh cỡ này có khả năng ~50/50 là đá, hoặc có lớp khí H/He mỏng. Chưa có khối lượng nên chưa kết luận được.
- **Nếu là đá** với ~3–5 M⊕: trọng lực bề mặt ~1.3–2 lần Trái Đất.
- **Khí hậu:** nhận ~1.1 lần bức xạ Trái Đất, a = 1.048 AU nằm **ngay trong mép trong** của vùng có thể sống bảo thủ (1.07 AU), nhưng nằm gọn trong vùng "lạc quan" (0.83–1.84 AU). Sao mẹ già 6 tỷ năm đang sáng dần lên, nên hành tinh có thể đang ở giai đoạn hiệu ứng nhà kính tăng dần như Trái Đất sau ~1 tỷ năm nữa.
- **Tồn tại hay không:** khả năng cao là có, nhưng chưa được xác nhận độc lập.

---

## 8. Những bài học riêng từ Kepler-452

### 8.1. Tín hiệu sát ngưỡng: BLS "mù" bị nhiễu đỏ đánh lừa

Nhiễu của Kepler không chỉ là nhiễu ngẫu nhiên từng điểm (*nhiễu trắng*) mà còn có **nhiễu đỏ** (*red noise / correlated noise*): các điểm liền nhau cùng lệch một hướng trong vài giờ, do tàu rung, nhiệt độ thay đổi, tia vũ trụ làm hỏng pixel... Một đợt nhiễu đỏ dài ~10 giờ trông y hệt một transit.

- Với hành tinh lớn (Kepler-6b sâu 10.000 ppm) nhiễu đỏ không đáng kể. Với Kepler-452b sâu ~170 ppm, chỉ trong quý Q3 đã có **4 chỗ trũng giả sâu hơn** transit thật.
- BLS chuẩn giả định nhiễu trắng, nên đánh giá quá cao các chỗ trũng giả đơn lẻ. Pipeline NASA dùng bộ lọc *whitening* (làm trắng nhiễu theo thang thời gian) và chỉ nhận tín hiệu có **MES ≥ 7.1**.

### 8.2. Muốn biết hành tinh, phải biết rõ sao mẹ

Kepler-452 là ví dụ cực đoan: KIC đánh giá sao **nhỏ hơn 30%** (0.794 vs 1.11 R☉) vì logg trắc quang sai (4.58 vs 4.32). Hệ quả dây chuyền: Rp nhỏ đi 30%, độ sáng sao nhỏ đi một nửa, bức xạ hành tinh nhận được giảm một nửa, Teq lạnh đi 40 K. Từ "siêu Trái Đất ấm" biến thành "Trái Đất lạnh". Ở Kepler-6 sai số này chỉ 10%.

**Thứ tự tin cậy thông số sao:** KIC (trắc quang) < quang phổ phân giải cao < quang phổ + thị sai Gaia (biết khoảng cách + độ sáng biểu kiến → độ sáng thật → bán kính).

### 8.3. "Kiểm chứng" khác "phát hiện"

- **Phát hiện:** tìm mù trên hàng nghìn chu kỳ, phải vượt ngưỡng rất cao vì thử nhiều lần thì kiểu gì cũng có cái "trông giống" do may rủi (*vấn đề so sánh bội* / *look-elsewhere effect*).
- **Kiểm chứng:** đã biết P, T0 từ nguồn khác, chỉ hỏi "ở đúng chỗ đó có tín hiệu không?". Ngưỡng thấp hơn nhiều.
- Phép thử báo động giả (mục 5.3) nối hai thứ đó: 0.4% cho một lần thử là nhỏ, nhưng nhân với số chu kỳ đã thử thì không còn nhỏ.

### 8.4. Bảng composite trên NASA ghép nhiều nguồn

`pscomppars` lấy mỗi cột từ nguồn "tốt nhất có cột đó". Với Kepler-452b, `pl_ratdor = 281.6` đến từ KOI DR24 (sao KIC) trong khi `st_rad = 1.11` đến từ Jenkins. Ghép lại thì mâu thuẫn (a/Rs đúng phải ~203). Khi cần một bộ số **nhất quán**, dùng bảng `ps` và lọc theo **một** `pl_refname`.

### 8.5. Vì sao chưa đo được khối lượng

RV dự kiến chỉ **~0.3 m/s** (Trái Đất làm Mặt Trời dao động 0.09 m/s). Kính tốt nhất hiện nay (ESPRESSO) đạt ~0.3–0.5 m/s cho sao **sáng**; Kepler-452 mờ (Kp = 13.4) và hành tinh cần theo dõi nhiều năm (chu kỳ 385 ngày). TTV cũng không áp dụng được vì hệ chỉ có 1 hành tinh đã biết.

---

## 9. Tìm vệ tinh quanh Kepler-452b

### 9.1. Kiến thức nền

**Thực tế:** tới nay **chưa có vệ tinh ngoài Hệ Mặt Trời (exomoon) nào được xác nhận**. Hai ứng viên nổi tiếng đều từ dữ liệu Kepler và đều đang bị tranh cãi: Kepler-1625b-i (Teachey & Kipping 2018, cỡ Sao Hải Vương) và Kepler-1708b-i (Kipping et al. 2022). Với dữ liệu Kepler, mục tiêu thực tế là **đặt giới hạn trên**: "nếu có vệ tinh thì nó không thể to/nặng hơn X".

**Bước 1. Vệ tinh có thể tồn tại ở đâu?**

| Đại lượng | Công thức | Ý nghĩa |
|---|---|---|
| Bán kính Hill | $R_H = a\left(\dfrac{M_p}{3M_s}\right)^{1/3}$ | Vùng lực hút hành tinh thắng lực hút sao |
| Quỹ đạo bền xa nhất | $a_{max} \approx 0.49\,R_H$ (cùng chiều; ngược chiều ~0.93 R_H; Domingos et al. 2006) | Xa hơn thì bị sao mẹ giật mất |
| Giới hạn Roche | $a_R \approx 2.44\,R_p(\rho_p/\rho_v)^{1/3}$, lấy vệ tinh đá $\rho_v$ = 3 g/cm³ | Gần hơn thì vệ tinh bị thủy triều xé vụn |
| Chu kỳ vệ tinh dài nhất | $P_{v,max} = 2\pi\sqrt{a_{max}^3/(GM_p)}$ | |
| Vận tốc quỹ đạo hành tinh | $v_p = 2\pi a/P$ | |
| Vệ tinh lệch trước/sau hành tinh tối đa | $\Delta t_{max} = a_{max}/v_p$ | Bề rộng "vùng vai" quanh transit |

**Bước 2. TTV (Transit Timing Variation)** (Sartoretti & Schneider 1999; Kipping 2009). Hành tinh và vệ tinh cùng quay quanh tâm khối chung, nên hành tinh lúc đến sớm lúc đến muộn tối đa $a_v M_v/(M_p v_p)$. Đo thời điểm từng transit, khớp đường thẳng $t_c = T_0 + nP$, tính **O − C** (đo được trừ dự đoán), rồi:
- Kiểm tra O − C có dao động **có chu kỳ** không (periodogram **Lomb–Scargle**, đọc **FAP**); cần ≥ 8 transit.
- Giới hạn khối lượng: $M_{v,max} = \sqrt{2}\,\sigma_{TTV}\,v_p M_p/a_{max}$, với $\sigma_{TTV}$ = O − C rms.
- Bẫy: sai số pipeline thường nhỏ hơn thực tế; O − C có thể dao động giả do **lệch pha lưới đo 29.4 phút** (cadence alias); hành tinh khác, vết đen sao cũng gây TTV.
- **TDV** (biến thiên thời lượng transit) lệch pha 90° so với TTV; có cả hai thì tách được khối lượng và khoảng cách vệ tinh. Script chưa đo TDV.

**Bước 3. OSE (Orbital Sampling Effect)** (Heller 2014). Mỗi transit vệ tinh ở một chỗ khác nhau trong khoảng ±Δt_max và tự tạo chỗ trũng $\delta_v = (R_v/R_s)^2$. Cộng nhiều transit lại thì thành một **vai trũng nông** hai bên transit hành tinh. Đo vai trũng D ± σ_D so với vùng nền, rồi
$$\delta_{v,max} = (\max(D,0) + 2\sigma_D)\cdot\frac{2\Delta t_{max} + T_{14}}{T_{14}}, \qquad R_{v,max} = R_s\sqrt{\delta_{v,max}}$$

Để so sánh: Mặt Trăng 0.273 R⊕, Titan 0.404, Ganymede 0.413, Sao Hỏa 0.532.

### 9.2. Vì sao Kepler-452b là chỗ "dễ có vệ tinh"

Hành tinh xa sao (~1 AU) nên bán kính Hill lớn (~1.6–2.3 triệu km, gấp ~1.1–1.5 lần của Trái Đất), vùng vệ tinh bền rộng từ ~20.000 tới ~800.000–1.100.000 km. Thủy triều từ sao yếu, vệ tinh tồn tại được hàng tỷ năm. Ngược lại, chỉ có **4 transit**, nên TTV gần như không kiểm định được.

### 9.3. Python

```bash
# Bước 4 (sau bước 2): tìm vệ tinh
.venv/Scripts/python scripts/04_moons.py "Kepler-452"
```

Kết quả: `outputs/Kepler452_moons.md`, `outputs/Kepler452_moons.png` (trái: O − C 4 transit; phải: vùng vai OSE), `data/csv/Kepler452_Kepler452b_transit_times.csv`, `data/csv/Kepler452_Kepler452b_ose_profile.csv`.

### 9.4. Google Sheets

Tab `moon`, đầu vào (bộ sao NASA; bộ KIC để so sánh): `B1` Mp = 3.29 M⊕ (NASA, ước tính) | 1.1, `B2` Ms = 1.037 | 0.870 M☉, `B3` a = 1.046 | 0.9885 AU, `B4` P = 384.843 ngày, `B5` Rp = 1.63 | 1.03 R⊕, `B6` Rs = 1.11 | 0.794 R☉, `B7` T14 = 10.16 giờ.

| Ô | Thông số | Công thức | Sao NASA | Sao KIC |
|---|---|---|---|---|
| B9 | Bán kính Hill (km) | `=B3*1.496E8*(B1*5.972E24/(3*B2*1.989E30))^(1/3)` | 2.300.000 | 1.582.000 |
| B10 | a_max (km) | `=0.4895*B9` | 1.126.000 | 774.000 |
| B11 | Mật độ hành tinh (g/cm³) | `=5.51*B1/B5^3` | 4.19 | — |
| B12 | Giới hạn Roche (km) | `=2.44*B5*6371*(B11/3)^(1/3)` | 28.300 | 19.400 |
| B14 | Chu kỳ vệ tinh dài nhất (ngày) | `=2*PI()*SQRT((B10*1000)^3/(6.674E-11*B1*5.972E24))/86400` | 75.9 | 76.1 |
| B15 | v_p (km/s) | `=2*PI()*B3*1.496E8/(B4*86400)` | 29.6 | 28.0 |
| B16 | Δt_max (giờ) | `=B10/B15/3600` | 10.6 | 7.7 |

TTV: import `Kepler452_Kepler452b_transit_times.csv` vào tab `tt` (A `epoch`, B `tc_bkjd`, C `sigma_min`, D `oc_min`, E `used`). Bốn transit: O − C = +23.6, −34.4, +6.5, +6.4 phút; rms **21.4 phút**; sai số mỗi transit 14–20 phút.

| Ô | Thông số | Công thức | Sao NASA | Sao KIC |
|---|---|---|---|---|
| B19 | O − C rms (phút) | `=SQRT(SUMPRODUCT(tt!D2:D5^2*(tt!E2:E5=1))/COUNTIF(tt!E2:E5,1))` | 21.4 | 21.4 |
| B21 | **Khối lượng vệ tinh tối đa (M⊕)** | `=SQRT(2)*B19*60*B15*B1/B10` | **0.16** | 0.07 |
| B22 | Theo Mặt Trăng | `=B21*81.3` | **~13** | ~6 |

OSE: import `Kepler452_Kepler452b_ose_profile.csv` vào tab `ose`, dùng công thức B23–B33 ở mục 8.2.E của [`kien-thuc-exoplanet.md`](kien-thuc-exoplanet.md). Kết quả bằng Sheets: **0.79 R⊕** với sao KIC (Python: 0.75), **1.19 R⊕** với sao NASA (Rs = 1.11, Δt_max = 10.6 giờ).

### 9.5. Kết quả

| | Python (sao KIC) | Tính lại với sao NASA |
|---|---|---|
| Vùng vệ tinh bền | 19.400 – 774.000 km | 28.300 – 1.126.000 km |
| Chu kỳ vệ tinh dài nhất | 76 ngày | 76 ngày |
| Vệ tinh lệch trước/sau tối đa | 7.7 giờ | 10.6 giờ |
| Số transit định thời | 4, sai số ~17 phút mỗi lần | |
| TTV | rms 21.4 phút, **quá ít transit để kiểm định** | |
| **Khối lượng vệ tinh tối đa** | 0.07 M⊕ ≈ 6 Mặt Trăng | **0.16 M⊕ ≈ 13 Mặt Trăng** |
| Vai trũng OSE | −8.9 ± 14.7 ppm (không thấy vai) | |
| **Bán kính vệ tinh tối đa** | 0.75 R⊕ | **~1.2 R⊕** (Sheets, mục 9.4) |

**Đọc kết quả:**
- Không thấy dấu hiệu vệ tinh. Dữ liệu chỉ loại được vệ tinh **lớn cỡ Trái Đất** (theo bộ sao NASA, thậm chí chưa loại hẳn được), và **nặng hơn ~13 Mặt Trăng** (nếu vệ tinh ở xa nhất có thể; ở gần hơn thì giới hạn lỏng hơn theo tỉ lệ).
- Giới hạn khối lượng từ 4 điểm rất thô: khớp đường thẳng qua 4 điểm đã "ăn" mất 2 bậc tự do, và vệ tinh có thể tình cờ ở cùng một pha cả 4 lần.
- Muốn có giới hạn tốt hơn cần thêm transit (kính PLATO), hoặc đo transit chính xác hơn nhiều bằng kính lớn.

---

## 10. Bảng thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|---|---|
| Exoplanet | Hành tinh quay quanh một ngôi sao khác ngoài Mặt Trời |
| Transit | Hành tinh đi ngang trước mặt sao, làm sao tối đi một chút |
| Light curve | Đồ thị/bảng độ sáng theo thời gian |
| Flux | Độ sáng đo được |
| Photometry | Kỹ thuật đo độ sáng (trắc quang) |
| Spectroscopy | Quang phổ học: phân tích ánh sáng theo bước sóng, cho Teff, logg, [Fe/H] chính xác hơn trắc quang |
| Aperture | Tập pixel được cộng lại để đo sáng một ngôi sao |
| Cadence | Khoảng thời gian giữa 2 lần đo (long cadence 29.4 phút) |
| Quarter | Một quý dữ liệu Kepler (~90 ngày), mỗi quý 1 file |
| KIC | Kepler Input Catalog: danh mục và mã số các sao |
| KOI | Kepler Object of Interest: ứng viên hành tinh |
| DR25 | Data Release 25: bản xử lý cuối cùng của dữ liệu Kepler |
| MAST | Kho lưu trữ dữ liệu của STScI, nơi chứa dữ liệu Kepler/K2/TESS |
| NASA Exoplanet Archive | Kho thông số hành tinh/ứng viên của NASA (Caltech/IPAC) |
| TAP / ADQL | Giao thức truy vấn bảng thiên văn qua URL / ngôn ngữ truy vấn giống SQL |
| pscomppars / ps | Bảng NASA: composite (1 dòng/hành tinh, ghép nguồn) / từng bộ thông số đã công bố |
| FITS / HDU | Định dạng file thiên văn / một "tab" trong file FITS |
| TOPCAT | Phần mềm miễn phí xem và chuyển đổi bảng thiên văn (FITS → CSV) không cần code |
| BKJD / BJD | Hệ thời gian (ngày); BKJD = BJD − 2454833 |
| RA / Dec | Tọa độ trên bầu trời (xích kinh / xích vĩ) |
| Magnitude | Cấp sao; số nhỏ = sáng hơn |
| ppm | Phần triệu |
| R☉ / R⊕ / M☉ / M⊕ | Bán kính, khối lượng Mặt Trời / Trái Đất |
| Flatten / detrend | Làm phẳng: loại biến thiên chậm của sao và thiết bị |
| BLS | Box Least Squares: thuật toán tìm tín hiệu transit có chu kỳ |
| Periodogram | Đồ thị độ mạnh tín hiệu theo chu kỳ thử |
| SDE | Đỉnh periodogram nổi bật hơn phần còn lại bao nhiêu lần độ lệch chuẩn |
| SNR | Tỉ số tín hiệu/nhiễu: độ sâu chia sai số độ sâu |
| MES | Multiple Event Statistic: SNR của pipeline Kepler khi cộng mọi transit, ngưỡng phát hiện 7.1 |
| Robovetter / koi_score | Bộ lọc tự động của Kepler phân loại ứng viên / độ tin của nó (0–1) |
| Phase fold | Gấp dữ liệu theo chu kỳ để chồng các transit lên nhau |
| Ephemeris | Bộ (P, T0) dùng để dự đoán thời điểm transit |
| Kiểm chứng (verification) | Kiểm tra tín hiệu tại P, T0 đã biết, khác với tìm mù |
| Phép thử báo động giả | Lặp lại phép đo ở các (P, T0) ngẫu nhiên để xem nhiễu tạo ra tín hiệu mạnh như vậy thường đến mức nào |
| Look-elsewhere effect | Thử càng nhiều chỗ thì càng dễ gặp tín hiệu giả do may rủi |
| White noise / Red noise | Nhiễu ngẫu nhiên độc lập từng điểm / nhiễu tương quan kéo dài, giả dạng được transit |
| Whitening | Làm trắng nhiễu: biến đổi dữ liệu để nhiễu đỏ thành gần nhiễu trắng trước khi tìm transit |
| Validation (thống kê) | "Xác nhận" hành tinh bằng xác suất loại trừ sao đôi/sao nền, không đo khối lượng |
| Controversial flag | Cờ `pl_controv_flag` của NASA: sự tồn tại của hành tinh đang bị nghi ngờ |
| False positive | Tín hiệu giả, không phải hành tinh |
| Eclipsing binary | Hệ sao đôi che khuất nhau, dễ bị nhầm là hành tinh |
| Ingress / Egress | Đoạn hành tinh đi vào / đi ra khỏi đĩa sao |
| T14 | Thời lượng transit từ lúc chạm mép đầu tới mép cuối |
| Impact parameter (b) | Hành tinh đi qua cách tâm sao bao xa (0 = chính giữa, ~1 = sượt mép) |
| a / Rs | Khoảng cách hành tinh – sao tính theo bán kính sao |
| Inclination (i) | Độ nghiêng quỹ đạo; 90° = nhìn đúng mép quỹ đạo |
| Semi-major axis (a) / AU | Bán trục lớn / đơn vị thiên văn ≈ 150 triệu km |
| Limb darkening | Tối rìa: rìa đĩa sao tối hơn tâm, đáy transit cong |
| Exposure smearing | Nhòe do phơi sáng 29.4 phút làm sườn transit bị kéo dài |
| batman | Thư viện Python tạo mô hình transit có tối rìa |
| Teq / Insolation / Albedo | Nhiệt độ cân bằng / bức xạ nhận được so với Trái Đất / tỉ lệ ánh sáng phản xạ |
| Habitable zone | Vùng có thể sống: khoảng cách mà nước có thể lỏng trên bề mặt |
| Runaway greenhouse | Hiệu ứng nhà kính mất kiểm soát: mép trong của vùng có thể sống bảo thủ |
| Radial velocity (RV), K | Vận tốc xuyên tâm của sao do hành tinh kéo / biên độ của nó (m/s) |
| TTV | Transit đến sớm/muộn do các hành tinh kéo nhau, dùng đo khối lượng |
| Mass–radius relation | Quan hệ thực nghiệm khối lượng – bán kính, ước tính khối lượng khi chưa đo được |
| Metallicity [Fe/H] | Độ kim loại so với Mặt Trời, thang log |
| Spectral type | Loại phổ: O B A F G K M (nóng → lạnh); Mặt Trời và Kepler-452 đều là G2 |
| Parallax / mas | Thị sai / mili giây cung |
| Parsec | 1 pc ≈ 3.26 năm ánh sáng |
| Gaia / RUWE | Vệ tinh ESA đo thị sai / chỉ số chất lượng (< 1.4 là tin được) |
| Distance modulus | m − M = 5·log₁₀(d / 10 pc) |
| Sub-Neptune | Hành tinh 1.6–4 R⊕: lõi đá + khí H/He hoặc nhiều nước |
| Thang logarit | Trục mà mỗi bậc gấp 10 lần |
| Exomoon | Vệ tinh của hành tinh ngoài Hệ Mặt Trời; chưa có cái nào được xác nhận |
| Hill sphere (bán kính Hill) | Vùng lực hút hành tinh thắng lực hút sao; vệ tinh bền tới ~0.49 R_H |
| Roche limit | Khoảng cách tối thiểu; gần hơn thì vệ tinh bị thủy triều xé vụn |
| O − C | Thời điểm transit đo được trừ thời điểm dự đoán theo chu kỳ đều |
| TTV / TDV | Biến thiên thời điểm / thời lượng transit, dấu hiệu bị vật khác kéo |
| OSE | Orbital Sampling Effect: bóng vệ tinh cộng qua nhiều transit thành "vai" trũng nông |
| Lomb–Scargle / FAP | Periodogram cho dữ liệu lấy mẫu không đều / xác suất báo động giả của đỉnh |
| Cadence alias | Dao động giả trong O − C do tâm transit rơi vào vị trí khác nhau trong lưới đo 29.4 phút |
| PLATO | Kính không gian ESA (kế hoạch phóng khoảng 2026–2027) săn hành tinh giống Trái Đất quanh sao giống Mặt Trời |

---

## 11. Tài liệu tham khảo

- Jenkins, J. M. et al. 2015, *Discovery and Validation of Kepler-452b: A 1.6 R⊕ Super Earth Exoplanet in the Habitable Zone of a G2 Star*, AJ 150, 56. https://ui.adsabs.harvard.edu/abs/2015AJ....150...56J/abstract
- Mullally, F. et al. 2018, *Kepler's Earth-like Planets Should Not Be Confirmed without Independent Detection: The Case of Kepler-452b*, ApJ Letters.
- Thompson, S. E. et al. 2018, *Planetary Candidates Observed by Kepler. VIII. A Fully Automated Catalog with Measured Completeness and Reliability Based on Data Release 25*, ApJS 235, 38.
- Berger, T. A. et al. 2018, ApJ 866, 99 (bán kính sao Kepler từ Gaia DR2).
- Chen, J. & Kipping, D. 2017, ApJ 834, 17 (quan hệ khối lượng – bán kính).
- Kopparapu, R. K. et al. 2013, ApJ 765, 131 (vùng có thể sống).
- Kipping, D. M. 2009, MNRAS 392, 181 (TTV và TDV do vệ tinh).
- Sartoretti, P. & Schneider, J. 1999, A&AS 134, 553 (ý tưởng tìm vệ tinh bằng thời điểm transit).
- Heller, R. 2014, ApJ 787, 14 (Orbital Sampling Effect).
- Domingos, R. C., Winter, O. C. & Yokoyama, T. 2006, MNRAS 373, 1227 (vùng bền của vệ tinh).
- Barnes, J. W. & O'Brien, D. P. 2002, ApJ 575, 1087 (vệ tinh quanh hành tinh gần sao).
- Teachey, A. & Kipping, D. M. 2018, Science Advances 4, eaav1784 (ứng viên Kepler-1625b-i).
- Kipping, D. et al. 2022, Nature Astronomy 6, 367 (ứng viên Kepler-1708b-i).
- NASA Exoplanet Archive, trang Kepler-452: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-452
- MAST Kepler: https://archive.stsci.edu/missions-and-data/kepler
- Lightkurve: https://lightkurve.github.io/lightkurve/
- TOPCAT: https://www.star.bris.ac.uk/~mbt/topcat/
- Sổ tay chung của dự án: [`kien-thuc-exoplanet.md`](kien-thuc-exoplanet.md)
