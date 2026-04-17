"""
Mine cultural entities from our 1,856 parallel samples.
Uses GPT-4o to extract Vi-Km entity pairs from data grouped by topic.
Focuses on topics with richest cultural content.
"""
import json, os, sys, time, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import httpx
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(Path(__file__).parent / ".env")
RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)


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


def call_gpt4o(client, system_prompt, user_prompt):
    deployment = os.getenv("AZURE_CHAT_DEPLOYMENT")
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0, max_tokens=4096,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [Retry {attempt+1}] {e}")
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


SYSTEM_EXTRACT = """You are a bilingual Vietnamese-Khmer linguistics expert specializing in Khmer Krom culture.

Given parallel Vietnamese-Khmer text samples from a specific cultural topic, extract ALL culture-specific terms/entities as Vi-Km pairs.

Focus on:
- Food/dish names
- Ritual/ceremony names
- Religious terms
- Kinship/social terms
- Traditional objects/tools
- Place-specific terms
- Proverbs or fixed expressions
- Flora/fauna with cultural significance
- Traditional practices
- Musical/artistic terms

Return ONLY valid JSON array. Each entry must have:
{
  "vi": "Vietnamese term",
  "km": "Khmer term (in Khmer script)",
  "km_romanized": "romanization",
  "category": "food|religious|kinship|practice|object|nature|proverb|ceremony|other",
  "context": "brief explanation in English"
}

IMPORTANT:
- Extract from BOTH the Vietnamese text AND the Khmer reference
- Only include terms that are culturally specific (not generic words)
- The Khmer must be from the reference translation, NOT your own translation
- If a term appears multiple times, include it only once"""


PRIORITY_TOPICS = [
    "PHONG TỤC TRƯỚC ĐÁM CƯỚI",
    "PHONG TỤC KHI KẾT HÔN",
    "PHONG TỤC SAU KHI ĐÁM CƯỚI",
    "ĐỒ ĂN Ở ĐÁM CƯỚI",
    "TRANG PHỤC CƯỚI HỎI NAM",
    "TRANG PHỤC CƯỚI HỎI NỮ",
    "QUÀ CƯỚI",
    "KHÁCH MỜI ĐÁM CƯỚI",
    "VỊ TRÍ TỔ CHỨC ĐÁM CƯỚI",
    "When death occurs",
    "Process of dealing with corpse",
    "The clothes of the mourners",
    "Traditions after the body is buried",
    "Traditions during pregnancy",
    "Traditions after birth",
    "Traditional medicine",
    "Mystical things",
    "Traditional dances",
    "Folk songs",
    "Musical instruments",
    "Truyền thống chăm sóc vật nuôi/thủy sản",
    "Traditions during religious holidays",
    "Traditions leading up to religious holidays",
    "Traditional sayings",
]


def build_topic_prompt(samples, topic, max_samples=10):
    """Build a prompt showing parallel samples for entity extraction."""
    lines = [f"Topic: {topic}\n"]
    for i, s in enumerate(samples[:max_samples]):
        ref = get_clean_reference(s.get("label", []))
        if not ref:
            continue
        lines.append(f"--- Sample {i+1} ---")
        lines.append(f"VI: {s['text']}")
        lines.append(f"KM: {ref}\n")
    return "\n".join(lines)


def main():
    print("Loading data...")
    data = load_data()

    topic_groups = defaultdict(list)
    for d in data:
        t = d.get("topic")
        if t:
            topic_groups[t].append(d)

    topics_to_mine = [t for t in PRIORITY_TOPICS if t in topic_groups]
    print(f"Found {len(topics_to_mine)} priority topics to mine")

    client = get_client()
    all_extracted = {}
    all_entities = []

    for ti, topic in enumerate(topics_to_mine):
        samples = topic_groups[topic]
        print(f"\n[{ti+1}/{len(topics_to_mine)}] {topic} ({len(samples)} samples)")

        prompt = build_topic_prompt(samples, topic, max_samples=12)
        raw = call_gpt4o(client, SYSTEM_EXTRACT, prompt)

        try:
            cleaned = raw
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            entities = json.loads(cleaned)
        except Exception as e:
            print(f"  Parse error: {e}")
            print(f"  Raw (first 200): {raw[:200]}")
            entities = []

        for ent in entities:
            ent["source_topic"] = topic
            ent["source"] = "DATA_MINING"

        all_extracted[topic] = entities
        all_entities.extend(entities)
        print(f"  Extracted {len(entities)} entities")

        for ent in entities[:5]:
            print(f"    {ent.get('vi','?'):30s} → {ent.get('km','?')[:30]}")
        if len(entities) > 5:
            print(f"    ... and {len(entities)-5} more")

    # Deduplicate
    seen = set()
    unique = []
    for e in all_entities:
        key = e.get("vi", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(e)

    print(f"\n{'='*60}")
    print(f"MINING COMPLETE")
    print(f"{'='*60}")
    print(f"Topics mined:    {len(topics_to_mine)}")
    print(f"Total extracted: {len(all_entities)}")
    print(f"After dedup:     {len(unique)}")

    cat_dist = defaultdict(int)
    for e in unique:
        cat_dist[e.get("category", "other")] += 1
    print(f"\nBy category:")
    for c, n in sorted(cat_dist.items(), key=lambda x: -x[1]):
        print(f"  {c:15s} {n}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = RESULTS_DIR / f"mined_entities_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "timestamp": timestamp,
                "topics_mined": len(topics_to_mine),
                "total_raw": len(all_entities),
                "total_unique": len(unique),
                "source": "Extracted from all_1.jsonl + all_2.jsonl by GPT-4o",
            },
            "by_topic": all_extracted,
            "unique_entities": unique,
        }, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {outpath}")


if __name__ == "__main__":
    main()
