# Sprint 7 Plan: Direction into Result

Branch `feature/20260905_Sprint_7` (carried forward from Sprint 6's head per 6.6).
Scope: **F33 + F34 + the QCi/paper update** (defined-scope rule: this list IS the
complete scope). Plan approved 2026-09-05 with all tasks and sub-tasks approved
and the auto-advance window open to Manual Validation.

## Objective

Sprint 6 established that the CVQBoost optimizer does real work on a
heterogeneous pool, but bought no accuracy with it: absolute AUPRC 0.7565
against the frozen pool's 0.7681 and Loke et al.'s reported >0.8 on the same
hardware and benchmark family. F33 tests whether the remaining gap is learner
QUALITY and tuning rather than pool composition. That is the difference between
reporting a direction and reporting a result, and it lands before the QCi letter
goes out on Monday night, so its outcome belongs in that letter either way.

## Capability pre-flight (mandatory, run before estimating)

Seed 42, k=6, schedule 2, one build per family:

| Family | Learners | Build | Params accepted |
|---|---|---|---|
| dct | 15 | 2.1 s | `max_depth=2, class_weight='balanced'` |
| lg | 15 | 1.2 s | `max_iter=300, class_weight='balanced'` |
| lda | 15 | 0.6 s | (none needed) |
| knn | 15 | 3.0 s | `n_neighbors=5` |

Two findings that shape the plan:

1. **Per-family hyperparameters pass through**, including
   `class_weight='balanced'`. That is the fit-time imbalance handling no prior
   control varied: the Sprint 5 class-weighted control reweighted only the
   ENSEMBLE OBJECTIVE and left the learners themselves untouched, which is why
   it could not move a degenerate pool.
2. Builds total under 7 s per configuration, so a sweep is compute-cheap. The
   cost is wall time across seeds, not per-fit expense.

## Tasks

| # | Task | Card | Est | Metered |
|---|---|---|---|---|
| A | F33 tuned mixed pool, sweep then 10 seeds | #38 | 150m | 0 |
| B | F34 spend-guard property tests | #39 | 60m | 0 |
| C | QCi package + paper update with the F33 outcome | #40 | 90m | 0 |

### Task A: F33 tuned mixed pool

Two stages so the expensive stage runs once on a chosen configuration.

**Stage 1, sweep on seed 42 only** (validation AP, never test): families at
Loke-style hyperparameters; class-weighted and balanced-bootstrap variants;
per-family learner counts sized against the free-tier 100-variable ceiling
(A12). Selection on VALIDATION AP, per the repo-wide rule.

**Stage 2, the selected configuration over ten seeds**, reporting exactly what
F31 reported so the two are comparable: absolute test AUPRC, L1 from uniform,
max weight over uniform, solved-minus-uniform against the 0.0268 MDE, and the
diversity measures BEFORE optimization.

Acceptance criteria:
- Absolute AUPRC reported against BOTH the frozen pool (0.7681) and the Loke
  figure (>0.8), with the comparison to Loke stated as a design comparison and
  never as a reproduction of their number
- Solved-minus-uniform tested against the MDE with the per-seed sign pattern
- Diversity measures before optimization, so a gain cannot be attributed to the
  optimizer when it came from the pool
- Registered as LABELED EXPLORATORY under amendment A13; H1b and every frozen
  gate keep their committed scoring and are NOT rescored
- Selection on validation AP only; test figures read once, after selection

### Task B: F34 spend-guard property tests

Three defects landed on this path in one sprint: a cap set above the approval, a
double-count that halted a block at half its real spend, and billing that
returned the first usage value rather than the conservative maximum. The guard
is what stands between an approval and an overrun, so it gets tests of its own.

Acceptance criteria: the cap never exceeds its stated approval; spend derives
from exactly one source so double-counting is structurally impossible;
unparseable billing is charged the conservative estimate and flagged; the cap
bounds the call it PRECEDES; and list-valued usage keys bill at their maximum.

### Task C: QCi package and paper update

The QCi letter sends Monday night 2026-09-07. F33's outcome belongs in it
whichever way it goes: a closed gap strengthens the request, and an unclosed one
is itself the finding QCi would want about how CVQBoost behaves at low
prevalence. Update the letter, proposal and appendix, rebuild all nine PDFs,
verify page limits and the confidentiality scan.

Claude never sends. The send decision and action are the team lead's.

## Risks

| Risk | Mitigation |
|---|---|
| **F33 finds nothing** and the mixed pool stays below the frozen pool | That is a publishable result, not a failure, and the plan says so before the run. It would mean pool composition is not the binding constraint and something else is, which changes the Phase 2 direction rather than emptying it |
| Sweeping on test AP would be a protocol violation | Selection on VALIDATION AP only, per the repo-wide rule; test read once after selection |
| A tuned win gets over-claimed | Same MDE discipline as F31: +0.0076 was reported as directional and anything below 0.0268 gets the same treatment |
| Deadline: 10 days | Task A is the only item whose absence weakens the submission; B and C are small |

## Not in scope

F3 (Sprint 8, scaffolding already built), F29, F4, F5, F16, F10. Per the
defined-scope rule these are not planned in by inference.
