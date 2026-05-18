# So sánh hiện tượng "đánh rơi Khmer-Việt" giữa 6 hệ thống dịch máy

> Câu hỏi của báo cáo: GPT-4o có phải trường hợp cá biệt, hay tất cả các
> mô hình hiện có đều đánh rơi marker Khmer-Việt theo cùng một cách?
>
> Trả lời ngắn: **Đây là pattern chung, không phải vấn đề riêng của
> GPT-4o**. Trên 5 mô hình khác (Aya-101, NLLB-200-3.3B, Gemma-SEA-LION,
> Llama-SEA-LION, Sailor2), tỉ lệ đánh rơi cao hơn hẳn GPT-4o. Duy nhất
> một mô hình (Llama-SEA-LION) phải loại khỏi phân tích vì output đã vỡ
> hoàn toàn, không sinh ra được Khmer.

## 1. Phương pháp

- Dùng cùng danh sách marker Khmer-Việt như báo cáo `15_bao_cao_3_lop_khmer.md`.
- Cho mỗi mẫu trong 1,856 mẫu benchmark, kiểm tra: (i) REF có chứa marker
  Khmer-Việt không, (ii) output của mô hình có giữ marker đó không.
- Đếm số mẫu mà REF có marker nhưng output đánh rơi → `drop rate`.
- Đồng thời đo "sức khoẻ output" để phân biệt variety collapse thực sự
  với output vỡ: mẫu có ≥ 20 ký tự *và* chứa ít nhất 1 ký tự Khmer
  (U+1780–U+17FF) được tính là "output hợp lệ". Mẫu còn lại là `broken`.

## 2. Bảng so sánh tổng quan

| Mô hình | chrF++ | REF có Krom | Đánh rơi | Drop rate | Output vỡ |
|---|---:|---:|---:|---:|---:|
| **GPT-4o** (Azure) | 40.47 | 181 | 139 | **76.8 %** | 8 |
| Aya-101 | 36.03 | 181 | 170 | **93.9 %** | 5 |
| NLLB-200-3.3B | 34.08 | 181 | 178 | **98.3 %** | 6 |
| Gemma-SEA-LION-9B-IT | 25.10 | 181 | 171 | **94.5 %** | 6 |
| Sailor2-8B | 32.91 | 181 | 157 | **86.7 %** | 33 |
| Llama-SEA-LION-8B-R | 0.06 | 181 | 181 | 100.0 % | **1856** |

### Đọc bảng này thế nào

- Cột `REF có Krom` bằng nhau ở cả 6 mô hình (`181`) vì được tính trên
  cùng tập tham chiếu.
- Cột `Drop rate` cho biết trong 181 mẫu đó, bao nhiêu phần trăm bị
  mô hình dịch thẳng sang Khmer Campuchia chuẩn.
- Cột `Output vỡ` đếm số mẫu mà mô hình **không sinh ra được Khmer**.
  Con số này là bộ lọc an toàn để không nhầm giữa **variety collapse**
  (model biết dịch Khmer nhưng chọn dạng chuẩn) và **output broken**
  (model không dịch được Khmer cho đúng).

### Llama-SEA-LION-8B-R phải loại khỏi phân tích

- `chrF++ = 0.06`, xấp xỉ bằng 0 trên toàn bộ 1,856 mẫu.
- `1856 / 1856 = 100 %` mẫu có output "vỡ" (không có ký tự Khmer hoặc
  quá ngắn). Đã kiểm tra ở báo cáo trước: output chủ yếu là token rác
  lặp đi lặp lại (`Sergeant Sergeant …`, chữ Trung, chữ Latin).
- Drop rate 100 % của nó **không** chứng minh variety collapse. Nó chỉ
  chứng minh mô hình không biết tiếng Khmer. **Không dùng con số này**
  để lập luận cho paper.

### 5 mô hình còn lại đều đánh rơi, nặng hơn GPT-4o

Drop rate ổn định ở mức **77 % – 98 %** bất kể kiến trúc (encoder-decoder
như Aya, NLLB; hay causal LM chỉnh theo chỉ thị như Gemma, Sailor2; hay
mô hình thương mại lớn như GPT-4o).

