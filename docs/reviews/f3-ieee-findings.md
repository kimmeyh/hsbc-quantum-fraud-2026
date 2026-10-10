# F3 IEEE-CIS findings that need stating, not burying

Written while Task C runs, against Task B's completed results. Both items below
make our own numbers look worse or more complicated. Both go in the paper.

## 1. The adversarial control never converged

Section 4 item 4 targets "AUC near 0.5" -- at 0.5 a classifier cannot tell early
training rows from late ones, so the feature set carries no period signal. Our
result, on every fold:

| Fold | Rounds | Hit cap | Final adversarial AUC |
|---|---|---|---|
| 0 | 20 | yes | 0.945 |
| 1 | 20 | yes | 0.888 |
| 2 | 20 | yes | 0.887 |

Twenty features dropped per fold and early/late rows remain almost perfectly
separable. The drift is not concentrated in a few columns; it is spread across
the feature set, which is consistent with IEEE-CIS spanning roughly six months
of genuinely changing behaviour.

WHAT THIS MEANS FOR THE NUMBERS. A classical baseline measured under a protocol
whose own drift control did not converge is weaker evidence than the AUPRC
suggests. We report the figures and this fact together. Raising the round cap is
not an obvious fix: it might simply strip the feature set toward nothing, and
choosing a cap that makes the control pass would be selecting a threshold to
produce a desired outcome, which is what the preregistration exists to prevent.

The honest Phase 2 statement is that IEEE-CIS drift needs a designed response --
drift-aware features, periodic retraining, or explicit domain adaptation -- not a
larger filter.

## 2. AUPRC is not comparable across datasets, and our own research doc says so

`docs/research-baselines-best-practices.md` rule 27: "Never compare or average
AUPRC across datasets. The average-precision baseline equals prevalence."

| Dataset | Prevalence | Best AUPRC | Lift over base |
|---|---|---|---|
| ULB | 0.17% | 0.8368 (CatBoost) | ~490x |
| IEEE-CIS | 3.5% | 0.5739 (LightGBM) | ~16x |

Placing 0.84 beside 0.57 invites the conclusion that the pipeline is worse on
IEEE-CIS. It is not the same measurement. Normalized as
(AP - baseline) / (1 - baseline), the IEEE-CIS arms are 0.484 / 0.558 / 0.460.
Every IEEE-CIS AUPRC in the paper carries its prevalence beside it.

## 3. Our protocol run sits BELOW the published band, and the scale check sits far above

| Source | AUPRC | Split | Features |
|---|---|---|---|
| Published leakage-free band | 0.64-0.67 | -- | -- |
| Our Sprint 5 scale check | 0.861 | stratified random | raw joined |
| Our F3 protocol run | 0.574 | temporal rolling origin | full recipe |

The scale check was labelled "NOT a preregistered cell" with four caveats,
including "single stratified split, not the preregistered temporal protocol".
That label is now doing real work: the 0.287 gap between it and the protocol run
is the same effect Sprint 5 measured on ULB, where a random split contributed
+0.2143 over a time-ordered one. A random split lets a model train on rows that
occur after its test rows, which on fraud data is future knowledge.

Our 0.574 falling BELOW the published 0.64-0.67 band is the expected direction
for a stricter split against reproductions whose protocols we cannot fully
verify, but it is a gap, and a reviewer will ask. Stated plainly rather than
explained away: we are below the published band under a temporal protocol, and
we do not claim the published figures are wrong -- we claim ours are measured
under a protocol we can describe completely.

Both facts belong in the same sentence in the paper, because quoting either
alone misleads: the scale check alone overstates, the protocol run alone invites
"worse than published" without the reason.
