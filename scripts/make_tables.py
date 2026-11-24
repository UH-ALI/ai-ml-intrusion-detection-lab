"""Summarise one experiment's results as mean ± 95% CI over seeds.

    python scripts/make_tables.py results/smoke

Prints a markdown table and writes <results_dir>/summary.csv.
"""

import sys
from pathlib import Path

import pandas as pd

from idslab.metrics import mean_ci
from idslab.results import load_results

METRICS = ["accuracy", "balanced_accuracy", "mcc", "recall_malicious", "fpr",
           "f1_macro", "roc_auc", "pr_auc", "precision_at_0.01"]


def summarise(results_dir):
    rows = []
    results = load_results(results_dir)
    for split in ("in_domain", "cross_domain"):
        for model in sorted({r["model"] for r in results}):
            runs = [r[split] for r in results if r["model"] == model and split in r]
            if not runs:
                continue
            row = {"split": split, "model": model, "seeds": len(runs)}
            for metric in METRICS:
                mean, half = mean_ci([run.get(metric, float("nan")) for run in runs])
                row[metric] = f"{mean:.4f} ± {half:.4f}" if half == half else f"{mean:.4f}"
            rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    table = summarise(sys.argv[1])
    table.to_csv(Path(sys.argv[1]) / "summary.csv", index=False)
    print(table.to_markdown(index=False))
