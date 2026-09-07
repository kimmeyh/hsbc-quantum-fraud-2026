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

37 metered fits over two campaigns, 163 device seconds, zero failures, zero retries, 4 to 5 s per fit; the classical solve takes milliseconds. The selected configuration carries a score-degeneracy warning on all ten seeds (95.1% of transactions share one score across 814 distinct values), so its threshold-dependent figures are weak evidence while its ranking metrics are sound.

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
diagonal of 170,235, because at 0.17% prevalence a depth-limited tree predicts
the negative class almost everywhere. A penalty sweep from 0 to 4x n_train
leaves it uniform even at zero penalty.

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

**Hardware (F32) ran a smaller configuration.** The A12 ceiling forecloses k=13,
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

**Matched-feature control.** The same LightGBM given the SAME six features
CVQBoost is limited to falls from 0.5424 to 0.0734: every model is starved there
and CVQBoost attains 85% of that ceiling. Gram ratios 0.950-0.973 rule out the
A.4 degeneracy mode.

**H3 ladder (scoreable, 12 cells).** delta = CVQBoost minus matched GBDT:
-0.0169 (k=5), -0.0764 (k=9), -0.0564 (k=13), -0.1031 (k=17, exceeds the free
tier). Slope -0.006 per feature: lifting the ceiling raises CVQBoost 2.8x and the
GBDT 3.6x, so the ceiling limits absolute performance without being why the arm
trails. Scope: one family set, schedule 2, continuous convex formulation. The
integer cardinality problem, three-feature subsets and the phase representation
are unrun.

**Two qualifications.** The adversarial control never converged, hitting its
20-round cap on every fold (final AUCs 0.945/0.888/0.887 against a target near
0.5), so drift is spread across the feature set. And our protocol run (0.574)
sits below the published leakage-free band (0.64-0.67) while our own labelled
scale check on a stratified random split reached 0.861 -- the random-versus-
temporal gap Sprint 5 measured at +0.2143 on ULB.

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
| H1a, H1c, H3, H5, H6, Phase 2 cardinality arm | Preregistered against MIQP, greedy and annealing controls | NOT RUN | [PROJ] |

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

Seventeen dated amendments, A1 to A17, each with rationale and approval; full
text in the repository. Three changed a reported figure, named here so they are
easy to find. **A15**: the
frozen pool's k=6 AUPRC was published as 0.7688, a five-seed mean carried into a
ten-seed writeup; the true value 0.7629 inverted the argument it carried.
**A17**: three exploratory fold builders skipped the deduplication section 4
mandates, so every A11/A13 figure was recomputed, moving the tuned-pool result
from below to above the MDE -- a direction that should invite checking rather
than acceptance. **A12**: the free-tier 100-variable ceiling, established when a
312-variable job was refused server-side.

No amendment changed a gate criterion; no gate was rescored after observation.

# Appendix C. Reproduction and references

Freeze commit `95751b9`, tag `prereg-freeze`, amendments A1 to A17. The
repository at `github.com/kimmeyh/hsbc-quantum-fraud-2026` carries the pinned
environment, both dataset checksums, the preregistration in full, the full
reference list, and the results store, whose every row holds a configuration
hash and evidence tag. All 37 QCi job identifiers, their raw responses and the
Dirac-3 parameters are retained there. Every figure in this submission
regenerates from that repository.

Comparisons. Loke et al., 2026 (ICAART): same Dirac-3 hardware, AUC-PR above 0.8
with a heterogeneous pool against our 0.767 single-family. AutoXGB ULB 0.782 is
its own protocol, not like-for-like.
