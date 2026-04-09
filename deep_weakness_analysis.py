"""Deep analysis: Find genuinely impactful LLM weaknesses for Vi-Khmer MT."""
import json
import sys
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("experiment_results/full_experiment_20260409_164322.json", "r", encoding="utf-8") as f:
    full = json.load(f)

with open("experiment_results/weakness_probe_20260408_163922.json", "r", encoding="utf-8") as f:
    weak = json.load(f)

with open("experiment_results/pilot_results_20260408_154436.json", "r", encoding="utf-8") as f:
    pilot = json.load(f)

KHMER_SCRIPT = re.compile(r'[\u1780-\u17FF\u19E0-\u19FF]')
KHMER_NUMERAL = re.compile(r'[\u17E0-\u17E9]')
ARABIC_NUMERAL = re.compile(r'[0-9]')

# ═════════════════════════════════════════════════════════════════
print("=" * 80)
print("ANALYSIS 1: SEMANTIC HALLUCINATION (not just wrong term, but WRONG MEANING)")
print("=" * 80)

for probe_name in ["food", "complex", "ritual", "kinship"]:
    for d in weak[probe_name]["details"]:
        src_lower = d["source"].lower()
        back_lower = d["back_translation"].lower()
        if ("cốm dẹp" in src_lower and "trái cây" in back_lower) or \
           ("bánh ống" in src_lower and "bánh mì" in back_lower) or \
           ("nùm bong" in src_lower and ("trái cây" in back_lower or "fruit" in back_lower)):
            print(f"\n  [{probe_name}] HALLUCINATION FOUND:")
            print(f"  SRC:  {d['source'][:120]}")
            print(f"  HYP:  {d['hypothesis'][:120]}")
            print(f"  BACK: {d['back_translation'][:120]}")

# ═════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("ANALYSIS 2: CKB-RAG REMAINING FAILURES (12 errors that CKB can't fix)")
print("=" * 80)

remaining_error_types = defaultdict(list)
for r in full["per_sample"]:
    for e in r["eval_kb"]["errors"]:
        remaining_error_types[e["type"]].append({
            "entity": e.get("entity", "N/A"),
            "source": r["source"][:80],
        })

for etype, cases in remaining_error_types.items():
    print(f"\n  {etype} ({len(cases)} cases):")
    for c in cases[:3]:
        print(f"    Entity: {c['entity']:30s} Source: {c['source'][:60]}")

# ═════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("ANALYSIS 3: NUMERAL SYSTEM (Arabic 123 vs Khmer ១២៣)")
print("=" * 80)

arabic_in_hyp = 0
khmer_num_in_hyp = 0
arabic_in_ref = 0
khmer_num_in_ref = 0

for r in full["per_sample"]:
    hyp = r["hyp_plain"]
    ref = r["reference"]
    if ARABIC_NUMERAL.search(hyp):
        arabic_in_hyp += 1
    if KHMER_NUMERAL.search(hyp):
        khmer_num_in_hyp += 1
    if ARABIC_NUMERAL.search(ref):
        arabic_in_ref += 1
    if KHMER_NUMERAL.search(ref):
        khmer_num_in_ref += 1

# Check pilot too
for d in pilot["exp1"]["details"]:
    hyp = d["hypothesis"]
    ref = d["reference"]
    if ARABIC_NUMERAL.search(hyp):
        arabic_in_hyp += 1
    if KHMER_NUMERAL.search(hyp):
        khmer_num_in_hyp += 1
    if ARABIC_NUMERAL.search(ref):
        arabic_in_ref += 1
    if KHMER_NUMERAL.search(ref):
        khmer_num_in_ref += 1

print(f"  GPT-4o output: Arabic numerals={arabic_in_hyp}, Khmer numerals={khmer_num_in_hyp}")
print(f"  References:    Arabic numerals={arabic_in_ref}, Khmer numerals={khmer_num_in_ref}")

# ═════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("ANALYSIS 4: ADEQUACY WITHOUT AUTHENTICITY — Cambodian style vs Krom style")
print("=" * 80)

