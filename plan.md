# Project plan

**Working title:** *Why ML Intrusion Detectors Fail Outside the Lab: A
Reproduction and Breakdown of Chua & Salam (2023)*

**Team:** 2 people · **Duration:** 9 weeks · **Compute:** laptop + free Kaggle
(see [docs/compute-strategy.md](docs/compute-strategy.md))

This is the single source of truth for what we do and in what order. If
something is not in this file, it is out of scope until we agree to add it.

---

## 0. At a glance

### Research question

ML intrusion detectors score about 99% in the lab. Do they still work:

1. on a **different network** (CIC-IDS2017 → CSE-CIC-IDS2018)?
2. at a **later time** (LUFlow July 2020 → January 2021)?
3. when an **attacker deliberately adjusts their traffic** to fool the model?
4. on **newer data** released after Chua & Salam (NetFlow v3, 2025)?

If not, **why**, and how much does each cause contribute?

### What the paper will contribute

| # | Contribution | Comes from |
|---|--------------|------------|
| C1 | An independent reproduction of Chua & Salam (2023), with seed variance they did not report | Step 1 |
| C2 | A fair re-evaluation (full test set, proper metrics, confidence intervals) plus modern models | Steps 2–3 |
| C3 | **A breakdown of the cross-dataset drop** by cause: shortcut features, label errors, unseen attacks, preprocessing, evaluation setup; then a check on newer data (NetFlow v3, 2025) | Steps 4–5 (5h) |
| C4 | A realistic evasion test: how easily an attacker can fool each model by changing only what they control | Step 6 |

C3 is the headline. Other papers show *that* models fail on new data; few
measure *how much of the failure each cause explains*.

### Why Chua & Salam (2023) is our baseline

- **Peer-reviewed, with clear claims we can test.** SVM and ANN are robust; DT
  and RF overfit; LUFlow models stay stable.
- **Public code and saved outputs.** We can check that our rebuild matches
  theirs number for number. Most papers don't make this possible.
- **It saves us weeks.** Features, hyperparameters and splits are already
  defined.
- **It fixes our integrity problem.** Our course report used their results.
  Citing them openly as the baseline turns that into a legitimate
  reproduction.
- **Its weak points are our experiments.** It used a single seed, a 1% test
  sample, accuracy-only reporting, shortcut features, and two months of
  LUFlow.

### Where the professor's checklist is covered

| Professor's item | Where | Notes |
|------------------|-------|-------|
| Include dataset(s) | §2.2, Steps 5f, 5h | CIC-IDS2017, CSE-CIC-IDS2018, LUFlow, the **corrected** CIC versions, and **NetFlow v3 (2025)**, released after Chua & Salam. We drop NSL-KDD because it is built from 1998 traffic and reviewers increasingly reject it |
| ML / DL algorithms | Steps 1, 3 | The original 6, plus logistic regression, LightGBM/XGBoost and a PyTorch MLP |
| Feature selection (SHAP, LIME, permutation) | Steps 4, 5c | SHAP and permutation for ranking; LIME for individual examples |
| Ablation (preprocessing, encoding, normalisation, standardisation) | Steps 5a, 5b | One change at a time |
| Confusion matrix + accuracy, precision, recall, F1, AUC-ROC | Step 2 | Plus MCC, false-positive rate, PR-AUC, recall per attack |
| Literature comparison table + latest datasets and papers | Step 7 | Papers from 2020–2026 and a table of recent datasets |

---

## 1. Ground rules (apply to every step)

- **Only our own numbers.** Every number in the paper comes from our code and
  traces to a results file and a git commit.
  - *How:* each run writes `results/<step>/<variant>/seed<k>.json` containing
    the metrics, config, commit hash, dataset version, row counts, library
    versions and hardware.
- **The test set is never used for decisions:** not features, hyperparameters,
  thresholds or early stopping.
  - *How:* tuning uses a validation split carved from the **training**
    dataset only. Everything that learns from data sits inside a scikit-learn
    `Pipeline`, so it is fit on training data only.
