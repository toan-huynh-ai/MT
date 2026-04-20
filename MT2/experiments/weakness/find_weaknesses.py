"""
Targeted weakness analysis for GPT-4o on Vietnamese-Khmer cultural MT.
Probes: kinship terms, Khmer Krom dialect, ritual/religious terms,
        cultural practices, complex food terminology, code-switching.
"""

import json
import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import sacrebleu
from dotenv import load_dotenv
import httpx
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(Path(__file__).parent / ".env")

RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)


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
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [Retry {attempt+1}] {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
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


SYSTEM_TRANSLATE = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "Translate the following Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_BACK_TRANSLATE = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "Translate the following Khmer text back into Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else."
)

SYSTEM_ANALYZE = (
    "You are a bilingual Vietnamese-Khmer linguistics expert. "
    "Compare the hypothesis Khmer translation with the reference Khmer translation. "
    "Identify specific errors in the hypothesis. "
    "Respond in JSON format with these fields: "
    '{"errors": [{"type": "...", "detail": "...", "severity": "high|medium|low"}], '
    '"overall_quality": "good|acceptable|poor", '
    '"cultural_accuracy": "correct|partially_correct|incorrect", '
    '"dialect_note": "standard_khmer|khmer_krom|mixed"}'
)


# ── Weakness Probes ──────────────────────────────────────────────

def find_samples_by_keywords(data, keywords, max_samples=10):
    """Find samples containing specific Vietnamese keywords."""
    matches = []
    for d in data:
        text = d.get("text", "").lower()
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        for kw in keywords:
            if kw.lower() in text:
                matches.append(d)
                break
    random.seed(42)
    if len(matches) > max_samples:
        matches = random.sample(matches, max_samples)
    return matches


def run_probe(client, probe_name, samples):
    """Run translation + back-translation + quality analysis on probe samples."""
    print(f"\n{'='*70}")
    print(f"PROBE: {probe_name} ({len(samples)} samples)")
    print(f"{'='*70}")

    results = []
    hyps = []
    refs = []

    for i, sample in enumerate(samples):
        ref = get_clean_reference(sample.get("label", []))
        source = sample["text"]

        print(f"  [{i+1}/{len(samples)}] {source[:70]}...")

        hyp = call_gpt4o(client, SYSTEM_TRANSLATE, f"Vietnamese: {source}")

        back_trans = call_gpt4o(
            client, SYSTEM_BACK_TRANSLATE, f"Khmer: {hyp}"
        )

        analysis_prompt = (
            f"Source Vietnamese: {source}\n"
            f"Reference Khmer: {ref}\n"
            f"Hypothesis Khmer: {hyp}\n"
            f"Back-translation of hypothesis: {back_trans}\n\n"
            f"Analyze the quality of the hypothesis translation."
        )
        analysis_raw = call_gpt4o(client, SYSTEM_ANALYZE, analysis_prompt)
        try:
            analysis = json.loads(analysis_raw)
        except Exception:
            analysis = {"raw": analysis_raw}

        hyps.append(hyp)
        refs.append(ref)
        results.append({
            "source": source,
            "reference": ref,
            "hypothesis": hyp,
            "back_translation": back_trans,
            "analysis": analysis,
            "topic": sample.get("topic"),
            "id": sample.get("id"),
        })

    scores = {
        "bleu": round(sacrebleu.corpus_bleu(hyps, [refs]).score, 2),
        "chrf++": round(sacrebleu.corpus_chrf(hyps, [refs], word_order=2).score, 2),
    }

    error_types = defaultdict(int)
    quality_dist = defaultdict(int)
    cultural_dist = defaultdict(int)
    dialect_dist = defaultdict(int)

    for r in results:
        a = r.get("analysis", {})
        quality_dist[a.get("overall_quality", "unknown")] += 1
        cultural_dist[a.get("cultural_accuracy", "unknown")] += 1
        dialect_dist[a.get("dialect_note", "unknown")] += 1
        for err in a.get("errors", []):
            error_types[err.get("type", "unknown")] += 1

    print(f"\n  Scores: BLEU={scores['bleu']}, chrF++={scores['chrf++']}")
    print(f"  Quality: {dict(quality_dist)}")
    print(f"  Cultural: {dict(cultural_dist)}")
    print(f"  Dialect: {dict(dialect_dist)}")
    print(f"  Error types: {dict(error_types)}")

    return {
        "probe": probe_name,
        "n_samples": len(samples),
        "scores": scores,
        "quality_distribution": dict(quality_dist),
        "cultural_accuracy": dict(cultural_dist),
        "dialect_distribution": dict(dialect_dist),
        "error_types": dict(error_types),
        "details": results,
    }


