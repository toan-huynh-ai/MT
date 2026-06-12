"""
Real-time Analysis: Monitor Gemini bidirectional evaluation progress
===================================================================
Analyzes current checkpoint and produces detailed report
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "kb"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "eval"))

from evaluation_framework import compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_latest_checkpoint():
    """Find the latest checkpoint file"""
    results_dir = Path(__file__).parent / "experiment_results"
    checkpoint_files = sorted(results_dir.glob("bidirectional_checkpoint_*.json"))
    if not checkpoint_files:
        return None
    return checkpoint_files[-1]


def analyze_checkpoint():
    """Analyze current checkpoint"""
    checkpoint_file = find_latest_checkpoint()
    
    if not checkpoint_file:
        print("No checkpoint found yet", flush=True)
        return
    
    with open(checkpoint_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    per_sample = data["per_sample"]
    completed = data["completed"]
    total = data["total"]
    
    print("\n" + "=" * 80, flush=True)
    print(f"GEMINI BIDIRECTIONAL ANALYSIS | Progress: {completed}/{total} ({100*completed/total:.1f}%)", flush=True)
    print("=" * 80, flush=True)

    # Vietnamese → Khmer
    vikh_plain = [r["vikh_plain"] for r in per_sample]
    vikh_kb = [r["vikh_kb"] for r in per_sample]
    vikh_refs = [r["vikh_reference"] for r in per_sample]
    
    # Khmer → Vietnamese
    khvi_plain = [r["khvi_plain"] for r in per_sample]
    khvi_kb = [r["khvi_kb"] for r in per_sample]
    khvi_refs = [r["khvi_reference"] for r in per_sample]
    
    # Metrics
    m_vikh_p = compute_standard_metrics(vikh_plain, vikh_refs)
    m_vikh_k = compute_standard_metrics(vikh_kb, vikh_refs)
    m_khvi_p = compute_standard_metrics(khvi_plain, khvi_refs)
    m_khvi_k = compute_standard_metrics(khvi_kb, khvi_refs)

    print(f"\n{'VIETNAMESE → KHMER TRANSLATION':^80}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Metric':<40} {'Plain':>15} {'KB-RAG':>15} {'Delta':>10}", flush=True)
    print(f"{'chrF++ (all)':<40} {m_vikh_p['chrf++']:>15.2f} {m_vikh_k['chrf++']:>15.2f} {m_vikh_k['chrf++'] - m_vikh_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'BLEU (all)':<40} {m_vikh_p['bleu']:>15.2f} {m_vikh_k['bleu']:>15.2f} {m_vikh_k['bleu'] - m_vikh_p['bleu']:>+10.2f}", flush=True)

    print(f"\n{'KHMER → VIETNAMESE TRANSLATION':^80}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Metric':<40} {'Plain':>15} {'KB-RAG':>15} {'Delta':>10}", flush=True)
    print(f"{'chrF++ (all)':<40} {m_khvi_p['chrf++']:>15.2f} {m_khvi_k['chrf++']:>15.2f} {m_khvi_k['chrf++'] - m_khvi_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'BLEU (all)':<40} {m_khvi_p['bleu']:>15.2f} {m_khvi_k['bleu']:>15.2f} {m_khvi_k['bleu'] - m_khvi_p['bleu']:>+10.2f}", flush=True)

    print(f"\n{'BIDIRECTIONAL COMPARISON':^80}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Direction':<40} {'Plain chrF++':>15} {'KB-RAG chrF++':>15} {'Improvement':>10}", flush=True)
    print(f"{'Vi → Km':<40} {m_vikh_p['chrf++']:>15.2f} {m_vikh_k['chrf++']:>15.2f} {m_vikh_k['chrf++'] - m_vikh_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'Km → Vi':<40} {m_khvi_p['chrf++']:>15.2f} {m_khvi_k['chrf++']:>15.2f} {m_khvi_k['chrf++'] - m_khvi_p['chrf++']:>+10.2f}", flush=True)
    print(f"{'Average':<40} {(m_vikh_p['chrf++'] + m_khvi_p['chrf++'])/2:>15.2f} {(m_vikh_k['chrf++'] + m_khvi_k['chrf++'])/2:>15.2f} {((m_vikh_k['chrf++'] + m_khvi_k['chrf++']) - (m_vikh_p['chrf++'] + m_khvi_p['chrf++']))/2:>+10.2f}", flush=True)

    # Quality analysis
    print(f"\n{'QUALITY ANALYSIS':^80}", flush=True)
    print("-" * 80, flush=True)
    
    # Count empty translations
    vikh_empty_plain = sum(1 for h in vikh_plain if not h or h.strip() == "")
    vikh_empty_kb = sum(1 for h in vikh_kb if not h or h.strip() == "")
    khvi_empty_plain = sum(1 for h in khvi_plain if not h or h.strip() == "")
    khvi_empty_kb = sum(1 for h in khvi_kb if not h or h.strip() == "")
    
    print(f"{'Empty translations:':<40}", flush=True)
    print(f"  {'Vi → Km Plain':<36} {vikh_empty_plain:>5} ({100*vikh_empty_plain/len(vikh_plain):>5.1f}%)", flush=True)
    print(f"  {'Vi → Km KB-RAG':<36} {vikh_empty_kb:>5} ({100*vikh_empty_kb/len(vikh_kb):>5.1f}%)", flush=True)
    print(f"  {'Km → Vi Plain':<36} {khvi_empty_plain:>5} ({100*khvi_empty_plain/len(khvi_plain):>5.1f}%)", flush=True)
    print(f"  {'Km → Vi KB-RAG':<36} {khvi_empty_kb:>5} ({100*khvi_empty_kb/len(khvi_kb):>5.1f}%)", flush=True)
    
    # Count perfect matches
    vikh_perfect_plain = sum(1 for h, r in zip(vikh_plain, vikh_refs) if h.strip() == r.strip())
    vikh_perfect_kb = sum(1 for h, r in zip(vikh_kb, vikh_refs) if h.strip() == r.strip())
    khvi_perfect_plain = sum(1 for h, r in zip(khvi_plain, khvi_refs) if h.strip() == r.strip())
    khvi_perfect_kb = sum(1 for h, r in zip(khvi_kb, khvi_refs) if h.strip() == r.strip())
    
    print(f"\n{'Perfect matches:':<40}", flush=True)
    print(f"  {'Vi → Km Plain':<36} {vikh_perfect_plain:>5} ({100*vikh_perfect_plain/len(vikh_plain):>5.1f}%)", flush=True)
    print(f"  {'Vi → Km KB-RAG':<36} {vikh_perfect_kb:>5} ({100*vikh_perfect_kb/len(vikh_kb):>5.1f}%)", flush=True)
    print(f"  {'Km → Vi Plain':<36} {khvi_perfect_plain:>5} ({100*khvi_perfect_plain/len(khvi_plain):>5.1f}%)", flush=True)
    print(f"  {'Km → Vi KB-RAG':<36} {khvi_perfect_kb:>5} ({100*khvi_perfect_kb/len(khvi_kb):>5.1f}%)", flush=True)

    # Top performers
    print(f"\n{'SAMPLE EXAMPLES':^80}", flush=True)
    print("-" * 80, flush=True)
    
    # Find best Vi→Km translation (highest chrF++)
    best_idx = None
    best_score = -1
    for i, (h, r) in enumerate(zip(vikh_kb, vikh_refs)):
        try:
            from sacrebleu import corpus_chrf
            score = corpus_chrf([h], [r]).score
            if score > best_score:
                best_score = score
                best_idx = i
        except:
            pass
    
    if best_idx is not None:
        sample = per_sample[best_idx]
        print(f"\n✓ Best Vi→Km translation (score: {best_score:.1f}):", flush=True)
        print(f"  Source (Vi): {sample['source_vi'][:70]}", flush=True)
        print(f"  Reference (Km): {sample['vikh_reference'][:70]}", flush=True)
        print(f"  Prediction (KB): {sample['vikh_kb'][:70]}", flush=True)

    print(f"\n{'Checkpoint info:':<40} {checkpoint_file.name}", flush=True)
    print(f"{'Progress:':<40} {completed}/{total} ({100*completed/total:.1f}%)", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    analyze_checkpoint()
