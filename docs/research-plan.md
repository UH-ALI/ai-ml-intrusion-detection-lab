# Research plan

## 1. Positioning

The baseline study and our course report show that classic ML models score
about 99% within CIC-IDS2017 and drop to 50–76% on CSE-CIC-IDS2018, while
staying near 99% on LUFlow over time. That headline pattern is already known in
the literature (see [reading-list.md](reading-list.md)). So the contribution
here cannot be "cross-dataset evaluation is new". It has to be:

1. **A reproducibility audit** of a specific published study with public code,
   with variance reporting the original lacks.
2. **A controlled decomposition** of the cross-dataset drop into its causes:
   unseen attack families, label noise, shortcut features, and evaluation
   artifacts. Each cause gets its own ablation.
3. **Practical extensions:**
   - how many labeled target-domain flows it takes to recover performance;
   - whether one-class detectors catch the families supervised models miss;
   - how fast LUFlow models decay over the full time span.

Here "better results" means better robustness under shift or better use of
labeled data. In-distribution accuracy on CIC-IDS2017 is already about 99.7%,
so there is no room left there.

## 2. Evaluation rules (fixed before any experiment)

1. Test data is never used for any choice: not features, hyperparameters,
   thresholds, or early stopping.
2. All preprocessing (scalers, encoders, feature selection) is fit on training
   folds only.
3. Every reported number is a mean with a 95% CI over at least 5 seeds; use 10
   seeds for headline numbers. Seeds control subsampling **and** model
   randomness.
4. Metrics, always reported together:
   - balanced accuracy, MCC, macro-F1, PR-AUC;
   - false-positive rate, and recall per attack family;
   - precision recomputed at realistic prevalence (e.g. 1% and 10% attacks).

   Accuracy alone is never reported.
5. Every table includes two reference rows: a **dummy** classifier (constant or
   stratified) and a **one-feature** baseline (destination port only).
6. Test sets keep the natural class distribution unless an experiment is
   explicitly about balancing.
7. Each results file records the git commit, config, dataset version, seed,
   library versions and hardware.
8. Expected outcomes are written in `docs/preregistration.md` **before** each
   phase runs. This prevents tuning the story to the results.

## 3. Phases

The timeline assumes two students working part-time: about 14 weeks.

### Phase 0: Setup and integrity (weeks 1–2)

- [ ] Both team members read the six must-read papers in
      [reading-list.md](reading-list.md).
- [ ] Both read the baseline's 10 notebooks end to end and note anything the
      paper does not say. The table at the bottom of
      [claims-to-test.md](claims-to-test.md) is a head start.
- [ ] Set up Kaggle accounts. Attach the raw datasets and create a private
      Kaggle Dataset for processed Parquet, shared with your teammate. See
      [compute-strategy.md](compute-strategy.md).
- [ ] Create the repo skeleton (`src/idslab`, `configs/`, `results/`) and a
      pinned `requirements.txt`.
- [ ] Write `docs/preregistration.md` for Phase 1 and Phase 2.
- [ ] Agree the team split (§6) and a weekly 30-minute sync. Review each
      other's pull requests.

**Exit criterion:** both of you can explain every claim in
`claims-to-test.md` and how it will be tested.

### Phase 1: Faithful replication (weeks 2–4)

| ID   | What | Output |
|------|------|--------|
| E1.1 | Run the baseline notebooks as-is on Kaggle, with the original library versions if possible | Side-by-side table: published vs re-run |
| E1.2 | Port to a clean pipeline in `src/idslab` with the same settings (sample sizes, features, hyperparameters) | Same numbers within ±1–2 points, or a written explanation of any gap |
| E1.3 | Repeat E1.2 over 10 seeds | Means ± CI. Does the model ranking (SVM > ANN > DNN > RF ≈ DT > NB) survive? |

**Exit criterion:** our pipeline reproduces the baseline's Tables 4, 5, 8 and
9, with variance quantified. This is already a reportable result.

### Phase 2: Stress tests, one variable at a time (weeks 4–7)

