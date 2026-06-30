import json
import math
import numpy as np
import scipy.stats as stats

# Đường dẫn đến file kết quả sau khi đã chạy LLM-as-a-judge của bạn
evaluated_file_path = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\eval\results\evaluated_khmer_quality_score_1_5_gpt4o.json"

try:
    with open(evaluated_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Trích xuất toàn bộ điểm số từ các mẫu câu
    all_scores = []
    for sample in data.get("per_sample", []):
        judge_eval = sample.get("judge_evaluation", {})
        # Bỏ qua các câu bị lỗi kết nối API không có điểm
        if "error" in judge_eval:
            continue
            
        metrics = judge_eval.get("evaluation_metrics", {})
        score = metrics.get("final_quality_score")
        
        if score is not None:
            all_scores.append(float(score))
            
    n = len(all_scores)
    
    if n == 0:
        print("❌ Không tìm thấy dữ liệu điểm số hợp lệ trong file JSON.")
    else:
        # 2. Tính toán các chỉ số thống kê cơ bản
        mean_score = np.mean(all_scores)
        std_dev = np.std(all_scores, ddof=1) # Độ lệch chuẩn mẫu
        std_error = std_dev / math.sqrt(n)   # Sai số chuẩn (Standard Error)
        
        # 3. Tính khoảng sai số (Confidence Interval) ở mức tin cậy 95% dựa trên phân phối t-student
        confidence_level = 0.95
        degrees_of_freedom = n - 1
        t_critical = stats.t.ppf((1 + confidence_level) / 2, degrees_of_freedom)
        
        margin_of_error = t_critical * std_error
        
        # --- IN KẾT QUẢ ---
        print("=" * 60)
        print("📊 BÁO CÁO THỐNG KÊ CHI TIẾT TOÀN BỘ BẢN DỊCH")
        print("=" * 60)
        print(f"🔹 Tổng số mẫu câu hợp lệ (N): {n}")
        print(f"🔹 Điểm chất lượng trung bình (Mean): {mean_score:.4f} / 5.0")
        print(f"🔹 Độ lệch chuẩn (Std Dev): {std_dev:.4f}")
        print(f"🔹 Sai số chuẩn (Standard Error): {std_error:.4f}")
        print("-" * 60)
        print(f"🔥 KHOẢNG SAI SỐ (Margin of Error - 95% CI): ±{margin_of_error:.4f}")
        print(f"👉 Điểm thực tế nằm trong khoảng: [{mean_score - margin_of_error:.4f} đến {mean_score + margin_of_error:.4f}]")
        print("=" * 60)

except FileNotFoundError:
    print(f"❌ Không tìm thấy file JSON tại đường dẫn: {evaluated_file_path}")
except Exception as e:
    print(f"❌ Đã xảy ra lỗi khi xử lý dữ liệu: {str(e)}")