"""Audit GPT-4o variety collapse per topic on the full 1856 sample run.

Evidence rule:
  - REF contains a Khmer-Krom / Vietnam-flavoured marker.
  - GPT-4o hypothesis does NOT contain that same marker (i.e. standardized
    toward Cambodian Khmer).

Outputs:
  - summary in console
  - results/topic_variety_collapse_evidence.json
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parents[2]
RESULTS = HERE / "results" / "gpt4o_full_1856.json"
OUT = HERE / "results" / "topic_variety_collapse_evidence.json"

# --- Extended Krom / Khmer-Vietnamese marker list ---
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


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    per = data["per_sample"]

    stats: dict[str, dict] = defaultdict(lambda: {
        "total": 0, "ref_has": 0, "dropped": 0,
        "cats": Counter(), "examples": [],
    })
    total_ref_has = 0
    total_dropped = 0
    cat_total_dropped: Counter = Counter()

    for r in per:
        topic = r.get("topic") or "(no topic / Q&A)"
        s = stats[topic]
        s["total"] += 1
        ref = r["reference"] or ""
        hyp = r.get("hyp_plain") or ""

        ref_has_krom = False
        dropped_cats = []
        for cat, pats in KROM_MARKERS.items():
            if has_any(ref, pats):
                ref_has_krom = True
                if not has_any(hyp, pats):
                    dropped_cats.append(cat)

        if ref_has_krom:
            s["ref_has"] += 1
            total_ref_has += 1
            if dropped_cats:
                s["dropped"] += 1
                total_dropped += 1
                for c in dropped_cats:
                    s["cats"][c] += 1
                    cat_total_dropped[c] += 1
                if len(s["examples"]) < 2:
                    s["examples"].append({
                        "source": r["source"][:180],
                        "reference": ref[:180],
                        "hyp_plain": hyp[:180],
                        "dropped_categories": dropped_cats,
                    })

    print("=" * 80)
    print(f"TỔNG: REF có marker Khmer-Việt trong "
          f"{total_ref_has}/1856 ({total_ref_has * 100 / 1856:.1f}%) mẫu")
    print(f"GPT-4o ĐÁNH RƠI marker trong "
          f"{total_dropped}/{max(total_ref_has, 1)} "
          f"({total_dropped * 100 / max(total_ref_has, 1):.0f}%) số đó")
    print()
    print("Phân bố loại marker bị đánh rơi:")
    for c, n in cat_total_dropped.most_common():
        print(f"  {c:<22} {n}")
    print()

    print("=" * 80)
    print("PHÂN BỐ THEO CHỦ ĐỀ (chỉ topic có ít nhất 1 bằng chứng)")
    print("=" * 80)
    print(f"{'Chủ đề':<50}{'Mẫu':>6}{'REF-Krom':>10}{'Rơi':>6}{'%':>6}")
    print("-" * 80)
    sorted_topics = sorted(stats.items(), key=lambda kv: -kv[1]["dropped"])
    topics_with_evidence = 0
    for topic, s in sorted_topics:
        if s["dropped"] == 0:
            continue
        topics_with_evidence += 1
        pct = f"{s['dropped'] * 100 / s['ref_has']:.0f}%" if s["ref_has"] else "-"
        print(f"{topic[:48]:<50}{s['total']:>6}{s['ref_has']:>10}{s['dropped']:>6}{pct:>6}")
    print("-" * 80)
    print(f"Chủ đề có ít nhất 1 bằng chứng: {topics_with_evidence}/{len(stats)}")

    dump = {
        "total_samples": 1856,
        "ref_with_krom_marker": total_ref_has,
        "gpt4o_dropped": total_dropped,
        "drop_rate_percent": round(
            total_dropped * 100 / max(total_ref_has, 1), 1
        ),
        "dropped_by_category": dict(cat_total_dropped),
        "per_topic": {
            t: {
                "total": s["total"],
                "ref_has_krom": s["ref_has"],
                "gpt4o_dropped": s["dropped"],
                "drop_rate": round(
                    s["dropped"] * 100 / max(s["ref_has"], 1), 1
                ),
                "categories_dropped": dict(s["cats"]),
                "examples": s["examples"],
            } for t, s in stats.items() if s["dropped"] > 0
        },
    }
    OUT.write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")
    print()
    print(f"Đã lưu: {OUT}")


if __name__ == "__main__":
    main()
