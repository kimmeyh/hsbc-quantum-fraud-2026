# Results Memo (Phase 1 evidence base) -- DRAFT, Sprint 4 Task D (F7)

**Purpose**: The one-page evidence summary the paper is written from; gate table scored as committed; headline-framing options for the team lead's Class-2 decision.
**Audience**: Team lead (gate review); Sprint 5 paper drafting.
**Last Updated**: 2026-09-03 (F22 tuning complete; hardware blocks pending approval)

Every number is [SIM] unless tagged otherwise and traces to `experiments/results/results.json` by config_hash via `gate_report.md`. Prevalence (test fold) = 0.00167 beside every AUPRC.

## Gate table (scored as committed; PREREGISTRATION section 3, amendments A1-A6)

| Gate | Prediction | Outcome | Evidence | Amendment ref |
|---|---|---|---|---|
| G0 | Tuned-XGB full-feature mean test AUPRC >= 0.85 (10 seeds) | **FAIL as committed**: 0.8296, t-95% CI [0.8092, 0.8501]. Footnote: the 0.85 threshold derived from a literature band that primary-source research (F21) could not corroborate; A7 sensitivity cells proposed | [SIM] gate_report | none (criterion unchanged); A7 proposed |
| G0 leakage tripwire | No cell > 0.95 AUPRC | PASS: max cell mean 0.8368 (CatBoost/full) | [SIM] | -- |
| G0b | Proxy-vs-hardware config rank Spearman >= 0.5 (top-3 + bottom-2 free-tier configs) | PENDING: needs F22 ranking + B1/G0b hardware approval | [PROJ] until run | A2 (variable counts), A3 (build) |
| H1a | SMU reproduction AUC-PR >= 0.80 | NOT YET RUN | [PROJ] | -- |
| H1b-primary | Best CVQBoost vs best tuned GBDT, matched top-k, paired per-seed delta-AP, 10 seeds | MACHINERY VERIFIED; PROXY ENDPOINT MEASURED: selected-config proxy (full-pair) minus CatBoost matched-13 = -0.0389 [CI -0.0574, -0.0203], 10 seeds; |delta| = 0.039 > MDE 0.0268, so the proxy is distinguishably BEHIND on this endpoint. Hardware endpoint pending B1 approval | [SIM] | A5 (MDE 0.0268) |
| H3 | Dose-response slope over k in {5,9,13,17} | NOT YET RUN (IEEE-CIS cells: F3) | [PROJ] | -- |
| H4 | CVQBoost minus best structural control (proxy) | Structural control = the proxy itself; delta measurable only once hardware rows exist | [PROJ] | A3 (pool identity) |
| H5 | In-segment advantage, SPECTRA replication + fraud transfer | NOT YET RUN (F5/F24) | [PROJ] | -- |
| H6 | QFE phase representation shifts the delta | NOT YET RUN (F4/F23) | [PROJ] | -- |

## Per-arm summary (ULB, stratified 60/20/20, 10 seeds, test AUPRC; prevalence 0.00167)

| Arm / cell | Mean AP | Seed SD | 95% t-CI | Mean AUC-ROC |
|---|---|---|---|---|
| CatBoost / full | 0.8368 | 0.0304 | [0.8150, 0.8585] | 0.9765 |
| XGBoost / full | 0.8296 | 0.0286 | [0.8092, 0.8501] | 0.9791 |
| LightGBM / full | 0.8240 | 0.0295 | [0.8029, 0.8451] | 0.9788 |
| CatBoost / matched-13 | 0.8070 | 0.0321 | [0.7841, 0.8300] | 0.9738 |
| LightGBM / matched-13 | 0.8024 | 0.0274 | [0.7828, 0.8220] | 0.9726 |
| XGBoost / matched-13 | 0.8019 | 0.0239 | [0.7847, 0.8190] | 0.9730 |
| CVQBoost proxy, SELECTED config = preregistered starting config (free, dct, full-pair; 91 vars) | 0.7681 | 0.0312 | [0.7458, 0.7905] | 0.9210 |
| CVQBoost proxy, F22 tuned best-healthy (lg balanced, k=9, sched 2, alpha 0.5, full-pair; 45 vars) | 0.7039 | 0.0229 | [0.6875, 0.7203] | 0.9560 |
| Logistic / full | 0.7218 | 0.0268 | [0.7026, 0.7410] | 0.9769 |

