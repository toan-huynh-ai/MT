# Reference: Vi-Km Cultural MT Benchmark

## 1. Complete Experimental Evidence

### Pilot Experiments (experiment_pilot.py)

**Exp 1 — Zero-shot Vi→Km** (30 samples):
- BLEU: 0.79, chrF++: 37.98
- Cultural entity samples (4): chrF++ 39.55
- Non-entity samples (26): chrF++ 37.53
- Finding: Cultural entity sentences ≈ same chrF++ but MUCH worse CuEA

**Exp 2 — Few-shot** (15 samples, k=3):
- Random 3-shot: BLEU 1.39, chrF++ 44.36
- Topic-matched 3-shot: BLEU 2.33, chrF++ 44.16
- **Finding**: Few-shot helps (+6 chrF++), but topic-matching ≈ random — any example helps

**Exp 3 — Dialogue context** (10 conversations):
- Isolated turn: BLEU 1.48, chrF++ 36.10
- With full context: BLEU 1.85, chrF++ 45.11
- **Finding**: Dialogue context = +9.01 chrF++, 8/10 win rate (LARGEST improvement)
- Per-sample range: +2.9 to +29.6 chrF++

### Weakness Probes (find_weaknesses.py)

6 probes × 8 samples each = 48 total:

| Probe | chrF++ | Observation |
|---|---|---|
| Complex sentences | 36.36 | WEAKEST — structural errors, cultural flattening |
| Kinship terminology | 37.43 | Generic terms used instead of specific Khmer kinship |
| Colloquial speech | 38.76 | Register mismatches |
| Food/cuisine terms | 39.46 | Transliteration of cultural food names |
| Religious/ritual terms | 43.13 | Partially correct — common terms OK, rare ones fail |
| Khmer Krom regional | 44.27 | STRONGEST despite dialect gap |

### KB-RAG v1 Ablation (test_kb_rag.py)

6 known-failure samples with CKB v1 (53 entries):

| Test Case | Plain | KB-RAG | Delta | Entities Fixed |
|---|---|---|---|---|
| cốm dẹp (flattened rice) | 39.7 | 52.3 | +12.6 | ✓ អំបុក |
| bánh ống tre + Kathina | 42.6 | 52.6 | +10.0 | ✓ នំបំពង់ឫស្សី ✓ កឋិនទាន |
| bánh tét + festivals | 41.4 | 41.2 | -0.2 | ✓ នំអន្សម |
| Religious terms (chùa, tụng kinh, cúng dường) | 37.8 | 49.5 | +11.7 | ✓ ថ្វាយ |
| Neak Ta + phum sóc | 36.1 | 32.4 | -3.7 | ✓ entities but sentence worse |
| Mixed religious + food (Bà La Môn) | 16.7 | 27.0 | +10.3 | ✓ នំអន្សម ✓ នំគម ✓ ព្រាហ្មណ៍ |

Corpus: Plain 33.66 → KB-RAG 40.46 (+6.80 chrF++), 11/13 entities fixed

### Full Experiment with CKB v2 + CulturalEval (experiment_full.py)

**40 samples** (culturally rich, selected by entity count), CKB v2 (132 entries):

| Metric | Plain (GPT-4o) | KB-RAG (GPT-4o + CKB v2) | Delta |
|---|---|---|---|
| chrF++ | 38.64 | 41.02 | **+2.38** |
| BLEU | 2.67 | 1.76 | -0.91 |
| **CuEA** | **0.419** | **0.937** | **+0.518** |
| Script Purity | 0.989 | 0.993 | +0.003 |
| chrF++ win rate | | 30/40 (75%) | |
| CuEA win rate | | 32/40 (80%) | |

Error reduction:

| Error Type | Plain | KB-RAG | Reduction |
|---|---|---|---|
| MISSING_OR_WRONG | 74 | 10 | **86%** |
| UNTRANSLATED | 7 | 0 | **100%** |
| FOREIGN_LEAK | 4 | 0 | **100%** |
| VIETNAMESE_LEAK | 2 | 1 | 50% |
| **Total** | **87** | **12** | **86%** |

**Key insight**: chrF++ only +2.38 (modest) but CuEA +0.518 (dramatic). This proves standard metrics are insufficient for cultural MT. CuEA captures entity-level accuracy that chrF++ misses.

---

## 2. Khmer Krom Dialect: Detailed Analysis

### A/B/C Taxonomy with Examples

**Group A — Loanwords (Từ mượn Việt hóa)**

Vietnamese borrowed Khmer words + wrote in Vietnamese phonetics. Must map to Khmer script:

