---
title: "Appendices: Quantum-Enhanced Credit Card Fraud Detection"
author: "Claude Shannon's Fraud Catchers"
date: "September 2026"
header-includes: |
  \usepackage{titling}
  \setlength{\droptitle}{-9em}
  \usepackage{ltablex}
  \keepXColumns
  \renewcommand{\topfraction}{0.95}
  \renewcommand{\bottomfraction}{0.95}
  \renewcommand{\textfraction}{0.05}
  \renewcommand{\floatpagefraction}{0.75}
---

# Appendix A. Results

ULB benchmark, 284,807 transactions, 1,081 exact duplicates removed before splitting, 60/20/20 stratified, seeds 42-51, test-fold prevalence 0.00167. Features are anonymized principal components plus amount and elapsed time; no merchant, device, geography or cardholder attributes exist, which bounds both feature engineering and the fairness testing a deployment would require. The PCA transform is unpublished, so no model fitted here transfers to raw bank traffic. AUPRC is step-wise average precision throughout.

## A.1 Detection quality (mean over 10 seeds, test AUPRC)

| Arm | Features | AUPRC | Seed SD | 95% interval | Tag |
|----------------------|--------|-------|-------|----------------|-----|
| CatBoost | 30 | 0.8368 | 0.0304 | [0.8150, 0.8585] | [SIM] |
| XGBoost | 30 | 0.8296 | 0.0286 | [0.8092, 0.8501] | [SIM] |
| CatBoost | 13 | 0.8070 | 0.0321 | [0.7841, 0.8300] | [SIM] |
| **CVQBoost on Dirac-3** | 13 | **0.7671** | 0.0302 | [0.7455, 0.7887] | **[HW]** |
| Logistic regression | 30 | 0.7218 | 0.0268 | [0.7026, 0.7410] | [SIM] |

Values are means and t-intervals across ten overlapping resplits: they describe split sensitivity, not deployment sampling error, since the splits share rows. An inferential interval needs a held-out temporal period, which Phase 2 supplies. AUC-ROC is 0.92 to 0.98 across arms and is not the operative metric at 0.17% prevalence. The exact proxy of the hardware row scores 0.7681 (within 0.001), and a tuned 9-feature pool scores 0.7014 [HW]. Every configuration uses one- and two-feature learners: 13 features give 13 singles plus 78 pairs, the 91 variables cited throughout.

## A.2 Operational view, with the budget ceiling stated

The test fold holds about 95 frauds in 56,746 transactions, so the 0.05% and 0.1% budgets fund 28 and 57 alerts, capping recall at 0.295 and 0.600. Every column is a ranking measure under a budget; only 0.5% is uncapped by the positive count. CVQBoost figures are proxy-derived [SIM]: Dirac-3 weights were not persisted (A.4).

| Arm | R@0.05% (cap .295) | R@0.1% (cap .600) | R@0.5% |
|------------------------|--------------------|----------------|--------|
| CatBoost, 30 feat | .294 (99.7% of cap) | .593 (98.8%) | .855 |
| CatBoost, 13 feat | .286 (96.9%) | .580 (96.7%) | .849 |
| CVQBoost proxy [SIM] | .283 (95.9%) | .565 (94.2%) | .819 |
| CVQBoost mixed k=6 [HW] | .271 | .509 | .839 |
| Logistic regression | .241 (81.7%) | .513 (85.5%) | .839 |

## A.3 Hardware campaign and score health

51 metered fits over three campaigns, 325 device seconds, zero failures, zero retries, 4 to 91 s per fit; the classical solve takes milliseconds. The third campaign spent the QCi grant: the A22 IEEE-CIS hardware ladder (12 fits, 62 s), one B2 fit at 833 variables (91 s), and the 10-second probe that retired the free-tier variable ceiling (A21). The selected configuration carries a score-degeneracy warning on all ten seeds (95.1% of transactions share one score across 814 distinct values), so its threshold-dependent figures are weak evidence while its ranking metrics are sound.

| Quantity | Value | Tag |
|----------------------------------|------------------------------|-----|
| G0b Spearman, proxy versus hardware ranking | 0.900 (exact permutation p: one-sided 0.042) | [HW] |
| H1b, CVQBoost minus best matched GBDT | -0.0399 [-0.0571, -0.0227], 9 of 10 seeds negative | [HW] |
| Per-seed paired BCa intervals excluding zero | 6 of 10 | [SIM] |
| Solver draws; identical draws; energy spread | 8; 0 of 27; median 0.019%, max 0.343% | [HW] |

