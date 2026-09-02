# Sprint Stopping Criteria

Adapted 2026-08-30 from spamfilter-multi's SPRINT_STOPPING_CRITERIA.md. Purpose: models work autonomously during sprint execution until one of these criteria is met. Stopping at the right time is not failure; stopping at the wrong time wastes the team lead's money and calendar.

## Criterion H (project-specific, overrides the auto-advance window): Metered Hardware

Any metered Dirac-3 run STOPS for explicit team-lead approval, every time: state the block, the call count, and the expected metered seconds, then wait. Sprint-plan approval never covers hardware execution. An errored hardware solve retries at most twice (frozen protocol); a third failure reports the cell as failed and continues with the rest of the approved list.

## Criteria 1-10 (adapted)

1. **NORMAL COMPLETION** -- all sprint tasks complete, tests green, acceptance criteria walked with evidence. Action: proceed to Phase 5 validation handoff, then Phase 6/7 per the workflow. Then present next-step options (review / next sprint / ad-hoc).
2. **BLOCKED** -- external dependency (QCi grant, portal, Kaggle, team-lead-only input) or an error persisting after 2-3 genuine resolution attempts. Action: document the blocker (root cause, attempted solutions, what unblocks) in the sprint issue, notify immediately, continue any unblocked tasks.
3. **SCOPE CHANGE** -- the team lead adds/changes requirements mid-sprint, or a task's true size is 2x+ the estimate. Action: stop, present original vs new estimate and options (reduce elsewhere / extend / defer), wait for decision. Deferring approved work is ALWAYS a Class-3 decision, never Claude's call.
4. **DISCOVERY** -- a defect in existing work. Critical (blocks the sprint): fix now, add a regression test, document. High: fix if time allows, else backlog with an issue. Medium/Low: issue + backlog, do NOT context-switch. **Precedence: a defect that invalidates recorded results, or any leak/protocol violation, is NEVER Criterion 4 -- it is ALWAYS Criterion 7 (stop, document, wait), even inside the auto-advance window. Never silently fix and re-run evidence-bearing results.**
   - **4a. Team-lead-found gap in sprint theme**: extend scope WITHOUT formal change when ALL hold: same category as sprint work, cumulative fix < 2h, no new design decisions, team-lead-reported. Otherwise treat as 3 or 4.
5. **REVIEW REQUEST** -- the team lead asks for early review. Stabilize, commit, go to Phase 7.
6. **SPRINT REVIEW COMPLETE** -- Phase 7 done, PR ready, team lead notified. Wait for approval; on merge, execute 6.6 carry-forward immediately.
7. **FUNDAMENTAL DESIGN FAILURE** -- evidence the approach cannot work (for this project also: a discovered leak or protocol violation that invalidates a result set). Takes precedence over Criterion 4 whenever both could apply. Action: document, propose 2-3 alternatives, wait. If the fix would amend the frozen preregistration, that is Class 1 and requires explicit approval as a dated amendment.
8. **CONTEXT LIMIT** -- near the window's end: commit everything, reconcile CHECKLIST.md, update sprint status, write a clean handoff so the next session resumes from the repo alone.
9. **TIME LIMIT** -- wall-clock hours are NOT a stop signal by themselves. The only hard time boundary in Phase 1 is the master timeline (submission-ready Sep 8; submitted never later than Sep 14). Do not wrap up early "concerned about hours"; do not defer approved scope on time intuition (Class 3).
10. **NOT A STOPPING CRITERION: implementation decisions.** Method A vs B, refactor vs extend, signature changes needed to meet acceptance criteria, single test failures, style warnings, approach uncertainty: make the best engineering judgment, document it, continue. Decision rule: "Does this decision enable the acceptance criteria?" YES -> decide and continue. NO -> it is scope change (Criterion 3).

## What should NOT cause stopping

Single test failure (fix it); analysis warning (fix or note); waiting on a push (background it); uncertainty (implement, test, iterate); feature seems minimal (acceptance criteria define done); minor style (fix or note); any implementation choice within scope.

## Stopping checklist (any stop)

- [ ] Work committed; no uncommitted changes stranded
- [ ] Sprint issue updated with status
- [ ] Blocker documented if applicable
- [ ] Team lead notified: reason, status (done/remaining), next steps, decision needed (if any)

## Communication template

```
STOP: [reason / criterion]
Status: [completed vs remaining]
Reason: [why stopping is necessary]
Action taken: [commits, docs, issues]
Next steps: [what resumes work]
Team-lead decision needed: [what, or "none"]
```
