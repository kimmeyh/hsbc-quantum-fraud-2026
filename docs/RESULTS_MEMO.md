# Results Memo (Phase 1 evidence base) -- Sprint 4 Task D (F7)

**Purpose**: The one-page evidence summary the paper is written from; gate table scored as committed; headline-framing options for the team lead's Class-2 decision.
**Audience**: Team lead (gate review); Sprint 5 paper drafting.
**Last Updated**: 2026-09-03 (B1 + G0b executed: 27 fits, 120 QPU s; corrections applied after an independent review of this memo)

Every number traces to `experiments/results/results.json` by config_hash via `gate_report.md`. Prevalence (test fold) = 0.00167 beside every AUPRC. Per-arm figures below are regenerated from `gate_report.md`, not transcribed.

## Gate table (scored as committed; PREREGISTRATION section 3, amendments A1-A6)

| Gate | Prediction | Outcome | Evidence | Amendment ref |
|---|---|---|---|---|
| G0 | Tuned-XGB full-feature mean test AUPRC >= 0.85 (10 seeds) | **FAIL as committed**: 0.8296, CI [0.8092, 0.8501]. Footnote: the 0.85 threshold derived from a literature band that primary-source research (F21) could not corroborate; A7 sensitivity cells proposed | [SIM] | none (criterion unchanged); A7 proposed |
| G0 leakage tripwire | No cell > 0.95 AUPRC | PASS: max cell mean 0.8368 (CatBoost/full) | [SIM] | -- |
| Shuffled-label tripwire | Shuffled labels collapse test AUPRC to base rate | PASS: 0.00225 vs prevalence 0.00167 (1.34x, chance) | [SIM] | -- |
| G0b | Proxy-vs-hardware config rank Spearman >= 0.5 over top-3 + bottom-2 free-tier configs | **PASS as committed**: Spearman 0.900, 5 hardware fits, 21 QPU s. Footnote: the design's bottom-2 anchors are degenerate configs (rank 33 emits a constant score, AP = prevalence; rank 32 carries a health WARN), and the single rank swap is between configs whose proxy val AP differ by 0.0001. Among the 3 competitive configs alone, Spearman = 0.5, exactly at the gate | [HW] | A2, A3 |
| H1a | SMU reproduction AUC-PR >= 0.80 | NOT YET RUN | [PROJ] | -- |
| H1b-primary | Best CVQBoost vs best tuned GBDT, matched top-k, paired per-seed delta-AP, 10 seeds | **NULL as preregistered**: Dirac-3 CVQBoost minus CatBoost matched-13 = **-0.0399** [CI -0.0571, -0.0227]; abs(delta) > MDE 0.0268; trails on 9 of 10 seeds (only seed 48 positive, +0.0108). Also vs XGBoost -0.0347 and LightGBM -0.0353, both exceeding the MDE. OPEN: the per-seed paired BCa the prereg lists as support needs persisted predictions (single fix, shared with A7 cell S1) | [HW] | A5 (MDE 0.0268) |
| H1c | Training-time log-log slopes | NOT YET RUN | [PROJ] | -- |
| H3 | Dose-response slope over k in {5,9,13,17} | NOT YET RUN (F3) | [PROJ] | -- |
| H4 | CVQBoost minus the BEST structural control: (i) non-negative ridge with lambda tuned over the same grid, (ii) non-negative sparse L1 variant | **PARTIAL**: the solver-fidelity component is measured (below); NEITHER preregistered control has been run, so H4 is not yet scoreable | [HW] partial | A3 (pool identity) |
| H5 | In-segment advantage; SPECTRA replication + fraud transfer | NOT YET RUN (F5/F24) | [PROJ] | -- |
| H6 | QFE phase representation shifts the delta | NOT YET RUN (F4/F23) | [PROJ] | -- |

Holm correction across exploratory cells (prereg 3) is not yet applicable: the exploratory family is incomplete (H3/H5/H6 unrun). It is applied at F7 gate review when the family closes.

