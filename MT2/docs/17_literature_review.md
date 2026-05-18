# Rà soát tài liệu: Đã có ai làm theo hướng của mình chưa?

> Câu hỏi: Hướng tiếp cận của paper (Vi → Khmer với **variety
> awareness** cho cộng đồng Khmer Nam Bộ, kèm **KB văn hoá** để vá
> lỗ hổng) đã có ai làm chưa?
>
> **Câu trả lời ngắn**: Theo dữ liệu mình rà được, **chưa ai làm đúng
> cả ba yếu tố gộp lại** (Vi ↔ Khmer + Khmer Nam Bộ variety + cultural
> KB / cultural benchmark). Có nhiều mảnh ghép riêng lẻ đã được công
> bố, nhưng chúng để hở đúng khoảng trống paper này đang lấp.

## 1. Các nghiên cứu đã làm về dịch Việt–Khmer

Đây là những paper trực tiếp nhất đến ngôn ngữ pair Vi–Km. **Không
một paper nào trong danh sách dưới đây nhắc đến Khmer Nam Bộ /
Khmer Krom hay variety awareness.**

### 1.1 KC4MT (Nguyen et al., LREC 2022)
- **Nội dung**: Bộ corpus song ngữ Vi–Km chất lượng cao, 150k cặp câu,
  trích từ **Voice of Vietnam (VOV) news**.
- **Trọng tâm**: Domain tin tức. Dùng ngôn ngữ nhà nước / báo chí.
- **Khoảng cách với paper bạn**: Toàn bộ bản Khmer trong KC4MT được
  các chuyên gia song ngữ duyệt, nhưng là **Khmer chuẩn báo chí**
  (Lớp 3 trong taxonomy của bạn), không phải Khmer Nam Bộ giao tiếp
  cộng đồng. Không có cơ sở tri thức văn hoá đi kèm.
- Link: `aclanthology.org/2022.lrec-1.588`.

### 1.2 Khmer–Vietnamese NMT Data Augmentation (Informatica 2024)
- **Nội dung**: Back-translation + English pivot để tăng dữ liệu.
  Thắng Google Translate 5.3 BLEU trên test set 2 000 câu.
- **Trọng tâm**: Phương pháp data augmentation cho low-resource MT.
- **Khoảng cách**: Không nói đến nội dung văn hoá, không có khái niệm
  Khmer Krom. Chỉ nhìn Vi–Km như một language pair low-resource chung.

### 1.3 PACLIC 2025 — Lightweight Training (Nguyen et al.)
- **Nội dung**: Pipeline 3 giai đoạn (Continual Pre-training → Supervised
  Fine-Tuning → DPO) trên **SeaLLMs-v3-1.5B**. Dùng lại VOV dataset,
  sinh synthetic data bằng LLM lớn, train mô hình nhẹ.
- **Trọng tâm**: Hiệu quả tính toán và dữ liệu tổng hợp.
- **Khoảng cách**: Nhắm hiệu suất BLEU/METEOR trên VOV dataset.
  Không có discussion nào về **variety**, **dialect**, hay **cultural
  fidelity**. Chỉ nhìn Vi–Km là "pair low-resource điển hình".
- Đây là **công trình Vi–Km gần đây nhất** và vẫn chưa chạm vào hướng
  của bạn.

### 1.4 Fine-Tuning Multilingual Khmer NMT (Springer 2025/2026)
- **Nội dung**: Fine-tune NLLB trên corpus Khmer–{Vi, En, Th, Lao}.
- **Trọng tâm**: Cải thiện chất lượng dịch Khmer trên nhiều cặp.
- **Khoảng cách**: Một lần nữa, chỉ Khmer chuẩn. Không có Khmer Nam Bộ.

### 1.5 PrahokBART (arXiv 2512.13552, Dec 2025)
- **Nội dung**: Mô hình seq2seq tiền huấn luyện chuyên cho Khmer,
  tích hợp word segmentation và normalization. Vượt mBART50 trên
  MT, tóm tắt, sinh tiêu đề.
- **Khoảng cách**: Đây là **Khmer chuẩn Campuchia** — PrahokBART tên
  cũng lấy từ `prahok` (mắm Khmer). Không có Khmer Nam Bộ / cộng đồng
  Khmer Krom.

**Kết luận mảng 1.x**: Mọi paper Vi–Km hiện có chỉ nhìn Khmer như
*một ngôn ngữ đơn nhất*. Không có paper nào đặt câu hỏi "Khmer nào?" /
"cho cộng đồng nào?".

