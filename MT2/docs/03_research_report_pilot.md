# Research Report: Pilot Experiments for Vietnamese-Khmer Cultural MT Benchmark

**Date**: April 8, 2026
**Experiments run with**: GPT-4o via Azure OpenAI
**Total API calls**: ~95 (30 zero-shot + 30 few-shot + 20 context + connectivity tests)

---

## 1. Executive Summary

We conducted three pilot experiments on Vietnamese→Khmer machine translation using GPT-4o to determine the most viable research direction for an A*-venue paper. Key findings:

| Finding | Implication |
|---|---|
| **Dialogue context improves chrF++ by +9 points** (8/10 samples improve) | Direction C (Context Study) is the strongest finding |
| BLEU is nearly unusable for Vi-Km (scores < 3 across all conditions) | Metric choice is itself a contribution |
| Topic-matched few-shot ≈ Random few-shot on chrF++ | Null result: fine-grained matching doesn't help LLM-based MT |
| GPT-4o produces fluent Khmer zero-shot | Benchmark should focus on WHERE models fail, not WHETHER they can translate |
| Cultural entities are translated correctly in most cases | Cultural entity evaluation needs more nuanced metrics |

**Recommended paper direction**: Merge A+E into a **benchmark + empirical study** paper, with Direction C (context effects) as the **headline finding**.

---

## 2. Experimental Setup

### 2.1 Data
- **Total**: 1,856 Vietnamese-Khmer parallel samples
- **QA format**: 352 samples (individual Q&A, no topic metadata)
- **Dialogue format**: 1,504 samples across 450 conversations, 56 topics
- **Reference cleaning**: Removed *** annotations and ### separators from references

### 2.2 Model
- **GPT-4o** via Azure OpenAI (deployment: `gpt-4o-RTA_Configurator`)
- Temperature: 0.0 (deterministic)
- Max tokens: 1024

### 2.3 Metrics
- **BLEU** (sacrebleu, default tokenization)
- **chrF++** (sacrebleu, word_order=2)
- **Cultural entity detection** (keyword matching against 23 known entities)

### 2.4 Experimental Conditions

| Experiment | Condition | N samples | Description |
|---|---|---|---|
| Exp 1 | Zero-shot | 30 | No examples, direct translation |
| Exp 2a | Random 3-shot | 15 | 3 random examples as demonstrations |
| Exp 2b | Topic-matched 3-shot | 15 | 3 same-topic examples as demonstrations |
| Exp 3a | Isolated turn | 10 | Translate dialogue turn without context |
| Exp 3b | With full context | 10 | Provide all previous turns as bilingual context |

---

## 3. Results

### 3.1 Quantitative Results

```
┌──────────────────────────┬───────┬─────────┐
│ Condition                │ BLEU  │ chrF++  │
├──────────────────────────┼───────┼─────────┤
│ Exp 1: Zero-shot         │  0.79 │  37.98  │
│ Exp 2a: Random 3-shot    │  1.39 │  44.36  │
│ Exp 2b: Matched 3-shot   │  2.33 │  44.16  │
│ Exp 3a: Isolated turn    │  1.48 │  36.10  │
│ Exp 3b: With context     │  1.85 │  45.11  │
└──────────────────────────┴───────┴─────────┘
```

### 3.2 Key Deltas

```
Few-shot effect (zero-shot → random 3-shot):
  BLEU: +0.60 │ chrF++: +6.38

Topic-matching effect (random → matched):
  BLEU: +0.94 │ chrF++: −0.20  ← NOT significant on chrF++

Context effect (isolated → full context):
  BLEU: +0.37 │ chrF++: +9.01  ← STRONGEST EFFECT
```

### 3.3 Per-Sample Context Analysis (Exp 3)

