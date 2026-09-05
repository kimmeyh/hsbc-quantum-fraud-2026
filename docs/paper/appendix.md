---
title: "Appendices: Quantum-Enhanced Credit Card Fraud Detection"
author: "Claude Shannon's Fraud Catchers"
date: "September 2026"
---

# Appendix A. Results

ULB benchmark, 284,807 transactions, 1,081 exact duplicates removed before splitting, 60/20/20 stratified, seeds 42-51, test-fold prevalence 0.00167. Features are anonymized principal components plus amount and elapsed time; no merchant, device, geography or cardholder attributes exist, which bounds both feature engineering and the fairness testing a deployment would require. The PCA transform is unpublished, so no model fitted here maps onto raw bank traffic without re-derivation. AUPRC is step-wise average precision throughout.

## A.1 Detection quality (mean over 10 seeds, test AUPRC)

| Arm | Features | AUPRC | Seed SD | 95% interval | Tag |
|---|---|---|---|---|---|
| CatBoost | 30 | 0.8368 | 0.0304 | [0.8150, 0.8585] | [SIM] |
| XGBoost | 30 | 0.8296 | 0.0286 | [0.8092, 0.8501] | [SIM] |
| CatBoost | 13 | 0.8070 | 0.0321 | [0.7841, 0.8300] | [SIM] |
| **CVQBoost on Dirac-3** | 13 | **0.7671** | 0.0302 | [0.7455, 0.7887] | **[HW]** |
| Logistic regression | 30 | 0.7218 | 0.0268 | [0.7026, 0.7410] | [SIM] |

Values are means and t-intervals across ten overlapping resplits: they describe split sensitivity, not deployment sampling error, since the splits share rows. An inferential interval needs a held-out temporal period, which Phase 2 supplies. AUC-ROC is 0.92 to 0.98 across arms and is not the operative metric at 0.17% prevalence. The exact proxy of the hardware row scores 0.7681 (within 0.001), and a tuned 9-feature pool scores 0.7014 [HW]. Every configuration uses one- and two-feature learners: 13 features give 13 singles plus 78 pairs, the 91 variables cited throughout.

## A.2 Operational view, with the budget ceiling stated

The test fold holds about 95 frauds in 56,746 transactions, so the 0.05% and 0.1% budgets fund 28 and 57 alerts, capping recall at 0.295 and 0.600. Every column is a ranking measure under a budget; only 0.5% is uncapped by the positive count. CVQBoost figures are proxy-derived [SIM]: Dirac-3 weights were not persisted (A.4).

| Arm | R@0.05% (cap .295) | R@0.1% (cap .600) | R@0.5% |
|---|---|---|---|
| CatBoost, 30 feat | .294 (99.7% of cap) | .593 (98.8%) | .855 |
| CatBoost, 13 feat | .286 (96.9%) | .580 (96.7%) | .849 |
| CVQBoost proxy [SIM] | .283 (95.9%) | .565 (94.2%) | .819 |
| CVQBoost mixed k=6 [HW] | .271 | .509 | .839 |
| Logistic regression | .241 (81.7%) | .513 (85.5%) | .839 |

## A.3 Hardware campaign and score health

37 metered fits over two campaigns, 163 device seconds, zero failures, zero retries, 4 to 5 s per fit; the classical solve takes milliseconds. The selected configuration carries a score-degeneracy warning on all ten seeds (95.1% of transactions share one score across 814 distinct values), so its threshold-dependent figures are weak evidence while its ranking metrics are sound.

| Quantity | Value | Tag |
|---|---|---|
| G0b Spearman, proxy versus hardware ranking, 5 configs | 0.900 (exact permutation p: one-sided 0.042) | [HW] |
| H1b, CVQBoost minus best matched GBDT, 10 seeds | -0.0399 [-0.0571, -0.0227], 9 of 10 seeds negative | [HW] |
| Per-seed paired BCa intervals excluding zero (proxy scores) | 6 of 10 | [SIM] |
| Solver draws per fit; identical-draw fits; within-fit energy spread | 8; 0 of 27; median 0.019%, max 0.343% | [HW] |

## A.4 Solver fidelity and the mechanism controls

Hardware minus exact proxy on identical Hamiltonians: -0.0010 [-0.0032, +0.0012]; solution weight cosine 0.975 to 0.999; hardware objective 0.013% to 0.413% above the exact minimum, never below [HW]. That agreement also bounds any effect of Dirac-3's continuous-variable resolution: quantization coarse enough to drive the flat optimum could not reproduce it. The solved weight vector is **uniform to seven decimal places** on all ten seeds (L1 from 1/91 of 7.2e-08 to 1.6e-07), so we ran the controls that demands, all classical at zero metered cost.

| Control | AUPRC | What it isolates |
|---|---|---|
| Uniform weights by construction | 0.7659 | The pool with NO optimization |
| Frozen objective, solved | 0.7681 | The +0.0022 is tie-breaking, not optimization (see below) |
| Class-weighted objective, re-solved | 0.7686 | Rules out objective weighting, not imbalance at fit time |
| Logistic stack, free signs | 0.7681 | Cost of the non-negative simplex form: none detectable |

