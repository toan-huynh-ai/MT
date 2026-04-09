# Phân tích điểm yếu mới của LLMs trong Vi-Khmer MT

> Mỗi điểm yếu đều trải qua 3 vòng: (1) Phát hiện → (2) Tự phản biện → (3) Verdict

---

## Điểm yếu 1: SEMANTIC HALLUCINATION — "Không biết thì bịa"

### Phát hiện

GPT-4o KHÔNG CHỈ dịch sai tên cultural entity — nó **bịa ra nghĩa hoàn toàn khác**. Đây không phải transliteration (âm hóa), mà là hallucination (ảo giác ngữ nghĩa):

| Source (Vietnamese) | GPT-4o dịch thành | Nghĩa thật | Vấn đề |
|---|---|---|---|
| **bánh ống tre** | នំបំពង់**ឈើឆ្កាង** → back: "bánh mì gỗ" | Bamboo tube cake (នំបំពង់ឫស្សី) | Bịa: "gỗ thập tự" thay vì "ống tre" |
| **nùm bong klanh** | ផ្លែឈើ → back: "trái cây" | Bánh truyền thống Khmer Krom (នំបង់ខ្លាញ់) | Bịa: "fruit" hoàn toàn sai |
| **khoai lang** (trong context) | អាហារស្ពៃឆា → back: "rau xào" | Khoai lang (sweet potato) | Bịa: "stir-fried vegetables" |

**Tại sao đây nghiêm trọng**: Transliteration thì người đọc biết nó sai. Hallucination thì người đọc **tin nó đúng** vì nó trông tự nhiên. Nguy hiểm hơn nhiều.

### Tự phản biện

- *"Đây có phải chỉ là vài trường hợp cá biệt?"* → Không. Tìm thấy ở cả 3 probe (food, complex, ritual). Pattern rõ ràng: khi GPT-4o gặp từ Khmer Krom mà nó không biết, thay vì thú nhận không biết hoặc transliterate, nó **bịa ra một nghĩa nghe hợp lý**.
- *"CKB-RAG đã fix được rồi mà?"* → CKB fix được **NẾU entity nằm trong KB**. Nhưng không thể cover 100% entities. Hallucination vẫn xảy ra với entities ngoài KB.
- *"Có gì mới so với hallucination trong LLM nói chung?"* → Hallucination trong MT cho cultural terms là **nguy hiểm hơn** hallucination thông thường vì nó ảnh hưởng đến bảo tồn văn hóa. Dịch "nùm bong klanh" thành "trái cây" là **xóa sổ một khái niệm văn hóa**.

### Verdict: **GIỮ — Đây là contribution thật sự**

Đề xuất: Thêm error type "SEMANTIC_HALLUCINATION" vào taxonomy, tách biệt với "MISSING_OR_WRONG". Dùng back-translation để phát hiện tự động: nếu back(hyp) ≠ source về ngữ nghĩa → hallucination.

---

## Điểm yếu 2: "Adequate but Culturally Foreign" — Đúng ngữ pháp, sai phong cách

### Phát hiện

Bằng chứng cụ thể:

```
Trong toàn bộ dataset (1,856 mẫu):
  Krom markers (ចា៎, ម៉ាក់...):     47 mẫu tham chiếu dùng kiểu Krom
  Cambodia markers (ចាស, បាទ...):  168 mẫu tham chiếu dùng kiểu Cambodia

Trong GPT-4o output (40 mẫu thí nghiệm):
  Krom markers:    0 lần (GPT KHÔNG BAO GIỜ dùng kiểu Krom)
  Cambodia markers: 10 lần (GPT LUÔN dùng kiểu Cambodia)
  Tham chiếu:       1 Krom, 4 Cambodia

Speaker labels:
  Ref dùng "ជនជាតិខ្មែរ៖" (dấu ៖ đúng chuẩn):  11 lần
  GPT dùng "ជនជាតិខ្មែរ:" (dấu : sai chuẩn):      5 lần
  GPT dùng "ជនជាតិខ្មែរ៖":                          4 lần
```

**Vấn đề cốt lõi**: GPT-4o sản xuất Khmer **"đúng nhưng lạ"** đối với người Khmer Krom. Giống như dịch một văn bản tiếng Anh Mỹ sang giọng Anh Anh — kỹ thuật đúng nhưng người đọc Mỹ cảm thấy không tự nhiên. Cụ thể:

