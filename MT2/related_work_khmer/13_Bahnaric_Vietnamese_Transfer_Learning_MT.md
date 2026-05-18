# Tóm tắt Paper: Bahnaric-Vietnamese Translation Using Transfer Learning of Seq2Seq Pre-training LM

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Towards Cultural Bridge by Bahnaric-Vietnamese Translation Using Transfer Learning of Sequence-To-Sequence Pre-training Language Model |
| **Authors** | Phan Tran Minh Dat, Vo Hoang Nhat Khang, Quan Thanh Tho |
| **Venue** | arXiv preprint (cs.CL) |
| **Year** | 2025 (submitted 16/05/2025) |
| **arXiv** | [2505.11421](https://arxiv.org/abs/2505.11421) |
| **Affiliations** | Ho Chi Minh City University of Technology (HCMUT), VNU-HCM (URA Research Group) |
| **Paper liên quan cùng nhóm** | Nguyen et al., "Serving the Underserved: Leveraging BARTBahnar Language Model for Bahnaric-Vietnamese Translation", LM4UC @ ACL 2025 ([ACL Anthology](https://aclanthology.org/2025.lm4uc-1.5/)); Vo et al., "Revitalizing Bahnaric Language through Neural Machine Translation", AAAI 2024 |

---

## 2. Tóm tắt (Abstract)

Paper khám phá hành trình xây dựng hệ thống dịch máy Bahnaric-Vietnamese nhằm **kết nối văn hóa** giữa hai nhóm dân tộc tại Việt Nam. Thách thức lớn nhất là **thiếu hụt nghiêm trọng tài nguyên** cho ngôn ngữ Bahnar: từ vựng, ngữ pháp, mẫu hội thoại, và corpus song ngữ đều cực kỳ hạn chế.

Phương pháp đề xuất:
- **Transfer learning** từ mô hình ngôn ngữ tiếng Việt pre-trained, cụ thể là mô hình **sequence-to-sequence** (encoder-decoder), không phải encoder-only (BERT) hay decoder-only (GPT).
- Tận dụng **sự tương đồng đáng kể** giữa tiếng Bahnar và tiếng Việt (cùng thuộc ngữ hệ Austroasiatic) để thực hiện transfer learning từ language model sang machine translation.
- **Data augmentation** để tăng cường dữ liệu huấn luyện hạn chế.
- **Heuristic methods** để cải thiện độ chính xác dịch thuật.

Kết quả được xác nhận là hiệu quả cao, đóng góp vào việc bảo tồn và mở rộng ngôn ngữ.

---

## 3. Bài toán giải quyết (Problem Statement)

### Bối cảnh

**Người Bahnar** là một trong 54 dân tộc thiểu số tại Việt Nam, chiếm khoảng **0.3% dân số** cả nước, sinh sống chủ yếu ở khu vực **Tây Nguyên** (Central Highlands). Ngôn ngữ Bahnar thuộc nhóm **Central Bahnaric**, nhánh **Austroasiatic** (Mon-Khmer) — cùng ngữ hệ với tiếng Việt nhưng có nhiều đặc trưng hình thái học riêng biệt.

### Vấn đề cốt lõi

1. **Extremely low-resource**: Bahnar là ngôn ngữ cực kỳ ít tài nguyên số:
   - Không có corpus song ngữ quy mô lớn
   - Thiếu từ điển điện tử, công cụ NLP, và benchmark đánh giá
   - Tài liệu chủ yếu tồn tại dạng in (sách tôn giáo, báo địa phương, bài hát)
2. **Mất cân bằng tài nguyên**: Tiếng Việt là ngôn ngữ có tài nguyên trung bình–cao (BARTPho pre-trained trên 145 triệu câu), trong khi Bahnar gần như bắt đầu từ số không.
3. **Rào cản giao tiếp**: Người Bahnar thiếu tiếp cận công bằng đến thông tin số, tài liệu giáo dục, và dịch vụ ngôn ngữ AI.

### Tại sao quan trọng?

- **Bảo tồn văn hóa**: Ngôn ngữ là xương sống của bản sắc dân tộc; mất ngôn ngữ đồng nghĩa mất di sản văn hóa.
- **Công bằng số (Digital equity)**: Cộng đồng dân tộc thiểu số cần được tiếp cận các công nghệ AI ngôn ngữ.
- **Chính sách quốc gia**: Chính phủ Việt Nam có chương trình bảo vệ di sản văn hóa-ngôn ngữ dân tộc thiểu số (KC-4.0/19-25).

### Đặc trưng ngôn ngữ Bahnar (so với tiếng Việt)

| Đặc điểm | Tiếng Việt | Bahnar |
|---|---|---|
| **Hình thái học** | Analytic/isolating (đơn lập) | Agglutinative (chắp dính), có prefixation & infixation |
| **Thanh điệu** | 6 thanh | Ít hoặc không có |
| **Cấu trúc từ** | Đơn âm tiết | Đa âm tiết |
| **Động từ** | Đồng nhất | Nhiều lớp động từ, causative (pơ-), passive/reciprocal (tơ-), completive (jo-) |
| **Ranh giới từ** | Tương đối rõ | Không rõ ràng, cần segmentation |
| **Từ vay mượn** | — | Nhiều từ vay mượn từ tiếng Việt (loanwords) |

→ Sự tương đồng (cùng Austroasiatic, cùng quốc gia, nhiều loanwords) là lợi thế cho transfer learning; nhưng khác biệt hình thái học tạo ra thách thức đặc thù.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Tổng quan pipeline

Dựa trên abstract và đối chiếu với paper cùng nhóm nghiên cứu (BARTBahnar @ LM4UC 2025), phương pháp bao gồm:

#### Giai đoạn 1: Vietnamese-based Initialization
- Sử dụng **BARTPho** — mô hình BART pre-trained trên 145 triệu câu tiếng Việt.
- Lý do chọn BART (seq2seq): kiến trúc encoder-decoder phù hợp tự nhiên với MT (encoder hiểu source, decoder sinh target). BERT (encoder-only) không thể sinh text, GPT (decoder-only) thiếu encoder cho source language và cần quá nhiều dữ liệu.
- BARTPho cung cấp nền tảng ngôn ngữ Việt mạnh: ngữ pháp, cú pháp, phân bố từ vựng.

#### Giai đoạn 2: Continual Pre-training trên Bahnar
- Tiếp tục pre-train BARTPho trên **monolingual Bahnar data** với objective **denoising autoencoder** (masked language modeling + sentence permutation).
- Mục đích: model học được phân bố từ vựng, hành vi function words, và đặc trưng hình thái-cú pháp riêng của Bahnar.
- Thu hẹp khoảng cách phân bố giữa initialization tiếng Việt và dữ liệu Bahnar.

#### Giai đoạn 3: Fine-tuning cho Translation
- Fine-tune trên **bilingual Bahnaric-Vietnamese dataset**: encoder nhận câu Bahnar không bị corrupt, decoder sinh câu tiếng Việt.
- Áp dụng **data augmentation** ở giai đoạn này để tăng cường dữ liệu huấn luyện.

### 4.2 Hybrid Architecture (từ BARTBahnar paper)

Ngoài language model, hệ thống kết hợp nhiều thành phần:

1. **Loanword Detection**: Phát hiện từ vay mượn chung Bahnar-Việt (tên riêng, con số), giữ nguyên không dịch.
2. **Word Segmentation**: Dùng **PMI (Pointwise Mutual Information)** để tách cụm từ Bahnar (vì Bahnar không có ranh giới từ rõ ràng).
3. **Lexical Mapping**: Dùng từ điển song ngữ (indexed bằng Solr) để map trực tiếp các cụm từ đã biết.
4. **BARTBahnar Translation**: Xử lý các phần không map được bằng từ điển.
5. **Post-Processing**: Giải quyết ambiguity bằng scoring mechanism với pre-trained LM, chuẩn hóa dấu câu/viết hoa.

### 4.3 Data Augmentation

[Thông tin chi tiết từ paper cùng nhóm — BARTBahnar @ LM4UC 2025]

Các phương pháp DA được áp dụng (lightweight, không cần pretrained NMT hay morphological analyzer):

| Phương pháp | Mô tả | Bảo toàn nghĩa? |
|---|---|---|
| **Combining** | Ghép nối các câu cùng chủ đề | Bảo toàn chủ đề, không bảo toàn nghĩa câu |
| **Swapping** | Hoán vị thứ tự câu trong đoạn | Bảo toàn local, thay đổi discourse |
| **Synonym Replacement** | Thay thế từ bằng từ đồng nghĩa | Bảo toàn nghĩa tốt |
| **Theme Replacement** | Thay thế từ cùng nhóm chủ đề | Thay đổi nghĩa có kiểm soát |
| **Insertion** | Chèn đơn vị địa điểm/thời gian | Mở rộng ngữ cảnh |
| **Deletion** | Xóa lần lượt từng token | Buộc model suy luận từ thiếu |
| **Sliding Window** | Trích đoạn con chồng lấp | Bảo toàn local syntax |
| **Back-translation** | Dịch ngược từ Vietnamese Wikipedia | Tạo pseudo-parallel data |

### 4.4 Heuristic Methods

[Thông tin hạn chế - cần đọc full paper arXiv 2505.11421]

Abstract đề cập "heuristic methods to help the translation more precise" — có thể bao gồm các rule-based components trong hybrid architecture (loanword detection, lexical mapping, post-processing scoring).

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Dataset

Dựa trên paper BARTBahnar (LM4UC 2025) — cùng nhóm nghiên cứu, cùng bài toán:

| Thống kê | Chi tiết |
|---|---|
| **Original bilingual pairs** | 53,942 cặp câu |
| **Back-translation augmented** | 270,587 cặp câu |
| **Tổng cộng** | 324,529 cặp câu |
| **Train/Test split** | 90% / 10% |
| **Nguồn dữ liệu** | Field survey: sách tôn giáo, báo, bài hát, bản tin, tài liệu lịch sử từ cộng đồng Bahnar ở Tây Nguyên |
| **Domain** | Đa lĩnh vực: kinh tế, xã hội, chính trị, thể thao |

**Lưu ý**: Từ paper data augmentation (Nguyen et al., AAAI 2026), dataset Bahnar-Vietnamese có **51,930 cặp câu train / 2,001 test** (original, chưa augmented). Avg. length phía Bahnar: 46.36 tokens (train). Có sự khác biệt thống kê giữa các phiên bản paper.

### 5.2 Baselines (từ BARTBahnar paper)

| Model | BLEU | METEOR |
|---|---|---|
| Transformer (vanilla) | 0.26 | 0.0431 |
| PhoBERT-Fused NMT | 2.05 | 0.2648 |
| ViT5 | 7.18 | 0.2386 |
| BARTPho (không continual pre-training) | 5.73 | 0.2076 |
| **BARTBahnar** | **10.41** | **0.2822** |

### 5.3 Kết quả Data Augmentation

| DA Method | BLEU↑ | METEOR↑ |
|---|---|---|
| BARTBahnar (baseline) | 10.41 | 0.2822 |
| Insert + Swap | 7.56 | 0.1905 |
| Swap | 13.74 | 0.2758 |
| Insert + Original | 12.18 | 0.2921 |
| Sliding Window | 16.37 | 0.2640 |
| Combine | 16.63 | 0.3170 |
| Delete | 19.45 | 0.3323 |
| Replace (theme) | 20.19 | 0.3210 |
| **Replace (synonym)** | **21.68** | **0.3459** |

Kết quả bổ sung từ paper DA (AAAI 2026), thêm Deletion + Original:

| DA Method | BLEU↑ | METEOR↑ |
|---|---|---|
| **Deletion + Original** | **22.37** | **0.3581** |

### 5.4 Setup

- GPU: A100 40GB
- Optimizer: AdamW (lr=2e-5, β1=0.9, β2=0.999)
- Epochs: 15
- Batch size: 256, gradient accumulation: 2 steps
- Early stopping: patience 3 epochs dựa trên validation BLEU

---

## 6. Kết quả chính (Key Results)

### Transfer learning hiệu quả

- **BARTBahnar vượt trội tất cả baselines**: 10.41 BLEU so với 7.18 (ViT5), 5.73 (BARTPho không adapt), 0.26 (Transformer vanilla).
- Continual pre-training trên monolingual Bahnar là **bước quan trọng bắt buộc** — drop rõ rệt nếu bỏ qua (BARTPho → 5.73 vs BARTBahnar → 10.41).
- Kiến trúc encoder-decoder (BART) vượt trội so với encoder-only (PhoBERT) trong bài toán MT.

### Data augmentation có chọn lọc

- **Synonym Replacement** hiệu quả nhất trong các phương pháp đơn lẻ: tăng BLEU **~108%** (10.41 → 21.68).
- **Deletion + Original** đạt kết quả tốt nhất tổng thể: 22.37 BLEU — tăng **~115%** so với baseline.
- **Insert + Swap gây hại**: giảm từ 10.41 → 7.56 BLEU — quá nhiều nhiễu phá vỡ cấu trúc verb complex của Bahnar.

### Hybrid architecture

- Kết hợp rule-based (loanword detection, lexical mapping) với neural (BARTBahnar) cải thiện chất lượng dịch thực tế.
- Xử lý đặc thù Bahnar: từ vay mượn, word segmentation bằng PMI.

### Insight ngôn ngữ học

- Bahnar có **agglutinative morphology** → DA phải tôn trọng ranh giới hình thái, prefix/suffix, verb-class compatibility.
- Các phương pháp **meaning-preserving** (synonym replacement, deletion + original) luôn hiệu quả hơn các phương pháp **structure-altering** (insert + swap).
- Khối lượng dữ liệu augmented **không tỷ lệ thuận** với chất lượng: Sliding Window tạo >10M câu nhưng kém hơn Synonym Replacement (682K câu).

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Giải quyết bài toán thực sự quan trọng**: Bahnar là ngôn ngữ cực kỳ low-resource, gần như chưa có nghiên cứu NMT trước đó. Paper mở đường cho MT với ngôn ngữ dân tộc thiểu số Việt Nam.
2. **Pipeline 3 giai đoạn thiết kế hợp lý**: Vietnamese init → Bahnar continual pre-training → translation fine-tuning. Tận dụng tối đa sự tương đồng Austroasiatic giữa hai ngôn ngữ.
3. **Hybrid architecture thực tiễn**: Kết hợp neural + rule-based + statistical phù hợp với đặc thù ngôn ngữ (loanwords, thiếu word boundary).
4. **Lựa chọn kiến trúc có lý do rõ ràng**: Giải thích tại sao seq2seq (BART) phù hợp hơn encoder-only hay decoder-only cho MT low-resource.
5. **Data augmentation có phân tích typology-aware**: Không áp dụng mù quáng, mà phân tích DA nào phù hợp với đặc trưng ngôn ngữ Bahnar.
6. **Dữ liệu từ fieldwork thực tế**: Thu thập trực tiếp từ cộng đồng Bahnar ở Tây Nguyên, validated bởi native speakers.
7. **Open-source**: Code và materials được chia sẻ tại [github.com/ura-hcmut/BARTBahnar](https://github.com/ura-hcmut/BARTBahnar).

### Điểm yếu

1. **BLEU score vẫn thấp**: Ngay cả kết quả tốt nhất (22.37 BLEU) vẫn ở mức thấp cho ứng dụng thực tế. Với high-resource pairs, BLEU thường >30-40.
2. **Phụ thuộc vào "sibling" language**: Phương pháp đòi hỏi ngôn ngữ "anh em" có tài nguyên cao (tiếng Việt) — không áp dụng được cho ngôn ngữ thiểu số không có sibling tương đồng.
3. **Đánh giá chỉ dùng automatic metrics**: BLEU và METEOR không phản ánh đầy đủ chất lượng dịch thuật, đặc biệt với ngôn ngữ low-resource. Thiếu human evaluation.
4. **Chỉ một chiều dịch**: Bahnar → Vietnamese. Chưa thử nghiệm chiều ngược (Vietnamese → Bahnar) — quan trọng cho ứng dụng song phương.
5. **Từ điển song ngữ thủ công**: Hybrid system phụ thuộc vào bilingual dictionary — tốn nhân lực xây dựng, coverage hạn chế.
6. **Chưa so sánh với LLM hiện đại**: Không benchmark với GPT-4, mT5, NLLB-200 hay các multilingual models mạnh.
7. **Data augmentation chưa adapt cho morphology Bahnar**: Các phương pháp DA vẫn là surface-level, chưa có morphology-aware augmentation chuyên biệt cho agglutinative structure.
8. **Chưa phân tích error types**: Không có phân tích lỗi chi tiết (mistranslation categories, prefix/suffix errors, loanword handling failures).

---

## 8. Ý tưởng có thể áp dụng

### Cho bài toán MT Vietnamese - minority languages nói chung

1. **Pipeline 3 giai đoạn (init → adapt → fine-tune)**: Có thể áp dụng cho bất kỳ cặp ngôn ngữ thiểu số - Việt nào (Ê-đê, Gia-rai, Tày, Nùng, Khmer...). Bước continual pre-training trên monolingual data của minority language là critical.

2. **Chọn pre-trained model theo kiến trúc phù hợp**: Seq2seq (BART/BARTPho) vượt trội so với encoder-only hay decoder-only cho MT. Đây là insight quan trọng khi chọn backbone.

3. **Typology-aware data augmentation**: Không phải DA nào cũng có lợi — phải đánh giá dựa trên đặc trưng hình thái học của ngôn ngữ đích:
   - Ngôn ngữ **analytic** (Tày, Việt): Surface-level DA an toàn (swap, delete, synonym replace).
   - Ngôn ngữ **agglutinative** (Bahnar, Khmer): Cần DA tôn trọng morphological boundaries.
   - **Deletion + Original** là phương pháp robust nhất xuyên suốt các ngôn ngữ.

4. **Hybrid neural + rule-based**: Đối với ngôn ngữ có nhiều loanwords hoặc thiếu word boundary, kết hợp dictionary-based mapping, PMI segmentation với neural model cho kết quả thực tế hơn pure neural.

5. **Fieldwork-based data collection**: Mô hình thu thập dữ liệu từ cộng đồng (community-centered) — digitize sách tôn giáo, báo, bài hát, tài liệu lịch sử. Validated bởi native speakers.

6. **Back-translation với model có sẵn**: Dùng Vietnamese-Bahnar model (dù chất lượng thấp) để tạo pseudo-parallel data từ Vietnamese Wikipedia — tăng đáng kể data volume.

### Cho nghiên cứu của mình

- Pipeline BARTPho → continual pre-training → fine-tune có thể là **baseline mạnh** cho bất kỳ MT system nào với ngôn ngữ thiểu số Việt Nam.
- Kết quả DA cho thấy **meaning-preserving > structure-altering**: Ưu tiên synonym replacement và deletion + original khi augment bilingual data.
- Hybrid approach (rule-based + neural) đáng cân nhắc khi ngôn ngữ đích có đặc thù riêng (loanwords, morphology phức tạp).

---

## 9. Các paper liên quan quan trọng

### Cùng nhóm nghiên cứu (URA @ HCMUT)

| Paper | Venue | Đóng góp |
|---|---|---|
| **Nguyen et al.** "Serving the Underserved: Leveraging BARTBahnar Language Model for Bahnaric-Vietnamese Translation" | [LM4UC @ ACL 2025](https://aclanthology.org/2025.lm4uc-1.5/) | BARTBahnar + hybrid architecture, chi tiết hơn paper arXiv. Open-source. |
| **Nguyen et al.** "Not All Data Augmentation Works: A Typology-Aware Study for Low-Resource NMT in Vietnamese Ethnic Minority Languages" | AAAI 2026 | So sánh systematic DA cho Tày-Việt và Bahnar-Việt. Typology-aware analysis. Deletion + Original tốt nhất. |
| **Vo et al.** "Revitalizing Bahnaric Language through Neural Machine Translation: Challenges, Strategies, and Promising Outcomes" | AAAI 2024 | Nghiên cứu tiên phong NMT Bahnar-Việt, xây dựng dataset, Vietnamese-Bahnar model cho back-translation. |
| **Bui et al.** "Handling imbalanced resources and loanwords in Vietnamese-Bahnaric NMT" | IJIIDS 2024 | Xử lý mất cân bằng tài nguyên và loanwords trong NMT Bahnar-Việt. |

### Pre-trained models nền tảng

| Paper | Mô tả |
|---|---|
| **Tran et al.** "BARTpho: Pre-trained Sequence-to-Sequence Models for Vietnamese" (Interspeech 2022) | Mô hình seq2seq pre-trained trên 145M câu tiếng Việt — backbone của BARTBahnar. |
| **Lewis et al.** "BART: Denoising Sequence-to-Sequence Pre-training" (ACL 2020) | Kiến trúc BART gốc — denoising autoencoder với bidirectional encoder + autoregressive decoder. |
| **Phan et al.** "ViT5: Pretrained Text-to-Text Transformer for Vietnamese" (NAACL 2022 SRW) | Mô hình T5 cho tiếng Việt, một trong các baselines. |

### Low-resource NMT & Data Augmentation

| Paper | Mô tả |
|---|---|
| **Sennrich et al.** "Improving NMT Models with Monolingual Data" (ACL 2016) | Back-translation — phương pháp DA kinh điển cho NMT. |
| **Wei & Zou** "EDA: Easy Data Augmentation" (EMNLP 2019) | Các kỹ thuật DA đơn giản: synonym replacement, random swap/insert/delete. |
| **Ranathunga et al.** "Neural Machine Translation for Low-resource Languages: A Survey" (ACM Computing Surveys, 2023) | Survey toàn diện về NMT low-resource. |
| **Hujon et al.** "Transfer Learning Based NMT of English-Khasi on Low-Resource Settings" (2023) | Transfer learning cho ngôn ngữ low-resource khác (Khasi). |

### Đặc trưng ngôn ngữ

| Paper | Mô tả |
|---|---|
| **Alves, M. J.** "Morphology in Austroasiatic Languages" (2019) | Hình thái học ngôn ngữ Austroasiatic — bao gồm Bahnar. |
| **Alves, M. J.** "Linguistic Research on the Origins of the Vietnamese Language" (2006) | Nguồn gốc ngôn ngữ học tiếng Việt trong bối cảnh Austroasiatic. |

---

## Ghi chú

> **[Thông tin hạn chế]**: Bản tóm tắt này dựa chủ yếu trên abstract của arXiv 2505.11421 và đối chiếu chi tiết với paper BARTBahnar (LM4UC @ ACL 2025) cùng nhóm nghiên cứu. Full paper arXiv chưa có bản HTML/PDF công khai tại thời điểm phân tích. Các section về phương pháp, dataset, và kết quả được bổ sung từ paper ACL 2025 và paper DA (AAAI 2026) vì cùng nhóm tác giả, cùng bài toán, và cùng pipeline kỹ thuật. Cần đọc full paper arXiv 2505.11421 để xác nhận các khác biệt cụ thể (nếu có) so với phiên bản ACL.