- **Seeds.** Every result is a mean ± 95% CI over **5 seeds**. Each seed
  controls both the data sampling and the model's `random_state`.
  - *How:* `for seed in [0, 1, 2, 3, 4]`. The CI is computed with a
    t-distribution.
- **One change at a time.** Every ablation changes exactly one thing relative
  to a fixed reference configuration.
- **Credit and citations.** Name Chua & Salam as the baseline in the abstract.
  Every reference must be one a team member has opened.
  - *How:* Zotero, with BibTeX exported from the publisher or Google Scholar.
- **Figures come from code.** Never draw a result figure by hand or copy one.
  - *How:* `scripts/make_figures.py` reads only from `results/`. Draw
    schematic figures ourselves in draw.io.

---

## 2. Setup (Week 1)

### 2.1 Repository and environment

- **Goal:** both of us can run the same code, locally and on Kaggle.
- **How:**
  - Create this layout:
    ```
    src/idslab/   data.py  features.py  models.py  metrics.py  explain.py  evasion.py
    configs/      one YAML per experiment variant
    scripts/      run_experiment.py  make_tables.py  make_figures.py
    results/      JSON/CSV outputs (committed)
    notebooks/    thin Kaggle runners that call src/
    ```
  - Pin versions in `requirements.txt`: scikit-learn, pandas, pyarrow,
    lightgbm, xgboost, torch (CPU), shap, lime, pyyaml.
  - Work on feature branches and merge through pull requests reviewed by the
    other person.
- **Done when:** `python scripts/run_experiment.py configs/smoke.yaml` runs
  end to end on a 1% sample on both laptops.

### 2.2 Get the data

- **Goal:** all raw data available on Kaggle, verified against official row
  counts.
- **How:**
  - **CIC-IDS2017:** the "MachineLearningCVE" CSVs (8 files) from UNB
    (unb.ca/cic/datasets/ids-2017.html), or a Kaggle mirror. Check the total
    of **2,830,743 rows**.
  - **CSE-CIC-IDS2018:** the "Processed Traffic Data for ML Algorithms" CSVs
    (10 files) from the public AWS bucket:
    `aws s3 sync --no-sign-request --region ca-central-1 "s3://cse-cic-ids2018/Processed Traffic Data for ML Algorithms/" data/raw/cse-cic-ids2018/`.
    A Kaggle mirror also works.
  - **LUFlow:** the daily CSVs for 2020-07 and 2021-01, from
    github.com/ruzzzzz/LUFlow or a Kaggle mirror.
  - **Corrected CIC versions:** the DistriNet (KU Leuven) improved
    CIC-IDS2017 and CSE-CIC-IDS2018, linked from Engelen et al. (2021) and Liu
    et al. (2022). The likely location is downloads.distrinet-research.be.
    **Confirm availability in Week 1.** If they are not available, fall back
    to LycoS-IDS2017 and LycoS-Unicas-IDS2018 (Cantone et al., 2024).
  - **NetFlow v3 (2025, newer data):** NF-CSE-CIC-IDS2018-v3, NF-UNSW-NB15-v3
    and NF-ToN-IoT-v3 from staff.itee.uq.edu.au/marius/NIDS_datasets/ (University
    of Queensland). All share the same 53 NetFlow features, so no column
    mapping is needed. Used in Step 5h.
- **Done when:** every dataset is attached to a Kaggle notebook and its row
  counts are logged in `docs/data-log.md`.

### 2.3 Build compact Parquet files once