Untuned pilot (Sprint 1): XGBoost 0.8268. Tuning at the frozen 100-trial budget moved XGBoost by +0.003 on test (CV optimism 0.8555 -> 0.8296). Dedupe-before-split removed 1,081 rows. F22 tuning (100 trials, section 6): best trial 0.6873 validation AP vs the starting config's 0.7232 on the tuning seed, so by the validation-AP rule the STARTING config stays selected; the tuned lg config is the best HEALTHY config (score_health clean: mode share 0.53, ~3,800 distinct scores) and lifts the lg quarantine, but scores lower. The TPE sampler spent 73/100 trials on lg configs (reported as-is). KNN weak learners were excluded on proxy cost (deviation noted).

## What the evidence says (plain terms)

- The tuned classical baselines are solid and clean: no leakage flags, the shuffled-label positive control collapses to base rate (AP 0.0023 vs prevalence 0.0017), tight seed CIs, ordering CatBoost > XGBoost > LightGBM.
- They land ~0.02 below the literature band we preregistered as the floor. F21's primary-source research (docs/research-ulb-baseline-protocols.md) found the band itself is not corroborated: its probable origin computes trapezoidal PR-AUC (banned by our section 9 as too optimistic), trains on 90% of the data with no held-out test fold, and keeps duplicates; the clean-protocol equivalent is ~0.80-0.81, and a step-wise-AP benchmark (AutoXGB) reports 0.78. Our 0.8296 exceeds both. G0 stays FAIL as committed; F21 proposes amendment A7 (three zero-metered exploratory sensitivity cells: metric definition S1, duplicate retention S2, split ratio S3) for the team lead's disposition. Implementation note for S1: the runner does not persist predictions, so S1 needs either a prediction dump added to the refit stage or a deterministic re-run (~1.5h unattended).
- The quantum arm's proxy (identical Hamiltonian, classical solve) trails the best matched GBDT by 0.039 (CI excludes zero; larger than the 0.0268 MDE) at its selected configuration, and section-6 tuning did not close the gap. One structural fact shapes what hardware can add here: the CVQBoost Hamiltonian is a strictly convex quadratic (J = HH^T + lambda*I with lambda > 0) on the simplex, so the classical proxy returns its GLOBAL optimum; Dirac-3 solving the identical objective can match it but cannot exceed it. On this primary endpoint, therefore, any measured hardware advantage would have to come from solver stochasticity (num_samples) or scaling/time (H1c), not from solution quality -- and G0b should show high proxy-hardware rank agreement for the same reason. The FourierWall2 in-segment wins were wins of the CVQBoost model form over XGBoost, not of the solver over its proxy.
- The build side-by-side (A3) favored the full-pair pool by a noise-level margin; it is the selected build.

## Headline-framing options (Class-2 decision for the team lead; nothing chosen here)

1. **Regime-map framing (pre-committed fallback, prereg section 1)**: "A preregistered, leakage-controlled benchmark of quantum-inspired boosting against tuned GBDTs, with a measured map of where CVQBoost does and does not earn its place." Honest under every current number; strongest on Validation and Technical Approach; weakest on the quantum-wins narrative.
2. **Hybrid-system framing**: "Best achievable detection is the tuned classical ensemble; CVQBoost is positioned as the in-segment specialist and the hardware-scaling arm, with Phase 2 evidence targets." Consistent with the team lead's stated goal (better predictions, quantum or not) and the QSTAR hybrid-routing citation; requires the H5/H3 [PROJ] blocks to be described as the Phase 2 program.
3. **Conditional quantum-advantage framing**: only defensible if the F22 tuned proxy or the hardware rows close the gap on the primary endpoint; otherwise it overclaims. Decide after F22 lands.

**Recommendation (now that F22 is in)**: option 1 (regime map) as the spine with option 2 (hybrid system) as the positioning -- both are fully honest under the measured numbers, both align with the stated goal (best predictions, quantum or not), and both are strengthened, not weakened, by the convexity argument (it is a genuine methodological contribution: a preregistered structural control that bounds what a quantum solver can add). Option 3 is not defensible on the ULB primary endpoint. The decision is yours at validation.

## Statistical review checklist walk

Walked 2026-09-03 (see the Sprint 4 validation package); items marked DONE / N/A / OPEN with evidence.