## 2. Các nghiên cứu về culturally-aware MT (không phải Vi–Km)

Đây là mảng mà hướng của bạn gần gũi về **phương pháp**, nhưng toàn
bộ **không chạm đến Khmer**.

### 2.1 NileChat (EMNLP 2025)
- **Nội dung**: LLM 3B cho tiếng Ả Rập Ai Cập và Ma-rốc, có sinh dữ
  liệu tổng hợp theo (i) ngôn ngữ, (ii) di sản văn hoá, (iii) giá trị
  văn hoá của cộng đồng cụ thể.
- **Vì sao liên quan**: Framework ba tầng (language / cultural heritage
  / cultural values) rất giống với triết lý bạn đang theo, nhưng
  **chỉ cho Ả Rập**. Không có Đông Nam Á, không có Khmer.
- **Điểm khác biệt**: Họ sinh **pre-training data**, bạn xây **KB +
  RAG**. Ngoài ra họ cho LLM từ đầu, không phải translate.
- Đây là paper hiện đại nhất minh hoạ *cùng vấn đề lớn* (LLM thiên
  về văn hoá của ngôn ngữ nguồn) nhưng áp cho Ả Rập chứ không Khmer.

### 2.2 CaMMT (EMNLP Findings 2025)
- **Nội dung**: Benchmark đa phương thức (ảnh + caption) cho MT có
  tính văn hoá. 5 800 triples, 19 ngôn ngữ, 23 khu vực. Tập trung
  vào culturally-specific items (CSI) như món ăn, trang phục, thành
  ngữ. Có cả hai cách dịch: *conserved* (giữ từ văn hoá gốc) và
  *substituted* (thay bằng tương đương).
- **Vì sao liên quan**: Thậm chí dùng khái niệm "conserved vs
  substituted" rất giống với variety preservation của bạn.
- **Khoảng cách**: **19 ngôn ngữ không có Khmer**. Không có Đông Nam Á
  nói chung. Không phủ Khmer Nam Bộ.
- Nếu bạn làm thêm Khmer vào benchmark kiểu CaMMT, đó là đóng góp
  thực sự có chỗ đứng.

### 2.3 Preserving Cultural Identity with Multi-Agent AI (LM4UC 2025)
- **Nội dung**: Framework multi-agent (translation + interpretation +
  bias eval) cho MT bảo toàn căn tính văn hoá. Vượt GPT-4o trên các
  benchmark liên quan.
- **Khoảng cách**: Framework tổng quát, không đánh cụ thể Khmer Krom.
  Mọi ngôn ngữ thử nghiệm đều là Indigenous languages ngoài Đông
  Nam Á.

### 2.4 KG-MT / Cross-Cultural MT với Multilingual KG (EMNLP 2024)
- **Nội dung**: Tích hợp knowledge graph đa ngữ vào NMT. Lift 129 %
  so với NLLB-200 và 62 % so với GPT-4 trên entity dịch văn hoá.
- **Vì sao liên quan**: Đây là **paper KB-RAG** cho MT văn hoá, rất
  gần với pipeline bạn đang xây.
- **Khoảng cách**: Dùng Wikidata / KG đa ngữ sẵn có. **Không có KG
  nào cho cộng đồng Khmer Nam Bộ trên Wikidata**. Paper không bàn
  về variety collapse, chỉ bàn về entity translation.

### 2.5 Wikidata-Driven Entity-Aware Translation (SemEval 2025)
- **Nội dung**: Dùng Wikidata retrieval để LLM dịch entity tốt hơn.
- **Khoảng cách**: Tương tự KG-MT. Chỉ chữa entity name, không chữa
  variety collapse. Và Wikidata **không bao phủ Khmer Nam Bộ**.

**Kết luận mảng 2.x**: Có một trào lưu 2024-2025 rất rõ: "làm MT
cho cộng đồng thiểu số theo hướng văn hoá + KB". Nhưng toàn bộ
các công trình đều **nhảy qua** Khmer / Đông Nam Á để làm Ả Rập,
Lebanese, Indigenous languages Mỹ Latin, v.v.

## 3. Các nghiên cứu về dialect / variety collapse

Đây là mảng mà *khái niệm* bạn đang dùng ("variety collapse") đã có
một số paper đặt tên và đo đạc, nhưng một lần nữa **không có Khmer**.