- **Goal:** experiments load in seconds and never re-parse raw CSVs.
- **How (Kaggle CPU session, one file at a time):**
  - Strip spaces from column names. Drop the duplicate `Fwd Header Length.1`
    column (2017). Drop repeated header rows and the extra columns in one
    2018 file (`Flow ID`, `Src IP`, `Src Port`, `Dst IP`).
  - **Map the 2018 column names to the 2017 names with an explicit dictionary
    covering all columns.** Don't do it the way the baseline did, with
    substring regex plus two hard-coded positions (columns 40 and 41).
    Sanity-check each mapped feature by comparing medians across the two
    datasets, to catch swapped columns.
  - Replace inf with NaN, drop rows with NaN, and drop exact duplicates
    **within** each dataset.
  - Downcast to float32. Keep **two** label columns: `label_binary` and
    `label_family` (the original attack name).
  - **NetFlow v3:** drop IP addresses and timestamps; keep `Label` and
    `Attack` as `label_binary` and `label_family`. Store a stratified 20%
    sample of the larger files if the full set is too big for Kaggle RAM.
  - Write one Parquet file per day (per file for NetFlow v3). Save the set as a **private Kaggle
    Dataset** and add the teammate as a collaborator.
- **Done when:** both of us load the Parquet files from Kaggle, and a 5%
  sample loads on a laptop.

### 2.4 Start the reading (in parallel; details in Step 7)

- Both of us read Chua & Salam (2023), Engelen et al. (2021), Liu et al.
  (2022), Arp et al. (2022), Cantone et al. (2024) and Apruzzese et al. (2022,
  realistic adversarial attacks).
- Both of us read the baseline's 10 notebooks end to end.

---

## 3. Step 1: Reproduce Chua & Salam (Week 2) → C1

- **Goal:** show we can produce their numbers with our own code, then measure
  how much those numbers vary.
- **Why it matters:** it is the foundation for every later claim, and it
  replaces the borrowed numbers in our course report with our own.
- **How:**
  - **1a. Run their notebooks as-is** on Kaggle, with the original library
    versions if possible (scikit-learn 0.24.1, Python 3.8). Record our
    numbers next to the published ones.
  - **1b. Rebuild in `src/idslab` with exactly their settings:**
    - **CIC:** the balanced 2017 set (649,762 rows), then `sample(frac=0.1)`,
      then a 70/30 split. Training set: 45,483 rows. Test set: a 10% sample
      of the cleaned 2018 data (51,558 rows).
    - **Features:** their 11 (listed in
      [docs/claims-to-test.md](docs/claims-to-test.md)).
    - **Hyperparameters:** SVC (RBF, C=100, γ=1); DT (entropy,
      ccp_alpha=1.44e-5); RF (350 trees, max_depth=20); GaussianNB
      (var_smoothing=1.0); MLP (50,) and (15,15,15), both tanh.
    - **LUFlow:** July 2020 for training, January 2021 for testing; the 6
      features `dest_port`, `bytes_out`, `total_entropy`, `src_port`,
      `num_pkts_in`, `duration`; `outlier` class dropped; 1:1 balancing.
  - **1c. Repeat 1b over 5 seeds.**
- **Output:**
  - Table "Published vs. re-run vs. our rebuild (mean ± CI)" for their Tables
    4, 5, 8 and 9.
  - One sentence on whether the ranking SVM > ANN > DNN > RF ≈ DT > NB holds
    across seeds.
- **Done when:** our rebuild is within ±2 points of their numbers, or each
  gap has a written explanation.

---

## 4. Step 2: Fair evaluation (Week 3) → C2

- **Goal:** report results in a way that cannot hide failure.
- **Why it matters:** on a balanced test set, accuracy makes a coin flip look
  like 50%. Their Naive Bayes scored 0.497 while catching almost no attacks.
  Recall per attack type shows *which* attacks fail.
