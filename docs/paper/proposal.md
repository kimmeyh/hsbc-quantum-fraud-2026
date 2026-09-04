---
title: "Quantum-Enhanced Credit Card Fraud Detection for Digital Payment Ecosystems"
subtitle: "A preregistered evaluation with measured hardware evidence and a production-trial path"
author: "Claude Shannon's Fraud Catchers"
date: "September 2026"
---

# 1. Problem framing

Card fraud detection is not an offline accuracy contest. It is a decision made under two hard constraints: a fixed review capacity, because analysts can only work so many alerts a day, and an asymmetric cost, because a missed fraud costs a chargeback while a false positive costs a good customer. At the fraud rates of real portfolios, around 0.17% in the benchmark used here, a model that optimizes accuracy is worthless and a model that optimizes ranking is only useful if its ranking holds at the top of the list, where the review budget actually binds.

HSBC's problem statement asks whether quantum methods can improve detection in digital payment ecosystems. We took that question literally and built the apparatus to answer it in the form a bank could act on: a working classical detector, a quantum-inspired candidate evaluated against it under a protocol frozen before any result was seen, and a measured verdict reported in both directions.

This proposal states what we built, what we measured on real quantum hardware, what the measurement means, and what a 90-day production trial would run.

# 2. Technical approach

**Paradigm**: hybrid classical plus quantum-inspired. The quantum component is CVQBoost on QCi's Dirac-3 entropy-computing optimizer, a continuous-variable quantum-inspired solver. A gate-based Amazon Braket arm is specified as a Phase 2 plan, not claimed as executed work.

**The system.** A tuned gradient-boosted ensemble (XGBoost, LightGBM, CatBoost, each given an equal 100-trial Optuna budget) is the production detector. CVQBoost is the evaluated candidate: it trains a pool of weak classifiers on one-, two-, and three-feature subsets, then selects ensemble weights by minimizing a quadratic objective on the simplex, which Dirac-3 solves natively. A third arm, the exact classical solve of the identical objective, serves as a structural control.

**The protocol is the contribution.** Before running anything we froze a preregistration: hypotheses, gates with numeric pass criteria, splits, seeds, metrics, statistical procedures, and the hardware budget. Changes since the freeze exist only as eight dated amendments, each with its rationale and approval, published in Appendix B. Concretely this means: gates are scored as committed even when they fail; every number carries an evidence tag ([HW] measured on hardware, [SIM] simulated or classical, [PROJ] projected); every number traces to a results record by configuration hash; leakage controls are enforced in code paths rather than by review; and a shuffled-label control confirms the pipeline collapses to chance when the signal is removed.

That discipline is why the results below can be trusted in the direction that is inconvenient for us.

# 3. What we measured

All figures: ULB benchmark, 284,807 transactions, 1,081 exact duplicates removed before splitting, 60/20/20 stratified, ten seeds, test-fold prevalence 0.00167. Full tables in Appendix A.

**Classical baselines are clean and strong.** CatBoost leads at 0.8368 AUPRC [SIM] (95% CI 0.8150 to 0.8585), with XGBoost and LightGBM within 0.013. The shuffled-label control collapses to 0.0023 against a base rate of 0.0017, and no cell approaches the 0.95 threshold that signals leakage.

**Gate G0 failed as committed.** Our preregistered floor of 0.85 AUPRC for tuned XGBoost was not met: 0.8296 [SIM]. We report it as a failure. Subsequent primary-source research found that the 0.85 to 0.88 band we had adopted is not corroborated: its probable origin computes an optimistic trapezoidal area, trains on 90% of the data with no held-out test fold, and retains duplicates. Clean-protocol equivalents fall near 0.80, and a benchmark using the same step-wise metric we use reports 0.78. We exceed both. The gate still reads FAIL, because moving a threshold after seeing the result is exactly what preregistration exists to prevent.

**Gate G0b passed on hardware.** Twenty-seven metered Dirac-3 fits, 120 QPU seconds, zero failures and zero retries. Ranking agreement between the classical proxy and hardware on validation AUPRC across the five preregistered configurations: Spearman 0.900 [HW], p = 0.037. Two qualifications we state rather than leave for a reader to find: n = 5 makes the interval wide, and the design deliberately includes two deliberately poor anchor configurations, one of which returns a constant score, which inflates a rank correlation. Restricted to the three competitive configurations the coefficient is 0.5, exactly at the gate. The gate passes as committed; we treat it as evidence that the proxy tracks the device, not as proof of tight numerical agreement.

**The primary hypothesis returned a null.** CVQBoost on Dirac-3 trails the best matched-feature GBDT by 0.0399 AUPRC [HW] (CI -0.0571 to -0.0227), beyond our minimum detectable effect of 0.0268, trailing on nine of ten seeds. Six of ten per-seed paired bootstrap intervals exclude zero, all in the same direction.

**Why, precisely.** The CVQBoost objective is a convex quadratic on the simplex, and empirically near-degenerate: the classical solve returns a global optimum that the quantum solver can match but not exceed. We measured this rather than asserting it: hardware minus exact proxy is -0.0010 AUPRC [HW] with the interval containing zero, solution weights agree to cosine 0.975 to 0.999, and and hardware objective values are always above the exact minimum, never below, by margins of 0.013% to 0.413% of the objective value. A regularization sweep then showed the optimum stays nearly uniform even at zero regularization, so the flatness comes from the simplex constraint over correlated weak learners, not from the penalty term. On this formulation the optimization problem is close to degenerate, which is why any solver reproduces it.

This is a negative result about one formulation, not about the approach. It also tells us exactly where to look next.

