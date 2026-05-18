"""
Translate ALL Khmer→Vietnamese samples with PARALLEL WORKERS (1852 samples)
==========================================================================
Uses ThreadPoolExecutor for 4 parallel workers to speed up translation.
Supports resume from checkpoint, automatic rate limiting.
"""

import json
import os
import re
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import queue

from dotenv import load_dotenv
import httpx
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.parent
load_dotenv(BASE / ".env")

OUTPUT_DIR = Path(__file__).parent / "translation_output"
OUTPUT_DIR.mkdir(exist_ok=True)

CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint_parallel.json"
RESULTS_FILE = OUTPUT_DIR / f"all_translations_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Configuration
NUM_WORKERS = 4
RATE_LIMIT_DELAY = 0.3  # seconds between API calls

SYSTEM_KM2VI = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "Translate the following Khmer text into Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else."
)

# Thread-safe progress tracking
progress_lock = Lock()
progress_dict = {}


def get_client() -> AzureOpenAI:
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
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return ""


def load_data():
    data = []
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = BASE / "data" / fname
        if not fpath.exists():
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    return data


def get_clean_khmer(labels):
    """Get cleanest Khmer text from labels (no *** annotations)."""
    best = ""
    for lbl in labels:
        clean = lbl.split("###")[0].strip()
        parts = clean.split("***")
        if len(parts) == 1 and len(clean) > len(best):
            best = clean
    if not best and labels:
        raw = labels[0].split("###")[-1].strip()
        best = re.sub(r'\S+\s*\*\*\*\s*', '', raw).strip()
        if not best:
            best = labels[0].split("###")[0].strip()
            best = re.sub(r'\*\*\*', ' ', best).strip()
    return best


def prepare_km2vi_pairs(data):
    """Prepare (khmer_source, vietnamese_reference) pairs."""
    pairs = []
    for d in data:
        km = get_clean_khmer(d.get("label", []))
        vi = d.get("text", "").strip()
        if km and vi and len(km) > 10:
            pairs.append({
                "km_source": km,
                "vi_reference": vi,
                "id": d.get("id"),
                "topic": d.get("topic"),
                "order": d.get("order"),
                "question": d.get("question"),
            })
    return pairs


def load_checkpoint():
    """Load checkpoint if exists."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_indices": set(), "translations": []}


def save_checkpoint(completed_indices, translations):
    """Save checkpoint."""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "completed_indices": list(completed_indices),
            "translations": translations
        }, f, ensure_ascii=False, indent=2)


def save_results(translations):
    """Save final results."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "experiment": "all_km2vi_translations_parallel",
            "total": len(translations),
            "workers": NUM_WORKERS,
            "timestamp": datetime.now().isoformat(),
            "translations": translations
        }, f, ensure_ascii=False, indent=2)


def translate_item(client, index, pair, total):
    """Translate a single item (called by worker thread)."""
    time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
    
    hyp = call_gpt4o(client, SYSTEM_KM2VI, f"Khmer: {pair['km_source']}")
    
    result = {
        **pair,
        "hypothesis": hyp,
        "index": index + 1,
    }
    
    # Update progress display
    with progress_lock:
        progress_dict[index] = result
        completed = len(progress_dict)
        percent = (completed / total) * 100
        km_text = pair["km_source"][:50] + ("..." if len(pair["km_source"]) > 50 else "")
        print(f"\r[{completed:4d}/{total}] {percent:5.1f}% | {km_text:55s} ✓", end="", flush=True)
    
    return index, result


def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples")

    pairs = prepare_km2vi_pairs(data)
    print(f"Prepared {len(pairs)} Km→Vi pairs")

    # Load checkpoint
    checkpoint = load_checkpoint()
    completed_indices = set(checkpoint["completed_indices"])
    existing_translations = {t["index"]: t for t in checkpoint["translations"]}

    if completed_indices:
        print(f"\n✓ Resuming from checkpoint: {len(completed_indices)}/{len(pairs)} completed")
    else:
        print(f"\n✓ Starting fresh")

    print("\nConnecting to GPT-4o...")
    client = get_client()

    test = call_gpt4o(client, "Translate Khmer to Vietnamese.", "Khmer: សួស្តី")
    if not test:
        print("ERROR: Cannot connect. Check .env")
        sys.exit(1)
    print(f"  OK: {test}")

    # Filter remaining items
    remaining_pairs = [(i, p) for i, p in enumerate(pairs) if i not in completed_indices]
    print(f"\n{'='*70}")
    print(f"TRANSLATING {len(remaining_pairs)} SAMPLES WITH {NUM_WORKERS} WORKERS")
    print(f"{'='*70}\n")

    translations_by_index = {}

    # Process with thread pool
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {
            executor.submit(translate_item, client, idx, pair, len(pairs)): idx
            for idx, pair in remaining_pairs
        }

        for future in as_completed(futures):
            try:
                idx, result = future.result()
                translations_by_index[idx] = result
                
                # Save checkpoint every 50 completed
                if (len(translations_by_index) + len(completed_indices)) % 50 == 0:
                    all_indices = completed_indices | set(translations_by_index.keys())
                    all_translations = list(existing_translations.values()) + list(translations_by_index.values())
                    save_checkpoint(all_indices, all_translations)
                    print(" [checkpoint saved]", end="", flush=True)
                    
            except Exception as e:
                print(f"\nError: {e}")

    # Combine results
    all_indices = completed_indices | set(translations_by_index.keys())
    all_translations = list(existing_translations.values()) + list(translations_by_index.values())
    
    # Sort by index
    all_translations.sort(key=lambda x: x.get("index", 0))

    # Final save
    print(f"\n\n{'='*70}")
    print("SAVING RESULTS...")
    save_results(all_translations)
    print(f"✅ Saved to: {RESULTS_FILE}")
    print(f"✅ Total translations: {len(all_translations)}")

    # Cleanup checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("✓ Checkpoint cleaned up")

    print(f"\n{'='*70}")
    print("TRANSLATION COMPLETE!")
    print(f"Results: {RESULTS_FILE.name}")
    print(f"Config: {NUM_WORKERS} workers, {RATE_LIMIT_DELAY}s rate limit")


if __name__ == "__main__":
    main()
