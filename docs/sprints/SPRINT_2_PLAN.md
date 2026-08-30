# Sprint 2 Plan: Classical Evidence

Dates: Sep 1 to Sep 3, 2026. Branch: `feature/20260831_Sprint_2` (carried forward from Sprint 1's head per SPRINT_PROCESS). PR target: `develop`.
Status: AWAITING TEAM-LEAD APPROVAL.

## Scope

1. **Tuned classical arms on ULB (frozen protocol sections 6 and 8):** XGBoost, LightGBM, CatBoost at 100 Optuna TPE trials each, logistic at 25, optimizing average precision with stratified 5-fold CV on train. Protocol interpretation recorded here for transparency: the search runs once per arm on the seed-42 training split; the winning configuration is then refit on each of the 10 primary seeds' training sets (early stopping on that seed's validation fold). Both full-feature and matched-feature (top-k MI inside folds) variants. All results into results.json with stratified BCa CIs.
2. **G0 scored as committed:** mean tuned-XGBoost AP across the 10 stratified seeds against the 0.85 bar; G0c preprocessing (log-Amount, Time retained, duplicates removed).
3. **Tuning Budget Equivalence table:** trials, fits per trial, wall-clock CPU-hours per arm, recorded and committed.
4. **Paired-delta variance measurement:** per-seed paired deltas between classical arms establish the empirical paired-delta SD; if materially below the pilot's raw-variance MDE (0.0242), a dated amendment refines the MDE estimate (decision rule unchanged).
5. **CVQBoost proxy pipeline:** weak-learner pool builder (dct/lg/knn/lda/shallow-xgb over single features and pairs per schedule), QUBO construction (J, C per Emami et al. eq. 5-6), proxy solve via non-negative ridge (identical objective; doubles as the H4 structural control), 100-trial tuning budget over pool composition, schedule, k, and lambda alpha; the free-tier (top-13, schedule 2, <= 100 vars) and full (top-17, schedule 3, 833 vars) configurations FROZEN and documented with variable counts.
6. **Structural-control results** (non-negative ridge and L1 variants) on the same cells, feeding H4.
7. **Hardware request prepared, not executed:** the B1 + G0b run list with exact call counts and expected metered seconds, presented for team-lead approval at sprint close.
8. **F15 (team-lead assigned 2026-08-30): best-practices and ADR review from spamfilter-multi (~3h).** Review its ARCHITECTURE.md and docs/adr/ for (a) architecture/development/SE practices to copy and adapt here, (b) additional SE best-practice suggestions, (c) ML best practices to propose as ADRs (feature engineering, data curation, leakage prevention, training, evaluation), applied to this challenge. Output: docs/adr/ with template, initial ADRs for decisions already made, and a disposition list for the team lead.

## Explicitly out of scope

Any metered Dirac-3 execution; IEEE-CIS tuning campaigns and the Deotte recipe (Sprint 3); QFE/H6 arms and the Braket gate-based arm (Sprint 3); SPECTRA replication (Sprint 3); paper drafting (Sprint 4).

## Acceptance criteria

- [ ] results.json holds tuned XGB/LGBM/CatBoost/logistic x {full, matched} x 10 ULB stratified seeds with BCa CIs, prevalence, tie fractions, operating points, calibration
- [ ] G0 scored with evidence (pass/fail stated as committed)
- [ ] Tuning Budget Equivalence table committed
- [ ] Paired-delta SD documented with the MDE refinement decision
- [ ] CVQBoost proxy runs end-to-end; free-tier and full configs frozen with variable counts within limits
- [ ] B1 + G0b hardware request written with call counts (awaiting approval, not executed)
- [ ] PR open to develop; CHECKLIST reconciled

## Hardware budget

Zero metered seconds this sprint. The first hardware approval request is this sprint's final deliverable.

## Retro (filled at close)

- What worked:
- What did not:
- Change next sprint:
