# GPT-4o Failure Report on Culturally Rich Vi→Khmer Samples (N=50)

> Quick quantitative + qualitative report on GPT-4o's ability to preserve
> Vietnamese cultural meaning when translating to Khmer. Evidence comes from
> a controlled subsample of the 1,856-item benchmark.

## 1. Methodology

- **Data source**: `results/gpt4o_full_1856.json` (GPT-4o, `temperature=0.0`,
  plain zero-shot prompt, no retrieval).
- **Subsampling**: All 1,856 samples were scored with the CKB v3 cultural
  entity lookup. We kept only samples that contain at least one cultural
  entity (1,068 of 1,856), then sorted them by number of unique entities
  detected, and selected the **top-50 culturally richest**.
- **Average density**: `5.5` cultural entities per sample (min=4, max=10).
- **Metric source**: `eval_plain` from the full run — i.e. the same model
  output, same prompt, same evaluator pipeline (`evaluation_framework.py`).
- **"Fail" definitions**:
  - *Total fail* — `CuEA == 0.0`: every cultural entity in the source is
    wrong in the Khmer output.
  - *Major fail* — `CuEA < 0.5`: more than half of the cultural entities
    are wrong.
  - *Mild fail*  — `CuEA < 1.0`: at least one entity is wrong.
  - *Fully correct* — `CuEA == 1.0`: all entities match the reference Khmer
    form.

## 2. Quantitative results

| Metric | Value |
|---|---:|
| Samples evaluated | 50 |
| Avg cultural entities / sample | 5.5 |
| Avg CuEA (plain GPT-4o) | **0.347** |
| Avg chrF++ (plain GPT-4o) | 40.63 |

### Failure counts

| Category | Count | Rate |
|---|---:|---:|
| **Fully correct** (CuEA = 1.0) | 1 | **2%** |
| **Mild fail** (CuEA < 1.0)     | 49 | **98%** |
| **Major fail** (CuEA < 0.5)    | 26 | **52%** |
| **Total fail** (CuEA = 0.0)    | 15 | **30%** |

### Error-type distribution on the 50 samples

| Error type | Count |
|---|---:|
| `MISSING_OR_WRONG` | 165 |
| `UNTRANSLATED` | 4 |
| `FOREIGN_LEAK` | 2 |
| `VIETNAMESE_LEAK` | 1 |

**Interpretation.** Surface fluency (chrF++ = 40.63) looks "acceptable", but
cultural entity fidelity (CuEA = 0.35) is poor: on the most culturally
demanding 50 samples, **only 1 in 50 got every cultural entity right**, and
**3 out of 10 had every entity wrong**. The dominant error mode is not
script leak, but *silent substitution*: GPT-4o produces plausible-looking
Khmer while replacing a culturally specific term with a generic or incorrect
one.

## 3. Qualitative case studies

For each case we show the Vietnamese source, human Khmer reference, and
GPT-4o output. Mistranslated entities are listed with the expected Khmer.

### Case 1 — Food-term transliteration (`FOOD_TRANSLIT`)

> GPT-4o transliterates Vietnamese food names phonetically instead of
> producing the correct Khmer cultural name.

- **CuEA = 0.00**, chrF++ = 43.2, entities = 5

```
VI  : Bún Nước Lèo ... Cốm Dẹp ... Bánh Cống ...
REF : ... នំបញ្ចុកទឹកសម្ល ... អំបុក ... នំកប៉ុង ...
HYP : ... ប៊ុននឹកលេវ ... កូមដេប ... [phonetic guesses, not real Khmer]
```

Mistranslated entities:

| Vietnamese | Expected Khmer | GPT-4o produced |
|---|---|---|
| `cốm dẹp` | `អំបុក` | phonetic `កូមដេប` |
| `bún nước lèo` | `នំបញ្ចុកទឹកសម្ល` | phonetic `ប៊ុននឹកលេវ` |
| `bánh cống` | `នំកប៉ុង` | (rewritten, wrong term) |
| `lễ hội` | `ពិធីបុណ្យទាន` | `ពិធីបុណ្យ` (dropped `ទាន`, loses specificity) |

