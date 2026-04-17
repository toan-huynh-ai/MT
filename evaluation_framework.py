"""
Cultural Translation Evaluation Framework (CulturalEval)
=========================================================
Four-tier evaluation for Vietnamese-Khmer cultural MT:
  Tier 1: Standard metrics (chrF++, BLEU)
  Tier 2: CuEA — Cultural Entity Accuracy
  Tier 3: Script Purity Score
  Tier 4: Linguistic taxonomy analysis (A/B/C error classification)
"""

import re
import sys
from collections import defaultdict
import sacrebleu
from cultural_kb_expanded import lookup, CULTURAL_KB, TOPONYMS, ROMANIZED_KHMER

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Unicode ranges
KHMER_SCRIPT = re.compile(r'[\u1780-\u17FF\u19E0-\u19FF]')
CHINESE_CHARS = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')
LATIN_ALPHA = re.compile(r'[A-Za-zÀ-ỹ]')
VIETNAMESE_SPECIFIC = re.compile(r'[ăâđêôơưĂÂĐÊÔƠƯạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]')


# ── Tier 1: Standard Metrics ────────────────────────────────────────

def compute_standard_metrics(hypotheses, references):
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references], word_order=2)
    return {
        "bleu": round(bleu.score, 2),
        "chrf++": round(chrf.score, 2),
        "n": len(hypotheses),
    }


def compute_sentence_metrics(hypothesis, reference):
    bleu = sacrebleu.sentence_bleu(hypothesis, [reference])
    chrf = sacrebleu.sentence_chrf(hypothesis, [reference], word_order=2)
    return {
        "bleu": round(bleu.score, 2),
        "chrf++": round(chrf.score, 2),
    }


# ── Tier 2: CuEA — Cultural Entity Accuracy ─────────────────────────

def compute_cuea(source_vi, hypothesis_km, reference_km=None):
    """
    Cultural Entity Accuracy (CuEA):
    Measures what fraction of cultural entities in the source are correctly
    rendered in the translation output.

    Returns:
        dict with cuea score (0-1), entity details, and error classification
    """
    entities = lookup(source_vi)
    if not entities:
        return {"cuea": None, "n_entities": 0, "details": [],
                "reason": "No cultural entities in source"}

    seen_keys = set()
    unique_entities = []
    for e in entities:
        key = e.get("vi", e.get("romanized", ""))
        if key not in seen_keys:
            seen_keys.add(key)
            unique_entities.append(e)

    correct = 0
    details = []
    for ent in unique_entities:
        km_term = ent.get("km", "")
        vi_term = ent.get("vi", ent.get("romanized", ""))

        in_hyp = km_term in hypothesis_km if km_term else False
        in_ref = km_term in reference_km if (km_term and reference_km) else None

        error_type = None
        if not in_hyp:
            if vi_term.lower() in hypothesis_km.lower():
                error_type = "UNTRANSLATED"
            elif any(c in hypothesis_km for c in vi_term if ord(c) > 127 and not KHMER_SCRIPT.match(c)):
                error_type = "FOREIGN_LEAK"
            else:
                romanized = ent.get("km_romanized", "")
                if romanized and romanized.lower() in hypothesis_km.lower():
                    error_type = "ROMANIZED_LEFT"
                else:
                    error_type = "MISSING_OR_WRONG"
        else:
            correct += 1

        details.append({
            "entity_vi": vi_term,
            "entity_km": km_term,
            "correct_in_hyp": in_hyp,
            "correct_in_ref": in_ref,
            "error_type": error_type,
            "category": ent.get("category", "unknown"),
            "group": ent.get("group", ent.get("type", "?")),
        })

    cuea = correct / len(unique_entities)
    return {
        "cuea": round(cuea, 3),
        "n_entities": len(unique_entities),
        "n_correct": correct,
        "details": details,
    }


# ── Tier 3: Script Purity Score ──────────────────────────────────────