| Vietnamese | Khmer Krom | Cambodian Khmer | Note |
|---|---|---|---|
| mắm bò hóc | ម៉ាំប្រហុក | ប្រហុក | Same concept, different Vietnamese phonetic |
| cốm dẹp | អំបុក | (same) | GPT-4o transliterates to "Kom Dêp" — wrong |
| ghe ngo | ទូកអុំ | N/A | Racing boat unique to Krom |
| xà rông | សំពត់ចង | (same) | Sarong — Khmer origin word |

**Group B — Romanized Khmer (Latin hóa tiếng Khmer)**

Khmer written in Latin because no keyboard. Back-transliterate to Khmer:

| Romanized | Khmer Script | GPT-4o Behavior |
|---|---|---|
| Chol Chnam Thmay | ចូលឆ្នាំថ្មី | Usually correct |
| Ok Om Bok | អកអំបុក | Usually correct |
| Num Ansam | នំអន្សម | Sometimes left romanized |
| Kathina | កឋិនទាន | Often left as "Kathina" — wrong |
| Neak Ta | អ្នកតា | Often transliterated as "នាគតា" — wrong |

**Group C — Vietnamized Toponyms (Địa danh Việt hóa)**

DO NOT translate these literally. Map to original Khmer place names:

| Vietnamese | Khmer Krom | Meaning | GPT-4o Error |
|---|---|---|---|
| Sóc Trăng | ខេត្តឃ្លាំង (Srok Khleang) | Land of depositories | Phonetic: ស្រុក ហ *** |
| Trà Vinh | ព្រះត្រពាំង (Preah Trapeang) | Sacred pond | Phonetic: ត្រាវ*** |
| Tri Tôn | ស្រុកបាយ៉ង់ (Srok Bayon) | Bayon district | Phonetic: ត្រីតោន (WRONG) |
| Châu Đốc | មាត់ជ្រូក (Moat Chrouk) | Pig's mouth | Usually omitted |
| Cà Mau | ខេត្តទឹកខ្មៅ (Tuk Khmau) | Black water | Phonetic |

### Administrative Loanwords (Khmer Krom-specific)

| Vietnamese | Khmer Krom | Cambodian Khmer |
|---|---|---|
| Ủy ban nhân dân | អ៊ុយបានប្រជាជន (phonetic) | គណៈកម្មាធិការប្រជាជន |
| Công an | កុងអាន (phonetic) | នគរបាល |

### Formality Markers

| Context | Khmer Krom | Cambodian Standard |
|---|---|---|
| Informal affirmative | ចា៎ | ចាស |
| Addressing interviewer | bong (បង) | typically neutral |
| Speaker label | ជនជាតិខ្មែរ៖ | varies |

GPT-4o always uses Cambodian standard → wrong for Krom context.

### KB Construction Strategy

```
Layer 1 (Primary — GROUND TRUTH):
  └── Our 1,856 parallel samples
      ├── *** alignment pairs (58 extracted)
      ├── Multi-reference translations (145 samples)
      └── Topic-rich cultural context
      → NEVER override with external sources

Layer 2 (External — CROSS-CHECK only):
  └── Wikipedia, KKF website, government sources
      ├── Used for: toponyms, historical place names
      ├── Used for: spelling verification
      └── Must be validated against Layer 1
      → Can ADD new entries, cannot CHANGE existing

Layer 3 (Metadata — ENRICHMENT):
  └── km_cambodia field: "Standard Khmer: X, Khmer Krom: Y"
  └── group field: A / B / C
  └── note field: explain phonetic origin, usage context
```

---

## 3. CKB v2 Full Reference (132 entries)

### Food (20 entries)
- cốm dẹp → អំបុក [A] (flattened rice, Ok Om Bok festival)
- bánh gừng → នំខ្ញី [A] (ginger cake, weddings)
- bánh tét → នំអន្សម [B] (cylindrical sticky rice cake)
- bánh ít → នំគម [B] (pyramid sticky rice cake)
- bánh ống tre → នំបំពង់ឫស្សី [A] (bamboo tube cake)
- bún nước lèo → នំបញ្ចុកទឹកសម្ល [A] (Khmer rice noodle soup)
- Num banh chok → នំបញ្ចុក [B] (rice noodles)
- mắm bò hóc → ម៉ាំប្រហុក [A] (fermented fish paste)
- Pro-hốc → ប្រហុក [B] (fermented fish paste, alternate)
- canh Som-lo Co Cô → សម្លកកូរ [B] (traditional sour soup)
- Amok Trey → អាម៉ុកត្រី [B] (steamed fish curry in banana leaf)
- nùm bong klanh → នំបង់ខ្លាញ់ [B] (traditional Krom cake, unique to ĐBSCL)
- đường thốt nốt → ស្ករត្នោត [A] (palm sugar)
- lạp → ឡាប [B] (minced meat salad for ceremonies)
- cà ri Khmer → សម្លការី [A] (Khmer-style curry)
- bánh bí → នំល្ពៅ [A] (pumpkin cake)
- bánh lá dừa → នំស្លឹកដូង [A] (coconut leaf cake)
- xôi → បាយដំណើប [A] (sticky rice)
- canh chuối → សម្លចេក [A] (banana soup)
- cá kho nghệ → ត្រីខជាមួយរមៀត [A] (fish braised with turmeric)

