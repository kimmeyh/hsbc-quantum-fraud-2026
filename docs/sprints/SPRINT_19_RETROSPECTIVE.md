# Sprint 19 Retrospective

**Sprint**: 19, Send the QCi Package Clean (F92)
**Date**: 2026-09-27
**Scope delivered**: Tasks A, B, D (105 minutes approved). Task C not
approved, moved to F96. Scope extended after Task D by team-lead direction.
**Metered Dirac-3 seconds**: **0**
**The objective**: the package was **SENT 2026-09-25 at 12:23 PM**.

## Scoring, both roles

The team lead scored all sixteen categories **Very Good**. Claude scored five
lower. Where the two disagree, both are recorded; the lower score is the one
the improvements are built from.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Good |
| Testing approach | Very Good | Very Good |
| Effort accuracy | Very Good | **Needs Improvement** |
| Planning quality | Very Good | Good |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | Good |
| Requirements clarity | Very Good | Good |
| Documentation | Very Good | Good |
| Process issues | Very Good | Good |
| Risk management | Very Good | Very Good |
| Next sprint readiness | Very Good | Very Good |
| Architecture maintenance | Very Good | Very Good |
| Assigned coding agents quality | Very Good | Very Good |

Team lead: no minor function updates, no backlog additions, no questions
before closing.

