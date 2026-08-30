# Maximizing Predictions from CVQBoost: Cumulative Findings

Summary of what we learned tuning the hybrid quantum **CVQBoost**
(`eqc_models.QBoostClassifier` on QCi **Dirac-3**) against classical **XGBoost** on the
four SPECTRA datasets. Last updated 2026-08-04, covering the full parameter sweep, the
tuned 8-run rollout, and the in-segment generalization analysis. Sections: 1-2 mechanism &
leakage; 3-5 parameters, QPU cost, variable ceiling; 6/10 results; 11 overfitting; 12 plots.

All experiments use the leak-free feature protocol and, where noted, a pinned seed
(`FIXED_RUN_SEED = 20260804`) so runs differ only by the knob under test.

---

## 1. How CVQBoost works, and why it trails XGBoost

**CVQBoost (QBoost on Dirac-3):**
1. Builds a pool of **weak classifiers**, each an XGBoost trained on a small feature
   subset: single features (`weak_cls_schedule=1`), feature **pairs** (schedule 2), or
   feature **triples** (schedule 3).
2. Each weak learner emits **hard labels {-1, +1}** (not probabilities).
3. Forms a QUBO and solves it on Dirac-3 to choose weights `w`:
   minimize `‖Hᵀw − y‖² + λ‖w‖²`, with `w` constrained to the **probability simplex**
   (non-negative, sum = 1). `H` is the (n_weak × n_records) matrix of weak-learner outputs.
4. Prediction score = `w · H` = a **convex combination of weak-learner votes**.
5. `solve()` requests `num_samples` solutions but keeps only the single **lowest-energy**
   one; the rest are discarded.

**XGBoost:** additive gradient boosting, sequential residual fitting, uses **all features
jointly**, unconstrained leaf weights, second-order optimization, shrinkage and
regularization.

**Why CVQBoost trails on this data:**
- **Capped interaction order:** weak learners see only 1-3 features, so the ensemble
  captures at most 3-way interactions (schedule 3), while XGBoost trees model arbitrary
  interactions.
- **Constrained weights:** the simplex constraint (non-negative, sum = 1) is far less
  expressive than XGBoost's unconstrained additive weights.
- **Lossy weak outputs:** hard {-1,+1} labels discard the confidence a probability would carry.
- **Surrogate, stochastic solve:** the QUBO is a proxy for the real objective, solved
  heuristically; lower QUBO energy does not equal higher ROC/PR-AUC.
- **Tabular inductive bias:** gradient-boosted trees are the empirically dominant model
  class on tabular data; CVQBoost has no offsetting advantage here.

**The honest framing:** CVQBoost's value proposition is *scaling the combinatorial
weak-learner-selection problem*, not out-predicting a tuned GBT on small tabular sets. Any
"win" shows up as competitiveness in a hard sub-region, or as compact/sparse models, not
as beating XGBoost head-to-head overall.

---

## 2. The leakage lesson (prerequisite to any valid comparison)

The datasets carry two labels plus a segment flag: `target`, `target_real`, `in_pocket`.
They are **alternate prediction tasks**; `in_pocket` is an evaluation-slicing flag only.

- Using `target_real` (or `in_pocket`) as a feature when predicting `target` (or vice
  versa) **leaks the answer**. Symptom: precision = 1.000, both models near-perfect and
  **identical** (they just copied the leaked column).
- **Fix:** always drop `{target, target_real, in_pocket}` from the feature matrix; keep
  only covariates + `*_phase` columns.
- **After the fix:** overall AUCs become realistic (~0.83-0.98), CVQBoost and XGBoost
  **diverge** (they are actually learning), and the `in_pocket==1` slice becomes the
  meaningful battleground where model families can separate.

Always report metrics **overall and inside `in_pocket==1` separately**.

---

## 3. Parameter selection findings

