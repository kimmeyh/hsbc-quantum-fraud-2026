# Sprint Execution Workflow

Adapted 2026-08-30 from spamfilter-multi's SPRINT_EXECUTION_WORKFLOW.md (its hard-won rules preserved; Flutter/Store specifics replaced with this project's equivalents). This is the authoritative step-by-step sprint process for hsbc-quantum-fraud-2026.

## SPRINT EXECUTION Documentation

| Document | Purpose |
|---|---|
| **ALL_SPRINTS_MASTER_PLAN.md** | Master plan: past sprint summary, last completed sprint, next sprint candidates, item details |
| **SPRINT_EXECUTION_WORKFLOW.md** (this doc) | Step-by-step execution checklist (Phases 1-8) |
| **SPRINT_CHECKLIST.md** | Single-page phase checklist consulted at every boundary |
| **SPRINT_STOPPING_CRITERIA.md** | When and why to stop working |
| **SPRINT_RETROSPECTIVE.md** | Retrospective protocol and the 16x4 template |
| **BACKLOG_REFINEMENT.md** | Refinement passes and the authoritative presentation format |
| **SPRINT_PROCESS.md** | One-page overlay: branch model, carry-forward, standing rules |
| **CHECKLIST.md** (repo root) | The submission-wide task ledger (Phase 1 deliverable map) |
| **experiments/PREREGISTRATION.md** | FROZEN protocol; amendment discipline overrides everything here |

## Phase Cheat Sheet

Consult this line at the START and END of every phase; state which steps were done. Crossing a boundary by "just doing the next work" is how steps get missed.

| Phase | Top actions | Done when |
|---|---|---|
| **1. Backlog Refinement** | MANDATORY every sprint, no request needed. Read master plan + CHECKLIST.md; present candidates in BACKLOG_REFINEMENT.md format (read its format section IN THE SAME TURN first); capture selection | Team lead has picked items; no scope questions open |
| **2. Sprint Pre-Kickoff** | Verify previous PR merged; sprint issues closed; working tree clean; develop current; venv tests green (`pytest experiments/src -q`) | All gates green |
| **3. Kickoff & Planning** | Draft `docs/sprints/SPRINT_N_PLAN.md`; verify plan against branch state (3.2.2.1); create GitHub issue per task + DRAFT PR (3.3.1); get explicit 3.7 approval | Team lead says "plan approved" -- durable authorization for Phases 4-7 |
| **4. Execution** | Implement tasks in plan order; run `pytest experiments/src -q` after each; commit with issue number; results only through the frozen protocol | All acceptance criteria met; tests green |
| **5. Review & Validation** | Full test suite; results.json integrity check (every number tagged); walk plan acceptance criteria line by line with evidence; hand to team lead for manual validation | Team-lead validation feedback addressed |
| **6. Push & Finalize PR** | Push branch; UPDATE the draft PR body (keep DRAFT); on merge notification, IMMEDIATELY create next sprint branch FROM THE CURRENT FEATURE BRANCH (6.6) | PR updated, still draft; next branch created on merge |
| **7. Retrospective** | 7-step protocol per SPRINT_RETROSPECTIVE.md (16 categories x 4 roles); apply-now improvements committed; THEN `gh pr ready` (the ONE place); notify team lead for final approval | Retro doc committed; PR ready; team lead notified |
| **8. Delivery Cycle** | After develop merge: team lead merges develop->main in parallel with Refinement Pass 1 (completeness sweep); submission-artifact refresh if due (see below); Refinement Pass 2 (scope selection) | Master plan rolled; next scope selected |

## Invariants (all phases)

