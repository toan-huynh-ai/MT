import sys
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Đảm bảo import được file convert_pdf_to_json.py nằm cùng thư mục
sys.path.insert(0, str(Path(__file__).parent))
from convert_pdf_to_json import convert_pdf_to_json

try:
    from openai import OpenAI
except ImportError:
    print("Error: Vui lòng chạy 'pip install openai'")
    sys.exit(1)

# Nạp file môi trường .env chứa API Key
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(f"Error: Không tìm thấy OPENAI_API_KEY trong file: {env_path}")
    sys.exit(1)

# Đường dẫn tới file PDF từ điển gốc của bạn
pdf_path = r"D:\Code\Python\Research\MachineTranslation\-Tu-dien-Khmer-Viet-KVDIC.pdf"
client = OpenAI(api_key=api_key)

print("=" * 60)
print("BẮT ĐẦU CHẠY THỬ NGHIỆM 10 TRANG ĐẦU TIÊN")
print("=" * 60)

start_time = time.time()

# Kiểm tra tổng số trang của tài liệu bằng PyMuPDF (fitz)
import fitz
try:
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    print(f"Tổng số trang phát hiện trong PDF: {total_pages}")
except Exception as e:
    print(f"Lỗi khi đọc file PDF: {e}")
    sys.exit(1)

print(f"Giới hạn cấu hình: Chỉ xử lý từ trang 1 đến trang 10\n")

# Gọi hàm xử lý chính, truyền tham số giới hạn max_pages=10
# Kết quả checkpoint và file output sẽ ghi ra thư mục hiện tại của bạn
output_filename = "test_output.json"
results = convert_pdf_to_json(pdf_path, client, output_filename, max_pages=386)

# Tính toán các chỉ số hiệu suất sau khi chạy xong
elapsed = time.time() - start_time
total_entries = sum(r.get("total_entries_found", 0) for r in results if isinstance(r, dict))

print("\n" + "=" * 60)
print("BÁO CÁO HIỆU SUẤT THỬ NGHIỆM")
print("=" * 60)
print(f"Số trang thực tế đã xử lý : {len(results)}")
print(f"Tổng số mục từ bóc tách được: {total_entries}")
print(f"Tổng thời gian thực thi     : {elapsed:.1f} giây")
if results:
    print(f"Thời gian trung bình / trang: {elapsed/len(results):.1f} giây")
print(f"File kết quả lưu tại        : {Path(output_filename).resolve()}")
print("=" * 60)