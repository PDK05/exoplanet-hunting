# Tìm vệ tinh quanh các hành tinh của Kepler-186

Light curve Kepler chỉ đặt được **giới hạn trên**: vệ tinh lớn/nặng hơn mức này đã bị loại. Giả định vệ tinh đá (mật độ 3 g/cm³), quỹ đạo tròn, cùng chiều; giới hạn tính cho vệ tinh ở xa nhất có thể (0.49 bán kính Hill), nơi tín hiệu lớn nhất.

| Thông số | Kepler-186 b | Kepler-186 c | Kepler-186 d | Kepler-186 e | Kepler-186 f |
|---|---|---|---|---|---|
| Khối lượng hành tinh dùng (M⊕) | 1.1 (ước tính từ bán kính) | 2.0 (ước tính từ bán kính) | 2.4 (ước tính từ bán kính) | 1.8 (ước tính từ bán kính) | 1.3 (ước tính từ bán kính) |
| Bán kính Hill (km) | 75,333 | 138,567 | 219,662 | 284,279 | 823,496 |
| Quỹ đạo vệ tinh xa nhất bền vững, 0.49 R_Hill (km) | 36,876 | 67,828 | 107,524 | 139,155 | 403,101 |
| Giới hạn Roche (km) | 19,812 | 24,012 | 25,386 | 23,254 | 20,869 |
| **Vệ tinh có thể tồn tại?** | ✅ có | ✅ có | ✅ có | ✅ có | ✅ có |
| Chu kỳ vệ tinh dài nhất (ngày) | 0.77 | 1.44 | 2.64 | 4.43 | 25.69 |
| Vệ tinh lệch trước/sau hành tinh tối đa (giờ) | 0.10 | 0.22 | 0.42 | 0.65 | 3.37 |
| Số transit định thời được | 299 | 158 (loại 2 ngoại lai) | 85 (loại 3 ngoại lai) | 45 | 9 |
| Sai số thời điểm mỗi transit (phút) | 22.7 | 16.2 | 15.6 | 23.3 | 20.5 |
| O−C rms (phút) | 29.5 | 20.4 | 15.7 | 31.9 | 60.5 |
| χ²_red của O−C (≈ 1 nếu sai số đúng) | 4.52 | 2.39 | 1.25 | 3.43 | 10.17 |
| Periodogram O−C: chu kỳ mạnh nhất (vòng) / FAP | 6.8 / 0.00034 | 19.9 / 0.1 | 2.9 / 0.26 | 4.8 / 0.87 | 8.3 / 0.64 |
| O−C phụ thuộc vị trí trong lưới đo 29.4 phút? (p) | 0.55 | 0.36 | 0.83 | 0.36 | — |
| Chu kỳ O−C lặp lại ở cả 2 nửa dữ liệu? | không | không | không | không | — |
| Kết luận TTV | O−C có chu kỳ ~6.8 vòng (FAP = 3.4e-04) nhưng **không lặp lại ở cả hai nửa dữ liệu** → nhiều khả năng là nhiễu (nhiễu đỏ, vết đen sao), không phải TTV | Không thấy TTV có chu kỳ (FAP = 0.10) | Không thấy TTV có chu kỳ (FAP = 0.26) | Không thấy TTV có chu kỳ (FAP = 0.87) | Không thấy TTV có chu kỳ (FAP = 0.64) |
| Giới hạn TTV rms = O−C rms (phút) | 29.5 | 20.4 | 15.7 | 31.9 | 60.5 |
| **Khối lượng vệ tinh tối đa (từ TTV)** | 8.18 M⊕ = 665 lần Mặt Trăng | 4.45 M⊕ = 362 lần Mặt Trăng | 2.08 M⊕ = 169 lần Mặt Trăng | 2.12 M⊕ = 172 lần Mặt Trăng | 0.557 M⊕ = 45.3 lần Mặt Trăng |
| Vai trũng OSE (ppm) | — | — | — | — | 38.5 ± 41.2 |
| **Bán kính vệ tinh tối đa (từ OSE)** | — | — | — | — | 0.84 R⊕: đã loại vật cỡ Trái Đất trở lên; chưa loại được vật cỡ Sao Hỏa |

Ghi chú:
- **TTV** ở đây là độ lệch thời điểm so với chu kỳ đều. TTV đáng kể có thể do hành tinh khác kéo, vết đen trên sao, nhiễu đỏ... chứ không nhất thiết là vệ tinh.
- Vệ tinh gần hành tinh hơn a_max thì TTV nhỏ hơn (tỉ lệ với khoảng cách), nên giới hạn khối lượng yếu đi tương ứng.
- **OSE** giả định nhiễu trắng; nhiễu đỏ làm giới hạn thực tế kém hơn. Một tín hiệu "vai" dương cũng có thể là do bước làm phẳng light curve.
- Hành tinh quá gần sao: bán kính Hill nhỏ, vệ tinh còn bị thủy triều kéo dần vào hành tinh hoặc văng ra trong thời gian ngắn hơn tuổi hệ (Barnes & O'Brien 2002), nên khó tồn tại kể cả khi nằm trong vùng bền.
