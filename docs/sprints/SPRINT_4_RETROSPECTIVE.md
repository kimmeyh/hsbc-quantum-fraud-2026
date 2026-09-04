# Sprint 4 Retrospective

**Purpose**: Sprint 4 (Proxy Tuning, Baseline Research, First Hardware Blocks, Results Memo) review per docs/SPRINT_RETROSPECTIVE.md.
**Audience**: Team lead; future sessions.
**Last Updated**: 2026-09-03

Team-lead feedback recorded VERBATIM (combined Product Owner / Scrum Master / Lead Developer per category, provided 2026-09-03 with "Manual Validation complete"). Sections follow the guide's canonical numbering; the team lead's list places Assigned Coding Agents Quality after Communication, recorded here at its canonical position 15.

## Sprint 4 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The sprint delivered its first metered hardware evidence (27 fits, 120 QPU s, 0 failures, 0 retries) plus two gates scored, on schedule. Efficiency came from reusing Sprint 3 machinery: the A3 full-pair WSL build made pool construction seconds rather than minutes, H-matrix caching made lambda-only tuning trials near-free, and the checkpoint pattern meant no work was ever repeated. One avoidable cost: the hardware H1b reporting block was inserted into score_gates.py three times before it produced output (a scoping error, then a guard that selected single-seed G0b cells). A ten-line standalone test of the computation first would have caught both in one pass.

### 2. Testing Approach

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The A6 health check earned its place immediately: it fired on 10/10 seeds of the selected hardware config, which is exactly the condition Sprint 3's validation caught by eye. The one-call-first discipline on metered hardware was the right call and paid for itself by revealing that eqc-models returns a SolutionResults object rather than a dict, so the metered-seconds field needed a different extraction path. Gap: score_gates.py has no test at all. It is now the single most consequential piece of unTESTED code we own, because every reported number passes through it (see proposal 1).

### 3. Effort Accuracy

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Authored work continues to run 0.5-0.75 of estimate (velocity log now 17 rows). The 100-trial tuning study finished in ~85 minutes against a 120-240 minute estimate. The hardware block ran ~150 minutes against a 240 minute estimate, with the billed portion only 120 seconds -- the wall-clock cost of metered work is pool building and queueing, not the QPU, which is worth carrying into every future hardware estimate.

### 4. Planning Quality

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Task ordering was correct and load-bearing: F22 had to precede F2 because G0b consumes the config ranking, and the plan said so. The capability pre-flights (WSL tuning smoke, one-call-first) both caught real issues. Planning miss worth naming: the F22 search space bounded decision-tree depth at 1-3 while the frozen starting config used unlimited depth, so the tuning could not rediscover its own baseline; it was carried in by hand at ranking time. Search spaces should be checked for containing the incumbent before they run.

### 5. Model Assignments

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Top tier in the main loop for all protocol-touching work (amendments, hardware, gate scoring). The single delegated research agent (F21) returned a decisive primary-source finding in about nine minutes of agent time, against a two-hour estimate -- the strongest return on delegation this project has seen.

### 6. Communication

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The metered-hardware stop was stated correctly: block, call count, expected seconds, and config hashes named before every launch. The plain-language explanations were requested rather than offered, which is the signal (see proposal 4). One good pattern to keep: when the CPU-utilization question came up, the answer was measured process CPU-time deltas, not a guess.

### 7. Requirements Clarity

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The team lead's production-framing direction late in the sprint materially improved the deliverable and could have been surfaced earlier: the question "who reads this and what do they need to believe" belongs at F7's start, not after the memo is drafted. Proposal 3 moves it.

### 8. Documentation

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The amendment log now runs A1-A7 with dates, approvals and rationale, and is the single best artifact this project has for demonstrating protocol integrity to a reviewer. The results memo went through a full correction cycle and is materially stronger for it.

### 9. Process Issues

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Three for the record. (1) The pre-commit confidentiality hook blocked a legitimate commit because the pattern list matched the env-var NAME `QCI_TOKEN` appearing in source; fixed by making the patterns value-shaped, and worth noting that the hook worked as designed and the pattern was wrong. (2) The results memo was overwritten mid-correction by a stale in-flight write, costing a full rewrite; the fix is to re-read immediately before writing a file another process may have touched. (3) The statistical checklist walk was performed BEFORE the hardware campaign and then referenced as if current, so it asserted "no hardware run" and "no temporal cells" against 27 hardware rows -- caught only by the external review (proposal 2).

