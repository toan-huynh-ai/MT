# Báo cáo sơ bộ: Ba lớp tiếng Khmer và khoảng cách dịch Việt–Khmer

> Tài liệu này được tạo tự động từ `results/report_data.json`.
> Dữ liệu đầu vào: kết quả GPT-4o trên 1,856 mẫu song ngữ Việt–Khmer
> (`results/gpt4o_full_1856.json`).

**Tổng quan nhanh**

- Tổng số mẫu: **1856**.
- Số mẫu mà bản dịch tham chiếu (REF) chứa marker Khmer-Việt / Khmer Nam Bộ: **181** (≈ 9.8% dataset).
- Số mẫu mà GPT-4o đánh rơi marker đó (dịch thẳng sang Khmer Cambodia chuẩn): **139 / 181 (76.8%)**.

---

## 1. Ba lớp của tiếng Khmer (khung phân tích)

Tiếng Khmer tại Việt Nam (Khmer Nam Bộ, Khmer Krom) không phải một ngôn ngữ
độc lập. Nó là một phương ngữ của tiếng Khmer. Để phân tích cho đúng, ta chia
nó thành ba lớp:

### 1.1 Lớp 1 — Cốt lõi (Core)

Lớp ngôn ngữ chung giữa Khmer Campuchia và Khmer Nam Bộ. Bao gồm:

- Ngữ pháp, cấu trúc câu SVO, bảng chữ cái.
- Từ vựng cơ bản: ăn, ngủ, nước, lửa, trời, đất, cha, mẹ (dạng trang trọng), người, nhà.
- Vốn học thuật – tôn giáo có gốc Pali/Sanskrit: `ព្រះសង្ឃ` (nhà sư),
  `វត្ត` (chùa), `មរណភាព` (qua đời), `សាកសព` (thi thể).

Người Khmer Nam Bộ và người Campuchia nói chuyện ở lớp này vẫn hiểu nhau.
**Ở lớp này, một bản dịch chuẩn Campuchia cũng xem là đúng.**

### 1.2 Lớp 2 — Khmer Krom thuần (văn nói / giao tiếp thực tế)

Đây là lớp làm nên bản sắc. Đặc trưng:

- **Mượn âm Việt Nam** cho đồ vật / khái niệm mới: xe máy → `សេម៉ាយ`,
  tivi → `ទីវី`, bệnh viện → `បេញវៀង`, Ủy ban → `អ៊ុយបាន`.
- **Phiên âm Việt Nam vào tiếng Khmer** cho tên món, địa danh, ethnonym:
  mắm bò hóc → `ម៉ាំប្រហុក`, người Kinh → `គិញ`, Tri Tôn → `ទ្រីតុង`,
  Nam Bộ → `ណាមបូ`.
- **Xưng hô khẩu ngữ**: mẹ → `ម៉ែ` / `ម៉ាក់`, ba → `ប៉ា`.
- **Code-switching**: chèn hư từ tiếng Việt vào câu tiếng Khmer.
- **Phát âm chệch** so với Khmer Campuchia chuẩn.

Lớp này sống chủ yếu ở dạng văn nói, tin nhắn cộng đồng, bài đăng mạng xã
hội. Rất hiếm khi lên báo chí.

### 1.3 Lớp 3 — Khmer hành chính / báo chí (văn viết đã chuẩn hoá)

Khi người Khmer Nam Bộ phải viết văn bản chính thức (cán bộ, phóng viên),
họ gạt Lớp 2 sang bên và dùng ngữ pháp + từ vựng học thuật Campuchia
(gốc Pali/Sanskrit) để dịch các khái niệm Việt Nam:

- Công an → `នគរបាល` (Nokorbal).
- Ủy ban nhân dân → `គណៈកម្មាធិការប្រជាជន`.
- Bộ Giáo dục → `ក្រសួងអប់រំ`.

Đặc trưng Lớp 3: **vỏ Campuchia, ruột Việt Nam** — dùng từ chuẩn Campuchia
để nói về thiết chế / khái niệm chỉ có trong bối cảnh Việt Nam.

---

## 2. So sánh Khmer Campuchia và Khmer-Việt Nam (Khmer Krom)

| Khía cạnh | Khmer Campuchia (chuẩn) | Khmer Nam Bộ (Krom) |
|---|---|---|
| Khu vực chính | Vương quốc Campuchia | Đồng bằng sông Cửu Long, Việt Nam |
| Số người dùng | ~16 triệu | ~1.3 triệu |
| Nguồn vay mượn hiện đại | Pháp, Anh | Tiếng Việt |
| Cách gọi "mẹ" (khẩu ngữ) | `ម៉ាក់` hoặc `ម្តាយ` | `ម៉ែ`, `ម៉ាក់`, `ប៉ា` |
| Cách gọi "người Kinh" | Thường dùng `វៀតណាម` hoặc `យួន` | `គិញ` |
| Tên "Nam Bộ" | `តំបន់ខាងត្បូង` (miền Nam địa lý) | `ណាមបូ` (phiên âm Việt) |
| Tên Trà Vinh | `ព្រះត្រពាំង` (tên Khmer cổ) | `ត្រាវិញ` (phiên âm Việt) |
| Tên Tri Tôn | `ស្រុកបាយ៉ង់` (Srok Bayon) | `ទ្រីតុង` (phiên âm Việt) |
| Mắm bò hóc | `ប្រហុក` (prahok) | `ម៉ាំប្រហុក` (mắm prahok) |
| Cốm dẹp | `អង្ករកន្ទក់` | `អំបុក` |
| Ủy ban | `គណៈកម្មាធិការ` (từ Pali) | `អ៊ុយបាន` (phiên âm Việt) |
| Ghe ngo | `ទូកង` / `ទូកអុំ` | cùng dạng, nhưng thường đi kèm `ប្រណាំងទូកអុំ` |
| Thần bảo hộ làng | `អ្នកតា` được dùng nhưng hạn hẹp hơn | `អ្នកតា`, `ភូមិសង្គម` dùng rộng hơn |
| Tôn giáo nền | Theravāda | Theravāda (Phật giáo Nam tông Khmer) |
| Độ phủ của NLP / MT | Trung bình (FLORES, NLLB, Google) | Rất thấp |

Phần lớn **từ vựng học thuật và tôn giáo giống nhau** (Lớp 1). Điểm khác
biệt tập trung ở **tên riêng, ẩm thực, xưng hô khẩu ngữ, thiết chế hành
chính mượn âm Việt** (Lớp 2 và Lớp 3).

---

## 3. Thống kê chủ đề trong bộ dữ liệu

Mỗi mẫu trong dataset được gắn một nhãn chủ đề. **Các mẫu không có nhãn
(chủ yếu là phần hỏi-đáp về ăn uống) được gán vào "Ăn uống" / "Eating (Q&A)"**
theo yêu cầu của báo cáo.

- Tổng số mẫu: **1856**.
- Số chủ đề độc nhất sau khi chuẩn hoá: **57**.
- Cột "REF có marker Khmer-Việt" đếm số mẫu mà bản dịch tham chiếu chứa ít
  nhất một dấu ngôn ngữ Khmer Nam Bộ (xưng hô khẩu ngữ, ethnonym `គិញ`,
  địa danh Nam Bộ dạng Krom, tên món Khmer-Việt, lễ hội Nam Bộ, thuật ngữ
  tôn giáo Krom, từ mượn âm Việt).
- Cột "GPT-4o đánh rơi" đếm số mẫu mà GPT-4o **không** tái hiện marker đó
  trong bản dịch, tức đã chuẩn hoá về Khmer Campuchia.