Chi tiết đáng chú ý:

- **GPT-4o đánh rơi ít nhất** (76.8 %). Nhưng ngay cả mức "tốt nhất"
  này vẫn là tỉ lệ rất cao.
- **NLLB-200-3.3B đánh rơi gần như toàn bộ** (98.3 %). Hợp lý vì
  FLORES và dữ liệu huấn luyện của NLLB cho Khmer đều là Khmer
  Campuchia chuẩn, hoàn toàn không có nguồn Khmer Nam Bộ.
- **Aya-101 và Gemma-SEA-LION đánh rơi ngang nhau** (~94 %). Mặc dù
  SEA-LION được quảng cáo là mô hình "Đông Nam Á", nó vẫn không bảo
  toàn dạng Khmer-Việt của cộng đồng Khmer tại Việt Nam.
- **Sailor2-8B ở giữa** (86.7 %), tốt hơn Aya/Gemma, kém hơn GPT-4o.

## 3. Bảng đánh rơi theo từng loại marker

| Loại marker (category) | GPT-4o | Aya-101 | NLLB | Gemma-SL | Llama-SL* | Sailor2 |
|---|---:|---:|---:|---:|---:|---:|
| `food_krom` (món ăn Khmer-Việt) | 63 | 71 | 74 | 75 | 75 | 65 |
| `festival_krom` (lễ hội Nam Bộ) | 40 | 37 | 42 | 43 | 43 | 35 |
| `kinship_colloq` (xưng hô khẩu ngữ) | 20 | 38 | 39 | 35 | 42 | 38 |
| `boat_racing` (đua ghe ngo) | 5 | 16 | 17 | 12 | 17 | 8 |
| `krom_religious` (thần làng, phum sóc) | 12 | 14 | 15 | 14 | 15 | 13 |
| `nam_bo_vn_translit` (Nam Bộ phiên âm) | 15 | 15 | 15 | 15 | 15 | 15 |
| `krom_ethno_label` (nhãn cộng đồng) | 10 | 10 | 10 | 10 | 10 | 10 |
| `ethnonym_kinh` (người Kinh) | 7 | 12 | 12 | 12 | 12 | 12 |
| `toponym_krom` (địa danh Nam Bộ) | 3 | 6 | 6 | 4 | 6 | 6 |
| `vn_loanword` (từ mượn âm Việt) | 2 | 2 | 2 | 2 | 2 | 2 |

\* Llama-SEA-LION để trong bảng vì chạy cùng pipeline, nhưng các con số
của nó **không có giá trị phân tích** do output vỡ. Xem mục 2.

### Điều quan sát được

1. **Pattern theo nhóm marker giống nhau giữa các mô hình**. Cái món ăn
   Khmer-Việt (`food_krom`) là nơi đánh rơi nặng nhất cho cả 6 mô hình,
   và lần lượt giảm dần đến `vn_loanword` ở đáy. Điều này chỉ ra rằng
   chính các khái niệm văn hoá đặc thù (món ăn, lễ hội, nghi lễ) mới là
   nơi mô hình không biết cách nói bằng hình thức của cộng đồng Khmer
   Nam Bộ.

2. **GPT-4o vượt trội rõ ở ba hạng mục**:
   - `kinship_colloq` (20 so với 35-42): GPT-4o hiểu được chút ít khẩu
     ngữ `ម៉ែ / ប៉ា` hơn các mô hình nhỏ hơn.
   - `boat_racing` (5 so với 8-17): GPT-4o viết được `ទូកង` đúng hơn.
   - `ethnonym_kinh` (7 so với 12): GPT-4o nhận ra `គិញ` là "người Kinh"
     nhiều hơn các mô hình khác.

3. **Ba hạng mục mà mọi mô hình cùng đánh rơi 100 %**:
   `nam_bo_vn_translit`, `krom_ethno_label`, `vn_loanword` có đúng cùng
   một số cho **tất cả 6 mô hình**. Tức là không mô hình nào biết phiên
   âm `ណាមបូ` cho "Nam Bộ", hay giữ `ខ្មែរក្រោម` / `ខ្មែរណាមបូ` như REF
   dùng, hay dùng được các từ mượn âm Việt như `អ៊ុយបាន`. **Đây là một
   bức tường trắng chung** — không có mô hình nào hiện tại có kiến thức
   về tầng Khmer-Việt này.

