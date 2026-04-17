# Km→Vi Experiments — Kết quả và Phân tích

## Phát hiện quan trọng nhất: BẤT ĐỐI XỨNG CHIỀU DỊCH

```
               Vi→Km (đã có)          Km→Vi (mới)
               ─────────────          ────────────
BLEU           0.79                   35.36          ← gấp 45 lần!
chrF++         37.98                  57.97          ← gấp 1.5 lần

Probes (chrF++, weakest first):
  Vi→Km                               Km→Vi
  Complex      36.36                   Kinship      52.03   ← weakest Km→Vi
  Kinship      37.43                   Krom_region  53.24
  Colloquial   38.76                   Colloquial   58.67
  Food         39.46                   Religious    59.99
  Religious    43.13                   Festivals    61.03
  Krom_region  44.27                   Food         62.05   ← strongest Km→Vi

Context effect:
  Vi→Km delta  +9.01 chrF++           Km→Vi delta  +5.06 chrF++
  Vi→Km win    8/10                   Km→Vi win    8/10
```

## Phân tích chi tiết

### 1. GPT-4o dịch Km→Vi TỐT HƠN NHIỀU so với Vi→Km

- **BLEU 35.36** (Km→Vi) vs **0.79** (Vi→Km) — chênh lệch khổng lồ
- **chrF++ 57.97** (Km→Vi) vs **37.98** (Vi→Km) — tốt hơn 20 điểm

**Lý do**: GPT-4o hiểu Vietnamese rất tốt (high-resource target). Khi dịch Km→Vi, nó chỉ cần "hiểu" Khmer rồi generate Vietnamese — và generate Vietnamese là thế mạnh. Ngược lại Vi→Km yêu cầu generate Khmer Krom — điều mà GPT-4o rất kém.

**Implication cho paper**: Đây là finding quan trọng — cho thấy vấn đề không phải ở "understanding" mà ở "generation" cho underserved variety. GPT-4o CÓ THỂ hiểu Khmer Krom ở mức độ nào đó, nhưng KHÔNG THỂ generate Khmer Krom chính xác.

### 2. Thứ tự weakness KHÁC NHAU giữa 2 chiều

| Rank | Vi→Km (weakest first) | Km→Vi (weakest first) |
|---|---|---|
| 1 (yếu nhất) | Complex sentences (36.36) | **Kinship (52.03)** |
| 2 | **Kinship (37.43)** | Khmer Krom regional (53.24) |
| 3 | Colloquial (38.76) | Colloquial (58.67) |
| 4 | Food (39.46) | Religious (59.99) |
| 5 | Religious (43.13) | Festivals (61.03) |
| 6 (mạnh nhất) | Khmer Krom regional (44.27) | Food (62.05) |

**Insights**:
- **Kinship** yếu ở CẢ HAI chiều — hệ thống xưng hô Khmer phức tạp, GPT-4o struggle bất kể direction
- **Food** mạnh nhất ở Km→Vi (62.05) nhưng yếu ở Vi→Km (39.46) — GPT-4o HIỂU tên món ăn Khmer nhưng KHÔNG BIẾT generate chúng
- **Complex sentences** yếu nhất ở Vi→Km nhưng không có probe tương đương ở Km→Vi

### 3. Dialogue context giúp CẢ HAI chiều

- Vi→Km: +9.01 chrF++, 8/10 win
- Km→Vi: +5.06 chrF++, 8/10 win

Context effect nhỏ hơn ở Km→Vi (vì baseline đã cao). Nhưng win rate giống nhau (8/10), cho thấy context **consistently** giúp bất kể direction.

Per-sample highlight:
- "Traditions leading up to religious holidays": +19.3 (iso=63.4 → ctx=82.7)
- "How to care for toddlers": +11.5
- "MỐI QUAN HỆ VỚI XÃ HỘI": **-15.7** (context gây hại — cùng conversation thua ở Vi→Km)

### 4. BLEU giờ đây HOẠT ĐỘNG cho Km→Vi

- Vi→Km: BLEU ≈ 0 (vì script khác, expected)
- Km→Vi: BLEU = 35.36 (meaningful! vì output là Vietnamese — same script as reference)

Đây là finding methodological: **chrF++ cần dùng cho Vi→Km, nhưng BLEU có thể dùng bổ sung cho Km→Vi**.

## Tóm tắt bảng so sánh 2 chiều

| Metric | Vi→Km | Km→Vi | Ratio |
|---|---|---|---|
| BLEU | 0.79 | 35.36 | ×45 |
| chrF++ | 37.98 | 57.97 | ×1.5 |
| Context delta | +9.01 | +5.06 | — |
| Context win rate | 8/10 | 8/10 | Same |
| Weakest probe | Complex (36.36) | Kinship (52.03) | — |
| Strongest probe | Krom_regional (44.27) | Food (62.05) | — |

## Contribution mới cho paper

1. **Direction asymmetry**: GPT-4o Km→Vi >> Vi→Km → vấn đề là ở generation, không phải comprehension
2. **Kinship là weakness persistent**: Yếu ở cả 2 chiều → structural challenge
3. **BLEU meaningful cho Km→Vi**: Bổ sung cho chrF++ khi target là high-resource language
4. **Context helps both directions**: 8/10 win rate ở cả 2 chiều → robust finding
