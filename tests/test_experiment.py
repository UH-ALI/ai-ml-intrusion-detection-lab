import json

import yaml

from idslab.experiment import run


def test_smoke_run_writes_one_result_per_model_and_seed(tmp_path):
    config = {
        "name": "t", "output_dir": str(tmp_path / "out"), "seeds": [0, 1],
        "data": {"train": {"source": "synthetic", "n_rows": 600, "domain": "source"},
                 "test": {"source": "synthetic", "n_rows": 600, "domain": "target", "seed": 1}},
        "prepare": {"train": {"balance": True}, "test": {"balance": True}},
        "features": "baseline_cic",
        "models": ["dummy", "dt_baseline", "lightgbm"],
    }
    path = tmp_path / "c.yaml"
    path.write_text(yaml.safe_dump(config))
    run(path)

    files = sorted((tmp_path / "out").rglob("seed*.json"))
    assert len(files) == 6
    result = json.loads(files[0].read_text())
    for key in ("in_domain", "cross_domain", "git_commit", "libraries", "n_train"):
        assert key in result
    assert "recall_by_family" in result["cross_domain"]


def test_model_params_override_defaults():
    from idslab.models import make_model
    rf = make_model("rf_baseline", seed=3, params={"n_estimators": 10})
    assert rf.n_estimators == 10 and rf.max_depth == 20 and rf.random_state == 3
