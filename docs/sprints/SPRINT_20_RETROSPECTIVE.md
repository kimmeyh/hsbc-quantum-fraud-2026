# Sprint 20 Retrospective

**Sprint**: 20, Make the Suite Readable Again
**Date**: 2026-10-03
**Scope delivered**: F97, F93, F98, F99 — all four
**Effort**: 161 minutes against 171 estimated (within 6%)
**Metered Dirac-3 seconds**: **0**

## Scoring, both roles

The team lead scored all sixteen categories **Very Good**. Claude scored four
lower. Where the two disagree, both are recorded; the lower score is the one
the improvements are built from.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Good |
| Testing approach | Very Good | Very Good |
| Effort accuracy | Very Good | Very Good |
| Planning quality | Very Good | Good |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | **Needs Improvement** |
| Requirements clarity | Very Good | Very Good |
| Documentation | Very Good | Very Good |
| Process issues | Very Good | **Needs Improvement** |
| Risk management | Very Good | Very Good |
| Next sprint readiness | Very Good | Very Good |
| Architecture maintenance | Very Good | Very Good |
| Assigned coding agents quality | Very Good | Very Good |

Team lead: no minor function updates, no backlog additions, no questions
before closing. Manual Validation complete.

## Sprint 20 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Scope was right and the sequencing
  worked — Task B's decision was held to the end as instructed, so three tasks
  finished before any question was asked. The inefficiency is Task B itself: I
  built its analysis without reading `docs/HARDWARE_REQUEST_B4.md`, which
  already contained the answer at line 89 (the 13 negative proxy edges are
  expected and "not a red flag for B4", with the reason). I spent most of a
  task rediscovering a conclusion this repository had already written down.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Every guard was proven RED
  before acceptance: 5 for F97's phase gates, 3 for F98's budget and ordering,
  4 for F99's hashes, 4 for F93's cross-references. Two of my own guards were
  caught vacuous by their own injection runs and fixed. The F97 proof is worth
  keeping as a pattern — the same code against nine sprint states, plus a
  separate proof that the guards still go red where an artifact is genuinely
  owed. The risk in that task was switching guards off while appearing to fix
  them, and the second proof is what rules it out.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. 161 against 171, within 6%, and
  the first sprint with a COMPLETE set of actuals — Sprint 19 recorded two of
  three, so IMP-1 from Sprint 18 now works. Per-task variance is small and
  honest: A over by 12 (six tests, not five, and four distinct boundaries), B
  under by 13, C over by 4, D over by 8 (a drift guard not in the card).

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The three pre-flights earned their
  place — each found something that changed its task before work began,
  including F93's dead acceptance criteria and F97 being wider than its card
  said. The miss: the pre-flight rule says to inventory CODE, and I did. It
  does not say to inventory DOCUMENTS, and for F93 the evidence was in a
  document. `HARDWARE_REQUEST_B4.md` is exactly where a capability pre-flight
  for a hardware block should have looked.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Top tier for the three judgment
  tasks, Sonnet nominated for F99's pattern-following work. The advisor call
  before Phase 6/7 caught two things I would have gotten wrong.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: **Needs Improvement**, and the team lead's
  correction sets this. I handed over Manual Validation by writing the items
  to a file and giving him the path; he had to ask for them on screen. That is
  the refer-back-to-scrollback failure one level removed, in the same sprint
  whose validation document opens by saying it exists so he would not have to
  scroll. Separately, I presented the SPECTRA decision as a balanced
  four-option choice when one option rested on a misread figure — a decision
  aid built on a wrong premise is worse than none, because it looks like
  diligence.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The scope list was unambiguous
  and matched the recommendation. One instruction worth naming because it
  worked: holding the question to the end meant three tasks completed before
  anything blocked.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The validation document exists
  as a file and was corrected when the memo state changed. Four cards were
  rewritten against current knowledge rather than left to rot, and the SPECTRA
  reconciliation records what I got wrong alongside the decision.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: **Needs Improvement.** Two recurring
  classes, both with existing prevention that did not fire. **The escape
  class, five times** — all five inside CORRECTLY QUOTED heredocs
  (`<<'PYEOF'`), where the shell is innocent and Python's own string escaping
  ate the backslash. `block_heredoc_escape_loss.py` exists and explicitly
  excludes quoted heredocs, so it could not fire. One instance wrote a literal
  null byte into a test file and corrupted it. **Presence-as-correctness, four
  times**, including inside a guard written to catch exactly that:
  `test_no_force_flag_exists` grepped for `--force` and matched the comment
  saying there deliberately is none.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Zero metered seconds. Nothing
  inside `docs/qci_package/` was written to, and the F99 red-leg proof altered
  a recorded hash rather than a sent artifact. When my own CI failure could
  have been fixed with a one-line `ALLOWED` exemption, I fixed the document
  instead.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. F90 is unblocked with the
  decision recorded, F2b's B4 line and F5 closed into it, and the tuned
  configuration plus the overfit caveat now on the card. F94, F17 and F6 were
  rewritten against current knowledge.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. No preregistration drift, no
  amendments. The phase-gate pattern is reusable by any future
  state-dependent guard, and the ordered `PHASE_ORDER` list makes "has this
  sprint reached X" a comparison rather than a membership test a new slug
  could silently fall out of.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: `[DEV] Report the train-test gap beside
  any in-segment win from the SPECTRA block -- target: next sprint plan, est:
  included in F90`

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond what is registered.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. No subagents this sprint; four
  small tasks where delegation overhead would have exceeded the tasks.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none.

## Summary

**The sprint did its job.** Four cards delivered, 161 minutes against 171,
zero metered seconds, no preregistration drift, and the first complete set of
actuals. The suite is green in a planning window for the first time, which was
the point.

**Both of my lower scores are the same shape: the prevention existed and did
not reach the failure.**

`block_heredoc_escape_loss.py` was written for this exact class and could not
fire, because it guards *unquoted* heredocs and all five of my failures were
*quoted* — the shell was innocent and Python's own escaping did the damage.
The capability pre-flight rule says to inventory code, and I did; the evidence
for F93 was in a document, and `HARDWARE_REQUEST_B4.md` already held the
answer I spent a task rediscovering.

That shape is what the improvements target. In both cases a new mechanism
would be the wrong response — there is already a hook for the escape class and
already a pre-flight rule for the planning class, and each needs its reach
extended rather than a sibling built beside it.

**The third item is presence-as-correctness, four times in one sprint**,
including inside a guard written to catch it. It has now appeared in three
consecutive sprints and is the most frequent single defect in my work on this
repository. It also has no existing mechanism to extend, which makes it the
one place a new check is justified.
