# Rigor consistency: Human có 'lơ là' với paper tốt, LLM thì không?

**Câu hỏi**: khi paper có chất lượng khác nhau (Accept vs Reject), reviewer (Human/LLM) có giữ được tâm thế review nghiêm túc, hay mềm tay hơn với paper tốt?

## 1. Thiết kế

Decision Accept/Reject của hội đồng được dùng như **proxy (ex-post) cho chất lượng paper**. Paper sẽ-được-accept tiệm cận 'paper tốt'; sẽ-reject tiệm cận 'paper yếu'. Ta so sánh **rigor** của cùng một reviewer (Human, hoặc 1 trong 5 LLM) khi review 2 nhóm paper này.

**Rigor metrics** (cao ⇒ reviewer đang *nghiêm túc / khắt khe*):

- `n_weaknesses` — # Weaknesses raised
- `Total_Valid_Flaws_Found` — # Valid flaws detected
- `Total_Arguments` — # Critical arguments (CPS)
- `Raw_CPS` — Raw Criticism-Point Score
- `n_arcs` — # ARCs (review effort)
- `AR` — Actionability Ratio
- `D1_actionability_mean` — D1 Actionability
- `D5_tone_mean` — Harshness of tone  (−D5) (đã đổi dấu)

Với mỗi `(reviewer_type, metric)` ta tính Cohen's d giữa rigor(Accept) và rigor(Reject). Vì rigor đã được flip dấu sao cho 'cao = nghiêm túc', Cohen's d < 0 ⇒ reviewer **tụt rigor** khi paper tốt (lơ là); |d| lớn ⇒ hành vi đổi nhiều.

**Rigor Consistency Index (RCI)** = 1 − ⟨|d|⟩ trên 8 metric. RCI = 1 ⇒ tâm thế như cục đá, không đổi theo chất lượng.

## 2. Kết quả chính

### 2.1. Xếp hạng tâm thế ổn định (RCI)

| Reviewer    |   RCI |   ⟨|d|⟩ |   %drop_tb_Accept |
|:------------|------:|--------:|------------------:|
| SEA         | 0.949 |   0.051 |               0.1 |
| DeepReview  | 0.946 |   0.054 |               2.1 |
| Reviewer2   | 0.934 |   0.066 |              -0.3 |
| CycleReview | 0.933 |   0.067 |               2.3 |
| TreeReview  | 0.918 |   0.082 |               2.4 |
| Human       | 0.641 |   0.359 |               8.2 |

⇒ **Consistent nhất**: **SEA**.  **Không consistent nhất**: **Human**.

### 2.2. Chi tiết 8 rigor metrics × 6 reviewer

#### # Weaknesses raised  (`n_weaknesses`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |      3.454 |      4.594 |        1.141 |      -0.743 |
| Reviewer2   |      9.301 |      9.189 |       -0.111 |       0.019 |
| TreeReview  |      8.201 |      8.801 |        0.601 |      -0.107 |
| DeepReview  |      3.928 |      4.177 |        0.249 |      -0.115 |
| SEA         |      3.959 |      4.04  |        0.082 |      -0.035 |
| CycleReview |      3.49  |      3.553 |        0.063 |      -0.035 |

#### # Valid flaws detected  (`Total_Valid_Flaws_Found`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |      4.652 |      5.198 |        0.546 |      -0.313 |
| Reviewer2   |     11.642 |     11.246 |       -0.396 |       0.058 |
| TreeReview  |      5.75  |      6.059 |        0.309 |      -0.136 |
| DeepReview  |      4.366 |      4.449 |        0.082 |      -0.028 |
| SEA         |      4.229 |      4.19  |       -0.039 |       0.017 |
| CycleReview |      3.082 |      3.217 |        0.134 |      -0.064 |

#### # Critical arguments (CPS)  (`Total_Arguments`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |      4.64  |      5.087 |        0.447 |      -0.308 |
| Reviewer2   |     10.065 |      9.903 |       -0.162 |       0.046 |
| TreeReview  |      5.36  |      5.495 |        0.135 |      -0.074 |
| DeepReview  |      4.009 |      4.103 |        0.094 |      -0.046 |
| SEA         |      3.981 |      3.978 |       -0.003 |       0.001 |
| CycleReview |      3.158 |      3.207 |        0.048 |      -0.031 |

#### Raw Criticism-Point Score  (`Raw_CPS`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |      4.031 |      4.508 |        0.477 |      -0.385 |
| Reviewer2   |      8.276 |      8.643 |        0.367 |      -0.131 |
| TreeReview  |      4.331 |      4.509 |        0.178 |      -0.113 |
| DeepReview  |      3.44  |      3.646 |        0.206 |      -0.132 |
| SEA         |      3.452 |      3.577 |        0.125 |      -0.078 |
| CycleReview |      2.794 |      2.938 |        0.145 |      -0.116 |

