# Self-Critique & Revised Research Directions

> This document critically examines the 5 research directions proposed in `research_directions.md`, using data-driven evidence to expose weaknesses, then iteratively revises each direction through multiple rounds of critique.

---

## Round 0: Hard Data Evidence

Before any critique, let's ground ourselves in the **actual numbers**:

| Metric | Value | Implication |
|---|---|---|
| Total samples | 1,856 | Very small for MT training |
| Unique conversation IDs | 450 | ~4.1 turns/conversation avg |
| QA format samples | 352 (19%) | Individual Q&A about food culture |
| Dialogue format samples | 1,504 (81%) | Structured interviews |
| Unique topics | 56 | Diverse but shallow coverage |
| **Samples with 2+ references** | **145 (7.8%)** | **Extremely sparse multi-reference** |
| **Samples with *** annotations** | **102 (5.5%)** | **Extremely sparse word alignments** |
| **Total word/phrase alignment pairs** | **92** | **Almost negligible signal** |
| Samples with ### separator | 15 (0.8%) | Rare annotation pattern |
| Identifiable interviewer turns | 314 | ~21% of dialogue data |
| Identifiable interviewee turns | 398 | ~26% of dialogue data |
| Non-empty Comments | 0 | Unused field |

**Critical takeaway**: The annotations I built the proposals around (multi-reference, ***, word alignments) are present in **less than 8%** of the data. This fundamentally undermines several directions.

---

## Round 1: Per-Direction Critique

---

### Direction 1: Culture-Grounded Retrieval-Augmented Translation

#### What I Claimed

> Build a Cultural Knowledge Base from conversational data and use retrieval to augment MT.

#### Critique

| Issue | Severity | Evidence |
|---|---|---|
| **CKB is just a glossary** | High | With ~1,856 samples, the "knowledge base" would contain maybe 50–100 unique cultural entities. That's a bilingual dictionary, not a knowledge base. Calling it a "CKB" overpromises. |
| **"Cultural concept similarity" is vague** | High | I never defined how cultural concept similarity differs from standard semantic similarity. If it's just cosine similarity on embeddings, this is standard RAG with marketing language. |
| **Entity detection is circular** | Medium | Training a cultural entity detector for Khmer requires labeled data... which we don't have. We'd need manual annotation just to build the detector. |
| **Pipeline = standard RAG** | High | Source → Detect → Retrieve → Augment → Translate is exactly what RAG does. Adding the word "cultural" doesn't make it novel enough for ACL. |
| **Evaluation gap** | Medium | How do we evaluate whether CKB retrieval improves *cultural accuracy* specifically? BLEU won't capture this. No existing metric exists. |

#### Verdict: Direction 1 is **over-engineered for what is essentially domain-specific RAG**. The novelty claim is inflated.

---

### Direction 2: Multi-Granularity Translator Annotations

#### What I Claimed

> Exploit three levels of annotation (sentence/phrase/word) using DPO/RLHF for multi-granularity preference learning.

#### Critique

| Issue | Severity | Evidence |
|---|---|---|
| **Multi-reference is too sparse** | **Critical** | Only **145/1,856 (7.8%)** samples have 2+ references. You cannot train DPO on 145 preference pairs for an MT system. This is statistically meaningless. |
| **Word alignments are negligible** | **Critical** | Only **92 alignment pairs** total across the entire dataset. The L_word loss term in my proposed loss function would receive signal from ~92 data points. This is noise, not signal. |
| **DPO requires quality ranking** | High | Having 2 references ≠ having preference pairs. Both references could be equally valid stylistic variants. The data provides **no quality ordering** between references. |
| **Overclaimed "extremely rare" annotations** | High | I said "three levels of annotation that are extremely rare in MT datasets." The truth: they're sparse **because most samples don't have them**, not because the dataset is uniquely rich. |
| **L_total is trivially a weighted sum** | Medium | The loss function `L_total = α·L_sent + β·L_phrase + γ·L_word` is technically just multi-task learning with three losses. This isn't architecturally novel. |

#### Verdict: Direction 2 is **fatally flawed** in its current form. The data does not support the proposed method. **92 alignment pairs and 145 multi-references cannot sustain a training framework.**

---

### Direction 3: Speaker-Role Discourse MT for Interviews

#### What I Claimed

> Speaker role conditioning (interviewer vs. interviewee) determines translation style in discourse-aware MT.

