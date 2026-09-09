---
title: "Dirac-3 Expanded Access: The Commercial Case"
subtitle: "30,000 QPU seconds, what QCi gets back, and what we would test"
date: "September 2026"
# STATUS, NOT RENDERED: not yet sent. Team lead 2026-09-07 -- the send moves
# to Sprint 9; the 2026-09-07 target is superseded. Until the send is
# confirmed, this letter and all of docs/paper/out/qci_package/ stay LIVE and
# are refreshed with every new result. QCi has seen no version of this, so it
# reads as a first proposal: no revision notes, no "since drafting".
---

# To QCi

**Request**: 30,000 QPU seconds of Dirac-3 access
**Enclosed, all marked DRAFT**: concept proposal, appendices, frozen preregistration with its twenty-one amendments, generated gate report, the hardware run plans, and the eqc-models integration feedback.

## Our goal in participating

We are exploring whether quantum computing can produce better fraud
predictions in a hybrid classical/quantum design, and we intend to follow that
wherever it leads. We believe Dirac-3 and eqc-models are a likely candidate,
and we want to find out how far predictions can be pushed with them. That is
the exploration; the analysis is what we publish either way.

## Why this is worth 30,000 seconds to QCi

A copy of the repository contents for the 2026 Global Quantum + AI Challenge,
HSBC's credit-card fraud problem, and specifically:

- **Your hardware named and measured in front of a tier-one bank**, by an
  independent party, with finalists advancing to a Phase 2 PoC with HSBC.
- **A CVQBoost configuration finding you can put in your documentation**: at
  low prevalence a single-family pool is degenerate and the optimizer has
  nothing to weight.
- **A validated classical proxy for the Dirac-3 CVQBoost path**, usable as a
  regression oracle and as a way for customers to size a problem before
  spending.
- **A measured cost model and integration notes** from 37 metered fits and five
  weeks of sustained use, enclosed as a document rather than a promise.

## What else we are trying to get from the 30,000 seconds

Three things we cannot obtain on the free tier:

1. **A paid-tier sizing curve.** The free tier refuses any continuous degree-2
   or degree-3 job above 100 variables, and several points of our analysis
   require more than 100. We have run degree-3 work on Dirac-3 before, on a
   paid account, for the full Fourier Wall and SPECTRA analysis -- so this is
   not a first attempt, it is the same work on a problem the free tier cannot
   hold. We want to characterise how solution quality and time behave from 100
   to several thousand variables, and publish it.
2. **The integer solver on an analysis that needs it.** Our continuous
   formulation is convex, so a classical solve returns the global optimum in
   milliseconds and no solver can beat it; the cardinality-constrained problem
   it relaxes is NP-hard and native to Dirac-3's integer mode.
3. **Phase 2 datasets are much larger and will need more seconds.**
   1. We have optimised usage with a proxy algorithm that does all setup and
      testing classically, at zero metered cost.
   2. Our estimates come from actual measured usage rather than from
      projection, so they are as close as we can reasonably make them.
   3. We commit to spending the seconds on this challenge and returning any
      unused balance at the end of it.

## The commercial case, in more detail

**The named account is the return.** This work is a Phase 1 entry to the 2026
Global Quantum + AI Challenge under HSBC's problem statement, judged by a panel
that includes enterprise representatives. A submission that runs on Dirac-3,
names Dirac-3, and reports measured device numbers puts your hardware in front
of a tier-one bank's fraud organization with an independent party doing the
measuring. That is a sales conversation you cannot buy at the price of 30,000
seconds, and one your own marketing cannot have on your behalf.

**The cost basis is small and known.** Our measured rate is 4 to 5 seconds per
fit across 37 metered fits with zero failures. 30,000 seconds is roughly 6,600
fits, and our entire campaign to date has consumed 163 seconds. We are not
asking for capacity you would otherwise sell at volume; we are asking for
headroom to run a grid a free tier cannot hold.

**A credible negative is worth more to you than an uncritical positive.** We
published a null against our own hypothesis. That is why the numbers in this
package will survive a reviewer who wants to attack them, and why a later
positive from the same protocol will be believed. A vendor-favourable result
from a protocol nobody trusts moves no procurement decision.

**What you keep regardless of outcome.** The findings, the integration
write-ups, the cost model, and the measured device behaviour. If our arm never
beats the classical baseline, all of it is still yours.

## The three needs, in more detail

**The variable ceiling, and what it forecloses.** A 312-variable submission came
back with "Number of variables '312' in problem is greater than the free-tier
device limit '100'". Our frozen configuration is 91 variables, sitting under
that ceiling by accident rather than design, so every scaling statement we can
currently make on this project is bounded by a tier limit rather than by the
device. The concrete degree-3 case here: three-feature weak-learner subsets
over 13 features need 377 variables, which the free tier cannot accept at all.