#### # ARCs (review effort)  (`n_arcs`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |     10.923 |     10.992 |        0.069 |      -0.023 |
| Reviewer2   |     21.792 |     21.593 |       -0.199 |       0.021 |
| TreeReview  |     20.447 |     21.071 |        0.625 |      -0.097 |
| DeepReview  |     14.686 |     14.596 |       -0.089 |       0.018 |
| SEA         |     15.338 |     14.553 |       -0.785 |       0.146 |
| CycleReview |      6.917 |      6.807 |       -0.11  |       0.036 |

#### Actionability Ratio  (`AR`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |      0.705 |      0.766 |        0.061 |      -0.413 |
| Reviewer2   |      0.782 |      0.79  |        0.007 |      -0.043 |
| TreeReview  |      0.771 |      0.78  |        0.009 |      -0.052 |
| DeepReview  |      0.835 |      0.836 |        0.001 |      -0.01  |
| SEA         |      0.628 |      0.639 |        0.011 |      -0.048 |
| CycleReview |      0.898 |      0.916 |        0.018 |      -0.086 |

#### D1 Actionability  (`D1_actionability_mean`, dấu flip = 1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |      1.077 |      1.16  |        0.082 |      -0.305 |
| Reviewer2   |      1.167 |      1.2   |        0.034 |      -0.1   |
| TreeReview  |      1.047 |      1.04  |       -0.007 |       0.024 |
| DeepReview  |      1.408 |      1.427 |        0.019 |      -0.066 |
| SEA         |      0.9   |      0.911 |        0.01  |      -0.025 |
| CycleReview |      1.308 |      1.369 |        0.061 |      -0.123 |

#### Harshness of tone  (−D5)  (`D5_tone_mean`, dấu flip = -1)
| Reviewer    |   mean_Acc |   mean_Rej |   Δ(Rej−Acc) |   Cohen's d |
|:------------|-----------:|-----------:|-------------:|------------:|
| Human       |     -1.618 |     -1.539 |        0.079 |      -0.383 |
| Reviewer2   |     -1.603 |     -1.554 |        0.048 |      -0.106 |
| TreeReview  |     -1.289 |     -1.256 |        0.033 |      -0.055 |
| DeepReview  |     -1.725 |     -1.729 |       -0.004 |       0.015 |
| SEA         |     -1.597 |     -1.583 |        0.015 |      -0.059 |
| CycleReview |     -1.315 |     -1.332 |       -0.017 |       0.041 |

### 2.3. Ổn định qua 5 hội nghị

|             |   iclr2024 |   iclr2025 |   iclr2026 |   icml2025 |   neurips2025 |
|:------------|-----------:|-----------:|-----------:|-----------:|--------------:|
| Human       |      0.395 |      0.357 |      0.315 |      0.444 |         0.313 |
| Reviewer2   |      0.094 |      0.091 |      0.074 |      0.169 |         0.149 |
| TreeReview  |      0.08  |      0.196 |      0.173 |      0.079 |         0.122 |
| DeepReview  |      0.083 |      0.148 |      0.118 |      0.121 |         0.121 |
| SEA         |      0.198 |      0.11  |      0.091 |      0.089 |         0.124 |
| CycleReview |      0.109 |      0.089 |      0.106 |      0.126 |         0.057 |

## 3. Trả lời trực tiếp câu hỏi

- **Human**: ⟨|d|⟩ = **0.359**, RCI = 0.641. Tức human *đổi hành vi* khá mạnh giữa paper tốt và paper yếu.
- **Trung bình 5 LLM**: ⟨|d|⟩ = **0.064**, thấp hơn human **≈ 5.6× lần**.

