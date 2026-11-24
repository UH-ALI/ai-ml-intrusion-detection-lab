"""Config-driven experiment runner: one results file per (model, seed)."""

import time
from pathlib import Path

import yaml
from sklearn.model_selection import train_test_split

from idslab.columns import BASELINE_FEATURES_CIC, CANONICAL_FEATURES
from idslab.data import balance_binary, cap_families, load_dataset, make_synthetic
from idslab.metrics import compute_metrics
from idslab.models import make_pipeline, malicious_scores
from idslab.results import run_metadata, save_result

FEATURE_SETS = {"baseline_cic": BASELINE_FEATURES_CIC, "all": CANONICAL_FEATURES}


def load_split(spec):
    if spec["source"] == "synthetic":
        return make_synthetic(spec["n_rows"], spec.get("domain", "source"), spec.get("seed", 0))
    if spec["source"] == "parquet":
        return load_dataset(spec["path"], sample_frac=spec.get("sample_frac"),
                            seed=spec.get("load_seed", 0))
    raise ValueError(f"unknown data source {spec['source']!r}")


def prepare(df, steps, seed):
    """Apply the sampling steps in a fixed order: cap -> balance -> frac."""
    steps = steps or {}
    if steps.get("cap_families"):
        df = cap_families(df, steps["cap_families"], seed)
    if steps.get("balance"):
        df = balance_binary(df, seed)
    if steps.get("frac"):
        df = df.sample(frac=steps["frac"], random_state=seed)
    return df.reset_index(drop=True)


def evaluate(pipeline, df, features):
    X = df[features]
    start = time.process_time()
    pred = pipeline.predict(X)
    seconds = time.process_time() - start
    metrics = compute_metrics(df["label_binary"], pred, malicious_scores(pipeline, X),
                              df["label_family"])
    metrics["predict_cpu_seconds"] = seconds
    return metrics


def run(config_path):
    config = yaml.safe_load(Path(config_path).read_text())
    features = config["features"]
    features = FEATURE_SETS.get(features, features) if isinstance(features, str) else features
    out_dir = Path(config["output_dir"])
    meta = run_metadata()

    train_all = load_split(config["data"]["train"])
    test_all = load_split(config["data"]["test"]) if "test" in config["data"] else None

    for seed in config["seeds"]:
        train = prepare(train_all, config.get("prepare", {}).get("train"), seed)
        train, holdout = train_test_split(
            train, test_size=config.get("in_domain_test_size", 0.3),
            stratify=train["label_binary"], random_state=seed)
        test = prepare(test_all, config.get("prepare", {}).get("test"), seed) \
            if test_all is not None else None

        for model in config["models"]:
            pipeline = make_pipeline(model, seed, scaler=config.get("scaler", "standard"),
                                     log1p=config.get("log1p", False),
                                     params=config.get("model_params", {}).get(model))
            start = time.process_time()
            pipeline.fit(train[features], train["label_binary"])
            fit_seconds = time.process_time() - start

            result = {
                "experiment": config["name"], "model": model, "seed": seed,
                "config": config, "features": features,
                "n_train": len(train), "fit_cpu_seconds": fit_seconds,
                "in_domain": evaluate(pipeline, holdout, features),
                **meta,
            }
            if test is not None:
                result["cross_domain"] = evaluate(pipeline, test, features)
            save_result(out_dir / model / f"seed{seed}.json", result)
            cross = result.get("cross_domain", {})
            print(f"seed {seed} {model:13s} in-domain acc {result['in_domain']['accuracy']:.4f}"
                  + (f"  cross-domain acc {cross['accuracy']:.4f} mcc {cross['mcc']:.4f}"
                     if cross else ""))
