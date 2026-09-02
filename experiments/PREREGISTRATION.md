# Preregistration v1.1 (FROZEN)

Status: FROZEN, approved by the team lead 2026-08-30. Supersedes v1.0 after a structured review: two independent model reviews, a full-paper reading of the six methodology references, and a primary-source methods research pass (adjudication record: `docs/prereg-review-adjudication.md`; research report: `docs/research-baselines-best-practices.md`). From this point, changes are recorded as dated amendments per section 11, never silent edits. Analysis code in `experiments/src/` freezes at the same commit.

## Amendment log

- 2026-08-30 (A1): Freeze recorded. Freeze commit `95751b9`, tag `prereg-freeze`. This amendment adds only this log line; no protocol content changed.
- 2026-09-02 (A2): Variable-count formula corrected (implementation-accuracy fix, team-lead approved). Section 10's `vars = n + C(n,2) [+ C(n,3)]` overstates by n for the build we run: the sequential weak-classifier strategy (mandatory on Windows; used for all prior measured evidence) caps pairs at the top-|correlation| n(n-3)/2 (eqc-models `_build_weak_classifiers_sq`), giving true totals C(n,2) at schedule 2 and C(n,2)+C(n,3) at schedule 3. Confirmed exactly by FourierWall2 measured hardware runs (n=15: 105 vars at schedule 2, 560 at schedule 3). Device ceiling: QCi documents 949 (Dirac-3 Developer Beginner Guide, "device limit (currently 949)"), replacing the ~940 estimate; largest fit verified by us remains 816 (n=17, schedule 3). No gate, budget, bound, or cell changes: free tier n<=13 and device n<=17 both stand under either formula (n=18 exceeds 949 under both builds). `qubo_vars` in experiments/src/data.py corrected in this amendment's commit per the section 11 analysis-code rule; section 10's formula line updated with an (A2) marker.
- 2026-09-02 (A3): Full-pair CVQBoost build added as a preregistered side-by-side option (team-lead directed: "the untested weak learners could prove to be an additional advantage"). The multi_processing strategy (Linux/WSL2 only; fork-based) builds ALL C(n,2) pairs where sequential builds the top-correlated n(n-3)/2, i.e. n additional weak learners and n additional QUBO variables. Bounds hold for both builds (free tier: n=13 full-pair = 91 <= 100; device: n=17 full-pair = 833 <= 949). Procedure: (1) both builds are constructed on identical training data with otherwise identical configuration (same weak_cls_type, params, seeds) and compared via the PROXY solve (ADR-0002 non-negative ridge) on VALIDATION AP across the 10 primary seeds, ULB matched features -- zero metered seconds; (2) the build with higher mean validation AP is selected BEFORE any test-set evaluation and applied uniformly to every CVQBoost cell (proxy and hardware); the non-selected build is reported as exploratory; (3) an optional hardware confirmation (one fit per build, same seed/config) may be charged to the section 10 contingency line, gated on Criterion H team-lead approval like every metered run; (4) every results.json row records the build (`pair_build`: sequential | full) inside its config; proxy and hardware always use the identical pool, preserving G0b and the H4 structural-control identity. This amendment adds an option; it changes no gate criterion, no budget, and no existing cell.

## 1. Central claims under test

Working theory: the Dirac-3 CVQBoost pipeline delivers (a) detection quality competitive with tuned gradient-boosted baselines, with measured wins inside structured sub-segments, (b) training-time scaling advantages as rows and features grow, and (c) representation-conditioned behavior that differs from classical models under quantum-native (phase) feature engineering. The submission's goal is best achievable detection plus an honest map of where the quantum-inspired component earns its place.

**Compound falsification criterion.** The central theory is considered unsupported if ALL of the following hold: H1b fails on the primary endpoint, the H3 dose-response slope is not positive, and H5 does not transfer to any fraud segment. In that case the submission's headline becomes the measured regime map and boundary statement, a pre-committed fallback, not a post-hoc pivot.

**Provenance disclosure.** H5 and the starting quantum configuration derive from a prior exploratory sweep (FourierWall2 campaign, 2026-08-04) on SPECTRA data that block B4 partially reuses. They are exploratory-derived hypotheses given a confirmatory test here, not blind predictions. Any configuration re-tuning for fraud segments uses its own held-out split and never touches transfer-test data.

