# Sprint 3 Plan: Classical Evidence Campaign

Dates: Sep 2-4, 2026. Branch: `feature/20260902_Sprint_3` (carried forward from Sprint 2's head). PR target: `develop` (DRAFT until Phase 7.7).
Status: AWAITING TEAM-LEAD APPROVAL.
Scope defined by the team lead 2026-09-02 (defined-scope rule: this list is complete; nothing additive): **F1 + F18**.

## Objective

Produce the classical evidence base the submission stands on: tuned GBDT baselines with G0 scored as committed, the CVQBoost proxy pipeline (structural control), the A3 build side-by-side, and a fully prepared (not executed) first hardware request — with F18's Dirac-3 notes mined first so hardware discipline is hardened before any request is drafted.

## Tasks

### Task A / F18: Complete the Dirac-3 notes mining (~60m)

Remaining 8 checklist items from the master plan entry (variable-count math and QSVM augmentation already done). Highest value: free-tier backoff pattern reconciled with the frozen retry-twice rule; credentials pattern into ADR-0011 practice; constructor-knob cross-check vs the frozen FourierWall2-derived config; H3 ladder low-rung check (k=5 -> schedule interaction).

- **Acceptance criteria**: all 10 checklist boxes checked in the master plan; findings memo at `docs/sprints/drafts/F18_dirac3_notes_findings.md` with an adopt/amend/reject disposition per item; zero amendments applied without team-lead approval; zero metered seconds.
- **Estimate**: 60m. **Model**: top tier (protocol-adjacent analysis). **Owner**: Claude.

### Task B / F1: Classical evidence campaign (~1.5 days wall, much of it unattended Optuna time)

Ordered sub-tasks; long runs execute in the background while later sub-tasks proceed.

1. **B1 Tuning harness + runs (~90m build, ~4-8h unattended)**: extend `tune.py` to the frozen spec -- XGB/LGBM/CatBoost x 100 Optuna trials each, full and matched (top-13 MI) features, class-weighting only, val-AP objective, per-seed refit of the best config across seeds {42..51}. Known-failure header; frd.* logging; checkpointed so a killed run resumes.
2. **B2 Logistic control (~20m)**: same splits/features, 10 seeds.
3. **B3 results.json writer (~45m)**: every row per the section 11 schema (arm, dataset, protocol, seed, config_hash, features_used, metrics, evidence_tag [SIM], metered_seconds=0, retry_count, timestamps); BCa CIs + across-seed t-intervals via frozen metrics.py.
4. **B4 Gate scoring (~40m)**: G0 scored as committed (tuned-XGB mean AP >= 0.85); Tuning Budget Equivalence table; measured paired-delta SD with the preregistered MDE-refinement decision surfaced to the team lead (amendment candidate, not auto-applied).
5. **B5 CVQBoost proxy pipeline (~2h)**: weak pools (dct/lg/knn/lda/shallow-xgb per frozen config), QUBO build (J, C), non-negative ridge solve = ADR-0002 structural control; free-tier (top-13, schedule 2, 78 vars) and full (top-17, schedule 3, 816 vars) configs materialized with config hashes.
6. **B6 A3 side-by-side (~60m + WSL setup [no-history], timebox 60m)**: capability pre-flight FIRST (see below); full-pair pool built under WSL2, sequential pool on Windows, identical data/seeds; proxy validation AP across the 10 primary seeds; build selected per A3 BEFORE any test-set evaluation; `pair_build` recorded in every affected results.json row.
7. **B7 Hardware request PREPARED, not executed (~30m)**: B1 free-tier block + G0b fidelity block as a written request: per-block call counts, expected metered seconds (26-34 s/fit basis), config hashes, seed lists. Execution waits for explicit per-block team-lead approval (Criterion H).
8. **Inline additions from the approved disposition (~4.5h, interleaved)**: ADRs 0005-0010 authored as their modules are built; logging conventions (frd.* namespaces); full-pipeline smoke fixture; ARCHITECTURE.md with ADR cross-references; TESTING_STRATEGY.md adaptation; known-failure headers on long-running scripts; velocity actuals log started; block-stash + closeout-verify hooks ported.

- **Acceptance criteria (quantifiable)**: results.json contains >= 90 [SIM] rows (4 classical arms x {full, matched} x 10 seeds + logistic + proxy-CVQBoost rows), every row schema-complete; G0 gate row scored with its evidence tag; A3 comparison table (2 builds x 10 seeds, mean validation AP each) and the selection recorded; hardware request document exists with call counts; all tests green including new known-answer tests for the tuning objective and QUBO build; velocity log has an actual for every sub-task; zero metered seconds spent.
- **Estimates**: above, in minutes; Optuna wall time unattended. **Model**: top tier for statistics/ADRs/QUBO; Sonnet subagents permitted for scripted implementation (B1/B2 harness code) per the planning table. **Owner**: Claude.

## Capability pre-flights (before estimates bind)

- **WSL2 eqc-models fork spike (~5m, gates B6)**: inside WSL, a venv with eqc-models imports `QBoostClassifier`, builds a multi_processing weak pool on 100 synthetic rows (NO Dirac call; local weak-learner training only). Failure -> B6 re-scoped to [Blocked], A3 comparison deferred, sprint proceeds sequential-only.
- **Optuna objective smoke (~5m, gates B1)**: 2-trial run end-to-end on 5k ULB rows.

## Explicitly out of scope

Any metered Dirac-3 execution (B7 prepares only; Criterion H stands); F2/F3/F4/F5 work; IEEE-CIS feature engineering; QFE arms; paper drafting; the pilot_variance.py amendment decision (open with the team lead, not blocking).

## Risks

- **Hardware budget**: zero-spend sprint by design; the only hardware artifact is a written request. Mitigation: Criterion H + B7 wording.
- **Leakage**: matched features via MI on train only (frozen rule); shuffled-label positive control deferred to F3 (IEEE-CIS) per prereg scoping; G0 band (0.85-0.88) itself flags leakage (>0.95).
- **Deadline**: Optuna wall time is the critical path; runs start the moment B1 code passes its smoke and run overnight if needed. Sep 8 target holds with Sprint 4 starting Sep 4.
- **Grant timing**: unaffected; nothing here waits on QCi.
- **Session continuity**: checkpointed tuning + results.json appends; sprint_status updated at each phase transition.

## Estimate total

~7h attended + 4-8h unattended Optuna + 60m timeboxed WSL setup. Velocity actuals recorded per sub-task (first calibrated sprint).
