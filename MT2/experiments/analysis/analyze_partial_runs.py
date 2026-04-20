import json
from pathlib import Path
from collections import defaultdict


RESULTS_DIR = Path(r"c:\Users\HOY9HC\Desktop\Code\Learning\MT\experiment_results")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sample_key(row):
    return (row["source"], row["reference"])


def merge_rows():
    files = [
        RESULTS_DIR / "exp500_final_20260417_174355.json",
        RESULTS_DIR / "expALL_checkpoint_20260417_183409.json",
        RESULTS_DIR / "expALL_resume_checkpoint_20260417_184109.json",
        RESULTS_DIR / "expALL_resume_checkpoint_20260417_192420.json",
    ]
    merged = {}
    provenance = {}

    for path in files:
        if not path.exists():
            continue
        payload = load_json(path)
        rows = payload.get("per_sample", [])
        for row in rows:
            k = sample_key(row)
            merged[k] = row
            provenance[k] = path.name
    return merged, provenance


def safe_get(row, side, path, default=None):
    cur = row.get(side, {})
    try:
        for p in path:
            cur = cur[p]
        return cur
    except Exception:
        return default


def avg(xs):
    return sum(xs) / len(xs) if xs else 0.0


def summarize(rows):
    n_total = len(rows)
    n_entities = sum(1 for r in rows if r.get("has_entities"))
    n_no_entities = n_total - n_entities

    plain_chrf_all = [safe_get(r, "eval_plain", ["standard_metrics", "chrf++"], 0) for r in rows]
    kb_chrf_all = [safe_get(r, "eval_kb", ["standard_metrics", "chrf++"], 0) for r in rows]
    plain_bleu_all = [safe_get(r, "eval_plain", ["standard_metrics", "bleu"], 0) for r in rows]
    kb_bleu_all = [safe_get(r, "eval_kb", ["standard_metrics", "bleu"], 0) for r in rows]

    ent_rows = [r for r in rows if r.get("has_entities")]
    no_ent_rows = [r for r in rows if not r.get("has_entities")]

    plain_chrf_ent = [safe_get(r, "eval_plain", ["standard_metrics", "chrf++"], 0) for r in ent_rows]
    kb_chrf_ent = [safe_get(r, "eval_kb", ["standard_metrics", "chrf++"], 0) for r in ent_rows]

    plain_chrf_noent = [safe_get(r, "eval_plain", ["standard_metrics", "chrf++"], 0) for r in no_ent_rows]
    kb_chrf_noent = [safe_get(r, "eval_kb", ["standard_metrics", "chrf++"], 0) for r in no_ent_rows]

    plain_cuea = [
        safe_get(r, "eval_plain", ["cuea", "cuea"], None)
        for r in ent_rows
        if safe_get(r, "eval_plain", ["cuea", "cuea"], None) is not None
    ]
    kb_cuea = [
        safe_get(r, "eval_kb", ["cuea", "cuea"], None)
        for r in ent_rows
        if safe_get(r, "eval_kb", ["cuea", "cuea"], None) is not None
    ]

    plain_purity = [safe_get(r, "eval_plain", ["script_purity", "purity"], 0) for r in rows]
    kb_purity = [safe_get(r, "eval_kb", ["script_purity", "purity"], 0) for r in rows]

    chrf_win_ent = sum(
        1
        for r in ent_rows
        if safe_get(r, "eval_kb", ["standard_metrics", "chrf++"], 0)
        > safe_get(r, "eval_plain", ["standard_metrics", "chrf++"], 0)
    )
    cuea_win_ent = sum(
        1
        for r in ent_rows
        if (safe_get(r, "eval_kb", ["cuea", "cuea"], 0) or 0)
        > (safe_get(r, "eval_plain", ["cuea", "cuea"], 0) or 0)
    )

    plain_err = defaultdict(int)
    kb_err = defaultdict(int)
    for r in ent_rows:
        for e in safe_get(r, "eval_plain", ["errors"], []) or []:
            plain_err[e.get("type", "UNKNOWN")] += 1
        for e in safe_get(r, "eval_kb", ["errors"], []) or []:
            kb_err[e.get("type", "UNKNOWN")] += 1

    topic_stats = defaultdict(lambda: {"n": 0, "plain_chrf": [], "kb_chrf": [], "plain_cuea": [], "kb_cuea": []})
    for r in rows:
        topic = r.get("topic") or "QA (no topic)"
        topic_stats[topic]["n"] += 1
        topic_stats[topic]["plain_chrf"].append(safe_get(r, "eval_plain", ["standard_metrics", "chrf++"], 0))
        topic_stats[topic]["kb_chrf"].append(safe_get(r, "eval_kb", ["standard_metrics", "chrf++"], 0))
        pc = safe_get(r, "eval_plain", ["cuea", "cuea"], None)
        kc = safe_get(r, "eval_kb", ["cuea", "cuea"], None)
        if pc is not None:
            topic_stats[topic]["plain_cuea"].append(pc)
        if kc is not None:
            topic_stats[topic]["kb_cuea"].append(kc)

    return {
        "n_total": n_total,
        "n_entities": n_entities,
        "n_no_entities": n_no_entities,
        "plain_chrf_all": avg(plain_chrf_all),
        "kb_chrf_all": avg(kb_chrf_all),
        "plain_bleu_all": avg(plain_bleu_all),
        "kb_bleu_all": avg(kb_bleu_all),
        "plain_chrf_ent": avg(plain_chrf_ent),
        "kb_chrf_ent": avg(kb_chrf_ent),
        "plain_chrf_noent": avg(plain_chrf_noent),
        "kb_chrf_noent": avg(kb_chrf_noent),
        "plain_cuea": avg(plain_cuea),
        "kb_cuea": avg(kb_cuea),
        "plain_purity": avg(plain_purity),
        "kb_purity": avg(kb_purity),
        "chrf_win_ent": chrf_win_ent,
        "cuea_win_ent": cuea_win_ent,
        "plain_err": dict(plain_err),
        "kb_err": dict(kb_err),
        "topic_stats": topic_stats,
    }


