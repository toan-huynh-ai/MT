"""Qualitative analysis of pilot experiment results."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("experiment_results/pilot_results_20260408_154436.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 80)
print("QUALITATIVE EXAMPLES — Exp 1 (Zero-shot)")
print("=" * 80)
for d in data["exp1"]["details"][:5]:
    src = d["source"][:120]
    ref = d["reference"][:120]
    hyp = d["hypothesis"][:120]
    ents = d["cultural_entities"]
    print(f"\nSource:     {src}")
    print(f"Reference:  {ref}")
    print(f"Hypothesis: {hyp}")
    print(f"Entities:   {ents}")
    print("-" * 60)

print("\n" + "=" * 80)
print("QUALITATIVE EXAMPLES — Exp 3 (Context Effects)")
print("=" * 80)
for d in data["exp3"]["details"][:5]:
    print(f"\nTopic: {d['topic']} | Context turns: {d['n_context_turns']}")
    print(f"Source:       {d['source'][:120]}")
    print(f"Reference:    {d['reference'][:120]}")
    print(f"Isolated:     {d['hyp_isolated'][:120]}")
    print(f"With context: {d['hyp_with_context'][:120]}")
    print("-" * 60)

print("\n" + "=" * 80)
print("QUALITATIVE EXAMPLES — Exp 2 (Few-shot)")
print("=" * 80)
for d in data["exp2"]["details"][:5]:
    print(f"\nTopic: {d['topic']}")
    print(f"Source:    {d['source'][:120]}")
    print(f"Reference: {d['reference'][:120]}")
    print(f"Random:    {d['hyp_random_shot'][:120]}")
    print(f"Matched:   {d['hyp_topic_matched'][:120]}")
    print("-" * 60)

print("\n" + "=" * 80)
print("LENGTH ANALYSIS")
print("=" * 80)

exp1_details = data["exp1"]["details"]
hyp_lens = [len(d["hypothesis"]) for d in exp1_details]
ref_lens = [len(d["reference"]) for d in exp1_details]
print(f"Exp1 zero-shot: avg hyp={sum(hyp_lens)/len(hyp_lens):.0f} chars, avg ref={sum(ref_lens)/len(ref_lens):.0f} chars")

exp3_details = data["exp3"]["details"]
iso_lens = [len(d["hyp_isolated"]) for d in exp3_details]
ctx_lens = [len(d["hyp_with_context"]) for d in exp3_details]
ref3_lens = [len(d["reference"]) for d in exp3_details]
print(f"Exp3 isolated:  avg hyp={sum(iso_lens)/len(iso_lens):.0f} chars, avg ref={sum(ref3_lens)/len(ref3_lens):.0f} chars")
print(f"Exp3 context:   avg hyp={sum(ctx_lens)/len(ctx_lens):.0f} chars, avg ref={sum(ref3_lens)/len(ref3_lens):.0f} chars")

# Per-sample chrF comparison for Exp 3
import sacrebleu
print("\n" + "=" * 80)
print("PER-SAMPLE chrF++ — Exp 3 (Isolated vs Context)")
print("=" * 80)
for d in exp3_details:
    iso_chrf = sacrebleu.sentence_chrf(d["hyp_isolated"], [d["reference"]], word_order=2)
    ctx_chrf = sacrebleu.sentence_chrf(d["hyp_with_context"], [d["reference"]], word_order=2)
    delta = ctx_chrf.score - iso_chrf.score
    marker = "▲" if delta > 0 else "▼" if delta < 0 else "="
    print(f"  {d['topic'][:35]:35s} | iso={iso_chrf.score:5.1f} ctx={ctx_chrf.score:5.1f} | {marker} {delta:+.1f}")
