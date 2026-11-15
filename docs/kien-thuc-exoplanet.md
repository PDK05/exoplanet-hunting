# Kiến thức Exoplanet & dữ liệu Kepler

Sổ tay ghi lại các khái niệm khi học săn exoplanet. Được cập nhật dần, không lặp lại nội dung đã có.

## Mục lục

1. [Kepler làm gì?](#1-kepler-làm-gì)
2. [Các loại dữ liệu Kepler](#2-các-loại-dữ-liệu-kepler)
3. [Mổ xẻ một file raw: định dạng FITS](#3-mổ-xẻ-một-file-raw-định-dạng-fits)
4. [Các khái niệm về hành tinh (bảng KOI)](#4-các-khái-niệm-về-hành-tinh-bảng-koi)
5. [Lộ trình bắt đầu](#5-lộ-trình-bắt-đầu)
6. [Bảng thuật ngữ nhanh](#6-bảng-thuật-ngữ-nhanh)
7. [Từ transit tính ra được gì?](#7-từ-transit-tính-ra-được-gì)
8. [Thực hành: tải dữ liệu, vẽ và tính thông số](#8-thực-hành-tải-dữ-liệu-vẽ-và-tính-thông-số)

---

## 1. Kepler làm gì?

Kepler là kính thiên văn không gian của NASA, hoạt động 2009–2013 (sau đó là nhiệm vụ K2, tới 2018). Kính **nhìn cố định vào một vùng trời** (chòm Thiên Nga – Thiên Cầm) và đo **độ sáng của khoảng 150.000 ngôi sao** liên tục, khoảng 30 phút một lần, trong 4 năm.

Phương pháp tìm hành tinh là **transit (quá cảnh)**: khi hành tinh đi ngang qua trước mặt ngôi sao, độ sáng của sao **giảm đi một chút** rồi trở lại bình thường, và hiện tượng này **lặp lại theo chu kỳ**.

```
Độ sáng
  1.000 ─────────┐     ┌──────────────┐     ┌──────
                 │     │              │     │
  0.999          └─────┘              └─────┘
                 ← transit →
                 |←──── chu kỳ (period) ────→|
```

Vậy "săn exoplanet" thực chất là **tìm những chỗ trũng nhỏ, lặp lại đều đặn trong chuỗi độ sáng theo thời gian**.

## 2. Các loại dữ liệu Kepler

| Loại | Là gì | Dùng khi nào |
|---|---|---|
| **Light curve** (`*_llc.fits`, `*_slc.fits`) | Bảng độ sáng theo thời gian của 1 ngôi sao | **Bắt đầu từ đây** |
| **Target Pixel File** (`*_lpd-targ.fits`) | Ảnh pixel thô quanh ngôi sao ở từng thời điểm | Nâng cao: tự làm photometry, kiểm tra nhiễu |
| **KOI table** (Kepler Objects of Interest) | Bảng ứng viên hành tinh NASA đã phân tích sẵn | Lấy nhãn để kiểm tra, hoặc train ML |
| **KIC** (Kepler Input Catalog) | Danh mục thông tin các ngôi sao | Tra kích thước, nhiệt độ của sao |

**Nguồn dữ liệu:**
- **MAST** (https://archive.stsci.edu): light curve, target pixel file.
- **NASA Exoplanet Archive** (https://exoplanetarchive.ipac.caltech.edu): bảng KOI, danh sách hành tinh đã xác nhận.

### 2.1. Dữ liệu Kepler có "chuyển qua K2" không?

**Không.** Toàn bộ dữ liệu Kepler gốc (2009–2013) **vẫn public, miễn phí và đã ở dạng bản cuối cùng**. K2 là **một nhiệm vụ khác** dùng lại cùng con tàu, dữ liệu được lưu riêng, không thay thế dữ liệu Kepler.

**Lịch sử ngắn:**
- **2009–2013, Kepler:** nhìn cố định 1 vùng trời suốt 4 năm. Tháng 5/2013, bánh xe giữ hướng thứ 2 bị hỏng, tàu không thể chĩa cố định được nữa.
- **2014–2018, K2:** dùng áp suất ánh sáng Mặt Trời để giữ thăng bằng, quan sát các vùng **dọc hoàng đạo**, mỗi vùng ~80 ngày (gọi là **campaign**, C0–C19). Tàu nghỉ hưu tháng 10/2018 vì hết nhiên liệu.
- **2018–nay, TESS:** nhiệm vụ kế nhiệm, quét gần như toàn bộ bầu trời, mỗi vùng ~27 ngày.

| | Kepler | K2 | TESS |
|---|---|---|---|
| Thời gian | 2009–2013 | 2014–2018 | 2018–nay |
| Vùng trời | 1 vùng cố định | ~20 vùng dọc hoàng đạo | Gần toàn bầu trời |
| Thời gian quan sát mỗi sao | ~4 năm | ~80 ngày | ~27 ngày (có vùng lâu hơn) |
| Mã sao | **KIC** | **EPIC** | **TIC** |
| Tên file | `kplr<KIC>-..._llc.fits` | `ktwo<EPIC>-c<campaign>_llc.fits` | `tess..._lc.fits` |
| Độ "sạch" dữ liệu | Rất tốt | Nhiễu hơn (tàu trôi, đốt động cơ ~6 giờ/lần) | Tốt, nhưng chuỗi ngắn hơn |

**Bản dữ liệu cuối cùng của Kepler:** **DR25** (Data Release 25), xử lý lại toàn bộ Q1–Q17. Bảng KOI tương ứng là **"Q1–Q17 DR25 KOI table"** trên NASA Exoplanet Archive. Đây là bảng nên dùng (các bảng cũ hơn như DR24 vẫn còn nhưng đã lỗi thời).

**Lấy dữ liệu Kepler ở đâu (đều miễn phí, không cần tài khoản):**
- **MAST Kepler**: https://archive.stsci.edu/missions-and-data/kepler (có trang tải hàng loạt *bulk download*).
- **MAST Portal**: https://mast.stsci.edu, tìm theo tên sao hoặc KIC.
- **NASA Exoplanet Archive**: bảng KOI DR25, bảng hành tinh đã xác nhận.
- **Thư viện `lightkurve`**: gọi MAST từ Python, tiện nhất khi bắt đầu.
- **AWS Open Data**: STScI có bản sao dữ liệu Kepler/K2/TESS trên AWS, dùng khi cần tải số lượng lớn.

**Nên dùng cái nào?** Người mới nên **bắt đầu với Kepler**: chuỗi dài 4 năm nên transit lặp lại nhiều lần, dữ liệu sạch, lại có bảng KOI làm "đáp án" để kiểm tra. K2 và TESS dùng sau, khi đã quen quy trình.

## 3. Mổ xẻ một file raw: định dạng FITS

FITS là định dạng file chuẩn của thiên văn học. Một file gồm nhiều **HDU** (Header + Data Unit), giống như nhiều "tab":

```
kplr011904151-2010265121752_llc.fits
 │     │         │            │
 │     │         │            └─ llc = long cadence light curve
 │     │         └─ thời điểm tạo file (năm 2010, ngày 265...)
 │     └─ KIC ID: mã ngôi sao (9 chữ số), ở đây là Kepler-10
 └─ kplr = Kepler

HDU 0  PRIMARY     → chỉ có header: thông tin về ngôi sao
HDU 1  LIGHTCURVE  → bảng dữ liệu chính (phần quan trọng nhất)
HDU 2  APERTURE    → ảnh nhỏ cho biết pixel nào được cộng lại để đo sáng
```

### 3.1. Header (HDU 0): thông tin ngôi sao

| Khóa | Ý nghĩa |
|---|---|
| `KEPLERID` | Mã KIC của sao |
| `RA_OBJ`, `DEC_OBJ` | **Xích kinh / Xích vĩ**: "kinh độ, vĩ độ" trên bầu trời, đơn vị độ |
| `KEPMAG` | **Cấp sao (magnitude)** theo bộ lọc Kepler. ⚠️ **Số càng nhỏ, sao càng sáng** (thang log ngược) |
| `TEFF` | Nhiệt độ bề mặt (Kelvin). Mặt Trời ≈ 5772 K |
| `LOGG` | Log gia tốc trọng trường bề mặt: cho biết sao lùn (~4.4) hay sao khổng lồ (~2–3) |
| `RADIUS` | Bán kính sao, đơn vị **bán kính Mặt Trời** (R☉) |
| `QUARTER` | Kepler chia dữ liệu thành các **quý** Q0–Q17, mỗi quý ~90 ngày, **mỗi quý một file** |

### 3.2. Bảng dữ liệu (HDU 1): mỗi dòng là một lần đo

| Cột | Ý nghĩa | Ghi chú |
|---|---|---|
| `TIME` | Thời điểm đo | Đơn vị **BKJD** = BJD − 2454833 (số ngày). BJD là thời gian đã hiệu chỉnh về tâm Hệ Mặt Trời |
| `CADENCENO` | Số thứ tự lần đo | |
| `SAP_FLUX` | Độ sáng **thô** (Simple Aperture Photometry): cộng sáng của các pixel quanh sao | Đơn vị e⁻/s (số electron/giây). Còn nhiễu do kính thiên văn |
| `PDCSAP_FLUX` | Độ sáng **đã làm sạch** nhiễu hệ thống của thiết bị | ✅ **Thường dùng cột này** |
| `*_ERR` | Sai số của từng giá trị | |
| `SAP_BKG` | Độ sáng nền trời đã bị trừ đi | |
| `SAP_QUALITY` | **Cờ chất lượng**: 0 = tốt, khác 0 = có vấn đề (tia vũ trụ, xoay tàu...) | Nên loại các dòng khác 0 |
| `MOM_CENTR1/2` | Vị trí tâm sáng của sao trên cảm biến | Dùng để phát hiện **false positive** (mục 4) |
| `POS_CORR1/2` | Độ lệch vị trí do tàu rung | |

**Lưu ý:**
- Dữ liệu có khá nhiều **NaN**: đó là các lần đo bị hỏng hoặc thiếu, phải lọc bỏ.
- **Cadence** là khoảng cách giữa 2 lần đo:
  - **Long cadence ≈ 29.4 phút**: mọi sao đều có.
  - **Short cadence ≈ 1 phút** (58.8 giây): chỉ một số sao được chọn.

## 4. Các khái niệm về hành tinh (bảng KOI)

| Khái niệm | Cột KOI | Ý nghĩa |
|---|---|---|
| **Chu kỳ** | `koi_period` | Số ngày hành tinh quay hết một vòng quanh sao |
| **Epoch / T0** | `koi_time0bk` | Thời điểm của transit đầu tiên (BKJD) |
| **Độ sâu** | `koi_depth` | Độ sáng giảm bao nhiêu, đơn vị **ppm** (phần triệu) |
| **Thời lượng** | `koi_duration` | Một lần transit kéo dài bao lâu (giờ) |
| **Bán kính hành tinh** | `koi_prad` | Đơn vị bán kính Trái Đất (R⊕) |
| **Kết luận** | `koi_disposition` | `CONFIRMED` / `CANDIDATE` / `FALSE POSITIVE` |

### 4.1. Công thức quan trọng nhất

$$\text{Độ sâu} \approx \left(\frac{R_{\text{hành tinh}}}{R_{\text{sao}}}\right)^2$$

Để hình dung độ lớn:
- Trái Đất đi qua Mặt Trời: sáng giảm **~84 ppm (0.0084%)**.
- Sao Mộc đi qua Mặt Trời: sáng giảm **~1%**.

Vì thế hành tinh nhỏ rất khó tìm.

### 4.2. False positive

Là tín hiệu trông giống transit nhưng **không phải hành tinh**. Hay gặp nhất:
- **Sao đôi che khuất nhau** (eclipsing binary).
- Ánh sáng từ **một sao khác ở gần** lọt vào vùng đo.

Phần lớn công sức thật sự nằm ở việc loại bỏ những trường hợp này.

## 5. Lộ trình bắt đầu

1. **Cài Python + thư viện `lightkurve`.** Đây là thư viện chính thức của cộng đồng Kepler/TESS: tự tải file từ MAST, đọc FITS, lọc chất lượng, làm phẳng và vẽ biểu đồ.
2. **Bắt đầu với một hành tinh đã biết**, ví dụ **Kepler-10** (KIC 11904151): tải light curve, vẽ ra và nhìn tận mắt các chỗ trũng.
3. **Làm sạch → làm phẳng (flatten) → tìm chu kỳ** bằng thuật toán **BLS** (Box Least Squares) → **gấp pha (fold)** theo chu kỳ để chồng các transit lên nhau.
4. **So kết quả với bảng KOI** để kiểm tra mình làm đúng chưa.
5. Sau đó mới săn trên các sao `CANDIDATE`, hoặc tải toàn bộ bảng KOI để làm bài toán phân loại bằng ML.

## 6. Bảng thuật ngữ nhanh

| Thuật ngữ | Giải thích ngắn |
|---|---|
| Exoplanet | Hành tinh quay quanh một ngôi sao khác ngoài Mặt Trời |
| Transit | Hành tinh đi ngang trước mặt sao, làm sao tối đi một chút |
| Light curve | Đồ thị/bảng độ sáng theo thời gian |
| Flux | Độ sáng đo được (lượng ánh sáng nhận được) |
| Photometry | Kỹ thuật đo độ sáng |
| Aperture | Tập pixel được cộng lại để đo sáng một ngôi sao |
| Cadence | Khoảng thời gian giữa 2 lần đo |
| Quarter | Một quý dữ liệu Kepler (~90 ngày) |
| KIC | Kepler Input Catalog: danh mục và mã số các sao |
| KOI | Kepler Object of Interest: ứng viên hành tinh |
| K2 | Nhiệm vụ thứ 2 của tàu Kepler (2014–2018), quan sát theo từng campaign |
| Campaign | Một đợt quan sát ~80 ngày của K2 (C0–C19) |
| EPIC | Mã số sao trong K2 (tương đương KIC của Kepler) |
| TESS | Kính thiên văn kế nhiệm Kepler, quét gần toàn bầu trời; mã sao là TIC |
| DR25 | Data Release 25: bản xử lý cuối cùng của dữ liệu Kepler |
| MAST | Kho lưu trữ dữ liệu của STScI, nơi chứa dữ liệu Kepler/K2/TESS |
| Ingress / Egress | Đoạn hành tinh đang đi vào / đi ra khỏi đĩa sao (2 sườn dốc của transit) |
| T14 / T23 | Thời lượng transit tính từ lúc chạm mép đầu tới mép cuối / phần đáy khi hành tinh nằm trọn trong đĩa sao |
| Impact parameter (b) | Tham số va chạm: hành tinh đi qua cách tâm sao bao xa (0 = qua chính giữa, ~1 = sượt mép) |
| a / Rs | Khoảng cách hành tinh – sao tính theo đơn vị bán kính sao |
| Inclination (i) | Độ nghiêng quỹ đạo so với hướng nhìn; 90° = nhìn đúng mép quỹ đạo |
| Semi-major axis (a) | Bán trục lớn: "bán kính" trung bình của quỹ đạo, thường đo bằng AU |
| AU | Đơn vị thiên văn = khoảng cách Trái Đất – Mặt Trời ≈ 150 triệu km |
| Limb darkening | Tối rìa: rìa đĩa sao tối hơn tâm, làm đáy transit cong chứ không phẳng |
| Exposure smearing | Nhòe do phơi sáng: mỗi điểm Kepler cộng dồn 29.4 phút nên ingress/egress bị kéo dài |
| Equilibrium temperature (Teq) | Nhiệt độ cân bằng: nhiệt độ ước tính của hành tinh chỉ do sao mẹ sưởi |
| Insolation | Lượng bức xạ hành tinh nhận được, so với Trái Đất |
| Albedo | Tỉ lệ ánh sáng bị phản xạ đi (0 = hấp thụ hết, 1 = phản xạ hết) |
| Radial velocity (RV) | Vận tốc xuyên tâm: sao bị hành tinh kéo nên dao động tới lui; cách để đo khối lượng hành tinh |
| Semi-amplitude K | Biên độ dao động vận tốc của sao do hành tinh gây ra (m/s) |
| Metallicity [Fe/H] | Độ kim loại: hàm lượng nguyên tố nặng hơn He so với Mặt Trời, thang log |
| Spectral type | Loại phổ của sao theo nhiệt độ: O B A F G K M (nóng → lạnh); Mặt Trời là G |
| Kepler's third law | Định luật Kepler 3: liên hệ chu kỳ, khoảng cách và khối lượng sao |
| batman | Thư viện Python tạo mô hình transit chính xác (có tối rìa) |
| Hot Jupiter | Khí khổng lồ quay rất gần sao, chu kỳ vài ngày, rất nóng |
| Parallax (thị sai) | Sao gần "dịch chuyển" nhẹ trên nền trời khi Trái Đất quay quanh Mặt Trời; góc dịch càng nhỏ thì sao càng xa |
| mas / µas | Mili giây cung / micro giây cung (1 giây cung = 1/3600 độ) |
| Parsec (pc) | Khoảng cách mà thị sai = 1 giây cung; 1 pc ≈ 3.26 năm ánh sáng ≈ 206.265 AU |
| Năm ánh sáng | Quãng đường ánh sáng đi trong 1 năm ≈ 9.46 nghìn tỷ km |
| Gaia | Vệ tinh của ESA đo vị trí và thị sai của gần 2 tỷ sao; DR3 là bản dữ liệu thứ 3 |
| RUWE | Chỉ số chất lượng phép đo Gaia; < 1.4 là đáng tin, lớn hơn có thể là sao đôi |
| Cấp sao biểu kiến (m) | Độ sáng sao *nhìn thấy* từ Trái Đất |
| Cấp sao tuyệt đối (M) | Độ sáng sao nếu đặt ở cách xa 10 pc; cho biết độ sáng thật |
| Distance modulus | m − M = 5·log₁₀(d / 10 pc): từ chênh lệch độ sáng suy ra khoảng cách |
| Extinction | Bụi giữa các vì sao làm sao trông mờ hơn, khiến ước tính khoảng cách bằng độ sáng bị sai |
| Mass–radius relation | Quan hệ thực nghiệm giữa khối lượng và bán kính hành tinh, dùng để ước tính khối lượng khi chưa đo được |
| TTV | Transit Timing Variation: transit đến sớm/muộn do các hành tinh kéo lẫn nhau, dùng để đo khối lượng |
| Mp sin i | Khối lượng tối thiểu: RV chỉ đo được Mp nhân sin i; transit cho biết i nên ra được Mp thật |
| SDE | Signal Detection Efficiency: đỉnh periodogram nổi bật hơn phần còn lại bao nhiêu lần độ lệch chuẩn |
| Masking | Che bỏ các điểm trong transit của hành tinh đã tìm thấy để tìm hành tinh tiếp theo |
| Non-transiting planet | Hành tinh không có transit vì quỹ đạo nghiêng; chỉ tìm được bằng RV |
| CMF | Core Mass Fraction: tỉ lệ khối lượng lõi sắt của hành tinh đá (Trái Đất 32.5%) |
| Envelope (lớp khí) | Lớp vỏ khí H/He bọc quanh lõi hành tinh |
| Water world | Thế giới nước: hành tinh có nước/băng chiếm phần lớn khối lượng |
| Heavy elements | Nguyên tố nặng: mọi nguyên tố nặng hơn heli (đá, băng, kim loại) |
| Inflated planet | Hành tinh bị phồng: bán kính lớn bất thường so với khối lượng, hay gặp ở hot Jupiter |
| Degeneracy | Thoái hóa: nhiều cấu trúc khác nhau cho cùng một khối lượng + bán kính |
| Habitable zone | Vùng có thể sống: khoảng cách tới sao mà nước có thể ở dạng lỏng trên bề mặt |
| Thang logarit | Trục mà mỗi bậc là gấp 10 lần; dùng khi các giá trị chênh nhau rất lớn |
| Lava world | Hành tinh đá quá nóng, bề mặt có thể nóng chảy thành biển dung nham |
| BJD / BKJD | Hệ thời gian thiên văn (ngày); BKJD = BJD − 2454833 |
| RA / Dec | Tọa độ trên bầu trời (xích kinh / xích vĩ) |
| Magnitude | Cấp sao; số nhỏ = sáng hơn |
| ppm | Phần triệu (parts per million) |
| R☉ / R⊕ | Bán kính Mặt Trời / bán kính Trái Đất |
| BLS | Box Least Squares: thuật toán tìm tín hiệu transit có chu kỳ |
| Phase fold | Gấp dữ liệu theo chu kỳ để chồng các transit lên nhau |
| False positive | Tín hiệu giả, không phải hành tinh |
| Eclipsing binary | Hệ sao đôi che khuất nhau, dễ bị nhầm là hành tinh |
| Periodogram | Đồ thị độ mạnh tín hiệu theo chu kỳ thử |
| Spectroscopy | Quang phổ học: cho Teff, logg, [Fe/H] chính xác hơn trắc quang (KIC) |
| TAP / ADQL | Giao thức truy vấn bảng thiên văn qua URL / ngôn ngữ truy vấn giống SQL |
| pscomppars / ps | Bảng NASA Exoplanet Archive: composite (1 dòng/hành tinh, ghép nhiều nguồn) / từng bộ thông số đã công bố |
| TOPCAT | Phần mềm miễn phí mở file FITS và lưu ra CSV, không cần code |
| MES | Multiple Event Statistic: SNR của pipeline Kepler khi cộng mọi transit; ngưỡng phát hiện 7.1 |
| Robovetter / koi_score | Bộ lọc tự động phân loại KOI / độ tin của nó (0–1) |
| Ephemeris | Bộ (P, T0) để dự đoán thời điểm transit |
| Kiểm chứng (verification) | Đo tín hiệu tại P, T0 đã biết từ nguồn khác, khác với tìm mù |
| Phép thử báo động giả | Đo lại ở nhiều (P, T0) ngẫu nhiên để xem nhiễu tạo ra tín hiệu mạnh như vậy thường tới mức nào |
| Look-elsewhere effect | Thử càng nhiều chỗ càng dễ gặp tín hiệu giả do may rủi |
| White noise / Red noise | Nhiễu độc lập từng điểm / nhiễu tương quan kéo dài vài giờ, giả dạng được transit |
| Whitening | Làm trắng nhiễu đỏ trước khi tìm transit (pipeline Kepler làm bước này) |
| Validation (thống kê) | "Xác nhận" hành tinh bằng xác suất loại trừ sao đôi/sao nền, không đo khối lượng |
| Controversial flag | Cột `pl_controv_flag` của NASA: sự tồn tại của hành tinh đang bị nghi ngờ |
| Runaway greenhouse | Hiệu ứng nhà kính mất kiểm soát; mép trong của vùng có thể sống bảo thủ |
| PLATO | Kính không gian ESA săn hành tinh giống Trái Đất quanh sao giống Mặt Trời |
| Exomoon | Vệ tinh quay quanh hành tinh ngoài Hệ Mặt Trời; chưa có cái nào được xác nhận |
| Hill sphere (bán kính Hill) | Vùng quanh hành tinh mà lực hút của nó thắng lực hút sao; vệ tinh bền tới ~0.49 R_H |
| Roche limit | Khoảng cách tối thiểu; gần hơn thì vệ tinh bị thủy triều xé vụn |
| O − C | Observed − Calculated: thời điểm transit đo được trừ thời điểm dự đoán theo chu kỳ đều |
| TDV | Transit Duration Variation: thời lượng transit thay đổi do vệ tinh kéo, lệch pha 90° so với TTV |
| OSE | Orbital Sampling Effect: cộng nhiều transit thì bóng vệ tinh thành "vai" trũng nông hai bên transit hành tinh |
| Lomb–Scargle | Periodogram cho dữ liệu lấy mẫu không đều, dùng tìm chu kỳ trong O − C |
| FAP | False Alarm Probability: xác suất một đỉnh periodogram mạnh như vậy chỉ do nhiễu |
| Cadence alias | Dao động giả trong O − C do tâm transit rơi vào vị trí khác nhau trong lưới đo 29.4 phút |
| Aliasing | Tín hiệu nhanh bị lấy mẫu thưa hiện ra như tín hiệu chậm hơn |
| Starspot / rotation | Vết đen trên sao quay theo sao, làm độ sáng dao động theo chu kỳ tự quay (vd. Kepler-186 ~35 ngày) |

## 7. Từ transit tính ra được gì?

⚠️ **Điểm quan trọng nhất:** chỉ riêng light curve thì **không** tính ra được *mọi* thông số. Mỗi thông số cần một nguồn khác nhau:

| Thông số | Nguồn | Ghi chú |
|---|---|---|
| Chu kỳ P, thời điểm T0 | ✅ Light curve | Rất chính xác |
| Độ sâu, thời lượng T14 | ✅ Light curve | |
| Rp/Rs, b, a/Rs, độ nghiêng i | ✅ Hình dạng transit | Cần mô hình có tối rìa + nhòe phơi sáng |
| Mật độ sao ρ* | ✅ Từ a/Rs và P | Không cần biết gì khác về sao! |
| Bán kính sao Rs, Teff, logg | 📚 Danh mục sao (KIC, Gaia) hoặc phổ | Header FITS có sẵn giá trị KIC (khá thô) |
| Khối lượng sao Ms | 🔀 Kết hợp: ρ* × thể tích, hoặc g·R²/G | |
| Bán kính hành tinh Rp | 🔀 (Rp/Rs) × Rs | **Sai số của Rs truyền thẳng vào Rp** |
| Bán trục lớn a | 🔀 Định luật Kepler 3 (cần Ms) | |
| Teq, bức xạ nhận được | 🔀 Teff, Rs, a | Phải giả định albedo |
| **Khoảng cách tới sao** | 🛰️ Thị sai **Gaia** | Hoặc ước tính thô bằng độ sáng |
| **Khối lượng hành tinh Mp** | ❌ Light curve không đo được | Cần **vận tốc xuyên tâm (RV)** hoặc TTV; có thể *ước tính* từ bán kính |
| Mật độ hành tinh | ❌ Cần Mp | Có Mp + Rp thì đoán được thành phần |
| **Số hành tinh trong hệ** | ✅ Light curve (chỉ hành tinh có transit) | Hành tinh không có transit phải tìm bằng RV (mục 7.6) |
| **Độ lệch tâm quỹ đạo e** | ❌ Gần như không đo được | Thường giả định quỹ đạo tròn (e = 0) |
| **Thành phần sao mẹ** | 📚 Phân tích **quang phổ** | Thường chỉ có [Fe/H] (độ kim loại) |
| **Thành phần / khí quyển hành tinh** | 🔭 Phổ truyền qua (JWST, HST) | Ngoài khả năng của Kepler |

### 7.1. Các công thức

**Hình học transit** (quỹ đạo tròn):

- $k = R_p / R_s \approx \sqrt{\text{độ sâu}}$ (tối rìa làm transit sâu hơn $k^2$ một chút)
- $\cos i = b / (a/R_s)$
- $T_{14} = \dfrac{P}{\pi} \arcsin\left(\dfrac{\sqrt{(1+k)^2 - b^2}}{(a/R_s)\sin i}\right)$

**Mật độ sao từ transit:**

$$\rho_* = \frac{3\pi}{G P^2}\left(\frac{a}{R_s}\right)^3$$

**Khối lượng sao:**

- Từ logg: $M_s = g R_s^2 / G$, với $g = 10^{\log g}$ (cgs, chia 100 để ra m/s²)
- Từ mật độ: $M_s = \rho_* \cdot \tfrac{4}{3}\pi R_s^3$

**Định luật Kepler 3** (khoảng cách hành tinh):

$$a = \left(\frac{G M_s P^2}{4\pi^2}\right)^{1/3}$$

**Nhiệt độ cân bằng và bức xạ:**

- $T_{eq} = T_{eff}\sqrt{\dfrac{R_s}{2a}}\,(1-A)^{1/4}$, với A là albedo
- $L/L_☉ = (R_s/R_☉)^2 (T_{eff}/5772)^4$
- $S/S_⊕ = (L/L_☉) / (a/\text{AU})^2$

**Xác suất một hành tinh có transit nhìn thấy được:** $\approx R_s / a$. Hành tinh càng xa sao thì càng hiếm khi thấy transit.

**Vận tốc xuyên tâm** (khi đã biết Mp):

$$K = \left(\frac{2\pi G}{P}\right)^{1/3} \frac{M_p \sin i}{M_s^{2/3}}$$

### 7.2. Hai cái bẫy khi khớp hình dạng transit

Khi chạy thử với Kepler-6b, mô hình hình thang đơn giản cho **b = 0.77, a/Rs = 5.2** (đúng ra là b ≈ 0.14, a/Rs ≈ 7.5). Có 2 nguyên nhân:

1. **Nhòe phơi sáng:** mỗi điểm long cadence cộng dồn ánh sáng trong 29.4 phút, nên sườn transit bị kéo dài, trông như hành tinh đi sượt mép (b lớn). Cách sửa: tính trung bình mô hình trong khoảng phơi sáng (*supersampling*).
2. **Tối rìa:** đáy transit cong chứ không phẳng, mà hình thang không mô tả được. Cách sửa: dùng mô hình vật lý (thư viện `batman`) với hệ số tối rìa bậc hai.

Sau khi sửa cả hai: a/Rs = 7.59, ρ* = 0.79 g/cm³, Ms = 1.21 M☉, rất khớp với giá trị NASA công bố.

Thêm: **b gần 0 rất khó đo chính xác**, vì transit qua tâm và transit hơi lệch tâm cho hình dạng gần như nhau.

### 7.3. Khoảng cách Trái Đất – sao mẹ – hành tinh

**Cách chính xác: thị sai (parallax) từ Gaia.** Khi Trái Đất đi từ bên này sang bên kia quỹ đạo, sao gần dịch chuyển rất nhẹ trên nền các sao xa. Góc dịch (thị sai, ký hiệu ϖ) càng nhỏ thì sao càng xa:

$$d\,[\text{pc}] = \frac{1000}{\varpi\,[\text{mas}]}$$

- Dữ liệu: Gaia DR3, tìm theo tọa độ RA/Dec trong header FITS (bán kính ~5 giây cung, chọn sao có độ sáng khớp để tránh nhầm sao bên cạnh).
- Kiểm tra **RUWE < 1.4** và sai số thị sai nhỏ (< 10–20% thị sai) thì phép tính 1/ϖ mới đáng tin.
- Thị sai Gaia có sai lệch hệ thống nhỏ (*zero-point*, cỡ −0.02 mas). Với sao ở xa thì nên hiệu chỉnh, còn ở mức học tập thì có thể bỏ qua.

**Cách thô: so độ sáng thật với độ sáng nhìn thấy** (*distance modulus*):

- Cấp sao tuyệt đối: $M = 4.74 - 2.5\log_{10}(L/L_☉)$
- $m - M = 5\log_{10}(d / 10\,\text{pc})$, suy ra $d = 10^{(m - M + 5)/5}$ pc
- Sai vì bỏ qua bụi (extinction) và coi cấp sao Kepler gần bằng cấp sao toàn phần, nên thường lệch ±10–20%.

**Khoảng cách tới hành tinh:** bằng khoảng cách tới sao ± a. Vì a (vài phần trăm AU) nhỏ hơn hàng tỷ lần so với khoảng cách hàng trăm parsec, coi như **bằng nhau**.

**Góc tách hành tinh – sao nhìn từ Trái Đất:** θ [giây cung] = a [AU] / d [pc]. Với Kepler-6b, θ ≈ 74 micro giây cung, nhỏ hơn hàng nghìn lần khả năng phân giải của mọi kính thiên văn, nên không thể chụp ảnh tách riêng hành tinh.

### 7.4. Khối lượng hành tinh

Light curve **không** đo được khối lượng: một hành tinh nặng và một hành tinh nhẹ cùng kích thước che sao y như nhau. Có 3 cách:

**1. Vận tốc xuyên tâm (RV), cách chuẩn.** Hành tinh kéo sao mẹ chuyển động tròn nhỏ quanh tâm khối chung. Kính quang phổ đo dịch chuyển Doppler của vạch phổ, ra biên độ K (m/s). Từ đó:

$$M_p \sin i = K \left(\frac{P}{2\pi G}\right)^{1/3} M_s^{2/3} \qquad (M_p \ll M_s)$$

- Chỉ RV thì chỉ có **khối lượng tối thiểu Mp sin i**. Kết hợp với transit (cho biết i ≈ 90°) thì ra **khối lượng thật**.
- Cần kính mặt đất lớn (Keck/HIRES, HARPS-N...). Dữ liệu RV đã công bố thì tra trên NASA Exoplanet Archive (cột `pl_rvamp` = K).
- Độ lớn: Sao Mộc làm Mặt Trời dao động ~12.5 m/s, Trái Đất chỉ ~0.09 m/s. Vì thế hành tinh nhỏ rất khó đo khối lượng.

**2. TTV (biến thiên thời điểm transit).** Trong hệ nhiều hành tinh, chúng kéo nhau làm transit đến sớm/muộn vài phút. Đo được bằng chính dữ liệu Kepler, nhưng chỉ áp dụng cho hệ nhiều hành tinh có quỹ đạo gần cộng hưởng.

**3. Ước tính từ bán kính** (quan hệ khối lượng – bán kính, Chen & Kipping 2017), dạng $R = C \cdot M^S$:

| Loại | Khoảng khối lượng | Công thức (R⊕, M⊕) |
|---|---|---|
| Đá | < 2 M⊕ | $R = 1.008\,M^{0.279}$ |
| Kiểu Neptune | 2 – 130 M⊕ | $R = 0.808\,M^{0.589}$ |
| Khí khổng lồ | > 130 M⊕ | Bán kính gần như **không đổi** theo khối lượng |

Đây chỉ là con số thống kê: cùng bán kính có thể lệch khối lượng gấp đôi. Với khí khổng lồ thì gần như vô dụng. Ví dụ Kepler-6b: ước tính ~114 M⊕, thực tế đo bằng RV là 212 M⊕.

**Có khối lượng thì tính thêm được:** mật độ $\rho_p = M_p / (\tfrac{4}{3}\pi R_p^3)$, trọng lực bề mặt $g = G M_p / R_p^2$, và đoán thành phần (mục 7.5).

### 7.5. Đoán thành phần hành tinh

**Theo bán kính** (thô):

| Bán kính | Loại thường gặp |
|---|---|
| < 1.6 R⊕ | Hành tinh đá |
| 1.6 – 4 R⊕ | Sub-Neptune: lõi đá + lớp khí H/He hoặc nhiều nước |
| 4 – 10 R⊕ | Giống Sao Hải Vương |
| > 10 R⊕ | Khí khổng lồ (H/He) |

**Theo mật độ** (cần khối lượng): Trái Đất 5.51 g/cm³, Sao Hải Vương 1.64, Sao Mộc 1.33, Sao Thổ 0.69. Ví dụ Kepler-6b có mật độ ~0.4–0.5 g/cm³, xốp hơn cả Sao Thổ. Đây là hiện tượng **"phồng"** thường gặp ở hot Jupiter, do bị sao mẹ sưởi rất nóng.

**Theo khối lượng + bán kính, so với mô hình lý thuyết** (cách script dùng):

**a) Hành tinh nhỏ (< ~50 M⊕): so với đường cong "đá – sắt"** (Zeng et al. 2016):

$$R = (1.07 - 0.21\cdot\text{CMF})\cdot M^{0.27} \quad (R_⊕, M_⊕)$$

CMF (*core mass fraction*) là tỉ lệ khối lượng lõi sắt: 1 = sắt nguyên chất, 0 = đá silicat nguyên chất, Trái Đất là 0.325. Với cùng khối lượng:

| Bán kính đo được so với các đường | Kết luận |
|---|---|
| Nhỏ hơn đường sắt nguyên chất (0.86·M^0.27) | Đặc bất thường, nhiều khả năng do sai số |
| Giữa đường sắt và đường đá (1.07·M^0.27) | **Hành tinh đá**; giải ngược ra CMF = (1.07 − R/M^0.27) / 0.21 |
| Giữa đường đá và đường 50% nước (~1.24·M^0.27) | **Không phân biệt được**: nhiều nước/băng HOẶC lõi đá + khí H/He mỏng |
| Lớn hơn đường 50% nước | **Phải có lớp khí H/He** |

**b) Ước lượng lượng khí H/He** (Lopez & Fortney 2014), coi lõi giống Trái Đất có bán kính $R_{lõi} \approx M^{0.25}$:

$$R_{khí} = R - R_{lõi} = 2.06\,R_⊕ \left(\frac{M}{M_⊕}\right)^{-0.21} \left(\frac{f_{khí}}{5\%}\right)^{0.59} \left(\frac{S}{S_⊕}\right)^{0.044} \left(\frac{\text{tuổi}}{5\,\text{tỷ năm}}\right)^{-0.11}$$

Giải ngược ra $f_{khí}$, tức phần trăm khối lượng là khí. Điều thú vị: chỉ **vài % khối lượng khí** đã đủ làm bán kính phồng thêm gấp rưỡi, gấp đôi.

**c) Khí khổng lồ: lượng nguyên tố nặng** (Thorngren et al. 2016): $M_{nặng} \approx 57.9\,M_⊕ \cdot (M/M_♃)^{0.61}$. Phần còn lại là H/He. Công thức này rút ra từ các khí khổng lồ "lạnh", nên với hot Jupiter bị phồng chỉ là ước lượng.

**Giới hạn:** đây đều là **suy đoán từ mật độ**. Cùng một mật độ có thể ứng với nhiều cấu trúc khác nhau (*thoái hóa*). Muốn biết khí quyển thật sự có gì (H₂O, CO₂, CH₄...) thì phải chụp **phổ truyền qua** bằng JWST/HST.

**Độ kim loại sao mẹ:** [Fe/H] = +0.34 nghĩa là kim loại gấp $10^{0.34}$ ≈ 2.2 lần Mặt Trời. Sao giàu kim loại thường có nhiều khí khổng lồ hơn. Đây là thông tin duy nhất về thành phần sao mẹ có sẵn trong header FITS; muốn chi tiết hơn (C, O, Mg, Si...) phải phân tích quang phổ phân giải cao.

### 7.6. Hệ có mấy hành tinh? Tìm nhiều hành tinh bằng BLS lặp

**Thuật toán:**

1. Chạy BLS trên toàn bộ light curve, lấy đỉnh mạnh nhất.
2. Kiểm tra đỉnh có phải transit thật không (bảng ngưỡng bên dưới).
3. Nếu đạt: **tinh chỉnh chu kỳ** bằng lưới thật mịn quanh đỉnh, ghi nhận hành tinh, rồi **che (mask) các điểm trong transit** của nó.
4. Quay lại bước 1 với dữ liệu đã che, tới khi đỉnh mạnh nhất chỉ còn là nhiễu.

| Ngưỡng | Ý nghĩa | Giá trị dùng |
|---|---|---|
| **SDE** (Signal Detection Efficiency) | Đỉnh cao hơn mức trung bình của periodogram bao nhiêu lần độ lệch chuẩn | ≥ 9 |
| **SNR** | Độ sâu transit / sai số độ sâu | ≥ 10 (Kepler dùng 7.1) |
| Số transit | Phải lặp lại để chắc là có chu kỳ | ≥ 3 |

Với Kepler-10: vòng 1 tìm ra b (SDE 19), vòng 2 ra c (SDE 13), vòng 3 chỉ còn nhiễu (SDE 5.3) thì dừng.

**Hai bài học khi làm:**

- **Lưới chu kỳ phải đủ mịn.** Chu kỳ sai chỉ 0.00004 ngày, sau ~450 vòng đã lệch ~26 phút, làm transit gấp pha bị nhòe và a/Rs sai (Kepler-6: 6.40 thay vì 7.59). Bước nhảy hợp lý của lưới là khoảng (thời lượng transit / độ dài dữ liệu) × chu kỳ.
- **Hành tinh nhỏ không đo được a/Rs.** Kepler-10b có ingress chỉ ~1 phút, nhỏ hơn rất nhiều so với 29.4 phút phơi sáng, nên b và a/Rs gần như không xác định (sai số a/Rs ±2.3). Script tính khối lượng sao bằng **trung bình có trọng số theo sai số** từ mọi hành tinh. Nếu không hành tinh nào đủ chính xác thì dùng logg từ KIC.

**Hành tinh không có transit:** quỹ đạo nghiêng một chút là hành tinh không đi qua trước mặt sao, nên light curve "mù" hoàn toàn với nó. Xác suất có transit chỉ khoảng Rs/a (Kepler-10 d: 0.9%). Những hành tinh này chỉ tìm được bằng RV, và chỉ biết **khối lượng tối thiểu**, không biết bán kính hay thành phần. Script lấy chúng từ NASA Exoplanet Archive (cột `discoverymethod`, `tran_flag = 0`).

**Đối chiếu KOI:** script so danh sách tự tìm với bảng KOI DR25, để thấy các ứng viên (`CANDIDATE`), tín hiệu giả (`FALSE POSITIVE`) và những gì bị bỏ sót.

### 7.7. Vẽ sơ đồ hệ bằng thang logarit

Trong hệ Kepler-10, sao mẹ to gấp ~80 lần hành tinh b, còn quỹ đạo d xa gấp ~30 lần quỹ đạo b. Vẽ đúng tỉ lệ thường thì hành tinh nhỏ hơn 1 pixel. **Thang log** biến "gấp 10 lần" thành "thêm 1 bậc", nên mọi thứ cùng hiện lên được.

| Phần sơ đồ | Cách quy đổi |
|---|---|
| Quỹ đạo nhìn từ trên xuống | Bán kính trên hình ρ = 1 + log₁₀(a / Rs): bề mặt sao ở ρ = 1, mỗi vòng chấm = xa gấp 10 lần |
| Kích thước | Đường kính = 1 + log₁₀(R / R⊕): 1 R⊕ → 1, 10 R⊕ → 2, 100 R⊕ → 3 |
| Khoảng cách | Trục log tính bằng AU, đặt cạnh Hệ Mặt Trời để so sánh |
| Vị trí hành tinh | Tính từ T0 và P cho ngày bất kỳ: góc = 360° × ((ngày − T0) / P mod 1). Lúc transit hành tinh nằm giữa sao và Trái Đất |
| Vùng có thể sống | Mép = $\sqrt{L/S_{eff}}$ AU, ngưỡng bức xạ $S_{eff}$ **phụ thuộc nhiệt độ sao** (Kopparapu et al. 2013): sao giống Mặt Trời ~1.04 (trong) và ~0.35 (ngoài); sao lùn M 3.750 K chỉ 0.88 và 0.25. Hệ số chi tiết xem [`kepler-186.md`](kepler-186.md) mục 3.2 |

⚠️ Trên thang log, khoảng cách trên hình **không còn tỉ lệ thuận** với thực tế, chỉ giữ đúng **thứ tự và tỉ số**.

### 7.8. Tín hiệu sát ngưỡng: khi BLS không tự tìm ra

Với hành tinh nhỏ, chu kỳ dài (ít transit), **nhiễu đỏ** của thiết bị tạo ra những chỗ trũng giả dài vài giờ, có khi sâu hơn transit thật. BLS chuẩn giả định nhiễu trắng nên bị đánh lừa: đỉnh mạnh nhất chỉ là một chỗ trũng đơn lẻ.

Khi đó chuyển sang **kiểm chứng**: lấy P, T0 đã công bố, gấp pha đúng chỗ đó và đo SNR. Kèm **phép thử báo động giả**: đo lại ở hàng nghìn cặp (P, T0) ngẫu nhiên, đếm bao nhiêu % cho SNR cao bằng. Tỉ lệ nhỏ cho một lần thử chưa chắc đã nhỏ khi đã thử hàng nghìn chu kỳ (*look-elsewhere effect*). Script: cờ `--verify-archive` của `02_analyze.py`.

Thêm 2 lưu ý về dữ liệu NASA:
- Bảng **composite** (`pscomppars`) ghép mỗi cột từ một nguồn, có thể mâu thuẫn nhau. Cần bộ số nhất quán thì dùng bảng `ps`, lọc theo một `pl_refname`.
- Cột khối lượng có `pl_bmassprov = M-R relationship` nghĩa là **ước tính từ bán kính**, không phải đo.

Ví dụ đầy đủ: Kepler-452b, xem [`kepler-452.md`](kepler-452.md).

**Sao có vết đen quay nhanh** (ví dụ sao lùn M Kepler-186, chu kỳ tự quay ~35 ngày): cửa sổ làm phẳng mặc định 18 ngày không khử được dao động, BLS bắt nhầm chu kỳ tự quay. Phải dùng cửa sổ ngắn (~2 ngày, vẫn ≥ 3 lần transit dài nhất) và **che transit đã biết** khi làm phẳng, nếu không transit bị nông đi (Kepler-186 f: 300 → 433 ppm). Xem [`kepler-186.md`](kepler-186.md) mục 8.

### 7.9. Tìm vệ tinh (exomoon) quanh hành tinh

**Tình hình thực tế:** tới nay **chưa có vệ tinh ngoài Hệ Mặt Trời nào được xác nhận**. Hai ứng viên nổi tiếng đều tìm trong dữ liệu Kepler và đều đang bị tranh cãi: Kepler-1625b-i (Teachey & Kipping 2018, cỡ Sao Hải Vương) và Kepler-1708b-i (Kipping et al. 2022). Vì vậy với dữ liệu Kepler, mục tiêu thực tế là **đặt giới hạn trên**: "nếu có vệ tinh thì nó không thể to/nặng hơn mức X".

**Bước 1. Vệ tinh có thể tồn tại ở đâu?**

| Đại lượng | Công thức | Ý nghĩa |
|---|---|---|
| Bán kính Hill | $R_H = a\left(\dfrac{M_p}{3M_s}\right)^{1/3}$ | Vùng mà lực hút hành tinh thắng lực hút sao |
| Quỹ đạo bền xa nhất | $a_{max} \approx 0.49\,R_H$ (cùng chiều quay; ngược chiều tới ~0.93 R_H) (Domingos et al. 2006) | Xa hơn thì vệ tinh bị sao mẹ giật mất |
| Giới hạn Roche | $a_R \approx 2.44\,R_p\left(\rho_p/\rho_v\right)^{1/3}$ | Gần hơn thì vệ tinh bị thủy triều xé vụn (thành vành đai) |
| Chu kỳ vệ tinh dài nhất | $P_{v,max} = 2\pi\sqrt{a_{max}^3/(GM_p)}$ | Luôn ngắn hơn ~1/5 chu kỳ hành tinh |
| Vệ tinh lệch trước/sau hành tinh tối đa | $\Delta t_{max} = a_{max}/v_p$, với $v_p = 2\pi a/P$ | Bề rộng "vùng vai" quanh transit hành tinh |

Nếu $a_{max} < a_R$ thì **không có quỹ đạo vệ tinh bền nào**. Ngoài ra hành tinh càng gần sao, thủy triều càng làm vệ tinh xoắn ốc rơi vào hành tinh hoặc văng ra trong thời gian ngắn hơn tuổi hệ (Barnes & O'Brien 2002). Hành tinh xa sao, nặng, như Sao Mộc là "nhà" tốt nhất cho vệ tinh.

**Bước 2. TTV: hành tinh bị vệ tinh kéo lắc** (Sartoretti & Schneider 1999; Kipping 2009)

Hành tinh và vệ tinh cùng quay quanh tâm khối chung. Hành tinh lệch khỏi tâm khối một đoạn $a_v M_v/M_p$, nên lúc đến sớm, lúc đến muộn tối đa $a_v M_v/(M_p v_p)$. Quy trình:

1. Đo thời điểm từng transit $t_c$ (dịch mô hình transit cố định hình dạng, chọn độ dịch khớp nhất).
2. Khớp đường thẳng $t_c = T_0 + n\cdot P$ (loại transit ngoại lai), tính **O − C** (Observed − Calculated) cho từng vòng n.
3. Kiểm tra O − C có dao động **có chu kỳ** không bằng periodogram **Lomb–Scargle**, đọc **FAP** (xác suất báo động giả; FAP < 0.001 mới đáng chú ý). Vệ tinh quay nhanh hơn hành tinh rất nhiều, nhưng mỗi vòng chỉ "chụp" được 1 lần, nên dao động hiện ra như một chu kỳ "ảo" dài hơn (*aliasing*).
4. Giới hạn khối lượng (TTV dạng sin có trung bình bình phương = biên độ/√2):
$$M_{v,max} = \sqrt{2}\,\sigma_{TTV}\,\frac{v_p\,M_p}{a_v}$$
với $\sigma_{TTV}$ = O − C rms, $a_v = a_{max}$ (giới hạn chặt nhất; vệ tinh gần hơn thì giới hạn lỏng hơn theo tỉ lệ $a_{max}/a_v$).

**Ba cái bẫy khi đọc TTV:**
- **Sai số bị đánh giá thấp**: sai số danh nghĩa của pipeline nhỏ hơn độ tán xạ thật, nhiễu đỏ làm tệ thêm. χ²_red > 1 chưa chắc là có tín hiệu. Lomb–Scargle không bị ảnh hưởng khi mọi sai số cùng bị nhân một hệ số.
- **Lỗi lấy mẫu (cadence alias)**: tâm transit mỗi vòng rơi vào một vị trí khác trong khoảng 29.4 phút giữa 2 lần đo, lệch đi $\text{frac}(P/\text{cadence})$. Phép định thời hơi thiên lệch theo vị trí đó, nên O − C dao động theo **chu kỳ phách** $1/\text{frac}$ và các họa âm. Kepler-10b: P/cadence = 40.985 → phách ~67 vòng, O − C có đỉnh ở 8.4 vòng = họa âm bậc 8, FAP 3·10⁻⁴¹ mà hoàn toàn là lỗi đo.
- **Nguồn TTV khác**: hành tinh khác trong hệ kéo (nguồn phổ biến nhất), vết đen sao, sao đồng hành.

Thêm: **TDV** (Transit Duration Variation, Kipping 2009) là biến thiên thời lượng transit do vận tốc hành tinh thay đổi khi bị vệ tinh kéo; lệch pha 90° so với TTV. Có cả TTV lẫn TDV thì tách được khối lượng và khoảng cách vệ tinh, và loại được nguyên nhân "hành tinh khác". Script chưa đo TDV.

**Bước 3. OSE: tìm bóng của chính vệ tinh** (Orbital Sampling Effect, Heller 2014)

Mỗi transit, vệ tinh nằm ở một chỗ khác nhau quanh hành tinh (trong khoảng ±Δt_max) và tự tạo một chỗ trũng nhỏ $\delta_v = (R_v/R_s)^2$. Cộng hàng trăm transit lại thì các chỗ trũng đó "nhòe" thành một **vai trũng nông** ở hai bên transit hành tinh.

- Đo độ trũng trung bình D ở vùng vai ($0.6\,T_{14} < |\Delta t| < \Delta t_{max} + T_{14}/2$) so với vùng nền xa hơn, kèm sai số $\sigma_D$.
- Diện tích trũng mỗi transit ≈ $\delta_v T_{14}$, trải trên bề rộng ~$2\Delta t_{max} + T_{14}$, nên
$$\delta_{v,max} = (\max(D, 0) + 2\sigma_D)\cdot\frac{2\Delta t_{max} + T_{14}}{T_{14}}, \qquad R_{v,max} = R_s\sqrt{\delta_{v,max}}$$
- Nếu $\Delta t_{max}$ nhỏ hơn nửa thời lượng transit (hot Jupiter, hành tinh rất gần sao) thì vệ tinh luôn "núp" trong transit hành tinh, OSE không tách ra được.

Để so sánh: Mặt Trăng 0.273 R⊕, Titan 0.404, Ganymede 0.413, Sao Hỏa 0.532. Kepler chỉ đủ nhạy với vệ tinh **cỡ Sao Hỏa trở lên**, lớn hơn mọi vệ tinh trong Hệ Mặt Trời. Muốn thấy vệ tinh cỡ Ganymede cần kính lớn hơn (PLATO, hoặc theo dõi transit bằng JWST/HST như với Kepler-1625b).

**Kết quả trên các hệ đã làm** (script `04_moons.py`):

| Hành tinh | Vệ tinh có thể tồn tại? | TTV | Khối lượng vệ tinh tối đa | Bán kính vệ tinh tối đa (OSE) |
|---|---|---|---|---|
| Kepler-6 b | Có, nhưng vùng rất hẹp (114.000–187.000 km) | Không (FAP 0.06), O − C rms 0.5 phút | 7.2 M⊕ | — (vệ tinh luôn núp trong transit) |
| Kepler-10 b | **Không**: vùng bền (18.700 km) nằm trong giới hạn Roche (28.000 km) | Chỉ có lỗi lấy mẫu | — | — |
| Kepler-10 c | Có (43.000–409.000 km) | Không (FAP 0.56), rms 5.8 phút | 0.79 M⊕ (64 Mặt Trăng) | 0.74 R⊕ |
| Kepler-452 b | Có (19.000–774.000 km) | Chỉ 4 transit, không kiểm định được | ~0.07 M⊕ (~6 Mặt Trăng)* | 0.75 R⊕ |

\* Dùng khối lượng ước tính từ bán kính KIC (1.1 M⊕). Với bán kính phổ học 1.6 R⊕ (~3 M⊕), giới hạn lỏng ra khoảng gấp đôi. Chỉ 4 điểm nên giới hạn này rất thô.

Kepler-186 (mục 9 của [`kepler-186.md`](kepler-186.md)): không thấy vệ tinh; f giới hạn ~0.56 M⊕ và 0.84 R⊕. Kepler-186b có đỉnh O − C với FAP 3·10⁻⁴ nhưng chỉ xuất hiện ở nửa sau dữ liệu, nên là nhiễu: luôn **chia đôi dữ liệu** để kiểm tra. Kepler-10c có TTV đã công bố (`ttv_flag = 1` trên NASA) nhưng biên độ chỉ vài phút, dưới độ nhạy của phép đo ở đây (sai số 4.6 phút mỗi transit).

## 8. Thực hành: tải dữ liệu, vẽ và tính thông số

Hai ví dụ (hai hệ nữa có file riêng, tự đủ từ đầu tới cuối: Kepler-452 trong [`kepler-452.md`](kepler-452.md), Kepler-186 trong [`kepler-186.md`](kepler-186.md)):
- **Kepler-6** (KIC 10874614): 1 hot Jupiter, transit sâu ~1%, chu kỳ 3.23 ngày. Nhìn rõ bằng mắt thường, kể cả trên Google Sheets.
- **Kepler-10** (KIC 11904151): 3 hành tinh. b là hành tinh đá, c là sub-Neptune, cả hai có transit; d chỉ tìm được bằng RV.

### 8.1. Bằng Python

```bash
# Cài đặt (1 lần)
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt

# Bước 1: tải 15 file FITS (Q0–Q17) từ MAST + xuất CSV
.venv/Scripts/python scripts/01_download.py "Kepler-6"

# Bước 2: tìm TẤT CẢ hành tinh, khớp mô hình, tính thông số + thành phần, so với NASA (~3–5 phút)
.venv/Scripts/python scripts/02_analyze.py "Kepler-6"

# Bước 3: vẽ sơ đồ hệ theo thang log (thêm --date YYYY-MM-DD để xem vị trí hành tinh vào ngày khác)
.venv/Scripts/python scripts/03_diagram.py "Kepler-6"

# Bước 4: tìm vệ tinh (vùng Hill/Roche, TTV, OSE) → giới hạn khối lượng và bán kính vệ tinh (mục 7.9)
.venv/Scripts/python scripts/04_moons.py "Kepler-6"
```

Tùy chọn thêm cho bước 1: `--flatten-window N` (cửa sổ làm phẳng, số điểm; sao có vết đen quay nhanh cần ngắn hơn) và `--mask-known` (che transit đã biết khi làm phẳng để không làm nông transit). Bước 2: `--verify-archive` (hành tinh BLS không tự tìm ra thì kiểm chứng bằng P, T0 của NASA).

| File tạo ra | Nội dung |
|---|---|
| `data/raw/mastDownload/...` | File FITS gốc (không đưa lên git) |
| `data/csv/Kepler6_star_header.csv` | Thông tin sao từ header FITS |
| `data/csv/Kepler6_Q2_raw.csv` | 1 quý dữ liệu thô (~3.400 dòng), cho Google Sheets |
| `data/csv/Kepler6_all_flat.csv` | Tất cả các quý đã ghép + làm phẳng |
| `data/csv/Kepler6_Kepler6b_folded.csv` | Transit đã gấp pha của từng hành tinh, cho Google Sheets |
| `outputs/Kepler6_report.md` | Báo cáo: sao mẹ, khoảng cách, bảng thông số mọi hành tinh, thành phần, đối chiếu KOI |
| `outputs/Kepler6_system.json` | Số liệu cả hệ (đầu vào của bước 3) |
| `outputs/Kepler6_*.png` | Light curve, periodogram từng vòng BLS, transit gấp pha, sơ đồ hệ |
| `outputs/Kepler6_moons.md`, `Kepler6_moons.png` | Bước 4: báo cáo + biểu đồ O − C và vùng vai OSE |
| `data/csv/Kepler6_Kepler6b_transit_times.csv` | Thời điểm từng transit, sai số, O − C (phút), cột `used` (0 = ngoại lai bị loại), cho Google Sheets |
| `data/csv/<sao>_<hành tinh>_ose_profile.csv` | Transit gấp pha gộp bin trong vùng vệ tinh, cho Google Sheets (không có với Kepler-6b vì vệ tinh luôn núp trong transit) |

Đổi sang sao khác chỉ cần thay tên, ví dụ `"Kepler-7"`, `"Kepler-11"`. Với sao có hành tinh chu kỳ dài thì thêm `--max-period 300` ở bước 2 (chạy lâu hơn).

### 8.2. Bằng Google Sheets

**A. Vẽ light curve thô và tìm transit bằng mắt**

1. Google Sheets → **File → Import → Upload** → chọn `Kepler6_Q2_raw.csv`.
2. Chọn cột A (`time_bkjd`) và cột E (`flux_normalized`) → **Insert → Chart** → Chart type: **Scatter chart**.
3. Customize → Vertical axis: đặt min **0.985**, max **1.005** để thấy rõ các chỗ trũng.
4. Đếm khoảng cách giữa 2 chỗ trũng liên tiếp, sẽ ra khoảng 3.23 ngày.

**B. Tự gấp pha ngay trong Sheets**

Đặt P và T0 vào 2 ô, ví dụ `H1 = 3.2347` (chu kỳ), `H2 = 121.4865` (T0, BKJD). Cột F (pha, giờ), ở F2:

```
=(MOD(A2 - $H$2 + $H$1/2, $H$1) - $H$1/2) * 24
```

Kéo xuống hết cột, rồi vẽ Scatter với F là trục X, E là trục Y. Mọi transit sẽ chồng lên nhau tại 0 giờ.

**C. Vẽ transit đã gấp pha sẵn**

Import `Kepler6_Kepler6b_folded.csv` → chọn cả 3 cột → Scatter chart. Cột `model` có thể đổi sang dạng đường (Customize → Series → model → Line).

**D. Tính thông số bằng công thức Sheets**

Giả sử các ô: `B1` = độ sâu (vd `=1-MIN(folded!B:B)`), `B2` = P (ngày), `B3` = Rs (R☉, lấy từ `star_header.csv`), `B4` = Ms (M☉), `B5` = Teff (K).

| Thông số | Công thức |
|---|---|
| Rp/Rs | `=SQRT(B1)` |
| Rp (R⊕) | `=SQRT(B1)*B3*109.1` |
| Rp (R♃) | `=SQRT(B1)*B3*9.73` |
| a (AU) | `=((6.674E-11*B4*1.989E30*(B2*86400)^2)/(4*PI()^2))^(1/3)/1.496E11` |
| Teq (K), albedo 0.3 | `=B5*SQRT(B3*6.957E8/(2*a_ô*1.496E11))*(0.7)^0.25` |
| Bức xạ (× Trái Đất) | `=B3^2*(B5/5772)^4/a_ô^2` |
| Khoảng cách (pc) từ thị sai | `=1000/thị_sai_mas` |
| Khoảng cách (năm ánh sáng) | `=1000/thị_sai_mas*3.2616` |
| Mp (M⊕) từ K (m/s) | `=K*((B2*86400)/(2*PI()*6.674E-11))^(1/3)*(B4*1.989E30)^(2/3)/5.972E24` |
| Mật độ hành tinh (g/cm³) | `=Mp_ô*5.972E24/(4/3*PI()*(Rp_ô*6.371E6)^3)/1000` |

(`a_ô`, `Mp_ô`, `Rp_ô` là các ô chứa kết quả vừa tính. Thị sai lấy từ Gaia, K lấy từ NASA Exoplanet Archive.)

**E. Tìm vệ tinh trong Sheets** (công thức mục 7.9)

Tab `moon`, đầu vào: `B1` = Mp (M⊕), `B2` = Ms (M☉), `B3` = a (AU), `B4` = P (ngày), `B5` = Rp (R⊕), `B6` = Rs (R☉), `B7` = T14 (giờ).

| Ô | Thông số | Công thức |
|---|---|---|
| B9 | Bán kính Hill (km) | `=B3*1.496E8*(B1*5.972E24/(3*B2*1.989E30))^(1/3)` |
| B10 | Quỹ đạo bền xa nhất a_max (km) | `=0.4895*B9` |
| B11 | Mật độ hành tinh (g/cm³) | `=5.51*B1/B5^3` |
| B12 | Giới hạn Roche, vệ tinh đá 3 g/cm³ (km) | `=2.44*B5*6371*(B11/3)^(1/3)` |
| B13 | Vệ tinh có thể tồn tại? | `=IF(B10>B12,"Có","Không")` |
| B14 | Chu kỳ vệ tinh dài nhất (ngày) | `=2*PI()*SQRT((B10*1000)^3/(6.674E-11*B1*5.972E24))/86400` |
| B15 | Vận tốc quỹ đạo hành tinh v_p (km/s) | `=2*PI()*B3*1.496E8/(B4*86400)` |
| B16 | Δt_max (giờ) | `=B10/B15/3600` |

TTV: import `<sao>_<hành tinh>_transit_times.csv` vào tab `tt` (A `epoch`, B `tc_bkjd`, C `sigma_min`, D `oc_min`, E `used`).

| Ô | Thông số | Công thức |
|---|---|---|
| B18 | Số transit dùng | `=COUNTIF(tt!E2:E,1)` |
| B19 | O − C rms (phút) | `=SQRT(SUMPRODUCT(tt!D2:D1500^2*(tt!E2:E1500=1))/B18)` |
| B20 | Sai số trung bình (phút) | `=SQRT(SUMPRODUCT(tt!C2:C1500^2*(tt!E2:E1500=1))/B18)` |
| B21 | **Khối lượng vệ tinh tối đa (M⊕)** | `=SQRT(2)*B19*60*B15*B1/B10` |
| B22 | Theo Mặt Trăng | `=B21*81.3` |

Vẽ O − C: chọn cột A và D của tab `tt` → Scatter (Customize → Series → Error bars → theo cột C, nếu muốn). Sheets không có sẵn Lomb–Scargle nên phần kiểm định chu kỳ chỉ làm được bằng mắt; hoặc dùng **lối tắt kiểm tra lỗi lấy mẫu**: cột F = `=MOD(tt!B2/0.0204340, 1)` (vị trí tâm transit trong lưới đo 29.4244 phút), vẽ D theo F; nếu O − C đổi đều theo F thì đó là lỗi đo.

OSE: import `<sao>_<hành tinh>_ose_profile.csv` vào tab `ose` (A `hours_from_mid_transit`, B `flux_binned`, C `n_points`). Với `B23` = mép trong vùng vai (giờ) `=0.6*B7+0.49`, `B24` = mép ngoài `=B16+B7/2`, `B25` = mép trong vùng nền `=B24+B7/2`, `B26` = mép ngoài vùng nền (giờ, lấy `=B25+MAX(2*B16,24)`):

| Ô | Thông số | Công thức |
|---|---|---|
| B27 | Độ sáng TB vùng vai | `=SUMPRODUCT(ose!B2:B200*ose!C2:C200*(ABS(ose!A2:A200)>B23)*(ABS(ose!A2:A200)<B24))/SUMPRODUCT(ose!C2:C200*(ABS(ose!A2:A200)>B23)*(ABS(ose!A2:A200)<B24))` |
| B28 | Độ sáng TB vùng nền | như B27, thay B23→B25, B24→B26 |
| B29 | Vai trũng D (ppm) | `=(B28-B27)*1E6` |
| B30 | Số bin vùng vai | `=SUMPRODUCT((ABS(ose!A2:A200)>B23)*(ABS(ose!A2:A200)<B24))` |
| B31 | Số bin vùng nền | `=SUMPRODUCT((ABS(ose!A2:A200)>B25)*(ABS(ose!A2:A200)<B26))` |
| B32 | Sai số σ_D (ppm), từ độ tán xạ các bin nền | `=STDEV(FILTER(ose!B2:B200,ABS(ose!A2:A200)>B25,ABS(ose!A2:A200)<B26))*1E6*SQRT(1/B30+1/B31)` |
| B33 | **Bán kính vệ tinh tối đa (R⊕)** | `=SQRT((MAX(B29,0)+2*B32)*1E-6*(2*B16+B7)/B7)*B6*109.1` |

(0.49 giờ ở B23 là nửa giờ nhòe phơi sáng. Sai số tính theo bin nên khác bản Python vài chục phần trăm: Kepler-10c ra 0.58 R⊕ so với 0.74 R⊕ của Python; phần vùng Hill/Roche và TTV thì khớp tuyệt đối.)

Google Sheets chỉ hợp để **nhìn và tính nhanh**. Còn tìm chu kỳ (BLS) hay khớp mô hình có tối rìa thì nên dùng Python.

### 8.3. Kết quả mẫu: Kepler-6b

| Thông số | Tự tính | NASA |
|---|---|---|
| Chu kỳ | 3.23470 ngày | 3.2347 |
| Rp/Rs | 0.0931 | 0.0942 |
| a/Rs | 7.59 | 7.50 |
| Mật độ sao | 0.79 g/cm³ | 0.78 |
| Khối lượng sao (từ transit) | 1.21 M☉ | 1.21 |
| Bán kính hành tinh | 13.1 R⊕ (dùng Rs của KIC = 1.29) | 14.6 (Rs = 1.39) |
| Khối lượng hành tinh (ước tính từ bán kính) | ~114 M⊕ | |
| Khối lượng hành tinh (K = 80.9 m/s + Ms, i tự tính) | 212 M⊕ = 0.668 M♃ | 212 M⊕ |
| Khoảng cách (thị sai Gaia DR3 1.711 mas) | 585 pc ≈ 1.906 năm ánh sáng | 587 pc |
| Khoảng cách (ước tính bằng độ sáng) | ~636 pc | |

Bán kính hành tinh lệch khoảng 10% **hoàn toàn do bán kính sao**: KIC ghi 1.29 R☉, còn NASA dùng 1.39 R☉ từ phân tích phổ. Bài học: **muốn biết hành tinh thì phải biết rõ sao mẹ trước.**

### 8.4. Kết quả mẫu: Kepler-10 (hệ 3 hành tinh)

| | Kepler-10 b | Kepler-10 c | Kepler-10 d |
|---|---|---|---|
| Phát hiện | Transit (tự tìm, SNR 274) | Transit (tự tìm, SNR 176) | Chỉ RV (NASA) |
| Chu kỳ (ngày) | 0.83749 | 45.2942 | 151.06 |
| Bán kính (R⊕) | 1.43 (NASA 1.47) | 2.17 (NASA 2.35) | ~3.7 (ước tính từ khối lượng) |
| Khối lượng (M⊕) | 3.2 | 11.3 | ≥ 13.0 (tối thiểu) |
| Mật độ (g/cm³) | 6.0 | 6.1 | — |
| Khoảng cách tới sao (AU) | 0.017 | 0.240 | 0.535 |
| Nhiệt độ cân bằng (K) | ~1970 | ~520 | ~350 |
| Thành phần | Đá + sắt, lõi sắt ~13% | Nhiều nước/băng hoặc khí H/He mỏng (~0.5%) | Không xác định |

Sao mẹ: loại G, 0.89 M☉, 1.06 R☉, [Fe/H] = −0.15, tuổi ~10.6 tỷ năm, cách Trái Đất **186 pc ≈ 607 năm ánh sáng** (thị sai Gaia 5.37 mas).

Kepler-10 b nóng gần 2.000 K, bề mặt có thể là biển dung nham. Kepler-10 c nặng gấp 11 lần Trái Đất mà bán kính chỉ 2.2 lần, đặc như đá nhưng vẫn quá lớn để là đá thuần.