## A.4 Solver fidelity and the mechanism controls

Hardware minus exact proxy on identical Hamiltonians: -0.0010 [-0.0032, +0.0012];
weight cosine 0.975 to 0.999; hardware objective 0.013% to 0.413% above the exact
minimum, never below [HW]. That agreement bounds any effect of Dirac-3's
continuous-variable resolution: quantization coarse enough to drive the flat
optimum could not reproduce it.

**The frozen pool's optimum is uniform to seven decimal places** on all ten seeds
(L1 from 1/91 of 7.2e-08 to 1.6e-07). Controls, all classical at zero metered
cost: uniform weights by construction give 0.7659, the solved objective 0.7681,
class-weighted 0.7686, and a free-sign logistic stack 0.7681 -- so the
non-negative simplex form costs nothing detectable and objective weighting is
ruled out (though not imbalance at fit time). The +0.0022 is TIE-BREAKING:
uniform weights leave 95.3% of test rows tied on one score (78 distinct values)
and weights differing by 1e-07 split those into 151, so rounding the solved
scores to six decimals returns the metric to the uniform value. The cause is
pool degeneracy -- off-diagonal Gram entries average 170,234.4 against a
diagonal of 170,235, because the frozen pool's unbounded trees memorise the
training fold: 80 to 84 of the 91 learners reproduce the training labels exactly
and are therefore the same vector, while ZERO predict the negative class
everywhere (A20). A penalty sweep from 0 to 4x n_train leaves it uniform even at
zero penalty.

**Mixed pool (exploratory, A11).** Four families at k=13, 312 variables, same
splits: gram ratio 0.9975, L1 from uniform 0.126, solved-minus-uniform +0.0076 on
10/10 seeds, absolute AUPRC 0.7466 -- below the frozen pool's 0.7681 at k=13 and
below the 0.0268 MDE [SIM]. Its two mechanism controls are seed 42 only.

**Tuned pool (exploratory, A13/A14/A16).** Fit-time class weighting in the tree
and logistic learners (LDA and KNN accept none) PLUS closer distance-weighted
neighbours: two interventions, not one. Gram ratio falls 0.9988 to 0.92. Selected
on validation AP at seed 42, then ten seeds: AUPRC 0.7700 (SD 0.0270). Against
the single-family pool rebuilt at the SAME k=6 on the SAME splits, the paired
difference is **+0.0319 (SD 0.0189), 10 of 10 seeds, EXCEEDING the MDE** -- the
first difference in this project to do so. The matched comparator matters:
quoting the k=13 figure against a k=6 arm is the order-mismatched comparison
ADR-0013 warns of, and the frozen pool scores 0.7381 at k=6, 0.0300 below its
k=13 figure (generator: `matched_comparator.py`). Solved minus uniform is +0.0047
(SD 0.0038): the accuracy came from the learners, not the optimizer.

**Hardware (F32) ran a smaller configuration.** The A12 ceiling foreclosed k=13 at the time,
so the metered block used k=6, 60 variables: ten fits, 43.0 device seconds, AUPRC
0.7630, hardware minus proxy -0.0007, cosine 0.977-0.983, recall
0.271/0.509/0.839 [HW]. It measures solver fidelity and supplies hardware
operating points; it does NOT confirm the k=13 mechanism, whose own k=6 spot
check is a single seed (L1 0.0204).

## A.5 IEEE-CIS: the second dataset and the feature ladder

590,540 transactions, 3 duplicates removed, 3.5% prevalence, GroupKFold-by-month
rolling origin, reduced Deotte recipe, UID excluded. Shuffled-label control
collapses on every fold (0.030/0.022/0.032 vs base rates 0.035/0.034/0.042).
AUPRC is not comparable across datasets -- its baseline IS the prevalence -- so
0.5739 at 3.5% is a 16x lift against ULB's 490x at 0.17%.

Arms use ULB-tuned hyperparameters carried as a hypothesis; the section 6
per-dataset search is unspent on IEEE-CIS, so these are floors.

| Arm | Mean AUPRC | Features |
|---|---|---|
| LightGBM | 0.5739 [0.5424, 0.6293] | ~182 |
| XGBoost | 0.5028 [0.4689, 0.5260] | ~182 |
| CatBoost | 0.4795 [0.4696, 0.4927] | ~182 |
| CVQBoost tuned / frozen [SIM] | 0.0571 / 0.0523 | 6 |

