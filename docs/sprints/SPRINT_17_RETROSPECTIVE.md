# Sprint 17 Retrospective

**Sprint**: 17, Clear the Deck for Phase 2
**Date**: 2026-09-22
**Scope delivered**: F86 (new), F82, F83, F84. F85 closed into F86, F81 closed.
**Metered Dirac-3 seconds**: ZERO, as planned.

## Scoring, both roles

The team lead scored all sixteen categories **Very Good**. Claude scored
thirteen of them lower. Where the two disagree, both are recorded; the lower
score is the one the improvements are built from.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Good |
| Testing approach | Very Good | Good |
| Effort accuracy | Very Good | **Needs Improvement** |
| Planning quality | Very Good | **Needs Improvement** |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | Good |
| Assigned coding agents quality | Very Good | Very Good |
| Requirements clarity | Very Good | Very Good |
| Documentation | Very Good | Very Good |
| Process issues | Very Good | **Needs Improvement** |
| Risk management | Very Good | Good |
| Next sprint readiness | Very Good | Very Good |
| Architecture maintenance | Very Good | Very Good |

Team lead: no minor function updates for the next sprint plan, no backlog
additions, no questions before closing.

## What the sprint delivered

Nine tasks, 2,357 insertions across 28 files, and the backlog afterwards holds
only experiments -- the stated success condition. Tests grew 1,031 -> 1,083
during the sprint and to 1,164 with the retrospective improvements, across
seven new guard files.

## The two patterns worth carrying forward

**Every significant defect was found by VERIFICATION, not by review and not by
the suite.** The suite was green while the cross-repository guard had never run
in CI, while two F82 tests were vacuous, and while the budget table omitted the
arm the whole submission is about. A green suite is the weakest signal in this
repository, and this sprint produced five more instances of that.

**Twice I wrote down a "finding" that was my own incomplete reading of an
artifact.** The QPU reconciliation and the linear-term span. Both times the
correct answer was already recorded in a file I had not opened. Both times I
wrote the false version before checking.

## Defects in this sprint's own work

- **The renderer destroyed the filed PDFs twice.** `render_all.py` rebuilt all
  three submitted artifacts on any invocation. The first fix added
  `--allow-overwrite-submitted`, and the very next command passed it -- not to
  rebuild a submission, but because it was the fastest way to get an unrelated
  test running. Recovered from git both times and hash-verified.
- **Five injections returned GREEN**, each a defect in the verification rather
  than the thing verified. Three rounds were needed on F82 alone.
- **The amendment approval token was left on disk**, disabling the
  reactive-amendment guard until three hook-parity tests caught it.
- **The escape-eaten class bit three times during the sprint fixing it**,
  including inside the test file that documents it.
- **A false finding was committed** (the linear-term span) and withdrawn the
  same day, before it reached any outward document.

## Improvements: disposition

Seven proposed. The team lead's rule for the conditional ones: **if the change
itself prevents the problem, do it now; if it only says to be careful, card
it.**

### Implemented this sprint

**IMP-1. The sprint total is DERIVED from the cards, never asserted in the
plan.** The team lead rejected the original proposal -- estimating before the
plan is written is stale and of little use -- and replaced it with the correct
ordering: each card carries its own estimate from its own detailed scope,
dependencies between cards are stated, the total is computed from those and
recorded, and the plan is then written or updated from the recorded total.
Applied to `SPRINT_PLANNING.md`, `SPRINT_EXECUTION_WORKFLOW.md`,
`BACKLOG_REFINEMENT.md` and `SPRINT_CHECKLIST.md`.

**IMP-4. No guard ships with an override flag in the commit that creates it.**
Added to CLAUDE.md's NOT-do list with the Sprint 17 evidence.

**IMP-5. The amendment token is now consumed by the hook**, not deleted by
memory. `test_amendment_token.py` pins the full cycle: blocks without a token,
allows exactly one edit with one, blocks again after. Proven by injection.

**IMP-6. `test_skip_conditions.py` flags any skip gated on a retired
dependency.** It found a real instance on its first run: two skip reasons
telling the reader to run `render-pdf.ps1`, deleted in Sprint 16. Also pins
that the cross-repository guard can never regain a skipif.

**IMP-7, as redefined by the team lead.** Not "read the rendered page" as a
rule, but requirements around the `.md` sources that generate the PDFs, so
wording established after submission is preserved.
`test_qci_document_requirements.py` enforces seventeen of them across the three
QCi sources. All nine wording requirements proven to fire by injection. The
team lead's intent on reviewing the rendered document stands -- this does not
replace it.

### Carded for a future sprint

**IMP-2 -> F88** (Priority 3). The proposal was "grep the summaries before
writing a contradiction claim". The team lead declined it: better to get it
right the first time than to add a step that fires on every claim and prevents
nothing structurally. F88 is to design and build a mechanism, with the two
Sprint 17 instances as its acceptance test.

**IMP-3 -> F89** (Priority 4). An injection helper that re-reads through the
same accessor the test uses and fails loudly if the mutation did not land. The
rule already exists in CLAUDE.md and was violated five times by its author,
which is the argument for building it rather than restating it.

## Next sprint readiness

The backlog holds F64, F2b, F87 (size the integer-solver block, Priority 2, do
first), F88, F89, and eight HOLD items. Nothing else competes.

Open and not blocking: the hardware plan still says "we are not quoting a cost"
for the integer block until F87 runs, and the QCi package is assembled but not
sent. Claude does not send it.
