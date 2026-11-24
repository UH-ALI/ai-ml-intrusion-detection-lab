# AI/ML Intrusion Detection Lab

A reproducibility and robustness study of machine-learning network intrusion
detection (NIDS) under **dataset shift** (CIC-IDS2017 → CSE-CIC-IDS2018),
**temporal drift** (LUFlow) and **realistic evasion attacks**, with checks
on newer data (NetFlow v3, 2025; CICIoT2023).

## Starting point

This project starts from Chua & Salam (2023),
*Evaluation of Machine Learning Algorithms in Network-Based Intrusion Detection
Using Progressive Dataset*, Symmetry 15(6):1251,
[doi:10.3390/sym15061251](https://doi.org/10.3390/sym15061251). Their code is
public at
[tuanhong3498/Evaluation-of-Machine-Learning-Algorithm-in-Network-Based-Intrusion-Detection-System](https://github.com/tuanhong3498/Evaluation-of-Machine-Learning-Algorithm-in-Network-Based-Intrusion-Detection-System).

Our Information Security course report (DHA Suffa University) used the same
setup: six classic models (DT, RF, SVM, NB, ANN, DNN), trained on CIC-IDS2017
and tested on CSE-CIC-IDS2018, and trained on LUFlow (July 2020) and tested on
LUFlow (January 2021). In this project we rebuild that pipeline from scratch,
test whether its conclusions hold up, and extend it with a breakdown of why
models fail and a realistic evasion test.

## Research questions

| ID  | Question |
|-----|----------|
| RQ1 | **Reproducibility.** Do the published results reproduce, and how stable are they across random seeds? |
| RQ2 | **Fair evaluation.** Does the picture change with proper metrics, a realistic test set and modern models (gradient-boosted trees, a PyTorch MLP)? |
| RQ3 | **Breakdown.** How much of the CIC-IDS2017 → CSE-CIC-IDS2018 drop comes from each of these: shortcut features (ports, TCP window sizes), label errors, attack types never seen in training, preprocessing, and evaluation choices? Do the findings hold on newer data: a benchmark released after the baseline (NetFlow v3, 2025) and newer IoT attacks (CICIoT2023)? |
| RQ4 | **Evasion.** How easily can an attacker fool each model by changing only what they control (payload padding, TCP initial window)? |

## Documents

| Document | What it covers |
|----------|----------------|
| [plan.md](plan.md) | **The plan:** every step, how to do it, who does it, and the 10-week timeline |
| [docs/claims-to-test.md](docs/claims-to-test.md) | Every claim we inherited, why it is in doubt, and the experiment that will test it |
| [docs/compute-strategy.md](docs/compute-strategy.md) | How to run this on a laptop plus free Kaggle and Colab |
| [docs/reading-list.md](docs/reading-list.md) | Core literature, grouped by why it matters to this project |

## Status

**Setup (Week 1 of [plan.md](plan.md)).** No experiments have been run in
this repository yet.
Every number in `docs/` that describes past results comes from the baseline
study's published notebooks and is labeled as such.

## Planned layout

```
docs/          plans and notes
configs/       one YAML file per experiment              (Week 1)
src/idslab/    data loading, features, models, metrics   (Week 1)
notebooks/     thin Kaggle/Colab runners that call src/  (Week 1)
scripts/       run_experiment, make_tables, make_figures (Week 1)
results/       metrics as JSON/CSV; small, committed
figures/       generated from results/ by script, never by hand
data/          raw and processed data; never committed
```
