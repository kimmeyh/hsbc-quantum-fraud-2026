# ADR-0003: Dataset acquisition, storage, and provenance handling

## Status

Accepted

## Date

2026-08-30

## Context

Four dataset families feed the study, with different licenses, roles, and citation obligations. Dataset mix-ups or silent corruption are the cheapest way to invalidate results, and the competition requires clean licensing. ULB contains real cardholder data (PCA-anonymized) and must never leak into logs or the public repo.

## Decision

- Raw data lives under `experiments/data/` (gitignored) and the pre-existing `XGBvHQXGB\datasets\` for ULB; treated strictly read-only by all code.
- Per-dataset inventory of record:

| Dataset | Source | License | Role (prereg s2) | Citation obligations |
|---|---|---|---|---|
| ULB creditcard.csv | Kaggle mlg-ulb/creditcardfraud | ODbL | Primary endpoint | Dal Pozzolo et al. 2015 |
| IEEE-CIS | Kaggle competition ieee-fraud-detection | Competition license (rules accepted 2026-08-30) | Scaling/regime, exploratory | Vesta/Kaggle 2019; reproduction band attributed to its source, never the competition |
| Sparkov | Kaggle kartik2112/fraud-detection | Open | Pipeline-correctness check ONLY | Sparkov Data Generation |
| SPECTRA x4 | Kaggle javierfalcondale/spectra-* | CC BY 4.0 | H5 replication ONLY, never fraud evidence | BOTH the releases AND original UCI substrates (851, 551, 601, 563), per docs/references.md |

- A checksum manifest (`experiments/data/MANIFEST.json`: SHA-256, row counts, source URL, download date) is generated on staging and verified at sprint start and before any hardware block. The B4 SPECTRA copies must provably match or provably differ from the FourierWall2-era files.
- Loader functions (`experiments/src/data.py`) validate shape and label contracts on every load; labels and segment flags are excluded from features by contract.
- Preprocessing artifacts (duplicate-removal counts, dtype downcasts) are recorded in results, never applied destructively to raw files.
- Never log dataset rows; log shapes, counts, hashes.

## Alternatives Considered

### Data committed to the repository (LFS)
- **Pros**: One clone gets everything.
- **Cons**: License redistribution problems (IEEE-CIS competition license forbids it), repo bloat, public-repo exposure of real transaction data.
- **Why Rejected**: Licensing alone is disqualifying; the manifest gives equivalent integrity.

## Consequences

### Positive
- Any result is traceable to checksummed inputs; the public repo ships the manifest, not the data.
### Negative
- A fresh environment requires re-downloading with credentials (documented in README).
### Neutral
- The manifest generator is one small script run rarely.

## Preregistration touchpoints

Section 2 (datasets and roles), section 5 (leakage controls the loaders enforce). The preregistration governs methodology; this ADR records engineering decisions only.

## References

`experiments/src/data.py`; `docs/references.md`; `.gitignore`; requirements-matrix D13/D15.
