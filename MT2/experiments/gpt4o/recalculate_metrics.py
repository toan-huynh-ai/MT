import json
import re
import sacrebleu
from pathlib import Path

# Cấu hình đường dẫn tới file JSON kết quả của bạn
JSON_FILE_PATH = Path(r"D:\Code\Python\Research\MachineTranslation\MT\MT2\experiments\gpt4o\experiment_results\expALL_twoway_zeroshot_gpt5_at_home_full.json")

def get_clean_reference(labels):
    """Bảo tồn hàm làm sạch reference giống hệt trong code gốc của bạn"""
    best = ""
    for lbl in labels:
        clean = lbl.split("###")[0].strip()
        parts = clean.split("***")
        if len(parts) == 1 and len(clean) > len(best):
            best = clean
    if not best and labels:
        raw = labels[0].split("###")[0].strip()
        best = re.sub(r"\S+\s*\*\*\*\s*", "", raw).strip()
        if not best:
            best = labels[0].split("###")[-1].strip()
    return best

def main():
    if not JSON_FILE_PATH.exists():
        print(f"Error: Không tìm thấy file JSON tại {JSON_FILE_PATH}")
        return

    print(f"Đang đọc dữ liệu từ: {JSON_FILE_PATH}...")
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("per_sample", [])
    if not samples:
        print("Không tìm thấy dữ liệu mẫu trong trường 'per_sample'.")
        return

    hyps_fwd, refs_fwd = [], []
    hyps_rev, refs_rev = [], []

    # Thu thập dữ liệu dịch từ các sample để tính toán
    for s in samples:
        ref_clean = get_clean_reference(s.get("label", []))
        
        # Chiều thuận: Việt -> Khmer
        hyps_fwd.append(s.get("hyp_vi_to_km", ""))
        refs_fwd.append(ref_clean)
        
        # Chiều nghịch: Khmer -> Việt
        hyps_rev.append(s.get("hyp_km_to_vi", ""))
        refs_rev.append(s.get("text", ""))

    print("\n--- Tiến hành tính toán lại Metrics ---")

    # 1. Tính toán cho chiều thuận (Vietnamese -> Khmer)
    # Giải pháp: Sử dụng tokenize="char" (Char-BLEU) chuyên dụng cho ngôn ngữ không phân tách từ bằng khoảng trắng.
    bleu_fwd = sacrebleu.corpus_bleu(hyps_fwd, [refs_fwd], tokenize="char")
    try:
        chrf_fwd = sacrebleu.corpus_chrf(hyps_fwd, [refs_fwd], word_order=2)
    except TypeError:
        chrf_fwd = sacrebleu.corpus_chrf(hyps_fwd, [refs_fwd])

    # 2. Tính toán cho chiều nghịch (Khmer -> Vietnamese)
    # Vì tiếng Việt đích có khoảng trắng rõ ràng, sử dụng '13a' tiêu chuẩn là chính xác nhất.
    bleu_rev = sacrebleu.corpus_bleu(hyps_rev, [refs_rev], tokenize="13a")
    try:
        chrf_rev = sacrebleu.corpus_chrf(hyps_rev, [refs_rev], word_order=2)
    except TypeError:
        chrf_rev = sacrebleu.corpus_chrf(hyps_rev, [refs_rev])

    # Làm tròn điểm số 2 chữ số thập phân
    new_metrics_fwd = {"bleu": round(bleu_fwd.score, 2), "chrf++": round(chrf_fwd.score, 2)}
    new_metrics_rev = {"bleu": round(bleu_rev.score, 2), "chrf++": round(chrf_rev.score, 2)}

    # Hiển thị kết quả mới lên màn hình để đối chiếu
    print("\n" + "=" * 60)
    print("                RECALCULATED METRICS RESULTS")
    print("=" * 60)
    print(f"{'Hướng dịch':<25} | {'BLEU Cũ':>10} -> {'BLEU Mới':>10} | {'chrF++':>10}")
    print("-" * 60)
    print(f"{'Vietnamese -> Khmer':<25} | {data['metrics']['vietnamese_to_mer']['bleu'] if 'vietnamese_to_mer' in data['metrics'] else data['metrics'].get('vietnamese_to_khmer', {}).get('bleu', 0):>10.2f} -> {new_metrics_fwd['bleu']:>10.2f} | {new_metrics_fwd['chrf++']:>10.2f}")
    print(f"{'Khmer -> Vietnamese':<25} | {data['metrics']['khmer_to_vietnamese']['bleu']:>10.2f} -> {new_metrics_rev['bleu']:>10.2f} | {new_metrics_rev['chrf++']:>10.2f}")
    print("=" * 60)

    # Cập nhật lại cấu trúc JSON gốc
    data["metrics"]["vietnamese_to_khmer"] = new_metrics_fwd
    data["metrics"]["khmer_to_vietnamese"] = new_metrics_rev

    # Ghi đè cập nhật lại file JSON kết quả ban đầu
    print(f"\nĐang ghi lại kết quả mới vào file: {JSON_FILE_PATH}...")
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Hoàn tất cập nhật file JSON thành công!")

if __name__ == "__main__":
    main()