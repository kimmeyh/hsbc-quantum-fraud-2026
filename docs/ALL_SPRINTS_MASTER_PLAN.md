# All Sprints Master Plan

Adapted 2026-08-30 from spamfilter-multi's ALL_SPRINTS_MASTER_PLAN.md structure. This document is IN THE REPOSITORY and persists across conversations. Read it before every sprint (Phase 1/2), update it after every sprint (Phase 7.7/8.2).

## Maintenance Guide

- **After each sprint (Phase 7.7 / 8.2)**: update "Last Completed Sprint"; add the sprint's row to "Past Sprint Summary" once its SUMMARY doc exists; prune shipped items from "Next Sprint Candidates"; add retro Category-14 items with new F#s.
- **During Sprint N+1 planning (Phase 3.2.1)**: create `docs/sprints/SPRINT_N_SUMMARY.md` for the just-finished sprint and link it here.
- **IDs**: F# for all features/process/tech-debt items; next available number; never reuse.
- **Estimates**: minutes/hours from recorded actuals; `[no-history]` where uncalibrated.
- The repo-root `CHECKLIST.md` remains the submission-wide deliverable ledger; this document is the sprint-scoping view over it. Keep them consistent; CHECKLIST wins on deliverable truth, this file wins on sprint sequencing.

## Past Sprint Summary

| Sprint | Summary doc | Status | Duration |
|---|---|---|---|
| 1 | docs/sprints/SPRINT_1_SUMMARY.md | [OK] Complete | ~1 day (Aug 30, 2026) |

## Last Completed Sprint

