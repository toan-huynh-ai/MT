# Tóm tắt Paper: Self-supervised RL for Low-Resource Machine Translation via Round-Trip Bootstrapping

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Improving Low-Resource Machine Translation via Round-Trip Reinforcement Learning |
| **Authors** | Ahmed Attia, Alham Fikri (MBZUAI) |
| **Venue** | arXiv Preprint |
| **Year** | 2025 |
| **arXiv** | [2601.12535](https://arxiv.org/abs/2601.12535) |
| **Code** | [GitHub](https://github.com/Copticoder/MT-via-Round-Trip-RL) |
| **Affiliations** | Mohamed bin Zayed University of Artificial Intelligence (MBZUAI), Masdar City, UAE |

---

## 2. Tóm tắt (Abstract)

Paper đề xuất một phương pháp **self-supervised reinforcement learning** để cải thiện dịch máy low-resource mà **không cần thêm dữ liệu song song** (parallel data). Ý tưởng cốt lõi:

1. Dịch câu tiếng Anh → ngôn ngữ đích (low-resource).
2. Dịch ngược kết quả → tiếng Anh (round-trip / back-translation).
3. So sánh câu tiếng Anh tái tạo với câu gốc bằng metric **chrF++** và **BLEU** → dùng làm **reward signal** cho RL.

Thuật toán RL được sử dụng là **GRPO** (Group Relative Policy Optimization), áp dụng lên mô hình **NLLB** (No Language Left Behind) với 2 kích thước: 600M và 1.3B parameters.

Kết quả: Cải thiện **nhất quán** trên 6 ngôn ngữ — Central Aymara, Friulian, Wolof, Dyula, Bhojpuri và Russian — cả về chất lượng dịch (chrF++) lẫn fluency (đo bằng Goldfish LM).

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Dịch máy low-resource vẫn là thách thức lớn nhất của NLP. Các hệ thống MT hiện đại đạt hiệu suất cao cho ngôn ngữ giàu tài nguyên (tiếng Anh, tiếng Pháp...) nhưng **thất bại** trên hàng nghìn ngôn ngữ thiếu dữ liệu song song.

### Hạn chế của phương pháp hiện tại

| Phương pháp | Hạn chế |
|---|---|
| **MLE (Maximum Likelihood Estimation)** | Bị **exposure bias** — train trên ground-truth nhưng inference trên output của chính mô hình → lỗi tích lũy. Không trực tiếp tối ưu evaluation metric (chrF++, BLEU). |
| **Back-translation** | Phụ thuộc chất lượng mô hình dịch ngược. Lỗi ở bản dịch ngược sớm sẽ **lan truyền** qua dữ liệu tổng hợp. Vẫn dùng MLE, không tối ưu trực tiếp metric. |
| **Unsupervised MT (UMT)** | Hàm mục tiêu phức tạp (auto-encoding + cross-domain + adversarial loss) → kết quả **không ổn định** giữa các ngôn ngữ. |

### Tại sao quan trọng?

- Hàng nghìn ngôn ngữ trên thế giới thiếu dữ liệu song song, khiến người nói các ngôn ngữ này bị **cô lập khỏi thông tin số** và công nghệ đa ngôn ngữ.
- Các mô hình multilingual lớn (NLLB) đã cover 200+ ngôn ngữ nhưng vẫn cần cơ chế **thích ứng** (adaptation) hiệu quả cho các hướng dịch low-resource.
- RL cho phép tối ưu trực tiếp metric đánh giá dịch thuật (non-differentiable) — giải quyết vấn đề mismatch giữa training objective và evaluation metric.

---

## 4. Phương pháp đề xuất (Proposed Method)

### 4.1 Tổng quan Pipeline

```
English source → [NLLB Forward] → Target language → [NLLB Backward] → Reconstructed English
                                                                              ↓
                                                              So sánh với English source
                                                              → Tính reward (chrF++ + BLEU)
                                                              → Cập nhật policy bằng GRPO
```

Pipeline gồm 3 bước chính:

1. **Forward Translation**: Dịch câu tiếng Anh → ngôn ngữ đích (low-resource).
2. **Backward Translation (Round-Trip)**: Dịch kết quả ngược lại → tiếng Anh.
3. **Reward Computation & Policy Update**: So sánh câu tiếng Anh tái tạo với câu gốc bằng metric tự động, dùng reward này để cập nhật mô hình bằng GRPO.

### 4.2 Thuật toán GRPO (Group Relative Policy Optimization)

GRPO là biến thể của PPO (Proximal Policy Optimization) — được đề xuất bởi Shao et al. (2024) trong DeepSeekMath:

- **Loại bỏ value critic**: Không cần train riêng một mô hình ước lượng value function → giảm tài nguyên.
- **Normalize reward theo nhóm**: Với mỗi input, sample G candidate outputs → tính advantage bằng cách normalize reward trong nhóm.
- **Clipping**: Giới hạn mức thay đổi policy (giống PPO) để tránh update quá lớn.
- **KL penalty**: Thêm regularization $\beta \cdot D_{KL}[\pi_\theta \| \pi_{ref}]$ để policy mới không đi quá xa so với policy gốc.

**Quy trình cụ thể:**

1. Với mỗi câu input $q$, sample $G$ bản dịch candidate $\{o_1, ..., o_G\}$ từ policy hiện tại.
2. Tính reward cho từng candidate dựa trên round-trip reconstruction quality.
3. Normalize reward trong nhóm $G$ → tính advantage $\hat{A}_{i,t}$.
4. Cập nhật policy bằng clipped objective + KL penalty.

### 4.3 Reward Function

Paper thử nghiệm 4 loại reward:

| Reward | Mô tả | Hiệu quả |
|---|---|---|
| **chrF++** | Character n-gram F-score, mượt hơn BLEU ở mức ký tự | **Tốt nhất** — ổn định, phù hợp ngôn ngữ có hình thái học phức tạp |
| **BLEU** | Word-level n-gram precision | Cải thiện nhưng yếu hơn chrF++ đáng kể |
| **chrF++ + BLEU** | Kết hợp cả hai (trọng số bằng nhau) | Cạnh tranh, đôi khi tốt hơn, nhưng không nhất quán vượt chrF++ đơn lẻ |
| **BLEURT** | Learned metric (neural) | **Thất bại** — mô hình nhanh chóng exploit metric → reward cao nhưng chất lượng thật sụp đổ (reward hacking) |

**Insight quan trọng**: Learned metric (BLEURT) bị reward over-optimization. Mô hình học cách "đánh lừa" metric neural thay vì cải thiện chất lượng dịch thật → chrF++ (rule-based) là reward ổn định và đáng tin cậy hơn.

### 4.4 Điểm khác biệt so với Back-Translation truyền thống

| Tiêu chí | Back-Translation (BT) | Round-Trip RL (đề xuất) |
|---|---|---|
| **Yêu cầu dữ liệu** | Cần mô hình dịch ngược (tgt→en) hoặc parallel signal | Chỉ cần **corpus đơn ngữ tiếng Anh** |
| **Training objective** | MLE trên synthetic parallel data | Trực tiếp tối ưu metric dịch thuật qua RL |
| **Exposure bias** | Vẫn bị | Giảm thiểu — train trên output của chính model |
| **Lỗi lan truyền** | Có — lỗi ở bản dịch ngược truyền vào synthetic data | Giảm thiểu — reward tính trên round-trip, không dùng synthetic data cố định |

---

## 5. Dataset & Thí nghiệm (Experiments)

### 5.1 Dataset

| Dataset | Mô tả |
|---|---|
| **NLLB-MD** | Dataset đánh giá chính thức từ dự án NLLB (No Language Left Behind). Được dùng cho cả training và out-of-distribution evaluation. |
| **Training data** | Corpus đơn ngữ tiếng Anh (English monolingual). Không cần dữ liệu song song thêm. |

### 5.2 Ngôn ngữ thử nghiệm

| Ngôn ngữ | Mã | Đặc điểm | Mức tài nguyên |
|---|---|---|---|
| Central Aymara | aym | Ngôn ngữ thổ dân Nam Mỹ, agglutinative | Rất thấp |
| Friulian | fur | Ngôn ngữ Romance (Ý), ít người nói | Rất thấp |
| Wolof | wol | Ngôn ngữ Tây Phi (Senegal) | Rất thấp |
| Dyula | dyu | Ngôn ngữ Tây Phi (Burkina Faso, Côte d'Ivoire) | Rất thấp |
| Bhojpuri | bho | Ngôn ngữ Indo-Aryan (Ấn Độ), hình thái học phức tạp | Thấp |
| Russian | rus | Ngôn ngữ Slavic, high-resource — dùng làm control | Cao |

### 5.3 Mô hình

- **NLLB-600M** (distilled): 600 triệu parameters
- **NLLB-1.3B** (distilled): 1.3 tỷ parameters
- Framework: PyTorch, HuggingFace Transformers
- Optimizer: Adam
- Số bước tối ưu: **8K optimization steps**

### 5.4 Baselines

| Baseline | Mô tả |
|---|---|
| **Vanilla NLLB** | Mô hình NLLB gốc, không fine-tune |
| **RT (Round-Trip)** | Round-trip translation không có RL (chỉ dịch vòng, không cập nhật) |
| **BT (Back-Translation)** | Back-translation truyền thống — cần mô hình dịch ngược tgt→en |
| **UMT (Unsupervised MT)** | Dịch máy không giám sát (auto-encoding + cross-domain + adversarial) |

### 5.5 Metrics

| Metric | Vai trò |
|---|---|
| **chrF++** | Metric chính để đánh giá forward translation (en→tgt). Cũng là reward signal. |
| **BLEU** | Đánh giá backward translation (tgt→en). |
| **BERTScore** | Đánh giá semantic similarity của back-translation. |
| **COMET** | Chỉ dùng cho Russian (có mô hình đáng tin cậy). |
| **Goldfish LM log-probability** | Đánh giá **fluency** của output ngôn ngữ đích. |

---

## 6. Kết quả chính (Key Results)

### 6.1 Bảng kết quả chrF++ (Forward Translation: English → Target)

**Với mô hình 600M:**

| Ngôn ngữ | Vanilla | RT | BT | UMT | **RL (đề xuất)** |
|---|---|---|---|---|---|
| Central Aymara | ~25 | — | 27.34 | — | **28.13** (+0.79 so với BT) |
| Wolof | ~21 | — | 23.57 | — | **23.96** (+0.39 so với BT) |
| Dyula | ~18 | — | 20.13 | — | **22.50** (+2.37 so với BT) |
| **Trung bình (6 ngôn ngữ)** | — | — | 36.18 | — | **36.49** (+0.31 so với BT) |

**Với mô hình 1.3B:**

| Ngôn ngữ | Vanilla | BT | UMT | **RL (đề xuất)** |
|---|---|---|---|---|
| Central Aymara | ~27 | — | — | **28.73** (tốt nhất) |
| Dyula | ~20 | — | — | **22.97** (tốt nhất) |
| Wolof | ~24 | — | **27.72** (UMT) | 26.66 (cạnh tranh) |
| **Trung bình (6 ngôn ngữ)** | — | **38.38** | — | 38.18 (chênh 0.20) |

**Nhận xét quan trọng:**
- Phương pháp RL hiệu quả **đặc biệt** với các ngôn ngữ **rất low-resource** (Aymara, Dyula, Wolof).
- Với ngôn ngữ có tài nguyên cao hơn (Russian, Friulian, Bhojpuri), BT thường mạnh hơn nhưng **khoảng cách rất nhỏ**.
- RL **luôn vượt** baseline Round-Trip (RT) đơn giản trên mọi ngôn ngữ và model size.

### 6.2 Fluency — Goldfish LM Log-Probability

| Ngôn ngữ | Trước training | Sau training | Δ |
|---|---|---|---|
| Central Aymara | -20.03 | -19.87 | +0.16 |
| Friulian | -19.23 | -19.09 | +0.14 |
| Russian | -15.64 | -15.37 | **+0.27** |
| Wolof | -18.26 | -18.07 | +0.19 |
| Bhojpuri | -14.93 | -14.97 | -0.04 (giảm nhẹ) |
| Dyula | -17.53 | -16.43 | **+1.09** (cải thiện lớn nhất) |

→ 5/6 ngôn ngữ có fluency tăng sau training. Bhojpuri giảm nhẹ, có thể do hình thái học phức tạp.

### 6.3 Back-Translation BERTScore (Target → English)

| Ngôn ngữ | F1 trước | F1 sau | Δ F1 |
|---|---|---|---|
| Central Aymara | 0.48 | 0.55 | +0.07 |
| Friulian | 0.75 | 0.77 | +0.02 |
| Russian | 0.73 | 0.79 | +0.06 |
| Wolof | 0.51 | 0.55 | +0.04 |
| Dyula | 0.40 | 0.56 | **+0.16** |
| Bhojpuri | 0.79 | 0.77 | -0.02 |

→ Dyula có cải thiện BERTScore lớn nhất (+0.16), cho thấy cải thiện đáng kể cả precision và recall.

### 6.4 Reward Function Ablation

| Reward | Trung bình chrF++ gain |
|---|---|
| BLEU only | +1.60 |
| BLEU + chrF++ | +2.41 |
| **chrF++ only** | **+2.47** (tốt nhất) |
| BLEURT | ❌ Collapse — reward hacking |

**Insight**: chrF++ (character-level) cho learning signal **mượt hơn** BLEU (word-level) trong setting low-resource với sparse n-gram matching. BLEURT (learned metric) bị exploit → mô hình tạo output "đánh lừa" scorer nhưng chất lượng thật sụp đổ.

### 6.5 COMET Score (chỉ Russian)

- Trước training: **0.84**
- Sau training: **0.86** (+0.02)

### 6.6 Ví dụ định tính (Qualitative)

| Ngôn ngữ | chrF++ Vanilla | chrF++ Trained | Nhận xét |
|---|---|---|---|
| Central Aymara | 35.32 | **64.09** | Cải thiện gần gấp đôi |
| Friulian | 16.61 | **70.46** | Cải thiện cực lớn, gần sát reference |
| Wolof | 5.84 | **42.22** | Từ gần như vô nghĩa (repetition) → có ý nghĩa |
| Russian | 21.32 | **74.52** | Bắt được ý chính, tăng coverage đáng kể |

**Đặc biệt với Wolof**: Vanilla model sinh ra repetition vô nghĩa ("bësum-bësum-bësum..."), trained model đã sửa lỗi này hoàn toàn.

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh

1. **Không cần dữ liệu song song thêm**: Chỉ cần corpus đơn ngữ tiếng Anh → phù hợp thực tế cho ngôn ngữ cực kỳ thiếu tài nguyên. Giả định yếu hơn BT (không cần mô hình dịch ngược riêng).

2. **Giải quyết exposure bias và objective mismatch**: RL tối ưu trực tiếp metric dịch thuật thay vì MLE, giảm tích lũy lỗi khi inference.

3. **Kết quả ổn định và nhất quán**: Validation curves mượt, gần monotonic, không oscillation lớn → quá trình tối ưu ổn định. Cải thiện trên **tất cả** ngôn ngữ và cả hai model sizes.

4. **Phân tích reward function kỹ lưỡng**: Ablation study cho thấy rõ chrF++ vượt trội, cảnh báo về reward hacking với learned metric (BLEURT) — insight có giá trị thực tiễn cao.

5. **Scalability evidence**: Mô hình 1.3B luôn tốt hơn 600M, gap duy trì ổn định → gợi ý phương pháp **scale tốt** với model lớn hơn.

6. **Đánh giá đa chiều**: Không chỉ chrF++ mà còn BLEU, BERTScore, COMET, Goldfish LM — đảm bảo cải thiện không phải artifact của metric training.

### Điểm yếu

1. **Chỉ test 6 ngôn ngữ**: Tuy cover nhiều họ ngôn ngữ (Aymara, Romance, Niger-Congo, Indo-Aryan, Slavic) nhưng vẫn chưa đủ để kết luận tổng quát. Thiếu ngôn ngữ tonal (Việt, Thái), logographic (Trung Quốc), polysynthetic.

2. **Chỉ test NLLB distilled (600M, 1.3B)**: Chưa thử trên mô hình full-size 3.3B. Chưa rõ liệu phương pháp có hiệu quả tương tự trên các LLM mới hơn (LLaMA, Gemma) hay decoder-only architectures.

3. **Bhojpuri không cải thiện fluency**: Gợi ý phương pháp có thể **kém hiệu quả** với ngôn ngữ có hình thái học rất phức tạp hoặc bilingual alignment yếu.

4. **Chỉ dịch từ tiếng Anh (English-centric)**: Pipeline luôn bắt đầu từ English → target. Chưa test cho non-English source languages hoặc dịch giữa hai ngôn ngữ low-resource.

5. **Reward chỉ đo trên English reconstruction**: Round-trip reward không trực tiếp đo chất lượng bản dịch forward. Có thể xảy ra trường hợp round-trip tốt nhưng bản dịch trung gian (forward) không chính xác — dù paper đã dùng Goldfish LM để kiểm chứng fluency.

6. **Thiếu human evaluation**: Chỉ có qualitative examples, không có systematic human evaluation (MQM, post-editing effort, adequacy/fluency rating). Đây là hạn chế phổ biến trong MT low-resource do thiếu annotator.

7. **Không so sánh với MT-R1-Zero**: Paper nhắc đến Feng et al. (2025) — MT-R1-Zero áp dụng RL cho LLM translation nhưng không đưa vào baseline so sánh trực tiếp.

8. **Training chỉ 8K steps**: Validation curves cho thấy chưa plateau → chưa biết optimal training length. Có thể overfitting nếu train quá lâu mà không có early stopping rõ ràng.

---

## 8. Ý tưởng có thể áp dụng

### 8.1 Áp dụng trực tiếp cho bài toán MT low-resource

- **Round-trip RL framework**: Có thể áp dụng cho bất kỳ cặp ngôn ngữ low-resource nào mà đã có mô hình multilingual (NLLB, M2M-100, hoặc LLM multilingual). Chỉ cần corpus đơn ngữ tiếng Anh — chi phí rất thấp.

- **chrF++ là reward ổn định**: Khi thiết kế reward function cho RL trong MT, **ưu tiên chrF++ hơn BLEU** (đặc biệt cho ngôn ngữ morphologically rich). **Tránh learned metric** (BLEURT, COMET) làm reward — dễ bị reward hacking.

### 8.2 Mở rộng và kết hợp

- **Kết hợp với knowledge-augmented MT**: Round-trip RL có thể kết hợp với RAG-based approach (như KG-MT) — dùng knowledge graph để cải thiện entity translation, đồng thời dùng RL để cải thiện fluency tổng thể.

- **Kết hợp với cultural knowledge base**: Trong bài toán dịch có yếu tố văn hóa, round-trip RL có thể là bước fine-tuning thứ hai sau khi đã inject cultural knowledge.

- **Multi-reward RL**: Thiết kế reward function kết hợp round-trip consistency + domain-specific signal (cultural accuracy, entity preservation).

### 8.3 Bài học thiết kế hệ thống

- **GRPO thay vì PPO**: Không cần value critic → giảm bộ nhớ và complexity. Phù hợp cho fine-tuning MT models trên hardware hạn chế.
- **Rule-based reward > Learned reward**: Insight quan trọng — trong RL cho NLP, learned metrics dễ bị exploit hơn rule-based metrics.
- **Monitoring fluency riêng biệt**: Dùng monolingual LM (Goldfish) để kiểm tra fluency là practice tốt — đảm bảo RL không tạo output "đánh lừa" reward nhưng vô nghĩa.

### 8.4 Hạn chế cần lưu ý khi áp dụng

- Round-trip reward có thể bias hướng **paraphrastic solutions** — bản dịch đúng nghĩa nhưng quá khác reference style.
- Cần cẩn thận với **error amplification** — RL tối ưu trên output của chính model → systematic errors có thể bị reinforce.
- English-centric limitation — nếu bài toán cần dịch giữa hai ngôn ngữ low-resource, cần thiết kế lại pipeline (pivot qua English hoặc dùng multilingual round-trip).

---

## 9. Các paper liên quan quan trọng

### RL cho Machine Translation

| Paper | Tóm tắt | Relevance |
|---|---|---|
| **Feng et al. (2025)** — MT-R1-Zero | RL không cần supervised warm-start cho LLM translation, dùng GRPO với rule-based reward. | Cùng hướng tiếp cận RL + GRPO cho MT, nhưng trên LLM thay vì NLLB. |
| **Ranzato et al. (2016)** — MIXER | Policy gradient methods cho sequence-level training, giảm exposure bias. | Nền tảng lý thuyết RL cho NMT. |
| **Wu et al. (2018)** — RL study for NMT | Nghiên cứu hệ thống về RL cho NMT, kết hợp RL + MLE. | Cung cấp insights về khi nào RL hiệu quả cho NMT. |
| **Shao et al. (2024)** — DeepSeekMath (GRPO) | Đề xuất GRPO — loại bỏ value critic từ PPO, normalize reward theo nhóm. | Thuật toán RL cốt lõi được sử dụng trong paper. |

### Low-Resource MT & Monolingual Data

| Paper | Tóm tắt | Relevance |
|---|---|---|
| **Sennrich et al. (2016)** — Back-translation | Kỹ thuật nền tảng — dùng dữ liệu đơn ngữ qua back-translation để cải thiện NMT. | Baseline chính trong paper. |
| **NLLB Team et al. (2022)** — No Language Left Behind | Mô hình multilingual MT cover 200+ ngôn ngữ, foundation cho paper. | Mô hình nền tảng được fine-tune. |
| **Lample et al. (2018)** — Unsupervised MT | Dịch máy không giám sát kết hợp denoising autoencoding + back-translation + cycle consistency. | Baseline UMT trong paper. |
| **Haddow et al. (2022)** — Survey Low-Resource MT | Survey toàn diện về các phương pháp MT low-resource. | Tổng quan lĩnh vực. |

### Evaluation & Metrics

| Paper | Tóm tắt | Relevance |
|---|---|---|
| **Chang et al. (2024)** — Goldfish LM | Monolingual language models cho 350 ngôn ngữ, dùng đánh giá fluency. | Metric đánh giá fluency trong paper. |
| **Rei et al. (2020)** — COMET | Neural framework cho MT evaluation, dùng cho Russian. | Metric bổ sung. |
| **Sellam et al. (2020)** — BLEURT | Learned metric cho text generation — bị reward hacking khi dùng làm training signal. | Bài học tiêu cực về learned reward. |
| **Popović (2015)** — chrF | Character n-gram F-score, hiệu quả cho ngôn ngữ morphologically rich. | Reward function chính và metric đánh giá. |

### Liên quan đến bài toán của mình

| Paper | Lý do nên đọc |
|---|---|
| **Ruiter et al. (2019)** — Self-supervised NMT | Mining parallel sentences từ comparable corpora bằng cross-lingual similarity signals — có thể kết hợp với round-trip RL. |
| **McNamee & Duh (2023)** — Back-translation in 60 languages | Khảo sát rộng về BT cho nhiều ngôn ngữ — benchmark và insights cho so sánh. |
| **Fernandes et al. (2023)** — Scaling laws for multilingual NMT | Scaling laws cho MT multilingual — dự đoán hiệu quả khi scale model. |

---

## 10. Tóm tắt một dòng

> **Round-trip RL (GRPO) + chrF++ reward** trên NLLB models cải thiện nhất quán MT low-resource mà **không cần thêm parallel data** — đặc biệt hiệu quả cho ngôn ngữ cực kỳ thiếu tài nguyên (Aymara, Dyula, Wolof), với insight quan trọng rằng rule-based reward (chrF++) ổn định hơn learned metric (BLEURT) trong RL cho NMT.
