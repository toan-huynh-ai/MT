# An Efficient Approach for Machine Translation on Low-resource Languages: Vietnamese-Chinese

## 1. Thông tin paper

| Mục | Chi tiết |
|-----|----------|
| **Title** | An Efficient Approach for Machine Translation on Low-resource Languages: A Case Study in Vietnamese-Chinese |
| **Authors** | Tran Ngoc Son, Nguyen Anh Tu, Nguyen Minh Tri |
| **Affiliation** | Samsung SDS R&D Center, Hanoi, Vietnam |
| **Venue** | VLSP 2022 Vietnamese-Chinese MT Challenge |
| **arXiv** | [2501.19314](https://arxiv.org/abs/2501.19314) |
| **Năm** | 2025 (submitted January 2025) |

---

## 2. Tóm tắt (Abstract)

Paper đề xuất một phương pháp hiệu quả cho dịch máy giữa cặp ngôn ngữ **Việt-Trung** trong bối cảnh dữ liệu song ngữ hạn chế, sử dụng mô hình đa ngôn ngữ tiền huấn luyện **mBART-50** kết hợp với kỹ thuật **back-translation** có chọn lọc dữ liệu bằng **TF-IDF**.

Đóng góp chính:
- Fine-tune mBART-50 trên dữ liệu song ngữ Việt-Trung (300K cặp câu) từ cuộc thi VLSP 2022.
- Đề xuất phương pháp **chọn lọc dữ liệu đơn ngữ dựa trên TF-IDF** để chọn 200K câu liên quan nhất từ kho đơn ngữ lớn (25M câu tiếng Việt, 19M câu tiếng Trung).
- Áp dụng **back-translation** trên dữ liệu đã chọn lọc để tạo dữ liệu song ngữ tổng hợp.
- Đạt kết quả **38.97 BLEU** (Vi→Zh) và **38.90 BLEU** (Zh→Vi), vượt Google Translate ở chiều Zh→Vi (+0.67 BLEU).

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Dịch máy Việt-Trung đối mặt với thách thức **low-resource** do:

1. **Dữ liệu song ngữ hạn chế**: Cặp ngôn ngữ Việt-Trung không có lượng dữ liệu song ngữ phong phú như Anh-Trung hay Anh-Việt. Cuộc thi VLSP 2022 chỉ cung cấp khoảng 300K cặp câu song ngữ — quá ít để train từ đầu một hệ thống NMT chất lượng cao.

2. **Dữ liệu đơn ngữ dồi dào nhưng chưa tận dụng hiệu quả**: Có 25 triệu câu tiếng Việt và 19 triệu câu tiếng Trung, nhưng việc sử dụng toàn bộ cho back-translation là không thực tế (tốn tài nguyên, nhiễu nhiều, chất lượng thấp).

3. **Khác biệt ngôn ngữ**: Tiếng Việt (hệ Latin, SVO, phân tích tính) và tiếng Trung (hệ chữ tượng hình, SVO nhưng cấu trúc modifier khác biệt) có khoảng cách typological đáng kể, đặc biệt ở hệ thống chữ viết và cách biểu đạt ngữ pháp.

### Tại sao quan trọng?

- Việt Nam và Trung Quốc có quan hệ thương mại, du lịch, và giao lưu văn hóa mật thiết → nhu cầu dịch Việt-Trung rất lớn.
- Google Translate tại thời điểm nghiên cứu chưa tối ưu cho chiều Zh→Vi.
- Bài toán VLSP 2022 là một benchmark chính thức cho cộng đồng NLP Việt Nam.

---

## 4. Phương pháp đề xuất (Proposed Method)

Pipeline gồm **3 bước chính**, tất cả xoay quanh mô hình **mBART-50** — một mô hình sequence-to-sequence đa ngôn ngữ đã được tiền huấn luyện trên 50 ngôn ngữ (bao gồm cả tiếng Việt và tiếng Trung).

### 4.1 Bước 1: Tiền xử lý dữ liệu (Data Cleaning)

Trước khi huấn luyện, dữ liệu được làm sạch kỹ lưỡng:

| Kỹ thuật | Mô tả |
|----------|-------|
| **Language detection** | Dùng `pycld3` để loại bỏ các câu không đúng ngôn ngữ |
| **HTML cleaning** | Loại bỏ thẻ HTML, ký tự đặc biệt |
| **Length filtering** | Chỉ giữ câu có 2–100 từ, loại bỏ câu quá ngắn hoặc quá dài |
| **Deduplication** | Loại bỏ các cặp câu trùng lặp |

### 4.2 Bước 2: Huấn luyện mô hình Baseline (Baseline mBART Training)

- **Mô hình nền**: mBART-50 (`facebook/mbart-large-50-many-to-many-mmt`) — đã tiền huấn luyện trên 50 ngôn ngữ với denoising objective (mask filling + sentence permutation).
- **Fine-tuning**: Dùng toàn bộ dữ liệu song ngữ sạch (~300K cặp câu) để fine-tune mBART-50 cho cả hai chiều dịch (Vi→Zh và Zh→Vi).
- **Hyperparameters**:

| Parameter | Giá trị |
|-----------|---------|
| Learning rate | 4e-5 |
| Batch size | 16 |
| Epochs | 4 |
| Optimizer | AdamW |
| Max sequence length | 100 tokens |
| Beam search | beam = 4 |

- **Kết quả baseline**: Vi→Zh = 38.22 BLEU, Zh→Vi = 35.58 BLEU.

### 4.3 Bước 3: Chọn lọc dữ liệu đơn ngữ bằng TF-IDF (TF-IDF Data Selection)

Đây là **đóng góp kỹ thuật chính** của paper — thay vì dùng toàn bộ kho đơn ngữ (hàng chục triệu câu), tác giả chọn lọc một tập con nhỏ nhưng **liên quan nhất** với domain của dữ liệu song ngữ.

**Cách hoạt động:**

1. **Tính TF-IDF** trên dữ liệu song ngữ (in-domain) → thu được vector đặc trưng của domain.
2. **Tính TF-IDF** cho từng câu trong kho đơn ngữ (out-of-domain: 25M tiếng Việt, 19M tiếng Trung).
3. **Tính độ tương đồng cosine** giữa vector TF-IDF của mỗi câu đơn ngữ với vector trung bình của dữ liệu in-domain.
4. **Xếp hạng** và chọn top-K câu có cosine similarity cao nhất → chọn **200K câu** cho mỗi ngôn ngữ.

**Tại sao TF-IDF?**
- Nhanh, nhẹ, không cần GPU — có thể xử lý hàng chục triệu câu trên CPU.
- Chọn được câu phù hợp về mặt **domain/topic** mà không cần supervised label.
- Loại bỏ câu nhiễu (off-topic) giúp back-translation chất lượng cao hơn.

### 4.4 Bước 4: Back-Translation và Fine-Tuning cuối cùng

1. **Back-translate**: Dùng mô hình baseline (Bước 2) để dịch 200K câu đơn ngữ đã chọn:
   - 200K câu tiếng Việt → dịch sang tiếng Trung (tạo pseudo-parallel Vi-Zh).
   - 200K câu tiếng Trung → dịch sang tiếng Việt (tạo pseudo-parallel Zh-Vi).
2. **Kết hợp dữ liệu**: Trộn dữ liệu song ngữ gốc (300K) + dữ liệu tổng hợp (200K) → tổng ~500K cặp câu.
3. **Fine-tune lại mô hình mBART-50** trên dữ liệu kết hợp → mô hình cuối cùng.

### Tổng quan Pipeline

```
Dữ liệu song ngữ (300K)    Dữ liệu đơn ngữ (25M Vi + 19M Zh)
         │                              │
    Fine-tune mBART-50             TF-IDF Selection
         │                              │
    Mô hình Baseline              200K câu được chọn
         │                              │
         └──────── Back-translate ───────┘
                        │
              Dữ liệu tổng hợp (200K)
                        │
         Kết hợp: 300K gốc + 200K tổng hợp
                        │
              Fine-tune mBART-50 lần 2
                        │
                  Mô hình cuối cùng
```

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Dataset: VLSP 2022 Vietnamese-Chinese MT Challenge

| Loại dữ liệu | Ngôn ngữ | Số lượng |
|---------------|----------|----------|
| **Song ngữ (Bilingual)** | Vi ↔ Zh | ~300,000 cặp câu |
| **Đơn ngữ (Monolingual)** | Tiếng Việt | ~25,000,000 câu |
| **Đơn ngữ (Monolingual)** | Tiếng Trung | ~19,000,000 câu |
| **Test set** | Vi ↔ Zh | Provided by VLSP organizers |

### 5.2 Tiền xử lý dữ liệu

Sau khi làm sạch, dữ liệu bị loại bỏ đáng kể:
- Loại bỏ câu sai ngôn ngữ (detected by pycld3)
- Loại bỏ câu có HTML tags
- Loại bỏ câu < 2 từ hoặc > 100 từ
- Loại bỏ câu trùng lặp

### 5.3 Metric đánh giá

| Metric | Mô tả |
|--------|-------|
| **BLEU** | Bilingual Evaluation Understudy — đo n-gram overlap giữa bản dịch và reference |

### 5.4 Hệ thống so sánh

| Hệ thống | Mô tả |
|-----------|-------|
| **Google Translate** | Hệ thống dịch thương mại của Google |
| **UET Engine** | Hệ thống dịch của University of Engineering and Technology (UET-VNU) — đội thi khác trong VLSP 2022 |
| **Baseline (mBART-50)** | Mô hình mBART-50 fine-tune chỉ trên dữ liệu song ngữ |

### 5.5 Cấu hình thí nghiệm

| Thành phần | Chi tiết |
|------------|----------|
| **Mô hình** | mBART-50 (facebook/mbart-large-50-many-to-many-mmt) |
| **Framework** | Hugging Face Transformers |
| **Optimizer** | AdamW |
| **Learning rate** | 4e-5 |
| **Batch size** | 16 |
| **Epochs** | 4 |
| **Beam search** | beam = 4 |
| **Max sequence length** | 100 tokens |
| **Tokenizer** | SentencePiece (built-in mBART-50) |

---

## 6. Kết quả chính (Key Results)

### 6.1 Kết quả tổng quan

#### Chiều Vi→Zh (Vietnamese → Chinese)

| Hệ thống | BLEU |
|-----------|------|
| Google Translate | **39.57** |
| Baseline (mBART-50, chỉ bilingual) | 38.22 |
| **Proposed (mBART-50 + TF-IDF + BT)** | **38.97** |

- Cải thiện **+0.75 BLEU** so với baseline.
- Vẫn thấp hơn Google Translate 0.60 BLEU ở chiều này.

#### Chiều Zh→Vi (Chinese → Vietnamese)

| Hệ thống | BLEU |
|-----------|------|
| Google Translate | 38.23 |
| Baseline (mBART-50, chỉ bilingual) | 35.58 |
| **Proposed (mBART-50 + TF-IDF + BT)** | **38.90** |

- Cải thiện **+3.32 BLEU** so với baseline — mức cải thiện rất đáng kể.
- **Vượt Google Translate +0.67 BLEU** ở chiều Zh→Vi.

### 6.2 So sánh với các đội thi VLSP 2022

| Đội/Hệ thống | Vi→Zh | Zh→Vi |
|---------------|-------|-------|
| Google Translate | 39.57 | 38.23 |
| UET Engine | — | — |
| **Samsung SDS (paper này)** | **38.97** | **38.90** |

### 6.3 Phân tích hiệu quả của TF-IDF Data Selection

| Chiến lược dữ liệu | Vi→Zh | Zh→Vi |
|---------------------|-------|-------|
| Chỉ dữ liệu song ngữ (300K) | 38.22 | 35.58 |
| + Back-translation ngẫu nhiên (random 200K) | — | — |
| + **Back-translation TF-IDF selection (200K)** | **38.97** | **38.90** |

Chiều Zh→Vi hưởng lợi nhiều hơn (+3.32 BLEU) so với Vi→Zh (+0.75 BLEU), cho thấy:
- Dữ liệu đơn ngữ tiếng Trung (19M) được chọn lọc tốt hơn nhờ TF-IDF, bổ sung đúng domain.
- Mô hình baseline ban đầu yếu hơn ở chiều Zh→Vi (35.58 vs 38.22), nên có nhiều room for improvement hơn.

### 6.4 Tóm tắt kết quả

- **Back-translation + TF-IDF selection là kỹ thuật hiệu quả** để cải thiện MT low-resource mà không cần dữ liệu song ngữ mới.
- Chỉ cần chọn **200K câu** (< 1% kho đơn ngữ) đã đem lại cải thiện có ý nghĩa.
- Mô hình cuối cùng **cạnh tranh được với Google Translate** ở chiều Zh→Vi.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Pipeline đơn giản, dễ tái tạo**: Phương pháp không đòi hỏi kiến trúc phức tạp hay kỹ thuật mới — chỉ kết hợp mBART-50 + TF-IDF + back-translation. Bất kỳ ai có GPU cũng có thể reproduce.

2. **TF-IDF data selection thực tế và hiệu quả**: Thay vì back-translate toàn bộ 25M+19M câu (tốn tài nguyên khổng lồ), chỉ chọn 200K câu liên quan → tiết kiệm compute đáng kể mà vẫn cải thiện mạnh.

3. **Kết quả cạnh tranh**: Vượt Google Translate ở chiều Zh→Vi là thành tựu đáng ghi nhận cho một hệ thống academic.

4. **Data cleaning kỹ lưỡng**: Quy trình tiền xử lý bài bản (pycld3, length filter, dedup) — đây là bước thường bị bỏ qua nhưng ảnh hưởng lớn đến chất lượng.

5. **Tận dụng tốt multilingual pre-training**: mBART-50 đã có kiến thức về cả tiếng Việt và tiếng Trung → fine-tuning hiệu quả với ít dữ liệu.

6. **Bối cảnh thực tế (VLSP 2022)**: Được đánh giá trên benchmark chính thức, không phải tự tạo test set → kết quả đáng tin cậy hơn.

### Điểm yếu

1. **Chỉ dùng BLEU**: Paper chỉ báo cáo BLEU — một metric lexical overlap cổ điển. Không có COMET, BERTScore, hay human evaluation. BLEU có nhiều hạn chế đã biết (không capture semantic similarity, penalize synonyms, vv).

2. **Thiếu ablation study chi tiết**:
   - Không so sánh TF-IDF selection với random selection → không chứng minh trực tiếp rằng TF-IDF tốt hơn chọn ngẫu nhiên.
   - Không thử nghiệm các giá trị K khác (50K, 100K, 500K) → 200K có phải tối ưu không?
   - Không so sánh TF-IDF với các phương pháp data selection khác (perplexity-based, embedding similarity).

3. **Không phân tích lỗi (error analysis)**: Không có ví dụ dịch cụ thể, không phân tích các loại lỗi (tên riêng, thành ngữ, cấu trúc ngữ pháp) → khó biết mô hình yếu ở đâu.

4. **Giới hạn ở mBART-50**: Không so sánh với các backbone khác (NLLB-200, M2M-100, hoặc LLM-based approaches). mBART-50 là mô hình 2020, có thể có alternatives mạnh hơn.

5. **Thiếu phân tích ngôn ngữ học**: Cặp Việt-Trung có nhiều hiện tượng thú vị (từ Hán-Việt, thành ngữ gốc Trung, khác biệt classifier system) nhưng paper không phân tích các khía cạnh này.

6. **Không tận dụng đặc thù Việt-Trung**: Tiếng Việt có khoảng 60-70% từ vựng gốc Hán-Việt → đây là lợi thế lớn cho MT Việt-Trung mà paper không khai thác (ví dụ: subword sharing, cognate injection).

7. **Back-translation chất lượng phụ thuộc baseline**: Baseline chỉ đạt 35.58 BLEU ở chiều Zh→Vi → back-translation từ mô hình yếu sẽ tạo ra pseudo-parallel data chất lượng thấp. Paper không thảo luận về vấn đề này hay áp dụng iterative back-translation.

8. **Không có reproducibility details đầy đủ**: Không công bố code, không chia sẻ dữ liệu đã tiền xử lý, không nêu rõ hardware sử dụng.

---

## 8. Ý tưởng có thể áp dụng

### 8.1 TF-IDF Data Selection cho bài toán MT low-resource

- **Ứng dụng trực tiếp**: Khi có kho đơn ngữ lớn nhưng chỉ muốn chọn một lượng nhỏ để back-translate, TF-IDF là phương pháp nhanh, rẻ, và hiệu quả. Có thể áp dụng cho bất kỳ cặp ngôn ngữ nào.
- **Mở rộng**: Thay TF-IDF bằng dense embedding similarity (dùng sentence-transformers) có thể chọn dữ liệu tốt hơn về mặt semantic.

### 8.2 Pipeline mBART + Back-Translation

- **Mô hình nền tốt**: mBART-50 (hoặc NLLB-200, mBART-large-cc25) là starting point tốt cho MT low-resource nhờ multilingual pre-training.
- **Back-translation có chọn lọc** hiệu quả hơn back-translation toàn bộ — đây là bài học quan trọng: quality > quantity.
- **Iterative back-translation**: Có thể cải thiện bằng cách lặp lại pipeline (train → BT → train → BT) với mô hình ngày càng tốt hơn.

### 8.3 Kết hợp với phương pháp Data Augmentation

Dựa trên paper liên quan (Nguyen et al., AAAI 2026 — DA for Vietnamese minority languages), có thể kết hợp:
- **Back-translation (paper này)** với **meaning-preserving DA** (Deletion + Original, Synonym Replacement) từ paper DA → augment cả dữ liệu song ngữ gốc và dữ liệu pseudo-parallel.
- Lưu ý: cần chọn DA phù hợp với typology của ngôn ngữ — tiếng Việt là analytic nên surface-level DA thường an toàn.

### 8.4 Cho bài toán cultural MT

- **Data selection theo domain văn hóa**: Dùng TF-IDF hoặc embedding similarity để chọn câu đơn ngữ liên quan đến văn hóa (ẩm thực, lễ hội, địa danh...) từ kho đơn ngữ lớn → back-translate → tạo dữ liệu dịch chuyên biệt về văn hóa.
- **Khai thác từ Hán-Việt**: Cho cặp Việt-Trung, từ Hán-Việt là nguồn cognates tự nhiên → có thể dùng để cải thiện alignment hoặc tạo dictionary-based augmentation.

### 8.5 Bài học rút ra

- **Data selection quan trọng hơn data volume**: 200K câu được chọn lọc > random 200K câu >> 25M câu noise.
- **mBART-50 là baseline mạnh cho MT Việt**: Đã có tiếng Việt và nhiều ngôn ngữ trong pre-training.
- **Back-translation vẫn là kỹ thuật gold-standard** cho MT low-resource, nhưng cần kết hợp với data selection để tối đa hiệu quả.
- **Chiều dịch khó hưởng lợi nhiều hơn**: Zh→Vi (khó hơn, baseline thấp hơn) cải thiện +3.32 BLEU trong khi Vi→Zh (baseline đã khá) chỉ cải thiện +0.75 BLEU.

---

## 9. Các paper liên quan quan trọng

### Back-Translation & Data Selection cho NMT

| Paper | Nội dung | Venue |
|-------|----------|-------|
| **Sennrich et al. (2016)** — Improving NMT with Monolingual Data | Paper gốc đề xuất back-translation cho NMT | ACL 2016 |
| **Edunov et al. (2018)** — Understanding Back-Translation at Scale | Phân tích back-translation ở quy mô lớn, so sánh beam search vs sampling | EMNLP 2018 |
| **Moore & Lewis (2010)** — Intelligent Selection of Language Model Training Data | Data selection dựa trên cross-entropy difference — tiền thân của TF-IDF selection | ACL 2010 |
| **Axelrod et al. (2011)** — Domain Adaptation via Pseudo In-Domain Data Selection | Data selection cho domain adaptation trong SMT | EMNLP 2011 |

### Multilingual Pre-trained Models cho MT

| Paper | Nội dung | Venue |
|-------|----------|-------|
| **Tang et al. (2020)** — mBART-50: Multilingual Translation with Extensible Multilingual Pretraining and Finetuning | Mô hình nền được dùng trong paper | arXiv 2020 |
| **Liu et al. (2020)** — mBART: Multilingual Denoising Pre-training for NMT | Mô hình gốc mBART | TACL 2020 |
| **NLLB Team (2022)** — No Language Left Behind | Mô hình đa ngôn ngữ 200 ngôn ngữ | arXiv 2022 |
| **Fan et al. (2021)** — Beyond English-Centric Multilingual MT (M2M-100) | Mô hình many-to-many 100 ngôn ngữ | JMLR 2021 |

### NMT cho tiếng Việt

| Paper | Nội dung | Venue |
|-------|----------|-------|
| **Tran et al. (2022)** — BARTpho | Mô hình BART tiền huấn luyện cho tiếng Việt | Interspeech 2022 |
| **Nguyen et al. (2026)** — Not All Data Augmentation Works: Typology-Aware Study for Low-Resource Vietnamese Minority Languages | DA có nhận thức typological cho Tày-Việt và Bahnar-Việt | AAAI 2026 |
| **VLSP 2022 Shared Task** — Vietnamese-Chinese MT | Cuộc thi MT Việt-Trung chính thức | VLSP 2022 |

### Low-Resource NMT General

| Paper | Nội dung | Venue |
|-------|----------|-------|
| **Ranathunga et al. (2023)** — NMT for Low-resource Languages: A Survey | Tổng quan toàn diện về NMT low-resource | ACM Computing Surveys |
| **Shi et al. (2022)** — Low-resource NMT: Methods and Trends | Survey về phương pháp và xu hướng NMT low-resource | ACM TALLIP |
| **Wang et al. (2021)** — A Survey on Low-Resource NMT | Survey IJCAI về NMT low-resource | IJCAI 2021 |

### Đáng đọc thêm (ưu tiên cao)

1. **Sennrich et al. (2016)** — Paper gốc về back-translation, nền tảng lý thuyết cho phương pháp trong paper này.
2. **Nguyen et al. (2026)** — Paper liên quan trực tiếp: cùng bối cảnh Vietnamese low-resource nhưng tiếp cận từ góc DA, bổ sung tốt cho paper này.
3. **Tang et al. (2020)** — Hiểu rõ mBART-50 để biết khi nào multilingual pre-training giúp và khi nào không.
4. **NLLB Team (2022)** — Đối thủ cạnh tranh của mBART-50, nên so sánh khi build hệ thống MT Vietnamese.
