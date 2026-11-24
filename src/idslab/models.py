"""Model registry. `*_baseline` models use Chua & Salam's published settings."""

import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, MinMaxScaler, RobustScaler, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier


def signed_log1p(x):
    """log1p that keeps the sign, so the few negative CIC values (e.g. -1
    window sizes) survive."""
    return np.sign(x) * np.log1p(np.abs(x))


def _lgbm_class():
    from lightgbm import LGBMClassifier
    return LGBMClassifier


# name -> (estimator class, default parameters, whether it takes random_state)
MODELS = {
    "dummy": (lambda: DummyClassifier, dict(strategy="most_frequent"), False),
    "dt_baseline": (lambda: DecisionTreeClassifier,
                    dict(criterion="entropy", ccp_alpha=1.4401469385343852e-05), True),
    "rf_baseline": (lambda: RandomForestClassifier,
                    dict(n_estimators=350, max_depth=20, min_samples_leaf=0.00001,
                         min_samples_split=0.00001, criterion="gini", n_jobs=-1), True),
    "svm_baseline": (lambda: SVC, dict(C=100, gamma=1, kernel="rbf"), False),
    "nb_baseline": (lambda: GaussianNB, dict(var_smoothing=1.0), False),
    "ann_baseline": (lambda: MLPClassifier,
                     dict(hidden_layer_sizes=(50,), activation="tanh", alpha=1e-4,
                          solver="adam", max_iter=1000), True),
    "dnn_baseline": (lambda: MLPClassifier,
                     dict(hidden_layer_sizes=(15, 15, 15), activation="tanh", alpha=1e-5,
                          solver="adam", max_iter=1000), True),
    "logreg": (lambda: LogisticRegression, dict(max_iter=2000), True),
    "lightgbm": (_lgbm_class, dict(n_estimators=300, learning_rate=0.05, num_leaves=63,
                                   verbose=-1), True),
}


def make_model(name, seed, params=None):
    """Build a model; `params` override the defaults."""
    if name not in MODELS:
        raise KeyError(f"unknown model {name!r}; choose from {sorted(MODELS)}")
    get_class, defaults, seeded = MODELS[name]
    kwargs = {**defaults, **(params or {})}
    if seeded:
        kwargs.setdefault("random_state", seed)
    return get_class()(**kwargs)


SCALERS = {
    "none": None,
    "standard": StandardScaler,
    "minmax": MinMaxScaler,
    "robust": RobustScaler,
}


def make_pipeline(model, seed, scaler="standard", log1p=False, params=None):
    """Preprocessing + model in one Pipeline, so everything is fit on training
    data only."""
    steps = []
    if log1p:
        steps.append(("log1p", FunctionTransformer(signed_log1p)))
    if SCALERS[scaler] is not None:
        steps.append(("scaler", SCALERS[scaler]()))
    steps.append(("model", make_model(model, seed, params)))
    return Pipeline(steps)


def malicious_scores(pipeline, X):
    """Continuous score for the malicious class, for AUC metrics."""
    if hasattr(pipeline, "predict_proba"):
        try:
            return pipeline.predict_proba(X)[:, 1]
        except AttributeError:
            pass
    if hasattr(pipeline, "decision_function"):
        return pipeline.decision_function(X)
    return None
