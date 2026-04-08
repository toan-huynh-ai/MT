# Research Directions: Machine Translation for Vietnamese-Khmer Cultural Conversations

## 1. Data Overview

| Property | Details |
|---|---|
| **Language Pair** | Vietnamese ↔ Khmer (ភាសាខ្មែរ) |
| **Scale** | ~1,856 samples (`all_1.jsonl`: 981, `all_2.jsonl`: 875) |
| **Data Format** | (1) Q&A about food culture, (2) Structured ethnographic interviews (interviewer/interviewee) |
| **Topics** | Cuisine, clan/family, childbirth customs, beliefs, agriculture, festivals... |
| **Special Features** | Multi-reference translations, word-level alignment annotations (`***`), correction notes |
| **Nature** | Low-resource pair, domain-specific (ethnographic/cultural), conversational |

### Data Schema

```json
{
  "id": 71645,
  "text": "Vietnamese source text",
  "question": "Optional Vietnamese question",
  "label": ["Khmer translation 1", "Khmer translation 2 with annotations"],
  "Comments": [],
  "topic": "Topic name (e.g., Traditions during pregnancy)",
  "order": 1.0
}
```

### Key Annotation Types Found in Data

- **Multi-reference**: Multiple Khmer translations per Vietnamese source
- **Word-level alignment**: `Kể *** និទាន` (Vietnamese word *** Khmer equivalent)
- **Phrase-level equivalence**: `chế biến tinh tế *** វិធីធ្វើដ៏ប៉ិនប្រសប់`
- **Correction notes**: Alternative translations with explanations
- **Speaker roles**: `Phóng viên:` (interviewer) vs. `Người Khmer:` (interviewee)

---

## 2. Related Work Landscape (2024–2026)

### Vietnamese-Khmer MT

| Paper | Venue | Approach |
|---|---|---|
| Lightweight Training & Synthetic Data for Vi-Km | PACLIC 2025 | Lightweight fine-tuning + synthetic data |
| Khmer-Vietnamese NMT with Data Augmentation | Informatica 2024 | Back-translation + English pivot augmentation |
| Multilingual NMT with Filtering | PACLIC 2020 | Iterative multilingual NMT + word alignment filtering |

### Culturally-Aware MT

| Paper | Venue | Approach |
|---|---|---|
| Culture-aware MT: Catalan-Chinese | MT Summit 2025 | ~1,000 culturally-specific sentences for localization |
| CaMMT: Culturally Aware Multimodal MT | EMNLP Findings 2025 | Visual context for cultural item translation |
| Compositional Translation for Low-Resource MT | EMNLP Findings 2025 | Decompose + retrieve demonstrations |

### Discourse-Level MT

| Paper | Venue | Approach |
|---|---|---|
| TransGraph: Discourse Graph for Doc MT | EACL 2026 | Discourse graph neighborhoods for translation |
| Source-primed Multi-turn Conversation MT | EMNLP Findings 2025 | Multi-turn iterative document translation |
| Quality-Aware Decoding for Discourse MT | EACL 2026 | MBR decoding for discourse phenomena |

### Human Feedback in MT

| Paper | Venue | Approach |
|---|---|---|
| Direct Quality Optimization (DQO) | WMT 2025 | Quality estimation as proxy for human preference |
| RLHF for NMT | EAMT 2024 | Data filtering + RL + reranking |

---

## 3. Proposed Research Directions

---

### Direction 1: Culture-Grounded Retrieval-Augmented Translation for Low-Resource Pairs

#### Core Idea

Build a **Cultural Knowledge Base (CKB)** from conversational data, storing cultural entities (food names, rituals, customs) with bilingual context. At translation time, retrieve relevant cultural context to augment the MT model input.

#### Motivation

The dataset contains rich cultural entities that lack standardized translations:
- `Mắm bò hóc` → `ម៉មប្រហុក` (a fermented fish paste)
- `Chol Chnam Thmay` (Khmer New Year)
- `cốm dẹp` → `អំបុក` (flattened rice)
- `lễ Ok Om Bok` (Moon Worship Festival)

Standard MT models fail on these because they are rare in training data and carry deep cultural meaning.

#### Why Novel?

