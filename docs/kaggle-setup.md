# Running on Kaggle

How to build the Parquet files and run experiments on Kaggle. Each block
below is one notebook cell.

## 1. Create the notebook

1. kaggle.com → **Create** → **New Notebook**.
2. In the right panel, under **Session options**:
   - **Accelerator:** None (CPU is enough for everything in Weeks 1–6).
   - **Internet:** On. Kaggle asks you to verify a phone number once before
     it allows internet access.
3. **Add Input** (right panel) → search for and attach the datasets you need,
   e.g. a CIC-IDS2017 mirror and a CSE-CIC-IDS2018 mirror. Attached inputs
   are read-only and don't count against your 20 GB output limit.

## 2. Get our code (pinned to a commit)

```python
!git clone -q -b claude/wizardly-hopper-kljeex https://github.com/UH-ALI/ai-ml-intrusion-detection-lab.git /kaggle/working/lab
%cd /kaggle/working/lab
!pip install -q -e .
!git rev-parse HEAD   # every results file records this commit
```

Kaggle's preinstalled scikit-learn, pandas and LightGBM are fine: each results
file records the versions it actually used.

## 3. Check everything works

```python
!python -m pytest -q
!python scripts/run_experiment.py configs/smoke.yaml
!python scripts/make_tables.py results/smoke
```

The smoke run uses small synthetic data and should take under a minute.

## 4. Build the Parquet files

Find the folder names of your attached inputs first:

```python
!ls /kaggle/input/*
```

Then point the build at the folder that holds the CSVs:

```python
!python scripts/build_parquet.py cic2017 /kaggle/input/<cic2017-folder> /kaggle/working/parquet/cic2017
!python scripts/build_parquet.py cse2018 /kaggle/input/<cse2018-folder> /kaggle/working/parquet/cse2018
```

- The build reads each CSV in 1-million-row chunks, so even the 4 GB
  CSE-CIC-IDS2018 file fits in memory.
- Each dataset folder gets a `build_log.json` with row and label counts.
  Copy those counts into [data-log.md](data-log.md) and compare them with the
  expected totals (CIC-IDS2017: 2,830,743 raw rows).
- Features are stored as float64, so duplicate removal matches the raw data
  exactly. `load_dataset()` removes duplicates and then converts to float32.

**No mirror for CSE-CIC-IDS2018?** Download it straight from the public AWS
bucket, one file at a time, building and deleting as you go to save disk:

```python
import subprocess, urllib.parse, pathlib
base = "https://cse-cic-ids2018.s3.ca-central-1.amazonaws.com/Processed%20Traffic%20Data%20for%20ML%20Algorithms/"
raw = pathlib.Path("/tmp/raw2018"); raw.mkdir(parents=True, exist_ok=True)
for day in ["Wednesday-14-02-2018", "Thursday-15-02-2018", "Friday-16-02-2018",
            "Thuesday-20-02-2018", "Wednesday-21-02-2018", "Thursday-22-02-2018",
            "Friday-23-02-2018", "Wednesday-28-02-2018", "Thursday-01-03-2018",
            "Friday-02-03-2018"]:
    name = f"{day}_TrafficForML_CICFlowMeter.csv"
    subprocess.run(["wget", "-q", "-O", str(raw / name), base + urllib.parse.quote(name)], check=True)
    subprocess.run(["python", "scripts/build_parquet.py", "cse2018", str(raw),
                    "/kaggle/working/parquet/cse2018"], check=True)
    (raw / name).unlink()
```

Each run adds its file to the same `build_log.json`. ("Thuesday" is the
dataset's own spelling.)

## 5. Save the Parquet files as a private Kaggle Dataset

1. Run the notebook with **Save Version → Save & Run All (Commit)**. It keeps
   running after you close the browser.
2. When it finishes, open the version's **Output** section and create a new
   dataset from it. Keep it **Private** and name it e.g. `idslab-parquet`.
3. In the dataset's **Settings → Sharing**, add your teammate as a
   collaborator.
4. From then on, every experiment notebook attaches `idslab-parquet` as an
   input instead of rebuilding.

## 6. Run an experiment

Edit the `path:` lines in the config to point at the attached Parquet
folders, then:

```python
!python scripts/run_experiment.py configs/step1/cic_baseline.yaml
!python scripts/make_tables.py results/step1/cic_baseline
```

Results land in `results/<experiment>/<model>/seed<k>.json`. Download the
`results/` folder and commit it to the repo. The files are small, and they are
the evidence behind every number in the paper.