#### Critique

| Issue | Severity | Evidence |
|---|---|---|
| **Speaker roles are not always labeled** | High | Only 314 + 398 = 712 turns have identifiable speaker roles out of 1,504 dialogue turns (~47%). The rest lack explicit speaker markers. |
| **Conversations are too short** | High | 450 conversations averaging ~3.3 turns. Discourse-level MT papers (TransGraph, etc.) use documents with 10+ sentences. 3-turn conversations have almost no discourse signal. |
| **Style difference is assumed, not verified** | High | I assumed interviewer = formal, interviewee = colloquial. But looking at the actual data, **both sides use fairly formal Vietnamese** in many cases. The style contrast may not exist as strongly as claimed. |
| **Overfitting risk** | High | Adding speaker role embeddings + topic embeddings + discourse position to a model trained on ~1,500 samples will almost certainly overfit. More parameters, same tiny data. |
| **Generalizability questioned** | Medium | "Interview MT" is an extremely niche genre. Reviewers will ask: "Does this generalize beyond ethnographic interviews?" Probably not. |

#### Verdict: Direction 3 has **an interesting intuition but is empirically unsupported**. The data is too small and the style contrast is unverified.

---

### Direction 4: Adaptive Cultural Translation Strategy

#### What I Claimed

> Automatically select between transliteration, explanation, and cultural equivalent strategies for culture-specific concepts.

#### Critique

| Issue | Severity | Evidence |
|---|---|---|
| **Strategy labels are unextractable** | **Critical** | The *** annotations are **not** strategy labels. They're mostly just word alignments (e.g., "Kể *** និទាន"). Extracting strategy types from them requires significant manual re-annotation. |
| **Only 102 annotated samples** | **Critical** | 102 samples with any *** annotation, and 92 alignment pairs total. This is far too little to train a strategy classifier. |
| **Strategy taxonomy is ad-hoc** | High | The transliterate/explain/equivalent taxonomy was proposed without grounding in Translation Studies literature. Venuti's domestication/foreignization is a binary, not a 4-way classification. |
| **Context features are unavailable** | Medium | "Audience familiarity" and "formality level" are not annotated in the data. These are hypothetical features, not usable ones. |
| **Pipeline error propagation** | Medium | Entity Detection → Strategy Classification → Conditioned Generation. Each step can fail, and errors cascade. In a low-resource setting, each component is fragile. |

#### Verdict: Direction 4 has the **strongest conceptual novelty** but the **weakest data support**. The idea is publishable, but not with this data alone.

---

### Direction 5: Culturally-Faithful Synthetic Data Generation

#### What I Claimed

> Use LLMs to generate culturally-faithful synthetic conversations for data augmentation.

#### Critique

