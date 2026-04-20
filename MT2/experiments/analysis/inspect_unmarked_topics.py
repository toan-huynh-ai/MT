"""Inspect REF vs GPT-4o hypothesis on topics that produced NO variety-collapse
evidence in the earlier audit. We want to know:
  - Is REF really standard Cambodian Khmer on these topics?
  - Or does REF use Khmer-Vietnamese markers we didn't include?
  - Or does GPT-4o paraphrase differently even when staying in standard form?

Prints a side-by-side sample list for 5 selected topics.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parents[2]
RESULTS = HERE / "results" / "gpt4o_full_1856.json"

# Topics that produced 0 variety-collapse evidence in earlier audit.
TARGET_TOPICS = [
    "When death occurs",
    "Process of dealing with corpse",
    "Traditional medicine",
    "Musical instruments",
    "Poetry or similar literature",
]
PER_TOPIC = 5


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    per = data["per_sample"]
    buckets: dict[str, list] = {t: [] for t in TARGET_TOPICS}
    for r in per:
        t = r.get("topic") or ""
        if t in buckets and len(buckets[t]) < PER_TOPIC:
            buckets[t].append(r)

    for topic in TARGET_TOPICS:
        rows = buckets[topic]
        print("=" * 90)
        print(f"TOPIC: {topic}   (showing {len(rows)} samples)")
        print("=" * 90)
        for i, r in enumerate(rows, 1):
            vi = (r.get("source") or "").strip()
            ref = (r.get("reference") or "").strip()
            hyp = (r.get("hyp_plain") or "").strip()
            print(f"\n-- Sample {i} --")
            print(f"VI : {vi[:260]}")
            print(f"REF: {ref[:260]}")
            print(f"HYP: {hyp[:260]}")
        print()


if __name__ == "__main__":
    main()
