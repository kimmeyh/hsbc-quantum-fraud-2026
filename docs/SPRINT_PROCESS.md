# Sprint Process

Adapted 2026-08-30 from the spamfilter-multi sprint execution model (SPRINT_EXECUTION_WORKFLOW, stopping criteria, decision-class taxonomy, auto-advance rule), scaled to this project: a solo team lead plus Claude, a hard external deadline, and metered quantum hardware. `CHECKLIST.md` remains the single source of truth for tasks; sprints are how the tasks get executed and pushed.

## Branch and push model

```
main      (stable; team lead merges develop -> main at milestones: prereg-freeze, results-frozen, submitted)
  ^
develop   (integration; every sprint PR targets this)
  ^
feature/YYYYMMDD_Sprint_N   (one branch per sprint; pushed continuously; PR to develop at sprint end)
```

Remote: private GitHub repo under kimmeyh until the Stage 7 confidentiality scan; the public reproducibility package is published separately at Stage 7. `develop` is the repository default branch; every PR opens against it from a feature branch.

**Branch carry-forward rule (adopted from spamfilter-multi Phase 6.6):** immediately after being notified that a sprint PR merged to `develop`, create the NEXT sprint's branch FROM the just-merged sprint branch's head, not from `develop`. Commit any post-merge work (retro fixes, checklist reconciliation, next-sprint planning, files changed after the PR) on that new branch; it reaches `develop` through the next sprint's PR. This carries changed files forward without temporary PRs and without stranding work on a merged branch. NEVER stash to carry forward; create-branch-then-commit is the only sanctioned flow. Recovery if work was committed to the merged branch after its PR: create the next branch off `develop`, cherry-pick the stranded commits onto it, reset the merged branch to its pushed head.

## Sprint lifecycle

1. **Plan.** A short `docs/sprints/SPRINT_N_PLAN.md`: scope (checklist items pulled in), acceptance criteria, exclusions, hardware budget if any. The team lead approves the plan.
2. **Execute with auto-advance.** Plan approval is durable authorization for everything in scope. Between plan approval and validation, Claude does NOT ask permission at task or phase boundaries; it states the next action in one sentence and executes. Commits and pushes to the sprint branch are within standing approval.
3. **Validate.** Claude presents the sprint deliverables against the acceptance criteria, walking the list line by line with evidence (never "I believe I did that"). The team lead reviews.
4. **Retro (lightweight).** Three questions appended to the plan file or a short `SPRINT_N_RETRO.md`: what worked, what did not, what changes next sprint. Improvements feed the next plan.
5. **Close.** PR from the sprint branch to develop; CHECKLIST.md reconciled and committed; next sprint plan stubbed.

## Stopping criteria (the ONLY valid mid-sprint pauses)

1. All in-scope tasks complete.
2. Blocked on an external dependency (QCi grant, portal, Kaggle, team-lead-only input).
3. **Any metered Dirac-3 run.** Hardware execution ALWAYS stops for explicit approval with the call count and expected seconds stated, regardless of sprint authorization. This overrides auto-advance.
4. A decision-class change surfaces (below).
5. Critical defect invalidating prior results.
6. The team lead requests a scope change or early review.
7. Context/session limits approaching (commit and hand off cleanly).

NOT valid reasons to stop: implementation choices, approach uncertainty, single test failures, style questions. Make the best engineering judgment, document it, continue.

## Decision-class taxonomy (STOP, surface, wait)

Sprint approval authorizes tasks AS PLANNED. It never authorizes:

1. **Protocol changes** (the architecture class here): anything that would amend the frozen PREREGISTRATION: gates, budgets, splits, arms, statistics. Surface: "This would amend the frozen preregistration: [what]. Approve as a dated amendment?"
2. **Evidence-claim changes** (the development class): promoting a claim beyond its evidence tag, changing the headline framing, adding a comparison not in the protocol. Surface: "This would change what we claim: [what]. Should I proceed?"
3. **Scope changes** (the scrum class): de-scoping or deferring an approved item without a stopping criterion. Surface: "This would change the approved sprint scope: [what]. Should I proceed?"

Surface at the moment they arise; never bury a class-1/2/3 decision inside a larger change.

## Sprint calendar (Phase 1)

| Sprint | Dates | Theme | Maps to CHECKLIST |
|---|---|---|---|
| 1 | Aug 31 - Sep 1 | Freeze and foundations | Stage 2 completion: prereg freeze, metrics.py v1.1, data staging, remote + branches |
| 2 | Sep 1 - Sep 3 | Classical evidence | Stage 3: GBDT trio, G0, controls, MDE pilot, proxy CVQBoost tuning |
| 3 | Sep 3 - Sep 5 | Quantum evidence | Stage 3: frozen configs, hardware blocks (each gated), QFE/H6, results.json |
| 4 | Sep 5 - Sep 7 | The paper | Stages 4-6: outline, draft V1, adversarial reviews, V3 |
| 5 | Sep 7 - Sep 8 | Ship | Stages 7-8: verification, confidentiality scan, compliance walk, submit |

Phase 2 (if selected, Nov 17 - Feb 28): same lifecycle, new calendar, added to this file at acceptance.

## Standing rules that survive every sprint

- Dirac-3 metered runs: explicit approval each time (stopping criterion 3).
- The pre-commit confidentiality hook stays active; never bypass it (`--no-verify` is banned).
- CHECKLIST.md reconciled at every sprint close; `git log CHECKLIST.md` is the project journal.
- Every result lands in results.json with its evidence tag before it is cited anywhere.