### Festivals (7 entries)
- Chol Chnam Thmay → ចូលឆ្នាំថ្មី [B] (Khmer New Year, April)
- Ok Om Bok → អកអំបុក [B] (Moon Worship Festival)
- Sene Dolta / Sen Đônta → សែនដូនតា [B] (Ancestor Worship Festival)
- Kathina → កឋិនទាន [B] (Robe-offering ceremony)
- lễ tắm Phật → ពិធីស្រង់ព្រះ [A] (bathing Buddha ceremony)
- đua ghe ngo → ប្រណាំងទូកអុំ [A] (traditional boat racing, Ok Om Bok)

### Religious (18 entries)
- Sư → ព្រះសង្ឃ [A] (Buddhist monk, Theravada)
- Achar → អាចារ្យ [B] (lay religious leader)
- chùa → វត្ត [A] (Buddhist temple — center of Khmer community)
- tụng kinh → សូត្រមន្ត [A] (chanting scriptures)
- cúng dường → ថ្វាយ [A] (offerings to monks)
- xuất gia → បួស [A] (to ordain as monk)
- thọ giới → សមាទានសីល [A] (to take precepts — NOT 戒律!)
- Phật Thích Ca → ព្រះសម្មាសម្ពុទ្ធ [A] (Shakyamuni Buddha)
- tắm Phật → ស្រង់ព្រះ [A] (bathing Buddha statue ritual)
- đắp núi cát → ពូនភ្នំខ្សាច់ [A] (sand mountain merit-making)
- cầu siêu → បង្សុកូល [A] (funeral prayer ceremony)
- bùa hộ mệnh → ខ្សែបន្តោង [A] (protective amulet)
- Neak Ta → អ្នកតា [B] (village guardian spirit — NOT នាគតា)
- Bà La Môn → ព្រាហ្មណ៍ [A] (Brahmanism)
- nhang đèn → ធូបទៀន [A] (incense and candles)
- lễ vật → គ្រឿងសក្ការៈ [A] (ritual offerings)
- Dôni và linga / thần ISo → យោនី និងលិង្គ / ព្រះឥសូ [B] (Hindu symbols)

### Kinship (11 entries)
- ông ngoại → តា (ខាងម្ដាយ) [A] (maternal grandfather)
- bà ngoại → យាយ (ខាងម្ដាយ) [A] (maternal grandmother)
- bác → ធំ [A] (elder sibling of father — NOT generic ពូ)
- cô → មីង [A] (younger sister of father)
- chú → ពូ [A] (younger brother of father)
- dì → មីង [A] (sister of mother)
- dượng → ពូថ្លៃ [A] (husband of aunt)
- con dâu → កូនប្រសា [A] (daughter-in-law)
- con rể → កូនប្រសា [A] (son-in-law)
- thông gia → សំណាន់ជើង [A] (in-law relationship between families)
- hiếu hỉ → ពិធីសួរសុខទុក្ខ [A] (weddings and funerals generic term)

### Cultural Practices (11 entries)
- phum sóc → ភូមិសង្គម [C] (Krom-specific village/community)
- rong vong → រាំវង់ [B] (circle dance)
- nằm than → ដេកចង្ក្រានធ្យូង [A] (postpartum charcoal bed practice)
- Dù Kê → យីកេ/ល្ខោនបាសាក់ [B] (traditional Khmer theater)
- Ngũ Âm → ពិណពាទ្យ [B] (five-instrument ensemble)
- trống Sadăm → ស្គរសាដំ [B] (temple drum)
- mẫu hệ → មាតាធិបតេយ្យ [A] (matrilineal system)
- lễ cúng trăng → ពិធីសំពះព្រះខែ [A] (moon worship ceremony)
- gọi hồn → ហៅព្រលឹង [A] (soul-calling for newborns)
- nước ngũ hoa → ទឹកផ្កាប្រាំ [A] (five-flower water for blessings)

