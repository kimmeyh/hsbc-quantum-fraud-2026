# Sprint 4 Statistical-Validity Checklist Walk (2026-09-03, REDONE after the hardware campaign)

Walked line by line against docs/STATISTICAL_REVIEW_CHECKLIST.md AFTER the B1/G0b campaign (an earlier pre-campaign walk was superseded: it recorded "all [SIM]; no hardware run" and "no temporal cell", both now false).

## Leakage (prereg s5)
- Transforms fit on TRAIN only inside the fold: DONE (MI top-k per seed's train fold; StandardScaler inside the logistic pipeline; weak pools trained on train; thresholds/calibration from validation only via metrics.summarize's signature). Hardware fits use the same _prep path.
- Feature selection inside the CV loop: DONE (top-k recomputed per seed; tuning used the tuning seed's train fold only).
- Temporal cells: DONE, 2 rows exist (hw_b1_dct and hw_b1_lg, temporal protocol, ULB 70/10/20 time-ordered). Prereg s8.2 labels ULB temporal a stated-weak sensitivity check (2-day span); no aggregate features are used, so the "aggregates strictly before boundary" rule is N/A for these cells.
- Resampling: DONE, none (weighting only).
- Shuffled-label positive control: DONE 2026-09-03 -- tuned XGBoost, seed 42, labels shuffled on train and validation: test AP 0.00225 vs prevalence 0.00167 (ratio 1.34, chance). Recorded in results.json meta.

## Splits and pairedness (prereg s8)
- Seed list: DONE (primary 42-51 on every 10-seed cell, hardware included).
- Identical test rows for paired arms: DONE (single split provider, same seed -> same rows; ADR-0010). Hardware and proxy share the pool AND the split.
- Paired bootstrap with identical resample indices: OPEN. The H1b decision rule (across-seed t-interval on per-seed deltas) is applied; the per-seed paired BCa (metrics.paired_delta_ci) requires persisted per-row predictions, which no writer currently stores. Single fix, tracked once: persist predictions in the refit/hardware writers (also unblocks A7 cell S1). Recorded as OPEN on the H1b gate row.

## Metrics (prereg s9)
- Step-wise AP via metrics.py only: DONE; tie_fraction per row; A6 score_health on all post-A6 rows.
- Prevalence beside every AUPRC; no cross-dataset comparison: DONE.
- Stratified BCa 2,000 per row; Wilson at operating points: DONE.
- Thresholds/calibration on validation only; both operating points: DONE. CAVEAT: the selected dct config carries score_health WARN on 10/10 seeds (mode share 0.951, 814 distinct scores), so its alert-budget and calibration numbers are weak evidence; ranking metrics (AP, AUC) are unaffected.
- H1b margin vs current MDE (A5, 0.0268): DONE -- |hardware delta| 0.0399 > MDE, reported as distinguishable; hardware-vs-proxy |delta| 0.0010 < MDE, reported as indistinguishable.
- Holm correction across exploratory cells: NOT YET APPLICABLE -- K (the count of scoreable exploratory cells) is fixed at freeze over the full grid; H3/H5/H6 cells are unrun, so no exploratory family is complete. To be applied at F7 gate review when the family closes.

## Provenance
- Evidence tags match execution: DONE -- 27 rows tagged [HW] (arm cvqboost_hw, metered_seconds 4.0-5.0 each, 120 s total); all classical/proxy rows [SIM]; unrun blocks [PROJ].
- Manifest verified: DONE (scripts/manifest.py verify -> VERIFY OK, 2026-09-03).
- Config provenance: DONE -- the lambda=2*n_train starting config's SPECTRA provenance recorded; its imbalance mismatch was the F22 subject; the A7-adjacent lambda sweep (experiments/results/lambda_sweep.json) shows the weight-uniformity is NOT lambda-driven (uniform even at lambda=0).
- results.json required keys: DONE for every row (store.append_row constructs schema-complete rows; hardware rows add block, fidelity, retry_count, status).
- Amendment lines for post-freeze analysis-code changes: DONE (A4, A6; run_hardware.py and lambda_sweep.py to be registered in the A7 amendment or its successor).

Open items carried to validation: per-seed paired BCa (prediction persistence); Holm at gate review; A7 disposition; registration of the Sprint 4 hardware/sweep code in an amendment line.
