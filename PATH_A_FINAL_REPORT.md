# Path A Final Report — CulturalMT-ViKm

**Date**: April 9, 2026
**Status**: Core experiments complete, ready for scale-up

---

## 1. What Was Built (Path A — Complete)

| Component | File | Status |
|---|---|---|
| **CKB v2** (132 entries, A/B/C taxonomy) | `cultural_kb_expanded.py` | Done |
| **CulturalEval Framework** (CuEA + Script Purity) | `evaluation_framework.py` | Done |
| **Full Experiment** (40 cultural samples, GPT-4o) | `experiment_full.py` | Done |
| **Exported KB** (JSON) | `cultural_knowledge_base_v2.json` | Done |
| **Pilot experiments** (30+15+10 samples) | `experiment_pilot.py` | Done |
| **Weakness probes** (6 probes, 48 samples) | `find_weaknesses.py` | Done |
| **KB-RAG v1 test** (6 critical samples) | `test_kb_rag.py` | Done |

---

## 2. CKB v2 — 132 Entries with A/B/C Taxonomy

```
Group A (Loanwords — Từ mượn Việt hóa):         67 entries
Group B (Romanized Khmer — Latin hóa):            46 entries
Group C (Vietnamized Toponyms — Địa danh Việt hóa): 19 entries
────────────────────────────────────────────────────────────
Total:                                           132 entries

By category:
  food                       20
  religious                  18
  toponyms                   18
  romanized backlit          24
  kinship                    11
  cultural_practices         11
  admin_loanwords             9
  festivals                   7
  agriculture                 6
  music_arts                  4
  clothing                    2
  transport                   2
```

---

## 3. Key Experimental Results (40 samples, GPT-4o)

### Main Results Table

```
┌─────────────────────┬──────────┬──────────┬──────────┐
│ Metric              │  Plain   │  KB-RAG  │  Delta   │
├─────────────────────┼──────────┼──────────┼──────────┤
│ chrF++              │  38.64   │  41.02   │  +2.38   │
│ CuEA ★              │   0.419  │   0.937  │ +0.518   │
│ Script Purity       │   0.989  │   0.993  │ +0.003   │
├─────────────────────┼──────────┼──────────┼──────────┤
│ chrF++ win rate     │          │ 30/40 (75%)          │
│ CuEA win rate       │          │ 32/40 (80%)          │
└─────────────────────┴──────────┴──────────┴──────────┘
★ CuEA (Cultural Entity Accuracy): 0=all entities wrong, 1=all correct
```

### Error Reduction

```
┌───────────────────────┬──────────┬──────────┬────────────┐
│ Error Type            │  Plain   │  KB-RAG  │ Reduction  │
├───────────────────────┼──────────┼──────────┼────────────┤
│ MISSING_OR_WRONG      │    74    │    10    │    86%     │
│ UNTRANSLATED          │     7    │     0    │   100%     │
│ FOREIGN_LEAK          │     4    │     0    │   100%     │
│ VIETNAMESE_LEAK       │     2    │     1    │    50%     │
├───────────────────────┼──────────┼──────────┼────────────┤
│ Total errors          │    87    │    12    │    86%     │
└───────────────────────┴──────────┴──────────┴────────────┘
```

### What These Numbers Mean

**CuEA is the headline metric.** chrF++ improved modestly (+2.38) because the CKB fixes specific terms, not the entire sentence. But CuEA jumped from **0.419 → 0.937** — meaning GPT-4o went from getting only 42% of cultural entities correct to **94% correct** with KB-RAG.

