# F100: the complete classical bar, and the proxy does not clear it

Sprint 21 Task D, run 2026-10-05. Five lanes x 3 frozen cells x 5 seeds, all
classical. Evidence tag `[SIM]`, **zero metered seconds**. Figures in
`experiments/results/f100_classical_bar.json`.

## The result

**HGB and GA2M beat the CVQBoost classical proxy on all three cells, on 5 of 5
seeds each, with bootstrap 95% CIs excluding zero in every case.**

| Cell | Lane | Mean AUPRC (sd) | Delta vs proxy | CI 95% | Seeds |
|---|---|---|---|---|---|
| energy_steel | hgb | 0.9649 (0.026) | **+0.0626** | [+0.0392, +0.0823] | 5/5 |
| energy_steel | ga2m | 0.9589 (0.023) | **+0.0566** | [+0.0391, +0.0709] | 5/5 |
| energy_steel | gam_additive | 0.8771 (0.005) | -0.0251 | [-0.0318, -0.0173] | 0/5 |
| energy_steel | joint_twin | 0.6761 (0.236) | -0.2262 | [-0.4455, -0.1084] | 0/5 |
| energy_steel | logreg | 0.6010 (0.194) | -0.3013 | [-0.4812, -0.2054] | 0/5 |
| oilgas_gasturbine | hgb | 0.8739 (0.010) | **+0.0350** | [+0.0343, +0.0358] | 5/5 |
| oilgas_gasturbine | ga2m | 0.8556 (0.011) | **+0.0167** | [+0.0155, +0.0176] | 5/5 |
| oilgas_gasturbine | joint_twin | 0.8035 (0.005) | -0.0354 | [-0.0397, -0.0305] | 0/5 |
| oilgas_gasturbine | gam_additive | 0.8030 (0.010) | -0.0358 | [-0.0375, -0.0343] | 0/5 |
| oilgas_gasturbine | logreg | 0.7807 (0.005) | -0.0581 | [-0.0626, -0.0531] | 0/5 |
| telecom_churn | hgb | 0.8669 (0.020) | **+0.1344** | [+0.1150, +0.1558] | 5/5 |
| telecom_churn | ga2m | 0.7988 (0.016) | **+0.0663** | [+0.0453, +0.0925] | 5/5 |
| telecom_churn | joint_twin | 0.7092 (0.018) | -0.0234 | [-0.0394, -0.0028] | 1/5 |
| telecom_churn | gam_additive | 0.7076 (0.017) | -0.0249 | [-0.0434, -0.0104] | 0/5 |
| telecom_churn | logreg | 0.6433 (0.023) | -0.0893 | [-0.1041, -0.0707] | 0/5 |

Deltas are **paired per seed**, then bootstrapped over 10,000 resamples.
Pairing matters: amendment A24 records that B2's +0.0256 gain was invisible
unpaired, sitting inside a seed-to-seed standard deviation of 0.030 and
reading as noise.

## Which of F100's three outcomes this is

The card named three, all reportable. This is **outcome 1 for two lanes and
outcome 3 for none**: the proxy does not survive the complete bar. Two
off-the-shelf classical lanes clear it everywhere, and the margin is largest
on `telecom_churn` (+0.134) — the cell whose in-segment pocket is also the
only one small enough to permit a matched control.

The two lanes that beat it are the two with **pairwise interactions**: HGB
unrestricted, GA2M constrained to main effects plus pairs. The two additive
lanes (gam_additive, logreg) and the JOINT twin all lose. That is a coherent
picture rather than a quirk: the signal in these datasets lives in feature
interactions, and the CVQBoost proxy's ridge-over-weak-learners construction
captures some of it but less than a gradient-boosted tree does.

## What this does and does not establish

**Does not say anything about Dirac-3.** Every number here is classical, and
the comparator is the CVQBoost **classical proxy**, `evidence_tag: PROJ`,
`metered_seconds: 0`. This repository has never run SPECTRA on Dirac-3. The
device could differ from its proxy — B2's weight cosine of 0.83 shows the
hardware solve departs materially from the classical one at this scale, and
A24 records that the sparsified hardware answer was *better* on ULB.

**Does not say anything about H5.** These are overall metrics on the full test
fold. H5 is an **in-segment** claim against a matched random-segment control,
and a method can lose overall while winning on a slice — that is the entire
premise of segment transfer. F90 is where that gets tested.

**Does constrain how an F90 win may be framed.** If the device result lands
near its proxy, it lands below `HistGradientBoostingClassifier` with default
settings, on every cell, on every seed. An in-segment win would still be a
real finding; an *overall* performance claim would not survive this table, and
any Phase 2 writeup has to carry it.

## Cost

Measured, not estimated: **3.77 seconds per cell**, dominated by HGB at 2.34 s
(`docs/F100_LANE_PILOT.md`). Fifteen cells ran in under a minute, against the
~6 hours the F100 card estimated `[no-history]`. The whole task cost less
device time than reading this document takes — there is none.
