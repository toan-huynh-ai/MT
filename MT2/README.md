# Vietnamese–Khmer Cultural MT (MT2)

Reorganized workspace for the Vietnamese→Khmer cultural machine-translation
benchmark focused on Khmer communities in Vietnam's Mekong Delta.

This folder is a **curated reorganization** of `Learning/MT`. Intermediate
checkpoints, superseded CKB v1/v2 files, and `__pycache__` artifacts were
intentionally dropped. Only the canonical artifacts needed to reproduce and
understand the project are kept here.

## Where to start

1. Read [`docs/00_READING_GUIDE.md`](docs/00_READING_GUIDE.md) first. It
   explains the order in which the markdown reports should be read.
2. If you want the current story in one file, jump straight to
   [`docs/06_path_a_final_report.md`](docs/06_path_a_final_report.md).
3. If you want hard numbers, see [`results/`](results/).

## Folder layout

```
MT2/
|-- README.md                         <- you are here
|-- config.py                         <- Azure config shared by experiments
|-- data/                             <- parallel corpus + source registries
|   |-- all_1.jsonl                   <- 981 Vi-Khmer samples
|   |-- all_2.jsonl                   <- 875 Vi-Khmer samples
|   |-- kb_sources.json               <- external URL registry for the KB
|   `-- data_pagodas_soctrang.json    <- raw pagoda list from Soc Trang gov
|
|-- kb/                               <- Cultural Knowledge Base (CKB v3)
|   |-- cultural_kb_expanded.py       <- builder / lookup / RAG prompt builder
|   |-- cultural_knowledge_base_v3.json
|   `-- mine_entities.py              <- extract entity candidates from corpus
|
|-- eval/
|   `-- evaluation_framework.py       <- chrF++, BLEU, CuEA, Script Purity
|
|-- core/                             <- shared Azure client helpers
|
|-- experiments/
|   |-- gpt4o/                        <- Azure GPT-4o experiments
|   |   |-- experiment_pilot.py       <- pilot (zero-shot / few-shot / context)
|   |   |-- experiment_full.py        <- 40 culture-rich samples
|   |   |-- experiment_500.py         <- 500-sample stratified run
|   |   |-- experiment_all.py         <- full 1856 run (main)
|   |   `-- experiment_all_resume.py  <- resume helper for the full run
|   |
|   |-- local_models/                 <- runners for open-weight models
|   |   |-- run_aya_101.py
|   |   |-- run_nllb_50.py
|   |   |-- run_sealion_50.py
|   |   |-- run_gemma_sealion_9b_it.py
|   |   `-- run_sailor2_8b.py
|   |
|   |-- weakness/                     <- targeted weakness probes
|   |-- kb_rag/                       <- KB-RAG ablation
|   `-- analysis/                     <- result inspection scripts
|
|-- khmer2vi/                         <- reverse direction (Khmer -> Vi)
|-- scripts/                          <- .sh launchers for local-model runs
|
|-- results/                          <- curated final result JSONs
|   |-- gpt4o_full_1856.json          <- main GPT-4o run (plain + KB-RAG)
|   |-- gpt4o_cultural_40.json        <- culture-rich subset
|   |-- gpt4o_500.json                <- 500-sample run
|   |-- gpt4o_pilot.json              <- early pilot (zero/few-shot/context)
|   |-- aya101_full_1856.json
|   |-- nllb_full_1856.json
|   |-- nllb_50.json
|   |-- sealion_full_1856.json
|   |-- sealion_50.json
|   |-- gemma_sealion_full_1856.json
|   |-- sailor2_full_1856.json
|   |-- weakness_probe.json
|   |-- kb_rag_ablation.json
|   `-- mined_entities.json
|
`-- docs/                             <- all markdown reports (numbered)
    |-- 00_READING_GUIDE.md
    |-- 01_research_directions.md
    |-- 02_critique_and_revised_directions.md
    |-- 03_research_report_pilot.md
    |-- 04_gpt4o_weakness.md
    |-- 05_final_research_report.md
    |-- 06_path_a_final_report.md     <- current canonical summary
    |-- 07_new_weaknesses.md
    |-- 08_khmer_diff.md
    |-- 09_kb_potential_report.md
    |-- 10_contributions.md
    |-- 11_source_collection_round2.md
    |-- 12_dialogue_mt_overview.md
    `-- 13_km2vi_report.md
```

## What was intentionally dropped

- `experiment_results/checkpoint_*.json` and `*_checkpoint_latest.json`
  — intermediate dumps superseded by the corresponding `*_final_*.json`.
- `cultural_kb.py`, `cultural_knowledge_base.json`,
  `cultural_knowledge_base_v2.json` — superseded by CKB v3.
- Older duplicates such as `full_experiment_20260409_164322.json` and
  `exp500_final_20260417_173924.json`.
- `__pycache__/` and `.env`. Create your own `.env` with Azure credentials
  if you want to run experiments.
- `core/create_paramDB.py` — unrelated legacy script.

## Reproducing the main GPT-4o run

```powershell
# From MT2/
python experiments/gpt4o/experiment_all.py
```

The script reads `data/all_1.jsonl` and `data/all_2.jsonl`, looks up cultural
entities via `kb/cultural_kb_expanded.py`, evaluates with
`eval/evaluation_framework.py`, and writes the final JSON next to the run.

## Current headline findings (see `docs/06_path_a_final_report.md`)

- Models tested: GPT-4o, Aya-101, NLLB-200-3.3B, Gemma-SEA-LION-9B-IT,
  Llama-SEA-LION-8B-R, Sailor2-8B.
- On the full 1,856-sample benchmark, the best `avg_cuea` across all tested
  models is around 0.43 (GPT-4o). Cultural-entity fidelity is the weak
  point, not surface fluency.
- CKB-RAG lifts GPT-4o `avg_cuea` from 0.428 to 0.834 and reduces
  `MISSING_OR_WRONG` errors from 1052 to 286 on the full dataset.
- See `docs/08_khmer_diff.md` for the important caveat about how "Khmer Krom"
  the target side really is.
