# AI/ML Intrusion Detection Lab

A reproducibility and robustness study of machine-learning network intrusion
detection (NIDS) under **dataset shift** (CIC-IDS2017 → CSE-CIC-IDS2018) and
**temporal drift** (LUFlow).

## Starting point

This project starts from Chua & Salam (2023),
*Evaluation of Machine Learning Algorithms in Network-Based Intrusion Detection
Using Progressive Dataset*, Symmetry 15(6):1251,
[doi:10.3390/sym15061251](https://doi.org/10.3390/sym15061251). Their code is
public at
[tuanhong3498/Evaluation-of-Machine-Learning-Algorithm-in-Network-Based-Intrusion-Detection-System](https://github.com/tuanhong3498/Evaluation-of-Machine-Learning-Algorithm-in-Network-Based-Intrusion-Detection-System).

Our Information Security course report (DHA Suffa University) used the same
setup: six classic models (DT, RF, SVM, NB, ANN, DNN), trained on CIC-IDS2017
and tested on CSE-CIC-IDS2018, and trained on LUFlow 2020 and tested on LUFlow
2021. In this project we rebuild that pipeline from scratch, test whether its
conclusions hold up, and extend it.

## Research questions

| ID  | Question |
|-----|----------|
| RQ1 | **Reproducibility.** Do the published results reproduce, and how stable are they across random seeds and subsamples? |
| RQ2 | **Attribution.** How much of the CIC-IDS2017 → CSE-CIC-IDS2018 performance drop comes from each of these: attack families never seen in training, known label and feature-extraction errors, environment-specific "shortcut" features, and evaluation choices? |
| RQ3 | **Temporal drift.** Is the reported stability of LUFlow models over time real, or an artifact of shortcut features (e.g. `dest_port`), dropping the `outlier` class, and a two-month window? How quickly does performance decay over the full LUFlow time span? |
| RQ4 | **Methods.** Do modern tabular learners (gradient-boosted trees, tabular deep learning, tabular foundation models) and adaptation strategies (a few labeled target-domain flows, one-class detectors) close the gap, and how much labeled data does that cost? |

## Documents

| Document | What it covers |
|----------|----------------|
| [docs/research-plan.md](docs/research-plan.md) | Phased plan, experiment matrix, evaluation rules, team split, risks |
| [docs/claims-to-test.md](docs/claims-to-test.md) | Every claim we inherited, why it is in doubt, and the experiment that will test it |
| [docs/compute-strategy.md](docs/compute-strategy.md) | How to run this on a laptop plus free Kaggle and Colab |
| [docs/reading-list.md](docs/reading-list.md) | Core literature, grouped by why it matters to this project |

## Status

**Phase 0: setup.** No experiments have been run in this repository yet.
Every number in `docs/` that describes past results comes from the baseline
study's published notebooks and is labeled as such.

## Planned layout

```
docs/          plans and notes
configs/       one YAML file per experiment              (phase 1)
src/idslab/    data loading, features, models, metrics   (phase 1)
notebooks/     thin Kaggle/Colab runners that call src/  (phase 1)
results/       metrics as JSON/CSV; small, committed
figures/       generated from results/ by script, never by hand
data/          raw and processed data; never committed
```
