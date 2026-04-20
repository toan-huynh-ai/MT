# Source Collection Round 2

This note records additional high-quality sources collected on `2026-04-17` for expanding the Khmer Krom Cultural Knowledge Base. These sources are also registered in `kb_sources.json` so they can be cited later in a paper or dataset card.

## Selection principles

- Prefer **government**, **academic**, or **community authority** sources over generic blogs
- Prefer sources that provide at least one of:
  - Khmer script
  - bilingual Vi-Km terminology
  - historical etymology
  - ritual sequence / cultural explanations
- Keep **traceability**: every source has an ID in `kb_sources.json`

## New sources collected

| Source ID | Source | Type | Main value |
|---|---|---|---|
| `WIKI_KHMER_WEDDING` | Vietnamese Wikipedia page on Khmer wedding | Encyclopedia | Wedding mythological figures, ceremony names, ritual logic |
| `AN_GIANG_FUNERAL` | Academic article on Khmer funerals in An Giang | Academic article | Detailed funeral sequence, ritual objects, monks/Achar roles |
| `TRAVINH_NEAKTA` | Trà Vinh government page on Đom Lơng Néak Tà | Government | Néak Tà deity vocabulary, heritage recognition |
| `TRAVINH_OKOMBOK` | Trà Vinh government page on Ok Om Bok | Government | Official framing of moon worship festival |
| `TRAVINH_ROBAM` | Trà Vinh government page on rô-bam | Government | Performing arts terminology |
| `SOCTRANG_NGUAM` | Sóc Trăng government page on Nhạc Ngũ Âm | Government | Instrument usage contexts, heritage documentation |
| `SOCTRANG_GHENGO_EN` | Sóc Trăng English page on Ngo boat race | Government | English-aligned explanations for festival and boat race terms |
| `CEMA_KHMER` | Committee for Ethnic Minority Affairs page on Khmer people | Government | Ethnographic overview, wedding/clothing context |
| `CEMA_DONTA` | CEMA page on Sene Dolta | Government | Ancestor worship terminology and ritual sequence |
| `CEMA_DUKE` | CEMA page on Dù Kê | Government | Performing arts terminology |
| `VJOL_FUNERAL` | Journal article on Khmer funerals | Academic article | Credible source for funeral terminology |
| `PANGLOSS_VOCAB` | CNRS Pangloss Krom Khmer vocabulary | Academic corpus | Lexical verification, diachronic comparison |

## What each source is best for

### Weddings
- `WIKI_KHMER_WEDDING`
- `CEMA_KHMER`
- internal source: `DATA_MINING_20260417`

### Funerals
- `AN_GIANG_FUNERAL`
- `VJOL_FUNERAL`
- internal source: `DATA_MINING_20260417`

### Festivals
- `KKF_CULTURE`
- `TRAVINH_OKOMBOK`
- `TRAVINH_NEAKTA`
- `CEMA_DONTA`

### Performing arts / music
- `SOCTRANG_NGUAM`
- `TRAVINH_ROBAM`
- `CEMA_DUKE`
- `WIKI_PINPEAT`
- `SOUNDS_ANGKOR`

### Lexicon / language verification
- `PANGLOSS_VOCAB`
- `GLOSBE_KM_VI`
- `OMNIGLOT_KINSHIP`

### Toponyms / place names
- `KKF_GEO`
- `WIKI_SOC_TRANG`
- `WIKI_TRA_VINH`
- `WIKI_AN_GIANG`
- `PAGODA_ST`
- `PAGODA_AG`

## Recommended use policy

### Tier 1 — Ground truth
- `all_1.jsonl`
- `all_2.jsonl`
- `DATA_MINING_20260417`

These should dominate whenever they conflict with outside sources.

### Tier 2 — Authoritative expansion
- government portals
- KKF pages
- academic papers / corpora

These can be used to add new entries and metadata, especially for:
- toponyms
- pagodas
- ritual names
- performing arts

### Tier 3 — Dictionary cross-check
- Glosbe
- Omniglot

Useful for checking spelling and romanization, but not sufficient alone for Khmer Krom-specific claims.

## Immediate high-yield next mining targets

1. `AN_GIANG_FUNERAL`:
   mine structured ritual objects and sequence terms like `Kok salla`, `Apithom`, `Achirăng`, `Otarapa`, `Tean Kol`, `Tông Prôlưng`, `Chơng thúp`, `Slatho`, `Sbau phleang`, `oppaset`, `bonlesop`.

2. `WIKI_KHMER_WEDDING`:
   mine symbolic names and wedding mythology terms like `Preah Thong`, `Neang Neak`, `Apéahâpĭpéah Khmêr`, `chang dai`, ceremonial umbrellas, hair-cutting and blessing rites.

3. `PAGODA_AG`:
   extract the full 37 pagoda list from Tri Tôn / An Giang into a dedicated raw JSON, analogous to `data_pagodas_soctrang.json`.

4. `TRAVINH_*` pages:
   mine festival aliases and intangible heritage terminology, especially `Néak Tà`, `rô-bam`, and local framing of `Ok Om Bok`.

## Bottom line

The source pool is now strong enough for a publication-grade KB pipeline:

- **internal data mining** for authentic Khmer Krom usage
- **government + academic sources** for expansion and verification
- **structured citation file** (`kb_sources.json`) for reproducibility

This means future KB growth can stay scientifically defensible instead of becoming an untraceable glossary.
