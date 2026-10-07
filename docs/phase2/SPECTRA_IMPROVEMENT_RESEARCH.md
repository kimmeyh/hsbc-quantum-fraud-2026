# F124: what could improve SPECTRA prediction, and what is worth device time

Sprint 22, Task C (#162). Phase 2. Zero metered seconds. Evidence tag SIM for
every number measured here. The card asked for
`docs/SPECTRA_IMPROVEMENT_RESEARCH.md`; it lives under `docs/phase2/` by the
F123 layout.

**The team lead approves this list before any Dirac-3 card starts** (F124
gates F95, F110, F20, F25 and F30, decision 2026-10-06).

## Bottom line

- **The top lever is leaf regularization: `min_samples_leaf=20` on the weak
  trees.** On energy_steel it lifts CVQBoost from 0.902 to 0.973 AUPRC (5
  seeds) and brings it level with HGB (0.965; CI of the difference includes
  zero). It is a native eqc_models parameter, so a device test needs no
  library change. A 1-seed device pilot costs about 82 s; 5 seeds about 410 s.
- **Laplace soft votes and leaf regularization are mostly one lever.** Both
  stop a 1-sample leaf from casting a full vote. Soft votes add +0.074 alone
  but only +0.006 on top of `min_samples_leaf=20`.
- **Nothing found closes the gap on telecom or oilgas.** HGB still leads by
  about 0.10 and 0.03 AUPRC. Every gain on this list is on energy_steel, or
  is small.
- **Parity, not advantage.** No lever beats HGB with a CI that excludes zero
  on any dataset.
- **Two levers are measured and rejected**: multi-sample ensembling (+0.0014
  AUPRC, 35 times below the seed spread) and an emulator as an AUPRC
  predictor (it returns the proxy's answer, as the device does).
- **NeuraWave does not fit this problem**, from QCi's own press releases: it
  is edge hardware for time series and signals, sold as a PCIe card, with no
  cloud access or SDK stated.
- **The device is not the lever.** It returns its classical proxy's answer.
  Every gain on this list comes from the problem (votes, pool, features,
  regularization), so every lever is tested on the proxy first, free.
- **The plan's falsifier did not fire.** Untried levers exist, and several
  move AUPRC on the proxy. But they move it to parity with the classical bar,
  not past it.

## Method

1. Started from what this repository already measured (section 1).
2. Searched EvidenceBasedDB's store read-only (`mode=ro`), the installed
   `eqc_models` 0.21.0 source, and QCi's primary press releases.
3. Measured on the exact proxy, at zero metered cost:
   - soft votes and multi-sample ensembling (F20,
     `docs/phase2/F20_SOFT_VOTES_RESULT.md`);
   - a 2-seed screen of learner type, tree regularization and lambda on all
     three datasets (`experiments/phase2/src/lever_screen.py`, results in
     `f124_lever_screen.json`);
   - a 5-seed confirmation of the screen's energy_steel winners against HGB
     on the same splits (`f124_lever_confirm_energy_steel.json`). This was
     added because the 2-seed screen looked better than it was: HGB's
     energy_steel AUPRC ranges 0.930-0.985 by seed, so a 2-seed comparison
     against its 5-seed mean misleads;
   - a stacking test, soft votes on the regularized pool
     (`f124_lever_stack_energy_steel.json`).
   All result files are in `experiments/phase2/results/`.
4. Device seconds come from the F17 emulator's cost model
   (`docs/phase2/F17_EMULATOR.md`): 81.7 s per fit at 816 variables, 38.5 s
   at 560, 8 samples, relaxation schedule 2. The model is FITTED; the
   allocation balance is 1,022 s.

## 1. What the repository already says

- The device returns its proxy's answer: in-pocket AUPRC within 0.0072 on all
  8 B4 cells, weight cosine 0.83-0.90 (`docs/B4_B5_HARDWARE_RESULT.md`).
- The lanes that win have feature interactions: HGB and GA2M beat the proxy
  on every cell; additive lanes lose (`docs/F100_CLASSICAL_BAR.md`).
- Train-test AUPRC gap is +0.15 to +0.30 on every B4 cell: the model
  overfits.
- `in_pocket` is predictable from the phase features at AUC 0.93-0.99
  (`docs/F101_IN_POCKET_PROVENANCE.md`).
- B5's QSVM Hamiltonians exceed A31's ~23 dB resolution limit on 11 of 12
  cells.
- energy_steel has never run on the device here.

## 2. The ranked list

Each entry gives: source and whether it is verified; expected effect; the
proxy test; device seconds if the proxy shows signal.

### Rank 1. Leaf regularization of the weak trees (`min_samples_leaf`)

- **Source**: this repository, measured (SIM). The lead came from F20's
  finding that the default trees end in 1-sample leaves.
- **Effect on the proxy, energy_steel, 5 seeds**: 0.902 to **0.973** AUPRC;
  seed SD 0.005; train-test gap 0.098 to 0.019. Against HGB on the same
  splits: **+0.0085, CI [-0.0063, +0.0256], 2 of 5 seeds: parity.**
  In-pocket: 0.955-0.965 against HGB's 0.939-0.967.
- **Effect elsewhere (2-seed screen)**: oilgas +0.004, telecom -0.009. No
  signal there.
- **Side effect worth knowing**: the proxy optimum becomes sparse. About 300
  of 816 weights are nonzero, against about 720 for the default pool. A31
  predicts the device returns something sparser than a diffuse optimum, and
  on B2 that sparser answer scored better (+0.0256, 10 of 10 seeds;
  `ALL_SPRINTS_MASTER_PLAN.md`, the A31 note under F90). When the optimum is
  already sparse, whether the device's sparsification still helps is open.
  That is an inference, not a measurement, and it is what a device run here
  would test.
- **Substitution, named**: the card asks for an energy_steel in-pocket
  comparison of CVQBoost against XGBoost. The figures here are against HGB,
  the F100 bar's strongest lane. XGBoost was not run as a separate lane.
- **Next proxy test (zero cost)**: a `min_samples_leaf` sweep (5, 10, 20,
  50) on all three datasets, 5 seeds, with HGB on the same splits.
- **Device test if approved**: B4's energy_steel cell with
  `weak_cls_params={"min_samples_leaf": 20}`, no other change. 816
  variables, 8 samples: **about 82 s per fit; 1-seed pilot about 82 s;
  5 seeds about 410 s** (F17 estimate, FITTED). energy_steel has never run
  on the device. What it tests: whether the device reproduces the proxy on a
  sparse, better-scoring problem. It cannot be expected to beat the proxy.

### Rank 2. Laplace soft votes

- **Source**: F20 (card) and this repository, measured (SIM).
  `docs/phase2/F20_SOFT_VOTES_RESULT.md`.
- **Effect**: +0.074 on energy_steel alone, +0.030 telecom, +0.005 oilgas,
  15 of 15 cells. **On top of rank 1: +0.006**, CI [0.0041, 0.0078], 5 of 5
  seeds (0.973 to 0.979). Real, consistent, and mostly the same lever as
  rank 1.
- **Cost of using it on the device**: a custom H matrix, which departs from
  eqc_models' builders. Rank 1 gets most of the gain without that.
- **Device test if approved**: only after rank 1, as its own arm. Same cost
  per fit, about 82 s.

### Rank 3. KNN weak learners

- **Source**: EvidenceBasedDB record `cvqboost-knn-aucpr-0-8108-kaggle-fraud`
  (certainty **low**): CVQBoost with KNN weak learners on Dirac-3 reached
  0.8108 AUC-PR on the MLG-ULB credit-card dataset, from Loke 2026, p.6
  Table 3. Our B1 (default trees, same dataset) is lower. Different setup;
  not a replication.
- **Effect on the proxy**: the only lever positive on all three datasets in
  the screen (energy_steel +0.035, oilgas +0.013, telecom +0.010). 5 seeds on
  energy_steel: 0.956, SD 0.021, parity with HGB.
- **Next proxy test**: 5 seeds on oilgas and telecom, and on ULB (B1's
  dataset) to test the record's claim directly.
- **Device**: same pool size, same cost per fit. Note: KNN prediction is
  slow on large test sets (the library comment mentions 435 pair KNNs on
  ~350k samples).

### Rank 4. Boosted weak learners (`lgb`, `xgb`)

- **Source**: eqc_models 0.21.0 `weak_cls_type` options, verified in the
  installed source.
- **Effect**: energy_steel 0.979 (lgb) and 0.977 (xgb), 5 seeds, SD 0.003;
  parity with HGB. **Worse** on oilgas (-0.027, -0.006) and telecom (-0.011,
  -0.025) in the screen.
- **Reading**: each "weak" learner is itself a boosted ensemble on a feature
  pair or triple. The gain comes mostly from the learner. This is a classical
  pool change that runs through CVQBoost, not a CVQBoost improvement.
- **Device**: not recommended. It would test the learner, not the device.

### Rank 5. Feature engineering: phase features and whitening

- **Source**: EvidenceBasedDB records `fourier-wall-is-a-feature-engineering-target`
  and `fourier-wall-correlation-partially-dequantizes` (tag N/A, from the
  Fourier Wall paper). They say re-expressing cyclic covariates as phases and
  whitening the encoded block moves a problem toward the QNN regime.
  **Unverified for CVQBoost**: the records are about angle-encoded QNNs.
- **Effect**: not measured.
- **Next proxy test**: phase-encode the cyclic columns (the
  `spectra_segment` phase features), whiten, rebuild the pool, 5 seeds, three
  datasets.
- **Device**: none until the proxy shows signal.

### Rank 6. Pool size (`weak_cls_pair_count`)

- **Source**: the installed `QBoostClassifier` signature exposes
  `weak_cls_pair_count`. Not used here before.
- **Effect**: not measured. The train-test gap suggests a smaller pool may
  generalize better; rank 1 already closes most of that gap on energy_steel.
- **Why it matters for the device**: cost grows with roughly the square of
  pool size, so a smaller pool is cheaper per fit.
- **Next proxy test**: pair counts of 100, 200, 400 on all three datasets.

## 3. Levers searched and not promoted

- **Multi-sample ensembling**: +0.0014 AUPRC on emulated samples, about 35
  times below the seed spread; not evaluable on the stored device samples
  (F20).
- **The F17 emulator as an AUPRC predictor**: it returns the proxy's AUPRC,
  as the device does (F17's falsifier met). Kept for cost estimates.
- **Stronger lambda (alpha 20, 10x)**: energy_steel -0.006, oilgas +0.000,
  telecom +0.008 (2-seed screen). No signal.
- **Shallow trees (`max_depth=4`)**: closes the train-test gap but loses
  AUPRC on all three datasets (-0.012, -0.074, -0.037). Leaf size, not depth,
  is the regularizer that works.
- **Resampling the training data**: EvidenceBasedDB
  `learning-ml-resampling-not-the-lever-for-strong-trees` and
  `resampling-degrades-calibration-recalibration-repairs` (both certainty
  low): no reliable gain for strong tree models, and calibration worsens.
- **Quantum ML models in general**: EvidenceBasedDB
  `learning-qml-no-reliable-tabular-accuracy-gain` (certainty moderate,
  awaiting team-lead adjudication there): no reliable gain on tabular data.
- **`batched_qboost_enabled`**: the F124 card lists it as verified on
  2026-10-06. **It is not in the installed eqc_models 0.21.0**: not in the
  `QBoostClassifier` signature and not anywhere in the package source. The
  likely origin is the off-repository `CVQBoost_Findings.md` (section 3),
  which describes a library whose weak learners default to XGBoost and which
  has the flag. The installed library defaults to logistic regression and
  this repository passes `dct`. So that document's library version differs
  from ours (inference; its version is not stated in the sections read).
- **eqc_models `feature_selection` and `decomposition` modules**: present,
  not tested. They solve their own optimization problems, so on the device
  they add metered calls before the classifier runs. Not ranked until a proxy
  version shows signal.
- **`QSVMClassifierDual`**: B5's QSVM Hamiltonians already exceed the
  device's resolution on 11 of 12 cells. Not ranked.
- **Non-convex selection (F25)**: the one formulation where the device is not
  just reproducing a convex optimum (EvidenceBasedDB
  `dirac3-fidelity-test-is-near-trivial-on-convex-formulation`, certainty
  high). It is a different question (does the device add anything?) from
  this list's (what improves the number?). It stays on its own card.

### Every source the card named, disposed

- **results.json, the F100 bar, F101, the B4/B5 result**: used, section 1
  and the HGB comparisons.
- **SPECTRA feasibility analysis** (`docs/SPECTRA_CONTROL_FEASIBILITY.md`):
  the matched control is infeasible on energy_steel. Every comparison here is
  against classical lanes on the same splits, which needs no control.
- **A31 (resolution)**: used in rank 1's sparsity note and the F17 emulator.
- **B2's sparsity result**: used in rank 1. **New caveat**: the B2 responses
  on disk carry the same truncated print as B4's (all 11 files), so the
  sparsity figures quoted from them were read from about 6 visible values per
  sample, not all 833. The figures are not wrong on what they saw; they are
  not a full count. Recovering B2's samples by job id would settle it.
- **F20 soft votes**: measured, rank 2.
- **F25 non-convex selection**: section 3; stays on its own card.
- **F104 resolution screen**: a pre-run check, not a lever. It belongs in
  front of any device run from this list, and rank 1's sparse optimum is the
  case it should be run on first.
- **F106 dequantization check**: about the gate-based circuit arm. Not
  relevant to CVQBoost levers.
- **F109 domain ladder and aggregation**: a cross-domain study on other
  datasets. Out of scope for improving these three cells.
- **F113 oracle gap**: bounds whether a router could help. Rank 1 brings
  CVQBoost to parity on energy_steel, which is the case where an oracle-gap
  test becomes informative. Not run here.
- **Off-repository `CVQBoost_Findings.md`** (planning reference only;
  nothing in it is cited as evidence). Read sections 1, 3, 8 and 11. It
  agrees with this list where they overlap: shallower learners hurt badly
  (our `max_depth=4` result), soft votes are named as a gap ("hard labels
  discard the confidence"), and CVQBoost overfits in-segment by 3-8x
  XGBoost's gap. It suggested more lambda or a smaller pool; more lambda
  showed nothing here (alpha 20). Leaf size is not in it.
- **EvidenceBasedDB**: cited per record above, with its certainty.
- **Dirac-3 and eqc_models**: installed 0.21.0 source, read directly.

## 4. QCi NeuraWave

**Verified from QCi's own press releases:**

- 2025-11-17: QCi would debut NeuraWave at SC25, "a photonics-based reservoir
  computing system", "built in a standard PCIe interface", "especially suited
  for edge-AI use cases such as signal processing, time-series forecasting,
  and pattern recognition".
  [QCi press release](https://quantumcomputinginc.com/news/press-releases/2025/quantum-computing-inc.-to-unveil-photonics-based-reservoir-computer-neurawave-at-supercompute25)
- 2026-04-23: NeuraWave is "deployment-ready", a "photonic reservoir
  computing platform" for "real-time AI inference" at the edge, "a standard
  server PCIe plug-in card", targeting "time-series prediction, anomaly
  detection, and edge intelligence"; "units currently being manufactured and
  now available for customer orders".
  [QCi press release](https://quantumcomputinginc.com/news/press-releases/2026/quantum-computing-inc.-announces-deployment-ready-neurawave-a-photonic-computing-platform-for-real-time-ai-inference-at-the-edge)
- 2026: a framework agreement with Planck Dynamics to deploy NeuraWave.
  [QCi press release](https://quantumcomputinginc.com/news/press-releases/2026/quantum-computing-inc.-announces-framework-agreement-with-planck-dynamics-to-deploy-neurawave-photonic-reservoir-computer-as-a-foundational-platform-for-next-generation-ai-applications)
  (Its terms were seen only in a search summary, not read in full:
  **unverified**.)

**Not stated in either release read in full**: tabular data,
classification, fraud, finance, feature extraction, an SDK, or cloud access.

**Assessment**:

- **Not a fit for SPECTRA.** SPECTRA rows are tabular and independent, not a
  time series or a signal. A reservoir computer's strength is memory of a
  sequence.
- **Not reachable.** It is purchased hardware. Nothing says it is on QCi's
  cloud, where this project's allocation is.
- **Relation to `eqc_models.ml.reservoir`: unverified.** The installed module
  names EmuCore as its device. Whether NeuraWave is EmuCore, its successor,
  or neither is not stated in either release. A question to QCi would settle
  it.
- **Where it could matter**: transaction streams as time series (sequence of
  a card's transactions). That is a different problem from the challenge
  datasets and is not proposed here.

## 5. What the team lead approves

The list in section 2, in order. No Dirac-3 fit runs from it without the
per-block Criterion H approval, with call count and expected seconds stated.
