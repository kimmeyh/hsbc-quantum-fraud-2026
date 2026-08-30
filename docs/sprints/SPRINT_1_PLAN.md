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

## Acceptance criteria

- [ ] PREREGISTRATION.md status line reads FROZEN with commit hash; tag `prereg-freeze` exists; pushed
- [ ] metrics.py tests pass, including BCa vs known-answer check and Wilson vs statsmodels cross-check
- [ ] All three fraud datasets plus SPECTRA load through `data.py` with validated shapes
- [ ] MDE statement written into `experiments/PILOT_VARIANCE.md` with the observed seed SD
- [ ] Sprint branch PR open to develop; CHECKLIST reconciled and committed

## Hardware budget

Zero metered seconds this sprint.

## Retro (filled at close)

- What worked:
- What did not:
- Change next sprint:
