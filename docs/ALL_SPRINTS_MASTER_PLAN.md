# All Sprints Master Plan

Adapted 2026-08-30 from spamfilter-multi's ALL_SPRINTS_MASTER_PLAN.md structure. This document is IN THE REPOSITORY and persists across conversations. Read it before every sprint (Phase 1/2), update it after every sprint (Phase 7.7/8.2).

## Maintenance Guide

- **After each sprint (Phase 7.7 / 8.2)**: update "Last Completed Sprint"; add the sprint's row to "Past Sprint Summary" once its SUMMARY doc exists; prune shipped items from "Next Sprint Candidates"; add retro Category-14 items with new F#s.
- **During Sprint N+1 planning (Phase 3.2.1)**: create `docs/sprints/SPRINT_N_SUMMARY.md` for the just-finished sprint and link it here.
- **IDs**: F# for all features/process/tech-debt items; next available number; never reuse.
- **Estimates**: minutes/hours from recorded actuals; `[no-history]` where uncalibrated.
- `CHECKLIST-Phase2.md` is the LIVE deliverable ledger; this document is the sprint-scoping view over it. Keep them consistent; the checklist wins on deliverable truth, this file wins on sprint sequencing. (`CHECKLIST-Phase1.md` is the CLOSED Phase 1 record and is never updated. The repo-root `CHECKLIST.md` was split into three files on 2026-09-12; `CHECKLIST-Phase2-pre.md` was merged into `CHECKLIST-Phase2.md` and deleted on 2026-10-03, and items 5 and 6 of the six were corrected to match the filed proposal at the same time.)

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
| 8 | docs/sprints/SPRINT_8_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 6-7, 2026) |
| 9 | docs/sprints/SPRINT_9_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 7-8, 2026) |
| 10 | docs/sprints/SPRINT_10_SUMMARY.md | [OK] Complete | ~1 day (Sep 9, 2026) |
| 11 | docs/sprints/SPRINT_11_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 9-10, 2026) |
| 12 | docs/sprints/SPRINT_12_SUMMARY.md | [OK] Complete | ~2.5 days (Sep 10-12, 2026) |
| 13 | docs/sprints/SPRINT_13_SUMMARY.md | [OK] Complete | ~1 day (Sep 12, 2026) |
| 14 | docs/sprints/SPRINT_14_SUMMARY.md | [OK] Complete | ~2 days (Sep 12-14, 2026) |
| 15 | docs/sprints/SPRINT_15_SUMMARY.md | [OK] Complete | ~1 day (Sep 16, 2026) |
| 16 | docs/sprints/SPRINT_16_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 16-17, 2026) |
| 17 | docs/sprints/SPRINT_17_SUMMARY.md | [OK] Complete | ~1 day (Sep 19, 2026) |
| 18 | docs/sprints/SPRINT_18_SUMMARY.md | [OK] Complete | ~2 days (Sep 22-23, 2026) |
| 19 | docs/sprints/SPRINT_19_SUMMARY.md | [OK] Complete | ~7 days (Sep 23-30, 2026) |
| 20 | docs/sprints/SPRINT_20_SUMMARY.md | [OK] Complete | ~4 days (Sep 30 - Oct 4, 2026) |

## Last Completed Sprint

