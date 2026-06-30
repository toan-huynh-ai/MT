import json
import os
import re
from collections import Counter

def load_khmer_dictionary(dict_path):
    """
    Đọc file từ điển và trích xuất tất cả các từ vựng tiếng Khmer làm từ khóa (Keys).
    Do tiếng Khmer dùng chữ Abugida, ta sẽ lọc các chuỗi ký tự thuộc dải Unicode của tiếng Khmer (\u1780-\u17FF).
    """
    khmer_words = set()
    khmer_pattern = re.compile(r'[\u1780-\u17FF]+')
    
    print(f"[*] Đang nạp từ điển từ: {dict_path}")
    with open(dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Tìm tất cả các từ Khmer xuất hiện ở đầu câu hoặc trong dòng giải nghĩa
            matches = khmer_pattern.findall(line)
            for word in matches:
                if len(word) > 1:  # Loại bỏ các ký tự phụ âm đơn lẻ đứng độc lập
                    khmer_words.add(word)
                    
    print(f"[+] Tổng số từ vựng Khmer độc nhất trích xuất được từ từ điển: {len(khmer_words)}")
    return khmer_words

def analyze_ground_truth_coverage(gt_path, dict_words):
    """
    Đọc tập Ground Truth, tách từ và tính toán tỷ lệ xuất hiện trong từ điển.
    """
    khmer_pattern = re.compile(r'[\u1780-\u17FF]+')
    all_gt_words = []
    
    print(f"[*] Đang đọc tập dữ liệu Ground Truth từ: {gt_path}")
    with open(gt_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            # Lấy chuỗi label chuẩn (tiếng Khmer)
            labels = item.get("label", [])
            for label in labels:
                matches = khmer_pattern.findall(label)
                all_gt_words.extend([w for w in matches if len(w) > 1])
                
    total_words_count = len(all_gt_words)
    unique_gt_words = set(all_gt_words)
    
    print(f"[+] Tổng số từ Khmer xuất hiện trong Ground Truth (tính cả lặp lại): {total_words_count}")
    print(f"[+] Tổng số từ Khmer độc nhất trong Ground Truth: {len(unique_gt_words)}")
    
    # Giao thoa dữ liệu: Tìm các từ trong Ground Truth CÓ XUẤT HIỆN trong từ điển
    matched_words = unique_gt_words.intersection(dict_words)
    missing_words = unique_gt_words.difference(dict_words)
    
    coverage_percentage = (len(matched_words) / len(unique_gt_words)) * 100
    
    print("\n" + "="*50)
    print("📊 KẾT QUẢ ĐỐI SÁNH NGÔN NGỮ HỌC")
    print("="*50)
    print(f"  - Số từ khớp (Matched Words): {len(matched_words)}")
    print(f"  - Số từ thiếu (Missing/Unlisted Words): {len(missing_words)}")
    print(f"  - TỶ LỆ PHỦ CỦA TỪ ĐIỂN (Coverage Rate): {coverage_percentage:.2f}%")
    print("="*50)
    
    # Thống kê thử một vài từ thiếu phổ biến nhất để anh xem xét
    word_counts = Counter(all_gt_words)
    sorted_missing = sorted([(w, word_counts[w]) for w in missing_words], key=lambda x: x[1], reverse=True)
    
    print("\n🔍 Top 10 từ xuất hiện nhiều trong Ground Truth nhưng từ điển KHÔNG CÓ (hoặc viết khác kiểu):")
    for word, count in sorted_missing[:10]:
        print(f"  * Từ: {word} (Xuất hiện {count} lần trong dataset)")

if __name__ == "__main__":
    # Anh cấu hình đường dẫn chính xác trên máy của anh nhé
    dict_file = r"D:\Code\Python\Research\MachineTranslation\-Tu-dien-Khmer-Viet-KVDIC.txt"
    gt_file = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\data\all_cleaned.jsonl"
    
    if os.path.exists(dict_file) and os.path.exists(gt_file):
        dict_vocabulary = load_khmer_dictionary(dict_file)
        analyze_ground_truth_coverage(gt_file, dict_vocabulary)
    else:
        print("[Lỗi] Vui lòng kiểm tra lại đường dẫn của file từ điển hoặc file Ground Truth.")