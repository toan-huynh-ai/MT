# Tóm tắt Paper: Low-resource Neural Machine Translation with Morphological Modeling

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Low-resource Neural Machine Translation with Morphological Modeling |
| **Authors** | Antoine Nzeyimana (University of Massachusetts Amherst) |
| **Venue** | NAACL 2024 |
| **Year** | 2024 |
| **arXiv** | [2404.02392](https://arxiv.org/abs/2404.02392) |
| **Code** | [github.com/anzeyimana/KinMT_NAACL2024](https://github.com/anzeyimana/KinMT_NAACL2024) |
| **Ngôn ngữ đánh giá** | Kinyarwanda ↔ English |

---

## 2. Tóm tắt (Abstract)

Paper đề xuất một **framework toàn diện** cho dịch máy neural (NMT) ở ngôn ngữ low-resource có hình thái học phức tạp (morphologically-rich languages — MRLs). Thay vì dựa vào sub-word tokenization (BPE) chỉ xử lý được surface form, tác giả xây dựng kiến trúc **two-tier transformer** kết hợp thông tin hình thái học tường minh (explicit morphological information) ở cả phía source và target.

Ba đóng góp chính:
1. **Morphological modeling**: Kiến trúc Morpho-Encoder hai tầng mã hóa stem, affixes, POS tag, affix set — cho phép open-vocabulary translation.
2. **Attention augmentation**: Tích hợp pre-trained BERT embeddings và cross-positional (XPOS) encodings vào cơ chế attention để cải thiện alignment giữa source-target.
3. **Data augmentation**: Nhiều kỹ thuật tăng cường dữ liệu (copy data, lexical data, backtranslation, code-switching) để bù đắp sự thiếu hụt parallel data.

Kết quả: Model 400M parameters đạt hiệu suất **cạnh tranh với NLLB-200 3.3B** và **vượt Google Translate trên TICO-19** cho hướng En→Kin.

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Dịch máy cho ngôn ngữ **low-resource** + **morphologically-rich** (như Kinyarwanda, ~15 triệu người nói) đối mặt hai thách thức đồng thời:

1. **Thiếu dữ liệu song ngữ** (parallel data scarcity): Số lượng câu song ngữ rất hạn chế so với các cặp ngôn ngữ phổ biến.
2. **Hình thái học phức tạp**: Một từ gốc (stem) có thể kết hợp với nhiều phụ tố (affixes) tạo ra hàng trăm dạng bề mặt (surface forms) khác nhau.

### Tại sao BPE không đủ?

| Hạn chế của BPE | Giải thích |
|---|---|
| Chỉ dựa trên surface form | Không hiểu cấu trúc hình thái ngầm bên dưới |
| Không xử lý morpho-graphemic alternations | Khi ghép morphemes, chính tả thay đổi (ví dụ: phụ âm đồng hóa) → BPE tách sai |
| Không xử lý non-concatenative morphology | Các ngôn ngữ có infixation, reduplication → BPE bất lực |
| Vocabulary không bao phủ | Trong low-resource, nhiều dạng biến thể hình thái không xuất hiện trong training data |

### Tại sao quan trọng?

- Kinyarwanda là ngôn ngữ Bantu với hệ thống hình thái **agglutinative** rất phong phú — một verb có thể mang nhiều prefix/suffix biểu thị subject, object, tense, aspect, mood.
- Khi model gặp tổ hợp morpheme mới (chưa thấy trong training), BPE-based model sẽ **hallucinate** hoặc **fail to translate**.
- Thêm vào đó, vocabulary mismatch giữa source và target khiến model khó **copy proper names** qua nguyên dạng.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1. Tổng quan kiến trúc

Kiến trúc gồm 3 thành phần chính xây dựng trên nền Transformer (pre-LayerNorm):

```
Source text → Morphological Analyzer → Morpho-Encoder → Main Encoder (with attention augmentation)
                                                              ↓
                                                     Auto-regressive Decoder → MTML prediction heads
                                                              ↓
                                                     Morphological Synthesizer → Target surface forms
```

### 4.2. Morphological Encoding (Source-side)

**Morpho-Encoder** là một transformer encoder nhỏ (3 layers, dim=128, 4 heads) xử lý ở cấp độ **word composition**:

- **Input**: Mỗi từ được phân tích thành 4 loại đơn vị:
  1. **Stem** (thân từ): Đơn vị từ vựng gốc
  2. **Affixes** (phụ tố): Số lượng biến đổi — prefix, suffix, infix
  3. **POS tag** (coarse-grained): Nhãn từ loại thô (verb, noun, adj...)
  4. **Affix set index** (fine-grained): Index của tổ hợp affix thường gặp — tương đương morphological tag chi tiết (24,000 affix sets)
- **Processing**: Xử lý tất cả đơn vị như một **set** (không có ordering information), vì không có đơn vị nào lặp lại trong cùng một từ.
- **Output**: Hidden vectors của stem, POS tag, affix set được **pull & concatenate** → tạo word vector đưa vào main sequence encoder.

**Điểm mấu chốt**: Morpho-Encoder áp dụng cho **cả encoder lẫn decoder input**. Đối với proper names, numbers, punctuation → dùng BPE và coi sub-word tokens như special stems không có affixes.

### 4.3. Attention Augmentation

Tác giả mở rộng cơ chế attention bằng cách thêm bias terms vào attention logits α_ij, tổng quát hóa ý tưởng untied positional encoding của Ke et al. (2020):

#### a) Source-to-source self-attention (Encoder)

Attention logits được augment với **3 thành phần**:

| Thành phần | Vai trò |
|---|---|
| Token-token attention | Tương tác ngữ nghĩa giữa hidden states (tiêu chuẩn) |
| Positional encoding (absolute + relative) | Mã hóa vị trí tương tự Ke et al. (2020) |
| **BERT embeddings** | Tích hợp contextual embeddings từ pre-trained KinyaBERT/RoBERTa |

→ Chia cho √(3d) thay vì √d để normalize 3 thành phần.

#### b) Target-to-source cross-attention (Decoder)

Ngoài BERT augmentation, tác giả đề xuất **Cross-Positional (XPOS) Encodings**:

- **Ý tưởng**: Học mối quan hệ **word order** giữa source và target language.
- **Cơ chế**: Absolute và relative positional embeddings **xuyên** từ target position sang source position (cross-positional).
- **Tại sao cần**: Kinyarwanda và English có thứ tự từ khác nhau (SVO vs. các biến thể) → XPOS giúp decoder biết nên attend vào vị trí nào của source tương ứng với vị trí hiện tại của target.

### 4.4. Target-side Morphology Learning

Ở phía target (khi target là MRL), decoder phải dự đoán **cùng loại đơn vị hình thái** như input:

**Multi-Task Multi-Label (MTML) classification** với 4 loss functions:

| Loss | Loại | Dự đoán |
|---|---|---|
| ℓ_S | Cross-Entropy | Stem |
| ℓ_A | Binary Cross-Entropy (multi-label) | Từng affix riêng lẻ |
| ℓ_P | Cross-Entropy | POS tag |
| ℓ_AS | Cross-Entropy | Affix set |

**Vấn đề tối ưu đa mục tiêu**: Naive summation các loss → biased vì range và difficulty khác nhau, gradient có thể conflict. Giải pháp: **Gradient Vaccine** (Wang et al., 2020) — align gradient updates bằng cách khuyến khích tính consistent về hướng giữa các gradients.

### 4.5. Morphological Inference (Decoding)

Beam search được adapt cho morphological output với 4 bước:

1. **Voting on inflection group**: Tính xác suất cho từng nhóm biến cách (verb, noun...) bằng cách aggregate top-M dự đoán của stem, POS, affix set.
2. **Filtering**: Lọc bỏ stems/affixes ít khả năng, áp dụng cut-off gap δ và minimum affix probability γ.
3. **Selecting target affixes**: Merge affix set's own affixes với extra predicted affixes.
4. **Morphological synthesis**: Gọi morphological synthesizer để tạo surface form từ (stem, affixes) — phải tuân thủ **morpho-graphemic rules** của ngôn ngữ.

→ Output: Danh sách candidate surface forms có điểm, đưa vào beam search cấp sequence.

### 4.6. Data Augmentation

| Kỹ thuật | Mô tả | Mục đích |
|---|---|---|
| **Copy data** | Proper names, numbers, world cities, CMU names → same src=tgt | Dạy model copy untranslatable tokens |
| **Number spelling** | 200K random integers → chữ viết bằng Kin & En | Xử lý number translation |
| **Lexical data** | Từ điển song ngữ (Iriza, kinyarwanda.net, 8K manually translated) | Tăng lexical coverage |
| **Code-switching** | Thêm từ tiếng Pháp, Swahili phổ biến vào src side | Xử lý hiện tượng trộn ngôn ngữ |
| **Backtranslation** | ~16M câu Kinyarwanda + ~16M câu English monolingual | Leverage unlabeled data |

### 4.7. Dataset Construction

Tác giả tự xây dựng parallel corpus từ public-domain sources:

| Nguồn | Kích thước | Đặc điểm |
|---|---|---|
| Jw.org website | 562,417 câu | Nội dung tôn giáo, đa dạng chủ đề |
| Rwanda's Official Gazette | 113,127 câu | Văn bản pháp luật, chất lượng cao (3 cột Kin/En/Fr) |
| Iriza dictionary 2006 | 108,870 từ | Từ điển song ngữ, trích xuất từ PDF |
| Kinyarwanda.net | 10,653 từ | Từ điển online do volunteers xây dựng |
| Manually translated | 8,000 từ | Loanwords, alternate spellings |
| Spelled numbers | 200,000 cụm | Số → chữ |
| Copy data | 157,668 từ | Proper names |
| Code-switching terms | 10,276 từ | Từ ngoại lai (Pháp, Swahili) |

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1. Benchmarks

| Benchmark | Domain | Đặc điểm |
|---|---|---|
| **FLORES-200** (Costa-jussà et al., 2022) | Wikipedia | Benchmark đa ngôn ngữ chuẩn, có dev+test |
| **MAFAND-MT** (Adelani et al., 2022) | News | Dành cho ngôn ngữ châu Phi |
| **TICO-19** (Anastasopoulos et al., 2020) | Covid-19 | Dịch tài liệu y tế, out-of-domain |

### 5.2. Metrics

| Metric | Mô tả |
|---|---|
| **ChrF++** (Popović, 2017) | Character + word n-gram F-score, không phụ thuộc tokenization, tương quan tốt hơn BLEU với human judgment |
| **BLEURT** (Sellam et al., 2020) | Embedding-based metric, chỉ dùng cho Kin→En (không có BLEURT pre-trained cho Kinyarwanda) |
| **chrF2** (SacreBLEU) | Dùng cho so sánh final models, với 10,000 bootstraps cho significance testing |

### 5.3. Baselines

| Model | Params | Đặc điểm |
|---|---|---|
| **BPE Seq2Seq + XPOS** | 187M | Transformer cùng backbone, BPE tokenization (SentencePiece 32K), không morpho/BERT |
| **Helsinki-opus-mt** (Tiedemann & Thottingal, 2020) | 76M | Open-source translation model |
| **NLLB-200 600M** (distilled) | 600M | Meta's multilingual model, distilled version |
| **NLLB-200 3.3B** | 3,300M | Meta's multilingual model, full version |
| **mBART** (Liu et al., 2020) fine-tuned | 610M | Multilingual denoising pre-training, fine-tuned trên dataset của tác giả |
| **Google Translate** | N/A | Commercial system |

### 5.4. Setup

- **Framework**: PyTorch 1.13.1, implement from scratch
- **Hardware**: 8x NVIDIA RTX 4090, 256GB RAM
- **Training**: Mixed precision (BFLOAT-16), Adam optimizer, inverse sqrt LR schedule
- **Hyperparameters chính**:
  - Hidden dim: 768, FFN dim: 3072, 12 attention heads
  - Encoder layers: 5 (with BERT) / 8 (without)
  - Decoder layers: 7 (with GPT) / 8 (without)
  - Morpho-Encoder: 3 layers, dim=128, 4 heads
  - Batch size: 32K tokens, Peak LR: 0.0005, Warmup: 8000 steps
  - Beam width: 4

---

## 6. Kết quả chính (Key Results)

### 6.1. Ablation Study: Từng thành phần đóng góp bao nhiêu?

#### a) Copy data (Table 1 — Kin→En)

| Setup | Avg BLEURT | Avg ChrF++ |
|---|---|---|
| Không có copy data | 53.3 | 36.6 |
| **Có copy data** | **54.9** | **38.0** |

→ Copy data cải thiện **+1.6 BLEURT, +1.4 ChrF++** trung bình.

#### b) Attention augmentation (Table 2 — Kin→En)

| Setup | Params | Avg BLEURT | Avg ChrF++ |
|---|---|---|---|
| Morpho (baseline) | 188M | 55.0 | 38.5 |
| + XPOS | 190M | 55.8 | 38.8 |
| + BERT | 190M | 57.5 | 39.7 |
| **+ BERT + XPOS** | **192M** | **58.2** | **40.5** |

→ BERT augmentation đóng góp lớn nhất (+2.5 BLEURT). XPOS bổ sung thêm (+0.7 BLEURT). Kết hợp cả hai cho kết quả tốt nhất: **+3.2 BLEURT, +2.0 ChrF++** so với Morpho baseline.

#### c) Lexical data — bilingual dictionaries (Table 3 — Kin→En)

| Setup | Avg BLEURT | Avg ChrF++ |
|---|---|---|
| Không có lexical data | 56.8 | 39.2 |
| **Có lexical data** | **58.2** | **40.5** |

→ Từ điển song ngữ cải thiện **+1.4 BLEURT, +1.3 ChrF++**.

#### d) Morphological modeling vs. BPE (Table 4 — Kin→En, Table 5 — En→Kin)

**Kin→En:**

| Setup | Avg BLEURT | Avg ChrF++ |
|---|---|---|
| BPE Seq2Seq + XPOS | 48.7 | 33.5 |
| **Morpho + XPOS** | **55.8** | **38.8** |

→ Morphological modeling cải thiện **+7.1 BLEURT, +5.3 ChrF++** — khoảng cách rất lớn.

**En→Kin:**

| Setup | Avg ChrF++ (Test) |
|---|---|
| BPE Seq2Seq + XPOS | 34.7 |
| Morpho + XPOS (Loss summation) | 37.0 |
| **Morpho + XPOS + GradVacc** | **38.0** |

→ Target-side morphology cải thiện **+3.3 ChrF++** (với Gradient Vaccine).

### 6.2. So sánh với Large Multilingual Models (Final results)

#### En→Kin (Table 6):

| Model | Params | FLORES Test | MAFAND Test | TICO-19 Test |
|---|---|---|---|---|
| Helsinki-opus-mt | 76M | 36.7 | 37.3 | 27.2 |
| NLLB-200 600M | 600M | 45.5 | 52.7 | 46.3 |
| mBART fine-tuned | 610M | 48.5 | 54.1 | 45.2 |
| NLLB-200 3.3B | 3,300M | 50.9 | 58.6 | 52.4 |
| **Ours** | **403M** | **53.1** | **61.9** | **50.2*** |
| Google Translate | N/A | 60.0 | 87.5 | 49.6 |

*\* Trên TICO-19, model của tác giả **vượt Google Translate** (p-value < 0.002)*

→ Model 403M params **vượt NLLB-200 3.3B** (lớn gấp 8 lần) trên FLORES và MAFAND.

#### Kin→En (Table 7):

| Model | Params | FLORES Test | MAFAND Test | TICO-19 Test |
|---|---|---|---|---|
| Helsinki-opus-mt | 76M | 35.1 | 35.1 | 29.7 |
| NLLB-200 600M | 600M | 52.3 | 54.9 | 48.6 |
| mBART fine-tuned | 610M | 43.1 | 46.0 | 38.8 |
| NLLB-200 3.3B | 3,300M | 56.0 | 59.6 | 54.1 |
| **Ours** | **396M** | **54.8** | **59.2** | **50.1** |
| Google Translate | N/A | 59.1 | 64.0 | 52.4 |

→ Kin→En: Model vượt NLLB-200 600M rõ rệt, **gần bằng NLLB-200 3.3B** trên MAFAND, và vượt mBART fine-tuned trên mọi benchmark.

### 6.3. Tóm tắt key takeaways

1. **Morphological modeling mang lại cải thiện lớn nhất** — đặc biệt ở source-side (+7.1 BLEURT cho Kin→En).
2. **BERT attention augmentation rất hiệu quả** — leverage pre-trained knowledge mà không cần fine-tune toàn bộ PLM.
3. **Gradient Vaccine tốt hơn naive loss summation** cho multi-task morphology prediction (+1.0 ChrF++).
4. **Data augmentation (copy, lexical, backtranslation) đều đóng góp tích cực**.
5. **Model nhỏ hơn 8x nhưng competitive/vượt trội** so với NLLB-200 3.3B nhờ language-specific inductive bias.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

| # | Điểm mạnh | Phân tích |
|---|---|---|
| 1 | **Explicit morphological modeling thay vì BPE** | Giải quyết tận gốc vấn đề vocabulary explosion cho MRLs — morphemes là đơn vị ngữ nghĩa thực sự, cho phép tổ hợp mới (open-vocabulary) |
| 2 | **End-to-end framework** | Bao phủ cả source encoding, target decoding, attention augmentation, data augmentation — không chỉ là trick đơn lẻ |
| 3 | **Hiệu quả tham số** | 400M params đạt kết quả tương đương/vượt 3.3B params models — chứng tỏ language-specific design tốt hơn brute-force scaling |
| 4 | **Ablation study kỹ lưỡng** | Đánh giá riêng rẽ từng thành phần trên 3 benchmarks, nhiều domains khác nhau |
| 5 | **Practical data solutions** | Xây dựng tools trích xuất parallel data từ PDF (Official Gazette), web crawling — giải quyết vấn đề thực tế |
| 6 | **Open-source** | Code, tools đều public — cho phép reproduce và extend |
| 7 | **Attention augmentation tổng quát** | XPOS encoding có thể áp dụng cho bất kỳ cặp ngôn ngữ nào có word order khác biệt |

### Điểm yếu

| # | Điểm yếu | Phân tích |
|---|---|---|
| 1 | **Phụ thuộc morphological analyzer** | Yêu cầu có sẵn bộ phân tích hình thái chất lượng — không phải ngôn ngữ low-resource nào cũng có. Đây là barrier lớn nhất để transfer sang ngôn ngữ khác |
| 2 | **Chỉ đánh giá trên 1 ngôn ngữ** | Kinyarwanda duy nhất — chưa chứng minh generalizability sang các MRLs khác (Turkish, Finnish, Swahili...) |
| 3 | **Decoding chậm** | Morphological inference algorithm có thêm filtering + synthesis steps → chậm hơn standard beam search đáng kể |
| 4 | **Vẫn hallucinate** | Với unseen words, model vẫn sinh output sai — chưa giải quyết triệt để |
| 5 | **Copy mechanism chưa hoàn hảo** | Data augmentation approach cho copying đôi khi tạo inexact copies |
| 6 | **Cần morphological synthesizer** | Ở target side, cần synthesizer tuân thủ morpho-graphemic rules — thêm một dependency nữa |
| 7 | **Không so sánh với character-level models** | Thiếu baseline so sánh với character-based NMT (Ataman & Federico, 2018), byte-level models |
| 8 | **BLEURT chỉ dùng cho Kin→En** | Không đánh giá được embedding-based metric cho hướng En→Kin, giảm tính toàn diện |

### Các lầm tưởng cần tránh

- **"Morphological modeling luôn tốt hơn BPE"**: Chỉ đúng khi có morphological analyzer tốt. Với unsupervised morphological segmentation (Macháček et al., 2018), kết quả **không cải thiện**.
- **"Model nhỏ hơn = hiệu quả hơn"**: Model vẫn cần 8x RTX 4090 để train, và inference chậm hơn do morphological decoding. Trade-off là **chất lượng dịch vs. tốc độ/tài nguyên phát triển**.
- **"Approach này scale được cho mọi ngôn ngữ"**: Yêu cầu (1) morphological analyzer, (2) morphological synthesizer, (3) pre-trained BERT cho source language — 3 tài nguyên hiếm có cho hầu hết ngôn ngữ low-resource.

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT low-resource nói chung

| # | Ý tưởng | Khả năng áp dụng |
|---|---|---|
| 1 | **Attention augmentation với pre-trained LM** | Rất applicable — có thể tích hợp XLM-R, mBERT embeddings vào attention thay vì chỉ dùng làm initialization. Generic approach, không cần morphological analyzer |
| 2 | **Cross-positional (XPOS) encodings** | Hữu ích cho các cặp ngôn ngữ có word order khác biệt lớn (VD: Vietnamese-Japanese, English-Korean). Dễ implement, chi phí parameter thấp (+2M params) |
| 3 | **Copy data augmentation** | Trực tiếp áp dụng cho bất kỳ cặp ngôn ngữ nào — thêm proper names, numbers, URLs vào training data với src=tgt |
| 4 | **Lexical data từ bilingual dictionaries** | Rất thực tế — nhiều ngôn ngữ low-resource có từ điển song ngữ (dù nhỏ). Đã chứng minh cải thiện +1.3 ChrF++ |
| 5 | **Multi-task target-side prediction** | Nếu target language có rich morphology, dự đoán morphological components riêng rẽ thay vì surface form trực tiếp → giảm vocabulary size, tăng generalization |
| 6 | **Official Gazette / Government documents** | Nguồn parallel data chất lượng cao bị bỏ qua — nhiều quốc gia đa ngôn ngữ công bố văn bản chính thức bằng nhiều thứ tiếng |
| 7 | **Gradient Vaccine cho multi-task learning** | Khi có nhiều loss functions xung đột, Gradient Vaccine cải thiện convergence — áp dụng được cho bất kỳ multi-task NMT nào |

### Cho bài toán Vietnamese-English MT cụ thể

- **XPOS encodings**: Vietnamese (SVO) và English (SVO) có word order khá tương đồng, nên XPOS có thể ít hiệu quả hơn so với Kin-En. Tuy nhiên, với các cấu trúc phức tạp (relative clause, passive voice), vẫn có thể hữu ích.
- **Copy data + Lexical data**: Trực tiếp áp dụng — đặc biệt cho proper names (tên riêng Việt Nam không có trong English training data).
- **Attention augmentation với PhoBERT/ViDeBERTa**: Có thể tích hợp embeddings từ PhoBERT vào encoder attention thay vì chỉ dùng làm feature extraction.

---

## 9. Các paper liên quan quan trọng

### Morphological Modeling trong NMT

| Paper | Nội dung chính |
|---|---|
| **Ataman & Federico (2018)** — *Compositional Representation of Morphologically-Rich Input for NMT* | RNN-based word compositional model cho MRLs — tiền thân trực tiếp của Morpho-Encoder |
| **Weller-Di Marco & Fraser (2020)** — *Modeling Word Formation in English-German NMT* | Source + target morphology modeling với lemma+tag representation cho En-De |
| **Passban et al. (2018)** — *Improving Character-Based Decoding Using Target-Side Morphological Information* | Multi-task learning cho target-side morphology |
| **Macháček et al. (2018)** — *Morphological and Language-Agnostic Word Segmentation for NMT* | **Kết quả tiêu cực**: unsupervised morphological analysis không cải thiện NMT |
| **Nzeyimana & Rubungo (2022)** — *KinyaBERT: A Morphology-Aware Kinyarwanda Language Model* | Kiến trúc two-tier gốc mà paper này mở rộng cho NMT. ACL 2022 |

### Pre-trained LM Integration trong NMT

| Paper | Nội dung chính |
|---|---|
| **Zhu et al. (2020)** — *Incorporating BERT into Neural Machine Translation* | Drop-net scheme để tích hợp BERT embeddings vào NMT |
| **Sun et al. (2021)** — *Multilingual Translation via Grafting Pre-trained Language Models* | Grafting PLM vào NMT architecture |
| **Ke et al. (2020)** — *Rethinking Positional Encoding in Language Pre-training* | Untied positional encoding — cơ sở cho attention augmentation trong paper này |

### Data & Evaluation

| Paper | Nội dung chính |
|---|---|
| **Costa-jussà et al. (2022)** — *No Language Left Behind (NLLB)* | NLLB-200 model + FLORES-200 benchmark — baseline chính |
| **Adelani et al. (2022)** — *A Few Thousand Translations Go a Long Way!* | MAFAND-MT benchmark cho ngôn ngữ châu Phi |
| **Edunov et al. (2018)** — *Understanding Back-Translation at Scale* | Backtranslation technique — cơ sở cho data augmentation |
| **Wang et al. (2020)** — *Gradient Vaccine* | Multi-task optimization technique dùng cho MTML training |

### Tokenization & Subword

| Paper | Nội dung chính |
|---|---|
| **Sennrich et al. (2016)** — *Neural Machine Translation of Rare Words with Subword Units* | BPE tokenization — baseline approach mà paper này so sánh |
| **Kudo & Richardson (2018)** — *SentencePiece* | Tokenizer dùng cho BPE baseline |

---

## 10. Tổng kết

Paper này là một **case study toàn diện** về việc kết hợp nhiều kỹ thuật (morphological modeling, attention augmentation, data augmentation) để xây dựng NMT system chất lượng cao cho ngôn ngữ low-resource có hình thái học phức tạp. Điểm nổi bật nhất là chứng minh rằng **language-specific inductive bias** (thông qua explicit morphology) có thể bù đắp cho thiếu hụt dữ liệu và cho kết quả tốt hơn cả model lớn gấp nhiều lần nhưng language-agnostic.

Tuy nhiên, **barrier chính để mở rộng** là yêu cầu về morphological analyzer và synthesizer — hai công cụ mà đa số ngôn ngữ low-resource chưa có. Đây là trade-off cốt lõi: **đầu tư xây dựng NLP tools cơ bản** vs. **dựa vào multilingual models lớn** (NLLB, mBART).