| # | English topic | Chủ đề tiếng Việt | Tổng mẫu | REF có marker Khmer-Việt | GPT-4o đánh rơi | Tỉ lệ |
|---:|---|---|---:|---:|---:|---:|
| 1 | Eating (Q&A) | Ăn uống | 352 | 95 | 70 | 74% |
| 2 | Pre-wedding customs | Phong tục trước khi kết hôn | 48 | 0 | 0 | – |
| 3 | Wedding customs | Phong tục khi kết hôn | 24 | 2 | 2 | 100% |
| 4 | Post-wedding customs | Phong tục sau khi kết hôn | 24 | 0 | 0 | – |
| 5 | Groom wedding attire | Trang phục cưới hỏi nam | 16 | 2 | 1 | 50% |
| 6 | Bride wedding attire | Trang phục cưới hỏi nữ | 16 | 2 | 1 | 50% |
| 7 | Wedding guests | Khách mời đám cưới | 16 | 1 | 0 | 0% |
| 8 | Wedding venue | Vị trí tổ chức đám cưới | 8 | 1 | 1 | 100% |
| 9 | Wedding cuisine | Ẩm thực đám cưới | 16 | 2 | 1 | 50% |
| 10 | Wedding gifts | Quà cưới | 16 | 0 | 0 | – |
| 11 | Immediate family relationships | Mối quan hệ trong gia đình chính | 36 | 3 | 2 | 67% |
| 12 | Extended family relationships | Mối quan hệ trong gia đình mở rộng | 18 | 0 | 0 | – |
| 13 | Society & neighbours | Mối quan hệ với xã hội/hàng xóm | 30 | 2 | 2 | 100% |
| 14 | Parent–adult-child interactions | Tương tác giữa cha mẹ và con cái khi trưởng thành | 24 | 1 | 1 | 100% |
| 15 | Pregnancy customs | Phong tục khi mang bầu | 47 | 0 | 0 | – |
| 16 | Postnatal customs | Phong tục sau khi đẻ con | 24 | 0 | 0 | – |
| 17 | Newborn care | Cách chăm sóc trẻ sơ sinh | 24 | 0 | 0 | – |
| 18 | Toddler care | Cách chăm sóc trẻ mới biết đi | 24 | 0 | 0 | – |
| 19 | Child care | Cách chăm sóc trẻ em | 24 | 0 | 0 | – |
| 20 | Teenager care | Cách chăm sóc trẻ vị thành niên | 24 | 0 | 0 | – |
| 21 | When death occurs | Khi có người mất | 24 | 2 | 2 | 100% |
| 22 | Corpse-handling process | Quy trình xử lý thi thể | 24 | 0 | 0 | – |
| 23 | Post-burial customs | Phong tục sau khi chôn cất | 24 | 1 | 1 | 100% |
| 24 | Mourner attire | Trang phục của người đưa tang | 24 | 0 | 0 | – |
| 25 | Inheritance matters | Vấn đề thừa kế | 24 | 0 | 0 | – |
| 26 | Pre-holiday customs | Những phong tục trước ngày lễ tôn giáo | 24 | 2 | 2 | 100% |
| 27 | Holiday preparation customs | Những phong tục chuẩn bị cho ngày lễ tôn giáo | 48 | 1 | 1 | 100% |
| 28 | Day-of holiday customs | Những phong tục ngay ngày lễ tôn giáo | 60 | 0 | 0 | – |
| 29 | Post-holiday customs | Những phong tục sau ngày lễ tôn giáo | 12 | 0 | 0 | – |
| 30 | Planting customs | Phong tục khi trồng trọt | 24 | 4 | 3 | 75% |
| 31 | Harvesting | Thu hoạch | 24 | 8 | 8 | 100% |
| 32 | Livestock & aquaculture care | Truyền thống chăm sóc vật nuôi/thủy sản | 75 | 2 | 2 | 100% |
| 33 | Musical instruments | Nhạc cụ | 36 | 1 | 1 | 100% |
| 34 | Folk songs | Dân ca | 37 | 1 | 1 | 100% |
| 35 | Traditional dances | Các điệu múa truyền thống | 46 | 0 | 0 | – |
| 36 | Art at events | Biểu diễn nghệ thuật tại một số sự kiện nhất định | 59 | 15 | 12 | 80% |
| 37 | Poetry or similar literature | Thơ hoặc văn học tương tự | 24 | 1 | 1 | 100% |
| 38 | Game types | Các loại trò chơi | 35 | 1 | 1 | 100% |
| 39 | Play locations | Vị trí chơi | 24 | 0 | 0 | – |
| 40 | Morning activities | Hoạt động buổi sáng | 12 | 0 | 0 | – |
| 41 | Afternoon activities | Hoạt động buổi chiều | 12 | 1 | 1 | 100% |
| 42 | Evening activities | Hoạt động buổi tối | 12 | 1 | 1 | 100% |
| 43 | Leisure activities | Hoạt động giải trí | 36 | 6 | 2 | 33% |
| 44 | Household & transport | Nhà cửa, gia đình và giao thông | 48 | 4 | 4 | 100% |
| 45 | Regular religious life | Sinh hoạt tôn giáo thường kỳ | 26 | 0 | 0 | – |
| 46 | Mystical beliefs | Những điều huyền bí | 24 | 6 | 4 | 67% |
| 47 | Traditional ceremonies | Nghi lễ truyền thống | 12 | 6 | 6 | 100% |
| 48 | Lifestyle | Lối sống | 36 | 3 | 2 | 67% |
| 49 | Self-care | Cách tự chăm sóc | 12 | 1 | 1 | 100% |
| 50 | Traditional medicine | Y học cổ truyền | 36 | 0 | 0 | – |
| 51 | Traditional sayings | Những câu nói truyền thống | 12 | 0 | 0 | – |
| 52 | Unknown | Không xác định | 30 | 1 | 1 | 100% |
| 53 | Buying and selling traditions | Buying and selling traditions | 24 | 1 | 1 | 100% |
| 54 | What to plant | What to plant | 24 | 0 | 0 | – |
| 55 | MỐI QUAN HỆ TRONG GIA | MỐI QUAN HỆ TRONG GIA | 17 | 1 | 0 | 0% |
| 56 | GIA TỘC | GIA TỘC | 12 | 0 | 0 | – |
| 57 | HẬU DUỆ / GIA TỘC | HẬU DUỆ / GIA TỘC | 12 | 0 | 0 | – |


---

## 4. Minh hoạ định tính: 50 mẫu

Chia làm hai nhóm:
- **25 mẫu dịch được** — nội dung thuộc Lớp 1 hoặc chỉ chứa khái niệm
  phổ thông. GPT-4o đưa ra bản Khmer chuẩn, không mất nét văn hoá nào có
  thể xác định được bằng heuristic.
- **25 mẫu dịch fail vì yếu tố văn hoá Việt Nam** — REF có marker
  Khmer-Việt, GPT-4o **đánh rơi** marker đó, dịch thẳng sang dạng Khmer
  Campuchia. Từng mẫu đi kèm một đoạn giải thích chỉ ra **đánh rơi chỗ
  nào** và **tại sao đó là lỗi văn hoá**.

### 4.1 — 25 mẫu GPT-4o dịch được Khmer Campuchia chuẩn

Dòng in nghiêng `_VI_` bên dưới mỗi mẫu là **câu nguồn tiếng Việt**.


