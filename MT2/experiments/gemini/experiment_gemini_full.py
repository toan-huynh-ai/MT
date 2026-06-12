"""
Full Dataset Experiment: 1,856 samples × Gemini 2.5 Flash (via Devmate OpenAI-compatible API)
=========================================================================================
Uses OpenAI-compatible API endpoint to evaluate Gemini on Vietnamese-Khmer translation.
Saves checkpoints every 50 samples, produces final results table.
"""

import json, os, sys, time, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import httpx, sacrebleu
from openai import OpenAI

# Setup paths
BASE_DIR = Path(__file__).parent.parent.parent  # MT2 root
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "kb"))
sys.path.insert(0, str(BASE_DIR / "eval"))

from cultural_kb_expanded import lookup, build_rag_context, count_entries
from evaluation_framework import compute_standard_metrics, compute_cuea, compute_script_purity, classify_errors

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUNBUFFERED"] = "1"

RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)
CHECKPOINT_EVERY = 50


def get_devmate_client():
    """Create OpenAI-compatible client for Devmate endpoint"""
    # Configure proxy if needed
    http_client = httpx.Client(
        proxy="http://rb-proxy-apac.bosch.com:8080",
        verify=False  # If SSL verification issues
    )
    
    return OpenAI(
        api_key="vQSFPyI6QmjfvoahtLnyJWU8ZoI-y0Gn",  # Your API key
        base_url="https://devmate.bosch.com/api/v3",
        http_client=http_client
    )


def call_gemini(client, system_prompt, user_prompt, max_retries=3):
    """Call Gemini 2.5 Flash model via Devmate OpenAI-compatible API"""
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="gemini-2.5-flash",  # Devmate's Gemini 2.5 Flash
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=1024,
                stream=False
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            wait = 5 * (2 ** attempt)
            print(f"    [Retry {attempt+1}] {str(e)[:80]}... wait {wait}s", flush=True)
            time.sleep(wait)
    return ""


def load_data():
    """Load translation dataset"""
    data = []
    base = Path(__file__).parent.parent.parent / "data"
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = base / fname
        if not fpath.exists():
            print(f"Warning: {fpath} not found", flush=True)
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    print(f"Loaded {len(data)} samples", flush=True)
    return data


def get_clean_reference(labels):
    """Extract clean reference translation from labels"""
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
    """Load checkpoint if exists"""
    path = RESULTS_DIR / f"expGemini_checkpoint_{timestamp}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_checkpoint(per_sample, completed, total, timestamp):
    """Save checkpoint"""
    path = RESULTS_DIR / f"expGemini_checkpoint_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"completed": completed, "total": total, "per_sample": per_sample},
                  f, ensure_ascii=False, default=str)