## Per-arm summary (ULB, stratified 60/20/20, 10 seeds, test AUPRC; prevalence 0.00167)

| Arm / cell | Mean AP | Seed SD | 95% t-CI | Mean AUC-ROC |
|---|---|---|---|---|
| CatBoost / full [SIM] | 0.8368 | 0.0304 | [0.8150, 0.8585] | 0.9765 |
| XGBoost / full [SIM] | 0.8296 | 0.0286 | [0.8092, 0.8501] | 0.9791 |
| LightGBM / full [SIM] | 0.8240 | 0.0295 | [0.8029, 0.8451] | 0.9788 |
| CatBoost / matched-13 [SIM] | 0.8070 | 0.0321 | [0.7841, 0.8300] | 0.9738 |
| LightGBM / matched-13 [SIM] | 0.8024 | 0.0274 | [0.7828, 0.8220] | 0.9726 |
| XGBoost / matched-13 [SIM] | 0.8019 | 0.0239 | [0.7847, 0.8190] | 0.9730 |
| **CVQBoost on Dirac-3 [HW]**, selected config (13 features, 91 vars) | **0.7671** | 0.0302 | [0.7455, 0.7887] | 0.9201 |
| CVQBoost exact proxy, same config and pool [SIM] | 0.7681 | 0.0312 | [0.7458, 0.7905] | 0.9210 |
| CVQBoost on Dirac-3 [HW], F22 tuned lg config (**9 features**, 45 vars; not a matched-13 comparison) | 0.7014 | 0.0263 | [0.6826, 0.7202] | 0.9557 |
| CVQBoost exact proxy, F22 tuned lg config [SIM] | 0.7039 | 0.0229 | [0.6875, 0.7203] | 0.9560 |
| Logistic / full [SIM] | 0.7218 | 0.0268 | [0.7026, 0.7410] | 0.9769 |

Untuned pilot (Sprint 1): XGBoost 0.8268. Tuning at the frozen 100-trial budget: CV 0.8555 vs test 0.8296 (normal CV-to-test optimism, not a tuning regression). Dedupe-before-split removed 1,081 rows. F22 (100 trials): the best trial reached 0.6873 validation AP against the starting config's 0.7232 on the tuning seed, so the validation-AP rule retains the starting config; the TPE sampler spent 73 of 100 trials on lg configs, and KNN weak learners were excluded on proxy cost (both reported as tuning-space deviations).

**Score-health caveat (A6)**: the selected dct hardware config carries a WARN on **10 of 10 seeds** (mode share 0.951, 814 distinct scores). Its AP and AUC are valid (step-wise AP handles ties), but its alert-budget precision and calibration figures are weak evidence. The F22 lg config is health-clean (mode share 0.518, ~4,000 distinct scores) but scores lower and uses 9 features.

## Hardware campaign (executed 2026-09-03, team-lead approved)

27 fits, 0 failures, 0 retries, **120 QPU s** billed against a ~100-145 s estimate (~380 s balance remains). B1: 22 fits over two pool variants, seeds 42-51 plus one temporal-sensitivity split each. G0b: 5 fits over the ranked configs. Measured cost 4-5 QPU s per fit at 25-91 variables, consistent with the FourierWall2 cost model. Every [HW] row carries billed seconds, the hardware objective, the exact proxy objective on the identical Hamiltonian, and the weight cosine.

**Temporal sensitivity (n = 1 per config, stated-weak per prereg 8.2)**: the ordering *reverses* against the stratified result -- hw_b1_lg 0.7776 vs hw_b1_dct 0.7095, a 0.068 gap in the opposite direction. One seed proves nothing, and there are no classical temporal rows to compare against, so this is flagged as a question for F3's temporal work rather than a finding.

## What the evidence says (plain terms)