### 3.1 DialUp! (ACL 2025)
- **Nội dung**: Training-time M→D + inference-time D→M, làm MT robust
  với phương ngữ. Áp cho 4 họ ngôn ngữ.
- **Khoảng cách**: Không có Khmer trong 4 họ ngôn ngữ.

### 3.2 CODET (Findings of EACL 2024)
- **Nội dung**: Contrastive benchmark dialect cho MT, 891 variations,
  12 ngôn ngữ.
- **Khoảng cách**: 12 ngôn ngữ đó **không có Khmer**. Kiểm lại bằng
  Grep trong PDF.

### 3.3 DIALECTBENCH (ACL 2024)
- **Nội dung**: Benchmark 281 varieties trên 10 task NLP. Phát hiện
  khoảng cách lớn giữa standard và non-standard varieties.
- **Khoảng cách**: Paper nói "281 varieties, 40 language clusters"
  nhưng không xác nhận có Khmer Krom. Theo thông tin public, Khmer
  trong danh sách chỉ là Khmer Campuchia chuẩn.

### 3.4 Lebanese Dialect MT (arXiv 2025)
- **Nội dung**: Fine-tune LLM cho dialect Liban, benchmark LebEval.
  Cho thấy "smaller authentic dialectal dataset beats larger
  translated dataset".
- **Khoảng cách**: Chỉ áp dụng Lebanese. Không làm Khmer.

### 3.5 AL-QASIDA (arXiv Dec 2024)
- **Nội dung**: Phân tích có hệ thống LLM trên Dialectal Arabic.
  Phát hiện quan trọng: "LLM *hiểu* dialect Ả Rập tốt nhưng *không
  chịu sinh ra* dialect Ả Rập" — vì post-training bias model sang
  Modern Standard Arabic.
- **Vì sao cực kỳ liên quan**: Pattern **đọc hiểu được, sinh ra không
  được, collapse về dạng chuẩn** giống **hệt** những gì bạn đang
  quan sát với GPT-4o và 5 mô hình khác trên Khmer Nam Bộ.
- **Khoảng cách**: Họ làm cho Ả Rập. Bạn có thể cite paper này để
  nói *"hiện tượng này đã được ghi nhận cho Arabic, chúng tôi trình
  bày kỷ lục đầu tiên cho Khmer Krom và chỉ ra nó có cùng bản
  chất"*.

**Kết luận mảng 3.x**: Khung phân tích "variety collapse" đã có sẵn
trong văn liệu, **nhưng chỉ áp dụng cho Ả Rập, Ý (Alassio), Liban,
các ngôn ngữ Ấn-Âu, không có Khmer Krom**.

## 4. Các nghiên cứu về ngôn ngữ thiểu số ở Việt Nam (không phải Khmer)

Có một số công trình NMT cho ngôn ngữ dân tộc thiểu số ở Việt Nam,
nhưng chưa ai chọn Khmer Krom.

### 4.1 Bahnar – Vietnamese (Bùi et al., arXiv 2505.11421; Luận et al.,
LM4UC 2025)
- **Nội dung**: BARTBahnar, pre-train thêm từ BARTPho, dịch Bahnar
  (ngôn ngữ thiểu số ở Tây Nguyên) sang tiếng Việt. Có motivation
  "cultural bridge".
- **Khoảng cách**: Cùng nhóm vấn đề (ngôn ngữ thiểu số ở VN), nhưng
  Bahnar **không phải** Khmer Krom. Phương pháp là transfer learning
  truyền thống, không có KB văn hoá, không có cultural entity
  evaluation.

### 4.2 "Not All Data Augmentation Works" (OpenReview 2024)
- **Nội dung**: Phân tích typology-aware cho Bahnar và Tày. Kết luận:
  chỉ các phương pháp data augmentation phù hợp typology mới giúp.
- **Khoảng cách**: Không có Khmer.

### 4.3 ViDia2Std / ViMD Datasets
- **Nội dung**: Benchmark **dialect tiếng Việt** (63 tỉnh) cho speech
  recognition và dialect-to-standard translation.
- **Vì sao đáng chú ý**: ViDia2Std có concept "dialect → standard
  translation" — gần với ý bạn, nhưng làm **cho tiếng Việt chứ
  không phải Khmer**.