## 2. Datasets

| Role | Dataset | Notes |
|---|---|---|
| Primary endpoint + calibration | ULB European Cardholder (`XGBvHQXGB\datasets\creditcard.csv`, 284,807 rows, 492 frauds, 0.172%) | Corroborated clean-protocol reference band: AUPRC 0.85-0.88, AUC-ROC 0.97-0.98 (see research report; results above ~0.95 AUPRC in the literature are leakage artifacts). Spans 2 days, so temporal splitting is a stated-weak sensitivity check. |
| Scaling and regime headline (exploratory) | IEEE-CIS (Kaggle, 590,540 train rows, 3.5% fraud) | Competition published AUC-ROC only (winner 0.9459 private); leakage-free reproduction band AUPRC 0.64-0.67 is the honest reference and is attributed to the reproduction, never to the competition. |
| Pipeline-correctness check only | Sparkov (Kaggle shipped fraudTrain/fraudTest temporal split) | Saturated at AUC-ROC 0.995-0.998; deterministic generator. Declared in advance: no substantive fraud-performance conclusions rest on it. |
| External-validity replication (NOT fraud evidence) | SPECTRA quantum-ready datasets (4 Kaggle datasets, CC BY 4.0), published at https://www.kaggle.com/javierfalcondale/datasets: spectra-energy-quantum-ready-steel-plant-data, spectra-oil-and-gas-quantum-ready-gas-turbine-data, spectra-maintenance-quantum-ready-failure-data, spectra-telecom-quantum-ready-churn-data | Used only for the H5(i) replication of the prior in-segment result; results reported as replication of a structural finding, never as fraud evidence. Cite both the releases and their original UCI substrates (851, 551, 601, 563) per docs/references.md. |

AUPRC baselines equal prevalence (ULB 0.0017, IEEE-CIS 0.035, Sparkov ~0.057); prevalence is reported beside every AUPRC value, and AUPRC is never compared or averaged across datasets.

## 3. Hypotheses and gates

**Confirmatory structure.** There is exactly ONE primary confirmatory endpoint (H1b-primary). All other hypotheses and cells are exploratory: reported with Holm-adjusted intervals across the K exploratory cells actually run, K fixed at freeze time in section 10, and labeled exploratory in the proposal.

