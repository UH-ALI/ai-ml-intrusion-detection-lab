# Data log

Where each dataset comes from, what we checked, and the row counts our build
produced. Update this file whenever a dataset is (re)built. Row counts come
from `build_log.json`, written by `scripts/build_parquet.py`.

## Sources

| Dataset | Where to get it | Status (checked 2026-11-24) |
|---------|-----------------|-----------------------------|
| CIC-IDS2017 (MachineLearningCVE, 8 CSVs) | unb.ca/cic/datasets/ids-2017.html (form), or a Kaggle mirror | UNB site not reachable from our cloud container; check from a browser. Expected total: **2,830,743 rows** |
| CSE-CIC-IDS2018 (10 CSVs, ~6.9 GB) | `s3://cse-cic-ids2018/Processed Traffic Data for ML Algorithms/` (public; also over HTTPS at cse-cic-ids2018.s3.ca-central-1.amazonaws.com), or a Kaggle mirror | ✅ Reachable. File list and sizes below. One day built and checked |
| Corrected CIC-IDS2017 / CSE-CIC-IDS2018 (DistriNet, KU Leuven) | intrusion-detection.distrinet-research.be (documentation, e.g. `/CNS2022/CSECICIDS2018.html`); downloads.distrinet-research.be/WTMC2021 (2017); Kaggle mirrors by `dhoogla`: "Distrinet-CIC-IDS2017" and "UNSW-Distrinet-CSE-CIC-IDS2018" | ✅ Still published (documentation page live, Kaggle mirrors exist). Per DistriNet, only `Friday-02-03-2018.csv` changed in the 2018 fix. Not yet downloaded |
| LUFlow | github.com/ruzzzzz/LUFlow, or a Kaggle mirror | Not checked yet (GitHub blocked from our container) |
| NetFlow v3 (NF-CSE-CIC-IDS2018-v3, NF-UNSW-NB15-v3, NF-ToN-IoT-v3) | staff.itee.uq.edu.au/marius/NIDS_datasets/ | Not reachable from our container; check from a browser |
| CICIoT2023 | unb.ca/cic/datasets/iotdataset-2023.html, or a Kaggle mirror | Not checked yet. **Open question for Week 1:** do the CSVs have a timestamp column? (Decides the Step 5i split.) |

**Kaggle mirrors:** before using one, compare its row counts with the
official numbers above. Some mirrors are pre-cleaned or subsampled.

### CSE-CIC-IDS2018 files (from the S3 listing)

| File | Size (bytes) | Notes |
|------|-------------:|-------|
| Wednesday-14-02-2018 | 358,223,333 | |
| Thursday-15-02-2018 | 375,945,899 | |
| Friday-16-02-2018 | 333,723,605 | |
| Thuesday-20-02-2018 | 4,054,925,350 | 84 columns: extra `Flow ID`, `Src IP`, `Src Port`, `Dst IP` (dropped by the build) |
| Wednesday-21-02-2018 | 328,893,673 | |
| Thursday-22-02-2018 | 382,636,202 | |
| Friday-23-02-2018 | 382,840,456 | |
| Wednesday-28-02-2018 | 209,249,758 | |
| Thursday-01-03-2018 | 107,842,858 | Built and checked, see below |
| Friday-02-03-2018 | 352,368,373 | The one file changed in DistriNet's corrected version |

## Build results

### CSE-CIC-IDS2018 · Thursday-01-03-2018 (test build, 2026-11-24)

| Step | Rows |
|------|-----:|
| Raw lines in CSV (excluding the first header) | 331,125 |
| Repeated header rows removed | 25 |
| Rows with NaN or ±inf removed | 2,919 |
| Written to Parquet | 328,181 (Benign 235,778; Infilteration 92,403) |
| After duplicate removal at load | 288,027 (benign 205,496; infiltration 82,531) |

Observations worth remembering:

- `Max Packet Length` reaches 65,160 bytes, far above the 1,500-byte Ethernet
  MTU. This is a capture artifact (offloading merged packets before
  CICFlowMeter saw them). Keep it in mind for Step 6, where padding is capped
  per packet.
- `Init_Win_bytes_forward` / `_backward` use -1 for "not observed".
- `protocol` takes values 0, 6 (TCP) and 17 (UDP). It is kept as metadata only,
  because CIC-IDS2017's MachineLearningCVE files have no protocol column.

### Full builds (fill in during Week 1)

| Dataset | Files | Rows written | After dedup | Matches expected? | Built by / date |
|---------|------:|-------------:|------------:|-------------------|-----------------|
| CIC-IDS2017 | 8 | | | expected 2,830,743 raw | |
| CSE-CIC-IDS2018 | 10 | | | | |
| LUFlow 2020-07 / 2021-01 | | | | | |
| Corrected CIC-IDS2017 | | | | | |
| Corrected CSE-CIC-IDS2018 | | | | | |
| NetFlow v3 (3 datasets) | | | | | |
| CICIoT2023 | | | | | |

The build script currently handles the two CIC datasets. LUFlow, NetFlow v3,
CICIoT2023 and the corrected CIC versions each need their own cleaning step,
added when they are first used.