**Kết luận mảng 4.x**: Cộng đồng NLP Việt Nam đang làm MT cho dân
tộc thiểu số (Bahnar, Tày, và dialect tiếng Việt), nhưng **chưa ai
chọn cộng đồng Khmer Nam Bộ** — dù đây là cộng đồng ~1.3 triệu
người, lớn hơn cả Bahnar và Tày.

## 5. Tài nguyên Khmer Krom hiện có

Thực trạng rất thưa thớt:

### 5.1 Pangloss Collection — Krom Khmer Corpus
- Là tài liệu **ngôn ngữ học cổ** do CNRS lưu, từ bản thu âm năm
  1970 của Marie Alexandrine Martin. Chỉ ~4 phút 27 giây, danh
  sách từ vựng.
- **Không phải** tài nguyên NLP có thể dùng để MT.

### 5.2 khmer-nltk (VietHoang1512)
- Toolkit Python cho Khmer (segmentation, POS). **Khmer chuẩn**,
  không phân biệt variety.

### 5.3 KhmerResearch.com
- Nền tảng dịch nghiên cứu học thuật sang Khmer. Hoàn toàn hướng
  về **Khmer chuẩn Campuchia**.

### 5.4 KOD — Khmer Online Dictionary
- Từ điển đa ngữ Khmer với glossary chuyên ngành (pháp luật, nấu
  ăn, tục ngữ). **Khmer Campuchia chuẩn**, không có dạng Nam Bộ.

**Kết luận mảng 5.x**: Chưa có **bất kỳ cơ sở tri thức NLP nào dành
cho Khmer Nam Bộ / Khmer Krom** với mục tiêu MT. Pangloss là
historical linguistics, các tài nguyên khác đều Khmer chuẩn.

## 6. Bảng so sánh với hướng của bạn

| Trục | Paper của bạn | Paper gần nhất | Khoảng trống |
|---|---|---|---|
| Language pair | Vi → Khmer | KC4MT, PACLIC 2025, Informatica 2024 | Chưa ai variety-aware cho Vi–Km |
| Khmer variety | Khmer Nam Bộ cộng đồng | AL-QASIDA (Ả Rập), DialUp (4 họ), CODET (12 ngôn ngữ) | Không paper nào có Khmer Krom |
| Cultural KB | CKB v3, 391 entries | KG-MT (Wikidata), CaMMT (19 ngôn ngữ) | Không có KB cho cộng đồng Khmer VN |
| Đánh giá variety collapse | Có, 77 % trên 6 model | AL-QASIDA cho Ả Rập | Chưa ai đo cho Khmer |
| Cộng đồng mục tiêu | Khmer Nam Bộ ~1.3 triệu người | Bahnar, Tày | Khmer Nam Bộ bị bỏ ngỏ |
| Benchmark dataset | 1,856 mẫu song ngữ văn hoá | KC4MT (news), VOV | Chưa có cultural benchmark Vi–Km |

## 7. Positioning cho paper — điểm mạnh và điểm yếu

### Điểm mạnh (dựa trên khoảng trống tìm được)

1. **Đây sẽ là paper đầu tiên công bố benchmark Vi → Khmer cho nội
   dung văn hoá cộng đồng Khmer Nam Bộ**. KC4MT, VOV, v.v. đều là
   domain báo chí, không phải nội dung cộng đồng.
2. **Đây sẽ là paper đầu tiên ghi nhận "variety collapse" cho Khmer
   Krom**. Hiện tượng này đã được đặt tên cho Ả Rập (AL-QASIDA),
   Ý (CODET), Liban, nhưng chưa có cho Khmer.
3. **Cơ sở tri thức văn hoá CKB v3 là KB NLP duy nhất cho Khmer
   Nam Bộ**. Các KB Khmer hiện có đều Cambodia-centric hoặc chỉ là
   từ điển chung.
4. **Benchmark đa mô hình 6 hệ thống (GPT-4o + Aya + NLLB + Gemma-SL
   + Llama-SL + Sailor2)** là đánh giá toàn diện nhất hiện có cho
   Vi → Khmer.

### Điểm yếu cần chủ động nhận

1. **Các mảnh phương pháp bạn dùng không hoàn toàn mới**: KB-RAG cho
   MT văn hoá đã có KG-MT; framework 3-tầng cultural đã có NileChat;
   biểu hiện variety collapse đã được báo cáo cho Ả Rập. Đóng góp
   riêng của bạn **không phải** phương pháp, mà là **ứng dụng vào
   cộng đồng mới + dữ liệu mới + KB mới + phân tích định lượng
   đầu tiên cho Khmer Krom**.