krom_markers = ["ចា៎", "ចាស៎", "ម៉ែ", "ម៉ាក់"]
cambodia_markers = ["ចាស", "បាទ", "បាទ/ចាស"]

krom_in_ref = 0
krom_in_hyp = 0
cambodia_in_ref = 0
cambodia_in_hyp = 0

all_details = full["per_sample"]
for r in all_details:
    ref = r["reference"]
    hyp = r["hyp_plain"]
    for m in krom_markers:
        if m in ref:
            krom_in_ref += 1
        if m in hyp:
            krom_in_hyp += 1
    for m in cambodia_markers:
        if m in ref:
            cambodia_in_ref += 1
        if m in hyp:
            cambodia_in_hyp += 1

# Also check across ALL data
import json as j2
all_data = []
for fname in ["all_1.jsonl", "all_2.jsonl"]:
    with open(fname, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                all_data.append(j2.loads(line))

total_krom_in_data = 0
total_cambodia_in_data = 0
for d in all_data:
    for lbl in d.get("label", []):
        for m in krom_markers:
            if m in lbl:
                total_krom_in_data += 1
                break
        for m in cambodia_markers:
            if m in lbl:
                total_cambodia_in_data += 1
                break

print(f"  In full dataset (1856 samples):")
print(f"    Krom markers (ចា៎, ម៉ាក់...):     {total_krom_in_data} samples")
print(f"    Cambodia markers (ចាស, បាទ...):  {total_cambodia_in_data} samples")
print(f"  In experiment references ({len(all_details)} samples):")
print(f"    Krom markers in ref: {krom_in_ref}, in GPT output: {krom_in_hyp}")
print(f"    Cambodia markers in ref: {cambodia_in_ref}, in GPT output: {cambodia_in_hyp}")

# ═════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("ANALYSIS 5: TRANSLATION LENGTH — over-generation vs under-generation")
print("=" * 80)

for label, details, hyp_key in [
    ("Full exp (plain)", full["per_sample"], "hyp_plain"),
    ("Full exp (KB-RAG)", full["per_sample"], "hyp_kb"),
]:
    ratios = []
    for r in details:
        ref_len = len(r["reference"])
        hyp_len = len(r[hyp_key])
        if ref_len > 0:
            ratios.append(hyp_len / ref_len)

    avg = sum(ratios) / len(ratios)
    over = sum(1 for r in ratios if r > 1.3)
    under = sum(1 for r in ratios if r < 0.7)
    print(f"  {label}: avg_ratio={avg:.2f}, over(>1.3)={over}/{len(ratios)}, under(<0.7)={under}/{len(ratios)}")

# ═════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("ANALYSIS 6: SPEAKER LABEL CONSISTENCY in dialogue")
print("=" * 80)

speaker_patterns = {
    "ជនជាតិខ្មែរ៖": "Khmer speaker (standard)",
    "ជនជាតិខ្មែរ:": "Khmer speaker (colon variant)",
    "អ្នកសម្ភាសន៍៖": "Interviewer (standard)",
    "អ្នកសម្ភាស:": "Interviewer (truncated)",
    "អ្នកសារព័ត៌មាន៖": "Reporter/Journalist",
    "Khmer:": "Left as English",
    "អ្នកខ្មែរ:": "Khmer person (informal)",
}

ref_labels = defaultdict(int)
hyp_labels = defaultdict(int)

for r in full["per_sample"]:
    for pattern, name in speaker_patterns.items():
        if pattern in r["reference"]:
            ref_labels[name] += 1
        if pattern in r["hyp_plain"]:
            hyp_labels[name] += 1

print(f"  {'Speaker Pattern':<35} {'In Ref':>8} {'In GPT':>8}")
print(f"  {'-'*55}")
for name in set(list(ref_labels.keys()) + list(hyp_labels.keys())):
    print(f"  {name:<35} {ref_labels[name]:>8} {hyp_labels[name]:>8}")
