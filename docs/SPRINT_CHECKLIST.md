# Sprint Checklist (single page)

Consult at EVERY phase boundary (open this file in the same turn; walk lines with DONE/N-A/NOT-DONE + evidence). Full detail: SPRINT_EXECUTION_WORKFLOW.md.

## Phase 1: Backlog Refinement (mandatory, every sprint)
- [ ] Read ALL_SPRINTS_MASTER_PLAN.md + repo CHECKLIST.md
- [ ] Read BACKLOG_REFINEMENT.md "Backlog Presentation Format" THIS TURN, then present candidates (Summary Index first, F# IDs, numeric priorities, HOLD one-liners)
- [ ] Record team-lead selection; update master plan; commit

## Phase 2: Pre-Kickoff
- [ ] Previous PR merged; previous sprint issues CLOSED (manual close; feature->develop does not auto-close)
- [ ] Working tree clean; develop pulled current; sprint branches never deleted
- [ ] `pytest experiments/src -q` green; dependency scan noted

## Phase 3: Kickoff & Planning
- [ ] Previous sprint SUMMARY doc created and linked in master plan (three-doc rule: PLAN + RETROSPECTIVE + SUMMARY, no exceptions)
- [ ] SPRINT_N_PLAN.md drafted: objective, tasks, quantifiable acceptance criteria, minute estimates
- [ ] Plan verified against branch state (already-shipped work marked, stale paths corrected); re-estimated if findings
- [ ] Branch exists (usually via prior 6.6 carry-forward); DRAFT PR created/updated (STAYS DRAFT until 7.7)
- [ ] One GitHub issue per task (`sprint` label) BEFORE first task file is touched; all OPEN
- [ ] Explicit team-lead approval obtained; PR body updated to approved plan

## Phase 4: Execution (auto-advance window: no permission-asking)
- [ ] Tasks in plan order; tests after each change; commits reference issue #N
- [ ] `git status --short` before every staging; every entry accounted for; 0* files committed neutrally, never read
- [ ] Results only via frozen protocol; every metric -> results.json with evidence tag
- [ ] HARDWARE: any metered run stops for approval (Criterion H), always

## Phase 5: Review & Validation
- [ ] Full suite green; no unamended drift from prereg-freeze in analysis code
- [ ] Plan acceptance criteria walked line by line WITH EVIDENCE
- [ ] Handed to team lead for manual validation (questions correct from here)

## Phase 6: Push & Finalize PR
- [ ] Branch pushed; existing draft PR body updated (still DRAFT); interim status given, not "ready"
- [ ] ON MERGE NOTIFICATION: next sprint branch created FROM CURRENT FEATURE BRANCH immediately; post-merge work committed there; never stash; never branch from develop post-merge

## Phase 7: Retrospective (before ready)
- [ ] 7-step protocol run in order (SPRINT_RETROSPECTIVE.md); 14 categories x 4 roles, verbatim, no placeholders
- [ ] Improvements proposed + dispositioned; now-items committed; backlog-items -> master plan with F#s
- [ ] Completion updates: master plan Last Completed Sprint; CHECKLIST.md reconciled; sprint_status updated
- [ ] `gh pr ready` (ONLY here); final gate; team lead notified for approval

## Phase 8: Delivery Cycle (after develop merge)
- [ ] Team lead merges develop->main (parallel; do not block on it)
- [ ] Refinement Pass 1 completeness sweep (issues, docs triad, master plan, pruning) -- corrections only
- [ ] Submission-artifact refresh if due (QCi letter numbers, requirements matrix, paper vs results.json)
- [ ] Refinement Pass 2 scope selection -> Phase 3
