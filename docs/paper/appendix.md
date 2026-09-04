---
title: "Appendices"
subtitle: "Quantum-Enhanced Credit Card Fraud Detection for Digital Payment Ecosystems"
author: "Claude Shannon's Fraud Catchers"
date: "September 2026"
---

# Appendix A. Results

All figures from a single results store; every row carries an evidence tag and a configuration hash. ULB benchmark, 284,807 transactions, 1,081 exact duplicates removed before splitting, 60/20/20 stratified, seeds 42-51, test-fold prevalence 0.00167. The benchmark's features are anonymized principal components (V1 to V28) plus transaction amount and elapsed time; no merchant, device, geography, or cardholder attributes are present, which bounds both the feature engineering possible here and the fairness testing that a deployment would require. AUPRC is step-wise average precision throughout, never a trapezoidal approximation.

## A.1 Detection quality by arm

| Arm | Features | Mean AUPRC | Seed SD | 95% t-CI | Mean AUC-ROC | Tag |
|---|---|---|---|---|---|---|
| CatBoost | all 30 | 0.8368 | 0.0304 | [0.8150, 0.8585] | 0.9765 | [SIM] |
| XGBoost | all 30 | 0.8296 | 0.0286 | [0.8092, 0.8501] | 0.9791 | [SIM] |
| LightGBM | all 30 | 0.8240 | 0.0295 | [0.8029, 0.8451] | 0.9788 | [SIM] |
| CatBoost | matched 13 | 0.8070 | 0.0321 | [0.7841, 0.8300] | 0.9738 | [SIM] |
| LightGBM | matched 13 | 0.8024 | 0.0274 | [0.7828, 0.8220] | 0.9726 | [SIM] |
| XGBoost | matched 13 | 0.8019 | 0.0239 | [0.7847, 0.8190] | 0.9730 | [SIM] |
| **CVQBoost on Dirac-3** | matched 13 | **0.7671** | 0.0302 | [0.7455, 0.7887] | 0.9201 | **[HW]** |
| CVQBoost exact proxy | matched 13 | 0.7681 | 0.0312 | [0.7458, 0.7905] | 0.9210 | [SIM] |
| CVQBoost on Dirac-3, tuned pool | matched 9 | 0.7014 | 0.0263 | [0.6826, 0.7202] | 0.9557 | [HW] |
| Logistic regression | all 30 | 0.7218 | 0.0268 | [0.7026, 0.7410] | 0.9769 | [SIM] |

The tuned-pool row uses 9 features and is not a like-for-like comparison with the matched-13 rows; it is included because it is the configuration with a healthy score distribution (see A.4).

## A.2 Operational view: fraud caught within a fixed review budget

Review capacity is a policy input set by analyst headcount, not a model property. Mean over ten seeds. The CVQBoost row is computed from the exact classical proxy, tagged [SIM]: hardware solution weights were not persisted during the Sprint 4 campaign, so per-transaction hardware scores are unavailable without further metered time. Hardware and proxy are measured as indistinguishable in aggregate (A.3), which supports the substitution but does not make it a hardware measurement.

| Arm | Recall @ 0.05% | Recall @ 0.1% | Recall @ 0.5% | Precision @ 0.1% |
|---|---|---|---|---|
| CatBoost, all features | 0.294 | 0.593 | 0.855 | 0.988 |
| XGBoost, all features | 0.291 | 0.588 | 0.856 | 0.981 |
| LightGBM, all features | 0.289 | 0.587 | 0.853 | 0.979 |
| CVQBoost, exact proxy [SIM] | 0.283 | 0.565 | 0.819 | 0.942 |
| Logistic regression | 0.241 | 0.513 | 0.839 | 0.854 |

Expected cost relative to alerting nothing, at the 0.1% budget, is monotone in the same order across cost ratios of 20, 50, and 100 (missed fraud versus false positive). The cost ratio is swept rather than fixed because its value is institution-specific.

## A.3 Hardware campaign

Twenty-seven metered Dirac-3 fits, 120 QPU seconds billed, zero failures, zero retries, 4 to 5 seconds per fit at 25 to 91 variables.

| Quantity | Value | Tag |
|---|---|---|
| G0b: Spearman(proxy rank, hardware rank), 5 configs | 0.900 (p = 0.037) | [HW] |
| H1b: CVQBoost minus best matched GBDT, 10 seeds | -0.0399, CI [-0.0571, -0.0227] | [HW] |
| Per-seed paired BCa intervals excluding zero (proxy scores) | 6 of 10 | [SIM] |
| Hardware minus exact proxy, identical Hamiltonians | -0.0010, CI [-0.0032, +0.0012] | [HW] |
| Solution weight cosine, hardware versus exact proxy | 0.975 to 0.999 | [HW] |
| Hardware objective above the exact minimum, relative | 0.013% to 0.413% | [HW] |

