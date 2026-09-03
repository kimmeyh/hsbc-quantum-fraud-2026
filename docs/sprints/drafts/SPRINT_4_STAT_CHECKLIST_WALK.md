# Sprint 4 Statistical-Validity Checklist Walk (2026-09-03)

Walked line by line against docs/STATISTICAL_REVIEW_CHECKLIST.md before the results memo was declared final (workflow invariant 4).

## Leakage (prereg s5)
- Transforms fit on TRAIN only inside the fold: DONE (MI top-k on each seed's train fold; StandardScaler inside the logistic pipeline; weak pools trained on train; thresholds/calibration from validation only by metrics.summarize's signature).
- Feature selection inside the CV loop: DONE (top-k recomputed per seed from that seed's train; tuning studies used the tuning seed's train fold only).
- Temporal cells: N/A (no temporal cell run this sprint).
- Resampling: DONE, none (weighting only).
- Shuffled-label positive control on file: DONE 2026-09-03 -- tuned XGBoost, seed 42, labels shuffled on train and validation: test AP 0.00225 vs prevalence 0.00167 (ratio 1.34, i.e. chance). A leaking pipeline would not collapse. Recorded in results.json meta.

## Splits and pairedness (prereg s8)
- Seed list: DONE (primary 42-51 on every 10-seed cell).
- Identical test rows for paired arms: DONE (single split provider, same seed -> same rows; ADR-0010).
- Paired bootstrap with identical resample indices: PARTIAL -- the H1b decision rule (across-seed t-interval on per-seed deltas) is applied; the per-seed paired BCa (metrics.paired_delta_ci) is implemented but not yet run because predictions are not persisted per row. OPEN item -> the A7 proposal's prediction-persistence addition covers it.

## Metrics (prereg s9)
- Step-wise AP via metrics.py only: DONE; tie_fraction per row; A6 score_health flags on all post-A6 rows.
- Prevalence beside every AUPRC; no cross-dataset comparison: DONE.
- Stratified BCa 2,000 per row; Wilson at operating points: DONE.
- Thresholds/calibration on validation only; both operating points: DONE.
- H1b margin vs current MDE (A5, 0.0268): DONE -- |delta| 0.039 > MDE, reported as distinguishable.

## Provenance
- Evidence tags match execution: DONE (all [SIM]; no hardware run).
- Manifest verified: DONE (scripts/manifest.py verify -> VERIFY OK, 2026-09-03).
- Config provenance: DONE -- the lambda=2*n_train starting config's SPECTRA provenance is recorded and its imbalance mismatch was the F22 subject; tuned configs carry their own hashes.
- results.json required keys: DONE (writers construct schema-complete rows; store.append_row).
- Amendment lines for post-freeze analysis-code changes: DONE (A4, A6; tune.py unchanged).

Open items carried to validation: paired per-seed bootstrap (needs prediction persistence), A7 disposition.