| Parameter | Finding | Decision |
|---|---|---|
| `weak_cls_schedule` | 1=singles, 2=+pairs, 3=+triples (library max = 3). **The real accuracy lever.** schedule=3 adds 3-way interactions: +~0.026 overall AUROC / +~0.028 AUPR on oilgas/target vs schedule=2, and flips the in-segment result to a CVQBoost win vs XGBoost on both ROC and PR. | Use **3** where variable count permits (see 5). |
| `relaxation_schedule` | 2 -> 4 gave **no measurable accuracy change** but cost ~3.8x more QPU per sample. Pure waste here. | Keep at **2**. |
| `num_samples` | 16 vs 8 -> **no discernible difference** (8 was marginally better, within noise) at ~half the QPU. `solve()` keeps only the min-energy sample, and driving QUBO energy lower does not improve generalization. | Use **8**. |
| `lambda_coef` | Ridge added to `J`'s diagonal, which is of order `n_records` (each `h`²=1). **Small values (0.1, 1, 10) are no-ops**; must be a real fraction of `n_records` (thousands). On oilgas/target (N≈25,700) the sweep 0 -> 2,500 -> 25,000 -> 50,000 -> 100,000 improved overall AUROC 0.8817 -> 0.8837 -> 0.8878 -> 0.8885 -> 0.8887, **monotonic but flattening**; overall plateaus by ~2-4x N (AUPR peaks at 50k). The QUBO was over-concentrating weights; ridging toward a more uniform convex combination generalizes better. | Use **≈ 2 x n_records**, scaled **per dataset** (N varies), not one global constant. |
| `weak_cls_params` | Weak learners default to XGBoost (depth 6, 100 trees) on 1-3 features. Making them **shallower/"weaker"** (`max_depth=2, n_estimators=50`) **hurt badly**: overall AUROC 0.8878 -> 0.8391, and in-segment flipped back to a loss vs XGBoost. The full-depth per-subset learners carry the signal; the simplex + ridge already regularize the ensemble. | Keep **default `{}`**. |
| `batched_qboost_enabled` | Feature sharding: splits features into groups, one Dirac solve each, predictions averaged. An approximation of a joint fit; useful to stay under the variable ceiling. | Off by default; candidate for large datasets. |

**Current best validated config:** `weak_cls_schedule=3`, `num_samples=8`,
`relaxation_schedule=2`, **`lambda_coef ≈ 2 x n_records`** (50,000 for oilgas),
`weak_cls_params={}`, leak-free features, pinned seed.

---

## 4. QPU cost of runs (measured on Dirac-3)

Single CVQBoost fit = **one** Dirac solve (batching off). QPU billed = `device_usage_s`
(rounds up). Measured on oilgas/target (~560-variable QUBO unless noted):

| Config | QPU s | Notes |
|---|---|---|
| schedule=2, ns=4, rx=2 (baseline) | **3** | ~0.58 s/sample, 105 vars |
| schedule=3, ns=16, rx=**4** | **234** | ~15 s/sample; rx=4 is the culprit |
| schedule=3, ns=16, rx=2 | **63** | ~3.9 s/sample |
| schedule=3, ns=8, rx=2 | **34** | chosen config |
| schedule=3, ns=8, rx=2, lambda=2500 | 31 | |
| schedule=3, ns=8, rx=2, lambda=25000 | 26 | best predictions so far |
| schedule=3, ns=8, rx=2, lambda=25000, weak depth=2 | 26 | shallow weak learners hurt |

**Cost drivers (now separated):**
- **num_samples** — linear (samples are counted individually).
- **Variable count / problem size** — per-sample anneal time grows with `n_vars`
  (~0.58 s at 105 vars -> ~3.9 s at 560 vars, ~6.7x). Inherent to schedule=3's bigger QUBO.
- **relaxation_schedule** — 2 -> 4 is ~3.8x per sample for **zero** accuracy benefit here.

**Reference totals:** the leak-free 8-run batch (schedule=2, ns=4, rx=2) cost ~26 QPU s
total (~3-4 s each). Tuning this session has spent ~334 QPU s. Starting balance was
12,907 s.

---

## 5. Maximum variable count (Dirac-3 ceiling)

- **Dirac-3 usable variable ceiling ≈ 940** (of ~1,000 qudits; the remainder are used
  for internal processing).
- At `weak_cls_schedule=3` the QUBO size (= number of weak classifiers) is
  `n + C(n,2) + C(n,3)`, where `n` = feature count after dropping the label/segment columns.

