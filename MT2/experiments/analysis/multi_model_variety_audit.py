"""Compare variety-collapse patterns across 6 translation systems.

Systems:
  - GPT-4o (Azure, zero-shot plain prompt)
  - Aya-101 (CohereLabs, encoder-decoder)
  - NLLB-200-3.3B (Meta, encoder-decoder)
  - Llama-SEA-LION-v3.5-8B-R (causal LM, causal prompt)  -- likely broken on vi->km
  - Gemma-SEA-LION-v3-9B-IT (instruction tuned causal LM)
  - Sailor2-8B (instruction tuned causal LM)

Heuristic: for every sample, check whether the REF contains any Khmer-Vietnamese
(Krom) marker and whether the hypothesis drops it. Same marker list as the
GPT-4o audit.

We also compute output-health signals to distinguish real variety collapse
from broken output:
  - corpus chrF++ from the pre-computed metadata
  - fraction of samples whose hypothesis is < 20 chars or contains no Khmer
    character (a proxy for "the model did not actually produce Khmer")
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parents[2]
RESULTS = HERE / "results"
OUT = HERE / "results" / "multi_model_variety_compare.json"

MODELS = [
    ("GPT-4o",                   "gpt4o_full_1856.json",           "hyp_plain"),
    ("Aya-101",                  "aya101_full_1856.json",          "hypothesis"),
    ("NLLB-200-3.3B",            "nllb_full_1856.json",            "hypothesis"),
    ("Gemma-SEA-LION-v3-9B-IT",  "gemma_sealion_full_1856.json",   "hypothesis"),
    ("Llama-SEA-LION-v3.5-8B-R", "sealion_full_1856.json",         "hypothesis"),
    ("Sailor2-8B",               "sailor2_full_1856.json",         "hypothesis"),
]

KROM_MARKERS = {
    "kinship_colloq":    ["ម៉ែ", "ម៉ាក់", "ប៉ា"],
    "ethnonym_kinh":     ["គិញ"],
    "toponym_krom":      [
        "ទ្រីតុង", "ទ្រីតូន", "សុកត្រាំង", "ខេត្តឃ្លាំង",
        "ព្រះត្រពាំង", "ត្រាវិញ", "អានយ៉ាង", "គៀងយ៉ាង", "គៀនយ៉ាង",
        "មាត់ជ្រូក", "បាយ៉ង់", "ហូវហ្សាង", "កាម៉ៅ",
        "ក្រុងហូជីមិញ", "បាកលៀវ", "ឡុងអាន", "ផ្សារទីញបៀន",
    ],
    "food_krom":         [
        "ម៉ាំប្រហុក", "អំបុក", "នំបង់ខ្លាញ់", "នំបញ្ចុកទឹកសម្ល",
        "នំបំពង់ឫស្សី", "នំគម", "នំអន្សោម", "នំអន្សម",
        "នំខ្ញី", "បាយឡាំ",
    ],
    "boat_racing":       ["ទូកង", "ទូកអុំ", "ប្រណាំងទូកង", "ប្រណាំងទូកអុំ"],
    "festival_krom":     [
        "អកអំបុក", "បុណ្យអកអំបុក", "សែនដូនតា",
        "ពិធីបុណ្យកឋិនទាន", "បុណ្យភ្ជុំបិណ្ឌ",
    ],
    "krom_religious":    ["អ្នកតា", "ភូមិសង្គម", "ព្រះឥសូរ", "ព្រះឥសូ"],
    "vn_loanword":       ["អ៊ុយបាន", "ដែនដីសណ្ដរទន្លេមេគង្គ", "តំបន់មាត់ទន្លេ"],
    "krom_ethno_label":  ["ខ្មែរក្រោម", "ខ្មែរណាមបូ"],
    "nam_bo_vn_translit": ["ណាមបូ", "យុគី"],
}


def has_any(text: str, patterns: list[str]) -> bool:
    if not text:
        return False
    return any(p in text for p in patterns)


def count_khmer_chars(text: str) -> int:
    """Khmer Unicode block: U+1780 - U+17FF."""
    if not text:
        return 0
    return sum(1 for ch in text if 0x1780 <= ord(ch) <= 0x17FF)


def analyze(per_samples: list[dict], hyp_key: str) -> dict:
    total_ref_has = 0
    total_dropped = 0
    by_cat: Counter = Counter()
    ref_has_by_cat: Counter = Counter()
    broken_hyp = 0
    no_khmer_hyp = 0
    very_short_hyp = 0

    for r in per_samples:
        ref = r.get("reference") or ""
        hyp = r.get(hyp_key) or ""

        # Health signals on hypothesis
        kh = count_khmer_chars(hyp)
        if kh == 0:
            no_khmer_hyp += 1
        if len(hyp) < 20:
            very_short_hyp += 1
        if kh == 0 or len(hyp) < 20:
            broken_hyp += 1

        has_krom = False
        dropped = []
        for cat, pats in KROM_MARKERS.items():
            if has_any(ref, pats):
                ref_has_by_cat[cat] += 1
                has_krom = True
                if not has_any(hyp, pats):
                    dropped.append(cat)
        if has_krom:
            total_ref_has += 1
            if dropped:
                total_dropped += 1
                for c in dropped:
                    by_cat[c] += 1

    return {
        "n": len(per_samples),
        "ref_has_krom": total_ref_has,
        "dropped": total_dropped,
        "drop_rate": round(total_dropped * 100 / max(total_ref_has, 1), 1),
        "drop_by_category": dict(by_cat),
        "ref_by_category": dict(ref_has_by_cat),
        "health": {
            "hyp_no_khmer_char": no_khmer_hyp,
            "hyp_very_short": very_short_hyp,
            "hyp_broken_any": broken_hyp,
        },
    }


def load_per_sample(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    # Support both GPT-4o and local-model JSON layouts
    return data.get("per_sample", [])


def main() -> None:
    all_results: dict[str, dict] = {}
    for name, fname, hyp_key in MODELS:
        path = RESULTS / fname
        if not path.exists():
            print(f"[skip] Missing file: {fname}")
            continue
        try:
            per = load_per_sample(path)
            stats = analyze(per, hyp_key)
            meta = json.loads(path.read_text(encoding="utf-8")).get("metadata", {})
            corpus_results = (
                json.loads(path.read_text(encoding="utf-8")).get("corpus_results")
                or json.loads(path.read_text(encoding="utf-8")).get("main_results", {}).get("all_plain", {})
            )
            stats["model"] = name
            stats["source_file"] = fname
            stats["corpus_chrf"] = corpus_results.get("chrf++") if corpus_results else None
            stats["corpus_bleu"] = corpus_results.get("bleu") if corpus_results else None
            stats["meta_model"] = meta.get("model")
            all_results[name] = stats
        except Exception as e:
            print(f"[error] {name}: {e}")

    # Print comparison
    print(f"\n{'Model':<28}{'N':>6}{'chrF++':>8}{'REF-Krom':>10}{'Drop':>6}{'Rate':>7}{'Broken':>8}")
    print("-" * 76)
    for name, s in all_results.items():
        chrf = f"{s['corpus_chrf']:.2f}" if s.get("corpus_chrf") else "?"
        print(
            f"{name:<28}{s['n']:>6}{chrf:>8}"
            f"{s['ref_has_krom']:>10}{s['dropped']:>6}{s['drop_rate']:>6}%"
            f"{s['health']['hyp_broken_any']:>8}"
        )

    # Print category breakdown
    print("\nDropped count by category (per model)")
    cats = sorted(KROM_MARKERS.keys())
    header = f"{'Category':<22}"
    for name in all_results:
        header += f"{name[:12]:>14}"
    print(header)
    print("-" * len(header))
    for cat in cats:
        row = f"{cat:<22}"
        for name, s in all_results.items():
            row += f"{s['drop_by_category'].get(cat, 0):>14}"
        print(row)

    OUT.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
