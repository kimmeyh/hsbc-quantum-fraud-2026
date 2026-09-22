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
| **CHECKLIST-Phase2-pre.md** (repo root) | The submission-wide task ledger (Phase 1 deliverable map) |
| **experiments/PREREGISTRATION.md** | FROZEN protocol; amendment discipline overrides everything here |

## Phase Cheat Sheet

Consult this line at the START and END of every phase; state which steps were done. Crossing a boundary by "just doing the next work" is how steps get missed.

| Phase | Top actions | Done when |
|---|---|---|
| **1. Backlog Refinement** | MANDATORY every sprint, no request needed. Read master plan + CHECKLIST-Phase2-pre.md; present candidates in BACKLOG_REFINEMENT.md format (read its format section IN THE SAME TURN first); capture selection | Team lead has picked items; no scope questions open |
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
   - **A repeated instruction means MY READING is wrong, not the instruction (Sprint 10 improvement 5).** If the team lead issues an instruction I believe I have already satisfied, do not execute the same interpretation again. State the reading back in one sentence and act on the other plausible reading. Sprint 10: "continue until backlog refinement" was given three times and answered three times by stopping BEFORE refinement, when it meant THROUGH it. Three identical results from three identical instructions is the signal.
6. **Read the format doc before producing its output**: retrospective template, backlog presentation format, plan template. Mirror exactly; never reproduce from memory.
7. **Decision-Class Checkpoint Protocol**: sprint-plan approval is NOT authorization for (Class 1) protocol changes -- anything amending the frozen PREREGISTRATION (gates, budgets, splits, arms, statistics); (Class 2) evidence-claim changes -- promoting a claim beyond its tag, changing headline framing, adding unprotocoled comparisons; (Class 3) scope changes -- de-scoping or deferring approved work. STOP, surface with the template phrasing ("This would change ...: [what]. Should I proceed?"), WAIT. Anti-pattern signals: "it is just a small change", "I will mention it in the retrospective", "we are running out of time, I will defer Z".
8. **(Class 4) SUBMISSION-DOCUMENT CHANGES require Product Owner approval BEFORE the edit** (team lead, 2026-09-12). Any change to `docs/paper/proposal.md`, `docs/paper/appendix.md` or `docs/paper/team_profile.md` -- and therefore to their PDFs -- is presented for approval first, never applied and reported. Present each proposed change as: **text before / text after / pros / cons / recommendation and why**. One message may carry several changes; a blanket approval ("all as recommended") is acceptable and is the team lead's to give, not Claude's to assume. This is Class 1-3's stopping discipline applied to the artifacts that are actually submitted: by Sprint 12 the documents had become the product, and edits to them were still being made at the speed of edits to code.
   - **A list presented for approval contains ONLY items you want changed (Sprint 13 improvement 1).** A recommendation to take NO action never appears as a numbered peer in that list; it goes in a separate section headed "Recommend no action". In Sprint 13 six findings were presented for approval and item 5 carried a recommendation to LEAVE it alone. The team lead approved all six, reasonably reading them as six fixes, and the unwanted change had to be backed out. The ambiguity was in the presentation, not the decision. Where an item could be read either way, say which it is in words: "this is a fix I want approved" or "this is a recommendation to take no action".
9. **VERIFY BEFORE AMENDING** (team lead, 2026-09-11). A review finding -- internal or external, from a person or a model -- is NOT actionable until independently verified against the code or the artifact it describes. Corrections to the frozen preregistration are BATCHED behind a completed analysis of the whole review; never write an amendment in response to a single finding while the review is still arriving.
   - **A verified finding is still bounded by the repository.** This repository's sessions NEVER write to `spamfilter-multi` or `EvidenceBasedDB`; reading them on request is fine (team lead, 2026-09-15). A review that examines a sibling repository produces INFORMATION for that repository, not a work order this session may execute. Report the file, the line and the fix, and hand it over; the change lands there through that repository's own review and tests. This happened in Sprint 14: a review of PR #97 also examined EvidenceBasedDB and the findings were fixed, committed and pushed there directly. The findings were real, and the changes still arrived with no review, no sprint record and no chance for the team lead to see them as a PR.
   - **This rule exists because the failure happened.** In Sprint 12 a reviewer's finding was accepted and a correction published within hours; the correction itself was false (the convexity claim, withdrawn in A27), and two independent external reviews caught it the same day. Amending under time pressure reproduced the exact defect class the amendment protocol exists to record. The team lead's intervention -- stop, analyze both reviews in full, address findings through planned sprint cards -- is what broke the loop.
   - Corollary: **correcting a document does not correct its generator.** When an amendment corrects a claim, check the code that produces that claim's evidence. F60 fixed a device-versus-pool conflation in the prose; the generator behind it carried the identical bug for another day until a PR review found it.
