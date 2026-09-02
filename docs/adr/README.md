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
| 0005-0010 | Reserved per the approved 2026-08-30 disposition (leakage enforcement, feature-recipe registry, training discipline, results store, metrics single-implementation, splits/seeds provider); authored in the F1 campaign sprint as their modules are built | Proposed | - |
| [0011](0011-secrets-and-credential-handling.md) | Secrets and credential handling | Accepted | 2026-08-30 |
