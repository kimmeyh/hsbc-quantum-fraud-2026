# Sprint 1 Summary: Freeze and Foundations

Archival record (three-doc rule). Dates: Aug 30, 2026 (planned Aug 31 - Sep 1; completed a day early). Branch `feature/20260831_Sprint_1`; PR #1 merged to develop; develop merged to main via PR #3. Sources: SPRINT_1_PLAN.md (acceptance walk + retro), git history, PR #1.

## Objective

Make the experimental protocol binding and the infrastructure ready so the evidence campaign can start without process debt: freeze the preregistration, bring the statistics code to the frozen spec, validate every dataset, measure seed variance for the MDE statement.

## Delivered

1. **PREREGISTRATION v1.1 FROZEN**: team-lead approved; freeze commit `95751b9`; tag `prereg-freeze`; amendment A1 records the hash; analysis code frozen at the same commit.
2. **metrics.py at the v1.1 statistical spec**: stratified BCa bootstrap (2,000 resamples, block-jackknife acceleration, documented approximation), identical-index paired delta-AP, across-seed t-interval (the H1b decision rule), MDE helper, Wilson intervals, dual operating points (max-F1 + fixed alert budget), equal-mass ECE with reliability data, Brier as joint score only, tie-fraction check. 11 known-answer tests, including BCa vs scipy.stats.bootstrap and Wilson vs statsmodels.
3. **Data foundation**: loaders + validation for ULB (284,807 rows / 492 frauds), IEEE-CIS (590,540 x 434, 3.5% fraud, float32 memory fix), all four SPECTRA sets (feature counts matching the FourierWall2 variable table). SPECTRA and IEEE-CIS downloaded via Kaggle (OAuth; legacy env-var shadowing diagnosed and removed).
4. **Pilot variance [SIM]**: ULB, 10 seeds, fixed untuned XGBoost: mean AP 0.8268, seed SD 0.0243, MDE(10 seeds, alpha .05, power .80) = 0.0242 (experiments/PILOT_VARIANCE.md).
5. **Infrastructure**: private GitHub remote (kimmeyh/hsbc-quantum-fraud-2026), main/develop/feature branch model with develop default, carry-forward rule, draft-PR-per-sprint lifecycle, Copilot review instructions, pre-commit confidentiality hook (verified blocking), Kaggle CLI wired.

## Estimated vs actual

Planned 2 days; actual ~1 day of focused execution. Task-level actuals not minute-logged (velocity logging begins Sprint 2).

## Key decisions

- Freeze approved with zero content edits after the dual-model review + research adjudication (v1.1).
- MDE nuance recorded rather than papered over: raw-variance MDE is conservative; paired-delta refinement path preregistered as an amendment candidate.
- 0*.txt team-lead working files: rewritten tip commit removed a stale snapshot from history at team-lead request; convention going forward is commit-with-neutral-message.

## Hardware

Zero metered seconds.

## Links

PR #1 (merged), PR #3 (develop->main), tag `prereg-freeze`, docs/sprints/SPRINT_1_PLAN.md, docs/sprints/SPRINT_1_RETROSPECTIVE.md.
