---
title: "Progress Update and Phase 2 Request"
subtitle: "Dirac-3 evaluation for the 2026 Global Quantum + AI Challenge, HSBC problem statement"
date: "September 2026"
---

# Cover note for QCi

**From**: Harold Kimmey, team lead, Claude Shannon's Fraud Catchers
**Enclosed, all marked DRAFT**: concept proposal, appendices, frozen preregistration with its amendment log, generated gate report, and the hardware run plan.

## Where the work stands

We completed the first metered Dirac-3 campaign under a preregistered protocol: 27 fits, 120 metered device seconds, zero failures and zero retries, 4 to 5 seconds per fit at 25 to 91 variables. The proxy-fidelity gate passed at Spearman 0.900, so the classical stand-in we develop against is demonstrably faithful to the device.

We also measured something we think is worth QCi's attention, and it is the reason for the request below.

## The finding

On the continuous-variable formulation, hardware and an exact classical solve of the identical Hamiltonian are statistically indistinguishable: the difference is -0.0010 AUPRC with the confidence interval containing zero, solution weights agree to cosine 0.975 to 0.999, and hardware objective values sit 0.013% to 0.413% above the exact minimum, never below. That is excellent solver fidelity, and it is what the mathematics predicts: the objective is strictly convex on the simplex, so a classical solve returns the global optimum and no solver can beat it.

The sharper result came from a control we ran afterwards. **The solved optimum is uniform to seven decimal places**: 1/91 on every learner, with an L1 distance from uniform between 7.2e-08 and 1.6e-07 across all ten seeds. Scoring the same pool with uniform weights by construction gives 0.7659 AUPRC against the solved 0.7681, and that residual 0.0022 is not a gain either: uniform weights leave 95.3% of test rows tied on one score, and perturbations of order 1e-07 split those ties, raising the distinct-score count from 78 to 151. Average precision is rank-based, so it moves; rounding the solved scores back to six decimals returns the metric to the uniform value. On this configuration neither Dirac-3 nor the classical solver is doing useful work at all.

The cause is pool degeneracy, and we can be specific: off-diagonal Gram entries average 170,234.4 against a diagonal of 170,235, so any two weak learners agree on 99.999% of training rows. At 0.17% fraud prevalence a depth-limited tree predicts the negative class almost everywhere, and a pool of near-identical learners gives an optimizer nothing to weight. We initially attributed the flatness to the simplex constraint; a class-weighted re-solve and a uniform-weight control show that was wrong, and we have corrected it. We note the scope of that control precisely: it rules out weighting in the ensemble objective, not imbalance handling during weak-learner fitting, which is a different intervention.

Loke et al. (ICAART 2026) point the same way from the other direction. Running CVQBoost on Dirac-3 against the same benchmark family with a heterogeneous pool of k-nearest neighbours, linear discriminant analysis, logistic regression and XGBoost, they report mean AUC-PR above 0.8 where our single-family pool of depth-limited trees gives 0.767. We read that as independent evidence that pool construction, not the solver, is the binding constraint on this problem.

This matters for QCi because it is a statement about how CVQBoost is configured for extreme class imbalance, not about the hardware. The device reproduced the exact optimum faithfully. The pool handed to it was the problem.

## What we would run next, and the request

The continuous relaxation is classically solvable. The problem it relaxes is not: selecting the best sparse subset of weak learners under a cardinality constraint is NP-hard in general and is the native problem class for Dirac-3's integer solver. That is the Phase 2 experiment we would run first, against time-capped MIQP, greedy and annealing controls, since NP-hardness bears on worst-case general instances and does not by itself establish an advantage on the finite instances we would test.

Also outstanding from the Phase 1 grid, all costed and specified: the full-configuration ULB block, the IEEE-CIS block with its feature-ladder cells, a segment-replication block, and a sign-augmented QSVM block. Together with the non-convex work these are the basis of our expanded-access request.

## What we can offer in return

Detailed feedback on eqc-models from sustained use, including the pool-degeneracy result above, which we believe is worth a note in the CVQBoost documentation for anyone applying it at low prevalence, and the specific integration issues we hit and worked around: the pool-construction strategy that fails on Windows, the response object whose billing field is not a dictionary key, the free-tier variable arithmetic and where the documentation and the implementation diverge, and a set of guards we built around metered execution that others would need.

We would also share the measured cost model, since our per-fit timings are consistent across 27 fits, along with the solver-dispersion data: across 8 samples per fit, no fit returned identical draws, and the within-fit energy spread has a median of 0.019% and a maximum of 0.343%.

Two questions we would value QCi's view on. First, whether relaxation schedule 4 would close the 0.013% to 0.413% residual we see between the hardware objective and the exact optimum, since the published schedules differ in accumulated photons and success probability. Second, whether a larger sum constraint would help, given that spreading 1.0 across 91 variables puts each weight near 0.011 and may approach the analog resolution floor. Both are single-fit experiments we would run on approval.

## A note on this package

Everything enclosed is DRAFT and pre-submission. The results are as measured; the preregistration and its ten dated amendments show exactly what was decided before any result was seen. We would welcome correction on anything QCi believes we have characterized wrongly about Dirac-3, especially the convexity argument, before this becomes a public submission.
