# Sprint 20 Manual Validation

**Sprint**: 20, Make the Suite Readable Again
**Branch**: `feature/20260930_Sprint_20` | **PR**: #146 (draft)
**Handed over**: 2026-10-02
**Scope**: F97, F93, F98, F99 — all four delivered
**Metered Dirac-3 seconds**: **0**. Nothing touched the device.

Written to a file rather than only the terminal, so it can be reopened without
scrolling back through a session.

## Recommended validation steps

Four things, in the order that makes them easiest to check. Each has a command
you can run yourself.

### 1. The suite is green in a planning window — the sprint's whole point

The defect was that six tests answered "where is this sprint?" rather than "is
the code right?". They failed for days at a time during planning windows.

```
.venv\Scripts\python.exe -m pytest -q
```

Expect **1,409 passed, 73 skipped**. Then, if you want the proof rather than
the claim, the harness that runs the same code against nine different sprint
states is at
`C:\Users\kimme\AppData\Local\Temp\claude\...\scratchpad\prove_f97.py` —
phases 1 through 8, an invented phase slug, and the live record. All nine
green with no code change.

**What to look for**: it should be green now, and it should have been green
during the planning window two days ago. That is the difference.

### 2. The guards still catch a genuinely missing artifact

The risk in fixing item 1 was turning the guards off instead of narrowing
them. Five checks prove that did not happen: with `pr: null`, empty
`github_issues`, `plan_approved: false`, a `plan_doc` naming a missing file,
or a sprint number with no plan — each still goes **red** at a phase where the
artifact is owed.

**What to look for**: the phase gates changed *when* the guards apply, not
*what* they check.

### 3. The close-out hook can no longer be silenced by a slow network

A measured finding worth knowing: **a Stop hook killed at its timeout produces
no exit code at all**, so it cannot block. A timeout fails **open**.

That made the ordering a real defect. The fail-open `gh` checks ran before the
deliberately fail-closed CI check, so one hanging `gh pr list` could kill the
hook before the CI guard ran — precisely when GitHub is slow.

Budget arithmetic, now recorded in the hook itself: 5 + 5 + 4 + 4 = **18s**
against the 20s budget. It was 20 + 20 + 60 + 60 = 160s, where one call
exceeded the whole budget alone.

**What to look for**: this was proven by stubbing a hang, not by reasoning. A
fake `gh` that sleeps 30s goes first on PATH and the CI violation still
appears, in 0.9 seconds.

### 4. The sent correspondence has a recorded hash

```
.venv\Scripts\python.exe -m pytest experiments/src/test_sent_correspondence.py -q -rs
```

Expect 9 passed on your machine. On any other machine the artifact tests
**skip**, and the skip message says plainly that nothing was checked — a skip
reading as a pass is the defect this repository has paid for most often.

The hashes are in `docs/QCI_CORRESPONDENCE_HASHES.md`. The ignore rule on
`docs/qci_package/` did not change, and nothing inside it was written to.

**What to look for**: the sidecar is pinned by one manifest hash rather than
per-file, because a manifest also catches a file added or removed.

## The one decision waiting for you

**Task B assembled the SPECTRA evidence and deliberately did not decide.** The
configuration is a Class 3 allocation call, so it is yours.

Read `docs/SPECTRA_BLOCK_RECONCILIATION.md`. The short version:

- Four records describe the same block and disagree. F2b's ~450 s cannot even
  be repaired, because the schedule underneath it was never recorded.
- **QCi has been told 270 seconds. F90's configuration costs about 1,236** —
  4.6x the figure in the vendor's hands, and 74% of the remaining 1,681.
- The hardware plan is final and sent, so it cannot be edited to match.
- The counter-argument is strong: a schedule-2 block would spend real seconds
  reproducing a configuration measured to lose 8 of 8 overall. Cheap and
  worthless beats nothing, but not by much.

Four options are laid out with their costs. Until you choose, F2b and F5 stay
open and F90 stays unscheduled.

## Verification evidence

- **Full suite**: 1,409 passed, 73 skipped (the count is stated here as a
  handover fact, not as a figure any document owns — run the suite)
- **Outward readability**: clean on both live QCi documents, exit 0
- **CI**: still running on `5ad0f4c` at handover; a watcher is armed, and
  per 7.0 this does not block the handover
- **Working tree**: clean
- **Every guard added this sprint proven RED**: 5 for F97's phase gates, 3 for
  F98's budget and ordering, 4 for F99's hashes, 4 for F93's cross-references

## Actuals

| Task | Estimate | Actual | |
|---|---|---|---|
| A (F97) | 40m | **52m** | over by 12 — six tests, not five, and four distinct boundaries |
| B (F93) | 60m | **47m** | under by 13 |
| C (F98) | 30m | **34m** | over by 4 |
| D (F99) | 20m | **28m** | over by 8 — the drift guard was not in the card |
| **Total** | **171m** | **161m** | within 6% |

First sprint with a complete set of actuals. Sprint 19 recorded two of three.

## What I would flag

**Presence-as-correctness, four times in one sprint.** A guard that asserted
`"270"` appeared somewhere in a document passed when the figure was deleted
from the comparison table, because it is discussed in five places. The same
substitution appeared three times in Sprint 19's review. It is now the most
frequent single defect in my work on this repository, and the pattern is
always the same: asserting a string exists rather than that the thing it
describes is true.

**The F82 escape class bit five times today**, all in heredocs writing Python.
Each was caught by a parse check or a failing test, but one wrote a literal
null byte into a file. The Edit tool avoids it entirely and I should reach for
it sooner.

## After your validation

Phase 6 pushes and updates the draft PR; Phase 7 runs the retrospective and is
the only place `gh pr ready` happens. The merge is yours, at every level.
