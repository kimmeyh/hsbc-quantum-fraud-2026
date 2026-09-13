# Architecture Decision Records

**Purpose**: Record engineering decisions for this repository so they survive context loss across sessions and reviewers can audit why things are the way they are.
**Audience**: Claude Code sessions; the team lead; eventual submission reviewers via the public reproducibility package.
**Last Updated**: 2026-08-30

Adopted from the spamfilter-multi ADR system (F15 review) with one addition: every ADR carries a **Preregistration touchpoints** section, because in this repository `experiments/PREREGISTRATION.md` (FROZEN) governs all methodology; ADRs record engineering decisions around it and may never restate or alter it.

## Conventions

- Sequential 4-digit numbering; file naming `NNNN-short-title.md`, lowercase, hyphens.
- Status lifecycle: Proposed -> Accepted -> Deprecated or Superseded by ADR-NNNN.
- **Immutability**: once Accepted, an ADR is never edited; a changed decision gets a new superseding ADR. (Sibling of the preregistration's amendment-only rule.)
- Dates exact where known, `~` prefix for estimates.
- New ADRs add a row to the index below and are committed with the related changes.
- Template: `template.md` in this directory.

## Index

| ADR | Title | Status | Date |
|---|---|---|---|
| [0001](0001-preregistration-freeze-governance.md) | Preregistration freeze governance and amendment mechanics | Accepted | 2026-08-30 |
| [0002](0002-proxy-as-structural-control.md) | Proxy-as-structural-control dual-role design | Accepted | 2026-08-30 |
| [0003](0003-dataset-provenance-and-storage.md) | Dataset acquisition, storage, and provenance handling | Accepted | 2026-08-30 |
| [0004](0004-branch-and-carry-forward-model.md) | Branch and carry-forward model for sprint work | Accepted | 2026-08-30 |
| [0005](0005-leakage-enforcement.md) | Leakage enforcement lives in code paths, not review vigilance | Accepted | 2026-09-02 |
| [0006](0006-feature-recipe-registry.md) | Feature recipes are named, hashed, and recorded per row | Accepted | 2026-09-02 |
| [0007](0007-training-discipline.md) | Training discipline: checkpointed stages, atomic rows, resumable | Accepted | 2026-09-02 |
| [0008](0008-results-store.md) | Single results.json store, append-only, schema-complete rows | Accepted | 2026-09-02 |
| [0009](0009-metrics-single-implementation.md) | One metrics implementation, known-answer tested, used by every arm | Accepted | 2026-09-02 |
| [0010](0010-splits-and-seeds-provider.md) | Splits and seeds from one provider; seed lists are constants | Accepted | 2026-09-02 |
| [0011](0011-secrets-and-credential-handling.md) | Secrets and credential handling | Accepted | 2026-08-30 |
| [0012](0012-pdf-rendering-toolchain.md) | PDF rendering toolchain: pandoc to docx to Word | Accepted | 2026-09-04 |
| [0013](0013-h6-qfe-twin-design.md) | H6 QFE representation and order-matched classical twin design | Proposed | 2026-09-05 |
| [0014](0014-fact-database.md) | Evidence Based DB: SQLite plus committed export, three record classes, reading level escalates 8 to 20; private repo `EvidenceBasedDB` | Proposed | 2026-09-12 |
| [0015](0015-reference-library.md) | Reference-paper library: a record class in the Evidence Based DB, records not PDFs, search before embeddings | Proposed | 2026-09-12 |