### 10. Risk Management

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The metered spend came in at 120 s against a 100-145 s estimate with block caps armed at 2x and never approached. Criterion H was honored: the sprint stopped and waited for approval even though the plan authorized the task. The one-call-first pattern is now the standing shape for any metered work.

### 11. Next Sprint Readiness

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Sprint 5 (F8 + F9, then F19) opens with an unusually complete input set: a corrected memo with a decided framing, the gate table scored, A7 approved, and F25-F28 registered. The one carried dependency is prediction persistence, which A7 requires and which unblocks the H1b paired BCa.

### 12. Architecture Maintenance

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Freeze discipline held under real pressure. The temptation to relabel G0 after F21 showed its threshold was miscalibrated was declined; the gate stays failed as committed and the research became an amendment instead. results.json schema adherence is total across 137 rows including the new hardware arm.

### 13. Minor Function Updates for the Next Sprint Plan

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: [DEV] Known-answer tests for score_gates.py aggregation (proposal 1) -- target: Sprint 5 plan, est: 45m.

### 14. Function Updates for the Future Backlog

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: None beyond the items already registered mid-sprint (F25, F26, F27, F28).

### 15. Assigned Coding Agents Quality

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: One agent (F21 research). It found the probable origin of the uncorroborated literature band, quantified the three protocol differences, identified a genuine gap in the published literature, and proposed a correctly-scoped amendment that respected the freeze -- in a single pass, under spec, with sources cited. It also flagged an unrelated labeling problem in an older document without editing it, per instruction.

### 16. Questions to be discussed before ending the sprint

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: None. The repository-visibility question was raised and answered during the sprint: this repo stays private permanently, a separate curated reproducibility repo publishes during the Sep 12-13 finalize window with the .env exclusion made explicit in the confidentiality scan.

## Improvement Decisions

Team-lead decision 2026-09-03: "all as recommended" (blanket approval).

| # | Title | Source | Type | Effort | Recommendation | Decision |
|---|---|---|---|---|---|---|
| 1 | Known-answer tests for score_gates.py: every reported number passes through untested aggregation code (gate verdicts, paired deltas, Spearman, cell keying) | Dev Team cat 2 | Code | 45m | Sprint 5 plan | RECORDED: F8 inline addition (master plan) |
| 2 | Evidence-generating steps invalidate their own verification: any checklist walk, memo, or report is regenerated AFTER the last evidence lands, never before (workflow Phase 5) | Dev Team cat 9 | Process | 10m | Apply now | APPLIED: SPRINT_EXECUTION_WORKFLOW Phase 5 |
| 3 | Audience-first rule for deliverables: before drafting any external-facing document, state who reads it and what they must believe; put it at the top of the task, not after the draft | Dev Team cat 7 | Process (planning + workflow) | 15m | Apply now | APPLIED: SPRINT_PLANNING audience-first rule |
| 4 | Plain-language companion becomes a deliverable, not a response: every validation package and every external document ships with its plain-terms version written at the same time | Dev Team cat 6 | Process | 10m | Apply now | APPLIED: SPRINT_EXECUTION_WORKFLOW Phase 5 (strengthened to deliverable) |
| 5 | Search-space containment check: a tuning search space must contain the incumbent config, verified before the study runs | Dev Team cat 4 | Docs (STATISTICAL_REVIEW_CHECKLIST + planning) | 10m | Apply now | APPLIED: STATISTICAL_REVIEW_CHECKLIST |
| 6 | External-review pass on every major evidence document before it reaches the team lead, using the fresh-context mechanism already adopted in Sprint 3 improvement 6 (this sprint's memo review found 3 real errors and 4 overclaims) | Dev Team cat 9 | Process | 10m | Apply now | APPLIED: SPRINT_EXECUTION_WORKFLOW Phase 5 |
| 7 | Re-read before write when another process may have touched a file; treat a stale-write overwrite as a defect class, not an accident | Dev Team cat 9 | Docs (QUALITY_STANDARDS) | 10m | Apply now | APPLIED: QUALITY_STANDARDS |
