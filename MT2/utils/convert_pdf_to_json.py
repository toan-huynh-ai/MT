import json
import time
import base64
import unicodedata
from pathlib import Path
import sys
import io

import fitz  # PyMuPDF
from PIL import Image, ImageOps


# =========================
# CONFIG
# =========================

MODEL_NAME = "gpt-5"

# Tăng DPI để OCR Khmer rõ hơn
IMAGE_DPI = 500

# Chia mỗi trang thành nhiều ảnh nhỏ hơn để model nhìn chữ rõ hơn
PAGE_NUM_SPLITS = 3
PAGE_SPLIT_OVERLAP = 120

DEBUG_RENDERED_PAGES = True


# =========================
# API CALL
# =========================

def call_gpt5(client, system_prompt, prompt_text, img_base64_list, max_retries=3):
    """
    Call OpenAI Responses API with text + multiple image chunks.
    """

    content = [
        {
            "type": "input_text",
            "text": prompt_text
        }
    ]

    for img_base64 in img_base64_list:
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{img_base64}",
                "detail": "high"
            }
        )

    for attempt in range(max_retries):
        try:
            resp = client.responses.create(
                model=MODEL_NAME,
                instructions=system_prompt,
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
            )

            return resp.output_text or ""

        except KeyboardInterrupt:
            raise

        except Exception as e:
            wait = 5 * (2 ** attempt)
            print(
                f"    [Retry {attempt + 1}/{max_retries}] "
                f"{str(e)[:200]}... wait {wait}s",
                flush=True
            )
            time.sleep(wait)

    return ""


# =========================
# PDF IMAGE RENDER
# =========================

def crop_whitespace_pil(img, padding=30):
    """
    Crop white margins from a PIL image.
    """

    gray = img.convert("L")
    inverted = ImageOps.invert(gray)
    bbox = inverted.getbbox()

    if not bbox:
        return img

    left, top, right, bottom = bbox

    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)

    return img.crop((left, top, right, bottom))


def split_image_vertically(img, num_splits=3, overlap=120):
    """
    Split one tall page image into vertical chunks.
    overlap helps avoid cutting lines/entries in half.
    """

    chunks = []
    width, height = img.size

    if num_splits <= 1:
        return [img]

    chunk_height = height // num_splits

    for i in range(num_splits):
        top = max(0, i * chunk_height - overlap)
        bottom = min(height, (i + 1) * chunk_height + overlap)

        if i == num_splits - 1:
            bottom = height

        chunk = img.crop((0, top, width, bottom))
        chunks.append(chunk)

    return chunks


def pil_image_to_base64_png(img):
    """
    Convert PIL image to base64 PNG string.
    """

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def pdf_page_to_base64_images(pdf_path, page_num, debug_dir=None, num_splits=PAGE_NUM_SPLITS):
    """
    Render one PDF page to high-DPI PNG, crop whitespace, split into chunks,
    and return list of base64 images.
    page_num is zero-based.
    """

    doc = fitz.open(str(pdf_path))

    try:
        page = doc[page_num]
        pix = page.get_pixmap(dpi=IMAGE_DPI, alpha=False)
        img_data = pix.tobytes("png")

    finally:
        doc.close()

    img = Image.open(io.BytesIO(img_data)).convert("RGB")

    # Crop useless white margins
    cropped_img = crop_whitespace_pil(img, padding=30)

    # Split into chunks for better OCR
    chunks = split_image_vertically(
        cropped_img,
        num_splits=num_splits,
        overlap=PAGE_SPLIT_OVERLAP
    )

    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)

        # Save raw rendered full page
        img.save(debug_path / f"page_{page_num + 1:04d}_raw_{IMAGE_DPI}dpi.png")

        # Save cropped full page
        cropped_img.save(debug_path / f"page_{page_num + 1:04d}_full_cropped.png")

        # Save chunks
        for idx, chunk in enumerate(chunks, start=1):
            chunk.save(debug_path / f"page_{page_num + 1:04d}_chunk_{idx}.png")

    return [pil_image_to_base64_png(chunk) for chunk in chunks]


# =========================
# CHECKPOINT
# =========================

def get_checkpoint_path(output_path):
    output_file = Path(output_path)
    return output_file.parent / f".{output_file.stem}_checkpoint.json"


def load_checkpoint(checkpoint_path):
    if checkpoint_path and checkpoint_path.exists():
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "last_page": -1,
        "results": []
    }


def save_checkpoint(checkpoint_path, last_page, results):
    if not checkpoint_path:
        return

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "last_page": last_page,
                "results": results
            },
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================
# JSON UTILS
# =========================

def normalize_unicode_nfc(obj):
    """
    Recursively normalize all strings in JSON object to Unicode NFC.
    """

    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)

    if isinstance(obj, list):
        return [normalize_unicode_nfc(x) for x in obj]

    if isinstance(obj, dict):
        return {
            normalize_unicode_nfc(k): normalize_unicode_nfc(v)
            for k, v in obj.items()
        }

    return obj


