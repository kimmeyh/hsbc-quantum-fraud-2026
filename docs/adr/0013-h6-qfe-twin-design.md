# ADR-0013: H6 QFE representation and order-matched classical twin design

## Status

Accepted (team lead, 2026-09-05)

## Date

2026-09-05

## Context

PREREGISTRATION v1.1 H6 (section 3) requires the Fourier Wall phase
representation (exact recipe: rank phases with log magnitudes first,
calendar cycles, train-only whitening, low-cardinality columns excluded) to
be given to EVERY H6 arm, and requires every H6 cell's classical bar to
include a trained-frequency GAM, a GA2M, and an order-matched JOINT twin
(supervised coarse-to-fine cosine frequency scan fit by logistic regression)
in addition to the GBDT trio. `docs/references.md` design implication 2
states the reason in the terms the source paper uses: publishing a
phase-feature quantum result without this twin is exactly how the Fourier
Wall paper shows apparent quantum wins get manufactured (0.758 fake vs 0.968
real in their reconstruction) -- an order-mismatched comparison lets the
representation, not the model family, do the winning. Sprint 6 Task C
(F23, card #33) is preparation only: build and test the transformer, prove
each twin family's core primitive works, and freeze the cell list -- no
arm runs, no results.json row, no reported metric. Execution is F4 in
Sprint 7.

Two design questions had to be settled before Sprint 7 can execute
mechanically rather than by re-deriving the recipe under time pressure:
(1) which twin implementations are available in the pinned environment, and
(2) how the phase-encoded feature count composes with the frozen CVQBoost
variable-count formula (amendment A2), since H6 matches features across
every arm including CVQBoost.

## Decision

**Transformer.** `experiments/src/qfe.py` implements
`FourierWallPhaseEncoder`, a sklearn-style fit/transform class. `fit(X_train)`
computes, from training data only: which columns are low-cardinality
(`<= LOW_CARD_THRESHOLD = 12` distinct train values, excluded from the
encoded block), the frozen train order statistics for rank-phase
interpolation (log-magnitude-transformed, sign-preserved `log1p(|x|)` first,
per the recipe), and the train-phase whitening moments. `transform(X)`
applies those frozen parameters to any X (including test) and never
recomputes a statistic from its input. ULB's `Time` column is routed to a
dedicated daily-cycle calendar path (`2*pi*(t mod 86400)/86400 - pi`)
instead of the rank path, matching G0c ("Time retained as a raw feature and
as a time-of-day phase"). The representation tag `qfe.QFE_REPRESENTATION_TAG
= "qfe_phase_v1"` is the `results.json`/config-hash label for this recipe
(ADR-0006 convention); any future recipe change gets a new tag, never a
silent edit to this one.

**Twin implementations (this environment, checked 2026-09-05).**
`pygam` and `interpret` (InterpretML) are NOT installed. Per the task
instruction, this is reported rather than resolved by installing a
heavyweight dependency this late in the sprint; Sprint 7 planning decides
whether to add one.
- **GAM**: `statsmodels.gam.api.GLMGam` with `BSplines` smooth terms
  (statsmodels 0.15.0, already pinned). The spline basis/knots are built
  from the training columns, which is the "trained" part of
  "trained-frequency GAM". Pre-flight PASS (`h6_twin_preflight.py`).
- **GA2M**: no EBM library is installed, so the GA2M-equivalent primitive is
  `sklearn.ensemble.HistGradientBoostingClassifier(interaction_cst=...)`
  (sklearn 1.9.0, pinned): `interaction_cst` restricts the ensemble to named
  main-effect and pairwise-interaction feature groups, which is the GA2M
  contract (a GAM plus pairwise terms, no higher order), without adding a
  dependency. Pre-flight PASS.
- **JOINT**: decomposes into (a) a coarse-to-fine supervised cosine
  frequency scan (score candidate frequencies by `|corr(cos(f*x), y)|` on a
  coarse grid, refine around the best candidate) and (b)
  `sklearn.linear_model.LogisticRegression` fit on the resulting small
  cosine-feature design matrix. Both provable with the pinned stack; no new
  library needed. Pre-flight PASS (recovered a synthetic true frequency of
  3.0 as 3.000, converged logistic fit).

All three pre-flights are asserted in `experiments/src/test_h6_twin_preflight.py`
as a standing regression guard, not a claim that F4's actual twin models are
built -- they are not; that is Sprint 7 scope.

**H6 cell list and representation tag freeze.** Recorded in
`experiments/src/qfe.py` (`QFE_REPRESENTATION_TAG`) and restated here for a
single point of reference: every H6 cell is (representation in {`raw`,
`qfe_phase_v1`}) x (arm in {XGBoost, LightGBM, CatBoost, logistic regression
floor, CVQBoost/proxy, GAM, GA2M, JOINT}), on ULB matched top-k features,
stratified protocol, the same seed ladder as H1b-primary. `raw` is the
existing matched-feature recipe (ADR-0006 `matched13`); `qfe_phase_v1` is
this ADR's transformer output concatenated with any columns the recipe does
not encode (low-cardinality passthrough). No cell runs under this ADR;
Sprint 7 (F4) executes and writes `results.json` rows carrying this tag.

**A2 variable-count re-check under QFE.** The frozen CVQBoost feature count
`n` used in `data.qubo_vars` is the count of *encoded* columns entering the
weak-learner pool, and the phase recipe changes `n` for whichever matched
features it touches: each rank-phase-encoded input becomes 2 output columns
(cos, sin), and the calendar-encoded `Time` column becomes 3 (raw + cos +
sin, per G0c). This ADR adopts the conservative assumption that a
rank-phase-encoded feature's RAW column is dropped from the CVQBoost feature
set in favor of its two phase columns (matching the FourierWall2 leak-free
convention of keeping "covariates + `*_phase` columns", not raw-plus-phase
for every encoded column) -- stated explicitly here because PREREGISTRATION
does not pin this arithmetic and Sprint 7 must not re-derive it under time
pressure. Under this convention, for a matched-`k` feature set where `Time`
is one of the `k` features: `n_qfe = 3 + 2*(k-1)`.

Re-derived bounds (A2 formula `qubo_vars`, both `sequential` and `full`
pair-builds; free tier ceiling ~100 vars at schedule 2, device ceiling 949
vars at schedule 3):

| k (pre-QFE matched features) | n after QFE | schedule 2 seq / full | schedule 3 seq / full |
|---|---|---|---|
| 6 | 13 | 78 / 91 | 364 / 377 |
| 7 | 15 | 105 / 120 | 560 / 575 |
| 8 | 17 | 136 / 153 | 816 / 833 |
| 9 | 19 | 171 / 190 | 1140 / 1159 |
| 13 | 27 | 351 / 378 | 3276 / 3303 |
| 17 | 35 | 595 / 630 | 7140 / 7175 |

**New bounds: free-tier schedule 2 admits at most k=6 matched features
under QFE (n=13, 78/91 vars, fits the ~100 ceiling); k=7 already exceeds it
(105/120 vars). Device schedule 3 admits at most k=8 (n=17, 816/833 vars,
fits the 949 ceiling); k=9 already exceeds it (1140/1159 vars).** This is
roughly HALF the pre-QFE matched-feature budget (free tier was k<=13,
device was k<=17, per amendment A2) -- QFE does not merely shift the
existing B1/B2 grid's `k`, it shrinks the feasible `k` for any QFE-bearing
CVQBoost cell by about half, because doubling the encoded-feature count
grows `C(n,2)`/`C(n,3)` combinatorially. If Sprint 7 wants QFE cells at the
existing B1 k=13 / B2 k=17 working points, either the CVQBoost schedule must
drop (schedule 1, singles only, no combinatorial blow-up) or `k` must be
cut roughly in half from the non-QFE grid; this ADR does not choose between
those for Sprint 7 -- it records the constraint so that choice is made
deliberately, not discovered mid-sprint. GBDT/GAM/GA2M/JOINT twins are
unaffected (they have no analogous combinatorial variable-count ceiling).

## Alternatives Considered

### Augment (keep raw column alongside both phase columns) instead of replace
- **Description**: every rank-phase-encoded feature contributes 3 output
  columns (raw, cos, sin) instead of 2.
- **Pros**: no information loss from dropping the raw scale; matches a
  literal reading of "given to every arm" as strictly additive.
- **Cons**: pushes `n_qfe = 3 + 3*(k-1)`, roughly 1.5x larger again; recomputed
  with the same formula, the free tier then admits only k<=4 at schedule 2
  (n=12, 66/78 vars) since k=5 (n=15, 105/120) exceeds the ~100 ceiling, and
  device admits only k<=5 at schedule 3 (n=15, 560/575 vars) since k=6
  (n=18, 969/987) exceeds the 949 ceiling -- a much harsher cut for no
  stated methodological benefit, and it contradicts the FourierWall2
  leak-free precedent (section 2 of `CVQBoost_Findings.md`: "keep only
  covariates + `*_phase` columns").
- **Why Rejected**: the source precedent this project already follows drops
  the raw column in favor of its phase pair; augmenting is a plausible but
  strictly worse-fitting reading, and is recorded here so Sprint 7 does not
  need to re-litigate it.

### Install `pygam`/`interpret` now to get library-native GAM/GA2M
- **Description**: add the canonical libraries instead of the
  statsmodels/sklearn substitutes.
- **Pros**: `interpret`'s EBM is the reference GA2M implementation cited in
  the GA2M literature; less risk of a subtle semantic gap versus "the GA2M
  everyone means".
- **Cons**: a new heavyweight dependency 10 days from the Sep 15 deadline,
  unvetted against the pinned environment, with its own version-pinning and
  reproducibility burden; the task instruction is explicit (report missing
  libraries rather than installing something heavyweight).
- **Why Rejected**: the substitutes proved in this ADR's pre-flights satisfy
  the GAM/GA2M CONTRACT (additive smooth terms; main-effects-plus-pairwise)
  without new dependency risk. Sprint 7 can revisit if a reviewer requires
  the reference implementation specifically.

## Consequences

### Positive
- Sprint 7 (F4) has a tested transformer, three proven twin primitives, and
  a frozen cell list/tag to execute against mechanically, with the
  order-matched-twin rationale documented so it cannot be silently dropped
  under deadline pressure.
- The A2 re-check surfaces the QFE/CVQBoost variable-count collision BEFORE
  any hardware block is requested for a QFE cell, avoiding a wasted metered
  run against an infeasible `k`.

### Negative
- The replace-vs-augment choice is a judgment call this ADR makes
  unilaterally (Proposed status, pending team-lead review); if the team
  lead prefers augment, the bounds table above must be recomputed before
  Sprint 7 requests any QFE hardware block.
- No EBM-native GA2M means any reviewer comparing against published EBM
  benchmarks numerically is comparing against a different (though
  contract-equivalent) implementation; this should be disclosed alongside
  any H6 GA2M number.

### Neutral
- The twin pre-flights prove primitives, not tuned models; Sprint 7 still
  bears the cost of actually fitting and tuning GAM/GA2M/JOINT per H6 cell.

## Preregistration touchpoints

Section 3 (H6, and G0c's Time-column handling), section 5 (feature handling
and leakage controls -- fit-on-train-only), section 10 (A2 variable-count
formula this ADR re-derives under QFE). The preregistration governs
methodology; this ADR records engineering decisions (transformer
implementation, twin substitute libraries, variable-count arithmetic) around
it and changes no gate, hypothesis, or cell.

## References

`experiments/PREREGISTRATION.md` sections 3, 5, 10 and amendment A2;
`docs/references.md` design implications 1-2 (Mancilla & Tagliani, "The
Fourier Wall", arXiv:2607.15815, section 6.4); `experiments/reference/fourierwall2/CVQBoost_Findings.md`
section 2 (leak-free feature convention this ADR follows for replace-vs-augment);
ADR-0002 (proxy as structural control, same variable-count formula);
ADR-0006 (feature recipe registry / representation tagging convention);
`experiments/src/qfe.py`, `experiments/src/h6_twin_preflight.py`,
`experiments/src/test_qfe.py`, `experiments/src/test_h6_twin_preflight.py`;
Sprint 6 Plan Task C (`docs/sprints/SPRINT_6_PLAN.md`); card #33 (issue #33, F23).

## Team-lead decisions, 2026-09-05

Both open questions were put to the team lead with pros, cons and a
recommendation. Both were decided as recommended.

**1. Raw column under phase encoding: REPLACE, not augment.** The raw column is
dropped in favour of its phase pair. Two reasons carried it. It preserves
comparability with the FourierWall2 recipe this implements, whose own convention
is replace. And it is the only variant that tests what H6 claims to test:
augment confounds the representation against sheer feature count, so a win could
come from having three columns where the comparator has one, which is precisely
the order-mismatched comparison this ADR exists to prevent. Augment would also
collapse the free-tier budget to k<=4, small enough to make the H6 comparison
noisy. Binding bounds are therefore **k<=6 free tier, k<=8 device**, both
independently re-verified.

**2. Twin libraries: KEEP the statsmodels/sklearn substitutes, disclose the
caveat.** The twin's job is to be an order-matched classical bar, not to
reproduce a specific library's published figure, and no EBM benchmark is quoted
anywhere in the submission, so nothing hinges on the implementation identity.
Installing pygam and interpret would add two unvalidated dependencies with their
own solver behaviour ten days before the deadline. The caveat stays disclosed
here and in any H6 reporting: our GAM and GA2M are contract-equivalent
substitutes, so our numbers are not directly comparable to published EBM
figures.
