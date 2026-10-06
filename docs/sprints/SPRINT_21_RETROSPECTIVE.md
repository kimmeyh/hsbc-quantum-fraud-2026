# Sprint 21 Retrospective

**Sprint**: 21, The SPECTRA Block, and a Bar That Can Read It
**Date**: 2026-10-06
**Scope delivered**: F90, F100, F101, F122 -- all four
**Effort**: 454 minutes against 750 estimated
**Metered Dirac-3 seconds**: **653** (B5 13 + B4 640), reconciled against the
device balance, 1,675 s to 1,022 s

## Scoring, both roles

The team lead scored all sixteen categories **Very Good**. Claude scored six
lower. Where the two disagree both are recorded, and the improvements are
built from the lower score.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Good |
| Testing approach | Very Good | **Needs Improvement** |
| Effort accuracy | Very Good | Good |
| Planning quality | Very Good | **Needs Improvement** |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | **Needs Improvement** |
| Requirements clarity | Very Good | Good |
| Documentation | Very Good | Good |
| Process issues | Very Good | **Needs Improvement** |
| Risk management | Very Good | **Needs Improvement** |
| Next sprint readiness | Very Good | Very Good |
| Architecture maintenance | Very Good | **Needs Improvement** |
| Assigned coding agents quality | Very Good | Very Good |

Team lead: Manual Validation complete; no minor function updates, no backlog
additions, no questions before closing.

## Sprint 21 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The outcome is right: both blocks
  ran, 22 fits, 0 failures, 653 s reconciled exactly against the device
  balance, and an honest H5 answer. It was not reached at least effort. The
  runners were rebuilt the night before the run because I had hand-built the
  request to QCi, and the team lead had to stop me mid-rebuild to ask why I was
  re-solving something already solved. Task A cost him a round trip for data
  the repository already held.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. The tests found real
  defects: the energy_steel control infeasibility before a second was spent,
  Option 3's missing cost, a scoring bug the full dry run reached, a test
  silently rewriting the gate report. But two of my own tests SUBMITTED REAL
  DIRAC-3 JOBS once the window opened -- a `pytest.skip` placed after
  `subprocess.run` -- and nothing was billed only by luck. Several first
  attempts at guards were themselves vacuous or over-broad.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. 454 minutes against 750. The
  variance is concentrated in Task D: estimated 360, took 133, because F100 was
  sized at ~6 hours `[no-history]` and measured 3.77 seconds per cell. The
  pilot that measured it is the rule working; the estimate was never checked
  against a single fit.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. Task A was declared
  blocked on the team lead for a configuration brought into the repository on
  2026-10-03 -- I turned a citation restriction into a missing input. B5 was
  reported as having "no definition in this repository" when the frozen
  preregistration defines it in section 10; I had not opened it. The capability
  pre-flight did find the cost conflict, the 816-variable correction and the
  infeasible control, all before spending.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. All work ran in the main loop on
  the top tier; no subagent was assigned and none was needed. No issues --
  expectations met.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. I called the runners
  "built, guarded and proven" when only the guards were proven. I typed
  status-footer timestamps by hand four times against an explicit CLAUDE.md
  rule, and had to correct them. I handed over a 260-character PowerShell line
  the terminal could not copy intact. Several explanations ran long where a
  conclusion would do.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The team lead's rulings were clear
  and each is recorded: no Phase 1 amendments, the 07:30 window, A deferred to
  F123, no QCi notice. Where I assumed, I said so (EST read as local Eastern).
  My own framing confused things once: I offered a "Class 1 amendment" that
  section 11 does not permit at all.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every result has a document and every
  correction is dated beside the text it corrects. Against that: CHANGELOG
  lapsed for two days until the pre-handover reconciliation; commit 6b902c3
  carried Task D's files under a message about something else; and the B4
  result's "Proxy's edge" column compared against a control built the old way,
  corrected only when the team lead's question exposed it.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. The defining failure is
  a named one: CLAUDE.md says "Don't hand-roll a reader for a format the
  repository already reads. Grep for the existing method first." I hand-built
  the request when three proven runners submitted through `eqc_models`, and
  `run_hardware_b3._submit_via_eqc`'s docstring says why not to. The rule
  existed and did not reach the moment of writing. The same is true of the
  footer rule.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. The hardware controls
  held: floor, cap, idempotency, ledger-before-spend, and the spend reconciled
  to the second. The infeasible control was caught at zero cost. But a test
  process could reach a metered submission, and the only reason it did not
  spend was a malformed request and a network error -- a risk that
  materialized and was absorbed by chance, not by a control.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. F124 (research before any
  Dirac-3 run) and F123 (Phase 1 / Phase 2 separation) are registered with the
  team lead's scope, and every open card that can spend device seconds depends
  on F124. Suite and CI green.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. I changed
  `spectra_segment.py` -- Phase 1 analysis code, which section 11 makes
  amendable only by a dated amendment -- without one, and five Phase 1 files
  changed this sprint. Recorded on F123 rather than reverted. The gate report's
  metered-arm predicate excludes `qsvm_hw`; deferred to F123.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond F123 and F124, which the team
  lead originated this sprint.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No issues -- expectations met. No coding
  agents were assigned this sprint.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

## Summary

**The sprint delivered, and the hardware discipline held where it was
mechanized.** Floor, cap, idempotency and ledger-before-spend all worked, and
653 s reconciled to the second.

**Every lower score has the same shape as Sprint 20's: a prevention existed
and did not reach the moment it was needed.** CLAUDE.md already forbade
hand-rolling a format the repository reads; the footer rule already said
"generate it, never type it"; the capability pre-flight already said to read
the documents holding findings. Each was a sentence, and each was bypassed
while the work was being written. The one failure with no prevention at all
-- a test able to spend device seconds -- was closed during the sprint by a
mechanism, not a sentence.

So the improvements below extend existing preventions so they fire at the
moment of failure, rather than adding new rules beside them.

## Improvement Decisions

Proposed 2026-10-06; awaiting the team lead's disposition.

| # | Title | Source | Type | Effort | Decision |
|---|---|---|---|---|---|
| IMP-1 | Extend the capability pre-flight's read list | Cat 4, 9 | Prevention, extends Sprint 20 IMP-2 | 15m | pending |
| IMP-2 | Footer check in the existing every-turn Stop hook | Cat 6, 9 | Prevention, extends `sprint_auto_advance.py` | 45m | pending |
| IMP-3 | The test suite may not change committed evidence | Cat 2, 10 | Detection, extends `test_evidence_artifacts_current.py` | 30m | pending |
| IMP-4 | Guard Phase 1 analysis code against unapproved edits | Cat 12 | Prevention, extends `block_unapproved_submission_edit.py` | in F123 | pending |