1. **Auto-advance window**: between Phase 3.7 approval and the start of Phase 5's team-lead validation, do NOT ask permission at task or phase boundaries; state the next action in one sentence and execute. Before approval, asking is REQUIRED. From validation onward, asking is CORRECT. Commits, pushes, PR-body updates, and test runs are within standing approval.
2. **Hardware override**: a metered Dirac-3 run ALWAYS stops for explicit team-lead approval with call count and expected seconds stated, regardless of the window. No exception (SPRINT_STOPPING_CRITERIA Criterion H).
3. **Stop only** for the criteria in SPRINT_STOPPING_CRITERIA.md; never for implementation choices, approach uncertainty, or "confirming the next step".
4. **Open-the-file verification**: before reporting any checklist section, phase, or close-out complete, OPEN the governing checklist in the same turn and walk it line by line: `DONE (<evidence>)`, `N/A (<why>)`, or `NOT DONE -> doing it now`. "I believe I did that" is not verification.
5. **User-request inventory**: a message with multiple asks is a CHECKLIST, not a theme. Enumerate every discrete ask before starting; restate each with its status before ending the turn. A terminal condition ("continue until X") is itself an ask.
6. **Read the format doc before producing its output**: retrospective template, backlog presentation format, plan template. Mirror exactly; never reproduce from memory.
7. **Decision-Class Checkpoint Protocol**: sprint-plan approval is NOT authorization for (Class 1) protocol changes -- anything amending the frozen PREREGISTRATION (gates, budgets, splits, arms, statistics); (Class 2) evidence-claim changes -- promoting a claim beyond its tag, changing headline framing, adding unprotocoled comparisons; (Class 3) scope changes -- de-scoping or deferring approved work. STOP, surface with the template phrasing ("This would change ...: [what]. Should I proceed?"), WAIT. Anti-pattern signals: "it is just a small change", "I will mention it in the retrospective", "we are running out of time, I will defer Z".
8. **If Phase 1 was skipped for a sprint, STOP and return to it** before any Phase 4 work.

## Phase detail (adaptations from the source; consult spamfilter's doc for rationale history)

