# Reading Guide

The `.md` files in this folder are numbered by the order in which they were
written during the project. Reading them in numeric order walks you through
how the research evolved — from initial brainstorming, through a hard
self-critique, into the canonical story currently used for the paper.

## Fastest path (for a new reader)

If you only have 30 minutes, read in this order:

1. `06_path_a_final_report.md` — the most up-to-date self-contained summary.
2. `03_research_report_pilot.md` — where the core empirical findings first
   appear (context effect, BLEU collapse, etc.).
3. `04_gpt4o_weakness.md` — the six-category weakness taxonomy for GPT-4o.
4. `07_new_weaknesses.md` — refinements and self-critique of the weakness
   claims, including semantic hallucination.
5. `08_khmer_diff.md` — critical context on how Khmer Krom differs from
   Cambodian Khmer, and the caveats about how "Krom" our target side is.
6. `10_contributions.md` — how the above is packaged into paper
   contributions.

## Full chronological order

| # | File | Purpose |
|---|------|---------|
| 01 | `01_research_directions.md` | Initial 5 proposed research directions |
| 02 | `02_critique_and_revised_directions.md` | Data-grounded critique of 01 |
| 03 | `03_research_report_pilot.md` | Pilot report, GPT-4o, 30/15/10 samples |
| 04 | `04_gpt4o_weakness.md` | Evidence-based weakness catalogue |
| 05 | `05_final_research_report.md` | First consolidated story (pre-Path A) |
| 06 | `06_path_a_final_report.md` | Canonical summary with CKB v2 + CuEA |
| 07 | `07_new_weaknesses.md` | Refined weaknesses: hallucination, style |
| 08 | `08_khmer_diff.md` | Khmer Krom vs Khmer Cambodia analysis |
| 09 | `09_kb_potential_report.md` | External-source expansion potential |
| 10 | `10_contributions.md` | Paper contribution plan (C1-C10) |
| 11 | `11_source_collection_round2.md` | Second round of URL collection |
| 12 | `12_dialogue_mt_overview.md` | Framing as conversational MT |
| 13 | `13_km2vi_report.md` | Reverse-direction (Km->Vi) experiment notes |
| 14 | `14_gpt4o_failure_report_50samples.md` | Failure report on top-50 culture-rich samples |
| 15 | `15_bao_cao_3_lop_khmer.md` | Three-layer Khmer taxonomy + topic stats + 25 clean vs 25 culture-fail samples |

## Files that are historically useful but NOT canonical

- `01_research_directions.md` — many proposals here were later rejected in
  `02_critique_and_revised_directions.md`. Do not quote directly.
- `05_final_research_report.md` — despite the word "final", this was
  superseded by `06_path_a_final_report.md`. Keep for diffing claims
  across versions.

## Files that are canonical and safe to quote

- `06_path_a_final_report.md`
- `08_khmer_diff.md`
- `04_gpt4o_weakness.md` and `07_new_weaknesses.md` (taken together)
- `10_contributions.md`

## A note on claims

Be careful with the phrase "Khmer Krom benchmark". As analysed in
`08_khmer_diff.md`, the target side of our parallel corpus is best described
as **Khmer written by Khmer-Vietnamese annotators about Mekong Delta cultural
content**, with some Krom-flavoured lexical choices but a largely
standardized written form. See that file for exact lexical counts (`mǎi` /
`ba` / `ot` / `cheng` vs `moeday` / `ou-puk` / `min`) before making strong
claims about dialect.