- **How:**
  - **`metrics.py` computes for every run:**
    - **The confusion matrix**, saved as numbers and plotted with the standard
      orientation (rows = true labels).
    - **Threshold metrics:** accuracy, precision, recall and F1 (per class and
      macro), balanced accuracy, **MCC**, **false-positive rate**.
    - **Score metrics:** **AUC-ROC** and **PR-AUC**. For SVM, use
      `decision_function` scores; don't turn on `probability=True`, which is
      slow.
    - **Recall per attack type**, using `label_family`.
    - **Precision at realistic attack prevalence:**
      `precision(π) = π·TPR / (π·TPR + (1−π)·FPR)` for π = 1% and 10%.
  - **Larger, realistic test set:** replace their balanced 51,558-row sample
    with the full cleaned 10% subset of CSE-CIC-IDS2018 at its **natural
    benign/attack ratio**. If SVM prediction is too slow, predict on a 200k
    stratified sample and say so.
  - **Reference rows in every table:**
    - a **dummy** classifier that always predicts the majority class;
    - a **port-only** model (a decision tree on `Destination Port` alone).
  - Re-run Step 1's models under this protocol.
- **Output:** the main results table (all models × all metrics, mean ± CI)
  and a confusion-matrix figure.
- **Done when:** every number in the main table has a CI, and both reference
  rows are present.

---

## 5. Step 3: Stronger models (Week 3) → C2

- **Goal:** test whether modern models change the picture.
- **Why it matters:** gradient-boosted trees are currently the strongest
  models for tabular data. Without them, reviewers will call the comparison
  outdated.
- **How:**
  - **Add these models:**
    - **Logistic regression** on log-scaled features: a simple reference.
    - **LightGBM** (and/or **XGBoost**): the expected strongest model.
    - **A PyTorch MLP:** 3 layers with dropout and batch norm, early-stopped
      on a validation split from the **training** dataset.
  - **Tuning:** a small grid or 30 Optuna trials per model, on a validation
    split of CIC-IDS2017 only. Keep the original 6 models with their published
    hyperparameters, so the comparison with the baseline stays fair.
  - Use the same features, data and metrics as Step 2.
- **Output:** new rows in the main results table, plus training and
  prediction time per 1,000 flows.
- **Done when:** all new models are run over 5 seeds under the Step 2
  protocol.

---

## 6. Step 4: What the models rely on (Week 4) → C3

- **Goal:** find out whether the models learned the attacks or memorised the
  lab network.
- **Why it matters:** this will likely be the headline finding. We expect the
  models to rely on "shortcut" features that describe the environment:
  `Destination Port` and the TCP initial window sizes (`Init_Win_bytes_*`) in
  CIC, and `dest_port` in LUFlow.
