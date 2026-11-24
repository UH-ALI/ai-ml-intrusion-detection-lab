"""Step 2 metrics. The positive class (1) is 'malicious'."""

import numpy as np
from scipy import stats
from sklearn import metrics as skm

PREVALENCES = (0.01, 0.10)


def precision_at_prevalence(tpr, fpr, prevalence):
    """Precision the detector would have if attacks made up `prevalence` of
    traffic: pi*TPR / (pi*TPR + (1-pi)*FPR)."""
    denom = prevalence * tpr + (1 - prevalence) * fpr
    return float(prevalence * tpr / denom) if denom > 0 else float("nan")


def compute_metrics(y_true, y_pred, scores=None, families=None):
    """All Step 2 metrics for one run, as a JSON-ready dict.

    scores: continuous scores for the malicious class (predict_proba[:, 1] or
    decision_function), used for AUC-ROC and PR-AUC.
    families: attack family per row, for recall per family.
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tn, fp, fn, tp = skm.confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    tpr = tp / (tp + fn) if tp + fn else float("nan")
    fpr = fp / (fp + tn) if fp + tn else float("nan")
    prec, rec, f1, _ = skm.precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0)

    out = {
        # rows = true label (benign, malicious), columns = predicted label
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "n": int(len(y_true)),
        "accuracy": float(skm.accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(skm.balanced_accuracy_score(y_true, y_pred)),
        "mcc": float(skm.matthews_corrcoef(y_true, y_pred)),
        "precision_benign": float(prec[0]), "recall_benign": float(rec[0]), "f1_benign": float(f1[0]),
        "precision_malicious": float(prec[1]), "recall_malicious": float(rec[1]),
        "f1_malicious": float(f1[1]),
        "f1_macro": float(np.mean(f1)),
        "fpr": float(fpr),
    }
    for pi in PREVALENCES:
        out[f"precision_at_{pi:g}"] = precision_at_prevalence(tpr, fpr, pi)

    if scores is not None and len(np.unique(y_true)) == 2:
        out["roc_auc"] = float(skm.roc_auc_score(y_true, scores))
        out["pr_auc"] = float(skm.average_precision_score(y_true, scores))

    if families is not None:
        families = np.asarray(families)
        out["recall_by_family"] = {
            str(fam): float(np.mean(y_pred[families == fam] == 1))
            for fam in np.unique(families) if fam != "benign"
        }
    return out


def mean_ci(values, confidence=0.95):
    """Mean and half-width of a t-distribution confidence interval over seeds."""
    values = np.asarray([v for v in values if v is not None and not np.isnan(v)], dtype=float)
    if len(values) == 0:
        return float("nan"), float("nan")
    if len(values) == 1:
        return float(values[0]), float("nan")
    sem = stats.sem(values)
    half = sem * stats.t.ppf((1 + confidence) / 2, len(values) - 1)
    return float(values.mean()), float(half)
