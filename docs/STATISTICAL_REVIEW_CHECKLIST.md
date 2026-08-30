# Statistical-Validity Self-Review Checklist

**Purpose**: Fixed pre-recording review run before ANY result is recorded as gate evidence. The failure modes this guards against (leakage, broken pairedness, metric drift) do not crash; they produce plausible wrong numbers.
**Audience**: Claude Code sessions executing experiments; the team lead auditing evidence.
**Last Updated**: 2026-08-30 (disposition item 7, Sprint 2)

Derived from the FROZEN preregistration sections 5-9. Walk EVERY line with evidence (invariant 4 of the workflow: DONE with evidence / N-A with reason) before a results.json record becomes gate evidence. This checklist changes only via prereg amendment or a new dated version here.

## Leakage (prereg s5)

- [ ] Every transform (scaler, encoder, imputer, selector, aggregate, whitening, calibration, threshold) fit on TRAIN only, inside the fold, via a fitted pipeline object
- [ ] Feature selection ran inside the CV loop, never on pre-split data
- [ ] Temporal cells: aggregates use only rows strictly before the split boundary; no identifier column entered any model raw
- [ ] Resampling: NONE in house protocol (H1a reproduction cells only, train-only, labeled)
- [ ] Shuffled-label positive control on file for this pipeline version, collapsing to base rate

## Splits and pairedness (prereg s8)

- [ ] Correct seed list for the cell class (primary {42..51}, exploratory {42..46}); splits varied with seed
- [ ] Paired comparisons: both arms scored on IDENTICAL test rows from the same split call
- [ ] Paired bootstrap used identical resample indices on both arms' prediction vectors

## Metrics (prereg s9)

- [ ] AUPRC from step-wise `average_precision_score` (metrics.py is the sole implementation); tie fraction checked
- [ ] Prevalence recorded beside every AUPRC; no cross-dataset comparison or averaging anywhere
- [ ] CIs: stratified BCa, 2,000 resamples; Wilson for precision/recall
- [ ] Thresholds and calibration fitted on validation only; both operating points reported
- [ ] H1b margins compared against the current MDE; sub-MDE margins reported as indistinguishable

## Provenance

- [ ] Evidence tag ([HW]/[SIM]/[PROJ]) matches what actually executed
- [ ] Data manifest verified since last staging change (`experiments/src/manifest.py verify`)
- [ ] results.json record carries all required keys (prereg s11), including config_hash, metered_seconds, retry_count
- [ ] Any post-freeze change to frozen analysis files has its amendment line (ADR-0001)
