"""
Test: Does Cultural KB RAG fix GPT-4o's weaknesses?
Compares zero-shot vs KB-augmented translation on the known weak samples.
"""
import json, os, sys, time
from pathlib import Path
import httpx, sacrebleu
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI
from cultural_kb import CULTURAL_KB, lookup, build_rag_context

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(Path(__file__).parent / ".env")


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
                temperature=0.0, max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [Retry {attempt+1}] {e}")
            time.sleep(5 * (attempt + 1))
    return ""


SYSTEM_PLAIN = (
    "You are an expert translator specializing in Vietnamese-Khmer translation. "
    "Translate the following Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

SYSTEM_KB = (
    "You are an expert translator specializing in Vietnamese-Khmer translation, "
    "particularly for the Khmer Krom community in Vietnam's Mekong Delta. "
    "You will be given cultural terminology references to use. "
    "ALWAYS use the provided Khmer terms for cultural entities. "
    "Translate the Vietnamese text into Khmer. "
    "Output ONLY the Khmer translation, nothing else."
)

# The exact samples where GPT-4o failed
TEST_CASES = [
    {
        "source": "Người dân không làm cốm dẹp vào ngày thường vì món này tốn nhiều thời gian và công sức để chế biến.",
        "reference": "ប្រជាជនខ្មែរមិនធ្វើ អំបុក នៅថ្ងៃធម្មតា ព្រោះនំនេះត្រូវចំណាយពេល និងកម្លាំងច្រើនក្នុងការរៀបចំ។",
        "weakness": "cốm dẹp → transliterated, not អំបុក",
    },
    {
        "source": "Tôi nhớ lần đầu tiên tôi nhận được món bánh ống tre trong dịp lễ dâng y Kathina nhà bạn tôi.",
        "reference": "ខ្ញុំចាំបានថាជាលើកដំបូងដែលខ្ញុំបានទទួលនំបំពង់ឫស្សី ក្នុងថ្ងៃចូលរួមបុណ្យកឋិនទានផ្ទះរបស់មិត្តខ្ញុំ។",
        "weakness": "bánh ống tre → wrong word, Kathina left romanized",
    },
    {
        "source": "Bánh tét cũng là món cổ truyền của dân tộc Khmer, khi tết đến Chôl Chnăm Thmây, Sene Đônta đều được gói và biếu cho mọi người.",
        "reference": "នំអន្សោមក៏ជាម្ហូបប្រពៃណីរបស់ជនជាតិខ្មែរដែរ។ ពេលចូលឆ្នាំថ្មីមកដល់ សេន ដូនតា ត្រូវបានវេចនិងជូនឲ្យអ្នករាល់គ្នា។",
        "weakness": "bánh tét → wrong phonetic, festival names",
    },
    {
        "source": "Con cháu thường lên chùa tụng kinh, cúng dường và làm phước để cầu an cho gia đình.",
        "reference": "កូនចៅតែងតែទៅវត្តសូត្រមន្ត ថ្វាយ និងធ្វើបុណ្យដើម្បីសូមសុខសន្តិភាពសម្រាប់គ្រួសារ។",
        "weakness": "Religious terms: chùa, tụng kinh, cúng dường",
    },
    {
        "source": "Chúng tôi thường thờ cúng Neak Ta, tin rằng vị thần bảo hộ làng sẽ mang lại may mắn cho cả phum sóc.",
        "reference": "យើងតែងតែគោរពអ្នកតា ព្រោះជឿថាវាជាដែនរក្សា ដែលនាំមកនូវសំណាងល្អទំាងភូមិ។",
        "weakness": "Neak Ta, phum sóc - Khmer Krom specific",
    },
    {
        "source": "Num Ansam (còn gọi là bánh Tét) và Kom (còn gọi là bánh ít) là hai loại bánh tượng trưng cho Dôni và linga của thần ISo trong tôn giáo Bà La Môn.",
        "reference": "នំអន្សម និង នំគម ជាប្រភេទនំ២តំណាងឲ្យយោនី នាងឧមា និងលិង្គព្រះឥសូ ក្នុងសាសនាព្រាហ្មណ៍ គឺជាម្ហូបមួយមុខដែលខ្ញុំចាំថា បានញ៉ាំក្នុងពិធីមង្គលការក្នុងភូមិ។",
        "weakness": "Untranslated romanized food + religious terms",
    },
]


def main():
    client = get_client()

    print("=" * 80)
    print("KB-RAG ABLATION: Zero-shot vs KB-augmented translation")
    print("=" * 80)

    plain_hyps, kb_hyps, refs = [], [], []
    results = []

    for i, tc in enumerate(TEST_CASES):
        print(f"\n--- Test {i+1}: {tc['weakness'][:60]} ---")

        rag_context = build_rag_context(tc["source"])
        entities = lookup(tc["source"])

        hyp_plain = call_gpt4o(client, SYSTEM_PLAIN, f"Vietnamese: {tc['source']}")

        user_with_kb = f"{rag_context}\n\nTranslate this Vietnamese text into Khmer:\n{tc['source']}"
        hyp_kb = call_gpt4o(client, SYSTEM_KB, user_with_kb)

        plain_chrf = sacrebleu.sentence_chrf(hyp_plain, [tc["reference"]], word_order=2).score
        kb_chrf = sacrebleu.sentence_chrf(hyp_kb, [tc["reference"]], word_order=2).score
        delta = kb_chrf - plain_chrf

        plain_hyps.append(hyp_plain)
        kb_hyps.append(hyp_kb)
        refs.append(tc["reference"])

        marker = "▲" if delta > 0 else "▼" if delta < 0 else "="
        print(f"  Entities found: {[e['vi'] for e in entities]}")
        print(f"  Plain:   {hyp_plain[:100]}")
        print(f"  KB-RAG:  {hyp_kb[:100]}")
        print(f"  Ref:     {tc['reference'][:100]}")
        print(f"  chrF++:  plain={plain_chrf:.1f}  kb={kb_chrf:.1f}  {marker} {delta:+.1f}")

        # Check if correct KB terms appear in output
        for ent in entities:
            km_term = ent["km"]
            in_plain = km_term in hyp_plain
            in_kb = km_term in hyp_kb
            if not in_plain and in_kb:
                print(f"  ✓ KB FIXED: '{ent['vi']}' → '{km_term}' now correct!")
            elif not in_plain and not in_kb:
                print(f"  ✗ STILL WRONG: '{ent['vi']}' → '{km_term}' not found in either")
            elif in_plain and in_kb:
                print(f"  = ALREADY OK: '{ent['vi']}' → '{km_term}' correct in both")

        results.append({
            "source": tc["source"],
            "reference": tc["reference"],
            "weakness": tc["weakness"],
            "hyp_plain": hyp_plain,
            "hyp_kb": hyp_kb,
            "chrf_plain": plain_chrf,
            "chrf_kb": kb_chrf,
            "delta": delta,
            "entities": [e["vi"] for e in entities],
        })

    corpus_plain = sacrebleu.corpus_chrf(plain_hyps, [refs], word_order=2)
    corpus_kb = sacrebleu.corpus_chrf(kb_hyps, [refs], word_order=2)

    print("\n" + "=" * 80)
    print("CORPUS-LEVEL RESULTS")
    print("=" * 80)
    print(f"  Plain (zero-shot): chrF++ = {corpus_plain.score:.2f}")
    print(f"  KB-RAG:            chrF++ = {corpus_kb.score:.2f}")
    print(f"  Delta:             {corpus_kb.score - corpus_plain.score:+.2f}")

    wins = sum(1 for r in results if r["delta"] > 0)
    print(f"  Win rate:          {wins}/{len(results)}")

    out_path = Path(__file__).parent / "experiment_results" / "kb_rag_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved to: {out_path}")


if __name__ == "__main__":
    main()
