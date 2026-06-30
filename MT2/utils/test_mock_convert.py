import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Mock GPT response
def mock_gpt5_response(page_num):
    return json.dumps({
        "page_number": page_num + 1,
        "total_entries_found": 3,
        "dictionary_entries": [
            {
                "entry_number": 1,
                "khmer_term": "ក",
                "word_class": "ន.",
                "vietnamese_meaning": "cổ",
                "context_examples": [
                    {"phrase_khmer": "កដប", "phrase_vietnamese": "cổ chai"},
                    {"phrase_khmer": "កអាវ", "phrase_vietnamese": "cổ áo"}
                ],
                "cultural_notes": None
            },
            {
                "entry_number": 2,
                "khmer_term": "ក",
                "word_class": "កិ.",
                "vietnamese_meaning": "tạo, tạo dựng",
                "context_examples": [
                    {"phrase_khmer": "កភូមិ", "phrase_vietnamese": "lập ấp"}
                ],
                "cultural_notes": "Khmer Krom Nam Bộ"
            },
            {
                "entry_number": 3,
                "khmer_term": "កា",
                "word_class": "វិ.",
                "vietnamese_meaning": "mặt",
                "context_examples": [],
                "cultural_notes": None
            }
        ]
    })

print("=" * 60)
print("MOCK TEST: 10 Pages")
print("=" * 60)

start_time = time.time()
all_results = []
checkpoint_file = Path("test_mock_checkpoint.json")

for page in range(10):
    print(f"Processing page {page + 1}/10...", flush=True)
    time.sleep(0.5)  # Simulate API delay

    response = mock_gpt5_response(page)
    page_data = json.loads(response)
    all_results.append(page_data)
    print(f"  [OK] Extracted {page_data['total_entries_found']} entries")

elapsed = time.time() - start_time
total_entries = sum(r.get("total_entries_found", 0) for r in all_results)

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Pages processed: {len(all_results)}")
print(f"Total entries: {total_entries}")
print(f"Total time: {elapsed:.2f}s")
print(f"Avg per page: {elapsed/len(all_results):.2f}s")
print(f"Output file: test_mock_output.json")

with open("test_mock_output.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
print("=" * 60)
