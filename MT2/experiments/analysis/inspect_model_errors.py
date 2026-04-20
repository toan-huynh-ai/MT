import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path("experiment_results")
FILES = {
    "Sailor2-8B": "sailor2_all_20260419_211517.json",
    "Gemma-SEA-LION-9B-IT": "gemma_sealion_all_20260419_174723.json",
    "Aya-101": "aya101_all_20260419_152724.json",
    "NLLB-200-3.3B": "nllb_all_20260419_005239.json",
}

WANTED = ["UNTRANSLATED", "CHINESE_LEAK", "ROMANIZED_LEFT", "FOREIGN_LEAK", "MISSING_OR_WRONG"]

for model, fname in FILES.items():
    data = json.load(open(BASE / fname, encoding="utf-8"))
    rows = data["per_sample"]
    print("=" * 100)
    print(model)
    shown = 0
    seen_types = set()
    for err_type in WANTED:
        for row in rows:
            errs = [e["type"] for e in row.get("eval", {}).get("errors", [])]
            if err_type in errs and err_type not in seen_types:
                print(f"[{err_type}]")
                print(f"  src: {row['source'][:100]}")
                print(f"  hyp: {row['hypothesis'][:160]}")
                print(f"  ref: {row['reference'][:160]}")
                print()
                shown += 1
                seen_types.add(err_type)
                break
        if shown >= 4:
            break
