import numpy as np
import pytest

from idslab.metrics import compute_metrics, mean_ci, precision_at_prevalence


def labels_from_confusion(tn, fp, fn, tp):
    y_true = np.array([0] * (tn + fp) + [1] * (fn + tp))
    y_pred = np.array([0] * tn + [1] * fp + [0] * fn + [1] * tp)
    return y_true, y_pred


def test_reproduces_baseline_table5_decision_tree():
    # Chua & Salam's decision tree on CSE-CIC-IDS2018 (rows = true label).
    y_true, y_pred = labels_from_confusion(tn=24956, fp=879, fn=20044, tp=5679)
    m = compute_metrics(y_true, y_pred)
    assert m["n"] == 51558
    assert m["accuracy"] == pytest.approx(0.5942, abs=5e-5)
    assert m["precision_benign"] == pytest.approx(0.5546, abs=5e-5)
    assert m["recall_benign"] == pytest.approx(0.9660, abs=5e-5)
    assert m["precision_malicious"] == pytest.approx(0.8660, abs=5e-5)
    assert m["recall_malicious"] == pytest.approx(0.2208, abs=5e-5)
    assert m["confusion_matrix"] == [[24956, 879], [20044, 5679]]


def test_family_recall_and_auc():
    y_true = np.array([0, 0, 1, 1, 1])
    y_pred = np.array([0, 1, 1, 0, 1])
    scores = np.array([0.1, 0.6, 0.9, 0.4, 0.8])
    fams = np.array(["benign", "benign", "bot", "bot", "ddos_hoic"])
    m = compute_metrics(y_true, y_pred, scores, fams)
    assert m["recall_by_family"] == {"bot": 0.5, "ddos_hoic": 1.0}
    assert m["fpr"] == 0.5
    assert 0 <= m["roc_auc"] <= 1


def test_precision_at_prevalence():
    # A detector with 90% recall and 1% false positives, when 1% of traffic is
    # attacks, is right only about half the time it alerts.
    assert precision_at_prevalence(0.9, 0.01, 0.01) == pytest.approx(0.476, abs=1e-3)


def test_mean_ci():
    mean, half = mean_ci([0.5, 0.6, 0.7])
    assert mean == pytest.approx(0.6)
    assert half == pytest.approx(0.2484, abs=1e-3)
    assert np.isnan(mean_ci([0.5])[1])
