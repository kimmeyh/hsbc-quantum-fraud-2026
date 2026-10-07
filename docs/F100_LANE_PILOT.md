# F100 lane pilot: the classical bar is cheap, and HGB already clears the proxy

Sprint 21 Task D, run 2026-10-05. Evidence tag `[SIM]`, zero metered seconds.
Figures in `experiments/results/f100_lane_pilot.json`.

## Why this ran before the full task

`SPRINT_PLANNING.md`, Sprint 9 improvement 2: name the dominant term and show
its measurement, or the sizing is not finished. F100 was estimated at ~6 hours
`[no-history]`, and GAM/GA2M twins were the Sprint 9 surprise that missed by
47x — 10 minutes planned against 7.9 hours actual, three times over, because
the dominant component was never on the list of things being measured.

So every lane F100 will run was timed separately on one real SPECTRA cell.

## Sizing: the estimate was two orders of magnitude too high

`oilgas_gasturbine`, seed 42, 15 features, 22,039 training rows:

| Lane | Seconds | AUPRC | AUC-ROC |
|---|---|---|---|
| logreg | 0.12 | 0.7869 | 0.8691 |
| hgb | **2.34** | 0.8871 | 0.9394 |
| ga2m | 0.51 | 0.8699 | 0.9275 |
| gam_additive | 0.47 | 0.8161 | 0.8911 |
| joint_twin | 0.33 | 0.8104 | 0.8897 |

**Dominant lane: HGB, 2.34 s of 3.77 s per cell.** All five lanes across all
15 cells is **under a minute**, against the ~6 hours the card assumed. Even
with 20 repeated draws per cell (the Phase 2 design in F102) the full grid is
about 19 minutes.

The capability risk was already retired separately: `h6_twin_preflight.py`
proves GAM via `statsmodels` splines, GA2M via sklearn's `interaction_cst`,
and the JOINT twin via a cosine frequency scan, all PASS in this environment
in 4.4 s total. Neither `pygam` nor `interpret` is needed.

## The finding that matters more than the timing

**HGB already beats the CVQBoost proxy on this cell, and so does GA2M.**

| Arm | AUPRC |
|---|---|
| hgb | 0.8871 |
| ga2m | 0.8699 |
| **cvqboost_proxy** | **0.8520** `[PROJ]` |
| gam_additive | 0.8161 |
| joint_twin | 0.8104 |
| logreg | 0.7869 |

This is the overall (not in-segment) comparison on one cell and one seed, and
the CVQBoost figure is the classical proxy rather than the device — so it is
**not** a result about Dirac-3. What it does establish is that the classical
bar F100 builds is not a formality: two of its five lanes sit above the arm
being tested, on the cell the prior work treated as a success case.

**Consequence for reading F90.** If the device result lands near the proxy's
0.852, it lands *below* an off-the-shelf `HistGradientBoostingClassifier` that
takes 2.3 seconds and no quantum hardware. The in-segment claim (H5) could
still hold — a method can win on a slice while losing overall, which is the
entire point of segment transfer — but any overall-performance framing would
need this table beside it.

This is outcome 1 of the three F100's card names, arriving before the device
data: the gain has to survive a complete bar, and the bar is higher than the
proxy.

## What this does not say

- Nothing about Dirac-3. Every number here is classical, and the CVQBoost
  comparator is `[PROJ]`.
- Nothing about H5. These are overall metrics on the full test fold, not
  in-segment against a matched control.
- Nothing yet about the other two cells. One cell, one seed, by design: this
  is a sizing pilot, and its job was to make the full run safe to launch.

## What runs next

The full F100 grid is cheap enough to run on every cell and seed without a
staged rollout. It still waits on Task A, because the card's purpose is to
read F90's result and the anchoring configuration has to match what the device
actually ran. The pilot's value is that the run itself is now sized, proven,
and known to be minutes rather than hours.
