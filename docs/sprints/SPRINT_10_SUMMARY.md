# Sprint 10 Summary

**Dates**: 2026-09-09. **Branch**: `feature/20260909_Sprint_10`. **PR**: #58 (merged to develop), #62 (develop to main).

Sources: SPRINT_10_RETROSPECTIVE.md, git history, PR #58. Not the master plan.

## Scope, as delivered

Planned as F40 -> F37 -> F38. **Re-scoped after plan approval** by team-lead
direction: F37 and F38 moved to Sprint 11, leaving **F40 alone**. Both remain
open submission blockers (#56, #57).

What actually consumed the sprint was not in any plan: two adversarial reviews
found correctness defects in evidence already shipped to QCi, and the second
review found a latent crash in the fix for the first.

## F40: segmentation (card #55, closed)

Seven team-lead `0*` files and `experiments/reference/fourierwall2/` (42 files,
2.0 MB) moved to a sibling folder outside the repository, `git rm --cached`,
gitignored. History deliberately NOT rewritten (team-lead decision, recorded).

All 49 moved files verified content-identical against their git blobs before
the repo copies were deleted: 17 byte-for-byte, 32 differing only in CRLF vs LF.
The check mattered because the destination now holds the only copies outside
git history.

The premise falsifier ("any test or script fails after the move") did not fire.

## The defect the plan did not anticipate

Removing absolute paths turned up a real reproducibility hole: `data.py`
hardcoded the ULB dataset location, so the repository Appendix C promises
"regenerates every figure" would have worked on no machine but the author's.
Now repo-relative with an `HSBC_ULB_CSV` override; `manifest.py verify` returns
VERIFY OK against the frozen checksums. A WSL shim in `qubo_proxy.py` became
dead code and was removed.

Twelve tracked files carried absolute paths. All are gone.

## The gate-report undercount

`score_gates.py` filtered hardware rows with `arm == "cvqboost_hw"`, silently
dropping the 10 `cvqboost_hw_mixed` fits. The generated report certified **27
fits / 120.0 s** while `results.json` held **37 / 163.0 s**.

This is the file CLAUDE.md designates as the verification path for every
reported number, so the undercount certified the wrong figure. It is also how
the submission came to contradict itself: the appendix quoted the true total and
the proposal and team profile quoted the report's.

Four regression tests now compare artifact to store, verified to fail on the
original bug.

## Correctness findings from two adversarial reviews

GPT-6 Astra and Fable 5.1. Every claim reproduced before acceptance.

Fixed this sprint, all edit-only: B.1 listed H3 and H6 as NOT RUN while A.5/A.6
reported them measured; the amendment count read ten in two files against
nineteen in a third; the G0b sentence claimed 27 fits for a gate that ranks five
configurations (G0b is 5 fits / 21.0 s); B.2 left two superseded figures both
looking current; two claimed artifacts were absent from the submission; and A.6
cited a GAM twin "at 0.26" that appears in **no artifact** -- a stale value from
the defective first H6 run, corrected to the measured 0.7893 / 0.7351.

Carded, not fixed: **F41** (#59) the pool-degeneracy mechanism, **F42** (#60)
items needing external source checks or reruns, **F43** (#61) IEEE-CIS AUC-ROC.

## PR review

Copilot: 2 findings, both real (a card-number collision where F43 named two
different items, and a duplicated phrase). Claude: 11 findings, all real,
including a **latent crash in my own gate-report fix** -- widening the metered
filter left the sibling `by_cell` branch narrow, so the first failed mixed fit
would have taken down the report generator. Reproduced, fixed, re-verified.

Six of the eleven were bypasses in the two hooks written this same sprint.

All 12 threads answered and resolved. No overlap between the reviews, so the
Copilot-preference rule did not apply.

## Retrospective and improvements

16 categories x 4 roles. Team lead: Very Good on all 13 rated categories.
All six improvements approved as recommended and applied:

1. `block-unraw-escape.ps1` hook for the recurring Python escape failure
2. F44 carded (evidence-vs-document consistency tests)
3. A20 registration targeted at Sprint 11
4. Risk-template addition targeted at Sprint 11
5. Workflow invariant 5: a repeated instruction means my reading is wrong
6. Capability pre-flight now inventories code, not only documents

Plus **F45** (#63), carded after the sprint from a process note: a diagnostic
script restored `results.json` correctly but had already regenerated
`gate_report.md` from the polluted store, briefly committing a 158-row artifact.

## Numbers

| | |
|---|---|
| Suite | 197 -> 201 passed, 1 skipped, 2 xfailed |
| Hooks | 2 -> 3 PreToolUse |
| Cards closed | #55 |
| Cards opened | #59, #60, #61, #63 (+F44, F45 in the master plan) |
| Metered Dirac-3 seconds | 0 |

The 2 xfails remain the F38 page-limit cases: appendix 5 of 3, proposal 7 of 6.
Page size runs after all correctness work, by team-lead sequencing.

## What Sprint 11 inherits

F37, F38, F41, F42, F43, F10, plus F44 and F45. Three are submission blockers
and two are Class 1/Class 2 requiring explicit approval before documents are
touched. The Sep 12 evidence freeze is the binding constraint.