The last three rows are the solver-fidelity component of the structural-attribution hypothesis. The two preregistered structural controls (tuned-penalty non-negative ridge, and a sparse variant) have not been run, so that hypothesis is reported as partial rather than scored.

## A.4 Score-distribution health

The selected configuration carries a degeneracy warning on all ten seeds: the modal score covers 95.1% of transactions across 814 distinct values. Ranking metrics handle ties correctly, but its alert-budget precision and calibration figures are weaker evidence than the AUPRC. The tuned 9-feature pool is health-clean (modal share 51.8%, approximately 4,000 distinct scores) and scores lower. Both are reported.

## A.5 Regularization sweep

Validation AUPRC across penalty multipliers 0, 0.001, 0.01, 0.1, 0.5, 1, 2, 4 varies only within 0.7207 to 0.7216, and the solution stays uniform (all 91 weights active, maximum weight 0.0110 against a uniform 0.0110) even at zero penalty. The near-degenerate optimum is therefore a property of the simplex constraint over correlated weak learners, not of the penalty term.

# Appendix B. Preregistration registry

The protocol was frozen before any result was observed. Changes exist only as dated amendments.

## B.1 Gates and hypotheses, scored as committed

| Gate | Criterion | Outcome | Tag |
|---|---|---|---|
| G0 | Tuned XGBoost mean AUPRC >= 0.85 | **FAIL**: 0.8296 | [SIM] |
| G0 leakage tripwire | No cell above 0.95 AUPRC | PASS: max 0.8368 | [SIM] |
| Shuffled-label tripwire | Collapses to base rate | PASS: 0.0023 vs 0.0017 | [SIM] |
| G0b | Proxy-hardware rank Spearman >= 0.5 | **PASS**: 0.900 | [HW] |
| H1b (primary) | CVQBoost versus best tuned GBDT | **NULL**: -0.0399, CI excludes zero | [HW] |
| H1a, H1c, H3, H5, H6 | Various | NOT RUN | [PROJ] |
| H4 | Versus best structural control | PARTIAL: solver-fidelity component only | [HW] |

Multiplicity correction across exploratory cells is not yet applicable because the exploratory family is incomplete.

## B.2 Amendment log

| ID | Date | Change |
|---|---|---|
| A1 | 2026-08-30 | Freeze recorded with commit hash and tag |
| A2 | 2026-09-02 | Variable-count formula corrected to the build actually used; documented device limit cited. No bound changed |
| A3 | 2026-09-02 | Full-pair pool build added as a preregistered side-by-side option with a validation-only selection rule |
| A4 | 2026-09-02 | Sprint 3 analysis-code additions registered |
| A5 | 2026-09-02 | Minimum detectable effect refined to the measured paired value 0.0268 |
| A6 | 2026-09-03 | Score-distribution health flags added to the metrics output |
| A7 | 2026-09-03 | Protocol-sensitivity ladder added as labeled exploratory cells; G0 unchanged. Prediction persistence added as the enabling change |
| A8 | 2026-09-04 | Review-fix registration: metered-spend accounting, provenance keying, and gate-scoring corrections |
| A9 | 2026-09-04 | Prediction-store keying corrected after adversarial review found hardware and proxy predictions colliding on a shared configuration hash; affected figures retagged [SIM] |
| A10 | 2026-09-04 | Hardware prediction artifacts version-controlled: regeneration cost, not file size, decides what is tracked |

No amendment changed a gate's pass criterion, and no gate was rescored after observation.

## B.3 Statistical procedures

AUPRC as step-wise average precision; stratified bias-corrected accelerated bootstrap with 2,000 resamples; paired comparisons on identical resample indices; across-seed t-intervals as the primary decision rule; Wilson intervals for precision and recall; equal-mass binned calibration error; prevalence reported beside every AUPRC; no cross-dataset averaging.

# Appendix C. Reproduction and references

## C.1 Reproduction

A public reproducibility package accompanies this submission containing the frozen preregistration with its amendment log, the analysis code, the results store with every configuration hash, and the generated gate report. Environment versions are pinned. Dataset files are not redistributed; a checksum manifest identifies them exactly.

Every quantitative claim in this proposal resolves to a row in that results store by configuration hash.

## C.2 Selected references

Full bibliography accompanies the reproducibility package.

- QCi, CVQBoost and Dirac-3 entropy computing: formulation and profiling reports.
- Chancellor et al., 2025, financial fraud detection with entropy computing.
- Neven et al., 2012, QBoost: the original binary formulation this work relaxes.
- Le Borgne, Siblini, Lebichot, Bontempi, 2022, Fraud Detection Handbook: metric discipline for imbalanced fraud data.
- Caro et al., 2022, generalization in quantum machine learning from few training data.
- Dal Pozzolo et al., ULB benchmark provenance and protocol.
