"""
Pilot Experiment: Cultural MT Benchmark for Vietnamese-Khmer
=============================================================
Tests 3 experimental conditions using GPT-4o via Azure OpenAI:
  1. Zero-shot baseline (Vi→Km)
  2. Few-shot: random vs topic-matched examples
  3. Dialogue context: isolated vs with-context

Evaluation: BLEU, chrF++ via sacrebleu + cultural entity extraction
"""

import json
import os
import re
import random
import time
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import ssl
import httpx
import sacrebleu
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

load_dotenv(Path(__file__).parent / ".env")

# Corporate proxy workaround: trust system certs or skip verification
os.environ.setdefault("AZURE_IDENTITY_DISABLE_CP1", "true")
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)


# ── Azure OpenAI Client ─────────────────────────────────────────────

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


def call_gpt4o(client: AzureOpenAI, system_prompt: str, user_prompt: str,
               max_retries: int = 3) -> str:
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
            print(f"  [Attempt {attempt+1}/{max_retries}] Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return ""


# ── Data Loading ─────────────────────────────────────────────────────

def load_data() -> list[dict]:
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


def get_clean_reference(labels: list[str]) -> str:
    """Extract the cleanest reference translation (no *** annotations)."""
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


def split_data(data: list[dict]) -> dict:
    """Split into QA-type and Dialogue-type."""
    qa = [d for d in data if d.get("topic") is None and d.get("question") is not None]
    dialogue = [d for d in data if d.get("topic") is not None]
    return {"qa": qa, "dialogue": dialogue}


def group_conversations(dialogue_data: list[dict]) -> dict[int, list[dict]]:
    """Group dialogue turns by conversation ID, sorted by order."""
    convs = defaultdict(list)
    for d in dialogue_data:
        convs[d["id"]].append(d)
    for cid in convs:
        convs[cid].sort(key=lambda x: x.get("order", 0) or 0)
    return dict(convs)


# ── Prompt Templates ─────────────────────────────────────────────────

SYSTEM_ZERO_SHOT = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "Translate the following Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_FEW_SHOT = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "Below are example translations for reference. "
    "Translate the given Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_CONTEXT = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "You are translating a conversation between an interviewer and a Khmer person. "
    "Previous turns of the conversation are provided for context. "
    "Translate ONLY the last Vietnamese utterance into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)


def build_few_shot_prompt(examples: list[dict], source_text: str) -> str:
    parts = ["Here are example Vietnamese → Khmer translations:\n"]
    for i, ex in enumerate(examples, 1):
        ref = get_clean_reference(ex.get("label", []))
        parts.append(f"Example {i}:")
        parts.append(f"Vietnamese: {ex['text']}")
        parts.append(f"Khmer: {ref}\n")
    parts.append(f"Now translate this:\nVietnamese: {source_text}")
    return "\n".join(parts)


def build_context_prompt(conversation: list[dict], target_idx: int) -> str:
    parts = ["Previous conversation turns:\n"]
    for i in range(target_idx):
        turn = conversation[i]
        ref = get_clean_reference(turn.get("label", []))
        parts.append(f"Vietnamese: {turn['text']}")
        parts.append(f"Khmer: {ref}\n")
    parts.append(f"Now translate the next turn:\nVietnamese: {conversation[target_idx]['text']}")
    return "\n".join(parts)


# ── Evaluation ───────────────────────────────────────────────────────

def evaluate_translations(hypotheses: list[str], references: list[str]) -> dict:
    """Compute BLEU and chrF++ scores."""
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references], word_order=2)
    return {
        "bleu": round(bleu.score, 2),
        "chrf++": round(chrf.score, 2),
        "n_samples": len(hypotheses),
    }


CULTURAL_ENTITIES_VI = [
    "Mắm bò hóc", "Pro-hốc", "Prahok", "bún nước lèo", "Num banh chok",
    "canh Som-lo", "cốm dẹp", "bánh gừng", "bánh tét", "bánh ít",
    "Chol Chnam Thmay", "Ok Om Bok", "Kathina", "Sene Dolta",
    "thốt nốt", "rong vong", "Achar", "pagoda", "chùa",
    "mắm", "nước lèo", "bánh ống", "lúa mùa nổi",
]


def detect_cultural_entities(text: str) -> list[str]:
    found = []
    text_lower = text.lower()
    for ent in CULTURAL_ENTITIES_VI:
        if ent.lower() in text_lower:
            found.append(ent)
    return found


def cultural_entity_analysis(samples: list[dict], hypotheses: list[str],
                             references: list[str]) -> dict:
    """Analyze how well cultural entities are preserved in translation."""
    with_entities = 0
    without_entities = 0
    hyps_with = []
    refs_with = []
    hyps_without = []
    refs_without = []

    for i, sample in enumerate(samples):
        entities = detect_cultural_entities(sample["text"])
        if entities:
            with_entities += 1
            hyps_with.append(hypotheses[i])
            refs_with.append(references[i])
        else:
            without_entities += 1
            hyps_without.append(hypotheses[i])
            refs_without.append(references[i])

    result = {
        "n_with_cultural_entities": with_entities,
        "n_without_cultural_entities": without_entities,
    }
    if hyps_with:
        result["scores_with_entities"] = evaluate_translations(hyps_with, refs_with)
    if hyps_without:
        result["scores_without_entities"] = evaluate_translations(hyps_without, refs_without)
    return result


