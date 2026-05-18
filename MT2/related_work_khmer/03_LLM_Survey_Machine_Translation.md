# Tóm tắt Paper: Bridging the Linguistic Divide — A Survey on Leveraging LLMs for Machine Translation

---

## 1. Thông tin paper

| Mục | Chi tiết |
|---|---|
| **Title** | Bridging the Linguistic Divide: A Survey on Leveraging Large Language Models for Machine Translation |
| **Authors** | Baban Gain, Dibyanayan Bandyopadhyay, Asif Ekbal, Trilok Nath Singh |
| **Venue** | arXiv preprint (survey paper) |
| **Year** | 2025 |
| **arXiv** | [2504.01919](https://arxiv.org/abs/2504.01919) |
| **Affiliations** | IIT Patna, India |
| **GitHub** | [babangain/llm-mt-survey](https://github.com/babangain/llm-mt-survey) |

---

## 2. Tóm tắt (Abstract)

Large Language Models (LLMs) đang thay đổi nhanh chóng lĩnh vực dịch máy (MT), đặc biệt qua khả năng **instruction-following**, **in-context learning**, và **preference-based alignment** — những thứ khác biệt căn bản so với mô hình encoder–decoder truyền thống.

Survey này cung cấp tổng quan toàn diện và cập nhật về cách LLM được tận dụng cho MT, bao gồm:
- Các phương pháp dựa trên **prompting**
- **Fine-tuning** toàn bộ và hiệu quả tham số (PEFT)
- **Synthetic data generation**
- **Preference-based optimization** (CPO, DPO, RLHF)
- **Reinforcement learning** với human feedback và weakly supervised feedback
- Mô hình **Mixture-of-Experts** (MoE)
- Dịch cấp **document-level** và **literary translation**
- **LLM-based evaluation** và các bias của nó

Kết luận chính: LLM-based MT là sự **tiến hóa** (không phải thay thế) của MT truyền thống, trong đó chất lượng dữ liệu, preference alignment, và context utilization quan trọng hơn quy mô mô hình.

---

## 3. Bài toán giải quyết (Problem Statement)

### Vấn đề cốt lõi

Mặc dù có nhiều survey về MT, **chưa có survey nào hệ thống hóa** các tiến bộ gần đây nhất mà LLM mang lại cho MT. Với sự đa dạng của kỹ thuật (prompting, fine-tuning, RLHF, MoE, agentic workflows...), việc định hướng trong lĩnh vực này là thách thức lớn cho cả người mới và practitioner.

### Tại sao quan trọng?

- MT đã chuyển từ rule-based → SMT → NMT → **LLM-based**, mỗi bước nhảy mang đến paradigm mới
- LLM cho phép **few-shot/zero-shot translation**, giảm phụ thuộc vào parallel corpora — đặc biệt quan trọng cho **low-resource languages**
- Tuy nhiên LLM cũng mang lại các vấn đề mới: **hallucination**, **bias**, **computational cost**, **robustness**
- Cần hệ thống hóa để hiểu rõ **khi nào LLM thực sự vượt trội** vs. khi nào encoder-decoder vẫn tốt hơn

---

## 4. Phương pháp đề xuất / Taxonomy (Proposed Method)

Đây là survey nên phần này trình bày **taxonomy phân loại các phương pháp** MT dùng LLM.

### 4.1. Synthetic Data Generation với LLMs (Section III)

#### Các kỹ thuật chính:
- **Back-translation**: Dùng LLM sinh text target, rồi back-translate để tạo parallel data
- **Forward translation**: Dịch xuôi source text rồi augment thêm
- **LexMatcher**: Giải quyết polysemous words bằng bilingual dictionaries + LLM augmentation
- **Large-scale forward translation**: Dịch Europarl data sang low-resource languages, rồi pivoting sang 147 cặp ngôn ngữ khác
- **Synthetic preference data**: Dùng LLM sinh multiple candidates, tự tạo preference pairs qua COMET scoring → fine-tune bằng DPO

#### Phát hiện quan trọng:
- Synthetic data **hiệu quả chủ yếu nhờ tăng parallel coverage**, KHÔNG phải nhờ reasoning signals
- CoT supervision **không cải thiện** chất lượng dịch — gains đến từ thêm translation attempts
- Hallucination trong synthetic data **nghiêm trọng hơn nhiều** ở low-resource directions
- **Diversity vs Quality trade-off**: Diverse data tốt hơn nhưng tăng diversity không kiểm soát → amplify noise
- Preference data nên được coi là **design variable**, không phải byproduct

### 4.2. Prompting-Based Techniques (Section IV.1–IV.2)

#### 4.2.1. Zero-Shot Prompting
- LLM dịch **không cần ví dụ mẫu**, chỉ dựa vào pre-trained knowledge
- ChatGPT **thua ~5 BLEU** so với Google MT, Tencent, DeepL
- **Pivot prompting**: Dịch qua English làm trung gian — cải thiện cho cặp ngôn ngữ xa nhau (De→Zh, Ro→Zh)
- GPT-4 **BLEU thấp hơn** Google MT nhưng **human evaluation tốt hơn** → mismatch giữa metric và chất lượng thực
- Thêm **domain info, keywords (~10), POS tags** vào prompt cải thiện COMET
- Prompt format tốt nhất: đơn giản, chỉ chỉ định source/target language

#### 4.2.2. In-Context Learning (ICL)
- Cung cấp **few-shot examples** trước khi dịch
- **Số lượng examples**: 5-shot thường là điểm cân bằng tốt nhất, gains giảm dần sau đó
- **Selection strategies**:
  - **CTQScorer**: Kết hợp BM25 + multiple linguistic features → +2.5 COMET over random
  - **Coherence-based**: Không chỉ similarity, mà còn semantic/stylistic consistency
  - **Submodular functions**: Tối ưu coverage + diversity, tránh redundancy
  - **Translation Memory (TM)**: Truy xuất similar sentence pairs từ TM database
  - **Fragment-Shot Prompting**: Chọn examples dựa trên syntactic coverage thay vì sentence-level similarity
- **Cross-lingual demonstrations**: Ví dụ từ ngôn ngữ khác đôi khi **tốt hơn** same-language examples cho low-resource
- **Example ordering**: Đặt examples tương tự nhất **gần input nhất** cho kết quả tốt hơn một chút
- **Cảnh báo**: Một example chất lượng kém có thể **phá hủy** toàn bộ chất lượng dịch

#### 4.2.3. Advanced Prompting / Chain-of-Thought
- **Naive CoT** (dịch từng từ) → **GIẢM chất lượng** dịch (COMET -8.8 cho EN→ZH) — CoT không phù hợp cho MT
- **Chain-of-Dictionary (COD)**: Chèn lexical chains qua auxiliary languages → hiệu quả cho low-resource
- **DecoMT**: Chunk-wise translation + contextual refinement → +8 chrF++ cho low-resource
- **Iterative Refinement**: Tự lặp lại refine → giảm BLEU nhưng human evaluation tốt hơn
- **MAPS**: Multi-Aspect Prompting (keywords + topic + examples → multiple candidates → selection)
- **TEaR**: Self-refinement qua Translate → Estimate (MQM-style) → Refine → giảm MQM errors
- **Multi-Agent Debate (MAD)**: Tranh luận giữa multiple LLM agents → vượt qua "Degeneration-of-Thought"
- **CompTra**: Decompose → translate phrases → recompose → mạnh cho low-resource và out-of-domain

#### 4.2.4. Agentic Methods
- **Self-refine workflow**: LLM tự critique rồi cải thiện — hiệu quả cho mid/low-resource
- **Multi-agentMT**: Translate → Postedit → Proofread — phụ thuộc mạnh vào chất lượng bản dịch ban đầu

### 4.3. Fine-Tuning Approaches (Section IV.3)

#### 4.3.1. Training Objectives

**Supervised Fine-Tuning (SFT):**
- Cross-entropy loss trên parallel corpora
- Cho phép multilingual generalization mạnh, kể cả với ít supervision
- **Nhược điểm**: Làm suy giảm emergent capabilities (formality control, few-shot adaptation, document-level contextualization)
- Fine-tuning trên 18K examples đã gây degradation

**Preference-Based & RL Objectives:**
- **CPO (Contrastive Preference Optimization)**: Phân biệt "adequate" vs "near-perfect" translations
- **RLHF**: Dùng human translations làm proxy cho preferred outputs → cross-lingual transfer
- **Token-level RL**: Gán reward ở mức từng token (dùng xCOMET error detection) → ổn định hơn sentence-level RL
- **MT-R1-Zero**: Mixed rule–metric reward + GRPO algorithm
- **SSR-Zero**: Self-rewarding RL — cùng LLM vừa làm actor vừa làm judge, chỉ cần 13K monolingual sentences
- **Plackett-Luce formulation**: Fine-grained graded preferences thay vì binary rankings

#### 4.3.2. Parameter Update Strategies

**Full-Parameter Fine-Tuning:**
- Cập nhật toàn bộ weights → performance mạnh nhất cho high-resource
- Ví dụ: ALMA (2-stage: monolingual → parallel SFT), Hunyuan-MT, SeamlessM4T
- **Đắt đỏ** về computational cost

**Parameter-Efficient Fine-Tuning (PEFT):**
- **LoRA**: Low-rank matrices vào frozen weights → match full fine-tuning với ~10% parameters
- **QLoRA**: LoRA + quantized weights → train <1% parameters, BLEU gains đáng kể
- **LSFTL**: Language-specific LoRA adapters → mô hình nhỏ (600M) match mô hình lớn hơn nhiều
- LoRA hiệu quả **phụ thuộc vào direction** (De→En tốt, En→De kém hơn full fine-tuning)

#### 4.3.3. Training Data Composition
- **ALMA 2-stage**: Monolingual SFT trước (strengthening multilingual) → Parallel SFT sau (alignment)
- **Mixed-data fine-tuning**: Kết hợp monolingual + parallel → bảo tồn capabilities + cải thiện MT
- Monolingual data đóng vai trò **regularizer**, giữ pre-existing capabilities

### 4.4. Mixture-of-Experts (MoE) cho MT

- **MoA (Mixture-of-Adapters)**: Lightweight adapters thay vì large FFN experts → ít parameters hơn nhiều
- **Lingual-SMoE**: Language-level routing trước, token-level routing sau → cải thiện low-resource balance
- **MoE-LLM**: Kết hợp shared LLM backbone + sparse experts → tốt cho low-resource và zero-shot

### 4.5. Specialized Domain Adaptation

- **DragFT**: Dictionary-enhanced prompting + RAG + PEFT cho domain terminology
- **E-commerce**: RAG framework cho product titles (chrF +15.3%), G2ST (2-stage fine-tuning + vocabulary expansion)
- **Finance**: LLM struggle với numerical fidelity, domain jargon → cần domain grounding
- **Clinical text**: Omission, residual technical terms, factual correctness errors → cần clinician oversight
- **Sentence-level terminology**: LLM đạt **>97% accuracy** khi có dictionaries
- **Document-level terminology**: Giảm xuống **70–80%** → open problem

### 4.6. Attribute-Controlled MT
- **Gender-controlled**: Few-shot examples hoặc GoE prompting cho gender-specific translations
- **Formality control**: INMTF framework dùng LLM làm reviser + reward model
- **PMMT**: Preference-aligned MT — diverse candidates → reward model selection

### 4.7. MT-Specific LLMs

| System | Đặc điểm nổi bật | Languages | Size |
|---|---|---|---|
| **ALMA / X-ALMA** | 2-stage (mono → parallel) + preference optimization | 50 | 7B, 13B |
| **Hunyuan-MT** | Pretraining + SFT + RL, Chimera ensemble | 33 | 1.8B, 7B |
| **Tower / Tower+** | Translation-centric instruction tuning | 15 | 2B–72B |
| **SeamlessM4T v2** | Multimodal (speech + text) | 200 | 1.2B, 2.3B |
| **GemmaX2** | Parallel-first pretraining + MT fine-tuning | 28 | 2B, 9B |
| **MT-R1-Zero** | RL-based, no human labels | — | 7B |
| **SSR-Zero** | Self-rewarding RL | — | 7B |
| **Qwen-MT** | Industrial MT, terminology control | 92 | — |

---

## 5. Dataset & Benchmarks

| Dataset/Benchmark | Mục đích | Chi tiết |
|---|---|---|
| **WMT14/22/23/24/25** | Standard MT evaluation | Multiple language pairs, shared tasks |
| **FLORES-200** | Multilingual evaluation | 200 ngôn ngữ, dùng nhiều cho low-resource |
| **MTOB** | Extreme low-resource | Grammar book + lexicon + minimal parallel data |
| **XC-Translate** | Cross-cultural entity translation | 10 cặp ngôn ngữ |
| **GENDEROUS** | Gender-ambiguous sentences | Dùng cho gender-controlled MT |
| **FinBENCH** | Financial MT | Multilingual, terminology-dense |
| **MQM-2020** | MT quality evaluation | Human MQM annotations |
| **LITRANSPROQA** | Literary translation evaluation | Reference-free, LLM-based, expert-designed |

### Metrics được đề cập:
- **BLEU**, **chrF/chrF++**: Surface-level lexical metrics
- **COMET**, **COMET-QE**, **COMETKiwi**: Neural learned metrics
- **xCOMET**: Extended COMET với error detection
- **BLEURT**, **BERTScore**, **MetricX**: Learned semantic metrics
- **MQM**: Multidimensional Quality Metrics (human annotation framework)
- **GEMBA**: LLM-as-judge prompting approach
- **GPTScore**: Likelihood-based evaluation

---

## 6. Kết quả chính (Key Findings)

### Về Prompting vs Fine-tuning
1. **Few-shot prompting** cho gains nhất quán nhưng nhỏ; **5-shot** thường là điểm saturating
2. **Fine-tuning** (cả full và LoRA) vượt trội rõ rệt so với prompting, đặc biệt hướng khó (En→De: +5 BLEU)
3. **LoRA hiệu quả phụ thuộc direction**: De→En tốt nhất, En→De kém hơn full fine-tuning
4. **Similarity-based example selection** KHÔNG nhất quán tốt hơn random selection

### Về LLM vs Encoder-Decoder
5. **High-resource**: LLM (GPT-4) **competitive** với Google Translate, DeepL
6. **Low-resource**: Encoder-decoder (M2M100 + kNN-MT) **vượt trội** LLM rõ rệt
7. **Extremely low-resource**: Parallel supervision vẫn là yếu tố quyết định, LLM prompting alone **underperforms**
8. **Direction asymmetry**: XX→En dễ hơn En→XX; Curse of Multilinguality chủ yếu ở post-training phase

### Về Synthetic Data
9. Hiệu quả đến từ **parallel coverage**, KHÔNG phải reasoning/CoT signals
10. Hallucination là vấn đề **nghiêm trọng** với low-resource synthetic data
11. Noisy synthetic data vẫn có thể **hiệu quả** khi clean data khan hiếm

### Về Evaluation
12. LLM-as-judge **tốt ở system-level**, nhưng **không ổn định ở segment-level**
13. GPT-4 human evaluation **tốt hơn BLEU scores** gợi ý — mismatch metric vs quality thực
14. **Multi-metric reporting** là bắt buộc; không nên dựa vào single metric

### Về Document-level & Literary
15. LLM cho DocMT scores cao nhưng **không nhất thiết exploit document context**
16. Gains từ context chỉ đáng kể khi **selective retrieval**, không phải uniform inclusion
17. Document-level terminology consistency (70–80%) **vẫn là open problem**
18. Literary translation cần **multi-stage pipelines** + human evaluation

### Về Fine-tuning Risks
19. SFT **làm suy giảm** formality control, few-shot adaptation, document-level capabilities
20. Fine-tuned LLM có xu hướng **"collapse"** thành NMT-like behavior — mất đi ưu thế LLM

---

## 7. Điểm mạnh & Điểm yếu (Strengths & Weaknesses)

### Điểm mạnh của Survey

| # | Điểm mạnh |
|---|---|
| 1 | **Coverage toàn diện**: Bao phủ từ prompting → fine-tuning → RLHF → MoE → document-level → evaluation → literary translation |
| 2 | **Scenario-based recommendation table** (Table 1): Hướng dẫn thực tế cho từng tình huống MT cụ thể |
| 3 | **Tự thực nghiệm**: Tái hiện prompting vs fine-tuning trên Qwen2.5-1.5B (Table 4) để verify claims |
| 4 | **Balanced viewpoint**: Không over-hype LLM, chỉ rõ khi nào encoder-decoder vẫn tốt hơn |
| 5 | **Phân tích preference-based training** rất chi tiết — đây là trend quan trọng nhất hiện nay |
| 6 | **Cảnh báo về fine-tuning risks**: Chỉ ra SFT có thể destroy emergent capabilities |
| 7 | **Liệt kê MT-specific LLMs** (Table 5) với comparison rõ ràng |
| 8 | **Evaluation critique**: Phân tích sâu biases của LLM-as-judge |

### Điểm yếu / Hạn chế

| # | Điểm yếu |
|---|---|
| 1 | **Thực nghiệm hạn chế**: Chỉ test trên Qwen2.5-1.5B, 1 cặp ngôn ngữ (De-En), WMT14 — không đại diện |
| 2 | **Thiếu low-resource experiments**: Survey nói nhiều về low-resource nhưng không tự verify |
| 3 | **Không có systematic comparison** giữa các methods trên cùng setup |
| 4 | **Chỉ cover text-to-text**: Bỏ qua multimodal, speech, dialogue translation |
| 5 | **Reference list không đầy đủ** trong bản survey (nhiều citation keys chưa resolve) |
| 6 | **Thiếu cost/efficiency analysis**: Không so sánh computational cost giữa methods |
| 7 | **Taxonomy có overlap**: Một số papers thuộc nhiều categories, ranh giới chưa rõ ràng |
| 8 | **Thiếu phân tích sâu về Asian/African languages**: Focus chủ yếu vào European languages |

---

## 8. Ý tưởng có thể áp dụng cho bài toán MT của mình

### 8.1. Prompting & In-Context Learning

| Ý tưởng | Áp dụng thế nào |
|---|---|
| **Chain-of-Dictionary (COD)** | Chèn lexical chains (Vietnamese ↔ English qua auxiliary languages) vào prompt → tăng chất lượng cho cultural terms |
| **Fragment-Shot Prompting** | Chọn ICL examples dựa trên syntactic coverage thay vì sentence similarity → phù hợp cho ngôn ngữ có cấu trúc khác biệt |
| **Translation Memory augmented prompting** | Tích hợp cultural KB của mình như TM vào prompt |
| **5-shot sweet spot** | Dùng 5 examples cho ICL, không cần nhiều hơn |
| **Coherence-based selection** | Chọn examples dựa trên coherence (semantic + stylistic), không chỉ similarity |

### 8.2. Fine-tuning Strategy

| Ý tưởng | Áp dụng thế nào |
|---|---|
| **ALMA 2-stage recipe** | Stage 1: Monolingual Vietnamese SFT → Stage 2: Small parallel SFT → tốt cho Vietnamese MT |
| **Mixed-data fine-tuning** | Trộn monolingual + parallel + cultural KB data để giữ general capabilities |
| **LoRA/QLoRA** | Fine-tune với <1% parameters, phù hợp với limited compute |
| **CPO/DPO với synthetic preferences** | Sinh multiple translations → COMET scoring → preference pairs → DPO training |

### 8.3. Synthetic Data

| Ý tưởng | Áp dụng thế nào |
|---|---|
| **Quality-filtered synthetic data** | Sinh parallel data cho cultural entities, filter bằng COMET |
| **Diversity-aware generation** | Đảm bảo lexical + structural diversity trong synthetic data |
| **Preference pair construction** | Tự tạo preference data từ cultural KB: correct cultural translation vs literal translation |

### 8.4. Document-level & Cultural Context

| Ý tưởng | Áp dụng thế nào |
|---|---|
| **Selective context retrieval** (self-retrieval) | Chỉ retrieve relevant cultural context, không dump toàn bộ KB |
| **DelTA (incremental state tracking)** | Maintain document-level state cho consistent entity translation |
| **Multi-agent workflow** | Translator + Cultural Specialist + Proofreader cho cultural MT |
| **Terminology tables** (từ WMT literary) | Xây terminology table cho cultural entities, enforce consistency |

### 8.5. Evaluation

| Ý tưởng | Áp dụng thế nào |
|---|---|
| **Multi-metric reporting** | Dùng BLEU + COMET + chrF + human eval, không chỉ 1 metric |
| **LLM-as-judge + learned metrics** | Kết hợp cả hai cho robust evaluation |
| **Error Analysis Prompting** | MQM-style error annotation để phân tích chất lượng dịch cultural terms |

---

## 9. Các paper liên quan quan trọng (đáng đọc thêm)

### Prompting & ICL cho MT
- **Jiao et al. (2023)** — "Is ChatGPT a Good Translator?" — Benchmark đầu tiên so sánh ChatGPT/GPT-4 với commercial MT
- **Vilar et al. (2023)** — Nghiên cứu chi tiết về prompting strategies cho MT với GPT-3
- **Lu et al. (2024)** — Chain-of-Dictionary Prompting → quan trọng cho low-resource
- **Mu et al. (2023)** — Translation Memory augmented prompting
- **Frontull (2025)** — Fragment-Shot Prompting: syntactic coverage-based ICL

### Fine-tuning & Preference Optimization
- **Xu et al. (2024) [ALMA]** — ALMA/ALMA-R: 2-stage SFT recipe → **rất quan trọng, blueprint cho MT fine-tuning**
- **Gisserot-Boukhlef et al. (2024)** — CPO cho MT: contrastive preference without reference policy
- **Ramos et al. (2025)** — Token-level RL với xCOMET error detection
- **Feng et al. (2025) [MT-R1-Zero]** — Rule-metric RL không cần human labels
- **Stap et al. (2024)** — Cảnh báo về fine-tuning degradation of LLM capabilities

### Synthetic Data & Low-Resource
- **de Gibert et al. (2025)** — Large-scale synthetic data cho 147 language pairs
- **Vajda et al. (2025)** — LLM-generated preference data cho DPO
- **Dang (2024)** — RLHF cho low-resource languages
- **Song (2025)** — "LLM is not a silver bullet for low-resource" — bottleneck analysis

### Document-Level & Literary
- **Wang et al. (2023)** — Document-level MT with GPT-3.5/4
- **Peng et al. (2025)** — Self-retrieval framework cho DocMT
- **Wang (2025) [DelTA]** — Incremental document state tracking
- **Wu et al. (2024)** — Adapting LLMs for DocMT → autoregressive error propagation issue
- **TRANSAGENTS (2025)** — Multi-agent literary translation company simulation

### Evaluation
- **Kocmi & Federmann (2023) [GEMBA]** — LLM-as-judge cho MT evaluation
- **Fernandes et al. (2023) [AutoMQM]** — MQM-style error annotation with LLMs
- **Feng et al. (2025) [M-MAD]** — Multi-agent debate evaluation
- **Zhang et al. (2025) [LITRANSPROQA]** — Reference-free literary translation evaluation

### MT-Specific Systems
- **TOWER/TOWER+** — Translation-centric instruction tuning (2B–72B)
- **Hunyuan-MT** — Industrial MT system (pretraining + SFT + RL)
- **SeamlessM4T v2** — 200 languages, multimodal
- **GemmaX2** — Open competitive with proprietary MT

### Architectural / Efficiency
- **Luo et al. (2025) [LaMaTE]** — LLM encoder + NMT decoder: 6.5× faster, 75% less memory
- **Zheng et al. (2025)** — Direction-Aware Training (DAT) cho Curse of Multilinguality
- **Zhao (2024) [Lingual-SMoE]** — Language-aware MoE routing

---

## Appendix: Scenario-based Recommendations (Table 1 của paper)

| Tình huống | Approach tốt nhất | Lý do | Hạn chế |
|---|---|---|---|
| High-resource pairs | Prompting hoặc light LoRA | Pre-training đủ mạnh | Over-fine-tuning giảm generalization |
| Mid-resource | LoRA/QLoRA + mixed data | Cân bằng efficiency & specialization | Direction-dependent |
| Low-resource (related languages) | Few-shot ICL + synthetic data | Cross-lingual transfer | Hallucination risk |
| Extremely low-resource | Encoder–decoder + parallel supervision | Parallel signal > prompting | LLM prompting underperforms |
| Domain adaptation (no retraining) | Dictionary/RAG-based prompting | Terminology grounding at inference | Weak document consistency |
| High-stakes (medical, finance) | PEFT/full SFT + terminology constraints | Parameter-level grounding | Cần curated data |
| Literary translation | Long-context prompting + refinement | Captures style, discourse | Auto metrics underrepresent gains |
| User preference alignment | CPO, RLHF | Align with subjective preferences | Preference data scarce for low-resource |
| Scalable deployment | Hybrid LLM encoder + NMT decoder | Flexibility + efficiency | Increased system complexity |
| Auto evaluation (system-level) | LLM-as-judge | High correlation after aggregation | Segment-level instability |
| Auto evaluation (segment-level) | Learned metrics (COMET, xCOMET) | Stable fine-grained scoring | Less interpretable |