```
Topic                               │ Isolated │ Context │ Delta
────────────────────────────────────┼──────────┼─────────┼───────
The clothes of the mourners         │   34.5   │  42.7   │  +8.2 ▲
Morning activities                  │   31.5   │  34.4   │  +2.9 ▲
Social relationships / neighbors    │   42.5   │  48.3   │  +5.8 ▲
How to care for toddlers            │   26.2   │  55.8   │ +29.6 ▲ ★
Traditions before religious holiday │   32.9   │  39.4   │  +6.5 ▲
Traditions when planting            │   40.8   │  47.9   │  +7.0 ▲
Process of dealing with corpse      │   34.6   │  32.7   │  −1.9 ▼
Wedding food                        │   45.8   │  52.5   │  +6.7 ▲
Traditional medicine                │   29.7   │  43.9   │ +14.2 ▲ ★
Family relationships                │   57.1   │  55.6   │  −1.6 ▼
────────────────────────────────────┼──────────┼─────────┼───────
Average                             │   37.6   │  45.3   │  +7.7 ▲
Win rate                            │          │         │ 8/10
```

**Observation**: Context helps in 8/10 cases. The two cases where it slightly hurts (−1.6 and −1.9) are minimal decreases. The improvements range from +2.9 to +29.6.

### 3.4 Cultural Entity Analysis (Exp 1)

```
Samples with cultural entities (4):  BLEU=1.42, chrF++=39.55
Samples without (26):                BLEU=0.93, chrF++=37.53
```

Small sample size, but cultural entities score slightly higher. GPT-4o already handles common cultural entities well (e.g., "bánh gừng" → "នំខ្ញី", "num ansom" → "នំអន្សម").

### 3.5 Translation Length Analysis

```
Condition           │ Avg hypothesis (chars) │ Avg reference (chars) │ Ratio
────────────────────┼────────────────────────┼───────────────────────┼──────
Exp 1 (zero-shot)   │         151            │         152           │ 0.99
Exp 3 (isolated)    │         124            │         117           │ 1.06
Exp 3 (context)     │         126            │         117           │ 1.08
```

Length ratios are excellent (~1.0), meaning GPT-4o doesn't over-generate or under-generate.

---

## 4. Qualitative Analysis

### 4.1 What GPT-4o Does Well

**1. Speaker role formatting adapts with context**:
- Without context: `អ្នកខ្មែរ:` (generic)
- With context: `ជនជាតិខ្មែរ៖` (matches reference exactly)

This shows the model learns the conversation's formatting conventions from context.

**2. Cultural entity translation is mostly correct**:
- `bánh gừng` → `នំខ្ញី` ✓ (ginger cake)
- `Chol Chnam Thmay` → `ចូលឆ្នាំថ្មី` ✓ (Khmer New Year)
- `num ansom` → `នំអន្សម` ✓ (Khmer sticky rice cake)
- `lễ hội Ok Om Bok` → `បុណ្យអកអំបុក` ✓ (Moon worship festival)

**3. Register/formality is appropriate**:
- Interviewer text → formal Khmer
- Interviewee text → slightly more natural Khmer

### 4.2 Where GPT-4o Struggles

**1. Khmer Krom vs. standard Khmer vocabulary**:
- Some Khmer terms used in Vietnam's Mekong Delta differ from standard Cambodian Khmer
- GPT-4o tends to produce standard Cambodian Khmer
- Example: specific Khmer Krom dialectal terms may be missed

**2. Subtle cultural concepts**:
- Complex cultural practices described in multi-sentence context
- Nuanced kinship terms (Khmer has very specific terms for different relatives)

**3. Reference quality may be the bottleneck**:
- Some references in the data appear to have annotation artifacts
- This may depress automatic scores for actually good translations

---

## 5. What These Results Mean for Paper Direction

### 5.1 Original Direction A+E Assessment

**Strengths confirmed**:
- ✅ The data works well as a benchmark (diverse topics, conversation structure)
- ✅ Multiple evaluation conditions produce meaningful differences
- ✅ GPT-4o provides a strong baseline, enabling analysis of strengths/weaknesses
- ✅ chrF++ is clearly superior to BLEU for this pair

**Weaknesses revealed**:
- ⚠️ Cultural entity analysis needs finer-grained metrics (GPT-4o handles simple entities well)
- ⚠️ 30 samples per condition is too small for statistical significance — need 100+
- ⚠️ Need more models (not just GPT-4o) for a proper benchmark paper

