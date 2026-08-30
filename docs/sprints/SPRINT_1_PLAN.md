# Sprint 1 Plan: Freeze and Foundations

Dates: Aug 31 to Sep 1, 2026. Branch: `feature/20260831_Sprint_1`. PR target: `develop`.
Status: AWAITING TEAM-LEAD APPROVAL. Approval authorizes all in-scope tasks per docs/SPRINT_PROCESS.md; the preregistration freeze itself remains a separate explicit team-lead decision embedded in task 1.

## Scope

1. **Preregistration freeze** (team-lead decision): v1.1 approved (with any requested edits applied first), committed, tagged `prereg-freeze`, commit hash recorded in the file by amendment. Analysis code in `experiments/src/` freezes at the same commit.
2. **metrics.py to v1.1 spec**: stratified BCa bootstrap (2,000 resamples), Wilson intervals for precision/recall, equal-mass-binned ECE with reliability-diagram data, dual operating points (max-F1 and fixed alert budget), paired delta-AP machinery with identical resample indices, prevalence reported beside AP. Unit-tested against known-answer cases on synthetic data.
3. **Data staging complete**: IEEE-CIS extracted to `experiments/data/ieee-cis/` with row-count validation (590,540 train transactions); SPECTRA already staged; loader functions extended for both.
4. **Pilot variance run** (classical only, no hardware): 10-seed tuned-lite XGBoost on ULB stratified splits to produce the seed-variance estimate feeding the MDE statement required before any hardware approval.
5. **Housekeeping**: CHECKLIST reconciliation, sprint close per process.

## Explicitly out of scope

Full 100-trial tuning campaigns (Sprint 2); any CVQBoost or hardware work (Sprints 2-3); paper drafting (Sprint 4).

## Acceptance criteria (validated at close, 2026-08-30)

- [x] PREREGISTRATION.md status line reads FROZEN with commit hash; tag `prereg-freeze` exists; pushed. Evidence: freeze commit 95751b9, amendment A1, tag pushed to origin.
- [x] metrics.py tests pass, including BCa vs known-answer check and Wilson vs statsmodels cross-check. Evidence: 11 passed (test_metrics.py), BCa cross-validated against scipy.stats.bootstrap.
- [x] All three fraud datasets plus SPECTRA load through `data.py` with validated shapes. Evidence: validate_all(): ULB 284,807/492; IEEE-CIS 590,540 x 434 at 3.5%; SPECTRA 35,040/36,733/10,000/3,150 rows with 17/15/12/18 features.
- [x] MDE statement written into `experiments/PILOT_VARIANCE.md` with the observed seed SD. Evidence: mean AP 0.8268, seed SD 0.0243, MDE(10 seeds) 0.0242, [SIM].
- [x] Sprint branch PR open to develop; CHECKLIST reconciled and committed. Evidence: PR #1 flipped from draft to ready at close.

## Hardware budget

Zero metered seconds this sprint. Confirmed: zero spent.

## Retro (filled at close)

- What worked: the review-adjudicate-freeze pipeline produced a bindable protocol in one day; the pre-commit hook caught a real staging risk on its first live test; background execution kept downloads and the pilot off the critical path; all acceptance criteria closed same-day.
- What did not: two metrics tests initially failed because the synthetic pilot data was perfectly separable (degenerate CI edge cases); legacy Kaggle env vars silently shadowed OAuth and cost two failed download cycles; develop lagged main by one commit when the sprint branch was cut, requiring a fast-forward fix.
- Change next sprint: sync develop with main before any branch cut (now moot under the carry-forward rule); design synthetic test data with realistic class overlap from the start. Note for Sprint 2 analysis: the pilot MDE (0.0242) derives from raw per-seed AP variance; per-seed PAIRED deltas remove shared split-difficulty variance, so the paired-delta SD measured in Sprint 2 will likely be smaller. The MDE estimate may be refined by dated amendment when that measurement exists; the decision rule itself is unchanged.
