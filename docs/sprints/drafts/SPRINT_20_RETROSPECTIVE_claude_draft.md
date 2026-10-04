# Sprint 20 Retrospective: Claude Code Development Team draft

Written 2026-10-03, step 2 of the 7-step protocol. The team lead scored all
sixteen categories **Very Good**. Where I score lower, both are recorded and
the improvements are built from the lower score.

The sprint delivered what it set out to: F97, F93, F98, F99, at 161 minutes
against 171 estimated, zero metered seconds. Everything below is about how.

### 1. Effective while as Efficient as Reasonably Possible

**Good.** Scope was right and the sequencing worked: Task B's decision was
held to the end exactly as instructed, so three tasks finished before any
question was asked.

The inefficiency is Task B itself. I built its analysis without reading
`docs/HARDWARE_REQUEST_B4.md`, which already contained the answer — line 89
states the 13 negative proxy edges are expected and "not a red flag for B4",
with the reason. I spent most of a task rediscovering a conclusion this
repository had already written down, and then presented a four-option decision
built on the wrong premise.

### 2. Testing Approach

**Very Good.** Every guard added this sprint was proven RED before it was
accepted: 5 for F97's phase gates, 3 for F98's budget and ordering, 4 for
F99's hashes, 4 for F93's cross-references. Two of my own guards were caught
as vacuous by their own injection runs and fixed.

The F97 proof is the one I would keep as a pattern: the same code run against
nine sprint states, and separately proven to still go red where an artifact is
genuinely owed. The risk in that task was switching guards off while appearing
to fix them, and the second proof is what rules it out.

### 3. Effort Accuracy

**Very Good.** 161 against 171, within 6%, and the first sprint with a
complete set of actuals — Sprint 19 recorded two of three. IMP-1 from Sprint
18 now works.

Per-task variance is honest and small: A over by 12 (six tests, not five, and
four distinct boundaries), B under by 13, C over by 4, D over by 8 (a drift
guard not in the card). No task was off by more than a third.

### 4. Planning Quality

**Good.** The three pre-flights earned their place — each found something that
changed its task before work began, including F93's dead acceptance criteria
and F97 being wider than its card said.

The miss is that the pre-flight rule says to inventory CODE, and I did. It
does not say to inventory DOCUMENTS, and for F93 the evidence was in a
document. `HARDWARE_REQUEST_B4.md` is exactly where a "capability pre-flight"
for a hardware block should have looked.

### 5. Model Assignments

**Very Good.** Top tier for the three judgment tasks, Sonnet nominated for
F99's pattern-following work. The advisor call before Phase 6/7 caught two
things I would have gotten wrong.

### 6. Communication

**Needs Improvement**, and it is the team lead's correction that sets this.

I handed over Manual Validation by writing the items to a file and giving him
the path. He had to ask for them on screen. That is the
refer-back-to-scrollback failure one level removed — and it happened in the
same sprint whose validation document opens by saying it exists so he would
not have to scroll.

Separately, I presented the SPECTRA decision as a balanced four-option choice
when one option rested on a misread figure. A decision aid built on a wrong
premise is worse than no decision aid, because it looks like diligence.

### 7. Assigned Coding Agents Quality

**Very Good.** No subagents this sprint; the work was four small tasks where
delegation overhead would have exceeded the tasks.

### 8. Requirements Clarity

**Very Good.** The scope list was unambiguous and matched my recommendation.
One instruction I followed correctly and should name: holding the question to
the end meant three tasks completed before anything blocked.

### 9. Process Issues

**Needs Improvement.** Two recurring classes, both with existing prevention
that did not fire.

**The escape class, five times.** All five were inside CORRECTLY QUOTED
heredocs (`<<'PYEOF'`), where the shell is innocent and Python's own string
escaping ate the backslash. `block_heredoc_escape_loss.py` exists and
explicitly excludes quoted heredocs, so it could not fire. One instance wrote
a literal null byte into a test file and corrupted it.

**Presence-as-correctness, four times**, including inside a guard written to
catch exactly that: `test_no_force_flag_exists` grepped the source for
`--force` and matched the comment saying there deliberately is none. Another
asserted `"270"` appeared somewhere in a document where the figure occurs five
times, so deleting it from the comparison table left four hits and the test
passed on a real loss.

### 10. Risk Management

**Very Good.** Zero metered seconds. Nothing inside `docs/qci_package/` was
written to, and the F99 red-leg proof altered a recorded hash rather than a
sent artifact. I declined to add an `ALLOWED` exemption for my own CI failure
when one line would have fixed it.

### 11. Next Sprint Readiness

**Very Good.** F90 is unblocked with the decision recorded, F2b's B4 line and
F5 closed into it, and the tuned configuration plus the overfit caveat now on
the card. F94, F17 and F6 were rewritten against current knowledge.

### 12. Architecture Maintenance

**Very Good.** No preregistration drift, no amendments. The phase-gate pattern
in `test_phase3_artifacts.py` is reusable by any future state-dependent guard,
and the ordered `PHASE_ORDER` list makes "has this sprint reached X" a
comparison rather than a membership test a new slug could fall out of.

### 13. Minor Function Updates for the Next Sprint Plan

`[DEV] Report the train-test gap beside any in-segment win from the SPECTRA
block -- target: next sprint plan, est: included in F90`

### 14. Function Updates for the Future Backlog

None beyond what is registered.

### 15. Questions to be discussed before ending the sprint

None.

### 16. Summary

The sprint did its job. Two failures are worth carrying forward, and both are
cases where the prevention existed and did not reach the failure: a hook that
guards unquoted heredocs while my failures were quoted, and a repository
document that held the answer I spent a task rediscovering.