2. **Một số paper cùng hướng ra ngay năm 2025**, nên sức ép thời
   gian nộp paper khá cao. Nếu paper chậm nửa năm, có thể sẽ có
   người khác làm Khmer Krom.
3. **Khmer Krom** vẫn là khái niệm bị tranh cãi về địa-chính trị.
   Khuyến nghị dùng thuật ngữ trung tính hơn trong paper: *Khmer
   for the ethnic Khmer community in Vietnam's Mekong Delta* hoặc
   *South-Vietnam Khmer*. Tránh dùng "Krom" trong tiêu đề.

### Đóng góp chính mình đề xuất viết

> "This paper provides the first NLP resources and empirical
> evaluation for Khmer as spoken by the ethnic Khmer community in
> Vietnam's Mekong Delta. We (i) release a 1,856-sample parallel
> benchmark of culturally grounded Vietnamese–Khmer translation,
> (ii) release a 391-entry Cultural Knowledge Base (CKB) with
> variety-aware annotations, (iii) document a systematic variety
> collapse pattern where state-of-the-art MT systems —GPT-4o,
> Aya-101, NLLB-200, Gemma-SEA-LION, Sailor2— drop community-level
> linguistic markers in 77–98% of cases. We show that a
> variety-aware CKB-RAG pipeline restores a substantial portion
> of this fidelity."

Đây là câu claim **có bằng chứng cứng, có khoảng trống cụ thể trong
literature, và không chạm vào hướng đã được ai làm**.

## 8. Các paper nên cite trong Related Work

Nhóm bắt buộc phải cite:

1. **KC4MT** (Nguyen et al., LREC 2022) — đối chiếu domain.
2. **PACLIC 2025** (Nguyen et al.) — công trình Vi-Km gần nhất.
3. **Informatica 2024** — công trình Vi-Km data augmentation.
4. **NileChat** (El Mekki et al., EMNLP 2025) — framework văn hoá
   gần nhất về triết lý.
5. **CaMMT** (EMNLP Findings 2025) — benchmark văn hoá, không phủ
   Khmer.
6. **KG-MT** (EMNLP 2024) — KB-RAG cho MT.
7. **AL-QASIDA** (arXiv 2412.04193) — variety collapse pattern ở
   ngôn ngữ khác.
8. **DialUp!** (ACL 2025) — adaptation dialect.
9. **DIALECTBENCH** (ACL 2024) — benchmark dialect rộng, không Khmer.
10. **Bahnar-Vietnamese** (arXiv 2505.11421, LM4UC 2025) — VN
    ethnic minority MT.
11. **Vietnamese LLM evaluation** (ViLLM-Eval) — chứng minh bench
    dịch từ English không đánh giá được văn hoá VN.

## 9. Gợi ý tiếp theo

1. **Kiểm tra thêm 2-3 paper** mình chưa đọc full: DIALECTBENCH
   repo để xem chính xác có Khmer không; KG-MT paper để xem có
   Southeast Asian languages không.
2. **Tải PDF của KC4MT và PACLIC 2025** về đọc kỹ để viết related
   work không trượt ý. Trích đúng câu gốc cho mỗi paper.
3. **Đọc AL-QASIDA rất kỹ**. Đây là paper gần nhất về methodology
   cho "variety collapse" phân tích. Bạn có thể mượn framework của
   họ (không làm lại từ đầu) và chỉ cần chứng minh hiện tượng cùng
   kiểu xảy ra với Khmer.

## 10. Kết luận

**Chưa có ai làm đúng hướng tổng hợp mà bạn đang đi**. Các mảnh ghép
(Vi-Km MT, cultural KB, variety-aware eval, dialect benchmark) đều
đã được làm *riêng lẻ* cho các ngôn ngữ khác hoặc *ở mức đơn giản*
cho Khmer chuẩn. Tổ hợp **Vi ↔ Khmer Nam Bộ + Cultural KB +
variety-aware eval** là khoảng trống rõ ràng và có thể nộp paper.

Rủi ro chính không phải là "hướng đã bị lấy", mà là **"ai đó cũng
đang nghĩ giống bạn và chạy đua"**. Trào lưu EMNLP 2025 / ACL 2025
về culturally-aware MT đã rất mạnh — nếu trong 3-6 tháng tới không
nộp paper, có thể sẽ có nhóm khác viết Khmer Krom.
