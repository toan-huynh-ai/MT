"""
Large-Scale Experiment: 500 samples with CKB v2 + CulturalEval
================================================================
350 samples WITH cultural entities + 150 WITHOUT (control group)
Compares Plain GPT-4o vs CKB-RAG augmented GPT-4o
Evaluates: chrF++, CuEA, Script Purity, Error Taxonomy
"""

import json, os, sys, time, random, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import httpx, sacrebleu
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

from cultural_kb_expanded import lookup, build_rag_context, count_entries
from evaluation_framework import compute_standard_metrics, compute_cuea, compute_script_purity, classify_errors

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUNBUFFERED"] = "1"
load_dotenv(Path(__file__).parent / ".env")
RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)

N_WITH_ENTITIES = 350
N_WITHOUT_ENTITIES = 150
CHECKPOINT_EVERY = 25


def get_client():
    http_client = httpx.Client(verify=False, proxy=os.getenv("HTTPS_PROXY"))
    credential = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("APPLICATION_AI_VOS_USERS_ID"),
        client_secret=os.getenv("APPLICATION_AI_VOS_USERS_SECRET"),
        connection_verify=False,
    )
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_API_VERSION", "2024-05-01-preview"),
        azure_ad_token_provider=token_provider,
        http_client=http_client,
    )


def call_gpt4o(client, system_prompt, user_prompt, max_retries=3):
    deployment = os.getenv("AZURE_CHAT_DEPLOYMENT")
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0, max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            wait = 5 * (attempt + 1)
            print(f"    [Retry {attempt+1}/{max_retries}] {str(e)[:80]}... waiting {wait}s")
            time.sleep(wait)
    return ""


def load_data():
    data = []
    base = Path(__file__).parent
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = base / fname
        if not fpath.exists():
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    return data


def get_clean_reference(labels):
    best = ""
    for lbl in labels:
        clean = lbl.split("###")[0].strip()
        parts = clean.split("***")
        if len(parts) == 1 and len(clean) > len(best):
            best = clean
    if not best and labels:
        raw = labels[0].split("###")[0].strip()
        best = re.sub(r'\S+\s*\*\*\*\s*', '', raw).strip()
        if not best:
            best = labels[0].split("###")[-1].strip()
    return best


SYSTEM_PLAIN = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "Translate the following Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_KB = (
    "You are an expert translator specializing in Vietnamese-Khmer Krom translation, "
    "particularly for the Khmer Krom community (ខ្មែរក្រោម) in Vietnam's Mekong Delta. "
    "You will be given cultural terminology references. "
    "ALWAYS use the provided Khmer terms for cultural entities. "
    "Use Khmer Krom dialect where applicable. "
    "Output ONLY the Khmer translation, nothing else."
)


def select_samples(data):
    random.seed(42)

    with_ents = []
    without_ents = []
    for d in data:
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        entities = lookup(d["text"])
        if entities:
            with_ents.append({"sample": d, "ref": ref, "entities": entities,
                              "n_entities": len(set(e.get("vi", e.get("romanized", "")) for e in entities))})
        else:
            without_ents.append({"sample": d, "ref": ref, "entities": [], "n_entities": 0})

    n_with = min(N_WITH_ENTITIES, len(with_ents))
    n_without = min(N_WITHOUT_ENTITIES, len(without_ents))

    selected_with = random.sample(with_ents, n_with)
    selected_without = random.sample(without_ents, n_without)

    all_selected = selected_with + selected_without
    random.shuffle(all_selected)
    return all_selected


