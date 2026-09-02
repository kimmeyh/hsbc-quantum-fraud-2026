# Sprint 1 Retrospective

Conducted 2026-08-30 at sprint close, under the pre-adoption lightweight protocol (three questions, recorded in SPRINT_1_PLAN.md). The full 14-category x 4-role protocol (SPRINT_RETROSPECTIVE.md, adopted later the same day) applies from Sprint 2 onward. This document preserves the retrospective content that exists and explicitly marks the protocol transition; it does not fabricate role feedback that was never collected.

## Retrospective content (from sprint close)

- **What worked**: the review-adjudicate-freeze pipeline produced a bindable protocol in one day; the pre-commit hook caught a real staging risk on its first live test; background execution kept downloads and the pilot off the critical path; all acceptance criteria closed same-day with evidence.
- **What did not**: two metrics tests initially failed because synthetic test data was perfectly separable (degenerate CI edge cases); legacy Kaggle env vars silently shadowed the OAuth cache and cost two failed download cycles; develop lagged main by one commit when the sprint branch was cut, requiring a fast-forward fix.
- **Change next sprint**: branch cuts follow the carry-forward rule (supersedes the sync issue); synthetic test data gets realistic class overlap by design. Analysis note carried to Sprint 2: the pilot MDE (0.0242) derives from raw per-seed AP variance; paired deltas should show smaller SD; refine by dated amendment when measured.

## Improvement decisions

| # | Title | Source | Type | Effort | Decision |
|---|---|---|---|---|---|
| 1 | Carry-forward branch rule adopted | What-did-not | Process | done | Applied now (SPRINT_PROCESS.md, workflow 6.6) |
| 2 | Overlapping synthetic test data convention | What-did-not | Tests | done | Applied now (test_metrics.py) |
| 3 | Paired-delta SD measurement -> MDE refinement | Analysis note | Protocol (amendment path) | ~30m | Sprint 2 plan (F1) |

## Protocol transition note

Team-lead PO/SM/LD role feedback was not collected per-category for Sprint 1; the sprint predates the adopted protocol. Recorded as a known process gap, accepted by adoption timing, not to be repeated: Sprint 2's retrospective runs the full 7-step, 14x4 protocol.