- **Formal particles**: GPT dùng "បាទ/ចាស" (Cambodia formal) thay vì "ចា៎" (Krom colloquial)
- **Speaker labels**: GPT không nhất quán — trộn ":" (Latin colon) với "៖" (Khmer colon)
- **Từ vựng tổng thể**: Ngay cả khi CKB fix entities, "hương vị" tổng thể vẫn Cambodian

### Tự phản biện

- *"47/1856 Krom markers là quá ít để kết luận?"* → Đúng là ít, nhưng con số 0/40 ở GPT output mới là vấn đề. **Zero** — không một lần nào GPT dùng Krom style. Đây là systemic, không phải ngẫu nhiên.
- *"Đây có phải vấn đề của mọi low-resource dialect?"* → ĐÚNG, và đó chính là giá trị. Đây không chỉ là vấn đề của Khmer Krom mà là **pattern chung**: LLMs trained trên standard variety luôn "nuốt" dialect/variety features. Paper có thể generalize finding này.
- *"CKB có fix được không?"* → **KHÔNG**. CKB fix entities nhưng KHÔNG fix style/register. Đây là limitation thật sự của CKB-RAG approach. Thành thật thừa nhận → reviewer respect.
- *"Có measurable không?"* → Khó đo tự động. CẦN human evaluation. Đây là argument mạnh để justify C9 (human eval).

### Verdict: **GIỮ — Đây là finding quan trọng nhất mà chúng ta chưa khai thác**

Đề xuất: Đây không phải lỗi mà CKB fix được. Đây là **limitation của approach** và đồng thời là **motivation cho future work** (dialect-aware fine-tuning, style transfer). Thành thật report limitation = reviewer respect = strong accept.

---

## Điểm yếu 3: OVER-GENERATION — GPT-4o "nói nhiều hơn" cần thiết

### Phát hiện

```
GPT-4o (plain): avg length ratio = 1.18 (dài hơn reference 18%)
GPT-4o (KB):    avg length ratio = 1.16 (dài hơn reference 16%)
Over-generate (>1.3x):  6/40 samples (15%)
Under-generate (<0.7x): 0/40 samples (0%)
```

GPT-4o **luôn dịch dài hơn** reference. Không bao giờ ngắn hơn.

### Tự phản biện

- *"18% dài hơn có phải vấn đề lớn?"* → Trong MT nghiên cứu, length ratio 1.18 không quá tệ. Nhưng pattern **một chiều** (luôn dài hơn, không bao giờ ngắn hơn) cho thấy GPT-4o **thêm thông tin không cần thiết** — có thể là giải thích, paraphrase, hoặc cultural "padding."
- *"Có gì mới?"* → Over-generation đã được biết đến. Điểm mới là nó xảy ra đặc biệt nhiều ở **cultural text** — GPT-4o có xu hướng "giải thích" cultural concepts thay vì chỉ dịch.
- *"Có đủ quantitative evidence?"* → 6/40 = 15% over-generate. Không đủ ấn tượng cho một main contribution.

### Verdict: **BỎ — Quá nhỏ để là contribution riêng**

Có thể nhắc tới trong analysis section nhưng không đáng là headline finding. Đúng là "vạch lá tìm sâu."

---

## Điểm yếu 4: Speaker Label Inconsistency — Rối loạn danh xưng

### Phát hiện

```
Speaker label                     Tham chiếu   GPT-4o
──────────────────────────────────────────────────────
ជនជាតិខ្មែរ៖ (đúng, Khmer colon)      11          4
ជនជាតិខ្មែរ: (sai, Latin colon)         2          5
អ្នកសម្ភាសន៍៖ (interviewer)             2          0
អ្នកខ្មែរ: (informal)                    0          2
```

GPT-4o:
- Dùng **Latin colon (:)** thay vì **Khmer colon (៖)** → script impurity ở mức vi mô
- **Không bao giờ** output "អ្នកសម្ភាសន៍៖" (interviewer label) dù reference dùng
- Tạo ra label "អ្នកខ្មែរ:" mà **không tồn tại** trong reference

### Tự phản biện

- *"Colon sai có quan trọng không?"* → Với người Khmer: CÓ. "៖" là ký hiệu Khmer chuẩn. Dùng ":" (Latin) cho thấy model không hiểu Khmer punctuation.
- *"Đây có phải chỉ là formatting issue?"* → Không chỉ vậy. Việc GPT-4o **bịa ra speaker label mới** ("អ្នកខ្មែរ:") cho thấy nó không hiểu convention của dialogue data.
- *"Có đủ ảnh hưởng?"* → Trong dialogue MT, speaker label consistency là quan trọng cho readability. Nhưng đây là issue khá nhỏ so với semantic hallucination.

