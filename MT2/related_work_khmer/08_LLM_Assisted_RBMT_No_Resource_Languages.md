# Tóm tắt Paper: LLM-Assisted Rule Based Machine Translation for Low/No-Resource Languages

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | LLM-Assisted Rule Based Machine Translation for Low/No-Resource Languages |
| **Authors** | Jared Coleman, Bhaskar Krishnamachari, Khalil Iskarous (University of Southern California), Ruben Rosales |
| **Venue** | arXiv preprint |
| **Year** | 2024 (May 16) |
| **arXiv** | [2405.08997](https://arxiv.org/abs/2405.08997) |
| **Code** | [github.com/kubishi/kubishi_sentences](https://github.com/kubishi/kubishi_sentences) |
| **Ngôn ngữ mục tiêu** | Owens Valley Paiute (OVP) — ngôn ngữ thổ dân Mỹ cực kỳ nguy cấp, thuộc họ Uto-Aztecan, ISO 639-3: `mnr` |

---

## 2. Tóm tắt (Abstract)

Paper đề xuất mô hình dịch máy mới: **LLM-RBMT** (LLM-Assisted Rule-Based Machine Translation), đặc biệt phù hợp cho **ngôn ngữ no-resource** — những ngôn ngữ không có bất kỳ corpus song ngữ hoặc đơn ngữ nào được công bố.

Sử dụng paradigm LLM-RBMT, nhóm tác giả xây dựng **hệ thống dịch máy đầu tiên** cho Owens Valley Paiute (OVP), hướng tới mục tiêu **giáo dục ngôn ngữ và phục hồi ngôn ngữ** (language revitalization). Hệ thống gồm ba thành phần:

1. **Sentence builder** dựa trên luật cho OVP
2. **OVP → English translator** (đạt 98% chính xác trên 100 câu ngẫu nhiên)
3. **English → OVP translator** (dịch câu tiếng Anh tùy ý sang OVP)

Phương pháp đánh giá sử dụng **semantic similarity** thay cho BLEU do không tồn tại parallel corpus.

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Các LLM (GPT-4, PaLM,...) hoạt động tốt với ngôn ngữ high-resource nhưng **thất bại** với ngôn ngữ low/no-resource vì chúng hầu như không xuất hiện trong dữ liệu huấn luyện. Phần lớn nghiên cứu MT tập trung vào low-resource (ít dữ liệu), nhưng **no-resource** (không có dữ liệu nào) gần như bị bỏ qua trong nghiên cứu.

### Ngữ cảnh cụ thể: Owens Valley Paiute

- Là ngôn ngữ **critically endangered** theo UNESCO Atlas of World's Languages in Danger.
- **Không có** bất kỳ corpus song ngữ hay đơn ngữ nào được công bố công khai.
- Thuộc họ ngôn ngữ Uto-Aztecan (thổ dân châu Mỹ).
- Mọi kiến thức ngôn ngữ học đều nằm trong tài liệu ngữ pháp và từ điển của các chuyên gia.

### Tại sao quan trọng?

- Hàng nghìn ngôn ngữ trên thế giới đang đối mặt nguy cơ tuyệt chủng.
- Các phương pháp NMT, transfer learning, semi-supervised learning đều **không áp dụng được** khi không có corpus.
- Cần một paradigm mới cho phép xây dựng công cụ dịch **mà không cần parallel data**.
- Công cụ dịch có thể hỗ trợ **giáo dục và phục hồi ngôn ngữ** (language revitalization).

### Hạn chế của các phương pháp hiện có

| Phương pháp | Yêu cầu dữ liệu | Áp dụng cho no-resource? |
|---|---|---|
| Supervised NMT | Parallel corpus lớn | ❌ |
| Unsupervised NMT | Monolingual corpus | ❌ |
| Transfer learning | Related language data | ❌ (thường không có) |
| Fine-tuning LLM | Bilingual corpus | ❌ |
| RBMT truyền thống | Luật ngữ pháp + từ điển | ✅ nhưng cần chuyên gia lập trình |
| **LLM-RBMT (đề xuất)** | Luật ngữ pháp + từ điển nhỏ | ✅ |

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1. Ý tưởng cốt lõi

> Con người có thể dịch câu đơn giản trong ngôn ngữ họ không biết, nếu được cung cấp đủ bảng chia động từ và từ vựng — giống sinh viên làm bài tập ngôn ngữ.

LLM-RBMT tận dụng khả năng ngôn ngữ tổng quát của LLM nhưng **không yêu cầu LLM biết ngôn ngữ đích**. LLM chỉ làm việc với tiếng Anh và cấu trúc JSON. Phần dịch thực sự do **rule-based engine** đảm nhiệm.

### 4.2. Kiến trúc tổng thể (Pipeline)

Hệ thống gồm **3 thành phần chính**:

#### Component 1: OVP Sentence Builder (Rule-Based)

- Cho phép xây dựng câu OVP hợp lệ theo cấu trúc SV (subject-verb) hoặc SVO (subject-verb-object).
- Người dùng chọn từng thành phần từ danh sách:
  - **Subject**: danh từ hoặc đại từ chủ ngữ
  - **Subject Suffix**: `-ii` (proximal — gần người nói) hoặc `-uu` (distal — xa người nói)
  - **Verb**: động từ (có/không có tân ngữ)
  - **Verb Suffix**: biểu thị thì/thể (past, present, future, continuous, perfect)
  - **Object**: tân ngữ (chỉ khi động từ là ngoại động từ)
  - **Object Suffix**: `-(n)eika` (proximal) hoặc `-(n)oka` (distal)
  - **Verb Object Pronoun Prefix**: đại từ tân ngữ gắn trước động từ (bắt buộc với ngoại động từ)
- Hệ thống **tự động kiểm tra tính hợp lệ**: danh sách lựa chọn thay đổi động dựa trên các lựa chọn trước đó.
- Toàn bộ từ vựng khả dụng: **14 ngoại động từ, 21 nội động từ, 33 danh từ, 6 hậu tố thì, 12 đại từ chủ ngữ**.

#### Component 2: OVP → English Translator (LLM-assisted)

**Pipeline:**
1. Sentence builder tạo câu OVP hợp lệ.
2. Encode thông tin câu thành **cấu trúc JSON chỉ dùng tiếng Anh** (dựa trên định nghĩa từ vựng):
   - Subject + proximity
   - Object + proximity
   - Verb + tense/aspect
3. Dùng **few-shot prompting** với LLM (gpt-3.5-turbo) để chuyển cấu trúc JSON → câu tiếng Anh tự nhiên.

**Điểm mấu chốt**: LLM **không bao giờ tiếp xúc trực tiếp** với ngôn ngữ OVP. LLM chỉ xử lý dữ liệu cấu trúc bằng tiếng Anh.

**Ví dụ:**
```
OVP:  Wo'ada-ii pagwi-noka u-zawa-dü.
JSON: [{'part_of_speech': 'subject', 'positional': 'proximal', 'word': 'mosquito'},
       {'part_of_speech': 'object', 'positional': 'distal', 'word': 'fish'},
       {'part_of_speech': 'verb', 'tense': 'present', 'word': 'cook'}]
EN:   This mosquito is cooking that fish.
```

#### Component 3: English → OVP Translator (LLM-assisted)

Đây là thành phần phức tạp nhất, cho phép dịch **câu tiếng Anh tùy ý** sang OVP.

**Pipeline (4 bước):**

1. **Sentence Segmenter** (LLM-powered): Phân tách câu đầu vào thành tập hợp câu đơn giản dạng SV/SVO.
   - Loại bỏ tính từ, trạng từ, giới từ, liên từ.
   - Giữ lại càng nhiều ngữ nghĩa càng tốt.
   - Sử dụng few-shot prompting + OpenAI function calling để đảm bảo output format JSON nhất quán.

2. **Vocabulary Matching**: Map các từ trong câu đơn giản sang từ vựng có sẵn trong OVP sentence builder.
   - Nếu từ không có → giữ nguyên dạng `[unknown_word]` (partial translation).

3. **OVP Sentence Construction**: Dùng sentence builder để xây câu OVP hợp lệ.

4. **Round-trip Verification**: Dịch ngược OVP → English bằng component 2 để người dùng kiểm chứng.

**Ví dụ hoàn chỉnh:**
```
Input:     "We are playing and laughing."
Simple:    [{'subject': 'we', 'verb': 'play', 'tense': 'present_continuous'},
            {'subject': 'we', 'verb': 'laugh', 'tense': 'present_continuous'}]
OVP:       "tübinohi-ti nüügwa. nishua'i-ti nüügwa."
Backwards: "We are playing. We are laughing."
```

### 4.3. Khả năng dịch một phần (Partial Translation)

Một **ưu điểm quan trọng** của paradigm: khi từ vựng không đầy đủ, hệ thống vẫn cho **bản dịch một phần** thay vì thất bại hoàn toàn.

```
Input:     "Birds will migrate and return."
OVP:       "[migrate]-wei tsiipa-uu. [return]-wei tiipa-uu."
Backwards: "That bird will migrate. That bird will return."
```

→ Người học vẫn thấy được **cấu trúc câu** đúng dù thiếu một vài từ vựng.

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1. Đánh giá OVP → English

- **Dataset**: 100 câu OVP ngẫu nhiên được tạo bởi sentence builder.
- **Model**: gpt-3.5-turbo
- **Metric**: Đánh giá nhị phân (accurate / inaccurate) bởi chuyên gia.
- **Kết quả**: **98/100** câu dịch chính xác.

### 5.2. Đánh giá English → OVP

#### Dataset test
- **125 câu tiếng Anh**, chia thành 5 loại (25 câu mỗi loại):

| Loại câu | Ví dụ |
|---|---|
| Subject-Verb (SV) | "I read", "She sings" |
| Subject-Verb-Object (SVO) | "Mom made dinner", "John read a book" |
| Two-verb | "She sings and dances", "I ate while watching TV" |
| Two-clause | "My brother drove and I waited" |
| Complex | "Rachel and Monica share an apartment" |

- **2 models**: gpt-3.5-turbo và gpt-4
- **Tổng**: 250 bản dịch (125 câu × 2 models)

#### Metrics: Semantic Similarity

Do không có parallel corpus, tác giả dùng **cosine similarity** giữa embeddings của các câu. Ba chỉ số:

| Metric | Ý nghĩa |
|---|---|
| **Simple** | Similarity giữa câu gốc và các câu đơn giản sau segmentation |
| **Comparator** | Similarity giữa câu gốc và câu đơn giản *sau khi loại bỏ từ vựng không có* → giới hạn trên với vocab hiện có |
| **Backwards** | Similarity giữa câu gốc và câu dịch ngược (OVP → EN) → chất lượng dịch thực tế |

#### Chọn Embedding Model

Đánh giá 7 embedding models trên 12 câu mục tiêu, mỗi câu có 10 câu xếp hạng theo mức tương đồng ngữ nghĩa (do con người đánh giá).

| Embedding Model | Avg Displacement ↓ | RBO ↑ |
|---|---|---|
| text-embedding-ada-002 | 0.967 ± 0.442 | 0.885 ± 0.053 |
| **all-MiniLM-L6-v2** | **0.933 ± 0.323** | **0.884 ± 0.050** |
| text-embedding-3-small | 1.000 ± 0.362 | 0.882 ± 0.051 |
| text-embedding-3-large | 0.917 ± 0.463 | 0.882 ± 0.054 |
| paraphrase-MiniLM-L6-v2 | 1.150 ± 0.410 | 0.870 ± 0.054 |
| bert-base-uncased | 1.600 ± 0.703 | 0.777 ± 0.100 |
| spacy/en_core_web_md | 1.833 ± 0.466 | 0.760 ± 0.090 |

→ Chọn **all-MiniLM-L6-v2** vì cân bằng tốt giữa cả hai metrics.

#### Baseline

- **Baseline similarity** (giữa các câu không liên quan trong dataset): μ ≈ 0.574, σ ≈ 0.061
- Phân phối xấp xỉ Gaussian → câu có similarity > μ + 3σ ≈ **0.757** gần như chắc chắn có liên quan ngữ nghĩa.

---

## 6. Kết quả chính (Key Results)

### 6.1. OVP → English: 98% accuracy

Trên 100 câu ngẫu nhiên, chỉ 2 câu dịch sai (gpt-3.5-turbo). Hệ thống rất đáng tin cậy cho các câu đơn giản SV/SVO.

### 6.2. English → OVP: Semantic Similarity Scores

| Model | Loại câu | Simple ↑ | Comparator | Backwards ↑ |
|---|---|---|---|---|
| gpt-3.5-turbo | Subject-Verb | 0.941 | — | — |
| | Subject-Verb-Object | 0.869 | — | — |
| | Two-verb | 0.906 | — | — |
| | Two-clause | 0.879 | — | — |
| | Complex | 0.829 | — | — |
| gpt-4 | Subject-Verb | 0.941 | — | — |
| | Subject-Verb-Object | 0.866 | — | — |
| | Two-verb | 0.905 | — | — |
| | Two-clause | 0.877 | — | — |
| | Complex | 0.830 | — | — |

### 6.3. Nhận xét quan trọng

- **Simple và Backwards scores luôn cao hơn Comparator** → chất lượng dịch bị giới hạn chủ yếu bởi **từ vựng**, không phải bởi khả năng của hệ thống. Mở rộng từ vựng sẽ cải thiện đáng kể.
- **gpt-3.5-turbo hoạt động gần ngang gpt-4** trong bài toán này, nhưng rẻ hơn rất nhiều:
  - Chi phí chạy toàn bộ 125 câu: **$0.09** (gpt-3.5-turbo) vs **$5.48** (gpt-4) — chênh lệch ~60x.
- **Câu đơn giản (SV)** đạt điểm cao nhất (~0.94), **câu phức tạp** đạt điểm thấp nhất (~0.83) nhưng vẫn vượt xa baseline (0.574).

### 6.4. Phân tích các trường hợp đặc biệt

| Trường hợp | Simple | Comparator | Backwards | Giải thích |
|---|---|---|---|---|
| Dịch hoàn hảo | 1.0 | 1.0 | 1.0 | "I am swimming" → perfect |
| Thiếu từ vựng | Cao | Thấp | Cao | Từ vựng bị thiếu nhưng cấu trúc đúng → partial translation |
| Mất nghĩa khi segment | Thấp | — | — | LLM chọn sai động từ chủ đề khi phân tách câu |
| Khác biệt ngữ pháp | Cao | Cao | Thấp | OVP không phân biệt giới tính đại từ → "she" → "he" khi dịch ngược |

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Không cần parallel corpus**: Điểm khác biệt lớn nhất — chỉ cần kiến thức ngữ pháp và từ điển nhỏ, hoàn toàn khả thi cho ngôn ngữ no-resource.
2. **LLM không cần biết ngôn ngữ đích**: LLM chỉ xử lý tiếng Anh và JSON, tránh hoàn toàn vấn đề hallucination trong ngôn ngữ lạ.
3. **Partial translation**: Hệ thống vẫn cho kết quả hữu ích khi thiếu từ vựng — rất có giá trị cho người học.
4. **Dễ mở rộng**: Thêm từ vựng mới (danh từ, động từ) rất đơn giản, không cần retrain.
5. **Chi phí thấp**: gpt-3.5-turbo cho kết quả gần tương đương gpt-4 với chi phí chỉ ~1.6% ($0.09 vs $5.48).
6. **Round-trip verification**: Dịch ngược để người dùng xác nhận chất lượng — tăng niềm tin.
7. **Hướng đến giáo dục**: Công cụ giúp người học hiểu cấu trúc câu, không chỉ là dịch máy thuần túy.
8. **Open-source**: Code được công bố hoàn toàn.

### Điểm yếu

1. **Giới hạn cấu trúc câu**: Chỉ hỗ trợ SV và SVO đơn giản — không có tính từ, trạng từ, giới từ, mệnh đề quan hệ, câu điều kiện,...
2. **Từ vựng cực kỳ nhỏ**: 14 ngoại động từ, 21 nội động từ, 33 danh từ — quá hạn chế cho giao tiếp thực tế.
3. **Mất thông tin khi segmentation**: Khi LLM phân tách câu phức thành câu đơn, các sắc thái ngữ nghĩa bị mất (adverbs, adjectives, prepositions).
4. **Phụ thuộc chuyên gia**: Xây dựng sentence builder **bắt buộc** cần chuyên gia ngôn ngữ OVP để định nghĩa luật.
5. **Thiếu evaluation bởi native speakers**: Đánh giá chủ yếu dựa trên semantic similarity tự động, không có đánh giá từ người bản ngữ OVP.
6. **Không xử lý được morphology phức tạp**: Hệ thống hiện tại chỉ xử lý suffix/prefix cơ bản, ngôn ngữ có hệ thống hình thái học phức tạp hơn sẽ rất khó áp dụng.
7. **Ambiguity trong OVP**: Ví dụ OVP không phân biệt giới tính đại từ, suffix `-ti` dùng cho cả present continuous và past continuous — dịch ngược có thể sai.
8. **Chưa so sánh với RBMT baselines khác**: Không có so sánh trực tiếp với Apertium hay các hệ thống RBMT truyền thống.
9. **Semantic similarity không phải gold standard**: Metric đánh giá chỉ là proxy, không thay thế được human evaluation.

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT với ngôn ngữ endangered/no-resource

1. **Paradigm LLM-as-structured-translator**: Ý tưởng dùng LLM làm "bộ xử lý ngôn ngữ tự nhiên" mà không cần nó biết ngôn ngữ đích — áp dụng được cho bất kỳ ngôn ngữ nào có tài liệu ngữ pháp tối thiểu.

2. **Partial translation cho giáo dục**: Thay vì fail khi thiếu từ vựng, hệ thống đưa ra bản dịch một phần. Rất phù hợp cho tools hỗ trợ người học ngôn ngữ.

3. **Round-trip evaluation**: Khi không có parallel corpus, dịch A → B → A' rồi so sánh A với A' bằng semantic similarity là cách đánh giá khả thi.

4. **Sentence segmentation as preprocessing**: Phân tách câu phức thành tập câu đơn giản trước khi dịch — có thể tích hợp vào pipeline KB-augmented MT.

5. **Kết hợp với knowledge base**: Paper gợi ý hướng **RAG** (Retrieval-Augmented Generation) — tìm kiếm cấu trúc câu, từ vựng, luật ngữ pháp trong KB rồi dịch zero-shot. Rất liên quan đến hướng nghiên cứu dùng cultural knowledge base cho MT.

6. **Template-based generation**: Sentence builder về bản chất là template-based generation — có thể mở rộng bằng cách tạo nhiều template phức tạp hơn thay vì chỉ SV/SVO.

7. **Cost-effective**: gpt-3.5-turbo cho kết quả gần gpt-4 → có thể dùng model nhỏ/rẻ hơn cho các bước structuring/segmentation.

### Bài học cho thiết kế hệ thống

- **Tách biệt "hiểu ngôn ngữ" và "biết ngôn ngữ"**: LLM hiểu cấu trúc ngôn ngữ tổng quát (hiểu) nhưng không cần biết ngôn ngữ cụ thể (biết). Rule-based engine bổ sung phần "biết".
- **Modular pipeline**: Mỗi component có thể đánh giá và cải thiện độc lập.
- **Expert knowledge remains essential**: Dù có LLM, kiến thức chuyên gia về ngôn ngữ đích vẫn không thể thay thế hoàn toàn.

---

## 9. Các paper liên quan quan trọng

### Surveys & Overviews

| Paper | Nội dung | Tại sao đáng đọc |
|---|---|---|
| Ranathunga et al. (2023) - *Neural MT for Low-Resource Languages: A Survey* | Survey toàn diện nhất về NMT cho ngôn ngữ low-resource | Phân loại kỹ thuật, hướng dẫn chọn phương pháp, future directions |
| Muennighoff et al. (2023) - *MTEB: Massive Text Embedding Benchmark* | Benchmark toàn diện cho embedding models | Cơ sở cho việc chọn embedding model đánh giá semantic similarity |

### LLM & Machine Translation

| Paper | Nội dung |
|---|---|
| Hendy et al. (2023) - *How Good Are GPT Models at Machine Translation?* | Đánh giá toàn diện GPT cho MT |
| Robinson et al. (2023) - *ChatGPT MT: Competitive for High- (but not Low-) Resource Languages* | Chứng minh ChatGPT kém với ngôn ngữ low-resource |
| Chowdhery et al. (2022) - *PaLM: Scaling Language Modeling with Pathways* | LLM scale lớn vẫn struggle với low-resource languages |
| Lankford et al. (2023) - *adaptMLLM: Fine-tuning Multilingual LMs on Low-Resource Languages* | Fine-tuning LLM cho low-resource (cần bilingual data → không áp dụng cho no-resource) |

### Rule-Based MT

| Paper | Nội dung |
|---|---|
| Khanna et al. (2021) - *Recent Advances in Apertium* | Hệ thống RBMT mã nguồn mở cho ngôn ngữ ít tài nguyên |
| Pirinen (2019) - *Workflows for Kickstarting RBMT in Virtually No-Resource Situation* | Workflow xây RBMT khi gần như không có dữ liệu — rất liên quan |
| Torregrosa et al. (2019) - *Leveraging RBMT Knowledge for Under-Resourced NMT Models* | Kết hợp RBMT và NMT cho ngôn ngữ ít tài nguyên |

### Semantic Similarity for MT Evaluation

| Paper | Nội dung |
|---|---|
| Cao et al. (2022) - *SemMT: Semantic-Based Testing for MT Systems* | Dùng semantic similarity đánh giá MT |
| Song et al. (2021) - *SentSim: Crosslingual Semantic Evaluation of MT* | Đánh giá MT bằng semantic similarity đa ngôn ngữ |

### Language Revitalization

| Paper | Nội dung |
|---|---|
| Coronel-Molina & McCarty (2016) - *Indigenous Language Revitalization in the Americas* | Tổng quan nỗ lực phục hồi ngôn ngữ bản địa |
| Baird (2016) - *Wopanaak Language Reclamation Program* | Case study phục hồi ngôn ngữ Wampanoag |
| Taylor & Kochem (2022) - *Access and Empowerment in Digital Language Learning* | Review công nghệ số trong duy trì/phục hồi ngôn ngữ |

### Retrieval-Augmented Generation (hướng mở rộng)

| Paper | Nội dung |
|---|---|
| Lewis et al. (2020) - *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* | RAG framework gốc — tác giả gợi ý đây là hướng mở rộng tiềm năng cho LLM-RBMT |

---

## 10. Tóm tắt một dòng

> **LLM-RBMT** tách rời vai trò "hiểu ngôn ngữ tổng quát" (LLM) và "biết ngôn ngữ đích" (rule-based engine), cho phép xây dựng hệ thống dịch máy cho ngôn ngữ no-resource mà không cần bất kỳ parallel corpus nào — một paradigm shift quan trọng cho MT endangered languages.