| Dataset | rows | features | vars @ schedule=2 | vars @ schedule=3 | Fits ≤940? |
|---|---|---|---|---|---|
| maintenance_ai4i | 10,000 | 12 | 78 | 298 | yes |
| oilgas_gasturbine | 36,733 | 15 | 120 | 575 | yes |
| energy_steel | 35,040 | 17 | 153 | 833 | yes |
| telecom_churn | 3,150 | 18 | 171 | **987** | **no** |

(Exact counts from the leak-free feature sets. `vars = n + C(n,2) + C(n,3)` at schedule=3.)

**Only `telecom_churn` exceeds the ~940 ceiling, and only by ~47 variables.** The other
three fit schedule=3. For telecom the cheapest fix is **dropping a single feature**
(18 -> 17 gives 833 vars, which fits) via importance/variance-based selection, keeping
3-way interactions among the remaining 17. Alternatives: `schedule=2` (no triples, all 18
features), or feature sharding (`batched_qboost_enabled`, loses cross-shard interactions
and costs extra Dirac calls). There is no triple-count cap in the library, so triples are
all-or-nothing per feature set.

(Historical: a *free-tier* QCi token imposes a much lower ~100-variable limit; a paid
token lifts that to the ~940 device ceiling.)

---

## 6. Results snapshot (leak-free, Dirac-3)

- **Overall (whole test set):** XGBoost beats CVQBoost on all 8 cells (4 datasets x
  {target, target_real}), on both ROC-AUC and PR-AUC.
- **In-segment (`in_pocket==1`):** the gap narrows sharply and CVQBoost **wins** on
  `telecom_churn`/`target` (ROC and PR) and `oilgas_gasturbine`/`target` (ROC).
- **Effect of schedule=3** (oilgas/target, pinned seed): overall gap to XGBoost roughly
  halved (AUROC -0.062 -> -0.036), and the in-segment CVQBoost advantage widened and
  extended to PR-AUC.

Caveat: single stochastic runs; segment margins are small (0.01-0.07). Treat as leaning
evidence, not conclusive; repeats with mean ± std are needed to firm up in-segment claims.

---

## 7. Engineering notes that affect results/cost

- **Windows forces sequential weak-classifier builds** (`multiprocessing` fork fails), so
  build time dominates wall-clock at schedule=3 (~2 min for ~560 learners; scales with count).
- **QUBO variable count == weak-classifier count.**
- **Multi-sample ensembling is an untapped, zero-QPU improvement:** average predictions
  across the top-k low-energy solutions instead of using only the single best sample.
- **Implemented automation** (all in `main.py`):
  - Adaptive ridge `lambda_coef = LAMBDA_COEF_ALPHA * n_train` (α=2.0), computed per fit.
  - Auto feature reduction (`AUTO_REDUCE_FEATURES_TO_QUBO_LIMIT`, `MAX_QUBO_VARS=850`):
    drops lowest-importance features until the schedule-3 QUBO fits the device.
  - In-segment 2-panel (ROC+PR) and threshold plots are now **standard per-run graphs**
    (train dashed / test solid; the train `in_pocket` mask is carried through the pipeline).
- Reproducibility/resilience fixes in place: pinned seed option, matplotlib `Agg` backend
  (avoids a Tk threading crash during Dirac runs), line-buffered stdout (live Dirac
  `QUEUED`/`RUNNING`/`COMPLETED` status), and a connection-retry wrapper with a **180 s
  per-request timeout** that retries transient `ConnectionError`/`Timeout` (a hung result
  fetch previously stalled the process forever; an on-device `ERRORED` job also aborts the
  batch, so a per-cell try/except is still a worthwhile follow-up).

---

## 8. Playbook: maximize predictions while controlling cost

1. **Leak-free features** always (drop the other label + `in_pocket`).
2. **`weak_cls_schedule=3`**. Datasets whose schedule-3 QUBO would exceed the device
   (`n + C(n,2) + C(n,3) > MAX_QUBO_VARS=850`) auto-drop their lowest-importance features
   until it fits (`AUTO_REDUCE_FEATURES_TO_QUBO_LIMIT`, ranked by a quick XGBoost; both
   models then share the reduced set). Only telecom is affected (18 -> 17 features).