| Issue | Severity | Evidence |
|---|---|---|
| **LLMs don't know Khmer Krom culture** | **Critical** | GPT-4/Claude likely confuse Khmer culture in Cambodia with Khmer minority culture in Vietnam's Mekong Delta. These are related but distinct. LLM-generated "Khmer cultural conversations" will likely be inaccurate. |
| **Cultural Faithfulness Classifier is circular** | High | Training a classifier to detect cultural inaccuracy requires labeled examples of both accurate and inaccurate cultural content. Where does this training data come from? |
| **Garbage-in-garbage-out for MT** | High | If the baseline MT model is poor (it's low-resource), translating synthetic Vietnamese into Khmer produces noisy translations. Augmenting with noisy data can **hurt** performance. |
| **"Endangered language" is factually wrong** | High | Khmer has ~16 million speakers. It is NOT endangered. Vietnamese-Khmer is a low-resource *pair*, but the language itself is well-resourced. Reviewers will flag this mischaracterization. |
| **Just back-translation with extra steps** | Medium | Strip away the cultural filtering, and this pipeline is: generate source → translate → filter by quality → augment. That's back-translation. The cultural filter is the only novel part, and it's the hardest part to build. |

#### Verdict: Direction 5 is **practically useful but has a circular dependency** (need good MT to augment MT) and the core novelty (cultural filter) is the hardest component to build.

---

## Round 1 Summary: What Survives?

| Direction | Original Rating | Post-Critique Rating | Status |
|---|---|---|---|
| 1. Cultural RAG | ★★★★ | ★★☆ | Overengineered, "just RAG" |
| 2. Multi-Granularity | ★★★★★ | ★☆☆ | **Fatally flawed** (data too sparse) |
| 3. Speaker-Role Discourse | ★★★★ | ★★☆ | Interesting but unverifiable |
| 4. Cultural Strategy | ★★★★★ | ★★★ | Best concept, worst data support |
| 5. Synthetic Data | ★★★★ | ★★☆ | Circular dependency |

**Honest conclusion: None of the 5 directions are publishable at ACL/EMNLP in their current form.**

---

## Round 2: Cross-Cutting Problems

Before revising, let's address the systemic issues:

### Problem A: Data Size (1,856 samples)

This is the elephant in the room. 1,856 parallel samples is:
- **Too small** to fine-tune any MT model from scratch
- **Too small** for DPO/RLHF (needs thousands of preference pairs)
- **Barely sufficient** for few-shot in-context learning with LLMs
- **Comparable to** the Catalan-Chinese cultural MT paper (1,000 samples) that was published at MT Summit 2025 (a B-tier venue, not A*)

**Implication**: Any A*-worthy paper must either (a) propose methods that work WITH small data, or (b) contribute the dataset itself as a resource paper, or (c) be primarily analytical (corpus study) rather than system-building.

### Problem B: Evaluation

- BLEU is unreliable for Khmer (morphologically rich, different script)
- COMET/COMETKiwi may not support Khmer well
- Human evaluation is expensive and requires Khmer-Vietnamese bilingual annotators
- No existing benchmark for Vietnamese-Khmer cultural MT

**Implication**: Any proposal must include a realistic evaluation plan. "We'll use BLEU and COMET" is insufficient.

### Problem C: Reproducibility & Dataset Release

- The data contains cultural interviews with identifiable speakers
- Privacy and consent issues may prevent public release
- Without a public dataset, the paper's impact and reproducibility suffer
- ACL/EMNLP increasingly require data availability

### Problem D: Baseline Reality

- What is the current SOTA for Vi-Km MT?
- Without strong baselines (Google Translate, NLLB, GPT-4), any improvement claim is hollow
- The PACLIC 2025 paper already addresses Vi-Km with lightweight training

---

## Round 3: Revised Directions (Post-Critique)

Based on the brutal self-critique above, here are **revised directions** that honestly account for the data limitations.

---

### Revised Direction A: Benchmarking Cultural Competence in LLM-Based Translation for Low-Resource Pairs

> **Shift from "building systems" to "evaluating and understanding"**

#### Core Idea

Instead of training a new MT model (impossible with 1,856 samples), **benchmark existing LLMs** (GPT-4, Claude, Gemini, NLLB, Google Translate) on culturally-grounded Vietnamese-Khmer translation. Propose a **Cultural Translation Evaluation Framework** with fine-grained metrics.

#### Why This Survives Critique

| Previous Weakness | How It's Addressed |
|---|---|
| Data too small for training | No training needed — evaluation/analysis paper |
| No evaluation metric | Proposing the metric IS the contribution |
| "Just RAG" concern | Not building a system; studying what helps |
| Baseline unknown | Establishing baselines IS the contribution |

#### Proposed Framework

```
Evaluation Dimensions:
├── 1. General Translation Quality (BLEU, COMET, human rating)
├── 2. Cultural Entity Accuracy
│   ├── Named entities (festivals, dishes, rituals)
│   ├── Concept preservation (do cultural concepts survive translation?)
│   └── Appropriateness (is the Khmer phrasing culturally natural?)
├── 3. Discourse Coherence (for dialogue data)
│   ├── Speaker consistency
│   ├── Topic continuity
│   └── Register appropriateness (formal/informal)
└── 4. Strategy Analysis
    ├── What strategies do LLMs use for cultural entities?
    ├── How do these compare to human translator strategies?
    └── Does providing cultural context (few-shot) change strategy?
```

#### Experimental Design

| Experiment | What It Tests |
|---|---|
| Zero-shot LLM translation | Baseline: how good are LLMs out-of-the-box? |
| Random few-shot (k=1,3,5) | Does any parallel example help? |
| Topic-matched few-shot | Does domain relevance matter? |
| Cultural entity-focused few-shot | Does retrieving examples with same cultural entities help? |
| Full dialogue context vs. isolated turns | Does discourse context help? |
| Vi→Km vs. Km→Vi direction | Is one direction harder? |

#### Contributions

1. **Benchmark**: First cultural MT evaluation benchmark for Vietnamese-Khmer
2. **Evaluation framework**: Fine-grained cultural competence metrics (reusable for other language pairs)
3. **Empirical findings**: What helps and what doesn't for culturally-grounded low-resource MT
4. **Dataset**: The 1,856 samples become the benchmark test set (natural role for small data)

#### Self-Critique of Revised Direction A

- Risk: "Just a benchmark paper" — some reviewers dislike pure evaluation papers
- Mitigation: The cultural evaluation framework is genuinely novel and reusable
- Risk: Human evaluation is expensive
- Mitigation: Focus on automatic metrics first, targeted human eval on cultural entities only
- Risk: LLMs might be surprisingly good, leaving no room for analysis
- Mitigation: That itself is a finding; plus cultural entity analysis will always reveal interesting patterns

#### Target Venues

ACL main (Resources & Evaluation track), EMNLP main, WMT shared task

#### Post-Revision Rating: ★★★★ (Novelty) / ★★★★★ (Feasibility) / ★★★★★ (Data Fit)

---

### Revised Direction B: A Corpus Study of Translation Strategies for Culture-Specific Concepts in Vietnamese-Khmer

> **Shift from "building a classifier" to "corpus analysis + taxonomy + human study"**

#### Core Idea

Conduct a **systematic corpus analysis** of how human translators handle culture-specific concepts in Vietnamese-Khmer translation. Build a **grounded taxonomy** of translation strategies, analyze when each is used, and evaluate whether MT systems match human strategy choices.

#### Why This Survives Critique

| Previous Weakness | How It's Addressed |
|---|---|
| Only 102 *** samples | Extend annotation on ALL 1,856 samples (manual) for cultural entities |
| Strategy taxonomy was ad-hoc | Ground in Translation Studies: Vinay & Darbelnet's procedures, Newmark's strategies |
| No strategy classifier training data | Don't train a classifier — do corpus analysis |
| "Audience familiarity" unavailable | Analyze from translator's actual choices, not predicted features |

#### Methodology

**Phase 1: Annotation (extend existing data)**
- Identify all cultural entities across 1,856 samples
- For each entity, annotate the translation strategy used:
  - **Borrowing**: Source term kept (e.g., "Phật" kept as-is)
  - **Calque**: Literal translation of components
  - **Cultural equivalent**: Replace with target culture equivalent
  - **Explicitation**: Add explanation not in source
  - **Reduction**: Simplify or omit cultural detail
  - **Transliteration**: Phonetic adaptation to target script
- Annotate context factors: entity type, discourse position, speaker role

**Phase 2: Corpus Analysis**
- Strategy distribution across entity types (food vs. ritual vs. kinship vs. ...)
- Strategy variation across topics (wedding customs vs. farming vs. ...)
- Inter-annotator agreement on strategy classification
- Correlation between strategy choice and translation quality

**Phase 3: MT System Evaluation**
- Run GPT-4, NLLB, Google Translate on same data
- Classify their strategy choices using same taxonomy
- Compare: Do MT systems match human strategies? Where do they diverge?

#### Contributions

1. **Taxonomy**: Grounded, empirically-validated translation strategy taxonomy for cultural concepts
2. **Annotated corpus**: 1,856 samples with cultural entity + strategy annotations
3. **Comparative analysis**: Human vs. MT strategy choices
4. **Guidelines**: Recommendations for culturally-appropriate MT evaluation

#### Self-Critique of Revised Direction B

- Risk: "Just a corpus study, no model" — some ACL reviewers want computational novelty
- Mitigation: Target *CL, TACL, or Computational Linguistics journal; also ACL Linguistic Diversity track
- Risk: Annotation is expensive and time-consuming
- Mitigation: Focus on a subset (e.g., food culture domain, ~352 QA samples) for manageable annotation
- Risk: Taxonomy might not transfer to other language pairs
- Mitigation: Design taxonomy to be language-pair agnostic; test on 1-2 other cultural pairs for validation

#### Target Venues

ACL main (Linguistic Diversity track), *CL, TACL, Computational Linguistics journal, LREC-COLING

#### Post-Revision Rating: ★★★★★ (Novelty) / ★★★★ (Feasibility) / ★★★★★ (Data Fit)

---

### Revised Direction C: Does Dialogue Context Help Low-Resource MT? Evidence from Vietnamese-Khmer Ethnographic Interviews

> **Shift from "building discourse-aware architecture" to "empirical study with LLMs"**

#### Core Idea

Use the structured dialogue data (450 conversations, 1,504 turns) to empirically test: **Does providing dialogue context (previous turns, speaker roles, topic) improve LLM-based translation quality?** This avoids the data scarcity problem (no training needed) while providing valuable insights for discourse-aware MT.

#### Why This Survives Critique

| Previous Weakness | How It's Addressed |
|---|---|
| Data too small for training | Use LLMs in-context, no training |
| Speaker style contrast unverified | Verify as part of the study (finding, not assumption) |
| Overfitting risk | No model parameters to overfit |
| 3-turn conversations too short | Study whether even short context helps |

#### Experimental Design

```
Conditions (systematically varied):
├── Context level
│   ├── C0: Isolated sentence (no context)
│   ├── C1: Previous 1 turn
│   ├── C2: Previous 2 turns
│   └── C_all: Full conversation
├── Metadata
│   ├── M0: No metadata
│   ├── M1: + Speaker role label
│   ├── M2: + Topic label
│   └── M3: + Speaker role + Topic
├── Translation direction
│   ├── Vi → Km
│   └── Km → Vi
└── Model
    ├── GPT-4o
    ├── Claude 3.5
    ├── Gemini 1.5
    └── NLLB-3.3B (no context baseline)
```

**Analysis dimensions:**
- Does context help overall quality? (BLEU, COMET, human eval)
- Which context elements help most? (previous turns vs. speaker role vs. topic)
- Does context help MORE for certain phenomena? (pronouns, ellipsis, cultural references)
- Is there a point of diminishing returns? (1 turn vs. 2 turns vs. all)
- QA data vs. dialogue data: does structure matter?

#### Contributions

1. **Empirical study**: First systematic study of context effects in low-resource cultural MT
2. **Practical guidelines**: How much context is "enough" for dialogue translation?
3. **Cross-model comparison**: Do different LLMs benefit from context differently?
4. **Error taxonomy**: What types of errors does context fix vs. introduce?

#### Self-Critique of Revised Direction C

- Risk: "Just prompt engineering" — some may see this as trivially varying prompts
- Mitigation: The SYSTEMATIC factorial design + fine-grained analysis is the value, not any single prompt
- Risk: Results might be language-pair-specific
- Mitigation: Discuss generalizability; encourage replication on other pairs
- Risk: If context doesn't help (null result), paper is harder to publish
- Mitigation: Null results ARE valuable if well-analyzed. Plus, some conditions will likely help while others won't — the pattern is the finding.

#### Target Venues

EMNLP main, ACL Findings, WMT, EACL

#### Post-Revision Rating: ★★★★ (Novelty) / ★★★★★ (Feasibility) / ★★★★★ (Data Fit)

---

### Revised Direction D: Targeted Data Augmentation for Culturally-Specific Low-Resource MT

> **Shift from "culturally-faithful LLM generation" to "targeted augmentation with controlled experiments"**

#### Core Idea

Compare data augmentation strategies specifically for **culturally-grounded low-resource MT**:
1. Generic back-translation
2. English-pivot augmentation
3. Topic-constrained LLM paraphrasing (Vietnamese side only)
4. Cross-lingual transfer from related high-resource pairs (e.g., Thai-Khmer, Vietnamese-Chinese)

The key question: **Does domain/cultural specificity of augmented data matter more than sheer volume?**

#### Why This Survives Critique

| Previous Weakness | How It's Addressed |
|---|---|
| LLMs don't know Khmer Krom culture | Augment Vietnamese side only (paraphrase), not generate from scratch |
| Cultural Faithfulness Classifier is circular | Don't need classifier — use topic-matching as proxy for cultural relevance |
| "Endangered language" was wrong | Correctly frame as "low-resource pair with cultural domain specificity" |
| Garbage-in-garbage-out | Compare augmentation strategies head-to-head; measure when noise hurts |

#### Experimental Design

| Strategy | Source of Augmented Data | Cultural Specificity |
|---|---|---|
| Baseline | Original 1,856 pairs only | High (real data) |
| Back-translation | Monolingual Khmer → translate to Vi | Low (generic) |
| English pivot | Vi → En → Km (via high-resource models) | Low (loses cultural nuance) |
| Paraphrase augmentation | LLM paraphrases Vietnamese source, keep Khmer target | Medium (same cultural entities) |
| Topic-constrained generation | LLM generates new Vi sentences ON SAME TOPICS | Medium-High |
| Cross-lingual transfer | Thai-Km or other related pair data | Variable |

**Controlled variable**: Fix total augmented data size (e.g., 5K, 10K, 20K) and vary only the augmentation strategy.

#### Contributions

1. **Controlled comparison**: First systematic comparison of augmentation strategies for cultural MT
2. **Finding**: Whether cultural specificity of augmented data matters
3. **Practical method**: Best augmentation strategy for low-resource cultural MT
4. **Analysis**: When does augmentation help cultural entity translation specifically?

#### Self-Critique of Revised Direction D

- Risk: "Just comparing known augmentation methods" — incremental
- Mitigation: The cultural specificity analysis angle is new; no one has asked "does cultural relevance of augmented data matter?"
- Risk: Paraphrase augmentation might not work for Khmer (limited Khmer LLM capability)
- Mitigation: Augment Vietnamese side only; Khmer target stays real
- Risk: Cross-lingual transfer from Thai-Khmer might not be available
- Mitigation: This is one condition among many; if unavailable, drop it

#### Target Venues

EMNLP main, ACL Findings, WMT, LREC-COLING

#### Post-Revision Rating: ★★★☆ (Novelty) / ★★★★★ (Feasibility) / ★★★★ (Data Fit)

---

### Revised Direction E: Vietnamese-Khmer Cultural MT — A Resource and Benchmark Paper

> **Shift from "method paper" to "resource contribution"**

#### Core Idea

Accept that 1,856 culturally-rich parallel samples is a **valuable resource for the community** even without a novel method. Package the dataset as a proper benchmark:
- Clean and standardize annotations
- Add linguistic metadata (cultural entity spans, strategy labels, discourse structure)
- Define train/dev/test splits
- Provide baselines (NLLB, Google Translate, GPT-4, fine-tuned mBART)
- Release publicly with documentation

#### Why This Survives Critique

| Previous Weakness | How It's Addressed |
|---|---|
| Data too small for training | Positioned as benchmark/test set, not training set |
| Annotations inconsistent | Cleaning and standardization IS the contribution |
| No novel method | Resource papers are a recognized contribution type |
| Reproducibility concern | Full public release with license |

#### What Makes This A*-Worthy

- **Linguistic diversity**: ACL/EMNLP value underrepresented language pairs
- **Cultural dimension**: The ethnographic content is genuinely unique
- **Multi-faceted evaluation**: The data supports testing MT on general quality, cultural competence, discourse coherence, and entity handling simultaneously
- **Comparable precedents**: FLORES-200 (resource paper, highly cited), NTREX-128, CaMMT benchmark

#### Dataset Documentation Required

```
├── Data Statement (Bender & Friedman, 2018)
│   ├── Curation rationale
│   ├── Language variety (Khmer Krom vs. standard Khmer)
│   ├── Speaker demographics
│   ├── Annotation process
│   └── Ethics and consent
├── Annotation Guidelines
│   ├── Cultural entity annotation
│   ├── Translation strategy annotation
│   └── Quality assessment rubric
├── Splits
│   ├── Test set: 500 samples (stratified by topic)
│   ├── Dev set: 200 samples
│   └── Training seed: 1,156 samples
└── Baselines
    ├── NLLB-200
    ├── Google Translate
    ├── GPT-4o (zero-shot and few-shot)
    └── Fine-tuned mBART/mT5
```

#### Self-Critique of Revised Direction E

- Risk: "Just a dataset, no method" — some reviewers want algorithmic novelty
- Mitigation: Combine with Direction A (benchmark + evaluation framework + baseline analysis)
- Risk: 1,856 samples might be seen as too small for a standalone resource paper
- Mitigation: Emphasize the **cultural annotation richness**, not raw size; CaMMT had 5,800 samples at EMNLP Findings
- Risk: Privacy/consent for public release
- Mitigation: Anonymize speaker identities; obtain institutional ethics approval; de-identify personal information

#### Target Venues

ACL main (Resource track), LREC-COLING, EMNLP (Resource track)

#### Post-Revision Rating: ★★★☆ (Novelty) / ★★★★★ (Feasibility) / ★★★★★ (Data Fit)

---

## Round 4: Final Comparison (Post All Critiques)

### Original vs. Revised Ratings

| # | Original Direction | Original Rating | Revised Direction | Revised Rating |
|---|---|---|---|---|
| 1 | Cultural RAG for MT | ★★★★ | **A. Benchmarking Cultural Competence in LLM-based MT** | ★★★★½ |
| 2 | Multi-Granularity Annotations | ★★★★★ | *(Absorbed into A and B)* | — |
| 3 | Speaker-Role Discourse MT | ★★★★ | **C. Does Dialogue Context Help Low-Resource MT?** | ★★★★ |
| 4 | Cultural Translation Strategy | ★★★★★ | **B. Corpus Study of Translation Strategies** | ★★★★½ |
| 5 | Culturally-Faithful Synthetic Data | ★★★★ | **D. Targeted Augmentation for Cultural MT** | ★★★½ |
| — | *(new)* | — | **E. Resource & Benchmark Paper** | ★★★★ |

### Feasibility × Impact Matrix

```
                    High Feasibility    Low Feasibility
                ┌───────────────────┬───────────────────┐
High Impact     │   A (Benchmark)   │                   │
                │   E (Resource)    │                   │
                ├───────────────────┼───────────────────┤
Medium Impact   │   C (Context)     │   B (Corpus       │
                │   D (Augment)     │      Study)       │
                └───────────────────┴───────────────────┘
```

---

## Round 5: Final Recommendations

### Strategy 1: The "Safe A*" Path — Combine A + E

**Paper title idea**: *"CulturalMT-ViKm: A Benchmark for Evaluating Cultural Competence in Vietnamese-Khmer Machine Translation"*

- Package the dataset as a benchmark (Direction E)
- Define the cultural evaluation framework (Direction A)
- Run comprehensive LLM experiments (Direction A)
- Submit to **ACL or EMNLP Resource Track**

**Why this works**: Resource papers with thorough evaluation are consistently accepted at A* venues. The cultural dimension and underrepresented language pair add novelty. The data size is appropriate for a benchmark/test set.

**Estimated effort**: 2–3 months (data cleaning, annotation, experiments, writing)

### Strategy 2: The "High Novelty" Path — Direction B (possibly + A)

**Paper title idea**: *"How Do Humans Translate Culture? A Corpus Study of Translation Strategies in Vietnamese-Khmer"*

- Deep corpus analysis of translation strategies (Direction B)
- Ground in Translation Studies theory
- Compare with MT system behavior
- Submit to **ACL main (Linguistic Diversity)** or **Computational Linguistics journal**

**Why this works**: Genuinely novel interdisciplinary contribution. Corpus studies with real linguistic insight are valued at top venues.

**Estimated effort**: 3–4 months (annotation work is bottleneck)

### Strategy 3: The "Maximum Papers" Path — C + D as separate papers

- Direction C → empirical study paper for EMNLP/WMT
- Direction D → augmentation comparison for LREC-COLING or ACL Findings

**Why this works**: Both are self-contained, well-scoped, and feasible with the existing data.

**Estimated effort**: 2 months each, can be done in parallel

### My Final Honest Ranking

| Rank | Strategy | Confidence for A* | Notes |
|---|---|---|---|
| 1 | A + E (Benchmark) | **High** | Safest path; clear contribution; feasible |
| 2 | B (Corpus Study) | **Medium-High** | Highest novelty; annotation effort is risk |
| 3 | C (Context Study) | **Medium** | Solid empirical work; might land Findings |
| 4 | D (Augmentation) | **Medium-Low** | More incremental; better for B-tier venues |

---

## Key Lessons from This Critique Exercise

1. **Always count your data before proposing methods.** I proposed DPO/RLHF for 145 preference pairs. That's embarrassing in retrospect.

2. **"Novel framing" ≠ "Novel method."** Adding "cultural" to "RAG" doesn't make it ACL-worthy.

3. **Small data → analysis papers, not system papers.** With 1,856 samples, you're building a benchmark, not training a model.

4. **The data's strength is its CONTENT, not its ANNOTATIONS.** The culturally-rich parallel conversations are valuable. The sparse *** annotations are not.

5. **Feasibility matters as much as novelty.** Direction 4 (original) was the most "novel" but the least feasible. Direction A+E is less exciting but much more publishable.

6. **Be honest about what the data CAN and CANNOT support.** Overpromising kills papers in review.