| # | Chủ đề | Tiếng Việt | REF (Khmer) | GPT-4o (Khmer) | chrF++ |
|---:|---|---|---|---|---:|
| 1 | Eating (Q&A) | Ăn uống | ឪខ្ញុំជាអ្នករៀបបាយ រួចហើយហូបបាយ ក្នុងពេលបាយយើងខ្ញុំជជែកគ្នាលេងនិយាយអំពីការងារដែលពេលរសៀលត្រូវធ្វើ ហូបហើយខ្ញុំជាអ្នករៀបចានយកទៅលាងឲ្យស្អាតផ្កាប់ចានឲ្យសណ្ដាប់ធ្នាប់។ | ឪពុកខ្ញុំជាអ្នករៀបចំអាហារ ពេលរៀបចំរួចហើយនឹងទទួលទានអាហារ ក្នុងពេលបរិភោគយើងនិយាយគ្នាអំពីការងារដែលត្រូវធ្វើនៅល្ងាច បន្ទាប់ពីបរិភោគរួចខ្ញុំជាអ្នករៀបចំចានយកទៅលាងស្អាតហើយដាក់ចានឲ្យរបៀបរៀបរយ។ | 37.7 |
|   | _VI_ | _nguồn_ | _Ba tôi là người dọn cơm, dọn xong thì ăn cơm, trong giờ cơm chúng nói chuyện với nhau nói về công việc của buổi chiều cần làm, ăn xong tôi là người dọn chén mang đi rửa sạch và úp chén cho gọn gàng._ |  |  |
| 2 | Wedding customs | Phong tục khi kết hôn | សម្លៀកបំពាក់អាពាហ៍ពិពាហ៍ប្រពៃណីរបស់កូនកំលោះក្រមំ ខ្មែរ តែងមានភាពស្រស់ស្អាតនិងមានអត្ថន័យ។ សម្លៀកបំពាក់របស់កូនក្រមុំខ្មែរជាទូទៅរួមមានអាវវេងសំពត់សារុង និងគ្រឿងប្រើប្រាស់ដូចជាស្បៃ មួកអាពាហ៍ពិពាហ៍ និងគ្រឿ… | - សម្លៀកបំពាក់អាពាហ៍ពិពាហ៍ប្រពៃណីរបស់កូនក្រមុំ និងកូនកំលោះខ្មែរមានភាពស្រស់ស្អាត និងមានន័យជ្រាលជ្រៅ។ សម្លៀកបំពាក់របស់កូនក្រមុំខ្មែរមានសម្លៀកបំពាក់ដូចជា អាវដៃវែង សំពត់សារ៉ុង និងគ្រឿងតុបតែងផ្សេងៗដូចជា ស… | 48.4 |
|   | _VI_ | _nguồn_ | _- Trang phục cưới truyền thống của cô dâu, chú rể Khmer thường rất lộng lẫy và mang nhiều ý nghĩa. Trang phục của cô dâu Khmer thường bao gồm áo dài, xăm-pốt sarong và các phụ kiện như sbay, mũ cưới …_ |  |  |
| 3 | Household & transport | Nhà cửa, gia đình và giao thông | ក្រៅពីស្ថាបត្យកម្មផ្ទះ តើការរស់នៅក្នុងគ្រួសារខ្មែរមានលក្ខណៈពិសេសអ្វីផ្សេងទៀត? | Khmer: ក្រៅពីស្ថាបត្យកម្មផ្ទះ វិធីសាស្រ្តរស់នៅក្នុងគ្រួសារខ្មែរមានលក្ខណៈពិសេសអ្វីខ្លះដែលខុសគ្នា? | 63.8 |
|   | _VI_ | _nguồn_ | _Ngoài kiến trúc nhà, sinh hoạt trong gia đình Khmer có đặc điểm gì khác biệt?_ |  |  |
| 4 | Self-care | Cách tự chăm sóc | អ្នកសម្ភាសន៍៖ ក្រៅពីនេះ ខ្ញុំបានឮថាជនជាតិខ្មែរនៅមានការយកចិត្តទុកដាក់ចំពោះភាពត្រជាក់-ក្តៅ ក្នុងអាហារ និងការរស់នៅប្រចាំថ្ងៃ។ | អ្នកសម្ភាសន៍៖ លើសពីនេះទៅទៀត ខ្ញុំបានឮថា ជនជាតិខ្មែរនៅតែផ្តោតលើភាពសមស្របរវាងក្តៅ-ត្រជាក់ក្នុងការទទួលទានអាហារ និងការរស់នៅប្រចាំថ្ងៃ។ | 51.2 |
|   | _VI_ | _nguồn_ | _Người phỏng vấn: Ngoài ra, tôi nghe nói người Khmer còn chú trọng đến sự hài hòa Nóng-Lạnh trong ăn uống và sinh hoạt hàng ngày._ |  |  |
| 5 | Society & neighbours | Mối quan hệ với xã hội/hàng xóm | តើបងគិតថាទំនាក់ទំនងទាំងនេះផ្លាស់ប្តូរនៅពេលដែលខ្មែរផ្លាស់ទៅរស់នៅនិងធ្វើការទេ? | Khmer: តើបងគិតថាការទំនាក់ទំនងទាំងនេះនឹងផ្លាស់ប្តូរឬទេនៅពេលដែលជនជាតិខ្មែរឡើងទៅរស់នៅនិងធ្វើការនៅទីក្រុង? | 56.6 |
|   | _VI_ | _nguồn_ | _Anh có nghĩ những mối quan hệ này thay đổi khi người Khmer lên thành phố sống và làm việc không?_ |  |  |
| 6 | Teenager care | Cách chăm sóc trẻ vị thành niên | ទន្ទឹមនឹងនោះ មនុស្សធំតែងតែស្តាប់នូវទំនុកចិត្តរបស់កូន ព្រោះបើហាមឃាត់ខ្លាំងពេក កូននឹងលាក់លៀម និងឃ្លាតឆ្ងាយពីអ្នកធំ។ | នៅពេលដូចគ្នា មនុស្សធំតែងតែស្តាប់ការប្រាប់ប្រាស្រ័យរបស់កូន ពីព្រោះប្រសិនបើហាមឃាត់ខ្លាំងពេក កូនងាយលាក់បាំង និងឆ្ងាយឆ្ងាញ់។ | 36.3 |
|   | _VI_ | _nguồn_ | _Đồng thời, người lớn luôn lắng nghe tâm sự của con, vì nếu cấm đoán quá mức thì con dễ giấu giếm và xa cách._ |  |  |
| 7 | Post-burial customs | Phong tục sau khi chôn cất | ចាសមាន ប្រជាជនមានជំនឿថា ការដាក់ធាតុក្នុងវត្ត នឹងជួយឱ្យអ្នកស្លាប់បានស្តាប់ធម៏រាល់ថ្ងៃ ជួយឱ្យព្រលឹងបានទៅកាន់សុគតិភព។ | បាទ/ចាស មាន, មនុស្សជឿថាការដាក់ធាតុធូលីនៅវត្តនោះ អ្នកដែលបានស្លាប់នឹងបានស្តាប់ព្រះធម៌ជារៀងរាល់ថ្ងៃ ដែលជួយឱ្យព្រលឹងមានសេចក្តីសុខចិត្ត។ | 35.7 |
|   | _VI_ | _nguồn_ | _Dạ có, người ta tin rằng đặt tro cốt ở chùa thì người mất sẽ được nghe kinh kệ hàng ngày, giúp linh hồn an lạc hơn._ |  |  |
| 8 | Newborn care | Cách chăm sóc trẻ sơ sinh | អរគុណបងស្រីច្រើន! ការចែករំលែករបស់បងទាំងនេះជួយឱ្យខ្ញុំយល់កាន់តែស៊ីជម្រៅអំពីភាពស្រស់ស្អាតប្រពៃណីនៃវប្បធម៌ខ្មែរ។ | អរគុណបងច្រើនណាស់! ការចែករំលែករបស់បងបានជួយឱ្យខ្ញុំយល់ច្បាស់ជាងមុនអំពីភាពស្រស់ស្អាតប្រពៃណីក្នុងវប្បធម៌ខ្មែរ។ | 53.0 |
|   | _VI_ | _nguồn_ | _Cảm ơn chị rất nhiều! Những chia sẻ của chị giúp em hiểu sâu hơn về nét đẹp truyền thống trong văn hóa Khmer._ |  |  |
| 9 | Wedding guests | Khách mời đám cưới | ក្រៅពីលិខិតអញ្ជើញ ប្រជាជនខ្មែរក៏មានសុភាសិតផ្សាយផ្ទាល់មាត់ ដែលមានន័យថា ការអញ្ជើញតាមពាក្យសម្ដីដើម្បីផ្សព្វផ្សាយព័ត៌មានក្នុងសហគមន៍។ | ខ្មែរ: - ក្រៅពីការផ្តល់ការអញ្ជើញជាសំបុត្រ អ្នកខ្មែរនៅមានទំនៀមទម្លាប់នៃការផ្តល់ការអញ្ជើញដោយមាត់ ដែលមានន័យថា អញ្ជើញដោយពាក្យសម្តីដើម្បីចែករំលែកព័ត៌មានក្នុងសហគមន៍។ | 39.2 |
|   | _VI_ | _nguồn_ | _- Ngoài giấy mời, người Khmer còn có tục ngữ truyền miệng, nghĩa là mời bằng lời để lan toả thông tin trong cộng đồng._ |  |  |
| 10 | Post-holiday customs | Những phong tục sau ngày lễ tôn giáo | ត្រូវហើយ! យើងចាប់ផ្តើមសំអាតស្រែចម្ការ រៀបចំឧបករណ៍កសិកម្ម គោក្របី និងគិតគូរពីពេលរដូវកាលដាំដុះថ្មី។ | មែនហើយ ពួកយើងចាប់ផ្តើមសម្អាតវាលស្រែ រៀបចំឧបករណ៍កសិកម្ម គោក្របី និងគិតគូរពីរដូវវារីស្រូវថ្មី។ | 53.1 |
|   | _VI_ | _nguồn_ | _Đúng vậy, chúng tôi bắt đầu dọn dẹp ruộng đồng, chuẩn bị nông cụ, trâu bò, và tính toán thời vụ gieo trồng mới._ |  |  |
| 11 | Art at events | Biểu diễn nghệ thuật tại một số sự kiện nhất định | អ្នកសម្ភាសន៍៖ តាមរយៈការចែករំលែករបស់បង ខ្ញុំយល់ថា សិល្បៈដើរតួនាទីមិនអាចខ្វះបានក្នុងការរក្សាវប្បធម៌ខ្មែរ។ | អ្នកសម្ភាសន៍៖ តាមការចែករំលែករបស់បង ខ្ញុំបានឃើញថា សិល្បៈមានតួនាទីមិនអាចខ្វះបានក្នុងការរក្សាវប្បធម៌ខ្មែរ។ | 65.5 |
|   | _VI_ | _nguồn_ | _Người phỏng vấn: Qua chia sẻ của anh, tôi nhận thấy nghệ thuật đóng vai trò không thể thiếu trong việc duy trì văn hóa Khmer._ |  |  |
| 12 | Traditional dances | Các điệu múa truyền thống | ជនជាតិខ្មែរ៖ មាន ព្រះអង្គតែងតែណែនាំយុវជនឱ្យនៅឱ្យឆ្ងាយពីអំពើអាក្រក់ ចូលរួមក្នុងការងារសប្បុរសធម៌ និងធ្វើការងារសេវាសាធារណៈជាមួយអ្នកភូមិ។ | អ្នកខ្មែរ៖ បាទ/ចាស ពួកគេជាញឹកញាប់ណែនាំយុវជនឱ្យចៀសវាងអំពើអាក្រក់ ចូលរួមធ្វើការសប្បុរស និងធ្វើការងារសាធារណៈជាមួយប្រជាជនក្នុងភូមិ។ | 39.8 |
|   | _VI_ | _nguồn_ | _Người Khmer: Có, các vị thường khuyên bảo thanh thiếu niên tránh xa tệ nạn, tham gia làm từ thiện, và cùng dân làng lao động công ích._ |  |  |
| 13 | Game types | Các loại trò chơi | អ្នកសម្ភាសន៍៖ តើល្បែងបិទភ្នែកវាយឆ្នាំង ត្រូវបានរៀបចំច្រើនក្នុងឱកាសលេងកម្សាន្តជាក្រុមដែរឬទេ? | អ្នកសម្ភាសៈ ការលេងបិទភ្នែកវាយអាងត្រូវបានរៀបចំជាញឹកញាប់ក្នុងឱកាសលេងសប្បាយរួមគ្នាឬទេ? | 41.0 |
|   | _VI_ | _nguồn_ | _Người phỏng vấn: Trò bịt mắt đập niêu có được tổ chức nhiều trong các dịp vui chơi tập thể không?_ |  |  |
| 14 | Folk songs | Dân ca | ជនជាតិខ្មែរ៖ ត្រូវមួយចំណែកដែរ ប៉ុន្តែប្រសិនបើចេះផ្សំការសម្តែងលើឆាក បណ្តាញសង្គម នោះចម្រៀងប្រពៃណីនៅតែមានភាពទាក់ទាញខ្លាំង។ | ជនជាតិខ្មែរ៖ មានភាពត្រឹមត្រូវខ្លះ ប៉ុន្តែប្រសិនបើដឹងរបៀបបញ្ចូលការសម្តែងលើឆាក និងបណ្តាញសង្គម នោះចម្រៀងប្រជាប្រិយនៅតែមានសម្រស់ទាក់ទាញខ្លាំង។ | 51.7 |
|   | _VI_ | _nguồn_ | _Người Khmer: Có phần đúng, nhưng nếu biết kết hợp biểu diễn trên sân khấu, mạng xã hội thì dân ca vẫn có sức hút mạnh mẽ._ |  |  |
| 15 | Traditional medicine | Y học cổ truyền | អ្នកសម្ភាសន៍៖ ស្ដាប់ទៅហាក់បីដូចជា ការព្យាបាលនេះមានទាំងកត្តាខាងស្មារតី ទាំងការគាំទ្រពីឱសថធម្មជាតិ។ | អ្នកសម្ភាសន៍៖ ស្តាប់ទៅហាក់ដូចជាការព្យាបាលមានទាំងធាតុផ្នែកចិត្ត និងការគាំទ្រពីរុក្ខជាតិធម្មជាតិ។ | 48.0 |
|   | _VI_ | _nguồn_ | _Người phỏng vấn: Nghe như vậy có vẻ sự chữa trị vừa mang yếu tố tinh thần vừa có sự hỗ trợ từ cây thuốc tự nhiên._ |  |  |
| 16 | Morning activities | Hoạt động buổi sáng | បងអាចរៀបរាប់ពីសកម្មភាពពេលព្រឹកដ៏ពិសេស ក្នុងជីវិតសហគមន៍ខ្មែរបានទេ? | អាចប្រាប់អំពីសកម្មភាពពេលព្រឹកដែលជាការពិសេសក្នុងជីវិតសហគមន៍ខ្មែរបានទេ? | 63.3 |
|   | _VI_ | _nguồn_ | _Anh có thể chia sẻ về những hoạt động buổi sáng đặc trưng trong đời sống cộng đồng Khmer không?_ |  |  |
| 17 | Regular religious life | Sinh hoạt tôn giáo thường kỳ | អ្នកសម្ភាសន៍៖ ក្រៅពីការបង្រៀន តើព្រះសង្ឃមានចូលរួមក្នុងសកម្មភាពសហគមន៍ ឬជួយប្រជាជនក្នុងជីវភាពប្រចាំថ្ងៃដែរឬទេ? | អ្នកសម្ភាសន៍: ក្រៅពីការបង្រៀន តើព្រះសង្ឃមានការចូលរួមក្នុងសកម្មភាពសហគមន៍ ឬជួយសង្រ្គោះប្រជាជនក្នុងជីវិតប្រចាំថ្ងៃដែរឬទេ? | 68.4 |
|   | _VI_ | _nguồn_ | _Người phỏng vấn: Ngoài việc giảng dạy, chư tăng có tham gia vào những hoạt động cộng đồng hay giúp đỡ người dân trong sinh hoạt đời thường không?_ |  |  |
| 18 | Wedding venue | Vị trí tổ chức đám cưới | បាទ! ពិធីមង្គលការខ្មែរ តែងតែធ្វើឡើងនៅផ្ទះកូនក្រមុំ ឬកូនកំលោះ អាស្រ័យលើលក្ខខណ្ឌរបស់ភាគីទាំងពីរ។ | - បាទ/ចាស, ពិធីអាពាហ៍ពិពាហ៍របស់ជនជាតិខ្មែរតែងតែត្រូវបានរៀបចំនៅផ្ទះរបស់កូនក្រមុំ ឬកូនកំលោះ ដោយអាស្រ័យលើលក្ខខណ្ឌរបស់ភាគីទាំងពីរ។ | 50.2 |
|   | _VI_ | _nguồn_ | _- Dạ, đám cưới của người Khmer thường được tổ chức ngay tại nhà của cô dâu hoặc chú rể, tuỳ theo điều kiện hai bên._ |  |  |
| 19 | Wedding cuisine | Ẩm thực đám cưới | អរគុណបងស្រីច្រើនណាស់ សម្រាប់ការចែករំលែកយ៉ាងរស់រវើកនៃមុខម្ហូបប្រពៃណីខ្មែរ។ | សូមអរគុណបងសម្រាប់ការចែករំលែកដ៏រស់រវើកអំពីម្ហូបប្រពៃណីក្នុងពិធីអាពាហ៍ពិពាហ៍របស់ជនជាតិខ្មែរ។ | 47.4 |
|   | _VI_ | _nguồn_ | _- Cảm ơn chị rất nhiều vì những chia sẻ sinh động về các món ăn truyền thống trong đám cưới của người Khmer._ |  |  |
| 20 | Pregnancy customs | Phong tục khi mang bầu | អ្នកសម្ភាសន៍៖ តើប្ដីមានតួនាទីអ្វីខ្លះក្នុងអំឡុងពេលនេះ? | អ្នកសារព័ត៌មាន៖ ប្តីមានតួនាទីអ្វីក្នុងអំឡុងពេលនេះដែរឬទេ? | 46.8 |
|   | _VI_ | _nguồn_ | _Phóng viên: Người chồng có vai trò gì trong thời gian này không ạ?_ |  |  |
| 21 | Child care | Cách chăm sóc trẻ em | អ្នកសម្ភាសន៍៖ ចំពោះការងូតទឹក តើមានអ្វីពិសេសទេអ៊ំ? | អ្នកសារព័ត៌មាន៖ អំពីការងូតទឹក មានអ្វីពិសេសទេបង? | 40.4 |
|   | _VI_ | _nguồn_ | _Phóng viên: Về việc tắm rửa thì có điều gì đặc biệt không bác?_ |  |  |
| 22 | GIA TỘC | GIA TỘC | ក្នុងឱកាស់ចូលឆ្នាំថ្មី កូនចៅទាំងអស់ មកជួបជុំគ្នា សូម្បីតែអ្នកស្រុកដូចគ្នា ក៏បានអញ្ជើញចូលរួមដូចជាសមាជិកក្នុងគ្រួសារដែរ។ | ក្នុងឱកាសបុណ្យដូចជា​ចូលឆ្នាំថ្មី (Chol Chnam Thmay) កូនចៅប្រមូលផ្តុំគ្នាជាច្រើន រួមទាំងអ្នកស្រុកដូចគ្នាក៏ត្រូវបានអញ្ជើញមកដូចជាសមាជិកក្នុងគ្រួសារ។ | 45.5 |
|   | _VI_ | _nguồn_ | _Trong dịp lễ như Chol Chnam Thmay, con cháu tụ họp đông đủ, kể cả người cùng quê cũng được mời đến như người thân trong gia đình._ |  |  |
| 23 | Mystical beliefs | Những điều huyền bí | ជនជាតិខ្មែរ: នៅពេលនោះ គ្រូខ្មែរ ឬគ្រូទាយ នឹងធ្វើពិធីហៅព្រលឹង, ថ្វាយគ្រឿងបូជា, រួមផ្សំជាមួយឱសថបុរាណ ដើម្បីបណ្តេញអារក្សចេញ។ | ខ្មែរ: នៅពេលនោះ Kru Khmer ឬគ្រូបួងសួងនឹងធ្វើពិធីហៅព្រលឹង ដាក់ដូងបួងសួង និងប្រើស្មៅថ្នាំដើម្បីបណ្តេញអារ៉ាក់។ | 36.3 |
|   | _VI_ | _nguồn_ | _Người Khmer: Khi ấy, Kru Khmer hoặc thầy cúng sẽ làm lễ gọi hồn, dâng đồ cúng, kết hợp thảo dược để xua đuổi Arak._ |  |  |
| 24 | When death occurs | Khi có người mất | សួស្តីបងស្រី តើបងអាចចែករំលែកជាមួយខ្ញុំបានទេ ថាបើនៅពេលដែលមាននរណាម្នាក់ក្នុងគ្រួសារខ្មែរទទួលមរណភាព ធម្មតាជំហានដំបូងគេធ្វើអ្វី? | ជំរាបសួរបងស្រី, តើបងស្រីអាចចែករំលែកឱ្យខ្ញុំដឹងបានទេថា នៅពេលដែលមានសមាជិកក្នុងគ្រួសារខ្មែរម្នាក់ស្លាប់ ការដំណើរការដំបូងជាអ្វីដែរ? | 38.4 |
|   | _VI_ | _nguồn_ | _Chào chị, chị có thể chia sẻ cho em được biết, khi trong gia đình người Khmer có người qua đời, bước đầu tiên thường là gì ạ?_ |  |  |
| 25 | Evening activities | Hoạt động buổi tối | អ្នកសម្ភាសន៍៖ ក្រៅពីអាហារពេលល្ងាច តើមានប្រពៃណីអ្វីដែលភ្ជាប់ជាមួយនឹងជីវិតខាងវិញ្ញាណនៃជំនាន់នានាក្នុងគ្រួសារទេ? | អ្នកសម្ភាសៈ ក្រៅពីអាហារពេលល្ងាច តើមានប្រពៃណីណាដែលទាក់ទងនឹងជីវិតផ្លូវចិត្តរបស់ជំនាន់ផ្សេងៗក្នុងគ្រួសារឬទេ? | 48.5 |
|   | _VI_ | _nguồn_ | _Người phỏng vấn: Ngoài bữa cơm tối, có truyền thống nào gắn liền với đời sống tinh thần của các thế hệ trong gia đình không?_ |  |  |


