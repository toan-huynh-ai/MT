#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import sys
import time
import unicodedata  # Module lõi dùng để chuẩn hóa NFC tiếng Bahnar
from pathlib import Path
import sacrebleu

# Đảm bảo hiển thị đúng font tiếng Bahnar và tiếng Việt trên Console
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Đường dẫn đến file kết quả của bạn
INPUT_FILE_PATH = r"C:\Users\HOY9HC\Desktop\Code\Learning\MT\MT2\bahnar\results\expALL_twoway_zeroshot_bahnar_gpt5_at_home.json"


def normalize_to_nfc(text):
    """
    Chuẩn hóa chuỗi về dạng Unicode NFC nhằm đồng bộ các ký tự dấu phụ tiếng Bahnar 
    (Ví dụ: gộp ký tự gốc và dấu móc rời rạc thành một ký tự thống nhất).
    """
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFC", text).strip()


def get_clean_reference(label_data):
    """
    Trích xuất và làm sạch bản dịch tham chiếu từ trường label.
    """
    if not label_data:
        return ""
    
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
        clean = lbl.split("###")[0].strip()
        parts = clean.split("***")
        if len(parts) == 1 and len(clean) > len(best):
            best = clean
            
    if not best and labels:
        first_lbl = labels[0]
        if isinstance(first_lbl, str):
            raw = first_lbl.split("###")[0].strip()
            best = re.sub(r"\S+\s*\*\*\*\*\s*", "", raw).strip()
            if not best:
                best = first_lbl.split("###")[-1].strip()
                
    return normalize_to_nfc(best)


def compute_metrics(hypotheses, references):
    """
    Tính toán metrics cho tiếng Bahnar và tiếng Việt.
    Do cả hai đều viết cách từ bằng khoảng trắng, ta dùng tokenizer tiêu chuẩn "13a"
    nhưng thực hiện chuẩn hóa NFC trước để tránh lệch dấu phụ.
    """
    if not hypotheses or not references:
        return {"bleu": 0.0, "chrf++": 0.0}

    # Chuẩn hóa NFC đồng loạt cho toàn bộ danh sách đầu vào
    hypotheses = [normalize_to_nfc(h) for h in hypotheses]
    references = [normalize_to_nfc(r) for r in references]

    # Tính BLEU (sử dụng tokenizer tiêu chuẩn 13a phù hợp với ngôn ngữ viết cách khoảng)
    try:
        bleu = sacrebleu.corpus_bleu(hypotheses, [references], tokenize="13a")
        bleu_score = round(bleu.score, 2)
    except Exception as e:
        print(f"[WARN] Lỗi tính toán BLEU: {e}. Tự động fallback về 'char'...", flush=True)
        bleu = sacrebleu.corpus_bleu(hypotheses, [references], tokenize="char")
        bleu_score = round(bleu.score, 2)

    # Tính chrF++ (word_order=2)
    try:
        chrf = sacrebleu.corpus_chrf(hypotheses, [references], word_order=2)
        chrf_score = round(chrf.score, 2)
    except TypeError:
        chrf = sacrebleu.corpus_chrf(hypotheses, [references])
        chrf_score = round(chrf.score, 2)

    return {"bleu": bleu_score, "chrf++": chrf_score}


def main():
    file_path = Path(INPUT_FILE_PATH)
    if not file_path.exists():
        print(f"ERROR: Không tìm thấy file JSON tại:\n{INPUT_FILE_PATH}", flush=True)
        sys.exit(1)

    print(f"--- ĐÁNH GIÁ CHẤT LƯỢNG DỊCH THUẬT TIẾNG BAHNAR ---", flush=True)
    print(f"Đang đọc dữ liệu từ: {file_path.name} ...", flush=True)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("per_sample", [])
    if not samples:
        print("ERROR: Không tìm thấy trường 'per_sample'.", flush=True)
        sys.exit(1)

    print(f"Tổng số mẫu cần xử lý: {len(samples)}", flush=True)

    hyps_fwd, refs_fwd = [], []  # Vi -> Ba
    hyps_rev, refs_rev = [], []  # Ba -> Vi

    for i, s in enumerate(samples):
        text_vi = s.get("text", "").strip()
        ref_ba_raw = s.get("label", [])
        ref_ba_clean = get_clean_reference(ref_ba_raw)

        # Sử dụng các trường khóa dành riêng cho tiếng Bahnar (ba)
        hyp_ba = s.get("hyp_vi_to_ba", "").strip()
        hyp_vi = s.get("hyp_ba_to_vi", "").strip()

        if not text_vi or not ref_ba_clean or not hyp_ba or not hyp_vi:
            continue

        hyps_fwd.append(hyp_ba)
        refs_fwd.append(ref_ba_clean)

        hyps_rev.append(hyp_vi)
        refs_rev.append(text_vi)

    if not hyps_fwd or not hyps_rev:
        print("ERROR: Không gom đủ dữ liệu hợp lệ để tiến hành tính toán.", flush=True)
        sys.exit(1)

    print("Đang tính toán các chỉ số chất lượng...", flush=True)
    start_time = time.time()

    # Đánh giá song chiều sử dụng cơ chế so khớp chữ Latin có khoảng trắng
    metrics_fwd = compute_metrics(hyps_fwd, refs_fwd)
    metrics_rev = compute_metrics(hyps_rev, refs_rev)

    duration = time.time() - start_time

    # --- IN BẢNG KẾT QUẢ ---
    print("\n" + "=" * 65)
    print(f"             KẾT QUẢ ĐÁNH GIÁ SONG CHIỀU VIỆT - BAHNAR")
    print("=" * 65)
    print(f"{'Hướng Dịch thuật':<30} | {'BLEU Score':>13} | {'chrF++ Score':>13}")
    print("-" * 65)
    print(f"{'Vietnamese -> Bahnar (Fwd)':<30} | {metrics_fwd['bleu']:>13.2f} | {metrics_fwd['chrf++']:>13.2f}")
    print(f"{'Bahnar -> Vietnamese (Rev)':<30} | {metrics_rev['bleu']:>13.2f} | {metrics_rev['chrf++']:>13.2f}")
    print("-" * 65)
    print(f"Số lượng mẫu hợp lệ: {len(hyps_fwd)} | Thời gian xử lý: {duration:.2f} giây")
    print("=" * 65)

    # --- CẬP NHẬT KẾT QUẢ VÀO FILE JSON GỐC ---
    data["metrics"] = {
        "vietnamese_to_bahnar": metrics_fwd,
        "bahnar_to_vietnamese": metrics_rev
    }
    
    if "metadata" in data:
        data["metadata"]["status"] = "completed"
        data["metadata"]["total_samples"] = len(samples)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[Xong] Đã cập nhật kết quả chính xác vào file JSON gốc.", flush=True)


if __name__ == "__main__":
    main()
