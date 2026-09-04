---
title: "Appendices"
subtitle: "Quantum-Enhanced Credit Card Fraud Detection for Digital Payment Ecosystems"
author: "Claude Shannon's Fraud Catchers"
date: "September 2026"
---

# Appendix A. Results

ULB benchmark, 284,807 transactions, 1,081 exact duplicates removed before splitting, 60/20/20 stratified, seeds 42-51, test-fold prevalence 0.00167. Features are anonymized principal components plus amount and elapsed time; no merchant, device, geography or cardholder attributes exist, which bounds both feature engineering and the fairness testing a deployment would require. AUPRC is step-wise average precision throughout.

## A.1 Detection quality (mean over 10 seeds, test AUPRC)

| Arm | Features | AUPRC | Seed SD | 95% interval | AUC-ROC | Tag |
|---|---|---|---|---|---|---|
| CatBoost | 30 | 0.8368 | 0.0304 | [0.8150, 0.8585] | 0.9765 | [SIM] |
| XGBoost | 30 | 0.8296 | 0.0286 | [0.8092, 0.8501] | 0.9791 | [SIM] |
| CatBoost | 13 | 0.8070 | 0.0321 | [0.7841, 0.8300] | 0.9738 | [SIM] |
| **CVQBoost on Dirac-3** | 13 | **0.7671** | 0.0302 | [0.7455, 0.7887] | 0.9201 | **[HW]** |
| CVQBoost exact proxy | 13 | 0.7681 | 0.0312 | [0.7458, 0.7905] | 0.9210 | [SIM] |
| CVQBoost on Dirac-3, tuned pool | 9 | 0.7014 | 0.0263 | [0.6826, 0.7202] | 0.9557 | [HW] |
| Logistic regression | 30 | 0.7218 | 0.0268 | [0.7026, 0.7410] | 0.9769 | [SIM] |

Intervals measure split dispersion, not sampling error: the ten splits share the same rows and their test folds overlap. The 9-feature arm shows higher AUC-ROC but lower AUPRC because heavy score ties (A.3) depress AUC-ROC more than step-wise average precision. Every configuration uses one- and two-feature weak learners: 13 features give 13 singles plus 78 pairs, the 91 variables cited throughout.

## A.2 Operational view, with the budget ceiling stated

The test fold holds about 95 frauds in 56,746 transactions, so the 0.05% and 0.1% budgets fund 28 and 57 alerts and cap attainable recall at 0.295 and 0.600. Only the 0.5% column measures ranking rather than budget. CVQBoost figures are proxy-derived and tagged [SIM]: Dirac-3 weights were not persisted, and hardware minus proxy is -0.0010 with the interval containing zero (A.4).

| Arm | Recall @ 0.05% (cap 0.295) | Recall @ 0.1% (cap 0.600) | Recall @ 0.5% | Precision @ 0.1% |
|---|---|---|---|---|
| CatBoost, 30 features | 0.294 (99.7% of cap) | 0.593 (98.8%) | 0.855 | 0.988 |
| CatBoost, 13 features | 0.286 (96.9%) | 0.580 (96.7%) | 0.849 | 0.967 |
| CVQBoost, exact proxy [SIM] | 0.283 (95.9%) | 0.565 (94.2%) | 0.819 | 0.942 |
| Logistic regression | 0.241 (81.7%) | 0.513 (85.5%) | 0.839 | 0.854 |

## A.3 Hardware campaign and score health

27 metered fits, 120 QPU seconds, zero failures, zero retries, 4 to 5 s per fit at 25 to 91 variables; the exact classical solve takes milliseconds. The selected configuration carries a score-degeneracy warning on all ten seeds (95.1% of transactions share one score across 814 distinct values), so its threshold-dependent figures are weak evidence while its ranking metrics are sound.

| Quantity | Value | Tag |
|---|---|---|
| G0b Spearman, proxy versus hardware ranking, 5 configs | 0.900 (exact permutation p: one-sided 0.042) | [HW] |
| H1b, CVQBoost minus best matched GBDT, 10 seeds | -0.0399 [-0.0571, -0.0227], 9 of 10 seeds negative | [HW] |
| Per-seed paired BCa intervals excluding zero (proxy scores) | 6 of 10 | [SIM] |
| Solver draws per fit / fits with identical draws | 8 / 0 of 27 | [HW] |
| Within-fit energy spread, median and maximum | 0.019%, 0.343% | [HW] |