- CaMMT (EMNLP Findings 2025) uses **visual context** for cultural MT → we use **structured cultural knowledge retrieval**
- Unlike generic RAG: retrieval is based on **cultural concept similarity**, not just semantic similarity
- No prior work combines cultural KB construction with retrieval-augmented low-resource MT

#### Proposed Method

```
Source (Vi) → Cultural Entity Detection → CKB Retrieval → Augmented Input → MT Model → Target (Km)
                                              ↑
                               Cultural Knowledge Base
                          (entities + bilingual definitions
                           + usage examples from data)
```

1. **CKB Construction**: Extract cultural entities from parallel data, cluster by concept, store with bilingual context
2. **Cultural-Aware Retrieval**: Given input sentence, detect cultural entities and retrieve relevant KB entries
3. **Augmented Translation**: Prepend retrieved cultural context to MT model input

#### Expected Contributions

- Framework: CKB construction + cultural-aware retrieval + augmented translation
- Benchmark: Vietnamese-Khmer Cultural MT benchmark with entity-level evaluation
- Analysis: When does cultural retrieval help vs. not help?

#### Target Venues

ACL main, EMNLP main (Cultural NLP + MT track)

---

### Direction 2: Learning from Multi-Granularity Translator Annotations in Low-Resource MT

#### Core Idea

The dataset contains **three levels of annotation that are extremely rare** in MT datasets:

| Level | Example | Signal Type |
|---|---|---|
| **Sentence-level** | Multiple reference translations | Preference pairs |
| **Phrase-level** | `chế biến tinh tế *** វិធីធ្វើដ៏ប៉ិនប្រសប់` | Phrase alignment |
| **Word-level** | `Kể *** និទាន`, `Nhà *** ផ្ទះ` | Lexical mapping |

Propose a **Multi-Granularity Preference Learning** framework that combines DPO/RLHF with signals from all three levels simultaneously.

#### Why Novel?

- DQO (WMT 2025) and RLHF for MT use only **sentence-level quality scores**
- No prior work exploits **word/phrase-level translator rationales** as reward signals in MT training
- Connects to the hot trend of "learning from human explanations" but in the MT domain

#### Proposed Method

```
             ┌─────────────────────────────────────┐
             │   Multi-Granularity Loss Function    │
             │                                      │
             │  L_total = α·L_sent + β·L_phrase     │
             │           + γ·L_word                 │
             └──────┬──────────┬──────────┬─────────┘
                    │          │          │
            ┌───────▼──┐ ┌────▼─────┐ ┌──▼────────┐
            │ Sentence  │ │  Phrase  │ │   Word    │
            │ Preference│ │ Alignment│ │ Alignment │
            │  (DPO)    │ │  Loss    │ │   Loss    │
            └───────────┘ └──────────┘ └───────────┘
                 ↑              ↑            ↑
            Multi-ref      *** phrase    *** word
            labels         annotations   annotations
```

1. **Sentence-level**: DPO between multiple references (better vs. worse translations)
2. **Phrase-level**: Contrastive alignment loss on annotated phrase pairs
3. **Word-level**: Lexical constraint loss ensuring annotated word pairs align in attention

#### Expected Contributions

- Novel training objective combining multi-granularity supervision for MT
- Ablation: How much does fine-grained annotation help compared to sentence-level only?
- Dataset contribution: annotation schema and guidelines for low-resource MT

#### Target Venues

**ACL main** (Machine Learning for NLP + MT), EMNLP main

#### Novelty Assessment: ★★★★★

This direction exploits the **most unique feature** of your data. Multi-granularity annotations are extremely rare and hard to replicate → strong competitive advantage.

---

### Direction 3: Speaker-Role-Conditioned Discourse Translation for Ethnographic Interviews

#### Core Idea

The data has clear dialogue structure: **Phóng viên** (interviewer) asks formal questions vs. **Người Khmer** (interviewee) gives colloquial answers, organized by `topic` and `order`. Propose a discourse-aware MT model specialized for **ethnographic interviews** where speaker role conditioning determines translation style.

#### Key Linguistic Observation

| Speaker | Vietnamese Style | Khmer Translation Style |
|---|---|---|
| Interviewer | Formal, standard Vietnamese | Formal Khmer, complete sentences |
| Interviewee | Colloquial, dialectal, code-mixed | Colloquial Khmer, natural speech |

