# Claims to test

Our course report repeated the conclusions of Chua & Salam (2023). Below, each
of those conclusions is treated as a hypothesis, not a finding. For every claim
we list what it rests on, why it is in doubt, and which experiment in
[research-plan.md](research-plan.md) will test it.

All numbers about the baseline come from the outputs saved in the baseline's
public notebooks (`CIC/0x_*.ipynb`, `LUFlow/0x_*.ipynb`). We have not
re-run anything yet.

**Verdict values:** `untested`, `holds`, `holds with caveats`, `does not hold`.

---

## C1. "Models pass CV on CIC-IDS2017 but fail on CSE-CIC-IDS2018 because they overfit"

- **What it rests on:** one run. Cross-validation accuracy on CIC-IDS2017 is
  0.73–0.997; accuracy on CSE-CIC-IDS2018 is 0.50–0.76. The 2018 test set is a
  51,558-row sample, about 1% of the full dataset.
- **Why it is in doubt:** "overfitting" is never separated from the other
  explanations listed below.
  - **Attack families the model has never seen.** DDoS-HOIC makes up about 27%
    of the malicious flows in the 2018 test set (68,628 of 257,791), and HOIC
    does not appear in CIC-IDS2017. In the other direction, PortScan is 14% of
    the training data and has no counterpart in the 2018 test set.
  - **Known dataset errors.** Engelen et al. (2021) and Liu et al. (2022)
    documented labeling and CICFlowMeter feature-extraction errors in both
    datasets. Infiltration flows in 2018 (about 6% of malicious test flows) are
    a known problem class.
  - **Shortcut features.** Three of the 11 selected features describe the
    environment rather than the attack: `Destination Port`,
    `Init_Win_bytes_forward` and `Init_Win_bytes_backward`. TCP initial window
    sizes depend on the operating system and testbed configuration.
  - **Different capture environments.** CIC-IDS2017 was captured on an
    on-premise testbed; CSE-CIC-IDS2018 was captured on AWS.
- **Tests:** E2.1, E2.2, E2.3, E2.5. **Verdict:** `untested`.

## C2. "SVM and ANN are the most robust; DT and RF suffer the most"

- **What it rests on:** one random seed, one subsample (10% of a 10% subset),
  and one hyperparameter setting per model, chosen by in-domain CV. No
  confidence intervals are reported.
- **Why it is in doubt:** the gaps between models (e.g. ANN 0.700 vs DNN 0.652)
  may fall within seed-to-seed variance. Hyperparameters tuned on in-domain CV
  favour models that fit the source domain most tightly.
- **Tests:** E1.3 (seed variance), E2.2, E3.1. **Verdict:** `untested`.

## C3. "ANN gives the best balance of accuracy and robustness"

- **What it rests on:** a qualitative judgment.
- **Why it is in doubt:** by the report's own numbers, SVM beats ANN on
  cross-dataset accuracy (0.756 vs 0.700) and on malicious-class recall
  (0.606 vs 0.496). The preference for ANN rests on SVM's slower inference,
  which is never stated as a criterion. The suitability matrix (Fig. 22) has no
  scoring rubric.
- **Test:** fix the criteria up front (e.g. recall at a fixed false-positive
  rate, and latency per 1,000 flows) and report the Pareto front.
  **Verdict:** `untested`.

## C4. "LUFlow models generalise over time, show no overfitting, and ML stays effective in stable settings"

- **What it rests on:**
  - Training data: July 2020 only, about 10% of lines, `outlier` class
    dropped, benign downsampled to 1:1.
  - Test data: January 2021 only, then a further 20% sample of 227,601 rows.
  - Feature ranking: in the baseline's random-forest ranking, `dest_port` has
    importance 0.347, three times the next feature. DT and RF are near-perfect
    with only one or two features.
- **Why it is in doubt:**
  - The data covers two single months, not two years; the report's text says
    "daily logs merged per year".
  - If one port feature nearly solves the task, the models may be doing a port
    lookup on honeypot traffic rather than learning attack behaviour. Stability
    over time could then simply mean attackers keep hitting the same ports.
  - `src_port` is also in the top 6, another likely shortcut.
  - Dropping the `outlier` class (8%) removes exactly the ambiguous cases.
  - Random K-fold over flows from the same scanners puts near-duplicates in
    both training and validation folds.
