# Compositional Translation: A Novel LLM-based Approach for Low-resource Machine Translation

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Compositional Translation: A Novel LLM-based Approach for Low-resource Machine Translation |
| **Authors** | Armel Zebaze, Benoît Sagot, Rachel Bawden |
| **Venue** | ICML (International Conference on Machine Learning) |
| **Year** | 2025 |
| **arXiv** | [2503.04554](https://arxiv.org/abs/2503.04554) |
| **Code** | [github.com/ArmelRandy/compositional-translation](https://github.com/ArmelRandy/compositional-translation) |
| **Affiliation** | Inria (PRAIRIE-PSAI institute, ANR France 2030) |

---

## 2. Tóm tắt (Abstract)

Khả năng In-Context Learning (ICL) của các mô hình ngôn ngữ lớn (LLM) đã mở ra nhiều hướng nghiên cứu về cách prompt tối ưu cho các tác vụ NLP. Trong dịch máy (MT), việc sử dụng các ví dụ in-context tương đồng về ngữ nghĩa với câu cần dịch đã được chứng minh là có hiệu quả.

Paper đề xuất **Compositional Translation (CompTra)** — một paradigm dịch máy mới dựa trên LLM, thay thế phương pháp few-shot MT thông thường bằng cách:
1. **Phân tách** (decompose) câu nguồn thành các cụm từ đơn giản hơn
2. **Dịch** từng cụm từ với sự hỗ trợ của các ví dụ được truy xuất qua similarity search
3. **Tổng hợp** (recombine) các cặp cụm từ-bản dịch để tạo bản dịch cuối cùng

Trực giác cốt lõi: các cụm từ ngắn hơn vốn dĩ dễ dịch hơn và dễ tìm được ví dụ in-context phù hợp hơn. Điều này đặc biệt có lợi trong bối cảnh low-resource. Kết quả thực nghiệm trên FLORES 200, NTREX 128 và TICO-19 cho thấy CompTra vượt trội so với các baseline mạnh.

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề chính
- **LLM gặp khó khăn khi dịch sang ngôn ngữ ít tài nguyên (LRL)**: Mặc dù đã thu hẹp khoảng cách với MT supervised cho ngôn ngữ giàu tài nguyên (HRL), LLM vẫn struggle với các LRL (Hendy et al., 2023; Enis & Hopkins, 2024).
- **Hạn chế của few-shot MT truyền thống**: Khi pool ví dụ nhỏ hoặc out-of-domain, việc tìm ví dụ tương đồng qua similarity search không luôn hiệu quả.
- **Các phương pháp decomposition trước đó có nhược điểm**:
  - **DecoMT** (Puduppully et al., 2023): Phân tách ở mức token → các subpart không mạch lạc, khó dịch; tuần tự nên chậm; chỉ áp dụng cho model kiểu T5/FIM.
  - **DiPMT / CoD** (Ghazvininejad et al., 2023; Lu et al., 2024): Phụ thuộc vào từ điển bên ngoài → hạn chế khả năng nội tại của LLM; các từ đơn lẻ không đủ ngữ cảnh.

### Tại sao quan trọng?
- Hàng ngàn ngôn ngữ trên thế giới thuộc nhóm low-resource, việc cải thiện chất lượng dịch cho chúng có tác động xã hội lớn.
- Similarity-based selection đã được chứng minh cải thiện đáng kể MT cho LRL (Moslem et al., 2023; Tanzer et al., 2024; Zebaze et al., 2024a), cho thấy đây là hướng nghiên cứu đầy triển vọng.
- Cần một phương pháp **chỉ dựa vào bản thân LLM** (không cần từ điển/model bên ngoài) để tận dụng tối đa khả năng nội tại.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Tổng quan Pipeline — CompTra (Compositional Translation)

CompTra frame bài toán dịch như một **quy trình suy luận từng bước** (step-by-step reasoning), gồm 3 giai đoạn chính:

```
Câu nguồn → [Decomposition] → Các cụm từ đơn giản
                                    ↓
                            [Translation] (few-shot cho mỗi cụm từ)
                                    ↓
                            Các cặp (cụm từ, bản dịch)
                                    ↓
                            [Recombination] → Bản dịch cuối cùng
```

**Mô tả Figure 1 (Overview của CompTra):**
- Input: Một câu tiếng Anh cần dịch
- Bước 1: LLM phân tách câu thành nhiều cụm từ sử dụng từ vựng của câu gốc
- Bước 2: Với mỗi cụm từ, truy xuất 4-5 ví dụ tương đồng từ pool → dịch few-shot
- Bước 3: Các cặp cụm từ-bản dịch được "clean" (lọc ngôn ngữ) rồi đưa vào prompt để LLM dịch toàn bộ câu gốc

### 4.2 Giai đoạn 1: Decomposition (Phân tách)

- **Mục tiêu**: Tạo ra các cụm từ đơn giản hơn, **chia sẻ từ vựng** với câu nguồn, sử dụng từ trong cùng ngữ cảnh.
- **Công cụ**: Sử dụng **divide prompt** chứa các ví dụ phân tách từ corpus **MinWikiSplit** (Niklaus et al., 2019) — tập hợp các câu được chia thành minimal propositions.
- **Đặc điểm quan trọng**:
  - Số lượng cụm từ **không phải hyperparameter** → phụ thuộc vào cấu trúc câu (trung bình ~3.166 cụm từ/câu)
  - Các cụm từ là câu đầy đủ, mạch lạc, có thể dịch độc lập
  - Khác với DecoMT (token-level) và DiPMT (word-level), CompTra tạo **phrase-level** — cân bằng giữa ngữ cảnh đầy đủ và độ ngắn gọn

### 4.3 Giai đoạn 2: Translation (Dịch từng cụm từ)

- Mỗi cụm từ được dịch **độc lập** bằng LLM với **k=5 ví dụ few-shot** (mặc định)
- Ví dụ được truy xuất qua **BM25 similarity search** từ selection pool
- **Lọc ngôn ngữ**: Sử dụng **FastText language identifier** để loại bỏ các bản dịch cụm từ ở sai ngôn ngữ đích
- Sinh tối đa **500 tokens** mới trong giai đoạn này
- Vì cụm từ ngắn hơn câu gốc → dễ tìm ví dụ tương đồng hơn → bản dịch chất lượng cao hơn

### 4.4 Giai đoạn 3: Recombination (Tổng hợp)

- LLM nhận các cặp (cụm từ nguồn, bản dịch cụm từ) + câu nguồn gốc → sinh bản dịch cuối cùng
- **Merge prompt** có cấu trúc giống hệt **translate prompt** → tách biệt nguồn cải thiện (từ decomposition, không phải từ thay đổi prompt)
- Sinh tối đa **2000 tokens** mới
- Hậu xử lý: Loại bỏ **repeating bigrams** ở cuối bản dịch

### 4.5 Các đặc tính thiết kế quan trọng

| Đặc tính | CompTra | DecoMT | DiPMT/CoD |
|---|---|---|---|
| Đơn vị phân tách | Phrase-level (câu đơn giản) | Token-level | Word-level |
| Cần model/tool ngoài | Không (chỉ LLM) | Không | Cần từ điển |
| Tính tuần tự | Song song (mỗi phrase dịch độc lập) | Tuần tự (chậm) | Song song |
| Hyperparameter-free | Có (số phrase tự động) | Không (chunk size) | Không |
| Chất lượng ngữ cảnh phrase | Cao (câu đầy đủ) | Thấp (token chunks) | Thấp (từ đơn lẻ) |

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Datasets

| Dataset | Mô tả | Selection Pool | Test Set | Ngôn ngữ đánh giá |
|---|---|---|---|---|
| **FLORES 200** | Bản dịch từ web articles sang 204 ngôn ngữ | dev set (997 câu) | devtest set (1012 câu) | Amharic, Burmese, Fijian, Khmer, Lao, Samoan, Sinhala, Tsonga, Turkmen, Uyghur |
| **NTREX 128** | MT benchmark từ WMT19 news data, dịch bởi người chuyên nghiệp | 997 câu cuối | 1000 câu đầu | Amharic, Fijian, Shona, Somali, Tswana |
| **TICO-19** | Văn bản về đại dịch COVID-19, 35 ngôn ngữ | validation (971 câu) | test (2100 câu) | Amharic, Khmer, Lingala, Luganda, Tamil |

Tổng cộng: **15 hướng dịch English → LRL** khác nhau.

### 5.2 Models

| Model | Kích thước | Loại |
|---|---|---|
| **LLaMA 3.1 Instruct** | 8B, 70B | Open-source |
| **Gemma 2 Instruct** | 9B, 27B | Open-source |
| **Command-R / R+** | Không công bố | Commercial API (Cohere) |

### 5.3 Evaluation Metrics

- **MetricX-23-XXL**: Điểm 0-25, **thấp hơn = tốt hơn** (đo lỗi dịch). Hỗ trợ 101 ngôn ngữ (dựa trên mT5).
- **XCOMET-XXL**: Điểm 0-100, **cao hơn = tốt hơn**. Hỗ trợ 100 ngôn ngữ (dựa trên XLM-RoBERTa).
- **BLEU** và **chrF++**: Metrics n-gram matching, dùng để minh bạch (transparency).
- MetricX và XCOMET được ưu tiên vì là top-ranked non-ensemble metrics theo WMT Metrics Shared Task 2024.

### 5.4 Baselines

- **Zero-shot MT**: Dịch không có ví dụ
- **5-shot SONAR**: 5 ví dụ truy xuất bằng SONAR embeddings (cosine similarity)
- **5-shot BM25**: 5 ví dụ truy xuất bằng BM25 (word-level matching)
- **Zero-shot + CoT**: Chain-of-thought prompting
- **MAPS** (He et al., 2024): Multi-Aspect Prompting and Selection
- **TEaR** (Feng et al., 2024): Translate, Estimate, and Refine
- **SBYS** (Briakou et al., 2024): Translating Step-by-Step (4 giai đoạn)
- **Self-Refine** (Chen et al., 2024): Tự cải thiện bản dịch
- **NLLB-200-distilled-600M**: Mô hình MT supervised

### 5.5 Chi tiết thực nghiệm

- Retriever: BM25 (dùng BM25s library)
- k = 5 ví dụ/phrase (mặc định)
- Language ID: FastText
- Inference: vLLM với greedy decoding
- Max tokens: 500 (translation), 2000 (recombination)
- Hậu xử lý: Loại bỏ repeating bigrams

---

## 6. Kết quả chính (Key Results)

### 6.1 Kết quả trên FLORES 200 (Bảng chính)

**CompTra vs. 5-shot BM25 (MetricX, thấp hơn = tốt hơn):**

| Model | Cải thiện MetricX trung bình | Cải thiện XCOMET trung bình |
|---|---|---|
| LLaMA 3.1 70B It | **-0.4 MetricX** | — |
| Gemma 2 27B It | **-0.4 MetricX** | **+1.0 XCOMET** |
| Command-R+ | **-1.5 MetricX** | **+1.8 XCOMET** |

CompTra **nhất quán vượt trội** so với similarity-based few-shot MT trên **tất cả** hướng dịch và **tất cả** LLM được đánh giá.

### 6.2 So sánh với các phương pháp hiện có (Table 4 — LLaMA 3.1 70B It, FLORES 200)

| Phương pháp | MetricX trung bình (ước tính) | Nhận xét |
|---|---|---|
| Zero-shot | Cao nhất (kém nhất) | Baseline yếu |
| Zero-shot + CoT | **Tệ hơn Zero-shot** | CoT không giúp MT |
| SBYS | Tương đương Zero-shot | Phức tạp nhưng không hiệu quả |
| MAPS | Cải thiện nhẹ | Cần COMET QE |
| TEaR | Cải thiện khá | Multi-step refinement |
| 5-shot BM25 | Baseline rất mạnh | Đơn giản nhưng hiệu quả |
| 5-shot BM25 + Refine | Cải thiện nhẹ | Refinement giúp nhưng hạn chế |
| **CompTra** | **Tốt nhất** | Vượt trội significant |

**Phát hiện quan trọng**: 5-shot BM25 là baseline cực kỳ mạnh, và **CoT không giúp ích (thậm chí gây hại) cho MT** — cả zero-shot + CoT lẫn 5-shot + CoT đều tệ hơn phiên bản không CoT.

### 6.3 Kết quả trên NTREX 128 và TICO-19

Xu hướng tương tự FLORES 200: CompTra nhất quán vượt trội trên cả hai benchmark bổ sung, khẳng định tính general của phương pháp.

### 6.4 Ablation Studies (Phân tích thành phần)

#### a) Ảnh hưởng của model nhỏ (Table 5)

| Model nhỏ | Cải thiện MetricX trung bình |
|---|---|
| LLaMA 3.1 8B It | -0.4 |
| Gemma 2 9B It | **-1.04** |
| Command-R | **-1.04** |

→ CompTra hoạt động tốt với cả model nhỏ, và **gap lớn hơn** với một số model nhỏ so với model lớn (đặc biệt Gemma 2 9B vs 27B).

#### b) Ảnh hưởng của retriever (Table 7)

| Retriever | 5-shot trung bình | CompTra trung bình |
|---|---|---|
| LCS | 9.98 | 9.70 |
| SONAR | 8.96 | 8.83 |
| **BM25** | **8.72** | **8.49** |

→ BM25 là retriever tốt nhất cho cả few-shot MT và CompTra. CompTra cải thiện **bất kể** retriever nào.

#### c) Ảnh hưởng của chiến lược decomposition (Table 8)

| Chiến lược | MetricX trung bình | Nhận xét |
|---|---|---|
| Words (từ đơn lẻ) | Tệ nhất (~11.73) | Không đủ ngữ cảnh |
| Structure (dependency tree) | Tệ (~11.49) | Phrase không phải câu đầy đủ |
| Repeat (lặp câu gốc) | Tương đương BM25 (~8.65) | Không có thông tin mới |
| **CompTra native** | **Tốt nhất (~8.28)** | Phrase đơn giản, đầy đủ |
| Paraphrase | Gần CompTra (~8.52) | Tốt nhưng chậm hơn (4.9 vs 3.2 phrases/câu) |

→ Chất lượng decomposition rất quan trọng. Phrase phải là **câu đầy đủ**, **đơn giản**, và **chia sẻ từ vựng** với câu gốc.

#### d) Thay thế few-shot bằng NLLB (Table 6)

- **NLLB + CompTra** (dùng NLLB dịch phrases, LLM tổng hợp) thường ngang hoặc vượt NLLB standalone
- Cho thấy LLM hoạt động tốt như "merger" ngay cả khi phrase translations đến từ model khác
- Trường hợp thú vị: NLLB + CompTra vượt NLLB ngay cả ở các ngôn ngữ mà LLM few-shot yếu hơn NLLB (Lao, Samoan) → kết hợp "strong translator + strong merger" > "strong translator alone"

#### e) Out-of-domain evaluation (Table 9)

- TICO-19 test (health domain) + FLORES dev pool (news domain) vs. TICO-19 validation pool (health domain)
- In-domain tốt hơn out-of-domain (dĩ nhiên)
- Nhưng CompTra **vẫn cải thiện** so với 5-shot BM25 trong cả hai scenario
- → CompTra robust với domain mismatch

#### f) High-resource languages (Table 13)

- CompTra **KHÔNG cải thiện** khi dịch sang HRL (French, German, Spanish, Portuguese, Japanese)
- Zero-shot và few-shot đã đạt kết quả rất tốt → self-generated demonstrations không thêm giá trị
- → CompTra đặc biệt dành cho **low-resource scenarios**

#### g) Ensembling (Table 11)

- Kết hợp CompTra + 5-shot BM25 bằng BLASER 2.0 QE (chọn bản dịch có quality estimation score cao hơn)
- Ensemble **nhất quán vượt trội** cả hai thành phần → outputs của CompTra và few-shot MT khác nhau, bổ sung cho nhau

#### h) Nko — Very low-resource (Table 10)

- Nko: hệ chữ viết rất khác, rủi ro data contamination thấp
- CompTra đạt gain lên tới **+4.5 BLEU** và **+8 chrF++**
- Giải quyết vấn đề repeating tokens thường gặp trong few-shot MT

### 6.5 Phát hiện về chất lượng dịch phrase (Table 15)

- MetricX-QE cho thấy: **phrases được dịch chính xác hơn câu đầy đủ** → xác nhận giả thuyết cốt lõi
- Khoảng cách chất lượng giữa dịch phrase và dịch câu **tương quan thuận** với hiệu quả CompTra
- Tuy nhiên, **semantic similarity giữa phrase và câu gốc** quan trọng hơn chất lượng dịch phrase đơn thuần

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Đơn giản và hiệu quả**: Pipeline 3 bước rõ ràng, không cần model/tool ngoài (chỉ LLM + BM25), không hyperparameter phức tạp.
2. **Nhất quán trên nhiều benchmark**: Cải thiện trên 3 benchmark (FLORES, NTREX, TICO-19), 15 ngôn ngữ LRL, 6 LLM khác nhau.
3. **Scalable**: Hoạt động tốt với cả model lớn (70B) và nhỏ (8-9B). Do CompTra không yêu cầu LLM tuân theo instruction phức tạp.
4. **Hyperparameter-free decomposition**: Số lượng phrase tự động theo cấu trúc câu.
5. **Song song hóa**: Các phrase được dịch độc lập → nhanh hơn DecoMT (tuần tự).
6. **Robust với domain mismatch**: Vẫn cải thiện khi pool và test khác domain.
7. **Ensembling complementary**: Outputs khác biệt với few-shot MT → kết hợp được.
8. **Ablation study toàn diện**: Phân tích retriever, decomposition strategy, model size, domain, HRL vs LRL, reference-free metrics.
9. **Có code & data**: Tái sản xuất được.

### Điểm yếu

1. **Không cải thiện cho HRL**: Chỉ hiệu quả cho LRL → giới hạn phạm vi áp dụng.
2. **Chi phí inference cao**: 3 lần gọi LLM (decompose + translate phrases + recombine) → tăng latency và cost đáng kể so với single-pass translation.
3. **Phụ thuộc vào khả năng decompose của LLM**: Nếu LLM decompose kém (tạo phrase không mạch lạc), chất lượng sẽ giảm. Chưa đánh giá trên các LLM yếu decomposition.
4. **Chỉ đánh giá English → X**: Không rõ hiệu quả với hướng dịch khác (X → English, X → Y). Thí nghiệm French → X cho thấy gap thu hẹp.
5. **Phụ thuộc vào selection pool**: Vẫn cần pool parallel sentences để truy xuất ví dụ (dù nhỏ hơn cũng được).
6. **Language ID filtering**: Chỉ áp dụng khi ngôn ngữ được FastText hỗ trợ → một số LRL rất rare có thể không được filter.
7. **Evaluation metrics bias**: MetricX và XCOMET không hỗ trợ tất cả LRL (100-101 ngôn ngữ). Nko chỉ đánh giá bằng BLEU/chrF++.
8. **Chưa so sánh với supervised SOTA**: Không so sánh trực tiếp với NLLB hoặc Google Translate trên cùng benchmark (ngoại trừ NLLB trong một ablation nhỏ).
9. **Repeating bigram heuristic**: Việc xử lý repeating bigrams ở cuối bản dịch là một workaround, cho thấy LLM đôi khi sinh output không ổn định.

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT low-resource của mình

1. **Decomposition strategy cho Vietnamese ↔ LRL**:
   - Áp dụng tư tưởng phân tách câu phức thành cụm từ đơn giản trước khi dịch
   - Đặc biệt hữu ích khi dịch các cultural expressions hoặc câu phức có nhiều thành phần
   - Cần tạo divide prompt phù hợp với cấu trúc tiếng Việt

2. **BM25 cho retrieval**:
   - Paper khẳng định BM25 đơn giản nhưng hiệu quả nhất cho MT few-shot → nên dùng BM25 làm default retriever
   - Hiệu quả hơn SONAR (dense retrieval) và LCS cho bài toán này

3. **Self-generated demonstrations**:
   - Thay vì chỉ truy xuất ví dụ từ pool, có thể để LLM tự tạo các cặp dịch trung gian → tận dụng tốt hơn khả năng nội tại
   - Đặc biệt hữu ích khi pool nhỏ hoặc thiếu diversity

4. **Ensembling CompTra + few-shot**:
   - Kết hợp output của CompTra và few-shot MT bằng quality estimation → đơn giản nhưng hiệu quả
   - Có thể dùng BLASER 2.0 QE hoặc COMET-QE để chọn bản dịch tốt hơn

5. **Phrase-level cultural knowledge injection**:
   - Ý tưởng decompose → dịch phrase → recombine có thể kết hợp với cultural knowledge base
   - Mỗi phrase có thể được augment với cultural context trước khi dịch

6. **Evaluation framework**:
   - Sử dụng cả MetricX-23 + XCOMET + BLEU + chrF++ cho comprehensive evaluation
   - Thêm reference-free metrics (MetricX-QE, COMETKIWI-QE) để giảm reference bias
   - Statistical significance testing (paper dùng bold cho results không statistically worse)

7. **MinWikiSplit cho decomposition**:
   - Có thể tạo Vietnamese MinWikiSplit tương tự để train decomposition prompt cho tiếng Việt
   - Hoặc dùng trực tiếp MinWikiSplit tiếng Anh nếu source là English

8. **NLLB + LLM hybrid**:
   - Dùng NLLB dịch phrases, LLM làm merger → kết hợp sức mạnh của cả hai
   - Phù hợp khi LLM few-shot yếu hơn supervised model cho ngôn ngữ đích

---

## 9. Các paper liên quan quan trọng

### Phương pháp dịch máy dựa trên LLM

| Paper | Nội dung | Đáng đọc vì |
|---|---|---|
| Zebaze et al., 2024a | In-context example selection via similarity search for LRL MT | Tiền thân trực tiếp của CompTra, chứng minh similarity search giúp LRL |
| Agrawal et al., 2023 | In-context examples selection for MT | Foundation work cho retrieval-based few-shot MT |
| Zhang et al., 2023a | Prompting LLM for MT: a case study | Template selection & example selection với LLM |
| Vilar et al., 2023 | Prompting PaLM for translation | Strategies cho few-shot MT |

### Decomposition & Prompting

| Paper | Nội dung | Đáng đọc vì |
|---|---|---|
| Puduppully et al., 2023 (DecoMT) | Decomposed prompting for MT | Tiền thân decomposition-based MT, so sánh trực tiếp |
| Ghazvininejad et al., 2023 (DiPMT) | Dictionary-based phrase-level prompting | Keyword-level augmentation cho MT |
| Lu et al., 2024 (CoD) | Chain-of-Dictionary prompting | Mở rộng DiPMT sang multilingual dictionary |
| He et al., 2024 (MAPS) | Multi-Aspect Prompting and Selection | Ensembling multiple perspectives |
| Briakou et al., 2024 (SBYS) | Translating Step-by-Step | Multi-turn MT pipeline |
| Feng et al., 2024 (TEaR) | Translate, Estimate, and Refine | Self-refinement cho MT |

### LLM & Low-resource Languages

| Paper | Nội dung | Đáng đọc vì |
|---|---|---|
| Hendy et al., 2023 | How good are GPT models at MT? | Đánh giá systematic LLM cho MT, phát hiện LRL challenge |
| Zhu et al., 2024 | Multilingual MT with LLMs (102 languages) | Phân tích rộng nhất về LLM MT đa ngôn ngữ |
| Costa-jussà et al., 2022 (NLLB) | No Language Left Behind | SOTA supervised multilingual MT |
| Tanzer et al., 2024 | Learning to translate from one grammar book | Benchmark cho LRL MT extreme case |

### Datasets & Metrics

| Paper | Nội dung | Đáng đọc vì |
|---|---|---|
| Goyal et al., 2022 (FLORES 200) | Evaluation benchmark for LRL MT | Standard benchmark cho LRL |
| Guerreiro et al., 2024 (XCOMET) | Transparent MT evaluation | Top-ranked MT metric |
| Juraska et al., 2023 (MetricX-23) | Google's MT metric | Top-ranked MT metric |
| Freitag et al., 2024 | WMT24 Metrics Shared Task | Latest comparison of MT metrics |

### Reasoning & Compositionality

| Paper | Nội dung | Đáng đọc vì |
|---|---|---|
| Wei et al., 2022 (CoT) | Chain-of-thought prompting | Foundation work cho reasoning |
| Khot et al., 2023 | Decomposed prompting for complex tasks | Lý thuyết decomposition |
| Zebaze et al., 2024b (Tree of Problems) | Compositionality for structured problem solving | Cùng nhóm tác giả, lý thuyết nền tảng |
| Niklaus et al., 2019 (MinWikiSplit) | Sentence splitting corpus | Dữ liệu dùng cho decomposition prompt |

---

*Ghi chú: File này được tạo ngày 13/05/2026 để phục vụ nghiên cứu MT low-resource.*