Same model needs **two different translation behaviors** depending on speaker role.

#### Why Novel?

- TransGraph (EACL 2026) and multi-turn MT (EMNLP Findings 2025) work on **high-resource languages** and **general text**
- **No existing work** studies discourse MT for interview genre in low-resource settings
- Unique insight: same language pair requires style-switching based on pragmatic context

#### Proposed Method

```
Dialogue History:
  [Interviewer] Q1 → Translation T1
  [Interviewee] A1 → Translation T1'
  [Interviewer] Q2 → Translation T2       ← Current turn
       ↓
  ┌─────────────────────┐
  │ Speaker Role Embed   │
  │ + Topic Embed        │
  │ + Discourse Position │
  └──────────┬──────────┘
             ↓
  ┌─────────────────────┐
  │ Context-Aware Encoder│ ← Previous turns as context
  └──────────┬──────────┘
             ↓
  ┌─────────────────────┐
  │ Style-Conditioned    │
  │ Decoder              │
  └──────────┬──────────┘
             ↓
        Translation T2
```

1. **Speaker Role Embedding**: Encode interviewer vs. interviewee role
2. **Discourse Context**: Use previous turns (with topic and order metadata) as context
3. **Style-Conditioned Decoding**: Adjust formality/style based on speaker role

#### Expected Contributions

- Speaker-role-aware architecture for dialogue MT
- Analysis: Impact of discourse context in low-resource interview translation
- Genre-specific findings: Interview translation vs. monologue translation quality

#### Target Venues

ACL main, NAACL (Discourse + MT), EMNLP

---

### Direction 4: Adaptive Translation Strategies for Culture-Specific Concepts

#### Core Idea

When translating cultural concepts, translators must choose between strategies:

| Strategy | Example (Vi → Km) |
|---|---|
| **(a) Transliteration** | `Mắm bò hóc` → Khmer phonetic approximation |
| **(b) Explanation** | `Mắm bò hóc` → Khmer description of fermented fish paste |
| **(c) Cultural Equivalent** | `Mắm bò hóc` → `ម៉ាំប្រហុក` (Prahok, the Khmer equivalent) |

The multi-reference labels provide evidence for all three strategies. Propose a model that **automatically selects the optimal translation strategy** for each cultural entity based on context.

#### Why Novel?

