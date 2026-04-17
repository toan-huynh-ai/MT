# Dialogue MT — Bức tranh toàn cảnh

## 1. Có nghiên cứu về Dialogue MT không?

**Có**, nhưng chúng chủ yếu rơi vào hai nhánh:

### Nhánh 1: Chat Translation (customer support)

Đây là hướng phổ biến nhất hiện nay.

- **WMT Chat Shared Task 2024**: benchmark dịch hội thoại chat song ngữ cho các cặp ngôn ngữ high-resource như En-De, En-Fr, En-Pt-BR, En-Ko, En-Nl.
- Bài tổng kết: **"Findings of the WMT 2024 Shared Task on Chat Translation"**
- Vấn đề chính họ quan tâm:
  - context modeling
  - anaphora resolution
  - agreement across turns
  - multi-speaker modeling
  - noisy input robustness

### Nhánh 2: Neural Chat Translation / Dialogue-aware MT

Một số paper tiêu biểu:

- **ACL 2021**: *Modeling Bilingual Conversational Characteristics for Neural Chat Translation*
  - Mô hình role preference, dialogue coherence, translation consistency
  - Datasets: English-German, English-Chinese
- **EMNLP 2025 Findings**: *Source-primed Multi-turn Conversation Helps Large Language Models Translate Documents*
  - Dùng multi-turn conversation như một cách đưa context vào LLM dịch tài liệu
- **WMT 2024**: *Context-Aware LLM Translation System Using Conversation Summarization and Dialogue History*
  - Dùng dialogue history + summarization cho translation system

## 2. Vậy cái gì CHƯA có?

Phần lớn các nghiên cứu hiện tại tập trung vào:
- **high-resource language pairs**
- **customer support / transactional chat**
- **general domain**

Trong khi đó, gần như **không có** nghiên cứu nào ở giao điểm sau:

1. **Dialogue MT cho low-resource pairs**
2. **Dialogue MT cho culturally-grounded content**
3. **Dialogue MT cho ethnographic interview / narrative interview**
4. **Dialogue MT cho underserved dialect/variety** như Khmer Krom

## 3. Dataset của chúng ta là điểm mạnh hay điểm trừ?

### Điểm mạnh

#### 3.1. Cultural + Conversational + Low-resource + Underserved variety

Dataset của chúng ta nằm đúng ở giao điểm rất hiếm:

- **Vi-Km** là low-resource pair
- **Khmer Krom** là underserved variety
- Nội dung là **ethnographic conversations** (ẩm thực, gia tộc, tôn giáo, phong tục...)
- Có cấu trúc hội thoại (`id`, `topic`, `order`)

Điều này khác hẳn các benchmark kiểu WMT Chat, vốn chỉ là customer support.

#### 3.2. Speaker roles có meaning thật

Trong WMT Chat, speaker roles thường là:
- agent
- customer

Còn trong data của ta, speaker roles mang nhiều tầng ý nghĩa hơn:
- interviewer (outsider, formal, elicitation style)
- interviewee (Khmer Krom community member, culturally-embedded, code-mixed)

Điều này ảnh hưởng không chỉ register mà cả **từ vựng, phong cách, nội dung văn hóa**.

#### 3.3. Context effect đã có bằng chứng thực nghiệm

Từ thí nghiệm pilot:

- **Isolated turn**: chrF++ = 36.10
- **With full context**: chrF++ = 45.11
- **Delta**: +9.01 chrF++
- **Win rate**: 8/10 samples

Nghĩa là dù hội thoại ngắn, context vẫn giúp mạnh.

### Điểm trừ

#### 3.4. Conversation ngắn

- 1,504 dialogue turns
- 450 conversations
- trung bình chỉ ~3.3 turns / conversation

So với WMT Chat hay các dialogue benchmarks khác thì ngắn hơn nhiều.
Reviewer có thể hỏi:

> "Với 3 turns thì có đủ discourse phenomena để gọi là dialogue MT không?"

#### 3.5. Không phải spontaneous chat

Đây không phải kiểu hội thoại tự nhiên giữa 2 người bạn hoặc customer-agent. Nó là **structured ethnographic interview**.

Tức là:
- có template hỏi-đáp
- nhiều câu mang tính elicitation
- gần với interview corpus hơn là free chat corpus

Do đó, nếu gọi thẳng là "dialogue MT dataset" thì có thể bị reviewer so sánh với WMT Chat và thấy mismatch.

## 4. Kết luận công tâm

### Nếu gọi nó là:
- **"Dialogue MT dataset"** → hơi nguy hiểm, vì reviewer sẽ so với WMT Chat và thấy nhỏ + ít turns
- **"Culturally-grounded conversational MT benchmark"** → hợp lý hơn nhiều
- **"Ethnographic conversational translation benchmark for an underserved language variety"** → chính xác nhất

### Đánh giá cuối cùng

| Khía cạnh | Đánh giá |
|---|---|
| Có novelty nếu chỉ là dialogue MT? | Không nhiều |
| Có novelty nếu là cultural + conversational + low-resource + Khmer Krom? | **Có, và khá mạnh** |
| Dialogue là điểm mạnh? | **Có, nhưng là multiplier chứ không phải selling point chính** |
| Điểm trừ lớn nhất | hội thoại ngắn, không phải chat tự nhiên |

## 5. Framing khuyến nghị cho paper

Không nên nói:

> "We propose a new dialogue MT benchmark."

Nên nói:

> "We introduce the first culturally-grounded conversational MT benchmark for Khmer Krom, an underserved language variety in Vietnam’s Mekong Delta. Unlike customer-support chat datasets, our benchmark captures ethnographic interviews rich in cultural entities, discourse cues, and community-specific lexical variation."

## 6. Một số paper / benchmark liên quan cần nhớ

### Dialogue / Chat MT
- WMT 2024 Shared Task on Chat Translation
- Context-Aware LLM Translation System Using Conversation Summarization and Dialogue History (WMT 2024)
- Modeling Bilingual Conversational Characteristics for Neural Chat Translation (ACL 2021)
- Source-primed Multi-turn Conversation Helps Large Language Models Translate Documents (EMNLP Findings 2025)

### Cultural / low-resource / community-centered MT
- Machine Translation Through Cultural Texts: Can Verses and Prose Help Low-Resource Indigenous Models? (LoResMT 2024)
- Preserving Cultural Identity with Context-Aware Translation Through Multi-Agent AI Systems (ACL 2025 Workshop LM4UC)

## 7. Nguồn tham khảo web đã dùng để tổng hợp

- WMT Chat Task 2024: https://wmt-chat-task.github.io/2024/
- WMT 2024 Findings on Chat Translation: https://www.aclanthology.org/2024.wmt-1.59/
- ACL 2021 Neural Chat Translation: https://www.aclanthology.org/2021.acl-long.444/
- EMNLP 2025 multi-turn conversation MT: https://www.aclanthology.org/2025.findings-emnlp.1289/
- WMT 2024 context-aware LLM translation: http://aclanthology.org/2024.wmt-1.102/
- DiaBLa dataset: https://huggingface.co/datasets/rbawden/DiaBLa
- ACL 2025 LM4UC paper: https://aclanthology.org/2025.lm4uc-1.7/