### Agriculture (6 entries)
- lúa mùa nổi → ស្រូវវស្សាអណ្ដែត [A] (floating rice, flood-adapted)
- cây thốt nốt → ដើមត្នោត [A] (toddy palm, Khmer symbol)
- tre → ឫស្សី [A] (bamboo)
- dừa → ដូង [A] (coconut palm)
- ruộng → ស្រែ [A] (rice paddy)
- rẫy → ចម្ការ [A] (upland field)

### Music & Arts (4 entries)
- hát đối đáp → ច្រៀងឆ្លើយឆ្លង [A] (call-and-response singing)
- truyện dân gian → រឿងប្រជាប្រិយ [A] (folk tales)
- thần thoại → ទេវកថា [A] (mythology)
- truyện cổ tích → រឿងនិទាន [A] (fairy tales)

### Toponyms — Group C (18 entries) — DO NOT TRANSLATE LITERALLY

| Vietnamese | Khmer | Original Name | Meaning |
|---|---|---|---|
| Sóc Trăng | ខេត្តឃ្លាំង | Srok Khleang | Land of silver storage |
| Trà Vinh | ព្រះត្រពាំង | Preah Trapeang | Sacred pond |
| An Giang | ខេត្តអាងគាង | Ang Kiang | Peaceful river |
| Kiên Giang | ខេត្តព្រះត្រពាំង | — | — |
| Bạc Liêu | ខេត្តពោធិ៍សាត់ | Pothisat Krom | South Pursat |
| Cà Mau | ខេត្តទឹកខ្មៅ | Tuk Khmau | Black water |
| Châu Đốc | មាត់ជ្រូក | Moat Chrouk | Pig's mouth |
| Sa Đéc | ផ្សារដែក | Psar Dèk | Iron market |
| Hà Tiên | ពាម | Peam | River mouth |
| Cần Thơ | ព្រែកឫស្សី | Prek Russey | Bamboo river |
| Vĩnh Long | ឡុង ហ | Long Hor | Long river valley |
| Tri Tôn | ស្រុកបាយ៉ង់ | Srok Bayon | Bayon district |
| Trà Cú | ត្រពាំងត្រកួន | Tra Kuon | Water spinach pond |
| Phú Quốc | កោះត្រល់ | Koh Trol | Trol island |

---

## 4. Paper Strategy

### Framing

> "We PROVE that LLMs have systematic blind spots on culturally-specific translation for underserved language varieties, and PROPOSE two interventions (CKB + dialogue context) plus an evaluation framework to detect and fix them. The Khmer Krom variety (~1.3M speakers, Vietnam's Mekong Delta) exemplifies a class of underserved language varieties where existing MT resources (trained on Cambodian Standard Khmer) systematically fail."

### Contribution Architecture

```
PROBLEM:  LLMs fail on Khmer Krom cultural MT → 6 weakness categories [C3]
          Khmer Krom ≠ Cambodian Khmer → proven via A/B/C taxonomy [C2]

RESOURCE: CulturalMT-ViKm benchmark [C1] + CKB v2 [C2/C4]
          → First NLP resources specifically targeting Khmer Krom

METHOD:   CKB-RAG (CuEA: 0.419→0.937, 86% error reduction) [C4]
          + Dialogue context (+9.0 chrF++, 80% win rate) [C5]
          → Two complementary, model-agnostic interventions

EVAL:     CuEA + Script Purity + Error Taxonomy [C6]
          → Standard metrics miss cultural errors; our framework catches them

BREADTH:  Multi-model comparison [C8 — TODO]
          + Human evaluation [C9 — TODO]
          → Findings generalize across models, validated by native speakers
```

### Why CuEA is the Headline Metric

```
Example: "Người dân không làm cốm dẹp vào ngày thường"

Plain:  "...អាហារកុមដេបi..."  ← phonetic guess
KB-RAG: "...អំបុក..."           ← correct Khmer Krom term
Ref:    "...អំបុក..."           ← same

chrF++ difference: ~5 points (modest — rest of sentence is OK)
CuEA difference:   0.0 → 1.0  (dramatic — the cultural entity went from WRONG to CORRECT)
```

### Mandatory TODO for Publication

1. **C8: Multi-model** — Add NLLB-3.3B + Google Translate (minimum). Without this, reviewers reject single-model papers.
2. **C9: Human evaluation** — 2 native Khmer Krom speakers, 100 samples, Fluency + Adequacy + Cultural Naturalness (1-5), Cohen's kappa. ACL/EMNLP nearly requires this for MT papers.
3. **C10: Public release** — HuggingFace dataset + CKB v2 with Data Statement (Bender & Friedman, 2018).