- **G0 (pipeline honesty gate):** mean AUPRC of tuned XGBoost across the 10 stratified ULB seeds (full features, weighting-only) reaches >= 0.85, the bottom of the corroborated clean band. Below that, the pipeline is presumed defective and everything halts. TrueLoop's 0.8937 is a reference under an unverified protocol, not the gate. **G0c:** ULB preprocessing is fixed in advance: `Time` retained as a raw feature and as a time-of-day phase (QFE arm), `Amount` log-transformed, no row dropped except exact duplicates (counts reported).
- **G0b (proxy fidelity gate):** the top-3 and bottom-2 proxy-ranked CVQBoost configurations each run once on Dirac-3 (5 budgeted fits). If the Spearman rank correlation between proxy and hardware AUPRC is < 0.5, proxy-selected configurations are declared non-transferable, and all hardware results are reported as single-config points with no tuning claim.
- **H1a (reproduction, exploratory):** the SMU/OCBC CVQBoost configuration (heterogeneous KNN/LDA/LG/XGB weak-classifier pool) reproduces AUC-PR >= 0.80 on ULB under the SOURCE paper's protocol (70/30 split, train-only SMOTE, 10 seeds), run and reported as a labeled reproduction, separate from all house-protocol tables.
- **H1b-primary (THE confirmatory endpoint):** on ULB, stratified protocol, matched top-k feature set, the best preregistered CVQBoost configuration beats the best of the tuned GBDT trio on AUPRC. Decision statistic: per-seed paired delta-AP on identical test rows; decision rule: the t-interval on the across-seed mean (10 seeds) excludes zero; per-seed paired stratified BCa CIs (2,000 resamples) reported as support. Executed on Dirac-3 hardware if access permits; otherwise evaluated on the proxy, labeled [SIM], with the [HW] confirmation deferred to Phase 2 under this committed grid. The gate's status is never ambiguous.
- **H1b-exploratory:** the same comparison on IEEE-CIS and on the temporal protocols, reported with Holm adjustment.
- **H1c (training economics, exploratory):** fit log(training time) = a + b log(n_rows) over the row ladder {25k, 50k, 100k, 200k, and 400k on IEEE-CIS} at fixed feature count, per arm. Passes if CVQBoost's slope b is below every GBDT's slope with non-overlapping 95% CIs. Hardware disclosed (CPU model, cores, GPU if any); GBDTs timed at 1-core and all-core; CVQBoost wall-clock INCLUDES weak-learner construction and Hamiltonian build, with the Dirac solve time also broken out.
- **H2 (expected null, exploratory):** on ULB full-feature unmatched comparisons, the GBDT ceiling stands. A CVQBoost win here would be reported but treated as surprising.
- **H3 (regime dose-response, exploratory):** on ULB and IEEE-CIS separately, run the frozen CVQBoost config and best GBDT at k in {5, 9, 13, 17} matched features; report the slope of delta-AUPRC vs k with a seed-clustered CI. Scored only if at least 3 ladder cells per dataset run; otherwise reported descriptively.
- **H4 (structural attribution, exploratory):** CVQBoost minus the BEST structural control, per cell. Controls: the identical weak-learner output matrix with weights fit by (i) non-negative ridge with lambda tuned over the same grid as CVQBoost's lambda_coef, and (ii) a non-negative sparse (L1) variant. Only this delta may be attributed to the Dirac solve.
- **H5 (in-segment advantage, exploratory-derived):** (i) replicate the SPECTRA in-segment result with 5 seeds on the 3 strongest cells, reporting mean, std, CIs; (ii) transfer test on fraud: segments defined a priori on train-only statistics by frozen predicates computable without labels at inference (Sparkov fraud-category pockets; IEEE-CIS device/email cohorts), evaluated in-segment vs overall for every arm, with a matched random-segment control (same size and base rate; the reported edge is in-segment minus random-segment) and a minimum of 50 test positives per scoreable cell; (iii) track the in-segment train-test generalization gap and test whether stronger regularization closes it without losing the win.
- **H6 (representation effect, exploratory):** the QFE phase representation (exact Fourier Wall recipe: rank phases, log magnitudes first, calendar cycles, train-only whitening, low-cardinality phases excluded from encoded blocks) is given to EVERY arm. Question: does it shift the quantum-minus-classical delta? Every H6 cell's classical bar includes trained-frequency GAM, GA2M, and an order-matched JOINT twin (supervised k-way cosine search fit by logistic regression) in addition to the GBDTs, per the Fourier Wall's demonstration that omitting the twin manufactures fake quantum wins.

Null results are published as nulls. All gates are scored as committed in the scoring table (section 11).

## 4. Model arms

| Arm | Specification |
|---|---|
| XGBoost, LightGBM, CatBoost | Tuned per section 6. NaN passed through natively (no sentinel imputation); library categorical handling used explicitly; CatBoost `boosting_type` set explicitly (Ordered claimed only if set); early stopping on a dedicated validation fold, never test; stopping iteration, patience, and monitored metric reported. |
| Logistic regression | Floor control, matched features. |
| CVQBoost (QBoostClassifier, Dirac-3) | Heterogeneous weak pool (KNN, LDA, LG, shallow XGB) and the FourierWall2 tuned settings as the starting configuration: schedule 3 where variables fit, num_samples=8, relaxation_schedule=2, lambda_coef = 2 x n_train, default weak learners, `weak_cls_strategy="sequential"` on Windows. All tuning on the proxy. |
| Structural controls / proxy | The identical QUBO objective solved classically: non-negative ridge (and L1 variant) over the same weak-learner outputs. Serves as both the tuning proxy and the H4 attribution control. |
| Trained-frequency GAM, GA2M, JOINT twin | H6 cells only; JOINT = few k-way cosine terms found by supervised coarse-to-fine frequency scan, fit by logistic regression. |
| Gate-based arm (Braket simulator, [SIM]) | PHASE-ACTIVE encoding only (sandwich or entangling encoding); plain Ry angle encoding is banned as provably classical (Inverse Born Rule). The arm's phase complexity C, Berry-connection magnitude, and mode mutual information are computed and reported as evidence the quantum framing is non-superficial. |
| QSVM (sign-augmented primal, Dirac-3) | Cheap secondary arm, ~1 metered second per fit. |