def compute_script_purity(text_km):
    """
    Script Purity Score:
    Measures what fraction of the output is in proper Khmer script.
    Detects foreign character leakage (Chinese, Vietnamese, Latin).

    Returns:
        dict with purity score (0-1), foreign character details
    """
    text_km = text_km or ""

    if not text_km.strip():
        return {
            "purity": 0,
            "is_pure": False,
            "n_chinese_chars": 0,
            "n_vietnamese_chars": 0,
            "n_latin_words": 0,
            "foreign_chars": [],
            "details": {},
        }

    chars = [c for c in text_km if not c.isspace() and c not in '.,;:!?()[]{}"-/\\\'']
    if not chars:
        return {
            "purity": 1.0,
            "is_pure": True,
            "n_chinese_chars": 0,
            "n_vietnamese_chars": 0,
            "n_latin_words": 0,
            "foreign_chars": [],
            "details": {},
        }

    khmer_count = sum(1 for c in chars if KHMER_SCRIPT.match(c))
    chinese_found = CHINESE_CHARS.findall(text_km)
    vietnamese_found = VIETNAMESE_SPECIFIC.findall(text_km)
    latin_found = LATIN_ALPHA.findall(text_km)

    digits = sum(1 for c in chars if c.isdigit())
    punctuation = sum(1 for c in chars if not c.isalnum())

    total_meaningful = len(chars) - digits
    if total_meaningful <= 0:
        total_meaningful = len(chars)

    purity = khmer_count / total_meaningful if total_meaningful > 0 else 0

    foreign_chars = []
    if chinese_found:
        foreign_chars.extend([{"char": c, "type": "chinese"} for c in chinese_found])
    if vietnamese_found:
        foreign_chars.extend([{"char": c, "type": "vietnamese"} for c in vietnamese_found])
    if latin_found and len(latin_found) > 3:
        latin_words = re.findall(r'[A-Za-zÀ-ỹ]{2,}', text_km)
        foreign_chars.extend([{"word": w, "type": "latin_word"} for w in latin_words])

    return {
        "purity": round(purity, 3),
        "is_pure": len(chinese_found) == 0 and len(vietnamese_found) == 0,
        "n_chinese_chars": len(chinese_found),
        "n_vietnamese_chars": len(vietnamese_found),
        "n_latin_words": len(re.findall(r'[A-Za-zÀ-ỹ]{2,}', text_km)),
        "foreign_chars": foreign_chars[:10],
    }


# ── Tier 4: Error Taxonomy ──────────────────────────────────────────

def classify_errors(source_vi, hypothesis_km, reference_km):
    """
    Classify translation errors by type.
    """
    hypothesis_km = hypothesis_km or ""
    reference_km = reference_km or ""

    cuea_result = compute_cuea(source_vi, hypothesis_km, reference_km)
    purity_result = compute_script_purity(hypothesis_km)
    if "is_pure" not in purity_result:
        purity_result = {
            "purity": purity_result.get("purity", 0),
            "is_pure": False,
            "n_chinese_chars": purity_result.get("n_chinese_chars", 0),
            "n_vietnamese_chars": purity_result.get("n_vietnamese_chars", 0),
            "n_latin_words": purity_result.get("n_latin_words", 0),
            "foreign_chars": purity_result.get("foreign_chars", []),
            "details": purity_result.get("details", {}),
        }
    standard = compute_sentence_metrics(hypothesis_km, reference_km)

    errors = []

    for detail in cuea_result.get("details", []):
        if detail["error_type"]:
            errors.append({
                "type": detail["error_type"],
                "entity": detail["entity_vi"],
                "expected_km": detail["entity_km"],
                "group": detail["group"],
            })

    if not purity_result["is_pure"]:
        if purity_result["n_chinese_chars"] > 0:
            errors.append({"type": "CHINESE_LEAK",
                           "count": purity_result["n_chinese_chars"]})
        if purity_result["n_vietnamese_chars"] > 0:
            errors.append({"type": "VIETNAMESE_LEAK",
                           "count": purity_result["n_vietnamese_chars"]})

    return {
        "standard_metrics": standard,
        "cuea": cuea_result,
        "script_purity": purity_result,
        "errors": errors,
        "n_errors": len(errors),
    }


