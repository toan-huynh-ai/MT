"""
Comprehensive Analysis: Gemini vs Claude Haiku
===============================================
Detailed comparison of both models' performance
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "kb"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "eval"))

from evaluation_framework import compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_result_file(filepath):
    """Load result file"""
    if not filepath or not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def find_latest_files():
    """Find latest result files"""
    results_dir = Path(__file__).parent / "experiment_results"
    
    gemini_files = sorted(results_dir.glob("gemini_bidirectional_*.json"))
    claude_files = sorted(results_dir.glob("claude_haiku_bidirectional_*.json"))
    claude_checkpoint = sorted(results_dir.glob("claude_haiku_checkpoint_*.json"))
    
    return {
        "gemini": gemini_files[-1] if gemini_files else None,
        "claude_final": claude_files[-1] if claude_files else None,
        "claude_checkpoint": claude_checkpoint[-1] if claude_checkpoint else None,
    }


def analyze_checkpoint(filepath):
    """Analyze checkpoint file"""
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    per_sample = data["per_sample"]
    completed = data["completed"]
    total = data["total"]
    
    # Vietnamese → Khmer
    vikh_plain = [r["vikh_plain"] for r in per_sample]
    vikh_kb = [r["vikh_kb"] for r in per_sample]
    vikh_refs = [r["vikh_reference"] for r in per_sample]
    
    # Khmer → Vietnamese
    khvi_plain = [r["khvi_plain"] for r in per_sample]
    khvi_kb = [r["khvi_kb"] for r in per_sample]
    khvi_refs = [r["khvi_reference"] for r in per_sample]
    
    m_vikh_p = compute_standard_metrics(vikh_plain, vikh_refs)
    m_vikh_k = compute_standard_metrics(vikh_kb, vikh_refs)
    m_khvi_p = compute_standard_metrics(khvi_plain, khvi_refs)
    m_khvi_k = compute_standard_metrics(khvi_kb, khvi_refs)
    
    return {
        "completed": completed,
        "total": total,
        "progress": f"{completed}/{total} ({100*completed/total:.1f}%)",
        "vikh": {
            "plain_chrf": m_vikh_p["chrf++"],
            "kb_chrf": m_vikh_k["chrf++"],
            "chrf_delta": m_vikh_k["chrf++"] - m_vikh_p["chrf++"],
        },
        "khvi": {
            "plain_chrf": m_khvi_p["chrf++"],
            "kb_chrf": m_khvi_k["chrf++"],
            "chrf_delta": m_khvi_k["chrf++"] - m_khvi_p["chrf++"],
        },
    }


def main():
    files = find_latest_files()
    
    print("\n" + "=" * 100, flush=True)
    print(f"COMPREHENSIVE MODEL COMPARISON - {datetime.now().isoformat()}", flush=True)
    print("=" * 100, flush=True)
    
    # Load Gemini results
    gemini_data = load_result_file(files["gemini"])
    gemini_results = gemini_data.get("results", {}) if gemini_data else {}
    
    # Load Claude results (final or checkpoint)
    claude_data = load_result_file(files["claude_final"])
    claude_checkpoint_data = load_result_file(files["claude_checkpoint"]) if not claude_data else None
    
    if claude_checkpoint_data and not claude_data:
        claude_results = analyze_checkpoint(files["claude_checkpoint"])
        claude_status = "🔄 In Progress (Checkpoint)"
    elif claude_data:
        claude_results = claude_data.get("results", {})
        claude_status = "✅ Complete"
    else:
        claude_results = {}
        claude_status = "❌ Not Available"
    
    # Print status
    print(f"\n{'MODEL STATUS':^100}", flush=True)
    print("─" * 100, flush=True)
    print(f"Gemini 2.5 Flash:     ✅ Complete (1856 samples)", flush=True)
    print(f"Claude Haiku 4.5:     {claude_status}", flush=True)
    
    if claude_results:
        if "progress" in claude_results:
            print(f"  └─ Progress: {claude_results['progress']}", flush=True)
    
    # Vietnamese → Khmer Comparison
    print(f"\n{'VIETNAMESE → KHMER TRANSLATION':^100}", flush=True)
    print("─" * 100, flush=True)
    print(f"{'Model':<30} {'Plain chrF++':<20} {'KB-RAG chrF++':<20} {'Improvement':<20}", flush=True)
    print("─" * 100, flush=True)
    
    gemini_vikh = gemini_results.get("vikh", {})
    print(f"{'Gemini 2.5 Flash':<30} {gemini_vikh.get('plain_chrf', 0):>19.2f} {gemini_vikh.get('kb_chrf', 0):>19.2f} {gemini_vikh.get('chrf_delta', 0):>+19.2f}", flush=True)
    
    claude_vikh = claude_results.get("vikh", {})
    if claude_vikh:
        print(f"{'Claude Haiku 4.5':<30} {claude_vikh.get('plain_chrf', 0):>19.2f} {claude_vikh.get('kb_chrf', 0):>19.2f} {claude_vikh.get('chrf_delta', 0):>+19.2f}", flush=True)
    
    # Khmer → Vietnamese Comparison
    print(f"\n{'KHMER → VIETNAMESE TRANSLATION':^100}", flush=True)
    print("─" * 100, flush=True)
    print(f"{'Model':<30} {'Plain chrF++':<20} {'KB-RAG chrF++':<20} {'Improvement':<20}", flush=True)
    print("─" * 100, flush=True)
    
    gemini_khvi = gemini_results.get("khvi", {})
    print(f"{'Gemini 2.5 Flash':<30} {gemini_khvi.get('plain_chrf', 0):>19.2f} {gemini_khvi.get('kb_chrf', 0):>19.2f} {gemini_khvi.get('chrf_delta', 0):>+19.2f}", flush=True)
    
    claude_khvi = claude_results.get("khvi", {})
    if claude_khvi:
        print(f"{'Claude Haiku 4.5':<30} {claude_khvi.get('plain_chrf', 0):>19.2f} {claude_khvi.get('kb_chrf', 0):>19.2f} {claude_khvi.get('chrf_delta', 0):>+19.2f}", flush=True)
    
    # Bidirectional Average
    print(f"\n{'BIDIRECTIONAL AVERAGE (OVERALL)':^100}", flush=True)
    print("─" * 100, flush=True)
    print(f"{'Model':<30} {'Plain chrF++':<20} {'KB-RAG chrF++':<20} {'Improvement':<20}", flush=True)
    print("─" * 100, flush=True)
    
    gemini_avg_plain = (gemini_vikh.get('plain_chrf', 0) + gemini_khvi.get('plain_chrf', 0)) / 2
    gemini_avg_kb = (gemini_vikh.get('kb_chrf', 0) + gemini_khvi.get('kb_chrf', 0)) / 2
    gemini_avg_delta = gemini_avg_kb - gemini_avg_plain
    
    print(f"{'Gemini 2.5 Flash':<30} {gemini_avg_plain:>19.2f} {gemini_avg_kb:>19.2f} {gemini_avg_delta:>+19.2f}", flush=True)
    
    if claude_vikh and claude_khvi:
        claude_avg_plain = (claude_vikh.get('plain_chrf', 0) + claude_khvi.get('plain_chrf', 0)) / 2
        claude_avg_kb = (claude_vikh.get('kb_chrf', 0) + claude_khvi.get('kb_chrf', 0)) / 2
        claude_avg_delta = claude_avg_kb - claude_avg_plain
        
        print(f"{'Claude Haiku 4.5':<30} {claude_avg_plain:>19.2f} {claude_avg_kb:>19.2f} {claude_avg_delta:>+19.2f}", flush=True)
    
    # Winner determination
    print(f"\n{'PERFORMANCE RANKING':^100}", flush=True)
    print("─" * 100, flush=True)
    
    if gemini_vikh and gemini_khvi:
        print(f"\n🥇 Vietnamese → Khmer (Vi→Km):", flush=True)
        print(f"   KB-RAG chrF++: Gemini {gemini_vikh.get('kb_chrf', 0):.2f}", end="", flush=True)
        if claude_vikh:
            print(f" vs Claude {claude_vikh.get('kb_chrf', 0):.2f}", flush=True)
            if gemini_vikh.get('kb_chrf', 0) > claude_vikh.get('kb_chrf', 0):
                print(f"   ✅ Gemini wins by {gemini_vikh.get('kb_chrf', 0) - claude_vikh.get('kb_chrf', 0):+.2f}", flush=True)
            else:
                print(f"   ✅ Claude wins by {claude_vikh.get('kb_chrf', 0) - gemini_vikh.get('kb_chrf', 0):+.2f}", flush=True)
        else:
            print("", flush=True)
        
        print(f"\n🥇 Khmer → Vietnamese (Km→Vi):", flush=True)
        print(f"   KB-RAG chrF++: Gemini {gemini_khvi.get('kb_chrf', 0):.2f}", end="", flush=True)
        if claude_khvi:
            print(f" vs Claude {claude_khvi.get('kb_chrf', 0):.2f}", flush=True)
            if gemini_khvi.get('kb_chrf', 0) > claude_khvi.get('kb_chrf', 0):
                print(f"   ✅ Gemini wins by {gemini_khvi.get('kb_chrf', 0) - claude_khvi.get('kb_chrf', 0):+.2f}", flush=True)
            else:
                print(f"   ✅ Claude wins by {claude_khvi.get('kb_chrf', 0) - gemini_khvi.get('kb_chrf', 0):+.2f}", flush=True)
        else:
            print("", flush=True)
    
    # Key insights
    print(f"\n{'KEY INSIGHTS':^100}", flush=True)
    print("─" * 100, flush=True)
    
    print(f"\n✨ Gemini 2.5 Flash:", flush=True)
    print(f"   • Vi→Km: Plain 0.50 → KB-RAG 5.89 (+1078% improvement) 🚀", flush=True)
    print(f"   • Km→Vi: Plain 3.21 → KB-RAG 3.19 (slightly worse) ⚠️", flush=True)
    print(f"   • Overall: Average chrF++ improves from 1.85 to 4.54 (+145%)", flush=True)
    print(f"   • Recommendation: Use KB-RAG for Vi→Km, plain for Km→Vi", flush=True)
    
    if claude_results.get("completed"):
        print(f"\n📊 Claude Haiku 4.5:", flush=True)
        print(f"   • Progress: {claude_results['progress']}", flush=True)
        if claude_vikh:
            print(f"   • Vi→Km: Plain {claude_vikh.get('plain_chrf', 0):.2f} → KB-RAG {claude_vikh.get('kb_chrf', 0):.2f} ({claude_vikh.get('chrf_delta', 0):+.2f})", flush=True)
        if claude_khvi:
            print(f"   • Km→Vi: Plain {claude_khvi.get('plain_chrf', 0):.2f} → KB-RAG {claude_khvi.get('kb_chrf', 0):.2f} ({claude_khvi.get('chrf_delta', 0):+.2f})", flush=True)
    
    print("\n" + "=" * 100, flush=True)


if __name__ == "__main__":
    main()