def print_report(summary):
    n_total = summary["n_total"]
    n_ent = summary["n_entities"]
    n_noent = summary["n_no_entities"]

    print("=" * 78)
    print(f"PARTIAL RESULTS REPORT — {n_total} samples already processed")
    print("=" * 78)
    print(f"Coverage: {n_total}/1856 ({n_total/1856*100:.1f}%)")
    print(f"  - With entities: {n_ent}")
    print(f"  - Without entities: {n_noent}")
    print()

    print(f"{'Metric':<35} {'Plain':>10} {'KB-RAG':>10} {'Delta':>10}")
    print("-" * 70)
    print(f"{'ALL samples chrF++':<35} {summary['plain_chrf_all']:>10.2f} {summary['kb_chrf_all']:>10.2f} {summary['kb_chrf_all'] - summary['plain_chrf_all']:>+10.2f}")
    print(f"{'ALL samples BLEU':<35} {summary['plain_bleu_all']:>10.2f} {summary['kb_bleu_all']:>10.2f} {summary['kb_bleu_all'] - summary['plain_bleu_all']:>+10.2f}")
    print(f"{'ENTITY samples chrF++':<35} {summary['plain_chrf_ent']:>10.2f} {summary['kb_chrf_ent']:>10.2f} {summary['kb_chrf_ent'] - summary['plain_chrf_ent']:>+10.2f}")
    print(f"{'NO-ENTITY samples chrF++':<35} {summary['plain_chrf_noent']:>10.2f} {summary['kb_chrf_noent']:>10.2f} {summary['kb_chrf_noent'] - summary['plain_chrf_noent']:>+10.2f}")
    print(f"{'Avg CuEA (entity samples)':<35} {summary['plain_cuea']:>10.3f} {summary['kb_cuea']:>10.3f} {summary['kb_cuea'] - summary['plain_cuea']:>+10.3f}")
    print(f"{'Avg Script Purity':<35} {summary['plain_purity']:>10.3f} {summary['kb_purity']:>10.3f} {summary['kb_purity'] - summary['plain_purity']:>+10.3f}")
    print(f"{'chrF++ win rate (entity)':<35} {'':>10} {summary['chrf_win_ent']}/{n_ent} ({summary['chrf_win_ent']/n_ent*100:.0f}%)")
    print(f"{'CuEA win rate (entity)':<35} {'':>10} {summary['cuea_win_ent']}/{n_ent} ({summary['cuea_win_ent']/n_ent*100:.0f}%)")
    print()

    print(f"{'Error Type':<25} {'Plain':>8} {'KB-RAG':>8} {'Reduction':>12}")
    print("-" * 60)
    all_err_types = sorted(set(summary["plain_err"]) | set(summary["kb_err"]))
    total_plain = sum(summary["plain_err"].values())
    total_kb = sum(summary["kb_err"].values())
    for et in all_err_types:
        p = summary["plain_err"].get(et, 0)
        k = summary["kb_err"].get(et, 0)
        red = f"{(1-k/p)*100:.0f}%" if p > 0 else "N/A"
        print(f"{et:<25} {p:>8} {k:>8} {red:>12}")
    if total_plain > 0:
        print(f"{'TOTAL':<25} {total_plain:>8} {total_kb:>8} {(1-total_kb/total_plain)*100:.0f}%")
    print()

    print("Top topics by sample count:")
    print(f"{'Topic':<40} {'N':>4} {'Plain':>7} {'KB':>7} {'P-CuEA':>7} {'K-CuEA':>7}")
    print("-" * 80)
    sorted_topics = sorted(summary["topic_stats"].items(), key=lambda x: -x[1]["n"])
    for topic, stats in sorted_topics[:15]:
        n = stats["n"]
        pc = avg(stats["plain_chrf"])
        kc = avg(stats["kb_chrf"])
        pcu = avg(stats["plain_cuea"]) if stats["plain_cuea"] else None
        kcu = avg(stats["kb_cuea"]) if stats["kb_cuea"] else None
        pcu_s = f"{pcu:.2f}" if pcu is not None else "—"
        kcu_s = f"{kcu:.2f}" if kcu is not None else "—"
        print(f"{topic[:38]:<38} {n:>4} {pc:>7.2f} {kc:>7.2f} {pcu_s:>7} {kcu_s:>7}")


if __name__ == "__main__":
    merged, provenance = merge_rows()
    rows = list(merged.values())
    summary = summarize(rows)
    print_report(summary)
