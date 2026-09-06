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
| 6 | docs/sprints/SPRINT_6_SUMMARY.md | [OK] Complete | ~1 day (Sep 5, 2026) |
| 7 | docs/sprints/SPRINT_7_SUMMARY.md | [OK] Complete | ~1 day (Sep 5, 2026) |

## Last Completed Sprint

**Sprint 7: Direction into Result** (Sep 5, 2026; PR #41).
Delivered: **F33** -- a tuned four-family pool reaches 0.7827 AUPRC (SD 0.0283) over ten seeds against 0.7565 untuned and ~0.80 reported by Loke et al. The MATCHED comparison is the one reported: the frozen single-family pool rebuilt at the same k=6 on the same splits gives a PAIRED +0.0198 (SD 0.0203), 9 of 10 seeds positive, still BELOW the 0.0268 MDE. **F34** -- eight spend-guard property tests, each asserting the property whose violation caused a real defect, verified to fail on the originals. Amendments A13 (registered before the run) and A14.
**The finding**: the accuracy came from the LEARNERS, not the optimizer. Solved-minus-uniform on the tuned pool is +0.0043. Fit-time class weighting -- inside each weak learner as it is built, the one intervention no earlier control varied -- drops the Gram ratio from 0.9988 to 0.92 and lifts absolute accuracy, while the optimization step stays nearly free. For CVQBoost at low prevalence the leverage is pool construction.
**Two corrections to our own interpretation**, both registered as A14: a mid-run prediction compared sweep VALIDATION AP against TEST AP comparators (validation runs ~0.005 below test on this design), and the k=6 tuned arm was initially set against k=13 comparators -- the order-mismatched comparison ADR-0013 warns of, which the Sprint 7 plan itself had invited by naming the k=13 figure as an acceptance criterion.
Retro: docs/sprints/SPRINT_7_RETROSPECTIVE.md (4 improvements, all applied or registered; suite 125 -> 132).

## Deferred to Phase 2 (team lead, 2026-09-05)

**Does F33 change the Phase 2 priority?** Held until after the submission is
approved. The open question, recorded now so it is not re-derived later: F33
measured the optimizer contributing only +0.0043 over uniform weights even on a
well-constructed pool, while fit-time learner tuning moved absolute accuracy by
+0.0198 at matched size. That is an argument that the leverage in this
formulation sits in pool construction rather than in the optimization step, and
it bears directly on whether the cardinality-constrained integer experiment (F25)
remains the first Phase 2 experiment or yields to pool work. Both readings are
defensible on the current evidence: the integer formulation is the one where a
classical solve is NOT trivially available, so a small optimizer contribution on
a CONVEX problem does not predict a small one on an NP-hard problem. Deciding
now would be deciding without the evidence that Phase 2 exists to gather.

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

**F33. Tune the mixed pool toward the Loke et al. configuration (~4-6h, zero metered) Priority 1**
- Phase: Experiments (Sprint 6 retrospective, Claude category 14; team lead selected for Sprint 7 on 2026-09-05)
- Platform: ULB classical proxy only. ZERO metered seconds
- **The gap this closes**: F31 established that a heterogeneous pool makes the optimizer work (L1 from uniform 0.127 against 8.0e-08, +0.0076 on 10 of 10 seeds, tie-breaking ruled out by two controls). But the mixed pool's ABSOLUTE AUPRC is 0.7565, BELOW the frozen pool's 0.7681 and well below the 0.8+ Loke et al. report on the same hardware and benchmark family. Diversity bought the optimizer headroom, not accuracy. F33 tests whether the remaining gap is learner QUALITY and tuning rather than pool composition
- **Design**: adopt Loke et al.'s families at their reported hyperparameters (KNN, LDA, logistic regression, XGBoost) rather than our defaults; add imbalance handling AT FIT TIME (class-weighted and balanced-bootstrap learners), which the A11 mixed pool did not vary and which the Sprint 5 class-weighted control explicitly did NOT test since it reweighted only the ensemble objective; sweep the per-family learner count against the free-tier 100-variable ceiling (A12), since four families at k=6 gives 60 variables and leaves headroom
- **Acceptance**: report absolute AUPRC against both the frozen pool (0.7681) and the Loke figure (>0.8), the solved-minus-uniform difference against the 0.0268 MDE, and the pool-diversity measures before optimization. A configuration that clears the frozen pool's absolute AUPRC while keeping a non-degenerate optimum is the result that would change the submission's headline from a direction to a finding
- **Honesty constraints**: exploratory under a dated amendment; H1b and every frozen gate keep their committed scoring; the Loke comparison is a design comparison, never a claim to have reproduced their number
- Depends on: F31 (done). Sequence BEFORE F3, per the team lead's 2026-09-05 decision

**F34. Spend-guard property tests (~1h) Priority 3**
- Phase: Experiments/tooling (Sprint 6 retrospective, Claude category 10)
- Platform: N/A
- **Why**: the metered spend guard had TWO arithmetic defects in one sprint. A cap was set at 60 s when 50 s was approved, which would have let the code authorize spend the team lead did not grant. And the pre-call projection added `_spent()` (which reads results.json) to the in-memory rows that `append_row` had ALREADY written there, double-counting every fit, so the block halted at a reported 50.0 s when 25.0 s had been spent and four approved seeds were lost. A guard whose own arithmetic is wrong is a risk, not a mitigation
- **Design**: property tests asserting the cap never exceeds the stated approval; that spend is computed from exactly one source of truth so double-counting is structurally impossible; that unparseable billing is charged the conservative estimate and flagged rather than counted as zero (A8); and that the cap bounds the call it PRECEDES rather than the one after it
- Depends on: nothing

**F35. Interpretation-layer tests (~2h) Priority 2**
- Phase: Experiments/tooling (Sprint 7 retrospective, Claude category 14)
- Platform: N/A
- **Why**: across three sprints the defects that travelled furthest were claims about what a number MEANS, not errors in the number. Sprint 5 reported a weight vector "exactly uniform" at 0.000000 when it was 8.0e-08, and the gain it implied was tie-breaking. Sprint 6 presented k=13 [SIM] mechanism evidence and k=6 [HW] hardware evidence as one narrative. Sprint 7 differenced a k=6 arm against k=13 comparators and compared sweep VALIDATION AP against TEST AP. Every one was caught by reading; none by a test
- **Already partly built**: `comparators.py` (improvement 1) refuses a difference whose arms mismatch on k, protocol, schedule or dataset, and refuses validation against test. F35 extends that from the computation to the DOCUMENT
- **Design**: assert that every quantitative claim in docs/paper/*.md that quotes a difference names its comparator's configuration; that no figure tagged [HW] appears in a sentence whose mechanism evidence is [SIM] without the distinction stated; that a difference quoted below the A5 MDE carries directional language rather than win language; and that rounding in prose never asserts more precision than the stored value supports (the Sprint 5 "0.000000" case)
- **Honest limit**: some of this is genuinely hard to test mechanically and will end up as a checklist rather than an assertion. The parts that CAN be asserted are worth asserting, and the parts that cannot belong in STATISTICAL_REVIEW_CHECKLIST where a human walks them
- Depends on: nothing (comparators.py already landed)

**F3. IEEE-CIS reduced Deotte recipe + temporal protocols (~1 day) Priority 14**
- Phase: Experiments
- Platform: IEEE-CIS
- **Scope decision (team lead, 2026-09-05)**: run BOTH pool configurations, the frozen single-family arm and the F33 tuned four-family arm. The frozen arm is the preregistered comparator and must be carried for continuity; the tuned arm is where F33 measured the accuracy to live. Running only one would either break comparability with every prior result or omit the configuration the evidence now favours
- Preregistered feature pass (D-normalization, UID excluded, named aggregates, V-reduction); leakage controls incl. shuffled-label positive control
- GroupKFold-by-month rolling origin; classical arms + proxy CVQBoost on the reduced set; H3 ladder cells
- Depends on: F1

**F29. Sample-size insensitivity of the CVQBoost optimum (~2h proxy, zero metered) Priority 15**
- Phase: Experiments (team-lead observation 2026-09-04; run "if we have time before submission", include only if the evidence supports it)
- Platform: ULB proxy (zero metered seconds); IEEE-CIS as a second regime if F3 lands first
- **The observation to test**: the team lead has repeatedly measured equivalent CVQBoost predictions training on 250k, 1M, 2M, 3M, 5M, 6M and 7M rows, across multiple datasets, in prior work outside this repository. No paper found in a survey of the QML randomness/generalization literature states this result; Caro et al. (few-training-data generalization) bounds a different quantity and assumes trainable gates that CVQBoost does not have, so it must NOT be cited as direct support
- **Candidate mechanism, from this project's own Sprint 4 finding**: both Hamiltonian terms scale linearly with n_train (J = HH^T + lambda*I with entries summed over rows; C = -2Hy), so scaling the row count scales the objective without moving its argmin. The optimum depends on the correlation structure among weak learners, which stabilizes once enough rows estimate it. The lambda sweep already showed the solution sits at near-uniform weights regardless of lambda
- **Design (all on the exact proxy)**: build pools at n in {50k, 100k, 250k, 500k, full} from the same seed's train fold, identical feature set and weak-learner config; report (a) cosine similarity of the optimal weight vectors against the full-n solution, (b) test AP at each n with seed CIs, (c) the n at which both curves flatten. Repeat across 3 seeds. Zero metered seconds; hardware confirmation only if the proxy curve is interesting and budget allows
- **Honesty constraints**: enters as a LABELED EXPLORATORY analysis under a dated amendment, never as a headline or a preregistered result; prior-work evidence gets the same provenance disclosure as the FourierWall2 material; and the paper must connect it to the near-degeneracy finding rather than let a reviewer discover the link, since "the optimum is insensitive to sample size" and "the optimum is nearly degenerate" are adjacent claims
- **Why it could matter to the submission**: training cost, retraining cadence, and data-retention footprint are production concerns a bank weighs directly; a measured "this arm reaches its ceiling at a fraction of the data" is practical evidence in the production-bound framing (F27), if it holds
- Depends on: nothing (reuses qubo_proxy build/solve); best run after F8 so it cannot displace paper work

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
