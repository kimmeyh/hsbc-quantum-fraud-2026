# Sprint 3 Summary: Classical Evidence Campaign

Archival record (three-doc rule). Dates: Sep 2-3, 2026. Branch `feature/20260902_Sprint_3` (carried forward from Sprint 2's head); PR #13 merged to develop 2026-09-03; develop merged to main via PR #16. Sources: SPRINT_3_PLAN.md, SPRINT_3_RETROSPECTIVE.md, gate_report.md, git history, PR #13.

## Objective

Produce the classical evidence base the submission stands on (tuned GBDT baselines with G0 scored as committed, the CVQBoost proxy pipeline, the A3 build side-by-side, a prepared hardware request), with F18's Dirac-3 notes mined first. Scope: F1 + F18 (defined-scope rule).

## Delivered

1. **F18 Dirac-3 notes mined**: 10 dispositions, zero amendments required; config-mutating backoff rejected (frozen identical-config retry rule preserved); new pipeline invariants adopted (label map, explicit sequential strategy, constructed-attribute round-trip assert, n<4 guard, credentials pattern).
2. **F1 classical evidence campaign, 110 [SIM] rows**: 4 arms x {full, matched-13} x 10 seeds (80) + 30 proxy rows. Tuning: 8 Optuna studies at the frozen budgets (CatBoost/full best CV AP 0.8580). **G0 scored as committed: FAIL** (tuned-XGB full mean test AP 0.8296, CI [0.8092, 0.8501], vs 0.85 floor); best arm overall CatBoost/full 0.8368; no leakage flag. Dedupe-before-split removed 1,081 rows (recorded in meta).
3. **CVQBoost proxy pipeline**: eqc-models-native pools, exact Hamiltonian replication (J=HH^T+lambda*I, C=-2Hy, simplex), FISTA solve verified vs SLSQP; 4 new known-answer tests (15 total). Paired proxy-vs-best-GBDT delta -0.0415 [CI -0.0608, -0.0222]; measured paired MDE(10) 0.0268.
4. **A3 side-by-side**: full-pair build (WSL2) selected on validation AP (0.7816 vs 0.7803, inside noise; rule deterministic); dct pools ~0.77 vs lg ~0.56 test AP.
5. **Validation findings**: lg proxy scoring degenerate (99.8% identical scores) -> quarantined from tables; dct tie caveat noted; root cause = frozen lambda=2*n_train (SPECTRA-calibrated) + unweighted weak learners on 0.17% positives; fix path = preregistered section-6 proxy tuning (F22). Caught via a fresh-context review of results.json (team lead, Claude Windows app).
6. **Amendments**: A4 (Sprint 3 analysis-code registration; tune.py left frozen after the suspected LightGBM bug proved to be the pinned API), A5 (MDE refined to measured 0.0268, team-lead approved).
7. **B7 hardware request prepared, NOT executed**: B1 22 calls ~90-140 QPU s + G0b 5 calls ~20-35 s; hold recommended until F22.
8. **Infrastructure**: ADRs 0005-0010 accepted (system complete 0001-0011); ARCHITECTURE.md, TESTING_STRATEGY.md, VELOCITY_LOG.md; spamfilter hooks ported (stash block, close-out verify) and payload-tested; gate-scoring aggregator; shared results-store module (review fix).
9. **Backlog registered mid-sprint**: F19 (QCi draft PDFs), F20 (soft-vote CVQBoost, HOLD), F21 (baseline-protocol research), F22 (proxy tuning; blocks G0b).
10. **Reviews**: Copilot 4 findings fixed and resolved; Claude review's one confirmed finding fixed (its full run was lost twice to a stall and a usage limit -- retro lesson: exclude the evidence store from review scope).

## Estimated vs actual

Authored work ran 0.45-0.7 of estimate (velocity log now 12 rows); unattended compute ~4.3 h of tuning + ~1.5 h refits; one refit relaunch (checkpoint-key fix). Zero metered seconds.

## Key decisions

- G0 FAIL reported as committed; headline framing deferred to F7 gate review (Class 2). Team-lead question answered: the 13-column matching is NOT the cause (G0 scores the full-feature arm).
- MDE amended to measured value (A5). Both B1 pool variants kept. Full-pair build stands per the A3 rule.
- Retro improvements 1-6 approved as recommended and applied (1 recorded into F22).

## Hardware

Zero metered seconds.

## Links

PR #13 (merged), PR #16 (develop->main), issues #14 #15 (closed), docs/sprints/SPRINT_3_PLAN.md, docs/sprints/SPRINT_3_RETROSPECTIVE.md, experiments/results/gate_report.md, docs/HARDWARE_REQUEST_B1_G0b.md.
