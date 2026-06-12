"""
Zero-shot Translation: Bahnar → Vietnamese
==============================================
Translates Bahnar text to Vietnamese language using GPT-4o via Azure OpenAI.
Uses zero-shot approach without few-shot examples.

Data format: JSONL with Vietnamese text, reference Bahnar translations for reverse direction
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

import httpx
import sacrebleu
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Corporate proxy workaround
os.environ.setdefault("AZURE_IDENTITY_DISABLE_CP1", "true")
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Blocked items log
BLOCKED_ITEMS_FILE = OUTPUT_DIR / "blocked_by_content_filter.jsonl"


# ── Azure OpenAI Client ──────────────────────────────────────────────

def get_client() -> AzureOpenAI:
    """Create and return Azure OpenAI client."""
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


def call_gpt4o(client: AzureOpenAI, system_prompt: str, user_prompt: str,
               max_retries: int = 3) -> tuple[str, str]:
    """Call GPT-4o with retry logic. Returns (status, result).
    
    Status can be:
    - 'success': Translation successful
    - 'content_filter': Blocked by Azure content filter
    - 'error': Other error (will retry)
    """
    deployment = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o-RTA_Configurator")
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
            return ("success", resp.choices[0].message.content.strip())
        except Exception as e:
            error_str = str(e)
            # Check if content filter error
            if "content_filter" in error_str or "ResponsibleAIPolicyViolation" in error_str:
                return ("content_filter", "")
            
            print(f"  [Attempt {attempt+1}/{max_retries}] Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return ("error", "")


# ── Data Loading ──────────────────────────────────────────────────

def load_data(data_path: str) -> list[dict]:
    """Load JSONL data file."""
    data = []
    fpath = Path(data_path)
    if not fpath.exists():
        print(f"Error: Data file not found: {fpath}")
        return data
    
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse JSON line: {e}")
                    continue
    
    print(f"Loaded {len(data)} records from {fpath}")
    return data


def get_clean_reference(labels: list) -> str:
    """Extract the cleanest reference translation."""
    if not labels:
        return ""
    
    best = ""
    for lbl in labels:
        if isinstance(lbl, str):
            clean = lbl.split("###")[0].strip()
            if clean and len(clean) > len(best):
                best = clean
    
    return best if best else (labels[0] if labels else "")


# ── Prompt Templates ──────────────────────────────────────────────

SYSTEM_ZERO_SHOT_BAHNAR_TO_VI = (
    "You are an expert translator specializing in Bahnar-Vietnamese translation. "
    "You have deep knowledge of Bahnar language, culture, and linguistic patterns. "
    "Translate the following Bahnar text (a language spoken in Vietnam's Central Highlands) into Vietnamese. "
    "Preserve cultural nuances and ensure the translation sounds natural in Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else. Do not include explanations or alternatives."
)


# ── Translation ────────────────────────────────────────────────

def translate_all(client: AzureOpenAI, data: list[dict], output_file: str = None) -> dict:
    """Translate all Bahnar texts to Vietnamese."""
    print("\n" + "="*70)
    print("ZERO-SHOT TRANSLATION: Bahnar → Vietnamese")
    print("="*70)
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"bahnar_to_vi_zeroshot_{timestamp}.jsonl"
    else:
        output_file = Path(output_file)
    
    results = []
    blocked_items = []
    hypotheses = []
    references = []
    
    for i, record in enumerate(data):
        vi_text = record.get("text", "").strip()  # This is Vietnamese reference
        bahnar_ref_list = record.get("label", [])
        
        if not bahnar_ref_list:
            continue
        
        bahnar_text = get_clean_reference(bahnar_ref_list)
        if not bahnar_text:
            continue
        
        print(f"  [{i+1}/{len(data)}] Translating: {bahnar_text[:70]}...")
        
        try:
            status, vi_predicted = call_gpt4o(
                client,
                SYSTEM_ZERO_SHOT_BAHNAR_TO_VI,
                f"Bahnar: {bahnar_text}"
            )
            
            if status == "content_filter":
                # Log blocked item but continue
                print(f"    ⚠ BLOCKED by content filter (skipping)")
                blocked_items.append({
                    "id": record.get("id"),
                    "source_bahnar": bahnar_text,
                    "reference_vi": vi_text,
                    "topic": record.get("topic", ""),
                })
                continue
            elif status != "success":
                print(f"    ✗ Failed to translate (skipping)")
                continue
            
            hypotheses.append(vi_predicted)
            if vi_text:
                references.append(vi_text)
            
            result_record = {
                "id": record.get("id"),
                "source_bahnar": bahnar_text,
                "reference_vi": vi_text,
                "predicted_vi": vi_predicted,
                "topic": record.get("topic", ""),
                "order": record.get("order"),
            }
            results.append(result_record)
            
            print(f"    Source (Bahnar): {bahnar_text[:60]}...")
            print(f"    Predicted (Vi): {vi_predicted[:60]}...")
            if vi_text:
                print(f"    Reference (Vi): {vi_text[:60]}...")
            print()
            
        except Exception as e:
            print(f"    Unexpected error: {e}")
            continue
    
    # Save results
    with open(output_file, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    print(f"\nResults saved to: {output_file}")
    
    # Save blocked items
    if blocked_items:
        with open(BLOCKED_ITEMS_FILE, "w", encoding="utf-8") as f:
            for item in blocked_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Blocked items saved to: {BLOCKED_ITEMS_FILE}")
    
    # Compute metrics if we have references
    scores = {}
    if references and hypotheses:
        try:
            bleu = sacrebleu.corpus_bleu(hypotheses, [references])
            chrf = sacrebleu.corpus_chrf(hypotheses, [references], word_order=2)
            scores = {
                "bleu": round(bleu.score, 2),
                "chrf++": round(chrf.score, 2),
                "n_samples": len(results),
                "n_with_reference": len(references),
            }
            print(f"\nScores:")
            print(f"  BLEU: {scores['bleu']}")
            print(f"  chrF++: {scores['chrf++']}")
            print(f"  Samples: {scores['n_samples']}")
        except Exception as e:
            print(f"Warning: Could not compute metrics: {e}")
    
    return {
        "output_file": str(output_file),
        "total_translated": len(results),
        "total_blocked": len(blocked_items),
        "scores": scores,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    """Main entry point."""
    # Data path
    data_path = r"C:\Users\HOY9HC\Desktop\Code\Learning\MT2\bahnar\data\vi_bahnar.jsonl"
    
    # Load data
    data = load_data(data_path)
    if not data:
        print("No data to translate")
        return
    
    # Initialize client
    client = get_client()
    
    # Translate
    result = translate_all(client, data)
    
    print("\n" + "="*70)
    print("Translation completed!")
    print(f"Total: {result['total_translated']} samples translated")
    print(f"Blocked: {result['total_blocked']} samples (by content filter)")
    print("="*70)


if __name__ == "__main__":
    main()