**Matched-feature control.** The same LightGBM falls from 0.5739 on the full
feature set to 0.0734 when restricted to the SAME six features CVQBoost is
limited to: every model is starved there, and CVQBoost attains 85% of that
constrained ceiling (0.0621 of 0.0734, both on fold 0 -- the control is a
fold-0 comparison, so the ratio uses the fold-0 CVQBoost value rather than the
three-fold mean quoted elsewhere). Gram ratios 0.950-0.973 rule out the
A.4 degeneracy mode.

**H3 ladder (scoreable, 12 cells).** delta = CVQBoost minus matched GBDT:
-0.0169 (k=5), -0.0764 (k=9), -0.0564 (k=13), -0.1031 (k=17, exceeds the free
tier at the time it ran). Slope -0.006 per feature: lifting the ceiling raises CVQBoost 2.8x and the
GBDT 3.6x, so the ceiling limits absolute performance without being why the arm
trails. Scope: one family set, schedule 2, continuous convex formulation. The
integer cardinality problem, three-feature subsets and the phase representation
are unrun.

**The same ladder, on hardware (A22).** The ladder above is [SIM]: it ran on the
classical proxy because the free-tier ceiling foreclosed its upper rungs on the
device. A21 retired that ceiling, and block B3 re-ran the ladder on Dirac-3 at
the frozen recipe -- same pipeline, same item-4 leakage controls, same
rolling-origin folds, same 100,000-row pool subsample, only the solver differs.
Twelve fits, 62 metered seconds, 107 minutes, every job id retained.

| k | Variables | AUPRC [HW] | AUPRC [SIM] | Difference |
|---|---|---|---|---|
| 5 | 10 | 0.0510 | 0.0508 | +0.0002 |
| 9 | 36 | 0.0804 | 0.0806 | -0.0002 |
| 13 | 78 | 0.1172 | 0.1174 | -0.0002 |
| 17 | 136 | 0.1430 | 0.1427 | +0.0003 |

Mean over three folds at eval prevalence 0.0368. The k=17 cell runs 136
continuous variables, above the retired ceiling, and is the first IEEE-CIS
hardware evidence that ceiling ever foreclosed.

**This is a solver-fidelity result, and it is the strongest one we have.**
Across the twelve individual cells the largest discrepancy is 0.0013 AUPRC, and
the errors scatter in both directions rather than favouring either arm. Dirac-3
reproduces the exact classical solve of the identical Hamiltonian to within
about 0.001 AUPRC at up to 136 variables. It also sharpens the null rather than
threatening it: CVQBoost trails the matched GBDT at every rung, by -0.1031 at
k=17, and the device is demonstrably solving the problem it was given, so that
gap belongs to the formulation and not to the hardware.

An earlier version of this section reported a different and more flattering
hardware ladder, claiming that lifting the ceiling roughly tripled CVQBoost's
AUPRC. That run built its pools on the whole training fold while the [SIM] arm
subsamples to 100,000 rows, so it saw up to 5.8x more data and a different
regularization constant; the apparent gain was the extra rows, not the released
ceiling. It was withdrawn and re-run the same day. A23 records what was
published, how it was found and what changed; the superseded figures appear
nowhere in this submission.

**Two qualifications.** The adversarial control never converged, hitting its
20-round cap on every fold (final AUCs 0.945/0.888/0.887 against a target near
0.5), so drift is spread across the feature set. And our protocol run (0.574)
sits below the published leakage-free band (0.64-0.67) while our own labelled
scale check on a stratified random split reached 0.861 -- the random-versus-
temporal gap Sprint 5 measured at +0.2143 on ULB.

## A.6 H6: does a phase representation move the delta?

Preregistration section 3, exploratory, registered as A18 BEFORE the run. The
QFE phase block (Fourier Wall recipe, train-only whitening) is given to EVERY
arm, and the reported quantity is the SHIFT between representations, not a
delta under one of them. Ten ULB seeds, schedule 2, CVQBoost via the exact classical proxy of the
identical Hamiltonian. [SIM], zero metered seconds.