## 5. Feature handling and leakage controls

1. Every transform (scaling, encoding, imputation, MI selection, whitening, aggregation) is fit on training data only, inside a fitted pipeline, per fold.
2. Feature selection runs inside the CV loop (Cawley-Talbot).
3. **IEEE-CIS reduced recipe, preregistered:** D-column time normalization (Dn = D - TransactionDT/86400 for D1, D2, D4, D10, D11, D15); one UID = card1 + addr1 + floor(day - D1), the UID itself EXCLUDED from the model; UID aggregations limited to this named list: TransactionAmt mean and std, C1-C14 means, D4/D9/D10/D15 aggregates; frequency encodings of card1_addr1 and card1_addr1_P_emaildomain; V-column reduction by missing-pattern grouping and within-group correlation (>0.75, keep highest cardinality). No client-mean post-processing; no model blending.
4. Time-consistency filter (single-feature train-early/test-late AUC must exceed 0.5) and adversarial validation (target AUC near 0.5, recursively dropping top adversarial features) both run inside training folds only.
5. Temporal protocols: aggregates use only rows strictly before the split boundary; no identifier column enters any model raw.
6. Positive control: shuffled-label run must collapse test AUPRC to the base rate; reported.
7. Exact duplicates removed before splitting; counts reported per dataset.

## 6. Tuning protocol and budget equivalence

- Equal budget: 100 Optuna TPE trials per arm per dataset (literature anchors: Grinsztajn ~400 random-search iterations; Shwartz-Ziv 1,000; McElfresh 30; the "60 trials" folklore is verified absent from Bergstra-Bengio and is not cited). Logistic: 25 trials.
- GBDT search spaces as in v1.0 (unchanged); optimization target average precision; early-stopping on `aucpr`/`average_precision`/`PRAUC`, headline numbers always from `average_precision_score`.
- CVQBoost tunes on the PROXY only (section 4), equal trial budget, over weak pool composition, schedule, k, lambda alpha in {0.5, 1, 2, 4}; num_samples and relaxation_schedule are FIXED from prior hardware evidence and not tuned.
- A Tuning Budget Equivalence table is published: trials, model fits per trial, and wall-clock CPU-hours per arm, reported as-is with the asymmetry acknowledged.

## 7. Class imbalance

Weighting only in house protocol (`scale_pos_weight` / `auto_class_weights`; exactly one mechanism per library). No resampling on top of weighting, ever; no resampling before splitting, ever. H1a's SMOTE (train-only, inside folds) is an isolated labeled reproduction. Because weighting degrades probability calibration, an uncorrected variant of the best GBDT is reported alongside for the calibration section.

## 8. Evaluation protocols and splits

1. **Stratified (primary):** ULB 60/20/20, stratified, seeds {42..51} for the primary cell (10 seeds; splits vary with seed per Bouthillier), {42..46} for exploratory cells.
2. **Temporal:** IEEE-CIS: GroupKFold by calendar month with 3-fold rolling-origin evaluation. Sparkov: the shipped fraudTrain/fraudTest split. ULB: single 70/10/20 time-ordered split, labeled a sensitivity check (2-day span; stated, not overclaimed).
3. A minimum-detectable-effect statement is computed from pilot seed variance before hardware runs; observed margins below the MDE are reported as indistinguishable, not as wins.

## 9. Metrics and statistics

