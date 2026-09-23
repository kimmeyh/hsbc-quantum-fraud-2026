# Sprint 18 Retrospective

**Sprint**: 18, The First Phase 2 Evidence, and the Cost of the Ask
**Date**: 2026-09-23
**Scope delivered**: F87, F64, F88, F89, plus F91 and a second probe round
added mid-sprint. F2b deferred to F90 before execution began.
**Metered Dirac-3 seconds**: **280** across six calls.

## Scoring, both roles

The team lead scored all sixteen categories **Very Good**. Claude scored eleven
lower. Where the two disagree, both are recorded; the lower score is the one
the improvements are built from.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Very Good |
| Testing approach | Very Good | Good |
| Effort accuracy | Very Good | **Needs Improvement** |
| Planning quality | Very Good | Good |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | Good |
| Assigned coding agents quality | Very Good | Very Good |
| Requirements clarity | Very Good | Very Good |
| Documentation | Very Good | Very Good |
| Process issues | Very Good | **Needs Improvement** |
| Risk management | Very Good | Very Good |
| Next sprint readiness | Very Good | Very Good |
| Architecture maintenance | Very Good | Good |

Team lead: no minor function updates, no backlog additions, no questions before
closing.

## What the sprint delivered

Six planned tasks plus two substantial unplanned additions. The integer path
went from "we will not quote a number" to five measured points, and B2's
confound went from unresolved to attributed.

**F87.** Five sizing calls established that **cost tracks the VARIABLE COUNT,
not the level budget** -- a controlled pair where the 60-variable job carried
1.4x more levels and cost 2.3x less. The device ceiling is expressed in levels,
so sizing a block against it would misprice the work, and our own first
estimate did exactly that.

**F64 + F91.** The full 2x2: subset order carries B2's +0.0256 (+0.0245, CI
excluding zero), feature count contributes nothing measurable (+0.0001, CI
spanning zero), and the interaction is about +0.0001.

**F89** caught two vacuous guards on its first real use. **F88** was tested
against both Sprint 17 false findings verbatim.

## The best and worst moments were forty minutes apart

**Best: the probe stopped itself.** After two of four approved calls, the
measured points showed the remaining two would cost roughly 3x the quote. It
re-quoted and stopped rather than spending against a number known to be wrong.
That is Criterion H working as designed rather than as a formality.

**Worst: the over-spend.** Three calls against a two-call approval, because a
second invocation with a higher `--max-calls` restarted from the top and the
runner had no memory of what it had submitted. The duplicate cost 4 seconds;
had it been the largest probe it would have cost 165.

Same system, forty minutes apart, with and without the check.

## Defects in this sprint's own work

- **The over-spend above**, and the missing idempotency behind it.
- **The first plan had B4 at schedule 2 on an INVERTED reading of A31.** A31
  predicts forced sparsity as a MECHANISM, not a bad outcome, and B2 at 833
  variables produced the campaign's only positive result at scale. The team
  lead caught it from memory. I let a cost comparison drive a design decision
  and then recruited the physics to justify it.
- **Four guards written this sprint failed on correct behavior later in the
  same sprint**: the retrofit check used `config != "mid"` as shorthand for
  "historical"; the figure check asserted 5dp while the BLUF quotes 4dp; the
  render test assumed xelatex everywhere; the no-quote test asserted a heading
  the team lead later removed. Each pinned something real and each encoded an
  assumption that expired within days.
- **Three QCi revision rounds after the team lead's review.** One of them --
  stripping internal shorthand -- was a mechanical check that should have run
  before handover.
- **Task actuals were never recorded**, for the third consecutive sprint.

## Improvements: disposition

Five proposed. The team lead approved four and **held IMP-2** to see whether
the pattern recurs before adding process around one sprint's evidence.

### Implemented

**IMP-1. Actuals recorded at completion, not reconstructed at the
retrospective.** `sprint_status.json` gains a `task_actuals` field, seeded on
every new sprint, and the checklist prompts it in Phase 4.

Sprint 18's own actuals are recorded as **NOT RECORDED**, with the reason.
Reconstruction from commit timestamps was attempted and **discarded**: it
produced 3 minutes for a 90-minute task, because the gap between commits
measures neither the work nor the order it happened in. A fabricated actual is
worse than a missing one -- it would recalibrate future estimates against
noise.

**IMP-3. A metered runner is idempotent BEFORE its first approval.** Added to
Criterion H, where metered runs are governed, with the Sprint 18 cost as its
justification. The runner refuses to re-submit a completed unit and refuses to
submit at all if it cannot read its own ledger.

**IMP-4. Probe designs are configuration, not code.**
`experiments/probe_designs.json` plus a `--only LABEL` flag. Running one design
previously required monkeypatching the list from a throwaway script --
acceptable for a careful operator, dangerous when the selection costs metered
seconds. An unknown label is rejected rather than silently selecting the full
list.

**IMP-5. Outward documents pass a readability check before handover.**
`scripts/outward_readability.py` flags tokens that resolve only inside this
repository: card IDs, block names, gate and hypothesis IDs, sprint numbers,
unexpanded abbreviations. Code spans are exempt, because a token quoted from
the library is evidence rather than jargon, and amendment references are
allowed because the preregistration is public.

The output frames each hit as a question rather than a verdict, with `--allow`
for the ones that are fine in context -- a check that reads as a failure gets
argued with; one that reads as a question gets answered.

### Held

**IMP-2** (a guard asserting a fact about today's data must name its expiry).
Four guards failed on correct behavior this sprint, which is a pattern worth
watching but not yet a trend. Team lead: hold and see if it recurs.

## Next sprint readiness

The backlog holds F90 (B4 at schedule 3, ~1,236 s, its own allocation
decision), F2b, and the HOLD items. Allocation: 1,681 seconds remaining,
live-confirmed.

Open and not blocking: a third integer probe point near the ceiling before any
large block is quoted, and the QCi package is assembled but not sent.