### Phase 1: Backlog Refinement (mandatory, every sprint)
- 1.1 Read ALL_SPRINTS_MASTER_PLAN.md and repo-root CHECKLIST.md; identify stale/obsolete items; re-prioritize.
- 1.2 Present candidates in the BACKLOG_REFINEMENT.md "Backlog Presentation Format" -- Summary Index first, `**<ID>. <Title> (~<effort>) Priority <N>**` items, phase-group headers, HOLD one-liners, no grid tables, real registered IDs (F#/Issue #N). Read the format section in the same turn before producing it.
- 1.3 Record selection; update master plan; commit.

### Phase 2: Sprint Pre-Kickoff
- 2.2 Previous sprint PR merged to develop (`git log origin/develop --oneline -1`). Branch retention: NEVER delete sprint branches, local or remote.
- 2.3 Previous sprint's GitHub issues all closed (`gh issue list --label sprint --state open`); `Closes #N` does NOT fire on feature->develop merges, so close manually.
- 2.4 Working tree clean. 2.5 develop current.
- 2.6 Dependency check: `uv pip list --outdated` scan; security-relevant bumps become scope or backlog items.

### Phase 3: Kickoff & Planning
- 3.2.1 **Three-doc rule, no exceptions**: every completed sprint has SPRINT_N_PLAN.md, SPRINT_N_RETROSPECTIVE.md, AND SPRINT_N_SUMMARY.md. The summary is created during Sprint N+1 planning (sources: retrospective, git history, PR; never the already-rolled master plan) and its absence blocks close-out.
- 3.2.2 Plan doc with objective, tasks, acceptance criteria (quantifiable), risk, estimates in MINUTES.
- 3.2.2.1 **Plan-to-branch-state verification**: before committing the plan, verify each task against the repo (artifact exists? already shipped? cited paths current?). 3.2.2.2 Re-estimate after findings.
- 3.3 Branch `feature/YYYYMMDD_Sprint_N` -- normally ALREADY CREATED by the previous sprint's 6.6 carry-forward; verify, do not duplicate.
- 3.3.1 **Draft PR immediately after the plan is drafted, before approval. The PR STAYS DRAFT through Phase 7.7.** Draft status suppresses Copilot per-commit reviews; marking ready early = review noise on every push. `gh pr ready` happens at exactly one place: end of 7.7.
- 3.4 One GitHub issue per task (`sprint` label), created in the SAME turn as approval acknowledgment, before any task file is touched. 3.4.1 Verify each issue is still real. 3.5 All cards OPEN.
- 3.7 Explicit approval; update PR body to approved plan (keep draft).

### Phase 4: Execution
- Tasks in plan order; `pytest experiments/src -q` after each change; commit referencing the issue (`#N`).
- `git status --short` before every staging; account for every entry. Team-lead working files (`0*` at root) are EXPECTED to change and be committed with a neutral message; never read, paraphrase, or exclude them.
- Never edit build/config inputs while a long-running background job depends on them.
- Results discipline: every metric lands in results.json with its evidence tag before being cited anywhere.

### Phase 5: Review & Validation
- Full test suite; verify no frozen-protocol drift (metrics/analysis code changes since `prereg-freeze` tag are amendments).
- **Evidence-generating steps invalidate their own verification (Sprint 4 retro improvement 2)**: any checklist walk, memo, gate report, or summary is generated AFTER the last piece of evidence lands, never before. A verification artifact written mid-campaign is stale by construction and must be regenerated, not referenced. (Sprint 4 escape: the statistical checklist walk asserted "no hardware run" and "no temporal cells" against 27 hardware rows.)
- **External-review pass on major evidence documents (Sprint 4 retro improvement 6)**: before any results memo, gate report, or external-facing document reaches the team lead, run the fresh-context review of improvement 6 over the DOCUMENT as well as the raw evidence. Sprint 4's memo review found 3 numeric errors and 4 overclaims that the authoring session did not see.
- **Fresh-eyes evidence review (Sprint 3 retro improvement 6)**: before the validation handoff, a fresh-context reviewer (subagent or fresh session with NO campaign context) reads the raw results.json / gate_report with an open prompt ("describe; any useful observations?"); findings attach to the validation package. Rationale: the invested session knows what the numbers are supposed to mean; fresh context describes what is actually there (this mechanism, via the Claude Windows app, caught the Sprint 3 score degeneracy).
- **Plain-language companion is a DELIVERABLE, not a response (Sprint 3 improvement 4, strengthened Sprint 4 improvement 4)**: every validation package item and every external-facing document ships with its plain-terms version WRITTEN AT THE SAME TIME as the technical version. If the team lead has to ask for a plain-language explanation, it was owed earlier.
- Walk the sprint plan's acceptance criteria line by line with evidence (invariant 4).
- Hand deliverables to the team lead for manual validation; from here on, questions are correct.

### Phase 6: Push & Finalize PR
- 6.3 Update the existing draft PR (never create a second). 6.5 interim status to the team lead, NOT "ready".
- 6.6 **Carry-forward**: on merge notification, immediately `git checkout -b feature/<date>_Sprint_<N+1>` FROM the current feature branch; commit post-merge work there; push. NEVER stash to carry forward; never branch from develop after the merge (loses uncommitted work; the recovery is cherry-pick onto a develop-cut branch and reset the merged branch to its pushed head).

### Phase 7: Retrospective (mandatory before merge-ready)
- Follow SPRINT_RETROSPECTIVE.md's 7-step protocol: prompt to team lead -> Claude drafts its role's feedback in parallel (`docs/sprints/drafts/`) -> record team lead's words verbatim -> combine and display -> propose improvements (Title/Source/Type/Effort/Recommendation) -> team lead disposes each (now/backlog/skip) -> apply now-items as commits, backlog-items to master plan.
- Exit gate: 16 categories x 4 roles, no placeholders; Category 13 feeds Sprint N+1's plan; Category 14 feeds the master plan.
- End of 7.7: `gh pr ready` (the only place). 7.7.5 final gate: manual validation + retro + improvements + Copilot review all complete -> notify team lead for final approval.
- **Requesting the Copilot review**: `gh pr edit --add-reviewer Copilot` and the REST call SILENTLY fail (success output, reviewer never attaches). Working path: team lead signs into the automation browser once, then check Copilot under the PR's Reviewers gear in the web UI. Always verify with `gh pr view <N> --json reviewRequests` or the PR timeline ("Copilot started reviewing") before reporting it requested.
- Update `.claude/sprint_status.json` `current_sprint.status` at every phase transition (it is how future tooling knows which side of the auto-advance window applies).

### Phase 8: Delivery Cycle (after every merge to develop)
- 8.1 Team lead merges develop -> main (do not wait on it; do not block Refinement Pass 1 on it).
- 8.2 **Refinement Pass 1, completeness sweep**: verify cards closed, docs triad exists, master plan rolled, sprint_status current, shipped items pruned. Corrections only; NEVER selects scope.
- 8.3 **Submission-artifact refresh** (replaces the Store release): if the sprint changed anything the outward artifacts depend on, refresh them now -- QCi letter numbers vs the frozen grid, requirements-matrix statuses, paper-draft numbers vs results.json. At Stage 7-8 of the master timeline this step becomes the confidentiality scan + submission itself, which requires the main merge as its precondition.
- 8.4 **Refinement Pass 2, scope selection**: present the slate per BACKLOG_REFINEMENT.md; the team lead selects; feed Phase 3.

## Standing hardware rule (restated because it overrides everything)

All development on the classical proxy. Every metered Dirac-3 run: explicit approval, call count and expected seconds stated first, retries per the frozen protocol (max 2, reported), results to results.json with [HW] tags.