**In operational terms the gap is smaller than the metric suggests.** At a 0.1% review budget the tuned CatBoost catches 59.3% of test-fold fraud; the CVQBoost arm catches 56.5% [SIM], a 2.8 point difference. At a 0.5% budget the figures are 85.5% and 81.9%, a 3.6 point difference. These operating points are computed from the exact classical proxy, not from hardware: Dirac-3 solution weights were not persisted during the Sprint 4 campaign, so per-transaction hardware scores cannot be recovered without spending further metered time. The substitution is licensed by measurement rather than assumption, since hardware and proxy differ by -0.0010 AUPRC with the interval containing zero, but the tag is [SIM] and stays [SIM] until a hardware run persists its predictions.

# 4. Production trial and expected impact

The apparatus above is what a bank would need before piloting anything, so we specify the pilot rather than gesture at it.

**A 90-day shadow-mode trial.** Days 1-30: the tuned classical ensemble scores live traffic in shadow, deciding nothing, while its alerts are compared against the incumbent's on the same transactions. The comparison metric is the one the fraud team already uses, fraud caught within the standing review budget, not AUPRC. Days 31-60: champion/challenger, with the challenger taking a small routed share of decisions under a rollback trigger tied to precision at the alert budget. Days 61-90: the quantum-inspired arm enters the same shadow track as a specialist candidate, evaluated on the segments identified in Phase 2 rather than on aggregate performance.

**What the trial must satisfy to proceed.** Latency: real-time scoring budgets are in the low tens of milliseconds, which the classical ensemble meets and which the CVQBoost arm meets trivially at inference, since inference is a weighted vote over small classifiers; the quantum solve happens at training time only. Calibration: the downstream rules engine consumes a score, so the model ships with a fitted calibration layer and reliability diagrams, reported here with equal-mass binning. Drift: fraud patterns decay in weeks, so the trial defines retraining triggers on population stability and on precision-at-budget degradation rather than on a fixed calendar. Our own temporal check is a warning worth naming precisely. On a single time-ordered split the two configurations swapped places: the configuration we selected fell from 0.7671 to 0.7095 AUPRC, while the configuration we rejected rose from 0.7014 to 0.7776 [HW]. One split proves nothing and we claim nothing from it, but it points the wrong way for our own choice, and establishing which configuration survives time ordering is the first thing the trial should measure.

**Explainability, which is the bar that actually gates adoption.** A CVQBoost ensemble is a weighted vote over classifiers that each read one to three named features, so a decision decomposes into exact arithmetic terms rather than a post-hoc approximation. We measured this on a real flagged fraud: the score is the sum of per-learner contributions, each naming its feature pair and its weight. The honest counterpart, also measured: at the current configuration weight is spread widely, taking 46 of 91 learners to reach half the total, so the explanation is exact but long. A sparser formulation would shorten it, which is one more reason it is the Phase 2 direction.

**Two requirements we have not yet met, stated rather than omitted.** Fairness and disparate-impact testing across protected characteristics is a regulatory precondition in UK retail banking and is absent from this work; the benchmark's anonymized features make it untestable here, and it becomes a first-class requirement the moment real customer data is in scope. Label latency is the second: chargeback labels arrive weeks after the transaction, so the trial's evaluation window must account for censored labels rather than treating recent unlabeled transactions as legitimate.

**Expected impact.** Under the trial's own metric, the decision is whether a candidate arm raises fraud caught within a fixed analyst budget. Our current measurement says the classical ensemble is the detector to deploy today, the quantum-inspired arm is within three percentage points of caught fraud without yet having its best formulation, and the routing architecture that would combine them is specified rather than speculative.

# 5. Hybrid integration

The deployed shape is a classical detector with a quantum-inspired specialist behind a router. The classical ensemble scores every transaction. The specialist is invoked on the segments where it is measured to help, at training-time cost only, since its inference is a linear vote. The quantum hardware sits at training and model-selection time, where its solve is a single call of a few seconds, not in the transaction path. This division is why the hybrid is deployable at all: nothing in the live path depends on a quantum device being reachable.

# 6. Phase 2 program

Four levers remain open, each with a preregistered test already written.

**Representation.** Quantum feature engineering, applied identically to every arm with order-matched classical twins, tests whether a phase-based representation shifts the quantum-minus-classical difference. The twins matter: omitting them is how apparent quantum wins are manufactured.

**Segment specialization.** Prior measured work found in-segment wins for this model family; the preregistered test replicates them with seeds and confidence intervals, then tests transfer to fraud segments defined a priori, with a matched random-segment control.

**Scale and sparsity.** The IEEE-CIS regime, with 590,540 transactions and several hundred features, is where the model form has room to differ, and it is where the feature-ladder dose-response test lives.

**The formulation where quantum optimization is necessary.** Our convexity result is the strongest argument for the next experiment: the continuous relaxation is classically solvable, so the interesting problem is the combinatorial one it relaxes. Choosing the best sparse subset of weak learners under a cardinality constraint is NP-hard, admits no exact classical proxy, and is the native problem class for Dirac-3's integer solver. That is the Phase 2 experiment we would run first, and the reason hardware access matters to it.

We also disclose a constraint honestly: the 13-feature configurations used here were sized to a free-tier variable limit, not to the problem. Production sizing is the reverse, and the corrected variable arithmetic in Appendix B gives the bounds.

# 7. Team capability

Solo entry led by Harold Kimmey, with Claude Code disclosed as an AI development tool used throughout under the team lead's direction and approval.

Directly relevant measured experience: prior Dirac-3 hardware campaigns using this model family, including the tuned configuration that seeds this work; quantum machine learning explainability work; near-expert AWS experience with hands-on Amazon Braket, which is why the Phase 2 gate-based arm is a credible plan rather than an aspiration; and a prior quantum-computing challenge entry.

Honest gaps: this is a solo entry, so throughput is the binding constraint, and the Phase 2 program is scoped accordingly.
