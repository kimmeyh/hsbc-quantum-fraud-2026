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
| 8 | docs/sprints/SPRINT_8_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 6-7, 2026) |
| 9 | docs/sprints/SPRINT_9_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 7-8, 2026) |
| 10 | docs/sprints/SPRINT_10_SUMMARY.md | [OK] Complete | ~1 day (Sep 9, 2026) |
| 11 | docs/sprints/SPRINT_11_SUMMARY.md | [OK] Complete | ~1.5 days (Sep 9-10, 2026) |
| 12 | docs/sprints/SPRINT_12_SUMMARY.md | [OK] Complete | ~2.5 days (Sep 10-12, 2026) |

## Last Completed Sprint

**Sprint 12: Spend the Grant, Then Submit** (Sep 10-12, 2026; PR #75 to develop,
PR #76 develop to main). Delivered **F2b blocks B2 and B3** on Dirac-3, **F37**
(repository public), **F38** (page limits), and **F49-F63**, the response to
three external reviews. Suite 277 -> 320. Hardware: 968 metered seconds of a
2,000 s authorization, 23 fits, zero device failures.
**The positive result**: B2 is the campaign's only gain at scale (A24). Eleven
fits at 833 continuous variables against B1's matched `hw_b1_dct` arm on
identical seeds: **+0.0256 AUPRC, 95% CI [+0.0203, +0.0310], 10 of 10 seeds**.
Unpaired it is invisible inside a 0.030 seed-to-seed SD. It still trails
full-feature CatBoost by 0.0440, so the null holds.
**The sprint's defining fact**: the review found three PUBLISHED claims that were
false, and we had written all three. The solver was not converged (A26) -- the
stopping test certified the objective, not the solution, at KKT residual 4.6e-05.
The convexity claim was false (A27) and had been written the previous day in
response to an internal review, then published within hours. Uniform is not the
zero-penalty optimum (A27), the same solved-from-versus-evaluated-at confusion in
a second place. Every internal check had agreed with itself, because the figure
and the error came from the same solver.
**What the review bought**: the 200:1 resolution finding (A31). Our claim that
hardware agreement bounded resolution effects was backwards -- on all ten pools
nothing in the problem is visible to the device, so uniform output is forced
rather than evidence. That turned the weakest mechanism paragraph into the
strongest argument for Phase 2: a device that cannot spread weight over ~200
learners has a native problem class, and it is cardinality-constrained selection.
**Process**: the team lead's intervention -- stop, analyse both reviews fully,
address findings through planned cards rather than reactive edits -- is what
broke the amend-under-pressure loop. It is now a standing rule and a hook.
Retro: docs/sprints/SPRINT_12_RETROSPECTIVE.md (all rated categories Very Good;
all seven improvements applied, three of them made deterministic).

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
| Finalize | Sep 11-13 | **F10 only.** F40, F37 and F38 all DONE (Sprints 10 and 12), so F10 is the sole remaining submission blocker | no new evidence after Sep 12; never later than Sep 14 |

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

**F64. Decompose the B2 confound: the k=17 order-2 cell (~45m) Priority 1 -- PHASE 2 EXPERIMENT 1**
- Phase: Experiments / correctness
- Platform: classical proxy (`qubo_proxy.py`, `mechanism_controls.py`)
- **THE MISSING MIDDLE OF A THREE-POINT LADDER.** B2's +0.0256 is the campaign's only positive result at scale, and two factors moved to produce it: k (13 -> 17) and subset order (2 -> 3). We hold both ends and neither middle:
  - k=13, order 2, 91 vars -> 0.7671 **[have]**
  - k=17, order 2, **153 vars** -> ? **[MISSING]**
  - k=17, order 3, 833 vars -> 0.7928 **[have]**
- Running the middle cell splits the gain into "more features" and "richer learners". Appendix B.3 currently has to say the disconfirming cell is unrun, about the one experiment that would resolve its own headline claim's confound
- **THE PHYSICS PREDICTS AN ANSWER, which is what makes it a test rather than a data point.** A31 established the device cannot spread weight over more than about 200 learners. At 153 variables it CAN; at 833 it cannot. If the gain is attributable to k, it should appear at 153 under a faithful solve. If it needs three-feature learners, it will not. Either outcome is informative, and one of them would materially change what B.3 claims
- **ZERO METERED SECONDS.** Classical proxy only, ten pool builds at 153 variables
- **Why it was NOT run in Sprint 12** (team lead decision, 2026-09-12): the submission documents were final and within limits, PR #75 was merge-ready, and the deadline was 2026-09-15. A new result means new figures in a 6-of-6-page proposal and possibly another amendment. The submission is stronger finished than with one more experiment squeezed into its last days. Deferred deliberately, not overlooked
- Acceptance: the cell runs on the same seeds and protocol as its two neighbours; B.3 states the decomposition instead of declining it; if the result changes what the +0.0256 is attributable to, that is an amendment
- Depends on: nothing. It is the first thing Phase 2 should run
- **SELECTED for Sprint 13 then WITHDRAWN the same day (team lead, 2026-09-12).** The reason is methodological and supersedes the Sprint 12 scheduling deferral above. F64 varies ONE axis with everything else frozen at values chosen for a different configuration (pool family, lambda, weak-learner type, the cardinality question). The gain that matters is likely a COMBINATION of these, so a one-factor-at-a-time probe measures the axis it varies and is silent about the interaction, which is where the leverage is expected to sit
- The result could not become FALSE, but it could become UNIMPORTANT: a true fact about a formulation Phase 2 abandons. A31 already established that the device cannot spread weight over more than ~200 learners, so F64 decomposes a result inside a formulation we already have evidence is the wrong ask of the hardware
- **Decisive**: proposal section 6 presents this cell as experiment 1 of SIX in an ordered program, each with its acceptance criterion written before it runs, and experiment 3 is the cardinality-constrained formulation A31 points to. Running experiment 1 early and reporting it alone converts an ordered program into one result plus five things we did not do. The program is the stronger artifact
- **Pre-flight already done** (2026-09-11/12), so Phase 2 starts from a measured base rather than a cold one: (k=17, order 2) is NOT reachable today because `CONFIGS` in `qubo_proxy.py` holds only the two ladder ENDS and `--config` is bounded by `choices=list(CONFIGS)` -- one dict entry clears it. Pool build measured at **6.6-7.3 s** (WSL, seed 42), prep 21.9 s, so ten seeds is ~10 minutes. The full-pair build CANNOT run on Windows (`fork` unavailable). And a new ten-seed full-pair cell enters `score_gates.py`'s argmax over validation AP, which can silently re-key the H1b confirmatory table -- diff `Proxy cell used:` before publishing

**F2b. Hardware campaign, remaining blocks B4 and B5 (~0.5 day + approvals) Priority 20**
- Phase: Experiments
- Platform: Dirac-3
- **B1 + G0b DONE** (Sprint 4, 120 QPU s). **B2 DONE** (Sprint 12, 11 fits, 906 s, A24). **B3 DONE** (Sprint 12, 12 fits, 62 s, A23 after the A22 withdrawal and matched re-run). Only B4 and B5 remain
- **B4** (SPECTRA, 15 fits, ~450 s) and **B5** (QSVM sign-augmented, 12 fits, ~15 s). B5 is cheap enough to run inside any remaining balance; B4 is the one that needs a real allocation decision
- B4 overlaps **F5** (SPECTRA in-segment replication), which sits in HOLD. They are the same block from two angles and should be reconciled before either is scheduled
- Neither is a submission blocker. Both are post-submission work on the current calendar
- Depends on: per-block team-lead approval (Criterion H); allocation balance
- **The billing rule is now validated far outside its anchors.** B2's first fit at 833 variables, degree 3 cost 91 metered seconds where the grid assumed ~40. `ceil(sum(runtime))` predicted it exactly (runtime sum 90.152 s, balance 2929 -> 2838). Per-sample cost 11.27 s against B3's ~0.6 s, an **18.8x** step. Use measured per-sample cost, not the original grid, for any B4 estimate


**F65. Per-fit artifact write in the hardware runner (~45m) Priority 11**
- Phase: Experiments / tooling (lifted out of the F2b card in the Sprint 12 close-out sweep, 2026-09-11, where it had no F# of its own)
- Platform: `experiments/src/run_hardware.py`
- `run_hardware.py` writes its block artifact only at BLOCK completion, so a process that dies after a billed call leaves no `bN_hardware.json` even though the money is spent
- **Observed in Sprint 12**: the first B2 fit did exactly that (WSL teardown on parent-shell exit, no traceback). Nothing was lost, because the raw response, the predictions `.npz` and a full `results.json` row with `metered_seconds: 91.0` had all persisted first. That was lucky, not structural
- The fix is to write or append the block artifact after each fit rather than at the end, so a dead process leaves a partial artifact instead of none
- Value: it prevents PAID evidence from being unrecoverable. At 91 metered seconds per B2-class fit, one lost fit is real money against a finite allocation
- Depends on: nothing


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

**F39. Fact database: one source of truth for every asserted fact (~1-2 days) Priority 2 -- HOLD until after submission**
- Phase: Post-submission / Phase 2 tooling (team lead, Sprint 8 retrospective 2026-09-07: "We need to create a 'fact database' ... It states facts that we can confirm with confidence intervals between 0.0% and 99.9%. There are likely over 1,000 and this makes it difficult to keep track of ... if we need to update the baseline facts it should be here and then all other sources use this as the basis")
- Platform: tooling
- **The problem it solves, with this sprint's evidence**: the same fact is currently restated in many documents with no link between the copies. Sprint 8 alone found the QCi letter asserting "twelve amendments" when the enclosed preregistration had seventeen; A15 corrected a k=6 AUPRC published as 0.7688 when the true value was 0.7629, a figure that had been carried from a five-seed run into a ten-seed writeup; and A17 forced recomputation of every A11/A13 figure across four documents. Each was caught by a human reading, or by a one-off script written for that one check
- **Scale**: the team lead estimates over 1,000 asserted facts. The current control is `score_gates.py` regenerating gate figures plus ad-hoc verification scripts; neither covers prose assertions, and nothing covers cross-document consistency
- **Design direction (team lead: research Cycorp/cyc.com, functionally representative, NOT a LISP reimplementation)**: each fact carries an identifier, a value, a provenance pointer to the results row or source that establishes it, an evidence tag ([HW]/[SIM]/[PROJ]), and a CONFIDENCE between 0.0% and 99.9%. Documents reference facts by identifier rather than restating values, and a build step resolves references and fails on an unresolved or stale one. The confidence field is the part worth taking from Cyc: it forces "how sure are we" to be recorded next to the claim rather than carried in someone's head
- **Why confidence intervals matter here specifically**: this project already distinguishes measured from projected via evidence tags, but not strong-measured from weak-measured. The score-degeneracy caveat, the single-seed spot checks, and the adversarial control that never converged are all facts we assert with genuinely different confidence, and today that distinction lives only in prose
- **Explicitly held until after submission** (team lead: "We may hold this until after submission"). It is infrastructure, and eight days out the risk of touching every document exceeds the benefit
- Acceptance: every numeric assertion in proposal, appendix and the QCi letter resolves to a fact record; the build fails on a stale reference; and a deliberate edit to one fact value propagates to every document that cites it
- Depends on: nothing. Best started after F16/F10 and the submission

(F40 segment non-public material: COMPLETED in Sprint 10, merged via PR #58 (main PR #62); history in SPRINT_10_SUMMARY.md. Removed from candidates per convention.)

(F37 make the repository public: COMPLETED in Sprint 12, merged via PR #75. Verified
anonymously -- HTTP 200, freeze commit 95751b9 resolves, `prereg-freeze` tag intact.
Removed from candidates per convention.)

### Paper (Stages 4-6)

### Finalize (Stages 7-8)

(F35 interpretation-layer tests, F41 mechanism correction (A20), F42 review findings, F43 IEEE-CIS AUC-ROC, F44 figure resolution, F45 evidence guard, F46 QCi grant and ceiling probe (A21), F47 metered-call wrapper: ALL COMPLETED in Sprint 11, merged via PR #66 (main PR #70); history in SPRINT_11_SUMMARY.md. Removed from candidates per convention.)

**F66. Record the Copilot reviewer-request procedure in the workflow (~15m) Priority 10**
- Phase: Finalize / process (Sprint 12 retrospective category 13, 2026-09-11)
- Platform: `docs/SPRINT_EXECUTION_WORKFLOW.md`
- Requesting a Copilot review needs the actor `copilot-pull-request-reviewer[bot]` (node id `BOT_kgDOCnlnWA`). NOT `Copilot`, and NOT `copilot-swe-agent`. The wrong name fails SILENTLY
- Compounding it: the REST `requested_reviewers` field returns only users, never bots, so a SUCCESSFUL bot request reads back as an empty list. There is no way to confirm from that field that the request landed
- **Observed in Sprint 12**: PR #73 never received a review for this reason and nobody noticed until PR #75 was being set up
- A cross-repository skill already documents the three silent-failure modes and the working GraphQL procedure. This card is the in-repo pointer to it, so the workflow document does not depend on the skill being loaded
- Value: it prevents a review step from silently not happening. The failure is invisible by construction, which is what makes it worth writing down
- Depends on: nothing


**F48. Extend the escape hook to shell metacharacters (~45m) Priority 9**
- Phase: Finalize / tooling (Sprint 11 retrospective improvement 4, backlogged 2026-09-09)
- Platform: .claude/hooks
- `block-unraw-escape.ps1` catches Windows path escapes in non-raw PYTHON strings and has fired correctly several times. It does not catch SHELL metacharacters: a backtick or `$(...)` inside a quoted string passed to Bash is expanded by bash before Python ever sees it
- **Observed in Sprint 11**: backticks inside a Python string in a Bash command were expanded as command substitution, executing a source file as shell and silently deleting the backticked filenames from a master-plan line. The edit "succeeded" and the damage was only visible on inspection
- The fix is the same shape as the existing hook: detect backticks or `$(` inside a quoted span destined for Bash, and require the single-quoted heredoc form that suppresses expansion
- Lower priority than the submission blockers, and real: the failure mode is SILENT corruption of a file that was edited successfully, which is worse than a crash
- Depends on: nothing

(F49 solver optimality certificate, F50 convexity withdrawal, F51 protocol-history
deviations, F52 document contradictions, F53 prior-work interpretations, F54 provenance,
F55 the two missing rubric sections, F56 framing, F57 the 200:1 resolution argument, F58-F63
the remaining review findings: ALL COMPLETED in Sprint 12, merged via PR #75 (main PR #76);
history in SPRINT_12_SUMMARY.md. Removed from candidates per convention.)

**F10. Verification, confidentiality scan, compliance walk, submission (~0.5 day) Priority 1 -- SUBMISSION BLOCKER**
- Phase: Finalize
- Platform: docs
- Every number vs results.json; repo-wide confidential-string scan (the fourierwall2 reference files were moved OUT of the repository at Sprint 10 F40, so the scan covers what remains rather than re-verifying them in place); requirements-matrix walk; public reproducibility repo; team-lead final PDF + portal submission, receipt archived
- Depends on: F8, F9 (both DONE, Sprint 5)
- **Priority corrected 2026-09-11** in the Sprint 12 close-out sweep. This card read Priority 40 while the targeted roadmap has carried it as a SUBMISSION BLOCKER for the Finalize sprint since 2026-09-03. The deadline is 2026-09-15. Nothing else in the backlog outranks it

### External (team-lead-owned, parallel)

(F11 QCi sponsorship letter send: COMPLETED by the team lead 2026-08-30. F12 portal verification and F15 best-practices/ADR review: COMPLETED in Sprint 2, merged via PR #2; history in SPRINT_2_SUMMARY.md. All three removed from candidates per convention.)

(F4 H6 representation arm, F14 eqc-models feedback package, and F16 minimal CI: COMPLETED in Sprint 9, merged via PR #53 (main PR #54); history in SPRINT_9_SUMMARY.md. All three removed from candidates per convention.)

### HOLD Items (post-submission)

**F5. SPECTRA in-segment replication, block B4 (~0.5 day) Priority HOLD**
- Phase: Experiments (moved to HOLD by team lead 2026-09-08 at Sprint 10 refinement)
- Platform: SPECTRA, Dirac-3
- 3 strongest cells x 5 seeds; random-segment negative control machinery reused for fraud transfer
- **Why HOLD**: needs the QCi grant, which has only been acknowledged, not granted (card #40 open). Blocked by the same pending reply as F25
- Depends on: QCi grant; F2 approval pattern

**F29. Sample-size insensitivity of the CVQBoost optimum (~1h measured, zero metered) Priority HOLD**
- Phase: Experiments (moved to HOLD by team lead 2026-09-08 at Sprint 10 refinement)
- Platform: ULB proxy
- **Effort re-measured 2026-09-08, and the old ~2h was wrong in the cheap direction**: pool build scales O(n^1.4) -- 8.8s at 50k rows, 25.9s at 100k, 82.2s at 250k. The ULB train fold is 170,236 rows after dedup and the 60/20/20 split, so the full 3-seed x 4-size grid is 8-10 minutes of build plus solve and scoring. It could have run in parallel with anything
- **Why HOLD anyway, and this is the deciding reason**: it scores against no rubric criterion. The weights are Problem Relevance & Impact 25%, Technical Approach & Innovation 25%, Feasibility 20%, Validation Plan 15%, Team Capability 10%, Hybrid 5%. A stability property of our own optimizer is not a fraud-detection result, a validation-protocol improvement, or a hybrid-integration argument
- **The proposal already makes the production-cost argument better** (section, line 94): CVQBoost's published claim is a runtime advantage from 1M to 70M samples, our null sits at 284k rows, and the untested question is end-to-end training time against sample count whose Hamiltonian construction grows with the square of the pool size. That is sharper than "the optimum is insensitive to sample size"
- **Three further costs**: it needs a dated amendment (A20) four days from the evidence freeze; the card's own honesty constraint requires connecting it to the near-degeneracy finding, which a reviewer reads as the same finding restated; and it needs page space in two documents that are currently OVER limit, working against F38
- Post-submission value is real; the Phase 2 plan can name it as a follow-up at zero cost
- Depends on: nothing (reuses qubo_proxy build/solve)

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
- **Measured queue behaviour, 2026-09-09**: the F46 probe submitted at 14:33 local was still queued 52 minutes later, having spent ~97 CPU-seconds on its local pool build. Flat CPU against growing wall clock is the signature of queue wait, not computation. The team lead reports the queue is ALMOST ALWAYS EMPTY AFTER 5PM LOCAL, so wall-clock cost is a function of WHEN a block runs, not what it computes
- **The team lead's intent for this card**: enqueue 4 or more jobs at once so they run CONSECUTIVELY, raising the odds they execute back to back rather than each paying a fresh queue wait. That is a different and stronger value case than the throughput argument below
- Value was judged to arrive with Phase 2 volume (81+ fit grids), and that judgment was made against a free tier with 163 spent seconds. With 3,000 granted seconds (F46) and queue wait as the binding cost rather than device seconds, the case is stronger: whenever a session needs more than one or two fits, serial submission wastes most of the wall clock. Still not recommended BEFORE submission, on calendar grounds alone
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