# ── Experiment Runners ───────────────────────────────────────────────

def run_experiment_1_zero_shot(client, data, n_samples=30):
    """Exp 1: Zero-shot Vi→Km translation."""
    print("\n" + "="*60)
    print("EXPERIMENT 1: Zero-Shot Baseline (Vi→Km)")
    print("="*60)

    random.seed(42)
    samples = random.sample(data, min(n_samples, len(data)))

    hypotheses = []
    references = []
    results_detail = []

    for i, sample in enumerate(samples):
        ref = get_clean_reference(sample.get("label", []))
        if not ref:
            continue

        print(f"  [{i+1}/{len(samples)}] Translating: {sample['text'][:60]}...")
        hyp = call_gpt4o(client, SYSTEM_ZERO_SHOT,
                         f"Vietnamese: {sample['text']}")

        hypotheses.append(hyp)
        references.append(ref)
        results_detail.append({
            "id": sample["id"],
            "source": sample["text"],
            "reference": ref,
            "hypothesis": hyp,
            "cultural_entities": detect_cultural_entities(sample["text"]),
        })

    scores = evaluate_translations(hypotheses, references)
    cultural = cultural_entity_analysis(samples[:len(hypotheses)], hypotheses, references)

    print(f"\n  Results: BLEU={scores['bleu']}, chrF++={scores['chrf++']}")
    print(f"  Cultural entity samples: {cultural['n_with_cultural_entities']}")

    return {
        "experiment": "zero_shot_vi_km",
        "scores": scores,
        "cultural_analysis": cultural,
        "details": results_detail,
    }


def run_experiment_2_few_shot(client, data, n_samples=20, k_shot=3):
    """Exp 2: Few-shot comparison — random vs topic-matched."""
    print("\n" + "="*60)
    print("EXPERIMENT 2: Few-Shot (Random vs Topic-Matched)")
    print("="*60)

    random.seed(42)

    qa_data = [d for d in data if d.get("question") is not None and d.get("topic") is None]
    dialogue_data = [d for d in data if d.get("topic") is not None]

    topic_groups = defaultdict(list)
    for d in dialogue_data:
        topic_groups[d["topic"]].append(d)
    eligible_topics = [t for t, items in topic_groups.items() if len(items) > k_shot + 1]

    test_samples = []
    for topic in random.sample(eligible_topics, min(n_samples, len(eligible_topics))):
        items = topic_groups[topic]
        test_samples.append(random.choice(items))

    random_hyps, matched_hyps, refs = [], [], []
    details = []

    for i, sample in enumerate(test_samples):
        ref = get_clean_reference(sample.get("label", []))
        if not ref:
            continue

        topic = sample["topic"]
        topic_pool = [d for d in topic_groups[topic]
                      if d is not sample and get_clean_reference(d.get("label", []))]
        random_pool = [d for d in data
                       if d is not sample and get_clean_reference(d.get("label", []))]

        random_examples = random.sample(random_pool, min(k_shot, len(random_pool)))
        matched_examples = random.sample(topic_pool, min(k_shot, len(topic_pool)))

        print(f"  [{i+1}/{len(test_samples)}] Topic: {topic[:40]}...")

        prompt_random = build_few_shot_prompt(random_examples, sample["text"])
        hyp_random = call_gpt4o(client, SYSTEM_FEW_SHOT, prompt_random)

        prompt_matched = build_few_shot_prompt(matched_examples, sample["text"])
        hyp_matched = call_gpt4o(client, SYSTEM_FEW_SHOT, prompt_matched)

        random_hyps.append(hyp_random)
        matched_hyps.append(hyp_matched)
        refs.append(ref)
        details.append({
            "id": sample["id"],
            "topic": topic,
            "source": sample["text"],
            "reference": ref,
            "hyp_random_shot": hyp_random,
            "hyp_topic_matched": hyp_matched,
        })

    scores_random = evaluate_translations(random_hyps, refs)
    scores_matched = evaluate_translations(matched_hyps, refs)

    print(f"\n  Random few-shot:  BLEU={scores_random['bleu']}, chrF++={scores_random['chrf++']}")
    print(f"  Matched few-shot: BLEU={scores_matched['bleu']}, chrF++={scores_matched['chrf++']}")

    return {
        "experiment": "few_shot_comparison",
        "scores_random": scores_random,
        "scores_topic_matched": scores_matched,
        "k_shot": k_shot,
        "details": details,
    }