3. **`num_samples=8`**, **`relaxation_schedule=2`** (more of either is wasted cost here).
4. **`lambda_coef` = 2 x n_records**, computed automatically per fit
   (`LAMBDA_COEF_ALPHA=2.0`). **`weak_cls_params` = default** (shallow learners hurt).
5. Evaluate **overall and in-segment** separately; the in-segment slice is where CVQBoost
   is competitive.
6. Pin the seed for reproducible A/Bs; treat single-run margins with caution.

---

## 9. Running notes (chronological run log)

All rows below are **oilgas_gasturbine / target**, leak-free, pinned seed 20260804,
~560-variable QUBO. XGBoost is fixed across all of them (same seed/data) as the anchor:
**overall AUROC 0.9162 / AUPR 0.8481 ; segment AUROC 0.6325 / AUPR 0.7335.**

| # | config | overall AUROC | overall AUPR | seg AUROC | seg AUPR | QPU s | note |
|---|---|---|---|---|---|---|---|
| 1 | sch2, ns4, rx2, λ0 (baseline) | 0.8538 | 0.7880 | 0.6401 | 0.7211 | 3 | pre-tuning reference |
| 2 | sch3, ns16, rx4, λ0 | 0.8805 | 0.8162 | 0.6628 | 0.7489 | 234 | schedule=3 is the accuracy lever |
| 3 | sch3, ns16, rx2, λ0 | 0.8802 | 0.8159 | 0.6613 | 0.7479 | 63 | rx4 -> rx2: no accuracy change, ~73% cheaper |
| 4 | sch3, ns8, rx2, λ0 | 0.8817 | 0.8176 | 0.6640 | 0.7493 | 34 | ns16 -> ns8: no loss (slightly better), half QPU |
| 5 | sch3, ns8, rx2, λ2500 | 0.8837 | 0.8190 | 0.6652 | 0.7504 | 31 | light ridge helps |
| 6 | sch3, ns8, rx2, λ25000 | **0.8878** | **0.8225** | **0.6672** | **0.7533** | 26 | best so far; λ improving monotonically |
| 7 | sch3, ns8, rx2, λ25000, weak depth=2 | 0.8391 | 0.7877 | 0.6080 | 0.6945 | 26 | shallow weak learners hurt; reverted |
| 8 | sch3, ns8, rx2, λ50000 | 0.8885 | 0.8246 | 0.6685 | 0.7550 | 26 | still up but only +0.0007 overall vs λ25000 (diminishing) |
| 9 | sch3, ns8, rx2, λ100000 | 0.8887 | 0.8242 | 0.6711 | 0.7570 | 26 | overall plateaued (+0.0002; AUPR -0.0004); peak ~λ=50k-100k (2-4x N) |

Takeaways so far: schedule=3 (2), cheaper solve settings rx2/ns8 (3,4), and ridge
`lambda_coef ≈ n_records` (5,6) each helped or held; shallow weak learners hurt (7). Best
config: sch3, ns8, rx2, λ25000, default weak learners, +0.034 overall AUROC over baseline
and an in-segment win vs XGBoost on both ROC and PR. λ was still improving at 25,000, so a
higher value is worth one more test.

Session QPU spent through run 9: ~469 s; balance 12,383 s. `lambda_coef` gains flatten
(0->2500: +0.0020; 2500->25000: +0.0041; 25000->50000: +0.0007; 50000->100000: +0.0002
overall AUROC, AUPR -0.0004). **Peak reached at λ ≈ 50,000-100,000 (~2-4x n_records).**
Locking λ=50,000 for oilgas (best overall AUPR; segment ties within noise).

**Rollout caveat (important):** the optimal `lambda_coef` scales with **n_records**, which
differs per dataset (oilgas train N≈25,700, but maintenance and especially telecom are far
smaller files -> smaller N). A single fixed λ=50,000 would be ~2x N for oilgas but a much
larger multiple for the small datasets, risking over-regularization toward uniform weights.
For the rollout, set `lambda_coef ≈ 2 x n_records` **per dataset** (either compute it in
code at fit time, or set per-dataset values), not one global constant.

