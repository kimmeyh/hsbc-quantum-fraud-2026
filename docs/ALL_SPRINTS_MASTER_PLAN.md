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
| 5 | docs/sprints/SPRINT_5_SUMMARY.md | [OK] Complete | ~1 day (Sep 4, 2026) |

## Last Completed Sprint

**Sprint 5: The Paper and the QCi Package** (Sep 4, 2026; PR #29 merged to develop, develop merged to main via PR #30).
Delivered: F8/F9 the submission documents (proposal 6/6 pages, appendix 3/3, team profile 1/1, all verified US Letter); F27 production-trial design; F26 cost-based operating points with the budget ceiling stated; F28 explainability thread with its scope limit; F19 QCi package, six DRAFT PDFs, team lead disposition "consider it sent". **The mechanism controls settled the flat optimum**: the cause is POOL DEGENERACY measured at the learner level (off-diagonal Gram 170,234.4 vs diagonal 170,235; any two learners agree on 99.999% of rows), not the simplex constraint as Sprint 4 had attributed it. Solver dispersion recovered at zero metered cost (0 of 27 fits returned identical draws; spread median 0.019%). Three external reviews applied with written dispositions. Amendments A9 (prediction-store keying; affected figures retagged [SIM]) and A10 (hardware predictions version-controlled).
Two defects worth carrying forward: the prediction-key collision, where the proxy backfill silently overwrote hardware predictions because hardware and proxy deliberately share a config_hash; and **"exactly uniform" was not exact** (8.0e-08, not 0), where the residual +0.0022 turned out to be TIE-BREAKING rather than optimization, which strengthens the finding to "the optimizer contributes nothing at all". All nine PDFs had also rendered 11x17 TABLOID via the old Word path, invalidating every page count; found only because the team lead asked.
Literature find: **Loke et al., ICAART 2026** -- same Dirac-3 hardware, same algorithm, same benchmark family, AUC-PR above 0.8 against our 0.767, with a heterogeneous pool. Independent corroboration of the degeneracy diagnosis and the motivation for F31.
Retro: docs/sprints/SPRINT_5_RETROSPECTIVE.md (7 improvements, all applied or registered; test suite 28 -> 50).

## Targeted roadmap (team lead, 2026-09-03; each sprint's scope is re-validated at its own refinement)

| Sprint | Dates | Targeted scope | Gate |
|---|---|---|---|
| 4 | Sep 3-5 | F22, F21, F2 (per-block approval), F7 | -- |
| 5 | Sep 4 | [DONE] F8, F9, F27, F26, F28, F19 | -- |
| 6 | Sep 5-7 | **F31 (diverse pool, team lead approved 2026-09-04)** + F3 + paper updates (diff-scoped reviews, rubric) + F23/F24 prep in parallel agents | still time for F16 + F10 |
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

**F31. Diverse weak-learner pool: replicate the Loke et al. pool construction (~6-10h, zero metered) Priority 1**
- Phase: Experiments (Sprint 5 retrospective, Claude category 14; team lead approved 2026-09-04 for Sprint 6 entry)
- Platform: ULB classical proxy only. ZERO metered seconds; hardware confirmation is a separate card (F32)
- **Why this is priority 1**: every external reviewer (Claude app, Codex 5.5, Codex 5.6) independently identified pool degeneracy as the central technical weakness, and Sprint 5 measured it directly: off-diagonal Gram entries average 170,234.4 against a diagonal of 170,235, so any two of our 91 depth-limited trees agree on 99.999% of training rows. With interchangeable learners uniform weights are genuinely optimal and NO optimizer, quantum or classical, can do useful work. The optimization step currently contributes nothing: the apparent +0.0022 is tie-breaking among transactions the pool cannot separate
- **The published target**: Loke, Sahoo, Guan, Xu, Verma and Griffin, "Improving credit card transaction fraud detection using CVQBoosting", ICAART 2026 (Singapore Management University) ran CVQBoost on the SAME Dirac-3 hardware against the SAME benchmark family with a HETEROGENEOUS pool (k-nearest neighbours, linear discriminant analysis, logistic regression, XGBoost) and reported mean AUC-PR above 0.8 against our 0.767. Same hardware, same algorithm, different pool, better result: that is the cleanest available evidence that pool construction is the binding constraint
- **Design**: build pools mixing learner FAMILIES (KNN, LDA, logistic regression, shallow boosted variants, trees at differing depths and feature subsets) rather than one family over many feature subsets; add imbalance handling AT FIT TIME (class-weighted and balanced-bootstrap learners), which the Sprint 5 class-weighted control explicitly did NOT test since it reweighted only the ensemble objective. Report pairwise prediction disagreement, residual-error correlation, distinct-score-vector count, and the Gram off-diagonal ratio as pool-diversity measures BEFORE any optimization, then uniform-weight AP against solved AP on the same pool
- **The decisive measurement**: does the solved optimum leave uniform? If the weight vector becomes non-degenerate and solved AP separates from uniform AP by more than the 0.0268 MDE, the optimizer has something to do and the quantum arm becomes worth a hardware run. If it stays uniform on a genuinely diverse pool, that is a stronger and more interesting negative result than the one we have
- **Honesty constraints**: enters as a LABELED EXPLORATORY analysis under a dated amendment; the frozen H1b result stands unchanged and is not rescored; the Loke et al. comparison is a design comparison, never a claim that we reproduced their number
- Depends on: nothing (classical only, reuses the qubo_proxy build/solve path)

**F32. Hardware prediction persistence, so operating points carry [HW] (~2h + 40-50 metered device seconds) Priority 2**
- Phase: Experiments (Sprint 5 retrospective, Claude category 14; external review finding 20)
- Platform: Dirac-3. REQUIRES explicit team-lead approval with call count and expected seconds stated (Criterion H)
- **The gap**: every operating-point figure in the proposal and appendix (recall at 0.05%/0.1%/0.5% budgets, precision at budget) is computed from the EXACT CLASSICAL PROXY and tagged [SIM], because Dirac-3 solution weights were not persisted during the Sprint 4 campaign. The substitution is licensed by measurement (hardware minus proxy is -0.0010 AUPRC with the interval containing zero) but aggregate AP similarity does NOT establish transaction-level or top-k equivalence, which is what an alert budget actually depends on
- **Design**: one fit per seed on the selected configuration with weights and per-transaction scores persisted (store.prediction_path already keys by arm after the A9 fix, so hardware and proxy predictions can coexist). Report hardware AP, recall at each budget, alert-set Jaccard overlap against the proxy, and cutoff tie behaviour. Three repetitions per seed would additionally quantify draw-to-draw variability at ~120-150 metered seconds
- **Cost**: ~40-50 metered device seconds for one job per seed at the measured 4-5s per fit; ~120-150 for three repetitions
- **Why it matters to the submission**: it converts the operational table, which is the table a bank actually reads, from [SIM] to [HW]
- Depends on: team-lead hardware approval; best sequenced AFTER F31 so the metered time is spent on a pool worth measuring

**F29. Sample-size insensitivity of the CVQBoost optimum (~2h proxy, zero metered) Priority 15**
- Phase: Experiments (team-lead observation 2026-09-04; run "if we have time before submission", include only if the evidence supports it)
- Platform: ULB proxy (zero metered seconds); IEEE-CIS as a second regime if F3 lands first
- **The observation to test**: the team lead has repeatedly measured equivalent CVQBoost predictions training on 250k, 1M, 2M, 3M, 5M, 6M and 7M rows, across multiple datasets, in prior work outside this repository. No paper found in a survey of the QML randomness/generalization literature states this result; Caro et al. (few-training-data generalization) bounds a different quantity and assumes trainable gates that CVQBoost does not have, so it must NOT be cited as direct support
- **Candidate mechanism, from this project's own Sprint 4 finding**: both Hamiltonian terms scale linearly with n_train (J = HH^T + lambda*I with entries summed over rows; C = -2Hy), so scaling the row count scales the objective without moving its argmin. The optimum depends on the correlation structure among weak learners, which stabilizes once enough rows estimate it. The lambda sweep already showed the solution sits at near-uniform weights regardless of lambda
- **Design (all on the exact proxy)**: build pools at n in {50k, 100k, 250k, 500k, full} from the same seed's train fold, identical feature set and weak-learner config; report (a) cosine similarity of the optimal weight vectors against the full-n solution, (b) test AP at each n with seed CIs, (c) the n at which both curves flatten. Repeat across 3 seeds. Zero metered seconds; hardware confirmation only if the proxy curve is interesting and budget allows
- **Honesty constraints**: enters as a LABELED EXPLORATORY analysis under a dated amendment, never as a headline or a preregistered result; prior-work evidence gets the same provenance disclosure as the FourierWall2 material; and the paper must connect it to the near-degeneracy finding rather than let a reviewer discover the link, since "the optimum is insensitive to sample size" and "the optimum is nearly degenerate" are adjacent claims
- **Why it could matter to the submission**: training cost, retraining cadence, and data-retention footprint are production concerns a bank weighs directly; a measured "this arm reaches its ceiling at a fraction of the data" is practical evidence in the production-bound framing (F27), if it holds
- Depends on: nothing (reuses qubo_proxy build/solve); best run after F8 so it cannot displace paper work

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

**F30. Concurrent Dirac-3 submission with bounded in-flight requests (~4h build + 1h dry run) Priority HOLD**
- Phase: Phase 2 preparation / infrastructure (team-lead request 2026-09-04)
- Platform: Dirac-3 (offline-testable; gated live vetting of 2-3 calls only)
- Dirac-3 queues one job at a time, so a 4-5 QPU s fit cost ~85 s of wall clock in Sprint 4; nearly all elapsed time is queue wait. Multiple requests CAN be enqueued concurrently, via separate processes or async submission inside one program
- Design: a BOUNDED window (default 4) of in-flight requests, topping up by one as each completes. Metered calls cannot be wasted, so the window is deliberately small: a reboot or network failure risks only the in-flight requests, never a 20-call block
- Crash safety: a durable job ledger records submission intent and job ids before each call, so a restart retrieves results for in-flight jobs instead of re-billing them
- Preserves every existing guard: spend caps computed against projected spend INCLUDING in-flight requests, frozen identical-config retry rule, B1 hash verification, unparseable-billing charge
- Fully tested offline first (fake client simulating queue latency, out-of-order completion, crash-restart, failed job, unreadable billing); only then 2-3 real calls at window size 2, on explicit approval
- Full card drafted at docs/sprints/drafts/F30_CARD_DRAFT.md
- Value arrives with Phase 2 volume (81+ fit grids); not recommended before submission
- Depends on: nothing to build; live vetting needs team-lead approval (Criterion H)

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
