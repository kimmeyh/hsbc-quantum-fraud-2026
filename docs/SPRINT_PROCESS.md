# Sprint Process (one-page overlay)

As of 2026-08-30 the full sprint execution doc set is adapted from spamfilter-multi and is authoritative: **SPRINT_EXECUTION_WORKFLOW.md** (phases 1-8), **SPRINT_CHECKLIST.md** (per-boundary single-pager), **SPRINT_STOPPING_CRITERIA.md**, **SPRINT_RETROSPECTIVE.md** (14x4 protocol), **BACKLOG_REFINEMENT.md** (two passes + presentation format), **ALL_SPRINTS_MASTER_PLAN.md** (backlog + history). This page keeps only the always-loaded essentials.

## Branch and push model

```
main      (stable; team lead merges develop -> main during Phase 8)
  ^
develop   (integration + repository default; every sprint PR targets it)
  ^
feature/YYYYMMDD_Sprint_N   (one branch per sprint; DRAFT PR from creation; ready only at Phase 7.7)
```

**Carry-forward (workflow 6.6):** on PR-merge notification, create the next sprint branch FROM the just-merged branch's head, never from develop; commit post-merge work there; never stash; recovery is cherry-pick. Sprint branches are never deleted.

Remote: private (kimmeyh/hsbc-quantum-fraud-2026) until the Stage 7 confidentiality scan; the public reproducibility package publishes separately.

## The window and the override

Auto-advance (no permission-asking) runs from Phase 3.7 plan approval to the start of Phase 5 team-lead validation. **Criterion H overrides it always: every metered Dirac-3 run stops for explicit approval with call count and expected seconds stated.**

## Decision classes (never covered by sprint approval)

1. Frozen-preregistration amendments (gates, budgets, splits, arms, statistics).
2. Evidence-claim changes (beyond-tag promotion, headline reframing, unprotocoled comparisons).
3. Scope changes (de-scoping/deferring approved work).
Surface with the template phrasing; wait.

## Standing rules

- `--no-verify` is banned; the pre-commit confidentiality hook stays active.
- Repo-root `CHECKLIST.md` is the submission deliverable ledger, reconciled at every sprint close; ALL_SPRINTS_MASTER_PLAN.md is the sprint-scoping view.
- Every reported number originates in results.json with an evidence tag.
- Team-lead `0*` working files at repo root: commit neutrally, never read.

## Sprint calendar (Phase 1 of the challenge)

| Sprint | Dates | Theme |
|---|---|---|
| 1 | Aug 30 (done) | Freeze and foundations |
| 2 | Sep 1-3 | Classical evidence |
| 3 | Sep 3-5 | Quantum evidence (hardware gated per block) |
| 4 | Sep 5-7 | The paper |
| 5 | Sep 7-8 | Ship |

Phase 2 of the challenge (Nov 17 - Feb 28, if selected): same process, new calendar, planned at acceptance (master plan F13).