def save_checkpoint(results, completed, total, timestamp):
    path = RESULTS_DIR / f"exp500_checkpoint_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"completed": completed, "total": total, "results": results},
                  f, ensure_ascii=False, indent=2, default=str)


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples, CKB has {count_entries()} entries")

    client = get_client()

    # Quick connectivity test
    test = call_gpt4o(client, "Translator.", "Translate to Khmer: xin chào")
    if not test:
        print("ERROR: Cannot connect to GPT-4o")
        sys.exit(1)
    print(f"Connected. Test: {test[:40]}")

    print("\nSelecting samples...")
    selected = select_samples(data)
    n_with = sum(1 for s in selected if s["n_entities"] > 0)
    n_without = sum(1 for s in selected if s["n_entities"] == 0)
    print(f"Selected {len(selected)} samples: {n_with} with entities, {n_without} without")

    per_sample = []
    start_time = time.time()

    for i, item in enumerate(selected):
        sample = item["sample"]
        ref = item["ref"]
        source = sample["text"]
        has_entities = item["n_entities"] > 0

        elapsed = time.time() - start_time
        rate = (i / elapsed * 60) if elapsed > 0 and i > 0 else 0
        eta = ((len(selected) - i) / (rate / 60)) / 60 if rate > 0 else 0

        ent_str = f"ents={item['n_entities']}" if has_entities else "no-ent"
        print(f"  [{i+1}/{len(selected)}] {ent_str} | {rate:.1f}/min | ETA {eta:.0f}min | {source[:50]}...")

        hyp_plain = call_gpt4o(client, SYSTEM_PLAIN, f"Vietnamese: {source}")

        if has_entities:
            rag_context = build_rag_context(source)
            user_kb = f"{rag_context}\n\nTranslate this Vietnamese text into Khmer:\n{source}"
            hyp_kb = call_gpt4o(client, SYSTEM_KB, user_kb)
        else:
            hyp_kb = hyp_plain

        eval_plain = classify_errors(source, hyp_plain, ref)
        eval_kb = classify_errors(source, hyp_kb, ref) if has_entities else eval_plain

        per_sample.append({
            "idx": i,
            "source": source,
            "reference": ref,
            "hyp_plain": hyp_plain,
            "hyp_kb": hyp_kb,
            "has_entities": has_entities,
            "n_entities": item["n_entities"],
            "topic": sample.get("topic"),
            "eval_plain": eval_plain,
            "eval_kb": eval_kb,
        })

        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(per_sample, i + 1, len(selected), timestamp)
            print(f"    [Checkpoint saved: {i+1}/{len(selected)}]")

    total_time = time.time() - start_time

    # ── Compute corpus metrics ──
    all_plain_hyps = [r["hyp_plain"] for r in per_sample]
    all_kb_hyps = [r["hyp_kb"] for r in per_sample]
    all_refs = [r["reference"] for r in per_sample]

    ent_plain_hyps = [r["hyp_plain"] for r in per_sample if r["has_entities"]]
    ent_kb_hyps = [r["hyp_kb"] for r in per_sample if r["has_entities"]]
    ent_refs = [r["reference"] for r in per_sample if r["has_entities"]]

    noent_hyps = [r["hyp_plain"] for r in per_sample if not r["has_entities"]]
    noent_refs = [r["reference"] for r in per_sample if not r["has_entities"]]

    corpus_all_plain = compute_standard_metrics(all_plain_hyps, all_refs)
    corpus_all_kb = compute_standard_metrics(all_kb_hyps, all_refs)
    corpus_ent_plain = compute_standard_metrics(ent_plain_hyps, ent_refs)
    corpus_ent_kb = compute_standard_metrics(ent_kb_hyps, ent_refs)
    corpus_noent = compute_standard_metrics(noent_hyps, noent_refs) if noent_hyps else {}

    # CuEA
    plain_cueas = [r["eval_plain"]["cuea"]["cuea"] for r in per_sample
                   if r["has_entities"] and r["eval_plain"]["cuea"]["cuea"] is not None]
    kb_cueas = [r["eval_kb"]["cuea"]["cuea"] for r in per_sample
                if r["has_entities"] and r["eval_kb"]["cuea"]["cuea"] is not None]

    avg_cuea_plain = sum(plain_cueas) / len(plain_cueas) if plain_cueas else 0
    avg_cuea_kb = sum(kb_cueas) / len(kb_cueas) if kb_cueas else 0

    # Script Purity
    plain_purities = [r["eval_plain"]["script_purity"]["purity"] for r in per_sample]
    kb_purities = [r["eval_kb"]["script_purity"]["purity"] for r in per_sample]

    # Error counts
    plain_errors = defaultdict(int)
    kb_errors = defaultdict(int)
    for r in per_sample:
        if r["has_entities"]:
            for e in r["eval_plain"]["errors"]:
                plain_errors[e["type"]] += 1
            for e in r["eval_kb"]["errors"]:
                kb_errors[e["type"]] += 1

    # Win rates
    chrf_wins = sum(1 for r in per_sample if r["has_entities"]
                    and r["eval_kb"]["standard_metrics"]["chrf++"] > r["eval_plain"]["standard_metrics"]["chrf++"])
    cuea_wins = sum(1 for r in per_sample if r["has_entities"]
                    and (r["eval_kb"]["cuea"]["cuea"] or 0) > (r["eval_plain"]["cuea"]["cuea"] or 0))
    n_ent_samples = sum(1 for r in per_sample if r["has_entities"])

    # ── Print Results ──
    print("\n" + "=" * 70)
    print(f"500-SAMPLE EXPERIMENT RESULTS (completed in {total_time/60:.1f} min)")
    print("=" * 70)

    print(f"\n{'':>30} {'Plain':>10} {'KB-RAG':>10} {'Delta':>10}")
    print("-" * 60)
    print(f"{'ALL SAMPLES (chrF++)':>30} {corpus_all_plain['chrf++']:>10.2f} {corpus_all_kb['chrf++']:>10.2f} {corpus_all_kb['chrf++'] - corpus_all_plain['chrf++']:>+10.2f}")
    print(f"{'ENTITY samples (chrF++)':>30} {corpus_ent_plain['chrf++']:>10.2f} {corpus_ent_kb['chrf++']:>10.2f} {corpus_ent_kb['chrf++'] - corpus_ent_plain['chrf++']:>+10.2f}")
    if corpus_noent:
        print(f"{'NO-ENTITY samples (chrF++)':>30} {corpus_noent['chrf++']:>10.2f} {'(same)':>10} {'':>10}")
    print(f"{'Avg CuEA (entity samples)':>30} {avg_cuea_plain:>10.3f} {avg_cuea_kb:>10.3f} {avg_cuea_kb - avg_cuea_plain:>+10.3f}")
    print(f"{'Avg Script Purity':>30} {sum(plain_purities)/len(plain_purities):>10.3f} {sum(kb_purities)/len(kb_purities):>10.3f}")
    print(f"{'chrF++ win rate':>30} {'':>10} {chrf_wins}/{n_ent_samples}")
    print(f"{'CuEA win rate':>30} {'':>10} {cuea_wins}/{n_ent_samples}")

    print(f"\n{'Error Type':>25} {'Plain':>8} {'KB-RAG':>8} {'Reduction':>10}")
    print("-" * 55)
    total_plain_err = sum(plain_errors.values())
    total_kb_err = sum(kb_errors.values())
    for et in sorted(set(plain_errors) | set(kb_errors)):
        p, k = plain_errors[et], kb_errors[et]
        red = f"{(1-k/p)*100:.0f}%" if p > 0 else "N/A"
        print(f"  {et:>23} {p:>8} {k:>8} {red:>10}")
    print(f"  {'TOTAL':>23} {total_plain_err:>8} {total_kb_err:>8} {(1-total_kb_err/total_plain_err)*100:.0f}%" if total_plain_err > 0 else "")

    # ── Save final results ──
    final = {
        "metadata": {
            "timestamp": timestamp,
            "total_samples": len(selected),
            "n_with_entities": n_with,
            "n_without_entities": n_without,
            "ckb_entries": count_entries(),
            "model": "GPT-4o",
            "runtime_minutes": round(total_time / 60, 1),
        },
        "corpus_results": {
            "all_plain": corpus_all_plain,
            "all_kb": corpus_all_kb,
            "entity_plain": corpus_ent_plain,
            "entity_kb": corpus_ent_kb,
            "no_entity": corpus_noent,
            "avg_cuea_plain": round(avg_cuea_plain, 3),
            "avg_cuea_kb": round(avg_cuea_kb, 3),
            "delta_cuea": round(avg_cuea_kb - avg_cuea_plain, 3),
            "chrf_win_rate": f"{chrf_wins}/{n_ent_samples}",
            "cuea_win_rate": f"{cuea_wins}/{n_ent_samples}",
        },
        "error_distribution": {"plain": dict(plain_errors), "kb_rag": dict(kb_errors)},
        "per_sample": per_sample,
    }

    outpath = RESULTS_DIR / f"exp500_final_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nResults saved to: {outpath}")


if __name__ == "__main__":
    main()
