# Sprint 21 Summary: The SPECTRA Block, and a Bar That Can Read It

**Sprint**: 21 | **Dates**: 2026-10-04 to 2026-10-06
**Branch**: `feature/20261004_Sprint_21`
**PRs**: #152 to develop, #158 develop to main (both merged 2026-10-06)
**Cards**: F90, F100, F101, F122 delivered. F123 and F124 registered by the
team lead.
**Metered Dirac-3 seconds**: **653** (B5 13 + B4 640), reconciled against the
device balance, 1,675 s to 1,022 s

Sources: `SPRINT_21_RETROSPECTIVE.md`, `SPRINT_21_VALIDATION.md`,
`docs/B4_B5_HARDWARE_RESULT.md`, git history, PR #152. Written during
Sprint 22 planning per the three-doc rule; the master plan is not a source.

## The objective, and what it found

**Run the SPECTRA block that could show an effect, and build the classical
bar that makes its result readable.** Both happened, and the answer is
negative.

**The H5 replication did not reproduce on Dirac-3.** Against a random group of
the same size and fraud rate, the pocket scored worse on all 8 scoreable cells.
Inside the pocket, the device matched its classical proxy within 0.0072 AUPRC
on every cell. HGB and GA2M beat the proxy on every cell and seed. energy_steel
-- the prior work's strongest cell -- could not be scored, because its matched
control is arithmetically impossible.

## What was delivered

- **F90 (B5 and B4)**: 22 fits, 0 failures, every job id retained, every
  returned sample stored. The cost conflict was settled by measurement: B2's
  82.4 s/fit anchor was right.
- **F100**: the complete classical bar, measured at 3.77 s per cell against a
  ~6 hour estimate.
- **F101**: `in_pocket` is predictable from the phase features at AUC
  0.93-0.99, so a router keyed on them is not independent.
- **F122**: four accurate-but-weak guards rewritten, each proven red.
- **The energy_steel control finding**: "13 of 13" corrected to 8 of 13 in
  three documents; the repaired design specified for Phase 2 in F102.
  `PREREGISTRATION.md` untouched.

## Defects in this sprint's own work

- **The first B4 and B5 runners hand-built the request to QCi** with invented
  field names; QCi rejected one. They were rebuilt on `eqc_models`, as every
  earlier block had used.
- **Two of my own tests submitted real Dirac-3 jobs** once the window opened.
  Nothing was billed, by luck. Runners now refuse inside any test process.
- **A test was rewriting the committed gate report**, invisible for sprints.
  It now restores the file.
- **Task A asked the team lead for data the repository held**, and B5 was
  called undefined when the preregistration defines it.
- **Phase 1 analysis code (`spectra_segment.py`) changed without an
  amendment.** Recorded on F123.
- **Four status-footer timestamps were typed by hand.**

## Improvements

IMP-1 (the pre-flight reads the proven runner and the preregistration) and
IMP-2 (a typed footer is held back by the every-turn Stop hook) applied. IMP-3
(the suite may not change evidence) and IMP-4 (guard Phase 1 analysis code)
carded on F123.

## Effort

- Task A: 0 min (already satisfied)
- Task B: 58 min (estimate 45)
- Task C: 229 min plus 653 device seconds (estimate 240)
- Task D: 133 min (estimate 360)
- Task E: 34 min (estimate 60)
- **Total: 454 minutes against 750 estimated**

## Next sprint readiness

`feature/20261006_Sprint_22` was cut from the Sprint 21 branch on merge
notification. F124 (research before any further Dirac-3 run) and F123 (Phase 1
/ Phase 2 separation) lead the backlog, and every open card that can spend
device seconds depends on F124. An unexplained 6 s gap in the device balance
before Sprint 21 is on record in `CHECKLIST-Phase2.md`.