**Sprint 20: Make the Suite Readable Again** (Sep 30 - Oct 4, 2026; PR #146 to
develop and PR #151 develop to main, both merged 2026-10-04).
Delivered **F97, F93, F98, F99**. 161 minutes against 171 estimated, zero
metered seconds, and the first sprint with a COMPLETE set of actuals. The
record is `docs/sprints/SPRINT_20_SUMMARY.md`, its retrospective and
`SPRINT_20_VALIDATION.md`.

**The suite is green in a planning window for the first time.** Six tests
asserted that Phase 3 artifacts exist while the repository sat in Phase 1,
before the plan that creates them had been written, so they failed for days at
a time. They now gate on the recorded phase, proven across nine sprint states
with the same code AND proven to still go red where an artifact is genuinely
owed.

**The close-out hook can no longer be silenced by a slow network.** Measured:
a Stop hook killed at its timeout produces no exit code, so it cannot block --
a timeout fails OPEN. The fail-open `gh` checks ran before the fail-closed CI
check, so one hanging call killed the hook before the guard ran. Reordered,
and the internal budget cut from 160s to 18s against a 20s allowance.

**The sent QCi correspondence has recorded hashes** in
`docs/QCI_CORRESPONDENCE_HASHES.md`, enforced by a guard that skips VISIBLY
where the gitignored artifacts are absent. The ignore rule did not change.

**a299ad2 is part of this sprint** (team lead, confirmed 2026-10-03): the
Phase 2 checklist merge, items 5 and 6 corrected against the filed proposal,
and F100-F121 registered.

### Sprint 19: Send the QCi Package Clean (Sep 23-30, 2026; PR #141 to
develop, PR #145 to main). Delivered **F92**. **The package was SENT 2026-09-25
at 12:23 PM** -- that was the objective. Task C was not approved and became
F96, since closed as overtaken; a fresh-context review found fourteen
cross-document disagreements, eight fixed. Zero metered seconds. The record is
`docs/sprints/SPRINT_19_SUMMARY.md`, `SPRINT_19_RETROSPECTIVE.md` and
`SPRINT_19_VALIDATION.md`; this section only points at them.

**THE FOUR PACKAGE DOCUMENTS ARE NOW FINAL** (team lead, 2026-09-27) and will
never change again. The memo is preserved as its `.htm` export with the
`_files` sidecar and as `Phase 1 - QCi memo AS SENT 2026-09-25.md`; its
thirteen wording guards were retired because the draft they read was deleted.
The guards on `QCI_EQC_MODELS_FEEDBACK.md` and `HARDWARE_PLAN_PHASE_2.md`
are KEPT: both sources are present and green, and on frozen text those guards
are the only thing that would notice an accidental edit.

**Known and permanent: the schedule-4 gap.** The memo commits to a ~60 s
schedule-4 check against the remaining 1,681 seconds; the attached hardware
plan does not mention it. Verified with `pypdf`: the sent PDF contains 1,681,
7,319, 7,500 and 9,000 and does not contain "schedule 4". Both documents are
final, so this is recorded rather than fixed.

Sprint 18: The First Phase 2 Evidence, and the Cost of the Ask (Sep 22-23,
2026; PR #139 to develop, PR #140 to main). Delivered **F87, F64, F88, F89**,
plus **F91** and a second integer probe round added mid-sprint. F2b deferred to
F90 before execution. The record is `docs/sprints/SPRINT_18_SUMMARY.md` and
`docs/sprints/SPRINT_18_RETROSPECTIVE.md`.

(Rolled 2026-09-23 in the Phase 8 sweep. This section had still described
Sprint 14 through four later sprints, because the Sprint 15, 16 and 17 sweeps
rolled `sprint_status.json` and not this heading. The Sprint 14 narrative that
stood here lives in SPRINT_14_SUMMARY.md.)

**What this document is, and is not** (team lead, 2026-09-15). The official
record of a sprint is five files: `SPRINT_n_PLAN.md`, the review/retrospective,
`SPRINT_n_SUMMARY.md`, `CHANGELOG.md` and `README.md`. This is a PLANNING
document. Its history section is convenience, not the audit trail, and it
REFERENCES those five rather than restating their numbers. Where a number does
appear here it needs to be right once, at backlog refinement, not continuously;
a stale PR number in a completion stub is not a defect worth a commit. Suite
counts are never restated anywhere: run the suite.

Why this is written down: a PR review asked for ten deleted completion stubs to
be restored as "the surviving audit trail". They were not. The summaries are.
Restoring them would have re-created ten copies of numbers owned elsewhere.

## Targeted roadmap (team lead, 2026-09-03; each sprint's scope is re-validated at its own refinement)

| Sprint | Dates | Targeted scope | Gate |
|---|---|---|---|
| 4 | Sep 3-5 | [DONE] F22, F21, F2 (per-block approval), F7 | -- |
| 5 | Sep 4 | [DONE] F8, F9, F27, F26, F28, F19 | -- |
| 6 | Sep 5 | [DONE] F31, F3 prep, F23, F24, F32 | -- |
| 7 | Sep 5-6 | [DONE] F33, F34, QCi/paper update | -- |
| 8 | Sep 6-7 | [DONE] **F3** (IEEE-CIS, all four tasks) + paper updates; F36 attempted and FAILED | -- |
| 9 | Sep 7-8 | [DONE] F4 (H6, measured null), F14, F16; **QCi package SENT** 2026-09-08 09:59 | -- |
| 10 | Sep 9 | [DONE] **F40** (segmentation) re-scoped to F40 only; gate-report undercount fixed (27/120 -> the true 37/163); 8 correctness findings from two adversarial reviews; 13 PR-review findings addressed | F37/F38 deferred to 11 |
| 11 | Sep 9-10 | [DONE] **F41** (A20, mechanism corrected), **F42** (+0.0319 decomposed: the gain is class weighting, not diversity), **F43**, **F44**, **F45**, **F35**, plus **F46** (A21, ceiling LIFTED) and **F47** added mid-sprint; 15 review findings addressed | F37 and the fresh-eyes review deferred to 12 |
| 12 | Sep 10-12 | [DONE] **F2b B2 and B3** on Dirac-3 (23 fits, 968 metered s), **F37**, **F38**, and **F49-F63** from three external reviews. F10 NOT reached | Evidence freeze held; F10 carries to Finalize |
| 13 | Sep 12 | [DONE] **F10**: evidence walk, requirements-matrix walk, confidentiality scan, final render, and the SUBMISSION -- filed 2026-09-12, three days early. F64 selected then withdrawn | **SUBMITTED**; 9 defects found and corrected |
| 14 | Sep 12-14 | [DONE] **F68-F72** plus **F48, F65, F66, F67**; two ADRs accepted for the Evidence Based DB. Two dead hooks found and fixed | **20 review findings**, all addressed; 2 vacuous guards caught by review |

**THE PHASE 1 ROADMAP IS COMPLETE (2026-09-12).** Every row above is [DONE] and
the submission is filed. The table described a run to a deadline; that deadline
has passed in our favor and the roadmap no longer describes any pending work.

What replaces it, recorded so the next refinement does not invent a schedule:
the judging window is **16 Sep to 14 Nov 2026**, with finalists announced
mid-November (Guidelines s2). Nothing we do changes the Phase 1 outcome, and no
backlog item is time-bound any more. The remaining items are tech debt, tooling,
and Phase 2 preparation, and they should be scheduled on value rather than
against a date.

The one exception is **F13, Phase 2 PoC sprint planning**, which becomes live
only on acceptance and is correctly held until then.

**Sprint 12 sequencing, DECIDED 2026-09-09 (Sprint 11 improvement 5) rather than under deadline pressure.** The order is forced by two dependencies, not by preference:

1. **Dirac-3 work first, if any is approved.** It produces new evidence, and evidence changes the documents. Run it in the evening window: measured queue wait is a 0.7s median after 19:00 local against the 52 minutes a 14:33 submission cost
2. **Then F38.** The page cut must run against FINAL content or it runs twice. This is why F38 has grown at every measurement
3. **Then F37.** Making the repository public is IRREVERSIBLE. Nothing that could still change a document should follow it
4. **Then F10**, the submission itself, which depends on all three

If the calendar forces a cut, drop the Dirac-3 work: it is the only one of the four that is not a submission blocker.

Renumbered 2026-09-05: the team lead noted the project is running more than one sprint per day, so F33 took Sprint 7 and F3 moved to Sprint 8 rather than competing for the same hours. A submittable paper exists after Sprint 5; every later sprint adds evidence and re-runs the review loop on the diff. The "still time" gate is a calendar lookup against the Sep 12 evidence freeze.

RESTORED 2026-09-06: this section was destroyed by a card-pruning script during the Sprint 7 close-out (commit c40038d) and again in the Sprint 8 sweep before the loss was noticed. Both scripts deleted from a shipped card's header until the next card header, and a `## ` section heading that fell inside that span went with it. The prune step now stops at any `## ` heading, and this recovery came from commit be1198c.

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

**NEW EVIDENCE 2026-09-11 (Sprint 12, F57/A31), recorded without deciding.** The
200:1 resolution finding bears directly on this question and points toward F25.
On all ten B2 pools the diagonal of J is 510,705 while off-diagonals span at most
20.0, against a resolvable difference of 2,554: nothing in the CONTINUOUS problem
is visible to the device. Quantised at that resolution the off-diagonal collapses
to one distinct value and the minimiser is uniform to 2e-15. The same limit
explains B2's 0.83 weight cosine -- a diffuse optimum over 833 learners averages
0.0012 per weight against a 0.005 resolution and is not representable.

That is an argument that the continuous formulation is the wrong ask of this
hardware, not that the optimizer has little leverage. A device that cannot spread
weight over ~200 learners has a native problem class, and it is
cardinality-constrained selection -- F25. It does NOT resolve the F33 reading
above, which is about where leverage sits rather than which formulation the
device can represent. Both are still open and the decision still waits for
Phase 2.

## Next Sprint Candidates

### Experiments (Stage 3 of the master timeline; submission-ready Sep 8)

(F1 classical evidence campaign and F18 Dirac-3 notes mining: COMPLETED in Sprint 3, merged via PR #13; history in SPRINT_3_SUMMARY.md. Removed from candidates per convention. F1 residual -- the section-6 CVQBoost proxy tuning -- continues as F22.)

(F22 CVQBoost proxy tuning and F2 hardware blocks B1+G0b: COMPLETED in Sprint 4, merged via PR #21; history in SPRINT_4_SUMMARY.md. F21 baseline research and F7 results memo likewise complete. Removed from candidates per convention. F2's remaining blocks B2/B3/B4/B5 continue as F2b below, gated on the QCi grant.)

(F68 freeze the submitted artifacts: COMPLETED in Sprint 14, merged via PR #94.
Both Edit-matcher hooks had never run; fixed, injection-proven, and guarded by
test_hook_registration.py. Removed from candidates per convention.)

(F69 README rebuilt for a public repository: COMPLETED in Sprint 14. Executing it
found an uninstallable lock file and a test that crashed where its peers skipped.
Removed from candidates per convention.)

(F70 CHANGELOG backfilled and wired into the close-out: COMPLETED in Sprint 14.
Workflow step 8.1.1 now runs before backlog refinement. Removed per convention.)

(F73 the submission explained at an 8th-grade level, and F74 its outline:
COMPLETED in Sprint 15. `docs/explainer/THE_SUBMISSION_EXPLAINED.md`, seven
sections, with the falsifier result recorded alongside it in
FALSIFIER_RESULT.md. See SPRINT_15_SUMMARY.md and CHANGELOG.md. Removed from
candidates per convention.)

(F87 the integer-solver sizing probe, F64 the k=17 order-2 ladder cell,
F91 the fourth ladder corner, F88 the false-finding mechanism and F89 the
injection helper: COMPLETED in Sprint 18. See SPRINT_18_SUMMARY.md and
CHANGELOG.md. Removed from candidates per convention.

Three findings outlived their cards and are recorded there:

- **B2's +0.0256 is attributed, not bounded.** F91 supplied the fourth corner:
  subset order carries the gain and feature count contributes nothing
  measurable. `docs/F64_LADDER_DECOMPOSITION.md` owns the figures.
- **Integer cost tracks VARIABLES, not the level budget**, from a controlled
  pair across five measured points. No high-variable point near the ceiling
  was run, so none is quoted. `docs/INTEGER_PROBE_RESULT.md` owns the figures.
- **Three metered calls were made against a two-call approval.** The runner
  had no idempotency check; it now has one, and Criterion H requires it before
  any metered runner's first approval.)

**F93. Reconcile the SPECTRA block: one card, one configuration, one cost -- CLOSED 2026-10-03 (decision made: F90 approved)**
- **CLOSED in the 2026-10-03 refinement.** The team lead approved F90 on 2026-10-03, which is the decision this card waited for; F2b's B4 line and F5 closed into F90 the same day. The card stays in place because `test_spectra_reconciliation.py` requires every SPECTRA record to remain findable and to point at the reconciliation
- **Sprint 20 delivered the reconciliation, not the decision.** All four
  records are now side by side in `docs/SPECTRA_BLOCK_RECONCILIATION.md` with
  their provenance, plus the tension the card did not know about: the sent
  hardware plan quotes 270 s while F90's configuration costs about 1,236 s,
  which is 4.6x the figure in the vendor's hands and 74% of the remaining
  balance. Four options are laid out. The choice is Class 3 and remains the
  team lead's
- Phase: Experiments / Phase 2 evidence (added 2026-09-23, Sprint 18 Phase 8 refinement)
- Platform: docs (SPECTRA, Dirac-3 planning only)
- **Four records describe the same SPECTRA block and disagree.** F2b quotes B4 at 15 fits and ~450 s; F90 at schedule 3, 833 variables, ~1,236 s; F5 (HOLD) at 3 cells x 5 seeds; and the hardware plan sent toward QCi sizes Experiment 5, segment transfer, at 30 fits of 91-136 variables, about 270 s. F90 alone would spend 74% of the 1,681 s balance, while the draft QCi memo tells QCi the balance goes to a schedule-4 check and Experiment 5 at "a few hundred seconds"
- This enables: any metered SPECTRA spend, and an honest F92. This prevents: spending 1,236 s on a block the vendor has been told costs 270 s
- Acceptance: the team lead picks one configuration (schedule 2 at 91-136 variables, or schedule 3 at 833) with the reason recorded; F2b and F5 closed into the survivor; the survivor's cost labeled measured or extrapolated; the hardware plan's Experiment 5 row either matches it or is flagged for F92
- Depends on: nothing. The configuration choice is the team lead's (Class 3)

**F94. Experiment 3 classical controls on the proxy: greedy, simulated annealing, exact solve at small n (~4h, zero metered) Priority 50**
- Phase: Phase 2 preparation, Experiment 3 (added 2026-09-23, SPLIT from F25; **taken off the preregistration gate 2026-10-02**; re-scored 8 to 50 in the 2026-10-03 refinement, behind the cards that make F90 readable and the preregistration framework). Sprints with F104
- Platform: classical proxy (`qubo_proxy.py`, `integer_path.py`)
- The hardware plan promises QCi that Experiment 3's controls are "stated before the block runs": a time-capped MIQP solve, greedy selection and simulated annealing. **Verified absent 2026-10-02**: no greedy, annealing or MIQP code exists anywhere in `experiments/src/`
- **BUILD NOW, DO NOT WAIT FOR THE PREREGISTRATION** (team lead, 2026-10-02: acceptance into Phase 2 is expected). The card previously deferred all work behind a Phase 2 preregistration that does not exist yet. That was over-cautious, because BUILDING a control and REPORTING a comparison are different acts. The build is reusable whatever the preregistration says, and having it ready is what lets Experiment 3 run the day an allocation arrives
- **What reporting still waits for**: any claim comparing device to control. The controls produce dated post-submission rows and touch no Phase 1 claim. If Phase 2 acceptance does not arrive, the work is a classical result on our own pools and is reported as exactly that
- **What already exists and is reusable, measured in Sprints 18-19**: `integer_path.py` builds and validates the cardinality-constrained integer job (`num_levels = upper_bound + 1` per variable, device budget `sum(upper_bound + 1)` against the 949 ceiling); `qubo_proxy.py` solves the identical Hamiltonian (`J = HH^T + lambda*I`, `C = -2Hy`, sum constraint 1.0, `w >= 0`); and the two measured sizes are 60 and 150 variables, at 71 s and 165 s of device time
- **Solver availability, now verified rather than unverified**: of `mip`, `pulp`, `cvxpy` and `gurobipy`, NONE is installed; only `scipy.optimize` is present. The commercial MIQP leg therefore needs a dependency decision, and `requirements.txt` plus `test_requirements_complete.py` must be updated with whatever is chosen. Exact enumeration needs no new dependency and is the honest floor
- Suggested order: exact enumeration at small n first, because it yields a certified optimum to measure the others against; then greedy; then simulated annealing; then the MIQP leg if a solver can be justified
- This enables: Experiment 3 running the day allocation arrives, with its comparison already fixed. This prevents: a device result reported against no control, which the hardware plan itself tells QCi is not a result
- Acceptance: each control returns a cardinality-feasible selection and objective value at both 60 and 150 variables with seeds recorded; the exact solve agrees with a brute-force check at a size where both run; results written as dated post-submission rows; no Phase 1 claim touched; any new dependency declared and covered by the requirements guard
- Depends on: nothing. Reporting a device-versus-control COMPARISON waits for a Phase 2 preregistration; the build does not
**F95. Relaxation schedule 4 on the residual (~1h build + approval, metered, cost unmeasured) Priority 160**
- **UNBLOCKED 2026-09-25**: the hold was "until the QCi memo is sent", and it
  was sent 2026-09-25 at 12:23 PM. The sent memo commits to this check, so it
  is now promised work rather than optional
- Phase: Experiments (added 2026-09-23; promised in the QCi memo and carded nowhere)
- Platform: Dirac-3
- The feedback document's open question 1, "Would relaxation schedule 4 close the residual?", is still open: every Phase 1 fit ran schedule 2, frozen before the grant. The memo names it as a use of the remaining balance
- **Four fits at 45-91 variables**, enumerated in the HELD note below. Schedule-2 cost there is 4-9 s per fit, measured; **schedule-4 cost is unmeasured**, so the block opens with one fit to establish the rate (the F87 pattern). (Corrected 2026-09-27: this bullet said "about five fits at 91-136 variables" while the note below enumerated four, one of them at 45 variables. IMP-4 directs future readers to trust this card's numbers rather than re-derive them, so a card contradicting itself undercuts the rule that cites it. Found by both PR #141 reviews.)
- Acceptance: the runner is idempotent before its first approval (Criterion H); per-fit residual against the proxy optimum reported as `[HW]` rows beside their schedule-2 twins
- Depends on: per-block team-lead approval (Criterion H)
- **HELD until the QCi memo (F92) is sent** (team lead, 2026-09-23). Case and cost worked out at refinement, recorded so it is not re-derived: 4 fits on frozen pools that already have schedule-2 and exact-optimum twins (B1 dct seeds 42 and 43 at 91 variables; the G0b fit with the 0.413% gap; B1 lg seed 42 at 45 variables), stopping after fit 1 to re-quote if the rate exceeds 27 s. About 60 s, range 40-110 s, cap 120 s. Extrapolated, low confidence: measured schedule-2 cost of 4-5 s per fit times the 3.4x schedule-4 ratio (range 2.3x-5.3x) in QCi's portfolio example, a problem of unstated size. The per-fit data suggests the residual is a fixed offset (all 8 samples clustered well above the optimum), which predicts schedule 4 will NOT close it; that is inference, and the run is what settles it

**F90. F2b at the configuration that can actually show an effect: B5, then B4 at schedule 3 (~4h + approvals) Priority 10**
- Phase: Experiments / Phase 2 evidence. **This is the replication half of Experiment 5, Segment transfer (H5)** (proposal section 5; the 2026-10-03 checklist correction). A failure of H5 is the third condition the proposal names as retiring the approach. The transfer half is F121. Sprints with F100 and F101, which make its result readable
- Platform: SPECTRA, Dirac-3
**The four records are reconciled in `docs/SPECTRA_BLOCK_RECONCILIATION.md` (F93, 2026-10-02), which also records that QCi was SENT 30 fits at 91-136 variables for 270 s. The configuration choice is open and is the team lead's.**
- **SUPERSEDES F2b's sizing.** F2b quotes B4 at "15 fits, ~450 s" from the original grid. That grid was proven wrong by 2.3x at 833 variables in Sprint 12 (assumed ~40 s, cost 91 s), and the schedule choice underneath it was never stated. This card carries the measured figure and names the configuration.
- **APPROVED 2026-10-03 and scheduled for the next sprint** (team lead): he ran SPECTRA on another computer and Dirac-3 won in almost all cases, and directs the analysis matching prior Dirac-3 quantum-enhanced datasets to run next. That result is `[UNVERIFIED -- OFF-REPOSITORY]` here until its configuration, fits, seeds and arm are brought in, which is the next sprint's first task. F2b's B4 line and F5 close into this card. See `docs/SPECTRA_BLOCK_RECONCILIATION.md`
- **THE TUNED CONFIGURATION IS WHAT WINS, AND IT IS NOT THE ONE OUR LOSS FIGURE DESCRIBES.** Consulted for planning only (a prior-campaign findings document the team lead holds outside this repository; nothing copied in, not cited as evidence): the in-segment wins come from schedule 3 with 8 samples, relaxation schedule 2, and a ridge of about 2x the record count, which our own `qubo_proxy.py` already uses (`LAMBDA_MULT = 2.0`). Relaxation schedule 4 cost about 3.8x more per sample for no measurable accuracy gain, and shallower weak learners hurt badly -- so the Sprint 18 instinct to leave schedule at 2 was right for the RELAXATION schedule and wrong only if confused with the WEAK-CLASSIFIER schedule. Two different knobs, similar names
- **CAVEAT TO CARRY, now in the acceptance criterion below**: those in-segment wins came with a train-to-test gap well above XGBoost's on the `target` cells, one case dropping from 0.98 train to 0.59 test. The wins are real and fragile. Any Phase 2 claim from this block must report the train-test gap beside the win. (Corrected 2026-10-03: this bullet said "three to eight times XGBoost's on every `target` cell", copying the summary line of the off-repository findings document. That document's own table gives ratios of 83, 7.6, 8.2 and 1.7, so the summary is wrong at both ends. The ratios come from the 2026-09-30 EvidenceBasedDB check of that document; they are not evidence in this repository)
- **THE ACCURACY FIGURES BELOW ARE PROXY, NOT DEVICE.** Checked 2026-10-03: `experiments/results/spectra_proxy_dry_run.json` holds 15 rows, 13 of 13 scored in-segment cells with a NEGATIVE edge at 560 and 816 variables, and the preregistration names the origin at line 46 (FourierWall2, 2026-08-04). They are sourced -- but every row is `evidence_tag: PROJ`, `metered_seconds: 0`. **This repository has never run SPECTRA on Dirac-3.** So "schedule 2 lost 8 of 8" means the PROXY lost in-segment, and says nothing about the device. The team lead's 2026-10-03 device run does not contradict it; it tests the arm we never tested. The COST anchor in the next bullet is measured and stands
- **B4 runs at schedule 3.** In the prior SPECTRA work, schedule 2 reportedly lost overall 8 of 8 to the classical arm with only ~3 in-segment metrics won; schedule 3 -- which adds three-feature interactions -- took CVQBoost to in-segment ROC 5 of 7 and PR 6 of 7, and to an overall win on energy_steel. Schedule 3 is the accuracy lever. **A schedule-2 block would spend real seconds reproducing a configuration already known to lose, which is not a cheap experiment but a worthless one.**
- **COST, measured rather than projected.** The schedule-3 QUBO is `n + C(n,2) + C(n,3)`. For energy_steel (17 features) that is **exactly 833 variables -- our B2 size** -- so B2's measured 82.4 s/fit is a DIRECT ANCHOR, not an extrapolation:
  - **B4: 15 fits x 82.4 s = about 1,236 s, which is 74% of the 1,681 remaining** (was 63% of 1,961 before the Sprint 18 integer probes spent 280 s). Provenance: `measured` at this exact variable count.
  - **B5 (QSVM, 12 fits): 15-62 s.** Provenance: `extrapolated` from B3's 5.2 s/fit.
  - Run B5 FIRST. It is cheap and it exercises the approval and ledger path before the expensive block.
- **THE A31 READING THAT MUST NOT BE REPEATED.** The Sprint 18 plan first argued that A31's ~200-learner resolution limit made schedule 3 a worse experiment. That is backwards. A31 predicts the MECHANISM -- weight over more than ~200 learners is not representable, so the device returns something sparser -- not a bad OUTCOME. B2 ran at 833 variables with weight cosine 0.83 and produced the campaign's ONLY positive result at scale, +0.0256 on ten of ten seeds. The sparsified answer was better. Whether that repeats on SPECTRA is the actual experiment.
- **Sizing note for any later cell**: telecom_churn at schedule 3 is 987 variables, over the ~940 usable ceiling. It needs one feature dropped (18 -> 17 gives 833) or it cannot run at all. energy_steel (833), oilgas (575) and maintenance (298) fit.
- **Reconcile with F5 BEFORE B4 runs.** F5 (SPECTRA in-segment replication) is the same block from another angle and they must not both be scheduled. F5's HOLD reason names a QCi grant that "has only been acknowledged, not granted"; the grant arrived 2026-09-09 and 1,681 s remain. That gate was stale and is corrected on the F5 card (Phase 8 sweep, 2026-09-23).
- **Acceptance**: B5 and B4 complete as `[HW]` rows with metered seconds from the response; the in-segment result reported against the matched random-segment control per H5(ii); the schedule-3 configuration stated with its variable count; and the weight cosine recorded, since forced sparsity is the expected mechanism rather than a defect.
- **Acceptance, added 2026-10-03**: (a) the F100 complete classical bar reported on the same rows; (b) repeats reported as mean and standard deviation, not single runs; (c) every returned sample stored, not only the lowest-energy one, so F20's multi-sample ensembling costs no further device time; (d) the train-test gap beside every win
- **Cost against the sent figure**: 15 fits at 833 variables is about 4.6x the 270 s the sent hardware plan states for Experiment 5 (`docs/SPECTRA_BLOCK_RECONCILIATION.md`). After F90, about 445 s of the 1,681 remain, which does not cover Experiment 3; Experiment 3 depends on the additional 7,500 s asked of QCi
- **This is an allocation DECISION, not an estimate.** 1,236 s of 1,681 leaves about 445 s for everything else. It stops for per-block approval with the figure quoted (Criterion H).
- Depends on: reconciliation with F5; per-block team-lead approval

**F2b. Hardware campaign, remaining blocks B4 and B5 -- CLOSED 2026-10-03 into F90**
- **CLOSED in the 2026-10-03 refinement.** B4's line closed into F90 earlier the same day, and F90's title is "B5, then B4", so the B5 line here duplicated it. Nothing is lost: B5 runs first inside F90. The card stays in place because `test_spectra_reconciliation.py` requires every SPECTRA record to remain findable
- Phase: Experiments
- Platform: Dirac-3
- **B1 + G0b DONE** (Sprint 4, 120 QPU s). **B2 DONE** (Sprint 12, 11 fits, 906 s, A24). **B3 DONE** (Sprint 12, 12 fits, 62 s, A23 after the A22 withdrawal and matched re-run). Only B4 and B5 remain
- **B4's line here is CLOSED into F90 (2026-10-03).** Its "15 fits, ~450 s" was from the original grid, with the schedule never recorded, so the figure could not be repaired -- there is no way to tell what it was costing. F90 carries the measured cost. **B5** (QSVM sign-augmented, 12 fits, ~15 s) remains here and is cheap enough to run inside any remaining balance
- B4 overlaps **F5** (SPECTRA in-segment replication), which sits in HOLD. They are the same block from two angles and should be reconciled before either is scheduled
  **The four records are reconciled in `docs/SPECTRA_BLOCK_RECONCILIATION.md` (F93, 2026-10-02), which also records that QCi was SENT 30 fits at 91-136 variables for 270 s. The configuration choice is open and is the team lead's.**
- Neither is a submission blocker. Both are post-submission work on the current calendar
- Depends on: per-block team-lead approval (Criterion H); allocation balance
- **The billing rule is now validated far outside its anchors.** B2's first fit at 833 variables, degree 3 cost 91 metered seconds where the grid assumed ~40. `ceil(sum(runtime))` predicted it exactly (runtime sum 90.152 s, balance 2929 -> 2838). Per-sample cost 11.27 s against B3's ~0.6 s, an **18.8x** step. Use measured per-sample cost, not the original grid, for any B4 estimate


(F65 per-fit artifact write: COMPLETED in Sprint 14. Also fixed a dry run that
overwrote committed evidence. Removed from candidates per convention.)

(F77 build the Evidence Based DB, F75 the 20-paper ADR checkpoint, and F76 the
shared-vocabulary guard: MOVED to the `kimmeyh/EvidenceBasedDB` repository
2026-09-16 by the team lead. All three are that repository's work, not this
one's. F77 builds its store; F75 reviews its schema against its own papers; F76
guards ITS ADR-0004 and ADR-0005, whose live copies live there. The copies here
are frozen and carry a banner saying so. Tracked in that repository's own
backlog. Removed from candidates per convention.)

(F78 the PowerShell-to-Python conversion, F79 the retrospective gate, and F80
the open-question falsifier re-run: COMPLETED in Sprint 16. See
SPRINT_16_SUMMARY.md and CHANGELOG.md. Two findings outlived their cards and are
recorded there: F79's defect was an exemption never revoked rather than a
missing check, and the confidentiality scan reported clean on any single-line
file. Removed from candidates per convention.)

(F82 the escape-eaten class, F83 the venv parity question, F84 the environment
in the row schema, F85 the gate-report rename and F86 the QCi post-submission
package: COMPLETED in Sprint 17. F81 CLOSED by the team lead. See
SPRINT_17_SUMMARY.md and CHANGELOG.md. Removed from candidates per convention.

Four findings outlived their cards and are recorded there rather than here:

- **F83's Appendix C question resolved in the document's favor.** "Python
  3.12, Linux" is accurate AND enforced in code -- run_hardware.py and
  tune_proxy.py hard-exit on any non-POSIX platform, because the full-pair pool
  build needs fork. No submitted document needed correcting. The suite is now
  identical on both platforms; the count is not restated here, per
  `docs/VENV_PARITY.md`, which owns that evidence. Run the suite.
- **The cross-repository guard had never run in CI.** 15 of its 17 cases
  skipped on non-Windows for a PowerShell reason that stopped applying when
  F78 converted the hooks. CI is ubuntu-latest, so the boundary rule was
  enforced on one workstation and nowhere else.
- **render_all.py rebuilt the three SUBMITTED PDFs on any invocation**, and the
  first fix's override flag was used within minutes to get an unrelated test
  running. No override exists now.
- **The QPU arithmetic does not subtract**, and the reconciliation is at
  docs/QPU_RECONCILIATION.md so it is not re-derived a fourth time.)

**F36. Pandoc Lua filter: floating tables for the submission PDFs -- CLOSED 2026-09-07, FAILED**
- **VERDICT: the filter works; the problem it was built for did not exist.** The premise (preserved in the review doc, because it is wrong in an instructive way) rested on a CHARACTER-COUNT page-fill measurement, and a table-heavy page always looks short by that measure. Measured as vertical extent, every page cited below was already full: 724 / 680 / 680 / 682pt of a 792pt page, zero free space anywhere. The appendix was over its limit because it had too much content
- **Failed criterion 1** (appendix 3 pages with the filter, 4 without): 4 and 4. **Failed criterion 6** (other documents unchanged), which is worse: floating tables in a table-dense document COSTS a page, taking gate_report.pdf from 3 to 4. Criteria 2, 3, 4, 5 and 7 pass
- Filter RETAINED but UNREGISTERED at `scripts/pandoc/float-tables.lua`, opt-in through `render-pdf.ps1 -LuaFilter`, which nothing passes. `render-all.ps1` is unchanged. Do not enable it without reading `docs/reviews/f36-float-tables-outcome.md`
- **What the card actually produced, and it is worth more than the filter**: `scripts/page-fill-report.py` now measures vertical extent in points instead of counting characters, and excludes the page-number folio, which sat at the same depth on every page and so made every page report zero free space -- including a nearly empty last page, the one case the tool exists to flag. `experiments/src/test_page_fill_report.py` covers both defects and all four tests fail against the previous implementation
- **The appendix DID reach 3 pages**, by the team lead's two suggestions: set pipe-table column widths from the longest cell each column holds (every table used `|---|---|`, giving "30" and "[SIM]" the same width as a sentence; removed 9 of 20 spilled lines with no content change), and move reference material to the public repository. It has since gone back to 4 with the B.1 compound-falsification statement, tracked as F38
- **Process lesson**: the card's dry run could not have failed. Deleting five tables removes their content AND their space, so the document was always going to shrink. It never distinguished "tables take room" from "tables waste room". A check that cannot fail is not evidence

The original card body is pruned as shipped. Its premise, the seven
acceptance criteria and the full failure analysis are preserved in
docs/reviews/f36-float-tables-outcome.md.

(F38 appendix to 3 pages AND proposal to 6: COMPLETED in Sprint 12, merged via PR #75.
proposal 6 of 6, appendix 3 of 3, team profile 1 of 1. Removed from candidates per convention.)

(F39 Evidence Based Database investigation and design: COMPLETED in Sprint 14 as
ADR-0014, ACCEPTED with early-innovation status and a 20-paper checkpoint.
Building is a SEPARATE card and is not authorised by the ADR. Removed per
convention; F75 actions the checkpoint.)

### Phase 2 (pre-notification preparation and the committed experiments)

Added in the 2026-10-03 refinement, which merged `CHECKLIST-Phase2-pre.md` into
`CHECKLIST-Phase2.md` and carded every Phase 2 item that had no card. Source:
the team lead's Phase 2 planning documents (held outside this repository;
consulted for planning, not cited as evidence). Priority order follows the
team lead's 2026-10-03 decision that field advancement leads if it conflicts
with the track outcome: F90 and the cards that make it readable first, then the
preregistration framework that gates all reporting, then the zero-cost screens,
then the builds for the committed experiments. Estimates are `[no-history]`.

**F100. Complete classical bar on identical SPECTRA features (~6h [no-history], zero metered) Priority 12**
- Phase: Phase 2 evidence, Experiment 5 (sprints with F90)
- Platform: SPECTRA
- LogReg, GAM, GA2M, HGB and an order-matched JOINT twin, each given the SAME SPECTRA phase features as CVQBoost, on the same splits and seeds; paired bootstrap CI on the metric difference; repeated splits
- This enables: reading F90's result. The Fourier Wall paper (arXiv:2607.15815) shows a fake quantum win without JOINT (0.758 against 0.721) that a JOINT twin reads classically at 0.968. This prevents: reporting a feature-engineering gain as a quantum gain
- Three outcomes, all reportable: the gain survives the complete bar; the gain vanishes against JOINT; or every lane gains from the phase features, so the feature engineering is the contribution
- Acceptance: all five classical lanes and CVQBoost per dataset with paired CIs; the outcome named as one of the three
- Depends on: F90's first task (the off-repository data and configuration brought in)

**F101. `in_pocket` provenance diagnostic (~1h [no-history], zero metered) Priority 14**
- Phase: Phase 2 evidence, Experiment 5 (sprints with F90)
- Platform: SPECTRA
- One model fit: is `in_pocket` predictable from the SPECTRA phase features, or only from raw covariates? Route-and-blend requires the router's gate to be independent of the specialist's features; a dependent gate re-correlates the pocket
- Acceptance: AUC of each predictor recorded with a one-line reading
- Depends on: F90's first task. The SPECTRA author's construction details settle it without inference if they arrive (team lead to ask)

**F102. Phase 2 preregistration framework (~3h [no-history], zero metered) Priority 30**
- Phase: Phase 2 preparation (the checklist's Deliverable)
- Platform: docs
- A per-experiment preregistration template and one reporting standard for every Phase 2 result: nested CV, Wilcoxon signed-rank, Bonferroni correction and multi-seed sensitivity (arXiv:2604.18837); AUPRC normalized by its closed-form floor with AUROC beside it; the F104 resolution screen as a gate before any metered block; and the two meanings of "order 3" stated (weak learners over feature triples in pool construction, against a QUBO that is quadratic on the device)
- This enables: every Phase 2 card below reporting honestly. This prevents: results seen before the protocol is fixed
- Acceptance: the template committed; each later experiment card names its preregistration file before it runs. `experiments/PREREGISTRATION.md` stays FROZEN; this is a new document
- Depends on: nothing

**F112. Experiment 1 interval on the k=17 decomposition (~1h [no-history], zero metered) Priority 32**
- Phase: Phase 2, Experiment 1
- Platform: ULB proxy
- F64 and F91 measured the ladder; `docs/F64_LADDER_DECOMPOSITION.md` owns the figures. Remaining: the paired bootstrap interval reported as the Phase 2 result under F102. Diff `Proxy cell used:` before publishing, because a new full-pair cell can re-key the H1b confirmatory table through `score_gates.py`'s argmax
- Depends on: F102

**F103. SPECTRA Tier 1 known-answer check on UCI Steel Industry Energy (~4h [no-history], zero metered) Priority 40**
- Phase: Phase 2 preparation (cross-domain study, step 1)
- Platform: SPECTRA
- Run Tier 1 on the Fourier Wall paper's own dataset and reproduce its published gate values before the screen is trusted anywhere else
- Acceptance: all five gate values within a stated tolerance of the paper's; if not, the cause is recorded and F109 stays blocked
- Depends on: nothing. The SPECTRA author's construction details help

**F104. Pre-run 200:1 resolution screen (~1h [no-history], zero metered) Priority 52**
- Phase: Phase 2 preparation, Experiment 3 (sprints with F94)
- Platform: Dirac-3 planning
- Before any metered call, test whether the job's coefficient range exceeds the device's 23 dB (200:1) resolution. It would have predicted B2: diagonal 510,705, off-diagonals at most 20.0, resolvable step 2,554 (Sprint 12, A31)
- Acceptance: flags the frozen B2 pools; passes a pool built to be resolvable; proven red
- Depends on: nothing

**F105. Experiment 2 build: IEEE-CIS rolling-origin folds and the classical gap (~6h [no-history], zero metered) Priority 60**
- Phase: Phase 2 preparation, Experiment 2
- Platform: IEEE-CIS
- Rolling-origin folds; entity reconstruction `card1_addr1_(day - D1)` used ONLY to compute group aggregations, never as a feature; client-mean post-processing; time-consistency feature selection; adversarial validation; a temporal-leakage audit of any graph features
- This enables: Experiment 2 and a credible classical bar for every other comparison. Published headroom on IEEE-CIS is about 5-6 AUC points (naive XGBoost 0.88-0.90 against the 0.9459 winning private score)
- Acceptance: the harness builds and is tested; no score is reported until F102 names its preregistration
- Depends on: F102 for reporting; nothing for the build

**F106. G3 dequantization check: random-Fourier-feature surrogate and JOINT twin (~3h [no-history], zero metered) Priority 72**
- Phase: Phase 2 preparation, gate-based arm (sprints with F107)
- Platform: Braket simulator, classical
- If an RFF surrogate or an order-matched JOINT twin matches the circuit's accuracy on identical features, the circuit is dequantized and hardware would measure nothing. Stop and report that
- Depends on: F6 recommends pursue

**F107. G1 Schmidt-rank threshold on the SV1 simulator (~4h [no-history], zero metered) Priority 74**
- Phase: Phase 2 preparation, gate-based arm (sprints with F106)
- Platform: Braket simulator
- Prediction error against (effective Schmidt rank, shot count) for our feature count, with the critical rank at each shot budget. Predicts the gate-based outcome before any hardware spend
- Depends on: F6 recommends pursue

**F108. Ceiling validation harness with hidden state (~6h [no-history], zero metered) Priority 80**
- Phase: Phase 2 preparation (ceiling methodology)
- Platform: Fraud Detection Handbook simulator
- Withhold compromised-terminal and targeted-customer state to induce a known, nonzero Bayes error; add FeeBee-style label-noise injection at known rates. A ceiling method that does not recover the known ceiling is not used on real data
- This enables: F114. This prevents: an unvalidated ceiling estimate on extreme-imbalance data, where published Bayes-error estimators are validated only on balanced classes with few features
- Depends on: nothing

**F109. SPECTRA domain ladder and aggregation experiments (~6h [no-history], zero metered) Priority 90**
- Phase: Phase 2 preparation (cross-domain study, steps 2-3)
- Platform: SPECTRA, IEEE-CIS, ULB
- Tier 1 on the seven-dataset ladder with all five gate values recorded; the phase pipeline on classical models alone; gates before and after aggregation, including the IEEE-CIS UID aggregation
- Depends on: F103

**F110. Experiment 6 scaling claim: end-to-end training time against sample count (~3h [no-history]) Priority 110**
- Phase: Phase 2 preparation, Experiment 6
- Platform: classical proxy first; Dirac-3 only under F102 and per-block approval
- Time including Hamiltonian construction. `HARDWARE_PLAN_PHASE_2.md` owns the sent sizing (12 fits at 833 variables) and the pool-build-to-device-time ratio
- Depends on: F102 for reporting; Criterion H for any metered fit

**F111. Experiment 4 build: Loke et al. replication harness (~4h [no-history], zero metered) Priority 120**
- Phase: Phase 2 preparation, Experiment 4
- Platform: ULB
- Their split and comparator, target AUC-PR 0.80, then re-evaluated under ours
- Depends on: F102 for reporting

**F113. Oracle-gap complementarity test, CVQBoost against XGBoost (~3h [no-history], zero metered) Priority 130**
- Phase: Phase 2 preparation (bounds the router, F121)
- Platform: ULB
- Matched operating point, rank correlation of the two score vectors, and the oracle gap (best per-transaction choice using true labels). If the oracle barely beats the best single model, no router can help
- Depends on: nothing

**F114. Ceiling estimates on real data: learning-curve floor and label noise (~6h [no-history], zero metered) Priority 140**
- Phase: Phase 2 preparation (ceiling methodology)
- Platform: ULB, IEEE-CIS
- Fit `a*N^(-b) + c` against N_positives within a fixed time window; confident learning with the diagonal-dominance condition tested and reported when it fails. Report intervals, not points
- Depends on: F108

**F115. Integer cost scaling stated correctly in a new document (~30m, zero metered) Priority 170**
- Phase: QCi/External
- Platform: docs
- `HARDWARE_PLAN_PHASE_2.md` says cost is "superlinear in variables". Its own two-factor fit, `vars^0.75 x levels^0.52`, is sublinear in variables; it is superlinear only when levels grow with variables (exponent sum 1.27). The document is FINAL (team lead, 2026-09-27), so the correction goes in a new document, per the F92 consequence above
- Depends on: nothing

### Paper (Stages 4-6)

### Finalize (Stages 7-8)

(F35 interpretation-layer tests, F41 mechanism correction (A20), F42 review findings, F43 IEEE-CIS AUC-ROC, F44 figure resolution, F45 evidence guard, F46 QCi grant and ceiling probe (A21), F47 metered-call wrapper: ALL COMPLETED in Sprint 11, merged via PR #66 (main PR #70); history in SPRINT_11_SUMMARY.md. Removed from candidates per convention.)

(F66 Copilot reviewer-request procedure: COMPLETED in Sprint 14, and CORRECTED
again during it: the working call is GraphQL requestReviews with botIds, not
userIds, and REST returns HTTP 200 while attaching nothing. Removed per convention.)

(F48 shell-metacharacter hook: COMPLETED in Sprint 14 after three iterations, each
correction driven by a false positive against a real command. Removed from
candidates per convention.)

(F71 CHECKLIST restructure and F72 reference-paper library: COMPLETED in Sprint 14.
See SPRINT_14_SUMMARY.md and CHANGELOG.md. F72's design is ADR-0015, whose live copy
moved to EvidenceBasedDB; its build is F77. Removed from candidates per convention.)

### External (team-lead-owned, parallel)

(F11 QCi sponsorship letter send: COMPLETED by the team lead 2026-08-30. F12 portal verification and F15 best-practices/ADR review: COMPLETED in Sprint 2, merged via PR #2; history in SPRINT_2_SUMMARY.md. All three removed from candidates per convention.)

(F4 H6 representation arm, F14 eqc-models feedback package, and F16 minimal CI: COMPLETED in Sprint 9, merged via PR #53 (main PR #54); history in SPRINT_9_SUMMARY.md. All three removed from candidates per convention.)

### HOLD Items (post-submission)

**THE HOLD CONDITION EXPIRED 2026-09-12 when the submission was filed.** Every
item below was held for one reason -- it must not compete with the submission --
and that reason is gone. They are NOT automatically live: "no longer blocked" is
not "selected", and the team lead sets priority. But they should be read as
candidates at the next refinement rather than skipped as held. (F39 was on this list and is
now done: ADR-0014 was accepted in Sprint 14 and its build is F77.)

Flagged rather than re-prioritized: re-scoring nine cards is a scope decision,
not a sweep correction.


**F5. SPECTRA in-segment replication, block B4 -- CLOSED into F90 (2026-10-03)**
- **CLOSED.** F93's reconciliation established that F5, F2b's B4 line and F90 are the same block from three angles. The team lead approved the block on 2026-10-03 and F90 is the surviving card. Nothing here is lost: F5's angle was in-segment replication at 3 cells x 5 seeds, which F90's card now carries as a sizing input rather than a separate item
- Phase: Experiments (moved to HOLD by team lead 2026-09-08 at Sprint 10 refinement)
- Platform: SPECTRA, Dirac-3
- 3 strongest cells x 5 seeds; random-segment negative control machinery reused for fraud transfer
- **Why HOLD**: originally, the QCi grant, then only acknowledged. **That reason is stale**: the grant arrived 2026-09-09 and 1,681 s remain. The live reason is that F90 is the same block from another angle and must be reconciled with it before either is scheduled (corrected in the Phase 8 sweep, 2026-09-23)
  **The four records are reconciled in `docs/SPECTRA_BLOCK_RECONCILIATION.md` (F93, 2026-10-02), which also records that QCi was SENT 30 fits at 91-136 variables for 270 s. The configuration choice is open and is the team lead's.**
- Depends on: QCi grant; F2 approval pattern

**F29. Sample-size insensitivity of the CVQBoost optimum (~1h measured, zero metered) Priority HOLD**
- Phase: Experiments (moved to HOLD by team lead 2026-09-08 at Sprint 10 refinement)
- Platform: ULB proxy
- **Effort re-measured 2026-09-08, and the old ~2h was wrong in the cheap direction**: pool build scales O(n^1.4) -- 8.8s at 50k rows, 25.9s at 100k, 82.2s at 250k. The ULB train fold is 170,236 rows after dedup and the 60/20/20 split, so the full 3-seed x 4-size grid is 8-10 minutes of build plus solve and scoring. It could have run in parallel with anything
- **Why HOLD anyway, and this is the deciding reason**: it scores against no rubric criterion. The weights are Problem Relevance & Impact 25%, Technical Approach & Innovation 25%, Feasibility 20%, Validation Plan 15%, Team Capability 10%, Hybrid 5%. A stability property of our own optimizer is not a fraud-detection result, a validation-protocol improvement, or a hybrid-integration argument
- **The proposal already makes the production-cost argument better** (section, line 94): CVQBoost's published claim is a runtime advantage from 1M to 70M samples, our null sits at 284k rows, and the untested question is end-to-end training time against sample count whose Hamiltonian construction grows with the square of the pool size. That is sharper than "the optimum is insensitive to sample size"
- **Three further costs**: it needs a dated amendment (A20) four days from the evidence freeze; the card's own honesty constraint requires connecting it to the near-degeneracy finding, which a reviewer reads as the same finding restated; and it needs page space in two documents that are currently OVER limit, working against F38
- Post-submission value is real; the Phase 2 plan can name it as a follow-up at zero cost
- Related to F110 (Experiment 6) but not the same question: F110 measures training TIME against sample count; this card measures whether the OPTIMUM moves (2026-10-03)
- Depends on: nothing (reuses qubo_proxy build/solve)

**F17. Dirac-3 simulator for pre-hardware test runs (~2-3h investigation, then build TBD; zero metered) Priority 100**
- Phase: Phase 2 preparation, Experiment 3 (**OFF HOLD 2026-10-02**, team lead: "lots of time between now and February 2027 to explore"; re-scored 14 to 100 in the 2026-10-03 refinement)
- Platform: Dirac-3 / local
- **Why this is worth more now than when it was held.** The hold reasoned that ADR-0002's proxy plus the G0b fidelity gate already filled the role. Two Sprint 18-19 findings changed that. The proxy solves the CONTINUOUS relaxation, which is convex and so has nothing a device can win, while Phase 2's Experiment 3 is the INTEGER cardinality problem where the proxy is no longer an equivalent. And we now know, from measurement, what makes the device diverge from the exact optimum
- **What the device model would encode, from our own measurements rather than the vendor figure alone**: the 200:1 (23 dB) analog resolution, against which our pools' off-diagonal coefficients differ by at most 20.0 where 2,553.5 is resolvable, so quantization collapses them to a single value; the sum constraint at 1.0, under which a diffuse optimum over 833 learners averages 0.0012 per weight against a representable step near 0.005, forcing sparsity; `num_samples` stochasticity; and that cost tracks the VARIABLE COUNT rather than the level budget (the controlled pair: 1.4x more levels, 2.3x less cost)
- **The point is to predict the SPARSIFICATION, not the objective value.** A simulator that returns the exact optimum tells us nothing the proxy does not already give free. One that reproduces "weights below the resolvable step are zeroed, and the answer returned is sparser than the one asked for" would let us size Experiment 3's cells before spending metered seconds
- **A falsifiable acceptance test already exists, which the original card lacked**: eleven B2 fits at 833 variables, each containing exact zeros with nonzero weights from 0.0007 to 0.0029, all below the resolution, at weight cosine 0.83. The simulator is worth building only if it reproduces that sparsity pattern on those frozen pools
- Investigation first: QCi's published products, docs and papers, for a documented simulator or device model before building one. The SLSQP/Hexaly precedent in Emami et al. is the optimizer-backend candidate
- Acceptance (investigation): a written finding on whether QCi publishes a usable model, and either a build plan with the sparsity-reproduction test as its gate, or a recorded decision not to build with the reason. Acceptance (build, if taken): reproduces the B2 sparsity pattern on the frozen pools; miniaturized subsets so any test run completes within 10 minutes
- Depends on: nothing. Pairs with F94 (both prepare Experiment 3) and with F20
**F20. Soft-vote CVQBoost exploration (multi-level weak outputs) (~3h proxy investigation) Priority HOLD**
- Phase: Phase 2 preparation (team-lead approved 2026-09-02, "fits naturally as a post-submission/Phase 2 exploration item next to F17")
- Platform: local proxy first; Dirac-3 only if the proxy shows signal
- Replace hard +/-1 weak-classifier votes in the H matrix with confidence scores (predict_proba mapped to [-1,1], optionally discretized to the device's ~200-level dynamic range); same Hamiltonian shape (J=HH^T+lambda*I, C=-2Hy), same simplex solve -- a model variant, not a protocol change
- Rationale: hard votes discard per-learner confidence; the weights are already continuous (CVQBoost), so the information bottleneck is the vote quantization
- Zero-cost evaluation path: proxy side-by-side vs hard-vote pools on identical seeds (the A3 comparison machinery reused verbatim)
- Constraints: custom H construction departs from eqc-models' builders (pool identity with the library is lost; document as its own arm); Phase 1 evidence chain untouched; any Phase 2 use enters through that phase's preregistration
- Depends on: F17 pairs well (the simulator would evaluate both); nothing blocks the proxy investigation
- **Expanded 2026-10-03 (Phase 2 plan W3.2): multi-sample ensembling.** Average predictions over the top-k low-energy samples instead of keeping only the best. Zero added QPU cost, because the samples are already paid for, and it attacks the variance behind the train-test gap F90 carries. Needs F90 to store every returned sample (F90 acceptance (c))

**F25. Non-convex CVQBoost: cardinality-constrained weak-learner selection on Dirac-3 (~4h investigation + hardware) Priority HOLD**
- Phase: Phase 2, **Experiment 3 device run** (team-lead approved 2026-09-03; the direct consequence of the Sprint 4 degeneracy finding)
- **HOLD reason, restated 2026-10-03**: needs F102 (preregistration), F94 (controls) and the allocation. Sized at 3,070 s in the sent hardware plan; after F90 about 445 s of the 1,681 remain, so this card depends on the additional 7,500 s asked of QCi
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
- **Measured queue behavior, 2026-09-09**: the F46 probe submitted at 14:33 local was still queued 52 minutes later, having spent ~97 CPU-seconds on its local pool build. Flat CPU against growing wall clock is the signature of queue wait, not computation. The team lead reports the queue is ALMOST ALWAYS EMPTY AFTER 5PM LOCAL, so wall-clock cost is a function of WHEN a block runs, not what it computes
- **The team lead's intent for this card**: enqueue 4 or more jobs at once so they run CONSECUTIVELY, raising the odds they execute back to back rather than each paying a fresh queue wait. That is a different and stronger value case than the throughput argument below
- Value was judged to arrive with Phase 2 volume (81+ fit grids), and that judgment was made against a free tier with 163 spent seconds. With 3,000 granted seconds (F46) and queue wait as the binding cost rather than device seconds, the case is stronger: whenever a session needs more than one or two fits, serial submission wastes most of the wall clock. Still not recommended BEFORE submission, on calendar grounds alone
- Depends on: nothing to build; live vetting needs team-lead approval (Criterion H)

**F13. Phase 2 PoC sprint planning (~unknown) Priority HOLD**
- Phase: Phase 2 (Nov 17 - Feb 28, if selected)
- Platform: All
- Braket hardware validation, IEEE-CIS at scale, calibrated deployment per the routing architecture; plan built on acceptance

**F6. Braket gate-based arm: what is possible and what is worth doing in Phase 2 (~0.5 day investigation, zero metered) Priority 70**
- Phase: Phase 2 preparation (**OFF HOLD 2026-10-02**, team lead: "we will try to analyze what is possible and valuable for Phase 2"; re-scored 16 to 70 in the 2026-10-03 refinement)
- **Covers the proposal's section 7 commitment** to a gate-based arm (the 2026-10-03 checklist correction moved it out of the six). A pursue recommendation leads to F106 and F107
- Platform: Braket simulator, then hardware only if justified
- **Scoped as an ANALYSIS, not a build.** The deliverable is a written answer to "what is possible and what is valuable", with a recommendation. The original card jumped straight to an encoding choice; that choice is an output of this work, not its premise
- **The one hard constraint already established**: plain Ry encoding is provably classical by the Inverse Born Rule, so any arm that could show a quantum effect needs a sandwich or entangling encoding. Stating that up front is cheaper than discovering it mid-build
- **Verified 2026-10-02**: no gate tooling is installed (`braket`, `qiskit`, `pennylane` and `classiq` are all absent), and `HARDWARE_PLAN_PHASE_2.md` makes no Braket commitment. Nothing is promised to QCi beyond the memo naming Braket and Classiq as planned additional experiments, which is the only external statement to honor
- **What the analysis must settle**: which encodings are not provably classical; what Braket's free simulator tier supports against what needs paid hardware time; whether any gate formulation addresses the problem Phase 1 actually hit, a convex objective with nothing to win, or merely relocates it; which diagnostics would distinguish a real effect from a reparameterization (phase complexity, Berry connection and mode mutual information are the candidates); and what the cheapest falsifiable first experiment would be
- **The risk, stated in advance**: Phase 1's null came from choosing a formulation where the optimizer could not win. A gate-based arm chosen for novelty rather than for having real work to do would repeat that mistake on different hardware. The analysis should say so plainly if that is where the evidence points
- The team lead brings near-expert AWS and hands-on Braket experience, so platform learning is not the cost here
- Acceptance: a written analysis with a recommendation (pursue, pursue narrowly, or decline with the reason); any pursue recommendation names the encoding, the diagnostic, the cost and the falsifier before any code is written
- Depends on: nothing. Informs F13 (Phase 2 PoC planning)

**F121. Experiment 5 transfer half and router acceptance (~unknown) Priority HOLD**
- Phase: Phase 2, Experiment 5 (added 2026-10-03). Transfer of the in-segment result to fraud segments, judged by the proposal's router criterion: at least one point of recall at the 0.5% budget above the classical champion, out of time, on prespecified segments, against a matched random-segment control
- HOLD until F90 reports. Bounded in advance by F113

**F122. Four guards that are accurate-but-weak, from the PR #146 review (~45m, zero metered) Priority 22**
- Phase: Finalize / tooling (added 2026-10-04 from the PR #146 reviews)
- Platform: N/A (`test_spectra_reconciliation.py`, `test_troubleshooting_index.py`, `test_ci_status.py`, `test_sent_correspondence.py`)
- **Backlogged rather than fixed in the review round, deliberately.** The ten findings fixed there were defects: a guard that passed on a commented-out ignore rule, a budget blind to 75 of 98 seconds, figures inflatable tenfold. These four are different in kind -- each guard works, and each is narrower or more brittle than its name claims. Rushing them at the end of a review round is how a careless edit reaches a file nobody is reviewing any more
- **(a) The ordering guard pins COMMENTS, not execution order.** `test_the_ci_check_runs_before_the_gh_dependent_issues_check` uses `src.index("# CI on the HEAD commit.")`. Renaming that comment fails the test with zero code change, and moving the code while leaving the comments in place passes it. Anchor on the calls (`ci.evaluate` against the `gh pr list` subprocess) instead
- **(b) The decision guard goes red the day the decision is recorded.** `test_the_reconciliation_does_not_pretend_to_decide` asserts that "does not pick" or "not yet made" appears. A guard that fails on correct progress gets deleted, which is a pattern this repository has already paid for four times
- **(c) The options guard checks no costs**, contrary to its name and docstring: it asserts only that "Option 1" through "Option 4" appear. Either assert each option carries a figure, or rename it to match what it does
- **(d) The sidecar manifest does not descend.** `d.iterdir()` with `is_file()` means a file added inside a new subdirectory leaves the hash UNCHANGED (verified by a reviewer). The real Word export is flat, so this is latent rather than live -- but the docstring claims the manifest catches "a file ADDED", and that is true only at the top level. `d.rglob("*")` with paths relative to `d` would make the claim hold as written
- Acceptance: each of the four rewritten so the assertion matches its name; each proven RED by a mutation the current version survives; no guard left that fails on correct progress
- Depends on: nothing


**F116. G2 entanglement ablation on the SV1 simulator (~3h [no-history]) Priority HOLD**
- Phase: Phase 2, gate-based arm (added 2026-10-03). Joint entangling terms ON against OFF, all else identical, with a paired bootstrap CI on the gap
- HOLD until F106 shows the circuit is not dequantized

**F117. G4 noise as regularizer: DM1 simulator, then the cheapest hardware (~4h + paid Braket time) Priority HOLD**
- Phase: Phase 2, gate-based arm (added 2026-10-03). Per-gate error rates 0.000 to 0.015; the published prediction for a tuned baseline is degradation
- HOLD: Phase 2, needs paid Braket time and F116

**F118. Latency benchmark p50/p95/p99 against the 100-300 ms envelope (D10) (~unknown) Priority HOLD**
- Phase: Phase 2, resourcing (added 2026-10-03, from the checklist). Phase 1 states the envelope as a target, not a measurement
- HOLD until the Phase 2 brief

**F119. Calibration layer fit (D1) (~unknown) Priority HOLD**
- Phase: Phase 2, resourcing (added 2026-10-03, from the checklist). Phase 1 specifies the layer and does not fit it
- HOLD until the Phase 2 brief

**F120. Structural feedback audit: delay, censorship, corruption, decline rate (~unknown) Priority HOLD**
- Phase: Phase 2, ceiling methodology (added 2026-10-03). Proxies for the four impairments in the payments-network regret floor (arXiv:2605.27557); that paper gives no estimation procedure
- HOLD: most proxies need sponsor data that a public dataset does not carry. Say so plainly where one cannot be estimated