We are not new to this. The full Fourier Wall and SPECTRA analysis was run on
Dirac-3 at degree 3 on a paid account, so we know what the device does above
the free-tier ceiling and what it costs to find out. That is why the estimates
below are costed rather than guessed, and why we are asking for a specific
number of seconds instead of open-ended access.

**Why the integer solver is the experiment that matters.** Cardinality-
constrained selection of weak learners is where your hardware is not competing
against an easy classical answer. Everything we have run so far is a convex
relaxation, and a convex relaxation is exactly the case where a classical
solver wins by construction.

**Sizing, from measurement rather than projection.** Our preregistered Phase 1
grid is 81 fits at roughly 2,300 to 2,600 seconds, each block costed from the
4 to 5 seconds per fit we actually measured. Phase 2 runs the same protocol on
larger data. We would rather ask once, against numbers we can show you, than
return repeatedly with revised guesses.

**Enough repetition to characterise the stochasticity honestly.** Across 8
samples per fit, no fit has returned identical draws, and the within-fit energy
spread is a median 0.019% and maximum 0.343%. That is a good number for you.
With headroom we can turn it into a proper distribution across configurations
and sizes rather than a footnote.

We have worked together for three years. This note is written the way I would
want one written to me: the ask first, then what you get, then the science.

## What we found, since it bears on how CVQBoost gets configured

The first campaign showed excellent solver fidelity: hardware and an exact classical solve of the identical Hamiltonian differ by -0.0010 AUPRC with the interval containing zero, weight cosine 0.975 to 0.999, and hardware objective values always above the exact minimum, never below.

The sharper result came from the control we ran afterwards. On the frozen configuration **the solved optimum is uniform to seven decimal places**, and the apparent 0.0022 AUPRC gain over uniform weights turned out to be tie-breaking: uniform weights leave 95.3% of test rows tied on one score, weight perturbations of order 1e-07 split those ties, and average precision is rank-based. Rounding the scores back returns the metric exactly.

The cause is pool degeneracy, and it is measurable: off-diagonal Gram entries average 170,234.4 against a diagonal of 170,235, so any two weak learners agree on 99.999% of training rows. The frozen pool's trees are unbounded, so they memorise the training fold: 80 to 84 of the 91 learners reproduce the labels exactly and are therefore the same vector (A20; the letter as sent said majority-class collapse, which the saved pools disprove). A pool of near-identical learners gives an optimizer nothing to weight.

**This is a statement about how CVQBoost is configured for extreme class imbalance, not about your hardware.** The device reproduced the exact optimum faithfully every time. The pool handed to it was the problem. We think it is worth a note in the CVQBoost documentation for anyone applying it at low prevalence, and we would rather you had it from us than from a customer who hit it silently.

We then tested the fix, in two steps, and the second one is the part we think is useful to you.

First, replacing the single family of unbounded trees with four families (decision tree, LDA, logistic, KNN) moves the optimum genuinely off uniform: L1 distance 0.126 against 8.0e-08, largest weight 1.24 times uniform, with two controls confirming this is optimization rather than tie-breaking. It bought the optimizer something to do, but no accuracy.

Second, adding imbalance handling AT FIT TIME -- class weighting inside the tree and logistic learners as they are built, rather than reweighting the ensemble objective afterwards -- changes the pool materially: the Gram off-diagonal ratio falls from 0.9988 to 0.92. Two of our four families take no class weight, and the selected configuration also tightened the KNN neighbourhood, so the accuracy number below carries both changes; the diversity number is attributable to class weighting alone. Against the same single-family pool rebuilt at the same size on the same splits, the tuned pool gains **+0.0319 AUPRC on ten of ten seeds**, reaching 0.7700 against Loke et al.'s reported 0.8 on your hardware. That clears our own 0.0268 detectable threshold -- the first difference in this work to do so.

We flag one thing about that number rather than let you find it. It reached significance only after we found and corrected a protocol violation in our own exploratory code: three modules written as standalone work skipped the deduplication our frozen protocol mandates, and had been training on 1,081 duplicate rows for two sprints. Correcting it moved the result across the threshold in our favour, which is exactly the direction that should make a reader sceptical. The mechanism is measured, not assumed: duplicate rows carry a 1.73% fraud rate against the dataset's 0.17%, a tenfold enrichment, so removing them strips memorisable positives -- and a pool of unbounded trees, which split a duplicated row exactly, loses more than a pool that averages over neighbourhoods. The generator, the data and the per-seed values are all in the package.

**The part worth your attention: the accuracy came from the learners, not the optimizer.** On the tuned pool the solved weights beat uniform weights by only +0.0047, an order of magnitude smaller than the learner effect and well inside our detectable threshold. So for CVQBoost at low prevalence, the leverage is in how the weak learners are built, and the optimization step is close to free either way. That is a configuration statement about your library rather than a limitation of your hardware, and it is the second thing we would put in the CVQBoost documentation alongside the degeneracy finding above.

## A second dataset, and what it says about the ceiling

