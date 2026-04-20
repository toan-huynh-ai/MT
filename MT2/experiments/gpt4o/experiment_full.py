"""
Full Experiment: CKB v2 + CulturalEval Framework
=================================================
Tests expanded CKB (132 entries) with A/B/C taxonomy on:
  1. Larger sample set (50 samples covering all cultural categories)
  2. Zero-shot vs CKB-RAG comparison
  3. Full CulturalEval metrics (chrF++, CuEA, Script Purity)
"""

import json, os, sys, time, random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import httpx, sacrebleu
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

from cultural_kb_expanded import lookup, build_rag_context, CULTURAL_KB, count_entries
from evaluation_framework import (
    compute_standard_metrics, compute_cuea, compute_script_purity, classify_errors
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(Path(__file__).parent / ".env")
RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)


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


def call_gpt4o(client, system_prompt, user_prompt):
    deployment = os.getenv("AZURE_CHAT_DEPLOYMENT")
    for attempt in range(3):
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
            print(f"  [Retry {attempt+1}] {e}")
            time.sleep(5 * (attempt + 1))
    return ""


def load_data():
    import re
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
    import re
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


def select_cultural_samples(data, n=50):
    """Select samples that contain cultural entities for meaningful comparison."""
    samples_with_entities = []
    for d in data:
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        entities = lookup(d["text"])
        if entities:
            samples_with_entities.append({
                "sample": d,
                "ref": ref,
                "entities": entities,
                "n_entities": len(set(e.get("vi", e.get("romanized", "")) for e in entities)),
            })

    random.seed(42)
    if len(samples_with_entities) > n:
        samples_with_entities.sort(key=lambda x: -x["n_entities"])
        top = samples_with_entities[:n // 2]
        rest = samples_with_entities[n // 2:]
        random_rest = random.sample(rest, min(n - len(top), len(rest)))
        selected = top + random_rest
    else:
        selected = samples_with_entities

    return selected[:n]


def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples, CKB has {count_entries()} entries")

    client = get_client()

    print("\nSelecting cultural samples...")
    selected = select_cultural_samples(data, n=40)
    print(f"Selected {len(selected)} samples with cultural entities")

    entity_dist = defaultdict(int)
    for s in selected:
        for e in s["entities"]:
            entity_dist[e.get("category", "?")] += 1
    print("Entity distribution:", dict(entity_dist))

    plain_hyps, kb_hyps, refs, sources = [], [], [], []
    per_sample_results = []

    for i, item in enumerate(selected):
        sample = item["sample"]
        ref = item["ref"]
        source = sample["text"]

        rag_context = build_rag_context(source)
        ent_names = [e.get("vi", e.get("romanized", "?")) for e in item["entities"]]

        print(f"  [{i+1}/{len(selected)}] entities={ent_names[:3]}...")

        hyp_plain = call_gpt4o(client, SYSTEM_PLAIN, f"Vietnamese: {source}")
        user_kb = f"{rag_context}\n\nTranslate this Vietnamese text into Khmer:\n{source}"
        hyp_kb = call_gpt4o(client, SYSTEM_KB, user_kb)

        plain_hyps.append(hyp_plain)
        kb_hyps.append(hyp_kb)
        refs.append(ref)
        sources.append(source)

        eval_plain = classify_errors(source, hyp_plain, ref)
        eval_kb = classify_errors(source, hyp_kb, ref)

        per_sample_results.append({
            "source": source,
            "reference": ref,
            "hyp_plain": hyp_plain,
            "hyp_kb": hyp_kb,
            "entities": ent_names,
            "eval_plain": eval_plain,
            "eval_kb": eval_kb,
        })

    print("\n" + "=" * 70)
    print("COMPUTING CORPUS-LEVEL RESULTS")
    print("=" * 70)

    corpus_plain = compute_standard_metrics(plain_hyps, refs)
    corpus_kb = compute_standard_metrics(kb_hyps, refs)

    plain_cueas = [r["eval_plain"]["cuea"]["cuea"] for r in per_sample_results
                   if r["eval_plain"]["cuea"]["cuea"] is not None]
    kb_cueas = [r["eval_kb"]["cuea"]["cuea"] for r in per_sample_results
                if r["eval_kb"]["cuea"]["cuea"] is not None]

    plain_purities = [r["eval_plain"]["script_purity"]["purity"] for r in per_sample_results]
    kb_purities = [r["eval_kb"]["script_purity"]["purity"] for r in per_sample_results]

    plain_errors = defaultdict(int)
    kb_errors = defaultdict(int)
    for r in per_sample_results:
        for e in r["eval_plain"]["errors"]:
            plain_errors[e["type"]] += 1
        for e in r["eval_kb"]["errors"]:
            kb_errors[e["type"]] += 1

    avg_cuea_plain = sum(plain_cueas) / len(plain_cueas) if plain_cueas else 0
    avg_cuea_kb = sum(kb_cueas) / len(kb_cueas) if kb_cueas else 0
    avg_purity_plain = sum(plain_purities) / len(plain_purities)
    avg_purity_kb = sum(kb_purities) / len(kb_purities)

    chrf_wins = sum(1 for r in per_sample_results
                    if r["eval_kb"]["standard_metrics"]["chrf++"] >
                    r["eval_plain"]["standard_metrics"]["chrf++"])
    cuea_wins = sum(1 for r in per_sample_results
                    if (r["eval_kb"]["cuea"]["cuea"] or 0) >
                    (r["eval_plain"]["cuea"]["cuea"] or 0))

    print(f"\n{'Metric':<25} {'Plain':>10} {'KB-RAG':>10} {'Delta':>10}")
    print("-" * 55)
    print(f"{'chrF++':<25} {corpus_plain['chrf++']:>10.2f} {corpus_kb['chrf++']:>10.2f} {corpus_kb['chrf++'] - corpus_plain['chrf++']:>+10.2f}")
    print(f"{'BLEU':<25} {corpus_plain['bleu']:>10.2f} {corpus_kb['bleu']:>10.2f} {corpus_kb['bleu'] - corpus_plain['bleu']:>+10.2f}")
    print(f"{'Avg CuEA':<25} {avg_cuea_plain:>10.3f} {avg_cuea_kb:>10.3f} {avg_cuea_kb - avg_cuea_plain:>+10.3f}")
    print(f"{'Avg Script Purity':<25} {avg_purity_plain:>10.3f} {avg_purity_kb:>10.3f} {avg_purity_kb - avg_purity_plain:>+10.3f}")
    print(f"{'chrF++ win rate':<25} {'':>10} {chrf_wins}/{len(selected)}")
    print(f"{'CuEA win rate':<25} {'':>10} {cuea_wins}/{len(selected)}")

    print(f"\n{'Error Type':<25} {'Plain':>8} {'KB-RAG':>8} {'Reduction':>10}")
    print("-" * 55)
    all_err_types = set(plain_errors.keys()) | set(kb_errors.keys())
    for et in sorted(all_err_types):
        p = plain_errors[et]
        k = kb_errors[et]
        reduction = f"{(1 - k/p)*100:.0f}%" if p > 0 else "N/A"
        print(f"  {et:<23} {p:>8} {k:>8} {reduction:>10}")

    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "n_samples": len(selected),
            "ckb_version": "v2",
            "ckb_entries": count_entries(),
            "model": "GPT-4o",
        },
        "corpus_results": {
            "plain": {**corpus_plain, "avg_cuea": round(avg_cuea_plain, 3),
                      "avg_purity": round(avg_purity_plain, 3)},
            "kb_rag": {**corpus_kb, "avg_cuea": round(avg_cuea_kb, 3),
                       "avg_purity": round(avg_purity_kb, 3)},
            "delta_chrf": round(corpus_kb["chrf++"] - corpus_plain["chrf++"], 2),
            "delta_cuea": round(avg_cuea_kb - avg_cuea_plain, 3),
            "chrf_win_rate": f"{chrf_wins}/{len(selected)}",
            "cuea_win_rate": f"{cuea_wins}/{len(selected)}",
        },
        "error_distribution": {
            "plain": dict(plain_errors),
            "kb_rag": dict(kb_errors),
        },
        "per_sample": per_sample_results,
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = RESULTS_DIR / f"full_experiment_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nResults saved to: {outpath}")


if __name__ == "__main__":
    main()
