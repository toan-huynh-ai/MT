"""
Real-time Dashboard Monitor
============================
Shows live progress of Gemini bidirectional evaluation
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "kb"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "eval"))

from evaluation_framework import compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_latest_checkpoint():
    """Find latest checkpoint"""
    results_dir = Path(__file__).parent / "experiment_results"
    checkpoint_files = sorted(results_dir.glob("bidirectional_checkpoint_*.json"))
    return checkpoint_files[-1] if checkpoint_files else None


def monitor():
    """Live monitoring"""
    checkpoint_file = find_latest_checkpoint()
    if not checkpoint_file:
        print("No checkpoint found", flush=True)
        return
    
    print(f"\n{'='*100}", flush=True)
    print(f"GEMINI BIDIRECTIONAL EVALUATION - LIVE MONITOR", flush=True)
    print(f"{'='*100}\n", flush=True)
    
    start_times = {}
    
    while True:
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            per_sample = data["per_sample"]
            completed = data["completed"]
            total = data["total"]
            
            # Calculate stats
            if not start_times:
                start_times["start"] = datetime.now()
                start_times["first_sample"] = completed
            
            elapsed = datetime.now() - start_times["start"]
            samples_processed = completed - start_times.get("first_sample", 0)
            rate = samples_processed / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
            remaining_samples = total - completed
            eta_seconds = remaining_samples / rate if rate > 0 else 0
            eta_time = datetime.now() + timedelta(seconds=eta_seconds)
            
            # Progress bar
            progress_pct = 100 * completed / total
            bar_length = 40
            filled = int(bar_length * completed / total)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # Metrics
            vikh_plain = [r["vikh_plain"] for r in per_sample]
            vikh_kb = [r["vikh_kb"] for r in per_sample]
            vikh_refs = [r["vikh_reference"] for r in per_sample]
            khvi_plain = [r["khvi_plain"] for r in per_sample]
            khvi_kb = [r["khvi_kb"] for r in per_sample]
            khvi_refs = [r["khvi_reference"] for r in per_sample]
            
            m_vikh_p = compute_standard_metrics(vikh_plain, vikh_refs)
            m_vikh_k = compute_standard_metrics(vikh_kb, vikh_refs)
            m_khvi_p = compute_standard_metrics(khvi_plain, khvi_refs)
            m_khvi_k = compute_standard_metrics(khvi_kb, khvi_refs)
            
            # Display
            print(f"\r[{bar}] {progress_pct:>5.1f}% | {completed:>4}/{total} | {rate:.2f} samples/s | ETA: {eta_time.strftime('%H:%M:%S')}", end="", flush=True)
            
            # Every 50 samples, show detailed metrics
            if completed % 50 == 0 and completed > 0:
                print(f"\n\n📊 CHECKPOINT {completed} METRICS", flush=True)
                print(f"{'─'*80}", flush=True)
                print(f"{'Vietnamese → Khmer':<30} {'Plain chrF++':<15} {'KB-RAG chrF++':<15} {'Δ':<15}", flush=True)
                print(f"{'':30} {m_vikh_p['chrf++']:>14.2f} {m_vikh_k['chrf++']:>14.2f} {m_vikh_k['chrf++'] - m_vikh_p['chrf++']:>+14.2f}", flush=True)
                
                print(f"\n{'Khmer → Vietnamese':<30} {'Plain chrF++':<15} {'KB-RAG chrF++':<15} {'Δ':<15}", flush=True)
                print(f"{'':30} {m_khvi_p['chrf++']:>14.2f} {m_khvi_k['chrf++']:>14.2f} {m_khvi_k['chrf++'] - m_khvi_p['chrf++']:>+14.2f}", flush=True)
                
                avg_plain = (m_vikh_p['chrf++'] + m_khvi_p['chrf++']) / 2
                avg_kb = (m_vikh_k['chrf++'] + m_khvi_k['chrf++']) / 2
                print(f"\n{'Average (Bidirectional)':<30} {avg_plain:>14.2f} {avg_kb:>14.2f} {avg_kb - avg_plain:>+14.2f}", flush=True)
                print(f"{'':30} (calculated from {completed} samples)\n", flush=True)
            
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"\nError: {e}", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print(f"\n\n✓ Monitoring stopped by user", flush=True)