The +0.0022 is tie-breaking. Uniform weights leave 95.3% of test rows tied on one score (78 distinct values); weights differing by order 1e-07 split those into 151, and average precision is rank-based. Rounding the solved scores to six decimals returns the metric to the uniform value (seed 42: 0.8073 solved, 0.8043 rounded, 0.8049 uniform).

**Mixed-pool test (exploratory, A11).** Four families (dct, lda, lg, knn) at **k=13, 312 variables**, identical splits: gram ratio 0.9975 vs 0.999994, L1 from uniform 0.127 vs 8.0e-08, solved-minus-uniform +0.0076 on 10/10 seeds, absolute AUPRC 0.7565, below the frozen pool's 0.7681 and below the 0.0268 MDE [SIM]. The two mechanism controls are **seed 42 only**: rounding to 2dp leaves 96 distinct scores vs uniform's 123 yet scores higher, and the shrinkage curve is monotone, so this is optimization rather than tie-breaking.

**Hardware (F32) ran a DIFFERENT, smaller configuration.** The free-tier ceiling of 100 variables (A12) forecloses k=13, so the metered block used **k=6, 60 variables**: ten fits, 43.0 device seconds, AUPRC 0.7630, hardware minus proxy -0.0007, cosine 0.977-0.983, recall 0.271/0.509/0.839 [HW]. It measures solver fidelity and supplies hardware operating points; it does NOT confirm the k=13 mechanism, which the free tier cannot run. That configuration's own mechanism is a single-seed spot check (L1 0.0204), an order of magnitude weaker.

The cause is pool degeneracy: off-diagonal Gram entries average 170,234.4 against a diagonal of 170,235, so any two learners agree on 99.999% of training rows, because at 0.17% prevalence a depth-limited tree predicts the negative class almost everywhere. With interchangeable learners uniform is genuinely optimal. A penalty sweep from 0 to 4 times n_train leaves it uniform even at zero penalty, ruling out the penalty term. Phase 2: the first requirement is pool diversity, not a better solver.

# Appendix B. Preregistration registry

## B.1 Gates, scored as committed

| Gate | Criterion | Outcome | Tag |
|---|---|---|---|
| G0 | Tuned XGBoost mean AUPRC >= 0.85 | **FAIL**: 0.8296 | [SIM] |
| G0 leakage tripwire | No cell above 0.95 | PASS: 0.8368 | [SIM] |
| Shuffled-label tripwire | Collapses to base rate | PASS: 0.0023 / 0.0017 | [SIM] |
| G0b | Proxy-hardware rank Spearman >= 0.5 | **PASS**: 0.900 | [HW] |
| H1b (primary) | CVQBoost versus best tuned GBDT | **NULL**: -0.0399, interval excludes zero | [HW] |
| H4 | Versus best structural control | PARTIAL: solver fidelity only; both controls unrun | [HW] |
| H1a, H1c, H3, H5, H6, Phase 2 cardinality arm | Cardinality arm preregistered against time-capped MIQP, greedy and annealing controls | NOT RUN | [PROJ] |

H1b is the sole confirmatory endpoint, reported unadjusted. All other completed analyses are exploratory and carry no family-wise confirmatory claim.

## B.2 Amendments

A1 freeze. A2 variable-count formula corrected. A3 full-pair build, validation-only selection. A4 analysis code registered. A5 MDE refined to 0.0268. A6 score-health flags. A7 protocol-sensitivity ladder as exploratory cells. A8 metered-spend accounting and gate scoring. A9 prediction-store keying corrected, figures retagged [SIM]. A10 hardware predictions version-controlled. A11 mixed-family pool, exploratory. A12 free-tier ceiling of 100 variables established empirically when a 312-variable job was refused server-side, correcting our inference that no device ceiling bound this work. No amendment changed a gate criterion; no gate was rescored after observation.

# Appendix C. Reproduction and references

Freeze commit `95751b9`, tag `prereg-freeze`, amendments A1 to A10. Environment: Python 3.12.10, eqc-models 0.21.0, qci-client 5.0.2, scikit-learn 1.9.0, numpy 1.26.4, scipy 1.17.1, xgboost 3.4.1, catboost 1.2.10, lightgbm 4.7.0. ULB SHA-256 begins `76274b691b16a6c4` (12-file manifest). The results store holds 147 rows, each with a configuration hash and evidence tag; 27 QCi job identifiers, raw responses and Dirac-3 parameters (`num_samples` 8, `relaxation_schedule` 2, `sum_constraint` 1.0, penalty 2 x n_train) are retained. Every figure regenerates from the repository.

References. Loke et al., 2026, CVQBoosting for card fraud, ICAART: same Dirac-3 hardware and benchmark family, AUC-PR above 0.8 with a heterogeneous pool (KNN, LDA, logistic regression, XGBoost) against our 0.767, the sharpest external evidence for A.4. Emami et al., 2025, arXiv:2503.11273: competitive AUC plus runtime scaling, so parity-plus-speed. Neven et al., 2012, QBoost. Le Borgne et al., 2022 (simulated-data AP, not a comparator). AutoXGB ULB, AP 0.782 under its own protocol: illustrative, not like-for-like.