### Target Venues

- **Primary**: ACL 2026 main (Resource & Evaluation track), EMNLP 2026 main
- **Secondary**: ACL Findings, LREC-COLING 2026, WMT 2026
- **Linguistic angle**: ACL Linguistic Diversity track, Computational Linguistics journal

---

## 5. Related Work (Key Papers)

### Vietnamese-Khmer MT
- Lightweight Training & Synthetic Data for Vi-Km (PACLIC 2025)
- Khmer-Vietnamese NMT with Data Augmentation (Informatica 2024)
- Multilingual NMT with Filtering (PACLIC 2020)

### Culturally-Aware MT
- Culture-aware MT: Catalan-Chinese (MT Summit 2025) — ~1,000 cultural sentences
- CaMMT: Culturally Aware Multimodal MT (EMNLP Findings 2025) — visual context, 5,800 triples
- Compositional Translation for Low-Resource MT (EMNLP Findings 2025)

### Benchmark Quality
- "Languages Still Left Behind" — FLORES+ critique (EMNLP 2025)
- FLORES-101 (2021) — 101-language benchmark paper

### Discourse-Level MT
- TransGraph: Discourse Graph for Doc MT (EACL 2026)
- Source-primed Multi-turn Conversation MT (EMNLP Findings 2025)
- Quality-Aware Decoding for Discourse MT (EACL 2026)

### Human Feedback in MT
- Direct Quality Optimization / DQO (WMT 2025)
- RLHF for NMT (EAMT 2024)

### Cultural NLP
- CARE: Multilingual Human Preference Learning for Cultural Awareness (EMNLP 2025)
- MakiEval: data-based Framework for Cultural Awareness Evaluation (ArXiv 2025)
- Culturally Aware and Adapted NLP: A Taxonomy (TACL 2025)

---

## 6. Prompt Templates (Proven Effective)

### Zero-shot Translation

```
System: You are an expert translator specializing in Vietnamese-Khmer translation.
        Translate the following Vietnamese text into Khmer.
        Output ONLY the Khmer translation, nothing else.
User:   Vietnamese: {source_text}
```

### CKB-RAG Augmented Translation (★ Best for cultural entities)

```
System: You are an expert translator specializing in Vietnamese-Khmer Krom translation,
        particularly for the Khmer Krom community (ខ្មែរក្រោម) in Vietnam's Mekong Delta.
        You will be given cultural terminology references to use.
        ALWAYS use the provided Khmer terms for cultural entities.
        Use Khmer Krom dialect where applicable.
        Output ONLY the Khmer translation, nothing else.
User:   Cultural terminology reference (Khmer Krom dialect):
          "cốm dẹp" → "អំបុក" (Flattened rice, used in Ok Om Bok festival)
          "Ok Om Bok" → "អកអំបុក" (Moon Worship Festival)
          "Sóc Trăng" → "ខេត្តឃ្លាំង" (Srok Khleang, province)

        Translate this Vietnamese text into Khmer:
        {source_text}
```

### Dialogue Context Translation (★ Best for discourse)

```
System: You are an expert translator specializing in Vietnamese-Khmer translation.
        You are translating a conversation between an interviewer and a Khmer person.
        Previous turns of the conversation are provided for context.
        Translate ONLY the last Vietnamese utterance into Khmer.
        Output ONLY the Khmer translation, nothing else.
User:   Previous conversation turns:

        Vietnamese: {turn_1_vi}
        Khmer: {turn_1_km}
        Vietnamese: {turn_2_vi}
        Khmer: {turn_2_km}

        Now translate the next turn:
        Vietnamese: {target_vi}
```

---

## 7. Data Quirks and Gotchas

- `all_1.jsonl` (981 samples) and `all_2.jsonl` (875 samples) — IDs may overlap across files
- Labels with `***` = alignment annotations — use `get_clean_reference()` to strip
- Labels with `###` = correction notes — split on `###` and take first part (pre-###)
- `Comments` field is always empty (unused)
- Only ~47% of dialogue turns have explicit speaker markers
- Conversations average ~3.3 turns — too short for discourse training, fine for LLM in-context
- BLEU ≈ 0 is **normal** for Vi→Km; do not treat as bug
- `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` needed on Windows
- CuEA returns `None` for samples with no cultural entities (don't average with zeros)
- `cultural_kb_expanded.py` supersedes `cultural_kb.py` — always import from v2
