# Sprint 8 Plan: The Second Dataset

Branch `feature/20260906_Sprint_8` (carried forward from Sprint 7's head per 6.6).
Scope: **F3** (defined-scope rule: this single item IS the complete scope).

## Objective

Run the preregistered IEEE-CIS protocol: 590,540 transactions, 3.5% prevalence,
several hundred features. This is the second-largest remaining evidence gap and
the regime where the model form has room to differ from ULB's 30 anonymized
components. It also supplies the temporal protocol our single time-ordered ULB
split cannot.

Team lead scope decision (2026-09-05, recorded on the F3 card): run BOTH pool
configurations. The frozen single-family arm is the preregistered comparator and
must be carried for continuity with every prior result; the tuned four-family arm
is where F33 measured the accuracy to live.

## Capability pre-flight (mandatory, run before estimating)

Run 2026-09-06 against the staged data and the Sprint 6 scaffolding. Three
findings, and each changed the plan.

**1. The scaffolding does NOT deduplicate, and section 4 item 7 requires it.**
"Exact duplicates removed before splitting; counts reported PER DATASET." The
ULB loaders implement it; `ieee_loader` does not. This is the same class of
defect as amendment A17, in code written in the same sprint and the same style
as the three modules that caused it.

The measured impact is small but the compliance question is not:

| | ULB | IEEE-CIS |
|---|---|---|
| Rows in duplicate groups | 1,854 | **6** |
| Fraud rate in duplicates | 1.73% | **0.00%** |
| Fraud rate overall | 0.17% | 3.50% |
| Enrichment | 10x | none |

On ULB the duplicates were 10x enriched in fraud and their removal moved a
result across the MDE. On IEEE-CIS there are six duplicate rows and none is a
fraud, so deduplication will change nothing measurable. We do it anyway, and
report the count, because the protocol says to and because "it would not have
mattered" is a conclusion available only after checking.

**2. Section 4 item 4's controls are NOT implemented.** The time-consistency
filter (single-feature train-early/test-late AUC must exceed 0.5) and adversarial
validation (target AUC near 0.5, recursively dropping top adversarial features),
both run INSIDE training folds only, exist in neither `ieee_features` nor
`ieee_splits`. `ieee_baseline.py` explicitly labels them out of scope for its own
scale check. They are in scope for F3 and are the largest unestimated piece of
this sprint.

**3. What IS built and tested** (Sprint 6, 38 tests): the loader with checksum
verification, the D-normalization and UID-aggregate feature pass with UID
excluded, V-column reduction, frequency encodings, and the GroupKFold-by-month
rolling-origin splitter with a no-temporal-leakage invariant. Measured 590,540
rows, 434 columns after join, prevalence 3.499% against the prereg's stated 3.5%,
both source checksums matching MANIFEST.json.

## Tasks

| # | Task | Est | Metered |
|---|---|---|---|
| A | Protocol compliance: deduplication + the item 4 controls | 90m | 0 |
| B | Classical arms on the reduced set, rolling origin | 120m | 0 |
| C | CVQBoost proxy arms, both pool configurations | 120m | 0 |
| D | H3 ladder cells and the results write-up | 90m | 0 |

Total 420m against the card's "~1 day". The card's estimate predates the
pre-flight; task A did not exist in it.

### Task A: protocol compliance

Add deduplication to the IEEE loader with the count reported, matching the ULB
loaders. Implement the item 4 controls as functions that run inside training
folds only: the time-consistency filter and adversarial validation with recursive
feature dropping. Tests for each, including one that fails if either control sees
a validation or test row.

Acceptance: `test_every_fold_builder_deduplicates` extended to cover the IEEE
path; duplicate count reported in the results record; both controls tested for
train-fold-only access; the shuffled-label positive control collapses to base
rate on IEEE-CIS as it does on ULB.

### Task B: classical arms

Tuned XGBoost, LightGBM and CatBoost on the reduced feature set under the
rolling-origin protocol, equal 100-trial Optuna budgets per section 6.

Acceptance: per-fold and pooled AUPRC with the evaluation window named; the
Tuning Budget Equivalence table extended with IEEE-CIS rows; every figure in
results.json with an evidence tag.

### Task C: CVQBoost proxy arms, both configurations

Frozen single-family and F33 tuned four-family, on the same folds and features.
Proxy only, zero metered seconds. Feature count sized to the free-tier ceiling
(A12) so the configuration remains hardware-runnable if a grant lands.

Acceptance: both arms reported with matched k and protocol; every cross-arm
difference routed through `comparators.reported_difference` so a mismatch raises
rather than serializing; differences tested against the MDE.

### Task D: H3 ladder and write-up

H3 is exploratory and scored only if at least three ladder cells per dataset run.
Report descriptively otherwise. Update the paper and QCi package with whatever
IEEE-CIS shows.

## Risks

| Risk | Mitigation |
|---|---|
| **The item 4 controls are unestimated work** on a 9-day deadline | Task A is first. If it overruns, tasks C and D compress before B, since a classical baseline on a non-compliant protocol is worth less than no baseline |
| A17 recurrence in new IEEE code | Task A extends the fold-builder test to the IEEE path before any arm runs |
| IEEE-CIS results contradict ULB | That is a finding, not a failure. The proposal already states ULB's limits; a second dataset disagreeing is worth more than a second dataset agreeing |
| Memory: 590,540 x 434 | The Sprint 6 loader already handles the full file; tests use sampled fixtures |
| Deadline: 9 days to Sep 15, target Sep 13 | F3 is the last large evidence item. F16 and F10 are the finalize gate and stay unscheduled until this lands |

## Not in scope

F35, F29, F4, F5, F16, F10. Per the defined-scope rule these are not planned in
by inference. F35 is deferred deliberately: it is 2h of test-writing best written
against F3's actual claims rather than in the abstract.