## A.4 Solver fidelity and the mechanism controls

Hardware minus exact proxy on identical Hamiltonians: -0.0010 [-0.0032, +0.0012]; solution weight cosine 0.975 to 0.999; hardware objective 0.013% to 0.413% above the exact minimum, never below [HW].

The solved weight vector is **exactly uniform** on all ten seeds (L1 distance from 1/91 is 0.000000), so we ran the controls that demands. All classical, zero metered seconds.

| Control | AUPRC | What it isolates |
|---|---|---|
| Uniform weights by construction | 0.7659 | The pool with NO optimization |
| Frozen objective, solved | 0.7681 | Optimization adds +0.0022, below the 0.0268 MDE |
| Class-weighted objective, re-solved | 0.7686 | Rules out prevalence weighting (optimum stays uniform) |
| Logistic stack, free signs | 0.7681 | Cost of the non-negative simplex form: none detectable |

The cause is pool degeneracy: off-diagonal Gram entries average 170,234.4 against a diagonal of 170,235, so any two learners agree on 99.999% of training rows, because at 0.17% prevalence a depth-limited tree predicts the negative class almost everywhere. With interchangeable learners uniform is genuinely optimal. A penalty sweep from 0 to 4 times n_train leaves the optimum uniform even at zero penalty, ruling out the penalty term. Phase 2 implication: the first requirement is pool diversity, not a better solver.

# Appendix B. Preregistration registry

## B.1 Gates, scored as committed

| Gate | Criterion | Outcome | Tag |
|---|---|---|---|
| G0 | Tuned XGBoost mean AUPRC >= 0.85 | **FAIL**: 0.8296 | [SIM] |
| G0 leakage tripwire | No cell above 0.95 | PASS: max 0.8368 | [SIM] |
| Shuffled-label tripwire | Collapses to base rate | PASS: 0.0023 vs 0.0017 | [SIM] |
| G0b | Proxy-hardware rank Spearman >= 0.5 | **PASS**: 0.900 | [HW] |
| H1b (primary) | CVQBoost versus best tuned GBDT | **NULL**: -0.0399, interval excludes zero | [HW] |
| H4 | Versus best structural control | PARTIAL: solver-fidelity component only; both preregistered controls unrun | [HW] |
| H1a, H1c, H3, H5, H6, Phase 2 cardinality arm | Various; the cardinality arm is preregistered against time-capped MIQP, greedy and annealing controls | NOT RUN | [PROJ] |

Multiplicity correction is not yet applicable: the exploratory family is incomplete.

## B.2 Amendments

A1 freeze recorded. A2 variable-count formula corrected to the build used, no bound changed. A3 full-pair pool build added with a validation-only selection rule. A4 Sprint 3 analysis code registered. A5 minimum detectable effect refined to the measured 0.0268. A6 score-health flags added. A7 protocol-sensitivity ladder added as exploratory cells, G0 unchanged, prediction persistence added. A8 review fixes: metered-spend accounting, provenance keying, gate scoring. A9 prediction-store keying corrected, affected figures retagged [SIM]. A10 hardware predictions version-controlled.

No amendment changed a gate criterion, and no gate was rescored after observation.

# Appendix C. Reproduction and references

Preregistration freeze commit `95751b9`, tag `prereg-freeze`, amendments A1 to A10. ULB dataset SHA-256 begins `76274b691b16a6c4`, with a 12-file checksum manifest. The results store holds 147 rows, each carrying a configuration hash and evidence tag; 27 QCi job identifiers are retained. Dirac-3 parameters throughout: `num_samples` 8, `relaxation_schedule` 2, `sum_constraint` 1.0, penalty 2 x n_train. Weak learners are depth-limited decision trees, one per feature and per correlation-ranked pair, emitting hard votes in {-1, +1}, with no subsampling or class weighting in the frozen configuration. Every figure regenerates from the committed repository, whose public package pins the full environment and carries the complete bibliography.

Key references: Emami et al., 2025, Financial Fraud Detection with Entropy Computing, arXiv:2503.11273. Neven et al., 2012, QBoost, the binary formulation this work relaxes. Le Borgne et al., 2022, Reproducible Machine Learning for Credit Card Fraud Detection (its AP figures are on simulated data, not used as ULB comparators). AutoXGB ULB benchmark, average precision 0.782, the like-for-like comparator our 0.8296 exceeds.
