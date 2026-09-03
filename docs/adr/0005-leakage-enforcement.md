# ADR-0005: Leakage enforcement lives in code paths, not review vigilance

## Status

Accepted

## Date

2026-09-02

## Context

Every leakage rule in PREREGISTRATION section 5 (train-only transforms, in-fold feature selection, no-identifier rule, dedupe-before-split) can be silently violated by one careless call. Review-time vigilance does not survive context loss across sessions; the honest-baselines research showed >0.95 ULB AUPRC almost always means leakage.

## Decision

Leakage rules are enforced by construction: (1) all feature selection goes through `data.top_k_features(X_train, y_train, ...)` which only ever receives train frames; (2) splits come only from `data.stratified_split`/`data.temporal_split` (ADR-0010) so no ad-hoc slicing; (3) `run_classical.py` dedupes BEFORE splitting and records the count in results.json meta; (4) early stopping uses the dedicated validation fold, threaded explicitly through `_fit_final`, never test; (5) thresholds and calibration inputs come from validation only (`metrics.summarize` signature makes passing test data for thresholds impossible without deliberate misuse); (6) the G0 band itself (0.85-0.88; >0.95 = leakage flag) is a runtime tripwire scored at gate review.

## Alternatives Considered

### Reviewer-checklist-only enforcement
- **Description**: Rely on STATISTICAL_REVIEW_CHECKLIST at gate time.
- **Pros**: No code constraints.
- **Cons**: Catches leakage after compute is spent; depends on memory.
- **Why Rejected**: The checklist stays as the second layer, not the only one.

## Consequences

### Positive
Leakage requires actively fighting the API. Sessions inherit the discipline from signatures.
### Negative
Some flexibility lost (e.g. quick experiments must still construct Split objects).
### Neutral
IEEE-CIS fold-internal feature engineering (F3) will extend this pattern, not bypass it.

## Preregistration touchpoints

Section 5 (feature handling and leakage controls), section 8 (splits), G0 band rationale in section 3. The preregistration governs methodology; this ADR records engineering decisions only.

## References

experiments/src/data.py, run_classical.py, metrics.py; docs/STATISTICAL_REVIEW_CHECKLIST.md; card #15.
