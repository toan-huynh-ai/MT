# GPT-4o Weakness Analysis for Vietnamese-Khmer Cultural MT

## Evidence-Based Weakness Catalog

We ran 6 targeted probes (48 samples total) across: kinship terms, religious/ritual terms, food/cuisine, Khmer Krom regional terms, complex sentences, and colloquial speech.

### chrF++ by Probe (lower = weaker)

```
complex sentences       36.36  ← WEAKEST
kinship terminology     37.43
colloquial speech       38.76
food/cuisine terms      39.46
religious/ritual terms  43.13
khmer krom regional     44.27
```

---

## Weakness 1: Cultural Food Terms → Transliteration Instead of Correct Khmer [CRITICAL]

GPT-4o does not know many Vietnamese-Khmer cultural food names and **transliterates instead of using the actual Khmer word**.

| Vietnamese | GPT-4o Output | Correct Khmer | Error Type |
|---|---|---|---|
| cốm dẹp | អាហារកុមដេប (phonetic "Kom Dêp") | អំបុក (Ambok) | Wrong term |
| bánh ống tre | នំបំពង់ឈើឆ្កាង (cake-tube-wood-cross) | នំបំពង់ឫស្សី (cake-tube-bamboo) | Wrong modifier |
| canh mắm (Tâc C'rương) | សម្លម្ជូរម៉ាំ | សម្លទឹកគ្រឿង | Wrong dish name |

**Back-translation proof**: GPT's translation of "cốm dẹp" back-translates to "Kom Dêp" (phonetic), not "flattened rice" (the actual meaning). The reference uses អំបុក which is the correct cultural term.

**Impact**: This is the strongest evidence that a **Cultural Knowledge Base** is needed. GPT-4o falls back to phonetic guessing when it doesn't know the Khmer-specific cultural equivalent.

---

## Weakness 2: Code-Mixed / Untranslated Foreign Scripts [CRITICAL]

GPT-4o sometimes **leaks Chinese characters or Vietnamese text** into Khmer translations.

### Evidence

**Chinese character leakage**:
```
Source: "Chúng tôi thường rủ nhau đi lễ chùa..."
GPT:    "យើងតែងតែអញ្ជើញគ្នាទៅ拜寺..."
                                    ^^^^
                           Chinese chars 拜寺 (worship temple)
```

**Vietnamese text retained in Khmer output**:
```
Source: "Num Ansam (còn gọi là bánh Tét) và Kom (còn gọi là bánh ít)..."
GPT:    "Num Ansam (ដែលគេហៅថា bánh Tét) និង Kom (ដែលគេហៅថា bánh ít)..."
                                ^^^^^^^^^                      ^^^^^^^^
                          Vietnamese left untranslated in Khmer output
```

**Impact**: This is a **language purity** error that would never occur in human translation. An automatic metric can easily flag this.

---

## Weakness 3: Religious/Ritual Terminology Gaps [HIGH]

GPT-4o struggles with Hindu-Buddhist religious terms that are specific to Khmer culture.

| Vietnamese | GPT-4o | Correct Khmer | Issue |
|---|---|---|---|
| Dôni và linga của thần ISo | Left romanized | យោនី នាងឧមា និងលិង្គព្រះឥសូ | No Khmer script |
| lễ dâng y Kathina | ពិធីបួងសួង Kathina | បុណ្យកឋិនទាន | Partially romanized |
| xuất gia và thọ giới | ចូលសង្ឃ និងទទួល戒律 | បួស និងសមាទានសីល | Chinese 戒律 leaked |
| tắm Phật | Not tested but likely standard | ស្រង់ព្រះ | Khmer-specific ritual term |

**Impact**: Religious terms are fundamental to Khmer cultural identity. Getting them wrong signals cultural incompetence.

---

## Weakness 4: Khmer Krom Dialect vs Standard Cambodian Khmer [HIGH]

GPT-4o consistently produces **standard Cambodian Khmer**, while the human translations use **Khmer Krom** (the dialect of Khmer spoken in Vietnam's Mekong Delta).

### Specific Dialect Differences Observed

| Feature | GPT-4o (Standard Khmer) | Reference (Khmer Krom) |
|---|---|---|
| Word choice for "village" | ភូមិ | ភូមិ/ឃុំ (+ phum sóc context) |
| Place names | ស្រុកត្រីតោន ខេត្តអនជាង (inaccurate phonetics) | ទ្រីតុង ខេត្តអានយ៉ាង (closer to local pronunciation) |
| Formality particles | បាទ/ចាស (standard) | ចា៎ / ចាស៎ (colloquial Krom markers) |
| Food terminology | Generic Khmer | Krom-specific terms (e.g., នំបង់ខ្លាញ់) |

**Impact**: For Khmer Krom speakers (the target audience), standard Cambodian Khmer may sound unnatural or even foreign. This is a key gap only a specialized benchmark can detect.

---

## Weakness 5: Complex Multi-Clause Sentences [HIGH]

chrF++ drops to **36.36** for complex sentences (vs 37.98 baseline). GPT-4o makes structural errors:

1. **Clause reordering**: Changes the order of information, sometimes losing emphasis
2. **Cultural nuance flattening**: Translates complex cultural descriptions into simpler, generic language
3. **Pronoun/reference confusion**: In long sentences with multiple actors

### Example

```
Source: "Có lần mẹ đi thăm ngoại về, trong giỏ sách rất nhiều đồ ăn khoai lang,
         1 con gà, 1 con vịt đặc biệt là nùm bong klanh mà ngoại gửi các cháu."

GPT back-translation: "Khi mẹ đến thăm ông bà, trong túi có nhiều thức ăn như
                        rau xào, một con gà, một con vịt, đặc biệt là trái cây..."
                                                                        ^^^^^^^^
                                              "nùm bong klanh" → "trái cây" (WRONG)
                                              Should be: "bánh bông lan" / នំបង់ខ្លាញ់

Reference back-translation: "Khi mẹ về thăm bà, có khoai lang, gà, vịt và đặc biệt
                              là nùm bong klanh mà bà gửi cho cháu."
```

**nùm bong klanh (នំបង់ខ្លាញ់)** is a traditional Khmer Krom cake. GPT-4o translates it as "trái cây" (fruit) — a **complete cultural entity loss**.

---

## Weakness 6: Kinship Term Specificity [MEDIUM]

Khmer has extremely specific kinship terms that Vietnamese doesn't map 1:1.

| Vietnamese | GPT-4o tends to use | More specific Khmer |
|---|---|---|
| bác (paternal uncle, older) | Generic ពូ | ធំ (elder paternal uncle) |
| cô (paternal aunt) | មីង | អ៊ំ/មីង (context-dependent) |
| ngoại (maternal grandmother) | អ្នកតា-អ្នកយាយ | យាយ (specific maternal grandmother) |
| hiếu hỉ (weddings & funerals) | ពិធីមង្គល | ពិធីសួរសុខទុក្ខ (more natural) |

---

## Weakness Summary Table

| # | Weakness | Severity | Frequency | KB Can Fix? | Metric Can Detect? |
|---|---|---|---|---|---|
| 1 | Food term transliteration | CRITICAL | High | **YES** | YES (entity match) |
| 2 | Foreign script leakage | CRITICAL | Medium | Partial | **YES** (script detection) |
| 3 | Religious term gaps | HIGH | Medium | **YES** | YES (entity match) |
| 4 | Khmer Krom dialect | HIGH | Pervasive | **YES** | YES (dialect classifier) |
| 5 | Complex sentence errors | HIGH | High | No | Partial (chrF++) |
| 6 | Kinship term specificity | MEDIUM | Medium | **YES** | YES (term matching) |

**Key insight**: 4 out of 6 weaknesses are directly addressable by a Cultural Knowledge Base. 5 out of 6 are detectable by a Cultural Evaluation Framework.

---

## What This Means for the Paper

### Contribution 1: GPT-4o's cultural blind spots

We can demonstrate that even the strongest LLM has **systematic cultural translation failures** that standard metrics (BLEU, chrF++) cannot fully capture. This motivates both the benchmark and the evaluation framework.

### Contribution 2: Cultural Knowledge Base as intervention

A KB containing the correct cultural entity mappings can be used via RAG to fix the most critical errors. This is a **concrete, measurable improvement**.

### Contribution 3: Cultural Evaluation Framework

We need metrics beyond chrF++ to catch:
- Cultural entity accuracy (Weakness 1, 3, 6)
- Language purity (Weakness 2)
- Dialect appropriateness (Weakness 4)
- Cultural concept preservation (Weakness 5)
