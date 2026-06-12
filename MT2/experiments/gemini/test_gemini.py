"""
Quick test: Verify Gemini Devmate connection and run 10 samples
"""

import json, os, sys, time, re
from pathlib import Path

import httpx
from openai import OpenAI

# Setup paths
BASE_DIR = Path(__file__).parent.parent.parent  # MT2 root
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "kb"))
sys.path.insert(0, str(BASE_DIR / "eval"))

from cultural_kb_expanded import lookup, build_rag_context
from evaluation_framework import compute_standard_metrics, compute_cuea, compute_script_purity

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUNBUFFERED"] = "1"


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


def call_gemini(client, system_prompt, user_prompt):
    """Call Gemini model"""
    try:
        resp = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=512,
            stream=False
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        return ""


def load_data(limit=10):
    """Load first N samples"""
    data = []
    base = Path(__file__).parent.parent.parent / "data"
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = base / fname
        if not fpath.exists():
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if len(data) >= limit:
                    break
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    return data


def main():
    print("=" * 70, flush=True)
    print("Gemini 2.5 Flash Test: Vietnamese-Khmer Translation (10 samples)", flush=True)
    print("=" * 70, flush=True)
    
    # Connect
    print("\n[1] Connecting to Devmate OpenAI-compatible API...", flush=True)
    try:
        client = get_devmate_client()
        print("✓ Connected successfully", flush=True)
    except Exception as e:
        print(f"✗ Connection failed: {e}", flush=True)
        return
    
    # Test connection
    print("\n[2] Testing basic connectivity...", flush=True)
    test_resp = call_gemini(
        client, 
        "You are a helpful assistant.",
        "Say 'Hello' in exactly one word."
    )
    if test_resp:
        print(f"✓ Test response: {test_resp}", flush=True)
    else:
        print("✗ Test failed", flush=True)
        return
    
    # Load data
    print("\n[3] Loading 10 sample translations...", flush=True)
    data = load_data(10)
    print(f"✓ Loaded {len(data)} samples", flush=True)
    
    # Run evaluations
    print("\n[4] Running translations...", flush=True)
    print("-" * 70, flush=True)
    
    SYSTEM_PLAIN = (
        "You are an expert translator specializing in Vietnamese-Khmer translation. "
        "Translate the following Vietnamese text into Khmer. "
        "Output ONLY the Khmer translation, nothing else."
    )
    
    SYSTEM_KB = (
        "You are an expert translator specializing in Vietnamese-Khmer Krom translation. "
        "You will be given cultural terminology references. "
        "ALWAYS use the provided Khmer terms for cultural entities. "
        "Output ONLY the Khmer translation, nothing else."
    )
    
    results = []
    for i, sample in enumerate(data, 1):
        src = sample["text"]
        ref = sample["label"][0].split("###")[0].strip() if sample["label"] else ""
        
        print(f"\n[Sample {i}]", flush=True)
        print(f"Vietnamese: {src[:60]}...", flush=True)
        
        # Plain translation
        start = time.time()
        hyp_plain = call_gemini(client, SYSTEM_PLAIN, src)
        elapsed = time.time() - start
        print(f"  Plain (took {elapsed:.1f}s): {hyp_plain[:50]}...", flush=True)
        
        # KB translation
        kb_context = build_rag_context(src)
        user_prompt_kb = f"{kb_context}\n\nTranslate: {src}"
        start = time.time()
        hyp_kb = call_gemini(client, SYSTEM_KB, user_prompt_kb)
        elapsed = time.time() - start
        print(f"  KB-RAG (took {elapsed:.1f}s): {hyp_kb[:50]}...", flush=True)
        
        # Basic metrics
        if ref:
            metrics_plain = compute_standard_metrics([hyp_plain], [ref])
            metrics_kb = compute_standard_metrics([hyp_kb], [ref])
            print(f"  Metrics: Plain chrF++={metrics_plain['chrf++']:.1f}, KB-RAG chrF++={metrics_kb['chrf++']:.1f}", flush=True)
        
        results.append({
            "sample_id": sample["id"],
            "plain_hyp": hyp_plain,
            "kb_hyp": hyp_kb,
        })
    
    print("\n" + "=" * 70, flush=True)
    print(f"✓ Test completed successfully! Processed {len(results)} samples", flush=True)
    print("=" * 70, flush=True)
    
    # Save test results
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {results_file}", flush=True)


if __name__ == "__main__":
    main()
