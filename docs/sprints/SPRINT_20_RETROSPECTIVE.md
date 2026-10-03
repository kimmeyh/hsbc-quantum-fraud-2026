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

## Improvement Decisions

Three proposed. The team lead approved IMP-1 and IMP-3 now, and challenged
IMP-2's scope (2026-10-03).

### Implemented

**IMP-1. `block_heredoc_escape_loss.py` extended to QUOTED heredocs.**

The hook was written for the escape class and could not fire on any of Sprint
20's five occurrences, because it guards UNQUOTED heredocs and all five were
quoted. In a quoted heredoc the shell is innocent -- the body arrives verbatim
-- and then PYTHON interprets the escape, because the string literal is not
raw. Same symptom, a layer lower.

Extended rather than duplicated, per the standing instruction: the file
already parses heredocs, finds delimiters, decides whether a command writes a
file, and formats a block message. A sibling hook would have copied all four.

Verified on eleven cases: all five real failures blocked, and `r""`, `rb""`,
`br""`, `chr(92)` construction, prose, a pager heredoc, an unquoted body with
no escape, and the bypass token all still allowed. A guard that fires on
correct work gets bypassed, so the allow half was tested as carefully as the
block half.

**One finding worth more than the hook.** The `b` prefix was initially exempt
alongside `r`, which made the hook miss its own worst instance -- a bytes
literal with `\x00` that wrote a real NUL byte into a test file. Only `rb`
and `br` are safe; `b""` interprets escapes exactly as `""` does.

**And it caught its author within minutes.** Writing the IMP-3 proof script, I
reached for a quoted heredoc containing `\n` and the hook blocked it. The
improvement fired on the behavior it was built for, in the same session it was
installed, against the person who installed it.

### Rejected after being built: IMP-3

**IMP-3 was built, tested, and REMOVED, because it caught none of the four
failures it was written for.**

The proposal was a mechanical check in `test_guard_discipline.py`: an
unanchored presence assertion on a repeated string must be anchored to the
line that owns it. Three attempts, each narrowed after the previous was wrong:

1. **Every `assert "X" in whole_file`** flagged 23 offenders, most correct.
   `assert "isfinite" in src` verifying a guard clause exists in code is a
   fine presence check. A guard firing on 23 mostly-correct cases is bypassed
   on first contact.
2. **Occurrence counting** did not separate them: `isfinite` occurs twice and
   is fine, `270` occurs eight times and is not.
3. **Scoped to numeric literals against documents** -- the shape three of the
   four shared -- reduced it to one offender, which proved to be a legitimate
   exemption.

Then the red-leg proof failed. Reverting the real Sprint 20 defect left the
check GREEN, for a structural reason: the failing assertions were
`assert fact in row` over a loop variable, not a string literal, and an AST
check for `ast.Constant` on the left of `in` cannot see them.

So it passed its own suite while catching zero of its four cases. That is
precisely the vacuous guard this repository bans -- false confidence is worse
than no check. Removed rather than shipped.

**What the class actually needs**, recorded for whoever takes it next: not a
static check. The four failures were all caught by INJECTION, by breaking the
thing and watching the guard stay green. `injection.py` already does that and
already found three of the four. The gap is that injection is run by choice
rather than by default, which is a process question rather than a tooling one.

### Open

**IMP-2** (the capability pre-flight should inventory documents, not only
code). The team lead challenged the scope: "isn't there a troubleshooting doc
that would be best for this instead of all docs files?"

Checked: no troubleshooting document exists, though `SPRINT_RETROSPECTIVE.md`
category 9 explicitly calls for one ("anything that belongs in a
troubleshooting note or hook"). So there is nothing to extend.

What does exist is a small, predictable set of documents where hardware
findings live: `HARDWARE_REQUEST_*`, `*_RESULT.md`, `*_RECONCILIATION.md`,
`RESULTS_MEMO.md`. F93's answer was in `HARDWARE_REQUEST_B4.md`, exactly where
a hardware-block pre-flight should look. Naming four file patterns is specific
enough to follow; "grep docs/" was not.

Revised proposal awaiting disposition. Whether a troubleshooting document
should exist at all is a separate question, deliberately not answered as a
side effect of this one.

## Scope addition confirmed: a299ad2

**Team lead, 2026-10-03: this commit was incorporated into Sprint 20 and
should be part of it. CONFIRMED, by checking rather than by agreeing.**

- It is HEAD of `feature/20260930_Sprint_20` and pushed
- `git branch -a --contains a299ad2` lists only this sprint's branch, local
  and remote, so it is in no other branch and reaches develop through PR #146
- It was authored in a different session (Opus 5.5) at 15:48, which is why it
  appears in no earlier record here

**What it changed**, and two items affect this sprint's close-out:

`CHECKLIST-Phase2-pre.md` is merged into `CHECKLIST-Phase2.md` and deleted, so
one live checklist now covers both the pre-notification period and the PoC
sprint. **My Phase 7 reconciliation walked the deleted file.** That report is
superseded: the merged checklist was walked on 2026-10-03 and stands at 12
ticked, 30 unticked, with every unticked item gated on the mid-November
notification, the Phase 2 preregistration, or a future sprint card. None is
Sprint 20 work, so nothing is owed. No document still references the deleted
path -- the commit updated the process docs that named it.

Items 5 and 6 of the six experiments are corrected against the FILED proposal.
The 2026-09-12 checklist listed 5 as the gate-based arm and 6 as B4/B5; the
filed PDF -- hash-pinned by `test_published_artifacts.py` -- commits to 5 =
Segment transfer (H5) and 6 = Scaling claim, in section 5. That restores the
published commitment, and it is the right direction of correction: the filed
document is the record, and the checklist was wrong.

F100 through F121 are registered so every Phase 2 item has a card. F93 and F2b
are closed into F90 and **kept in place**, because
`test_spectra_reconciliation.py` requires every SPECTRA record to stay
findable -- the guard written in Task B constrained how a later session could
close those cards, which is the guard working as intended.

F90's "three to eight times" overfit caveat is corrected to the source ratios.
I wrote that figure into the card from the findings document; the correction
tightens it to what the source actually reports.

Markdown only, no code. Suite verified green after it: 1,417 passed, 73
skipped.
