# ADR-0010: Splits and seeds come from one provider; seed lists are constants

## Status

Accepted

## Date

2026-09-02

## Context

The protocol pins split shapes (60/20/20 stratified; 70/10/20 temporal) and seed lists ({42..51} primary, {42..46} exploratory). ForrierWall's retro-noted gotcha -- seeds drawn with random.randint and only logged -- is the anti-pattern: results that cannot be regenerated from the repo alone.

## Decision

`data.stratified_split(df, seed)` and `data.temporal_split(df)` are the only split constructors; every runner takes seeds from module-level constants (`run_classical.SEEDS`, `qubo_proxy.SEEDS`, both = range(42, 52) per section 8). No runner accepts a "random seed" default, draws entropy, or shuffles outside these constructors. The tuning seed is the named constant TUNING_SEED = 42. A row's seed field plus the repo state at its config_hash regenerates its exact splits.

## Alternatives Considered

### Seed lists in a config file
- **Why Rejected**: Same indirection argument as ADR-0006; the frozen prereg already IS the config, and constants mirror it verbatim.

### Hash-derived per-purpose seeds (seed = f(base, purpose))
- **Pros**: Avoids accidental seed reuse across purposes.
- **Cons**: Obscures the direct prereg-to-code correspondence reviewers will check.
- **Why Rejected**: Transparency wins at this scale; distinct purposes already use distinct explicit seeds.

## Consequences

### Positive
Bit-level regenerability of every split from the repo; Bouthillier-style seed variation is exactly the preregistered list, no more, no less.
### Negative
None material.
### Neutral
F3's GroupKFold-by-month construction joins data.py under the same contract.

## Preregistration touchpoints

Section 8 (protocols, splits, seeds). The preregistration governs methodology; this ADR records engineering decisions only.

## References

experiments/src/data.py, run_classical.py, qubo_proxy.py; F18 findings memo (ForrierWall seed gotcha); card #15.
