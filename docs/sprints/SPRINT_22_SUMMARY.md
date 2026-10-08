# Sprint 22 Summary: Separate the Phases, Then Look for Better Numbers

**Sprint**: 22 | **Dates**: 2026-10-06 to 2026-10-07
**Branch**: `feature/20261006_Sprint_22`
**PRs**: #159 to develop, #166 develop to main (both merged 2026-10-07)
**Cards**: F123, IMP-3, F124, F17, F20, F125 delivered. F126 and F127
registered at Manual Validation.
**Metered Dirac-3 seconds**: **0**. Balance 1,022 s throughout.

Sources: `SPRINT_22_RETROSPECTIVE.md`, `SPRINT_22_VALIDATION.md`,
`docs/PHASE_SEPARATION.md`, `docs/phase2/`, git history, PR #159. Written in
the Sprint 22 Pass 1 sweep per the three-doc rule; the master plan is not a
source.

## The objective, and what it found

**Keep Phase 2 work out of the Phase 1 files, then look for levers that
improve SPECTRA prediction before any further device run.** Both happened.
The levers found reach parity with the classical bar, not advantage.

- **Leaf regularization is the top lever** (F124, rank 1). On energy_steel,
  `min_samples_leaf=20` lifts CVQBoost on the proxy from 0.902 to 0.973 AUPRC
  over 5 seeds, level with HGB. Nothing found closes the gap on telecom or
  oilgas.
- **Phase 2 moves to its own private repository** (team lead, Manual
  Validation round 2). This repository is then restored as filed and
  archived, under F127. That supersedes F123's in-repository layout.

## What was delivered

- **F123**: the phase-separation decision document,
  `docs/PHASE_SEPARATION.md`. Section 9 records the separate-repository
  decision that replaced its first recommendation.
- **IMP-3**: the test suite may not change committed evidence. The guard
  hashes the evidence files at session start and end, and now sits in the
  repository-root `conftest.py` so it runs however pytest is started.
- **F124**: the ranked lever list, `docs/phase2/SPECTRA_IMPROVEMENT_RESEARCH.md`,
  approved by the team lead. Every device run from it still needs Criterion H
  approval. NeuraWave does not fit this problem.
- **F17**: a Dirac-3 emulator with exact and emulate modes. It fails the
  card's own sparsity test: the device returns far more exact zeros than the
  emulator. The follow-up is F126.
- **F20**: soft votes help on 15 of 15 cells; multi-sample ensembling does
  not (+0.0014 AUPRC, 7 to 22 times below the seed SD).
- **F125**: the close-out hook counts commits against `origin/develop`.

## Defects in this sprint's own work

- **B4's device samples were never stored in full.** They were recovered by
  job id and the cause was fixed. B2's samples were truncated the same way,
  and QCi returned 404 for all 11 B2 jobs, so they are lost.
- **A commit message stated a test result that was false** (63bc375,
  corrected in c62248a).
- **A security review reported four findings and only three reached the main
  loop.** The fourth could not be recovered.
- **The pre-commit confidentiality scan missed renamed files and names with a
  space.** Found by the PR review and fixed before merge.
- **`injection.py` rewrote LF files with CRLF endings on Windows.** It now
  keeps bytes exactly.
- **Three cards carried claims nobody checked at refinement** (F17, F124,
  F125).

## Improvements

IMP-1 (refinement checks card claims against disk and the installed package),
IMP-2 (ask a dependent decision after its parent), IMP-3 (tracked pre-commit
hook), IMP-4 (no test outcomes in commit messages), IMP-5 (background reviews
write findings to a file) and IMP-7 (estimation reads the velocity log)
applied. IMP-6 (every Phase 2 device row carries its job id) is on F127.

## Effort

- Task A (F123): 30 min (estimate 120)
- Task B (IMP-3): 32 min (estimate 30)
- Task F (F125): 45 min (estimate 20)
- Tasks D+E (F17, F20), in parallel: 54 min including F17's acceptance test
  (estimate 570)
- Task C (F124): 95 min (estimate 240)
- **Total: 256 minutes against 980 estimated**
- Unplanned: Manual Validation 45, retrospective and improvements 70, second
  security review 55, PR review 85

## Next sprint readiness

`feature/20261007_Sprint_23` was cut from the Sprint 22 branch on merge
notification. F127 (Phase 2 to `kimmeyh/hsbc-quantum-fraud-2026p2`, this
repository restored as filed) is Priority 1. Its first step is the team
lead's: create the new private repository.