10. **If Phase 1 was skipped for a sprint, STOP and return to it** before any Phase 4 work.

## Phase detail (adaptations from the source; consult spamfilter's doc for rationale history)

### Phase 1: Backlog Refinement (mandatory, every sprint)
- 1.1 Read ALL_SPRINTS_MASTER_PLAN.md and repo-root CHECKLIST-Phase2-pre.md; identify stale/obsolete items; re-prioritize.
- 1.2 Present candidates in the BACKLOG_REFINEMENT.md "Backlog Presentation Format" -- Summary Index first, `**<ID>. <Title> (~<effort>) Priority <N>**` items, phase-group headers, HOLD one-liners, no grid tables, real registered IDs (F#/Issue #N). Read the format section in the same turn before producing it.
- 1.3 Record selection; update master plan; commit.

### Phase 2: Sprint Pre-Kickoff
- 2.2 Previous sprint PR merged to develop (`git log origin/develop --oneline -1`). Branch retention: NEVER delete sprint branches, local or remote.
- 2.3 Previous sprint's GitHub issues all closed (`gh issue list --label sprint --state open`); `Closes #N` does NOT fire on feature->develop merges, so close manually.
- 2.4 Working tree clean. 2.5 develop current.
- 2.6 Dependency check: `uv pip list --outdated` scan; security-relevant bumps become scope or backlog items.

### Phase 3: Kickoff & Planning
- 3.2.1 **Three-doc rule, no exceptions**: every completed sprint has SPRINT_N_PLAN.md, SPRINT_N_RETROSPECTIVE.md, AND SPRINT_N_SUMMARY.md. The summary is created during Sprint N+1 planning (sources: retrospective, git history, PR; never the already-rolled master plan) and its absence blocks close-out.
- 3.2.2 Plan doc with objective, tasks, acceptance criteria (quantifiable), risk, estimates in MINUTES. **The sprint total is DERIVED from the card estimates and their dependencies and RECORDED first; the plan reports that number rather than originating one** (SPRINT_PLANNING.md, Sprint 17 improvement 1). A total typed straight into the plan was wrong in two consecutive sprints.
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
  - **Both clauses are hook-enforced** (`.claude/hooks/`): `block-carry-forward-stash.ps1` blocks `git stash`, `block-branch-from-develop.ps1` blocks a `checkout -b`/`switch -c` that names develop, main or master as the start point. Bare `git checkout -b <name>` is the prescribed form and passes; both hooks carry a sanctioned bypass token for the genuine exception.
  - **A clean result does not mean the cut was right.** At the Sprint 9 close-out the branch was cut from `origin/develop`; no commits were lost, because the merge had already carried everything and the uncommitted work followed the checkout. The violation was invisible in `git status` and surfaced only on re-reading this rule. Verify the flow, not the outcome.

### Phase 7: Retrospective (mandatory before merge-ready)
- Follow SPRINT_RETROSPECTIVE.md's 7-step protocol: prompt to team lead -> Claude drafts its role's feedback in parallel (`docs/sprints/drafts/`) -> record team lead's words verbatim -> combine and display -> propose improvements (Title/Source/Type/Effort/Recommendation) -> team lead disposes each (now/backlog/skip) -> apply now-items as commits, backlog-items to master plan.
- Exit gate: 16 categories x 4 roles, no placeholders; Category 13 feeds Sprint N+1's plan; Category 14 feeds the master plan.
- **Merge-readiness definition (team lead, 2026-09-04)**: a PR is handed to the team lead as merge-ready ONLY when EVERY review has COMPLETED and EVERY finding is addressed and its thread resolved. A review still running means the PR is not ready, no matter how clean it looks; never describe it as "yours to merge" while an agent is mid-review. State review status explicitly instead: which reviews are complete, which are running, how many findings are open.
- End of 7.7: `gh pr ready` (the only place). 7.7.5 final gate: manual validation + retro + improvements + Copilot review all complete -> notify team lead for final approval.
- **Requesting the Copilot review (CORRECTED 2026-09-12, F66).** This has three independent silent-failure modes, and the earlier note in this document recorded the workaround while misdiagnosing the cause.
  - **The actor name is `copilot-pull-request-reviewer[bot]`** (node id `BOT_kgDOCnlnWA`). NOT `Copilot`, and NOT `copilot-swe-agent`, which is a different bot. `gh pr edit --add-reviewer Copilot` reports success and attaches nothing, because it resolves a user named Copilot that does not exist on the repository.
  - **`requestedReviewers` cannot confirm a bot request.** The REST field returns USERS only, so a bot reviewer that attached correctly still reads back as an empty list. Verifying there produces a false negative every time, which is what made the first failure mode look like a second one.
  - **Verify on the TIMELINE instead**: the PR shows "Copilot started reviewing" / "Copilot reviewed", or `gh pr view <N> --comments` shows the review body. That is the only reliable confirmation.
  - **Consequence, recorded because it actually happened**: PR #73 never received a Copilot review. The request was issued, reported as successful, verified against a field that cannot show it, and nobody noticed until PR #75 was being set up. A review step that silently does not happen is worse than one that visibly fails.
  - **The working request path, verified 2026-09-14 on PR #94**: the GraphQL `requestReviews` mutation with the bot id in `botIds`, NOT `userIds`. `userIds` fails loudly with "Could not resolve to User node", which is at least honest. **The REST call fails SILENTLY**: `POST /pulls/{n}/requested_reviewers` with the bot login returns HTTP 200 and a full PR object, and attaches nothing. That is a fourth silent-failure mode beyond the three already listed.
    ```
    gh api graphql -f query='mutation($pr:ID!){requestReviews(input:{pullRequestId:$pr, botIds:["BOT_kgDOCnlnWA"], union:true}){pullRequest{number}}}' -f pr="<PR node id>"
    ```
  - **Verify with GraphQL `reviewRequests`, never REST.** REST's `requested_reviewers` showed an EMPTY array while GraphQL showed `Bot: copilot-pull-request-reviewer` attached. The timeline also showed no `review_requested` event for the bot, so the timeline check in the line above is necessary but NOT sufficient. A cross-repository skill holds the full procedure; this note exists so the workflow does not depend on that skill being loaded.
- Update `.claude/sprint_status.json` `current_sprint.status` at every phase transition (it is how future tooling knows which side of the auto-advance window applies).

### Phase 8: Delivery Cycle (after every merge to develop)
- 8.1 Team lead merges develop -> main (do not wait on it; do not block Refinement Pass 1 on it).
- 8.1.1 **CHANGELOG reconciliation, BEFORE refinement (F70, Sprint 14).** Walk the days since the last entry and write one per day with commits, sourced from git history, the sprint summaries, the amendment log and the merged PRs. A day that cannot be reconstructed with confidence says so rather than being invented.
  - **Why this step exists and why it sits here.** The policy at the top of CHANGELOG.md says entries are written in the SAME commit as the change they describe. That policy held for six days and then silently stopped: the file ran from 2026-08-29 to 2026-09-04 and then nothing, while Sprints 7 through 13 delivered the entire hardware campaign, three external reviews, the public-repository flip and the submission itself. Eight days missing, and nobody noticed for eight days.
  - A same-commit policy depends on remembering at the moment of committing, which is exactly the class of rule this workflow keeps having to replace with a step. The reconciliation is cheap when it runs every cycle and expensive once it has lapsed -- the F70 backfill cost about ninety minutes for eight days.
  - It is placed BEFORE Refinement Pass 1 deliberately: the sweep reads the sprint's own record, and a record with a hole in it is what the sweep is meant to catch.
- 8.2 **Refinement Pass 1, completeness sweep**: verify cards closed, docs triad exists, master plan rolled, sprint_status current, shipped items pruned. Corrections only; NEVER selects scope.
  - **Prune shipped cards BY HAND. Do not write a pruning script.** Sprint 8 improvement 4. An ad-hoc prune script destroyed the master plan's roadmap section TWICE -- at Sprint 7 close-out (c40038d) and again in the Sprint 8 sweep -- by walking from a card header to the next card header and consuming a `## ` section heading that fell inside the span. The second loss went unnoticed for a full sprint. Pruning is a handful of cards per cycle; the script has negative value at that volume. Delete the card block with an editor, then run `pytest experiments/src/test_row_schema.py -k master_plan` before committing.
- 8.3 **Submission-artifact refresh** (replaces the Store release): if the sprint changed anything the outward artifacts depend on, refresh them now -- QCi letter numbers vs the frozen grid, requirements-matrix statuses, paper-draft numbers vs results.json. At Stage 7-8 of the master timeline this step becomes the confidentiality scan + submission itself, which requires the main merge as its precondition.
- 8.4 **Refinement Pass 2, scope selection**: present the slate per BACKLOG_REFINEMENT.md; the team lead selects; feed Phase 3.

## Standing hardware rule (restated because it overrides everything)

All development on the classical proxy. Every metered Dirac-3 run: explicit approval, call count and expected seconds stated first, retries per the frozen protocol (max 2, reported), results to results.json with [HW] tags.
