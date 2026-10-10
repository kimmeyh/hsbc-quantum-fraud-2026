# Sprint 11 Summary

**Dates**: 2026-09-09 to 2026-09-10. **Branch**: `feature/20260910_Sprint_11`.
**PRs**: #66 (to develop), #70 (develop to main).

Sources: SPRINT_11_RETROSPECTIVE.md, SPRINT_11_VALIDATION.md, git history, PR #66.
Not the master plan.

## Scope, as delivered

Planned as seven tasks (F41, F42, F43, F37, F44, F45, F35). Two were added
mid-sprint by team-lead direction after QCi granted hardware time: **F46** (grant
verification and ceiling probe) and **F47** (metered-call wrapper, set as a hard
gate before any further Dirac-3 work).

Two were deferred to Sprint 12: **F37** (repository public) and the fresh-eyes
evidence review. Both Class 3 decisions, made explicitly.

Suite **201 -> 280**. One approved metered call, 10 seconds of 3,000.

## The three findings that changed what we claim

**F41: the published mechanism was wrong (A20).** The submission explained the
pool degeneracy by saying depth-limited trees mostly predict the negative class
at 0.17% prevalence. The saved pools disprove it: the frozen arm's trees are
UNBOUNDED, exactly ZERO learners predict all-negative, and 80 to 84 of the 91
reproduce the training labels exactly -- making them literally the same column
vector. Measured pairwise agreement 1.000000 among the perfect learners against
0.999964 among the rest. Right observation, wrong cause.

The correction is scoped: `tuned_pool.py` sets `max_depth` 2/3/4, so only the
frozen arm is unbounded. A blanket fix would have introduced a new false claim.

**F42: the +0.0319 gain came from class weighting, not classifier variety.**
Decomposed for the first time, against a per-seed comparator:

| Change | Effect | Clears MDE? |
|---|---|---|
| Four learner families instead of one | **-0.0047** | no |
| Fit-time class weighting | **+0.0328** | yes, 10/10 seeds |
| Shallower tree, distance-weighted kNN | +0.0038 | no |
| All three | **+0.0319** | reproduces the published figure |

Excluding the selection seed leaves +0.0313, so the selection bias is 0.0006.
The decomposition rebuilds every pool from the splits, so reproducing the
published number is itself evidence the original path was sound.

**F46: the 100-variable ceiling was a billing tier, not the device (A21).** One
approved call at 105 continuous variables was ACCEPTED. The ceiling that shaped
the entire hardware campaign was a free-tier restriction. No reported figure
changes; what changes is what is now possible.

## Corrections to published claims

- **F7**: QCi's hardware paper (arXiv:2407.04512) says "a hybrid
  photonic-electronic computer". It never says "entropy quantum computer", which
  we had attributed to it and then leaned on. Now quotes the vendor and claims no
  quantum resource.
- **F43**: HSBC names AUC-ROC 0.9459 on IEEE-CIS and we reported AUPRC only. The
  classical figures were already stored per fold -- LightGBM 0.9139, CatBoost
  0.8941, XGBoost 0.8640 -- and are now reported with the leaderboard mismatch
  stated rather than implied.
- **F13/F6/F16/F17**: a bracket bound quoted as a mean (0.5424 for 0.5739), the
  title contradicting section 2, a lowercase sentence start present since
  16618bb, and the Equality Act scoped to Great Britain.
- **The 85% ratio**, found in review: 0.0571/0.0734 = 77.8%, not 85%. Corrected
  in all three documents.

## Infrastructure

**F44, F45, F35** -- three test files, each verified by injecting the defect it
targets. **F47** -- job ids captured at submission, cost measured from the
allocation balance rather than a response field that vanished on the paid tier.

The billing rule was established and validated: `ceil(sum(device.samples.runtime))`,
preprocessing NOT billed. It reproduces the recorded 120s total and the per-job
distribution (15 jobs at 4.0s, 12 at 5.0s) across all 27 retained jobs, where
four other candidate rules fail. The team lead supplied the rule that works
after mine failed its own validation.

**Queue behaviour measured**: across all 27 historical jobs, queue wait median
0.7s against processing median 5.3s -- every one submitted 19:00-20:00 local.
The F46 probe went in at 14:33 and waited 5,452 seconds of wall clock for 10
seconds of device time.

## PR review

15 findings (Claude 13, Copilot 2, overlapping), all addressed before merge. The
reviewer named the pattern: **the sprint's new safety nets were not wired to
reality**. Three tests would have passed while providing no assurance --
`test_pool_mechanism` collected ZERO cases in CI because the pools are
gitignored, `metered_call.balance()` could fail inside a `finally` after a call
was billed, and `CallRecord` wrote a schema the tests did not read.

The repr scrape removed from `run_hardware.py` in this sprint turned out to
exist in three places; all are now gone.

## Numbers

| | |
|---|---|
| Suite | 201 -> 280 passed, 1 skipped, 2 xfailed |
| Amendments | A19 -> A21 |
| Cards closed | #59, #60, #61, #63, #64, #65, #67, #68 |
| Cards opened | #69 (F48) |
| Metered seconds | 10 of 3,000, one approved call |

The 2 xfails remain the F38 page-limit cases: appendix 5 of 3, proposal 7 of 6.

## What Sprint 12 inherits

F37, F38, F10, the fresh-eyes evidence review, F48, and any approved Dirac-3
work -- against a Sep 12 evidence freeze, which is T-2 at the time of writing.

Sequencing was decided in advance (Sprint 11 improvement 5) and is forced by
dependencies rather than preference: Dirac-3 work produces evidence, evidence
changes documents, F38 must cut against final content, and F37 is irreversible
so nothing that could still change a document may follow it. F10 depends on all
three. If the calendar forces a cut, the Dirac-3 work goes -- it is the only one
of the four that is not a submission blocker.