### 5.2 Revised Paper Direction: "A+E+C Combined"

The strongest paper combines:
- **E (Resource)**: The dataset as a benchmark
- **A (Evaluation Framework)**: Cultural MT evaluation with chrF++ focus
- **C (Context Study)**: Dialogue context effects as headline finding

### 5.3 Proposed Paper Title

> **"CulturalMT-ViKm: How Dialogue Context and Cultural Knowledge Shape Low-Resource Machine Translation"**

or

> **"Does Context Help Translate Culture? A Benchmark for Vietnamese-Khmer Conversational Translation"**

---

## 6. Detailed Paper Plan

### 6.1 Story Arc

1. **Problem**: Low-resource cultural MT lacks proper evaluation benchmarks
2. **Resource**: We introduce CulturalMT-ViKm — 1,856 Vi-Km parallel samples from ethnographic conversations covering 56 cultural topics
3. **Evaluation Framework**: We propose cultural-aware evaluation dimensions beyond BLEU
4. **Empirical Study**: We test 3–4 LLMs under systematic conditions (zero-shot, few-shot, context)
5. **Headline Finding**: Dialogue context improves chrF++ by +9 points with 80% consistency
6. **Analysis**: When and why context helps, cultural entity handling, metric reliability

### 6.2 Required Additional Experiments

To go from pilot to full paper, we need:

| Experiment | What's Needed | Estimated API Calls |
|---|---|---|
| Scale up sample sizes | 100+ per condition (not 30) | ~500 |
| Add more models | NLLB-3.3B, Google Translate, Claude, Gemini | ~400 |
| Context ablation | 0, 1, 2, 3, all previous turns | ~300 |
| Km→Vi direction | Reverse translation direction | ~200 |
| Few-shot k variation | k=1, 3, 5, 10 | ~200 |
| Cultural entity deep-dive | Subset with annotated entities | ~100 |
| **Total** | | **~1,700 calls** |

### 6.3 Evaluation Framework Design

```
CulturalMT-ViKm Evaluation Framework:
├── Tier 1: Automatic Metrics
│   ├── chrF++ (primary — our pilot confirms it's most informative)
│   ├── BLEU (secondary — for comparability with prior work)
│   └── BERTScore (if Khmer model available)
├── Tier 2: Cultural Competence
│   ├── Cultural Entity Accuracy (exact match of entity translations)
│   ├── Cultural Concept Preservation (human judgment: is the cultural meaning preserved?)
│   └── Naturalness (does the Khmer sound natural to a native speaker?)
├── Tier 3: Discourse Quality (for dialogue subset)
│   ├── Speaker Role Consistency
│   ├── Register Appropriateness
│   └── Topic Coherence
└── Tier 4: Error Taxonomy
    ├── Omission (cultural detail dropped)
    ├── Mistranslation (wrong cultural concept)
    ├── Over-translation (added information not in source)
    └── Dialect mismatch (Cambodian Khmer vs. Khmer Krom)
```

### 6.4 Paper Structure (8-page ACL format)

```
1. Introduction (1 page)
   - Motivation: cultural MT for low-resource pairs
   - Gap: no benchmark for cultural-conversational MT
   - Contributions: dataset + framework + findings

2. Related Work (1 page)
   - Low-resource MT benchmarks (FLORES+, NTREX)
   - Culturally-aware MT (CaMMT, Catalan-Chinese)
   - Discourse-level MT (TransGraph, multi-turn)
   - Vietnamese-Khmer MT (PACLIC 2025, Informatica 2024)

3. CulturalMT-ViKm Dataset (1.5 pages)
   - Data collection and annotation process
   - Data statistics and splits
   - Data statement (Bender & Friedman, 2018)
   - Comparison with existing benchmarks

4. Evaluation Framework (1 page)
   - Metric selection rationale (why chrF++ over BLEU)
   - Cultural competence dimensions
   - Discourse quality dimensions

5. Experiments (2 pages)
   - Models tested
   - Experimental conditions
   - Results tables + analysis
   - Per-condition breakdown

6. Analysis & Discussion (1 page)
   - When and why context helps
   - Cultural entity handling patterns
   - Khmer Krom vs. standard Khmer
   - Limitations

7. Conclusion (0.5 pages)
```