### 4.2 — 25 mẫu GPT-4o dịch fail do yếu tố văn hoá Việt Nam

Mỗi mẫu trình bày dưới dạng khối (block) để có chỗ cho phần giải thích
chi tiết. Các mẫu được đánh dấu **false positive** là trường hợp heuristic
marker khớp nhầm; chúng được giữ lại để minh hoạ giới hạn của phương pháp
rà soát tự động, chứ không tính là bằng chứng lỗi dịch.


#### Mẫu 1 — Eating (Q&A) / Ăn uống

- **Câu tiếng Việt**: Tôi còn nhớ năm 2020, Tôi tham gia đoàn đi dự lễ Khánh thành chánh điện một ngôi chùa Phật giáo Nam tông Khmer tại Tri Tôn, An Giang. Xe Tôi 7 chỗ, khi dừng lại 1 điểm gần chợ Tịnh Biên, vừa bướt xuống xe trước mắt tôi là giang hàng bán rất nhiều sản phẩm Khmer, nhưng ai cũng ghé mua num tnot bởi có mùi thơm và vị ngọt của thốt Lốt, mọi người vừa ăn, vừa khen không ngớt đến khi lên xe còn mua mang về để biếu.
- **REF (Khmer)**: ខ្ញុំនៅតែចងចាំឆ្នាំ ២០២០ ខ្ញុំបានចូលរួមជាមួយក្រុមទៅចូលរួមពិធីសម្ពោធព្រះវិហារវត្ត ថេរវាទខ្មែរនៅទ្រីតុង ខេត្តអានយ៉ាង។ ឡាន៧កៅអីរបស់ខ្ញុំបានឈប់នៅកន្លែងក្បែរផ្សារទីញបៀន។ ពេលខ្ញុំចុះពីឡានភ្លាម មានតូបលក់ផលិតផលខ្មែរជាច្រើន ប៉ុន្តែគ្រប់គ្នាទិញតែនំត្នោត ដោយសារតែនំក្លិនឈ្ងុយ និងផ្អែមរស់ជាតនៃផ្លែត្នោត។ គ្រប់គ្នាបានញ៉ាំហើយសរសើរមិនដាច់ពីមាត់ រហូតដល់ពួកគេឡើងឡានមកវិញ ហើយទិញខ្លះយកទៅផ្ទះជូនអ្នកដទៃ។
- **GPT-4o (Khmer)**: ខ្ញុំនៅតែចងចាំឆ្នាំ 2020 ខ្ញុំបានចូលរួមក្រុមទៅចូលរួមពិធីសម្ពោធសាលាធម្មសាលានៃវត្តពុទ្ធសាសនាខ្មែរនៅស្រុកទ្រីតន ខេត្តអនជាង។ រថយន្តខ្ញុំមាន 7 កៅអី នៅពេលដែលបានឈប់នៅចំណុចមួយជិតផ្សារតិញបៀន ខ្ញុំទើបចុះពីរថយន្ត មុខខ្ញុំមានតូបលក់ផលិតផលខ្មែរច្រើនណាស់ ប៉ុន្តែអ្នកទាំងអស់គ្នាបានចូលទៅទិញនំត្នោត ព្រោះមានក្លិនឈ្ងុយនិងរសជាតិស្ករត្នោតផ្អែម។ មនុស្សទាំងអស់បានញ៉ាំហើយសរសើរមិនឈប់ រហូតដល់ឡើងរថយន្តវិញ ក៏បានទិញយកទៅផ្តល់ជាអំណោយ។
- **Marker bị đánh rơi**: `toponym_krom` | **chrF++**: 37.7
- **Giải thích**: REF giữ cách phiên âm địa danh Nam Bộ mà cộng đồng Khmer ĐBSCL đã dùng quen: `ទ្រីតុង` (Tri Tôn), `អានយ៉ាង` (An Giang), `ទីញបៀន` (Tịnh Biên). GPT-4o không biết dạng chuẩn này nên tự đặt phiên âm khác: `ទ្រីតន`, `អនជាង`, `តិញបៀន`. Với người Khmer Nam Bộ, các dạng của GPT-4o nghe như tên lạ.

#### Mẫu 2 — Wedding customs / Phong tục khi kết hôn