- **How:**
  - **SHAP:** TreeSHAP for DT, RF and LightGBM; KernelSHAP on a 500-row
    sample for SVM and the MLP. Report mean |SHAP| per feature, on the 2017
    test split **and** on 2018.
  - **Permutation importance** (`sklearn.inspection.permutation_importance`)
    on the 2017 validation split, as a model-agnostic check of the SHAP
    ranking.
  - **LIME:** explain about 20 attacks that were caught in 2017 but missed in
    2018. These give the examples for the paper ("this DoS flow was missed
    because…"). LIME is for examples, not for feature selection.
  - **Measure environment shift.** Compare **benign 2017 traffic with benign
    2018 traffic**. Benign traffic should look similar everywhere, so features
    that differ there describe the network, not the attacks.
    - For each feature, compute the Wasserstein distance and the KS statistic.
    - Train a "domain classifier" to tell 2017 benign flows from 2018 benign
      flows. Its most important features are the ones that identify the
      environment.
  - **Define the shortcut set S:** features with high importance **and** high
    environment shift. Starting candidates: `Destination Port`,
    `Init_Win_bytes_forward`, `Init_Win_bytes_backward`.
  - **LUFlow:**
    - a `dest_port`-only model;
    - the models retrained without `dest_port` and `src_port`;
    - a variant that keeps the `outlier` flows (counted as malicious) instead
      of dropping them.
- **Output:**
  - A SHAP summary figure (2017 vs. 2018).
  - A table of environment shift per feature.
  - The shortcut set S, with justification.
- **Done when:** S is fixed and documented. Step 5 uses it unchanged.

---

## 7. Step 5: Ablation study, the breakdown (Weeks 4–5) → C3

- **Goal:** measure how much each factor contributes to the drop from 2017 to
  2018.
- **Why it matters:** this is the paper's main contribution. It turns "models
  fail" into "models fail mostly because of X".
- **Reference configuration:** the Step 2 protocol with Chua & Salam's 11
  features and StandardScaler fit on training data. Each ablation changes
  **one** thing. Report in-domain (2017 test) **and** cross-domain (2018)
  results for every variant.

### 5a. Scaling (professor: normalisation / standardisation)

- **How:** compare no scaling, MinMaxScaler, StandardScaler, RobustScaler,
  and `log1p` followed by StandardScaler. Also compare fitting the scaler on
  training data only (correct) with fitting a separate scaler on 2018 (a
  domain-adaptation shortcut; report it as such).
- **Expectation:** trees are unaffected by scaling, which also works as a
  sanity check. SVM, NB, logistic regression and MLP change. `log1p` should
  help NB considerably.

### 5b. Encoding (professor: encoding technique)

- **How:** ports are categories, not quantities (port 443 is not "bigger"
  than port 80). Compare:
  - the raw number (the baseline's choice);
  - port-range one-hot (well-known 0–1023 / registered 1024–49151 / dynamic
    49152+);
  - top-20 most frequent ports one-hot, plus "other";
  - frequency encoding, fit on training data only;
  - the port dropped.

  Apply the same comparison to LUFlow's `dest_port`, `src_port` and `proto`.

### 5c. Feature selection method (professor: SHAP / permutation)

- **How:** rank features by RF impurity (the baseline's method), by
  permutation importance, and by mean |SHAP|. Keep k = 5, 11, 20, or all
  features. **Ranking and selection happen inside the training folds only.**
- **Question:** does the selection method change cross-dataset performance,
  or only in-domain performance?

### 5d. Evaluation setup

- **How:**
  - Compare the balanced 1% test sample (the baseline) with the full test set
    at its natural ratio.
  - Compare accuracy with MCC and recall per attack type.
  - For in-domain validation, compare random 5-fold (the baseline) with a
    **time-blocked split**: within each day's file, train on the earlier 70%
    of flows and validate on the later 30%. This stops near-identical flows
    from the same attack session landing on both sides.
    - Row order is roughly chronological. The "GeneratedLabelledFlows"
      version of CIC-IDS2017 has exact timestamps if needed.
    - Don't group whole days: each day mostly holds one attack type, so that
      would turn into an unseen-attack test.
- **Question:** how much of the reported picture comes from the evaluation
  choices alone?

### 5e. Seen vs. unseen attacks

- **How:** group the 2018 attack types by whether training covered them:
  - **Seen:** DoS Hulk, GoldenEye, Slowloris; FTP and SSH brute force; web
    attacks; DDoS-LOIC-HTTP (≈ the 2017 "DDoS LOIT").
  - **Partly seen:** Bot (Ares in 2017; Zeus and Ares in 2018).
  - **Unseen:** DDoS-HOIC and DDoS-LOIC-UDP.
  - **Label-suspect:** Infiltration, FTP-BruteForce and DoS-SlowHTTPTest,
    whose 2018 labels have documented problems.

  Report recall per group. Check each mapping against the dataset
  documentation.

### 5f. Label errors: corrected datasets (professor: additional dataset)

- **How:** re-run the Step 2 protocol on the corrected CIC-IDS2017 →
  corrected CSE-CIC-IDS2018. Map columns as in §2.3. Write down how
  "attempted" or relabelled flows are handled, if the corrected data has
  them.
- **Question:** how much of the drop disappears when the labels are fixed?

### 5g. Remove the shortcut features

- **How:** retrain every model without the set S from Step 4.
- **Expectation:** in-domain accuracy falls slightly while cross-domain
  accuracy holds or improves. That would show the models had been
  memorising the network.

### 5h. Newer data: NetFlow v3 (2025)

- **Why:** Chua & Salam used datasets from 2017–2021. NetFlow v3 is a
  standardised benchmark released in 2025, after their paper. It re-extracts
  several datasets with one tool and one shared set of 53 features. This tests
  whether our findings hold on newer data, beyond a single CIC pair.
  - Note: NetFlow v3 is a newer **release**, not newer attacks. The underlying
    traffic is from 2015–2020. Say this plainly in the paper.
- **How:**
  - **Datasets:** NF-CSE-CIC-IDS2018-v3, NF-UNSW-NB15-v3 and NF-ToN-IoT-v3.
  - **Cross-dataset grid:** train on each, test on the other two, giving a 3×3
    matrix. Models: RF, LightGBM, the MLP, and the best classic model from
    Step 2 (SVM on ≤ 50k training rows).
  - **Repeat the key checks on this data:**
    - the Step 2 metrics and both reference rows;
    - the Step 4 domain classifier on benign traffic, to find environment
      features. Candidates: destination and source ports, and the TCP window
      fields (in v2 these were `L4_DST_PORT`, `L4_SRC_PORT`, `TCP_WIN_MAX_IN`
      and `TCP_WIN_MAX_OUT`; check the v3 names);
    - the Step 5g retraining without those features.
- **Question:** do the shortcut-feature finding and the model ranking from the
  CIC pair hold on a newer, standardised benchmark?

### Output of Step 5

- **The "waterfall" figure:** the 2017 → 2018 drop, broken into the
  contribution of each factor (5d, 5e, 5f, 5g).
- A 3×3 heatmap of cross-dataset results on NetFlow v3 (5h), with and without
  shortcut features.
- One results table per ablation.

**Done when:** every ablation is run over 5 seeds for at least DT, RF, SVM,
the MLP and LightGBM.

---

## 8. Step 6: Realistic evasion test (Weeks 6–7) → C4

- **Goal:** measure how easily an attacker can fool each model by changing
  only what they actually control.
- **Why it matters:**
  - It links the paper to current research on attacks against AI systems.
  - Many papers use unrealistic attacks that alter features no attacker can
    touch. We avoid that, following Apruzzese et al. (2022).
- **Threat model:**
  - The attacker sends the **forward** direction of the flow: CICFlowMeter
    treats the side that sends the first packet as forward. Restrict the test
    to attacks the attacker initiates: DoS, DDoS, brute force, web attacks.
  - The attacker sees only the model's decision, as a black box.
  - The attacker cannot change the target port or the server's responses.
  - **Simplifying assumption:** padding is added to every forward packet,
    including the handshake. Flow-level CSVs have no per-packet data, so this
    is the only version we can recompute exactly. State it as a limitation.
- **Attacker controls** (applied on the CIC-IDS2017 test split, where the
  model is in its home environment):
  - **K1, payload padding:** add p bytes to every forward packet,
    p ∈ {0, 8, 32, 128, 512}. Cap the payload at 1,460 bytes per packet.
  - **K2, TCP initial window:** set `Init_Win_bytes_forward` to a value drawn
    from benign 2017 traffic. The attacker's own TCP stack sets this value, so
    it is cheap to change.
- **How:**
  - **Recompute every affected feature consistently.** Padding raises the
    forward mean, max and min by p and leaves the forward standard deviation
    unchanged. Recompute the overall packet-length mean and variance from the
    per-direction counts, means and variances. Also update Average Packet
    Size, Avg Fwd Segment Size, Total Length of Fwd Packets, Subflow Fwd Bytes
    and Flow Bytes/s.
    - **Check the recomputation first:** with p = 0, the recomputed features
      must reproduce the original values within a small tolerance. Leave out
      any feature that can't be reproduced exactly, and say so.
  - **Attack:** for each attack flow the model correctly detected, try the
    knob combinations (5 padding values × 2 window settings = 10 queries) and
    keep the smallest change that makes the model output "benign". All of
    this lives in `evasion.py`.
  - **Metrics:** evasion rate (the share of detected attacks that can be
    flipped to "benign"), median padding needed, and results per model and
    per attack type.
  - **Compare three models:**
    - trained on all features;
    - trained without the shortcut set S (Step 5g);
    - *optional* quick defence: retrained with padded and window-changed
      attack flows added to the training data.
  - *Optional contrast:* an unconstrained attack (e.g. HopSkipJump in IBM's
    Adversarial Robustness Toolbox), to show that unrealistic attacks
    overstate the vulnerability.
- **Output:** an evasion-rate table, and a curve of evasion rate against
  padding budget for each model.
- **Done when:** the p = 0 check passes and evasion rates are reported over 5
  seeds.
- **Ethics note:** the test runs offline on public datasets for defensive
  research.

---

## 9. Step 7: Literature review and comparison table (Weeks 1–7, in parallel)

- **Goal:** know what is already established, so we can state what is new.
  This also covers the professor's comparison-table item.
- **How:**
  - **Where to search:** Google Scholar, arXiv cs.CR, IEEE Xplore and the ACM
    Digital Library; also skim recent proceedings of USENIX Security, IEEE
    S&P, CCS, NDSS, EuroS&P, RAID and AISec.
  - **Search terms:** "cross-dataset" intrusion detection; "generalization"
    NIDS; CIC-IDS2017 CSE-CIC-IDS2018 transfer; "adversarial" "network
    intrusion detection" realistic; "dataset errors" CICIDS. Limit to
    2020–2026.
  - **Snowballing:** follow the citations to and from Cantone et al. (2024),
    Flood et al. (2024) and Apruzzese et al. (2022, 2023).
  - **Screening:** keep peer-reviewed papers and well-cited preprints. Drop
    papers that only report within-dataset accuracy.
  - **Extraction sheet (shared Google Sheet), one row per paper:**
    - year and venue;
    - dataset(s);
    - models;
    - evaluation type (within / cross-dataset / temporal / adversarial);
    - metrics;
    - headline result;
    - code available?;
    - limitations.
  - **Target:** 25–40 papers, split 50/50 between us.
  - **Two tables for the paper:**
    - **Related-work comparison:** about 10 closest papers, with columns for
      dataset, models, evaluation type, cross-dataset tested?, adversarial
      tested?, key finding.
    - **Recent datasets:** CICIoT2023, CICIoMT2024, NetFlow v3 (2025),
      BCCC-CIC-IDS2017 and the corrected CIC versions, with year, setting,
      attack types and features. This shows we know the newer datasets, and
      explains our choices: the CIC pair to stay comparable with the
      baseline, and NetFlow v3 as the newer benchmark.
- **Done when:** both tables are filled and every entry has a verified
  citation in Zotero.

---

## 10. Step 8: Writing, figures and release (Weeks 8–9)

- **Paper outline, and which step feeds each section:**
  1. Introduction: the problem, the baseline, our contributions C1–C4.
  2. Background and related work: Step 7 tables.
  3. The baseline and our reproduction: Step 1.
  4. Experimental setup: datasets (§2), models (Steps 1 and 3), metrics
     (Step 2), protocol (§1).
  5. Results:
     - 5.1 Reproduction (Step 1)
     - 5.2 Fair evaluation and modern models (Steps 2–3)
     - 5.3 What models rely on (Step 4)
     - 5.4 Breakdown of the drop (Step 5, the waterfall figure)
     - 5.5 Does it hold on newer data? (Step 5h, NetFlow v3)
     - 5.6 Evasion (Step 6)
  6. Discussion: implications for deployment, limitations, future work (§13).
  7. Conclusion.
  8. Reproducibility statement: the code link and how to re-run.
- **How:**
  - Write in Overleaf, using the IEEE conference template.
  - Generate every table and figure with `scripts/make_tables.py` and
    `scripts/make_figures.py`.
  - Each person drafts the sections for their own steps; the other edits.
- **Before submitting:**
  - Give the professor a draft for review.
  - Run the definition-of-done checklist (§14).
  - Post to arXiv (cs.CR). First-time submitters may need an endorsement, so
    ask a faculty member in Week 7.
  - Submit to a security workshop or a journal (e.g. *Computers & Security*,
    *JISA*, *IEEE Access*).
  - Tag a GitHub release.

---

## 11. Team split and timeline

| Week | Person A (data and models) | Person B (evaluation and attacks) |
|------|----------------------------|-----------------------------------|
| 1 | Repo, environment, data download, Parquet build (2.1–2.3) | Confirm corrected datasets; reading list; literature search starts |
| 2 | Step 1 on CIC | Step 1 on LUFlow; `metrics.py` |
| 3 | Step 3 (new models) | Step 2 protocol; re-run Step 1 models under it |
| 4 | Step 5a–5c (scaling, encoding, selection) | Step 4 (SHAP, permutation, LIME, shortcut set S) |
| 5 | Step 5f (corrected datasets) | Step 5d, 5e, 5g |
| 6 | Step 5h: NetFlow v3 data build and 3×3 cross-dataset runs | Step 6: feature recomputation, its check, first evasion runs |
| 7 | Step 5h: domain classifier and shortcut removal on NetFlow v3 | Step 6 evasion runs finished; literature tables finished |
| 8 | Figures and tables; methods and results sections | Related work, introduction, discussion |
| 9 | Revise after the professor's review; release; arXiv | Same |

- **Weekly:** a 30-minute sync. Update this file's checkboxes (§14), and
  review each other's pull requests.

---

## 12. Risks and fallbacks

| Risk | Fallback |
|------|----------|
| Corrected CIC datasets not downloadable | Use LycoS-IDS2017 and LycoS-Unicas-IDS2018 (Cantone et al., 2024). If neither is available, drop 5f and state it as a limitation |
| Kaggle quota or session limits | Parquet files built once (§2.3); each run under 2 hours; one results file per seed, so a crash loses one run |
| SVM too slow on large sets | Train on ≤ 50k rows (as the baseline did) and predict on a 200k stratified sample. Report the sizes |
| Evasion feature recomputation doesn't match | Restrict the attack to features that pass the p = 0 check, and document which ones |
| Results confirm known findings | The breakdown (C3) and the realistic evasion test (C4) are still new; the headline drop is not the contribution |
| NetFlow v3 files too large for Kaggle RAM | Use stratified samples (§2.3); report the sizes |
| Running out of time | Cut in this order: adversarial-training defence → unconstrained attack contrast → LIME examples → LUFlow encoding variants → NF-ToN-IoT-v3 (keep a 2×2 grid) → 5f |

## 13. Out of scope (future work)

- NSL-KDD and other legacy datasets.
- Month-by-month drift on LUFlow, and retraining schedules.
- "How many labelled examples from the new network fix the model."
- NF-BoT-IoT-v3; IoT-specific datasets (CICIoT2023, CICIoMT2024).
- Poisoning and backdoor attacks; LLM-based detectors.

## 14. Definition of done (check before submission)

- [ ] Every number traces to `results/*.json` and a commit
- [ ] Every result has mean ± 95% CI over 5 seeds
- [ ] Every table has the dummy and port-only reference rows
- [ ] No test-set data was used for any choice (checked by both of us)
- [ ] Chua & Salam are credited in the abstract, introduction and Section 3
- [ ] Every reference was opened by a team member; BibTeX comes from the
      source
- [ ] Every figure is generated by script; no copied images
- [ ] The README lets a stranger reproduce one headline number on Kaggle in
      under an hour
- [ ] The professor has reviewed the draft