def clean_json_response(text):
    """
    Remove markdown fences and keep only JSON-looking content.
    """

    if not text:
        return ""

    clean = text.strip()

    # Remove markdown code fences if present
    if clean.startswith("```"):
        lines = clean.splitlines()

        # Remove first fence
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        # Remove last fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        clean = "\n".join(lines).strip()

    # If model accidentally adds text before/after JSON object
    first_brace = clean.find("{")
    last_brace = clean.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean = clean[first_brace:last_brace + 1]

    return clean


def parse_json_response(response_text):
    clean_response = clean_json_response(response_text)
    data = json.loads(clean_response)
    data = normalize_unicode_nfc(data)
    return data


# =========================
# PROMPTS
# =========================

def build_system_prompt():
    return """Bạn là hệ thống OCR và cấu trúc hóa từ điển Khmer - Việt.

Nhiệm vụ của bạn:
- Đọc DUY NHẤT nội dung nhìn thấy trong ảnh trang PDF được gửi kèm.
- Chuyển nội dung nhìn thấy thành JSON hợp lệ.
- Không dùng kiến thức ngoài ảnh.
- Không tự bịa mục từ, nghĩa, ví dụ hoặc ghi chú.
- Không copy ví dụ/schema trong prompt vào kết quả.
- Giữ đúng thứ tự mục từ từ trên xuống dưới.
- Với tiếng Khmer, giữ nguyên tối đa chữ chính, dấu, nguyên âm, phụ âm chân và ký tự nhìn thấy được.
- Nếu chữ không chắc, vẫn chép phần đọc được và đánh dấu uncertain_text = true.
- Không tự sửa chính tả Khmer/Vietnamese nếu không chắc chắn từ ảnh.
- Chuẩn hóa toàn bộ text Unicode NFC.
- Chỉ trả về JSON thuần, không Markdown, không giải thích.
"""


def build_page_prompt(page_number):
    return f"""
Hãy OCR trang từ điển Khmer - Việt trong ảnh đính kèm.

Lưu ý:
- Trang này có thể được gửi dưới dạng nhiều ảnh nhỏ liên tiếp.
- Hãy xem tất cả ảnh được gửi trong request như các phần liên tiếp của cùng một trang.
- Không được tạo entry trùng lặp do vùng overlap giữa các ảnh.
- Nếu một entry xuất hiện ở vùng giao giữa hai ảnh, chỉ ghi entry đó một lần.

Quy tắc đọc layout:
1. Mỗi số thứ tự ở cột trái là một mục từ mới.
2. Dòng có số thứ tự thường chứa:
   - entry_number
   - từ/cụm từ Khmer chính
   - từ loại trong ngoặc nếu có
   - nghĩa tiếng Việt ở cột phải
3. Các dòng ngay bên dưới không có số thứ tự là dòng con của mục từ trước đó.
4. Cột trái thường là tiếng Khmer.
5. Cột phải thường là nghĩa tiếng Việt.
6. Nếu thấy "ví dụ:", "vd:", "ឧ." hoặc phần tương đương thì đưa vào examples.
7. Nếu một dòng con chỉ là cụm Khmer + nghĩa Việt tương ứng thì đưa vào sub_entries.
8. Nếu không có dữ liệu cho field nào thì dùng null hoặc [].
9. Không được tạo dữ liệu không nhìn thấy trong ảnh.
10. Không sửa/chỉnh chính tả dựa trên suy đoán ngoại ảnh.
11. Nếu không chắc chữ nào, đặt uncertain_text = true cho entry tương ứng.
12. total_entries_found phải bằng số lượng entry có số thứ tự nhìn thấy trên trang.

Trả về JSON đúng cấu trúc sau:

{{
  "page_number": {page_number},
  "total_entries_found": 0,
  "entries": [
    {{
      "entry_number": 1,
      "khmer_headword": "",
      "word_class": null,
      "main_vietnamese_meaning": "",
      "sub_entries": [
        {{
          "khmer_text": "",
          "vietnamese_text": "",
          "type": "continuation"
        }}
      ],
      "examples": [
        {{
          "khmer_text": "",
          "vietnamese_text": ""
        }}
      ],
      "uncertain_text": false,
      "notes": null
    }}
  ]
}}
"""


# =========================
# MAIN CONVERSION
# =========================

