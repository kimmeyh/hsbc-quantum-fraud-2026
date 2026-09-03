# Sprint 3 Retrospective

**Purpose**: Sprint 3 (Classical Evidence Campaign) review per docs/SPRINT_RETROSPECTIVE.md.
**Audience**: Team lead; future sessions.
**Last Updated**: 2026-09-02

Team-lead feedback recorded VERBATIM (combined Product Owner / Scrum Master / Lead Developer per category, as provided 2026-09-02 with "Manual Validation complete"). Sections follow the guide's canonical numbering (the team lead's list places Assigned Coding Agents Quality after Communication; it is recorded at its canonical position 15).

## Sprint 3 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Three compute tracks ran in parallel (Optuna campaign, sequential proxy, WSL full-pair builds) with zero idle waits and every long stage checkpointed. Two avoidable detours for the record: PowerShell-to-WSL inline quoting failed twice before switching to script files, and the tune.py "LightGBM bug fix" was itself wrong (the pinned 4.7 API was correct as frozen) -- caught by the smoke run's deprecation warning and reverted same-session with A4 recording the truth.

### 2. Testing Approach

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Known-answer suite grew 11 to 15 (FISTA vs SLSQP, pool count vs the A2 formula, guards); the smoke pre-flight caught real defects cheaply (CatBoost positive-class starvation at 5k rows). The honest gap: the score degeneracy escaped every automated check -- tie_fraction was RECORDED in every row but nothing thresholded it. How it WAS caught (team lead, noted 2026-09-02): dropping results.json into the Claude Windows app with the prompt "Can you describe? any useful observations?" -- a fresh-context review of the raw evidence file, carrying none of the campaign session's assumptions. Two lessons, two proposals: automate the check that should have existed (proposal 1), and institutionalize the fresh-eyes evidence review that actually worked (proposal 6).

### 3. Effort Accuracy

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: First sprint with the velocity log live. Authored-work estimates ran high (actual/estimate 0.45-0.7 across ADRs, hooks, modules); unattended compute ran roughly to plan except CatBoost/full (56 min, the long pole). The log now has 12 calibration rows.

### 4. Planning Quality

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The capability pre-flight rule earned its place (WSL spike re-scoped nothing but proved the path; Optuna smoke caught two defects before hours of compute). Planning miss worth naming: the frozen lambda=2*n_train starting config was ported from SPECTRA-balance data to 0.17%-positive ULB without an imbalance sanity check -- the degeneracy was foreseeable from config provenance. Proposal 2 addresses the class.

### 5. Model Assignments

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Top tier in the main loop throughout; the planned Sonnet-subagent option for harness code went unused because the skeleton existed and the marginal handoff cost exceeded the work. Right call at this scale.

### 6. Communication

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Mid-run status was measurement-based (the CPU-5% question was answered with process CPU-time deltas, not guesses); G0 FAIL was reported plainly with context and without spin.

### 7. Requirements Clarity

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: The validation exchange surfaced that my technical summaries assumed shared context (the A3 explanation needed an 8th-grade retelling; the G0 question showed the full-vs-matched distinction had not landed). Proposal 4: plain-language companions in validation packages.

### 8. Documentation

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: ADR set completed (0001-0011), ARCHITECTURE/TESTING_STRATEGY/VELOCITY_LOG live, the amendment log carried A4/A5 with exact dates and approvals, and the hardware request doc is a reusable template for every future block.

### 9. Process Issues

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Three frictions: (1) PowerShell-to-WSL inline quoting mangles arguments -- script files are the reliable channel (proposal 3); (2) one background commit swept in volatile run artifacts before the gitignore fence landed (proposal 5); (3) the refit stage crashed on a checkpoint-key assumption when proxy rows shared the store -- one-line fix, checkpointing contained the cost to a relaunch.

### 10. Risk Management

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Zero metered seconds spent while the campaign generated 110 evidence rows; the score degeneracy was caught at validation BEFORE any hardware spend, which is the layered-gates design working; Criterion H never came under pressure.

### 11. Next Sprint Readiness

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: F22 (proxy tuning; unblocks G0b and the lg quarantine) and F21 (baseline-protocol research re G0) are registered and scoped; F19 (QCi draft PDFs) is queued at priority 13; A5 is applied; the hardware request waits ready.

### 12. Architecture Maintenance

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: Freeze discipline held under pressure twice: the tune.py non-bug was reverted rather than papered over, and the degeneracy fix routes through the preregistered tuning rather than an ad-hoc patch. results.json schema adherence is total (110/110 rows).

### 13. Minor Function Updates for the Next Sprint Plan

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: [DEV] Score-distribution health check (proposal 1) -- target: Sprint 4 plan, est: 20m.

### 14. Function Updates for the Future Backlog

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: None beyond items already registered mid-sprint (F19, F20, F21, F22).

### 15. Assigned Coding Agents Quality

- **PO/SM/LD (verbatim)**: "Very Good"
- **Claude Code Development Team**: No delegated coding agents this sprint -- the parallel work was background scripts, not subagents. Recorded as N/A rather than claimed credit.

### 16. Questions to be discussed before ending the sprint

- **PO/SM/LD (verbatim)**: "none"
- **Claude Code Development Team**: None.

## Improvement Decisions

Team-lead decision 2026-09-02: "all improvements as recommended" (blanket approval).

| # | Title | Source | Type | Effort | Recommendation | Decision |
|---|---|---|---|---|---|---|
| 1 | Score-distribution health check: threshold tie_fraction/mode-share in summarize output; WARN flag in rows and gate report | Dev Team cat 2 | Code (amendment-registered) | 20m | Sprint 4 plan | RECORDED: F22 inline addition (master plan) |
| 2 | Config-provenance rule: porting a config across datasets requires recording source-data characteristics and an imbalance sanity check | Dev Team cat 4 | Docs | 15m | Apply now | APPLIED: STATISTICAL_REVIEW_CHECKLIST + SPRINT_PLANNING |
| 3 | WSL interop practices: script files not inline quoting; per-distro venv; path shim pattern | Dev Team cat 9 | Docs | 15m | Apply now | APPLIED: WINDOWS_POWERSHELL_GUIDE |
| 4 | Plain-language companion in every Phase 5 validation package | Dev Team cat 7 | Process note | 10m | Apply now | APPLIED: SPRINT_EXECUTION_WORKFLOW Phase 5 |
| 5 | Background-launch fencing rule: outputs gitignored or deliberately tracked before launch | Dev Team cat 9 | Docs | 10m | Apply now | APPLIED: QUALITY_STANDARDS |
| 6 | Fresh-eyes evidence review at Phase 5 (fresh-context reviewer of raw evidence files; credits the team lead's Claude-Windows-app catch) | PO cat 2 note | Process | 15m + ~5m/sprint | Apply now | APPLIED: SPRINT_EXECUTION_WORKFLOW Phase 5 |
