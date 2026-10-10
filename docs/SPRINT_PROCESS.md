# Sprint Process (one-page overlay)

As of 2026-08-30 the full sprint execution doc set is adapted from spamfilter-multi and is authoritative: **SPRINT_EXECUTION_WORKFLOW.md** (phases 1-8), **SPRINT_CHECKLIST.md** (per-boundary single-pager), **SPRINT_STOPPING_CRITERIA.md**, **SPRINT_RETROSPECTIVE.md** (16x4 protocol), **BACKLOG_REFINEMENT.md** (two passes + presentation format), **ALL_SPRINTS_MASTER_PLAN.md** (backlog + history). This page keeps only the always-loaded essentials.

## Branch and push model

```
main      (stable; team lead merges develop -> main during Phase 8)
  ^
develop   (integration + repository default; every sprint PR targets it)
  ^
feature/YYYYMMDD_Sprint_N   (one branch per sprint; DRAFT PR from creation; ready only at Phase 7.7)
```

**Merges are team-lead-only, at every level** (clarified 2026-08-30): Claude never merges any PR -- feature to develop included. Claude's responsibility ends at ready-for-review plus notification; the team lead merges and says when done.

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
- Repo-root `CHECKLIST-Phase2-pre.md` is the submission deliverable ledger, reconciled at every sprint close; ALL_SPRINTS_MASTER_PLAN.md is the sprint-scoping view.
- Every reported number originates in results.json with an evidence tag.
- Team-lead `0*` working files at repo root: commit neutrally, never read.

## Sprint calendar (Phase 1 of the challenge)

| Sprint | Dates | Theme |
|---|---|---|
| 1 | Aug 30 (done) | Freeze and foundations |
| 2 | Aug 31 - Sep 1 (done) | Process foundations and external readiness |
| 3 | Sep 2-3 (done) | Classical evidence |
| 4 | Sep 3-5 | Proxy tuning, baseline research, first hardware blocks, results memo |
| 5 | Sep 5-7 | The paper (draft V1, reviews) + QCi draft package |
| 6 | Sep 7-9 | IEEE-CIS evidence + paper updates + F4/F5 prep |
| 7 | Sep 9-11 | QFE evidence + paper updates |
| 8 | Sep 11-12 | SPECTRA replication (or fallback) + paper updates |
| Finalize | Sep 12-13 | CI, verification, confidentiality scan, submission (evidence freeze Sep 12; never later than Sep 14) |

Keep this table reconciled with ALL_SPRINTS_MASTER_PLAN.md at every sprint close; the master plan wins on scope, this table only mirrors it.

Phase 2 of the challenge (Nov 17 - Feb 28, if selected): same process, new calendar, planned at acceptance (master plan F13).
