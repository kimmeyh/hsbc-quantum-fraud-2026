# Sprint 4 Plan: Proxy Tuning, Baseline Research, First Hardware Blocks, Results Memo

Dates: Sep 3-5, 2026. Branch: `feature/20260903_Sprint_4` (carried forward from Sprint 3's head). PR target: `develop` (PR #21, DRAFT until Phase 7.7). Cards: #17 (A), #18 (B), #19 (C), #20 (D).
Status: APPROVED by the team lead 2026-09-03 ("Sprint 4 plan approved as recommended. All Sprint tasks and sub-tasks are approved.").
Scope defined by the team lead (defined-scope rule; F19 moved to the end of Sprint 5): **F22 + F21 + F2 + F7**.

## Objective

Make the quantum arm real: tune CVQBoost on the proxy per the frozen section-6 protocol (fixing the score degeneracy and producing the G0b config ranking), research the ULB baseline-protocol gap behind G0, run the first hardware blocks on per-block approval, and close with the one-page results memo and gate review that Sprint 5's paper draft will be written from.

## Tasks

### Task A / F22 (#17): CVQBoost proxy tuning per prereg section 6 (~3h attended + unattended solves)

1. **A1 Amendment A6 -- score-health flags (~20m)**: `metrics.summarize` gains `score_health` (n_distinct scores, mode share, WARN when mode share > 0.90 or n_distinct < 50) with a known-answer test; registered as analysis-code amendment A6 (retro improvement 1).
2. **A2 Tuning harness (~90m build; ~2-4h unattended)**: `tune_proxy.py`, run under WSL with the A3-selected full-pair build (fork-based pool builds are seconds, not minutes). Optuna TPE, 100 trials, objective = validation AP on the tuning-seed (42) split. Search space per section 6: weak pool composition (weak_cls_type in {dct, lg, lda, xgb-shallow}; class_weight in {None, balanced} where supported; dct max_depth in {1,2,3}), schedule in {1,2,3}, k in {5,9,13,17}, lambda alpha in {0.5,1,2,4} x n_train; (k, schedule) pairs above the 949-variable ceiling pruned; num_samples/relaxation_schedule fixed. Pool builds cached per (k, schedule, weak config) so lambda trials reuse H matrices. KNN weak learners EXCLUDED on proxy-cost grounds (O(n^2) prediction over 170k rows per learner) and reported as a tuning-space deviation.
3. **A3 Tuned refits (~40m)**: best free-tier-eligible config (<= 100 vars) and best overall config refit on the 10 primary seeds -> `cvqboost_proxy` rows tagged `tuned_free` / `tuned_full` with health flags; lg pools return to tables only if a tuned lg config passes the health check.
4. **A4 Config ranking + hardware request update (~20m)**: ranking table (val AP per config, config hashes); G0b list = top-3 + bottom-2 among free-tier-eligible configs; HARDWARE_REQUEST_B1_G0b.md updated with exact hashes and counts; gate_report regenerated.

- **Acceptance**: tuning record with 100 completed trials; >= 20 tuned proxy rows carrying `score_health`; no health WARN on the selected configs, or the residual degeneracy explicitly reported with an amendment candidate (surfaced, never applied); ranking table + G0b list written; tests green (16+); zero metered seconds.
- **Model**: top tier (protocol-touching). **Owner**: Claude.

### Task B / F21 (#18): Baseline-protocol research (~2h)

Primary-source research on published ULB methodology: exact-duplicate handling in strong baselines (which papers retain or remove, cited), leakage-free feature engineering (Amount/Time transforms, interactions), and which protocol differences explain the 0.85-0.88 literature band vs our 0.8296.

- **Acceptance**: `docs/research-ulb-baseline-protocols.md` with linked sources, a findings table, and a recommended amendment proposal (or a reasoned "no amendment") for team-lead disposition at validation; nothing applied to the frozen protocol.
- **Model**: top tier (research is top-tier mandatory). **Owner**: Claude.

### Task C / F2 (#19): Hardware campaign, first blocks (Criterion H)

After A4, present the block request (B1: 22 calls ~90-140 QPU s; G0b: 5 calls ~20-35 s) with exact config hashes and seed lists, then STOP for per-block team-lead approval (Criterion H overrides the auto-advance window). On approval: execute from WSL (full-pair build), one metered call per fit, frozen retry rule (identical config, max 2 retries, counts recorded), [HW] rows into results.json via the shared store with `metered_seconds` from the response.

- **Acceptance**: request presented with exact counts; approved blocks produce schema-complete [HW] rows; G0b scored (Spearman >= 0.5) if run; unapproved blocks stand ready and are reported [PROJ] in the memo.
- **Model**: top tier. **Owner**: Claude executes; team lead approves.

### Task D / F7 (#20): Results memo + gate review (~2h)

One-page `docs/RESULTS_MEMO.md`: gate table scored as committed (G0 FAIL with protocol context; G0b if run; H1b machinery status with the paired-delta CI and the A5 MDE; A3 selection), per-arm summary with prevalence beside every AUPRC, evidence tags on every number, and the headline-framing OPTIONS for the Class-2 decision the team lead makes at validation (no framing chosen unilaterally).

- **Acceptance**: memo exists; every number traces to results.json/gate_report by config_hash; framing options listed with evidence tags; STATISTICAL_REVIEW_CHECKLIST walked line by line.
- **Model**: top tier. **Owner**: Claude drafts; team lead decides framing.

## Capability pre-flights

- WSL tuning smoke: 2 Optuna trials end-to-end under WSL before the 100-trial launch (~5m).
- Health-check known-answer test green before any tuned row is written.

## Explicitly out of scope

F19 (Sprint 5 end), F3/F4/F5/F23/F24, paper drafting (F8), any metered run without a per-block approval, any change to gates/budgets/splits.

## Risks

- **Hardware**: Criterion H stop before every block; hold recommendation stands until A4 completes.
- **Degeneracy may survive the frozen lambda grid**: report with evidence, propose an amendment, never patch ad hoc.
- **Compute**: 100 pool builds, mitigated by WSL fork builds and H-matrix caching.
- **Usage limits**: no multi-agent review passes mid-sprint (Sprint 3 lesson); every long job checkpointed.
- **Deadline**: the memo closes the sprint by Sep 5 so Sprint 5 drafts the paper on schedule.

## Estimate total

~7.5h attended + 2-4h unattended tuning; hardware time only on approval.
