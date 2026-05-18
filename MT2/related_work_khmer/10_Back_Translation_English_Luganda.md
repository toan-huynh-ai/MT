# Tóm tắt Paper: Data Augmentation With Back Translation for Low Resource Languages — English & Luganda

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Data Augmentation With Back Translation for Low Resource Languages: A case of English and Luganda |
| **Authors** | Richard Kimera (Mbarara University of Science and Technology), DongNyeong Heo, Daniela N. Rim, Heeyoul Choi (Handong Global University) |
| **Venue** | NLPIR 2024 — 8th International Conference on Natural Language Processing and Information Retrieval (Okayama, Japan) |
| **Year** | 2024 |
| **arXiv** | [2505.02463](https://arxiv.org/abs/2505.02463) |
| **DOI** | 10.1145/3711542.3711594 |
| **Affiliations** | Mbarara University of Science and Technology (Uganda), Handong Global University (South Korea) |

---

## 2. Tóm tắt (Abstract)

Paper khảo sát việc sử dụng **Back Translation (BT)** như một kỹ thuật bán giám sát (semi-supervised) để nâng cao chất lượng mô hình **Neural Machine Translation (NMT)** cho cặp ngôn ngữ **English–Luganda**, đặc biệt nhắm vào thách thức của ngôn ngữ ít tài nguyên (low-resource languages — LRLs).

Đóng góp chính:

1. **Xây dựng bộ dữ liệu** song ngữ và đơn ngữ từ các nguồn công khai + web crawling, cung cấp công khai để cộng đồng tái sử dụng.
2. **Đề xuất OurBT** — phương pháp back translation kết hợp Iterative BT và Incremental BT, với cơ chế **chọn tập dữ liệu đơn ngữ tối ưu** dựa trên BLEU score.
3. **Đạt cải thiện >10 BLEU** so với mô hình bilingual cơ sở cho cả hai chiều dịch (Eng→Lug và Lug→Eng).
4. **Sử dụng đa metric**: SacreBLEU, ChrF2, TER bên cạnh BLEU — phù hợp hơn cho ngôn ngữ giàu hình thái học (morphologically rich).

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

- **Thiếu hụt dữ liệu song ngữ nghiêm trọng** cho ngôn ngữ Luganda (và các ngôn ngữ châu Phi nói chung), khiến việc huấn luyện mô hình NMT chất lượng cao gần như bất khả thi.
- Luganda được nói bởi **hơn 20 triệu người** tại Uganda và các nước lân cận, nhưng sự hiện diện kỹ thuật số (digital presence) rất hạn chế.
- Các bộ dữ liệu đơn ngữ dùng cho BT trong nghiên cứu trước đó **không được công khai**, làm trầm trọng thêm vấn đề khan hiếm dữ liệu và cản trở khả năng tái tạo kết quả.

### Đặc điểm của Luganda gây khó cho MT

| Đặc điểm | Tác động |
|---|---|
| **Morphologically rich** (agglutinative) | Từ được cấu tạo phức tạp bằng prefix, suffix, infix → vocabulary explosion |
| **10 noun classes** | Lớp danh từ ảnh hưởng trực tiếp đến cấu trúc câu |
| **Phonemic distinction** | Sự khác biệt nhỏ về phát âm thay đổi hoàn toàn nghĩa (ví dụ: "kuta" = thả, "kutta" = giết) |
| **Thuộc nhóm ngôn ngữ Bantu** | Chia sẻ đặc điểm với nhiều ngôn ngữ châu Phi khác → kết quả có thể tổng quát hóa |

### Khoảng trống nghiên cứu (Research gaps)

1. Các công trình trước chỉ áp dụng **Standard BT** đơn giản, chưa khám phá cách **kết hợp chiến lược** nhiều nguồn dữ liệu đơn ngữ.
2. Dữ liệu đơn ngữ dùng trong nghiên cứu trước **không công khai** → không thể so sánh và tái tạo.
3. Đánh giá chỉ dựa trên **BLEU score** — không đủ cho ngôn ngữ giàu hình thái học.

### Tại sao quan trọng?

- Bất bình đẳng công nghệ: ngôn ngữ high-resource phát triển nhanh trong lĩnh vực số, ngôn ngữ low-resource bị bỏ lại phía sau.
- Hạn chế truy cập thông tin và công nghệ cho người nói LRLs.
- Tiềm ẩn nguy cơ suy giảm ngôn ngữ trong kỷ nguyên số.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1. Pipeline tổng quan

Paper triển khai **3 giai đoạn** chính:

```
Phase 1: Thu thập & xây dựng dữ liệu
    ├── Bilingual data từ open-source repositories
    └── Monolingual data từ open-source + web crawling

Phase 2: Huấn luyện mô hình bilingual cơ sở
    └── Transformer base model trên bilingual data

Phase 3: Back Translation
    ├── Standard BT
    ├── Incremental BT (IncBT)
    ├── Iterative BT (IteBT)
    └── OurBT (phương pháp đề xuất)
```

### 4.2. Thu thập dữ liệu

#### Dữ liệu song ngữ (Bilingual)

| Dataset | Số câu | Nguồn |
|---|---|---|
| NMT for English and Luganda | 41.070 | Kimera et al. 2022 |
| Translation Initiative for Covid-19 (TICO-19) | 15.022 | Anastasopoulos et al. 2020 |
| Makerere Sentiment Corpus | 10.000 | Babirye et al. 2023 |
| Bible WorldProject | 32.291 | Web scraped |
| **Tổng** | **~98.383** | |

#### Dữ liệu đơn ngữ English

| Dataset | Số câu | Nguồn |
|---|---|---|
| Digital Umuganda | 14.400 | HuggingFace |
| Gamayun Mini kit | 5.000 | Gamayun |
| Tatoeba | 1.000.000 | Tatoeba |
| YouTube news headlines + websites | 20.005 | Web scraped |
| Softpower news articles | 49.945 | Web scraped |
| Chimpreports news articles | 90.284 | Web scraped |

#### Dữ liệu đơn ngữ Luganda

| Dataset | Số câu | Nguồn |
|---|---|---|
| Mozilla Common Voice | 128.491 | HuggingFace |
| cc-100 (Web Crawl) | 78.556 | Conneau et al. 2019 |
| Masakhane | 9.809 | Adelani et al. 2023 |
| Makerere Radio Dataset | 11.550 | Mukiibi et al. 2022 |
| Makerere Text and Speech | 100.000 | Mukiibi et al. 2023 |
| YouTube news headlines (Luganda) | 5.253 | Web scraped |

→ Dữ liệu web crawled được trích xuất bằng **Selenium API**, sau đó làm sạch (loại bỏ hyperlinks, text trùng lặp, code-mixed text, khoảng trắng thừa, ký tự đặc biệt).

### 4.3. Kiến trúc mô hình

- **Transformer base** (Vaswani et al. 2017): N=6 layers, d_model=512, d_ff=2048, h=8 heads, d_k=d_v=64, P_drop=0.1
- **BPE** (Byte-Pair Encoding): vocabulary 10.000 subword units — dùng chung giữa mô hình bilingual và BT
- **Beam search** để sinh dữ liệu tổng hợp khi dịch monolingual data

### 4.4. Các kỹ thuật Back Translation

#### Standard BT (Sennrich et al. 2015)

Quy trình cơ bản: Huấn luyện model → Dịch monolingual data → Merge synthetic + bilingual → Retrain.

#### Incremental BT (IncBT)

Tăng dần lượng dữ liệu đơn ngữ theo từng phần (portions), mỗi lần thêm một tập dữ liệu mới.

#### Iterative BT (IteBT)

Lặp lại quá trình BT nhiều lần cho đến khi convergence (trong paper: 4 iterations cho đến khi convergence tại iteration 3).

#### OurBT — Phương pháp đề xuất (Algorithm 1)

Đây là đóng góp kỹ thuật chính của paper. Ý tưởng cốt lõi: **không phải tất cả monolingual data đều hữu ích như nhau** — cần chọn lọc tổ hợp dataset tối ưu.

**Quy trình chi tiết:**

1. **Khởi tạo**: Huấn luyện 2 mô hình M_EL (Eng→Lug) và M_LE (Lug→Eng) trên bilingual data D.
2. **Vòng lặp qua N tập monolingual** (mỗi tập từ nguồn khác nhau):
   - Dùng M_LE dịch monolingual Luganda thứ i → synthetic English
   - Dùng M_EL dịch monolingual English thứ i → synthetic Luganda
   - Retrain M_EL và M_LE trên dữ liệu tổng hợp tương ứng
3. **Chọn tổ hợp tối ưu**: Dựa trên BLEU score, chọn:
   - Dataset combination tốt nhất (L_best, E_best)
   - Model tốt nhất (M_LE^best, M_EL^best)
4. **Huấn luyện cuối cùng**:
   - Dùng model tốt nhất dịch dataset tốt nhất
   - Retrain → Mô hình cuối cùng M_EL* và M_LE*

**Điểm mới so với Standard/IncBT**: OurBT đánh giá từng tập monolingual data riêng rẽ, từ đó xác định tổ hợp dataset mang lại hiệu quả cao nhất — thay vì dùng tất cả monolingual data một cách "mù quáng".

### 4.5. Xử lý Bible text

Paper thực nghiệm **có và không có** Bible text trong bilingual data:

- **Có Bible**: Tăng data size nhưng ngữ cảnh King James English ("thee", "thy", "believeth"...) khác biệt lớn so với ngôn ngữ tự nhiên hiện đại.
- **Không Bible**: Data nhỏ hơn nhưng ngữ cảnh nhất quán hơn → **cho kết quả tốt hơn**.

### 4.6. Metrics đánh giá

| Metric | Mô tả | Tại sao cần cho Luganda |
|---|---|---|
| **BLEU** | N-gram precision trên word level | Metric tiêu chuẩn nhưng bất lợi cho morphologically rich languages |
| **SacreBLEU** | BLEU chuẩn hóa, reproducible | Đảm bảo so sánh công bằng giữa các nghiên cứu |
| **ChrF2** | Character n-gram F-score (β=2, thiên về recall) | Bắt được sự tương đồng hình thái học, inflections — quan trọng cho ngôn ngữ agglutinative |
| **TER** | Translation Edit Rate — số lần chỉnh sửa cần thiết | Đo lường bổ sung về chất lượng, TER thấp = ít chỉnh sửa hơn |

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1. Setup thí nghiệm

- **Hardware**: Ubuntu server, 2× NVIDIA GeForce RTX 3090
- **Software**: Python 3.8.10, PyTorch
- **Optimizer**: Adam
- **Early stopping**: Nếu validation loss không cải thiện sau 40 epochs
- **Mini-batch size**: 1000

### 5.2. Ba thí nghiệm chính

| Thí nghiệm | Bilingual data | Test/Val set | BT approach |
|---|---|---|---|
| **Exp 1** | Có Bible text | Default T/V | IncBT |
| **Exp 2** | Không Bible text | Default T/V | IncBT |
| **Exp 3** | Không Bible text | Newtest (mở rộng, tin tức) | OurBT + IteBT |

**Newtest**: Bộ test/val mở rộng thêm các cặp dịch từ domain tin tức, giảm bias từ sự mất cân bằng giữa các nguồn bilingual data.

### 5.3. Baselines

- **Bilingual model** (Transformer base, không có BT)
- **Standard BT** (Sennrich et al. 2015)
- So sánh định tính với **Google Translate**
- Kết quả trước đó: Akera et al. 2022 (BLEU ~26.7 Eng→Lug, ~33.2 Lug→Eng)

---

## 6. Kết quả chính (Key Results)

### 6.1. Default T/V — Ảnh hưởng của Bible text

**Eng→Lug (Default T/V):**

| Model | BLEU |
|---|---|
| Bilingual + Bible | 39.05 |
| + IncBT | 39.46 (+0.41) |
| Bilingual − Bible | 53.77 |
| + IncBT | 53.88 (+0.11) |

**Lug→Eng (Default T/V):**

| Model | BLEU |
|---|---|
| Bilingual + Bible | 44.36 |
| + IncBT | 35.65 (−8.71) |
| Bilingual − Bible | 57.46 |
| + IncBT | 57.25 (−0.21) |

**Nhận xét**: Loại bỏ Bible text cải thiện BLEU đáng kể (~14 điểm cho Eng→Lug, ~13 điểm cho Lug→Eng). IncBT trên default T/V chỉ cải thiện nhẹ hoặc thậm chí giảm.

### 6.2. Newtest — Kết quả chính (OurBT + IteBT)

**Eng→Lug (Newtest):**

| Model | BLEU | Gain | SacreBLEU | ChrF2 | TER |
|---|---|---|---|---|---|
| Bilingual | 29.67 | — | 28.3 | 47.9 | 69.7 |
| Standard BT | 32.29 | +2.49 | 31.2 | 50.2 | 70.2 |
| **OurBT** | **35.94** | **+6.27** | 34.0 | 51.9 | 67.2 |
| + IteBT iter 1 | 37.96 | +8.29 | 36.1 | 52.6 | 65.7 |
| + IteBT iter 2 | 39.31 | +9.64 | 37.3 | 53.1 | 65.9 |
| **+ IteBT iter 3** | **40.25** | **+10.58** | **38.2** | **53.2** | **65.4** |

**Lug→Eng (Newtest):**

| Model | BLEU | Gain | SacreBLEU | ChrF2 | TER |
|---|---|---|---|---|---|
| Bilingual | 32.92 | — | 32.8 | 46.8 | 64.7 |
| Standard BT | 33.37 | +0.45 | 32.8 | 49.4 | 68.6 |
| **OurBT** | **39.97** | **+7.05** | 38.4 | 52.3 | 63.4 |
| + IteBT iter 1 | 41.94 | +9.02 | 40.9 | 52.9 | 63.2 |
| + IteBT iter 2 | 43.42 | +10.50 | 43.0 | 53.4 | 61.0 |
| **+ IteBT iter 3** | **44.25** | **+11.33** | **44.0** | **53.8** | **60.4** |

### 6.3. So sánh với nghiên cứu trước

| Nghiên cứu | Eng→Lug BLEU | Lug→Eng BLEU | BLEU Gain từ BT |
|---|---|---|---|
| Akera et al. 2022 | ~26.7 | ~33.2 | ~+3 |
| **Paper này (OurBT + IteBT)** | **40.25** | **44.25** | **+10~11** |

### 6.4. Tổ hợp dataset tốt nhất

- **Eng→Lug**: Monolingual Luganda tốt nhất = Mozilla Common Voice + Makerere Text and Speech + YouTube news headlines
- **Lug→Eng**: Monolingual English tốt nhất = Digital Umuganda + Gamayun MiniKit + Chimpreports news articles

**Quan sát quan trọng**: ~90% dữ liệu hoạt động tốt nhất đều được thu thập từ Uganda → **domain match** giữa monolingual data và training data là yếu tố then chốt.

### 6.5. So sánh định tính với Google Translate

Paper cung cấp ví dụ cụ thể cho thấy mô hình đề xuất:
- Dịch chính xác hơn Google Translate trong một số trường hợp (ví dụ: Google dịch "Maize" thành "coffee"/Emmwaanyi — sai nghĩa hoàn toàn)
- Kết quả "highly comparable and sometimes better" so với Google Translate

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Practical & reproducible**: Công khai cả bilingual lẫn monolingual datasets, giải quyết một vấn đề thực tế mà các nghiên cứu trước bỏ qua.
2. **OurBT — ý tưởng đơn giản nhưng hiệu quả**: Việc đánh giá từng tập monolingual data riêng rẽ rồi chọn tổ hợp tối ưu là approach thực dụng, dễ hiểu, dễ tái tạo.
3. **Cải thiện lớn**: >10 BLEU gain là con số đáng kể, đặc biệt cho low-resource setting.
4. **Multi-metric evaluation**: Sử dụng ChrF2, SacreBLEU, TER bên cạnh BLEU — phản ánh chính xác hơn chất lượng dịch cho ngôn ngữ agglutinative.
5. **Domain-aware insights**: Phát hiện về tầm quan trọng của domain match (dữ liệu Uganda cho ngôn ngữ Uganda) có giá trị hướng dẫn thực tiễn.
6. **So sánh định tính với Google Translate**: Cung cấp bằng chứng cụ thể về chất lượng dịch.

### Điểm yếu

1. **Không sử dụng pre-trained models / LLMs**: Chỉ dùng Transformer base train from scratch — không so sánh với fine-tuning mBART, mT5, NLLB, hay LLM-based approaches. Trong bối cảnh 2024, đây là hạn chế đáng kể.
2. **Default T/V bias cao**: Bilingual BLEU 53.77 (Eng→Lug) trên default test set là bất thường cao — cho thấy test set có thể bị **data leakage** hoặc quá tương đồng với training data. Kết quả trên Newtest (29.67) phản ánh thực tế hơn.
3. **Tiêu chí chọn dataset chưa rõ ràng**: OurBT chọn dựa trên BLEU, nhưng không giải thích chi tiết cách "combination" được tạo ra — thử tất cả permutations? Dùng greedy selection? Computational cost của quá trình này không được đề cập.
4. **Scalability không rõ**: Với N tập monolingual data, số lượng tổ hợp có thể tăng exponentially. Paper không thảo luận vấn đề này.
5. **Không có human evaluation**: Chỉ dùng automatic metrics — thiếu đánh giá con người về fluency và adequacy.
6. **So sánh với Google Translate không công bằng**: Chỉ 2 ví dụ cherry-picked, không có đánh giá hệ thống.
7. **BPE vocabulary nhỏ (10K)**: Có thể không đủ cho ngôn ngữ agglutinative — SentencePiece hoặc BPE lớn hơn có thể cho kết quả tốt hơn.
8. **Không thảo luận quality filtering**: Monolingual data (đặc biệt web-crawled) có thể chứa noise, nhưng paper chỉ đề cập cleaning cơ bản mà không có quality filtering riêng cho BT (ví dụ: round-trip translation filtering, language ID filtering).

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT low-resource nói chung

1. **Strategic dataset selection cho BT**: Không gộp tất cả monolingual data một cách mù quáng. Thay vào đó, đánh giá hiệu quả từng tập/tổ hợp riêng rẽ rồi chọn tối ưu. Áp dụng cho bất kỳ cặp ngôn ngữ low-resource nào.

2. **Domain matching**: Ưu tiên thu thập monolingual data từ cùng domain và cultural context với bilingual training data. Dữ liệu từ cùng quốc gia/khu vực thường hiệu quả hơn.

3. **Iterative BT sau OurBT**: Kết hợp 2 bước: (1) chọn dataset tối ưu bằng OurBT, (2) iterative BT trên dataset đã chọn → tối đa hóa hiệu quả.

4. **Multi-metric evaluation cho morphologically rich languages**: Luôn dùng ChrF (hoặc ChrF2) bên cạnh BLEU cho ngôn ngữ giàu hình thái — BLEU đánh giá thấp hơn chất lượng thực tế.

5. **Cẩn trọng với religious/archaic text**: Bible data có thể tăng quantity nhưng giảm quality do domain mismatch — cần xử lý riêng hoặc loại bỏ.

6. **Web crawling cho monolingual data**: News websites và YouTube transcripts là nguồn thực tế, dễ thu thập cho nhiều ngôn ngữ châu Phi.

### Cho nghiên cứu MT2 cụ thể

- Nếu knowledge base hoặc monolingual data được thu thập từ nhiều nguồn, nên **đánh giá contribution** của từng nguồn thay vì gộp tất cả.
- Kết hợp BT với knowledge-augmented approaches có thể giải quyết đồng thời data scarcity và cultural knowledge gap.
- Bài học về test set design: cần test set đại diện, tránh bias từ sự mất cân bằng trong bilingual data sources.

---

## 9. Các paper liên quan quan trọng

### Back Translation — Foundations

| Paper | Đóng góp | Đáng đọc? |
|---|---|---|
| **Sennrich et al. 2015** — *Improving NMT with Monolingual Data* | Đề xuất Standard BT — nền tảng của toàn bộ hướng nghiên cứu | ⭐⭐⭐ Must-read |
| **Edunov et al. 2018** — *Understanding Back-Translation at Scale* | Phân tích BT ở quy mô lớn: beam search vs sampling vs noised BT | ⭐⭐⭐ Must-read |
| **Hoang et al. 2018** — *Iterative Back-Translation for NMT* | Đề xuất Iterative BT và Incremental BT — paper này dựa trên framework đó | ⭐⭐ |

### Low-Resource NMT & Data Augmentation

| Paper | Đóng góp | Đáng đọc? |
|---|---|---|
| **Lamar & Kaya 2023** — *Measuring Impact of Data Augmentation for Extremely Low-Resource NMT* | So sánh các phương pháp augmentation cho NMT cực kỳ low-resource | ⭐⭐ |
| **Mojapelo & Buys 2023** — *Data Augmentation for Low Resource NMT for Sotho-Tswana Languages* | BT cho ngôn ngữ Nam Phi, bối cảnh tương tự | ⭐⭐ |
| **Gitau & Marivate 2023** — *Textual Augmentation Techniques for Low Resource MT: Case of Swahili* | Augmentation cho Swahili — cùng khu vực Đông Phi | ⭐⭐ |
| **Oh et al. 2023** — *Data Augmentation for NMT Using Generative Language Model* | Dùng LLM để tạo augmented data — hướng mới hơn | ⭐⭐ |
| **Chauhan et al. 2022** — *Improved Unsupervised NMT with Semantically Weighted BT* | BT cho morphologically rich + low-resource languages, unsupervised setting | ⭐⭐ |

### Luganda & African Languages NMT

| Paper | Đóng góp | Đáng đọc? |
|---|---|---|
| **Akera et al. 2022** — *MT for African Languages: Community Creation of Datasets and Models in Uganda* | Baseline trực tiếp cho paper này; BT trên English-Luganda | ⭐⭐ |
| **Bapna et al. 2022** — *Building MT Systems for the Next Thousand Languages* (Google) | BT ở quy mô lớn cho 1000+ ngôn ngữ, bao gồm Luganda; ChrF cho morphological languages | ⭐⭐⭐ |
| **Babirye et al. 2022** — *Building Text and Speech Datasets for Low Resourced Languages: East Africa* | Xây dựng dataset cho ngôn ngữ Đông Phi | ⭐ |

### Morphology & Subword Encoding

| Paper | Đóng góp | Đáng đọc? |
|---|---|---|
| **Sennrich et al. 2016** — *NMT of Rare Words with Subword Units (BPE)* | BPE — kỹ thuật tokenization được dùng trong paper | ⭐⭐ |
| **Ssentumbwe et al. 2019** — *English to Luganda SMT: Noun Class Prefix Segmentation* | Segmentation dựa trên morphology cho Luganda | ⭐ |

---

## 10. Tổng kết một dòng

> Paper chứng minh rằng **chọn lọc chiến lược dữ liệu đơn ngữ** (thay vì gộp tất cả) kết hợp **iterative back translation** có thể cải thiện >10 BLEU cho NMT low-resource, với insights quan trọng về **domain matching** và **multi-metric evaluation** cho ngôn ngữ giàu hình thái.
