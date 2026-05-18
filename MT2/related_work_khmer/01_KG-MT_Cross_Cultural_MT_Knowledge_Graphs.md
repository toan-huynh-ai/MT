# Tóm tắt Paper: Cross-Cultural Machine Translation with RAG from Multilingual Knowledge Graphs

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Towards Cross-Cultural Machine Translation with Retrieval-Augmented Generation from Multilingual Knowledge Graphs |
| **Authors** | Simone Conia (Sapienza University of Rome), Daniel Lee (Adobe), Min Li (Apple), Umar Farooq Minhas (Apple), Saloni Potdar (Apple), Yunyao Li (Adobe) |
| **Venue** | EMNLP 2024 |
| **Year** | 2024 |
| **arXiv** | [2410.14057](https://arxiv.org/abs/2410.14057) |
| **Affiliations** | Sapienza University of Rome, Adobe, Apple |

---

## 2. Tóm tắt (Abstract)

Paper giải quyết bài toán **dịch máy xuyên văn hóa** (cross-cultural translation), tập trung vào các văn bản chứa **tên thực thể** (entity names) mà tên gọi có thể khác biệt đáng kể giữa các ngôn ngữ do yếu tố văn hóa (transcreation — không chỉ đơn thuần là phiên âm hay dịch từng từ).

Hai đóng góp chính:

1. **XC-Translate**: Benchmark đầu tiên quy mô lớn, được tạo thủ công, dành cho dịch máy tập trung vào văn bản chứa tên thực thể mang sắc thái văn hóa — 10 cặp ngôn ngữ, ~58.000 instances.
2. **KG-MT**: Phương pháp end-to-end tích hợp thông tin từ **đồ thị tri thức đa ngôn ngữ** (multilingual knowledge graph — Wikidata) vào mô hình dịch máy thông qua cơ chế **dense retrieval**.

Kết quả: KG-MT vượt NLLB-200 **129%** và GPT-4 **62%** (relative improvement) trên metric M-ETA (đo chính xác dịch tên thực thể).

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Khi dịch văn bản chứa tên thực thể (tên phim, sách, địa điểm, món ăn, người...), việc dịch từng từ (literal/word-for-word translation) thường cho kết quả **sai về mặt ngữ nghĩa**. Lý do: tên thực thể thường được **transcreate** — thích ứng theo ngữ cảnh văn hóa, không chỉ phiên âm.

### Ví dụ minh họa

| Ngôn ngữ nguồn (IT) | Dịch từng từ (EN) | Dịch đúng (EN) |
|---|---|---|
| "Il Giovane Holden" | "The Young Holden" ❌ | "The Catcher in the Rye" ✅ |

→ Tên tiểu thuyết trong tiếng Ý hoàn toàn khác tiếng Anh, không thể suy ra bằng phiên âm hay dịch word-by-word.

### Tại sao quan trọng?

- Các hệ thống MT hiện tại (kể cả GPT-4) vẫn **struggle** với bài toán này.
- Benchmark hiện có không tập trung vào thách thức dịch tên thực thể xuyên văn hóa.
- Phương pháp data augmentation hiện tại cần retrain liên tục khi có thực thể mới, tốn tài nguyên tính toán.

### Ba lỗ hổng trong nghiên cứu trước đó

1. Tập trung chủ yếu vào **transliteration** (phiên âm), bỏ qua **transcreation** (thích ứng văn hóa).
2. Thiếu benchmark quy mô lớn, chất lượng cao cho bài toán này.
3. Phương pháp chủ yếu dựa trên **data augmentation tổng hợp** → tốn tài nguyên, cần retrain thường xuyên.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Ý tưởng cốt lõi

Thay vì cố gắng **ghi nhớ** (memorize) tất cả tên thực thể trong mọi cặp ngôn ngữ qua data augmentation, KG-MT **truy vấn** (retrieve) tên thực thể từ đồ thị tri thức đa ngôn ngữ (Wikidata) **khi cần** (on the fly) và tích hợp vào quá trình dịch.

### 4.2 Kiến trúc tổng quan (Figure 1)

KG-MT gồm 2 thành phần chính + 1 chiến lược fusion:

```
Source text (ngôn ngữ nguồn)
       │
       ├──→ [Knowledge Retriever] ──→ Top-k entities từ KG (Wikidata)
       │         │                         │
       │         │ entity embeddings       │ entity names (source → target)
       │         │                         │
       └──→ [Knowledge-Enhanced Translator]
                  │
                  ├── Explicit Integration: nối tên thực thể vào input
                  │
                  └── Implicit Integration: fuse entity embeddings với encoder states
                  │
                  ▼
            Target text (ngôn ngữ đích)
```

### 4.3 Component 1: Knowledge Retriever (Section 3.1)

**Mục tiêu**: Cho source text **t**, tìm top-k thực thể liên quan nhất từ KG.

- **Biểu diễn thực thể**: Mỗi entity `e_i = <n_i, d_i>` với `n_i` = tên chính, `d_i` = mô tả (để phân biệt đồng âm/homonyms).
- **Relevance score**: Cosine similarity giữa embedding của entity và embedding của source text.
- **Encoder**: Dựa trên **mContriever** (pretrained multilingual dense retriever), fine-tune bằng contrastive learning.
- **Loss function**: Contrastive loss — maximize likelihood retrieve entity đúng, minimize likelihood retrieve entity sai.
- **Hard negative mining**: Thay vì random in-batch negatives, chọn **n thực thể đồng âm** (cùng tên nhưng khác nghĩa) làm negative examples → giúp retriever phân biệt homonyms.
- **Kết quả retrieval**: hits@1 = 85.9%, hits@3 = 92.1% trên XC-Translate.
- **k = 3** (trade-off giữa coverage và computational cost).

### 4.4 Component 2: Knowledge-Enhanced Translator

#### 4.4.1 Explicit Knowledge Integration (Section 3.2)

Nối thông tin tên thực thể trực tiếp vào source text:

```
t^{+KG} = <w_1, ..., w_n, [KG], n_1^s → n_1^t, ..., n_k^s → n_k^t>
```

- `[KG]`: Special token đánh dấu bắt đầu phần entity translations.
- `n_i^s → n_i^t`: Tên entity i trong ngôn ngữ nguồn → ngôn ngữ đích (lấy từ KG).
- MT model được fine-tune để học cách attend vào phần entity translations khi sinh bản dịch.

**Ưu điểm**: Đơn giản, dễ implement.
**Nhược điểm**: Tăng chiều dài input → attention mechanism O(n²) bị ảnh hưởng.

#### 4.4.2 Implicit Knowledge Integration (Section 3.3)

Fuse embedding từ retriever với encoder hidden states:

```
h^{+KG+E} = <e_1, ..., e_k, h_1, ..., h_{n+k+1}>
```

- Prepend entity embeddings (`e_i` từ retriever) vào trước encoder hidden states.
- Decoder có thể attend vào cả entity embeddings lẫn hidden states.
- Lấy cảm hứng từ **Fusion-in-Decoder (FiD)** nhưng fuse hidden states từ **hai encoder khác nhau** (retriever encoder vs. MT encoder).

**Ưu điểm**: Input length của decoder chỉ tăng theo số entity (controllable qua hyperparameter), chứa latent information tinh vi hơn.
**Nhược điểm**: Phức tạp hơn, cần can thiệp vào kiến trúc bên trong MT model.

#### 4.4.3 Kết hợp Explicit + Implicit

Kết hợp cả hai phương pháp cho kết quả tốt nhất — hai phương pháp **bổ trợ** cho nhau (complementary). Entity embeddings có thể đóng vai trò **indicator** cho MT model biết khi nào nên dựa vào parametric memory vs. retrieved knowledge.

### 4.5 Training

| Component | Dataset | Chi tiết |
|---|---|---|
| Knowledge Retriever | Mintaka (Sen et al., 2022) | ~14,000 instances, QA dataset với entity tags |
| Knowledge-Enhanced Translator | Mintaka + NLLB-200 data | Uniform sampling mixture |

**Hardware**: 1x NVIDIA V100, 32GB RAM, 32-core CPU.
**Thời gian training**: Retriever ~4 giờ, Translator ~6 giờ → **khả thi trên single GPU**.

**Hyperparameters chính**:
- Learning rate: 1e-5
- Batch size: 32
- Epochs: 5
- Optimizer: AdamW
- Max query/context length (retriever): 128
- Max input/output length (translator): 512

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Benchmark: XC-Translate

| Thuộc tính | Chi tiết |
|---|---|
| **Quy mô** | ~5,000 câu/cặp ngôn ngữ, tổng >58,000 instances |
| **Số cặp ngôn ngữ** | 10 (EN→AR, DE, ES, FR, IT, JA, KO, TH, TR, ZH) |
| **Multi-reference** | >100,000 references (~2 bản dịch/câu trung bình) |
| **Chất lượng** | Tạo thủ công bởi annotators bản ngữ, qua 2 vòng: dịch + xác minh |
| **Nguồn entities** | Wikidata (entities có tên khác ≥50% so với dịch word-for-word, đo bằng Levenshtein distance) |
| **Dạng văn bản** | Câu hỏi ngắn (<25 từ) về thực thể → giảm nhiễu, tập trung test khả năng dịch entity |

**Design Principles**:
1. Văn bản phải chứa entity names bị ảnh hưởng bởi transcreation (không chỉ transliteration).
2. Thách thức nằm ở dịch tên thực thể, không phải dịch phần còn lại.

**Quality Assurance**:
- Annotators phải pass entrance test (threshold 85%).
- Mỗi câu được dịch bởi ≥3 translators, xác minh bởi ≥3 annotators.
- Tổng effort: ~5,133 giờ nhân công.

### 5.2 Evaluation Metrics

| Metric | Mô tả | Vai trò |
|---|---|---|
| **M-ETA** (Manual Entity Translation Accuracy) | Kiểm tra bản dịch có chứa tên thực thể đúng không (dựa trên danh sách gold names) | **Metric chính** — đo entity-level quality |
| **BLEU** | N-gram overlap | Đo translation quality tổng thể |
| **COMET** | Neural metric (semantic similarity) | Đo translation quality tổng thể |

**M-ETA**: Với bản dịch `t'` và tập gold entities, tính trung bình xem mỗi entity có ít nhất 1 tên đúng xuất hiện trong `t'` hay không. Đơn giản, interpretable, trực tiếp đo khả năng dịch tên thực thể.

### 5.3 Baselines

| Loại | Hệ thống | Kích thước |
|---|---|---|
| **LLM** | GPT-3 (text-davinci-003), GPT-3.5 (gpt-3.5-turbo-0613), GPT-4 (gpt-4-0613) | 175B / ? / ? |
| **MT** | mBART-50, M2M-100, NLLB-200 | 0.6B / 0.4B / 0.6B |
| **RAG (đề xuất)** | KG-MT_mBART, KG-MT_M2M, KG-MT_NLLB | 0.6B / 0.4B / 0.6B |

Tất cả MT models và KG-MT được fine-tune trên cùng dataset (Mintaka).

---

## 6. Kết quả chính (Key Results)

### 6.1 Kết quả trung bình trên XC-Translate (Table 1)

| Hệ thống | BLEU | COMET | M-ETA | Size |
|---|---|---|---|---|
| GPT-3 | 37.4 | 75.4 | 14.1 | 175B |
| GPT-3.5 | 42.8 | 77.8 | 20.9 | ? |
| GPT-4 | 50.9 | 82.1 | 25.3 | ? |
| mBART-50 | 36.1 | 79.8 | 12.2 | 0.6B |
| M2M-100 | 34.8 | 77.9 | 11.5 | 0.4B |
| NLLB-200 | 39.5 | 81.9 | 17.9 | 0.6B |
| **KG-MT_mBART** | 44.1 | 79.7 | **39.1** | 0.6B |
| **KG-MT_M2M** | 42.6 | 80.8 | **38.3** | 0.4B |
| **KG-MT_NLLB** | **51.8** | **84.6** | **41.1** | 0.6B |

**Nhận xét chính**:
- KG-MT_NLLB đạt M-ETA 41.1% — cải thiện **+129%** so với NLLB-200 (17.9%) và **+62%** so với GPT-4 (25.3%).
- KG-MT (0.6B params) vượt GPT-4 (ước tính lớn hơn ~100 lần) trên cả BLEU, COMET, M-ETA.
- Cải thiện M-ETA **nhất quán** qua các backbone MT khác nhau (39.1, 38.3, 41.1).
- BLEU và COMET **không phản ánh tốt** khả năng dịch entity: GPT-4 đạt COMET 82.1 nhưng M-ETA chỉ 25.3.

### 6.2 Kết quả theo từng cặp ngôn ngữ (Table 2 — M-ETA)

| Hệ thống | AR | DE | ES | FR | IT | JA | KO | TH | TR | ZH |
|---|---|---|---|---|---|---|---|---|---|---|
| NLLB-200 | 20.5 | 19.6 | 31.5 | 24.7 | 26.4 | 8.4 | 17.7 | 1.8 | 25.4 | 3.1 |
| GPT-4 | 23.8 | 27.8 | 35.2 | 28.5 | 34.7 | 22.9 | 18.4 | 5.4 | 36.4 | 19.9 |
| **KG-MT_NLLB** | **50.6** | 36.5 | **47.8** | 39.8 | **47.5** | **42.2** | **47.1** | **39.6** | **49.7** | 10.6 |

**Nhận xét**:
- Cải thiện lớn nhất ở **Thai** (1.8→39.6), **Japanese** (8.4→42.2), **Korean** (17.7→47.1) — các ngôn ngữ khác script với English.
- **Chinese** (ZH) là ngoại lệ: KG-MT vẫn thấp (10.6) — có thể do đặc thù script/tokenization.
- Cải thiện nhất quán ở cả ngôn ngữ cùng script (ES, FR, IT, DE) lẫn khác script (AR, JA, KO, TH).

### 6.3 Kết quả trên WMT benchmarks (Table 3)

| Hệ thống | BLEU | COMET |
|---|---|---|
| NLLB-200 | 23.3 | 60.2 |
| GPT-4 | 24.4 | 61.0 |
| **KG-MT_NLLB** | 24.1 | **61.9** |

→ KG-MT **không làm giảm** chất lượng dịch tổng quát, thậm chí cải thiện nhẹ (+0.8 BLEU, +1.7 COMET so với NLLB-200 vanilla).

### 6.4 Ablation Study

#### Explicit vs. Implicit Knowledge Integration (Figure 2)
- Explicit alone: hiệu quả.
- Implicit alone: hiệu quả.
- **Cả hai kết hợp**: tốt nhất → **bổ trợ** cho nhau (complementary).

#### Knowledge Retrieval Quality
- Retriever đạt **hits@1 = 85.9%**, **hits@3 = 92.1%**.
- Hard negative mining cải thiện: +5.6% hits@1, +4.2% hits@3 so với mContriever pretrained.

#### Gold Knowledge (Figure 3)
- Dùng gold entities (thay vì retrieved): M-ETA chỉ tăng thêm **11.6%**.
- → Bottleneck chính KHÔNG phải ở retrieval mà ở **knowledge integration** — translator chưa luôn biết cách sử dụng tốt thông tin retrieved.
- → Hướng cải thiện tương lai: fusion strategies tốt hơn, dataset fine-tuning tốt hơn cho bước integration.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Vấn đề được định nghĩa rõ ràng và có giá trị thực tiễn**: Dịch tên thực thể xuyên văn hóa là bài toán thực sự quan trọng mà MT hiện tại vẫn yếu.
2. **Benchmark chất lượng cao**: XC-Translate được tạo thủ công với quy trình annotation nghiêm ngặt (entrance test, multi-annotator verification), đa ngôn ngữ, multi-reference.
3. **Phương pháp thanh lịch và hiệu quả**: Ý tưởng retrieve-then-translate đơn giản nhưng mạnh — tận dụng KG có sẵn thay vì cố gắng memorize mọi thứ.
4. **Hiệu quả tài nguyên**: Train trên single V100, ~10 giờ tổng. So với data augmentation cần retrain trên nhiều GPU.
5. **Khả năng cập nhật**: KG (Wikidata) được cập nhật liên tục — model không cần retrain khi có entity mới.
6. **Kết quả ấn tượng**: Vượt GPT-4 dù nhỏ hơn ~100x về params.
7. **Evaluation metric mới (M-ETA)**: Đo trực tiếp entity translation quality, interpretable hơn BLEU/COMET cho bài toán này.
8. **Ablation study kỹ lưỡng**: Phân tích explicit vs implicit, gold vs retrieved knowledge, per-language analysis.

### Điểm yếu

1. **Scope hẹp — chỉ entity names**: Không xử lý các yếu tố văn hóa khác (idioms, metaphors, cultural references không phải entity).
2. **Chỉ EN→X**: Benchmark chỉ test chiều English-to-X, không có X→X hay X→English.
3. **Dạng văn bản hạn chế**: Chỉ test trên câu hỏi ngắn (<25 từ). Chưa rõ hiệu quả trên văn bản dài, đoạn văn, tài liệu.
4. **Phụ thuộc vào Wikidata**: Nếu entity không có trong Wikidata hoặc thiếu tên trong target language → model không thể retrieve. Wikidata cũng thừa hưởng bias từ Wikipedia.
5. **Kết quả thấp trên tiếng Trung (ZH)**: KG-MT_NLLB chỉ đạt 10.6 M-ETA cho EN→ZH — rõ ràng có vấn đề đặc thù chưa được giải quyết.
6. **Knowledge integration là bottleneck**: Ngay cả với gold entities, M-ETA chỉ tăng 11.6% → translator chưa tận dụng tốt thông tin retrieved.
7. **k = 3 cố định**: Số entity retrieved cố định, không thích ứng theo context (văn bản dài có thể cần nhiều hơn).
8. **Không so sánh với open LLMs**: Chỉ so với GPT family, không test LLaMA, Mistral, hay các open-source LLMs.
9. **Training data nhỏ (Mintaka ~14K)**: Có thể giới hạn khả năng generalize. Chưa thử dataset lớn hơn.
10. **M-ETA metric đơn giản**: Chỉ kiểm tra string match — không xử lý biến thể viết hoa/thường, dạng rút gọn, hay partial matches.

---

## 8. Ý tưởng có thể áp dụng

### 8.1 Trực tiếp áp dụng cho bài toán MT

- **RAG từ Knowledge Base cho cultural terms**: Xây dựng KB chứa tên thực thể văn hóa (đặc biệt Vietnamese cultural entities — tên phim, sách, món ăn, địa danh) và retrieve khi dịch. Tương tự cách KG-MT dùng Wikidata.
- **Explicit knowledge integration format**: Format `[KG] n_s → n_t` rất đơn giản và có thể áp dụng ngay vào prompt engineering cho LLMs hoặc fine-tuning MT models.
- **Hard negative mining với homonyms**: Chiến lược tạo negative examples từ entities đồng âm — áp dụng cho training retriever trong bất kỳ NER/entity linking task nào.

### 8.2 Tham khảo cho methodology

- **Benchmark design**: Cách thiết kế XC-Translate (dùng Levenshtein distance để chọn entities khó, tạo câu hỏi ngắn, multi-reference, entrance test cho annotators) — tham khảo cho việc tạo evaluation dataset.
- **M-ETA metric**: Có thể adapt cho bài toán riêng — tạo danh sách gold entity translations, đo string match accuracy.
- **Two-pronged evaluation**: Dùng cả entity-level metric (M-ETA) và translation-level metrics (BLEU, COMET) để có cái nhìn toàn diện.

### 8.3 Cho bài toán MT cụ thể (Vietnamese)

- **Xây KB cho Vietnamese cultural entities**: Tên phim/sách/nhân vật có bản dịch khác biệt (VD: "Frozen" → "Nữ Hoàng Băng Giá", "The Little Prince" → "Hoàng Tử Bé").
- **Kết hợp với Wikidata Vietnamese labels**: Wikidata có Vietnamese labels cho nhiều entities — có thể khai thác trực tiếp.
- **Implicit knowledge fusion**: Ý tưởng prepend entity embeddings vào encoder states có thể áp dụng cho các mô hình encoder-decoder bất kỳ.
- **Cultural knowledge base (đã xây)**: Nếu project MT2 đã có `cultural_knowledge_base_v3.json`, có thể structure nó theo dạng tương tự Wikidata để làm nguồn retrieve.

### 8.4 Limitations cần lưu ý khi áp dụng

- Phương pháp chỉ mạnh với **entity names** — các nuance văn hóa khác (idioms, social norms) cần approach khác.
- Cần đảm bảo KB có **coverage tốt** cho target entities.
- Knowledge integration vẫn là bottleneck → cần thiết kế fusion strategy cẩn thận.

---

## 9. Các paper liên quan quan trọng

### Core — Nên đọc

| Paper | Nội dung | Venue |
|---|---|---|
| **Zeng et al. (2023)** — "Extract and Attend" | Extract entity names + dictionary lookup → append vào source text (tương tự explicit integration). Focus transliteration. | ACL 2023 Findings |
| **Hu et al. (2022)** — "DEEP" | DEnoising Entity Pre-training cho NMT — data augmentation approach | ACL 2022 |
| **Campolungo et al. (2022)** | Lexical constraints từ WordNet để cải thiện dịch word senses | NAACL 2022 |
| **Izacard & Grave (2021)** — "FiD" | Fusion-in-Decoder — foundation cho implicit knowledge integration | EACL 2021 |
| **Izacard et al. (2021)** — "mContriever" | Unsupervised dense retrieval với contrastive learning | arXiv |

### Knowledge Graphs & Multilingual

| Paper | Nội dung | Venue |
|---|---|---|
| **Conia et al. (2023)** | Tăng coverage thông tin textual trong multilingual KGs | EMNLP 2023 |
| **Kaffee et al. (2023)** | Survey: Multilingual KGs và low-resource languages | TGDK |
| **Navigli et al. (2021)** | 10 years of BabelNet — survey | IJCAI 2021 |

### MT Systems (Baselines)

| Paper | Nội dung | Venue |
|---|---|---|
| **Costa-jussà et al. (2022)** — NLLB-200 | No Language Left Behind — 200 ngôn ngữ | arXiv |
| **Fan et al. (2021)** — M2M-100 | Beyond English-centric multilingual MT | JMLR |
| **Liu et al. (2020)** — mBART-50 | Multilingual denoising pre-training cho NMT | TACL |

### Cross-Cultural NLP

| Paper | Nội dung | Venue |
|---|---|---|
| **Hershcovich et al. (2022)** | Challenges and strategies in cross-cultural NLP | ACL 2022 |
| **Díaz-Millón & Olvera-Lobo (2023)** | Systematic review: định nghĩa transcreation | Perspectives |

### Retrieval-Augmented MT

| Paper | Nội dung | Venue |
|---|---|---|
| **Zhang et al. (2018)** | Guiding NMT with retrieved translation pieces | NAACL 2018 |
| **Bulte & Tezcan (2019)** | Neural fuzzy repair — integrating fuzzy matches vào NMT | ACL 2019 |

### Evaluation

| Paper | Nội dung | Venue |
|---|---|---|
| **Sen et al. (2022)** — Mintaka | Dataset multilingual QA — dùng để train KG-MT | COLING 2022 |
| **Rei et al. (2020)** — COMET | Neural framework cho MT evaluation | EMNLP 2020 |
| **Perrella et al. (2024)** | Beyond correlation: interpretable evaluation of MT metrics | EMNLP 2024 |

---

*Ghi chú: File này được tạo cho mục đích review related work trong project MT2. Cập nhật lần cuối: 2026-05-13.*
