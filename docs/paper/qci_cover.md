---
title: "Progress Update and Phase 2 Request"
subtitle: "Dirac-3 evaluation for the 2026 Global Quantum + AI Challenge, HSBC problem statement"
date: "September 2026"
---

# Cover note for QCi

**From**: Harold Kimmey, team lead, Claude Shannon's Fraud Catchers
**Enclosed, all marked DRAFT**: concept proposal, appendices, frozen preregistration with its amendment log, generated gate report, and the hardware run plan.

## Where the work stands

We completed the first metered Dirac-3 campaign under a preregistered protocol: 27 fits, 120 QPU seconds, zero failures and zero retries, 4 to 5 seconds per fit at 25 to 91 variables. The proxy-fidelity gate passed at Spearman 0.900, so the classical stand-in we develop against is demonstrably faithful to the device.

We also measured something we think is worth QCi's attention, and it is the reason for the request below.

## The finding

On the continuous-variable formulation, hardware and an exact classical solve of the identical Hamiltonian are statistically indistinguishable: the difference is -0.0010 AUPRC with the confidence interval containing zero, solution weights agree to cosine 0.975 to 0.999, and hardware objective values sit 0.013% to 0.413% above the exact minimum, never below. That is excellent solver fidelity, and it is what the mathematics predicts: the objective is strictly convex on the simplex, so a classical solve returns the global optimum and no solver can beat it.

A regularization sweep sharpened the point. The optimum stays nearly uniform even at zero penalty, so the flatness comes from the simplex constraint over correlated weak learners rather than from regularization. On this formulation the optimization problem is close to degenerate.

We state this plainly in the submission rather than obscuring it, because it identifies precisely where the hardware is and is not the active ingredient, and because it points at the formulation where it would be.

## What we would run next, and the request

The continuous relaxation is classically solvable. The problem it relaxes is not: selecting the best sparse subset of weak learners under a cardinality constraint is NP-hard, admits no exact classical proxy, and is the native problem class for Dirac-3's integer solver. That is the Phase 2 experiment we would run first.

Also outstanding from the Phase 1 grid, all costed and specified: the full-configuration ULB block, the IEEE-CIS block with its feature-ladder cells, a segment-replication block, and a sign-augmented QSVM block. Together with the non-convex work these are the basis of our expanded-access request.

## What we can offer in return

Detailed feedback on eqc-models from sustained use, including the specific integration issues we hit and worked around: the pool-construction strategy that fails on Windows, the response object whose billing field is not a dictionary key, the free-tier variable arithmetic and where the documentation and the implementation diverge, and a set of guards we built around metered execution that others would need.

We would also share the measured cost model, since our per-fit timings are consistent across 27 fits and may be useful reference data.

## A note on this package

Everything enclosed is DRAFT and pre-submission. The results are as measured; the preregistration and its ten dated amendments show exactly what was decided before any result was seen. We would welcome correction on anything QCi believes we have characterized wrongly about Dirac-3, especially the convexity argument, before this becomes a public submission.
