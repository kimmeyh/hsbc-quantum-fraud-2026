# HSBC Quantum Fraud 2026: Phase 1 Submission Project

Working project for Harold Kimmey's Phase 1 concept proposal to the 2026 Global Quantum + AI Challenge (Resonance Alliance / The Quantum Insider), HSBC track: "Quantum-Enhanced Credit Card Fraud Detection for Digital Payment Ecosystems."

**Phase 1 deadline: September 15, 2026.** Verified against the official program page on 2026-08-29.

## Layout

| Path | Purpose |
|---|---|
| `docs/PLAN.md` | The 8-stage submission development process with dates |
| `docs/requirements-matrix.md` | Master requirements and evidence matrix (the acceptance checklist) |
| `docs/trueloop-teardown.md` | Reviewer-style teardown of the public TrueLoop Compute HSBC proposal |
| `docs/thesis-candidates.md` | Candidate central theses with recommendation |
| `docs/source/` | Put the four official challenge PDFs here (T&C, Assessment Criteria, Submission Guidelines, HSBC Challenge Statement) |
| `experiments/` | Code and results (Stage 2 onward) |
| `paper/` | Outline, drafts, final PDF (Stage 4 onward) |

## Key external references

- Program page: https://quantumai.thequantuminsider.com/program/
- TrueLoop HSBC proposal (public competitor example): https://github.com/MatthewLeibel/TrueLoop-Compute-HSBC-Challenge-Reproducibility
- Prior submission template (different challenge): held locally by the team lead, not part of this repository

## Datasets (required before anything runs)

The raw datasets are NOT redistributed here: their licences do not permit it,
and `experiments/data/` is gitignored apart from `MANIFEST.json`, which carries
the SHA-256 of every file the frozen loaders read.

| Dataset | Place at | Source |
|---|---|---|
| ULB creditcard | `experiments/data/ulb/creditcard.csv` (plus `creditcard_x1_train.csv`, `creditcard_x1_test.csv`) | Kaggle "Credit Card Fraud Detection" (ULB) |
| SPECTRA | `experiments/data/spectra/spectra_<name>.csv` | SPECTRA release (see `docs/references.md`) |
| IEEE-CIS | `experiments/data/ieee-cis/` | Kaggle "IEEE-CIS Fraud Detection" |

Set `HSBC_ULB_CSV` to override the ULB location if you keep it elsewhere.

Verify a staged copy against the frozen checksums before running anything:

```
python scripts/manifest.py verify
```

`VERIFY OK` means every file matches the manifest the results were produced
from. Any other output means the data differs from what the evidence store
records, and figures will not reproduce.

## Immediate to-do

1. Copy the four official challenge PDFs into `docs/source/` so requirements can be verified against primary text, not page-1 images.
2. Decide the central thesis (see `docs/thesis-candidates.md`).