### Case 2 — Religious / ritual terminology gap (`RITUAL_GAP`)

> GPT-4o leaves romanized names, leaks Vietnamese, and miswrites Hindu
> Brahman terminology borrowed into Khmer.

- **CuEA = 0.00**, chrF++ = 28.2, entities = 7

```
VI  : Num Ansam (còn gọi là bánh Tét) và Kom (còn gọi là bánh ít) là
      hai loại bánh tượng trưng cho Dôni và linga của thần ISo trong
      tôn giáo Bà La Môn.
REF : នំអន្សម និង នំគម ... យោនី នាងឧមា និងលិង្គព្រះឥសូ ក្នុងសាសនាព្រាហ្មណ៍។
HYP : Num Ansam (ដែលគេហៅថា bánh Tét) និង Kom (ដែលគេហៅថា bánh ít) ...
      Dôni និង linga ... ព្រះ ISo ... សាសនាប្រាហ្មញ្ញ។
```

Leak evidence reported by the evaluator:
- `UNTRANSLATED` × 4 — `bánh tét`, `bánh ít`, `Num Ansam`, `Kom` are all left
  in Latin script in the Khmer output.
- `FOREIGN_LEAK` × 2 — `Bà La Môn`, `Dôni và linga` kept as source
  romanization.
- `VIETNAMESE_LEAK` × 1 — Vietnamese words retained inline.

### Case 3 — Krom-regional entity failure (`KROM_REGIONAL`)

> GPT-4o defaults to generic / standard Cambodian Khmer when the source
> mentions Khmer-Krom-specific community vocabulary.

- **CuEA = 0.33**, chrF++ = 40.1, entities = 6

```
VI  : Người Khmer: Thường cả phum sóc cùng tụ tập, dâng lễ vật đơn giản
      như gạo, trầu cau, nhang đèn, thể hiện lòng thành kính với Neak Ta.
REF : ជនជាតិខ្មែរ: ... ភូមិទាំងមូល ... ថ្វាយគ្រឿងសក្ការៈ ... ស្លាម្លូ ធូបទៀន ... ការគោរពដ៏ស្មោះចំពោះ​អ្នកតា។
HYP : ជនជាតិខ្មែរ: ... សហគមន៍ភូមិសង្កាត់ ... បូជាដោយប្រើសក្ការៈ ... ស្លឹកប៉ោម ស្ពាន់ និងទៀន ... អ្នកតា។
```

Mistranslated entities:

| Vietnamese | Expected Khmer | GPT-4o produced |
|---|---|---|
| `phum sóc` | `ភូមិសង្គម` (Krom community) | `ភូមិសង្កាត់` (administrative term) |
| `sóc` | `ស្រុក` (district) | absorbed into previous | 
| `lễ vật` | `គ្រឿងសក្ការៈ` | `សក្ការៈ` (incomplete) |
| `nhang đèn` | `ធូបទៀន` | `ស្ពាន់ និងទៀន` (*copper and candle* — wrong compound) |
| `trầu cau` | `ស្លាម្លូ` | `ស្លឹកប៉ោម` (*apple leaf* — hallucination) |

Note: the **semantic hallucination** on `trầu cau` → *apple leaf* is a
severe error that standard chrF++ barely penalizes (chrF++ is still 40.1).

### Case 4 — Complete knowledge collapse (`KNOWLEDGE_GAP`)

> On one very culturally dense sample, GPT-4o produces degenerate repetitive
> output — the model essentially gives up.

- **CuEA = 0.00**, chrF++ = 2.2, entities = 5