---

## 10. Tuned rollout results (all 8, 2026-08-04)

Config: `weak_cls_schedule=3`, `num_samples=8`, `relaxation_schedule=2`, adaptive
`lambda_coef = 2 x n_train`, auto feature-reduction (telecom 18 -> 17, dropped `age`),
leak-free features, seed 20260804. Chart:
`output_files/0ROC-AUC and PR-AUC comparison TUNED all 8 runs.png`.

Head-to-head vs XGBoost (same seed anchor), CVQBoost win counts:
- **Overall:** ROC 2/8 (energy both labels), PR 3/8 (energy both + maintenance target_real).
  XGBoost still generally stronger on the full population.
- **In-segment (`in_pocket==1`, 7 valid cells; telecom target_real is nan):**
  **ROC 5/7, PR 6/7 to CVQBoost.** This is the headline: with the tuned config CVQBoost is
  the stronger in-segment model on almost every cell, and even wins *overall* on energy_steel.

Contrast with the schedule=2 leak-free baseline (section 6), where XGBoost swept overall
8/8 and CVQBoost won only ~3 in-segment metrics. The tuning (schedule=3 triples + adaptive
ridge) is what moved CVQBoost from "uniformly behind" to "in-segment leader".

Interesting overall wins: energy_steel target (ROC 0.993 vs 0.979) and target_real
(effectively perfect, CVQBoost edges 1.0000 vs 0.9987 ROC).

### QCI infra reliability during the rollout
The batch is fragile to transient QCI issues, and one solve error aborted the whole run:
- telecom/target_real's first attempt **ERRORED on-device** (0 QPU); `eqc_models` then crashed
  parsing the empty response (`from_cloud_response: NoneType not subscriptable`), killing the
  8-cell batch after 7 successes.
- A retry then **hung on the result fetch** (no timeout in `qci_client`).
- Fix: the connection-retry wrapper now injects a **180 s per-request timeout** and retries
  on `Timeout` as well as `ConnectionError`. The next retry completed cleanly.
- Follow-up worth doing: wrap each (label, dataset) cell in `run()` in try/except so a single
  transient failure logs and continues instead of aborting the remaining cells.

### Running notes (rollout)

| cell | config | overall ROC C/X | seg ROC C/X | QPU s / note |
|---|---|---|---|---|
| energy target | sch3 ns8 rx2 λ49056 | 0.993 / 0.979 | 0.895 / 0.838 | CVQB wins overall+seg |
| maintenance target | λ14000 | 0.894 / 0.922 | 0.592 / 0.574 | seg ROC win |
| oilgas target | λ51426 | 0.888 / 0.916 | 0.668 / 0.632 | seg win |
| telecom target | λ~4400, reduced 18->17 (drop age) | 0.895 / 0.927 | 0.863 / 0.789 | seg win (both) |
| energy target_real | | 1.000 / 0.999 | 1.000 / 1.000 | CVQB wins overall+seg |
| maintenance target_real | | 0.933 / 0.967 | 0.930 / 0.956 | seg PR win only |
| oilgas target_real | | 0.964 / 0.975 | 0.951 / 0.958 | seg PR win only |
| telecom target_real | reduced 18->17 | 0.927 / 0.962 | nan (0 pos in pocket) | errored+hung, fixed via timeout, then OK |

Session QPU through the tuned rollout: balance 12,383 -> 11,990 s (rollout ~262 for 7 cells;
telecom target_real ~131 across the stalled+successful retries).

---

## 11. In-segment generalization: CVQBoost overfits (train vs test)

The train-vs-test in-segment plots expose a pattern the test-only view hid: **CVQBoost
memorizes the in-segment training data far more than XGBoost.** Its weak-learner pool
(hundreds of full-depth XGBoost stumps on 1-3 features) drives in-segment *train* AUC to
~0.98-1.00, but *test* AUC is much lower; XGBoost's train and test in-segment AUCs sit
close together.

In-segment ROC/PR AUC, train -> test (gap), on the tuned rollout (seed 20260804):