## 4. Ý nghĩa cho paper

Những con số này chuyển hẳn câu chuyện từ "**GPT-4o không biết Khmer-Việt**"
sang một câu chuyện mạnh hơn và đúng hơn về mặt khoa học:

> Trên cả mô hình thương mại lớn (GPT-4o), mô hình nghiên cứu đa ngữ
> (Aya-101, NLLB), lẫn các mô hình được thiết kế riêng cho Đông Nam Á
> (Sailor2, SEA-LION), **không mô hình nào trong nhóm hiện có bảo toàn
> được hình thức Khmer-Việt khi dịch văn hoá cộng đồng Khmer Nam Bộ**.
> Drop rate dao động từ 77 % đến 98 %. Các loại từ phiên âm Việt
> (`ណាមបូ`), tên gọi cộng đồng (`ខ្មែរក្រោម` / `ខ្មែរណាមបូ`), và từ mượn
> hành chính (`អ៊ុយបាន`) bị đánh rơi **100 %** ở tất cả các mô hình.
> Pattern này nhất quán bất kể kiến trúc mô hình, khiến nó trở thành
> một **lỗ hổng hệ thống** chứ không phải đặc điểm riêng của một mô
> hình nào.

Cái framing này **đứng vững hơn** vì:

1. Nó không còn phụ thuộc vào GPT-4o. Nếu GPT-5 hay model khác tốt hơn
   xuất hiện, bằng chứng vẫn còn giá trị.
2. Nó biến vấn đề thành "thiếu tài nguyên" thay vì "model kém". Đó
   chính là nơi **cơ sở tri thức văn hoá (KB)** có thể can thiệp.
3. Nó justify cho đóng góp của paper: một KB tầng phương ngữ có thể
   thu hẹp lỗ hổng này cho **tất cả các mô hình**, không chỉ GPT-4o.

## 5. Các caveat cần giữ lại khi trích dẫn số

- `181` mẫu là lower bound của "REF có marker Khmer-Việt", dựa trên
  danh sách marker hiện tại. Native reviewer có thể tìm thêm marker →
  số này sẽ tăng. Drop rate có thể thay đổi nhưng không nhiều.
- **Llama-SEA-LION-8B-R bị loại khỏi analysis**. Đừng trích các con số
  của nó ra paper.
- Aya-101 là `aya-101` (encoder-decoder 13B, cũ hơn Aya-23). Không
  giống dòng Aya mới.
- NLLB-200-3.3B là checkpoint Meta open-source, đại diện cho pipeline
  MT đa ngữ truyền thống.
- Các mô hình SEA-LION / Sailor2 được chạy theo instruction template
  mặc định; việc tinh chỉnh prompt có thể thay đổi kết quả, nhưng với
  mức độ chung thì khó có khả năng đảo ngược drop rate 94-98 % xuống
  dưới 50 %.

## 6. Bước tiếp theo đề xuất

1. **Chọn 3 mô hình cho paper**: GPT-4o + Aya-101 + Sailor2 (đại diện
   cho 3 nhóm: commercial, multilingual research, SEA-specific). NLLB
   có thể bổ sung như baseline MT truyền thống.
2. **Chạy lại tất cả các mô hình đó với KB-RAG** (thay vì plain) và
   đo drop rate mới. Nếu KB giảm drop rate trên cả 3 nhóm mô hình →
   đóng góp "KB cứu được variety collapse" vững.
3. **Chọn 5–10 case chung ở cả 6 mô hình** làm minh hoạ qualitative.
   Những case mà mọi mô hình cùng fail là evidence mạnh nhất.

## 7. Tệp kèm theo

- `results/multi_model_variety_compare.json` — dữ liệu đầy đủ cho 6
  mô hình, kèm số đếm theo từng loại marker.
- `experiments/analysis/multi_model_variety_audit.py` — script tái tạo.
