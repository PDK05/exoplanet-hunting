# Hệ Kepler-186: hành tinh cỡ Trái Đất đầu tiên trong vùng có thể sống, từ A tới Z

Tài liệu tự đủ: gom toàn bộ kiến thức nền (vốn nằm trong [`kien-thuc-exoplanet.md`](kien-thuc-exoplanet.md)) cộng phần riêng của Kepler-186. Mọi nguồn dữ liệu đều có **link cụ thể**. Có **2 cách làm**: code Python (phần 5) hoặc chỉ dùng Google Sheets (phần 6). Đối chiếu NASA ở phần 7. Phần 9 là phương án **tìm vệ tinh** quanh các hành tinh.

Số liệu trong tài liệu được tính thật từ dữ liệu Kepler ngày 26/10/2026.

## Mục lục

0. [Tóm tắt: cần tải gì, ở đâu](#0-tóm-tắt-cần-tải-gì-ở-đâu)
1. [Kiến thức nền: Kepler và phương pháp transit](#1-kiến-thức-nền-kepler-và-phương-pháp-transit)
2. [Kiến thức nền: dữ liệu Kepler và file FITS](#2-kiến-thức-nền-dữ-liệu-kepler-và-file-fits)
3. [Kiến thức nền: từ transit tính ra được gì, công thức](#3-kiến-thức-nền-từ-transit-tính-ra-được-gì-công-thức)
4. [Hệ Kepler-186: lý lịch](#4-hệ-kepler-186-lý-lịch)
5. [Phương án A: chơi bằng code Python](#5-phương-án-a-chơi-bằng-code-python)
6. [Phương án B: chỉ dùng Google Sheets](#6-phương-án-b-chỉ-dùng-google-sheets)
7. [Kết quả và so sánh với NASA](#7-kết-quả-và-so-sánh-với-nasa)
8. [Những bài học riêng từ Kepler-186](#8-những-bài-học-riêng-từ-kepler-186)
9. [Tìm vệ tinh quanh các hành tinh Kepler-186](#9-tìm-vệ-tinh-quanh-các-hành-tinh-kepler-186)
10. [Bảng thuật ngữ](#10-bảng-thuật-ngữ)
11. [Tài liệu tham khảo](#11-tài-liệu-tham-khảo)

---

## 0. Tóm tắt: cần tải gì, ở đâu

### 0.1. Thẻ căn cước của hệ

| | Giá trị |
|---|---|
| Tên sao | **Kepler-186** = **KIC 8120608** = KOI-571 = Gaia DR3 2079000330051813504 |
| Tọa độ | RA 298.65272°, Dec +43.95502° (chòm Thiên Nga) |
| Loại sao | **Sao lùn đỏ loại M1**, ~0.5 lần Mặt Trời về kích thước và khối lượng, nhiệt độ ~3.750 K |
| Cấp sao Kepler | Kp = 14.63 (rất mờ: mờ hơn Kepler-452 khoảng 3 lần) |
| Hành tinh | **5 hành tinh** b, c, d, e, f, đều cỡ Trái Đất (1.0–1.4 R⊕), đều có transit |
| Nổi bật | **Kepler-186 f**: chu kỳ 129.9 ngày, ~1.2 R⊕, ở **mép ngoài vùng có thể sống** |

### 0.2. Có cần tải hết dữ liệu không?

| Mục đích | Cần những file nào |
|---|---|
| **Tự tìm cả 5 hành tinh từ đầu** | **Cả 17 file** Q1–Q17 (Kepler không quan sát sao này ở Q0). BLS tự tìm ra b, c, d, e; f phải kiểm chứng (mục 5.3). |
| **Chỉ nhìn thấy cả 5 hành tinh trong Sheets** | **1 file Q2** đủ: trong 89 ngày của Q2 có dữ liệu cho 22 transit của b, 11 của c, 7 của d, 4 của e và **1 của f** (BKJD 176.83). |
| **Kiểm chứng + tính thông số Kepler-186 f** | **10 file** chứa transit của f (bảng 0.3). Transit thứ 11 (BKJD 566.66, Q6) rơi đúng vào khoảng trống dữ liệu. |
| Thông tin sao (KIC) | Header của bất kỳ file FITS nào |
| Đáp án NASA | Các link truy vấn ở mục 0.4 (trả về CSV) |
| Khoảng cách | Link Gaia ở mục 0.5 |

### 0.3. Light curve: link tải từng file

Thư mục gốc chứa đủ 17 file (MAST, miễn phí, không cần tài khoản):
**https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/**

> Quy tắc: `.../lightcurves/<4 chữ số đầu của KIC 9 chữ số>/<KIC 9 chữ số>/`. KIC 8120608 → `008120608` → `0081/008120608/`.

**10 file chứa transit của Kepler-186 f** (thời điểm tính từ T0 = BJD 2455789.494, P = 129.9441 ngày của NASA):

| Transit | Giữa transit (BKJD) | Ngày (UTC) | Quý | File |
|---|---|---|---|---|
| −6 | 176.829 | 27/06/2009 | **Q2** | [kplr008120608-2009259160929_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2009259160929_llc.fits) |
| −5 | 306.774 | 04/11/2009 | Q3 | [kplr008120608-2009350155506_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2009350155506_llc.fits) |
| −4 | 436.718 | 14/03/2010 | Q4 | [kplr008120608-2010078095331_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2010078095331_llc.fits) |
| −3 | 566.662 | 22/07/2010 | (Q6) | rơi vào khoảng trống dữ liệu |
| −2 | 696.606 | 29/11/2010 | Q7 | [kplr008120608-2010355172524_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2010355172524_llc.fits) |
| −1 | 826.550 | 08/04/2011 | Q9 | [kplr008120608-2011177032512_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2011177032512_llc.fits) |
| 0 | 956.494 | 15/08/2011 | Q10 | [kplr008120608-2011271113734_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2011271113734_llc.fits) |
| 1 | 1086.438 | 23/12/2011 | Q11 | [kplr008120608-2012004120508_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2012004120508_llc.fits) |
| 2 | 1216.382 | 01/05/2012 | Q13 | [kplr008120608-2012179063303_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2012179063303_llc.fits) |
| 3 | 1346.326 | 08/09/2012 | Q14 | [kplr008120608-2012277125453_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2012277125453_llc.fits) |
| 4 | 1476.270 | 16/01/2013 | Q16 | [kplr008120608-2013098041711_llc.fits](https://archive.stsci.edu/missions/kepler/lightcurves/0081/008120608/kplr008120608-2013098041711_llc.fits) |

<details>
<summary>Danh sách đủ 17 file (bấm để mở)</summary>

| Quý | File | Khoảng thời gian (BKJD) |
|---|---|---|
| Q1 | kplr008120608-2009166043257_llc.fits | 131.5 – 165.0 |
| **Q2** | kplr008120608-2009259160929_llc.fits | 169.5 – 258.5 |
| Q3 | kplr008120608-2009350155506_llc.fits | 260.2 – 349.5 |
| Q4 | kplr008120608-2010078095331_llc.fits | 352.4 – 442.2 |
| Q5 | kplr008120608-2010174085026_llc.fits | 443.5 – 538.2 |
| Q6 | kplr008120608-2010265121752_llc.fits | 539.4 – 629.3 |
| Q7 | kplr008120608-2010355172524_llc.fits | 630.2 – 719.5 |
| Q8 | kplr008120608-2011073133259_llc.fits | 735.4 – 802.3 |
| Q9 | kplr008120608-2011177032512_llc.fits | 808.5 – 905.9 |
| Q10 | kplr008120608-2011271113734_llc.fits | 906.8 – 1000.3 |
| Q11 | kplr008120608-2012004120508_llc.fits | 1001.2 – 1098.3 |
| Q12 | kplr008120608-2012088054726_llc.fits | 1099.4 – 1182.0 |
| Q13 | kplr008120608-2012179063303_llc.fits | 1182.7 – 1273.1 |
| Q14 | kplr008120608-2012277125453_llc.fits | 1274.1 – 1371.3 |
| Q15 | kplr008120608-2013011073258_llc.fits | 1373.5 – 1471.1 |
| Q16 | kplr008120608-2013098041711_llc.fits | 1472.1 – 1558.0 |
| Q17 | kplr008120608-2013131215648_llc.fits | 1559.2 – 1591.0 |

Mỗi file 180–500 KB, tổng ~7 MB, long cadence (29.4 phút/điểm).
</details>

Cách khác: **MAST Portal** https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html (gõ `Kepler-186`, lọc *Mission = Kepler*, *timeseries*); Python `lightkurve`; hoặc **CSV có sẵn trong repo** (`data/csv/Kepler186_*`, mục 5.4).

### 0.4. Dữ liệu NASA: lấy ở đâu, lấy cái gì

**Trang tổng quan:** https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-186

**Truy vấn TAP (trả về CSV; dán vào trình duyệt, hoặc dùng `IMPORTDATA` trong Sheets):**

| Bảng | Là gì | Link |
|---|---|---|
| `pscomppars` | Composite, 1 dòng/hành tinh, ghép nhiều nguồn (⚠️ lẫn nguồn, mục 8.3) | [link](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,pl_orbper,pl_tranmid,pl_trandur,pl_trandep,pl_ratror,pl_rade,pl_bmasse,pl_bmassprov,pl_orbsmax,pl_orbincl,pl_imppar,pl_ratdor,pl_eqt,pl_insol,pl_orbeccen,st_teff,st_rad,st_mass,st_met,st_logg,st_age,st_spectype,sy_dist,sy_plx,pl_controv_flag,ttv_flag+from+pscomppars+where+hostname='Kepler-186'&format=csv) |
| `ps` | Mọi bộ thông số đã công bố (Kepler-186 f có 13 bộ); `default_flag = 1` là bộ chuẩn (Torres et al. 2015) | [link](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,default_flag,pl_refname,pl_orbper,pl_rade,st_rad,st_mass,st_teff+from+ps+where+hostname='Kepler-186'&format=csv) |
| `q1_q17_dr25_koi` | Bảng KOI DR25 (pipeline Kepler) | [link](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+kepoi_name,kepler_name,koi_disposition,koi_score,koi_period,koi_time0bk,koi_duration,koi_depth,koi_prad,koi_ror,koi_dor,koi_impact,koi_model_snr,koi_max_mult_ev,koi_num_transits,koi_steff,koi_srad,koi_smass,koi_slogg,koi_insol,koi_teq+from+q1_q17_dr25_koi+where+kepid=8120608&format=csv) |

Giao diện bảng: Composite https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PSCompPars ; KOI DR25 https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=q1_q17_dr25_koi . Giải thích cột: https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html và https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html

**Giá trị thực tế** (`pscomppars`):

| Cột | Ý nghĩa | b | c | d | e | f |
|---|---|---|---|---|---|---|
| `pl_orbper` | Chu kỳ (ngày) | 3.8867907 | 7.267302 | 13.342996 | 22.407704 | 129.9441 |
| `pl_tranmid` | Giữa transit (BJD) | 2454966.3304 | 2455007.3142 | 2455009.9045 | 2454986.8006 | 2455789.494 |
| `pl_trandur` | T14 (giờ) | 1.81 | 2.27 | 2.90 | 3.32 | 5.62 |
| `pl_trandep` | Độ sâu (**%**) | 0.0514 | 0.0659 | 0.0873 | 0.0709 | 0.0467 |
| `pl_ratror` | Rp/Rs | 0.0208 | 0.0242 | 0.0272 | 0.0246 | 0.0205 |
| `pl_rade` | Rp (R⊕) | 1.07 | 1.25 | 1.40 | 1.27 | 1.17 |
| `pl_bmasse` / `pl_bmassprov` | Khối lượng (M⊕) / nguồn | 1.24 / M-R | 2.10 / M-R | 2.54 / M-R | 2.15 / M-R | 1.71 / M-R |
| `pl_orbsmax` | a (AU) | 0.0343 | 0.0451 | 0.0781 | 0.1100 | 0.4320 |
| `pl_eqt` | Teq (K) | 571 | 464 | 379 | 319 | 177 |
| `pl_insol` | Bức xạ (× Trái Đất) | 37.4 | 14.0 | 7.2 | 3.6 | 0.30 |
| `st_rad`, `st_mass`, `st_teff` | Sao dùng cho dòng này | 0.472, 0.478, 3788 | ← | ← | ← | **0.523, 0.544, 3755** |
| `pl_controv_flag` | Cờ tranh cãi | 0 | 0 | 0 | 0 | **1** |
| `ttv_flag` | Có TTV đã công bố? | 0 | 0 | 0 | 0 | 0 |

Chung: `st_spectype` = M1, `st_met` = −0.26 đến −0.28, `st_age` = 4.0 tỷ năm, `sy_dist` = 177.6 pc, `sy_plx` = 5.602 mas. `pl_bmassprov = M-R relationship` nghĩa là **ước tính từ bán kính, không phải đo**.

**Bảng KOI DR25** (bộ sao khác nữa: `koi_srad` = 0.443, `koi_smass` = 0.452, `koi_steff` = 3751):

| KOI | Tên | `koi_period` | `koi_depth` (ppm) | `koi_prad` | `koi_model_snr` | MES | Số transit | `koi_score` |
|---|---|---|---|---|---|---|---|---|
| K00571.03 | b | 3.886795 | 471 | 0.97 | 41.8 | 34.2 | 332 | 1.000 |
| K00571.01 | c | 7.267311 | 659 | 1.14 | 47.8 | 38.0 | 179 | 1.000 |
| K00571.02 | d | 13.343003 | 800 | 1.29 | 47.1 | 36.2 | 99 | 1.000 |
| K00571.04 | e | 22.407778 | 661 | 1.15 | 33.9 | 23.6 | 54 | 0.999 |
| K00571.05 | **f** | 129.945392 | 500 | 1.18 | 13.1 | **7.67** | 8 | **0.677** |

### 0.5. Khoảng cách: Gaia DR3

- Truy vấn (CSV): [link](https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=SELECT+source_id,parallax,parallax_error,ruwe,phot_g_mean_mag+FROM+gaiadr3.gaia_source+WHERE+source_id=2079000330051813504)
- Kết quả: thị sai **5.6336 ± 0.0169 mas**, RUWE 0.99, G = 14.58 → **177.5 ± 0.5 pc ≈ 579 năm ánh sáng**.
- Giao diện web: https://gea.esac.esa.int/archive/ → *Search* → tọa độ ở mục 0.1, bán kính 5″.

---

## 1. Kiến thức nền: Kepler và phương pháp transit

### 1.1. Kepler làm gì?

Kepler là kính thiên văn không gian của NASA (2009–2013), **nhìn cố định một vùng trời** (Thiên Nga – Thiên Cầm), đo **độ sáng ~150.000 sao** khoảng 30 phút một lần trong 4 năm.

Phương pháp **transit**: hành tinh đi ngang trước sao làm sao **tối đi một chút**, lặp lại **theo chu kỳ**.

```
Độ sáng
  1.000 ─────────┐     ┌──────────────┐     ┌──────
                 │     │              │     │
  0.999          └─────┘              └─────┘
                 ← transit →
                 |←──── chu kỳ (period) ────→|
```

"Săn exoplanet" là **tìm các chỗ trũng nhỏ, lặp lại đều đặn trong chuỗi độ sáng**.

### 1.2. Kepler, K2, TESS

| | Kepler | K2 | TESS |
|---|---|---|---|
| Thời gian | 2009–2013 | 2014–2018 | 2018–nay |
| Vùng trời | 1 vùng cố định | ~20 vùng dọc hoàng đạo (*campaign* ~80 ngày) | Gần toàn bầu trời |
| Quan sát mỗi sao | ~4 năm | ~80 ngày | ~27 ngày (có vùng lâu hơn) |
| Mã sao | **KIC** | **EPIC** | **TIC** |
| Tên file | `kplr<KIC>-..._llc.fits` | `ktwo<EPIC>-c<campaign>_llc.fits` | `tess..._lc.fits` |

Dữ liệu Kepler gốc vẫn public, miễn phí, bản cuối là **DR25**. Kepler-186 f (chu kỳ 130 ngày) cần quan sát dài nên chỉ Kepler thấy đủ transit.

### 1.3. Độ lớn tín hiệu và vì sao sao lùn M có lợi

$$\text{Độ sâu} \approx \left(\frac{R_{\text{hành tinh}}}{R_{\text{sao}}}\right)^2$$

Trái Đất qua Mặt Trời: ~84 ppm. Nhưng sao Kepler-186 chỉ to bằng ~0.5 Mặt Trời, nên **cùng một hành tinh cỡ Trái Đất cho transit sâu gấp ~4 lần** (~400–800 ppm). Thêm nữa sao lùn M mờ, nên vùng có thể sống nằm rất gần sao (~0.2–0.45 AU), chu kỳ ngắn, nhiều transit. Đó là lý do hành tinh cỡ Trái Đất trong vùng có thể sống được tìm thấy quanh sao M trước tiên.

### 1.4. False positive

Tín hiệu giả: **sao đôi che nhau**, **sao lân cận** lọt sáng, **nhiễu thiết bị**, và với sao M: **vết đen + bùng sáng (flare)**. Hệ có **nhiều hành tinh transit** như Kepler-186 ít khả năng là tín hiệu giả hơn hẳn (thống kê "multiplicity boost", Lissauer et al. 2012), đó là một trong các lý do 5 hành tinh này được xác nhận bằng thống kê.

---

## 2. Kiến thức nền: dữ liệu Kepler và file FITS

### 2.1. Các loại dữ liệu

| Loại | Là gì | Dùng khi nào |
|---|---|---|
| **Light curve** (`*_llc.fits`) | Độ sáng theo thời gian của 1 sao | **Bắt đầu từ đây** |
| Target Pixel File (`*_lpd-targ.fits`) | Ảnh pixel thô quanh sao | Nâng cao |
| **KOI table** | Ứng viên hành tinh NASA đã phân tích | "Đáp án" |
| **KIC** | Danh mục thông tin sao | Kích thước, nhiệt độ sao |

### 2.2. Tên file và cấu trúc FITS

```
kplr008120608-2009259160929_llc.fits
 │     │           │          └─ llc = long cadence light curve (29.4 phút/điểm)
 │     │           └─ thời điểm tạo file (năm 2009, ngày thứ 259, ...)
 │     └─ KIC ID 9 chữ số: Kepler-186
 └─ kplr = Kepler

HDU 0  PRIMARY     → header: thông tin ngôi sao
HDU 1  LIGHTCURVE  → bảng dữ liệu chính
HDU 2  APERTURE    → các pixel được cộng lại để đo sáng
```

⚠️ Google Sheets/Excel **không đọc được FITS**: phải chuyển sang CSV (Python hoặc TOPCAT, mục 6.1).

### 2.3. Header (HDU 0) của Kepler-186

| Khóa | Ý nghĩa | Kepler-186 |
|---|---|---|
| `KEPLERID` | Mã KIC | 8120608 |
| `RA_OBJ`, `DEC_OBJ` | Tọa độ (độ) | 298.65272, 43.95502 |
| `KEPMAG` | Cấp sao (số nhỏ = sáng) | 14.625 |
| `TEFF` | Nhiệt độ (K) | 3755 |
| `LOGG` | log g (cgs) | 4.778 (sao lùn) |
| `FEH` | [Fe/H] | −0.16 |
| `RADIUS` | Bán kính (R☉) | 0.475 |

Với sao M, KIC khá sát: 0.475 so với 0.472–0.523 R☉ của các nghiên cứu phổ (khác hẳn Kepler-452, nơi KIC lệch 30%).

⚠️ Script phân loại phổ theo ngưỡng đơn giản: Teff ≥ 3700 K → "K". Kepler-186 (3755 K) nằm sát ranh giới nên script ghi "K", còn phổ học xếp **M1**. Ranh giới K/M thực tế ~3.800–3.900 K.

### 2.4. Bảng dữ liệu (HDU 1)

| Cột | Ý nghĩa | Ghi chú |
|---|---|---|
| `TIME` | Thời điểm, **BKJD** = BJD − 2454833 (ngày) | |
| `SAP_FLUX` | Độ sáng thô (e⁻/s) | |
| `PDCSAP_FLUX` | Độ sáng đã làm sạch nhiễu thiết bị | ✅ Dùng cột này |
| `PDCSAP_FLUX_ERR` | Sai số | Kepler-186: ~267 ppm/điểm (thực tế ~360–400) |
| `SAP_QUALITY` | Cờ chất lượng, 0 = tốt | Bỏ dòng ≠ 0 |
| `MOM_CENTR1/2` | Tâm sáng trên cảm biến | Phát hiện sao lân cận |

### 2.5. Quy trình chuẩn

1. **Lọc** `SAP_QUALITY ≠ 0` và NaN.
2. **Chuẩn hóa** mỗi quý về 1.
3. **Làm phẳng (flatten)**: chia cho đường xu hướng chậm. Cửa sổ phải **dài ≥ 3 lần transit dài nhất** nhưng **ngắn hơn nhiều so với biến thiên của sao**. Kepler-186 có vết đen quay ~35 ngày, dao động tới ~0.3%, nên cửa sổ mặc định 18 ngày **không đủ** (mục 8.1); dùng 101 điểm ≈ 2 ngày (gấp ~8 lần transit dài nhất 5.7 giờ), và **che transit đã biết** khi làm phẳng.
4. **BLS** tìm chu kỳ; **lặp**: che transit hành tinh vừa tìm rồi tìm tiếp.
5. **Gấp pha**, **khớp mô hình** (`batman`, có tối rìa + nhòe phơi sáng).
6. Kết hợp thông số sao, so với NASA.

---

## 3. Kiến thức nền: từ transit tính ra được gì, công thức

### 3.1. Mỗi thông số lấy từ đâu

| Thông số | Nguồn | Với Kepler-186 |
|---|---|---|
| P, T0 | ✅ Light curve | b–e tự tìm; f kiểm chứng |
| Độ sâu, T14, Rp/Rs | ✅ Light curve | Khớp NASA trong 3–7% |
| b, a/Rs, i, mật độ sao | ✅ Hình dạng transit | ❌ Sai số quá lớn (ingress ngắn so với 29.4 phút, sao mờ) |
| Rs, Teff, Ms | 📚 KIC hoặc phổ | KIC 0.475 R☉; phổ 0.47–0.52 R☉ |
| Rp | 🔀 (Rp/Rs) × Rs | |
| a | 🔀 Kepler 3 | |
| Teq, bức xạ, vùng có thể sống | 🔀 Teff, Rs, a | **Ngưỡng vùng sống phụ thuộc Teff** (mục 3.2) |
| Khoảng cách | 🛰️ Gaia | |
| **Khối lượng** | ❌ RV/TTV | Chưa đo được hành tinh nào; chỉ ước tính |
| Thành phần | 🔀 cần Mp + Rp | Chỉ đoán theo bán kính: đều < 1.5 R⊕ nên nhiều khả năng là **đá** |

### 3.2. Công thức

**Hình học transit** (quỹ đạo tròn): $k = R_p/R_s \approx \sqrt{\text{độ sâu}}$; $\cos i = b/(a/R_s)$; $T_{14} = \dfrac{P}{\pi}\arcsin\left(\dfrac{\sqrt{(1+k)^2-b^2}}{(a/R_s)\sin i}\right)$.

**Mật độ sao:** $\rho_* = \dfrac{3\pi}{GP^2}\left(\dfrac{a}{R_s}\right)^3$. **Khối lượng sao:** $M_s = gR_s^2/G$ ($g = 10^{\log g}$, cgs).

**Kepler 3:** $a\,[\text{AU}] = \left(M_s[M_☉]\cdot P[\text{năm}]^2\right)^{1/3}$.

**Năng lượng:** $L/L_☉ = (R_s/R_☉)^2(T_{eff}/5772)^4$; $S/S_⊕ = L/a^2$; $T_{eq} = T_{eff}\sqrt{R_s/(2a)}\,(1-A)^{1/4}$, A = 0.3.

**Vùng có thể sống phụ thuộc nhiệt độ sao** (Kopparapu et al. 2013): ngưỡng bức xạ $S_{eff} = S_☉ + aT + bT^2 + cT^3 + dT^4$, với $T = T_{eff} - 5780$:

| Mép | S☉ | a | b | c | d | Kepler-186 (3755 K) | Mặt Trời |
|---|---|---|---|---|---|---|---|
| Trong, lạc quan (Sao Kim thời trẻ) | 1.7763 | 1.4335e-4 | 3.3954e-9 | −7.6364e-12 | −1.1950e-15 | 1.54 | 1.78 |
| **Trong, bảo thủ** (nhà kính mất kiểm soát) | 1.0385 | 1.2456e-4 | 1.4612e-8 | −7.6345e-12 | −1.7511e-15 | **0.88** | 1.04 |
| **Ngoài, bảo thủ** (nhà kính CO₂ cực đại) | 0.3507 | 5.9578e-5 | 1.6707e-9 | −3.0058e-12 | −5.1925e-16 | **0.253** | 0.35 |
| Ngoài, lạc quan (Sao Hỏa thời trẻ) | 0.3207 | 5.4471e-5 | 1.5275e-9 | −2.1709e-12 | −3.8282e-16 | 0.228 | 0.32 |

Khoảng cách mép = $\sqrt{L/S_{eff}}$ AU. Sao lạnh phát nhiều hồng ngoại, mà nước và CO₂ hấp thụ hồng ngoại tốt, nên hành tinh quanh sao M cần **ít** bức xạ hơn để ấm. Dùng ngưỡng của Mặt Trời cho sao M sẽ đặt vùng sống quá gần sao.

**Xác suất có transit:** $\approx R_s/a$. **Khoảng cách:** $d\,[\text{pc}] = 1000/\varpi\,[\text{mas}]$ (tin được khi RUWE < 1.4); 1 pc = 3.2616 năm ánh sáng. **Thô bằng độ sáng:** $M = 4.74 - 2.5\log L$, $d = 10^{(m-M+5)/5}$ pc.

**RV:** $K \approx 28.4\,\text{m/s}\cdot(M_p/M_♃)(P/\text{năm})^{-1/3}(M_s/M_☉)^{-2/3}$.

**Ước tính khối lượng** (Chen & Kipping 2017): đá ($R$ < 1.23 R⊕) $M = (R/1.008)^{3.584}$; kiểu Neptune $M = (R/0.808)^{1.698}$. **Mật độ:** $5.51\cdot M/R^3$ g/cm³. **Phân loại theo bán kính:** < 1.6 R⊕ đá; 1.6–4 sub-Neptune; 4–10 giống Hải Vương; > 10 khí khổng lồ.

### 3.3. Các bẫy khi khớp transit

1. **Nhòe phơi sáng 29.4 phút** làm sườn transit dài ra → dùng supersampling.
2. **Tối rìa** làm đáy cong → dùng `batman`. Script dùng hệ số tối rìa của sao loại G; với sao M hệ số khác một chút, làm Rp/Rs lệch vài phần trăm.
3. **Lưới chu kỳ** phải đủ mịn.
4. **Hành tinh nhỏ, sao mờ**: b và a/Rs gần như không đo được (Kepler-186: sai số a/Rs lớn hơn chính giá trị).
5. **Làm phẳng ăn mất transit**: cửa sổ ngắn mà không che transit thì transit bị nông đi (mục 8.2).

---

## 4. Hệ Kepler-186: lý lịch

### 4.1. Vì sao nổi tiếng

Tháng 4/2014, Quintana et al. (Science) công bố **Kepler-186 f: hành tinh cỡ Trái Đất đầu tiên tìm thấy trong vùng có thể sống của một ngôi sao khác**. Bốn hành tinh trong (b–e) đã được xác nhận từ trước (Rowe et al. 2014; Lissauer et al. 2014), quay rất gần sao, quá nóng.

- f: ~1.1–1.2 R⊕, chu kỳ 130 ngày, nhận ~**30% bức xạ** Trái Đất nhận được (ít hơn cả Sao Hỏa nhận từ Mặt Trời, ~43%), nằm ở **mép ngoài** vùng có thể sống.
- Sao mẹ: sao lùn đỏ M1, ~0.5 lần Mặt Trời, ~4 tỷ năm tuổi, cách ~580 năm ánh sáng (báo chí 2014 ghi ~500 năm ánh sáng; Gaia đo lại ~579).

### 4.2. Tín hiệu f yếu, NASA gắn cờ tranh cãi

- MES của f chỉ **7.67** (ngưỡng phát hiện Kepler 7.1), `koi_score` 0.677, chỉ 8 transit trong bảng DR25. `pl_controv_flag = 1`.
- Năm hành tinh được "xác nhận" bằng **thống kê** (*validation*): hệ nhiều hành tinh rất khó là tín hiệu giả, cộng ảnh quang học độ phân giải cao loại trừ sao lân cận. Chưa hành tinh nào được đo khối lượng (RV dự kiến < 0.5 m/s trên sao Kp 14.6: ngoài khả năng hiện nay).
- Trong phân tích ở đây, sau khi làm phẳng đúng cách f có SNR 17 và **0/3000** lần chọn bừa P, T0 cho tín hiệu mạnh bằng, nên tín hiệu khá chắc chắn hơn Kepler-452b.

### 4.3. Ba bộ thông số sao

| | KIC (header FITS) | KOI DR25 | Quintana et al. 2014 (NASA dùng cho b–e) | Torres et al. 2015 (NASA dùng cho f) |
|---|---|---|---|---|
| Teff (K) | 3755 | 3751 | 3788 | 3755 |
| Rs (R☉) | 0.475 | 0.443 | 0.472 | 0.523 |
| Ms (M☉) | 0.493 (từ logg) | 0.452 | 0.478 | 0.544 |

Chênh lệch ~10%, nên Rp chênh ~10%. Nhỏ hơn nhiều so với Kepler-452 (30%) vì sao M ít biến thiên kích thước theo tuổi.

---

## 5. Phương án A: chơi bằng code Python

### 5.1. Cài đặt (1 lần)

```bash
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # lightkurve, batman-package, matplotlib, requests, setuptools
```

### 5.2. Chạy 4 bước

```bash
# Bước 1: tải 17 file FITS + xuất CSV.
#   --flatten-window 101: làm phẳng với cửa sổ ~2 ngày (sao có vết đen quay ~35 ngày)
#   --mask-known: che transit của 5 hành tinh đã biết (lấy P, T0, T14 từ NASA) khi làm phẳng
.venv/Scripts/python scripts/01_download.py "Kepler-186" --flatten-window 101 --mask-known

# Bước 2: BLS lặp từ 0.5 tới 150 ngày (5 vòng × ~1.5 phút); hành tinh BLS không tự tìm ra thì kiểm chứng
.venv/Scripts/python scripts/02_analyze.py "Kepler-186" --max-period 150 --verify-archive

# Bước 3: sơ đồ hệ (thang log, vùng có thể sống theo nhiệt độ sao)
.venv/Scripts/python scripts/03_diagram.py "Kepler-186"

# Bước 4: tìm vệ tinh (mục 9)
.venv/Scripts/python scripts/04_moons.py "Kepler-186"
```

Bước 1 gọi MAST qua `lightkurve.search_lightcurve("Kepler-186", author="Kepler", cadence="long")` (đúng 17 file ở mục 0.3) và gọi bảng `pscomppars` của NASA cho `--mask-known`. Bước 2 gọi `pscomppars`, `q1_q17_dr25_koi` và Gaia DR3 (link mục 0.4, 0.5).

> `--mask-known` dùng "đáp án" để làm phẳng, nên không còn là tìm mù hoàn toàn. Trong nghiên cứu thật, người ta làm 2 lượt: tìm → che transit vừa tìm → làm phẳng lại → tìm lại. Lượt 1 không che (chỉ `--flatten-window 101`) vẫn tìm được b–e.

### 5.3. Chuyện gì xảy ra khi chạy

**Lần 1 (cửa sổ mặc định 18 ngày): thất bại hoàn toàn.**
```
Vòng 1: P = 34.85369 ngày, độ sâu = 574 ppm, SNR = 59, SDE = 4.6 → nhiễu, dừng
```
Đỉnh 34.85 ngày không phải hành tinh mà là **chu kỳ tự quay của sao** (vết đen). Độ nhiễu sau làm phẳng 839 ppm, gấp 3 lần sai số danh nghĩa.

**Lần 2 (cửa sổ 2 ngày, không che transit):** độ nhiễu còn 360 ppm, BLS tìm ra b, c, d, e; f kiểm chứng được nhưng chỉ sâu **300 ppm, SNR 12**, Rp/Rs = 0.0171 (thấp hơn NASA 17%).

**Lần 3 (cửa sổ 2 ngày + che transit), kết quả chính thức:**
```
Light curve: 64437 điểm, dài 1459 ngày
BLS: thử 148982 chu kỳ từ 0.50 đến 150.0 ngày
  Vòng 1: P = 13.34284 ngày, độ sâu = 709 ppm, SNR = 56, SDE = 16.3, 100 transit → HÀNH TINH
  Vòng 2: P = 7.26724 ngày,  độ sâu = 528 ppm, SNR = 56, SDE = 16.9, 179 transit → HÀNH TINH
  Vòng 3: P = 3.88684 ngày,  độ sâu = 407 ppm, SNR = 50, SDE = 15.4, 341 transit → HÀNH TINH
  Vòng 4: P = 22.40842 ngày, độ sâu = 524 ppm, SNR = 38, SDE = 11.7, 61 transit  → HÀNH TINH
  Vòng 5: P = 129.17983 ngày, độ sâu = 539 ppm, SNR = 25, SDE = 7.0, 10 transit → nhiễu, dừng
BLS không tự tìm ra Kepler-186 f → kiểm chứng bằng P, T0 của NASA
  Kiểm chứng P = 129.9441 ngày: độ sâu = 433 ± 25 ppm, SNR = 17.3, 10 transit;
  0.00% trong 3000 lần chọn bừa P, T0 cho SNR cao bằng
```

- BLS tự tìm ra **4/5 hành tinh** (thứ tự theo độ mạnh tín hiệu: d, c, b, e).
- Vòng 5 có đỉnh 129.18 ngày, **gần** 129.94 nhưng không phải cùng tín hiệu (lệch 0.76 ngày mỗi vòng, sau 5 vòng đã lệch ~4 ngày), SDE 7.0 dưới ngưỡng 9, nên script dừng. Tức là f nằm **sát ngưỡng** phát hiện mù, đúng như MES 7.67 của NASA.
- Kiểm chứng tại đúng P, T0 của NASA: SNR 17.3, không lần chọn bừa nào (trong 3000) đạt tới.

### 5.4. File tạo ra

| File | Nội dung | Dùng cho |
|---|---|---|
| `data/raw/mastDownload/Kepler/kplr008120608_lc_Q011111111111111111/` | 17 file FITS (không đưa lên git) | |
| `data/csv/Kepler186_star_header.csv` | Header sao (KIC) | |
| `data/csv/Kepler186_Q2_raw.csv` | Quý 2 thô (3.612 dòng), có transit của **cả 5 hành tinh** | ⭐ Sheets |
| `data/csv/Kepler186_all_flat.csv` | 17 quý đã ghép + làm phẳng (64.437 dòng) | Python |
| `data/csv/Kepler186_Kepler186f_transits.csv` | 10 cửa sổ ±1.5 ngày quanh 10 transit của f (1.397 dòng) | ⭐ Sheets |
| `data/csv/Kepler186_Kepler186{b,c,d,e,f}_folded.csv` | Transit gấp pha, gộp bin + mô hình, từng hành tinh | Sheets |
| `data/csv/Kepler186_Kepler186{b..f}_transit_times.csv` | Thời điểm từng transit + O − C | Sheets (mục 9) |
| `data/csv/Kepler186_Kepler186f_ose_profile.csv` | Vùng vai quanh transit f | Sheets (mục 9) |
| `outputs/Kepler186_report.md` | Báo cáo đầy đủ | |
| `outputs/Kepler186_lightcurve.png`, `_periodogram.png`, `_folded.png` | Light curve, periodogram 5 vòng, 5 transit gấp pha | |
| `outputs/Kepler186_Kepler186f_transits.png` | 10 transit riêng của f + histogram báo động giả | |
| `outputs/Kepler186_diagram.png` | Sơ đồ hệ | |
| `outputs/Kepler186_moons.md`, `_moons.png` | Tìm vệ tinh | |

### 5.5. Đọc kết quả Python

Script dùng sao **KIC** (Rs 0.475, Ms 0.493 từ logg). a/Rs và b của mọi hành tinh có sai số lớn hơn giá trị (ví dụ f: a/Rs = 169 ± 763) nên **không dùng được**; khối lượng sao suy từ transit cũng vô nghĩa, script quay về dùng logg. Phần đáng tin là P, độ sâu, T14, Rp/Rs.

---

## 6. Phương án B: chỉ dùng Google Sheets

> ⚠️ Sheets vùng *Việt Nam* dùng `;` giữa các đối số. Công thức dưới viết theo vùng *United States* (**File → Settings → Locale → United States**), hoặc tự đổi `,` → `;`.

### 6.1. Lấy dữ liệu vào Sheets

- **Lối 1 (nhanh nhất):** dùng CSV có sẵn trong repo: `Kepler186_Q2_raw.csv` (thô, 1 quý) và `Kepler186_Kepler186f_transits.csv` (10 transit của f, đã làm phẳng).
- **Lối 2 (từ FITS, không code): TOPCAT** https://www.star.bris.ac.uk/~mbt/topcat/ (miễn phí, cần Java). Tải file ở mục 0.3 → TOPCAT **File → Load Table** (tự mở bảng LIGHTCURVE) → **Views → Columns Info** bỏ tick cột thừa, giữ `TIME`, `PDCSAP_FLUX`, `PDCSAP_FLUX_ERR`, `SAP_QUALITY` → **File → Save Table**, định dạng **csv**.
- **Lối 3:** chỉ chạy bước 1 Python để có CSV, còn lại làm trong Sheets.

### 6.2. Thấy cả 5 hành tinh trong 1 quý (Q2)

Import `Kepler186_Q2_raw.csv` (A `time_bkjd`, B `sap_flux`, C `pdcsap_flux`, D `pdcsap_flux_err`, E `flux_normalized`). Nếu đi Lối 2 thì lọc trước: `=FILTER(Q2!A2:B, Q2!D2:D=0, Q2!B2:B<>"")`.

1. **Vẽ thô**: A và E → Scatter. Bạn sẽ thấy sóng lên xuống tới ~0.3% kéo dài nhiều ngày: đó là **vết đen quay theo sao**, che lấp mọi transit.
2. **Làm phẳng** (trung vị trượt 49 điểm ≈ 1 ngày; ngắn hơn bản Python vì Sheets không che transit được, nhưng vẫn gấp ~4 lần transit dài nhất), F2, kéo xuống:
   ```
   =MEDIAN(INDEX(E:E, MAX(2, ROW()-24)):INDEX(E:E, MIN(COUNT(E:E)+1, ROW()+24)))
   ```
   G2: `=E2/F2`.
3. **Gấp pha từng hành tinh**: đặt bảng P, T0 (BKJD) ở J1:L6:

   | Hành tinh | P (ngày) | T0 (BKJD) |
   |---|---|---|
   | b | 3.8867907 | 133.3304 |
   | c | 7.267302 | 174.3142 |
   | d | 13.342996 | 176.9045 |
   | e | 22.407704 | 153.8006 |
   | f | 129.9441 | 176.829 |

   (T0 = `pl_tranmid` − 2454833.) Cột H (giờ từ tâm transit của b), H2: `=(MOD(A2-$L$2+$K$2/2,$K$2)-$K$2/2)*24`; tương tự cột I cho c (dùng $K$3, $L$3)...
4. **Vẽ** H và G → Scatter, trục X −6 tới 6 giờ, trục Y 0.998–1.0015: thấy lòng chảo của b (22 transit chồng lên nhau). Làm tương tự c, d, e. Với f trong Q2 chỉ có **1 transit** (BKJD 176.83), sâu ~500 ppm, chìm trong nhiễu ~400 ppm/điểm: chỉ thấy rõ khi gộp nhiều điểm (trung bình trượt 5 điểm).

### 6.3. Tính độ sâu và SNR của Kepler-186 f

Import `Kepler186_Kepler186f_transits.csv` vào tab `transits` (A `transit_no`, B `time_bkjd`, C `hours_from_mid_transit`, D `flux`). Trong transit = |giờ| ≤ 2 (phần giữa của transit 5.6 giờ); ngoài = |giờ| ≥ 6.

| Ô | Nội dung | Công thức | Kết quả |
|---|---|---|---|
| B1 | TB trong transit | `=AVERAGE(FILTER(transits!D2:D, ABS(transits!C2:C)<=2, transits!D2:D<>""))` | 0.999467 |
| B2 | TB ngoài transit | `=AVERAGE(FILTER(transits!D2:D, ABS(transits!C2:C)>=6, transits!D2:D<>""))` | 0.999978 |
| B3 | **Độ sâu** | `=(B2-B1)/B2` | 0.000511 |
| B4 | Độ sâu (ppm) | `=B3*1E6` | **511** |
| B5 | Số điểm trong | `=COUNTIFS(transits!C2:C,">=-2",transits!C2:C,"<=2")` | 80 |
| B6 | Số điểm ngoài | `=COUNTIFS(transits!C2:C,">=6")+COUNTIFS(transits!C2:C,"<=-6")` | 1154 |
| B7 | Nhiễu 1 điểm | `=STDEV(FILTER(transits!D2:D, ABS(transits!C2:C)>=6, transits!D2:D<>""))` | 0.000395 |
| B8 | **SNR** | `=B3/(B7*SQRT(1/B5+1/B6))` | **11.2** |

Từng transit (thêm `transits!A2:A=k` vào FILTER): 872, 474, 385, 401, 680, 489, 556, 166, 140, 932 ppm cho transit −6…4. Sai số mỗi transit ~140 ppm (8 điểm), nên độ tán xạ này hơi lớn hơn mong đợi: dấu hiệu của nhiễu đỏ và bùng sáng trên sao M.

Với b–e: import `Kepler186_Kepler186b_folded.csv` (v.v.). Cách nhanh `=1-MIN(B:B)` cho b 577, c 796, d 881, e 757 ppm, **cao hơn thật** ~15–20% vì lấy đúng bin thấp nhất (bị nhiễu kéo xuống). Chính xác hơn: lấy trung bình các bin trong nửa giữa transit, ví dụ với b (T14 1.84 giờ) `=1-AVERAGEIFS(B:B,A:A,">=-0.46",A:A,"<=0.46")`. Kết quả cách này: b 501, c 656, d 784, e 620 ppm (Python: 477, 662, 796, 636; KOI: 471, 659, 800, 661).

### 6.4. Thông số vật lý

Tab `params`: `B1` = độ sâu (tỉ lệ), `B2` = P, `B3` = Rs, `B4` = Ms, `B5` = Teff, `B6` = thị sai (mas) = 5.6336.

| Ô | Thông số | Công thức | f, sao NASA (0.523, 0.544, 3755) | f, sao KIC (0.475, 0.493, 3755) |
|---|---|---|---|---|
| B8 | Rp/Rs | `=SQRT(B1)` | 0.0226 | 0.0226 |
| B9 | **Rp (R⊕)** | `=B8*B3*109.1` | **1.29** | 1.17 |
| B10 | **a (AU)** | `=(B4*(B2/365.25)^2)^(1/3)` | **0.410** | 0.397 |
| B11 | L (L☉) | `=B3^2*(B5/5772)^4` | 0.0490 | 0.0404 |
| B12 | **S (× Trái Đất)** | `=B11/B10^2` | **0.29** | 0.26 |
| B13 | **Teq (K)** | `=B5*SQRT(B3*0.00465/(2*B10))*0.7^0.25` | **187** | 181 |
| B14 | Đặt T | `=B5-5780` | −2025 | −2025 |
| B15 | Ngưỡng trong (bảo thủ) | `=1.0385+1.2456E-4*B14+1.4612E-8*B14^2-7.6345E-12*B14^3-1.7511E-15*B14^4` | 0.880 | 0.880 |
| B16 | Ngưỡng ngoài (bảo thủ) | `=0.3507+5.9578E-5*B14+1.6707E-9*B14^2-3.0058E-12*B14^3-5.1925E-16*B14^4` | 0.253 | 0.253 |
| B17 | Vùng sống (AU) | `=SQRT(B11/B15)` → `=SQRT(B11/B16)` | **0.236 – 0.440** | 0.214 – 0.400 |
| B18 | Trong vùng sống? | `=IF(AND(B12<=B15,B12>=B16),"Có","Không")` | Có (gần mép ngoài) | Có (sát mép ngoài) |
| B19 | Khối lượng ước tính (M⊕) | `=IF(B9<1.23,(B9/1.008)^3.584,(B9/0.808)^1.698)` | ~2.2 | ~1.6 |
| B20 | Xác suất transit (%) | `=B3*0.00465/B10*100` | 0.59 | 0.56 |
| B21 | **Khoảng cách (pc)** | `=1000/B6` | **177.5** | |
| B22 | Năm ánh sáng | `=B21*3.2616` | **579** | |

(Rp ở đây dùng độ sâu "phần giữa transit" nên lớn hơn bản Python ~7%: tối rìa làm phần giữa sâu hơn trung bình.)

### 6.5. Transit tiếp theo của Kepler-186 f

`=2455789.494 + n*129.9441 - 2415018.5` rồi định dạng ô **Date time**:

| n | Ngày (UTC) |
|---|---|
| 43 | 02/12/2026 |
| 44 | 11/04/2027 |
| 45 | 19/08/2027 |

Sai số chu kỳ ~0.001 ngày × 45 vòng → lệch cỡ 1–2 giờ.

### 6.6. Giới hạn của Sheets

Không có BLS (không tự tìm chu kỳ), không khớp được mô hình tối rìa, không làm phẳng có che transit. Nhưng với P, T0 của NASA thì Sheets ra độ sâu, Rp, a, vùng sống, khoảng cách khớp Python trong ~10%.

---

## 7. Kết quả và so sánh với NASA

### 7.1. Từng hành tinh (Python, sao KIC; trong ngoặc: NASA `pscomppars`)

| | b | c | d | e | f |
|---|---|---|---|---|---|
| Tìm được | BLS tự tìm | BLS tự tìm | BLS tự tìm | BLS tự tìm | Kiểm chứng |
| P (ngày) | 3.88680 (3.88679) | 7.26727 (7.26730) | 13.34301 (13.34300) | 22.40776 (22.40770) | 129.9441 (129.9441) |
| SNR / số transit | 50 / 341 | 56 / 179 | 56 / 100 | 38 / 61 | 17 / 10 |
| KOI MES | 34.2 | 38.0 | 36.2 | 23.6 | 7.67 |
| Độ sâu (ppm) | 477 | 662 | 796 | 636 | 522 |
| T14 (giờ) | 1.84 (1.81) | 2.25 (2.27) | 2.70 (2.90) | 3.29 (3.32) | 5.67 (5.62) |
| Rp/Rs | 0.0201 (0.0208) | 0.0236 (0.0242) | 0.0259 (0.0272) | 0.0230 (0.0246) | 0.0210 (0.0205) |
| **Rp (R⊕)**, sao KIC | 1.04 (1.07) | 1.22 (1.25) | 1.34 (1.40) | 1.19 (1.27) | 1.09 (1.17) |
| a (AU), sao KIC | 0.0382 (0.0343*) | 0.0580 (0.0451*) | 0.0870 (0.0781*) | 0.1229 (0.1100*) | 0.3968 (0.4320*) |
| Teq (K) | 584 (571) | 474 (464) | 387 (379) | 326 (319) | 181 (177) |
| Bức xạ (× Trái Đất) | 28 (37) | 12 (14) | 5.3 (7.2) | 2.7 (3.6) | 0.26 (0.30) |
| Khối lượng ước tính (M⊕) | ~1.1 (1.24) | ~2.0 (2.10) | ~2.4 (2.54) | ~1.8 (2.15) | ~1.3 (1.71) |

\* a trên NASA **không khớp** định luật Kepler 3 với chính khối lượng sao NASA ghi: b với Ms = 0.478 phải là 0.0378 AU, không phải 0.0343; f với Ms = 0.544 phải là 0.410, không phải 0.432. Các cột trong bảng composite đến từ những bài báo khác nhau (mục 8.3).

**Tính lại f với sao Torres 2015** (Rs 0.523, Ms 0.544): Rp = 0.0210 × 0.523 × 109.1 = **1.20 R⊕** (NASA 1.17), a = 0.410 AU, S = 0.29, Teq = 187 K.

**Sao mẹ:**

| | Tự tính | NASA |
|---|---|---|
| Khoảng cách | **Gaia DR3: 177.5 ± 0.5 pc ≈ 579 năm ánh sáng** (RUWE 0.99) | 177.6 pc |
| Khoảng cách thô bằng độ sáng | ~191 pc | |
| Độ sáng L | 0.040 L☉ (KIC) | 0.049 (Torres) |
| Chu kỳ tự quay | ~35 ngày (từ đỉnh BLS giả) | |

### 7.2. Đọc bảng

- **Phần chỉ cần light curve** (P, T14, Rp/Rs): khớp NASA trong 3–7% (P khớp tới 5 chữ số). Rp/Rs của mình hơi thấp, một phần do hệ số tối rìa của sao G (mục 3.3).
- **Phần cần biết sao**: lệch ≤ 10% vì các bộ thông số sao M khá gần nhau.
- **Khối lượng**: NASA cũng chỉ ước tính từ bán kính, như mình.
- **f nằm trong vùng có thể sống** theo cả bộ sao KIC lẫn NASA, gần mép ngoài. Nếu dùng ngưỡng của sao giống Mặt Trời (1.06 / 0.36 S⊕) thì f bị xếp **ra ngoài** vùng sống: lý do phải dùng công thức phụ thuộc Teff.

### 7.3. Vậy Kepler-186 f là hành tinh thế nào?

- Cỡ **1.1–1.2 R⊕**, nhiều khả năng **đá** (dưới ranh giới 1.6 R⊕ khá xa). Nếu đá giống Trái Đất thì ~1.5–2 M⊕.
- Nhận ~**30% bức xạ** của Trái Đất, Teq ~180–190 K (−90 °C, chưa tính hiệu ứng nhà kính). Cần khí quyển CO₂ dày cỡ vài bar mới giữ được nước lỏng.
- Quay quanh sao M: có thể bị **khóa thủy triều** (một mặt luôn hướng về sao), sao M hay **bùng sáng** (flare) có thể bào mòn khí quyển. Cả hai đều chưa chắc chắn với f vì nó khá xa sao.
- Bốn hành tinh trong: đều cỡ Trái Đất, nhưng quá nóng (Teq 326–584 K, bức xạ 2.7–37 lần Trái Đất).

---

## 8. Những bài học riêng từ Kepler-186

### 8.1. Vết đen của sao M che lấp mọi thứ

Sao lùn M thường có **vết đen** lớn; sao quay ~35 ngày nên vết đen làm độ sáng dao động theo chu kỳ đó, tới ~3.200 ppm từ đỉnh tới đáy trong Q2, gấp 4–7 lần mọi transit. Cửa sổ làm phẳng 18 ngày (hợp với sao G yên tĩnh như Kepler-6, -10) thì quá dài: BLS bắt được ngay **chu kỳ tự quay** 34.85 ngày thay vì hành tinh. Bài học: **xem light curve thô trước khi chọn cửa sổ làm phẳng**.

### 8.2. Làm phẳng có thể "ăn" mất transit

Cửa sổ ngắn (2 ngày) khử được vết đen, nhưng đường xu hướng bám theo cả transit 5.7 giờ của f, làm nó nông đi: độ sâu 300 ppm, SNR 12. **Che transit đã biết** khi làm phẳng (tham số `mask` của `lightkurve.flatten`) đưa độ sâu về 433 ppm (BLS) / 522 ppm (mô hình), SNR 17, Rp/Rs khớp NASA.

### 8.3. Bảng composite lẫn nguồn ngay trong một hệ

Trong `pscomppars`, b–e dùng sao Quintana 2014 (0.472 R☉), còn f dùng sao Torres 2015 (0.523 R☉). Cột `pl_orbsmax` lại không khớp Kepler 3 với cả hai. Muốn bộ số nhất quán: dùng bảng `ps`, lọc theo **một** `pl_refname`.

### 8.4. Nhiều hành tinh là một "giấy chứng nhận"

Ứng viên đơn lẻ có tỉ lệ tín hiệu giả khá cao, nhưng **5 tín hiệu transit có chu kỳ khác nhau trên cùng một sao** thì gần như chắc chắn là hệ hành tinh thật (sao đôi che nhau không tạo ra 5 chu kỳ). Nhờ vậy cả hệ được xác nhận bằng thống kê dù không đo được khối lượng.

### 8.5. "Kiểm chứng" khác "phát hiện"

f không vượt ngưỡng phát hiện mù (SDE 7 < 9) nhưng kiểm chứng tại P, T0 đã biết thì rất rõ (SNR 17, 0/3000 báo động giả). Thử càng nhiều chu kỳ thì càng phải đòi tín hiệu mạnh hơn (*look-elsewhere effect*).

---

## 9. Tìm vệ tinh quanh các hành tinh Kepler-186

### 9.1. Kiến thức nền

Tới nay **chưa có exomoon nào được xác nhận**. Hai ứng viên từ dữ liệu Kepler đều đang bị tranh cãi: Kepler-1625b-i (Teachey & Kipping 2018) và Kepler-1708b-i (Kipping et al. 2022). Với dữ liệu Kepler, mục tiêu thực tế là **đặt giới hạn trên**.

**Bước 1. Vệ tinh có thể tồn tại ở đâu?**

| Đại lượng | Công thức |
|---|---|
| Bán kính Hill | $R_H = a\left(M_p/(3M_s)\right)^{1/3}$ |
| Quỹ đạo bền xa nhất | $a_{max} \approx 0.49\,R_H$ (cùng chiều; Domingos et al. 2006) |
| Giới hạn Roche (vệ tinh đá 3 g/cm³) | $a_R \approx 2.44\,R_p(\rho_p/\rho_v)^{1/3}$ |
| Chu kỳ vệ tinh dài nhất | $2\pi\sqrt{a_{max}^3/(GM_p)}$ |
| Vận tốc hành tinh | $v_p = 2\pi a/P$ |
| Vệ tinh lệch trước/sau hành tinh tối đa | $\Delta t_{max} = a_{max}/v_p$ |

Nếu $a_{max} < a_R$ thì không có quỹ đạo vệ tinh bền. Hành tinh càng gần sao, thủy triều càng nhanh làm mất vệ tinh (Barnes & O'Brien 2002). Sao M nhẹ nên **bán kính Hill của hành tinh quanh sao M lớn hơn** so với cùng khoảng cách quanh sao G, nhưng các hành tinh lại ở rất gần sao.

**Bước 2. TTV**: hành tinh bị vệ tinh kéo lắc quanh tâm khối chung nên đến sớm/muộn tối đa $a_v M_v/(M_p v_p)$.
1. Đo thời điểm từng transit; khớp $t_c = T_0 + nP$ (loại transit ngoại lai > 5 MAD); tính **O − C**.
2. Periodogram **Lomb–Scargle** của O − C, đọc **FAP**; cần ≥ 8 transit.
3. Loại 3 nguồn giả: **lệch pha lưới đo 29.4 phút** (họa âm chu kỳ phách, và O − C có đổi theo vị trí tâm transit trong lưới đo không), **tín hiệu không lặp lại ở cả hai nửa dữ liệu** (nhiễu đỏ, vết đen), và **hành tinh khác** trong hệ.
4. Giới hạn: $M_{v,max} = \sqrt{2}\,\sigma_{TTV}\,v_p M_p/a_{max}$, với $\sigma_{TTV}$ = O − C rms.

**TDV** (biến thiên thời lượng, lệch pha 90° với TTV) giúp tách khối lượng và khoảng cách vệ tinh; script chưa đo.

**Bước 3. OSE** (Heller 2014): cộng nhiều transit, bóng vệ tinh thành **vai trũng nông** hai bên transit hành tinh trong ±Δt_max. Đo vai trũng D ± σ_D so với nền:
$$R_{v,max} = R_s\sqrt{(\max(D,0)+2\sigma_D)\cdot\frac{2\Delta t_{max}+T_{14}}{T_{14}}}$$
Nếu $\Delta t_{max}$ nhỏ hơn nửa T14 thì vệ tinh luôn "núp" trong transit hành tinh, OSE không tách được.

So sánh: Mặt Trăng 0.273 R⊕, Titan 0.404, Ganymede 0.413, Sao Hỏa 0.532.

### 9.2. Python

```bash
.venv/Scripts/python scripts/04_moons.py "Kepler-186"
```
Kết quả `outputs/Kepler186_moons.md`, `outputs/Kepler186_moons.png` (trái: O − C từng hành tinh, dấu × đỏ là transit ngoại lai đã loại; phải: vùng vai OSE), cùng `data/csv/Kepler186_<hành tinh>_transit_times.csv` và `Kepler186_Kepler186f_ose_profile.csv`.

### 9.3. Google Sheets

Tab `moon`, đầu vào: `B1` Mp (M⊕), `B2` Ms (M☉), `B3` a (AU), `B4` P (ngày), `B5` Rp (R⊕), `B6` Rs (R☉), `B7` T14 (giờ).

| Ô | Thông số | Công thức |
|---|---|---|
| B9 | Bán kính Hill (km) | `=B3*1.496E8*(B1*5.972E24/(3*B2*1.989E30))^(1/3)` |
| B10 | a_max (km) | `=0.4895*B9` |
| B11 | Mật độ hành tinh | `=5.51*B1/B5^3` |
| B12 | Giới hạn Roche (km) | `=2.44*B5*6371*(B11/3)^(1/3)` |
| B13 | Có thể có vệ tinh? | `=IF(B10>B12,"Có","Không")` |
| B14 | Chu kỳ vệ tinh dài nhất (ngày) | `=2*PI()*SQRT((B10*1000)^3/(6.674E-11*B1*5.972E24))/86400` |
| B15 | v_p (km/s) | `=2*PI()*B3*1.496E8/(B4*86400)` |
| B16 | Δt_max (giờ) | `=B10/B15/3600` |

**TTV:** import `Kepler186_Kepler186f_transit_times.csv` vào tab `tt` (A `epoch`, B `tc_bkjd`, C `sigma_min`, D `oc_min`, E `used`):
- `B19` O − C rms (phút): `=SQRT(SUMPRODUCT(tt!D2:D20^2*(tt!E2:E20=1))/COUNTIF(tt!E2:E20,1))` → **60.5**
- `B21` Khối lượng vệ tinh tối đa (M⊕): `=SQRT(2)*B19*60*B15*B1/B10`; `B22` theo Mặt Trăng: `=B21*81.3`
- Kiểm tra lỗi lấy mẫu bằng mắt: cột F `=MOD(tt!B2/0.0204340,1)`, vẽ D theo F.

**OSE:** import `Kepler186_Kepler186f_ose_profile.csv` vào tab `ose` (A giờ, B độ sáng gộp bin, C số điểm). Ranh giới: `B23` `=0.6*B7+0.49`, `B24` `=B16+B7/2`, `B25` `=B24+B7/2`, `B26` `=B25+MAX(2*B16,24)`.

| Ô | Thông số | Công thức |
|---|---|---|
| B27 | TB vùng vai | `=SUMPRODUCT(ose!B2:B200*ose!C2:C200*(ABS(ose!A2:A200)>B23)*(ABS(ose!A2:A200)<B24))/SUMPRODUCT(ose!C2:C200*(ABS(ose!A2:A200)>B23)*(ABS(ose!A2:A200)<B24))` |
| B28 | TB vùng nền | như B27, thay B23→B25, B24→B26 |
| B29 | Vai trũng D (ppm) | `=(B28-B27)*1E6` |
| B30, B31 | Số bin vai / nền | `=SUMPRODUCT((ABS(ose!A2:A200)>B23)*(ABS(ose!A2:A200)<B24))` / tương tự với B25, B26 |
| B32 | σ_D (ppm) | `=STDEV(FILTER(ose!B2:B200,ABS(ose!A2:A200)>B25,ABS(ose!A2:A200)<B26))*1E6*SQRT(1/B30+1/B31)` |
| B33 | **Bán kính vệ tinh tối đa (R⊕)** | `=SQRT((MAX(B29,0)+2*B32)*1E-6*(2*B16+B7)/B7)*B6*109.1` |

Kết quả Sheets cho f: **0.91 R⊕** (sao KIC), **1.0 R⊕** (sao NASA); Python 0.84 R⊕ (sai số theo bin khác một chút).

### 9.4. Kết quả (Python, sao KIC, khối lượng hành tinh ước tính từ bán kính)

| | b | c | d | e | f |
|---|---|---|---|---|---|
| Khối lượng hành tinh dùng (M⊕) | 1.1 | 2.0 | 2.4 | 1.8 | 1.3 |
| Vùng vệ tinh bền (km) | 19.800 – 36.900 | 24.000 – 67.800 | 25.400 – 107.500 | 23.300 – 139.200 | 20.900 – **403.100** |
| Chu kỳ vệ tinh dài nhất (ngày) | 0.77 | 1.44 | 2.64 | 4.43 | 25.7 |
| Δt_max (giờ) | 0.10 | 0.22 | 0.42 | 0.65 | 3.37 |
| Transit định thời được | 299 | 158 (loại 2) | 85 (loại 3) | 45 | 9 |
| Sai số mỗi transit (phút) | 23 | 16 | 16 | 23 | 21 |
| O − C rms (phút) | 29.5 | 20.4 | 15.7 | 31.9 | 60.5 |
| Periodogram O − C: chu kỳ / FAP | 6.8 vòng / 3·10⁻⁴ | 19.9 / 0.10 | 2.9 / 0.26 | 4.8 / 0.87 | 8.3 / 0.64 |
| **Kết luận TTV** | Đỉnh 6.8 vòng **chỉ có ở nửa sau** dữ liệu → nhiễu | Không | Không | Không | Không |
| **Khối lượng vệ tinh tối đa** | 8.2 M⊕ | 4.5 M⊕ | 2.1 M⊕ | 2.1 M⊕ | **0.56 M⊕ (45 Mặt Trăng)** |
| **Bán kính vệ tinh tối đa (OSE)** | — (núp trong transit) | — | — | — | **0.84 R⊕** |

Tính lại cho f với sao NASA (Rp 1.20 R⊕ → Mp ~1.9 M⊕): a_max 452.000 km, Roche 23.400 km, Δt_max 3.7 giờ, khối lượng vệ tinh tối đa ~**0.72 M⊕ (~59 Mặt Trăng)**, bán kính tối đa ~**1.0 R⊕** (Sheets).

**Đọc kết quả:**
- Mọi hành tinh đều **có thể** giữ vệ tinh về mặt hình học, nhưng b–e quá gần sao: vùng bền hẹp, thủy triều mạnh, vệ tinh khó tồn tại lâu. f là ứng viên hợp lý nhất.
- **Không thấy dấu hiệu vệ tinh nào.** Giới hạn còn rất lỏng: chỉ loại được vệ tinh cỡ Trái Đất quanh f; vệ tinh cỡ Sao Hỏa, Ganymede, Mặt Trăng vẫn hoàn toàn có thể có.
- Kepler-186b cho thấy vì sao phải kiểm tra kỹ: FAP 3·10⁻⁴ trông "có ý nghĩa", nhưng tín hiệu không lặp lại ở nửa đầu dữ liệu (nửa đầu đỉnh mạnh nhất ở 2.4 vòng). NASA cũng không ghi nhận TTV cho hệ này (`ttv_flag = 0`).
- O − C của f tán xạ 60 phút trong khi sai số ước tính 21 phút: với transit yếu (mỗi transit chỉ SNR ~5), phép định thời đánh giá thấp sai số. Giới hạn dùng chính độ tán xạ 60 phút nên vẫn an toàn (thận trọng).

---

## 10. Bảng thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|---|---|
| Exoplanet | Hành tinh quay quanh một sao khác ngoài Mặt Trời |
| Transit | Hành tinh đi ngang trước sao, làm sao tối đi một chút |
| Light curve | Đồ thị/bảng độ sáng theo thời gian |
| Flux / Photometry | Độ sáng đo được / kỹ thuật đo độ sáng |
| Spectroscopy | Quang phổ học: cho Teff, logg, [Fe/H] chính xác hơn trắc quang |
| Aperture | Tập pixel được cộng lại để đo sáng |
| Cadence | Khoảng giữa 2 lần đo (long cadence 29.4 phút) |
| Quarter | Một quý dữ liệu Kepler (~90 ngày), mỗi quý 1 file |
| KIC / KOI | Danh mục sao Kepler / ứng viên hành tinh Kepler |
| DR25 | Bản xử lý cuối cùng của dữ liệu Kepler |
| MAST | Kho dữ liệu STScI chứa dữ liệu Kepler/K2/TESS |
| NASA Exoplanet Archive | Kho thông số hành tinh của NASA (Caltech/IPAC) |
| TAP / ADQL | Truy vấn bảng thiên văn qua URL / ngôn ngữ giống SQL |
| pscomppars / ps | Bảng composite (ghép nguồn) / từng bộ thông số đã công bố |
| FITS / HDU | Định dạng file thiên văn / một "tab" trong file |
| TOPCAT | Phần mềm miễn phí chuyển FITS → CSV không cần code |
| BKJD / BJD | Hệ thời gian (ngày); BKJD = BJD − 2454833 |
| ppm | Phần triệu |
| R☉ / R⊕ / M☉ / M⊕ | Bán kính, khối lượng Mặt Trời / Trái Đất |
| Red dwarf / M dwarf | Sao lùn đỏ: sao nhỏ, lạnh (< ~3.900 K), phổ biến nhất Ngân Hà |
| Starspot / rotation | Vết đen trên sao quay theo sao, làm độ sáng dao động theo chu kỳ tự quay |
| Flare | Bùng sáng đột ngột trên sao, hay gặp ở sao lùn M |
| Flatten / detrend | Làm phẳng: loại biến thiên chậm của sao và thiết bị |
| Transit mask | Che các điểm trong transit khi làm phẳng để transit không bị nông đi |
| BLS / Periodogram | Thuật toán tìm transit có chu kỳ / đồ thị độ mạnh theo chu kỳ thử |
| SDE / SNR / MES | Độ nổi bật của đỉnh periodogram / tín hiệu trên nhiễu / SNR pipeline Kepler (ngưỡng 7.1) |
| Robovetter / koi_score | Bộ lọc tự động của Kepler / độ tin của nó (0–1) |
| Phase fold | Gấp dữ liệu theo chu kỳ để chồng các transit |
| Ephemeris | Bộ (P, T0) dự đoán thời điểm transit |
| Kiểm chứng (verification) | Đo tín hiệu tại P, T0 đã biết, khác với tìm mù |
| Phép thử báo động giả | Đo lại ở nhiều (P, T0) ngẫu nhiên xem nhiễu tạo ra tín hiệu mạnh như vậy thường đến mức nào |
| Look-elsewhere effect | Thử càng nhiều chỗ càng dễ gặp tín hiệu giả do may rủi |
| White / red noise | Nhiễu độc lập từng điểm / nhiễu tương quan kéo dài, giả dạng được transit |
| Validation | Xác nhận hành tinh bằng thống kê, không đo khối lượng |
| Multiplicity boost | Hệ nhiều hành tinh transit ít khả năng là tín hiệu giả, giúp xác nhận bằng thống kê |
| Controversial flag | `pl_controv_flag = 1`: sự tồn tại của hành tinh đang bị nghi ngờ |
| Ingress / Egress / T14 | Đoạn đi vào / đi ra đĩa sao / tổng thời lượng transit |
| Impact parameter b / a/Rs / i | Hành tinh đi qua cách tâm sao bao xa / khoảng cách theo bán kính sao / độ nghiêng quỹ đạo |
| Limb darkening | Tối rìa: rìa sao tối hơn tâm, đáy transit cong |
| Exposure smearing | Nhòe do phơi sáng 29.4 phút |
| batman | Thư viện Python mô hình transit có tối rìa |
| Teq / Insolation / Albedo | Nhiệt độ cân bằng / bức xạ nhận được / tỉ lệ phản xạ |
| Habitable zone | Vùng có thể sống: nước có thể lỏng trên bề mặt; ngưỡng phụ thuộc nhiệt độ sao |
| Runaway / maximum greenhouse | Mép trong / mép ngoài của vùng có thể sống bảo thủ |
| Tidal locking | Khóa thủy triều: một mặt hành tinh luôn hướng về sao |
| RV, K | Vận tốc xuyên tâm của sao do hành tinh kéo / biên độ |
| Mass–radius relation | Ước tính khối lượng từ bán kính |
| Parallax / Gaia / RUWE | Thị sai / vệ tinh ESA đo thị sai / chỉ số chất lượng (< 1.4 tin được) |
| Exomoon | Vệ tinh của hành tinh ngoài Hệ Mặt Trời |
| Hill sphere / Roche limit | Vùng hành tinh giữ được vệ tinh / khoảng cách tối thiểu trước khi vệ tinh bị xé vụn |
| O − C | Thời điểm transit đo được trừ dự đoán |
| TTV / TDV | Biến thiên thời điểm / thời lượng transit |
| OSE | Bóng vệ tinh cộng qua nhiều transit thành "vai" trũng nông |
| Lomb–Scargle / FAP | Periodogram cho dữ liệu lấy mẫu không đều / xác suất báo động giả |
| Cadence alias | Dao động giả trong O − C do tâm transit rơi vào vị trí khác nhau trong lưới đo |

---

## 11. Tài liệu tham khảo

- Quintana, E. V. et al. 2014, *An Earth-Sized Planet in the Habitable Zone of a Cool Star*, Science 344, 277. https://ui.adsabs.harvard.edu/abs/2014Sci...344..277Q/abstract
- Torres, G. et al. 2015, ApJ 800, 99 (thông số mặc định của Kepler-186 f trên NASA). https://ui.adsabs.harvard.edu/abs/2015ApJ...800...99T/abstract
- Thompson, S. E. et al. 2018, ApJS 235, 38 (danh sách ứng viên Kepler DR25).
- Lissauer, J. J. et al. 2012, ApJ 750, 112 (hệ nhiều hành tinh ít khả năng là tín hiệu giả).
- Kopparapu, R. K. et al. 2013, ApJ 765, 131 (vùng có thể sống phụ thuộc nhiệt độ sao).
- Chen, J. & Kipping, D. 2017, ApJ 834, 17 (quan hệ khối lượng – bán kính).
- Kipping, D. M. 2009, MNRAS 392, 181 (TTV và TDV do vệ tinh).
- Heller, R. 2014, ApJ 787, 14 (Orbital Sampling Effect).
- Domingos, R. C., Winter, O. C. & Yokoyama, T. 2006, MNRAS 373, 1227 (vùng bền của vệ tinh).
- Barnes, J. W. & O'Brien, D. P. 2002, ApJ 575, 1087 (vệ tinh quanh hành tinh gần sao).
- Teachey, A. & Kipping, D. M. 2018, Science Advances 4, eaav1784; Kipping, D. et al. 2022, Nature Astronomy 6, 367 (hai ứng viên exomoon).
- NASA Exoplanet Archive, Kepler-186: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-186
- MAST Kepler: https://archive.stsci.edu/missions-and-data/kepler ; Lightkurve: https://lightkurve.github.io/lightkurve/ ; TOPCAT: https://www.star.bris.ac.uk/~mbt/topcat/
- Sổ tay chung: [`kien-thuc-exoplanet.md`](kien-thuc-exoplanet.md); hệ khác: [`kepler-452.md`](kepler-452.md)