- **Câu tiếng Việt**: - Khi về nhà chồng, ngoài việc đôi tân hôn được rải nước thơm và lời chúc phúc cô dâu sẽ thực hiện một số nghi thức truyền thống, bao gồm: lễ rửa chân cho con dâu, lễ buộc chỉ tay, lễ nhập phòng. Và các nghi lễ như: cắt và rắc hoa cau, lễ cúng ông bà.
- **REF (Khmer)**: ពេលទៅដល់ផ្ទះប្ដី គូស្វាមីភរិយាថ្មីក្រៅពីបានស្រោចទឹកអប់និងសុំដៃជូនពរ កូនប្រសាស្រីនឹងធ្វើពិធីប្រពៃណីមួយចំនួន រួមមានៈ ពិធីលាងជើងកូនប្រសា ពិធីចងដៃ និងពិធីចូលរោង។ និងពិធីផ្សេងៗដូចជា ពិធីកាត់បាចផ្កាស្លា និងពិធីសែនដូនតា។
- **GPT-4o (Khmer)**: - នៅពេលដែលត្រឡប់ទៅផ្ទះប្ដី បន្ថែមពីការដែលគូស្វាម៉ីភរិយាថ្មីត្រូវបានបាញ់ទឹកក្រអូប និងទទួលពរជ័យសិរីមង្គល កូនក្រមុំនឹងអនុវត្តពិធីសាសនាបុរាណមួយចំនួន រួមមាន៖ ពិធីលាងជើងឲ្យកូនស្រីក្រមុំ, ពិធីចងខ្សែដៃ, ពិធីចូលបន្ទប់។ និងពិធីសាសនាដូចជា៖ កាត់និងបោះផ្កាព្រៅ, ពិធីបូជាឪពុកម្តាយ។
- **Marker bị đánh rơi**: `festival_krom` | **chrF++**: 31.1
- **Giải thích**: Trong văn hoá Khmer Nam Bộ, "lễ cúng tổ tiên" có tên chuyên biệt là `ពិធីសែនដូនតា` (Sen Dolta, được REF dùng). GPT-4o dịch word-for-word thành `បូជាឪពុកម្តាយ` (cúng cha mẹ) — tuy đúng nghĩa đen nhưng mất tên riêng của nghi lễ truyền thống của cộng đồng. Ngoài ra, GPT cũng dịch "nghi thức truyền thống" thành `ពិធីសាសនាបុរាណ` (nghi lễ tôn giáo cổ) — chuyển khung khái niệm từ văn hoá sang tôn giáo, lệch so với bản gốc.

#### Mẫu 3 — Household & transport / Nhà cửa, gia đình và giao thông

- **Câu tiếng Việt**: Nó vừa là phương tiện buôn bán, vận chuyển nông sản, vừa là hình ảnh gắn liền với lễ hội đua ghe ngo truyền thống.
- **REF (Khmer)**: វាជាមធ្យោបាយធ្វើជំនួញ ដឹកជញ្ជូនកសិផល ផងដែរជារូបភាពដែលជាប់ទាក់ទងនឹងពិធីបុណ្យប្រណាំងទូកងប្រពៃណី។
- **GPT-4o (Khmer)**: វា​គឺ​ជា​ទាំង​មធ្យោបាយ​ពាណិជ្ជកម្ម និង​ដឹកជញ្ជូន​ផលិតផល​កសិកម្ម ហើយ​ជា​រូបភាព​ដែល​ទាក់ទង​នឹង​ពិធីបុណ្យ​ប្រណាំង​ទូក​ងូរ​ប្រពៃណី។
- **Marker bị đánh rơi**: `boat_racing` | **chrF++**: 33.5
- **Giải thích**: "Ghe ngo" là loại thuyền đặc trưng của Phật giáo Nam tông Khmer ĐBSCL, có tên chuẩn là `ទូកង` (REF dùng đúng). GPT-4o viết `ទូកងូរ` (thêm âm `ូរ`), làm sai tên riêng của một hiện vật văn hoá. Lỗi này nhỏ về ký tự nhưng nặng về ngữ cảnh: nó biến một từ chuyên biệt thành một từ không có trong từ vựng Khmer chuẩn.

#### Mẫu 4 — Self-care / Cách tự chăm sóc

- **Câu tiếng Việt**: Chúng tôi thường thờ cúng Neak Ta, tin rằng vị thần bảo hộ làng sẽ mang lại sức khỏe, may mắn và sự bình an cho mọi người.
- **REF (Khmer)**: ពួកយើងតែងតែបន់ស្រន់ អ្នកតា ជឿថាទេវតាដែលការពារភូមិស្រុកនឹងនាំមកនូវសុខភាពសំណាងល្អនិងសេចក្តីសុខសាន្តដល់មនុស្សគ្រប់គ្នា។
- **GPT-4o (Khmer)**: យើងតែងតែបូជា Neak Ta ដោយជឿថាព្រះដែលការពារភូមិនឹងនាំមកនូវសុខភាព សំណាង និងសន្តិភាពដល់មនុស្សគ្រប់គ្នា។
- **Marker bị đánh rơi**: `krom_religious` | **chrF++**: 40.6
- **Giải thích**: `អ្នកតា` (Neak Ta) là tên thần bảo hộ làng trong tín ngưỡng Khmer Nam Bộ, REF dùng đúng chữ Khmer. GPT-4o lại **giữ nguyên phiên âm Latin** `Neak Ta` trong một câu tiếng Khmer — nghĩa là nó không nhận ra đây vốn là thuật ngữ Khmer, chỉ coi đó là tên riêng nước ngoài. Đây là lỗi nặng vì độ tinh khiết chữ viết (Khmer thuần) bị phá.

#### Mẫu 5 — Society & neighbours / Mối quan hệ với xã hội/hàng xóm

- **Câu tiếng Việt**: Có chứ chị. Dịp lễ Sen Dolta hay Ok Om Bok, cả xóm tụ tập nấu ăn, múa hát, thăm hỏi và thắp hương ông bà tổ tiên.
- **REF (Khmer)**: មានតើបងស្រី។ ក្នុងឱកាសសែនដូនតា ឬអកអំបុក អ្នកទាំងក្នុងភូមិមូលប្រមូលផ្តុំគ្នាធ្វើម្ហូបស៊ី រាំ ច្រៀង សួរសុខទុក្ខ និងអុជធូបដូនតា។
- **GPT-4o (Khmer)**: មានចាសបង។ ក្នុងឱកាសបុណ្យសែនដុលតា ឬអុកអុំបុក សហគមន៍ទាំងមូលប្រមូលផ្តុំគ្នាធ្វើម្ហូប, រាំច្រៀង, សួរសុខទុក្ខ និងបួងសួងដល់បុព្វបុរស។
- **Marker bị đánh rơi**: `food_krom`, `festival_krom` | **chrF++**: 40.5
- **Giải thích**: Hai lễ hội Khmer Nam Bộ có tên chuẩn trong cộng đồng: `សែនដូនតា` (Sen Dolta) và `អកអំបុក` (Ok Om Bok). GPT-4o viết sai thành `សែនដុលតា` và `អុកអុំបុក` — chuyển phiên âm gần với cách đọc tiếng Việt hơn là cách viết đã định hình trong cộng đồng Khmer. `អកអំបុក` có gốc từ `អក` (vỗ) + `អំបុក` (cốm dẹp) và mô tả chính nghi lễ, còn `អុកអុំបុក` của GPT không có nghĩa rõ.

#### Mẫu 6 — Art at events / Biểu diễn nghệ thuật tại một số sự kiện nhất định

- **Câu tiếng Việt**: Người phỏng vấn: Vậy hình thức sân khấu có được tổ chức trong dịp lễ Sen Dolta không?
- **REF (Khmer)**: អ្នកសម្ភាសន៍: អញ្ចឹង តើទម្រង់ល្ខោនត្រូវបានរៀបចំក្នុងឱកាសបុណ្យសែនដូនតាដែរឬទេ?
- **GPT-4o (Khmer)**: អ្នកសម្ភាសៈ តើរបៀបសម្តែងលើឆាកត្រូវបានរៀបចំក្នុងឱកាសបុណ្យសែនដុលតាឬទេ?
- **Marker bị đánh rơi**: `festival_krom` | **chrF++**: 45.2
- **Giải thích**: Lặp lại lỗi Sen Dolta: REF `សែនដូនតា`, HYP `សែនដុលតា`. Lỗi xuất hiện lặp lại nhiều lần cho thấy GPT-4o không thuộc cách viết chuẩn của tên lễ hội này, thay vào đó phiên âm lại từ tiếng Việt một cách sai lệch.

#### Mẫu 7 — Game types / Các loại trò chơi

- **Câu tiếng Việt**: Chủ yếu vào các lễ hội lớn như Chol Chnam Thmay hay Ok Om Bok, khi mọi người rảnh rỗi và cùng vui chơi tập thể.
- **REF (Khmer)**: ភាគច្រើនគឺក្នុងពិធីបុណ្យធំៗ ដូចជា ពិធីបុណ្យចូលឆ្នាំថ្មី ឬ ពិធីបុណ្យអកអំបុក នៅពេលដែលមនុស្សគ្រប់គ្នារួចរាល់ ហើយរីករាយលេងជាមួយគ្នាយ៉ាងសមូហភាព។
- **GPT-4o (Khmer)**: ជាធម្មតានៅពេលពិធីបុណ្យធំៗដូចជា ចូលឆ្នាំថ្មីឬអុកអុំបុក ដែលជាពេលដែលមនុស្សទាំងអស់មានពេលទំនេរនិងរីករាយជាក្រុម។
- **Marker bị đánh rơi**: `food_krom`, `festival_krom` | **chrF++**: 28.7
- **Giải thích**: REF dùng `ពិធីបុណ្យអកអំបុក` (Ok Om Bok). GPT-4o bỏ chữ `ពិធីបុណ្យ` (lễ hội) và viết `អុកអុំបុក` — vừa rút ngắn vừa phiên âm sai. Với các cộng đồng Khmer ở Sóc Trăng, Trà Vinh, Bạc Liêu, Ok Om Bok là lễ hội trung tâm năm; dạng của GPT-4o làm nó trông như một tên nước ngoài lạ.

#### Mẫu 8 — Folk songs / Dân ca

- **Câu tiếng Việt**: Anh có thể chia sẻ vai trò của dân ca trong đời sống tinh thần và văn hóa cộng đồng Khmer Nam Bộ không?
- **REF (Khmer)**: បងអាចចែករំលែកតួនាទីរបស់ចម្រៀងប្រជាប្រិយក្នុងជីវិតស្មារតី និងវប្បធម៌សហគមន៍ខ្មែរណាមបូបានទេ?
- **GPT-4o (Khmer)**: តើបងអាចចែករំលែកពីតួនាទីរបស់បទចម្រៀងប្រជាប្រិយក្នុងជីវិតផ្លូវចិត្តនិងវប្បធម៌សហគមន៍ខ្មែរនៅតំបន់ខាងត្បូងបានទេ?
- **Marker bị đánh rơi**: `krom_ethno_label`, `nam_bo_vn_translit` | **chrF++**: 58.9
- **Giải thích**: REF dùng `សហគមន៍ខ្មែរណាមបូ` — phiên âm trực tiếp "Khmer Nam Bộ" vào chữ Khmer, là cách cộng đồng dùng để gọi chính mình. GPT-4o thay bằng `សហគមន៍ខ្មែរនៅតំបន់ខាងត្បូង` (Khmer ở miền Nam) — đúng địa lý nhưng không còn là tên gọi cộng đồng. Đây là hiện tượng sụp đổ điển hình: **tên cộng đồng bị kéo xuống thành mô tả địa danh trừu tượng**.

