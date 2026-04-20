"""
Resume full-dataset experiment by reusing completed results.

Sources reused:
  - exp500_final_20260417_174355.json (500 samples)
  - expALL_checkpoint_20260417_183409.json (50 samples, 19 overlap with exp500)

Net reused samples: 531
Remaining to run: 1325
"""

import json, os, sys, time, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import httpx, sacrebleu
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

from cultural_kb_expanded import lookup, build_rag_context, count_entries
from evaluation_framework import compute_standard_metrics, classify_errors

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUNBUFFERED"] = "1"
load_dotenv(Path(__file__).parent / ".env")

RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)
CHECKPOINT_EVERY = 50


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
                temperature=0.0,
                max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            wait = 5 * (2 ** attempt)
            print(f"    [Retry {attempt+1}] {str(e)[:80]}... wait {wait}s", flush=True)
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
        best = re.sub(r"\S+\s*\*\*\*\s*", "", raw).strip()
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


def sample_key_from_result(r):
    return (r["source"], r["reference"])


def sample_key_from_data(d, ref):
    return (d["text"], ref)


def load_prior_results():
    merged = {}
    files = [
        RESULTS_DIR / "exp500_final_20260417_174355.json",
        RESULTS_DIR / "expALL_checkpoint_20260417_183409.json",
    ]
    resume_ckpts = sorted(RESULTS_DIR.glob("expALL_resume_checkpoint_*.json"))
    files.extend(resume_ckpts)
    for path in files:
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        rows = payload["per_sample"]
        for row in rows:
            merged[sample_key_from_result(row)] = row
    return merged


def save_checkpoint(per_sample, completed_new, remaining_total, timestamp):
    path = RESULTS_DIR / f"expALL_resume_checkpoint_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "completed_new": completed_new,
                "remaining_total": remaining_total,
                "per_sample": per_sample,
            },
            f,
            ensure_ascii=False,
            default=str,
        )


