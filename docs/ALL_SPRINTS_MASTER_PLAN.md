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
| 4 | docs/sprints/SPRINT_4_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 3-4, 2026) |

## Last Completed Sprint

**Sprint 4: Proxy Tuning, Baseline Research, First Hardware Blocks, Results Memo** (Sep 3-4, 2026; PR #21 merged to develop, develop merged to main via PR #22).
Delivered: F22 section-6 proxy tuning (100 trials; validation-AP rule retained the starting config; lg quarantine lifted); F21 research showing G0's 0.85 band is uncorroborated by primary sources (G0 still FAIL as committed); **F2 first metered hardware campaign -- 27 Dirac-3 fits, 120 QPU s, 0 failures, G0b PASSED at Spearman 0.900**; H4 solver-fidelity component measured at -0.0010 [CI -0.0032, +0.0012] with the lambda sweep showing near-degeneracy is structural, not ridge-driven; H1b null as preregistered (-0.0399 vs CatBoost); F7 results memo with the production-bound framing DECIDED. Amendments A6/A7/A8. 17 review findings fixed across two reviews. Retro: docs/sprints/SPRINT_4_RETROSPECTIVE.md (7 improvements applied).

## Targeted roadmap (team lead, 2026-09-03; each sprint's scope is re-validated at its own refinement)

| Sprint | Dates | Targeted scope | Gate |
|---|---|---|---|
| 4 | Sep 3-5 | F22, F21, F2 (per-block approval), F7 | -- |
| 5 | Sep 5-7 | F8, F9, then F19 at sprint end (QCi package with the actual paper draft) | -- |
| 6 | Sep 7-9 | F3 + paper updates (outline, draft, diff-scoped reviews, rubric) + F23/F24 prep in parallel agents | still time for F16 + F10 |
| 7 | Sep 9-11 | F4 + paper updates | still time for F16 + F10 |
| 8 | Sep 11-12 | F5 (or its named fallback) + paper updates | still time for F16 + F10 |
| Finalize | Sep 12-13 | F16, F10; submit Sep 13 | no new evidence after Sep 12; never later than Sep 14 |

A submittable paper exists after Sprint 5; every later sprint adds evidence and re-runs the review loop on the diff. The "still time" gate is a calendar lookup against the Sep 12 evidence freeze.

## Next Sprint Candidates

### Experiments (Stage 3 of the master timeline; submission-ready Sep 8)

(F1 classical evidence campaign and F18 Dirac-3 notes mining: COMPLETED in Sprint 3, merged via PR #13; history in SPRINT_3_SUMMARY.md. Removed from candidates per convention. F1 residual -- the section-6 CVQBoost proxy tuning -- continues as F22.)

(F22 CVQBoost proxy tuning and F2 hardware blocks B1+G0b: COMPLETED in Sprint 4, merged via PR #21; history in SPRINT_4_SUMMARY.md. F21 baseline research and F7 results memo likewise complete. Removed from candidates per convention. F2's remaining blocks B2/B3/B4/B5 continue as F2b below, gated on the QCi grant.)

**F2b. Hardware campaign, remaining blocks (~0.5 day + approvals) Priority 20**
- Phase: Experiments
- Platform: Dirac-3
- B2 (ULB full config, 816 vars, 11 fits, ~450 s), B3 (IEEE-CIS + H3 ladder, 16 fits, ~650 s), B4 (SPECTRA, 15 fits, ~450 s), B5 (QSVM sign-augmented, 12 fits, ~15 s); frozen spend priority B3 > B2 > ladder > B4
- B1 + G0b already executed (Sprint 4, 120 QPU s); ~380 s of the current balance remain, so B5 is affordable now and the rest need the grant
- Depends on: QCi grant; per-block team-lead approval (Criterion H)

**F26. Cost-based operating-point analysis (~2h) Priority 13**
- Phase: Experiments (team-lead direction 2026-09-03: the proposal must read as production-bound)
- Platform: ULB, docs (zero metered seconds; reuses existing rows)
- Report every arm at a realistic review capacity (alerts/day budget) and under an asymmetric cost assumption (missed fraud vs declined-good-customer), alongside AUPRC: "fraud caught per analyst-hour" is the number a fraud team buys on
- Uses the existing validation-chosen operating points (metrics.evaluate_at, threshold_alert_budget) and the persisted-prediction fix shared with A7 cell S1; states cost assumptions explicitly as assumptions, with a sensitivity range
- Output: a cost table for the paper's Validation section + one paragraph translating AUPRC into operational terms
- Depends on: prediction persistence (shared with A7 S1)

**F27. Production-trial design section (~2h) Priority 13**
- Phase: Paper (team-lead direction 2026-09-03)
- Platform: docs
- A concrete 90-day trial the bank could start: shadow-mode scoring against live traffic, champion/challenger vs the incumbent, the review-capacity operating point, latency budget for real-time scoring, calibration requirements for the downstream rules engine, drift monitoring with named retraining triggers, and the dispute/regulator explainability path
- Cites measured inputs we already hold: per-fit hardware cost (4-5 QPU s), calibration data, operating points, the temporal-decay question from the Sprint 4 temporal rows
- Names the free-tier feature constraint honestly: 13 features fit the device tier, not the problem; production sizing math included
- Depends on: F7 memo (done); feeds F8

**F28. Explainability thread: ensemble inspectability vs GBDT baseline (~3h) Priority 14**
- Phase: Experiments + Paper (team-lead direction 2026-09-03; team lead has prior QML explainability work to cite as capability)
- Platform: ULB, docs (zero metered seconds)
- Structural argument plus evidence: a CVQBoost ensemble is a weighted vote over small, individually inspectable weak learners (1-3 features each), versus a 2,000-tree boosted model requiring post-hoc attribution; quantify with weight concentration, per-learner feature attribution, and a worked single-decision explanation for both arms
- Frames explainability as the bar that actually gates deployment in banking (dispute handling, regulator review), not as a nice-to-have
- Output: an explainability subsection for the paper with a side-by-side worked example
- Depends on: existing pools and rows; team-lead input on which prior QML explainability work to cite

**F3. IEEE-CIS reduced Deotte recipe + temporal protocols (~1 day) Priority 14**
- Phase: Experiments
- Platform: IEEE-CIS
- Preregistered feature pass (D-normalization, UID excluded, named aggregates, V-reduction); leakage controls incl. shuffled-label positive control
- GroupKFold-by-month rolling origin; classical arms + proxy CVQBoost on the reduced set; H3 ladder cells
- Depends on: F1

**F23. F4 prep: QFE phase recipe + twin scaffolding (~3h, subagent-parallel) Priority 15**
- Phase: Experiments (team-lead roadmap 2026-09-03: prep in Sprint 6 alongside F3, execution F4 in Sprint 7)
- Platform: ULB (IEEE-CIS later), docs
- Implement the exact Fourier Wall phase recipe as a fitted, train-only transformer: rank phase phi = 2*pi*(rank - 1/2)/n - pi, log magnitudes first, calendar cycles (ULB Time -> daily cycle), train-only whitening, low-cardinality columns excluded from encoded blocks; known-answer tests (phase range, rank invariance, no test leakage)
- Capability pre-flights for the three twin families the H6 bar requires: trained-frequency GAM, GA2M, and the JOINT twin (supervised coarse-to-fine cosine frequency scan fit by logistic regression); pin dependencies; ADR candidate recording the twin design (Fourier Wall: omitting the twin manufactures fake quantum wins)
- Freeze the H6 cell list (arms x representation), the results.json representation tag, and the A2 variable-count implications of phase blocks for CVQBoost (n changes -> free-tier/device bounds re-checked)
- No arm is RUN in prep; execution is F4. Zero metered seconds
- Depends on: F1 (done); F22 (tuned proxy config so H6 sits on a tuned CVQBoost)

**F24. F5 prep: SPECTRA in-segment machinery + B4 request (~3h, subagent-parallel) Priority 15**
- Phase: Experiments (team-lead roadmap 2026-09-03: prep in Sprint 6, execution F5 in Sprint 8)
- Platform: SPECTRA, Dirac-3 (request only)
- In-segment evaluation machinery per H5: in_pocket segment metrics, matched random-segment negative control (same size and base rate), the >= 50-test-positives-per-cell rule, 5-seed splits, leak-free contract enforced (target/target_real/in_pocket never features); tests
- Identify the 3 strongest in-segment cells from the FourierWall2 evidence (experiments/reference/fourierwall2/) and freeze them with config hashes; prove via scripts/manifest.py whether the staged SPECTRA files match or differ from the FourierWall2-era files (ADR-0003 requirement for B4)
- Proxy dry run on the 3 cells (zero metered) to set expected values; write the B4 hardware request (15 fits, ~450 QPU s) in the HARDWARE_REQUEST template, ready for grant arrival
- Named fallback for Sprint 8 if no grant: proxy-only replication labeled [SIM], or the sprint re-scopes to an F4 extension -- decided by the team lead at Sprint 8 refinement
- Depends on: F1 (done); QCi grant status for the hardware path

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

(F7 results memo + gate review: COMPLETED Sprint 4 -> docs/RESULTS_MEMO.md. A REFRESH of the memo is folded into each later evidence sprint rather than tracked as a separate item.)

### Paper (Stages 4-6)

**F8. Outline + Draft V1 (~1 day) Priority 30**
- Phase: Paper
- Platform: docs
- Inline addition (Sprint 4 retro improvement 1, approved): known-answer tests for score_gates.py aggregation -- gate verdicts, paired deltas, Spearman, cell keying against hand-computed fixtures (~45m); every reported number passes through this code and it is currently untested
- Seven rubric-mapped sections + appendices; [HW]/[SIM]/[PROJ] tags; prevalence beside every AUPRC; references from docs/references.md
- Depends on: F7; team-lead outline approval

**F9. Adversarial reviews V2/V3 + rubric pass (~0.5 day) Priority 32**
- Phase: Paper
- Platform: docs
- Domain pass, quantum pass (encoding diagnostics, evidence-tag audit), rubric scoring; fix lowest criterion
- Depends on: F8

**F19. Draft submission PDF(s) to QCi (~2h assemble + team-lead send) Priority 34**
- Phase: External (team-lead request 2026-09-02; moved 2026-09-03 to the END of Sprint 5 so the package carries the actual F8/F9 paper draft)
- Platform: docs
- Assemble the Sprint-5-end package: the F8/F9 paper draft (reviewed, rubric-scored) plus preregistration incl. amendments, gate report / results memo, and hardware plan, rendered as PDF(s) marked DRAFT
- MANDATORY pre-send confidentiality scan of every page (the Stage 7 scan run early, scoped to the sent artifacts: no employer references, no account identifiers, no QPU balances tied to a named account)
- Team lead reviews and personally sends; Claude records what was sent and when in requirements-matrix
- Value: progress evidence for the pending QCi grant; early feedback on how Dirac-3 is represented; honors the sponsorship letter's collaborative framing
- Depends on: F8, F9 (Sprint 5)

### Finalize (Stages 7-8)

**F10. Verification, confidentiality scan, compliance walk, submission (~0.5 day) Priority 40**
- Phase: Finalize
- Platform: docs
- Every number vs results.json; repo-wide confidential-string scan (fourierwall2 reference files file-by-file); requirements-matrix walk; public reproducibility repo; team-lead final PDF + portal submission, receipt archived
- Depends on: F8, F9

### External (team-lead-owned, parallel)

(F11 QCi sponsorship letter send: COMPLETED by the team lead 2026-08-30. F12 portal verification and F15 best-practices/ADR review: COMPLETED in Sprint 2, merged via PR #2; history in SPRINT_2_SUMMARY.md. All three removed from candidates per convention.)

**F16. Minimal CI: pytest + lint on PRs with smoke fixture (~30m) Priority 36**
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

**F25. Non-convex CVQBoost: cardinality-constrained weak-learner selection on Dirac-3 (~4h investigation + hardware) Priority HOLD**
- Phase: Phase 2 (team-lead approved 2026-09-03; the direct consequence of the Sprint 4 degeneracy finding)
- Platform: Dirac-3 integer/qudit solver, local proxy for the relaxation only
- The Sprint 4 evidence: the continuous-weight formulation is strictly convex AND nearly degenerate (uniform weights even at lambda = 0), so an exact classical proxy always matches the hardware. The formulation where that stops being true is combinatorial selection: choose the best subset of m weak learners from a pool of n (cardinality or L0 sparsity constraint), optionally with integer weights -- NP-hard, no exact classical proxy, and the native problem class for Dirac-3's integer solver (num_levels budget against the documented 949 device limit)
- Design sketch: same H matrix and objective, plus a cardinality constraint; classical comparators become greedy/forward selection, L1-then-threshold, and a MIP solver at small n; the honest question is solution QUALITY at fixed wall-clock, not just feasibility
- Expected value: this is the concrete "where quantum optimization is necessary rather than optional" program the Phase 1 paper points at, and the strongest technical item for the QCi conversation
- Depends on: Phase 2 preregistration; QCi grant for meaningful hardware time; pairs with F17 (simulator) and F20 (soft votes)

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
