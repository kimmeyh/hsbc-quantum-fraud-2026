# Sprint 23 Retrospective: Claude's draft (Development Team)

Drafted 2026-10-08 while the team lead's feedback is collected (step 2 of
`docs/SPRINT_RETROSPECTIVE.md`). Sprint 23 is the last sprint in this
repository: F127 step (6), restore as filed. Tasks C and D (restore commit,
`as-filed` tag) follow this retrospective by design (plan, Deviations).

### 1. Effective while as Efficient as Reasonably Possible
The pre-flight did the work that mattered. Four hazards were found before
any restore step ran, and each would have failed silently: the as-filed
`.gitignore` leaving `docs/qci_package/` unignored; the as-filed status file
and hooks tripping the old close-out hook; the pre-commit scan skipping in a
fresh worktree because its pattern file is gitignored; and the sprint branch
being checked out, so no worktree could take it. Task A then proved the
recipe in one pass. Rework: one extra decision round (D5), from my own D2
option (see 7).

### 2. Testing Approach
The dry run checked bytes, not intent: the diff against `f35699c`, the PDF
hashes against `PACKAGE.md`, ignore coverage for all 260 ignored files, and
the hook blocking a planted match (proven able to fail, not just passing).
The Phase 3 tests went red between plan and approval, as designed, and the
CI checkpoint read the failing run before calling it expected.

### 3. Effort Accuracy
Task A: 45 minutes estimated, about 20 recorded. Tasks B-D not yet done.
Planning and the pre-flight are not task-tracked; they took most of the
sprint's time.

### 4. Planning Quality
The plan named its deviations (summary written in the Phase 2 repository,
Phase 7 before the restore commit) for approval instead of discovering them
at close-out. Two gaps were caught in review before approval: the
checked-out branch and the CI order (D3). The secrets-pattern gap I found
while checking the hook's interpreter.

### 5. Model Assignments
Main loop only; no subagents. The advisor review before presenting the plan
caught both plan gaps in 4.

### 6. Communication
I acted on an ambiguous "yes" (copying memory to the Phase 2 project) as a
stated assumption, reversible, and said so. One footer was typed instead of
generated; the Stop hook caught it.

### 7. Requirements Clarity
**D2 option 2 said "this repository's sprint is renumbered" and gave no
number.** That left a dependent decision open and cost a round (D5), where
the team lead set the rule that settles it: the Phase 2 repository's first
sprint is this repository's last plus one. This is the Sprint 22 IMP-2 class
again (a decision whose answer needs a second decision). An option must be
complete enough to execute on its own.

### 8. Documentation
Plan, validation file and CHANGELOG were updated in the same commits as the
decisions. The F127 card records the session split and the `.gitignore`
finding. All of it leaves this tree at the restore and survives in history
and in the Phase 2 repository.

### 9. Process Issues
The heredoc escape hook blocked two Python heredocs that carried an intended
`\n`; the Edit tool was the right route both times. The `test_ci_status.py`
hazard (F131) is carded for the Phase 2 repository.

### 10. Risk Management
The exposure risk was the one that mattered, and it was caught in planning,
not after a push. Open: the as-filed suite on today's CI runner (D3: reported,
not blocking).

### 11. Next Sprint Readiness
No next sprint here. The Phase 2 repository's Sprint 24 has its handoff
prompt; it waits only for this retrospective to write `SPRINT_23_SUMMARY.md`.

### 12. Architecture Maintenance
The restore reverts `PREREGISTRATION.md` by amendment A33 in this tree only
(approved, V2). The frozen protocol is untouched; A33 continues in the Phase
2 repository.

### 13. Minor Function Updates for the Next Sprint Plan
None for this repository. [DEV] A decision option that implies a second
choice names that choice's default inline -- target: Phase 2 repository
Sprint 24 plan, est: 10m

### 14. Function Updates for the Future Backlog
None new; F131 was carded in this sprint's refinement.

### 15. Assigned Coding Agents Quality
No coding agents used.

### 16. Questions to be discussed before ending the sprint
None.
