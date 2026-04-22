import json
from pathlib import Path
import numpy as np
import pandas as pd

CONFS = ["iclr2024", "iclr2025", "iclr2026", "icml2025", "neurips2025"]
CONF_DIR = {
    "iclr2024":    "ICLR2024",
    "iclr2025":    "ICLR2025",
    "iclr2026":    "ICLR2026",
    "icml2025":    "ICML2025",
    "neurips2025": "NEURLPS2025",
}
HUMAN_CONSTR = {
    "iclr2024":    "human_iclr2024",
    "iclr2025":    "human_iclr2025",
    "iclr2026":    "human_iclr2026",
    "icml2025":    "human_icml2025",
    "neurips2025": "human_neurilps2025",
}

ROOT = Path("Final Metric Data")

dec = {}
for conf in CONFS:
    fp = ROOT / "Human" / "Constructiveness" / HUMAN_CONSTR[conf] / "all_results_lite.jsonl"
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            d = (obj.get("metadata", {}).get("decision") or "")
            dec[(conf, obj["paper_id"])] = "Accept" if d.lower().startswith("accept") else "Reject"

rows = []
for conf in CONFS:
    fp = ROOT / "Reviewer2" / CONF_DIR[conf] / "Flaw" / f"reviewer2_{conf}" / "all_papers_results.jsonl"
    if not fp.exists():
        continue
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            mr = (obj.get("metrics_report") or {}).get("cfi") or {}
            gt = mr.get("Ground_Truth_Summary") or {}
            rows.append({
                "conference": conf,
                "paper_id": obj.get("paper_id"),
                "decision": dec.get((conf, obj["paper_id"])),
                "GT_Total_Valid_Flaws": gt.get("Total_Valid_Flaws"),
                "GT_Critical_Flaws":    gt.get("Total_Critical_Flaws"),
                "GT_Minor_Flaws":       gt.get("Total_Minor_Flaws"),
            })

df = pd.DataFrame(rows).dropna(subset=["decision"])
for c in ["GT_Total_Valid_Flaws", "GT_Critical_Flaws", "GT_Minor_Flaws"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")


def cohen_d(a, r):
    a = np.asarray(a, dtype=float); r = np.asarray(r, dtype=float)
    a = a[~np.isnan(a)]; r = r[~np.isnan(r)]
    na, nr = len(a), len(r)
    if na < 2 or nr < 2:
        return float("nan")
    sa, sr = a.std(ddof=1), r.std(ddof=1)
    sp = (((na-1)*sa*sa + (nr-1)*sr*sr)/(na+nr-2))**0.5
    return (a.mean() - r.mean()) / sp if sp > 0 else float("nan")


print("=== Ground-truth flaw counts per decision (GT = consensus issues) ===")
for c in ["GT_Total_Valid_Flaws", "GT_Critical_Flaws", "GT_Minor_Flaws"]:
    a = df.loc[df.decision == "Accept", c]
    r = df.loc[df.decision == "Reject", c]
    print(f"{c}:  Accept mean={a.mean():.2f}  Reject mean={r.mean():.2f}  "
          f"delta(Rej-Acc)={r.mean()-a.mean():+.2f}  d={cohen_d(a, r):+.3f}  "
          f"n=({a.count()},{r.count()})")

print()
print("Per-conference GT_Total_Valid_Flaws:")
for conf in CONFS:
    sub = df[df.conference == conf]
    a = sub.loc[sub.decision == "Accept", "GT_Total_Valid_Flaws"]
    r = sub.loc[sub.decision == "Reject", "GT_Total_Valid_Flaws"]
    if a.count() and r.count():
        print(f"  {conf}: A={a.mean():.2f} R={r.mean():.2f} d={cohen_d(a, r):+.3f}")
