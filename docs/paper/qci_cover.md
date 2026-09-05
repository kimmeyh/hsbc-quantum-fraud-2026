---
title: "Dirac-3 Expanded Access: The Commercial Case"
subtitle: "30,000 QPU seconds, what QCi gets back, and what we would test"
date: "September 2026"
# STATUS, NOT RENDERED: not yet sent. Team lead 2026-09-05 -- target Monday
# night 2026-09-07 so it lands Tuesday. Until the send is confirmed, this
# letter and all of docs/paper/out/qci_package/ stay LIVE and are refreshed
# with every new result. Sprint 7 (F33) completes before that date, so its
# outcome belongs here whichever way it goes.
---

# To QCi

**From**: Harold Kimmey
**Request**: 30,000 QPU seconds of Dirac-3 access
**Enclosed, all marked DRAFT**: concept proposal, appendices, frozen preregistration with its twelve amendments, generated gate report, and the hardware run plans.

We have worked together for three years. This note is written the way I would want one written to me: the commercial case first, then what else you get, then the science.

## Why this is worth 30,000 seconds to QCi

**The named account is the return.** This work is a Phase 1 entry to the 2026 Global Quantum + AI Challenge under HSBC's problem statement, judged by a panel that includes enterprise representatives. Finalists advance to a Phase 2 PoC sprint with HSBC engagement. A submission that runs on Dirac-3, names Dirac-3, and reports measured device numbers puts your hardware in front of a tier-one bank's fraud organization with an independent party doing the measuring. That is a sales conversation you cannot buy at the price of 30,000 seconds, and it is one your own marketing cannot have on your behalf.

**The cost basis is small and known.** Our measured rate is 4 to 5 seconds per fit across 37 metered fits with zero failures. 30,000 seconds is roughly 6,600 fits, and our entire campaign to date has consumed 163 seconds. We are not asking for capacity you would otherwise sell at volume; we are asking for headroom to run a grid that a free tier cannot hold.

**A credible negative is worth more to you than an uncritical positive.** We published a null against our own hypothesis. That is why the numbers in this package will survive a reviewer who wants to attack them, and it is why a later positive from the same protocol will be believed. A vendor-favourable result from a protocol nobody trusts moves no procurement decision.

**What you can reuse regardless of outcome.** Everything below is yours: the finding, the integration write-ups, the cost model, and the measured device behaviour. If our arm never beats the classical baseline, you still keep all of it.

## What else we are trying to get from the 30,000 seconds

Beyond the challenge itself, three things we cannot obtain on the free tier:

1. **A paid-tier sizing curve.** We established empirically that the free tier refuses any continuous degree-2 job above 100 variables: a 312-variable submission came back with "Number of variables '312' in problem is greater than the free-tier device limit '100'". Our frozen configuration is 91 variables, sitting under that ceiling by accident rather than design. Every scaling statement we can currently make is therefore bounded by a tier limit rather than by the device. We would like to characterise how solution quality and time behave from 100 to several thousand variables, and to publish it.
2. **The integer solver on a problem that needs it.** Our continuous formulation is convex, so a classical solve returns the global optimum in milliseconds and no solver can beat it. The problem it relaxes -- cardinality-constrained selection of weak learners -- is NP-hard and is native to Dirac-3's integer mode. That is the first experiment where your hardware is not competing against an easy classical answer.
3. **Enough repetition to characterise the stochasticity honestly.** Across 8 samples per fit, no fit has returned identical draws, and the within-fit energy spread is a median 0.019% and maximum 0.343%. That is a good number for you. With headroom we can turn it into a proper distribution across configurations and sizes rather than a footnote.

## What we found, since it bears on how CVQBoost gets configured

The first campaign showed excellent solver fidelity: hardware and an exact classical solve of the identical Hamiltonian differ by -0.0010 AUPRC with the interval containing zero, weight cosine 0.975 to 0.999, and hardware objective values always above the exact minimum, never below.