def compute_and_print_results(per_sample, total_time):
    n_total = len(per_sample)
    n_ent = sum(1 for r in per_sample if r["has_entities"])
    n_noent = n_total - n_ent

    all_plain = [r["hyp_plain"] for r in per_sample]
    all_kb = [r["hyp_kb"] for r in per_sample]
    all_refs = [r["reference"] for r in per_sample]

    ent_plain = [r["hyp_plain"] for r in per_sample if r["has_entities"]]
    ent_kb = [r["hyp_kb"] for r in per_sample if r["has_entities"]]
    ent_refs = [r["reference"] for r in per_sample if r["has_entities"]]

    noent_hyps = [r["hyp_plain"] for r in per_sample if not r["has_entities"]]
    noent_refs = [r["reference"] for r in per_sample if not r["has_entities"]]

    m_all_p = compute_standard_metrics(all_plain, all_refs)
    m_all_k = compute_standard_metrics(all_kb, all_refs)
    m_ent_p = compute_standard_metrics(ent_plain, ent_refs) if ent_plain else {}
    m_ent_k = compute_standard_metrics(ent_kb, ent_refs) if ent_kb else {}
    m_noent = compute_standard_metrics(noent_hyps, noent_refs) if noent_hyps else {}

    p_cueas = [
        r["eval_plain"]["cuea"]["cuea"]
        for r in per_sample
        if r["has_entities"] and r["eval_plain"]["cuea"]["cuea"] is not None
    ]
    k_cueas = [
        r["eval_kb"]["cuea"]["cuea"]
        for r in per_sample
        if r["has_entities"] and r["eval_kb"]["cuea"]["cuea"] is not None
    ]
    avg_cuea_p = sum(p_cueas) / len(p_cueas) if p_cueas else 0
    avg_cuea_k = sum(k_cueas) / len(k_cueas) if k_cueas else 0

    p_pur = [r["eval_plain"]["script_purity"]["purity"] for r in per_sample]
    k_pur = [r["eval_kb"]["script_purity"]["purity"] for r in per_sample]

    plain_err = defaultdict(int)
    kb_err = defaultdict(int)
    for r in per_sample:
        if r["has_entities"]:
            for e in r["eval_plain"]["errors"]:
                plain_err[e["type"]] += 1
            for e in r["eval_kb"]["errors"]:
                kb_err[e["type"]] += 1

    chrf_wins = sum(
        1
        for r in per_sample
        if r["has_entities"]
        and r["eval_kb"]["standard_metrics"]["chrf++"]
        > r["eval_plain"]["standard_metrics"]["chrf++"]
    )
    cuea_wins = sum(
        1
        for r in per_sample
        if r["has_entities"]
        and (r["eval_kb"]["cuea"]["cuea"] or 0)
        > (r["eval_plain"]["cuea"]["cuea"] or 0)
    )

    print("\n" + "=" * 78, flush=True)
    print(f"FULL DATASET RESULTS (RESUMED) — {n_total} samples ({total_time/60:.1f} min new run)", flush=True)
    print("=" * 78, flush=True)
    print(f"{'Metric':<36} {'Plain':>10} {'KB-RAG':>10} {'Delta':>10}", flush=True)
    print("-" * 68, flush=True)
    print(f"{'ALL samples chrF++':<36} {m_all_p['chrf++']:>10.2f} {m_all_k['chrf++']:>10.2f} {m_all_k['chrf++'] - m_all_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'ENTITY samples chrF++':<36} {m_ent_p['chrf++']:>10.2f} {m_ent_k['chrf++']:>10.2f} {m_ent_k['chrf++'] - m_ent_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'NO-ENTITY samples chrF++':<36} {m_noent['chrf++']:>10.2f} {'(same)':>10}", flush=True)
    print(f"{'ALL samples BLEU':<36} {m_all_p['bleu']:>10.2f} {m_all_k['bleu']:>10.2f} {m_all_k['bleu'] - m_all_p['bleu']:>+10.2f}", flush=True)
    print(f"{'Avg CuEA (entity samples)':<36} {avg_cuea_p:>10.3f} {avg_cuea_k:>10.3f} {avg_cuea_k - avg_cuea_p:>+10.3f}", flush=True)
    print(f"{'Avg Script Purity':<36} {sum(p_pur)/len(p_pur):>10.3f} {sum(k_pur)/len(k_pur):>10.3f}", flush=True)
    print(f"{'chrF++ win rate (entity)':<36} {'':>10} {chrf_wins}/{n_ent} ({chrf_wins/n_ent*100:.0f}%)", flush=True)
    print(f"{'CuEA win rate (entity)':<36} {'':>10} {cuea_wins}/{n_ent} ({cuea_wins/n_ent*100:.0f}%)", flush=True)

    print(f"\n{'Error Type':<25} {'Plain':>8} {'KB-RAG':>8} {'Reduction':>12}", flush=True)
    print("-" * 58, flush=True)
    tp = sum(plain_err.values())
    tk = sum(kb_err.values())
    for et in sorted(set(plain_err) | set(kb_err)):
        p, k = plain_err[et], kb_err[et]
        red = f"{(1-k/p)*100:.0f}%" if p > 0 else "N/A"
        print(f"  {et:<23} {p:>8} {k:>8} {red:>12}", flush=True)
    if tp > 0:
        print(f"  {'TOTAL':<23} {tp:>8} {tk:>8} {(1-tk/tp)*100:.0f}%", flush=True)

    return {
        "metadata": {
            "total_samples": n_total,
            "n_with_entities": n_ent,
            "n_without_entities": n_noent,
            "ckb_entries": count_entries(),
            "model": "GPT-4o",
            "new_runtime_min": round(total_time / 60, 1),
            "reused_samples": 531,
        },
        "main_results": {
            "all_plain": m_all_p,
            "all_kb": m_all_k,
            "entity_plain": m_ent_p,
            "entity_kb": m_ent_k,
            "no_entity": m_noent,
            "avg_cuea_plain": round(avg_cuea_p, 3),
            "avg_cuea_kb": round(avg_cuea_k, 3),
            "chrf_win_rate": f"{chrf_wins}/{n_ent}",
            "cuea_win_rate": f"{cuea_wins}/{n_ent}",
        },
        "errors": {"plain": dict(plain_err), "kb_rag": dict(kb_err)},
    }


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Loading data...", flush=True)
    data = load_data()
    print(f"Total dataset: {len(data)} samples, CKB: {count_entries()} entries", flush=True)

    prior = load_prior_results()
    print(f"Loaded prior results: {len(prior)} unique samples reused", flush=True)

    client = get_client()
    test = call_gpt4o(client, "Translator.", "Translate to Khmer: xin chào")
    if not test:
        print("ERROR: Cannot connect", flush=True)
        sys.exit(1)
    print("Connected OK", flush=True)

    all_rows = []
    remaining = []
    for d in data:
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        key = sample_key_from_data(d, ref)
        if key in prior:
            row = prior[key]
            row.setdefault("has_entities", len(row.get("entities", [])) > 0 if "entities" in row else len(lookup(d["text"])) > 0)
            row.setdefault("n_entities", len(set(e.get("vi", e.get("romanized", "")) for e in lookup(d["text"]))))
            row.setdefault("topic", d.get("topic"))
            all_rows.append(row)
        else:
            ents = lookup(d["text"])
            remaining.append({
                "sample": d,
                "ref": ref,
                "has_entities": len(ents) > 0,
                "n_entities": len(set(e.get("vi", e.get("romanized", "")) for e in ents)),
            })

    n_ent_rem = sum(1 for r in remaining if r["has_entities"])
    n_noent_rem = len(remaining) - n_ent_rem
    est_calls = n_ent_rem * 2 + n_noent_rem
    print(f"Remaining: {len(remaining)} samples ({n_ent_rem} with entities, {n_noent_rem} without)", flush=True)
    print(f"Est. remaining API calls: {est_calls}, Est. time: {est_calls/17:.0f} min", flush=True)

    start = time.time()
    for i, item in enumerate(remaining):
        s = item["sample"]
        source = s["text"]
        ref = item["ref"]
        has_ent = item["has_entities"]

        elapsed = time.time() - start
        rate = (i / elapsed * 60) if elapsed > 0 and i > 0 else 0
        rem = len(remaining) - i
        eta = (rem / (rate / 60)) / 60 if rate > 0 else 0
        if i % 10 == 0 or i < 5:
            tag = f"e={item['n_entities']}" if has_ent else "no-e"
            print(f"  [new {i+1}/{len(remaining)}] {tag} | {rate:.0f}/m | ETA {eta:.0f}m", flush=True)

        try:
            hyp_plain = call_gpt4o(client, SYSTEM_PLAIN, f"Vietnamese: {source}")
            if has_ent:
                rag = build_rag_context(source)
                hyp_kb = call_gpt4o(client, SYSTEM_KB, f"{rag}\n\nTranslate this Vietnamese text into Khmer:\n{source}")
            else:
                hyp_kb = hyp_plain

            eval_p = classify_errors(source, hyp_plain, ref)
            eval_k = classify_errors(source, hyp_kb, ref) if has_ent else eval_p
        except Exception as e:
            print(f"    [WARN] sample failed, storing fallback result: {str(e)[:120]}", flush=True)
            hyp_plain = hyp_plain if 'hyp_plain' in locals() else ""
            hyp_kb = hyp_kb if 'hyp_kb' in locals() else hyp_plain
            eval_p = classify_errors(source, hyp_plain or "", ref or "")
            eval_k = classify_errors(source, hyp_kb or "", ref or "") if has_ent else eval_p

        all_rows.append({
            "source": source,
            "reference": ref,
            "hyp_plain": hyp_plain,
            "hyp_kb": hyp_kb,
            "has_entities": has_ent,
            "n_entities": item["n_entities"],
            "topic": s.get("topic"),
            "eval_plain": eval_p,
            "eval_kb": eval_k,
        })

        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(all_rows, i + 1, len(remaining), timestamp)
            print(f"    ** Resume checkpoint {i+1}/{len(remaining)} **", flush=True)

    total_time = time.time() - start
    summary = compute_and_print_results(all_rows, total_time)
    summary["per_sample"] = all_rows

    outpath = RESULTS_DIR / f"expALL_resume_final_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved: {outpath}", flush=True)


if __name__ == "__main__":
    main()
