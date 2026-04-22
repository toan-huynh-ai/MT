"""
Phân tích hành vi review của Human vs LLM giữa paper được Accept và Reject.

Nguồn dữ liệu:
- Decision (Accept/Reject): `Final Metric Data/Human/Constructiveness/human_<conf>/all_results_lite.jsonl`
  → trường `metadata.decision`. Tất cả string bắt đầu bằng "Accept" được coi là Accept,
  còn lại là Reject.
- DoA per paper: `Final Metric Data/DoA Result/metrics/<llm>_<conf>_Metrics.csv`
  và `human_<conf>_Metrics.csv`.
- Flaw per paper: `Final Metric Data/<LLM>/<CONF>/Flaw/<llm>_<conf>/all_papers_results.jsonl`
  (mỗi paper có `metrics_report.cfi.Reviewer_Rankings` cho LLM_Reviewer và Human_*).
- Constructiveness per reviewer/paper:
  `Final Metric Data/<LLM>/<CONF>/Constructiveness/<llm>_<conf>/all_results_lite.jsonl`
  và `Final Metric Data/Human/Constructiveness/human_<conf>/all_results_lite.jsonl`.

Output (ghi vào `Final Metric Data/Accept_Reject_Analysis/`):
- `tables/per_paper_master.csv`   : dữ liệu dài (long format) mọi metric
- `tables/summary_by_reviewer_decision.csv`
- `tables/delta_accept_minus_reject.csv`
- `tables/per_conference_summary.csv`
- `figures/*.png`
- `REPORT.md`
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]  # Final Metric Data
OUT = Path(__file__).resolve().parent
OUT_TABLES = OUT / "tables"
OUT_FIGS = OUT / "figures"
OUT_TABLES.mkdir(exist_ok=True)
OUT_FIGS.mkdir(exist_ok=True)

CONFS = ["iclr2024", "iclr2025", "iclr2026", "icml2025", "neurips2025"]
# Human Constructiveness dùng "neurilps" (typo), còn DoA CSV dùng "neurips"
HUMAN_CONSTR_FOLDER = {
    "iclr2024": "human_iclr2024",
    "iclr2025": "human_iclr2025",
    "iclr2026": "human_iclr2026",
    "icml2025": "human_icml2025",
    "neurips2025": "human_neurilps2025",
}
HUMAN_DOA_FILE = {c: f"human_{c}_Metrics.csv" for c in CONFS}

# short_name -> (folder trong Final Metric Data, prefix jsonl folder)
LLMS = {
    "reviewer2":   ("Reviewer2",   "reviewer2"),
    "tree":        ("TreeReview",  "tree"),
    "deepreview":  ("DeepReview",  "deepreview"),
    "sea":         ("SEA",         "sea"),
    "cyclereview": ("CycleReview", "cyclereview"),
}

# Conference → tên folder hoa cho LLM (ICLR2024, NEURLPS2025,...)
CONF_DIR = {
    "iclr2024":   "ICLR2024",
    "iclr2025":   "ICLR2025",
    "iclr2026":   "ICLR2026",
    "icml2025":   "ICML2025",
    "neurips2025": "NEURLPS2025",
}

LLM_LABEL = {
    "reviewer2":   "Reviewer2",
    "tree":        "TreeReview",
    "deepreview":  "DeepReview",
    "sea":         "SEA",
    "cyclereview": "CycleReview",
    "human":       "Human",
}

# ----------------------------------------------------------------------
# 1. Decision mapping
# ----------------------------------------------------------------------
def build_decision_map() -> pd.DataFrame:
    """Return DataFrame with columns: conference, paper_id, decision_raw, decision."""
    rows = []
    for conf in CONFS:
        folder = HUMAN_CONSTR_FOLDER[conf]
        fp = ROOT / "Human" / "Constructiveness" / folder / "all_results_lite.jsonl"
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                dec_raw = obj.get("metadata", {}).get("decision", "") or ""
                dec = "Accept" if dec_raw.lower().startswith("accept") else "Reject"
                rows.append({
                    "conference": conf,
                    "paper_id": obj["paper_id"],
                    "decision_raw": dec_raw,
                    "decision": dec,
                    "avg_rating": obj.get("metadata", {}).get("avg_rating"),
                    "avg_confidence": obj.get("metadata", {}).get("avg_confidence"),
                    "num_reviewers": obj.get("metadata", {}).get("num_reviewers"),
                })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# 2. DoA per paper
# ----------------------------------------------------------------------
def load_doa_per_paper() -> pd.DataFrame:
    """Return long-format DataFrame: paper_id, conference, reviewer_type, metric -> value."""
    metrics_dir = ROOT / "DoA Result" / "metrics"
    rows = []
    # Human
    for conf in CONFS:
        fp = metrics_dir / HUMAN_DOA_FILE[conf]
        if not fp.exists():
            print(f"[WARN] Missing human DoA CSV: {fp}")
            continue
        df = pd.read_csv(fp)
        for _, r in df.iterrows():
            rows.append({
                "conference": conf,
                "paper_id": r["paper_id"],
                "reviewer_type": "human",
                "R_premise": r.get("R_premise"),
                "S_depth": r.get("S_depth"),
                "DoA_score": r.get("DoA_score"),
                "DoA_score_HM": r.get("DoA_score_HM"),
                "Total_Claims": r.get("Total_Claims"),
                "Total_Premises": r.get("Total_Premises"),
            })
    # LLMs
    for short, _ in LLMS.items():
        for conf in CONFS:
            fp = metrics_dir / f"{short}_{conf}_Metrics.csv"
            if not fp.exists():
                # Some LLMs (sea, cyclereview) use "neurlps2025" instead of "neurips2025"
                if conf == "neurips2025":
                    alt = metrics_dir / f"{short}_neurlps2025_Metrics.csv"
                    if alt.exists():
                        fp = alt
                if not fp.exists():
                    print(f"[WARN] Missing LLM DoA CSV: {fp}")
                    continue
            df = pd.read_csv(fp)
            for _, r in df.iterrows():
                rows.append({
                    "conference": conf,
                    "paper_id": r["paper_id"],
                    "reviewer_type": short,
                    "R_premise": r.get("R_premise"),
                    "S_depth": r.get("S_depth"),
                    "DoA_score": r.get("DoA_score"),
                    "DoA_score_HM": r.get("DoA_score_HM"),
                    "Total_Claims": r.get("Total_Claims"),
                    "Total_Premises": r.get("Total_Premises"),
                })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# 3. Flaw per paper
# ----------------------------------------------------------------------
FLAW_METRIC_KEYS = [
    "Total_Valid_Flaws_Found",
    "Critical_Recall",
    "Minor_Recall",
    "Critical_Recall_ConsensusWeighted",
    "Minor_Recall_ConsensusWeighted",
]
CPS_METRIC_KEYS = ["Raw_CPS", "ICPS", "nCPS", "Total_Arguments"]

def parse_flaw_jsonl(fp: Path, conference: str, llm_short: str) -> list[dict]:
    rows = []
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            pid = obj.get("paper_id")
            mr = obj.get("metrics_report") or {}
            cfi = mr.get("cfi") or {}
            cps = mr.get("cps") or {}
            cfi_rankings = {d["Reviewer_ID"]: d for d in cfi.get("Reviewer_Rankings", [])}
            cps_rankings = {d["Reviewer_ID"]: d for d in cps.get("Reviewer_Rankings", [])}
            all_ids = set(cfi_rankings) | set(cps_rankings)
            for rid in all_ids:
                # Each Flaw jsonl file is tied to a specific LLM context,
                # so LLM_Reviewer ↔ that LLM; Human_k ↔ human.
                if rid == "LLM_Reviewer":
                    rtype = llm_short
                elif rid.startswith("Human"):
                    rtype = "human"
                else:
                    continue
                row = {
                    "conference": conference,
                    "paper_id": pid,
                    "reviewer_type": rtype,
                    "reviewer_raw_id": rid,
                    "llm_context": llm_short,
                }
                rank_cfi = cfi_rankings.get(rid, {})
                rank_cps = cps_rankings.get(rid, {})
                for k in FLAW_METRIC_KEYS:
                    row[k] = rank_cfi.get(k)
                for k in CPS_METRIC_KEYS:
                    row[k] = rank_cps.get(k)
                rows.append(row)
    return rows


def load_flaw_per_paper() -> pd.DataFrame:
    rows = []
    for short, (llm_dir, prefix) in LLMS.items():
        for conf in CONFS:
            fp = ROOT / llm_dir / CONF_DIR[conf] / "Flaw" / f"{prefix}_{conf}" / "all_papers_results.jsonl"
            if not fp.exists():
                print(f"[WARN] Missing flaw jsonl: {fp}")
                continue
            rows.extend(parse_flaw_jsonl(fp, conf, short))
    df = pd.DataFrame(rows)
    # Aggregate per (conf, paper_id, reviewer_type, llm_context) across Human_1..6
    # → take mean over human reviewers (per paper per llm_context).
    # Keep separate rows per (paper, reviewer_type, llm_context) → but there
    # are many Human_i; we compute their mean here so each human has 1 row per
    # (conf, paper, llm_context).
    agg_cols = FLAW_METRIC_KEYS + CPS_METRIC_KEYS
    for c in agg_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = (
        df.groupby(["conference", "paper_id", "reviewer_type", "llm_context"], as_index=False)[agg_cols]
          .mean()
    )
    return df


# ----------------------------------------------------------------------
# 4. Constructiveness per paper (one row per reviewer per paper)
# ----------------------------------------------------------------------
CONSTR_METRICS = [
    "MCS", "AR", "SD", "CD",
    "D1_actionability_mean", "D2_specificity_mean", "D3_justification_mean",
    "D4_solution_mean", "D5_tone_mean",
    "n_arcs", "n_weaknesses", "n_strengths", "n_questions", "n_suggestions",
]

def parse_constructiveness_jsonl(fp: Path, conference: str, reviewer_type_for_llm: str, is_human: bool) -> list[dict]:
    """Human jsonl: per-paper object with `reviewers` list (Human_1..Human_k).
    LLM jsonl: per-paper object is itself a single reviewer (flat schema:
    top-level `reviewer_id`, `metrics`, ...)."""
    rows = []
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            pid = obj.get("paper_id")
            if is_human:
                for rv in obj.get("reviewers", []):
                    rid = rv.get("reviewer_id", "")
                    if not rid.startswith("Human"):
                        continue
                    metrics = rv.get("metrics", {}) or {}
                    row = {
                        "conference": conference,
                        "paper_id": pid,
                        "reviewer_type": "human",
                        "reviewer_raw_id": rid,
                    }
                    for k in CONSTR_METRICS:
                        row[k] = metrics.get(k)
                    rows.append(row)
            else:
                metrics = obj.get("metrics", {}) or {}
                row = {
                    "conference": conference,
                    "paper_id": pid,
                    "reviewer_type": reviewer_type_for_llm,
                    "reviewer_raw_id": obj.get("reviewer_id", ""),
                }
                for k in CONSTR_METRICS:
                    row[k] = metrics.get(k)
                rows.append(row)
    return rows


def load_constructiveness_per_paper() -> pd.DataFrame:
    rows = []
    for conf in CONFS:
        fp = ROOT / "Human" / "Constructiveness" / HUMAN_CONSTR_FOLDER[conf] / "all_results_lite.jsonl"
        rows.extend(parse_constructiveness_jsonl(fp, conf, "human", is_human=True))
    for short, (llm_dir, prefix) in LLMS.items():
        for conf in CONFS:
            base = ROOT / llm_dir / CONF_DIR[conf] / "Constructiveness" / f"{prefix}_{conf}"
            fp = base / "all_results_lite.jsonl"
            if not fp.exists():
                alt = base / "all_results_lite_200.jsonl"
                if alt.exists():
                    fp = alt
                else:
                    print(f"[WARN] Missing constructiveness jsonl: {fp}")
                    continue
            rows.extend(parse_constructiveness_jsonl(fp, conf, short, is_human=False))
    df = pd.DataFrame(rows)
    for c in CONSTR_METRICS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Average across Human_1..Human_k per (conf, paper, reviewer_type)
    df = (
        df.groupby(["conference", "paper_id", "reviewer_type"], as_index=False)[CONSTR_METRICS]
          .mean()
    )
    return df


# ----------------------------------------------------------------------
# 5. Build master per-paper long table
# ----------------------------------------------------------------------
def build_master(dec: pd.DataFrame, doa: pd.DataFrame, flaw: pd.DataFrame, constr: pd.DataFrame) -> pd.DataFrame:
    # Flaw: each human row was computed per llm_context. We want a single human
    # flaw row per (conf,paper). Average across llm_contexts for human to remove
    # dependency on which LLM the GT-flaw set came from.
    flaw_human = (
        flaw[flaw["reviewer_type"] == "human"]
        .groupby(["conference", "paper_id", "reviewer_type"], as_index=False)[FLAW_METRIC_KEYS + CPS_METRIC_KEYS]
        .mean()
    )
    flaw_llm = flaw[flaw["reviewer_type"] != "human"].drop(columns=["llm_context"])
    flaw_agg = pd.concat([flaw_human, flaw_llm], ignore_index=True)

    # Merge DoA + Flaw + Constr on (conf, paper, reviewer_type)
    m = doa.merge(flaw_agg, on=["conference", "paper_id", "reviewer_type"], how="outer")
    m = m.merge(constr, on=["conference", "paper_id", "reviewer_type"], how="outer")
    # Attach decision
    m = m.merge(dec[["conference", "paper_id", "decision", "decision_raw",
                     "avg_rating", "avg_confidence"]],
                on=["conference", "paper_id"], how="left")
    return m


# ----------------------------------------------------------------------
# 6. Summary tables
# ----------------------------------------------------------------------
KEY_METRICS = {
    # (display_name, column, higher_is_more_critical_direction_note)
    "Total_Valid_Flaws_Found": ("Số flaw hợp lệ tìm được", "flaw"),
    "Critical_Recall":         ("Recall với critical flaw",  "flaw"),
    "Minor_Recall":            ("Recall với minor flaw",     "flaw"),
    "nCPS":                    ("nCPS (Critical-weighted)",  "flaw"),
    "Raw_CPS":                 ("Raw Criticism Point Score", "flaw"),
    "Total_Arguments":         ("Số argument phê bình",      "flaw"),
    "R_premise":               ("Tỉ lệ Premise / (Claim+Premise)", "doa"),
    "S_depth":                 ("Structure depth",           "doa"),
    "DoA_score":               ("DoA score",                 "doa"),
    "Total_Claims":            ("Số Claims",                 "doa"),
    "Total_Premises":          ("Số Premises",               "doa"),
    "n_arcs":                  ("Số ARCs (constructiveness)", "constr"),
    "n_weaknesses":            ("Số weaknesses",             "constr"),
    "n_strengths":             ("Số strengths",              "constr"),
    "MCS":                     ("Mean Constructiveness Score", "constr"),
    "AR":                      ("Actionability Ratio",       "constr"),
    "SD":                      ("Solution Density",          "constr"),
    "CD":                      ("Coverage Density",          "constr"),
    "D1_actionability_mean":   ("D1 actionability",          "constr"),
    "D3_justification_mean":   ("D3 justification",          "constr"),
    "D4_solution_mean":        ("D4 solution",               "constr"),
    "D5_tone_mean":            ("D5 tone",                   "constr"),
}

def summarise(master: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for rtype, grp in master.groupby("reviewer_type"):
        for dec, sub in grp.groupby("decision"):
            for metric in KEY_METRICS:
                vals = pd.to_numeric(sub[metric], errors="coerce").dropna()
                if len(vals) == 0:
                    continue
                recs.append({
                    "reviewer_type": rtype,
                    "decision": dec,
                    "metric": metric,
                    "n": len(vals),
                    "mean": vals.mean(),
                    "std": vals.std(ddof=1) if len(vals) > 1 else 0.0,
                    "median": vals.median(),
                })
    return pd.DataFrame(recs)


def summarise_per_conference(master: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for (conf, rtype), grp in master.groupby(["conference", "reviewer_type"]):
        for dec, sub in grp.groupby("decision"):
            for metric in KEY_METRICS:
                vals = pd.to_numeric(sub[metric], errors="coerce").dropna()
                if len(vals) == 0:
                    continue
                recs.append({
                    "conference": conf,
                    "reviewer_type": rtype,
                    "decision": dec,
                    "metric": metric,
                    "n": len(vals),
                    "mean": vals.mean(),
                    "std": vals.std(ddof=1) if len(vals) > 1 else 0.0,
                })
    return pd.DataFrame(recs)


def deltas(summary: pd.DataFrame) -> pd.DataFrame:
    """Return per-(reviewer_type, metric): mean_accept, mean_reject, delta, pct_delta."""
    piv = summary.pivot_table(index=["reviewer_type", "metric"], columns="decision",
                              values="mean").reset_index()
    piv["delta_Accept_minus_Reject"] = piv.get("Accept") - piv.get("Reject")
    piv["pct_delta_vs_Reject"] = (piv["delta_Accept_minus_Reject"] / piv.get("Reject")).replace([np.inf, -np.inf], np.nan)
    # Also include n_accept, n_reject
    n_piv = summary.pivot_table(index=["reviewer_type", "metric"], columns="decision",
                                values="n", aggfunc="sum").reset_index().rename(
        columns={"Accept": "n_Accept", "Reject": "n_Reject"})
    std_piv = summary.pivot_table(index=["reviewer_type", "metric"], columns="decision",
                                  values="std").reset_index().rename(
        columns={"Accept": "std_Accept", "Reject": "std_Reject"})
    res = piv.merge(n_piv, on=["reviewer_type", "metric"]).merge(
        std_piv, on=["reviewer_type", "metric"])
    # Cohen's d (pooled)
    def cohen_d(row):
        ma, mr = row.get("Accept"), row.get("Reject")
        sa, sr = row.get("std_Accept"), row.get("std_Reject")
        na, nr = row.get("n_Accept"), row.get("n_Reject")
        if any(pd.isna([ma, mr, sa, sr, na, nr])) or na < 2 or nr < 2:
            return np.nan
        sp = math.sqrt(((na-1)*sa*sa + (nr-1)*sr*sr) / (na+nr-2))
        return (ma - mr) / sp if sp > 0 else np.nan
    res["cohens_d"] = res.apply(cohen_d, axis=1)
    res = res.rename(columns={"Accept": "mean_Accept", "Reject": "mean_Reject"})
    return res


# ----------------------------------------------------------------------
# 7. Figures
# ----------------------------------------------------------------------
REVIEWER_ORDER = ["human", "reviewer2", "tree", "deepreview", "sea", "cyclereview"]
REVIEWER_COLORS = {
    "human":       "#d62728",
    "reviewer2":   "#1f77b4",
    "tree":        "#2ca02c",
    "deepreview":  "#9467bd",
    "sea":         "#ff7f0e",
    "cyclereview": "#8c564b",
}

def grouped_bar(ax, summary_df, metric: str, ylabel: str):
    sub = summary_df[summary_df["metric"] == metric]
    labels = [LLM_LABEL[r] for r in REVIEWER_ORDER]
    x = np.arange(len(REVIEWER_ORDER))
    w = 0.35
    a_means, a_errs, r_means, r_errs = [], [], [], []
    for r in REVIEWER_ORDER:
        sa = sub[(sub["reviewer_type"] == r) & (sub["decision"] == "Accept")]
        sr = sub[(sub["reviewer_type"] == r) & (sub["decision"] == "Reject")]
        a_means.append(sa["mean"].iloc[0] if len(sa) else np.nan)
        r_means.append(sr["mean"].iloc[0] if len(sr) else np.nan)
        a_errs.append(sa["std"].iloc[0] / math.sqrt(sa["n"].iloc[0]) if len(sa) else 0)
        r_errs.append(sr["std"].iloc[0] / math.sqrt(sr["n"].iloc[0]) if len(sr) else 0)
    b1 = ax.bar(x - w/2, a_means, w, yerr=a_errs, label="Accept", color="#4c9a2a", alpha=0.88, capsize=3)
    b2 = ax.bar(x + w/2, r_means, w, yerr=r_errs, label="Reject", color="#c0392b", alpha=0.88, capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.legend(fontsize=8)


def fig_core_metrics(summary_df: pd.DataFrame, outpath: Path):
    metrics_to_plot = [
        ("Total_Valid_Flaws_Found", "Valid Flaws Found"),
        ("Critical_Recall",         "Critical Recall"),
        ("nCPS",                    "nCPS"),
        ("n_arcs",                  "#ARCs (constructiveness)"),
        ("S_depth",                 "S_depth (DoA)"),
        ("R_premise",               "R_premise (DoA)"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (m, lbl) in zip(axes.flatten(), metrics_to_plot):
        grouped_bar(ax, summary_df, m, lbl)
        ax.set_title(lbl, fontsize=11, weight="bold")
    fig.suptitle("Human vs LLM: Hành vi review theo Decision (Accept vs Reject)", fontsize=14, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def fig_delta_heatmap(delta_df: pd.DataFrame, outpath: Path):
    metrics = ["Total_Valid_Flaws_Found", "Critical_Recall", "Minor_Recall", "nCPS",
               "Raw_CPS", "Total_Arguments",
               "R_premise", "S_depth", "DoA_score",
               "n_arcs", "n_weaknesses", "n_strengths",
               "MCS", "AR", "D1_actionability_mean", "D3_justification_mean",
               "D4_solution_mean"]
    mat = []
    for rtype in REVIEWER_ORDER:
        row = []
        for m in metrics:
            sub = delta_df[(delta_df["reviewer_type"] == rtype) & (delta_df["metric"] == m)]
            if len(sub):
                row.append(sub["delta_Accept_minus_Reject"].iloc[0])
            else:
                row.append(np.nan)
        mat.append(row)
    mat = np.array(mat, dtype=float)
    # Normalize each column to [-1,1] for color comparability
    norm = np.zeros_like(mat)
    for j in range(mat.shape[1]):
        col = mat[:, j]
        mx = np.nanmax(np.abs(col))
        if mx and not np.isnan(mx) and mx > 0:
            norm[:, j] = col / mx
    fig, ax = plt.subplots(figsize=(14, 4.8))
    im = ax.imshow(norm, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(REVIEWER_ORDER)))
    ax.set_yticklabels([LLM_LABEL[r] for r in REVIEWER_ORDER], fontsize=10)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=7, color="black")
    ax.set_title("Δ = mean(Accept) − mean(Reject) \n"
                 "(đỏ = reviewer đánh giá GAY GẮT hơn với Accept, xanh = gay gắt hơn với Reject)",
                 fontsize=12, weight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Δ chuẩn hoá theo cột (|max|=1)")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def fig_cohens_d(delta_df: pd.DataFrame, outpath: Path):
    metrics = ["Total_Valid_Flaws_Found", "Critical_Recall", "Minor_Recall", "nCPS",
               "Raw_CPS", "Total_Arguments",
               "n_arcs", "n_weaknesses",
               "R_premise", "S_depth", "DoA_score",
               "MCS", "AR", "D1_actionability_mean", "D3_justification_mean",
               "D4_solution_mean"]
    mat = []
    for rtype in REVIEWER_ORDER:
        row = []
        for m in metrics:
            sub = delta_df[(delta_df["reviewer_type"] == rtype) & (delta_df["metric"] == m)]
            if len(sub):
                row.append(sub["cohens_d"].iloc[0])
            else:
                row.append(np.nan)
        mat.append(row)
    mat = np.array(mat, dtype=float)
    fig, ax = plt.subplots(figsize=(14, 4.8))
    vmax = np.nanmax(np.abs(mat)) if np.isfinite(np.nanmax(np.abs(mat))) else 1
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(REVIEWER_ORDER)))
    ax.set_yticklabels([LLM_LABEL[r] for r in REVIEWER_ORDER], fontsize=10)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=7, color="black")
    ax.set_title("Cohen's d: Accept − Reject (kích thước hiệu ứng)",
                 fontsize=12, weight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Cohen's d")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def fig_conference_panels(perconf_df: pd.DataFrame, outpath: Path, metric: str, title: str):
    fig, ax = plt.subplots(figsize=(13, 5))
    x_labels = []
    x_pos = []
    cur = 0
    gap = 1.3
    group_w = len(REVIEWER_ORDER) * 2 + 1
    for ci, conf in enumerate(CONFS):
        for ri, rtype in enumerate(REVIEWER_ORDER):
            sub = perconf_df[(perconf_df["conference"] == conf) &
                             (perconf_df["reviewer_type"] == rtype) &
                             (perconf_df["metric"] == metric)]
            for offset, dec, color in [(-0.22, "Accept", "#4c9a2a"), (0.22, "Reject", "#c0392b")]:
                row = sub[sub["decision"] == dec]
                if len(row):
                    ax.bar(cur + ri + offset, row["mean"].iloc[0],
                           width=0.42, color=color,
                           edgecolor=REVIEWER_COLORS[rtype], linewidth=1.3,
                           label=dec if (ci == 0 and ri == 0) else None)
        x_labels.append(conf)
        x_pos.append(cur + (len(REVIEWER_ORDER)-1)/2)
        cur += len(REVIEWER_ORDER) + gap
    ax.set_xticks(x_pos)
    ax.set_xticklabels([c.upper() for c in CONFS], fontsize=10)
    ax.set_ylabel(metric, fontsize=10)
    ax.set_title(title, fontsize=12, weight="bold")
    # Legend for reviewer colors
    from matplotlib.patches import Patch
    legend_items = [Patch(facecolor="#4c9a2a", label="Accept"),
                    Patch(facecolor="#c0392b", label="Reject")]
    legend_items += [Patch(facecolor="white", edgecolor=REVIEWER_COLORS[r],
                           linewidth=2, label=LLM_LABEL[r])
                     for r in REVIEWER_ORDER]
    ax.legend(handles=legend_items, ncol=len(legend_items), loc="upper center",
              bbox_to_anchor=(0.5, -0.08), fontsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_accept_reject_gap_vs_human(delta_df: pd.DataFrame, outpath: Path):
    """Compare delta(Accept-Reject) of each LLM vs Human, for selected metrics."""
    metrics = [("Total_Valid_Flaws_Found", "Valid Flaws"),
               ("Critical_Recall", "Critical Recall"),
               ("nCPS", "nCPS"),
               ("n_arcs", "#ARCs"),
               ("n_weaknesses", "#weaknesses"),
               ("S_depth", "S_depth"),
               ("R_premise", "R_premise"),
               ("D1_actionability_mean", "D1 actionability")]
    fig, axes = plt.subplots(2, 4, figsize=(17, 8))
    for ax, (m, lbl) in zip(axes.flatten(), metrics):
        human_delta = delta_df[(delta_df["reviewer_type"] == "human") &
                               (delta_df["metric"] == m)]
        human_val = human_delta["delta_Accept_minus_Reject"].iloc[0] if len(human_delta) else 0
        llm_rts = [r for r in REVIEWER_ORDER if r != "human"]
        vals = []
        for r in llm_rts:
            sub = delta_df[(delta_df["reviewer_type"] == r) & (delta_df["metric"] == m)]
            vals.append(sub["delta_Accept_minus_Reject"].iloc[0] if len(sub) else np.nan)
        x = np.arange(len(llm_rts))
        ax.bar(x, vals, color=[REVIEWER_COLORS[r] for r in llm_rts], alpha=0.85)
        ax.axhline(human_val, color=REVIEWER_COLORS["human"], linestyle="--", lw=2,
                   label=f"Human Δ = {human_val:+.3f}")
        ax.axhline(0, color="black", lw=0.6)
        ax.set_xticks(x)
        ax.set_xticklabels([LLM_LABEL[r] for r in llm_rts], rotation=20, ha="right", fontsize=8)
        ax.set_title(lbl, fontsize=10, weight="bold")
        ax.set_ylabel("Δ = Accept − Reject", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(axis="y", linestyle=":", alpha=0.4)
    fig.suptitle("So sánh 'độ nhạy' với decision: Δ(Accept−Reject) của LLM vs Human",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


# ----------------------------------------------------------------------
# 8. Report
# ----------------------------------------------------------------------
def write_report(summary: pd.DataFrame, delta: pd.DataFrame, master: pd.DataFrame, outpath: Path):
    n_by_conf = master.groupby(["conference", "decision"])["paper_id"].nunique().unstack(fill_value=0)
    lines = []
    lines.append("# Phân tích hành vi review: Human vs LLM theo Decision (Accept / Reject)\n")
    lines.append("## 1. Dữ liệu\n")
    lines.append("- 5 hội nghị: " + ", ".join(CONFS) + ".")
    lines.append("- Mỗi hội nghị có 200 paper; decision được lấy từ `metadata.decision` trong "
                 "`Human/Constructiveness/*/all_results_lite.jsonl` (mọi giá trị bắt đầu bằng "
                 "\"Accept\" → Accept, còn lại → Reject).")
    lines.append("- 5 LLM baseline: Reviewer2, TreeReview, DeepReview, SEA, CycleReview; "
                 "và Human (trung bình các reviewer Human_1..Human_6).\n")
    lines.append("### Phân phối paper theo decision\n")
    lines.append(n_by_conf.to_markdown())
    lines.append("")

    lines.append("## 2. Bảng tổng hợp (mean ± std, n papers) theo reviewer × decision\n")
    # Key metric table
    pivotable = summary.copy()
    pivotable["mean_str"] = pivotable.apply(
        lambda r: f"{r['mean']:.3f} ± {r['std']:.3f} (n={int(r['n'])})", axis=1)
    focus = ["Total_Valid_Flaws_Found", "Critical_Recall", "Minor_Recall",
             "nCPS", "Raw_CPS", "Total_Arguments",
             "R_premise", "S_depth", "DoA_score",
             "n_arcs", "n_weaknesses", "n_strengths", "MCS", "AR",
             "D1_actionability_mean", "D3_justification_mean", "D4_solution_mean",
             "D5_tone_mean"]
    for m in focus:
        sub = pivotable[pivotable["metric"] == m]
        if sub.empty:
            continue
        piv = sub.pivot_table(index="reviewer_type", columns="decision",
                              values="mean_str", aggfunc="first")
        piv = piv.reindex([r for r in REVIEWER_ORDER if r in piv.index])
        lines.append(f"### {m}")
        lines.append(piv.to_markdown())
        lines.append("")

    lines.append("## 3. Độ nhạy Δ = mean(Accept) − mean(Reject)\n")
    lines.append(
        "Δ>0 ⇒ reviewer cho điểm metric này CAO hơn với paper được accept (và ngược lại). "
        "Ta kỳ vọng human sẽ tìm ÍT flaw hơn & viết NHIỀU điểm mạnh hơn cho paper sẽ accept; "
        "LLM có replicate pattern đó không?\n")
    d_piv = delta.pivot_table(index="metric", columns="reviewer_type",
                              values="delta_Accept_minus_Reject")
    d_piv = d_piv[[r for r in REVIEWER_ORDER if r in d_piv.columns]]
    lines.append(d_piv.loc[focus].round(3).to_markdown())
    lines.append("")

    lines.append("## 4. Cohen's d (kích thước hiệu ứng giữa Accept vs Reject)\n")
    d_piv2 = delta.pivot_table(index="metric", columns="reviewer_type",
                               values="cohens_d")
    d_piv2 = d_piv2[[r for r in REVIEWER_ORDER if r in d_piv2.columns]]
    lines.append(d_piv2.loc[focus].round(3).to_markdown())
    lines.append("")

    # Narrative highlights (computed automatically)
    lines.append("## 5. Điểm chính tự động rút ra\n")

    def comment_line(metric_col: str, higher_is_worse: bool, pretty_name: str) -> str:
        sub = delta[delta["metric"] == metric_col].set_index("reviewer_type")
        if "human" not in sub.index:
            return ""
        h = sub.loc["human", "delta_Accept_minus_Reject"]
        h_d = sub.loc["human", "cohens_d"]
        comment = f"- **{pretty_name}** — Human: Δ = {h:+.3f} (d={h_d:+.2f}). "
        pieces = []
        for r in [x for x in REVIEWER_ORDER if x != "human" and x in sub.index]:
            v = sub.loc[r, "delta_Accept_minus_Reject"]
            d = sub.loc[r, "cohens_d"]
            pieces.append(f"{LLM_LABEL[r]} Δ={v:+.3f} (d={d:+.2f})")
        comment += "; ".join(pieces)
        return comment

    lines.append(comment_line("Total_Valid_Flaws_Found", True, "Số flaw hợp lệ tìm được"))
    lines.append(comment_line("Critical_Recall", True, "Recall với critical flaw"))
    lines.append(comment_line("nCPS", True, "nCPS (điểm phê bình chuẩn hoá)"))
    lines.append(comment_line("n_arcs", False, "Số ARCs"))
    lines.append(comment_line("n_weaknesses", True, "Số weaknesses"))
    lines.append(comment_line("n_strengths", False, "Số strengths"))
    lines.append(comment_line("S_depth", False, "S_depth"))
    lines.append(comment_line("R_premise", False, "R_premise"))
    lines.append(comment_line("D1_actionability_mean", False, "D1 actionability"))
    lines.append(comment_line("MCS", False, "Mean Constructiveness Score"))

    lines.append("\n## 6. Figures")
    lines.append("- `figures/core_metrics_accept_vs_reject.png`")
    lines.append("- `figures/delta_heatmap.png`")
    lines.append("- `figures/cohens_d_heatmap.png`")
    lines.append("- `figures/delta_vs_human.png`")
    lines.append("- `figures/per_conference_<metric>.png`")

    outpath.write_text("\n".join(lines), encoding="utf-8")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    print("Step 1/5: decisions")
    dec = build_decision_map()
    dec.to_csv(OUT_TABLES / "decisions.csv", index=False, encoding="utf-8")
    print(f"  decisions: {len(dec)} rows")

    print("Step 2/5: DoA")
    doa = load_doa_per_paper()
    print(f"  doa: {len(doa)} rows")

    print("Step 3/5: Flaw")
    flaw = load_flaw_per_paper()
    print(f"  flaw: {len(flaw)} rows")

    print("Step 4/5: Constructiveness")
    constr = load_constructiveness_per_paper()
    print(f"  constr: {len(constr)} rows")

    print("Step 5/5: master + summary")
    master = build_master(dec, doa, flaw, constr)
    master.to_csv(OUT_TABLES / "per_paper_master.csv", index=False, encoding="utf-8")

    summary = summarise(master)
    summary.to_csv(OUT_TABLES / "summary_by_reviewer_decision.csv", index=False, encoding="utf-8")

    per_conf = summarise_per_conference(master)
    per_conf.to_csv(OUT_TABLES / "per_conference_summary.csv", index=False, encoding="utf-8")

    delta_df = deltas(summary)
    delta_df.to_csv(OUT_TABLES / "delta_accept_minus_reject.csv", index=False, encoding="utf-8")

    # figures
    fig_core_metrics(summary, OUT_FIGS / "core_metrics_accept_vs_reject.png")
    fig_delta_heatmap(delta_df, OUT_FIGS / "delta_heatmap.png")
    fig_cohens_d(delta_df, OUT_FIGS / "cohens_d_heatmap.png")
    fig_accept_reject_gap_vs_human(delta_df, OUT_FIGS / "delta_vs_human.png")
    for metric, title in [
        ("Total_Valid_Flaws_Found", "Valid Flaws Found — theo hội nghị"),
        ("nCPS", "nCPS — theo hội nghị"),
        ("n_arcs", "#ARCs — theo hội nghị"),
        ("S_depth", "S_depth — theo hội nghị"),
        ("R_premise", "R_premise — theo hội nghị"),
        ("Critical_Recall", "Critical Recall — theo hội nghị"),
    ]:
        fig_conference_panels(per_conf, OUT_FIGS / f"per_conference_{metric}.png",
                              metric, title)

    write_report(summary, delta_df, master, OUT / "REPORT.md")
    print("Done. Output in:", OUT)


if __name__ == "__main__":
    main()