def compute_and_print_results(per_sample, total_time):
    """Compute and display final results"""
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
    print(f"GEMINI 2.5 FLASH FULL DATASET RESULTS — {n_total} samples ({total_time/60:.1f} min)", flush=True)
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
    print(f"{'Avg Script Purity':<35} {sum(p_pur)/len(p_pur) if p_pur else 0:>10.3f} {sum(k_pur)/len(k_pur) if k_pur else 0:>10.3f}", flush=True)
    print(f"{'chrF++ wins for KB-RAG':<35} {chrf_wins}/{n_ent} samples", flush=True)
    print(f"{'CuEA wins for KB-RAG':<35} {cuea_wins}/{n_ent} entity samples", flush=True)

    print(f"\n{'ERROR BREAKDOWN (entity samples only)':^75}", flush=True)
    print(f"{'Error Type':<35} {'Plain':>10} {'KB-RAG':>10}", flush=True)
    print("-" * 55, flush=True)
    all_error_types = set(plain_err.keys()) | set(kb_err.keys())
    for err_type in sorted(all_error_types):
        print(f"{err_type:<35} {plain_err[err_type]:>10} {kb_err[err_type]:>10}", flush=True)

    print(f"\n{'TOPIC BREAKDOWN':^75}", flush=True)
    print(f"{'Topic':<30} {'Plain chrF++':>12} {'KB-RAG chrF++':>13} {'KB wins':>10}", flush=True)
    print("-" * 70, flush=True)
    for topic in sorted(topic_scores.keys()):
        scores = topic_scores[topic]
        avg_plain = sum(scores["plain_chrf"]) / len(scores["plain_chrf"]) if scores["plain_chrf"] else 0
        avg_kb = sum(scores["kb_chrf"]) / len(scores["kb_chrf"]) if scores["kb_chrf"] else 0
        kb_wins = sum(1 for p, k in zip(scores["plain_chrf"], scores["kb_chrf"]) if k > p)
        total = len(scores["plain_chrf"])
        print(f"{topic:<30} {avg_plain:>12.2f} {avg_kb:>13.2f} {kb_wins}/{total:>8}", flush=True)

    return {
        "model": "gemini-2.5-flash",
        "total_samples": n_total,
        "entity_samples": n_ent,
        "plain_chrf": m_all_p["chrf++"],
        "kb_chrf": m_all_k["chrf++"],
        "plain_bleu": m_all_p["bleu"],
        "kb_bleu": m_all_k["bleu"],
        "avg_cuea_plain": avg_cuea_p,
        "avg_cuea_kb": avg_cuea_k,
        "chrf_delta": m_all_k["chrf++"] - m_all_p["chrf++"],
        "topic_breakdown": dict(topic_scores),
    }


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Gemini evaluation at {timestamp}", flush=True)
    
    # Initialize client
    client = get_devmate_client()
    print("✓ Connected to Devmate (OpenAI-compatible API)", flush=True)
    
    # Load data
    data = load_data()
    if not data:
        print("ERROR: No data loaded", flush=True)
        sys.exit(1)
    
    # Check for checkpoint
    checkpoint = load_checkpoint(timestamp)
    per_sample = checkpoint["per_sample"] if checkpoint else []
    start_idx = checkpoint["completed"] if checkpoint else 0
    
    if start_idx > 0:
        print(f"Resuming from checkpoint: {start_idx}/{len(data)} completed", flush=True)
    
    start_time = time.time()
    
    # Process samples
    for idx in range(start_idx, len(data)):
        sample = data[idx]
        src = sample["text"]
        ref = get_clean_reference(sample["label"])
        
        # Check for cultural entities
        entities = lookup(src)
        has_entities = len(entities) > 0
        
        # Plain translation
        hyp_plain = call_gemini(client, SYSTEM_PLAIN, src)
        eval_plain = {
            "standard_metrics": compute_standard_metrics([hyp_plain], [ref]),
            "cuea": compute_cuea(src, hyp_plain, ref) if has_entities else {"cuea": None, "n_entities": 0, "details": []},
            "script_purity": compute_script_purity(hyp_plain),
            "errors": classify_errors(src, hyp_plain, ref) if has_entities else [],
        }
        
        # KB-augmented translation
        kb_context = build_rag_context(src)
        user_prompt_kb = f"{kb_context}\n\nTranslate: {src}"
        hyp_kb = call_gemini(client, SYSTEM_KB, user_prompt_kb)
        eval_kb = {
            "standard_metrics": compute_standard_metrics([hyp_kb], [ref]),
            "cuea": compute_cuea(src, hyp_kb, ref) if has_entities else {"cuea": None, "n_entities": 0, "details": []},
            "script_purity": compute_script_purity(hyp_kb),
            "errors": classify_errors(src, hyp_kb, ref) if has_entities else [],
        }
        
        per_sample.append({
            "id": sample["id"],
            "source": src,
            "reference": ref,
            "has_entities": has_entities,
            "hyp_plain": hyp_plain,
            "hyp_kb": hyp_kb,
            "eval_plain": eval_plain,
            "eval_kb": eval_kb,
            "topic": sample.get("topic"),
        })
        
        # Progress
        if (idx + 1) % 10 == 0:
            print(f"  [{idx+1}/{len(data)}] Processed", flush=True)
        
        # Checkpoint
        if (idx + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(per_sample, idx + 1, len(data), timestamp)
            print(f"  ✓ Checkpoint saved at {idx+1}", flush=True)
    
    total_time = time.time() - start_time
    
    # Final results
    results = compute_and_print_results(per_sample, total_time)
    
    # Save final results
    results_file = RESULTS_DIR / f"expGemini_results_{timestamp}.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "total_time_sec": total_time,
            "results": results,
            "per_sample": per_sample,
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Results saved to {results_file}", flush=True)
    print(f"Total time: {total_time/60:.1f} minutes", flush=True)


if __name__ == "__main__":
    main()