- AUPRC primary, computed as step-wise `average_precision_score` (never trapezoidal); tie-frequency check reported, cross-checked against a second implementation if ties are common. AUC-ROC secondary. Prevalence beside every AUPRC.
- Thresholded metrics (F1, precision, recall, confusion matrix) at two validation-chosen operating points: max-F1, and a fixed alert budget (card precision at k). Wilson intervals for precision and recall; bootstrap for F1. Validation-to-test threshold drift reported as a robustness metric under temporal protocols.
- CIs: stratified BCa bootstrap, 2,000 resamples. Paired comparisons: identical resample indices on both arms' predictions.
- Within-dataset model comparisons: paired tests on identical folds and seeds (corrected resampled t-test or 5x2cv where refits allow; DeLong for AUC-ROC pairs; paired bootstrap for AUPRC). No cross-dataset omnibus test at N=3; no cross-dataset averaging of any metric. Holm correction across the K exploratory cells; effect sizes reported with every interval.
- Calibration: fit on a held-out fold via CalibratedClassifierCV; Platt scaling where positives are scarce (ULB), isotonic where supported (IEEE-CIS); reliability diagrams plus ECE with equal-mass binning and a stated bin count; Brier reported only as a joint score, never as a calibration measure.
- Every quantitative claim carries an evidence tag: [HW], [SIM], or [PROJ].

## 10. Phase 1 hardware run grid v2 (the only metered runs; each block requires team-lead approval)

Variable budget (corrected by A2; side-by-side build option added by A3): sequential build vars = C(n,2) at schedule 2, C(n,2) + C(n,3) at schedule 3; full-pair build adds n. Free tier ~100 vars (n <= 13 at schedule 2, 78 sequential / 91 full-pair); documented device ceiling 949 (n <= 17 at schedule 3, 816 sequential / 833 full-pair).

| Block | Runs | Est. QPU s | Gated on |
|---|---|---|---|
| B1: ULB free-tier configs (top-13, schedule 2, 78 vars), 2 pool variants x (10-seed primary + temporal sensitivity) | 22 fits | ~300-600 | current ~500 s balance |
| G0b: proxy-fidelity fits (top-3 + bottom-2 configs) | 5 fits | ~100 | current balance or grant |
| B2: ULB full config (top-17, schedule 3, 833 vars), 10-seed primary + temporal | 11 fits | ~450 | QCi grant |
| B3: IEEE-CIS reduced-recipe subset, full config, 5 seeds x 2 protocols + H3 ladder cells (k in {5,9,13,17}, 5 seeds at k=17 already counted; 3 extra k x 2 seeds) | 16 fits | ~650 | QCi grant |
| B4: SPECTRA replication, 3 strongest in-segment cells x 5 seeds | 15 fits | ~450 | QCi grant + SPECTRA re-download |
| B5: QSVM arms | 12 fits | ~15 | current balance |
| Contingency (~15%; errored solves retried at most twice, retries counted) | | ~350 | |
| **Total** | **81 fits** | **~2,300-2,600** | |

Granted-seconds spend priority: B3 > B2 > H3 ladder > B4 > contingency. K (the number of exploratory cells for Holm) is fixed at freeze as the count of scoreable cells in this grid. If no grant arrives by Sep 8: B1, G0b (partial), B5 run on the current balance; H1b-primary is evaluated on the proxy as [SIM]; B2-B4 enter the proposal as [PROJ] with this grid cited as the committed plan; the proposal is submitted regardless.

## 11. Scoring, amendments, and deviations

- **Gate table:** every gate/hypothesis is published in a table with columns Gate, Prediction, Outcome (pass / fail / null / unscoreable), Evidence tag, Amendment ref. Nulls included.
- **Amendments** may add exploratory analyses or fix implementation bugs, with date and reason. They may NEVER change a gate's pass/fail criterion, add cells to an existing hypothesis after its data is observed, or remove an observed hypothesis; any such change is a reported DEVIATION.
- **Analysis code freeze:** metric and analysis code freezes at the same commit as this file; later changes are dated amendments.
- **Failed runs:** an errored hardware solve is retried at most twice with identical config and seed; retry counts reported per cell; three failures = the cell is reported as failed, never silently dropped.
- **results.json schema (required keys):** arm, dataset, protocol, seed, config_hash, features_used, metrics (all of section 9), evidence_tag, metered_seconds, retry_count, timestamps.

## 12. Reproducibility and freeze procedure

Pinned environment (library versions shift GBDT results measurably), fixed seeds, all configs and results in results.json, public repository at Stage 7 after the confidentiality scan.

Freeze: (1) the team lead reviews and approves; (2) `git init` if needed, commit this file plus `experiments/src/`, record the commit hash here by amendment; (3) amendments only thereafter, per section 11.
