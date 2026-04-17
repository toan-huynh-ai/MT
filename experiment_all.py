"""
Full Dataset Experiment: 1,856 samples × GPT-4o (Plain + KB-RAG)
=================================================================
Runs ALL data, saves checkpoints every 50 samples, produces final results table.
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
from evaluation_framework import compute_standard_metrics, compute_cuea, compute_script_purity, classify_errors

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
                temperature=0.0, max_tokens=1024,
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


def load_checkpoint(timestamp):
    path = RESULTS_DIR / f"expALL_checkpoint_{timestamp}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_checkpoint(per_sample, completed, total, timestamp):
    path = RESULTS_DIR / f"expALL_checkpoint_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"completed": completed, "total": total, "per_sample": per_sample},
                  f, ensure_ascii=False, default=str)


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

    p_cueas = [r["eval_plain"]["cuea"]["cuea"] for r in per_sample
               if r["has_entities"] and r["eval_plain"]["cuea"]["cuea"] is not None]
    k_cueas = [r["eval_kb"]["cuea"]["cuea"] for r in per_sample
               if r["has_entities"] and r["eval_kb"]["cuea"]["cuea"] is not None]
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

    chrf_wins = sum(1 for r in per_sample if r["has_entities"]
                    and r["eval_kb"]["standard_metrics"]["chrf++"] > r["eval_plain"]["standard_metrics"]["chrf++"])
    cuea_wins = sum(1 for r in per_sample if r["has_entities"]
                    and (r["eval_kb"]["cuea"]["cuea"] or 0) > (r["eval_plain"]["cuea"]["cuea"] or 0))

    # Topic breakdown
    topic_scores = defaultdict(lambda: {"plain_chrf": [], "kb_chrf": [], "plain_cuea": [], "kb_cuea": []})
    for r in per_sample:
        t = r.get("topic") or "QA (no topic)"
        topic_scores[t]["plain_chrf"].append(r["eval_plain"]["standard_metrics"]["chrf++"])
        topic_scores[t]["kb_chrf"].append(r["eval_kb"]["standard_metrics"]["chrf++"])
        if r["has_entities"]:
            if r["eval_plain"]["cuea"]["cuea"] is not None:
                topic_scores[t]["plain_cuea"].append(r["eval_plain"]["cuea"]["cuea"])
            if r["eval_kb"]["cuea"]["cuea"] is not None:
                topic_scores[t]["kb_cuea"].append(r["eval_kb"]["cuea"]["cuea"])

    print("\n" + "=" * 75, flush=True)
    print(f"FULL DATASET RESULTS — {n_total} samples ({total_time/60:.1f} min)", flush=True)
    print("=" * 75, flush=True)

    print(f"\n{'MAIN RESULTS TABLE':^75}", flush=True)
    print(f"{'Metric':<35} {'Plain':>10} {'KB-RAG':>10} {'Delta':>10}", flush=True)
    print("-" * 65, flush=True)
    print(f"{'ALL samples chrF++ (n='+str(n_total)+')':<35} {m_all_p['chrf++']:>10.2f} {m_all_k['chrf++']:>10.2f} {m_all_k['chrf++'] - m_all_p['chrf++']:>+10.2f}", flush=True)
    if m_ent_p:
        print(f"{'ENTITY samples chrF++ (n='+str(n_ent)+')':<35} {m_ent_p['chrf++']:>10.2f} {m_ent_k['chrf++']:>10.2f} {m_ent_k['chrf++'] - m_ent_p['chrf++']:>+10.2f}", flush=True)
    if m_noent:
        print(f"{'NO-ENTITY samples chrF++ (n='+str(n_noent)+')':<35} {m_noent['chrf++']:>10.2f} {'(same)':>10}", flush=True)
    print(f"{'ALL samples BLEU':<35} {m_all_p['bleu']:>10.2f} {m_all_k['bleu']:>10.2f} {m_all_k['bleu'] - m_all_p['bleu']:>+10.2f}", flush=True)
    print(f"{'Avg CuEA (entity samples)':<35} {avg_cuea_p:>10.3f} {avg_cuea_k:>10.3f} {avg_cuea_k - avg_cuea_p:>+10.3f}", flush=True)
    print(f"{'Avg Script Purity':<35} {sum(p_pur)/len(p_pur):>10.3f} {sum(k_pur)/len(k_pur):>10.3f}", flush=True)
    print(f"{'chrF++ win rate (entity)':<35} {'':>10} {chrf_wins}/{n_ent} ({chrf_wins/n_ent*100:.0f}%)", flush=True)
    print(f"{'CuEA win rate (entity)':<35} {'':>10} {cuea_wins}/{n_ent} ({cuea_wins/n_ent*100:.0f}%)", flush=True)

    print(f"\n{'ERROR REDUCTION TABLE':^75}", flush=True)
    print(f"{'Error Type':<25} {'Plain':>8} {'KB-RAG':>8} {'Reduction':>12}", flush=True)
    print("-" * 55, flush=True)
    tp = sum(plain_err.values())
    tk = sum(kb_err.values())
    for et in sorted(set(plain_err) | set(kb_err)):
        p, k = plain_err[et], kb_err[et]
        red = f"{(1-k/p)*100:.0f}%" if p > 0 else "N/A"
        print(f"  {et:<23} {p:>8} {k:>8} {red:>12}", flush=True)
    if tp > 0:
        print(f"  {'TOTAL':<23} {tp:>8} {tk:>8} {(1-tk/tp)*100:.0f}%", flush=True)

    # Top 10 topics by sample count
    print(f"\n{'TOP TOPICS BY SAMPLE COUNT':^75}", flush=True)
    print(f"{'Topic':<40} {'N':>4} {'Plain':>7} {'KB':>7} {'P-CuEA':>7} {'K-CuEA':>7}", flush=True)
    print("-" * 75, flush=True)
    sorted_topics = sorted(topic_scores.items(), key=lambda x: -len(x[1]["plain_chrf"]))
    for topic, scores in sorted_topics[:15]:
        n = len(scores["plain_chrf"])
        pc = sum(scores["plain_chrf"]) / n
        kc = sum(scores["kb_chrf"]) / n
        pcu = sum(scores["plain_cuea"]) / len(scores["plain_cuea"]) if scores["plain_cuea"] else -1
        kcu = sum(scores["kb_cuea"]) / len(scores["kb_cuea"]) if scores["kb_cuea"] else -1
        pcu_s = f"{pcu:.2f}" if pcu >= 0 else "—"
        kcu_s = f"{kcu:.2f}" if kcu >= 0 else "—"
        print(f"  {topic[:38]:<38} {n:>4} {pc:>7.1f} {kc:>7.1f} {pcu_s:>7} {kcu_s:>7}", flush=True)

    return {
        "metadata": {
            "total_samples": n_total, "n_with_entities": n_ent,
            "n_without_entities": n_noent, "ckb_entries": count_entries(),
            "model": "GPT-4o", "runtime_min": round(total_time / 60, 1),
        },
        "main_results": {
            "all_plain": m_all_p, "all_kb": m_all_k,
            "entity_plain": m_ent_p, "entity_kb": m_ent_k,
            "no_entity": m_noent,
            "avg_cuea_plain": round(avg_cuea_p, 3), "avg_cuea_kb": round(avg_cuea_k, 3),
            "chrf_win_rate": f"{chrf_wins}/{n_ent}",
            "cuea_win_rate": f"{cuea_wins}/{n_ent}",
        },
        "errors": {"plain": dict(plain_err), "kb_rag": dict(kb_err)},
    }


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Loading data...", flush=True)
    data = load_data()
    print(f"Total: {len(data)} samples, CKB: {count_entries()} entries", flush=True)

    client = get_client()
    test = call_gpt4o(client, "Translator.", "Translate to Khmer: xin chào")
    if not test:
        print("ERROR: Cannot connect", flush=True)
        sys.exit(1)
    print(f"Connected OK", flush=True)

    # Prepare all samples
    samples = []
    for d in data:
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        entities = lookup(d["text"])
        samples.append({
            "sample": d, "ref": ref, "entities": entities,
            "has_entities": len(entities) > 0,
            "n_entities": len(set(e.get("vi", e.get("romanized", "")) for e in entities)),
        })

    n_ent = sum(1 for s in samples if s["has_entities"])
    n_noent = len(samples) - n_ent
    total_calls = n_ent * 2 + n_noent
    print(f"Samples: {len(samples)} ({n_ent} with entities, {n_noent} without)", flush=True)
    print(f"Est. API calls: {total_calls}, Est. time: {total_calls/17:.0f} min", flush=True)

    per_sample = []
    start = time.time()

    for i, item in enumerate(samples):
        s = item["sample"]
        source = s["text"]
        ref = item["ref"]
        has_ent = item["has_entities"]

        elapsed = time.time() - start
        rate = (i / elapsed * 60) if elapsed > 0 and i > 0 else 0
        remaining = len(samples) - i
        eta = (remaining / (rate / 60)) / 60 if rate > 0 else 0
        tag = f"e={item['n_entities']}" if has_ent else "no-e"

        if i % 10 == 0 or i < 5:
            print(f"  [{i+1}/{len(samples)}] {tag} | {rate:.0f}/m | ETA {eta:.0f}m", flush=True)

        hyp_plain = call_gpt4o(client, SYSTEM_PLAIN, f"Vietnamese: {source}")

        if has_ent:
            rag = build_rag_context(source)
            hyp_kb = call_gpt4o(client, SYSTEM_KB, f"{rag}\n\nTranslate this Vietnamese text into Khmer:\n{source}")
        else:
            hyp_kb = hyp_plain

        eval_p = classify_errors(source, hyp_plain, ref)
        eval_k = classify_errors(source, hyp_kb, ref) if has_ent else eval_p

        per_sample.append({
            "source": source, "reference": ref,
            "hyp_plain": hyp_plain, "hyp_kb": hyp_kb,
            "has_entities": has_ent, "n_entities": item["n_entities"],
            "topic": s.get("topic"),
            "eval_plain": eval_p, "eval_kb": eval_k,
        })

        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(per_sample, i + 1, len(samples), timestamp)
            print(f"    ** Checkpoint {i+1}/{len(samples)} **", flush=True)

    total_time = time.time() - start

    summary = compute_and_print_results(per_sample, total_time)
    summary["per_sample"] = per_sample

    outpath = RESULTS_DIR / f"expALL_final_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved: {outpath}", flush=True)


if __name__ == "__main__":
    main()
