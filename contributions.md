# Paper Contributions — Phân tích & Kế hoạch

## Framing tổng thể

> **"Chúng tôi CHỨNG MINH rằng LLMs có blind spots có hệ thống trên culturally-specific translation cho underserved language varieties, và ĐỀ XUẤT hai interventions (CKB + dialogue context) cùng evaluation framework để detect và fix chúng."**

```
PROBLEM:  LLMs fail on cultural MT for underserved varieties (Khmer Krom ≠ Khmer Cambodia)
          → Chứng minh bằng 6 weakness categories [C2]

RESOURCE: CulturalMT-ViKm benchmark [C1] + Cultural Knowledge Base [C3]
          → First resources for Khmer Krom NLP

METHOD:   CKB-RAG (+6.8 chrF++) [C3] + Dialogue context (+9.0 chrF++) [C4]
          → Two complementary, model-agnostic interventions

EVAL:     CuEA + Script Purity [C5]
          → Standard metrics miss cultural errors; new metrics catch them

BREADTH:  Multi-model comparison [C6] + Human evaluation [C8]
          → Findings generalize across models and validated by humans
```

---

## Contributions hiện tại (đã có bằng chứng thực nghiệm)

| # | Contribution | Loại | Reviewer sẽ hỏi gì? | Trả lời bằng? |
|---|---|---|---|---|
| **C1** | **Benchmark CulturalMT-ViKm** — dataset đầu tiên cho Khmer Krom MT | Resource | "Tại sao cần thêm 1 benchmark nữa?" | Khmer Krom ≠ Khmer Cambodia, chưa ai có |
| **C2** | **Taxonomy 6 điểm yếu** của LLMs trên culturally-specific MT | Finding | "Có generalizable không?" | Pattern (transliteration, script leak) áp dụng cho bất kỳ low-resource cultural pair |
| **C3** | **Cultural Knowledge Base + RAG** → +6.8 chrF++, fix 11/13 entities | Method | "Chỉ là glossary + prompt?" | Không — KB có structure (category, dialect, context), RAG có entity detection |
| **C4** | **Dialogue context effect** → +9.0 chrF++, 80% win rate | Finding | "Có gì mới so với TransGraph?" | Đây là low-resource + cultural domain, chưa ai test |
| **C5** | **CuEA metric + Script Purity** — evaluation framework mới | Metric | "Sao không dùng metric có sẵn?" | BLEU ≈ 0 cho Vi-Km, chrF++ bỏ sót cultural errors |

---

## Contributions có thể thêm

### Dễ làm, impact cao

#### C6: Multi-model comparison — không chỉ GPT-4o

Hiện tại chỉ test GPT-4o. Nếu thêm 2-3 model nữa, paper mạnh hơn rất nhiều:

- **NLLB-3.3B** (Meta, open-source) — trained trên Cambodia Khmer, sẽ cho thấy cùng weakness pattern
- **Google Translate** — free, baseline phổ biến nhất
- **Claude / Gemini** — so sánh across LLM families

Kết quả kỳ vọng: tất cả đều fail trên Khmer Krom cultural terms → chứng minh đây là **systemic gap**, không chỉ của GPT-4o. Reviewer rất thích multi-model comparison.

### Trung bình khó, impact rất cao

#### C7: CKB giúp cải thiện MỌI model, không chỉ GPT-4o

Chạy KB-RAG trên nhiều model → chứng minh CKB là **model-agnostic intervention**. Nếu KB-RAG cải thiện cả GPT-4o, Claude, và Gemini, đó là contribution cực mạnh vì nó có nghĩa bất kỳ ai cũng có thể dùng CKB.

### Cần annotator, nhưng rất valuable

#### C8: Human evaluation từ native Khmer Krom speakers

Automatic metrics (chrF++, CuEA) là cần thiết nhưng chưa đủ cho A\*. Cần ít nhất:
- 2 annotators đánh giá 100 mẫu
- Đánh giá: Fluency, Adequacy, Cultural Naturalness (1-5 scale)
- Inter-annotator agreement (Cohen's kappa)

ACL/EMNLP gần như **bắt buộc** human evaluation cho MT papers.

### Bonus — nếu có thời gian

#### C9: Khmer Krom vs Cambodia Khmer linguistic analysis

Phân tích chính thức sự khác biệt qua lens MT. Ví dụ: "X% từ vựng trong data không tìm thấy trong từ điển Khmer Cambodia standard." Đây là interdisciplinary contribution (Linguistics + NLP) mà ACL đánh giá cao.

#### C10: Open-source dataset + CKB release

Public release trên HuggingFace với Data Statement (Bender & Friedman, 2018). ACL Resource track rất coi trọng việc này. Nếu release, paper sẽ được cite nhiều hơn.

---

## Khuyến nghị: 3 contributions cần thêm ngay

| Priority | Contribution | Effort | Impact cho paper |
|---|---|---|---|
| **MUST** | C6: Thêm ít nhất 2 models (NLLB + Google Translate) | 1-2 tuần | Reviewers sẽ reject nếu chỉ có 1 model |
| **MUST** | C8: Human evaluation (2 annotators, 100 mẫu) | 2-3 tuần | ACL/EMNLP yêu cầu cho MT papers |
| **SHOULD** | C10: Public release dataset + CKB | 1 tuần | Tăng citation impact đáng kể |
