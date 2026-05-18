# Tóm tắt Paper: Machine Translation Advancements of Low-Resource Indian Languages by Transfer Learning

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Machine Translation Advancements of Low-Resource Indian Languages by Transfer Learning |
| **Authors** | Bin Wei, Jiawei Zhen, Zongyao Li, Zhanglin Wu, Daimeng Wei, Jiaxin Guo, Zhiqiang Rao, Shaojun Li, Yuanchang Luo, Hengchao Shang, Jinlong Yang, Yuhao Xie, Hao Yang |
| **Affiliation** | Huawei Translation Service Center (HW-TSC), Beijing, China |
| **Venue** | WMT24 (Workshop on Machine Translation 2024) — Shared Task: Indian Languages MT |
| **Year** | 2024 |
| **arXiv** | [2409.15879](https://arxiv.org/abs/2409.15879) |

---

## 2. Tóm tắt (Abstract)

Paper trình bày hệ thống dự thi của Huawei Translation Center (HW-TSC) cho **WMT24 Indian Languages Machine Translation Shared Task**. Nhóm nghiên cứu sử dụng **hai chiến lược transfer learning** khác nhau tùy theo đặc trưng ngôn ngữ và mức độ hỗ trợ của mô hình mã nguồn mở hiện có:

1. **Với Assamese (as) và Manipuri (mn)**: Fine-tune mô hình mã nguồn mở **IndicTrans2** — một mô hình đa ngôn ngữ hỗ trợ 22 ngôn ngữ Ấn Độ — để dịch hai chiều với tiếng Anh.
2. **Với Khasi (kh) và Mizo (mz)**: Huấn luyện mô hình đa ngôn ngữ (multilingual model) từ đầu sử dụng dữ liệu song ngữ từ cả 4 cặp ngôn ngữ trên cộng thêm ~8 triệu câu Anh-Bengali, sau đó fine-tune cho từng cặp ngôn ngữ cụ thể.

Kết quả đạt được:
- en→as: **23.5 BLEU**, en→mn: **31.8 BLEU**, as→en: **36.2 BLEU**, mn→en: **47.9 BLEU**
- en→kh: **19.7 BLEU**, en→mz: **32.8 BLEU**, kh→en: **16.1 BLEU**, mz→en: **33.9 BLEU**

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Các ngôn ngữ low-resource của Ấn Độ (Assamese, Manipuri, Khasi, Mizo) có **lượng dữ liệu song ngữ rất hạn chế** (chỉ từ 21K đến 50K câu song ngữ), gây khó khăn lớn cho việc xây dựng hệ thống NMT chất lượng cao. Bài toán cần giải quyết:

- **Thiếu dữ liệu song ngữ nghiêm trọng**: Dữ liệu parallel cho mỗi cặp ngôn ngữ cực kỳ ít (thấp nhất chỉ 21K cho en-mn).
- **Không có mô hình sẵn cho tất cả ngôn ngữ**: IndicTrans2 hỗ trợ Assamese và Manipuri nhưng **không hỗ trợ** Khasi và Mizo.
- **Đặc trưng ngôn ngữ khác biệt**: Khasi và Mizo thuộc nhóm ngôn ngữ khác (Austroasiatic và Tibeto-Burman), không nằm trong 22 ngôn ngữ chính thức được Ấn Độ lên lịch.

### Tại sao quan trọng?

- Hàng triệu người nói các ngôn ngữ này cần công cụ dịch máy phục vụ giao tiếp, giáo dục, hành chính.
- Đây là bài toán đại diện cho thách thức chung của NMT low-resource trên toàn cầu.
- Cần chiến lược transfer learning linh hoạt, tùy chỉnh theo đặc điểm từng ngôn ngữ.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Tổng quan kiến trúc

Toàn bộ hệ thống dựa trên kiến trúc **Transformer** (Vaswani, 2017), với hai nhánh chiến lược:

| Nhóm ngôn ngữ | Baseline model | Kiến trúc |
|---|---|---|
| en-as, en-mn | IndicTrans2 (pre-trained) | 18-layer encoder, 18-layer decoder |
| en-kh, en-mz | Multilingual model (tự huấn luyện) | 35-layer encoder, 3-layer decoder |

### 4.2 Chiến lược 1: Fine-tune IndicTrans2 (cho Assamese & Manipuri)

- **Ý tưởng**: Assamese và Manipuri nằm trong 22 ngôn ngữ được IndicTrans2 hỗ trợ → tận dụng trực tiếp kiến thức đã học.
- **Quy trình**:
  1. Lấy IndicTrans2 làm mô hình khởi tạo (checkpoint)
  2. Fine-tune trên dữ liệu WMT24 với các kỹ thuật tăng cường dữ liệu
  3. Áp dụng pipeline đầy đủ: DD → FT/BT → Denoise → TEL

### 4.3 Chiến lược 2: Multilingual Model + Transfer Learning (cho Khasi & Mizo)

- **Ý tưởng**: Khasi và Mizo không được IndicTrans2 hỗ trợ → phải tự xây dựng baseline từ đầu.
- **Lý do chọn Bengali làm ngôn ngữ pivot**: Bengali thuộc nhánh Indo-Aryan, có đặc trưng ngôn ngữ gần gũi với một số ngôn ngữ mục tiêu, và có dữ liệu phong phú (~8 triệu câu song ngữ Anh-Bengali).
- **Quy trình**:
  1. Gộp tất cả dữ liệu song ngữ: en-as, en-mn, en-kh, en-mz + en-bn (8M câu)
  2. Huấn luyện mô hình multilingual chung
  3. Fine-tune riêng cho en-kh và en-mz
  4. Áp dụng pipeline tương tự: DD → FT/BT → Denoise → TEL

### 4.4 Các kỹ thuật tối ưu hóa (Training Strategies)

#### a) Regularized Dropout (R-Drop)
- Mỗi mẫu dữ liệu đi qua forward pass **hai lần** với dropout khác nhau → tạo ra 2 phân phối output.
- Tối thiểu hóa **KL divergence hai chiều** giữa 2 phân phối đó.
- Giảm khoảng cách giữa training và inference (vì inference không dùng dropout).
- Hệ số λ = 5 cho tất cả subtask.

#### b) Data Diversification (DD)
- Sử dụng **1 forward model + 1 backward model** để đa dạng hóa dữ liệu huấn luyện.
- Dự đoán của các mô hình được gộp lại với dữ liệu gốc.
- Không cần dữ liệu đơn ngữ thêm, không thêm tham số mới.

#### c) Forward Translation (FT) — Self-Training
- Lấy mẫu từ dữ liệu đơn ngữ nguồn (2M câu tiếng Anh).
- Dùng mô hình "teacher" để dịch sang ngôn ngữ đích.
- Kết hợp dữ liệu tổng hợp + dữ liệu gốc để huấn luyện mô hình "student".

#### d) Back Translation (BT)
- Dùng dữ liệu đơn ngữ phía đích (as: 2.62M, mn: 2.14M, kh: 182K, mz: 1.9M).
- Sử dụng **sampling-based BT** (thay vì beam search) để tạo dữ liệu tổng hợp đa dạng hơn.
- Hiệu quả hơn greedy/beam search vì tạo ra nguồn đa dạng, giúp mô hình phân biệt dữ liệu gốc vs. tổng hợp.

#### e) Denoise
- Lọc bỏ dữ liệu nhiễu: bản dịch không chính xác, lỗi ngữ pháp, cấu trúc câu không tự nhiên.
- Giúp mô hình tập trung vào dữ liệu chất lượng cao, cải thiện robustness và generalization.

#### f) Transductive Ensemble Learning (TEL)
- Sử dụng nhiều mô hình riêng lẻ để dịch bộ test.
- Dùng dữ liệu dịch tổng hợp từ ensemble để fine-tune một mô hình mạnh.
- Tận dụng **transductive setting**: biết trước câu nguồn của test set.

### 4.5 Data Pre-processing Pipeline

1. Loại bỏ câu/cặp câu trùng lặp
2. Chuyển ký tự full-width → half-width
3. **FastText** để lọc câu sai ngôn ngữ
4. **Moses decoder** để chuẩn hóa dấu câu tiếng Anh
5. Lọc câu > 150 từ
6. **Fast-align** để lọc cặp câu có alignment kém
7. **SentencePiece (SPM)** cho subword segmentation, vocab = 32K
8. **LaBSE** (Language-Agnostic BERT Sentence Embedding) để đo semantic similarity → loại cặp câu có similarity < 0.75

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Dữ liệu

| Cặp ngôn ngữ | Dữ liệu song ngữ | Dữ liệu đơn ngữ (English) | Dữ liệu đơn ngữ (Indic) |
|---|---|---|---|
| en-as | 50K | 2M | 2.62M |
| en-mn | 21K | 2M | 2.14M |
| en-kh | 24K | 2M | 182K |
| en-mz | 50K | 2M | 1.9M |

Ngoài ra: ~8M câu song ngữ en-bn (Bengali) dùng cho multilingual baseline.

### 5.2 Hyperparameters

| Tham số | Subtask 1-2 (en-as, en-mn) | Subtask 3-4 (en-kh, en-mz) |
|---|---|---|
| Optimizer | Adam (β₁=0.9, β₂=0.98) | Adam |
| Learning rate | 3×10⁻⁵ | 5×10⁻⁴ |
| Warmup steps | 2,000 | 4,000 |
| Warmup LR | 10⁻⁷ | — |
| Dropout | 0.2 | — |
| Activation | GeLU | — |
| Update frequency | — | 2 |
| Checkpoint save | — | Mỗi 1,000 steps |
| R-Drop λ | 5 | 5 |
| Loss | Smoothed label cross-entropy | — |

### 5.3 Metrics

- **BLEU** (sacrebleu): Metric chính để đánh giá.
- **ChrF2** (character n-gram F-score, word order = 2): Metric phụ, phù hợp hơn cho ngôn ngữ giàu hình thái học.

### 5.4 Baselines

- **IndicTrans2** (cho en-as, en-mn): Mô hình mã nguồn mở hỗ trợ 22 ngôn ngữ Ấn Độ.
- **Multilingual model tự huấn luyện** (cho en-kh, en-mz): Transformer deep (35E-3D) huấn luyện trên dữ liệu gộp.

---

## 6. Kết quả chính (Key Results)

### 6.1 Kết quả en-as và en-mn (Fine-tune IndicTrans2)

| Cặp ngôn ngữ | Chiến lược | BLEU (test) | ChrF2 (test) | BLEU (dev) | ChrF2 (dev) |
|---|---|---|---|---|---|
| en→as | IndicTrans2 baseline | 18.9 | 51.4 | 14.7 | 44.8 |
| | + DD, FT, BT | 22.9 | 52.5 | 21.1 | 47.7 |
| | + denoise | 23.3 | 53.1 | 22.5 | 48.9 |
| | + TEL | **23.5** | **53.2** | **22.8** | **49.0** |
| en→mn | IndicTrans2 baseline | 11.9 | 48.5 | 11.9 | 48.5 |
| | + DD, FT, BT | 30.9 | 62.8 | 31.1 | 63.4 |
| | + denoise | 31.7 | 64.7 | 31.7 | 64.9 |
| | + TEL | **31.8** | **64.6** | **31.6** | **64.9** |
| as→en | IndicTrans2 baseline | 29.7 | 56.3 | 25.6 | 49.3 |
| | + DD, FT, BT | 35.8 | 58.6 | 35.0 | 54.5 |
| | + denoise | 36.1 | 58.6 | 34.8 | 54.6 |
| | + TEL | **36.2** | **59.4** | **33.7** | **54.2** |
| mn→en | IndicTrans2 baseline | 32.6 | 62.3 | 33.4 | 61.8 |
| | + DD, FT, BT | 47.5 | 70.8 | 47.0 | 69.7 |
| | + denoise | 47.7 | 70.8 | 47.2 | 69.7 |
| | + TEL | **47.9** | **70.8** | **47.4** | **69.8** |

**Nhận xét**: Cải thiện lớn nhất ở en→mn: **+19.9 BLEU** so với baseline (11.9 → 31.8), chủ yếu nhờ Data Diversification.

### 6.2 Kết quả en-kh và en-mz (Multilingual Model)

| Cặp ngôn ngữ | Chiến lược | BLEU (test) | ChrF2 (test) | BLEU (dev) | ChrF2 (dev) |
|---|---|---|---|---|---|
| en→kh | multilingual baseline | 17.4 | 40.4 | 17.0 | 39.7 |
| | + DD, FT, BT | 18.1 | 41.8 | 17.9 | 41.3 |
| | + denoise | 19.5 | 43.3 | 19.2 | 42.7 |
| | + TEL | **19.7** | **43.5** | **19.3** | **42.8** |
| en→mz | multilingual baseline | 25.0 | 51.6 | 22.3 | 46.6 |
| | + DD, FT, BT | 30.8 | 55.7 | 25.2 | 49.1 |
| | + denoise | 32.5 | 57.1 | 25.4 | 49.3 |
| | + TEL | **32.8** | **57.3** | **25.7** | **49.4** |
| kh→en | multilingual baseline | 15.1 | 37.7 | 15.0 | 38.1 |
| | + DD, FT, BT | 15.8 | 37.8 | 15.0 | 38.3 |
| | + denoise | 15.9 | 38.5 | 15.5 | 39.0 |
| | + TEL | **16.1** | **38.8** | **15.6** | **39.2** |
| mz→en | multilingual baseline | 26.7 | 48.2 | 22.9 | 44.0 |
| | + DD, FT, BT | 32.9 | 52.2 | 25.0 | 45.4 |
| | + denoise | 33.7 | 52.2 | 25.8 | 46.5 |
| | + TEL | **33.9** | **52.7** | **26.0** | **46.7** |

**Nhận xét**:
- Cải thiện lớn nhất ở en→mz: **+7.8 BLEU** (25.0 → 32.8), chủ yếu nhờ FT và BT.
- kh→en cải thiện ít nhất (**+1.0 BLEU**), có thể do dữ liệu đơn ngữ Khasi rất ít (chỉ 182K).
- Denoise đóng góp đáng kể: trung bình thêm ~1-2 BLEU sau khi đã áp dụng FT/BT.
- TEL mang lại cải thiện nhỏ (< 1 BLEU) nhưng nhất quán.

### 6.3 Phân tích đóng góp của từng kỹ thuật

| Kỹ thuật | Đóng góp trung bình (BLEU) | Nhận xét |
|---|---|---|
| DD + FT + BT | +3 đến +19 BLEU | Đóng góp lớn nhất, đặc biệt khi baseline yếu |
| Denoise | +0.5 đến +1.7 BLEU | Lọc dữ liệu chất lượng cao luôn có ích |
| TEL | < 1 BLEU | Cải thiện nhỏ nhưng ổn định, phù hợp giai đoạn cuối |

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Chiến lược phân biệt hợp lý (Differentiated Strategy)**:
   - Không áp dụng cùng một cách tiếp cận cho tất cả ngôn ngữ. Phân tích đặc trưng từng ngôn ngữ trước khi chọn baseline → thiết kế thực tế, có thể nhân rộng.

2. **Pipeline hoàn chỉnh và có hệ thống**:
   - Kết hợp đầy đủ các kỹ thuật: data filtering (LaBSE, FastText, fast-align) → data augmentation (FT, BT, DD) → regularization (R-Drop, denoise) → ensemble (TEL).
   - Mỗi bước đều có ablation study rõ ràng.

3. **Kết quả thực nghiệm ấn tượng**:
   - Cải thiện lên đến +19.9 BLEU cho en→mn, chứng minh rõ ràng hiệu quả của transfer learning cho low-resource.

4. **Data pre-processing pipeline kỹ lưỡng**:
   - Sử dụng LaBSE để lọc semantic similarity (threshold 0.75) — giải quyết vấn đề noisy parallel data phổ biến trong low-resource.

5. **Tận dụng Bengali như ngôn ngữ trung gian**:
   - Quyết định thêm 8M dữ liệu en-bn vào multilingual training là sáng tạo, khai thác được related language transfer.

### Điểm yếu

1. **Thiếu phân tích sâu về lý do chọn Bengali**:
   - Paper chỉ nêu Bengali thuộc nhánh Indo-Aryan, nhưng Khasi (Austroasiatic) và Mizo (Tibeto-Burman) thuộc các họ ngôn ngữ **hoàn toàn khác nhau**. Không có bằng chứng thuyết phục về "linguistic feature similarities" được chia sẻ.
   - Thiếu thí nghiệm so sánh: chọn Bengali vs. Hindi vs. ngôn ngữ khác → kết quả thay đổi như thế nào?

2. **Không có human evaluation**:
   - Chỉ dùng BLEU và ChrF2, không có đánh giá người. Với ngôn ngữ low-resource, automatic metrics có thể không phản ánh đúng chất lượng thực tế.

3. **Kiến trúc asymmetric chưa được giải thích rõ**:
   - Multilingual model dùng 35-layer encoder nhưng chỉ 3-layer decoder — tỷ lệ rất bất cân xứng. Paper không giải thích lý do chọn cấu hình này hay so sánh với các cấu hình khác.

4. **Thiếu so sánh với các hệ thống khác trong WMT24**:
   - Không có bảng so sánh kết quả với các đội tham gia khác, khó đánh giá vị trí tương đối của hệ thống.

5. **TEL có vấn đề về tính hợp lệ**:
   - TEL sử dụng transductive learning (biết trước câu nguồn test) → trong thực tế deployment thì không áp dụng được, chỉ có ý nghĩa trong competition setting.

6. **Ablation study không đầy đủ**:
   - Các kỹ thuật được thêm lũy tiến (cumulative) → không rõ đóng góp độc lập của từng kỹ thuật.
   - Không có thí nghiệm bỏ đi từng component riêng lẻ (leave-one-out ablation).

7. **Không đề cập computational cost**:
   - Không báo cáo thời gian huấn luyện, số GPU, tổng chi phí tính toán → khó tái tạo hoặc so sánh efficiency.

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT low-resource nói chung

1. **Chiến lược transfer learning phân biệt theo ngôn ngữ**:
   - Kiểm tra xem mô hình pre-trained nào đã hỗ trợ ngôn ngữ mục tiêu → ưu tiên fine-tune. Nếu không → xây dựng multilingual baseline từ ngôn ngữ liên quan.
   - Áp dụng được cho bài toán MT của tiếng Việt với các ngôn ngữ dân tộc thiểu số.

2. **Pipeline data filtering đa tầng**:
   - FastText (lọc ngôn ngữ) → fast-align (lọc alignment) → LaBSE (lọc semantic similarity) → áp dụng trực tiếp cho bất kỳ bài toán nào có dữ liệu song ngữ noisy.

3. **Kết hợp FT + BT + DD**:
   - Ba kỹ thuật data augmentation bổ trợ nhau, tạo hiệu ứng synergy mạnh. Có thể áp dụng ngay cho cặp ngôn ngữ low-resource bất kỳ.

4. **Sampling BT thay vì beam search BT**:
   - Tạo dữ liệu tổng hợp đa dạng hơn, đặc biệt hiệu quả khi kết hợp với FT.

5. **Sử dụng ngôn ngữ liên quan (related language) làm bridge**:
   - Thêm dữ liệu từ ngôn ngữ có tài nguyên phong phú cùng họ/vùng để cải thiện multilingual model. Với tiếng Việt, có thể xem xét tiếng Trung hoặc tiếng Khmer tùy ngôn ngữ đích.

6. **R-Drop cho regularization**:
   - Kỹ thuật đơn giản, không cần thêm dữ liệu hay tham số, cải thiện nhất quán → nên áp dụng mặc định trong training pipeline.

7. **LaBSE threshold 0.75 cho lọc parallel data**:
   - Mức ngưỡng cụ thể có thể dùng làm điểm khởi đầu cho bài toán tương tự, cần điều chỉnh theo đặc trưng ngôn ngữ.

---

## 9. Các paper liên quan quan trọng

### Mô hình nền tảng
| Paper | Nội dung | Tại sao cần đọc |
|---|---|---|
| **Gala et al. (2023)** — IndicTrans2 | Mô hình MT mã nguồn mở cho 22 ngôn ngữ Ấn Độ | Baseline model chính, kiến trúc transformer multilingual cho Indic languages |
| **Vaswani (2017)** — Attention Is All You Need | Kiến trúc Transformer gốc | Nền tảng kiến trúc của toàn bộ hệ thống |

### Data Augmentation
| Paper | Nội dung | Tại sao cần đọc |
|---|---|---|
| **Sennrich et al. (2016)** | Back Translation cho NMT | Kỹ thuật BT kinh điển, nền tảng cho data augmentation |
| **Edunov et al. (2018)** | Understanding BT at scale | Phân tích sâu các biến thể BT: sampling vs. beam vs. noised |
| **Caswell et al. (2019)** | Tagged Back-Translation | Tagged BT đánh dấu dữ liệu tổng hợp, đơn giản và hiệu quả |
| **Abdulmumin (2021)** | Enhanced BT with self-training (FT) | Forward translation + self-training cho low-resource |
| **Nguyen et al. (2020)** | Data Diversification | Tăng cường dữ liệu không cần dữ liệu đơn ngữ thêm |

### Kỹ thuật huấn luyện
| Paper | Nội dung | Tại sao cần đọc |
|---|---|---|
| **Wu et al. (2021)** — R-Drop | Regularized Dropout | Regularization đơn giản qua KL divergence giữa 2 forward pass |
| **Wang et al. (2020)** | Transductive Ensemble Learning | Ensemble cho NMT trong transductive setting |
| **Zhang et al. (2019)** | Curriculum Learning for domain adaptation | Curriculum learning cho NMT, liên quan đến chiến lược huấn luyện |

### Công cụ tiền xử lý
| Paper | Nội dung | Tại sao cần đọc |
|---|---|---|
| **Feng et al. (2022)** — LaBSE | Language-Agnostic BERT Sentence Embedding | Đo semantic similarity đa ngôn ngữ, lọc dữ liệu song ngữ |
| **Kudo & Richardson (2018)** — SentencePiece | Subword segmentation | Tokenization không phụ thuộc ngôn ngữ |
| **Joulin et al. (2016)** — FastText | Phân loại ngôn ngữ nhanh | Lọc câu sai ngôn ngữ trong dữ liệu noisy |
| **Dyer et al. (2013)** — fast-align | Word alignment nhanh | Lọc cặp câu có alignment kém |

### Hệ thống WMT trước đó của HW-TSC
| Paper | Nội dung |
|---|---|
| **Wei et al. (2021)** | HW-TSC tại WMT 2021 |
| **Wei et al. (2022)** | HW-TSC tại WMT 2022 |
| **Wei et al. (2023)** | Text Style Transfer Back-Translation (ACL 2023) |
| **Wu et al. (2023)** | HW-TSC cho WMT23 Biomedical MT |

---

## 10. Tóm tắt một dòng

> Paper trình bày một hệ thống MT low-resource cho 4 ngôn ngữ Ấn Độ, sử dụng chiến lược transfer learning phân biệt: fine-tune IndicTrans2 cho ngôn ngữ được hỗ trợ (as, mn) và xây dựng multilingual baseline với Bengali bridge cho ngôn ngữ chưa được hỗ trợ (kh, mz), kết hợp pipeline data augmentation đa tầng (FT + BT + DD + denoise + TEL) đạt cải thiện lên đến +19.9 BLEU.