```
VI  : Khi đi làm rẫy, người Khmer mang theo cơm (với cá khô, ruốc),
      cá khô/mắm khô, trái cây và nước uống để ăn trưa...
REF : ... ពេលទៅស្រែចម្ការ ជនជាតិខ្មែរយកទៅជាមួយនូវ បាយ (ជាមួយត្រីងៀត ផ្អក) ...
HYP : ខ្មែរឃ្មែរឃ្មែរឃ្មែរឃ្មែរឃ្មែរឃ្មែរ... (repetition loop, ~200 tokens)
```

Mistranslated entities (model never produced correct Khmer for any of
them): `rẫy`, `mắm`, `trái cây`, `vớ`, `khấn nguyện`.

**Caveat for the report**: This degenerate-loop failure is a decoding
pathology, not a cultural fidelity issue per se. It should be reported as
*robustness failure on culturally dense long inputs*, not counted in the
same bucket as Case 1–3.

### Case 5 — Mixed failure on cultural food names with partial success (`MIXED_PARTIAL`)

> Even when GPT-4o gets some entities right, it still loses on the ones
> that are Krom-specific or require Vietnamese → Khmer back-mapping.

- **CuEA = 0.50**, chrF++ = 44.2, entities = 10

```
VI  : ...Lạp (Lap)... Cà Ri Khmer (Samlor Kari)... Num Ansam
      (Bánh Tét)... Bánh Ít... Bai Lam (Cơm Lam)...
REF : ...ឡាប ... សម្លការី ... នំអន្សម ... នំគម ... បាយឡាំ...
HYP : ...ឡាប (Lap)... សម្លការី... [bánh tét/bánh ít kept Vietnamese]
```

Mistranslated entities:

| Vietnamese | Expected Khmer | GPT-4o produced |
|---|---|---|
| `bánh tét` | `នំអន្សម` | kept Vietnamese |
| `tre` | `ឫស្សី` | (unchanged, wrong) |
| `rẫy` | `ចម្ការ` | `វាលស្រែ` (generic paddy) |
| `nước cốt dừa` | `ខ្ទិះដូង` | descriptive paraphrase |
| `khoai lang` | `ដំឡូងជ្វា` | wrong cultivar |

## 4. Takeaways for the paper

1. **98% of culture-rich samples contain at least one cultural entity
   error.** "Fully correct" is essentially a 2% event.
2. **The dominant failure mode is `MISSING_OR_WRONG` (165/172 of all
   errors, ≈ 96%).** Script leakage is rare — the problem is not Khmer
   generation, it is cultural knowledge.
3. **chrF++ systematically underestimates cultural failure.** Cases 1 and 3
   score chrF++ ≈ 40–43 but CuEA = 0 or 0.33. Reporting only surface
   metrics hides the cultural fidelity gap.
4. **Failure categories worth calling out separately**:
   - phonetic substitution (Case 1),
   - romanized-term retention + religious term gap (Case 2),
   - variety collapse on Krom-specific vocabulary (Case 3),
   - decoding degeneration on dense inputs (Case 4; this is a robustness
     issue, distinct from cultural failure),
   - partial-success cases where half the entities are still wrong (Case 5).
5. **Caveat on Khmer Krom**: cases like the `phum sóc` and `trầu cau`
   examples above do suggest variety collapse, but the reference side of
   the benchmark is itself partially standardized (see
   `08_khmer_diff.md`). The strongest honest claim is *GPT-4o is
   unreliable on culturally grounded Vietnamese→Khmer translation for
   Mekong-Delta Khmer community content*, not *GPT-4o cannot translate
   Khmer Krom*.

## 5. Files referenced

- `results/gpt4o_full_1856.json` — full run, source of truth.
- `results/top50_culture_rich.json` — the 50-sample subset used here.
- `eval/evaluation_framework.py` — metric definitions for CuEA and error
  taxonomy.
- `kb/cultural_kb_expanded.py` — the KB that drives the entity lookup.