#### Mẫu 9 — Wedding venue / Vị trí tổ chức đám cưới

- **Câu tiếng Việt**: - Ngoài ra, một số nghi thức quan trọng như cúng tổ tiên hoặc lễ buộc chỉ đỏ vào cổ tay được làm trong gian thờ hoặc phòng chính của nhà.
- **REF (Khmer)**: លើសពីនេះ ពិធីសំខាន់ៗមួយចំនួនដូចជា ការសែនដូនតា ឬពិធីចងខ្សែអំបោះពណ៌ក្រហមកដៃ ត្រូវបានអនុវត្តនៅក្នុងអាសនៈទីសក្ការបូជា ឬបន្ទប់សំខាន់នៃផ្ទះ។
- **GPT-4o (Khmer)**: ខ្មែរ: - លើសពីនេះទៅទៀត ពិធីសំខាន់ៗមួយចំនួនដូចជាការបូជា祖先 ឬពិធីចងខ្សែពណ៌ក្រហមនៅកដៃ ត្រូវបានធ្វើឡើងនៅក្នុងបន្ទប់បូជា ឬបន្ទប់មេនៃផ្ទះ។
- **Marker bị đánh rơi**: `festival_krom` | **chrF++**: 44.1
- **Giải thích**: REF dùng `ការសែនដូនតា` (Sen Dolta, nghi lễ cúng tổ tiên Khmer Nam Bộ). GPT-4o dịch thành `ការបូជា祖先` — **ghép tiếng Khmer `បូជា` với chữ Hán `祖先`**. Đây là lỗi ô nhiễm chữ viết rất nặng: bản dịch Khmer chứa chữ Hán, chứng tỏ model lấy khái niệm từ vùng tri thức tiếng Trung chứ không từ văn hoá Khmer.

#### Mẫu 10 — Wedding cuisine / Ẩm thực đám cưới

- **Câu tiếng Việt**: - Một trong những món không thể thiếu là bún nước lèo, được nấu từ cá lóc, sả, nghệ và mắm bò hóc đặc trưng.
- **REF (Khmer)**: មុខម្ហូបមួយមុខដែលមិនអាចខ្វះបានគឺ នំបញ្ចុកទឹកសម្លរ បានចម្អិនពីត្រីរ៉ស់ ស្លឹកគ្រៃ រមៀត និងមាំប្រហុក។
- **GPT-4o (Khmer)**: - មួយក្នុងចំណោមម្ហូបដែលមិនអាចខ្វះបានគឺគុយទាវទឹកល្អក់ ដែលចម្អិនពីត្រីស្រឡៅ ស្លឹកគ្រៃ រមៀត និងប្រហុកដ៏លក្ខណៈពិសេស។
- **Marker bị đánh rơi**: `food_krom` | **chrF++**: 46.1
- **Giải thích**: REF giữ tên cộng đồng cho các món ăn đặc trưng: `នំបញ្ចុកទឹកសម្ល` (bún nước lèo Khmer) và `ម៉ាំប្រហុក` (mắm bò hóc — `ម៉ាំ` là phiên âm Việt, nối với `ប្រហុក` prahok). GPT-4o dịch thành `គុយទាវ` (hủ tiếu — **sai món hoàn toàn**) + `ទឹកល្អក់` (nước đục — không phải tên món), và giản lược `ម៉ាំប្រហុក` thành `ប្រហុក` generic. Mất cả tên món đặc thù Nam Bộ lẫn dạng phiên âm Việt hoá.

#### Mẫu 11 — Mystical beliefs / Những điều huyền bí

- **Câu tiếng Việt**: Người Khmer: Neak Tà là vị thần cai quản đất đai, làng xóm, người dân tin rằng phải cúng bái để được che chở, mùa màng thuận lợi.
- **REF (Khmer)**: ជនជាតិខ្មែរ: អ្នកតា គឺ​ជា​ទេវតា​ដែល​គ្រប់គ្រង​ដីធ្លី និង​ភូមិ​ស្រុក, ប្រជាជន​ជឿថា​ត្រូវ​តែ​បន់ស្រន់​បូជា​ដើម្បី​បាន​ការ​ថែរក្សា និង​ការ​បង្កបង្កើន​ផល​បាន​ល្អ។
- **GPT-4o (Khmer)**: អ្នកខ្មែរ៖ នាគតា គឺជាទេវតាដែលគ្រប់គ្រងដីធ្លី ភូមិឃុំ ប្រជាជនជឿថាត្រូវធ្វើពិធីបូជា ដើម្បីទទួលបានការពារនិងសំណាងល្អក្នុងការដាំដុះ។
- **Marker bị đánh rơi**: `krom_religious` | **chrF++**: 22.7
- **Giải thích**: REF: `អ្នកតា` (Neak Ta, thần bảo hộ làng Khmer Nam Bộ). GPT-4o viết `នាគតា` — tức `នាគ` (rồng/nāga) + `តា` (ông). Đây là **ảo giác nghĩa** (semantic hallucination): GPT tạo ra một từ nghe có cấu trúc hợp lý nhưng không tồn tại trong tín ngưỡng Khmer. Từ này không nói gì về thần bảo hộ làng.

#### Mẫu 12 — When death occurs / Khi có người mất

- **Câu tiếng Việt**: Thay vào đó, người thân tập trung đọc kinh, làm lễ bái Tam bảo, dưới sự hướng dẫn của Achar lễ và Achar duki để người khuất được nhẹ nhàng ra đi một cách thanh thản.
- **REF (Khmer)**: ផ្ទុយទៅវិញ ញាតិសន្ដាន ផ្ដំគ្នាសូត្រធម៌ នមស្ការព្រះរតនត្រ័យ ក្រោមការដឹកនាំរបស់លោកអាចារ្យនិង លោកអាចារ្យយុគីដើម្បីឱ្យអ្នកស្លាប់បានលាចាកលោកដោយស្ងប់ស្ងាត់។
- **GPT-4o (Khmer)**: ជំនួសវិញ គ្រួសារប្រមូលផ្តុំអានសូត្រ ធ្វើពិធីបួងសួងត្រាំបាវ ក្រោមការណែនាំរបស់អាចារ្យលិ និងអាចារ្យដូគី ដើម្បីឱ្យអ្នកស្លាប់បានចាកចេញដោយស្ងប់ស្ងាត់។
- **Marker bị đánh rơi**: `nam_bo_vn_translit` | **chrF++**: 34.8
- **Giải thích**: `អាចារ្យយុគី` (Achar duki) là chức sắc trợ lễ cho nhà sư trong Phật giáo Nam tông Khmer ĐBSCL. GPT-4o viết `អាចារ្យដូគី` — phiên âm gần với cách đọc tiếng Việt "duki" hơn là cách viết đã định hình trong cộng đồng Khmer. Cũng có thể GPT không phân biệt được vai trò Achar lễ (`អាចារ្យ`) và Achar duki (`អាចារ្យយុគី`) là hai chức vụ khác nhau.

#### Mẫu 13 — Evening activities / Hoạt động buổi tối

- **Câu tiếng Việt**: Đúng vậy, lễ cúng trăng trong dịp Ok Om Bok diễn ra ban đêm, mọi người dâng cốm dẹp, trái cây để tạ ơn thần mặt trăng.
- **REF (Khmer)**: ត្រឹមត្រូវហើយ ពិធីបុណ្យសំពះព្រះខែ ក្នុងឱកាសបុណ្យអកអំបុក ប្រព្រឹត្តទៅនៅពេលយប់ មនុស្សគ្រប់គ្នាថ្វាយអំបុក ផ្លែឈើ ដើម្បីតបស្នងគុណព្រះច័ន្ទ។
- **GPT-4o (Khmer)**: មែនហើយ ពិធីបួងសួងព្រះច័ន្ទក្នុងឱកអុំបុកធ្វើឡើងនៅពេលយប់ មនុស្សទាំងអស់នាំគ្នាដាក់អំពៅស្ងោរ និងផ្លែឈើដើម្បីថ្លែងអំណរគុណចំពោះព្រះច័ន្ទ។
- **Marker bị đánh rơi**: `food_krom`, `festival_krom` | **chrF++**: 30.4
- **Giải thích**: Lặp cả hai pattern: (1) `អកអំបុក` → `អុកអុំបុក` (sai Ok Om Bok); (2) `អំបុក` → `អំពៅស្ងោរ` — GPT-4o dịch "cốm dẹp" thành "mía luộc" (!) Đây là **ảo giác nghĩa nghiêm trọng**: cốm dẹp (làm từ lúa) bị thay bằng mía — hai loại nguyên liệu hoàn toàn khác nhau.

#### Mẫu 14 — Pre-holiday customs / Những phong tục trước ngày lễ tôn giáo

- **Câu tiếng Việt**: Chúng tôi thường cùng nhau gói bánh truyền thống như bánh tét, bánh ít, vừa để dâng chùa vừa để chia cho họ hàng.
- **REF (Khmer)**: យើងខ្ញុំតែង វេចនំប្រពៃណី ដូចជានំអន្សមជ្រូក នំគម សម្រាប់យកទៅប្រគេនវត្តផង និងចែកជូនសាច់ញាតិផង។
- **GPT-4o (Khmer)**: យើងតែងតែរួមគ្នាដើម្បីច្របាច់នំប្រពៃណីដូចជានំតេត និងនំអិត ទាំងសម្រាប់បួងសួងនៅវត្តទាំងសម្រាប់ចែកជូនសាច់ញាតិ។
- **Marker bị đánh rơi**: `food_krom` | **chrF++**: 33.4
- **Giải thích**: REF `នំអន្សមជ្រូក នំគម` (bánh tét nhân thịt lợn, bánh ít). GPT-4o `នំតេត និងនំអិត` — phiên âm trực tiếp từ "tét" và "ít" tiếng Việt, không biết rằng hai loại bánh này đã có tên Khmer riêng đã lưu truyền trong cộng đồng Khmer Nam Bộ hàng trăm năm.

