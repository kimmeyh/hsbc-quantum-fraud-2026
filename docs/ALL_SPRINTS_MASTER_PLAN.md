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
| 2 | docs/sprints/SPRINT_2_SUMMARY.md | [OK] Complete | ~2 days (Aug 31 - Sep 2, 2026) |
| 3 | docs/sprints/SPRINT_3_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 2-3, 2026) |

## Last Completed Sprint

**Sprint 3: Classical Evidence Campaign** (Sep 2-3, 2026; PR #13 merged to develop, develop merged to main via PR #16).
Delivered: F18 mined (10 dispositions, zero amendments); F1 campaign with 110 [SIM] rows -- G0 scored as committed = FAIL (0.8296 vs 0.85; no leakage flag), best arm CatBoost/full 0.8368, paired proxy-vs-GBDT delta -0.0415, measured MDE 0.0268 (A5); CVQBoost proxy pipeline with exact Hamiltonian + known-answer tests; A3 full-pair selected; B7 hardware request prepared (not executed); ADRs 0005-0010; hooks ported; validation found lg scoring degeneracy (quarantined; fix = F22). Zero metered seconds. Retro: docs/sprints/SPRINT_3_RETROSPECTIVE.md (6 improvements applied).

## Next Sprint Candidates

### Experiments (Stage 3 of the master timeline; submission-ready Sep 8)

(F1 classical evidence campaign and F18 Dirac-3 notes mining: COMPLETED in Sprint 3, merged via PR #13; history in SPRINT_3_SUMMARY.md. Removed from candidates per convention. F1 residual -- the section-6 CVQBoost proxy tuning -- continues as F22.)

**F22. CVQBoost proxy tuning per prereg section 6 (~2-3h + unattended solves) Priority 11**
- Phase: Experiments (team-lead validation 2026-09-02; PREREQUISITE for G0b and for un-quarantining lg)
- Platform: ULB, local proxy (zero metered seconds)
- The preregistered equal-budget tuning: 100 trials over weak pool composition (incl. class-weighted weak learners), schedule, k, lambda alpha in {0.5, 1, 2, 4}; num_samples/relaxation_schedule stay fixed
- Expected to fix the score degeneracy found at Sprint 3 validation (near-uniform weights under lambda=2*n_train; unweighted weak learners voting -1 on ~99.8% of rows): smaller lambda spreads scores, weighted weak learners grade the votes
- Produces the proxy config RANKING that G0b's top-3 + bottom-2 hardware fits require; lg pools return to tables only if tuning fixes them
- Inline addition (Sprint 3 retro improvement 1, approved): score-distribution health check -- threshold tie_fraction/mode-share in summarize output, WARN flag in rows and gate report (~20m, amendment-registered code change)
- Depends on: nothing (proxy-only); blocks G0b execution

**F21. Baseline-protocol research: duplicates methodology + ULB feature engineering (~2h) Priority 12**
- Phase: Experiments (team-lead request at Sprint 3 validation, re G0 FAIL)
- Platform: docs -> possible amendment proposal
- Research published ULB methodology: how do strong published baselines handle exact duplicates (retain? partial? per which papers); what leakage-free feature engineering exists (Amount/Time transforms, interaction features); what protocol differences explain the 0.85-0.88 literature band vs our 0.8296
- Output: findings memo with a recommended amendment proposal if justified (e.g., a LABELED duplicate-retained sensitivity protocol as an added exploratory analysis -- allowed by section 11; the primary protocol and G0's scored outcome stay as committed) -> team-lead disposition, then retry under the amended protocol if approved
- Depends on: nothing

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

**F19. Draft submission PDF(s) to QCi (~2h assemble + team-lead send) Priority 13**
- Phase: External (team-lead request 2026-09-02: "send a draft of the PDFs we will eventually submit ... based on what we have by the end of the next sprint")
- Platform: docs
- Assemble the best draft-state package available at that sprint's end (expected: preregistration incl. amendments, gate report / results memo, hardware plan; the F8 paper draft only if it exists yet), rendered as PDF(s) marked DRAFT
- MANDATORY pre-send confidentiality scan of every page (the Stage 7 scan run early, scoped to the sent artifacts: no employer references, no account identifiers, no QPU balances tied to a named account)
- Team lead reviews and personally sends; Claude records what was sent and when in requirements-matrix
- Value: progress evidence for the pending QCi grant; early feedback on how Dirac-3 is represented; honors the sponsorship letter's collaborative framing
- Depends on: end-of-next-sprint state (F7 results memo strengthens it; F8 not required)

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

(F11 QCi sponsorship letter send: COMPLETED by the team lead 2026-08-30. F12 portal verification and F15 best-practices/ADR review: COMPLETED in Sprint 2, merged via PR #2; history in SPRINT_2_SUMMARY.md. All three removed from candidates per convention.)

**F16. Minimal CI: pytest + lint on PRs with smoke fixture (~30m) Priority 34**
- Phase: Finalize
- Platform: docs
- GitHub Actions on PRs to develop; sub-minute; no dataset or metered access
- Backlogged per the approved 2026-08-30 disposition (item 11)

### HOLD Items (post-submission)

**F17. Dirac-3 simulator for pre-hardware test runs (~2-3h investigation, build TBD) Priority HOLD**
- Phase: Phase 2 preparation (team lead: "prioritize for after submission")
- Platform: Dirac-3 / local
- Investigate quantumcomputinginc.com products, docs, papers to build a simulator-backed QBoostClassifier: same QUBO objective, classical optimizer backend (SLSQP/Hexaly precedent in Emami et al.), device-behavior modeling (sum constraint, ~23 dB dynamic-range clipping, num_samples stochasticity), miniaturized data subsets so every test run completes in <= 10 minutes
- Preliminary feasibility: YES (Sprint 2 retro category 14, Function Updates for the Future Backlog); pre-submission value judged low because ADR-0002's proxy plus the G0b fidelity gate already fill the role and changes would require prereg amendments

**F20. Soft-vote CVQBoost exploration (multi-level weak outputs) (~3h proxy investigation) Priority HOLD**
- Phase: Phase 2 preparation (team-lead approved 2026-09-02, "fits naturally as a post-submission/Phase 2 exploration item next to F17")
- Platform: local proxy first; Dirac-3 only if the proxy shows signal
- Replace hard +/-1 weak-classifier votes in the H matrix with confidence scores (predict_proba mapped to [-1,1], optionally discretized to the device's ~200-level dynamic range); same Hamiltonian shape (J=HH^T+lambda*I, C=-2Hy), same simplex solve -- a model variant, not a protocol change
- Rationale: hard votes discard per-learner confidence; the weights are already continuous (CVQBoost), so the information bottleneck is the vote quantization
- Zero-cost evaluation path: proxy side-by-side vs hard-vote pools on identical seeds (the A3 comparison machinery reused verbatim)
- Constraints: custom H construction departs from eqc-models' builders (pool identity with the library is lost; document as its own arm); Phase 1 evidence chain untouched; any Phase 2 use enters through that phase's preregistration
- Depends on: F17 pairs well (the simulator would evaluate both); nothing blocks the proxy investigation

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