| ID   | Manipulation | Tests claim |
|------|--------------|-------------|
| E2.1 | Evaluate on the full CSE-CIC-IDS2018 at its natural class ratio instead of a balanced 1% sample; add the dummy baseline and full metric set | C1, C5 |
| E2.2 | Recall per attack family. Split families into **seen** (DoS Hulk, GoldenEye, Slowloris, SlowHTTPTest, FTP/SSH brute force, web attacks, DDoS-LOIC-HTTP ≈ 2017 "DDoS LOIT"), **partly seen** (Bot: Ares in 2017, Zeus and Ares in 2018), **unseen** (DDoS-HOIC, DDoS-LOIC-UDP) and **label-suspect** (Infiltration); report the drop for each group. Check each mapping against the dataset documentation before relying on it | C1, C2 |
| E2.3 | Remove environment-specific features (`Destination Port`, `Init_Win_bytes_*`; also screen for others with per-feature distribution shift between domains) and compare in-domain vs cross-domain | C1 |
| E2.4 | Nest feature selection inside CV; use folds grouped by capture day or attack window; compare against random K-fold | C7 |
| E2.5 | Repeat E1.3 and E2.2 on the corrected datasets (DistriNet's improved CIC-IDS2017/CSE-CIC-IDS2018, and/or LycoS-IDS2017) | C1 |
| E2.6 | LUFlow: port-only baseline; remove `dest_port`/`src_port`; keep `outlier` as a third class, or count it as malicious; time-blocked CV | C4 |

**Exit criterion:** a "waterfall" figure showing how much of the CIC drop each
factor explains.

### Phase 3: Extensions and new methods (weeks 7–11)

Pick **two or three**; do not attempt all of them.

| ID   | Idea | Why it matters | Compute |
|------|------|----------------|---------|
| E3.1 | Stronger learners: logistic regression on log-scaled features, LightGBM/XGBoost/CatBoost, a PyTorch MLP; optionally FT-Transformer or TabM | Gradient-boosted trees are the tabular state of the art (Grinsztajn et al., 2022). Without them the comparison is outdated | CPU; GPU optional |
| E3.2 | **Label-budget curve.** Add k labeled target-domain flows (k = 0, 50, 500, 5k, 50k) and retrain or fine-tune; include TabPFN for small k | Answers the practical question "how much labeling does a new network need?" Cheap to run and easy to explain | CPU; GPU for TabPFN |
| E3.3 | One-class detectors trained on benign traffic only (Isolation Forest, autoencoder), evaluated on unseen families by leaving one attack family out at a time | Tests whether anomaly detection covers the supervised models' blind spot. Both the report and the baseline list this as future work | CPU / small GPU |
| E3.4 | **LUFlow drift over the full span:** train on month t, test on months t+1…t+k; compare retraining cadences (never, quarterly, monthly), in the style of TESSERACT (Pendlebury et al., 2019) | Turns "retrain regularly" from advice into a measured curve. Probably the least-studied angle here | CPU |
| E3.5 | N×N cross-dataset matrix on the NetFlow-v2 datasets, which share 43 features | Moves from one dataset pair to a general picture; directly answers the feature-mismatch gap raised in the report | CPU (Kaggle) |
| E3.6 | Explain the drop: how SHAP attributions shift between domains; per-feature distribution shift (KS test, Wasserstein distance); optionally conformal prediction to flag drifting inputs | Gives the "why", which reviewers want | CPU |

**Recommended core:** E3.1 + E3.2 + E3.4. Add E3.3 or E3.5 if time allows.

### Phase 4: Write-up and release (weeks 11–14)

- Rewrite the paper as an experimental reproducibility and robustness study.
  It is not a survey. Credit the baseline in the title or abstract.
- Regenerate every figure from `results/` with one script.
- Tag a release. The README should let a stranger reproduce one headline
  number in under an hour on Kaggle.
- Post an arXiv preprint. First-time submitters may need an endorsement for
  the category, so ask a faculty member early. Then target a workshop or
  journal; see §8.

## 4. New algorithms: what is worth adding

**Worth adding**
- Gradient-boosted trees (LightGBM/XGBoost/CatBoost): the expected strongest
  baseline.
- Logistic regression: the simple robustness reference.
- TabPFN: few-shot adaptation.
- One-class models: unseen attacks.

**Optional**
- FT-Transformer or TabM, only if time allows. They rarely beat boosted trees
  on this kind of data, and Kaggle GPU time is limited.

**Not worth it here**
- Yet another deep architecture that reaches 99.9% in-distribution. Reviewers
  have seen hundreds of these.
- LLM-based classifiers for flow features: high cost, weak evidence.
- Graph-based NIDS (E-GraphSAGE and similar): interesting, but it needs IP
  graphs, which LUFlow anonymises, and it would be a separate project.

## 5. Experiment bookkeeping

- One config file per run: `configs/<experiment>/<variant>.yaml`.
- One results file per run: `results/<experiment>/<variant>/seed<k>.json`.
- `scripts/make_tables.py` and `scripts/make_figures.py` read only from
  `results/`.
- Pull requests are small and reviewed by the other person. The commit
  history is part of the portfolio.

## 6. Team split (suggested)

| | Member A: "shift" track | Member B: "time" track |
|---|---|---|
| Phase 1 | CIC replication (E1.x on CIC) | LUFlow replication (E1.x on LUFlow) |
| Phase 2 | E2.1–E2.5 | E2.6, and builds the shared `metrics.py` |
| Phase 3 | E3.1, E3.2 | E3.4, plus E3.3 or E3.5 |
| Shared | Reading list, preregistration, evaluation rules, writing | |

## 7. Risks

| Risk | Mitigation |
|------|------------|
| Kaggle quota or session limits | Process raw data once into compact Parquet; keep runs under 2 hours; checkpoint results per seed |
| Corrected datasets have different columns | Write a column-mapping table in `configs/features/`; test it on 1,000 rows first |
| Results match the literature, so "nothing new" | The decomposition (E2), label budget (E3.2) and temporal curve (E3.4) are the contribution, not the headline drop |
| Scope creep | Phase 3 is capped at three experiments; anything else goes in "future work" |
| Overlap with recent papers | Re-run the literature search before writing (Google Scholar: "cross-dataset" NIDS, from 2024 on) |

## 8. Portfolio outputs

1. This repository, with a clean README and reproducible headline numbers.
2. An arXiv preprint.
3. A submission to a workshop on ML and security, or a journal such as
   *Computers & Security* or *Journal of Information Security and
   Applications*.
4. A short blog post with the waterfall figure, plus a LinkedIn post.
5. A cold-email line for supervisors abroad: "We reproduced [published
   study], found that X% of its cross-dataset drop comes from Y, and showed
   that Z labeled flows recover it."