def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples")

    client = get_client()

    all_results = {}

    # ── Probe 1: Kinship Terms ──
    kinship_kw = [
        "cô", "chú", "bác", "dì", "dượng", "cháu", "con dâu", "con rể",
        "mẹ chồng", "bố chồng", "mẹ vợ", "bố vợ", "anh em",
        "họ hàng", "dòng tộc", "gia tộc", "thông gia",
    ]
    kinship_samples = find_samples_by_keywords(data, kinship_kw, max_samples=8)
    all_results["kinship"] = run_probe(client, "Kinship Terminology", kinship_samples)

    # ── Probe 2: Religious / Ritual Terms ──
    ritual_kw = [
        "sư", "Achar", "pagoda", "chùa", "tụng kinh", "cúng",
        "Phật", "hồn vía", "bùa", "cầu siêu", "tang lễ",
        "nhang đèn", "lễ vật", "khấn", "tắm Phật",
    ]
    ritual_samples = find_samples_by_keywords(data, ritual_kw, max_samples=8)
    all_results["ritual"] = run_probe(client, "Religious/Ritual Terms", ritual_samples)

    # ── Probe 3: Food / Cuisine Cultural Terms ──
    food_kw = [
        "mắm bò hóc", "bún nước lèo", "Num banh chok", "cốm dẹp",
        "bánh gừng", "bánh tét", "bánh ít", "canh chua", "thốt nốt",
        "nước lèo", "Pro-hốc", "Prahok", "bánh ống",
        "Som-lo", "Amok", "lạp", "cà ri Khmer",
    ]
    food_samples = find_samples_by_keywords(data, food_kw, max_samples=8)
    all_results["food"] = run_probe(client, "Food/Cuisine Cultural Terms", food_samples)

    # ── Probe 4: Khmer Krom Specific (farming, local practices) ──
    krom_kw = [
        "phum sóc", "Đồng bằng sông Cửu Long", "rẫy", "ruộng",
        "lúa mùa nổi", "nước lũ", "sông", "kênh",
        "vùng quê", "làng", "chợ nổi",
    ]
    krom_samples = find_samples_by_keywords(data, krom_kw, max_samples=8)
    all_results["khmer_krom"] = run_probe(client, "Khmer Krom Regional Terms", krom_samples)

    # ── Probe 5: Complex Sentences (long, multi-clause) ──
    complex_samples = [d for d in data
                       if len(d.get("text", "")) > 200
                       and get_clean_reference(d.get("label", []))]
    random.seed(42)
    complex_samples = random.sample(complex_samples, min(8, len(complex_samples)))
    all_results["complex"] = run_probe(client, "Complex Long Sentences", complex_samples)

    # ── Probe 6: Dialectal Greetings / Colloquial Speech ──
    colloquial_kw = [
        "dạ", "ạ", "nha", "hen", "nghen", "à nha",
        "quá trời", "thiệt", "dữ lắm", "vậy đó",
    ]
    colloquial_samples = find_samples_by_keywords(data, colloquial_kw, max_samples=8)
    all_results["colloquial"] = run_probe(client, "Colloquial/Dialectal Speech", colloquial_samples)

    # ── Save Results ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = RESULTS_DIR / f"weakness_probe_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("WEAKNESS PROBE SUMMARY")
    print("=" * 70)
    print(f"\n{'Probe':<30} {'chrF++':>8} {'Cultural':>15} {'Top Error Types'}")
    print("-" * 90)
    for name, res in all_results.items():
        chrf = res["scores"]["chrf++"]
        cultural = res["cultural_accuracy"]
        top_cultural = max(cultural, key=cultural.get) if cultural else "N/A"
        errors = res["error_types"]
        top_errors = ", ".join(f"{k}({v})" for k, v in
                              sorted(errors.items(), key=lambda x: -x[1])[:3])
        print(f"  {name:<28} {chrf:>8.2f} {top_cultural:>15}   {top_errors}")

    print(f"\nResults saved to: {outpath}")


if __name__ == "__main__":
    main()
