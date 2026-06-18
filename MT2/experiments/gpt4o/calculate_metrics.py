#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import sys
import time
from pathlib import Path
import sacrebleu

# Thiết lập bảng mã UTF-8 cho Terminal để tránh lỗi hiển thị tiếng Khmer/tiếng Việt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Đường dẫn cố định đến file dữ liệu của bạn
INPUT_FILE_PATH = r"C:\Users\HOY9HC\Desktop\Code\Learning\MT\MT2\experiments\gpt4o\experiment_results\expALL_twoway_zeroshot_gpt4o_at_home_full.json"


def get_clean_reference(label_data):
    """
    Trích xuất và làm sạch bản dịch tham chiếu từ trường label.
    Xử lý linh hoạt cả dạng chuỗi (string) và mảng (list).
    """
    if not label_data:
        return ""
    
    # Chuẩn hóa dữ liệu đầu vào thành danh sách các chuỗi
    if isinstance(label_data, str):
        labels = [label_data]
    elif isinstance(label_data, list):
        labels = label_data
    else:
        return ""

    best = ""
    for lbl in labels:
        if not isinstance(lbl, str):
            continue
        # Tách bỏ phần bình luận (phía sau ký tự ### nếu có)
        clean = lbl.split("###")[0].strip()
        parts = clean.split("***")
        # Chọn chuỗi sạch dài nhất không chứa ký tự phân tách đặc biệt
        if len(parts) == 1 and len(clean) > len(best):
            best = clean
            
    if not best and labels:
        first_lbl = labels[0]
        if isinstance(first_lbl, str):
            raw = first_lbl.split("###")[0].strip()
            best = re.sub(r"\S+\s*\*\*\*\*\s*", "", raw).strip()
            if not best:
                best = first_lbl.split("###")[-1].strip()
                
    return best


def compute_metrics(hypotheses, references, target_lang="vi"):
    """
    Tính toán BLEU và chrF++ chính xác cao:
    - Tiếng Khmer (km): Sử dụng tokenizer 'flores200' để phân rã từ viết liền.
    - Tiếng Việt (vi): Sử dụng tokenizer '13a' tiêu chuẩn.
    - chrF++: Kích hoạt tham số word_order=2 để tính toán cả ký tự n-gram và từ n-gram.
    """
    if not hypotheses or not references:
        return {"bleu": 0.0, "chrf++": 0.0}

    # 1. Xác định phương pháp tokenize phù hợp cho BLEU
    if target_lang == "km":
        # Sử dụng tokenizer SentencePiece của FLORES-200 dành cho tiếng Khmer
        tokenize_method = "flores200"
    else:
        # Tiếng Việt phân tách bằng khoảng trắng, dùng 13a tiêu chuẩn
        tokenize_method = "13a"

    # Tính BLEU
    try:
        bleu = sacrebleu.corpus_bleu(hypotheses, [references], tokenize=tokenize_method)
        bleu_score = round(bleu.score, 2)
    except Exception as e:
        print(f"[WARN] Tokenizer '{tokenize_method}' gặp lỗi: {e}. Tự động fallback về 'char'...", flush=True)
        # Fallback về Character-level BLEU nếu hệ thống thiếu thư viện hỗ trợ
        bleu = sacrebleu.corpus_bleu(hypotheses, [references], tokenize="char")
        bleu_score = round(bleu.score, 2)

    # Tính chrF++ (word_order=2 bổ sung trọng số n-gram từ cho chrF)
    try:
        chrf = sacrebleu.corpus_chrf(hypotheses, [references], word_order=2)
        chrf_score = round(chrf.score, 2)
    except TypeError:
        # Tương thích ngược nếu thư viện sacrebleu phiên bản quá cũ không hỗ trợ word_order
        chrf = sacrebleu.corpus_chrf(hypotheses, [references])
        chrf_score = round(chrf.score, 2)

    return {"bleu": bleu_score, "chrf++": chrf_score}


