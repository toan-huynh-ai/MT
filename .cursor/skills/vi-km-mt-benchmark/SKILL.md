---
name: vi-km-mt-benchmark
description: Research Vietnamese-Khmer cultural machine translation and benchmark LLMs. Use when running Vi-Km translation experiments, building or querying the Cultural Knowledge Base (CKB v2), evaluating with CuEA/Script Purity metrics, analyzing LLM weaknesses, extending the A/B/C taxonomy, designing new experiments, or writing the research paper. Covers Khmer Krom dialect, CKB-RAG, dialogue context effects, multi-model benchmarking, and the CulturalEval framework.
---

# Vietnamese-Khmer Cultural MT Benchmark

## Project Overview

Research project benchmarking LLM cultural competence on Vietnamese-Khmer translation, focusing on **Khmer Krom** (ខ្មែរក្រោម — the Khmer variety spoken in Vietnam's Mekong Delta, ~1.3M speakers) — distinct from Cambodian Standard Khmer.

**Paper target**: ACL 2026 / EMNLP 2026
**Working title**: "CulturalMT-ViKm: A Benchmark and Cultural Knowledge Base for Vietnamese-Khmer Conversational Translation"
**Current phase**: Core experiments done. Next: multi-model + human evaluation.

---

## Critical Domain Knowledge

### Khmer Krom ≠ Cambodian Khmer

All existing MT resources (FLORES, NLLB, Google Translate) target **Cambodian Standard Khmer**. Our data is **Khmer Krom** — this is the core research gap.

| Aspect | Cambodian Khmer | Khmer Krom (our data) |
|---|---|---|
| NLP resources | FLORES, NLLB, Google | Nearly none → our contribution |
| Vocabulary | Standard | Vietnamese loanwords mixed in |
| Admin terms | Cambodian native | Phonetic from Vietnamese (e.g., "Ủy ban nhân dân" → "អ៊ុយបានប្រជាជន") |
| Food terms | Cambodian names | Mekong Delta-specific (e.g., "cốm dẹp" = "អំបុក") |
| Formality | ចាស (standard) | ចា៎ (Krom colloquial marker) |
| Speakers | ~16M (Cambodia) | ~1.3M (Vietnam) |
| LLM support | Moderate | Very poor (proven experimentally) |

When generating translations or evaluating output, **always prefer Khmer Krom terms** from the CKB over standard Cambodian Khmer.

### A/B/C Linguistic Taxonomy of Khmer Krom MT Challenges

This is a key paper contribution. Every cultural entity falls into one of:

- **Group A — Vietnamese-Khmer Loanwords** (Từ mượn Việt hóa): Words with Khmer origin now written in Vietnamese. Need etymological mapping back to Khmer script. Example: "mắm bò hóc" → ម៉ាំប្រហុក, "ghe ngo" → ទូកអុំ
- **Group B — Romanized Khmer** (Latin hóa tiếng Khmer): Khmer terms written in Latin script (no keyboard, social media). Need back-transliteration. Example: "Num Ansam" → នំអន្សម, "Ok Om Bok" → អកអំបុក
- **Group C — Vietnamized Toponyms** (Địa danh Việt hóa): Khmer place names phonetically adapted to Vietnamese. Do NOT translate literally. Example: "Sóc Trăng" → ខេត្តឃ្លាំង (Srok Khleang), "Trà Vinh" → ព្រះត្រពាំង (Preah Trapeang)

### Six GPT-4o Weakness Categories (Proven Experimentally)

1. **Food term transliteration** [CRITICAL] — phonetic guess instead of correct Khmer (e.g., cốm dẹp → "Kom Dêp" instead of អំបុក)
2. **Foreign script leakage** [CRITICAL] — Chinese chars (拜寺) or Vietnamese text ("bánh Tét") in Khmer output
3. **Religious/ritual term gaps** [HIGH] — terms left romanized or Chinese script leaked (戒律 instead of សមាទានសីល)
4. **Khmer Krom dialect mismatch** [HIGH] — standard Cambodian Khmer instead of Krom variety
5. **Complex sentence errors** [HIGH] — structural errors, cultural flattening (chrF++ 36.36)
6. **Kinship term specificity** [MEDIUM] — generic terms instead of specific Khmer kinship vocabulary

---

## Project Structure

```
MT/
├── .env                               # Azure OpenAI credentials (NEVER commit)
├── all_1.jsonl, all_2.jsonl           # Parallel data (1,856 samples total)
├── config.py                          # Azure/project config
├── core/                              # Shared clients
│   ├── auth.py
│   ├── azure_client.py
│   └── embeddings.py
│
├── ── CKB & EVALUATION ──
├── cultural_kb_expanded.py            # ★ CKB v2: 132 entries, A/B/C taxonomy
├── cultural_knowledge_base_v2.json    # ★ Exported CKB v2 (JSON)
├── evaluation_framework.py            # ★ CuEA + Script Purity implementation
├── cultural_kb.py                     # CKB v1 (53 entries, superseded by v2)
├── cultural_knowledge_base.json       # CKB v1 export (legacy)
│
├── ── EXPERIMENTS ──
├── experiment_full.py                 # ★ Full exp: 40 cultural samples, KB-RAG
├── experiment_pilot.py                # Pilot: zero-shot, few-shot, context
├── find_weaknesses.py                 # 6 weakness probes (48 samples)
├── test_kb_rag.py                     # KB-RAG v1 ablation (6 samples)
├── analyze_results.py                 # Pilot results analysis
├── analyze_weaknesses.py              # Weakness probe analysis
│
├── ── RESULTS ──
├── experiment_results/
│   ├── full_experiment_20260409_164322.json   # ★ Main results (40 samples)
│   ├── pilot_results_20260408_154436.json
│   ├── weakness_probe_20260408_163922.json
│   └── kb_rag_results.json
│
├── ── REPORTS & DOCS ──
├── PATH_A_FINAL_REPORT.md             # ★ Latest comprehensive report
├── FINAL_RESEARCH_REPORT.md           # Previous full report
├── GPT4o_WEAKNESS_REPORT.md           # Weakness catalog
├── contributions.md                   # Paper contribution plan (C1-C10)
├── khmer_diff.md                      # Khmer Cambodia vs Krom analysis
├── critique_and_revised_directions.md # Self-critique of 5 directions
└── research_directions.md             # Original 5 proposed directions
```

---

## Data Schema

Each sample in `all_1.jsonl` / `all_2.jsonl`:

```json
{
  "id": 71645,
  "text": "Vietnamese source text",
  "question": "Optional Vietnamese question (QA format only)",
  "label": ["Khmer translation 1", "Khmer translation 2 with *** annotations"],
  "Comments": [],
  "topic": "Topic name (dialogue format only)",
  "order": 1.0
}
```

- **QA format**: 352 samples (19%) — `question` present, no `topic`
- **Dialogue format**: 1,504 samples (81%) — `topic` present, grouped by `id` + `order`
- **Multi-reference**: 145 samples (7.8%) have 2+ translations
- **Alignment annotations**: `word *** ពាក្យ` pairs in labels (92 pairs total, 58 clean)
- **Topics**: 56 unique topics, 450 conversations, avg 3.3 turns/conversation

---

## Running Experiments

### Prerequisites

```bash
pip install openai azure-identity httpx sacrebleu python-dotenv
```

### Azure Client Pattern (Corporate proxy workaround — use everywhere)

```python
import httpx
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

http_client = httpx.Client(verify=False, proxy=os.getenv("HTTPS_PROXY"))
credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("APPLICATION_AI_VOS_USERS_ID"),
    client_secret=os.getenv("APPLICATION_AI_VOS_USERS_SECRET"),
    connection_verify=False,
)
token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_ad_token_provider=token_provider,
    http_client=http_client,
)
```

### Experiment Catalog

| Script | What it does | Time | Key results |
|---|---|---|---|
| `experiment_full.py` | 40 cultural samples, plain vs KB-RAG | ~45 min | **Main paper results** |
| `experiment_pilot.py` | Zero-shot, few-shot, dialogue context | ~30 min | Pilot baselines |
| `find_weaknesses.py` | 6 targeted probes + back-translation | ~20 min | Weakness evidence |
| `test_kb_rag.py` | CKB-RAG v1 on 6 known-fail samples | ~5 min | Entity fix proof |
| `cultural_kb_expanded.py` | Build/export CKB v2, lookup, RAG context | instant | Run standalone |
| `evaluation_framework.py` | CuEA + Script Purity demo | instant | Metric validation |

```powershell
cd C:\Users\HOY9HC\Desktop\Code\Learning\MT
python experiment_full.py        # ★ Main experiment
python experiment_pilot.py       # Pilot (context, few-shot)
python find_weaknesses.py        # Weakness probes
python cultural_kb_expanded.py   # Build/verify CKB v2
```

---

## Evaluation Metrics

### Standard Metrics
- **BLEU** via sacrebleu — near-zero for Vi→Km (different scripts, expected — do NOT treat as bug)
- **chrF++** via sacrebleu — **primary standard metric** (character-level, script-agnostic)

### Cultural Metrics (our contribution, implemented in `evaluation_framework.py`)

**CuEA (Cultural Entity Accuracy)**:
```python
from evaluation_framework import compute_cuea
result = compute_cuea(source_vi, hypothesis_km, reference_km)
# Returns: {"cuea": 0.937, "n_entities": 8, "n_correct": 7, "details": [...]}
```
- 0 = all cultural entities wrong, 1 = all correct
- Only computed for samples that contain CKB entities

**Script Purity Score**:
```python
from evaluation_framework import compute_script_purity
result = compute_script_purity(hypothesis_km)
# Returns: {"purity": 0.913, "is_pure": False, "n_chinese_chars": 2, ...}
```
- Detects Chinese (拜寺), Vietnamese, or Latin characters leaked into Khmer output

**Full evaluation**:
```python
from evaluation_framework import classify_errors
result = classify_errors(source_vi, hypothesis_km, reference_km)
# Returns: standard_metrics + cuea + script_purity + error_taxonomy
```

### Error Taxonomy (from `classify_errors`)
- `MISSING_OR_WRONG` — entity not found or wrong Khmer term
- `UNTRANSLATED` — Vietnamese text left in Khmer output
- `FOREIGN_LEAK` — non-Khmer script in output
- `ROMANIZED_LEFT` — Khmer term left in Latin romanization
- `CHINESE_LEAK` / `VIETNAMESE_LEAK` — specific script leak types

---

## All Experimental Results Snapshot

```
┌───────────────────────────────────────┬───────┬─────────┬────────┐
│ Condition                             │ BLEU  │ chrF++  │ CuEA   │
├───────────────────────────────────────┼───────┼─────────┼────────┤
│ Zero-shot GPT-4o (general)            │  0.79 │  37.98  │   —    │
│ Zero-shot GPT-4o (cultural samples)   │  2.67 │  38.64  │  0.419 │
│ Random 3-shot                         │  1.39 │  44.36  │   —    │
│ Topic-matched 3-shot                  │  2.33 │  44.16  │   —    │
│ Full dialogue context                 │  1.85 │  45.11  │   —    │
│ CKB-RAG v2 (40 cultural samples)      │  1.76 │  41.02  │  0.937 │
├───────────────────────────────────────┼───────┼─────────┼────────┤
│ CKB-RAG delta                         │       │  +2.38  │ +0.518 │
│ CKB error reduction                   │       │         │  86%   │
│ chrF++ win rate (context)             │       │ 8/10    │        │
│ CuEA win rate (CKB)                   │       │ 32/40   │        │
└───────────────────────────────────────┴───────┴─────────┴────────┘

Weakness probes (chrF++, weakest first):
  Complex sentences   36.36
  Kinship terms       37.43
  Colloquial speech   38.76
  Food/cuisine        39.46
  Religious/ritual    43.13
  Khmer Krom regional 44.27
```

**Key insight**: CuEA jumps from 0.419 → 0.937 with CKB-RAG. chrF++ only improves +2.38 because it measures the whole sentence, but CuEA measures specifically whether cultural entities were correctly translated. This is why standard metrics are insufficient.

---

## Cultural Knowledge Base (CKB v2)

**132 entries** across 3 linguistic groups + 9 semantic categories.
**Active file**: `cultural_kb_expanded.py`

```
Group A (Loanwords):  67 entries  — need etymological mapping
Group B (Romanized):  46 entries  — need back-transliteration
Group C (Toponyms):   19 entries  — do NOT translate literally
```

### Usage

```python
from cultural_kb_expanded import lookup, build_rag_context

# Find entities in Vietnamese text
entities = lookup("Tôi làm cốm dẹp cho lễ Ok Om Bok tại Tri Tôn")
# Returns: [{vi: "cốm dẹp", km: "អំបុក", group: "A", category: "food"}, ...]

# Generate RAG context for translation prompt
rag_text = build_rag_context("Tôi làm cốm dẹp cho lễ Ok Om Bok tại Tri Tôn")
# Returns: "Cultural terminology reference (Khmer Krom dialect):\n  'cốm dẹp' → 'អំបុក' ..."
```

### CKB Categories Quick Reference

| Category | Count | Key examples |
|---|---|---|
| food | 20 | cốm dẹp→អំបុក, bánh tét→នំអន្សម, mắm bò hóc→ម៉ាំប្រហុក |
| religious | 18 | chùa→វត្ត, Sư→ព្រះសង្ឃ, tắm Phật→ស្រង់ព្រះ |
| toponyms | 18 | Sóc Trăng→ខេត្តឃ្លាំង, Trà Vinh→ព្រះត្រពាំង, Tri Tôn→ស្រុកបាយ៉ង់ |
| romanized | 24 | Chol Chnam Thmay→ចូលឆ្នាំថ្មី, Ok Om Bok→អកអំបុក |
| kinship | 11 | bác→ធំ, cô→មីង, bà ngoại→យាយ |
| cultural_practices | 11 | phum sóc→ភូមិសង្គម, rong vong→រាំវង់ |
| agriculture | 6 | lúa mùa nổi→ស្រូវវស្សាអណ្ដែត, tre→ឫស្សី |
| festivals | 7 | Kathina→កឋិនទាន, Sene Dolta→សែនដូនតា |
| music_arts | 4 | Dù Kê→យីកេ, Ngũ Âm→ពិណពាទ្យ |

---

## Paper Contributions (C1–C10)

| # | Contribution | Evidence | Status |
|---|---|---|---|
| **C1** | CulturalMT-ViKm benchmark (1,856 samples, 56 topics) | Dataset | **Done** |
| **C2** | A/B/C linguistic taxonomy of Khmer Krom MT challenges | CKB v2, 132 entries | **Done** |
| **C3** | 6-category GPT-4o weakness taxonomy | 48 probe samples | **Done** |
| **C4** | CKB v2 + RAG → CuEA 0.419→0.937, 86% error reduction | 40-sample exp | **Done** |
| **C5** | Dialogue context → +9.0 chrF++, 80% win rate | 10 conversations | **Done** |
| **C6** | CuEA + Script Purity metrics (CulturalEval framework) | Implemented | **Done** |
| **C7** | BLEU≈0 for Vi-Km; CuEA catches what chrF++ misses | All experiments | **Done** |
| **C8** | Multi-model comparison (NLLB, Google Translate, Claude) | TODO | **MUST** |
| **C9** | Human evaluation (2 Krom annotators, 100 samples) | TODO | **MUST** |
| **C10** | Public release: dataset + CKB on HuggingFace | TODO | **SHOULD** |

---

## Workflows

### Adding a New Model to the Benchmark

1. Create `experiment_<model>.py` following `experiment_full.py` pattern
2. Implement the model's API client
3. Run same conditions: zero-shot, CKB-RAG, dialogue context
4. Use `evaluation_framework.py` for consistent metrics (CuEA, Script Purity)
5. Save to `experiment_results/` with model name in filename
6. Update results table in `PATH_A_FINAL_REPORT.md`

### Extending the CKB

1. Identify new entities from experiment errors or data analysis
2. Classify as Group A (loanword), B (romanized), or C (toponym)
3. Add to appropriate section in `cultural_kb_expanded.py`
4. For Krom-specific terms: add `km_cambodia` field to note the difference
5. Run `python cultural_kb_expanded.py` to verify
6. Re-run `experiment_full.py` to measure impact on CuEA

### KB Entry Schema

```python
# Cultural entity (Group A or B)
{"vi": "cốm dẹp", "km": "អំបុក", "km_romanized": "ambok",
 "context": "Flattened rice, used in Ok Om Bok festival",
 "group": "A",  # A=loanword, B=romanized, C=toponym
 "km_cambodia": "optional_cambodia_variant"}  # if differs from Krom

# Toponym (Group C)
{"vi": "Sóc Trăng", "km": "ខេត្តឃ្លាំង", "km_original": "Srok Khleang",
 "meaning": "Land of depositories/silver storage",
 "type": "province",
 "note": "Sốc Kha Lang → Sóc Trăng (Vietnamese phonetic)"}
```

---

## Key Design Decisions

- **No model training** — data too small (1,856 samples); benchmark/evaluation paper
- **BLEU ≈ 0 is expected** — different scripts; chrF++ is primary standard metric
- **CuEA is the headline metric** — captures cultural entity accuracy that chrF++ misses
- **CKB v2 is the active KB** — supersedes `cultural_kb.py` (v1, 53 entries)
- **Azure OpenAI via service principal** — corporate env, SSL verify=False required
- **Khmer Krom focus** — not general Khmer; the dialect distinction is the novelty
- **UTF-8 reconfigure** — always needed for Khmer/Vietnamese on Windows stdout
- **Data-First KB strategy** — our data = ground truth; external sources = verification only

---

## Additional Resources

- Full experimental evidence and paper strategy: [reference.md](reference.md)