def convert_pdf_to_json(pdf_path, client, output_path=None, max_pages=None, start_page=None):
    """
    Convert PDF dictionary pages to JSON.

    Args:
        pdf_path: path to PDF file
        client: OpenAI client
        output_path: output JSON path
        max_pages: max number of pages to process
        start_page: optional 1-based start page. If None, use checkpoint.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if output_path is None:
        output_path = "output.json"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint_path = get_checkpoint_path(output_path)
    checkpoint = load_checkpoint(checkpoint_path)

    doc = fitz.open(str(pdf_path))
    total_pdf_pages = len(doc)
    doc.close()

    total_pages_to_process = min(total_pdf_pages, max_pages) if max_pages else total_pdf_pages

    if start_page is not None:
        # User gives 1-based page number
        current_start_page = max(0, start_page - 1)
        all_results = []
        print(f"Starting from user-defined page {current_start_page + 1}", flush=True)
    else:
        current_start_page = checkpoint.get("last_page", -1) + 1
        all_results = checkpoint.get("results", [])

        if current_start_page > 0:
            print(
                f"Resuming from page {current_start_page + 1}/{total_pages_to_process}...",
                flush=True
            )

    system_prompt = build_system_prompt()

    debug_dir = None
    if DEBUG_RENDERED_PAGES:
        debug_dir = output_path.parent / f"{output_path.stem}_debug_pages"

    for page_num in range(current_start_page, total_pages_to_process):
        page_number_1based = page_num + 1

        print(
            f"\nProcessing page {page_number_1based}/{total_pages_to_process}...",
            flush=True
        )

        try:
            img_base64_list = pdf_page_to_base64_images(
                pdf_path,
                page_num,
                debug_dir=debug_dir,
                num_splits=PAGE_NUM_SPLITS
            )

            print(
                f"  Rendered {len(img_base64_list)} image chunks "
                f"at {IMAGE_DPI} DPI",
                flush=True
            )

            prompt_text = build_page_prompt(page_number_1based)

            response = call_gpt5(
                client=client,
                system_prompt=system_prompt,
                prompt_text=prompt_text,
                img_base64_list=img_base64_list
            )

            if not response.strip():
                print("  [FAIL] Empty response", flush=True)
                continue

            try:
                page_data = parse_json_response(response)

            except json.JSONDecodeError as e:
                print(f"  [FAIL] JSON parse error: {str(e)[:120]}", flush=True)

                # Save raw failed response for debugging
                failed_dir = output_path.parent / f"{output_path.stem}_failed_responses"
                failed_dir.mkdir(parents=True, exist_ok=True)
                failed_file = failed_dir / f"page_{page_number_1based:04d}_raw.txt"

                with open(failed_file, "w", encoding="utf-8") as f:
                    f.write(response)

                print(f"  Raw response saved to: {failed_file}", flush=True)
                continue

            # Validate page number
            returned_page = page_data.get("page_number")
            if returned_page != page_number_1based:
                print(
                    f"  [WARN] Model returned page_number={returned_page}, "
                    f"expected {page_number_1based}. Overriding.",
                    flush=True
                )
                page_data["page_number"] = page_number_1based

            # Validate total_entries_found
            entries = page_data.get("entries", [])
            if isinstance(entries, list):
                actual_count = len(entries)
                reported_count = page_data.get("total_entries_found")

                if reported_count != actual_count:
                    print(
                        f"  [WARN] total_entries_found={reported_count}, "
                        f"actual entries={actual_count}. Overriding.",
                        flush=True
                    )
                    page_data["total_entries_found"] = actual_count

                if actual_count <= 3:
                    print(
                        "  [WARN] Very few entries found. "
                        "Check rendered page image and OCR quality.",
                        flush=True
                    )

            all_results.append(page_data)

            print(
                f"  [OK] Extracted {page_data.get('total_entries_found', 0)} entries",
                flush=True
            )

            # Save checkpoint after every successful page
            save_checkpoint(checkpoint_path, page_num, all_results)

            # Also write output after every page for safety
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Checkpoint already saved for completed pages.", flush=True)
            raise

        except Exception as e:
            print(
                f"  [FAIL] Error processing page {page_number_1based}: {str(e)[:200]}",
                flush=True
            )
            continue

    # Final save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Results saved to: {output_path}", flush=True)

    if DEBUG_RENDERED_PAGES:
        print(f"Rendered page images saved to: {debug_dir}", flush=True)

    return all_results


# =========================
# CLI
# =========================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python convert_pdf_to_json.py <pdf_path> [output_json_path] [max_pages]")
        print()
        print("Examples:")
        print("  python convert_pdf_to_json.py dictionary.pdf output.json")
        print("  python convert_pdf_to_json.py dictionary.pdf output_10pages.json 10")
        sys.exit(1)

    pdf_file_path = sys.argv[1]
    output_json_path = sys.argv[2] if len(sys.argv) > 2 else "output.json"
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else None

    try:
        from openai import OpenAI
        openai_client = OpenAI()
    except ImportError:
        print("Error: OpenAI client not available.")
        print("Install with:")
        print("  pip install openai")
        sys.exit(1)

    convert_pdf_to_json(
        pdf_path=pdf_file_path,
        client=openai_client,
        output_path=output_json_path,
        max_pages=max_pages
    )


if __name__ == "__main__":
    main()