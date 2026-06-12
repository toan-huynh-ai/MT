"""
Full Bidirectional Evaluation: Gemini 2.5 Flash (Vi→Khmer + Khmer→Vi)
====================================================================
Uses OpenAI-compatible API endpoint. Saves checkpoints every 50 samples.
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
    http_client = httpx.Client(
        proxy="http://rb-proxy-apac.bosch.com:8080",
        verify=False
    )
    
    return OpenAI(
        api_key="vQSFPyI6QmjfvoahtLnyJWU8ZoI-y0Gn",
        base_url="https://devmate.bosch.com/api/v3",
        http_client=http_client
    )


def call_gemini(client, system_prompt, user_prompt, max_retries=3):
    """Call Gemini 2.5 Flash model"""
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="gemini-2.5-flash",
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
            print(f"    [Retry {attempt+1}] {str(e)[:60]}...", flush=True)
            time.sleep(wait)
    return ""


def load_data():
    """Load translation dataset"""
    data = []
    base = BASE_DIR / "data"
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
    """Extract clean reference translation"""
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


SYSTEM_VIKH_PLAIN = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "Translate the following Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_VIKH_KB = (
    "You are an expert translator specializing in Vietnamese-Khmer Krom translation. "
    "You will be given cultural terminology references. "
    "ALWAYS use the provided Khmer terms for cultural entities. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_KHVI_PLAIN = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "Translate the following Khmer text into Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else."
)

SYSTEM_KHVI_KB = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "You will be given cultural terminology references. "
    "ALWAYS use the provided Vietnamese terms for cultural entities. "
    "Output ONLY the Vietnamese translation, nothing else."
)


def load_checkpoint(timestamp):
    """Load checkpoint if exists"""
    path = RESULTS_DIR / f"bidirectional_checkpoint_{timestamp}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_checkpoint(per_sample, completed, total, timestamp):
    """Save checkpoint"""
    path = RESULTS_DIR / f"bidirectional_checkpoint_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"completed": completed, "total": total, "per_sample": per_sample},
                  f, ensure_ascii=False, default=str)


def compute_and_print_results(per_sample, total_time):
    """Compute and display final results"""
    n_total = len(per_sample)
    n_ent = sum(1 for r in per_sample if r.get("has_entities", False))
    
    # Vietnamese → Khmer
    vikh_plain = [r["vikh_plain"] for r in per_sample]
    vikh_kb = [r["vikh_kb"] for r in per_sample]
    vikh_refs = [r["vikh_reference"] for r in per_sample]
    
    # Khmer → Vietnamese
    khvi_plain = [r["khvi_plain"] for r in per_sample]
    khvi_kb = [r["khvi_kb"] for r in per_sample]
    khvi_refs = [r["khvi_reference"] for r in per_sample]
    
    # Compute metrics
    m_vikh_p = compute_standard_metrics(vikh_plain, vikh_refs)
    m_vikh_k = compute_standard_metrics(vikh_kb, vikh_refs)
    m_khvi_p = compute_standard_metrics(khvi_plain, khvi_refs)
    m_khvi_k = compute_standard_metrics(khvi_kb, khvi_refs)
    
    print("\n" + "=" * 80, flush=True)
    print(f"GEMINI 2.5 FLASH BIDIRECTIONAL RESULTS — {n_total} samples ({total_time/60:.1f} min)", flush=True)
    print("=" * 80, flush=True)

    print(f"\n{'Vietnamese → Khmer Translation':^80}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Metric':<40} {'Plain':>15} {'KB-RAG':>15} {'Delta':>10}", flush=True)
    print(f"{'chrF++ (all)':<40} {m_vikh_p['chrf++']:>15.2f} {m_vikh_k['chrf++']:>15.2f} {m_vikh_k['chrf++'] - m_vikh_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'BLEU (all)':<40} {m_vikh_p['bleu']:>15.2f} {m_vikh_k['bleu']:>15.2f} {m_vikh_k['bleu'] - m_vikh_p['bleu']:>+10.2f}", flush=True)

    print(f"\n{'Khmer → Vietnamese Translation':^80}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Metric':<40} {'Plain':>15} {'KB-RAG':>15} {'Delta':>10}", flush=True)
    print(f"{'chrF++ (all)':<40} {m_khvi_p['chrf++']:>15.2f} {m_khvi_k['chrf++']:>15.2f} {m_khvi_k['chrf++'] - m_khvi_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'BLEU (all)':<40} {m_khvi_p['bleu']:>15.2f} {m_khvi_k['bleu']:>15.2f} {m_khvi_k['bleu'] - m_khvi_p['bleu']:>+10.2f}", flush=True)

    print(f"\n{'BIDIRECTIONAL SUMMARY':^80}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Pair':<40} {'Plain chrF++':>15} {'KB-RAG chrF++':>15}", flush=True)
    print(f"{'Vi → Km':<40} {m_vikh_p['chrf++']:>15.2f} {m_vikh_k['chrf++']:>15.2f}", flush=True)
    print(f"{'Km → Vi':<40} {m_khvi_p['chrf++']:>15.2f} {m_khvi_k['chrf++']:>15.2f}", flush=True)
    print(f"{'Average':<40} {(m_vikh_p['chrf++'] + m_khvi_p['chrf++'])/2:>15.2f} {(m_vikh_k['chrf++'] + m_khvi_k['chrf++'])/2:>15.2f}", flush=True)

    return {
        "model": "gemini-2.5-flash",
        "total_samples": n_total,
        "timestamp": datetime.now().isoformat(),
        "vikh": {
            "plain_chrf": m_vikh_p["chrf++"],
            "kb_chrf": m_vikh_k["chrf++"],
            "plain_bleu": m_vikh_p["bleu"],
            "kb_bleu": m_vikh_k["bleu"],
            "chrf_delta": m_vikh_k["chrf++"] - m_vikh_p["chrf++"],
        },
        "khvi": {
            "plain_chrf": m_khvi_p["chrf++"],
            "kb_chrf": m_khvi_k["chrf++"],
            "plain_bleu": m_khvi_p["bleu"],
            "kb_bleu": m_khvi_k["bleu"],
            "chrf_delta": m_khvi_k["chrf++"] - m_khvi_p["chrf++"],
        },
    }


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Gemini bidirectional evaluation at {timestamp}", flush=True)
    
    # Initialize client
    client = get_devmate_client()
    print("✓ Connected to Devmate (OpenAI-compatible API)", flush=True)
    
    # Load data
    data = load_data()
    if not data:
        print("ERROR: No data loaded", flush=True)
        sys.exit(1)
    print(f"✓ Loaded {len(data)} samples", flush=True)
    
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
        src_vi = sample["text"]
        ref_km = get_clean_reference(sample["label"])
        
        has_entities = len(lookup(src_vi)) > 0
        
        # Vietnamese → Khmer (Plain)
        vikh_plain = call_gemini(client, SYSTEM_VIKH_PLAIN, src_vi)
        
        # Vietnamese → Khmer (KB-RAG)
        kb_context = build_rag_context(src_vi)
        user_prompt_kb = f"{kb_context}\n\nTranslate: {src_vi}"
        vikh_kb = call_gemini(client, SYSTEM_VIKH_KB, user_prompt_kb)
        
        # Khmer → Vietnamese (using reference as source)
        khvi_plain = call_gemini(client, SYSTEM_KHVI_PLAIN, ref_km)
        khvi_kb = call_gemini(client, SYSTEM_KHVI_KB, ref_km)
        
        per_sample.append({
            "id": sample["id"],
            "source_vi": src_vi,
            "vikh_reference": ref_km,
            "khvi_reference": src_vi,
            "has_entities": has_entities,
            "vikh_plain": vikh_plain,
            "vikh_kb": vikh_kb,
            "khvi_plain": khvi_plain,
            "khvi_kb": khvi_kb,
        })
        
        # Progress
        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed
            remaining = (len(data) - idx - 1) / rate if rate > 0 else 0
            print(f"  [{idx+1}/{len(data)}] {rate:.1f} samples/s | ETA: {remaining/60:.0f}m", flush=True)
        
        # Checkpoint
        if (idx + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(per_sample, idx + 1, len(data), timestamp)
            print(f"  ✓ Checkpoint saved at {idx+1}", flush=True)
    
    total_time = time.time() - start_time
    
    # Final results
    results = compute_and_print_results(per_sample, total_time)
    
    # Save final results
    results_file = RESULTS_DIR / f"gemini_bidirectional_{timestamp}.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "total_time_sec": total_time,
            "results": results,
            "per_sample": per_sample,
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Results saved to {results_file}", flush=True)
    print(f"Total time: {total_time/60:.1f} minutes ({total_time/len(data):.1f}s per sample)", flush=True)


if __name__ == "__main__":
    main()