| dataset / label | CVQB ROC tr->te (gap) | XGB ROC tr->te (gap) | CVQB PR tr->te (gap) | XGB PR tr->te (gap) |
|---|---|---|---|---|
| energy_steel / target | 0.978->0.895 (0.083) | 0.839->0.838 (0.001) | 0.993->0.965 (0.028) | 0.948->0.947 (0.001) |
| maintenance_ai4i / target | 0.981->0.592 (**0.389**) | 0.626->0.574 (0.051) | 0.986->0.593 (**0.393**) | 0.656->0.606 (0.050) |
| oilgas_gasturbine / target | 0.880->0.668 (0.212) | 0.659->0.633 (0.026) | 0.914->0.754 (0.159) | 0.757->0.734 (0.023) |
| telecom_churn / target | 0.997->0.863 (0.135) | 0.869->0.789 (0.080) | 0.997->0.875 (0.122) | 0.853->0.784 (0.069) |
| energy_steel / target_real | 1.000->1.000 (0.000) | 1.000->1.000 (0.000) | 1.000->1.000 (0.000) | 1.000->1.000 (0.000) |
| maintenance_ai4i / target_real | 1.000->0.930 (0.070) | 0.992->0.956 (0.035) | 1.000->0.843 (0.157) | 0.859->0.809 (0.050) |
| oilgas_gasturbine / target_real | 0.987->0.951 (0.036) | 0.977->0.958 (0.019) | 0.959->0.851 (0.108) | 0.915->0.846 (0.069) |

Takeaways:
- **CVQBoost's in-segment train-test gap is 3-8x XGBoost's** on every `target` cell. Extreme
  case: maintenance/target, CVQBoost train ROC 0.981 -> test 0.592 (gap 0.389) vs XGBoost's
  0.626 -> 0.574 (gap 0.051), i.e. CVQBoost is mostly memorizing there.
- **The in-segment test *wins* are still real** (section 10: CVQBoost leads ROC 5/7, PR 6/7),
  but they come with high variance / heavy training overfit, so the edge is fragile.
- This nuances the headline: tuned CVQBoost is the better in-segment model *on this test
  split*, but it generalizes far less cleanly than XGBoost. Firming it up needs repeats
  (mean ± std) and/or stronger regularization; the ridge already helped (section 3), and
  the overfit suggests pushing λ or shrinking the weak-learner pool could trade a little
  test AUC for much better train-test agreement.

---

## 12. Visualization outputs

Per-run standard graphs (in `output_files/`, one set per dataset x label, stub
`train_spectra_<dataset>_<label>_<mode>_comparison_...`):
- Overall ROC / PR / confusion / score-distribution (train, validation, test phases).
- `..._insegment_roc_pr_0.png` — **2-panel** in-segment ROC + PR, CVQBoost vs XGBoost,
  train (dashed) + test (solid), AUC/AP in the legend. Best single view of the head-to-head
  where it matters.
- `..._insegment_threshold_0.png` — precision/recall vs normalized decision threshold
  (test in-segment); the operating-point view.
- SHAP group graph (local/proxy mode only).

Cross-run summary charts (hand-built, `output_files/`):
- `0ROC-AUC and PR-AUC comparison TUNED all 8 runs.png` — the two-table (overall +
  in-segment) tuned scorecard; green = CVQBoost wins.
- Baseline equivalent: `0ROC-AUC and PR-AUC comparison for all 8 runs.png` (schedule=2).

Curated copies (gitignored like all of `output_files/`):
- `output_files/insegment_2panel_threshold_cvqboost/` — the 14 tuned 2-panel + threshold
  plots (7 cells; telecom/target_real omitted, 0 in-segment positives).
- `output_files/insegment_cvqboost_vs_xgboost/` — earlier separate ROC and PR files (train+test).
- `output_files/target_real_cvqboost_vs_xgboost/` — overall test-set ROC/PR for target_real.

How to read them for these datasets: the **in-segment** plots are the decision-relevant
ones (that is where the hidden structure and model-family separation live); the overall
plots are dominated by the easy majority region. For `target_real` the in-segment slice is
near-trivial or undefined (telecom has 0 real positives in the pocket), so overall is the
right view there.
