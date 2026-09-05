# Sprint 6 Plan: The Diverse Pool

Branch `feature/20260905_Sprint_6` (carried forward from Sprint 5's head per 6.6).
Scope selected by the team lead 2026-09-04: **F31, F3 prep, F23, F24, F32**
(defined-scope rule: this list IS the complete scope).

Plan approved 2026-09-04. Amendment A11 approved. F32's 40-50 metered device
seconds pre-approved, conditional on Task A's outcome, with no further stop.

## Objective

Test whether the CVQBoost optimizer does useful work on a pool that is not
degenerate. Sprint 5 established that our frozen 91-learner pool is
interchangeable (any two learners agree on 99.999% of training rows) and that
the optimization step therefore contributes nothing. Loke et al. (ICAART 2026)
reach AUC-PR above 0.8 on the same hardware and benchmark family with a
heterogeneous pool. F31 asks the direct question. In parallel, three agents
prepare Sprint 7 and 8 work that has no dependency on the answer.

## Capability pre-flight (mandatory, run before estimating)

Run 2026-09-04 on seed 42 at schedule 1 (52 learners, singles only):

| Measure | Frozen dct pool | Mixed dct+lda+lg+knn |
|---|---|---|
| L1 distance from uniform | 8.0e-08 | **2.9e-02** |
| Max weight / uniform | 1.0000000 | **1.0552** |
| Gram off-diagonal ratio | 0.999994 | 0.997010 |
| Solved minus uniform AP | +0.0022 | **+0.0178** |
| Distinct test scores (solved) | 151 | 266 |

Findings that shaped this plan:

1. `build_pool` delegates to eqc-models' builder, whose `weak_cls_type` takes ONE
   value, so a heterogeneous pool needs per-type builds concatenated along the
   learner axis. Valid because H rows are learners and columns are training
   rows, so any stack sharing a train fold forms a consistent J = H diag(sw) H'.
2. All four families build in under 10 s each at schedule 1, so F31 is compute
   cheap. The original 6-10 h estimate was wrong; revised to 180 m.
3. **The optimum leaves uniform on a mixed pool.** That is the result F31 exists
   to find. It is one seed, at schedule 1, and +0.0178 is still BELOW the 0.0268
   MDE, so it is a hypothesis to test at full scale, not a finding.

## Tasks

| # | Task | Card | Track | Model | Est | Metered |
|---|---|---|---|---|---|---|
| A | F31 mixed-family pool, 10 seeds | #31 | Main | Fable/Opus | 180m | 0 |
| B | F3 prep, IEEE-CIS scaffolding | #32 | Agent | Sonnet | 120m | 0 |
| C | F23 QFE recipe + twins | #33 | Agent | Sonnet | 150m | 0 |
| D | F24 SPECTRA machinery + B4 | #34 | Agent | Sonnet | 150m | 0 |
| E | F32 hardware persistence | #35 | Main | Fable/Opus | 90m | 40-50s |

### Task A: F31 mixed-family weak-learner pool

Build the pool by concatenating per-type H matrices on a shared train fold; run
ten seeds at schedule 2 (singles plus pairs); report pool-diversity measures
BEFORE any optimization, then the solved-versus-uniform comparison.

Acceptance criteria:
- Mixed-pool AP and L1-from-uniform for all 10 seeds, with split-dispersion
  intervals labeled as such (not confidence intervals)
- Diversity measured before optimization: Gram off-diagonal ratio, pairwise
  disagreement, distinct-score-vector count, per family and for the mixed pool
- Solved minus uniform tested against the 0.0268 MDE, with the sign pattern
  across seeds reported
- Registered as LABELED EXPLORATORY under amendment A11; the frozen H1b result
  is unchanged and NOT rescored
- Every row in results.json with its evidence tag; tests green

### Task B: F3 prep, IEEE-CIS (no arms run)

Preregistered feature pass (D-normalization, UID excluded, named aggregates,
V-reduction), leakage controls including the shuffled-label positive control,
and a GroupKFold-by-month rolling-origin splitter with tests.

Acceptance criteria: loader plus feature pass with a checksum manifest; the
shuffled-label control collapses to base rate; splitter tested for no temporal
leakage across folds; **zero arms run and zero results.json rows** (execution is
F3 in Sprint 7).

### Task C: F23, QFE phase recipe and twin scaffolding

Phase recipe as a fitted train-only transformer: rank phase
phi = 2*pi*(rank - 1/2)/n - pi, log magnitudes first, calendar cycles, train-only
whitening, low-cardinality columns excluded.

Acceptance criteria: known-answer tests (phase range, rank invariance, no test
leakage); capability pre-flights for the trained-frequency GAM, GA2M and JOINT
twins; H6 cell list and representation tag frozen; A2 variable-count
implications re-checked; ADR drafted. No arm is run.

### Task D: F24, SPECTRA in-segment machinery and the B4 request

Acceptance criteria: in-segment metrics with a matched random-segment control
(same size and base rate); the >= 50-test-positives-per-cell rule enforced in
code; leak-free contract enforced (target/target_real/in_pocket never features);
the 3 strongest FourierWall2 cells frozen with config hashes; `scripts/manifest.py`
proof of whether staged SPECTRA files match the FourierWall2-era files; proxy dry
run (zero metered); B4 request drafted in the HARDWARE_REQUEST template.

### Task E: F32, hardware prediction persistence (metered)

Conditional on Task A: run on the pool worth measuring. Pre-approved at 40-50
metered device seconds (one fit per seed at the measured 4-5 s per fit).

Acceptance criteria: hardware weights and per-transaction scores persisted via
the arm-keyed store path (the A9 fix); operating points recomputed and retagged
[HW]; hardware AP, recall at 0.05/0.1/0.5% budgets, and alert-set Jaccard versus
the proxy reported; metered seconds recorded per fit with the block cap enforced.

## Risks

| Risk | Mitigation |
|---|---|
| **Class 2 decision**: if A confirms the pre-flight, the proposal's central finding changes and section 3 needs a rewrite | Surface to the team lead as an evidence-claim change; do NOT absorb it silently. This is the one thing that will interrupt the auto-advance window |
| Result stays below MDE (+0.0178 vs 0.0268) | Report as "directionally consistent, below our own detectable threshold"; never inflate a sub-MDE difference |
| Deadline: 11 days to Sep 15 | F32 is the drop-first item; Task A is the only one whose absence would weaken the submission |
| Four-track integration conflicts | Agents write to distinct paths; only the main loop touches results.json, the master plan and the paper |
| Metered budget | 40-50 s pre-approved and capped; the runner enforces a per-block cap and charges a conservative estimate on unparseable billing |

## Not in scope

F29 (defer to Sprint 7, where F31 gives it a non-degenerate pool to test), F3
execution, F4, F5, F16. Per the defined-scope rule these are not planned in by
inference.
