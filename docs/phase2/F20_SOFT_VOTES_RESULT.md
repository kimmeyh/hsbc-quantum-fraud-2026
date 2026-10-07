# F20: soft votes and multi-sample ensembling

Sprint 22, Task E (#164). Phase 2. Zero metered seconds. Evidence tag SIM.
All solves use the exact classical proxy unless stated.

## Bottom line

- **Soft votes as the card specified them do not work.** The learners' raw
  `predict_proba` is exactly 0 or 1, so the "soft" vote equals the hard vote.
- **A Laplace-smoothed soft vote improves CVQBoost on all 15 cells** (3
  datasets, 5 seeds). The gain is large on energy_steel (+0.074 AUPRC), and
  small on telecom (+0.030) and oilgas (+0.005).
- **Only energy_steel passes the plan's falsifier** (a gain larger than the
  seed-to-seed spread, about 0.05). On the other two the gain is consistent
  (5 of 5 seeds) but smaller than that spread.
- **With soft votes, CVQBoost reaches parity with HGB on energy_steel only**
  (+0.011, CI includes zero). It still loses to HGB clearly on telecom and
  oilgas.
- **Multi-sample ensembling on the stored device samples is not evaluable.**
  A rebuilt weak-learner pool does not reproduce the device's pool on any of
  the 10 B4 cells. On emulated samples the gain is +0.0014 AUPRC: real, but
  far below the seed spread. Ensembling is not a lever worth device time.

Code: `experiments/phase2/src/soft_votes.py`. Tests:
`experiments/src/test_soft_votes.py`. Results, all in
`experiments/phase2/results/`:

- `f20_soft_votes.json` (hard vs soft, 15 cells)
- `f20_soft_vs_classical.json` (soft vs HGB and GA2M, same splits)
- `f20_multisample_ensemble.json` (device samples: reproducibility check)
- `f20_multisample_ensemble_emulated.json` (emulated samples)

## 1. Why the specified soft vote is degenerate

The weak learners are decision trees grown to about 17 levels, with a median
leaf of 1 sample. A pure leaf gives `predict_proba` of exactly 0 or 1. So
2 * P(fraud) - 1 is exactly -1 or +1: the hard vote again. A test pins this
(`test_soft_votes.py`), so a future library change that alters it is seen.

**The variant used**: Laplace smoothing of each leaf's counts,
P = (n1 + 1) / (n + 2). A 1-sample leaf now votes 1/3 rather than 1, and a
large pure leaf still votes near 1. This is a change to the vote, not to the
pool, the Hamiltonian shape or the solve. On sklearn 1.9, `tree_.value` holds
fractions, so counts are fraction times `weighted_n_node_samples`.

## 2. Soft (Laplace) against hard, exact proxy

From `f20_soft_votes.json`, 5 seeds each, paired by seed, bootstrap 95% CI:

- energy_steel: hard 0.9024; soft - hard **+0.0739**, CI [0.0674, 0.0803];
  soft better on 5 of 5 seeds.
- oilgas_gasturbine: hard 0.8388; **+0.0050**, CI [0.0046, 0.0055]; 5 of 5.
- telecom_churn: hard 0.7319; **+0.0295**, CI [0.0207, 0.0396]; 5 of 5.

In-pocket (cells with at least 50 in-pocket positives, 13 of 15): soft is
better on all 13.

Train-test AUPRC gap, mean over seeds (hard, then soft):

- energy_steel: 0.098, then 0.024
- oilgas_gasturbine: 0.161, then 0.156
- telecom_churn: 0.268, then 0.239

Soft votes reduce overfitting most where they help most. The large gap on
telecom and oilgas remains: soft votes are not the regularization fix.

**The plan's falsifier** was a change smaller than the seed-to-seed spread,
about 0.05 in-pocket. energy_steel clears it. oilgas and telecom do not, even
though every seed moved the same way. Read those two as real but small.

## 3. Soft-vote CVQBoost against the classical lanes

From `f20_soft_vs_classical.json`. Same splits and seeds. HGB and GA2M are
configured as in `f100_lane_pilot.py`.

- energy_steel: HGB 0.9649. Soft - HGB **+0.0114**, CI [-0.0073, +0.0336],
  soft better on 2 of 5 seeds: **parity**. GA2M 0.9589; soft - GA2M
  +0.0174, CI [0.0057, 0.0373], 5 of 5.
- oilgas_gasturbine: soft - HGB **-0.0301**, CI [-0.0315, -0.0289], 0 of 5.
  Soft - GA2M -0.0118, 0 of 5.
- telecom_churn: HGB 0.8669. Soft - HGB **-0.1055**, CI [-0.1205, -0.0900],
  0 of 5. Soft - GA2M -0.0374, 0 of 5.

This is the first configuration in this repository where CVQBoost is level
with HGB on any SPECTRA cell. It is one dataset, on the proxy, and parity is
not a win.

## 4. Multi-sample ensembling

### On the stored device samples: not evaluable

The test rebuilds each B4 cell's weak-learner pool and rescores the device's
best stored sample on it. If the pool is the same, the rescored AUPRC equals
the stored device AUPRC.

- It does not on any of the 10 cells. The rescored value differs from the
  stored one by about 0.0001 to 0.003. The cause is that the trees break ties
  at random, so a rebuilt pool is a slightly different pool.
- A device weight vector means nothing on a different pool. So top-k
  ensembling on device samples is **not evaluable**, and no number is
  reported for it.
- To make it evaluable in future, a device run must store the pool itself
  (the fitted learners or their H matrix), not only the samples.

### On emulated samples

The F17 emulator returns 8 samples on the pool it built, so averaging them is
a valid test of the idea within one pool. Calibrated budget 25, the 10 B4
cells, hard votes. From `f20_multisample_ensemble_emulated.json`:

- Mean of the top 8 samples minus the lowest-energy sample: **+0.0014**
  AUPRC, CI [0.0003, 0.0025]. Top 8 better on 7 of 10 cells. Range -0.0008
  to +0.0047.
- That is real but about 35 times smaller than the seed-to-seed spread
  (about 0.05). By the plan's falsifier, **ensembling fails**: it is not a
  lever worth device time.
- Caveat: the emulator's samples are its own, not the device's. The device's
  samples are closer to the exact answer on oilgas (F17), so their spread,
  and any ensembling gain, is likely smaller still. That is an inference.

### Also noted

- The part `ensemble-emulated` reuses the B4 configuration from
  `results.json` (read only).

## 5. What this means for F124 and any device run

- Soft votes are a lever worth ranking, with energy_steel as the cell to test.
- **F124 ranked them second, not first.** A native leaf-size setting
  (`min_samples_leaf=20`) gets most of the same gain, and soft votes add only
  +0.006 on top of it (`docs/phase2/SPECTRA_IMPROVEMENT_RESEARCH.md`). The
  HGB parity stated in section 3 is correct for soft votes alone.
- A device test of soft votes needs no new device behavior: the Hamiltonian
  shape is unchanged. It needs a custom H matrix, which departs from
  eqc_models' builders, so it is its own arm (the card's constraint).
- Cost, from the F17 emulator, for one energy_steel fit: see
  `docs/phase2/SPECTRA_IMPROVEMENT_RESEARCH.md`.
- The soft vote reads a library internal (`WeakClassifier.clf`). The installed
  eqc_models version (0.21.0) is recorded in each result file.
