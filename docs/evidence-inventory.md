# Evidence Inventory: What We Have Measured So Far

Compiled 2026-08-29 from the local repos. This is the honest starting point for the submission. Every number below is from files on disk, cited by path.

## 1. ULB credit-card fraud: hybrid QBoost vs XGBoost (XGBvHQXGB, run 2026-05-25)

Source: `XGBvHQXGB\quantum_processes\photonic\output_files\creditcard_x1_train_xgb_comparison_case_a_stable_summary.csv` and `logs\log_20260525_234915.log`. Dirac-3 hardware run (3-shard batched QBoost, ~309 s).

| Metric (test) | Hybrid QBoost [HW] | XGBoost |
|---|---|---|
| AUC-ROC | 0.8831 | 0.9770 |
| AUPRC | 0.6757 | 0.7090 |
| Precision | 0.792 | 0.857 |
| Recall | 0.384 | 0.606 |

Classical wins every metric. Also note both are well below TrueLoop's tuned ULB baseline (AUPRC 0.8937, AUC 0.9864), so this XGBoost configuration is under-tuned relative to the competitive reference.

## 2. SPECTRA datasets: CVQBoost vs XGBoost (ForrierWall, runs 2026-08-02)

Source: `ForrierWall\quantum_processes\photonic\output_files\*_summary.csv`. Real Dirac-3 rows only (the `xgboost_proxy` rows are a classical stand-in and prove nothing about quantum).

| Dataset | CVQBoost AUPRC [HW] | XGBoost AUPRC | Winner |
|---|---|---|---|
| energy_steel | 0.9866 | 0.9892 | Classical, narrowly |
| maintenance_ai4i | 0.5720 | 0.7887 | Classical, large gap |
| oilgas_gasturbine | 0.9708 | 0.9755 | Classical, narrowly |

Interesting detail: on ai4i the proxy arm (classical XGBoost inside the same sharded-ensemble structure) slightly beat plain XGBoost (AUPRC 0.8015 vs 0.7968). The ensemble structure is not the bottleneck; the Dirac QUBO solve under free-tier variable limits is.

## 3. QML Unlocked book datasets: QSVM and CVQBoost on Dirac-3 (2026-08-24 to 26)

Source: `qml-unlocked\DIRAC3.md`. All hardware-executed [HW], cheap (1 to 4 metered seconds each).

- Chapter 4 (PCA-2 pipeline): sign-augmented QSVM 0.987 AUC, matching classical baselines and beating the book's simulated QSVC (0.959). But a plain linear SVC on the identical pipeline also scores 0.987, so this is parity, not advantage.
- Chapter 10 Diabetes: QSVM 0.799 AUC, near logistic regression, beats CVQBoost (0.761).
- Chapter 10 Default: QSVM 0.707 AUC after sign augmentation, near logistic regression.
- Methodological finding with real value: the non-negative-weight constraint of Dirac-3 continuous variables requires sign-augmenting features (`[X, -X]`), discovered when un-augmented QSVM scored 0.18 AUC on anti-correlated features.

## 3b. FourierWall2: Harold's better-than-SMU results (read 2026-08-30, no re-runs; source `D:\Data\Harold\github\FourierWall2\docs\CVQBoost_Findings.md`, runs of 2026-08-04 on real Dirac-3)

The tuned CVQBoost configuration, found via a disciplined parameter sweep: `weak_cls_schedule=3` (feature triples; the accuracy lever), `num_samples=8`, `relaxation_schedule=2`, adaptive ridge `lambda_coef = 2 x n_train` per dataset, default full-depth weak learners, leak-free features, pinned seed 20260804, auto feature-reduction to the Dirac-3 ~940-variable ceiling.

Tuned 8-cell rollout on the four SPECTRA datasets (dual labels), CVQBoost vs XGBoost, [HW]:
- **In-segment (`in_pocket==1`, the hidden-structure slice, 7 valid cells): CVQBoost wins ROC 5/7 and PR 6/7.** This is the headline.
- Overall: XGBoost still generally stronger (CVQBoost overall wins ROC 2/8, PR 3/8), but CVQBoost wins overall outright on energy_steel both labels (ROC 0.993 vs 0.979; 1.0000 vs 0.9987).
- Tuning moved CVQBoost from "XGBoost sweeps 8/8 overall, ~3 in-segment metrics" (schedule=2 baseline) to "in-segment leader".

Measured QPU economics (Dirac-3, ~560-variable QUBO): tuned single fit 26 to 34 QPU seconds; full 7-cell rollout ~262 QPU seconds; whole tuning campaign ~800 QPU seconds. Account balance was 11,990 QPU seconds after the campaign (2026-08-04). A paid token lifts the free-tier ~100-variable limit to the ~940-qudit device ceiling.

Documented caveats (Harold's own, which is to the submission's credit):
1. Single stochastic runs; in-segment margins 0.01 to 0.07; repeats with mean and std are needed.
2. CVQBoost's in-segment train-test gap is 3 to 8x XGBoost's (worst: maintenance/target, 0.981 train to 0.592 test). The wins are real on the test split but fragile; more regularization or pool shrinkage is the identified fix.
3. XGBoost anchor is one fixed config, not the tuned GBDT trio of our protocol.

