from pathlib import Path

import numpy as np
import pandas as pd

from idslab.columns import CANONICAL_FEATURES
from idslab.data import balance_binary, build_parquet, cap_families, clean_chunk, load_dataset

FIXTURES = Path(__file__).parent / "fixtures"


def raw_2018_frame(n=6):
    cols = (FIXTURES / "cse2018_header.csv").read_text().strip().split(",")
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.integers(0, 100, (n, len(cols))).astype(str), columns=cols)
    df["Timestamp"] = "02/03/2018 08:47:38"
    df["Label"] = ["Benign", "Bot", "Benign", "DDOS attack-HOIC", "Benign", "Bot"][:n]
    return df


def test_clean_chunk_drops_header_rows_and_bad_values():
    df = raw_2018_frame()
    header_row = pd.DataFrame([df.columns], columns=df.columns)  # repeated header
    df = pd.concat([df.iloc[:3], header_row, df.iloc[3:]], ignore_index=True)
    df.loc[0, "Flow Byts/s"] = "Infinity"
    df.loc[1, "Flow Pkts/s"] = "NaN"

    clean, stats = clean_chunk(df, "cse2018", "x.csv")

    assert stats == {"rows_raw": 7, "header_rows_dropped": 1,
                     "nan_inf_rows_dropped": 2, "rows_written": 4}
    assert list(clean.columns[:len(CANONICAL_FEATURES)]) == CANONICAL_FEATURES
    assert clean["label_binary"].tolist() == [0, 1, 0, 1]
    assert clean["row_in_file"].tolist() == [2, 4, 5, 6]
    assert clean["timestamp"].notna().all()


def test_clean_chunk_2017_drops_duplicate_header_column():
    cols = (FIXTURES / "cic2017_header.csv").read_text().strip().split(",")
    df = pd.DataFrame(np.ones((2, len(cols))), columns=cols)
    df[" Label"] = ["BENIGN", "Web Attack � XSS"]
    clean, _ = clean_chunk(df, "cic2017", "y.csv")
    assert "Fwd Header Length.1" not in clean.columns
    assert clean["label_family"].tolist() == ["benign", "web_xss"]
    assert clean["protocol"].isna().all()


def test_build_and_load_roundtrip_with_dedup(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    df = raw_2018_frame()
    pd.concat([df, df.iloc[:2]]).to_csv(raw / "day.csv", index=False)  # 2 duplicates

    log = build_parquet(raw, tmp_path / "pq", "cse2018", chunksize=3)
    assert log["files"]["day.csv"]["rows_written"] == 8

    loaded = load_dataset(tmp_path / "pq")
    assert len(loaded) == 6
    assert loaded[CANONICAL_FEATURES].dtypes.eq(np.float32).all()


def test_cap_and_balance():
    df = pd.DataFrame({
        "label_family": ["benign"] * 10 + ["dos_hulk"] * 6 + ["bot"] * 2,
        "label_binary": [0] * 10 + [1] * 8,
    })
    capped = cap_families(df, cap=3, seed=0)
    assert capped["label_family"].value_counts().to_dict() == {"benign": 10, "dos_hulk": 3, "bot": 2}
    balanced = balance_binary(capped, seed=0)
    assert balanced["label_binary"].value_counts().to_dict() == {1: 5, 0: 5}


def test_build_one_file_at_a_time_keeps_earlier_log_entries(tmp_path):
    for name in ("a.csv", "b.csv"):
        raw = tmp_path / f"raw_{name}"
        raw.mkdir()
        raw_2018_frame().to_csv(raw / name, index=False)
        log = build_parquet(raw, tmp_path / "pq", "cse2018")
    assert sorted(log["files"]) == ["a.csv", "b.csv"]