**86% error reduction** across all categories. The CKB eliminated:
- 64 MISSING_OR_WRONG errors (entities GPT-4o couldn't translate)
- 7 UNTRANSLATED errors (Vietnamese left in Khmer output)
- 4 FOREIGN_LEAK errors (Chinese/other scripts leaked)

---

## 4. Combined Results (All Experiments)

```
┌───────────────────────────────────────┬───────┬─────────┬───────┐
│ Condition                             │ BLEU  │ chrF++  │ CuEA  │
├───────────────────────────────────────┼───────┼─────────┼───────┤
│ BASELINES                             │       │         │       │
│   Zero-shot GPT-4o (general)          │  0.79 │  37.98  │  —    │
│   Zero-shot GPT-4o (cultural samples) │  2.67 │  38.64  │ 0.419 │
├───────────────────────────────────────┼───────┼─────────┼───────┤
│ FEW-SHOT                              │       │         │       │
│   Random 3-shot                       │  1.39 │  44.36  │  —    │
│   Topic-matched 3-shot                │  2.33 │  44.16  │  —    │
├───────────────────────────────────────┼───────┼─────────┼───────┤
│ DIALOGUE CONTEXT                      │       │         │       │
│   Full context                        │  1.85 │  45.11  │  —    │
├───────────────────────────────────────┼───────┼─────────┼───────┤
│ CKB-RAG (v2, 132 entries)             │       │         │       │
│   On cultural samples (40)            │  1.76 │  41.02  │ 0.937 │
│   CuEA win rate                       │       │         │ 80%   │
│   Error reduction                     │       │         │ 86%   │
├───────────────────────────────────────┼───────┼─────────┼───────┤
│ WEAKNESS PROBES (by category)         │       │ chrF++  │       │
│   Complex sentences                   │       │  36.36  │       │
│   Kinship terminology                 │       │  37.43  │       │
│   Colloquial speech                   │       │  38.76  │       │
│   Food/cuisine terms                  │       │  39.46  │       │
│   Religious/ritual terms              │       │  43.13  │       │
│   Khmer Krom regional                 │       │  44.27  │       │
└───────────────────────────────────────┴───────┴─────────┴───────┘
```

---

## 5. Paper Contributions (Final)

| # | Contribution | Evidence | Novelty |
|---|---|---|---|
| **C1** | CulturalMT-ViKm benchmark (1,856 samples, 56 topics, Khmer Krom) | Dataset analysis | ★★★★ |
| **C2** | A/B/C Linguistic taxonomy of Khmer Krom MT challenges | 132 entries classified | ★★★★★ |
| **C3** | 6-category GPT-4o weakness taxonomy | 48 probe samples | ★★★★ |
| **C4** | CKB v2 + RAG → CuEA: 0.419 → 0.937, 86% error reduction | 40-sample experiment | ★★★★ |
| **C5** | Dialogue context → +9.0 chrF++, 80% win rate | 10 conversations | ★★★★ |
| **C6** | CuEA metric + Script Purity metric (evaluation framework) | Implemented + validated | ★★★★★ |
| **C7** | BLEU ≈ 0 for Vi-Km; chrF++ is primary; CuEA catches what chrF++ misses | All experiments | ★★★ |

---

## 6. Critical Insight: Why CuEA Matters

chrF++ improved only +2.38 points, which might seem modest. But CuEA tells a dramatically different story:

```
Example: "Người dân không làm cốm dẹp vào ngày thường"

Plain GPT-4o output:  "...អាហារកុមដេប..."  (phonetic "Kom Dêp")
KB-RAG output:        "...អំបុក..."          (correct: Ambok)
Reference:            "...អំបុក..."          (correct: Ambok)

chrF++ improvement: +5.7 points (modest — most of the sentence is correct)
CuEA improvement:   0.0 → 1.0 (dramatic — the cultural entity went from WRONG to CORRECT)
```

**This is exactly why standard metrics are insufficient for cultural MT.** A single wrong cultural entity might look like a small chrF++ difference, but it completely changes the cultural meaning. CuEA captures this.

---

## 7. What Remains for Full Paper

| Priority | Task | Effort | Impact |
|---|---|---|---|
| **MUST** | Add 2+ more models (NLLB, Google Translate) | 2 weeks | Proves findings are systemic |
| **MUST** | Human evaluation (2 Khmer Krom annotators) | 2-3 weeks | Required for A* venue |
| **MUST** | Scale up to 100+ samples per condition | 1 week | Statistical significance |
| **SHOULD** | Public release on HuggingFace | 1 week | Community impact |
| **SHOULD** | Expand CKB to 200+ entries with community input | Ongoing | Larger coverage |
| **COULD** | Back-transliteration module for Group B | 2 weeks | Technical contribution |

---

## 8. File Inventory

```
MT/
├── cultural_kb_expanded.py          # CKB v2: 132 entries, A/B/C taxonomy
├── cultural_knowledge_base_v2.json  # Exported CKB v2
├── evaluation_framework.py          # CuEA + Script Purity implementation
├── experiment_full.py               # Full experiment (40 samples, KB-RAG)
├── experiment_pilot.py              # Pilot experiments (3 conditions)
├── find_weaknesses.py               # 6 weakness probes
├── test_kb_rag.py                   # KB-RAG v1 ablation
├── cultural_kb.py                   # CKB v1 (53 entries, superseded)
├── analyze_results.py               # Pilot analysis
├── analyze_weaknesses.py            # Weakness analysis
├── experiment_results/
│   ├── full_experiment_20260409_164322.json    # ★ Main results
│   ├── pilot_results_20260408_154436.json
│   ├── weakness_probe_20260408_163922.json
│   └── kb_rag_results.json
├── research_directions.md           # Original directions
├── critique_and_revised_directions.md
├── contributions.md                 # Contribution plan
├── khmer_diff.md                    # Khmer Cambodia vs Krom
├── GPT4o_WEAKNESS_REPORT.md         # Weakness catalog
├── RESEARCH_REPORT.md               # Initial report
├── FINAL_RESEARCH_REPORT.md         # Previous full report
└── PATH_A_FINAL_REPORT.md           # ★ This file
```
