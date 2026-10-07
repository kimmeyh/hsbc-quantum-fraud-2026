# Sprint 22 Retrospective

**Sprint**: 22, Separate the Phases, Then Look for Better Numbers
**Date**: 2026-10-07
**Scope delivered**: F123, IMP-3, F124, F17, F20, F125 -- all six
**Effort**: 256 minutes recorded against 980 estimated, plus 45 minutes of
Manual Validation work (`.claude/sprint_status.json`, `task_actuals`)
**Metered Dirac-3 seconds**: **0**. Balance 1,022 s throughout.

## Scoring, both roles

The team lead scored every category **Very Good**. Claude scored four
lower. Where the two disagree both are recorded, and the improvements are
built from the lower score.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Good |
| Testing approach | Very Good | Good |
| Effort accuracy | Very Good | **Needs Improvement** |
| Planning quality | Very Good | **Needs Improvement** |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | Good |
| Requirements clarity | Very Good | Good |
| Documentation | Very Good | Good |
| Process issues | Very Good | **Needs Improvement** |
| Risk management | Very Good | Good |
| Next sprint readiness | Very Good | Good |
| Architecture maintenance | Very Good | Good |
| Assigned coding agents quality | Very Good | Good |

Team lead: "Manual Validation complete"; minor function updates "none";
backlog additions "none"; questions before ending the sprint "none".

## Sprint 22 Retrospective Feedback

The team lead gave combined Product Owner, Scrum Master and Lead Developer
feedback, recorded verbatim under each of the three roles.

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. All six tasks done with zero
  metered seconds; F124's list was approved as written. Rework: the
  phase-separation recommendation (`PHASE_SEPARATION.md` section 4.1) was
  superseded across three validation rounds by a separate repository. The
  analysis behind 4.1 never checked what the filed documents point at.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every new guard was proven red.
  `test_requirements_complete.py` caught an undeclared import during
  validation. The sample-storage defect was found by testing, not by a
  reviewer. Against it: commit 63bc375 said the hook tests passed when one
  had failed (corrected in c62248a).

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. 256 minutes against
  980 estimated, 3.8 times over in total. One task ran the other way: F125
  took 45 minutes against 20. `docs/VELOCITY_LOG.md`, which exists to calibrate estimates, stops at
  Sprint 14.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. Three cards carried
  claims nobody checked at refinement: F17's acceptance test named B2 pools
  that were never stored; F124 named `batched_qboost_enabled`, which the
  installed eqc_models 0.21.0 does not have; F125's diagnosis was
  incomplete (a correct count alone still blocked).

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Main-loop work on the main
  model, the security review as a background agent, and the advisor before
  each approach.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every validation item was listed
  on screen. But D2, D4 and D5 were asked beside D3 although their options
  depended on D3's answer, so D2 was answered on a premise that changed one
  round later.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The full F123 requirement (the
  filed, public link shows what was filed; Phase 2 completely separate)
  surfaced only at Manual Validation.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every result has its document and
  evidence file. CHANGELOG entries were written at the end, not in each
  commit: the policy F70 restored failed again.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. The CHANGELOG lapse;
  a test outcome stated wrongly in a commit message; the security review's
  fourth finding title never reached the main loop. The heredoc and
  metacharacter hooks blocked three commands and were right each time.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Zero spend held. One risk
  materialized: B2's full samples are lost (QCi returns 404), because B2's
  rows never stored a job id and only the truncated print kept one.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. F127 is first and starts with two
  team lead actions. The local pre-commit confidentiality hook is not
  tracked by git, so a new repository would not get it without a hand copy.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Phase 2 code imported Phase 1
  code read-only throughout; the storage defect is fixed at its cause; the
  phase boundary is now settled by repository, not by convention.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond the improvements below.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none new; F126 and F127 were carded
  during Manual Validation.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The security review found real
  issues, but its fourth title did not reach the main loop, so one finding
  is unaddressed. The advisor predicted near-uniform weights for boosted
  pools; the data showed otherwise and was reported as measured.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

## Improvements proposed (awaiting the team lead's decision)

| # | Title | Source | Type | Effort | Recommendation |
|---|---|---|---|---|---|
| IMP-1 | Check every card claim against what exists before scheduling | Cat 4 | Prevention, extends the capability pre-flight (Sprint 21 IMP-1) | 15m | now |
| IMP-2 | Ask a dependent decision after the one it depends on | Cat 6 | Prevention, extends the CLAUDE.md one-decision-per-question rule | 10m | now |
| IMP-3 | Track the pre-commit hook and add a CHANGELOG check to it | Cat 8, 9, 11 | Prevention, extends the confidentiality pre-commit hook | 45m | now |
| IMP-4 | Commit messages state no test outcome | Cat 2, 9 | Prevention, extends the CLAUDE.md restated-number rule | 5m | now |
| IMP-5 | Background reviews write findings to a file read in full | Cat 9, 15 | Prevention, extends the review step in `SPRINT_EXECUTION_WORKFLOW.md` | 30m | now |
| IMP-6 | Every device row carries its job id | Cat 10 | Detection, extends `test_row_schema.py` | 20m | backlog, on F127 |
| IMP-7 | Restart the velocity log and calibrate estimates from it | Cat 3 | Prevention, extends `VELOCITY_LOG.md` and the planning estimate step | 30m | now |

## Improvement Decisions

Pending.