**This arm is NOT the frozen k=13 configuration, and the difference is the
hypothesis.** A top-13 feature selection would exclude the phase columns --
the best of them ranks about fourteenth by relevance on ULB -- so reducing
first would hand the quantum arm a pool containing no phase information and
H6 could not be tested. The pool is therefore built over every column: 30 in
the baseline representation and 90 under QFE, which at a sequential pair
build is 435 and 4,005 variables against the frozen arm's 78. That is
possible only because this arm runs entirely on the classical proxy, where
the A12 free-tier ceiling of 100 continuous degree-2 variables does not
apply. It was not a configuration the free tier could execute, and it remains unrun for reasons beyond that retired tier, and the shift
reported here is therefore a statement about the FORMULATION rather than
about anything Dirac-3 has run.

| Quantity | Value |
|---|---|
| Mean delta, baseline representation | -0.0685 |
| Mean delta, QFE representation | -0.0800 |
| **Representation shift** | **-0.0115** |
| Paired seed-to-seed SD of the shift | 0.0135 |
| Seeds negative | 7 of 10 |

**The answer: the phase representation does not move the delta by an amount we
can claim.** The shift is 0.85 of its own paired SD, and 43% of the 0.0268 MDE.
The preregistered falsifier -- |shift| below the paired SD -- fires.

We state the direction rather than hide it: the shift is negative on 7 of 10
seeds, which is *suggestive* that the classical bar exploits the added
representation slightly better than a weighted vote over one- and two-feature
learners does. That would be consistent with the A.5 ladder. But 43% of the
MDE is below the smallest difference we preregistered as detectable, so it is
not a finding, and reporting it as one would repeat the error A15 records.

**The classical bar, which is what makes the question answerable.** Every cell
carries a trained-frequency GAM, a GA2M and an order-matched JOINT twin
alongside the three GBDTs, because the Fourier Wall result is that omitting the
twin is how apparent quantum wins get manufactured. Mean AP under the baseline
representation: XGBoost 0.8328, CatBoost 0.8185, **GAM 0.7893**, CVQBoost
0.7646. The GAM twin outscores the quantum arm.

A GBDT was nonetheless the best classical arm in all 20 cells (XGBoost 17,
CatBoost 3), so the twins never set the delta. Both facts belong together: the
twins did not change the NUMBER, and they changed what the number MEANS,
because "best classical" now denotes a bar containing a periodic-structure
model -- the GAM twin at 0.7893 in the baseline representation and 0.7351
under QFE -- rather than a bar of models with no periodic component at all.

**A limitation in the twin design, disclosed because it is the kind a reader
should not have to find.** The twins take a fixed input budget, and under the
QFE representation half of it is reserved for phase columns -- which is what
guarantees they receive the treatment at all. So a QFE twin sees fewer raw
columns than its baseline counterpart, and if the dropped raw columns carried
signal the QFE twin is handicapped, biasing the shift negative. That is the
direction we observed. It cannot have affected the reported number, because a
twin was never the best classical arm in any of the 20 cells and the delta is
measured against that maximum: the shift comes from CVQBoost falling further
(0.7646 to 0.7513) than the GBDT bar did (0.8331 to 0.8313). But the bias would
matter in any cell where a twin took the bar, and a design that gave each twin
its full raw budget PLUS the phase block would avoid it.

**Scope.** Exploratory; H1b remains the sole confirmatory endpoint and H6
carries no confirmatory weight. One dataset, one family set, one phase recipe.
The QFE encoder is fitted on train folds only, asserted by test.

**Two earlier runs of this arm were discarded rather than reported**, and the
reasons are recorded because they bear on how much the third should be
trusted. The first predicted through a spline basis refitted on test data. The
second selected twin inputs by variance, so the whitened phase columns could
never be chosen and two of three twins never received the representation under
test -- identical scores in 10 of 10 seeds. Neither defect changed which arm
set the bar, so neither changed the headline number materially; both made the
classical bar something other than what section 3 specifies. The corrected run
is the one reported here.

# Appendix B. Preregistration registry

## B.1 Gates, scored as committed

| Gate | Criterion | Outcome | Tag |
|------------------|------------------------------|------------------------|-----|
| G0 | Tuned XGBoost mean AUPRC >= 0.85 | **FAIL**: 0.8296 | [SIM] |
| G0 leakage tripwire | No cell above 0.95 | PASS: 0.8368 | [SIM] |
| Shuffled-label tripwire | Collapses to base rate | PASS: 0.0023 / 0.0017 | [SIM] |
| G0b | Proxy-hardware rank Spearman >= 0.5 | **PASS**: 0.900 | [HW] |
| H1b (primary) | CVQBoost versus best tuned GBDT | **NULL**: -0.0399, interval excludes zero | [HW] |
| H4 | Versus best structural control | PARTIAL: solver fidelity only, controls unrun | [HW] |
| H3 (feature ladder) | Does lifting the feature restriction close the gap | **MEASURED**: no. Proxy slope -0.006 AUPRC per feature; the hardware ladder to k=17 / 136 vars reproduces the proxy to within 0.0013 and trails the matched GBDT by -0.1031 (A.5, A22) | [SIM] + [HW] |
| H6 (phase representation) | Does a phase representation move the delta | **MEASURED**: shift -0.0115, preregistered falsifier fired (A.6) | [SIM] |
| H1a, H1c, H5, Phase 2 cardinality arm | Preregistered against MIQP, greedy and annealing controls | NOT RUN | [PROJ] |

