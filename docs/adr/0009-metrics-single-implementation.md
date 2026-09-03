# ADR-0009: One metrics implementation, known-answer tested, used by every arm

## Status

Accepted

## Date

2026-09-02

## Context

The statistical spec (PREREGISTRATION section 9) is precise: step-wise average_precision_score only, stratified BCa with identical resample indices for paired arms, Wilson intervals, equal-mass ECE, Brier as joint score only. Two implementations of any of these WILL disagree at the third decimal, and a paper number that moves between drafts is a credibility wound.

## Decision

`experiments/src/metrics.py` (frozen at prereg-freeze) is the ONLY metrics implementation. Every runner (classical, proxy, later hardware and QFE) calls `metrics.summarize` for its row metrics and the shared helpers for aggregate statistics; no runner computes its own AP/CI/threshold logic. New metric needs are added to metrics.py by dated amendment with known-answer tests (the Sprint 1 pattern: BCa vs scipy.stats.bootstrap, Wilson vs statsmodels), never inlined in a runner. Score-domain adapters (e.g. the proxy's affine [-1,1] -> [0,1] map for the calibration block) live in the runner and must be monotone so ranking metrics are unchanged.

## Alternatives Considered

### Per-runner metrics with a comparison test
- **Description**: Each runner computes metrics; a test asserts agreement.
- **Pros**: Runner independence.
- **Cons**: The comparison test just re-derives the single-source-of-truth requirement with more code.
- **Why Rejected**: Strictly worse.

## Consequences

### Positive
Every number in every row is produced by the same audited code path; paired statistics reuse identical resample indices by construction.
### Negative
metrics.py changes require amendments (intended friction).
### Neutral
The second-implementation cross-check for tie-heavy AP (section 9) is a validation activity, not a second production path.

## Preregistration touchpoints

Section 9 (metrics and statistics), section 11 (analysis-code freeze). The preregistration governs methodology; this ADR records engineering decisions only.

## References

experiments/src/metrics.py, test_metrics.py (11 known-answer tests), test_qubo_proxy.py; card #15.
