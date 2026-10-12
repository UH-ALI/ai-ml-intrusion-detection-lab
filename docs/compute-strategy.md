# Compute strategy

## Bottom line

- **The core of this project does not need a GPU.** Every model in Phases 1–2,
  plus gradient-boosted trees, runs on CPU. The constraint is **RAM**, not
  GPU.
- **Kaggle is the main workhorse.** CPU sessions have far more RAM than a
  laptop, and the datasets can be attached without downloading anything.
- **Colab is the backup** for short GPU jobs when the Kaggle quota runs out.
- **Your laptop** (8 GB RAM shared with integrated graphics, so no CUDA) is for
  writing code, unit tests, and running on small samples.

## How big the data is

| Dataset | Rows (approx.) | Raw size | Fits in 8 GB laptop RAM? |
|---------|---------------|----------|--------------------------|
| CIC-IDS2017 (MachineLearningCVE CSVs) | 2.83 M flows × 79 columns | ~1 GB CSV | Yes, as float32 Parquet |
| CSE-CIC-IDS2018 (10 daily CSVs) | ~16.2 M flows × 80 columns | ~6.5 GB CSV | **No**, not all at once. Process one file at a time, or use Kaggle |
| LUFlow (daily CSVs) | ~2.5 M rows per month at a 10% sample, so ~25 M per full month | GBs per month | Samples yes; full months, no |
| Corrected CIC-IDS2017 / CSE-CIC-IDS2018 (DistriNet or LycoS) | similar to the originals | similar to the originals | Same as the originals |

**Rule of thumb:** memory ≈ rows × columns × 4 bytes in float32. Double that
for float64, and add 2–3× headroom for pandas operations. Example: all of
CSE-CIC-IDS2018 is 16.2 M × 80 × 4 ≈ 5.2 GB as float32, which is too much for
a laptop. With 20 selected columns it is about 1.3 GB, which is fine anywhere.

## Process once, then reuse Parquet

The most important habit for limited compute: **never re-parse raw CSVs in an
experiment.**

1. In one Kaggle CPU session, read each raw CSV **one file at a time**. For
   each file:
   - fix the column names (strip spaces; map 2017 and 2018 names to one
     scheme);
   - drop repeated header rows, inf and NaN values, and exact duplicates;
   - downcast to float32 or int32;
   - write a Parquet file.
2. Save the output as a **private Kaggle Dataset** (versioned) and add your
   teammate as a collaborator. Every later notebook attaches this dataset and
   loads in seconds.
3. Download only the Parquet files, or a 5% stratified sample, to your laptop
   for development.

```python
# sketch: build step, one raw file at a time
for path in sorted(RAW_DIR.glob("*.csv")):
    df = pd.read_csv(path, low_memory=False)   # on a laptop: chunksize=1_000_000
    df = clean(df)        # names, header rows, inf/NaN, duplicates, float32
    df.to_parquet(OUT_DIR / f"{path.stem}.parquet", index=False)
```

For grouping and joins across many files, **Polars** (`scan_parquet`) or
**DuckDB** can query Parquet without loading it all into RAM.

## What runs where

| Task | Laptop | Kaggle CPU | Kaggle GPU | Colab |
|------|--------|-----------|-----------|-------|
| Writing code, unit tests, 1–5% samples | ✅ | | | |
| Raw CSV → Parquet build | CIC-IDS2017 only | ✅ all datasets | | |
| DT / RF / NB / logistic regression / LightGBM on full training sets | samples | ✅ | | |
| Seed sweeps (5 seeds × all models) | | ✅ (run as a background "commit") | | |
| RBF SVM | ≤ 50k rows | ≤ 100k rows | cuML SVC for larger sets | |
| XGBoost with many hyperparameter trials | | ✅ | ✅ `device="cuda"` | ✅ |
| PyTorch MLP | small | ✅ | ✅ (optional) | ✅ (optional) |
| SHAP: TreeSHAP for trees; KernelSHAP on ≤ 500 rows for SVM/MLP | small | ✅ | | |
| Evasion test (10 queries per attack flow) | small | ✅ | | |

### Model-specific notes

- **SVM.** Kernel SVM training scales between quadratically and cubically
  with the number of rows, so RBF `SVC` on hundreds of thousands of rows is
  impractical on any free machine. The baseline trained its SVM on only 45k
  rows, so we can match that exactly. For larger runs, use either
  `Nystroem` + `LinearSVC`/`SGDClassifier`, or cuML's SVC on a Kaggle GPU.
  Always report the training-set size.
- **Gradient-boosted trees.** LightGBM handles millions of rows on 4 CPU cores
  in minutes. Use `float32` input and `max_bin=255`.
- **Neural networks.** Use PyTorch rather than sklearn's `MLPClassifier`
  (which has no dropout, batch norm or GPU support), with mini-batches loaded
  from Parquet.
- **SHAP.** TreeSHAP is fast for trees and LightGBM. KernelSHAP is slow, so
  explain at most about 500 rows against a background sample of about 100
  rows.

## Platform tips

**Kaggle**
- Limits change. Check your account settings for the current GPU quota and
  session length. Recent reports suggest about 30 GPU-hours a week, sessions
  up to 12 hours, and about 30 GB RAM.
- Use **"Save Version → Save & Run All"** for long jobs. It runs in the
  background after you close the browser, and the files in `/kaggle/working`
  are kept with that version.
- Install our code at a fixed commit so results are traceable:
  `pip install git+https://github.com/UH-ALI/ai-ml-intrusion-detection-lab@<commit>`.
- Write one JSON file per (model, seed) as soon as it finishes. A crash then
  loses one run, not the whole sweep.
- Kaggle mirrors of these datasets are sometimes pre-cleaned or subsampled.
  Before using one, check its row counts against the official numbers
  (CIC-IDS2017: 2,830,743 rows).

**Colab (free)**
- Expect about 12 GB of RAM, a GPU when one is available, and disconnects
  when idle.
- Keep the Parquet files on Google Drive, mount it, and checkpoint often.
- Good for one-off GPU jobs, such as training the PyTorch MLP. Not good for
  data building.

**Laptop**
- Close the browser before big runs.
- Read only the columns you need (`usecols=`) and set `dtype` to float32.
- Never load all of CSE-CIC-IDS2018 at once.
- Integrated graphics cannot run CUDA, so GPU libraries will not help locally.

## Reproducibility checklist for every run

- [ ] Git commit hash, config file, and dataset version saved in the results
      JSON
- [ ] Seed passed to **both** the subsampling and the model (`random_state`)
- [ ] Training and test row counts saved
- [ ] Library versions (`pip freeze`) and hardware (CPU/GPU, RAM) saved
- [ ] Wall-clock time saved separately for training and prediction, with the
      number of rows
