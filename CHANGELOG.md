# Changelog

Policy (disposition item 8, adapted from spamfilter-multi ADR-0025): updated in the SAME commit as the change it describes, under `## [Unreleased]`, grouped by date, newest first. Format: `- **type**: Description (Issue #N / PR #N)` with type in feat | fix | docs | test | chore | process. Entries move under a version heading when develop merges to main at a milestone tag.

## [Unreleased]

### 2026-08-30

- **process**: Sprint 2 dispositions applied: statistical-review checklist, CHANGELOG policy, data manifest + verifier, QUALITY_STANDARDS, secrets ADR-0011; F1-sprint items recorded in master plan; CI to backlog as F16 (Issue #10)
- **docs**: ADR system adopted with ADRs 0001-0004 (freeze governance, proxy-as-structural-control, dataset provenance, branch/carry-forward) and Preregistration-touchpoints template section (Issue #10, F15)
- **docs**: Portal verified; submission mechanism is 5-slot file upload; team-profile-as-PDF plan added (A5b); Braket resolved as [PROJ] plan + team-lead expertise (Issue #11, F12)
- **process**: Full sprint execution doc set adapted from spamfilter-multi (workflow, checklist, stopping criteria incl. Criterion H, retrospective 14x4, backlog refinement, planning, master plan); defined-scope rule adopted
- **feat**: Preregistration v1.1 FROZEN (commit 95751b9, tag prereg-freeze, amendment A1); analysis code frozen at same commit (PR #1)
- **feat**: metrics.py at v1.1 statistical spec (stratified BCa 2000, paired identical-index deltas, across-seed t-interval, MDE, Wilson, equal-mass ECE, dual operating points); 11 known-answer tests (PR #1)
- **feat**: Data loaders + validation for ULB, IEEE-CIS (float32), and four SPECTRA sets; Kaggle OAuth wired; datasets staged (PR #1)
- **feat**: Pilot variance run [SIM]: ULB 10-seed mean AP 0.8268, seed SD 0.0243, MDE(10) 0.0242 (PR #1)
- **chore**: Private remote, main/develop/feature branch model, draft-PR lifecycle, pre-commit confidentiality hook (verified blocking), Copilot review instructions (PR #1)

### 2026-08-29

- **docs**: Requirements matrix verified against all four official challenge PDFs; reference library read in full; preregistration v1.0 through dual-model review + methods research to v1.1; QCi sponsorship letter v3 with Outlook draft