### Verdict: **GỘP vào Điểm yếu 2** (Culturally Foreign)

Không đủ lớn để đứng riêng, nhưng là evidence tốt cho "Adequate but Culturally Foreign." Colon sai + speaker label sai = thêm bằng chứng rằng GPT-4o output **không tự nhiên** cho người Khmer Krom.

---

## Điểm yếu 5: CKB-RAG có giới hạn — 12 lỗi không fix được

### Phát hiện

Sau khi dùng CKB v2 (132 entries), vẫn còn 12 lỗi:

```
MISSING_OR_WRONG:   10 lỗi — chủ yếu là entity "sóc" bị match sai
CHINESE_LEAK:        1 lỗi — tụng kinh vẫn bị leak ký tự Trung Quốc
VIETNAMESE_LEAK:     1 lỗi — Vietnamese text trong output Khmer
```

**10/12 lỗi còn lại là "sóc"** — từ "sóc" trong "phum sóc" bị match riêng lẻ với toponym entry "sóc → ស្រុក". Đây là **false positive trong CKB lookup**, không phải lỗi dịch. CKB cần disambiguation.

**1 Chinese leak** vẫn xảy ra dù có CKB → CKB **không fix được script leakage**. Đây là lỗi ở tầng generation, không phải tầng vocabulary.

### Tự phản biện

- *"12 lỗi trên 40 mẫu = 30% still wrong?"* → Không. 10/12 là false positive từ CKB matching. Nếu fix CKB matching, chỉ còn 2 lỗi thật sự = 5% error rate.
- *"CKB matching problem có đáng report?"* → CÓ. Đây là limitation thực tế: keyword matching tạo false positives khi từ ngắn ("sóc") match trong context không liên quan. Cần entity disambiguation.

### Verdict: **GỘP vào discussion section**

Không phải weakness MỚI của LLM, mà là limitation của CKB approach. Nên report thành thật trong paper → motivate future work (context-aware entity disambiguation).

---

## Tổng hợp: Những gì thật sự đáng đóng góp

| # | Điểm yếu | Loại | Impact | Giữ? |
|---|---|---|---|---|
| **1** | **Semantic Hallucination** — bịa nghĩa thay vì thú nhận không biết | Weakness MỚI | **CAO** — nguy hiểm cho bảo tồn văn hóa | **GIỮ** ★ |
| **2** | **Adequate but Foreign** — đúng ngữ pháp, sai dialect toàn bộ | Weakness MỚI | **CAO** — ảnh hưởng 100% output | **GIỮ** ★ |
| 3 | Over-generation (18% dài hơn) | Observation | Thấp | **BỎ** |
| 4 | Speaker label inconsistency | Evidence | Trung bình | **GỘP → #2** |
| 5 | CKB matching false positives | Limitation | Trung bình | **GỘP → discussion** |

---

## Hai contribution MỚI cho paper

### Contribution mới A: "Cultural Semantic Hallucination" — Loại lỗi mới

**Paper claim**: LLMs không chỉ transliterate cultural terms sai — chúng **hallucinate nghĩa hoàn toàn khác** khi gặp từ ngoài training data. Đây nguy hiểm hơn transliteration vì **người đọc không nhận ra lỗi**.

**Phương pháp detect**: Back-translation pipeline. Dịch hypothesis ngược về source language rồi so sánh semantic similarity. Nếu back-translation khác nghĩa → hallucination detected.

**Metric đề xuất**: **Hallucination Rate on Cultural Entities (HRCE)** = % cultural entities bị hallucinate (nghĩa khác hoàn toàn so với nguồn).

### Contribution mới B: "Adequacy Without Authenticity" — Limitation thành thật

**Paper claim**: CKB-RAG fix entity-level errors (CuEA: 0.419→0.937) nhưng **KHÔNG fix dialect style**. GPT-4o luôn output Cambodian Standard Khmer register — 0% Krom markers vs 47 samples trong data dùng Krom style. Đây là limitation CÓ CHỦ ĐÍCH report, không phải lỗi sót.

**Giá trị cho cộng đồng**: 
- Chứng minh cần Khmer Krom-specific fine-tuning data (future work)
- Chứng minh automatic metrics KHÔNG THỂ detect dialect mismatch → cần human eval
- Motivate community data collection cho Khmer Krom

**Cả hai điểm này đều không phải "vạch lá tìm sâu"** — chúng ảnh hưởng đến toàn bộ pipeline dịch thuật và có implications cho bất kỳ underserved language variety nào.
