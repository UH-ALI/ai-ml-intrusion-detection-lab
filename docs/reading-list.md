# Reading list

Entries marked † were cited from memory. Entries without a mark had their
title, authors and venue checked in October 2026. **Open every paper before
citing it**, and export BibTeX from the publisher or Google Scholar. Never copy
references from another paper's reference list or from an AI tool.

Step numbers refer to [plan.md](../plan.md).

## Must-read in Week 1 (both team members)

1. **Chua, T.-H. & Salam, I. (2023).** Evaluation of Machine Learning
   Algorithms in Network-Based Intrusion Detection Using Progressive Dataset.
   *Symmetry* 15(6):1251. doi:10.3390/sym15061251. Code:
   github.com/tuanhong3498/Evaluation-of-Machine-Learning-Algorithm-in-Network-Based-Intrusion-Detection-System.
   **Why:** the baseline we reproduce (Step 1).
2. **Engelen, G., Rimmer, V. & Joosen, W. (2021).** Troubleshooting an
   Intrusion Detection Dataset: the CICIDS2017 Case Study. *IEEE Security and
   Privacy Workshops (SPW / WTMC)*. †venue
   **Why:** labeling and CICFlowMeter errors in CIC-IDS2017; the source of the
   corrected 2017 data (Step 5f).
3. **Liu, L., Engelen, G., Lynar, T., Essam, D. & Joosen, W. (2022).** Error
   Prevalence in NIDS datasets: A Case Study on CIC-IDS-2017 and
   CSE-CIC-IDS-2018. *IEEE CNS 2022*, 254–263.
   doi:10.1109/CNS56114.2022.9947235.
   **Why:** the same kind of errors in the 2018 data, plus corrected labels
   (Steps 5e, 5f).
4. **Arp, D. et al. (2022).** Dos and Don'ts of Machine Learning in Computer
   Security. *USENIX Security*. †
   **Why:** a checklist of the pitfalls our ground rules and ablations target.
5. **Cantone, M., Marrocco, C. & Bria, A. (2024).** On the Cross-Dataset
   Generalization of Machine Learning for Network Intrusion Detection.
   arXiv:2402.10974.
   **Why:** the closest prior work, covering CIC-IDS2017, CSE-CIC-IDS2018 and
   their LycoS-corrected versions, with results per attack type. Our fallback
   for corrected data. Read it before claiming novelty.
6. **Apruzzese, G., Andreolini, M., Ferretti, L., Marchetti, M. & Colajanni,
   M. (2022).** Modeling Realistic Adversarial Attacks against Network
   Intrusion Detection Systems. *ACM Digital Threats: Research and Practice*
   3(3), Article 31. arXiv:2106.09380.
   **Why:** the threat-model basis for our evasion test (Step 6).

## Cross-dataset generalisation and dataset quality (Steps 4–5)

7. **D'hooge, L. et al. (2023).** Investigating Generalized Performance of
   Data-Constrained Supervised Machine Learning Models on Novel, Related
   Samples in Intrusion Detection. *Sensors* 23(4):1846.
8. **D'hooge, L. et al. (2023).** *Journal of Cybersecurity and Privacy*
   3(2), doi:10.3390/jcp3020008. CIC-IDS2017-trained models tested on
   CSE-CIC-IDS2018, with drops of 0–50% depending on attack class. †check
   the exact title.
9. **Catillo, M., Del Vecchio, A., Pecchia, A. & Villano, U. (2022).**
   Transferability of machine learning models learned from public intrusion
   detection datasets: the CICIDS2017 case study. *Software Quality Journal*.
10. **Layeghy, S. & Portmann, M. (2023).** Explainable cross-domain
    evaluation of ML-based network intrusion detection systems. *Computers
    and Electrical Engineering* 108:108692. **Why:** SHAP-based explanation
    of cross-dataset shift; the closest work to our Step 4.
11. **Flood, R., Engelen, G., Aspinall, D. & Desmet, L. (2024).** Bad Design
    Smells in Benchmark NIDS Datasets. *IEEE EuroS&P 2024* (Distinguished
    Paper).