- **The classical baselines are clean and solid**: no leakage flags, the shuffled-label tripwire collapses to chance, tight seed CIs, ordering CatBoost > XGBoost > LightGBM.
- **G0's floor was miscalibrated, and the gate still fails as committed.** F21's primary-source research found the 0.85-0.88 band uncorroborated: its probable origin uses trapezoidal PR-AUC (banned by our section 9), trains on 90% of the data with no held-out test fold, and keeps duplicates. Clean-protocol equivalents are ~0.80-0.81, and a step-wise-AP benchmark (AutoXGB) reports 0.78. This is exploratory post-hoc context for a failed gate and stays in the footnote, never in a headline.
- **Solver fidelity is excellent and, on this formulation, expected.** Dirac-3 minus its exact classical proxy on identical Hamiltonians = **-0.0010 AUPRC** [CI -0.0032, +0.0012], inside the MDE; weight cosine 0.975-0.999; hardware objective always above (worse than) the exact minimum by 0.013% to 0.413%. This is the **H4 solver-fidelity component**, not H4 itself: the preregistration defines H4 against tuned-lambda non-negative ridge and an L1 variant, and neither control has been run.
- **Why fidelity is near-trivial here, stated plainly.** J = HH^T + lambda*I is strictly convex on the simplex, so the proxy returns the global optimum and hardware can only match it. An independent review of this memo raised that the frozen lambda = 2 x n_train might be dominating the objective (diag(HH^T) = n_train exactly, for +/-1 weak-learner outputs). A zero-metered proxy sweep tested that directly: at alpha in {0, 0.001, 0.01, 0.1, 0.5, 1, 2, 4}, validation AP moves only within 0.7207-0.7216 and the solution stays uniform (all 91 weights active, max weight 0.0110 ~ 1/91) **even at lambda = 0**. So the flat optimum is driven by the simplex constraint over highly correlated +/-1 weak learners, not by the ridge term. That conclusion is stronger than the original one: on this formulation the optimization problem itself is nearly degenerate, which is why any solver reproduces it, and why the interesting Phase 2 direction is a non-convex formulation (cardinality or L0 sparsity, integer weights, native higher-order terms) where an exact classical proxy stops existing.
- **On the ULB primary endpoint, CVQBoost trails**, on hardware, by 0.035 to 0.040 against all three tuned GBDTs, every CI excluding zero, 9 of 10 seeds negative. Reported as the preregistered null.

## Headline-framing options (Class-2 decision for the team lead)

1. **Regime-map framing** (prereg section 1's pre-committed fallback): "A preregistered, leakage-controlled benchmark of quantum-inspired boosting against tuned GBDTs, with a measured map of where CVQBoost does and does not earn its place." **Note on the trigger**: the prereg's compound falsification criterion requires H1b to fail AND the H3 slope to be non-positive AND H5 not to transfer. H3 and H5 are unrun, so the condition has NOT been evaluated; choosing this framing now is an early team-lead choice, not a fired trigger, and the paper must say so.
2. **Hybrid-system framing**: best achievable detection is the tuned classical ensemble; CVQBoost is positioned as the in-segment specialist and the hardware-scaling arm, with Phase 2 evidence targets.
3. **Conditional quantum-advantage framing**: not defensible on the ULB primary endpoint given the measured null.

**Recommendation**: option 1 as the spine with option 2's positioning, stated as an early choice pending H3/H5. The methodological contribution to lead with is the exact structural control plus the measured solver-fidelity result and the degeneracy analysis; that combination is rarer, and more credible, than another performance claim.

## Statistical review checklist walk

Walked 2026-09-03 AFTER the hardware campaign: `docs/sprints/drafts/SPRINT_4_STAT_CHECKLIST_WALK.md`. All leakage, split, metric, and provenance items DONE with evidence. Open items: per-seed paired BCa (needs prediction persistence; shared fix with A7 cell S1), Holm correction deferred until the exploratory family closes, and registration of the Sprint 4 hardware/sweep code in an amendment line.