- **Tests:** E2.6, E3.4. **Verdict:** `untested`.

## C5. "Accuracy below 0.80 is inadequate for practical deployment"

- **Why it is in doubt:**
  - The 0.80 threshold has no source.
  - On a 1:1 test set, a constant "benign" classifier scores 0.50, which is
    roughly what Naive Bayes achieved (0.497, malicious recall 0.0003).
  - Whether an IDS is usable depends on its false-positive rate at realistic
    attack prevalence (Axelsson, 2000), not on accuracy on a balanced set.
- **Test:** report false-positive rate, precision at realistic prevalence,
  PR-AUC, MCC and balanced accuracy, alongside a dummy baseline (E2.1).
  **Verdict:** `untested`.

## C6. "Cross-dataset evaluation is under-explored"

- **Why it is in doubt:** transfer from CIC-IDS2017 to CSE-CIC-IDS2018 has been
  studied directly by D'hooge et al. (2023), Catillo et al. (2022) and Cantone
  et al. (2024). Sarhan et al. built the NetFlow-v2 datasets specifically so
  that models can be compared across datasets. See
  [reading-list.md](reading-list.md).
- **Action:** position this project as reproducibility work plus a controlled
  decomposition of the drop, not as the first cross-dataset study.
  **Verdict:** `does not hold` as stated (based on the literature, not an
  experiment).

## C7. "DT and RF reach about 99.7% CV accuracy on CIC-IDS2017"

- **Why it is in doubt:** the number will very likely reproduce, but it is
  optimistic, for three reasons.
  - Feature ranking was done outside the CV folds.
  - The loop "add features until accuracy is highest" used the same data that
    CV later scored.
  - Random flow-level folds put flows from the same attack session into both
    training and validation.
- **Test:** E2.4 (feature selection nested inside CV; folds grouped by capture
  day or attack window). **Verdict:** `untested`.

---

## Baseline implementation facts (from the published notebooks)

These matter for a faithful replication (E1.1/E1.2). Several of them are not
stated in the paper.

| Item | Value in the baseline code |
|------|----------------------------|
| CIC-IDS2017 cleaned + balanced | 649,762 rows (324,881 benign + 324,881 attack) |
| CSE-CIC-IDS2018 (10% subset) cleaned + balanced | 515,582 rows |
| Extra subsampling before training/testing | `sample(frac=0.1)` on both, so training = 70% of 64,976 = **45,483 rows** and the 2018 test set = **51,558 rows** |
| CV data | `sample(frac=0.3)` of the 649,762 rows, `StratifiedKFold(5, shuffle=True)` |
| Seed | `random.seed(10)`, `np.random.seed(10)`; no `random_state` passed to the models |
| Scaling | `StandardScaler` fit on CIC-IDS2017 training split only, applied to the 2018 test set |
| 11 CIC features (RF importance order) | Bwd Packet Length Std, Average Packet Size, Max Packet Length, Packet Length Variance, Packet Length Std, Avg Bwd Segment Size, Packet Length Mean, Destination Port, Init_Win_bytes_forward, Fwd Packet Length Mean, Init_Win_bytes_backward |
| CIC hyperparameters | DT: entropy, `ccp_alpha=1.44e-5`. RF: 350 trees, `max_depth=20`. SVC: RBF, `C=100`, `gamma=1`. GaussianNB: `var_smoothing=1.0`. ANN: MLP (50,), tanh. DNN: MLP (15,15,15), tanh |
| LUFlow periods | Daily CSVs for 2020-07-01..31 (train) and 2021-01 (test; 16th and 21st missing), about 1 in 10 lines kept at load time |
| LUFlow features | `src_ip`, `dest_ip`, `time_start`, `time_end` dropped, leaving 11 features. Top 6 used: `dest_port`, `bytes_out`, `total_entropy`, `src_port`, `num_pkts_in`, `duration` |
| LUFlow sizes | Training pool 1,759,480 rows (879,740 per class); test pool 1,138,006 rows; each then `sample(frac=0.2)`, giving a 2021 test set of 227,601 rows |
| Software | Python 3.8.8, scikit-learn 0.24.1, pandas 1.2.4, NumPy 1.20.1 |