**Sprint 1: Freeze and Foundations** (Aug 30, 2026; PR #1 merged to develop, develop merged to main via PR #3).
Delivered: PREREGISTRATION v1.1 FROZEN (commit 95751b9, tag prereg-freeze); metrics.py at the v1.1 statistical spec (11 known-answer tests); loaders validated across ULB/IEEE-CIS/SPECTRA; pilot variance run (mean AP 0.8268, seed SD 0.0243, MDE(10) 0.0242 [SIM]); repo infrastructure (private remote, branch model, Copilot instructions, pre-commit confidentiality hook). Zero metered seconds. Retro: docs/sprints/SPRINT_1_RETROSPECTIVE.md (lightweight protocol; full 14x4 applies from Sprint 2).

## Next Sprint Candidates

### Experiments (Stage 3 of the master timeline; submission-ready Sep 8)

**F1. Classical evidence campaign (~1.5 days) Priority 10**
- Phase: Experiments
- Platform: ULB
- Tuned XGB/LGBM/CatBoost (100 Optuna trials each) + logistic; full and matched features; 10 seeds; BCa CIs into results.json
- G0 scored as committed (mean AP >= 0.85); Tuning Budget Equivalence table; paired-delta SD measurement with MDE refinement decision
- CVQBoost proxy pipeline (weak pools, QUBO build, non-negative-ridge solve = structural control); free-tier and full configs frozen
- B1+G0b hardware request PREPARED with call counts (not executed)
- Inline scope additions from the approved 2026-08-30 disposition (retro Category 13 pattern): ADRs 0005-0010 authored as their modules are built; logging conventions (frd.* namespaces); full-pipeline smoke fixture; ARCHITECTURE.md with inline ADR cross-references; TESTING_STRATEGY.md adaptation; known-failure headers on long-running scripts (~4h total added)
- Depends on: prereg freeze (done)

**F2. Hardware campaign, first blocks (~0.5 day + approvals) Priority 12**
- Phase: Experiments
- Platform: Dirac-3
- Execute B1 (free-tier ULB) and G0b (proxy fidelity) on team-lead approval per block; B2/B3 if the QCi grant lands
- results.json [HW] rows; retry discipline per frozen protocol
- Depends on: F1; team-lead approval; QCi grant for B2/B3

**F3. IEEE-CIS reduced Deotte recipe + temporal protocols (~1 day) Priority 14**
- Phase: Experiments
- Platform: IEEE-CIS
- Preregistered feature pass (D-normalization, UID excluded, named aggregates, V-reduction); leakage controls incl. shuffled-label positive control
- GroupKFold-by-month rolling origin; classical arms + proxy CVQBoost on the reduced set; H3 ladder cells
- Depends on: F1

**F4. QFE phase arms + order-matched twins (~0.5 day) Priority 16**
- Phase: Experiments
- Platform: ULB, IEEE-CIS
- Fourier Wall recipe applied identically to all arms; trained-frequency GAM/GA2M/JOINT twins in every H6 cell
- Depends on: F1

**F5. SPECTRA in-segment replication, block B4 (~0.5 day) Priority 18**
- Phase: Experiments
- Platform: SPECTRA, Dirac-3
- 3 strongest cells x 5 seeds; random-segment negative control machinery reused for fraud transfer
- Depends on: QCi grant; F2 approval pattern

(F6 Braket gate-based arm: moved to HOLD per team-lead steering 2026-08-30; no Braket execution before submission/acceptance. The proposal covers Braket via the written [PROJ] Phase 2 plan plus Team Capability citing the team lead's near-expert AWS and hands-on Braket experience.)

**F7. Results memo + gate review (~2h) Priority 22**
- Phase: Experiments
- Platform: docs
- One-page results memo; gate table scored as committed; headline promotion decision per the thesis rule (team-lead review, Sep 4 target)
- Depends on: F1-F4 (F5/F6 as available)

### Paper (Stages 4-6)

**F8. Outline + Draft V1 (~1 day) Priority 30**
- Phase: Paper
- Platform: docs
- Seven rubric-mapped sections + appendices; [HW]/[SIM]/[PROJ] tags; prevalence beside every AUPRC; references from docs/references.md
- Depends on: F7; team-lead outline approval

**F9. Adversarial reviews V2/V3 + rubric pass (~0.5 day) Priority 32**
- Phase: Paper
- Platform: docs
- Domain pass, quantum pass (encoding diagnostics, evidence-tag audit), rubric scoring; fix lowest criterion
- Depends on: F8

### Finalize (Stages 7-8)

**F10. Verification, confidentiality scan, compliance walk, submission (~0.5 day) Priority 40**
- Phase: Finalize
- Platform: docs
- Every number vs results.json; repo-wide confidential-string scan (fourierwall2 reference files file-by-file); requirements-matrix walk; public reproducibility repo; team-lead final PDF + portal submission, receipt archived
- Depends on: F8, F9

### External (team-lead-owned, parallel)

**F12. Portal account verification (~15m) Priority 9 -- ASSIGNED Sprint 2 (team-lead-owned)**
- Phase: External
- Platform: N/A
- Confirm portal login and note required submission fields into requirements-matrix A5

(F11 QCi sponsorship letter send: COMPLETED by the team lead 2026-08-30, per convention removed from candidates; history in SPRINT_2_PLAN.md Task H and CHECKLIST.md.)

**F15. Best-practices and ADR review from spamfilter-multi (~3h) Priority 11**
- Phase: Experiments (assigned to Sprint 2 by the team lead, 2026-08-30)
- Platform: docs
- Review spamfilter-multi ARCHITECTURE.md and docs/adr/ for (1) architecture, development, and software-engineering practices to copy and adapt here, (2) additional SE best-practice suggestions, (3) ML best practices to propose as ADRs for this repo: feature engineering, data curation, leakage prevention, training, evaluation of results, applied to the challenge effort
- Output: adapted docs/adr/ directory with an ADR template, initial ADRs for decisions already made, and a proposal list for team-lead disposition
- Depends on: nothing

**F16. Minimal CI: pytest + lint on PRs with smoke fixture (~30m) Priority 34**
- Phase: Finalize
- Platform: docs
- GitHub Actions on PRs to develop; sub-minute; no dataset or metered access
- Backlogged per the approved 2026-08-30 disposition (item 11)

### HOLD Items (post-submission)

**F13. Phase 2 PoC sprint planning (~unknown) Priority HOLD**
- Phase: Phase 2 (Nov 17 - Feb 28, if selected)
- Platform: All
- Braket hardware validation, IEEE-CIS at scale, calibrated deployment per the routing architecture; plan built on acceptance

**F6. Braket gate-based phase-active arm (~0.5 day) Priority HOLD**
- Phase: Phase 2 (if selected)
- Platform: Braket simulator, then hardware
- Sandwich/entangling encoding only (Inverse Born Rule: plain Ry is provably classical); phase-complexity, Berry-connection, mode-MI diagnostics reported
- Team lead brings near-expert AWS + hands-on Braket experience; Phase 1 covers this as a written [PROJ] plan only

**F14. eqc-models feedback package to QCi (~2h) Priority HOLD**
- Phase: External
- Platform: Dirac-3
- Promised in the sponsorship letter; assemble after the hardware campaign