def run_experiment_3_context(client, data, n_convs=10):
    """Exp 3: Dialogue context — isolated turn vs with-context."""
    print("\n" + "="*60)
    print("EXPERIMENT 3: Dialogue Context Effects")
    print("="*60)

    dialogue_data = [d for d in data if d.get("topic") is not None]
    conversations = group_conversations(dialogue_data)

    long_convs = {cid: turns for cid, turns in conversations.items() if len(turns) >= 4}

    random.seed(42)
    selected_cids = random.sample(list(long_convs.keys()), min(n_convs, len(long_convs)))

    isolated_hyps, context_hyps, refs = [], [], []
    details = []

    for ci, cid in enumerate(selected_cids):
        turns = long_convs[cid]
        target_idx = len(turns) - 1
        target = turns[target_idx]
        ref = get_clean_reference(target.get("label", []))
        if not ref:
            target_idx = len(turns) - 2
            target = turns[target_idx]
            ref = get_clean_reference(target.get("label", []))
        if not ref:
            continue

        topic = target.get("topic", "unknown")
        print(f"  [{ci+1}/{len(selected_cids)}] Conv {cid}, topic: {topic[:40]}...")

        hyp_isolated = call_gpt4o(
            client, SYSTEM_ZERO_SHOT,
            f"Vietnamese: {target['text']}"
        )

        prompt_ctx = build_context_prompt(turns, target_idx)
        hyp_context = call_gpt4o(client, SYSTEM_CONTEXT, prompt_ctx)

        isolated_hyps.append(hyp_isolated)
        context_hyps.append(hyp_context)
        refs.append(ref)
        details.append({
            "id": cid,
            "topic": topic,
            "n_context_turns": target_idx,
            "source": target["text"],
            "reference": ref,
            "hyp_isolated": hyp_isolated,
            "hyp_with_context": hyp_context,
        })

    scores_isolated = evaluate_translations(isolated_hyps, refs)
    scores_context = evaluate_translations(context_hyps, refs)

    print(f"\n  Isolated:     BLEU={scores_isolated['bleu']}, chrF++={scores_isolated['chrf++']}")
    print(f"  With context: BLEU={scores_context['bleu']}, chrF++={scores_context['chrf++']}")

    return {
        "experiment": "dialogue_context",
        "scores_isolated": scores_isolated,
        "scores_with_context": scores_context,
        "details": details,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} samples")

    print("Connecting to Azure OpenAI (GPT-4o)...")
    client = get_client()

    print("Running quick connectivity test...")
    test = call_gpt4o(client, "You are a translator.", "Translate to Khmer: Xin chào")
    if not test:
        print("ERROR: Cannot connect to GPT-4o. Check .env credentials.")
        sys.exit(1)
    print(f"  Connectivity OK. Test response: {test[:80]}")

    all_results = {}

    all_results["exp1"] = run_experiment_1_zero_shot(client, data, n_samples=30)
    all_results["exp2"] = run_experiment_2_few_shot(client, data, n_samples=15, k_shot=3)
    all_results["exp3"] = run_experiment_3_context(client, data, n_convs=10)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = RESULTS_DIR / f"pilot_results_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"ALL RESULTS SAVED TO: {outpath}")
    print(f"{'='*60}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    e1 = all_results["exp1"]["scores"]
    print(f"\nExp 1 — Zero-shot:       BLEU={e1['bleu']:6.2f}  chrF++={e1['chrf++']:6.2f}")

    e2r = all_results["exp2"]["scores_random"]
    e2m = all_results["exp2"]["scores_topic_matched"]
    print(f"Exp 2 — Random few-shot: BLEU={e2r['bleu']:6.2f}  chrF++={e2r['chrf++']:6.2f}")
    print(f"Exp 2 — Matched few-shot:BLEU={e2m['bleu']:6.2f}  chrF++={e2m['chrf++']:6.2f}")

    e3i = all_results["exp3"]["scores_isolated"]
    e3c = all_results["exp3"]["scores_with_context"]
    print(f"Exp 3 — Isolated turn:   BLEU={e3i['bleu']:6.2f}  chrF++={e3i['chrf++']:6.2f}")
    print(f"Exp 3 — With context:    BLEU={e3c['bleu']:6.2f}  chrF++={e3c['chrf++']:6.2f}")

    ca = all_results["exp1"].get("cultural_analysis", {})
    if "scores_with_entities" in ca:
        cw = ca["scores_with_entities"]
        cwo = ca.get("scores_without_entities", {})
        print(f"\nCultural Entity Analysis (Exp 1):")
        print(f"  With entities ({ca['n_with_cultural_entities']} samples):    "
              f"BLEU={cw.get('bleu','N/A')}, chrF++={cw.get('chrf++','N/A')}")
        if cwo:
            print(f"  Without entities ({ca['n_without_cultural_entities']} samples): "
                  f"BLEU={cwo.get('bleu','N/A')}, chrF++={cwo.get('chrf++','N/A')}")


if __name__ == "__main__":
    main()
