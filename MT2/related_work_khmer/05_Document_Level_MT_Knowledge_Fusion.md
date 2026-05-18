# Improving LLM-based Document-level Machine Translation with Multi-Knowledge Fusion

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Improving LLM-based Document-level Machine Translation with Multi-Knowledge Fusion |
| **Authors** | Bin Liu, Xinglin Lyu, Junhui Li, Daimeng Wei, Min Zhang, Shimin Tao, Hao Yang |
| **Affiliations** | Soochow University (China) & Huawei Translation Services Center (Beijing) |
| **Year** | 2025 |
| **arXiv** | [2503.12152](https://arxiv.org/abs/2503.12152) |
| **Code** | [github.com/gfvmjcdfg/Mutil_knowledge_fusion](https://github.com/gfvmjcdfg/Mutil_knowledge_fusion) |

---

## 2. Tóm tắt (Abstract)

Các nghiên cứu gần đây về prompting LLM cho dịch máy cấp tài liệu (Document-level Machine Translation - DMT) chủ yếu tập trung vào ngữ cảnh liên câu bằng cách nối toàn bộ tài liệu nguồn thành một chuỗi dài. Cách tiếp cận này chỉ dựa trên trình tự các câu trong tài liệu, trong khi độ phức tạp của chuỗi cấp tài liệu lớn hơn nhiều so với cấp câu, điều này có thể hạn chế khả năng của LLM khi chỉ sử dụng một nguồn tri thức duy nhất.

Paper đề xuất **Multi-Knowledge Fusion (KFMT)** — một phương pháp kết hợp nhiều nguồn tri thức bao gồm **tóm tắt tài liệu (summarization)** và **dịch thực thể (entity translation)** để nâng cao chất lượng dịch. Pipeline gồm 3 bước: (1) trích xuất tri thức, (2) tích hợp từng loại tri thức riêng lẻ để sinh bản dịch, (3) fusion nhiều bản dịch bằng chiến lược reranking cấp câu. Kết quả thực nghiệm trên 8 hướng dịch cho thấy cải thiện trung bình 0.8, 0.6, và 0.4 điểm COMET lần lượt trên LLaMA3-8B, Mistral-Nemo, và GPT-4o-mini.

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Dịch máy cấp tài liệu (DMT) yêu cầu mô hình nắm bắt **phụ thuộc liên câu (inter-sentence dependency)** để giải quyết các vấn đề discourse như:
- Dịch đại từ (pronoun translation)
- Không nhất quán từ vựng giữa các câu (word translation inconsistency)
- Mất mạch lạc (coherence) khi dịch từng câu độc lập

### Tại sao quan trọng?

- Các phương pháp **prompt engineering (PE)** hiện tại cho DMT chỉ sử dụng **một nguồn tri thức duy nhất** — thường là ngữ cảnh liên câu (inter-sentence context) — và điều này không đủ để giải quyết các vấn đề discourse phức tạp.
- Phương pháp **SFT (supervised fine-tuning)** đòi hỏi tài nguyên tính toán lớn để huấn luyện, trong khi PE tiết kiệm hơn nhưng bị giới hạn bởi lượng tri thức đưa vào.
- Dịch giả chuyên nghiệp thường đọc toàn bộ tài liệu trước, nắm chủ đề chính, xác định thực thể quan trọng, rồi mới dịch — LLM hiện tại chưa mô phỏng được quy trình này.

### Analogy với dịch giả chuyên nghiệp

Paper lấy cảm hứng từ cách dịch giả thực tế làm việc (Figure 1):
1. **Đọc hiểu tổng quan** → tương đương với **summarization**
2. **Đánh dấu thực thể quan trọng** → tương đương với **entity translation**
3. **Dịch có tri thức bổ trợ** → tương đương với **knowledge-integrated translation**

---

## 4. Phương pháp đề xuất (Proposed Method)

### Tổng quan pipeline — 3 bước chính

```
Source Document X
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
  [Step 1: Knowledge Acquisition]        [Step 1: Knowledge Acquisition]
  Prompt LLM → Summarization (S)         Prompt LLM → Entity Pairs (E)
       │                                      │
       ▼                                      ▼
  [Step 2: Single-Knowledge Integration] [Step 2: Single-Knowledge Integration]
  Prompt LLM with S → Y^s               Prompt LLM with E → Y^e
       │                                      │
       │              + Baseline Y^b          │
       │              (no extra knowledge)     │
       ▼                   ▼                   ▼
  ┌────────────────────────────────────────────┐
  │    [Step 3: Multi-Knowledge Fusion]        │
  │    For each sentence X_i:                  │
  │      Select best Y_i from {Y_i^s, Y_i^e,  │
  │      Y_i^b} using reference-free COMET     │
  │    → Final translation Y^f                 │
  └────────────────────────────────────────────┘
```

### 4.1. Step 1: Document-Level Knowledge Acquisition

Hai loại tri thức được trích xuất từ tài liệu nguồn bằng cách prompt LLM:

#### a) Summarization Knowledge
- Prompt LLM tạo **bản tóm tắt** tài liệu nguồn bằng ngôn ngữ nguồn.
- Mục đích: cung cấp cái nhìn tổng quan về chủ đề, ý chính, giúp LLM hiểu ngữ cảnh rộng hơn khi dịch → dịch chính xác hơn các ẩn dụ, nội dung văn hóa, ý phức tạp.
- Prompt mẫu: *"Please summarize the following text. Text: \<source\>. Summarization:"*

#### b) Entity Translation Knowledge
- Prompt LLM **trích xuất các thực thể** (Person, Organization, Location, Date, Money, Work of Art, Product, Event, Occupation, Social Group, Animal...) và **dịch chúng trước**.
- Mục đích: đảm bảo **nhất quán** trong dịch thuật ngữ/tên riêng xuyên suốt tài liệu, giảm tình trạng bỏ sót không dịch.
- Prompt mẫu: *"Please extract as many entity words as possible from the following text and list each entity word along with its translation."*

### 4.2. Step 2: Single-Knowledge Integration

Tạo **3 bản dịch** khác nhau cho cùng một tài liệu:

| Ký hiệu | Mô tả | Tri thức bổ sung |
|---|---|---|
| **Y^b** (Baseline) | Dịch tài liệu không có tri thức bổ sung | Không |
| **Y^s** (SuMT) | Dịch với summarization được chèn vào prompt | Summarization |
| **Y^e** (EnMT) | Dịch với entity pairs được chèn vào prompt | Entity translation pairs |

Mỗi bản dịch chứa N câu tương ứng với N câu nguồn, được đánh dấu bằng `#1`, `#2`, ... để dễ mapping.

### 4.3. Step 3: Multi-Knowledge Fusion (KFMT)

Đây là **đóng góp chính** của paper.

**Insight quan trọng**: Mỗi loại tri thức không phải lúc nào cũng có lợi cho mọi câu.
- Summarization giúp những câu liên quan đến chủ đề chính.
- Entity translation giúp những câu chứa nhiều thực thể.
- Có những câu mà thêm tri thức vào lại **làm giảm** chất lượng dịch.

**Chiến lược**: Với mỗi câu X_i, chọn bản dịch tốt nhất từ 3 ứng viên:

$$Y_i^f = \arg\max_{Y \in \{Y_i^s, Y_i^e, Y_i^b\}} S(Y, X_i)$$

Trong đó S(·) là **hàm scoring không cần reference** — cụ thể là **COMETKiwi** (`wmt22-cometkiwi-da`), một mô hình đánh giá chất lượng dịch chỉ cần source + hypothesis (không cần reference).

**Oracle variant (KFMT_Oracle)**: Thay COMETKiwi bằng **COMET có reference** để chọn — đây là upper bound lý thuyết, dùng để đo khoảng cách tiềm năng cải thiện.

### Tổng chi phí LLM calls

Cho mỗi tài liệu, cần tổng cộng **5 lần gọi LLM**:
1. Tạo summarization
2. Trích xuất entity pairs
3. Dịch baseline (Y^b)
4. Dịch với summarization (Y^s)
5. Dịch với entity translation (Y^e)

Plus 1 lần chạy COMETKiwi scoring cho reranking.

---

## 5. Dataset & Thí nghiệm (Experiments)

### Dataset

- **Nguồn**: WMT 2023 News Commentary v18
- **Cặp ngôn ngữ**: En ↔ {De, Fr, Es, Ru} = **8 hướng dịch**
- **Kích thước**: 150 cặp tài liệu cho mỗi hướng dịch

### LLMs được đánh giá

| Model | Loại | Ghi chú |
|---|---|---|
| **LLaMA3-8B-Instruct** | Open-source | Chạy trên 1x NVIDIA V100 32GB |
| **Mistral-Nemo-Instruct** | Open-source | Chạy trên 1x NVIDIA V100 32GB |
| **GPT-4o-mini** | Closed-source (API) | Gọi qua OpenAI API |

### Inference settings
- **Decoding**: Greedy (temperature = 0)
- **Scoring function cho fusion**: COMETKiwi (`wmt22-cometkiwi-da`) — reference-free

### Evaluation Metrics

| Metric | Mô tả |
|---|---|
| **COMET** (chính) | Reference-based, model `wmt22-comet-da`. Metric chính được báo cáo |
| **dCOMET** | Document-level COMET (Appendix) |
| **BLEU** | N-gram overlap truyền thống (Appendix) |
| **BlonDe** | Đánh giá hiện tượng discourse (pronoun, lexical consistency...) |
| **Perplexity** | Đo fluency bằng GPT-2 |
| **Coherence** | Đo mạch lạc liên câu bằng SimCSE similarity |
| **GPT-4o evaluation** | Chấm điểm 0-100 bởi GPT-4o |
| **Human evaluation** | Annotator chọn bản dịch tốt hơn (A, B, hoặc ngang nhau) |

### Baselines

| System | Mô tả |
|---|---|
| **Baseline** | Prompt LLM dịch tài liệu mà không có tri thức bổ sung |
| **Reranking** | Sinh 3 bản dịch từ Baseline (không có tri thức) rồi rerank — để chứng minh rằng improvement đến từ tri thức chứ không phải từ việc có nhiều ứng viên |
| **SuMT** | Chỉ dùng summarization knowledge |
| **EnMT** | Chỉ dùng entity translation knowledge |
| **KFMT** | Multi-knowledge fusion (phương pháp đề xuất) |
| **KFMT_Oracle** | Upper bound — dùng reference-based COMET để chọn |

---

## 6. Kết quả chính (Key Results)

### 6.1. Bảng kết quả COMET chính (Table 2)

#### LLaMA3-8B-Instruct

| System | En→De | De→En | En→Es | Es→En | En→Ru | Ru→En | En→Fr | Fr→En | **Avg** |
|---|---|---|---|---|---|---|---|---|---|
| Baseline | 85.2 | 88.2 | 87.1 | 88.8 | 83.8 | 83.9 | 84.9 | 87.0 | **86.1** |
| Reranking | 85.7 | 88.4 | 87.4 | 88.9 | 84.5 | 84.2 | 85.3 | 87.2 | 86.5 |
| SuMT | 85.3 | 88.3 | 87.2 | 88.8 | 83.7 | 84.1 | 85.0 | 87.3 | 86.2 |
| EnMT | 85.3 | 88.3 | 86.9 | 88.4 | 83.4 | 83.9 | 84.8 | 86.9 | 86.0 |
| **KFMT** | **86.1** | **88.6** | **87.8** | **89.0** | **85.5** | **84.7** | **85.8** | **87.6** | **86.9** |
| KFMT_Oracle | 86.4 | 88.8 | 88.2 | 89.4 | 86.0 | 85.1 | 86.3 | 88.0 | 87.3 |

#### Mistral-Nemo-Instruct

| System | En→De | De→En | En→Es | Es→En | En→Ru | Ru→En | En→Fr | Fr→En | **Avg** |
|---|---|---|---|---|---|---|---|---|---|
| Baseline | 86.5 | 89.0 | 87.3 | 89.4 | 87.0 | 85.2 | 85.9 | 88.0 | **87.3** |
| **KFMT** | **87.6** | **89.3** | **88.2** | **89.6** | **87.9** | **85.4** | **86.7** | **88.1** | **87.9** |

#### GPT-4o-mini

| System | En→De | De→En | En→Es | Es→En | En→Ru | Ru→En | En→Fr | Fr→En | **Avg** |
|---|---|---|---|---|---|---|---|---|---|
| Baseline | 88.5 | 89.3 | 88.9 | 89.6 | 88.7 | 85.5 | 87.3 | 88.1 | **88.2** |
| **KFMT** | **88.9** | **89.6** | **89.3** | **89.9** | **89.2** | **85.8** | **87.7** | **88.4** | **88.6** |

### 6.2. Các quan sát chính

1. **KFMT cải thiện nhất quán trên cả 3 LLMs**: +0.8 (LLaMA3), +0.6 (Mistral-Nemo), +0.4 (GPT-4o-mini) điểm COMET trung bình so với Baseline.
2. **En→X cải thiện nhiều hơn X→En**: Với LLaMA3, En→X cải thiện trung bình +1.1, trong khi X→En chỉ +0.5. Lý do: LLM được huấn luyện chủ yếu trên dữ liệu tiếng Anh, nên hiểu source tiếng Anh tốt hơn → tri thức bổ sung hữu ích hơn.
3. **KFMT > Reranking**: Chứng minh cải thiện đến từ **tri thức bổ sung**, không đơn thuần từ việc có nhiều ứng viên để chọn.
4. **Single knowledge (SuMT, EnMT) không luôn tốt hơn Baseline**: EnMT thậm chí đôi khi tệ hơn Baseline → khẳng định sự cần thiết của fusion strategy.
5. **Khoảng cách KFMT ↔ KFMT_Oracle**: Còn ~0.4 điểm COMET → room for improvement nếu có scoring function tốt hơn.

### 6.3. Ablation Study (Table 3)

| System | En→Ru | Ru→En | En→Fr | Fr→En |
|---|---|---|---|---|
| Baseline | 83.8 | 83.9 | 84.9 | 87.0 |
| KFMT | **85.5** | **84.7** | **85.8** | **87.6** |
| w/o Summarization | 84.8 | 84.4 | 85.5 | 87.4 |
| w/o Entity | 85.0 | 84.5 | 85.5 | 87.5 |

- Bỏ summarization giảm nhiều hơn bỏ entity → **summarization đóng vai trò quan trọng hơn**.
- Cả hai loại tri thức đều đóng góp, nhưng summarization có ảnh hưởng lớn hơn.

### 6.4. Phân tích tỷ lệ chọn (Figure 3)

- Trung bình **~50% câu** trong bản dịch cuối cùng đến từ Baseline (không cần tri thức bổ sung).
- **~50% còn lại** hưởng lợi từ summarization hoặc entity translation.
- Summarization được chọn **thường xuyên hơn** entity translation.

### 6.5. Fluency (Table 4)

| Metric | Baseline | KFMT | Nhận xét |
|---|---|---|---|
| Perplexity (En→Ru) | 10.7 | **7.5** | Giảm = tốt hơn |
| Coherence (En→Fr) | 91.7 | **92.6** | Tăng nhẹ hoặc giữ nguyên |

→ KFMT **không làm giảm fluency** mặc dù chọn câu từ nhiều hệ thống khác nhau, thậm chí còn cải thiện perplexity.

### 6.6. GPT-4o Evaluation (Table 5)

| System | En→Ru | Ru→En | En→Fr | Fr→En |
|---|---|---|---|---|
| Baseline | 70.1 | 82.7 | 79.7 | 84.0 |
| **KFMT** | **74.6** | **84.7** | **82.9** | **86.1** |

KFMT vượt trội trên cả 4 hướng dịch khi đánh giá bởi GPT-4o (0-100 scale).

### 6.7. Human Evaluation (Figure 4)

- **46.3%** trường hợp: hai bản dịch ngang nhau.
- **41.8%** trường hợp: KFMT được chọn tốt hơn.
- **11.9%** trường hợp: Baseline được chọn tốt hơn.
- → Tỷ lệ win **41.8% vs 11.9%** cho thấy ưu thế rõ ràng của KFMT.

### 6.8. Sentence-level vs Token-level Fusion (Table 6)

| System | En→Ru | Ru→En | En→Fr | Fr→En |
|---|---|---|---|---|
| Baseline | 83.8 | 83.9 | 84.9 | 87.0 |
| TFMT (token-level) | 84.0 | 84.2 | 85.1 | 87.2 |
| **KFMT (sentence-level)** | **85.5** | **84.7** | **85.8** | **87.6** |

- Fusion cấp câu (KFMT) **tốt hơn nhiều** so với fusion cấp token (TFMT).
- TFMT chỉ cải thiện nhẹ so với Baseline, cho thấy reranking cấp câu là chiến lược phù hợp hơn.

### 6.9. Chất lượng Summarization & Entity Extraction (Table 13)

GPT-4o chấm chất lượng (0-100):

| Task | En→Ru | Ru→En | En→Fr | Fr→En | **Avg** |
|---|---|---|---|---|---|
| Summarization | 78.0 | 78.6 | 77.1 | 80.5 | **78.6** |
| Entity Translation | 87.1 | 87.1 | 91.7 | 83.6 | **87.4** |

- Entity extraction/translation đạt chất lượng cao hơn summarization.
- Tuy entity extraction chính xác hơn, summarization lại **có ích hơn** cho DMT → gợi ý rằng hiểu tổng quan tài liệu quan trọng hơn dịch đúng từng thực thể.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Ý tưởng trực giác và thuyết phục**: Mô phỏng quy trình của dịch giả chuyên nghiệp (đọc hiểu → đánh dấu thực thể → dịch) là cách tiếp cận tự nhiên và hợp lý.
2. **Không cần training**: Hoàn toàn dựa trên prompt engineering, không cần fine-tuning LLM → tiết kiệm tài nguyên, dễ áp dụng với bất kỳ LLM nào.
3. **Thí nghiệm toàn diện**: 3 LLMs × 8 hướng dịch, kết hợp automatic metrics, GPT evaluation, và human evaluation. Ablation study rõ ràng.
4. **Insight quan trọng**: Single knowledge có thể **làm hại** một số câu → cần fusion strategy. Đây là observation có giá trị thực tiễn.
5. **KFMT > naive Reranking**: Chứng minh được improvement đến từ tri thức, không phải sampling luck.
6. **Không ảnh hưởng fluency**: Mặc dù ghép câu từ nhiều nguồn, coherence và perplexity vẫn tốt.

### Điểm yếu

1. **Chi phí inference cao**: Cần 5 lần gọi LLM + 1 lần chạy COMETKiwi cho mỗi tài liệu. Với API models như GPT-4o-mini, chi phí tăng 5× so với dịch thông thường. Paper **không phân tích chi phí/latency**.
2. **Chỉ 2 loại tri thức**: Summarization và entity translation là lựa chọn hợp lý nhưng **hạn chế**. Chưa khám phá các tri thức khác như: discourse structure, coreference chains, terminology glossary, style/register information.
3. **Fusion strategy quá đơn giản**: Chỉ chọn 1 trong 3 bản dịch cho mỗi câu bằng COMETKiwi score. Chưa thử: (a) merge/combine tốt nhất từ nhiều bản dịch ở mức chi tiết hơn, (b) prompt LLM chọn/merge, (c) weighted combination.
4. **Dataset hạn chế**: Chỉ dùng News Commentary (WMT) → domain tin tức. Chưa đánh giá trên literary text, technical docs, conversation, hoặc low-resource languages.
5. **Chỉ European languages**: En ↔ {De, Fr, Es, Ru} — toàn bộ là ngôn ngữ châu Âu. Chưa thử nghiệm với ngôn ngữ có cấu trúc rất khác (Zh, Ja, Ko, Vi...) nơi entity translation và summarization có thể hoạt động khác.
6. **Khoảng cách với Oracle**: KFMT_Oracle tốt hơn KFMT ~0.4 điểm → COMETKiwi chưa phải scoring function tối ưu, nhưng paper không khám phá alternatives (e.g., XCOMET, MetricX).
7. **Không phân tích error cases**: Thiếu case study chi tiết về khi nào và tại sao KFMT chọn sai.
8. **Giả định mapping 1-1 giữa câu nguồn và câu đích**: Cần N câu trong bản dịch khớp chính xác với N câu nguồn. Nếu LLM merge/split câu khi dịch thì pipeline bị phá vỡ.

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán Document-level MT của mình (Vi ↔ En)

1. **Summarization as context**: Tạo bản tóm tắt tài liệu nguồn bằng LLM rồi chèn vào prompt khi dịch. Đặc biệt hữu ích cho văn bản dài, nhiều chủ đề.

2. **Entity pre-translation cho tiếng Việt**: Tiếng Việt có nhiều thực thể đặc thù (tên riêng Việt, địa danh, tổ chức) mà LLM hay dịch sai hoặc bỏ sót. Có thể kết hợp với **cultural knowledge base** đã xây dựng.

3. **Multi-translation + reranking**: Sinh nhiều bản dịch với các loại tri thức khác nhau, rồi chọn bản tốt nhất cho từng câu. Có thể mở rộng thêm nguồn tri thức:
   - **Cultural context** (kiến thức văn hóa Việt Nam)
   - **Terminology glossary** (bảng thuật ngữ chuyên ngành)
   - **Discourse structure** (cấu trúc đoạn văn)

4. **COMETKiwi cho reranking**: Reference-free metric hiệu quả, có thể áp dụng trực tiếp. Nên so sánh thêm với XCOMET, MetricX cho cặp Vi-En.

5. **Cải tiến fusion strategy**: Thay vì chỉ chọn 1 trong K bản dịch, có thể:
   - Dùng LLM để **merge** các bản dịch tốt nhất (MBR-like approach)
   - Dùng **weighted scoring** kết hợp nhiều metric
   - Áp dụng cho cultural-aware MT: dùng cultural KB làm thêm 1 nguồn tri thức

6. **Sentence-level alignment**: Cách đánh dấu câu bằng `#1`, `#2`... trong prompt để đảm bảo mapping 1-1 là technique đơn giản nhưng hiệu quả, nên áp dụng.

7. **Kết hợp với KB đã có**: Entity translation knowledge trong paper này rất giống concept cultural knowledge base. Có thể:
   - Dùng KB làm "entity translation dictionary" inject vào prompt
   - So sánh entity extraction từ LLM vs entity lookup từ KB

---

## 9. Các paper liên quan quan trọng

### Về Document-level MT

| Paper | Ghi chú |
|---|---|
| **Wang et al. (2023b)** — Document-level MT with LLM | PE approach, dịch từng câu với inter-sentence context |
| **Wu and Hu (2023)** | Prompt engineering cho DMT |
| **Lyu et al. (2024)** | SFT approach cho document-level MT |
| **Li et al. (2024)** | SFT approach cho document-level MT |
| **Wu et al. (2024)** | SFT approach cho document-level MT |

### Về Knowledge-enhanced MT

| Paper | Ghi chú |
|---|---|
| **He et al. (2024)** | Nguồn cảm hứng chính cho pipeline 3 bước của paper |
| **Lyu et al. (2021)** | Entity translation consistency trong document MT |

### Về Evaluation

| Paper | Ghi chú |
|---|---|
| **Rei et al. (2022)** — COMET | Reference-based MT evaluation metric |
| **Jiang et al. (2022)** — BlonDe | Discourse-aware MT evaluation |
| **Kocmi and Federmann (2023)** | GPT-based MT evaluation, prompt template |

### Về LLM và Summarization

| Paper | Ghi chú |
|---|---|
| **Pu et al. (2023)** | LLM tạo summarization chất lượng cao |
| **Zhang et al. (2024)** | LLM summarization fluency/authenticity |

### Về Scoring/Reranking

| Paper | Ghi chú |
|---|---|
| **COMETKiwi (wmt22-cometkiwi-da)** | Reference-free quality estimation, dùng làm scoring function |
| **Li et al. (2023a); Kallini et al. (2024)** | Perplexity và coherence evaluation cho fluency |
| **Gao et al. (2021)** — SimCSE | Sentence embeddings cho coherence measurement |

---

## Ghi chú cá nhân

- Paper này thuộc hướng **prompt engineering for DMT** — không cần training, phù hợp khi muốn leverage LLM sẵn có.
- Ý tưởng core (multi-source knowledge → multiple translations → sentence-level reranking) là **generalizable** và có thể extend dễ dàng bằng cách thêm nguồn tri thức mới.
- Với bài toán Vi ↔ En, **cultural knowledge** có thể là nguồn tri thức thứ 3 rất mạnh mà paper này chưa khai thác.
- Điểm yếu lớn nhất khi áp dụng: **chi phí inference** — cần cân nhắc trade-off giữa quality improvement (+0.4~0.8 COMET) và cost (×5 API calls).
