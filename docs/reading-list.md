# Reading list

Entries marked † were cited from memory. Entries without a mark had their
title, authors and venue checked in October 2026. **Open every paper before
citing it**, and export BibTeX from the publisher or Google Scholar. Never copy
references from another paper's reference list or from an AI tool.

## Must-read in Phase 0 (both team members)

1. **Chua, T.-H. & Salam, I. (2023).** Evaluation of Machine Learning
   Algorithms in Network-Based Intrusion Detection Using Progressive Dataset.
   *Symmetry* 15(6):1251. doi:10.3390/sym15061251. Code:
   github.com/tuanhong3498/Evaluation-of-Machine-Learning-Algorithm-in-Network-Based-Intrusion-Detection-System.
   **Why:** this is the baseline we reproduce.
2. **Engelen, G., Rimmer, V. & Joosen, W. (2021).** Troubleshooting an
   Intrusion Detection Dataset: the CICIDS2017 Case Study. *IEEE Security and
   Privacy Workshops (SPW)*. †venue
   **Why:** documents labeling and CICFlowMeter errors in CIC-IDS2017 (E2.5).
3. **Liu, L., Engelen, G., Lynar, T., Essam, D. & Joosen, W. (2022).** Error
   Prevalence in NIDS datasets: A Case Study on CIC-IDS-2017 and
   CSE-CIC-IDS-2018. *IEEE CNS 2022*, 254–263.
   doi:10.1109/CNS56114.2022.9947235.
   **Why:** the same kind of errors in the 2018 dataset, plus corrected data
   and labeling logic.
4. **Arp, D. et al. (2022).** Dos and Don'ts of Machine Learning in Computer
   Security. *USENIX Security*. †
   **Why:** a checklist of the pitfalls our stress tests target (sampling
   bias, data snooping, base rates, spurious correlations).
5. **Cantone, M., Marrocco, C. & Bria, A. (2024).** On the Cross-Dataset
   Generalization of Machine Learning for Network Intrusion Detection.
   arXiv:2402.10974.
   **Why:** the closest prior work. Covers CIC-IDS2017, CSE-CIC-IDS2018 and
   their LycoS-corrected versions, with results per attack type. Read it
   before claiming novelty.
6. **Apruzzese, G., Laskov, P. & Schneider, J. (2023).** SoK: Pragmatic
   Assessment of Machine Learning for Network Intrusion Detection. *IEEE
   EuroS&P 2023*, 592–614. arXiv:2305.00550.
   **Why:** what practitioners need from ML-NIDS evaluations.

## Cross-dataset and generalisation

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
    and Electrical Engineering* 108:108692.
11. **Sarhan, M., Layeghy, S. & Portmann, M. (2022).** Towards a Standard
    Feature Set for Network Intrusion Detection System Datasets. *Mobile
    Networks and Applications* 27:357–370. arXiv:2101.11315. **Why:** the
    NetFlow-v2 datasets (E3.5).
12. **Flood, R., Engelen, G., Aspinall, D. & Desmet, L. (2024).** Bad Design
    Smells in Benchmark NIDS Datasets. *IEEE EuroS&P 2024* (Distinguished
    Paper).
13. **Rosay, A. et al. (2022).** Network Intrusion Detection: A Comprehensive
    Analysis of CIC-IDS2017. *ICISSP 2022*. **Why:** source of LycoS-IDS2017.
    †authors
14. **Hossain, M. Z. et al. (2026).** Assessing Generalisation Capability of
    Machine Learning Models for Intrusion Detection. arXiv:2605.04407.
    **Why:** recent; UNSW-NB15 ↔ TON_IoT.
15. arXiv:2607.00553 (2026). Cross-Domain Generalization Failure in
    Lightweight Intrusion Detection Models for IIoT Networks. **Why:**
    reportedly ablates a single confounding feature. Check its overlap with
    our E2.3.

## Evaluation methodology

16. **Axelsson, S. (2000).** The base-rate fallacy and the difficulty of
    intrusion detection. *ACM TISSEC* 3(3). †
17. **Sommer, R. & Paxson, V. (2010).** Outside the Closed World: On Using
    Machine Learning for Network Intrusion Detection. *IEEE S&P*. †
18. **Pendlebury, F. et al. (2019).** TESSERACT: Eliminating Experimental
    Bias in Malware Classification across Space and Time. *USENIX Security*.
    † **Why:** the time-aware evaluation behind E3.4.

## Methods we may add

19. **Grinsztajn, L., Oyallon, E. & Varoquaux, G. (2022).** Why do
    tree-based models still outperform deep learning on typical tabular data?
    *NeurIPS Datasets & Benchmarks*. †
20. **Gorishniy, Y. et al. (2021).** Revisiting Deep Learning Models for
    Tabular Data (FT-Transformer). *NeurIPS*. †
21. **Hollmann, N. et al. (2025).** Accurate predictions on small data with a
    tabular foundation model (TabPFN v2). *Nature*. †
22. **Barbero, F. et al. (2022).** Transcending Transcend: Revisiting
    Malware Classification in the Presence of Concept Drift. *IEEE S&P*. †
    **Why:** conformal drift detection (E3.6).
23. **Lundberg, S. & Lee, S.-I. (2017).** A Unified Approach to Interpreting
    Model Predictions (SHAP). *NeurIPS*. †
24. **Ganin, Y. et al. (2016).** Domain-Adversarial Training of Neural
    Networks. *JMLR*. † **Sun, B. & Saenko, K. (2016).** Deep CORAL. *ECCV
    Workshops*. † **Why:** background for domain adaptation, if E3.2 grows
    beyond fine-tuning.

## Data sources

- CIC-IDS2017: unb.ca/cic/datasets/ids-2017.html
- CSE-CIC-IDS2018: registry.opendata.aws/cse-cic-ids2018 (public S3 bucket)
- LUFlow: github.com/ruzzzzz/LUFlow (Kaggle mirrors also exist)
- Improved CIC-IDS2017 / CSE-CIC-IDS2018 (DistriNet, KU Leuven): linked from
  papers 2 and 3. †confirm the download page
- NetFlow-v2 datasets: University of Queensland, linked from paper 11.