#### Mẫu 15 — Immediate family relationships / Mối quan hệ trong gia đình chính

- **Câu tiếng Việt**: Người Khmer: Nếu đối với người Khmer Nam bộ thì có sự khác biệt, và do họ sống cùng với người Kinh nên cách gọi sẽ như thế này, đối với ông bên cha thì sẽ gọi là “Ta Nội”, bà bên cha gọi là “Yey Nội”, còn ông bà bên mẹ cũng vậy cũng sẽ gọi như thế, ông ngoại sẽ là “Ta Ngoại”, bà ngoại sẽ là “Yey Ngoại”. Nhưng thực chất thì giữa ông bà nội ngoại không có gì khác biệt đều gọi chung là “Ta” hoặc “Yey”
- **REF (Khmer)**: ជនជាតិខ្មែរ៖ ចំពោះជនជាតិខ្មែណាមបូមានលក្ខណៈខុសប្លែកគ្នា ដោយសារពួកគាត់រស់នៅលាយឡំជាមួយជនជាតិគិញ ដូច្នេះរបៀបហៅក៏មានភាពខុសគ្នាដែរ។ ចំពោះជីតាខាងឪពុក គឺហៅថា “តា Nội” ជីដូនខាងឪពុកហៅថា “យាយ Nội” រីឯជីតាខាងម្ដាយ និងជីដូនខាងម្ដាយក៏ហៅដូចគ្នាដែរ គឺជីតាខាងម្ដាយហៅថា “តា Ngoại” ជីដូនខាងម្ដាយហៅថា “យាយ Ngoại”។ ប៉ុន្តែតាមពិត រវាងជីតាខាងឪពុក និងជីតាខាងម្ដាយមិនមានអ្វីខុសប្លែកគ្នាទេ គឺហៅជារួមថា “តា” ឬ “យាយ”។
- **GPT-4o (Khmer)**: ជនជាតិខ្មែរ: ប្រសិនបើសម្រាប់ជនជាតិខ្មែរនៅតំបន់ខាងត្បូងវិញ វាមានភាពខុសគ្នា ហើយដោយសារតែពួកគេរស់នៅជាមួយជនជាតិវៀតណាម ដូច្នេះការហៅនឹងមានលក្ខណៈដូចខាងក្រោម៖ សម្រាប់តា​ខាងឪពុក នឹងហៅថា "តាណៃ" យាយខាងឪពុក នឹងហៅថា "យាយណៃ" ចំណែកតា និងយាយខាងម្ដាយក៏ដូចគ្នា ដោយតាខាងម្ដាយ នឹងហៅថា "តាណៃ" និងយាយខាងម្ដាយ នឹងហៅថា "យាយណៃ"។ ប៉ុន្តែនៅក្នុងការពិត វាមិនមានភាពខុសគ្នារវាងតា និងយាយខាងឪពុក ឬម្ដាយទេ ពួកគេតែងតែហៅសរុបថា "តា" ឬ "យាយ"។
- **Marker bị đánh rơi**: `ethnonym_kinh`, `nam_bo_vn_translit` | **chrF++**: 30.6
- **Giải thích**: Nhiều lỗi nặng trong một câu: (1) REF dùng `ខ្មែណាមបូ` và `ជនជាតិគិញ` (Khmer Nam Bộ và người Kinh); HYP thay bằng `ខ្មែរនៅតំបន់ខាងត្បូង` và `ជនជាតិវៀតណាម` — kéo cả hai ethnonym cộng đồng về dạng địa lý/quốc gia trừu tượng. (2) Về xưng hô ông bà, REF giữ lai ghép `តា Nội`, `យាយ Ngoại` (mang nguyên các từ Việt "Nội", "Ngoại" trong bản Khmer — đặc trưng code-switching Krom). GPT-4o phiên âm sai thành `តាណៃ` và `យាយណៃ`, tức là nó bịa ra một phiên âm không tồn tại, cũng xoá cả sự phân biệt nội/ngoại.

#### Mẫu 16 — Parent–adult-child interactions / Tương tác giữa cha mẹ và con cái khi trưởng thành

- **Câu tiếng Việt**: Dạ, dù con cái đã lớn và lập gia đình, người Khmer vẫn giữ truyền thống yêu thương, tôn trọng và gắn bó chặt chẽ với cha mẹ.
- **REF (Khmer)**: ចាស ទោះបីកូនធំពេញវ័យ និងមានគ្រួសារក៏ដោយ ក៏ខ្មែរនៅតែរក្សាទំនៀមទំលាប់នៃការស្រលាញ់ គោរព និងរាប់អានយ៉ាងជិតស្និទ្ធជាមួយឪពុកម្តាយ។
- **GPT-4o (Khmer)**: បាទ/ចាស, ទោះបីជាកូនៗបានធំធាត់ និងបង្កើតគ្រួសាររួចទៅហើយក៏ដោយ ក៏ប្រជាជនខ្មែរនៅតែរក្សាប្រពៃណីស្រឡាញ់ គោរព និងទាក់ទាញជិតស្និទ្ធជាមួយឪពុកម្តាយ។
- **Marker bị đánh rơi**: `toponym_krom` | **chrF++**: 40.9
- **Giải thích**: **Đây có thể là false positive của heuristic**: pattern `អានយ៉ាង` (tên Khmer của An Giang) vô tình trùng với chuỗi con trong `រាប់អានយ៉ាងជិត` (tôn trọng rất gần gũi). REF không thực sự nói về địa danh An Giang, mà dùng cụm ngữ pháp `រាប់អាន`. Cần native reviewer loại bỏ trường hợp này khỏi bảng chính thức.

#### Mẫu 17 — Lifestyle / Lối sống

- **Câu tiếng Việt**: Anh có thể chia sẻ một vài nét khái quát về lối sống của cộng đồng Khmer ở Nam Bộ hiện nay không?
- **REF (Khmer)**: បងអាចចែករំលែកទិដ្ឋភាពទូទៅខ្លះ អំពីរបៀបរស់នៅរបស់សហគមន៍ខ្មែរណាមបូបច្ចុប្បន្នបានទេ?
- **GPT-4o (Khmer)**: តើបងអាចចែករំលែកពីលក្ខណៈសង្ខេបមួយចំនួនអំពីរបៀបរស់នៅរបស់សហគមន៍ខ្មែរនៅតំបន់នាគប្បូរបច្ចុប្បន្នបានទេ?
- **Marker bị đánh rơi**: `krom_ethno_label`, `nam_bo_vn_translit` | **chrF++**: 53.8
- **Giải thích**: REF dùng `ខ្មែរណាមបូ` (Khmer Nam Bộ, phiên âm Việt vào chữ Khmer). GPT-4o tạo ra `ខ្មែរនៅតំបន់នាគប្បូរ` — từ `នាគប្បូរ` không tồn tại trong tiếng Khmer, nó là **ảo giác** mà model tự đặt khi không biết "Nam Bộ". So với việc thay bằng `តំបន់ខាងត្បូង` (miền Nam) đã thấy ở mẫu khác, lần này nặng hơn vì bịa ra từ vô nghĩa.

#### Mẫu 18 — Harvesting / Thu hoạch

- **Câu tiếng Việt**: Người Khmer: Chính xác, cốm dẹp tượng trưng cho thành quả lao động, vừa ngon miệng vừa nhắc nhở thế hệ trẻ trân trọng hạt gạo quê hương.
- **REF (Khmer)**: ជនជាតិខ្មែរ៖ ពិតប្រាកដណាស់ អំបុកគឺជានិមិត្តរូបនៃសមិទ្ធផលពលកម្ម ទាំងឆ្ងាញ់ពិសារ ទាំងរំលឹកដល់យុវជនឱ្យចេះឱ្យតម្លៃគ្រាប់អង្ករនៃមាតុភូមិ។
- **GPT-4o (Khmer)**: ជនជាតិខ្មែរ៖ ត្រឹមត្រូវ កុមដេបតំណាងឱ្យលទ្ធផលនៃការប្រឹងប្រែងការងារ ដែលទាំងឆ្ងាញ់ទាំងរំលឹកដល់ជំនាន់ក្មេងឱ្យគោរពស្រូវអង្កររបស់ស្រុកកំណើត។
- **Marker bị đánh rơi**: `food_krom` | **chrF++**: 28.8
- **Giải thích**: REF: `អំបុក` — tên Khmer chuẩn cho "cốm dẹp", món ăn lễ hội Ok Om Bok của Khmer Nam Bộ. GPT-4o viết `កុមដេប` — phiên âm trực tiếp từ tiếng Việt "cốm dẹp" mà không biết đã có tên Khmer tồn tại. Kết quả là một từ không có trong từ vựng Khmer.

#### Mẫu 19 — Traditional ceremonies / Nghi lễ truyền thống

- **Câu tiếng Việt**: Người phỏng vấn: Còn lễ hội Ok Om Bok dâng cúng trăng, thường gắn với hoạt động đua ghe ngo, thì được cộng đồng Khmer tổ chức ra sao?
- **REF (Khmer)**: អ្នកសម្ភាសន៍៖ ពិធីបុណ្យអកអំបុក ថ្វាយព្រះខែ ដែលតែងតែជាប់ទាក់ទងនឹងប្រណាំងទូកង តើសហគមន៍ខ្មែរប្រារព្ធធ្វើដូចម្តេច?
- **GPT-4o (Khmer)**: អ្នកសម្ភាសៈ ចំពោះពិធីបុណ្យ Ok Om Bok ដែលបូជា​ព្រះច័ន្ទ និងភ្ជាប់ជាមួយសកម្មភាពប្រណាំងទូកងូ តើសហគមន៍ខ្មែររៀបចំយ៉ាងដូចម្តេច?
- **Marker bị đánh rơi**: `food_krom`, `festival_krom` | **chrF++**: 35.2
- **Giải thích**: Hai lỗi cùng câu: (1) tên lễ hội Ok Om Bok — REF `អកអំបុក`, HYP giữ `Ok Om Bok` bằng chữ Latin trong bản Khmer; (2) "ghe ngo" — REF `ទូកង`, HYP `ទូកងូ` (thiếu ký tự). Một câu ngắn mất cả tên lễ hội lẫn tên hiện vật văn hoá trung tâm.

#### Mẫu 20 — Holiday preparation customs / Những phong tục chuẩn bị cho ngày lễ tôn giáo

