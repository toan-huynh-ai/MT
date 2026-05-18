# RAGtrans: Retrieval-Augmented Machine Translation with Unstructured Knowledge

## 1. Thông tin paper

| Mục | Chi tiết |
|-----|----------|
| **Title** | Retrieval-Augmented Machine Translation with Unstructured Knowledge |
| **Authors** | Jiaan Wang, Fandong Meng (corresponding), Yingxue Zhang, Jie Zhou |
| **Affiliation** | Pattern Recognition Center, WeChat AI, Tencent Inc |
| **arXiv** | [2412.04342](https://arxiv.org/abs/2412.04342) |
| **GitHub** | [https://github.com/krystalan/RAGtrans](https://github.com/krystalan/RAGtrans) |
| **Năm** | 2024 |

---

## 2. Tóm tắt (Abstract)

Paper nghiên cứu việc áp dụng **Retrieval-Augmented Generation (RAG)** vào bài toán dịch máy (MT), nhưng thay vì dùng các nguồn tri thức truyền thống (cặp câu song ngữ, knowledge graph), tác giả tập trung vào **tri thức phi cấu trúc (unstructured knowledge)** từ các tài liệu văn bản — cụ thể là Wikipedia.

Đóng góp chính:
- Xây dựng **RAGtrans** — benchmark đầu tiên cho retrieval-augmented MT với tài liệu phi cấu trúc, gồm **169K mẫu dịch** được thu thập bởi GPT-4o và dịch giả chuyên nghiệp.
- Đề xuất phương pháp **multi-task training (CSC)** gồm 3 objective để dạy LLM cách sử dụng thông tin từ tài liệu đa ngôn ngữ khi dịch.
- Kết quả cải thiện đáng kể: **+1.6~3.1 BLEU** và **+1.0~2.0 COMET** (En→Zh), **+1.7~2.9 BLEU** và **+2.1~2.7 COMET** (En→De).

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Các hệ thống RAG cho MT trước đây chủ yếu dùng hai loại nguồn tri thức:
1. **In-context examples / Translation Memory**: Truy xuất cặp câu song ngữ tương tự từ bilingual corpora.
2. **Knowledge Graphs**: Truy xuất triplet từ knowledge graph có cấu trúc (VD: Wikidata).

**Hạn chế nghiêm trọng**: Phần lớn tri thức thế giới nằm trong **tài liệu phi cấu trúc** (bài viết Wikipedia, bài báo, sách...) và **không phải lúc nào cũng có song ngữ đầy đủ**. Ví dụ: một bài Wikipedia về một nhân vật lịch sử có thể rất chi tiết bằng tiếng Anh nhưng chỉ có vài dòng bằng tiếng Trung.

### Tại sao quan trọng?

- Khi dịch các câu **knowledge-intensive** (chứa tên riêng, thuật ngữ chuyên ngành, sự kiện lịch sử...), model cần thêm context/knowledge bên ngoài để dịch chính xác.
- Trong thực tế, retriever có thể trả về tài liệu bằng **nhiều ngôn ngữ khác nhau** (không chỉ ngôn ngữ nguồn và đích), model cần biết cách tận dụng tri thức đa ngôn ngữ này.
- Chưa có benchmark nào đánh giá khả năng retrieval-augmented MT với tài liệu phi cấu trúc.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Xây dựng RAGtrans Benchmark

#### 4.1.1 Chọn câu nguồn và tài liệu liên quan

Pipeline thu thập dữ liệu từ Wikipedia:

- **Câu nguồn**: Lấy **lead paragraph** (đoạn mở đầu) của các trang Wikipedia tiếng Anh được chọn ngẫu nhiên → đảm bảo câu chứa nội dung knowledge-intensive.
- **Tài liệu liên quan (relevant document)**: Các đoạn văn còn lại trên cùng trang Wikipedia (loại bỏ lead paragraph) → đảm bảo liên quan chặt chẽ với câu nguồn.
- **Tài liệu đa ngôn ngữ**: Khai thác các phiên bản Wikipedia song song bằng tiếng Trung (Zh), Đức (De), Pháp (Fr), Séc (Cs) → cũng loại bỏ lead paragraph để tránh answer leakage.
- **Tài liệu nhiễu (noisy document)**: Chọn ngẫu nhiên tài liệu từ Wikipedia khác để kiểm tra tính robust.

#### 4.1.2 Thu thập bản dịch

- **Training + Validation set**: Dịch bằng **GPT-4o** theo quy trình CoT (Chain-of-Thought):
  1. GPT-4o đánh giá độ liên quan của tài liệu (5-point scale)
  2. Sau đó dịch câu nguồn dựa trên thông tin đã đánh giá
- **Test set**: Dịch bởi **17 dịch giả chuyên nghiệp** (10 En→Zh, 7 En→De), với quy trình review bởi 5 reviewer.

#### 4.1.3 Quy mô dữ liệu

| | En→Zh | En→De |
|---|---|---|
| **Training** | 74,500 | 85,250 |
| **Validation** | 2,500 | 2,750 |
| **Test** | 2,000 | 2,000 |
| **Tổng** | **79,000** | **90,000** |

Mỗi mẫu là bộ ba `⟨s, d^l, t⟩`: câu nguồn (s), tài liệu ngôn ngữ l (d), và bản dịch (t).

Mỗi mẫu test là bộ năm `⟨s, d^en, d^zh, d^de, t⟩` (có tài liệu ở 3 ngôn ngữ).

#### 4.1.4 Ba setting đánh giá

1. **Golden Evaluation**: Cung cấp tài liệu liên quan chính xác → đo khả năng tận dụng tri thức.
2. **Robustness Evaluation**: Cung cấp tài liệu không liên quan → đo tính robust, model không bị "nhiễu" bởi thông tin sai.
3. **Full Wiki Evaluation**: Trang bị retriever (BM25 hoặc BGE-m3) để truy xuất tài liệu từ toàn bộ Wikipedia → đánh giá end-to-end.

---

### 4.2 Phương pháp Multi-Task Training (CSC)

CSC gồm **3 training objective** được thiết kế để dạy LLM sử dụng tri thức đa ngôn ngữ:

#### Objective 1: Cross-lingual Information Completion (CLIC)

- **Mục tiêu**: Dạy LLM tổng hợp và hoàn thiện thông tin từ tài liệu đa ngôn ngữ.
- **Cách tạo dữ liệu**: Từ Wikipedia, lấy lead paragraph làm summary `y`, cắt ngắn thành `ŷ`. Dùng thuật toán **MMR (Maximal Marginal Relevance)** để chọn các đoạn văn từ nhiều ngôn ngữ tạo thành tài liệu hỗn hợp `d_mix`. LLM phải hoàn thiện `ŷ` thành `y` dựa trên `d_mix`.
- **Công thức**: `Θ(y | d_mix, ŷ)`

#### Objective 2: Self-Knowledge-Enhanced Translation (SKET)

- **Mục tiêu**: Dạy LLM tự sinh ra tri thức liên quan rồi dùng nó để dịch.
- **Cách tạo dữ liệu**: Dùng TED talk corpus (đã có câu song ngữ). Cho LLM tự sinh tri thức liên quan `d̃^l` bằng ngôn ngữ l từ câu nguồn, rồi dùng tri thức đó để dịch.
- **Công thức**: `Θ(t | d̃^l | s)` — model vừa là "retriever" (sinh knowledge) vừa là "translator".
- **Ý tưởng lấy cảm hứng từ**: Self-RAG (Asai et al., 2024).

#### Objective 3: Cross-lingual Relevance Discrimination (CLRD)

- **Mục tiêu**: Dạy LLM phân biệt tài liệu liên quan vs. không liên quan khi chúng ở các ngôn ngữ khác nhau.
- **Cách tạo dữ liệu**: Từ Wikipedia song song — đoạn văn từ cùng trang Wikipedia = relevant, đoạn văn từ trang khác = irrelevant. Tạo cặp `⟨d^l1, d^l2⟩` với nhãn boolean.
- **Công thức**: `Θ(r | d^l1, d^l2)`

#### Ưu điểm thiết kế

- **Không cần gán nhãn mới**: Tất cả dữ liệu CSC đều được tạo tự động từ corpus có sẵn (Wikipedia, TED talks).
- **Mỗi objective 40K mẫu** trong thí nghiệm chính (tổng 120K mẫu CSC).
- Hiệu quả bắt đầu bão hòa khi vượt **120K mẫu CSC** (theo thí nghiệm scalability).

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Datasets

| Dataset | Mục đích |
|---------|----------|
| **RAGtrans** (169K mẫu) | Benchmark chính — train + eval retrieval-augmented MT |
| **Wikipedia dumps** (phiên bản 20241001) | Knowledge source cho full Wiki evaluation, gồm En, Zh, De, Fr, Cs, Ru, Ko, Ja |
| **TED talk corpus** (Aharoni et al., 2019) | Tạo mẫu cho SKET objective |

### 5.2 Metrics

| Metric | Loại | Mô tả |
|--------|------|-------|
| **BLEU** | Reference-based, lexical | Đo n-gram overlap giữa bản dịch và reference |
| **COMET** | Reference-based, semantic | Đo semantic similarity dựa trên model (wmt22-comet-da) |
| **GRB** | Reference-based, LLM-judge | GPT-4o đánh giá chất lượng dịch so với reference |
| **GRF** | Reference-free, LLM-judge | GPT-4o đánh giá chất lượng dịch không cần reference |

### 5.3 Backbone LLMs

| Model | Kích thước |
|-------|-----------|
| Qwen2.5-7B-Instruct | 7B |
| Qwen2.5-14B-Instruct | 14B |
| Llama-3-8B (Chinese-Instruct-v3) | 8B |
| Mistral-7B-Instruct-v0.3 | 7B |

### 5.4 Retrievers

| Retriever | Đặc điểm |
|-----------|----------|
| **BM25** | Lexical search, chỉ retrieve cùng ngôn ngữ |
| **BGE-m3** | Dense retrieval, hỗ trợ cross-lingual retrieval |

### 5.5 Training Setup

- Framework: **LlamaFactory**
- Hardware: 8× NVIDIA A100 (40G)
- Learning rate: 1e-5, batch size: 32 (8×4)
- Optimization: DeepSpeed ZeRO-2 (7B models) / ZeRO-3 (8B/14B models)
- Input truncation: 2K tokens
- Epochs: 2

---

## 6. Kết quả chính (Key Results)

### 6.1 Golden & Robustness Evaluation (Bảng 3)

**Quan sát chính từ Zero-Shot LLMs:**
- Khi nhận tài liệu nhiễu → hiệu suất **giảm** so với không có tài liệu (VD: Qwen2.5-7B En→Zh: 50.1→48.6 BLEU) → LLM zero-shot **thiếu robust**.
- Khi nhận tài liệu liên quan → hiệu suất **không tăng hoặc giảm** → LLM zero-shot **không biết cách tận dụng tri thức**.
- Khi tài liệu ở "ngôn ngữ thứ ba" (VD: tài liệu tiếng Đức cho dịch En→Zh) → hiệu suất **giảm mạnh**.

**Sau SFT trên RAGtrans:**
- Cải thiện lớn: VD Qwen2.5-7B En→Zh (empty doc): +4.5 BLEU, +2.1 COMET.
- Model **biết tận dụng** tài liệu liên quan (golden doc > empty doc).
- Model **robust hơn** — tài liệu nhiễu không làm giảm hiệu suất đáng kể.

**Sau SFT + CSC:**
- Cải thiện thêm so với SFT thuần:

| Setting | En→Zh (BLEU/COMET) | En→De (BLEU/COMET) |
|---------|---------------------|---------------------|
| Empty doc | +1.1~2.2 / +0.9~1.0 | +1.4~1.7 / +1.4~2.1 |
| Golden En doc | +1.6~2.2 / +1.0~1.0 | +2.3~2.5 / +1.9~2.1 |
| Golden 3rd-lang doc | +2.3~3.1 / +1.0~2.0 | +2.0~2.6 / +2.1~2.7 |

- **CSC đặc biệt hiệu quả** khi tài liệu ở ngôn ngữ thứ ba → nâng cao khả năng xử lý tri thức cross-lingual.

### 6.2 Full Wiki Evaluation (Bảng 4)

- Retrieve tài liệu từ Wikipedia thực sự **giúp cải thiện** dịch thuật so với empty document.
- **BGE-m3 > BM25**: Dense retriever hiệu quả hơn lexical retriever.
- Tài liệu từ ngôn ngữ khác (third language) cũng mang lại cải thiện trong setting full Wiki.
- Kết quả tốt nhất: Qwen2.5-14B + BGE-m3 từ Chinese Wikipedia cho En→Zh: **59.0 BLEU / 88.5 COMET**.

### 6.3 Ablation Study (Bảng 5 & 8)

| Loại tài liệu | Objective quan trọng nhất |
|----------------|--------------------------|
| Empty / Source-lang / Target-lang doc | **SKET** (Self-Knowledge-Enhanced Translation) |
| Third-language doc | **CLIC** và **CLRD** (Cross-lingual objectives) |

→ Mỗi objective đều đóng góp, nhưng tầm quan trọng tương đối thay đổi tùy setting.

### 6.4 Human Evaluation (Bảng 6 & 7)

- Lỗi phổ biến nhất: **Word-level** (3.5~8.17%) và **Phrase-level** (1.33~5.33%).
- CSC giảm lỗi word-level và phrase-level.
- **Phát hiện quan trọng**: Tài liệu tiếng Đức cho dịch En→Zh làm **tăng word-level error** (8.17% vs 5.5% empty) — vì model có xu hướng dịch entity sang tiếng Đức thay vì tiếng Trung khi thấy entity trong tài liệu tiếng Đức.

### 6.5 Scalability của CSC

- Hiệu quả bắt đầu bão hòa khi CSC samples > **120K**.
- Tăng từ 210K→240K mẫu **không cải thiện thêm**.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Bài toán mới, đúng thực tế**: Đây là paper đầu tiên nghiên cứu retrieval-augmented MT với tài liệu phi cấu trúc — một khoảng trống nghiên cứu quan trọng vì phần lớn tri thức thế giới nằm ở dạng unstructured.
2. **Benchmark chất lượng cao**: RAGtrans được thiết kế cẩn thận với test set do dịch giả chuyên nghiệp dịch, có quy trình review, và hỗ trợ 5 ngôn ngữ.
3. **Phương pháp CSC scalable**: Không cần gán nhãn mới, tận dụng corpus có sẵn để tạo training objectives → dễ mở rộng.
4. **Đánh giá toàn diện**: 3 setting đánh giá (Golden, Robustness, Full Wiki) + 4 metrics + human evaluation → kết quả đáng tin cậy.
5. **Phân tích sâu**: Ablation study chi tiết, thí nghiệm scalability, phân tích hiệu ứng của từng loại tài liệu.
6. **Phát hiện thú vị về third-language**: Chứng minh rằng tri thức ở ngôn ngữ thứ ba cũng có thể hữu ích cho dịch thuật, mở ra hướng nghiên cứu mới.

### Điểm yếu

1. **Giới hạn ngôn ngữ**: Chỉ thử nghiệm En→Zh và En→De, với tài liệu bổ sung bằng Fr, Cs. Chưa rõ phương pháp có hiệu quả với các cặp ngôn ngữ low-resource hay typologically distant hơn không.
2. **Phụ thuộc Wikipedia**: Source sentences và documents đều từ Wikipedia → có thể không đại diện cho các domain khác (y khoa, pháp luật, văn học...).
3. **Training data từ GPT-4o**: 165K/169K mẫu training dịch bởi GPT-4o → chất lượng phụ thuộc vào GPT-4o, có thể có bias, và model student có thể học theo phong cách dịch của GPT-4o thay vì dịch giả con người.
4. **Không dùng CoT khi SFT**: Paper thừa nhận trong Limitations — GPT-4o dùng CoT để dịch nhưng khi SFT lại không dạy model CoT reasoning, có thể bỏ lỡ cải thiện đáng kể.
5. **Vấn đề entity từ third-language**: Human evaluation cho thấy tài liệu tiếng Đức gây lỗi word-level nghiêm trọng cho En→Zh — model "bị nhiễu" bởi entity viết bằng ngôn ngữ thứ ba, nhưng paper chưa đề xuất giải pháp cụ thể.
6. **Bão hòa nhanh**: CSC bão hòa ở ~120K mẫu → room for improvement có thể hạn chế với approach hiện tại.
7. **Chi phí tính toán**: SFT+CSC cho Qwen2.5-14B tốn 208 GPU hours/epoch (so với 54 GPU hours cho SFT thuần) — gấp ~4x.

---

## 8. Ý tưởng có thể áp dụng

### 8.1 Cho bài toán MT của mình

1. **Xây dựng knowledge base từ Wikipedia tiếng Việt**: Tương tự RAGtrans, có thể thu thập tài liệu từ Wikipedia VN, EN, và các ngôn ngữ khác để hỗ trợ dịch En→Vi hoặc Vi→En, đặc biệt cho các câu chứa tri thức văn hóa.

2. **CSC training framework**: Ba objective (CLIC, SKET, CLRD) có thể áp dụng trực tiếp:
   - **CLIC**: Dạy model tổng hợp thông tin từ tài liệu cultural knowledge base đa ngôn ngữ.
   - **SKET**: Cho model tự sinh cultural context rồi dùng nó để dịch → đặc biệt hữu ích khi không có retriever mạnh.
   - **CLRD**: Dạy model phân biệt tài liệu liên quan/không liên quan → tăng robustness.

3. **Pipeline đánh giá 3 setting**: Có thể adopt Golden/Robustness/Full-Wiki evaluation cho benchmark MT cultural.

4. **Tận dụng tài liệu phi cấu trúc từ cultural KB**: `cultural_knowledge_base_v3.json` có thể được format thành unstructured documents và đưa vào model như retrieval context.

5. **MMR algorithm cho document selection**: Khi có nhiều nguồn tri thức đa ngôn ngữ, dùng MMR để chọn đoạn văn đa dạng nhất, tránh redundancy.

### 8.2 Bài học rút ra

- **Zero-shot LLM không biết cách dùng retrieved context cho MT** → cần SFT/fine-tuning.
- **Tài liệu ở ngôn ngữ thứ ba có thể gây hại** (entity confusion) → cần cẩn thận khi dùng cultural KB đa ngôn ngữ.
- **Robustness rất quan trọng**: Nên bao gồm noisy documents trong training để model học cách phân biệt và bỏ qua thông tin không liên quan.

---

## 9. Các paper liên quan quan trọng

### Retrieval-Augmented MT

| Paper | Nội dung | Venue |
|-------|----------|-------|
| **Conia et al. (2024)** — Cross-cultural MT with RAG from multilingual KGs | Dùng Wikidata (structured KG) cho cross-cultural MT | EMNLP 2024 |
| **Chen et al. (2024b)** — CRAT | Multi-agent framework cho causality-enhanced reflective & retrieval-augmented translation | arXiv 2024 |
| **Zhang et al. (2018)** — Guiding NMT with retrieved translation pieces | Retrieve sentence pairs tương tự để hướng dẫn NMT | NAACL 2018 |
| **Khandelwal et al. (2021)** — kNN-MT | Nearest neighbor machine translation | ICLR 2021 |
| **Bulte & Tezcan (2019)** — Neural Fuzzy Repair | Fuzzy retriever cho translation memory | ACL 2019 |
| **Cai et al. (2021)** — NMT with Monolingual Translation Memory | Relax bilingualism constraint, retrieve target-lang sentences | ACL 2021 |

### RAG & Self-RAG

| Paper | Nội dung |
|-------|----------|
| **Asai et al. (2024)** — Self-RAG | Model tự học retrieve, generate, và critique thông qua self-reflection (ICLR 2024) |
| **Wang et al. (2023b)** — Self-Knowledge Guided RAG | Dùng self-knowledge để hướng dẫn retrieval cho LLM |
| **Gao et al. (2023)** — RAG Survey | Survey toàn diện về RAG cho LLM |

### Cross-lingual & Multilingual

| Paper | Nội dung |
|-------|----------|
| **Perez-Beltrachini & Lapata (2021)** — Cross-lingual Summarisation | Models và datasets cho cross-lingual summarisation từ Wikipedia (EMNLP 2021) |
| **Aharoni et al. (2019)** — Massively Multilingual NMT | NMT đa ngôn ngữ quy mô lớn (NAACL 2019) |
| **Chen et al. (2024a)** — BGE-m3 | Multilingual, multi-functionality text embeddings |

### LLM Backbones & Tools

| Paper | Nội dung |
|-------|----------|
| **Yang et al. (2024)** — Qwen2.5 Technical Report | Backbone LLM chính trong thí nghiệm |
| **Zheng et al. (2024)** — LlamaFactory | Framework fine-tuning LLM được dùng trong paper (ACL 2024 Demo) |
| **Rei et al. (2022)** — CometKiwi / COMET | Metric đánh giá chất lượng dịch (WMT 2022) |

### Đáng đọc thêm (ưu tiên cao)

1. **Conia et al. (2024)** — So sánh trực tiếp: structured KG vs unstructured documents cho cross-cultural MT.
2. **Asai et al. (2024) — Self-RAG** — Ý tưởng gốc cho SKET objective.
3. **Perez-Beltrachini & Lapata (2021)** — Cách khai thác Wikipedia đa ngôn ngữ cho NLP tasks.
4. **Cai et al. (2021)** — Monolingual translation memory — relaxing bilingualism constraint.
