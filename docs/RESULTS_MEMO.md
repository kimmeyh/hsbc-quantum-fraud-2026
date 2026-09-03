# Results Memo (Phase 1 evidence base) -- DRAFT, Sprint 4 Task D (F7)

**Purpose**: The one-page evidence summary the paper is written from; gate table scored as committed; headline-framing options for the team lead's Class-2 decision.
**Audience**: Team lead (gate review); Sprint 5 paper drafting.
**Last Updated**: 2026-09-03 (tuned-proxy and hardware sections fill in as Sprint 4 completes)

Every number is [SIM] unless tagged otherwise and traces to `experiments/results/results.json` by config_hash via `gate_report.md`. Prevalence (test fold) = 0.00167 beside every AUPRC.

## Gate table (scored as committed; PREREGISTRATION section 3, amendments A1-A6)

| Gate | Prediction | Outcome | Evidence | Amendment ref |
|---|---|---|---|---|
| G0 | Tuned-XGB full-feature mean test AUPRC >= 0.85 (10 seeds) | **FAIL**: 0.8296, t-95% CI [0.8092, 0.8501] | [SIM] gate_report | none (criterion unchanged) |
| G0 leakage tripwire | No cell > 0.95 AUPRC | PASS: max cell mean 0.8368 (CatBoost/full) | [SIM] | -- |
| G0b | Proxy-vs-hardware config rank Spearman >= 0.5 (top-3 + bottom-2 free-tier configs) | PENDING: needs F22 ranking + B1/G0b hardware approval | [PROJ] until run | A2 (variable counts), A3 (build) |
| H1a | SMU reproduction AUC-PR >= 0.80 | NOT YET RUN | [PROJ] | -- |
| H1b-primary | Best CVQBoost vs best tuned GBDT, matched top-k, paired per-seed delta-AP, 10 seeds | MACHINERY VERIFIED, ENDPOINT PENDING hardware: starting-config proxy delta = -0.0415 [CI -0.0608, -0.0222]; tuned-proxy delta = (fill from F22) | [SIM] | A5 (MDE 0.0268) |
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
| CVQBoost proxy, starting config (free, dct, full-pair) | 0.7681 | 0.0312 | [0.7458, 0.7905] | 0.9210 |
| CVQBoost proxy, tuned (F22) | (fill) | | | |
| Logistic / full | 0.7218 | 0.0268 | [0.7026, 0.7410] | 0.9769 |

Untuned pilot (Sprint 1): XGBoost 0.8268. Tuning at the frozen 100-trial budget moved XGBoost by +0.003 on test (CV optimism 0.8555 -> 0.8296). Dedupe-before-split removed 1,081 rows. lg-pool proxy rows are quarantined (degenerate scores) pending F22.

## What the evidence says (plain terms)

- The tuned classical baselines are solid and clean: no leakage flags, tight seed CIs, ordering CatBoost > XGBoost > LightGBM.
- They land ~0.02 below the literature band we preregistered as the floor. F21 (research memo) explains why (duplicate handling and split protocol are the leading candidates) and proposes what, if anything, to amend as a labeled sensitivity analysis.
- The quantum arm's proxy (identical Hamiltonian, classical solve) at its starting configuration trails the best matched GBDT by 0.04. The tuned proxy result (F22) is the number that matters for H1b; the hardware number requires B1/G0b approval.
- The build side-by-side (A3) favored the full-pair pool by a noise-level margin; it is the selected build.

## Headline-framing options (Class-2 decision for the team lead; nothing chosen here)

1. **Regime-map framing (pre-committed fallback, prereg section 1)**: "A preregistered, leakage-controlled benchmark of quantum-inspired boosting against tuned GBDTs, with a measured map of where CVQBoost does and does not earn its place." Honest under every current number; strongest on Validation and Technical Approach; weakest on the quantum-wins narrative.
2. **Hybrid-system framing**: "Best achievable detection is the tuned classical ensemble; CVQBoost is positioned as the in-segment specialist and the hardware-scaling arm, with Phase 2 evidence targets." Consistent with the team lead's stated goal (better predictions, quantum or not) and the QSTAR hybrid-routing citation; requires the H5/H3 [PROJ] blocks to be described as the Phase 2 program.
3. **Conditional quantum-advantage framing**: only defensible if the F22 tuned proxy or the hardware rows close the gap on the primary endpoint; otherwise it overclaims. Decide after F22 lands.

Recommendation is withheld until the F22 numbers are in; the decision is yours at validation.

## Statistical review checklist walk

Deferred to the end of Sprint 4 (walked line by line before this memo is declared final).