- **Câu tiếng Việt**: Lễ vật thường có gạo, trái cây, bánh truyền thống như bánh tét, bánh ít, cùng hoa và nhang, thể hiện lòng biết ơn thành kính.
- **REF (Khmer)**: ចង្ហាន់បច្ច័យជាទូទៅមានអង្ករ ផ្លែឈើ នំប្រពៃណីដូចជានំអន្សម នំគម ព្រមទាំងផ្កា និងធូប ដើម្បីបង្ហាញនូវសេចក្តីគោរពដឹងគុណ។
- **GPT-4o (Khmer)**: សក្ការៈធម្មតាមានអង្ករ ផ្លែឈើ នំប្រពៃណីដូចជានំតេត នំអិត រួមទាំងផ្កា និងធូប ដើម្បីបង្ហាញការដឹងគុណដោយក្តីគោរព។
- **Marker bị đánh rơi**: `food_krom` | **chrF++**: 49.1
- **Giải thích**: REF dùng `នំអន្សម` (Num Ansom, tức bánh tét Khmer) và `នំគម` (Num Kom, tức bánh ít). GPT-4o viết `នំតេត` và `នំអិត` — tức là **phiên âm trực tiếp từ tiếng Việt "tét" và "ít"** mà không biết mỗi món bánh này đã có tên Khmer riêng. Về mặt nghĩa đen thì người đọc Khmer Nam Bộ có thể đoán được, nhưng về mặt tên chuẩn thì sai hoàn toàn.

#### Mẫu 21 — Leisure activities / Hoạt động giải trí

- **Câu tiếng Việt**: Đua ghe Ngo diễn ra vào dịp Ok Om Bok, ghe dài hàng chục mét, hàng chục tay chèo phối hợp nhịp nhàng đầy khí thế.
- **REF (Khmer)**: ការប្រណាំងទូកងធ្វើឡើងក្នុងឱកាសអកអំបុក ។ ទូកងមានប្រវែងរាប់សិបម៉ែត្រ ជាមួយអ្នកចែវរាប់សិបនាក់ដែលសម្របសម្រួលគ្នាយ៉ាងចុះសម្រុងពោរពេញដោយថាមពល។
- **GPT-4o (Khmer)**: ការប្រណាំងទូកងូរ​ត្រូវបានរៀបចំឡើងក្នុងឱកាសអុកអុំបុក។ ទូកមានប្រវែងជាងដប់ម៉ែត្រ ហើយមានអ្នកចែវជាច្រើននាក់សហការគ្នាដោយស្មោះស្ម័គ្រដើម្បីបង្ហាញស្មារតីដ៏រឹងមាំ។
- **Marker bị đánh rơi**: `food_krom`, `festival_krom` | **chrF++**: 31.2
- **Giải thích**: Ba lỗi trong một câu: (1) `ទូកង` → `ទូកងូរ` (sai tên ghe ngo); (2) `អកអំបុក` → `អុកអុំបុក` (sai tên Ok Om Bok); (3) GPT-4o còn dịch chi tiết số đo: REF `រាប់សិបម៉ែត្រ` (hàng chục mét) → HYP `ជាងដប់ម៉ែត្រ` (hơn mười mét) — đổi nghĩa số lượng. Câu này là ví dụ gọn của việc mất sạch lớp 2 khi dịch cảnh văn hoá lễ hội.

#### Mẫu 22 — Livestock & aquaculture care / Truyền thống chăm sóc vật nuôi/thủy sản

- **Câu tiếng Việt**: Anh có thể chia sẻ về những truyền thống chăm sóc vật nuôi và thủy sản của đồng bào Khmer ở Nam Bộ không?
- **REF (Khmer)**: តើបងអាចចែករំលែកអំពីប្រពៃណីនៃការថែទាំសត្វពាហនៈ និងផលត្រីទឹកសាបរបស់បងប្អូនខ្មែរណាមបូ បានទេ?
- **GPT-4o (Khmer)**: តើអ្នកអាចចែករំលែកអំពីប្រពៃណីក្នុងការថែទាំសត្វចិញ្ចឹម និងសត្វទឹករបស់បងប្អូនខ្មែរនៅតំបន់នាគរបត់បានទេ?
- **Marker bị đánh rơi**: `krom_ethno_label`, `nam_bo_vn_translit` | **chrF++**: 46.9
- **Giải thích**: REF dùng `បងប្អូនខ្មែរណាមបូ` (bà con Khmer Nam Bộ). GPT-4o tạo `បងប្អូនខ្មែរនៅតំបន់នាគរបត់` — `នាគរបត់` là từ bịa, không có trong tiếng Khmer. Đây lại là **ảo giác nghĩa** theo đúng pattern: khi gặp "Nam Bộ" GPT-4o không biết phiên âm đúng nên tạo ra các biến thể ngẫu nhiên nghe có cấu trúc Khmer nhưng vô nghĩa.

#### Mẫu 23 — Groom wedding attire / Trang phục cưới hỏi nam

- **Câu tiếng Việt**: - Chúng tôi thường mặc sampot chang kben, là loại váy quấn truyền thống, kết hợp với áo dài tay được thêu hoa văn tinh xảo.
- **REF (Khmer)**: យើងខ្ញុំតែងតែស្លៀកសំពត់ចងក្បិន ជាស្លៀកពាក់សំពត់ខ្លីបែបប្រពៃណី រួមនឹងអាវដៃវែងដែលមានប៉ាក់យ៉ាងប្រណិត។
- **GPT-4o (Khmer)**: - ពួកយើងជាញឹកញាប់ស្លៀកសំពត់ចងក្បិន ដែលជាប្រភេទសំពត់បុរាណ រួមផ្សំជាមួយអាវដៃវែងដែលមានការច្នៃប្រឌិតលំអដោយលំនាំផ្កាដ៏ល្អឯក។
- **Marker bị đánh rơi**: `kinship_colloq` | **chrF++**: 29.0
- **Giải thích**: **Đây có thể là false positive của heuristic**: pattern `ម៉ែ` (mẹ, xưng hô Krom) trùng với substring trong các từ như `ព្យាយាម` hoặc các tiếng có chứa chuỗi này. Nội dung mẫu nói về trang phục cưới (sampot chang kben), không có xưng hô gia đình. Cần native reviewer xác nhận lại.

#### Mẫu 24 — Musical instruments / Nhạc cụ

- **Câu tiếng Việt**: Anh có thể chia sẻ về vai trò của nhạc cụ trong đời sống văn hóa và tinh thần của người Khmer Nam Bộ không?
- **REF (Khmer)**: តើបងអាចរៀបរាប់អំពីតួនាទីរបស់ឧបករណ៍តន្ត្រីនៅក្នុងជីវភាពវប្បធម៌ និងស្មារតីរបស់ជនជាតិខ្មែរណាមបូ បានទេ?
- **GPT-4o (Khmer)**: តើអ្នកអាចចែករំលែកអំពីតួនាទីនៃឧបករណ៍ភ្លេងក្នុងជីវិតវប្បធម៌ និងស្មារតីរបស់ប្រជាជនខ្មែរនៅតំបន់ខាងត្បូងបានទេ?
- **Marker bị đánh rơi**: `krom_ethno_label`, `nam_bo_vn_translit` | **chrF++**: 40.3
- **Giải thích**: REF dùng `ខ្មែរណាមបូ` (Khmer Nam Bộ). GPT-4o thay bằng `ខ្មែរនៅតំបន់ខាងត្បូង` (Khmer ở miền Nam địa lý). Pattern giống mẫu dân ca: tên cộng đồng bị kéo xuống thành mô tả địa danh trừu tượng, đánh mất bản sắc định danh cộng đồng.

#### Mẫu 25 — Bride wedding attire / Trang phục cưới hỏi nữ

- **Câu tiếng Việt**: - Mỗi bộ trang phục đều có màu sắc và phụ kiện riêng, phù hợp với không khí từng phần như lễ rước dâu, buộc chỉ cổ tay, cúng tổ tiên.
- **REF (Khmer)**: ឈុតសំលៀកបំពាក់នីមួយៗមានពណ៌ និងគ្រឿងប្រើប្រាស់រៀងៗខ្លួន សាកសម សម្រាប់បរិយាកាសនីមួយៗ ដូចជា ពិធីដង្ហែអាពាហ៍ពិពាហ៍ ចងខ្សែ អំបោះពណ៌ក្រហមកដៃ និងការថ្វាយសែនដូនតាជាដើម។
- **GPT-4o (Khmer)**: - រាល់សំលៀកបំពាក់នីមួយៗសុទ្ធតែមានពណ៌ស និងគ្រឿងបន្លាស់ផ្ទាល់ខ្លួន ដែលសមស្របនឹងបរិយាកាសនៃពិធីនីមួយៗ ដូចជាពិធីទទួលកូនស្រី, ចងខ្សែដៃ, និងបូជាបុព្វបុរស។
- **Marker bị đánh rơi**: `festival_krom` | **chrF++**: 30.6
- **Giải thích**: REF dùng `ការថ្វាយសែនដូនតា` (lễ cúng tổ tiên Sen Dolta). GPT-4o dịch thành `បូជាបុព្វបុរស` (cúng tổ tiên — phiên bản Pali-Sanskrit trừu tượng). Tuy đúng nghĩa nhưng mất tên riêng lễ `សែនដូនតា` mà cộng đồng Khmer Nam Bộ dùng làm danh pháp nghi lễ chính thức.



---

## 5. Ghi chú phương pháp

- Heuristic marker Khmer-Việt / Khmer Krom được liệt kê trong
  `experiments/analysis/build_report_data.py`. Danh sách này là **sàn**,
  chưa phủ hết mọi biến thể địa phương. Native reviewer có thể tìm ra
  thêm các trường hợp khác.
- Nhóm "25 mẫu dịch được" chọn ngẫu nhiên phân tầng theo chủ đề, ưu tiên
  mẫu có `chrF++ ≥ 35` và `CuEA = 1.0` hoặc không có thực thể văn hoá nào.
- Nhóm "25 mẫu dịch fail" chọn từ 139 mẫu đã được flag variety collapse,
  phân tầng theo chủ đề để tránh lặp lại.
- Giải thích trong mục 4.2 là phân tích ngôn ngữ học dựa trên so sánh
  REF và HYP. Đây **không phải** đánh giá của người Khmer bản ngữ, mà là
  suy luận từ pattern được nhìn thấy trong dữ liệu. Một số case được
  đánh dấu false positive khi marker khớp nhầm ngữ pháp.
- Con số `CuEA` được giữ để tham chiếu nhưng **không dùng làm chuẩn mực
  đánh giá trong báo cáo này** — độ đo đó sẽ được đề xuất ở phần sau của
  dự án, sau khi cơ sở tri thức văn hoá được xây dựng.
