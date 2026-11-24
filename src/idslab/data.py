"""Cleaning raw CIC CSVs into Parquet, loading them back, and sampling."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from idslab.columns import (
    CANONICAL_FEATURES,
    CIC_DROP_COLUMNS,
    CIC_META_COLUMNS,
    CSE2018_TO_CANONICAL,
    label_family,
)

DATASETS = ("cic2017", "cse2018")
META_COLUMNS = ["label", "label_family", "label_binary", "source_file",
                "row_in_file", "protocol", "timestamp"]

# Features stay float64 on disk so exact-duplicate removal matches the raw
# data; load_dataset() downcasts to float32 after deduplication.
PARQUET_SCHEMA = pa.schema(
    [(name, pa.float64()) for name in CANONICAL_FEATURES]
    + [
        ("label", pa.string()),
        ("label_family", pa.string()),
        ("label_binary", pa.int8()),
        ("source_file", pa.string()),
        ("row_in_file", pa.int64()),
        ("protocol", pa.float64()),
        ("timestamp", pa.string()),
    ]
)


def clean_chunk(df, dataset, source_file, row_offset=0):
    """Clean one chunk of a raw CIC CSV. Returns (clean_df, stats)."""
    if dataset not in DATASETS:
        raise ValueError(f"dataset must be one of {DATASETS}")
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df["row_in_file"] = np.arange(row_offset, row_offset + len(df), dtype=np.int64)
    stats = {"rows_raw": len(df)}

    # CSE-CIC-IDS2018 files repeat their header row inside the data.
    is_header = df["Label"].astype(str).str.strip() == "Label"
    stats["header_rows_dropped"] = int(is_header.sum())
    df = df.loc[~is_header]

    df = df.drop(columns=[c for c in CIC_DROP_COLUMNS if c in df.columns])
    if dataset == "cse2018":
        df = df.rename(columns=CSE2018_TO_CANONICAL)
    df = df.rename(columns=CIC_META_COLUMNS)

    expected = set(CANONICAL_FEATURES) | {"Label", "row_in_file"} | set(CIC_META_COLUMNS.values())
    missing = [c for c in CANONICAL_FEATURES if c not in df.columns]
    unexpected = [c for c in df.columns if c not in expected]
    if missing or unexpected:
        raise ValueError(f"{source_file}: missing {missing}, unexpected {unexpected}")

    features = df[CANONICAL_FEATURES].apply(pd.to_numeric, errors="coerce")
    features = features.replace([np.inf, -np.inf], np.nan)
    bad = features.isna().any(axis=1)
    stats["nan_inf_rows_dropped"] = int(bad.sum())

    out = features.loc[~bad].astype(np.float64)
    kept = df.loc[~bad]
    out["label"] = kept["Label"].astype(str).str.strip()
    out["label_family"] = out["label"].map(label_family)
    out["label_binary"] = (out["label_family"] != "benign").astype(np.int8)
    out["source_file"] = source_file
    out["row_in_file"] = kept["row_in_file"].to_numpy()
    out["protocol"] = (pd.to_numeric(kept["protocol"], errors="coerce")
                       if "protocol" in kept else np.nan)
    out["timestamp"] = kept["timestamp"].astype(str) if "timestamp" in kept else None
    stats["rows_written"] = len(out)
    return out.reset_index(drop=True), stats


def build_parquet(raw_dir, out_dir, dataset, chunksize=1_000_000):
    """Convert every CSV in raw_dir to one Parquet file each, chunk by chunk.

    Writes out_dir/build_log.json with per-file row counts and label counts,
    adding to the log of any earlier build into the same folder.
    """
    raw_dir, out_dir = Path(raw_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "build_log.json"
    # Builds can be run one file at a time into the same folder; keep the log
    # entries for files built earlier.
    log = json.loads(log_path.read_text()) if log_path.exists() else {"dataset": dataset, "files": {}}
    if log["dataset"] != dataset:
        raise ValueError(f"{out_dir} already holds {log['dataset']} data")
    for path in sorted(raw_dir.glob("*.csv")):
        totals = {"rows_raw": 0, "header_rows_dropped": 0,
                  "nan_inf_rows_dropped": 0, "rows_written": 0}
        labels = {}
        offset = 0
        with pq.ParquetWriter(out_dir / f"{path.stem}.parquet", PARQUET_SCHEMA) as writer:
            for chunk in pd.read_csv(path, chunksize=chunksize, encoding="latin-1",
                                     low_memory=False):
                clean, stats = clean_chunk(chunk, dataset, path.name, offset)
                offset += len(chunk)
                for key, value in stats.items():
                    totals[key] += value
                for label, count in clean["label"].value_counts().items():
                    labels[label] = labels.get(label, 0) + int(count)
                writer.write_table(pa.Table.from_pandas(clean, schema=PARQUET_SCHEMA,
                                                        preserve_index=False))
        log["files"][path.name] = {**totals, "labels": labels}
        print(f"{path.name}: {totals['rows_written']:,} rows written")
    log_path.write_text(json.dumps(log, indent=2))
    return log


def load_dataset(parquet_dir, sample_frac=None, seed=0, dedup=True, downcast=True):
    """Load a built dataset. Optionally sample each file first (as the baseline
    did with its 10% CSE-CIC-IDS2018 subset), then drop exact duplicates of
    features + label within the whole dataset."""
    frames = []
    for path in sorted(Path(parquet_dir).glob("*.parquet")):
        df = pq.read_table(path).to_pandas()
        if sample_frac is not None:
            df = df.sample(frac=sample_frac, random_state=seed)
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"no .parquet files in {parquet_dir}")
    df = pd.concat(frames, ignore_index=True)
    if dedup:
        df = df.drop_duplicates(subset=CANONICAL_FEATURES + ["label_family"])
    if downcast:
        df[CANONICAL_FEATURES] = df[CANONICAL_FEATURES].astype(np.float32)
    return df.reset_index(drop=True)


def cap_families(df, cap, seed):
    """Downsample every attack family larger than `cap` rows to `cap` rows."""
    parts = []
    for family, group in df.groupby("label_family", sort=True):
        if family != "benign" and len(group) > cap:
            group = group.sample(n=cap, random_state=seed)
        parts.append(group)
    return pd.concat(parts).sort_index()


def balance_binary(df, seed):
    """Downsample benign rows to the number of malicious rows (1:1)."""
    malicious = df[df["label_binary"] == 1]
    benign = df[df["label_binary"] == 0]
    if len(benign) > len(malicious):
        benign = benign.sample(n=len(malicious), random_state=seed)
    return pd.concat([malicious, benign]).sort_index()


def make_synthetic(n_rows, domain="source", seed=0):
    """Small fake CIC-shaped dataset for smoke tests. 'target' is shifted the way
    an environment change would shift it (window sizes, ports, sizes)."""
    rng = np.random.default_rng(seed)
    malicious = rng.random(n_rows) < 0.3
    data = {name: rng.lognormal(3.0, 1.0, n_rows) for name in CANONICAL_FEATURES}
    data["Average Packet Size"] = np.where(malicious, rng.normal(60, 10, n_rows),
                                           rng.normal(300, 80, n_rows)).clip(0)
    data["Bwd Packet Length Std"] = np.where(malicious, rng.normal(20, 5, n_rows),
                                             rng.normal(200, 60, n_rows)).clip(0)
    data["Destination Port"] = np.where(malicious, 80.0, rng.choice([443.0, 53.0, 22.0], n_rows))
    data["Init_Win_bytes_forward"] = np.where(malicious, 29200.0, 8192.0)
    if domain == "target":
        data["Init_Win_bytes_forward"] = np.where(malicious, 26883.0, 65535.0)
        data["Average Packet Size"] = data["Average Packet Size"] * 1.5
    df = pd.DataFrame(data)
    families = rng.choice(["dos_hulk", "ddos_hoic", "bot"], n_rows)
    df["label_family"] = np.where(malicious, families, "benign")
    df["label"] = df["label_family"]
    df["label_binary"] = malicious.astype(np.int8)
    df["source_file"] = f"synthetic_{domain}.csv"
    df["row_in_file"] = np.arange(n_rows)
    df[CANONICAL_FEATURES] = df[CANONICAL_FEATURES].astype(np.float32)
    return df