## Sprint 19 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The objective was met and the
  105-minute cut was right: Task C was declined and became F96 rather than
  expanding the sprint. Task D's fresh-context review was the highest-value 20
  minutes, returning fourteen findings against a plan that predicted few. The
  inefficiency: Task B built thirteen guards that were retired within about 24
  hours. Each caught a stale claim during a revision round, so they were not
  waste in the moment, but the plan did not anticipate that the memo would be
  frozen inside the same sprint.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Every Task B guard was proven
  RED against the old text with the F89 injection helper before being
  accepted. The same discipline caught a defect in my own later work:
  `test_the_qci_package_is_clean` filtered its document list through
  `exists()`, so deleting the memo would have narrowed the scan from three
  documents to two and still passed -- the
  "could-not-check-reads-as-clean" class. Found and fixed with a red-leg
  proof.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: **Needs Improvement.** Task D's actual is
  NOT RECORDED: it spanned an approval stop of several hours, so wall clock
  does not measure the work. IMP-1 shipped last sprint to make actuals a
  completion-time habit, and on its first real use it captured two of three
  tasks -- it needs a form for "this task contained a wait" rather than
  falling back to null. Separately, the post-validation work (validation
  document, guard retirement, HTML converter, several rounds of BLUF
  compression and fact-checking) was substantial, requested, and unestimated,
  so the sprint's recorded effort understates what it cost.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The structure was sound:
  dependencies stated, the total derived from the cards rather than typed in,
  and a premise falsifier that fired. The miss: the plan treated the memo as
  an editable document for its whole life. Task B's guards, the readability
  check's document list and the cross-document tests were all built on that
  assumption, and the memo was sent three days later. One planning question --
  "which of these documents will be frozen before the next sprint?" -- would
  have changed Task B's scope.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The fresh-context reviewer for
  Task D produced the sprint's most valuable output. Consulting the advisor
  before committing to the Phase 6/7 approach caught two things I would have
  gotten wrong: I was about to restate suite counts in a committed document,
  and I had not verified the sent PDF's contents before writing them up.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The PR body and commits record what
  happened, including the failures. Two of my own: I answered a request for
  the BLUF compressions with "Answered above in three lengths", referring the
  team lead back to scrollback -- the exact behavior CLAUDE.md bans, in the
  session where I had just written a validation document to a file to avoid
  it, and he had to ask twice. And the schedule-4 inconsistency went out
  unresolved: I flagged it, offered to fix the plan, the conversation moved on
  to deleting the memo, and the email went out with that plan attached.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The six memo passages were drafted
  and approved during planning, which is why Task A took two minutes. Two
  ambiguities I asked about rather than assumed: whether "OK on your 1. and
  2." approved an observation or selected an option, and whether the `_files`
  folder or the `.htm` was the sent document. One I got wrong: I asserted the
  schedule retest needed its own bullet on cost grounds, estimating 96 metered
  fits and ~2,000 seconds, when the master plan already scoped it as F95 at
  four fits and ~60 seconds. I had not searched the backlog before estimating.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The three-doc rule is intact and the
  validation document now exists as a file rather than terminal scrollback.
  But that document was stale within two days in three ways: it pointed at a
  deleted file, it restated the suite count (which CLAUDE.md bans outright),
  and it described the memo as a draft after it had been sent. I wrote a
  durable handover and then let it rot, in the same sprint.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Three worth recording. A hand-rolled
  PDF extractor produced a confident wrong answer -- my zlib stream-parse
  reported "9,000 ABSENT" from a document whose headline is the 9,000-second
  ask, and only checking against `pypdf` (the method the repo already uses)
  exposed it; a broken tool reporting ABSENT reads exactly like a real
  finding. A regex escape was eaten by the shell again (the F82 class), fixed
  by writing to a file. And my AST-based guard retirement scanned function
  bodies for `MEMO`, finding thirteen tests but missing the `parametrize`
  decorator, so collection failed with `NameError` -- caught by running the
  suite.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The irreversible actions were
  handled correctly. I refused to delete the memo draft myself and said so. I
  did not edit `HARDWARE_PLAN_PHASE_2.md` after its PDF was sent, because that
  would create the version problem the AS SENT convention exists to prevent,
  and I flagged the freeze question as the team lead's decision rather than
  making it. Zero metered seconds spent.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. **F95 is now unblocked** -- it
  was held until the memo was sent: four fits at schedule 4, ~60 s, against
  the 1,681 balance. **F96** holds Task C, now complicated by the plan having
  been sent. **F90** is the schedule-3 decision at 833 variables, ~1,236 s,
  which would spend 74% of the remaining balance and needs its own approval.
  The schedule-4 documentation gap is a new item.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. `scripts/outlook_htm_to_md.py`
  is a reusable tool rather than a throwaway, verified byte-identical to the
  hand conversion and verified to fail closed when a named figure does not
  survive. The AS SENT naming convention now has a second instance, which
  makes it a pattern rather than a one-off. No divergence from the frozen
  preregistration; no amendments this sprint.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: `[DEV] Disposition the schedule-4 gap
  between the memo and the hardware plan -- target: Sprint 20 plan, est: 15m`

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond the F95, F96 and F90 items
  already registered.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The Task D reviewer had no
  sprint context and found fourteen disagreements, each verified against the
  documents and `results.json` before it reached the team lead. No false
  findings required rework -- a change from Sprint 17, where two review
  findings were wrong.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: One, and it blocks nothing: **is
  `HARDWARE_PLAN_PHASE_2.md` now frozen like the memo?** Its PDF was sent on
  2026-09-25. If it is frozen, F96's Task C work needs a new file rather than
  an edit, and its guards should be retired the way the memo's were. If it is
  not, the next edit silently diverges from what QCi holds.

## Summary

**The sprint did what it set out to do.** The package went to QCi on
2026-09-25 with every figure traced to an owning document, and a fresh-context
review caught fourteen cross-document disagreements before it went rather than
after. Zero metered seconds. No preregistration drift.

**The pattern across my five lower scores is one thing: a document's lifecycle
was not planned.** The memo was treated as editable for its whole life, so
thirteen guards, a readability document list, and a set of cross-document
tests were all built against a file that was frozen three days later. The
validation document I wrote to make the handover durable went stale in two
days for the same reason. None of this broke anything, and all of it was
avoidable with one question at planning time.

**Two smaller threads.** IMP-1 (actuals at completion) shipped last sprint and
captured two of three tasks on its first real use, because it has no form for
a task containing a multi-hour approval wait. And twice I produced a confident
wrong answer from a tool I had built myself rather than the one the repository
already used -- the PDF extractor, and a cost estimate I made without
searching the backlog first.
