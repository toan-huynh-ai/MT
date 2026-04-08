# Khmer Cambodia vs Khmer Krom: Phân tích sự khác biệt

## Khmer Krom là gì?

Khmer Krom (ខ្មែរក្រោម) là tiếng Khmer của cộng đồng Khmer ở ĐBSCL Việt Nam, đã phân hóa với Khmer Cambodia qua hàng trăm năm. Đây **không phải cùng một thứ**, mặc dù cùng nguồn gốc.

---

## Sự khác biệt cụ thể

### 1. Từ vựng — khác biệt lớn nhất

Data của chúng ta đã chứng minh điều này. Khi chạy thí nghiệm, GPT-4o (trained chủ yếu trên Khmer Cambodia) đã dịch sai nhiều thuật ngữ vì nó **không biết từ Khmer Krom**:

| Thuật ngữ | Khmer Krom (data của ta) | GPT-4o output (Cambodia) | Vấn đề |
|---|---|---|---|
| nùm bong klanh | នំបង់ខ្លាញ់ | Dịch thành "trái cây" | Không tồn tại trong Khmer Cambodia |
| phum sóc | ភូមិសង្គម (cộng đồng) | ភូមិ (chỉ là "village") | Khmer Krom pha trộn Khmer-Vietnamese |
| cốm dẹp | អំបុក (ambok) | កុមដេប (phonetic guess) | GPT không biết từ Krom |

### 2. Vay mượn từ tiếng Việt

- **Khmer Krom**: Vay mượn rất nhiều từ tiếng Việt cho đời sống hàng ngày (hành chính, giáo dục, thương mại)
- **Khmer Cambodia**: Vay từ tiếng Pháp hoặc tiếng Anh

### 3. Ngữ âm

- Khmer Krom chịu ảnh hưởng thanh điệu từ tiếng Việt ở một số vùng
- Phát âm một số nguyên âm cũng hơi khác

### 4. Phong cách viết / Particles

Data của ta cho thấy references dùng:
- **Khmer Krom**: "ចា៎" (colloquial particle)
- **Khmer Cambodia**: "ចាស" (formal)
- GPT-4o luôn dùng dạng Cambodia

### 5. Tên món ăn / Phong tục

Nhiều tên món ăn trong data dùng cách gọi Vietnamese-influenced mà Khmer Cambodia không dùng. Phong tục cũng có sự khác biệt do ảnh hưởng văn hóa Việt.

---

## Dùng nguồn bên ngoài cho Knowledge Base: Nên hay không?

### Câu trả lời: CÓ, nhưng phải rất cẩn thận và minh bạch

### Cái NÊN dùng từ bên ngoài

| Nguồn | Dùng được | Lý do |
|---|---|---|
| Từ điển Khmer-Vietnamese (SEAlang, Headley's) | Dùng làm **tham chiếu**, không phải ground truth | Core vocabulary 80%+ giống nhau |
| Wikipedia Khmer (km.wikipedia.org) | Kiểm tra thuật ngữ tôn giáo, lịch sử | Thuật ngữ Phật giáo Theravada gần như đồng nhất |
| Unicode Khmer resources | Kiểm tra chính tả | Script giống nhau |

### Cái KHÔNG NÊN dùng trực tiếp

| Nguồn | Rủi ro |
|---|---|
| Google Translate (Khmer) | Train trên Cambodia Khmer, sẽ sai dialect |
| NLLB / FLORES | Dataset Khmer = Cambodia, không phải Krom |
| Từ điển online phổ thông | Không phân biệt Krom vs Cambodia |
| Khmer cultural websites Cambodia | Phong tục có thể khác (ăn uống, lễ hội) |

---

## Chiến lược xây dựng KB: "Data-First, External-Validated"

```
Lớp 1 (Primary — TRUSTED):
  └── Data của ta (1,856 mẫu Khmer Krom thực tế)
      ├── 58 alignment pairs từ *** annotations
      ├── Multi-reference translations
      └── Cultural context from conversations
      → ĐÂY LÀ GROUND TRUTH

Lớp 2 (Secondary — CROSS-CHECK):
  └── External Khmer resources
      ├── Dùng để verify spelling/grammar
      ├── Dùng để mở rộng coverage
      └── PHẢI được validate lại bởi annotator Khmer Krom
      → KHÔNG BAO GIỜ override Lớp 1

Lớp 3 (Metadata — ENRICHMENT):
  └── Ghi chú khác biệt dialect
      ├── "Standard Khmer: X, Khmer Krom: Y"
      └── Giúp paper có thêm linguistic contribution
```

### Ví dụ CKB entry với dialect annotation

```json
{
  "vi": "cốm dẹp",
  "km_krom": "អំបុក",
  "km_cambodia": "អង្ករកន្ទក់",
  "note": "Krom-specific term used in Ok Om Bok festival in Mekong Delta"
}
```

---

## Tại sao đây là ĐIỂM MẠNH chứ không phải điểm yếu?

Sự khác biệt Khmer Cambodia vs Khmer Krom **chính là gap mà paper này fill**:

1. **FLORES+, NLLB, Google Translate** → tất cả train trên Cambodia Khmer
2. **GPT-4o** → cũng train chủ yếu trên Cambodia Khmer
3. **Data của ta** → Khmer Krom thực tế từ ĐBSCL
4. **Kết quả**: GPT-4o dịch sai cultural entities → **chứng minh gap tồn tại**
5. **CKB của ta** → xây từ Khmer Krom data → **fill the gap**

### Framing cho paper:

> *"Existing MT systems and resources predominantly represent Cambodian Standard Khmer, leaving the Khmer Krom variety — spoken by approximately 1.3 million people in Vietnam's Mekong Delta — critically underserved. Our benchmark and Cultural Knowledge Base are, to our knowledge, the first NLP resources specifically targeting Khmer Krom."*

Đây là **contribution cực mạnh** về linguistic diversity — ACL/EMNLP rất ưu tiên điều này.

---

## Kết luận

| Khía cạnh | Khmer Cambodia | Khmer Krom (data của ta) |
|---|---|---|
| Tài nguyên NLP | Tương đối đầy đủ (FLORES, NLLB, Google) | Gần như không có |
| Từ vựng lõi | Chuẩn | Pha trộn Vietnamese |
| Thuật ngữ văn hóa | Phong tục Cambodia | Phong tục ĐBSCL Việt Nam |
| Phong cách nói | Formal | Colloquial, Vietnamese-influenced |
| Dân số | ~16 triệu (Cambodia) | ~1.3 triệu (Việt Nam) |
| Được LLMs hỗ trợ | Tương đối | Rất kém (đã chứng minh bằng thực nghiệm) |