- Existing cultural MT (Catalan-Chinese, MT Summit 2025) only **evaluates** quality, does not **model translation strategy selection**
- This is a new task: **Cultural Translation Strategy Classification + Strategy-Conditioned Generation**
- Bridges NLP with Translation Studies theory (Venuti's domestication vs. foreignization) but operationalized computationally

#### Proposed Method

```
Source (Vi) ──→ Cultural Entity ──→ Strategy    ──→ Strategy-Conditioned ──→ Target (Km)
                Detection            Classifier       Generation
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │ Transliterate │
                                 │ Explain       │
                                 │ Equivalent    │
                                 │ Hybrid        │
                                 └──────────────┘
                                        ↑
                              Context features:
                              - Entity type (food/ritual/kinship)
                              - Audience familiarity
                              - Discourse context
                              - Formality level
```

#### Annotation Scheme for Strategy Labels

Extract strategy labels from existing multi-reference data:

```
Reference 1: "ម៉មប្រហុក" (equivalent)       → Strategy: EQUIVALENT
Reference 2: "Mắm bò hốc *** ម៉ាំប្រហុក"   → Strategy: ALIGNED_EQUIVALENT
Reference 3: "ម៉ាំប្រហុក ...explanation..."  → Strategy: EXPLAIN
```

#### Expected Contributions

- Taxonomy: Classification of cultural translation strategies from data
- Model: Strategy classifier + strategy-conditioned generation
- Human evaluation: When is each strategy preferred?
- Interdisciplinary bridge: Translation Studies × NLP

#### Target Venues

**ACL main** (highly interdisciplinary), EMNLP (computational linguistics angle)

#### Novelty Assessment: ★★★★★

Highly original, bridges two disciplines, and directly addresses a real-world problem in cultural preservation.

---

### Direction 5: Culturally-Faithful Synthetic Data Generation for Endangered Language MT

#### Core Idea

Existing data augmentation for Vietnamese-Khmer MT uses back-translation or pivot through English — neither preserves **cultural faithfulness**. Propose using LLMs to generate new Vietnamese ethnographic conversations within the same cultural domain, then apply a **Cultural Faithfulness Filter** to ensure synthetic data accurately reflects Khmer cultural practices before translating to Khmer.

#### Why Novel?

- Back-translation (Informatica 2024) and pivot-based augmentation have no mechanism for **cultural accuracy control**
- Compositional Translation (EMNLP Findings 2025) decomposes sentences but ignores **domain/cultural constraints**
- New concept: **Cultural Faithfulness Score** — a metric evaluating whether synthetic data is culturally appropriate

#### Proposed Pipeline

```
Step 1: Topic-Guided Generation
  ┌──────────────────────────────────────────┐
  │ LLM + Topic Prompt                       │
  │ "Generate a conversation about Khmer     │
  │  wedding food traditions in Mekong Delta" │
  └──────────────┬───────────────────────────┘
                 ↓
Step 2: Cultural Faithfulness Filtering
  ┌──────────────────────────────────────────┐
  │ Cultural Faithfulness Classifier          │
  │ - Entity accuracy (real dishes/rituals?)  │
  │ - Practice accuracy (correct customs?)    │
  │ - Geographic consistency (Mekong Delta?)  │
  └──────────────┬───────────────────────────┘
                 ↓
Step 3: Translation + Quality Filtering
  ┌──────────────────────────────────────────┐
  │ MT Model → Khmer Translation             │
  │ + Quality Estimation Filter              │
  │ + Optional Human Verification            │
  └──────────────┬───────────────────────────┘
                 ↓
Step 4: Augmented Training
  ┌──────────────────────────────────────────┐
  │ Original Data + Filtered Synthetic Data  │
  │ → Fine-tune MT Model                     │
  └──────────────────────────────────────────┘
```

#### Expected Contributions

- Pipeline: Topic-guided generation → Cultural filtering → Translation → Quality filtering
- New metric: Cultural Faithfulness Score (CFS)
- Ablation: Culturally-filtered vs. unfiltered synthetic data impact on MT quality
- Broader impact: Framework applicable to other endangered language MT tasks

#### Target Venues

ACL main (Resources + MT), EMNLP, LREC-COLING

---

## 4. Comparison & Recommendation

| # | Direction | Novelty | Feasibility | Data Fit | Recommended Venue |
|---|---|:---:|:---:|:---:|---|
| 1 | Cultural KB Retrieval-Augmented MT | ★★★★ | ★★★ | ★★★★ | ACL/EMNLP main |
| 2 | Multi-Granularity Translator Annotations | ★★★★★ | ★★★★ | ★★★★★ | **ACL main** |
| 3 | Speaker-Role Discourse MT | ★★★★ | ★★★★ | ★★★★ | ACL/NAACL |
| 4 | Adaptive Cultural Translation Strategy | ★★★★★ | ★★★ | ★★★★ | **ACL main** |
| 5 | Culturally-Faithful Synthetic Data | ★★★★ | ★★★★ | ★★★ | ACL/EMNLP/LREC |

### Top Recommendations

**Best single paper**: Direction **#2** (Multi-Granularity Annotations)
- Directly exploits the most unique feature of your data
- Multi-reference + word-level annotations are extremely rare → hard for competitors to replicate
- Clean, well-defined contribution with clear ablation experiments

**Most interdisciplinary**: Direction **#4** (Adaptive Translation Strategy)
- Bridges Translation Studies and NLP — ACL/EMNLP strongly favors this
- Novel task formulation with practical impact on cultural preservation

**Best combination for a strong paper**: Directions **#2 + #4** merged
- Use multi-granularity annotations to learn when to apply which cultural translation strategy
- This would be a comprehensive contribution covering both methodology and linguistic analysis

**Safest bet with high feasibility**: Direction **#5** (Synthetic Data)
- Well-understood evaluation framework (BLEU/COMET improvement)
- Clear pipeline with concrete experiments
- Cultural faithfulness metric is a novel yet evaluable contribution