We ran the preregistered IEEE-CIS protocol as well: 590,540 transactions, 3.5%
prevalence, rolling-origin evaluation by month, with the shuffled-label control
collapsing on every fold. Classical arms reach 0.5739 AUPRC -- on
hyperparameters carried from our tuned ULB settings as a hypothesis, not a
per-dataset search, so treat that as a floor. The CVQBoost arm, held to the six
features the 100-variable ceiling permits, reaches 0.0571.

That gap is not a hardware result, and the control that establishes it matters
more than the number: the same LightGBM given the SAME six features falls from
0.5424 to 0.0734. Every model is starved at six features, and the quantum arm
attains 85% of that constrained ceiling. All of this is a classical proxy solve
of the identical Hamiltonian, marked [SIM]; no metered time was spent.

We then ran the preregistered feature ladder to test whether the ceiling is what
binds, and we report the answer against our own interest: it is not. Across k in
{5, 9, 13, 17} both arms improve and the classical arm improves faster, a slope
of -0.006 AUPRC per feature. Lifting the ceiling raises CVQBoost 2.8x and the
GBDT 3.6x. So the 100-variable limit bounds absolute performance without being
why the arm trails.

We state that plainly because it cuts against our own case for more variables.
It weakens the pure sizing argument below and sharpens the integer-solver one:
if a weighted vote over one- and two-feature learners does not represent the
interactions a boosted tree exploits, then the formulation worth testing is the
one the continuous relaxation drops -- the cardinality-constrained integer
problem and three-feature subsets. Neither has been run, and that is our first
ask.

We have since tested the third candidate, the phase representation, and it does
not help: across ten seeds the quantum-minus-classical difference shifts by
-0.0115 against a paired SD of 0.0135, well inside our detectable threshold. We
report that because it narrows the ask honestly. The remaining two are the ones
that need your hardware, and one of them -- the cardinality-constrained integer
problem -- is the only formulation here where a classical solver does not win by
construction.

## What we would test with the access

In priority order, each with a preregistered protocol already written:

1. **Cardinality-constrained selection on the integer solver**, against time-capped MIQP, greedy and annealing controls. A win against a certified-optimal classical solve is a result; a win against no control is not.
2. **The paid-tier sizing curve**, 100 to several thousand variables, published.
3. **The full ULB and IEEE-CIS grids**, which the 100-variable ceiling currently forecloses. IEEE-CIS is 590,540 transactions and several hundred features, the regime where CVQBoost's published runtime claim actually lives. The ladder above shows more features help both arms without closing the gap, so this ask is to characterise the device, not to rescue the result.
4. **Segment replication (block B4)**, 15 fits at roughly 450 seconds, and a sign-augmented QSVM block.

## What we give back

- The pool-degeneracy finding above, written up for your documentation.
- **Integration feedback, enclosed as a document rather than a promise**
  (`eqc-models and Dirac-3: Integration Feedback`). Every finding cites the
  file and line that establishes it, so you can check any of them: the pool-construction strategy that fails on Windows, the response object whose billing field is not a dictionary key, the free-tier variable arithmetic and where the documentation and implementation diverge, and the guards we built around metered execution that any serious user would need.
- The measured cost model: per-fit timings consistent across 37 fits, and the solver-dispersion data above.
- **A validated classical proxy for Dirac-3's CVQBoost path, which may be the most reusable thing here.** It reads the Hamiltonian eqc-models actually constructs (J = HH^T + lambda*I, C = -2Hy, sum constraint 1.0, w >= 0) and solves that identical objective classically by accelerated projected gradient on the simplex. Because it builds its pools through eqc-models' own builders, the problem it solves is the same problem, not a reimplementation that has drifted. Two things that buys: it is how we could measure hardware-minus-exact at -0.0010 AUPRC with weight cosine 0.975 to 0.999, since without an exact solve of the SAME Hamiltonian there is nothing to compare a device result against; and it let us develop against the free tier while spending 163 metered seconds in total. For QCi it is a test oracle for CVQBoost regressions and a way for evaluating customers to size a problem before they spend on it. It is yours, and we would be glad to have your correction on whether we have read the Hamiltonian right.
- Named attribution in a submission to a tier-one bank, and in whatever is published afterwards.

Two questions we would value your view on, both single-fit experiments we would run on approval. First, whether relaxation schedule 4 would close the 0.013% to 0.413% residual we see between the hardware objective and the exact minimum. Second, whether a larger sum constraint would help, given that spreading 1.0 across 91 variables puts each weight near 0.011 and may approach the analog resolution floor.

## A note on this package

Everything enclosed is DRAFT and pre-submission. The results are as measured; the preregistration and its twenty-one dated amendments show exactly what was decided before any result was seen, including the gate we failed and the two claims we had to correct. We would welcome correction on anything we have characterised wrongly about Dirac-3 -- especially the convexity argument and the free-tier ceiling -- before this becomes a public submission.

Thank you for considering the request.

Best regards,

Harold Kimmey  
Team Lead, Claude Shannon's Fraud Catchers  
kimmeyharold@aol.com | 216-357-9227
