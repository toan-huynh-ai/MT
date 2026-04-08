"""
Cultural Knowledge Base (CKB) for Vietnamese-Khmer Translation
================================================================
Extracts cultural entities from the parallel data and builds a structured
KB that can be used for:
  1. RAG-augmented translation (provide correct terms in prompt)
  2. Cultural entity evaluation (check if MT output uses correct terms)
  3. Dialect mapping (standard Khmer vs Khmer Krom)
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


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


def extract_alignment_pairs(data):
    """Extract word/phrase alignment pairs from *** annotations."""
    pairs = []
    for d in data:
        for lbl in d.get("label", []):
            matches = re.findall(r'([^\n*]+?)\s*\*\*\*\s*([^\n*]+)', lbl)
            for vi, km in matches:
                vi = vi.strip().rstrip(".")
                km = km.strip().rstrip(".")
                if vi and km and len(vi) < 100 and len(km) < 200:
                    pairs.append({
                        "vietnamese": vi,
                        "khmer": km,
                        "source_id": d.get("id"),
                        "topic": d.get("topic"),
                    })
    return pairs


# Manually curated cultural entities from data analysis + weakness probing
CULTURAL_KB = {
    "food": [
        {"vi": "cốm dẹp", "km": "អំបុក", "km_romanized": "ambok", "category": "traditional_food",
         "context": "Flattened rice, used in Ok Om Bok festival"},
        {"vi": "bánh gừng", "km": "នំខ្ញី", "km_romanized": "nom khgnei", "category": "traditional_food",
         "context": "Ginger-shaped cake for wedding ceremonies"},
        {"vi": "bánh tét", "km": "នំអន្សម", "km_romanized": "nom ansom", "category": "traditional_food",
         "context": "Cylindrical sticky rice cake"},
        {"vi": "bánh ít", "km": "នំគម", "km_romanized": "nom kom", "category": "traditional_food",
         "context": "Pyramid-shaped sticky rice cake"},
        {"vi": "bánh ống tre", "km": "នំបំពង់ឫស្សី", "km_romanized": "nom bampong ruessei",
         "category": "traditional_food", "context": "Bamboo tube cake"},
        {"vi": "bún nước lèo", "km": "នំបញ្ចុកទឹកសម្ល", "km_romanized": "nom banchok tuk samlor",
         "category": "traditional_food", "context": "Khmer rice noodle soup"},
        {"vi": "Num banh chok", "km": "នំបញ្ចុក", "km_romanized": "nom banchok",
         "category": "traditional_food", "context": "Khmer rice noodles"},
        {"vi": "mắm bò hóc", "km": "ម៉ាំប្រហុក", "km_romanized": "mam prahok",
         "category": "traditional_food", "context": "Fermented fish paste"},
        {"vi": "Pro-hốc", "km": "ប្រហុក", "km_romanized": "prahok",
         "category": "traditional_food", "context": "Fermented fish paste (alternate name)"},
        {"vi": "canh Som-lo Co Cô", "km": "សម្លកកូរ", "km_romanized": "samlor kakou",
         "category": "traditional_food", "context": "Traditional sour soup"},
        {"vi": "Amok Trey", "km": "អាម៉ុកត្រី", "km_romanized": "amok trey",
         "category": "traditional_food", "context": "Steamed fish curry in banana leaf"},
        {"vi": "nùm bong klanh", "km": "នំបង់ខ្លាញ់", "km_romanized": "nom bong klanh",
         "category": "traditional_food", "context": "Traditional Khmer Krom cake"},
        {"vi": "đường thốt nốt", "km": "ស្ករត្នោត", "km_romanized": "skor tnaot",
         "category": "ingredient", "context": "Palm sugar from toddy palm"},
        {"vi": "lạp", "km": "ឡាប", "km_romanized": "lab",
         "category": "traditional_food", "context": "Minced meat salad for ceremonies"},
        {"vi": "cà ri Khmer", "km": "សម្លការី", "km_romanized": "samlor kari",
         "category": "traditional_food", "context": "Khmer-style curry"},
    ],
    "festivals": [
        {"vi": "Chol Chnam Thmay", "km": "ចូលឆ្នាំថ្មី", "km_romanized": "chol chnam thmei",
         "context": "Khmer New Year (April)"},
        {"vi": "Ok Om Bok", "km": "អកអំបុក", "km_romanized": "ok ambok",
         "context": "Moon Worship Festival"},
        {"vi": "Sene Dolta", "km": "សែនដូនតា", "km_romanized": "saen don ta",
         "context": "Ancestor Worship Festival"},
        {"vi": "Kathina", "km": "កឋិនទាន", "km_romanized": "kathin tean",
         "context": "Robe-offering ceremony"},
    ],
    "religious": [
        {"vi": "Sư", "km": "ព្រះសង្ឃ", "km_romanized": "preah sangkh",
         "context": "Buddhist monk (Theravada)"},
        {"vi": "Achar", "km": "អាចារ្យ", "km_romanized": "achar",
         "context": "Lay religious leader"},
        {"vi": "chùa", "km": "វត្ត", "km_romanized": "wat",
         "context": "Buddhist temple/pagoda"},
        {"vi": "tụng kinh", "km": "សូត្រមន្ត", "km_romanized": "sot mon",
         "context": "Chanting Buddhist scriptures"},
        {"vi": "cúng dường", "km": "ថ្វាយ", "km_romanized": "thvay",
         "context": "Making offerings to monks"},
        {"vi": "xuất gia", "km": "បួស", "km_romanized": "buos",
         "context": "To ordain as a monk"},
        {"vi": "thọ giới", "km": "សមាទានសីល", "km_romanized": "samathean sel",
         "context": "To take precepts"},
        {"vi": "Phật Thích Ca", "km": "ព្រះសម្មាសម្ពុទ្ធ", "km_romanized": "preah somma somput",
         "context": "Shakyamuni Buddha"},
        {"vi": "tắm Phật", "km": "ស្រង់ព្រះ", "km_romanized": "srang preah",
         "context": "Ritual of bathing the Buddha statue"},
        {"vi": "đắp núi cát", "km": "ពូនភ្នំខ្សាច់", "km_romanized": "pun phnom khsach",
         "context": "Building sand mountains (merit-making ritual)"},
        {"vi": "cầu siêu", "km": "បង្សុកូល", "km_romanized": "bangsoukol",
         "context": "Funeral prayer ceremony"},
        {"vi": "bùa hộ mệnh", "km": "ខ្សែបន្តោង", "km_romanized": "khsae bontong",
         "context": "Protective amulet/talisman"},
        {"vi": "Neak Ta", "km": "អ្នកតា", "km_romanized": "neak ta",
         "context": "Village guardian spirit"},
        {"vi": "Bà La Môn", "km": "ព្រាហ្មណ៍", "km_romanized": "preamh",
         "context": "Brahmanism/Hindu religion"},
    ],
    "kinship": [
        {"vi": "ông ngoại", "km": "តា (ខាងម្ដាយ)", "km_romanized": "ta (khang mdaay)",
         "context": "Maternal grandfather"},
        {"vi": "bà ngoại", "km": "យាយ (ខាងម្ដាយ)", "km_romanized": "yeay (khang mdaay)",
         "context": "Maternal grandmother"},
        {"vi": "bác (anh/chị của cha)", "km": "ធំ", "km_romanized": "thom",
         "context": "Elder sibling of father"},
        {"vi": "cô (em gái của cha)", "km": "មីង", "km_romanized": "ming",
         "context": "Younger sister of father"},
        {"vi": "chú (em trai của cha)", "km": "ពូ", "km_romanized": "pu",
         "context": "Younger brother of father"},
        {"vi": "dì (chị/em gái của mẹ)", "km": "មីង", "km_romanized": "ming",
         "context": "Sister of mother"},
        {"vi": "dượng", "km": "ពូថ្លៃ", "km_romanized": "pu thlay",
         "context": "Husband of aunt"},
        {"vi": "con dâu", "km": "កូនប្រសា", "km_romanized": "kon prosa",
         "context": "Daughter-in-law"},
        {"vi": "con rể", "km": "កូនប្រសា", "km_romanized": "kon prosa",
         "context": "Son-in-law"},
        {"vi": "thông gia", "km": "សំណាន់ជើង", "km_romanized": "somnoan cheung",
         "context": "In-law relationship between families"},
    ],
    "cultural_practices": [
        {"vi": "phum sóc", "km": "ភូមិសង្គម", "km_romanized": "phum sangkum",
         "context": "Khmer village/community (Krom-specific term)"},
        {"vi": "rong vong", "km": "រាំវង់", "km_romanized": "roam vong",
         "context": "Traditional circle dance"},
        {"vi": "múa Ramvang", "km": "រាំវង់", "km_romanized": "roam vong",
         "context": "Traditional circle dance (alternate spelling)"},
        {"vi": "nằm than", "km": "ដេកចង្ក្រានធ្យូង", "km_romanized": "dek changkran thyung",
         "context": "Postpartum practice of lying on charcoal bed"},
        {"vi": "Dù Kê", "km": "យីកេ/ល្ខោនបាសាក់", "km_romanized": "yikee/lkhaon basak",
         "context": "Traditional Khmer theater form"},
        {"vi": "Ngũ Âm", "km": "ពិណពាទ្យ", "km_romanized": "pin peat",
         "context": "Traditional five-instrument ensemble"},
        {"vi": "trống Sadăm", "km": "ស្គរសាដំ", "km_romanized": "skor sadam",
         "context": "Traditional drum used in temples"},
        {"vi": "mẫu hệ", "km": "មាតាធិបតេយ្យ", "km_romanized": "meatea thippatey",
         "context": "Matrilineal system in Khmer culture"},
    ],
    "agriculture": [
        {"vi": "lúa mùa nổi", "km": "ស្រូវវស្សាអណ្ដែត", "km_romanized": "srov vossa andaet",
         "context": "Floating rice variety adapted to floods"},
        {"vi": "cây thốt nốt", "km": "ដើមត្នោត", "km_romanized": "daem tnaot",
         "context": "Toddy/sugar palm tree, symbol of Khmer culture"},
    ],
}


def build_kb():
    """Build the full KB and print statistics."""
    total_entries = sum(len(v) for v in CULTURAL_KB.values())
    print(f"Cultural Knowledge Base Statistics:")
    print(f"  Total entries: {total_entries}")
    for cat, entries in CULTURAL_KB.items():
        print(f"  {cat}: {len(entries)} entries")

    data = load_data()
    alignment_pairs = extract_alignment_pairs(data)
    print(f"\n  Auto-extracted alignment pairs from ***: {len(alignment_pairs)}")
    for p in alignment_pairs[:10]:
        print(f"    {p['vietnamese'][:40]:40s} → {p['khmer'][:50]}")

    return CULTURAL_KB, alignment_pairs


def lookup(text, kb=None):
    """Find all cultural entities in Vietnamese text."""
    if kb is None:
        kb = CULTURAL_KB
    found = []
    text_lower = text.lower()
    for category, entries in kb.items():
        for entry in entries:
            vi_term = entry["vi"].lower()
            if vi_term in text_lower:
                found.append({**entry, "category": category})
    return found


def build_rag_context(text, kb=None, max_entries=5):
    """Build a RAG context string for translation augmentation."""
    entities = lookup(text, kb)
    if not entities:
        return ""

    lines = ["Cultural terminology reference:"]
    seen = set()
    for ent in entities[:max_entries]:
        key = ent["vi"]
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"  \"{ent['vi']}\" → \"{ent['km']}\" ({ent.get('context', '')})")

    return "\n".join(lines)


if __name__ == "__main__":
    kb, pairs = build_kb()

    print("\n" + "=" * 70)
    print("SAMPLE KB LOOKUPS")
    print("=" * 70)

    test_sentences = [
        "Người dân không làm cốm dẹp vào ngày thường vì món này tốn nhiều thời gian.",
        "Tôi nhớ lần đầu tiên tôi nhận được món bánh ống tre trong dịp lễ dâng y Kathina.",
        "Num Ansam (còn gọi là bánh Tét) và Kom (còn gọi là bánh ít) là hai loại bánh.",
        "Con cháu thường lên chùa tụng kinh, cúng dường và làm phước.",
        "Người Khmer rất coi trọng tình quê, người cùng quê dù không ruột thịt.",
        "Chúng tôi thường thờ cúng Neak Ta, tin rằng vị thần bảo hộ làng.",
    ]

    for sent in test_sentences:
        ents = lookup(sent)
        rag = build_rag_context(sent)
        print(f"\nInput: {sent[:80]}...")
        print(f"Found {len(ents)} entities:")
        for e in ents:
            print(f"  [{e['category']}] {e['vi']} → {e['km']}")
        if rag:
            print(f"RAG context:\n{rag}")

    out_path = Path(__file__).parent / "cultural_knowledge_base.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(CULTURAL_KB, f, ensure_ascii=False, indent=2)
    print(f"\nKB saved to: {out_path}")
