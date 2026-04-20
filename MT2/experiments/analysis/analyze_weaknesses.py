"""Deep qualitative analysis of GPT-4o weakness probes."""
import json
import sys
import sacrebleu

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("experiment_results/weakness_probe_20260408_163922.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 90)
print("CHRF++ SCORE BY PROBE (lower = weaker)")
print("=" * 90)
probes = sorted(data.items(), key=lambda x: x[1]["scores"]["chrf++"])
for name, res in probes:
    print(f"  {name:<20} chrF++={res['scores']['chrf++']:6.2f}  (n={res['n_samples']})")

for probe_name in ["complex", "kinship", "food", "colloquial"]:
    print(f"\n{'=' * 90}")
    print(f"DETAILED: {probe_name.upper()} (chrF++={data[probe_name]['scores']['chrf++']})")
    print(f"{'=' * 90}")

    for i, d in enumerate(data[probe_name]["details"]):
        sent_chrf = sacrebleu.sentence_chrf(d["hypothesis"], [d["reference"]], word_order=2)

        print(f"\n--- Sample {i+1} (chrF++={sent_chrf.score:.1f}) ---")
        print(f"VI:   {d['source'][:150]}")
        print(f"REF:  {d['reference'][:150]}")
        print(f"HYP:  {d['hypothesis'][:150]}")
        print(f"BACK: {d['back_translation'][:150]}")

        analysis = d.get("analysis", {})
        if isinstance(analysis, dict):
            if "errors" in analysis:
                for err in analysis["errors"]:
                    print(f"  ERR: [{err.get('severity','?')}] {err.get('type','?')}: {err.get('detail','?')[:100]}")
            if "cultural_accuracy" in analysis:
                print(f"  Cultural: {analysis['cultural_accuracy']}")
            if "dialect_note" in analysis:
                print(f"  Dialect: {analysis['dialect_note']}")
            if "overall_quality" in analysis:
                print(f"  Quality: {analysis['overall_quality']}")
        elif isinstance(analysis, str):
            print(f"  Analysis: {analysis[:200]}")

# Cross-probe error type summary
print(f"\n{'=' * 90}")
print("CROSS-PROBE ERROR SUMMARY")
print(f"{'=' * 90}")

all_errors = {}
all_cultural = {}
all_dialect = {}
for probe_name, res in data.items():
    probe_errors = []
    probe_cultural = []
    probe_dialect = []
    for d in res["details"]:
        a = d.get("analysis", {})
        if isinstance(a, dict):
            for err in a.get("errors", []):
                probe_errors.append(err.get("type", "unknown"))
            probe_cultural.append(a.get("cultural_accuracy", "unknown"))
            probe_dialect.append(a.get("dialect_note", "unknown"))
    all_errors[probe_name] = probe_errors
    all_cultural[probe_name] = probe_cultural
    all_dialect[probe_name] = probe_dialect

print("\nError types per probe:")
for probe, errors in all_errors.items():
    if errors:
        from collections import Counter
        c = Counter(errors)
        print(f"  {probe}: {dict(c)}")
    else:
        print(f"  {probe}: (no structured errors)")

print("\nCultural accuracy per probe:")
for probe, ca in all_cultural.items():
    from collections import Counter
    c = Counter(ca)
    print(f"  {probe}: {dict(c)}")

print("\nDialect per probe:")
for probe, dl in all_dialect.items():
    from collections import Counter
    c = Counter(dl)
    print(f"  {probe}: {dict(c)}")