12. **Rosay, A. et al. (2022).** Network Intrusion Detection: A Comprehensive
    Analysis of CIC-IDS2017. *ICISSP 2022*. **Why:** source of LycoS-IDS2017.
    †authors
13. **Hossain, M. Z. et al. (2026).** Assessing Generalisation Capability of
    Machine Learning Models for Intrusion Detection. arXiv:2605.04407.
    Recent; UNSW-NB15 ↔ TON_IoT.
14. arXiv:2607.00553 (2026). Cross-Domain Generalization Failure in
    Lightweight Intrusion Detection Models for IIoT Networks. **Why:**
    reportedly ablates a single confounding feature. Check its overlap with
    our Step 5g.

## Evaluation methodology (Steps 2, 5d)

15. **Apruzzese, G., Laskov, P. & Schneider, J. (2023).** SoK: Pragmatic
    Assessment of Machine Learning for Network Intrusion Detection. *IEEE
    EuroS&P 2023*, 592–614. arXiv:2305.00550.
16. **Axelsson, S. (2000).** The base-rate fallacy and the difficulty of
    intrusion detection. *ACM TISSEC* 3(3). † **Why:** the reason we report
    precision at realistic attack prevalence.
17. **Sommer, R. & Paxson, V. (2010).** Outside the Closed World: On Using
    Machine Learning for Network Intrusion Detection. *IEEE S&P*. †

## Adversarial attacks on ML (Step 6)

18. **Pierazzi, F., Pendlebury, F., Cortellazzi, J. & Cavallaro, L. (2020).**
    Intriguing Properties of Adversarial ML Attacks in the Problem Space.
    *IEEE S&P*. † **Why:** why attacks must respect real-world constraints.
19. **Nicolae, M.-I. et al. (2018).** Adversarial Robustness Toolbox v1.0.0.
    arXiv:1807.01069. † **Why:** the library for the optional unconstrained
    attack.

## Models and explanation (Steps 3–4)

20. **Grinsztajn, L., Oyallon, E. & Varoquaux, G. (2022).** Why do
    tree-based models still outperform deep learning on typical tabular data?
    *NeurIPS Datasets & Benchmarks*. † **Why:** justifies gradient-boosted
    trees as the strong baseline.
21. **Lundberg, S. & Lee, S.-I. (2017).** A Unified Approach to Interpreting
    Model Predictions (SHAP). *NeurIPS*. †
22. **Ribeiro, M. T., Singh, S. & Guestrin, C. (2016).** "Why Should I Trust
    You?": Explaining the Predictions of Any Classifier (LIME). *KDD*. †

## Recent datasets (for the dataset table in Step 7)

23. **CICIoT2023:** 33 attacks on 105 IoT devices, in 7 categories. UNB CIC;
    described in *Sensors* (2023). †authors
24. **CICIoMT2024:** 18 attacks on 40 medical IoT devices over Wi-Fi, MQTT and
    Bluetooth. UNB CIC; *Internet of Things* (2024). †authors
25. **Luay, M., Layeghy, S. et al. (2025).** Temporal Analysis of NetFlow
    Datasets for Network Intrusion Detection Systems. arXiv:2503.04404.
    **Why:** NetFlow v3, which adds timing features (53 features in total).
    Our newer-data check (Step 5h).
26. **Shafi, M., Lashkari, A. H. & Haghighian Roudsari, A. (2024).**
    NTLFlowLyzer. *Computers & Security*. **Why:** the tool behind
    BCCC-CIC-IDS2017.

## Data sources

- CIC-IDS2017: unb.ca/cic/datasets/ids-2017.html
- CSE-CIC-IDS2018: registry.opendata.aws/cse-cic-ids2018 (public S3 bucket)
- LUFlow: github.com/ruzzzzz/LUFlow (Kaggle mirrors also exist)
- Corrected CIC-IDS2017 / CSE-CIC-IDS2018 (DistriNet, KU Leuven): likely at
  downloads.distrinet-research.be, linked from papers 2 and 3. †confirm in
  Week 1
- NetFlow v3: staff.itee.uq.edu.au/marius/NIDS_datasets/