# ── Full Evaluation Pipeline ─────────────────────────────────────────

def evaluate_full(sources, hypotheses, references):
    """Run complete evaluation on a set of translations."""
    corpus_standard = compute_standard_metrics(hypotheses, references)

    all_cuea = []
    all_purity = []
    all_errors = defaultdict(int)
    per_sample = []

    for src, hyp, ref in zip(sources, hypotheses, references):
        result = classify_errors(src, hyp, ref)
        per_sample.append(result)

        if result["cuea"]["cuea"] is not None:
            all_cuea.append(result["cuea"]["cuea"])
        all_purity.append(result["script_purity"]["purity"])

        for err in result["errors"]:
            all_errors[err["type"]] += 1

    avg_cuea = sum(all_cuea) / len(all_cuea) if all_cuea else None
    avg_purity = sum(all_purity) / len(all_purity) if all_purity else 0

    return {
        "corpus_metrics": corpus_standard,
        "avg_cuea": round(avg_cuea, 3) if avg_cuea else None,
        "n_cuea_samples": len(all_cuea),
        "avg_script_purity": round(avg_purity, 3),
        "error_distribution": dict(all_errors),
        "per_sample": per_sample,
    }


# ── Demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("Cultural Evaluation Framework — Demo")
    print("=" * 70)

    test_cases = [
        {
            "source": "Người dân không làm cốm dẹp vào ngày thường vì tốn thời gian.",
            "hypothesis_bad": "ប្រជាជនមិនធ្វើអាហារកុមដេបនៅថ្ងៃធម្មតាទេព្រោះចំណាយពេលច្រើន។",
            "hypothesis_good": "ប្រជាជនមិនធ្វើអំបុកនៅថ្ងៃធម្មតា ព្រោះម្ហូបនេះចំណាយពេលវេលាច្រើន។",
            "reference": "ប្រជាជនខ្មែរមិនធ្វើ អំបុក នៅថ្ងៃធម្មតា ព្រោះនំនេះត្រូវចំណាយពេល និងកម្លាំងច្រើន។",
        },
        {
            "source": "Chúng tôi thường rủ nhau đi lễ chùa.",
            "hypothesis_bad": "យើងតែងតែអញ្ជើញគ្នាទៅ拜寺។",
            "hypothesis_good": "យើងតែងតែបបួលគ org នាទៅវត្ត។",
            "reference": "យើងច្រើនតែបបួយគ្នាទៅវត្ត។",
        },
    ]

    for i, tc in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Source: {tc['source']}")

        print(f"\n  BAD hypothesis:")
        result_bad = classify_errors(tc["source"], tc["hypothesis_bad"], tc["reference"])
        print(f"    chrF++: {result_bad['standard_metrics']['chrf++']}")
        print(f"    CuEA:   {result_bad['cuea']['cuea']}")
        print(f"    Purity: {result_bad['script_purity']['purity']} (pure={result_bad['script_purity']['is_pure']})")
        print(f"    Errors: {[e['type'] for e in result_bad['errors']]}")

        print(f"\n  GOOD hypothesis (KB-RAG):")
        result_good = classify_errors(tc["source"], tc["hypothesis_good"], tc["reference"])
        print(f"    chrF++: {result_good['standard_metrics']['chrf++']}")
        print(f"    CuEA:   {result_good['cuea']['cuea']}")
        print(f"    Purity: {result_good['script_purity']['purity']} (pure={result_good['script_purity']['is_pure']})")
        print(f"    Errors: {[e['type'] for e in result_good['errors']]}")
