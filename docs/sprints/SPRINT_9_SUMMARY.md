# Sprint 9 Summary: Representation, and Paying What We Promised

**Dates**: 2026-09-07 to 2026-09-08 (~1.5 days)
**Cards**: #50 (F4), #51 (F14), #52 (F16) -- all closed. #40 open pending QCi.
**Metered Dirac-3 seconds spent: ZERO.**

## What shipped

**F4 -- H6, the last preregistered experimental arm.** The QFE phase
representation given to every arm, with the order-matched classical twins the
Fourier Wall result requires. Ten ULB seeds, 20 cells.

| Quantity | Value |
|---|---|
| Mean delta, baseline | -0.0685 |
| Mean delta, QFE | -0.0800 |
| **Representation shift** | **-0.0115** |
| Paired SD | 0.0135 (ratio 0.85) |
| Falsifier | **fired** |

The answer is a measured null: the phase representation does not move the
quantum-minus-classical delta by an amount we can claim. The shift is 43% of
our 0.0268 MDE, negative on 7 of 10 seeds. Reported as "a small negative shift
that does not reach claimable size" -- not "no effect", not "the representation
widens the gap". The framing was fixed in writing before any result was seen.

**F14 -- the eqc-models feedback package.** `docs/QCI_EQC_MODELS_FEEDBACK.md`,
3 pages, four findings each stating what we observed, what we expected and what
we did. Every claim cites a file and line, verified mechanically. It converts
a promise in the QCi letter into an attachment.

**F16 -- minimal CI.** `pytest -m "not slow"` plus advisory lint on PRs to
develop. The point is the dirty-tree gate: a test that modifies tracked files
now fails the build, which is the Sprint 8 defect that lost an evidence file.

## The sprint's defining fact: three runs, two discarded

| run | wall clock | outcome |
|---|---|---|
| 1 | 3h 12m | 8/20 cells; crashed on a spline basis refitted on TEST data |
| 2 | 7h 42m | 20/20 cells; DISCARDED -- twins never received the treatment |
| 3 | 7h 57m | 20/20 cells; reported |

18.9 hours of compute against a 10-minute estimate.

**Both defects share a shape: the code ran, the numbers were plausible, and the
experiment was not the experiment the preregistration specifies.** Run 1's
crash was lucky -- the underlying error was silently wrong through two runs
before it raised. Run 2 completed cleanly and was caught only because per-arm
scores were inspected before drafting.

The twin defect is the instructive one. Both GAM and JOINT selected input
columns by variance; ULB's `Time` column has variance 2.3e9 while the QFE phase
columns are whitened to unit variance, so a phase column could never be chosen.
Two of three twins returned identical scores in 10 of 10 seeds -- present in the
record, absent in substance.

**The fix changed what the number means, not the number.** A GBDT was the best
classical arm in all 20 cells, so the twins never set the delta. But mean
baseline AP is XGBoost 0.8328, CatBoost 0.8185, **GAM 0.7893**, CVQBoost 0.7646:
the corrected GAM twin outscores the quantum arm, where before it scored 0.2590
and was noise. "Best classical" now denotes a bar containing a
periodic-structure model, which is what makes the comparison survive the
Fourier Wall objection.

## QCi letter sent

Sent 2026-09-08 09:59:03 -0400, tagged `qci-letter-sent-20260908` (commit
9774e40). Acknowledged; no substantive reply yet. Restructured at the team
lead's direction to lead with the ask, the goal and the return as bullets.

The repository diverged from what QCi holds at 16:03 the same day, when the H6
result replaced the letter's "None have been run" passage. The sent version was
accurate at 09:59 and the correction NARROWS the ask, so no correction is owed.
Team lead decision: hold the H6 follow-up and fold it into the next substantive
exchange.

## Retrospective improvements (1, 2, 4 applied; 3 declined)

1. **Guard the artifact, not just the code.** `test_artifact_guards.py` asserts
   that every runner writing evidence has a test reading it. It found two real
   gaps on its first run; `test_ieee_artifacts.py` closes them with eight
   preregistration checks.
2. **Runtime sizing must name the dominant term.** Sprint 8's rule was followed
   and still missed by 47x, because the CVQBoost pool build -- 300s of 335s per
   cell -- was never on the list.
4. **Verify an instrument before iterating against it.** Third instance of the
   pattern.

## Numbers

| | Sprint start | End |
|---|---|---|
| Tests passing | 173 | 191 |
| Test files | 18 | 21 |
| Commits | -- | 26 |
| Metered seconds | -- | 0 |

Two tests xfail by design: appendix 4/3 and proposal 7/6 pages, both tracked as
F38 with `strict=True` so the markers cannot outlive the card.

## Registered to the backlog

**F40 (~1h) -- segment non-public material, BLOCKS F37.** The seven `0*`
team-lead working files and `experiments/reference/fourierwall2/` move to a
folder outside the repository. Structural scanning found contact details in one
file and credential-shaped patterns in another; `.env` was verified never
committed, and QCi job identifiers are opaque hashes that stay. History is
deliberately not rewritten -- a team-lead decision, recorded as such.

## Carried into Sprint 10

Card #40 open pending QCi's substantive reply. Four submission blockers in
order: F40 -> F37, plus F38 and F10.
