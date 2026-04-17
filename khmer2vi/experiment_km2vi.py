"""
Khmer→Vietnamese Translation Experiments
==========================================
Tests GPT-4o on the REVERSE direction: Khmer Krom → Vietnamese.
Key question: Does GPT-4o struggle differently when the SOURCE is Khmer Krom?

Experiments:
  1. Zero-shot Km→Vi baseline (50 samples)
  2. Weakness probes by category (8 samples × 6 probes)
  3. Dialogue context effect (10 conversations)
  4. Back-translation consistency check (Vi→Km→Vi round-trip)

Data: source = label[0] (Khmer), reference = text (Vietnamese)
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

import sacrebleu
from dotenv import load_dotenv
import httpx
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.parent
load_dotenv(BASE / ".env")

RESULTS_DIR = Path(__file__).parent / "results"
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
        fpath = BASE / fname
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


# ── Prompts ──────────────────────────────────────────────────────

SYSTEM_KM2VI = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "Translate the following Khmer text into Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else."
)

SYSTEM_KM2VI_CONTEXT = (
    "You are an expert translator specializing in Khmer-Vietnamese translation. "
    "You are translating a conversation between an interviewer and a Khmer person. "
    "Previous turns are provided for context. "
    "Translate ONLY the last Khmer utterance into Vietnamese. "
    "Output ONLY the Vietnamese translation, nothing else."
)

SYSTEM_ANALYZE = (
    "You are a bilingual Vietnamese-Khmer linguistics expert. "
    "The SOURCE is Khmer Krom (from Vietnam's Mekong Delta). "
    "Compare the hypothesis Vietnamese translation with the reference. "
    "Focus on: (1) cultural entity preservation, (2) Khmer Krom-specific terms, "
    "(3) meaning accuracy, (4) naturalness. "
    "Respond in JSON: "
    '{"errors": [{"type": "...", "detail": "...", "severity": "high|medium|low"}], '
    '"overall_quality": "good|acceptable|poor", '
    '"cultural_accuracy": "correct|partially_correct|incorrect", '
    '"krom_handling": "recognized|ignored|confused"}'
)


# ── Experiment 1: Zero-shot Km→Vi ────────────────────────────────

def run_exp1_zero_shot(client, pairs, n=50):
    print("\n" + "=" * 70)
    print("EXP 1: Zero-shot Km→Vi (n={})".format(n))
    print("=" * 70)

    random.seed(42)
    selected = random.sample(pairs, min(n, len(pairs)))

    hyps, refs = [], []
    details = []

    for i, p in enumerate(selected):
        print(f"  [{i+1}/{len(selected)}] {p['km_source'][:60]}...")

        hyp = call_gpt4o(client, SYSTEM_KM2VI, f"Khmer: {p['km_source']}")

        hyps.append(hyp)
        refs.append(p["vi_reference"])
        details.append({**p, "hypothesis": hyp})

    bleu = sacrebleu.corpus_bleu(hyps, [refs])
    chrf = sacrebleu.corpus_chrf(hyps, [refs], word_order=2)

    print(f"\n  BLEU={bleu.score:.2f}, chrF++={chrf.score:.2f}")
    return {
        "experiment": "km2vi_zero_shot",
        "n": len(selected),
        "bleu": round(bleu.score, 2),
        "chrf++": round(chrf.score, 2),
        "details": details,
    }


# ── Experiment 2: Weakness probes ────────────────────────────────

def find_km_samples_by_vi_keywords(pairs, keywords, max_n=8):
    """Find Km→Vi pairs where the VIETNAMESE reference contains keywords."""
    matches = []
    for p in pairs:
        vi_lower = p["vi_reference"].lower()
        for kw in keywords:
            if kw.lower() in vi_lower:
                matches.append(p)
                break
    random.seed(42)
    if len(matches) > max_n:
        matches = random.sample(matches, max_n)
    return matches


def run_exp2_weakness_probes(client, pairs):
    print("\n" + "=" * 70)
    print("EXP 2: Km→Vi Weakness Probes")
    print("=" * 70)

    probes = {
        "food_cultural": ["mắm bò hóc", "cốm dẹp", "bún nước lèo", "bánh gừng",
                          "bánh tét", "bánh ít", "thốt nốt", "bánh ống"],
        "religious": ["chùa", "tụng kinh", "cúng", "Phật", "sư", "nhang đèn",
                      "cầu siêu", "Achar", "tang lễ"],
        "kinship": ["bác", "chú", "dì", "cô", "dượng", "con dâu", "họ hàng",
                    "dòng tộc", "gia tộc", "thông gia"],
        "khmer_krom_regional": ["phum sóc", "ruộng", "rẫy", "lúa", "làng",
                                 "Đồng bằng sông Cửu Long", "kênh"],
        "festivals": ["Chol Chnam", "Ok Om Bok", "Sene Dolta", "Kathina",
                       "lễ hội", "cốm dẹp", "đua ghe"],
        "colloquial": ["dạ", "ạ", "nha", "bác ơi", "vậy đó"],
    }

    all_probe_results = {}

    for probe_name, keywords in probes.items():
        samples = find_km_samples_by_vi_keywords(pairs, keywords, max_n=8)
        if not samples:
            print(f"  [{probe_name}] No samples found, skipping")
            continue

        print(f"\n  [{probe_name}] {len(samples)} samples")

        hyps, refs = [], []
        probe_details = []

        for i, p in enumerate(samples):
            hyp = call_gpt4o(client, SYSTEM_KM2VI, f"Khmer: {p['km_source']}")

            analysis_prompt = (
                f"Source Khmer (Khmer Krom): {p['km_source']}\n"
                f"Reference Vietnamese: {p['vi_reference']}\n"
                f"Hypothesis Vietnamese: {hyp}\n\n"
                f"Analyze the quality."
            )
            analysis_raw = call_gpt4o(client, SYSTEM_ANALYZE, analysis_prompt)
            try:
                analysis = json.loads(analysis_raw)
            except Exception:
                analysis = {"raw": analysis_raw}

            hyps.append(hyp)
            refs.append(p["vi_reference"])
            probe_details.append({**p, "hypothesis": hyp, "analysis": analysis})

        bleu = sacrebleu.corpus_bleu(hyps, [refs])
        chrf = sacrebleu.corpus_chrf(hyps, [refs], word_order=2)

        quality_dist = defaultdict(int)
        cultural_dist = defaultdict(int)
        krom_dist = defaultdict(int)
        error_types = defaultdict(int)

        for d in probe_details:
            a = d.get("analysis", {})
            if isinstance(a, dict):
                quality_dist[a.get("overall_quality", "unknown")] += 1
                cultural_dist[a.get("cultural_accuracy", "unknown")] += 1
                krom_dist[a.get("krom_handling", "unknown")] += 1
                for err in a.get("errors", []):
                    error_types[err.get("type", "unknown")] += 1

        print(f"    BLEU={bleu.score:.2f}, chrF++={chrf.score:.2f}")
        print(f"    Quality: {dict(quality_dist)}")
        print(f"    Cultural: {dict(cultural_dist)}")
        print(f"    Krom handling: {dict(krom_dist)}")
        if error_types:
            print(f"    Errors: {dict(error_types)}")

        all_probe_results[probe_name] = {
            "n": len(samples),
            "bleu": round(bleu.score, 2),
            "chrf++": round(chrf.score, 2),
            "quality": dict(quality_dist),
            "cultural": dict(cultural_dist),
            "krom_handling": dict(krom_dist),
            "errors": dict(error_types),
            "details": probe_details,
        }

    return {"experiment": "km2vi_weakness_probes", "probes": all_probe_results}


# ── Experiment 3: Dialogue context ───────────────────────────────

def run_exp3_dialogue_context(client, data, n_convs=10):
    print("\n" + "=" * 70)
    print("EXP 3: Km→Vi Dialogue Context Effect")
    print("=" * 70)

    dialogue = [d for d in data if d.get("topic") is not None]
    convs = defaultdict(list)
    for d in dialogue:
        km = get_clean_khmer(d.get("label", []))
        if km and d.get("text"):
            convs[d["id"]].append({**d, "km": km})
    for cid in convs:
        convs[cid].sort(key=lambda x: x.get("order", 0) or 0)

    long_convs = {cid: turns for cid, turns in convs.items() if len(turns) >= 4}
    random.seed(42)
    selected_cids = random.sample(list(long_convs.keys()), min(n_convs, len(long_convs)))

    iso_hyps, ctx_hyps, refs = [], [], []
    details = []

    for ci, cid in enumerate(selected_cids):
        turns = long_convs[cid]
        target_idx = len(turns) - 1
        target = turns[target_idx]
        vi_ref = target["text"]
        km_source = target["km"]

        if not vi_ref or not km_source:
            continue

        topic = target.get("topic", "unknown")
        print(f"  [{ci+1}/{len(selected_cids)}] Conv {cid}, topic: {topic[:40]}...")

        hyp_iso = call_gpt4o(client, SYSTEM_KM2VI, f"Khmer: {km_source}")

        ctx_parts = ["Previous conversation turns:\n"]
        for j in range(target_idx):
            t = turns[j]
            ctx_parts.append(f"Khmer: {t['km']}")
            ctx_parts.append(f"Vietnamese: {t['text']}\n")
        ctx_parts.append(f"Now translate the next turn:\nKhmer: {km_source}")
        ctx_prompt = "\n".join(ctx_parts)

        hyp_ctx = call_gpt4o(client, SYSTEM_KM2VI_CONTEXT, ctx_prompt)

        iso_hyps.append(hyp_iso)
        ctx_hyps.append(hyp_ctx)
        refs.append(vi_ref)

        iso_chrf = sacrebleu.sentence_chrf(hyp_iso, [vi_ref], word_order=2).score
        ctx_chrf = sacrebleu.sentence_chrf(hyp_ctx, [vi_ref], word_order=2).score

        details.append({
            "id": cid, "topic": topic,
            "km_source": km_source, "vi_reference": vi_ref,
            "hyp_isolated": hyp_iso, "hyp_context": hyp_ctx,
            "chrf_isolated": round(iso_chrf, 1),
            "chrf_context": round(ctx_chrf, 1),
            "delta": round(ctx_chrf - iso_chrf, 1),
        })

    scores_iso = sacrebleu.corpus_chrf(iso_hyps, [refs], word_order=2)
    scores_ctx = sacrebleu.corpus_chrf(ctx_hyps, [refs], word_order=2)

    wins = sum(1 for d in details if d["delta"] > 0)

    print(f"\n  Isolated:     chrF++={scores_iso.score:.2f}")
    print(f"  With context: chrF++={scores_ctx.score:.2f}")
    print(f"  Delta:        {scores_ctx.score - scores_iso.score:+.2f}")
    print(f"  Win rate:     {wins}/{len(details)}")

    print(f"\n  Per-sample:")
    for d in details:
        marker = "▲" if d["delta"] > 0 else "▼" if d["delta"] < 0 else "="
        print(f"    {d['topic'][:35]:35s} iso={d['chrf_isolated']:5.1f} ctx={d['chrf_context']:5.1f} {marker}{d['delta']:+.1f}")

    return {
        "experiment": "km2vi_dialogue_context",
        "scores_isolated": round(scores_iso.score, 2),
        "scores_context": round(scores_ctx.score, 2),
        "delta": round(scores_ctx.score - scores_iso.score, 2),
        "win_rate": f"{wins}/{len(details)}",
        "details": details,
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples")

    pairs = prepare_km2vi_pairs(data)
    print(f"Prepared {len(pairs)} Km→Vi pairs")

    print("\nConnecting to GPT-4o...")
    client = get_client()

    test = call_gpt4o(client, "Translate Khmer to Vietnamese.", "Khmer: សួស្តី")
    if not test:
        print("ERROR: Cannot connect. Check .env")
        sys.exit(1)
    print(f"  OK: {test}")

    results = {}

    results["exp1"] = run_exp1_zero_shot(client, pairs, n=50)
    results["exp2"] = run_exp2_weakness_probes(client, pairs)
    results["exp3"] = run_exp3_dialogue_context(client, data, n_convs=10)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("KM→VI SUMMARY")
    print("=" * 70)

    e1 = results["exp1"]
    print(f"\nExp 1 Zero-shot:  BLEU={e1['bleu']:6.2f}  chrF++={e1['chrf++']:6.2f}")

    print(f"\nExp 2 Weakness probes:")
    for name, res in results["exp2"]["probes"].items():
        print(f"  {name:25s}  chrF++={res['chrf++']:6.2f}  (n={res['n']})")

    e3 = results["exp3"]
    print(f"\nExp 3 Context:")
    print(f"  Isolated:  chrF++={e3['scores_isolated']:6.2f}")
    print(f"  Context:   chrF++={e3['scores_context']:6.2f}")
    print(f"  Delta:     {e3['delta']:+.2f}, Win rate: {e3['win_rate']}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = RESULTS_DIR / f"km2vi_results_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved to: {outpath}")


if __name__ == "__main__":
    main()
