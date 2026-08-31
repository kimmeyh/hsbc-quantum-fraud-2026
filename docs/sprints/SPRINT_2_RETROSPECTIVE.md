# Sprint 2 Retrospective

**Purpose**: Sprint 2 (Process Foundations and External Readiness) review per docs/SPRINT_RETROSPECTIVE.md.
**Audience**: Team lead; future sessions.
**Last Updated**: 2026-08-30

Team-lead feedback recorded VERBATIM (combined Product Owner / Scrum Master / Lead Developer per category, as provided). Claude Code Development Team lines added per protocol. Note: the team lead's category list adds "Assigned Coding Agents Quality" and "Questions to be discussed before ending the sprint"; proposal 7 adopts both into the template permanently.

Team-lead preamble, verbatim: "this retrospective has proven highly effective at improving effectiveness and efficiency over time. It is not about who did what wrong, rather it is about how can we all be more successful in the future. It is a way to 'run the race better in order to get the prize.'"

## Sprint 2 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner / Scrum Master / Lead Developer (verbatim)**: "Good. Noticed several situations where PowerShell commands or scripts were attempted and errored out. Did you review the PowerShell best practices, hooks and troubleshooting from the spamfilter repo. If not, can you review and see if any would be applicable to this repo and then move over (adjusting appropriately for the differences in this repo versus the prior repo). Can you clarify for backlog refinement - all items in the list should be referenced by the backlog item name/number (currently F#) - no other #'s are needed."
- **Claude Code Development Team**: Confirmed on both counts. The F15 review covered ARCHITECTURE.md, adr/, QUALITY_STANDARDS, TESTING_STRATEGY, and LOGGING_CONVENTIONS but did NOT cover WINDOWS_DEVELOPMENT_GUIDE.md, TROUBLESHOOTING.md's PowerShell sections, or .claude/hooks/ -- that is the gap behind the observed errors (empty-directory listings exiting 1, Select-String no-match exit codes treated as failures, a JSON file edited by regex replace). Proposal 1 ports them. The backlog-presentation rule is understood: F# identifiers only in refinement presentations; GitHub issue numbers live on cards and PR bodies, never in the candidate slate. Proposal 2 encodes it.

### 2. Testing Approach

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Known-answer testing carried the sprint (manifest line counts doubled as an integrity test of all 12 staged files). No test escapes in Sprint 2.

### 3. Effort Accuracy

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: F15 estimated ~3h; actual was ~45 minutes of wall time (research agent ~6 min, authoring the rest) -- a 4x over-estimate consistent with the source repo's pre-velocity-log era. The velocity actuals log (proposal 6) starts the calibration loop in the F1 sprint.

### 4. Planning Quality

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The sprint's one real process failure belongs here: the initial Sprint 2 plan carried the F1 campaign forward on inference against the team lead's defined scope, costing a re-plan cycle and six prematurely created cards. The defined-scope rule is now binding in SPRINT_PLANNING.md and memory; the recovery (close cards, re-plan, re-present) was clean.

### 5. Model Assignments

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Top-tier research agent for F15 and top-tier authoring/adjudication in the main loop matched the planning doc's mandatory-tier table.

### 6. Assigned Coding Agents Quality

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The F15 agent produced a complete 42-ADR inventory, faithful template reproduction, and correctly grounded every ML candidate against the frozen preregistration in a single pass with zero rework. The output file was exactly to spec.

### 7. Communication

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: One self-flagged miss: the F15 summary compressed ~30 transferable items into what read as 4, and the team lead had to challenge to surface the full accounting. Proposal 5 sets the rule: full counts first, triage second.

### 8. Requirements Clarity

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The portal walkthrough converted an unknown (submission mechanics) into hard requirements (5-slot upload, team-profile-as-PDF, format list) days before they could bite.

### 9. Documentation

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Heavy documentation sprint by design; the same-commit CHANGELOG policy is now in force and this retrospective is the first document written under the full QUALITY_STANDARDS header convention.

