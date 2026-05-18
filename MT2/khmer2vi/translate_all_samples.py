"""
Translate ALL Khmer→Vietnamese samples (1852 samples)
====================================================
Translates entire dataset using GPT-4o and saves progress periodically.
Supports resume from last checkpoint if interrupted.
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

CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.json"
RESULTS_FILE = OUTPUT_DIR / f"all_translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

SYSTEM_KM2VI = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "Translate the following Khmer text into Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else."
)


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
            print(f"  [Retry {attempt+1}] {e}")
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
    return {"index": 0, "translations": []}


def save_checkpoint(index, translations):
    """Save checkpoint."""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"index": index, "translations": translations}, f, ensure_ascii=False, indent=2)


def save_results(translations):
    """Save final results."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "experiment": "all_km2vi_translations",
            "total": len(translations),
            "timestamp": datetime.now().isoformat(),
            "translations": translations
        }, f, ensure_ascii=False, indent=2)


def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples")

    pairs = prepare_km2vi_pairs(data)
    print(f"Prepared {len(pairs)} Km→Vi pairs")

    # Load checkpoint
    checkpoint = load_checkpoint()
    start_index = checkpoint["index"]
    translations = checkpoint["translations"]

    if start_index > 0:
        print(f"\n✓ Resuming from checkpoint: {start_index}/{len(pairs)}")
    else:
        print(f"\n✓ Starting fresh")

    print("\nConnecting to GPT-4o...")
    client = get_client()

    test = call_gpt4o(client, "Translate Khmer to Vietnamese.", "Khmer: សួស្តី")
    if not test:
        print("ERROR: Cannot connect. Check .env")
        sys.exit(1)
    print(f"  OK: {test}")

    # Process remaining pairs
    print(f"\n{'='*70}")
    print(f"TRANSLATING {len(pairs)} SAMPLES")
    print(f"{'='*70}\n")

    for i in range(start_index, len(pairs)):
        p = pairs[i]
        km_text = p["km_source"][:60] + ("..." if len(p["km_source"]) > 60 else "")

        # Print progress
        percent = (i + 1) / len(pairs) * 100
        print(f"[{i+1:4d}/{len(pairs)}] {percent:5.1f}% | {km_text:65s}", end="", flush=True)

        # Translate
        hyp = call_gpt4o(client, SYSTEM_KM2VI, f"Khmer: {p['km_source']}")

        # Store
        translations.append({
            **p,
            "hypothesis": hyp,
            "index": i + 1,
        })

        # Save checkpoint every 50 samples
        if (i + 1) % 50 == 0:
            save_checkpoint(i + 1, translations)
            print(" ✓ [checkpoint saved]")
        else:
            print(" ✓")

        time.sleep(0.5)  # Rate limiting

    # Final save
    print(f"\n{'='*70}")
    print("SAVING RESULTS...")
    save_results(translations)
    print(f"✅ Saved to: {RESULTS_FILE}")
    print(f"✅ Total translations: {len(translations)}")

    # Cleanup checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("✓ Checkpoint cleaned up")

    print(f"\n{'='*70}")
    print("TRANSLATION COMPLETE!")
    print(f"Results: {RESULTS_FILE.name}")


if __name__ == "__main__":
    main()
