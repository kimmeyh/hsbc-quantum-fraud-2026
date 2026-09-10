# Sprint 12 Plan: Spend the Grant, Then Submit

**Dates**: 2026-09-10 to 2026-09-12 (evidence freeze Sep 12, target submit Sep 13, hard deadline Sep 15)
**Branch**: `feature/20260910_Sprint_12`
**Scope** (DEFINED, team lead 2026-09-10): **F2b (B2 + B3)**, then updates and full
testing, then the independent review with updates as needed. F38, F37 and F10
follow in sequence as the submission chain.

## Objective

Spend the 3,000 granted seconds on the pre-submission work they were requested
for, then cut, publish and submit. The QCi letter names these exact blocks as
what the access would buy; leaving them unspent while citing them in the
submission is its own inconsistency.

## Capability pre-flight (run 2026-09-10 BEFORE estimating)

Every number measured today. **Three findings change the plan materially.**

| Check | Expected | Measured | Consequence |
|---|---|---|---|
| B2/B3 runners exist | assumed | **NO** -- `run_hardware.py` defines only `B1_VARIANTS`; there is no B2 or B3 config | Build work before any call |
| IEEE hardware path | assumed | **NO** -- `run_ieee_cvqboost.py` solves via `qp.` (classical proxy) with no submission path | B3 needs a new runner |
| B2 pool build (k=17, sched 3, 833 vars) | ~97s, as at 91 vars | **>617 CPU-s and still running** at time of writing | The LOCAL build dominates, not the device |
| B2 cost estimate | ~450s for 11 fits | **UNKNOWN** -- `estimate_for` returns `known: False`, no degree-3 anchor within 2x of 833 vars | Criterion H request must say "unknown" and bound by call count |
| Degree-2 cost, ~105-136 vars | -- | 4-10s, 28 anchors | B3's ladder cells are estimable |
| IEEE-CIS staged | assumed | `manifest.py verify` -> **VERIFY OK** | B3 prerequisite met |
| Allocation | 3000 | **2990** (probe spent 10) | Confirmed |
| Queue window | after 17:00 | now 23:27, **inside the window** | Submit tonight, not tomorrow afternoon |

**The pre-flight found that this sprint's headline item has no code.** The frozen
grid describes B2 and B3; the runners were never written, because the ceiling
foreclosed them. That is the real work of this sprint, and it was invisible in
the card.

## Tasks

| # | Task | Est | Runtime | Dominant cost | Model |
|---|---|---|---|---|---|
| A | **B2 runner**: k=17 schedule 3 config, wired through `metered_call` | 90m | build measured below | pool build, >10 min/fit | Opus |
| B | **B2 execution**: 11 fits, ULB full config | 30m | **[unbounded]** | Criterion H, cost UNKNOWN | Opus + **team lead** |
| C | **B3 runner**: IEEE-CIS hardware submission path | 120m | -- | no hardware path exists today | Opus |
| D | **B3 execution**: 16 fits, IEEE-CIS + ladder cells | 30m | ~650s est (free-tier basis) | Criterion H | Opus + **team lead** |
| E | **Documents updated** with B2/B3 results, amendment registered | 90m | ~2m | A22 drafting | Opus |
| F | **Full test suite + artifact regeneration** | 30m | ~4m | suite is ~2 min | Opus |
| G | **Independent review** (fresh-eyes, deferred from Sprint 11) + updates | 90m | -- | review turnaround | Opus |

**Then the submission chain**: F38 (~3h, 250pt + 439pt to cut) -> F37 (45m,
irreversible) -> F10 (0.5 day). Sequencing fixed in advance by Sprint 11
improvement 5 and not re-litigated here.

### Runtime is the risk, and it is NOT device time

The measured pool build at 833 variables exceeded 617 CPU-seconds and had not
finished. Eleven B2 fits could therefore cost **hours of local CPU** before a
single second is billed. This is the Sprint 9 lesson exactly: the dominant term
was never the one being estimated.

**Mitigation, in order:**
1. Measure one complete B2 fit end to end before committing to eleven
2. If the build exceeds ~15 min/fit, propose reducing B2 to a subset of seeds
   and say so -- a smaller B2 that runs is worth more than a full B2 that does not
3. B3's cells are degree-2 and far cheaper; if only one block fits, **B3 goes
   first**, which is also the frozen spend priority (B3 > B2)

### Criterion H, with provenance (Sprint 11 improvement 2)

- **B2**: 11 fits, cost **UNKNOWN**. No measured anchor at degree 3 within 2x of
  833 variables. The request will be bounded by CALL COUNT, not by a quoted
  number, and I will propose running ONE fit first to establish the anchor
- **B3**: 16 fits, estimated 4-10s each from 28 degree-2 anchors, so roughly
  **65-160s**. The frozen grid's ~650s was a free-tier figure and is likely high

## Acceptance criteria

**A/C (runners)**: B2 and B3 configs exist, route through `metered_call.run_metered`
so job ids are captured at submission, and are exercised offline with a fake
client before any real call.

**B/D (execution)**: every fit recorded in `results.json` with `[HW]`, a job id,
and a balance-measured cost; the ledger shows intent before outcome for each.

**E (documents)**: B2/B3 results reported with evidence tags; an amendment
registers the arms as run; no figure asserted that does not trace to an artifact.

**F (testing)**: full suite green; `gate_report.md` regenerates with no diff; all
PDFs render.

**G (review)**: fresh-eyes findings addressed or explicitly deferred with reason.

**Premise falsifier for the sprint**: the premise is that B2 and B3 are runnable
within the calendar. Falsifier: one complete B2 fit taking more than ~20 minutes
of wall clock. If that fires, B2 is reduced or dropped in favour of B3, and the
proposal keeps its `[PROJ]` framing for the unrun block -- which the frozen grid
already anticipates.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **B2 pool build exceeds the calendar** | **High** -- already >617 CPU-s unfinished | Measure one fit first; reduce seeds; B3 has priority |
| B2 cost unknown, could be large per fit | Medium | One fit establishes the anchor before ten more |
| New evidence grows the documents again | **Certain** | F38 already re-measured at 250pt + 439pt; cut AFTER evidence lands |
| Writing two runners at T-2 | Medium | They route through tested infrastructure; the new code is config plus a submission path |
| F37 irreversible with less review time | Medium | It follows F38, which follows the evidence. Order is fixed |
| Suite regression from new runners | Low | Artifact guards require a test per evidence file |

## Decision-Class checkpoints

- **Class 1**: an amendment registers B2/B3 as run. The frozen grid already
  specifies both, so this records execution rather than changing protocol
- **Class 2**: any B2/B3 result that changes a headline claim is surfaced, not
  applied silently
- **Class 3**: reducing B2's seed count is a scope change and is the team lead's
  call. I will propose it with the measurement, not decide it

## Definition of Done

B2 and B3 executed or explicitly reduced with reason; results in the documents
with evidence tags and an amendment; suite green; artifacts regenerate; the
independent review's findings addressed; then F38, F37, F10 in that order, ending
with the team lead's portal submission.