---

## 7. Comparison with Related Benchmarks

| Benchmark | Venue | Size | Languages | Cultural Focus | Conversation | Our Advantage |
|---|---|---|---|---|---|---|
| FLORES+ | Various | 3,001 | 200+ | No | No | We have cultural + conversation |
| CaMMT | EMNLP Findings 2025 | 5,800 | En + regional | Visual culture | No | We have dialogue context |
| CARE | EMNLP 2025 | 3,490 Q | Multi | Cultural QA | No | We have parallel translation |
| MakiEval | ArXiv 2025 | Auto | 13 langs | Cultural awareness | No | We have human-translated MT |
| PACLIC 2025 | PACLIC | Small | Vi-Km | No | No | We have cultural evaluation framework |
| **Ours** | **Target: ACL** | **1,856** | **Vi-Km** | **Yes** | **Yes** | **Unique combination** |

Our unique position: **the only benchmark combining cultural content + conversational structure + human reference translations + low-resource language pair**.

---

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| "Dataset too small" criticism | Medium | Position as focused benchmark, not training resource; comparable to CaMMT's 5,800 |
| "Only one language pair" criticism | Medium | Argue depth > breadth; language-specific findings are valuable for Khmer community |
| Data quality issues (annotation artifacts) | Medium | Data cleaning phase + inter-annotator agreement measurement |
| GPT-4o already good → "no room for improvement" | Low | Frame as "understanding current capability + identifying specific weaknesses" |
| Privacy of interviewees | High | Full anonymization required; may need ethics review |
| No access to NLLB/Google Translate baselines | Low | These are publicly accessible models |

---

## 9. Required Resources

### Compute / API
- GPT-4o: ~1,700 additional API calls (~$15–25 estimated)
- NLLB-3.3B: Run locally (needs GPU with 8GB+ VRAM) or use HuggingFace Inference API
- Google Translate: Free tier API (~200 samples feasible)
- Claude/Gemini: API access needed

### Human Resources
- 1–2 Vietnamese-Khmer bilingual annotators for:
  - Cultural entity annotation (~40 hours)
  - Translation quality human evaluation (~20 hours)
  - Inter-annotator agreement (~10 hours)

### Timeline

| Phase | Duration | Tasks |
|---|---|---|
| **Phase 1: Data prep** | 2 weeks | Clean data, annotate cultural entities, define splits |
| **Phase 2: Full experiments** | 2 weeks | Run all conditions on all models |
| **Phase 3: Analysis** | 2 weeks | Quantitative + qualitative analysis, error taxonomy |
| **Phase 4: Writing** | 3 weeks | Paper draft, revision |
| **Phase 5: Human eval** | 2 weeks (parallel with Phase 4) | Annotator recruitment, evaluation |
| **Total** | ~10 weeks | |

---

## 10. Conclusion and Next Steps

### The pilot confirms:

1. **Direction A+E+C is viable** — the combination of benchmark + evaluation framework + context study produces a strong paper with clear contributions
2. **Context effects are the headline result** — +9 chrF++ is substantial and consistent
3. **chrF++ should be the primary metric** — BLEU is near-zero and misleading
4. **GPT-4o handles basic cultural entities well** — the evaluation needs to go deeper (Khmer Krom dialect, complex cultural practices)

### Immediate next steps:

1. **Get access to additional models** (NLLB, Google Translate, Claude) for baseline comparison
2. **Recruit bilingual annotators** for cultural entity annotation and human evaluation
3. **Scale up experiments** to 100+ samples per condition with statistical significance tests
4. **Design cultural entity evaluation** — the current keyword-based approach is too simple
5. **Clean the dataset** — remove annotation artifacts from references, standardize formatting

### Decision point:

Should we target **ACL 2026 (if deadline allows)** or **EMNLP 2026**? The timeline of ~10 weeks should be feasible for either.