**Why this matters for HSBC:** the finding is a measured regime statement: the quantum-inspired ensemble wins inside structured sub-segments (where hidden coordinated structure lives) while the GBDT wins on the easy majority region. Mapped to fraud, the in-segment slice is the analogue of coordinated fraud campaigns. This is a direct, evidence-backed answer to the statement's secondary objective ("under what conditions do quantum approaches perform differently") that nobody in the public field has. Phase 1/2 job: replicate the in-segment effect with repeats and fair baselines, then test whether it transfers to fraud datasets with definable segments (Sparkov fraud categories, IEEE-CIS device or email cohorts).

Variable-count reality for fraud at schedule=3 (`n + C(n,2) + C(n,3) <= ~940` requires n <= 17): ULB's 30 features need reduction to 17, IEEE-CIS needs aggressive selection regardless. The QCi ask should cover both QPU seconds and the variable ceiling (see qci-sponsorship-request.md).

## 4. Assessment

**The on-disk evidence does not show any QML arm beating a tuned XGBoost on any dataset.** The recorded pattern is: classical wins, usually narrowly on easy datasets, decisively on hard imbalanced ones (fraud, ai4i). This matches TrueLoop's G1 gate and the published literature.

**What we genuinely have that TrueLoop does not:**
1. Real hardware execution already done. TrueLoop's Phase 1 is 100% simulation. We have [HW] rows on a commercial quantum-photonic device (Dirac-3) across six datasets, with measured costs.
2. A working two-mode pipeline (local proxy vs hardware) with cost-control discipline.
3. Documented, honest methodological findings (sign augmentation, free-tier variable-limit backoff, sharded-ensemble structure effects) that read as exactly the "under which conditions" evidence the HSBC statement asks for.
4. A second hardware paradigm: Dirac-3 is an entropy/photonic optimizer, complementary to the gate-based devices (Braket) the statement names. Compliance note: verify whether the statement requires Braket or merely suggests it; if required, position Dirac-3 results as supplementary [HW] evidence and gate-based work as the Phase 2 Braket plan.

## 3a. Published CVQBoost evidence (read 2026-08-29, from `D:\Data\Harold\0.Quantum\`)

**QCi paper (Emami et al., arXiv:2503.11273), ULB fraud.** XGBoost wins AUC in 23 of 24 cells across four balancing strategies and six class ratios. The single CVQBoost win: ADASYN at ratio 1.0, 0.8855 vs 0.8826. The paper's real claim is training-time scaling: CVQBoost stays ~2s (Dirac-3 solve ~1.3s) while XGBoost grows to 117s (1 core), 4.2s (8 cores), 3.6s (GPU) at 150k rows; at 1M to 70M synthetic rows and 100 to 900 features, CVQBoost scales linearly while XGBoost grows quadratically, beating even 48-core and 4x L4 GPU setups. Uses AUC only, not AUPRC. Public code: github.com/qci-github/eqc-studies (CVQBoost).

**SMU/OCBC paper (Loke, Sahoo, Guan, Xu, Verma, Griffin, March 2026), ULB fraud. This is the source of the "beats classical" claim.** CVQBoost on Dirac-3 with a heterogeneous weak-classifier pool. Best arm, KNN weak learners: **AUC-PR 0.8108, AUC-ROC 0.9821** (10 seeds, 70/30 split, SMOTE on train only, threshold calibrated on validation resamples). They beat the best published baseline they cite, CAD, a semi-supervised anomaly detector (0.7423 AUC-PR, 0.9734 AUC-ROC), by +0.0685 AUC-PR (~9.2% relative). Other arms: XGB weak learners 0.757, LG 0.673, LDA 0.660 AUC-PR. Dirac-3 solve <10s; KNN weak-classifier construction dominates cost (378s, classical).

**Honest assessment of the SMU result.** It is a genuine, published, hardware-executed AUPRC result, and it is reproducible with the exact stack Harold already has (`eqc_models` QBoostClassifier supports knn/lda/lg/xgb weak learners per `qml-unlocked\DIRAC3.md`). But its baseline is the semi-supervised anomaly-detection literature, not tuned supervised GBDTs: published supervised baselines on ULB are higher (XGB+SMOTE AUPRC 0.867 per IIETA 2024, cited in the HSBC statement itself; TrueLoop's tuned XGBoost 0.8937). A reviewer will notice this immediately. So the claim we can carry into the proposal after reproduction is: "CVQBoost with heterogeneous weak learners beats the published semi-supervised anomaly-detection SOTA on AUPRC and approaches tuned supervised GBDTs at a fraction of the training-scaling cost," plus whatever our own head-to-head shows. Whether CVQBoost-KNN can beat OUR tuned GBDT trio under one protocol is exactly preregistered hypothesis H1.

**Status of the QML-beats-XGBoost claim (updated 2026-08-29):** Harold confirms the winning algorithms are not in the repositories on this computer, and that he has beaten the XGBoost results elsewhere. Status: claimed, not yet reproduced in this project. Plan: rebuild the winning configuration inside this repo during Stage 3 and re-run it under the preregistered protocol against tuned XGBoost, LightGBM, and CatBoost. Only reproduced numbers go into the proposal. Inputs needed from Harold when ready: which dataset, which model and configuration (knobs, features, encoding), which metric the win was on, and the split protocol used. If the win reproduces, it becomes the headline [SIM]/[HW] result; if it does not reproduce under fair conditions, the regime-map framing carries the submission unchanged.

## 5. Hardware budget rule (standing)

Dirac-3 time is limited and metered. All development runs use `USE_DIRAC_EQC=0` (local proxy). Every metered run requires Harold's explicit approval, with the expected number of Dirac calls stated in advance. Reserve hardware for final, preregistered [HW] rows only.