H1b is the sole confirmatory endpoint, reported unadjusted. All other completed analyses are exploratory and carry no family-wise confirmatory claim.

**Compound falsification criterion.** Section 2 committed that the theory is
unsupported if ALL THREE hold: H1b fails, the H3 slope is not positive, and H5
does not transfer. Two are now measured and both went against the theory: H1b
is NULL at -0.0399, interval excluding zero, and the H3 slope is -0.006 per
feature. H5 is unrun, so the criterion has not fired -- but neither has it been
survived. It sits one unrun condition away. The pre-committed fallback, a
headline of the measured regime map and boundary statement, is already what
this submission reports.

## B.2 Amendments

Twenty-three dated amendments, A1 to A23, each with rationale and approval; full
text in the repository. Three changed a reported figure, named here so they are
easy to find. **A15**: the
frozen pool's k=6 AUPRC was published as 0.7688, a five-seed mean carried into a
ten-seed writeup; the corrected ten-seed value, 0.7629, inverted the argument it
carried. A17 then superseded that figure in turn: on the deduplicated data the
same comparator scores **0.7381**, which is the value reported throughout this
submission. 0.7629 is pre-A17 and appears here only as the history of A15.
**A17**: three exploratory fold builders skipped the deduplication section 4
mandates, so every A11/A13 figure was recomputed, moving the tuned-pool result
from below to above the MDE -- a direction that should invite checking rather
than acceptance. **A12**: the free-tier 100-variable ceiling, established when a
312-variable job was refused server-side.

No amendment changed a gate criterion; no gate was rescored after observation.

**A21 and A22** are the late pair and are worth reading together. A21 established
by a single cheap probe that the 100-variable ceiling shaping the whole campaign
was a billing tier, not a device limit. A22 then spent the grant on the block
that ceiling had cost the most, the IEEE-CIS ladder, and reports it above.

## B.3 Committed blocks that did not run

Section 10 of the preregistration commits a run grid and provides that unrun
blocks enter the proposal as [PROJ] with the grid cited as the plan. One block
qualifies.

**B2 (ULB full config: top-17 features, schedule 3, 833 variables, 11 fits).**
[PROJ], never submitted, zero metered seconds. A12's ceiling foreclosed it for
most of the campaign and A21 lifted that, so it was scheduled. It did not run for
a reason unrelated to the device: the full pair-build that amendment A3 requires
uniformly of every CVQBoost cell uses `fork`, which is POSIX-only, and the
available Linux environment ships Python 3.14 while `eqc-models` requires below
3.14. We stopped rather than work around it, because both available workarounds
-- reimplementing the pool build, or rebuilding the environment days before
submission -- put the frozen recipe at risk to gain one block. The honest
statement is that B2's variable count, 833, is the largest the campaign planned
and remains untested by us on hardware.

# Appendix C. Reproduction and references

Freeze commit `95751b9`, tag `prereg-freeze`, amendments A1 to A23. The
repository at `github.com/kimmeyh/hsbc-quantum-fraud-2026` carries the pinned
environment, both dataset checksums, the preregistration in full, the full
reference list, and the results store, whose every row holds a configuration
hash and evidence tag. The 40 QCi job identifiers the client returned, their raw responses and the
Dirac-3 parameters are retained there. For eleven earlier fits the runner did
not persist the identifier the client returned; the gap was closed mid-campaign,
and every fit since records one. Those eleven costs were measured
from the allocation balance and their metrics computed in process, so no
reported figure depends on a handle we do not have. Every figure in this
submission regenerates from that repository.

Comparisons. Loke et al., 2026 (ICAART): same Dirac-3 hardware, AUC-PR above 0.8
with a heterogeneous pool against our 0.767 single-family. AutoXGB ULB 0.782 is
its own protocol, not like-for-like.