The sharper result came from the control we ran afterwards. On the frozen configuration **the solved optimum is uniform to seven decimal places**, and the apparent 0.0022 AUPRC gain over uniform weights turned out to be tie-breaking: uniform weights leave 95.3% of test rows tied on one score, weight perturbations of order 1e-07 split those ties, and average precision is rank-based. Rounding the scores back returns the metric exactly.

The cause is pool degeneracy, and it is measurable: off-diagonal Gram entries average 170,234.4 against a diagonal of 170,235, so any two weak learners agree on 99.999% of training rows. At 0.17% fraud prevalence a depth-limited tree predicts the negative class almost everywhere, and a pool of near-identical learners gives an optimizer nothing to weight.

**This is a statement about how CVQBoost is configured for extreme class imbalance, not about your hardware.** The device reproduced the exact optimum faithfully every time. The pool handed to it was the problem. We think it is worth a note in the CVQBoost documentation for anyone applying it at low prevalence, and we would rather you had it from us than from a customer who hit it silently.

We then tested the fix, in two steps, and the second one is the part we think is useful to you.

First, replacing the single family of depth-limited trees with four families (decision tree, LDA, logistic, KNN) moves the optimum genuinely off uniform: L1 distance 0.127 against 8.0e-08, largest weight 1.24 times uniform, with two controls confirming this is optimization rather than tie-breaking. It bought the optimizer something to do, but no accuracy.

Second, adding imbalance handling AT FIT TIME -- class weighting inside each weak learner as it is built, rather than reweighting the ensemble objective afterwards -- changes the pool materially: the Gram off-diagonal ratio falls from 0.9988 to 0.92. Against the same single-family pool rebuilt at the same size on the same splits, the tuned pool gains +0.0198 AUPRC on nine of ten seeds, reaching 0.7827 against Loke et al.'s reported 0.8 on your hardware. It remains below our own 0.0268 detectable threshold, so we report it as a direction with a measured mechanism rather than a win.

**The part worth your attention: the accuracy came from the learners, not the optimizer.** On the tuned pool the solved weights beat uniform weights by only +0.0043. So for CVQBoost at low prevalence, the leverage is in how the weak learners are built, and the optimization step is close to free either way. That is a configuration statement about your library rather than a limitation of your hardware, and it is the second thing we would put in the CVQBoost documentation alongside the degeneracy finding above.

## What we would test with the access

In priority order, each with a preregistered protocol already written:

1. **Cardinality-constrained selection on the integer solver**, against time-capped MIQP, greedy and annealing controls. A win against a certified-optimal classical solve is a result; a win against no control is not.
2. **The paid-tier sizing curve**, 100 to several thousand variables, published.
3. **The full ULB and IEEE-CIS grids**, which the 100-variable ceiling currently forecloses. IEEE-CIS is 590,540 transactions and several hundred features, the regime where CVQBoost's published runtime claim actually lives.
4. **Segment replication (block B4)**, 15 fits at roughly 450 seconds, and a sign-augmented QSVM block.

## What we give back

- The pool-degeneracy finding above, written up for your documentation.
- Integration notes from sustained use of eqc-models: the pool-construction strategy that fails on Windows, the response object whose billing field is not a dictionary key, the free-tier variable arithmetic and where the documentation and implementation diverge, and the guards we built around metered execution that any serious user would need.
- The measured cost model: per-fit timings consistent across 37 fits, and the solver-dispersion data above.
- Named attribution in a submission to a tier-one bank, and in whatever is published afterwards.

Two questions we would value your view on, both single-fit experiments we would run on approval. First, whether relaxation schedule 4 would close the 0.013% to 0.413% residual we see between the hardware objective and the exact minimum. Second, whether a larger sum constraint would help, given that spreading 1.0 across 91 variables puts each weight near 0.011 and may approach the analog resolution floor.

## A note on this package

Everything enclosed is DRAFT and pre-submission. The results are as measured; the preregistration and its twelve dated amendments show exactly what was decided before any result was seen, including the gate we failed and the two claims we had to correct. We would welcome correction on anything we have characterised wrongly about Dirac-3 -- especially the convexity argument and the free-tier ceiling -- before this becomes a public submission.