### 10. Process Issues

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Three small frictions for the record: PowerShell command errors (see category 1; proposal 1), sprint_status.json edited via regex string replacement instead of parsed JSON (fragile; proposal 4), and MANIFEST.json nearly swallowed by the data-directory gitignore (caught same-turn, exception added).

### 11. Risk Management

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Zero metered seconds spent, as planned; the do-not-upload-until-final portal risk is documented in the requirements matrix.

### 12. Next Sprint Readiness

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: F1 is fully specified (plan content, inline ADR additions, budget arithmetic) and blocked on nothing but selection and approval.

### 13. Architecture Maintenance

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The ADR system is live with five accepted records and six reserved; the Preregistration-touchpoints section makes protocol non-contradiction self-enforcing.

### 14. Minor Function Updates for the Next Sprint Plan

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: None beyond the already-recorded F1 inline additions.

### 15. Function Updates for the Future Backlog

- **PO/SM/LD (verbatim)**: "Can you investigate all the relevent information on quantumcomputinginc.com products, instructions, documentation, papers and articles to determine - is it reasonably possible to create a Dirac-3 simulator such that we could call the simulator QBoostClassifier for all the test runs prior to running on Dirac-3 using appropriately miniturized subsets of data (so that all test runs end in 10 mintues or less (or some other number we choose). It could use classical optimization python packages. Prioritize for after submission unless you think there is high value in doing this earlier."
- **Claude Code Development Team**: Registered as F17 (proposal 3). Preliminary feasibility read: YES, reasonably possible -- QCi's own paper trains CVQBoost with Scipy SLSQP and Hexaly as drop-in solvers, and eqc-models exposes the QUBO (J, C) cleanly, so a simulator = same objective + classical optimizer + device-behavior modeling (sum constraint, ~23 dB dynamic-range clipping, solution stochasticity via num_samples draws). Timing recommendation: AFTER submission. The frozen protocol already fields the proxy-as-structural-control (ADR-0002) plus the G0b fidelity gate for exactly the pre-hardware-confidence role, and swapping tuning machinery now would require amendments for modest marginal value; in Phase 2, a behavior-faithful simulator would save real metered budget and is worth doing properly.

### 16. Questions to be discussed before ending the sprint

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: None.

## Improvement Decisions

| # | Title | Source | Type | Effort | Recommendation | Decision |
|---|---|---|---|---|---|---|
| 1 | Port PowerShell best practices, troubleshooting, and applicable hooks from spamfilter (WINDOWS_DEVELOPMENT_GUIDE, TROUBLESHOOTING PowerShell sections, .claude/hooks), adapted | PO/SM cat 1 | Process/docs | ~45m | Apply now | pending |
| 2 | Backlog presentation rule: F# identifiers only in refinement presentations; issue #s never appear in candidate slates | PO cat 1 | Docs | 5m | Apply now | pending |
| 3 | F17: Dirac-3 simulator feasibility investigation and build (classical-optimizer backend, miniaturized data, <=10-min runs) | PO cat 15 | Backlog | ~2-3h investigate | Backlog, post-submission (rationale in cat 15) | pending |
| 4 | sprint_status.json updated via parsed JSON (ConvertFrom-Json round-trip or Python helper), never regex replace | Dev Team cat 10 | Tooling | 15m | Apply now | pending |
| 5 | Full-accounting-first rule for research summaries: totals and category counts first, triage second | Dev Team cat 7 | Process note | 10m | Apply now | pending |
| 6 | Velocity actuals log (CODING_VELOCITY-lite): record per-task actual minutes from F1 sprint onward; recompute at retros | Dev Team cat 3 | Process | 15m setup | F1 sprint | pending |
| 7 | Retrospective template extended with the team lead's two categories: "Assigned Coding Agents Quality" and "Questions to be discussed before ending the sprint" (14 -> 16 categories) | This retro | Docs | 10m | Apply now | pending |
