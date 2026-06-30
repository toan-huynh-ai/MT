import json
from pathlib import Path
import fitz
from PIL import Image, ImageOps
import io

IMAGE_DPI = 500
PAGE_NUM_SPLITS = 3
PAGE_SPLIT_OVERLAP = 120


def crop_whitespace_pil(img, padding=30):
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


def prerender_all_pages(pdf_path, output_dir, max_pages=None):
    """
    Pre-render tất cả trang PDF thành PNG chunks và lưu vào thư mục.
    Trả về metadata JSON mapping page -> list of chunk files.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    pages_to_render = min(total_pages, max_pages) if max_pages else total_pages

    metadata = {"pages": []}

    print(f"Pre-rendering {pages_to_render} pages at {IMAGE_DPI} DPI...")

    for page_num in range(pages_to_render):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=IMAGE_DPI, alpha=False)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data)).convert("RGB")

        cropped_img = crop_whitespace_pil(img, padding=30)
        chunks = split_image_vertically(cropped_img, num_splits=PAGE_NUM_SPLITS, overlap=PAGE_SPLIT_OVERLAP)

        chunk_files = []
        for idx, chunk in enumerate(chunks):
            chunk_filename = f"page_{page_num + 1:04d}_chunk_{idx + 1}.png"
            chunk_path = output_dir / chunk_filename
            chunk.save(chunk_path)
            chunk_files.append(chunk_filename)

        metadata["pages"].append({
            "page_number": page_num + 1,
            "chunk_files": chunk_files
        })

        if (page_num + 1) % 10 == 0:
            print(f"  Rendered {page_num + 1}/{pages_to_render} pages")

    doc.close()

    # Save metadata
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nDone! Images saved to: {output_dir}")
    print(f"Metadata saved to: {metadata_path}")
    return metadata


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python prerender_pdf_images.py <pdf_path> <output_dir> [max_pages]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    out_dir = sys.argv[2]
    max_p = int(sys.argv[3]) if len(sys.argv) > 3 else None

    prerender_all_pages(pdf_file, out_dir, max_p)