def main():
    file_path = Path(INPUT_FILE_PATH)
    if not file_path.exists():
        print(f"ERROR: Không tìm thấy file JSON tại đường dẫn:\n{INPUT_FILE_PATH}", flush=True)
        sys.exit(1)

    print(f"Đang đọc dữ liệu từ: {file_path.name} ...", flush=True)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("per_sample", [])
    if not samples:
        print("ERROR: Không tìm thấy trường 'per_sample' hoặc danh sách rỗng.", flush=True)
        sys.exit(1)

    print(f"Tổng số mẫu cần xử lý: {len(samples)}", flush=True)

    # Khởi tạo các danh sách gom cụm dữ liệu đánh giá
    hyps_fwd, refs_fwd = [], []  # Chiều thuận (Vi -> Km)
    hyps_rev, refs_rev = [], []  # Chiều nghịch (Km -> Vi)

    for i, s in enumerate(samples):
        # 1. Trích xuất dữ liệu gốc và nhãn tham chiếu sạch
        text_vi = s.get("text", "").strip()
        ref_km_raw = s.get("label", [])
        ref_km_clean = get_clean_reference(ref_km_raw)

        # 2. Trích xuất bản dịch máy của mô hình
        hyp_km = s.get("hyp_vi_to_km", "").strip()
        hyp_vi = s.get("hyp_km_to_vi", "").strip()

        # Bỏ qua mẫu nếu thiếu một trong các thông tin quan trọng để tính điểm
        if not text_vi or not ref_km_clean or not hyp_km or not hyp_vi:
            print(f"  [Bỏ qua] Mẫu thứ {i+1} (ID: {s.get('id')}) bị thiếu dữ liệu dịch thuật.")
            continue

        # Thêm vào mảng đánh giá chiều Thuận: Việt -> Khmer
        hyps_fwd.append(hyp_km)
        refs_fwd.append(ref_km_clean)

        # Thêm vào mảng đánh giá chiều Nghịch: Khmer -> Việt
        hyps_rev.append(hyp_vi)
        refs_rev.append(text_vi)

    if not hyps_fwd or not hyps_rev:
        print("ERROR: Không gom đủ dữ liệu hợp lệ để tiến hành tính toán.", flush=True)
        sys.exit(1)

    print("\nĐang tính toán các chỉ số chất lượng...", flush=True)
    start_time = time.time()

    # Tính toán chỉ số riêng biệt cho từng chiều với cấu hình tối ưu ngôn ngữ
    metrics_fwd = compute_metrics(hyps_fwd, refs_fwd, target_lang="km")
    metrics_rev = compute_metrics(hyps_rev, refs_rev, target_lang="vi")

    duration = time.time() - start_time

    # --- IN BẢNG KẾT QUẢ ĐẸP MẮT ---
    print("\n" + "=" * 65)
    print(f"      KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG SONG CHIỀU CHÍNH XÁC CAO")
    print("=" * 65)
    print(f"{'Hướng Dịch thuật':<30} | {'BLEU Score':>13} | {'chrF++ Score':>13}")
    print("-" * 65)
    print(f"{'Vietnamese -> Khmer (Fwd)':<30} | {metrics_fwd['bleu']:>13.2f} | {metrics_fwd['chrf++']:>13.2f}")
    print(f"{'Khmer -> Vietnamese (Rev)':<30} | {metrics_rev['bleu']:>13.2f} | {metrics_rev['chrf++']:>13.2f}")
    print("-" * 65)
    print(f"Số lượng mẫu hợp lệ: {len(hyps_fwd)} | Thời gian xử lý: {duration:.2f} giây")
    print("=" * 65)

    # --- CẬP NHẬT KẾT QUẢ VÀO FILE JSON GỐC ---
    data["metrics"] = {
        "vietnamese_to_khmer": metrics_fwd,
        "khmer_to_vietnamese": metrics_rev
    }
    
    # Đổi trạng thái metadata thành completed
    if "metadata" in data:
        data["metadata"]["status"] = "completed"
        data["metadata"]["total_samples"] = len(samples)

    print(f"\nĐang ghi đè và cập nhật chỉ số chính xác vào file JSON gốc...", end="", flush=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(" [Xong]", flush=True)
    print(f"Đã cập nhật thành công file: {file_path}", flush=True)


if __name__ == "__main__":
    main()
