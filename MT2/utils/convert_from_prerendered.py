import json
import time
import base64
from pathlib import Path
import io
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.insert(0, str(Path(__file__).parent))
from convert_pdf_to_json import (
    call_gpt5, build_system_prompt, build_page_prompt,
    parse_json_response, get_checkpoint_path, load_checkpoint, save_checkpoint
)

PARALLEL_WORKERS = 30


def load_prerendered_chunks(images_dir, page_number):
    images_dir = Path(images_dir)
    with open(images_dir / "metadata.json", "r") as f:
        metadata = json.load(f)

    page_meta = next((p for p in metadata["pages"] if p["page_number"] == page_number), None)
    if not page_meta:
        raise ValueError(f"Page {page_number} not found in metadata")

    base64_list = []
    for chunk_file in page_meta["chunk_files"]:
        with Image.open(images_dir / chunk_file) as img:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            base64_list.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))
    return base64_list


def process_one_page(images_dir, client, system_prompt, page_num_1based):
    img_base64_list = load_prerendered_chunks(images_dir, page_num_1based)
    response = call_gpt5(client, system_prompt, build_page_prompt(page_num_1based), img_base64_list)

    if not response.strip():
        print(f"  [FAIL] Page {page_num_1based}: empty response", flush=True)
        return None

    try:
        page_data = parse_json_response(response)
    except json.JSONDecodeError as e:
        print(f"  [FAIL] Page {page_num_1based}: JSON error {str(e)[:80]}", flush=True)
        return None

    page_data["page_number"] = page_num_1based
    if isinstance(page_data.get("entries"), list):
        page_data["total_entries_found"] = len(page_data["entries"])

    print(f"  [OK] Page {page_num_1based}: {page_data.get('total_entries_found', 0)} entries", flush=True)
    return page_data


def convert_from_prerendered(images_dir, client, output_path, max_pages=None, start_page=None):
    images_dir = Path(images_dir)
    with open(images_dir / "metadata.json", "r") as f:
        metadata = json.load(f)

    total_available = len(metadata["pages"])
    total_pages = min(total_available, max_pages) if max_pages else total_available

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint_path = get_checkpoint_path(output_path)
    checkpoint = load_checkpoint(checkpoint_path)

    if start_page is not None:
        current_start = max(1, start_page)
        all_results = []
    else:
        # checkpoint last_page is 0-based (from original convert_pdf_to_json.py)
        last_done_0based = checkpoint.get("last_page", -1)
        current_start = last_done_0based + 2  # convert to 1-based next page
        all_results = checkpoint.get("results", [])
        if current_start > 1:
            print(f"Resuming from page {current_start}/{total_pages} (checkpoint: {len(all_results)} pages done)")

    system_prompt = build_system_prompt()
    pages_to_do = list(range(current_start, total_pages + 1))

    for batch_start in range(0, len(pages_to_do), PARALLEL_WORKERS):
        batch = pages_to_do[batch_start: batch_start + PARALLEL_WORKERS]
        print(f"\nBatch: pages {batch[0]}-{batch[-1]}", flush=True)

        batch_results = {}
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            futures = {
                executor.submit(process_one_page, images_dir, client, system_prompt, p): p
                for p in batch
            }
            for future in as_completed(futures):
                p = futures[future]
                try:
                    result = future.result()
                    if result:
                        batch_results[p] = result
                except Exception as e:
                    print(f"  [FAIL] Page {p}: {str(e)[:120]}", flush=True)

        # Append results in order
        for p in batch:
            if p in batch_results:
                all_results.append(batch_results[p])

        # Save checkpoint after each batch (0-based last page for compatibility)
        last_page_0based = batch[-1] - 1
        save_checkpoint(checkpoint_path, last_page_0based, all_results)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(all_results)} pages saved to: {output_path}", flush=True)
    return all_results


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from openai import OpenAI

    if len(sys.argv) < 3:
        print("Usage: python convert_from_prerendered.py <images_dir> <output_json> [max_pages]")
        sys.exit(1)

    img_dir = sys.argv[1]
    out_json = sys.argv[2]
    max_p = int(sys.argv[3]) if len(sys.argv) > 3 else None

    load_dotenv(Path(__file__).parent.parent / ".env")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    t0 = time.time()
    results = convert_from_prerendered(img_dir, client, out_json, max_p)
    elapsed = time.time() - t0

    if results:
        print(f"Avg: {elapsed/len(results):.1f}s/page, Total: {elapsed:.0f}s")
