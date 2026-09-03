# ADR-0006: Feature recipes are named, hashed, and recorded per row

## Status

Accepted

## Date

2026-09-02

## Context

The campaign spans feature sets (full, matched top-k, the IEEE-CIS reduced Deotte recipe, QFE phase blocks) across arms and seeds. A result row whose feature provenance is ambiguous is unusable for the paper's evidence tags, and silent feature drift between proxy and hardware would invalidate G0b/H4 comparability.

## Decision

Every results.json row carries `features_used` (the literal column list) and a `config_hash` covering the recipe inputs. Recipes are named (`full`, `matched13`, later `deotte_reduced`, `qfe_phase`) and computed by exactly one function per recipe living in experiments/src (A4-registered), parameterized by split and seed. Matched features are recomputed per seed from that seed's train fold (never cached across seeds). Proxy and hardware runs of the same cell must share the recipe function output verbatim; `qubo_proxy.cmd_solve` asserts saved-pool features equal freshly computed ones before solving.

## Alternatives Considered

### Central features.yaml configuration
- **Description**: Declare recipes in a config file.
- **Pros**: Single place to look.
- **Cons**: Drifts from code; cannot express per-seed recomputation; adds indirection.
- **Why Rejected**: The function IS the recipe; rows record its output.

## Consequences

### Positive
Any number in the paper traces to literal column names. Pool identity checks are mechanical.
### Negative
results.json rows are larger (column lists).
### Neutral
F3's Deotte recipe lands as one function with the same contract.

## Preregistration touchpoints

Sections 3 (H1b matched top-k), 5.3 (IEEE-CIS recipe), 6 (CVQBoost tunes over k). The preregistration governs methodology; this ADR records engineering decisions only.

## References

experiments/src/data.py (top_k_features), run_classical.py (_features), qubo_proxy.py (_prep, cmd_solve assert); card #15.
