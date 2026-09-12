---
title: "Appendices: Quantum-Enhanced Credit Card Fraud Detection for Digital Payment Ecosystems"
author: "Claude Shannon's Fraud Catchers | September 2026"
documentclass: article
fontsize: 10pt
geometry: "letterpaper, margin=0.9in"
header-includes: |
  \usepackage{titling}
  \setlength{\droptitle}{-11em}
  \setlength{\thanksmarkwidth}{0em}
  \usepackage{booktabs}
  \usepackage{enumitem}
  \setlist{nosep, leftmargin=*}
  \setlength{\parskip}{2pt}
  \usepackage[compact]{titlesec}
  \titlespacing*{\section}{0pt}{6pt}{3pt}
  \setlength{\parindent}{0pt}
  \setlength{\LTpre}{3pt}
  \setlength{\LTpost}{3pt}
---

Every figure regenerates from the public repository (https://github.com/kimmeyh/hsbc-quantum-fraud-2026, freeze commit 95751b9, tag `prereg-freeze`) and carries a configuration hash and an evidence tag: **[HW]** measured on Dirac-3, **[SIM]** simulated or classical, **[PROJ]** projected. The repository holds the resolved environment (experiments/requirements-lock.txt: eqc-models 0.21.0, qci-client 5.0.2, Python 3.12, Linux), both dataset checksums, the preregistration, all amendments, the results store, sixty QCi job identifiers, 48 raw device responses and the Dirac-3 parameters; the A21 probe has no identifier and no reported figure depends on it.

# A. Results

**A.1 ULB detection quality.** 284,807 transactions, 1,081 exact duplicates removed before splitting, 60/20/20 stratified, seeds 42 to 51, test-fold prevalence 0.00167. AUPRC is step-wise average precision throughout; intervals are t-intervals across ten overlapping resplits and describe split sensitivity, not sampling error.

| Arm | Features | AUPRC | Seed SD | 95% interval | Tag |
|:------------------------------|:----:|:------:|:------:|:----------------:|:---:|
| CatBoost | 30 | 0.8368 | 0.0304 | 0.8150 to 0.8585 | SIM |
| XGBoost | 30 | 0.8296 | 0.0286 | 0.8092 to 0.8501 | SIM |
| CatBoost (H1b comparator) | 13 | 0.8070 | 0.0321 | 0.7841 to 0.8300 | SIM |
| CVQBoost on Dirac-3 (frozen, 91 variables) | 13 | 0.7671 | 0.0302 | 0.7455 to 0.7887 | HW |
| Logistic regression | 30 | 0.7218 | 0.0268 | 0.7026 to 0.7410 | SIM |

The exact classical solve of the hardware row scores 0.7681; a tuned 9-feature pool scores 0.7014 [HW]. Every ULB configuration except B2 uses singles plus pairs (13 + 78 = 91 variables).

**A.2 Operational view.** About 95 frauds in 56,746 test transactions: the 0.05% and 0.1% budgets fund 28 and 57 alerts, capping recall at 0.295 and 0.600; only 0.5% is uncapped. Proxy figures are [SIM] because the first campaign did not persist Dirac-3 weights.

| Arm | R@0.05% (cap 0.295) | R@0.1% (cap 0.600) | R@0.5% |
|:---------------------------------|:---------------:|:---------------:|:------:|
| CatBoost, 30 features | 0.294 (99.7% of cap) | 0.593 (98.8%) | 0.855 |
| CatBoost, 13 features | 0.286 (96.9%) | 0.580 (96.7%) | 0.849 |
| CVQBoost proxy, 13 features [SIM] | 0.283 (95.9%) | 0.565 (94.2%) | 0.819 |
| CVQBoost mixed pool, 6 features [HW] | 0.271 | 0.509 | 0.839 |
| Logistic regression | 0.241 (81.7%) | 0.513 (85.5%) | 0.839 |

**A.3 Hardware campaign.** 61 metered fits, 1,141 device seconds, zero failures, zero retries, 4 to 92 s per fit; every fit ran relaxation_schedule 2, sum_constraint 1, num_samples 8. G0b: Spearman 0.900 over five paired configurations (exact permutation p 0.042 one-sided), a smoke test only. H1b: -0.0399 [-0.0571, -0.0227], nine of ten seeds negative [HW]; six of ten per-seed paired BCa intervals exclude zero [SIM]. Within-fit energy spread across eight draws: median 0.020%, maximum 0.343% over 48 fits [HW].

**A.4 Solver fidelity and mechanism controls.** Hardware minus exact proxy on identical Hamiltonians: -0.0010 [-0.0032, +0.0012] AUPRC; weight cosine 0.975 to 0.999 on order-2 pools (the order-3 pool reaches 0.83, B.3); hardware objective 0.013% to 0.413% above the exact minimum, never below [HW], which holds by construction against a certified convex minimum. On the frozen pool the agreement is forced rather than earned. QCi documents an effective analog resolution of about 200:1 (Emami et al. cite a 23 dB dynamic-range limit). The frozen Hamiltonian's diagonal is 510,705 while its off-diagonal entries differ by at most 20.0 and its linear terms by at most 28.0, against a resolvable difference of 2,554: no coefficient difference is visible to the device, the quantized problem's minimizer is uniform to 2e-15, and hardware returning uniform is what resolution predicts whatever the true optimum is (A31).

The frozen optimum is uniform to within 3.3e-06 to 7.4e-06 in L1 of 1/91 on all ten seeds, under a solve certified by KKT residual below 1e-9 (A26). Classical controls at zero metered cost: uniform weights 0.7659, solved 0.7687, class-weighted objective 0.7690, free-sign logistic stack 0.7681, so the simplex form costs nothing detectable and objective reweighting is ruled out. The +0.0028 is tie-breaking: 95.2% of test rows share one score and reordering within that block spans 0.0120 of AP. Cause: the unbounded trees memorise the 170,235-row fold; 80 to 84 of 91 learners reproduce the labels exactly, and zero predict the negative class everywhere (A20). At lambda = 0 the minimiser set is a face of the simplex, so the penalty selects a diffuse solution near uniform rather than being irrelevant to it (A27).

*Mixed pool (exploratory, A11).* Four families at k=13, 312 variables, same splits: L1 from uniform 0.126, solved minus uniform +0.0076 on 10 of 10 seeds, absolute AUPRC 0.7466, below the frozen pool's 0.7681 [SIM]. *Tuned pool (A13, A14, A16).* Fit-time class weighting in the tree and logistic learners (LDA and KNN accept none) plus closer distance-weighted neighbours: Gram ratio falls from 0.9988 to 0.92; selected on validation AP at seed 42, then ten seeds: AUPRC 0.7700 (SD 0.0270); against the single-family pool rebuilt at the same k=6 on the same splits, +0.0319 (SD 0.0189), 10 of 10 seeds; solved minus uniform +0.0047 (SD 0.0028). *Hardware block.* The ceiling foreclosed k=13 at the time, so the metered mixed-pool block used k=6, 60 variables: ten fits, 43.0 device seconds, AUPRC 0.7630, hardware minus proxy -0.0007, cosine 0.977 to 0.983 [HW]; it measures solver fidelity, not the k=13 mechanism.

**A.5 IEEE-CIS.** 590,540 transactions, 3 duplicates removed, 3.5% prevalence, rolling-origin evaluation over 30-day TransactionDT buckets, reduced feature recipe after Deotte with UID excluded. Evaluation periods hold 85,302 / 86,524 / 8,111 rows; headline figures are unweighted means. The shuffled-label control (permuted training labels, true evaluation labels) lands at or below the base rate on every fold; a leaking pipeline would score above it. Hyperparameters are carried from ULB as a hypothesis, so classical figures are floors.

| Arm | Mean AUPRC | Features |
|:---------------------------------|:------------------------:|:----:|
| LightGBM | 0.5739 [0.5424, 0.6293] | ~182 |
| XGBoost | 0.5028 [0.4689, 0.5260] | ~182 |
| CatBoost | 0.4795 [0.4696, 0.4927] | ~182 |
| CVQBoost tuned / frozen [SIM] | 0.0571 / 0.0523 | 6 |

*Matched-feature control.* LightGBM restricted to the same six features falls from 0.5424 to 0.0734; CVQBoost attains 85% of that ceiling (0.0621 of 0.0734, fold 0). Gram ratios 0.950 to 0.973 rule out the A.4 degeneracy mode. *H3 ladder (12 cells, proxy).* CVQBoost minus matched GBDT: -0.0169 (k=5), -0.0764 (k=9), -0.0564 (k=13), -0.1031 (k=17); slope -0.006 per feature. *The same ladder on hardware (A22).* Same pipeline, folds and 100,000-row pool subsample; only the solver differs. Twelve fits, 62 metered seconds, pairs only:

| k | Variables | AUPRC [HW] | AUPRC [SIM] | Difference |
|:--:|:---:|:------:|:------:|:-------:|
| 5 | 10 | 0.0510 | 0.0508 | +0.0002 |
| 9 | 36 | 0.0804 | 0.0806 | -0.0002 |
| 13 | 78 | 0.1172 | 0.1174 | -0.0002 |
| 17 | 136 | 0.1430 | 0.1427 | +0.0003 |

Means over three folds at prevalence 0.0368; the largest cell discrepancy is 0.0013 and errors scatter both ways (five above, five below, two exact). CVQBoost trails the matched GBDT at every rung (-0.1028 [HW] at k=17), so the gap belongs to the formulation. An earlier hardware ladder that appeared to triple CVQBoost's AUPRC had built pools on the whole fold; it was withdrawn and re-run the same day (A23).

**A.6 H6: phase representation.** Preregistered as exploratory (A18). The phase block (rank phases, train-only whitening, after Mancilla and Tagliani) is given to every arm; the reported quantity is the shift in the quantum-minus-classical delta between representations. Ten ULB seeds, pairs over every column (30 baseline, 90 with phases: 435 and 4,005 variables, built over all columns because a top-13 selection would exclude every phase column), CVQBoost via the exact proxy [SIM], zero metered seconds.

Mean delta: -0.0685 in the baseline representation, -0.0800 with phases; representation shift -0.0115, paired seed-to-seed SD 0.0135, negative on 7 of 10 seeds. The shift is 0.85 of its paired SD and 43% of the MDE; the preregistered falsifier (|shift| below the paired SD) fires. Baseline mean AP: XGBoost 0.8328, CatBoost 0.8185, trained-frequency GAM 0.7893, CVQBoost 0.7646; a GBDT set the bar in all 20 cells, so the twins changed what "best classical" means, not the number (GBDT figures sit below A.1 because every arm takes a fixed 30-column budget). A twin-budget handicap under the phase block can only raise the delta; the shift comes from CVQBoost falling further (0.7646 to 0.7513) than the GBDT bar (0.8331 to 0.8313).

# B. Preregistration registry

**B.1 Gates, scored as committed.**

| Gate and criterion | Outcome | Tag |
|:----------------------------------------------|:------------------------------------------------------|:------:|
| G0: tuned XGBoost mean AUPRC >= 0.85 | FAIL: 0.8296; halt rule not honoured, deviation A28 | SIM |
| G0 leakage tripwire: no cell above 0.95 | PASS: 0.8368 | SIM |
| Shuffled-label tripwire: collapses to base rate | PASS: 0.0023 / 0.0017 | SIM |
| G0b: proxy vs hardware Spearman >= 0.5 | PASS: 0.900 | HW |
| H1b (primary): CVQBoost vs matched GBDT | NULL: -0.0399, interval excludes zero | HW |
| H4: vs best structural control | PARTIAL: solver fidelity only; committed controls unrun | HW |
| H3: feature ladder closes the gap? | NO: slope -0.006 per feature; hardware within 0.0013 of proxy | SIM+HW |
| H6: phase representation moves the delta? | NO: shift -0.0115, falsifier fired | SIM |
| H1a, H1c, H5, cardinality arm | NOT RUN (vs MIQP, greedy, annealing controls) | PROJ |

H1b is the sole confirmatory endpoint, reported unadjusted; all else is exploratory. The compound falsification criterion (H1b null, H3 slope non-positive, H5 non-transfer) has two of three conditions fired and H5 unrun.

**B.2 Amendments.** Thirty-two dated amendments, A1 to A32, each with rationale and approval, in the repository. Cited here: A11 to A18 register exploratory arms; A12 the free-tier 100-variable ceiling; A17 every A11/A13 figure recomputed after three fold builders skipped deduplication, moving the tuned-pool result from below to above the MDE; A20 memorisation, not majority-class collapse; A21 the ceiling was a billing tier; A22/A23 the hardware ladder published, withdrawn, re-run; A26 the comparator certified by KKT residual; A27 two mechanism claims withdrawn; A28 two protocol deviations including the G0 halt; A31 frozen-pool agreement forced by resolution; A32 the linear-term spread in A31 corrected. No amendment changed a gate criterion; no gate was rescored after observation.

**B.3 B2, the largest metered configuration.** Top-17 features, order-3 pool, 833 continuous variables against B1's 91; foreclosed by A12 until A21, run on 2026-09-10. Eleven fits, 906 metered seconds: ten stratified seeds plus the temporal protocol. Ten-seed means: B2 (833 variables) 0.7928 AUPRC (SD 0.0296), AUC-ROC 0.9423 [HW]; B1 frozen (91 variables) 0.7671 [HW]; CatBoost, all features, 0.8368 [SIM]. Temporal protocol: 0.7605 AUPRC, 0.9261 AUC-ROC [HW]. Paired on identical seeds, B2 minus B1 is +0.0256, 95% CI [+0.0203, +0.0310], 10 of 10 seeds (unpaired it hides inside a seed SD of 0.028). k (13 to 17) and subset order (2 to 3; three-feature learners are 680 of the 833 variables) moved together, so a larger, richer pool scores better; the ceiling alone is not shown to have cost 0.0256. The disconfirming cell, k=17 at order 2 (153 variables), is Phase 2 experiment 1. The objective stays convex: a three-feature tree is still one variable emitting a vector in {-1, +1}, and on B2's own pool the smallest eigenvalue of J = HH^T + lambda I is exactly lambda (A27). The device solves this block less faithfully: weight cosine 0.8192 to 0.8327 (mean 0.8272) against 0.9747 to 0.9825 for order-2 cells, and the recomputed objective sits 191.5 above the classical minimum. The cause is resolution: at sum constraint 1 the device resolves about 0.005 per weight, a diffuse optimum over 833 learners averages 0.0012, every fit returned exact zeros, and printed nonzero weights run 0.0007 to 0.0029. The 0.83 cosine measures a device solving a sparsified version of the problem, which is why cardinality-constrained selection is the Phase 2 direction. Score health: mode share 0.857 over 4,412 distinct values (B1: 0.951 over 814); the tie block sits at the bottom of the range, so AUPRC ambiguity is 0.0009 against 0.0804 for AUC-ROC, and only AUPRC is sound here.

**C. References.** (1) Loke et al., Improving Credit Card Transaction Fraud Detection Using CVQBoosting, ICAART 2026, DOI 10.5220/0014628400004052. (2) Emami et al., Financial Fraud Detection with Entropy Computing, arXiv:2503.11273. (3) Nguyen et al., Entropy computing, a paradigm for optimization in open photonic systems, Communications Physics 8, 411 (2025), arXiv:2407.04512; critical comment arXiv:2605.03612. (4) Mancilla and Tagliani, The Fourier Wall, arXiv:2607.15815. (5) Deotte, XGB Fraud with Magic, Kaggle (2019); Yakovlev and Deotte, IEEE-CIS 1st place write-up (2019). (6) FCA FG22/5, Consumer Duty guidance (2022), paras 5.12, 1.27 to 1.28, chapter 11; Equality Act 2010. (7) QCi Dirac-3 documentation. Datasets: MLG-ULB Credit Card Fraud Detection; IEEE-CIS Fraud Detection (Kaggle).