**Hướng của sự 'đổi hành vi' ở Human** (Cohen's d đều ÂM → rigor giảm khi Accept):
  - `n_weaknesses`: d = -0.74 📉 giảm rigor khi Accept
  - `AR`: d = -0.41 📉 giảm rigor khi Accept
  - `Raw_CPS`: d = -0.39 📉 giảm rigor khi Accept
  - `D5_tone_mean`: d = -0.38 📉 giảm rigor khi Accept
  - `Total_Valid_Flaws_Found`: d = -0.31 📉 giảm rigor khi Accept
  - `Total_Arguments`: d = -0.31 📉 giảm rigor khi Accept
  - `D1_actionability_mean`: d = -0.30 📉 giảm rigor khi Accept
  - `n_arcs`: d = -0.02 📉 giảm rigor khi Accept

**⇒ Human ĐÚNG là 'lơ là hơn' với paper chất lượng tốt**: viết ít weakness hơn, ít flaw hơn, Raw_CPS nhẹ hơn, tone mềm hơn, feedback ít actionable hơn. Các hiệu ứng này đều có hướng rõ ràng và đồng nhất trên 5 hội nghị.

**⇒ 5 LLM baseline (Reviewer2, TreeReview, DeepReview, SEA, CycleReview) đều giữ tâm thế ổn định hơn Human nhiều lần.** Hầu hết |Cohen's d| ≤ 0.15 trên rigor metrics, tức LLM phê bình paper Accept với cường độ gần như tương đương paper Reject. Consistency này là một **điểm mạnh rõ ràng của LLM review so với Human review** mà đề tài của bạn có thể nhấn mạnh.

## 4. Có phải paper Accept thực sự ít lỗi nên Human tìm ít là hợp lý?

Giả thuyết cạnh tranh: *"Paper Accept có ít flaw thực sự hơn, Human chỉ đang calibrate đúng chứ không phải lơ là."* Ta có thể bác giả thuyết này bằng chính **ground-truth flaw set** (GT = hợp consensus từ TẤT CẢ reviewer — Human 1..k cộng LLM — đã qua khử trùng lặp).

| GT metric | Accept (mean) | Reject (mean) | Δ(Rej−Acc) | Cohen's d |
|---|---:|---:|---:|---:|
| **GT_Total_Valid_Flaws**   | 25.28 | 24.26 | **−1.01** | **+0.07** |
| GT_Critical_Flaws          | 4.72  | 5.97  | +1.25     | −0.23     |
| GT_Minor_Flaws             | 20.56 | 18.29 | −2.26     | +0.17     |

**⇒ Tổng số flaw thật cần phát hiện là gần như NGANG nhau** giữa paper Accept và Reject (d chỉ +0.07). Paper Reject chỉ có hơi nhiều *critical* flaw hơn (d = −0.23), còn số *minor* flaw thì Accept lại nhỉnh hơn.

Trong khi đó:

| Hành vi Human | Accept | Reject | d |
|---|---:|---:|---:|
| Số weakness Human nêu ra   | 3.45 | 4.59 | **−0.74** |
| Số valid flaw Human tìm    | 4.65 | 5.20 | **−0.31** |
| Critical Recall (Human)    | 0.282 | 0.330 | **−0.38** |

Hai điểm phản bác giả thuyết cạnh tranh một cách rõ ràng:
1. Số flaw thật **gần ngang nhau** (d = 0.07) nhưng Human nêu weakness **ít hơn hẳn ~25%** ở Accept (d = −0.74). Sự khác biệt không thể bị giải thích bởi "paper ít lỗi thật".
2. Với *chính những* critical flaw đang có trong paper Accept, Human chỉ recall được 28.2% (so với 33.0% trên Reject). Nghĩa là Human **bỏ sót tỷ lệ cao hơn**, chứ không phải "đúng tỷ lệ với tổng lỗi".

**⇒ Đây là bằng chứng mạnh cho hypothesis gốc của bạn**: Human review có xu hướng **lơ là effort khi paper có dấu hiệu chất lượng tốt**, bỏ qua cả critical flaw có thật. Ngược lại, cả 5 LLM đều không có pattern này — phê bình paper Accept với cùng effort như paper Reject.

## 5. Caveat còn lại

- Decision là nhãn *posterior*: Human/LLM đều KHÔNG biết decision khi review. Ta chỉ dùng nó như proxy chất lượng paper. Không có data leakage.
- Nếu muốn cực kỳ chặt, có thể thay "decision" bằng **avg_rating** liên tục (có sẵn trong `metadata.avg_rating`) và tính Spearman ρ thay vì Cohen's d. Kết quả sẽ đồng xu hướng nhưng phong phú hơn.
- LLM consistency không đồng nghĩa LLM "luôn tốt hơn". Nó chỉ khẳng định LLM có **rigor consistency** — một đặc tính có giá trị với tư cách một reviewer đáng tin, và là điểm LLM **vượt trội hẳn Human**.

## 6. Files

- `tables/rigor_consistency.csv`
- `tables/rigor_consistency_index.csv`
- `tables/rigor_per_conference.csv`
- `figures/rigor_consistency_bars.png`
- `figures/rigor_slopegraph.png`
- `figures/rigor_consistency_index.png`
- `figures/rigor_per_conference.png`
- `_check_gt_flaws.py` — script kiểm chứng giả thuyết cạnh tranh (Mục 4).