"""
Comprehensive Comparison Report: Gemini vs GPT-4o vs Local Models
==================================================================
Generates detailed analysis comparing all models across multiple metrics
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_result_files():
    """Find all result files"""
    results_dir = Path(__file__).parent / "experiment_results"
    
    gemini_files = sorted(results_dir.glob("gemini_bidirectional_*.json"))
    gpt4o_files = sorted(results_dir.glob("expALL_results_*.json"))
    
    return {
        "gemini": gemini_files[-1] if gemini_files else None,
        "gpt4o": gpt4o_files[-1] if gpt4o_files else None,
    }


def load_result_file(filepath):
    """Load and parse result file"""
    if not filepath or not filepath.exists():
        return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def generate_comparison_report():
    """Generate comprehensive comparison report"""
    files = find_result_files()
    
    print("\n" + "=" * 100, flush=True)
    print(f"COMPREHENSIVE MODEL COMPARISON REPORT | {datetime.now().isoformat()}", flush=True)
    print("=" * 100, flush=True)

    # Load data
    gemini_data = load_result_file(files["gemini"])
    gpt4o_data = load_result_file(files["gpt4o"])
    
    if not gemini_data:
        print("\n⚠ Gemini results not available yet", flush=True)
        print(f"  Looking for: {files['gemini']}", flush=True)
        return
    
    gemini_results = gemini_data.get("results", {})
    gpt4o_results = gpt4o_data.get("results", {}) if gpt4o_data else {}
    
    print("\n" + "─" * 100, flush=True)
    print("MODEL OVERVIEW", flush=True)
    print("─" * 100, flush=True)
    
    print(f"\n✓ Gemini 2.5 Flash (via Devmate)", flush=True)
    print(f"  Samples: {gemini_results.get('total_samples', 'N/A')}", flush=True)
    print(f"  Timestamp: {gemini_results.get('timestamp', 'N/A')}", flush=True)
    
    if gpt4o_results:
        print(f"\n✓ GPT-4o (via Azure OpenAI)", flush=True)
        print(f"  Samples: {gpt4o_results.get('total_samples', 'N/A')}", flush=True)
    else:
        print(f"\n✗ GPT-4o results not available", flush=True)

    # Vietnamese → Khmer comparison
    print("\n" + "─" * 100, flush=True)
    print("VIETNAMESE → KHMER TRANSLATION", flush=True)
    print("─" * 100, flush=True)
    
    vikh_gemini = gemini_results.get("vikh", {})
    vikh_gpt4o = gpt4o_results.get("vikh", {}) if gpt4o_results else {}
    
    print(f"\n{'Model':<25} {'Plain chrF++':<15} {'KB-RAG chrF++':<15} {'Improvement':<15}", flush=True)
    print("─" * 70, flush=True)
    
    if vikh_gemini:
        print(f"{'Gemini 2.5 Flash':<25} {vikh_gemini.get('plain_chrf', 0):>14.2f} {vikh_gemini.get('kb_chrf', 0):>14.2f} {vikh_gemini.get('chrf_delta', 0):>+14.2f}", flush=True)
    
    if vikh_gpt4o:
        print(f"{'GPT-4o':<25} {vikh_gpt4o.get('plain_chrf', 0):>14.2f} {vikh_gpt4o.get('kb_chrf', 0):>14.2f} {vikh_gpt4o.get('chrf_delta', 0):>+14.2f}", flush=True)

    # Khmer → Vietnamese comparison
    print("\n" + "─" * 100, flush=True)
    print("KHMER → VIETNAMESE TRANSLATION", flush=True)
    print("─" * 100, flush=True)
    
    khvi_gemini = gemini_results.get("khvi", {})
    khvi_gpt4o = gpt4o_results.get("khvi", {}) if gpt4o_results else {}
    
    print(f"\n{'Model':<25} {'Plain chrF++':<15} {'KB-RAG chrF++':<15} {'Improvement':<15}", flush=True)
    print("─" * 70, flush=True)
    
    if khvi_gemini:
        print(f"{'Gemini 2.5 Flash':<25} {khvi_gemini.get('plain_chrf', 0):>14.2f} {khvi_gemini.get('kb_chrf', 0):>14.2f} {khvi_gemini.get('chrf_delta', 0):>+14.2f}", flush=True)
    
    if khvi_gpt4o:
        print(f"{'GPT-4o':<25} {khvi_gpt4o.get('plain_chrf', 0):>14.2f} {khvi_gpt4o.get('kb_chrf', 0):>14.2f} {khvi_gpt4o.get('chrf_delta', 0):>+14.2f}", flush=True)

    # Overall performance
    print("\n" + "─" * 100, flush=True)
    print("OVERALL BIDIRECTIONAL PERFORMANCE", flush=True)
    print("─" * 100, flush=True)
    
    avg_plain_gemini = (vikh_gemini.get('plain_chrf', 0) + khvi_gemini.get('plain_chrf', 0)) / 2 if vikh_gemini and khvi_gemini else 0
    avg_kb_gemini = (vikh_gemini.get('kb_chrf', 0) + khvi_gemini.get('kb_chrf', 0)) / 2 if vikh_gemini and khvi_gemini else 0
    avg_delta_gemini = avg_kb_gemini - avg_plain_gemini
    
    avg_plain_gpt4o = (vikh_gpt4o.get('plain_chrf', 0) + khvi_gpt4o.get('plain_chrf', 0)) / 2 if vikh_gpt4o and khvi_gpt4o else 0
    avg_kb_gpt4o = (vikh_gpt4o.get('kb_chrf', 0) + khvi_gpt4o.get('kb_chrf', 0)) / 2 if vikh_gpt4o and khvi_gpt4o else 0
    avg_delta_gpt4o = avg_kb_gpt4o - avg_plain_gpt4o
    
    print(f"\n{'Model':<25} {'Plain Avg':<15} {'KB-RAG Avg':<15} {'KB Improvement':<15}", flush=True)
    print("─" * 70, flush=True)
    print(f"{'Gemini 2.5 Flash':<25} {avg_plain_gemini:>14.2f} {avg_kb_gemini:>14.2f} {avg_delta_gemini:>+14.2f}", flush=True)
    if vikh_gpt4o or khvi_gpt4o:
        print(f"{'GPT-4o':<25} {avg_plain_gpt4o:>14.2f} {avg_kb_gpt4o:>14.2f} {avg_delta_gpt4o:>+14.2f}", flush=True)

    # Key insights
    print("\n" + "─" * 100, flush=True)
    print("KEY INSIGHTS", flush=True)
    print("─" * 100, flush=True)
    
    if avg_kb_gemini > avg_kb_gpt4o:
        print(f"\n✓ Gemini KB-RAG outperforms GPT-4o: {avg_kb_gemini:.2f} vs {avg_kb_gpt4o:.2f} ({avg_kb_gemini - avg_kb_gpt4o:+.2f})", flush=True)
    elif avg_kb_gpt4o > 0:
        print(f"\n✗ GPT-4o KB-RAG outperforms Gemini: {avg_kb_gpt4o:.2f} vs {avg_kb_gemini:.2f} ({avg_kb_gpt4o - avg_kb_gemini:+.2f})", flush=True)
    
    if avg_delta_gemini > 0:
        print(f"✓ KB-RAG helps Gemini: +{avg_delta_gemini:.2f} chrF++ improvement", flush=True)
    
    # Directionality analysis
    if vikh_gemini.get('kb_chrf', 0) > khvi_gemini.get('kb_chrf', 0):
        print(f"✓ Gemini performs better on Vi→Km ({vikh_gemini.get('kb_chrf', 0):.2f}) than Km→Vi ({khvi_gemini.get('kb_chrf', 0):.2f})", flush=True)
    else:
        print(f"✓ Gemini performs better on Km→Vi ({khvi_gemini.get('kb_chrf', 0):.2f}) than Vi→Km ({vikh_gemini.get('kb_chrf', 0):.2f})", flush=True)

    print("\n" + "=" * 100, flush=True)
    
    # Save report
    report_file = Path(__file__).parent / "experiment_results" / f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "gemini": gemini_results,
        "gpt4o": gpt4o_results,
        "summary": {
            "bidirectional_avg_gemini": {
                "plain": avg_plain_gemini,
                "kb": avg_kb_gemini,
                "improvement": avg_delta_gemini,
            },
            "bidirectional_avg_gpt4o": {
                "plain": avg_plain_gpt4o,
                "kb": avg_kb_gpt4o,
                "improvement": avg_delta_gpt4o,
            }
        }
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Report saved to: {report_file}", flush=True)


if __name__ == "__main__":
    generate_comparison_report()
