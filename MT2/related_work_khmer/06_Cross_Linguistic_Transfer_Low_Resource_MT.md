# Tóm tắt Paper: Cross-Linguistic Transfer Learning for Low-Resource MT

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Improving Low-Resource Machine Translation via Cross-Linguistic Transfer from Typologically Similar High-Resource Languages |
| **Authors** | Saughmon Boujkian |
| **Affiliations** | Department of Computer Science, University of British Columbia, Canada |
| **Venue** | arXiv preprint (research conducted at Technical University of Darmstadt) |
| **Year** | 2025 |
| **arXiv** | [2501.00045](https://arxiv.org/abs/2501.00045) |
| **Code** | [GitHub](https://github.com/soghomon-b/fine-tuning-for-machine-translation) |

---

## 2. Tóm tắt (Abstract)

Paper nghiên cứu **hiệu quả xuyên ngôn ngữ (cross-linguistic)** của transfer learning cho dịch máy low-resource bằng cách **fine-tune** mô hình đã được train trên ngôn ngữ high-resource **có quan hệ typological tương đồng**, sử dụng lượng dữ liệu hạn chế từ ngôn ngữ low-resource mục tiêu.

**Giả thuyết chính:** Sự tương đồng ngôn ngữ học (linguistic similarity) cho phép adaptation hiệu quả, giảm nhu cầu về lượng dữ liệu training lớn.

**Thí nghiệm:** 5 cặp ngôn ngữ thuộc các họ khác nhau:
- **Semitic:** Modern Standard Arabic → Levantine Arabic
- **Bantu:** Hausa → Zulu
- **Romance:** Spanish → Catalan
- **Slavic:** Slovak → Macedonian
- **Language isolate:** Eastern Armenian → Western Armenian

**Kết quả:** Transfer learning cải thiện chất lượng dịch một cách nhất quán trên tất cả các cặp. Batch size trung bình (~32) tối ưu cho cặp tương đồng cao, batch size nhỏ hơn có lợi cho cặp ít tương đồng, và learning rate quá cao gây bất ổn training.

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Các hệ thống dịch máy hiện đại (transformer-based) đạt hiệu suất cao nhờ dữ liệu parallel corpora lớn, nhưng **phần lớn ngôn ngữ trên thế giới là low-resource** — thiếu dữ liệu song ngữ đủ lớn để train mô hình từ đầu.

### Khoảng trống nghiên cứu (Research Gap)

1. **Nghiên cứu trước chỉ test trong cùng 1 họ ngôn ngữ:** Paper của Maillard et al. (2023) — "Small Data, Big Impact" — chỉ thử nghiệm với các ngôn ngữ Indo-European (chủ yếu Romance). Chưa rõ liệu kết quả có generalize sang các họ ngôn ngữ khác nhau.

2. **Thiếu bằng chứng cross-linguistic:** Gheini et al. (2021) cho thấy fine-tune cross-attention đã đủ hiệu quả, nhưng không đánh giá rõ ràng trên các họ ngôn ngữ khác biệt lớn.

3. **Nghiên cứu đơn lẻ:** Hujon et al. (2023) thử transfer learning cho English–Khasi (không cùng họ), nhưng chỉ trên 1 cặp duy nhất, không khám phá pattern rộng hơn.

### Tại sao quan trọng?

- Hàng nghìn ngôn ngữ low-resource trên thế giới cần giải pháp MT hiệu quả với **ít dữ liệu**.
- Nếu transfer learning hoạt động **xuyên họ ngôn ngữ**, đây sẽ là phương pháp **scalable** cho cộng đồng ngôn ngữ thiểu số với tài nguyên tính toán hạn chế.
- Cần xác định liệu **hyperparameter settings có thể standardize** được không, giảm chi phí tìm kiếm hyperparameter cho từng ngôn ngữ.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Tổng quan Pipeline

```
Parent Model (High-Resource Language → English)
        ↓ Initialize parameters θ
Fine-tune Model (Low-Resource Language → English)
        ↓ Optimize with child data
Fine-tuned Model (φ) → Evaluate (BLEU + Human Eval)
```

### 4.2 Định nghĩa hình thức (Formal Definition)

Dựa trên Gheini et al. (2021):

- **Parent model** $f_\theta$: Train trên dataset high-resource $(x_{sp}, y_{tp})$ — cặp câu source (ngôn ngữ high-resource) và target (English).
- **Fine-tuning:** Lấy parameters $\theta$ từ $f_\theta$ để khởi tạo $g_\theta$, rồi optimize trên dataset child $(x_{sc}, y_{tc})$ — ngôn ngữ low-resource → English — cho đến khi hội tụ thành $g_\phi$.
- **Ràng buộc:** Parent và child chia sẻ ít nhất một phía (ở đây target luôn là English).

### 4.3 Lựa chọn cặp ngôn ngữ

5 cặp được chọn để cover **đa dạng typological**:

| Cặp | Họ ngôn ngữ | Mức độ tương đồng | Đặc điểm |
|---|---|---|---|
| MSA → Levantine Arabic | Semitic | Rất cao (~0.85) | Cùng gốc, khác morphology nhẹ, khác từ vựng colloquial |
| Eastern → Western Armenian | Language isolate | Cao (~0.80) | Khác case marking, vị trí trợ động từ, morphology đáng kể |
| Spanish → Catalan | Romance (Indo-European) | Rất cao (~0.83) | Syntax gần giống, vocab overlap lớn — **positive control** |
| Slovak → Macedonian | Slavic (Indo-European) | Trung bình-cao (~0.74) | Cùng Slavic nhưng khác morphology và lexicon |
| Hausa → Zulu | Bantu | Thấp (~0.55) | Khác họ ngôn ngữ đáng kể — **challenging case** |

> **Lưu ý:** Similarity score được tính bằng Levenshtein Distance trên các câu test dịch sang từng ngôn ngữ.

### 4.4 Mô hình sử dụng

- Tất cả đều là mô hình **Helsinki-NLP (OPUS-MT)** — transformer-based, có sẵn trên HuggingFace.
- Tokenization: **SentencePiece** (Armenian có thêm bước Normalization).
- Architecture: **Encoder-Decoder Transformer** (MarianMT).
- Mô hình Arabic: `opus-mt-tc-big-ar-en` (BLEU 44.4 trên tico19-test).
- Mô hình Armenian: `opus-mt-hy-en` (BLEU 29.5 trên Tatoeba) — nhỏ hơn.

### 4.5 Dữ liệu Fine-tuning

- Mỗi cặp ngôn ngữ sử dụng đúng **5,000 câu song ngữ** (low-resource language ↔ English).
- Chia tỷ lệ: **80% train / 10% validation / 10% test**.
- Kích thước đồng nhất để kiểm soát biến thiên do data volume.

### 4.6 Hyperparameter Variation

Paper không tối ưu hyperparameter mà **thay đổi có kiểm soát** để đảm bảo kết quả không phụ thuộc vào 1 cấu hình duy nhất.

**Các hyperparameter thay đổi:**

| Hyperparameter | Phân phối | Phạm vi |
|---|---|---|
| Learning Rate | Uniform | $U(0.002, 0.1)$ — nhưng thực tế chỉ hoạt động ở $n \times 10^{-4}$ |
| Weight Decay | Uniform | $U(0.0, 0.3)$ |
| Epochs | Discrete | {5, 8, 10, 12} |
| Batch Size | Discrete | {8, 16, 32, 64} |

**Cấu hình cuối cùng (4 runs/cặp ngôn ngữ):**

| Run | Learning Rate | Weight Decay | Batch Size | Epochs |
|---|---|---|---|---|
| 1 | 0.0002 | 0.02 | 8 | 12 |
| 2 | 0.0002 | 0.2 | 32 | 8 |
| 3 | 0.0004 | 0.2 | 64 | 5 |
| 4 | 0.06 | 0.14 | 8 | 8 |

> Run 4 sử dụng learning rate cao **cố ý** để chứng minh nó phá hủy mô hình → **negative control**.

### 4.7 Hệ thống đánh giá kết hợp (OES)

Paper đề xuất **Overall Evaluation Score (OES)** kết hợp BLEU và đánh giá con người:

1. **BLEU Score**: Đo n-gram overlap với bản dịch tham chiếu (tự động, objective).
2. **Human Evaluation Score (HES)**: 3 câu test được dịch sang ngôn ngữ low-resource, sau đó cho mô hình dịch ngược lại sang English. Native speakers đánh giá trên thang 1-3:
   - 1 = Hoàn toàn sai
   - 2 = Đúng ý nhưng có lỗi
   - 3 = Nghĩa chính xác
   - HES = Tổng điểm 3 câu / 9

3. **OES = BLEU × HES**: Nếu HES thấp (output kém) nhưng BLEU cao → OES vẫn thấp, phản ánh chất lượng thực.

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Dataset

| Ngôn ngữ low-resource | Nguồn dữ liệu | Kích thước | Đặc điểm |
|---|---|---|---|
| Western Armenian | Western Armenian–English Parallel Corpus (Boyacıoğlu & Niehues, SIGUL 2024) | 5,000 câu (từ 147k) | Đa domain: tin tức, văn hóa, văn học, Wikipedia, tôn giáo |
| Levantine Arabic | LINDAT/CLARIN repository | 5,000 câu | Chủ yếu spoken variety, parallel corpora hiếm |
| Catalan | Softcatalà Parallel Corpus | 5,000 câu | Chất lượng cao, đa domain |
| Macedonian | NLLB v1 corpus (OPUS) | 5,000 câu | Medium-similarity case |
| Zulu | NLLB v1 corpus (OPUS) | 5,000 câu | Challenging case, khác biệt typological lớn nhất |

### 5.2 Thiết kế thí nghiệm

- **5 cặp ngôn ngữ × 4 cấu hình hyperparameter = 20 mô hình** fine-tuned.
- **Negative control:** Fine-tune Catalan từ Hausa parent → BLEU chỉ 0.0007 (chứng minh linguistic similarity quan trọng).
- **Additional control:** Fine-tune Catalan từ Finnish parent → BLEU ~20 (dù khác họ, có một số typological similarities).

### 5.3 Metrics

| Metric | Mô tả | Vai trò |
|---|---|---|
| **BLEU** | N-gram overlap tự động | Primary metric — objective, stable |
| **HES** | Human Evaluation Score (thang 1-3, 3 câu) | Bổ sung đánh giá chủ quan |
| **OES** | Overall Evaluation Score = BLEU × HES | Combined metric |

### 5.4 Phân tích thống kê

- **Welch's t-test**: So sánh nhóm high-similarity vs. low-similarity.
- **ANOVA**: Kiểm tra ảnh hưởng của weight decay.
- **Shapiro-Wilk test**: Kiểm tra giả định phân phối chuẩn.
- **Cohen's d**: Đo effect size.

### 5.5 Phần cứng

- 1 × NVIDIA GeForce RTX 6000 GPU
- 20 cores CPU (Intel Xeon, 10 physical cores)
- Linux Debian 12

---

## 6. Kết quả chính (Key Results)

### 6.1 Transfer learning hiệu quả hơn khi ngôn ngữ tương đồng

**Kết quả BLEU trung bình theo cặp ngôn ngữ:**

| Nhóm | Cặp ngôn ngữ | Similarity Score | BLEU trung bình |
|---|---|---|---|
| **High-similarity** | Spanish → Catalan | ~0.83 | Cao nhất (>40) |
| **High-similarity** | MSA → Levantine Arabic | ~0.85 | Cao |
| **High-similarity** | Eastern → Western Armenian | ~0.80 | Cao |
| **High-similarity** | Slovak → Macedonian | ~0.74 | Trung bình-cao |
| **Low-similarity** | Hausa → Zulu | ~0.55 | Thấp (<20) |

**Thống kê:**
- Mean BLEU high-similarity: **μ ≈ 24.76**
- Mean BLEU low-similarity: **μ ≈ 7.10**
- Welch's t-test: **t ≈ 3.00, p ≈ 0.0096** (significant ở p < 0.05)
- Cohen's d ≈ **1.8** (very large effect size)

### 6.2 Negative Control — Linguistic similarity là yếu tố quyết định

| Thí nghiệm | BLEU |
|---|---|
| Catalan fine-tuned từ **Hausa** parent | **0.0007** |
| Catalan fine-tuned từ **Finnish** parent | **~20** |
| Catalan fine-tuned từ **Spanish** parent | **>40** |

→ Khoảng cách typological càng lớn → transfer learning càng kém hiệu quả, thậm chí gần như vô nghĩa.

### 6.3 Ảnh hưởng của Hyperparameters

#### Learning Rate
- Learning rate ở mức $n \times 10^{-4}$ (0.0002–0.0004): Hoạt động tốt.
- Learning rate cao (0.06): **Catastrophic failure** — output chỉ là ký tự lặp (>>>), OES = 0 trên tất cả ngôn ngữ.
- Trong phạm vi hợp lệ, giá trị cụ thể không ảnh hưởng đáng kể.

#### Weight Decay
- **Không có ảnh hưởng thống kê** (ANOVA p = 0.981).
- BLEU gần như giống nhau ở weight decay 0.2, 0.02, và 0.002 (dao động 37.2–41.2 qua 8 epochs).

#### Batch Size — Hyperparameter quan trọng nhất

| Batch Size | Hiệu quả |
|---|---|
| **32** | Tối ưu cho 4/5 cặp ngôn ngữ (high-similarity) |
| **8** | Tối ưu cho Zulu (low-similarity) |
| **64** | Kém hơn 32 ở hầu hết trường hợp |

**Giải thích:** Cặp ít tương đồng cần batch size nhỏ hơn để cho phép cập nhật chi tiết hơn (finer-grained updates), giúp mô hình học các đặc trưng ngôn ngữ khác biệt.

#### Epochs
- Số epochs tối ưu: **6-7 epochs** là đủ (parent model đã encode nhiều linguistic knowledge).
- Epochs >10: Có nguy cơ overfitting.

### 6.4 Quan sát định tính

- Tất cả mô hình **xử lý tốt hơn với câu dài, phức tạp** so với câu ngắn SVO đơn giản (do training data chủ yếu là câu dài).
- Mô hình MSA gốc dịch kém câu Levantine Arabic dài → Mô hình fine-tuned dịch chính xác → Chứng minh transfer learning bảo toàn và adapt linguistic structures.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Thiết kế thí nghiệm đa dạng typological:** 5 cặp ngôn ngữ thuộc các họ khác nhau (Semitic, Bantu, Indo-European, language isolate) — vượt xa các nghiên cứu trước chỉ test trong 1 họ.

2. **Negative controls tốt:** Fine-tune từ parent không liên quan (Hausa → Catalan) để chứng minh linguistic similarity thực sự quan trọng, không phải artifact.

3. **Hyperparameter variation có kiểm soát:** Không chỉ chọn 1 bộ hyperparameter, mà chạy 4 cấu hình/cặp ngôn ngữ để đảm bảo robustness.

4. **Kết hợp automatic + human evaluation:** OES = BLEU × HES giải quyết hạn chế của BLEU đơn thuần.

5. **Tính thực tiễn cao:** Chỉ cần 5,000 câu song ngữ → có thể áp dụng cho nhiều ngôn ngữ low-resource. Phần cứng chỉ cần 1 GPU.

6. **Phân tích thống kê đầy đủ:** Welch's t-test, ANOVA, Cohen's d, Shapiro-Wilk — không chỉ báo cáo số mà còn kiểm tra giả định.

7. **Hướng dẫn thực hành cụ thể:** Đưa ra guidance rõ ràng về learning rate range, batch size theo similarity level, số epochs phù hợp.

### Điểm yếu

1. **Chỉ 1 cặp low-similarity:** Hausa → Zulu là cặp duy nhất trong nhóm low-similarity → t-test với n=1 ở 1 nhóm có statistical power rất thấp, dù p ≈ 0.0096. Cần thêm nhiều cặp cross-family để kết luận vững chắc hơn.

2. **Human evaluation quá nhỏ:** Chỉ 3 câu test, ít raters, thang đo 1-3 rất thô. Không tuân theo chuẩn MQM hay WMT human evaluation guidelines. HES dễ bị bias bởi cách chọn câu.

3. **Dữ liệu 5,000 câu đồng nhất:** Tuy giúp kiểm soát biến, nhưng không thể hiện ảnh hưởng của data volume lên transfer learning. Real-world settings có thể có từ 100 đến 50,000 câu.

4. **Similarity metric đơn giản:** Dùng Levenshtein Distance trên 3 câu test để đo typological similarity — quá thô sơ. Các metric tốt hơn: lang2vec features, URIEL typological database, syntax/morphology-based distances.

5. **Chỉ test encoder-decoder (MarianMT):** Không thí nghiệm trên decoder-only LLMs (GPT, LLaMA) hay massively multilingual models (mBART, NLLB-200). Kết luận có thể không áp dụng cho các kiến trúc khác.

6. **Không có ablation study chuyên sâu:** Không test ảnh hưởng của data size (1k, 2k, 5k, 10k), domain mismatch, hoặc multi-source transfer.

7. **English luôn là target:** Tất cả cặp đều dịch **sang English**. Chưa rõ transfer learning hiệu quả thế nào khi dịch **từ English** sang low-resource language (hướng khó hơn).

8. **Hausa → Zulu classification có vấn đề:** Hausa không phải ngôn ngữ Bantu (thuộc Chadic/Afro-Asiatic), nhưng paper dùng Xhosa model (Bantu) cho parent. Việc labeling "Bantu: Hausa → Zulu" gây nhầm lẫn — thực tế Hausa và Zulu thuộc **hai họ ngôn ngữ khác nhau** (Afro-Asiatic vs Niger-Congo).

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT low-resource nói chung

1. **Recipe thực tiễn cho low-resource MT:**
   - Bước 1: Tìm mô hình pre-trained trên ngôn ngữ high-resource **gần nhất** (typologically similar).
   - Bước 2: Thu thập ~5,000 câu song ngữ cho ngôn ngữ target.
   - Bước 3: Fine-tune với learning rate ~$2\times10^{-4}$, batch size 32 (hoặc 8 nếu similarity thấp), 6-7 epochs.
   - → Đạt chất lượng dịch usable mà không cần cluster GPU.

2. **Similarity-guided model selection:** Dùng typological similarity (lang2vec, URIEL) để tự động chọn parent model tốt nhất từ zoo of pretrained models.

3. **Batch size as similarity proxy:** Insight rằng batch size tối ưu tương quan với linguistic similarity có thể được dùng như heuristic nhanh: nếu languages gần → batch lớn, nếu xa → batch nhỏ.

4. **Kết hợp BLEU + human eval:** Metric OES = BLEU × HES là ý tưởng hay (dù implementation ở paper này còn thô), có thể được cải tiến với human eval quy mô lớn hơn.

### Cho project MT2 cụ thể

5. **Transfer từ ngôn ngữ high-resource gần nhất:** Nếu làm dịch Việt-Anh (Vietnamese low-resource tương đối), có thể thử transfer từ Chinese model vì Vietnamese chịu ảnh hưởng Hán-Việt về từ vựng, hoặc từ Thai model vì tương đồng typological (SVO, tonal, analytic).

6. **Chỉ 5,000 câu đã tạo khác biệt:** Minh chứng rằng data curation quan trọng hơn data volume. Tập trung vào **chất lượng** parallel data (đúng domain, đa dạng cấu trúc) hơn là thu thập số lượng lớn.

7. **Hyperparameter không cần grid search phức tạp:** Weight decay và learning rate (trong khoảng hợp lệ) ít ảnh hưởng → tiết kiệm thời gian thí nghiệm.

---

## 9. Các paper liên quan quan trọng

### Trực tiếp liên quan (cited trong paper)

| # | Paper | Tác giả | Năm | Đóng góp chính |
|---|---|---|---|---|
| 1 | **Small Data, Big Impact: Leveraging Minimal Data for Effective Machine Translation** | Maillard et al. | 2023 (ACL) | Train MT cho low-resource languages chỉ với vài nghìn câu, init từ related high-resource language. Giới hạn: chỉ test trong Romance languages. |
| 2 | **Cross-Attention is All You Need: Adapting Pretrained Transformers for MT** | Gheini et al. | 2021 (EMNLP) | Chỉ fine-tune cross-attention parameters đã gần bằng full fine-tuning → learned representations cross-linguistically robust. Cung cấp formal definition cho transfer learning trong MT. |
| 3 | **Transfer Learning Based Neural MT of English-Khasi on Low-Resource Settings** | Hujon et al. | 2023 | Transfer learning cho cặp English–Khasi (không cùng họ) dùng LSTM. Cải thiện accuracy dù languages unrelated, nhưng chỉ 1 cặp. |
| 4 | **Trivial Transfer Learning for Low-Resource Neural MT** | Kocmi & Bojar | 2018 (WMT) | Chứng minh transfer learning "trivial" — chỉ cần init từ bất kỳ parent nào đã giúp low-resource MT. Cung cấp learning rate range reference. |
| 5 | **OPUS-MT – Building Open Translation Services for the World** | Tiedemann & Thottingal | 2020 (EAMT) | Helsinki-NLP OPUS-MT: hệ thống mô hình MT open-source cho hàng trăm cặp ngôn ngữ. Tất cả parent models trong paper này đều từ OPUS-MT. |
| 6 | **The First Parallel Corpus and NMT Model of Western Armenian and English** | Boyacıoğlu & Niehues | 2024 (SIGUL@LREC-COLING) | Corpus 147k câu Western Armenian–English. Nguồn dữ liệu cho thí nghiệm Armenian trong paper này. |

### Nên đọc thêm (mở rộng)

| # | Paper | Lý do đọc |
|---|---|---|
| 7 | **CCMatrix: Mining Billions of High-Quality Parallel Sentences on the Web** (Schwenk et al., 2020) | Nguồn dữ liệu NLLB/OPUS — hiểu cách mine parallel data quy mô lớn cho low-resource languages |
| 8 | **Hyperparameter Optimization for Fine-Tuning Pre-Trained Transformer Models** (Klein et al., 2022) | Best practices cho hyperparameter tuning MT models, ASHA-based early stopping |
| 9 | **Multilingual Denoising Pre-training for Neural MT** (mBART — Liu et al., 2020) | Multilingual pre-training approach khác — so sánh với transfer learning single-pair |
| 10 | **No Language Left Behind** (NLLB Team, 2022) | Massively multilingual MT model 200 ngôn ngữ — baseline mạnh cho bất kỳ low-resource MT task |

---

## 10. Tổng kết nhanh

| Khía cạnh | Đánh giá |
|---|---|
| **Novelty** | Trung bình — ý tưởng transfer learning cho MT không mới, nhưng việc test systematic trên 5 họ ngôn ngữ khác nhau có giá trị |
| **Rigor** | Trung bình-khá — có thống kê, negative controls, nhưng scale nhỏ (5 cặp, 5k câu, 3 câu human eval) |
| **Reproducibility** | Cao — code public trên GitHub, dùng HuggingFace models, data sources rõ ràng |
| **Practical value** | Cao — recipe rõ ràng: 5k parallel data + OPUS-MT parent + simple fine-tuning = usable low-resource MT |
| **Relevance cho MT2** | Trung bình — cung cấp insights về transfer learning strategy và hyperparameter guidance, nhưng không address knowledge-augmented hay cultural adaptation |
