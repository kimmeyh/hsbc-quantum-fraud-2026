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
| 13 | docs/sprints/SPRINT_13_SUMMARY.md | [OK] Complete | ~1 day (Sep 12, 2026) |

## Last Completed Sprint

**Sprint 13: Submit** (Sep 12, 2026; PR #82 to develop). Delivered **F10** and
**FILED THE SUBMISSION** on 2026-09-12, three days before the deadline. Portal
returned "Your submission received": proposal 6 of 6 pages, appendix 3 of 3,
team profile 1 of 1. Suite 320 -> 321. Zero metered seconds.
**The finding**: a sprint scoped as routine verification found NINE defects, and
the suite caught none of them. One in the evidence artifacts (the B2 comparator
written as 78 variables where its rows carry 91), six in the requirements matrix
including C5 and C6 pointing at the wrong sections after F55's renumbering, and
six in the submission documents.
**The defect that justifies F39**: appendix A.5 quoted the IEEE matched-feature
control as falling "from 0.5739 to 0.0734 ... fold 0", where the artifact's
control is fold-0 to fold-0 at 0.5424 and 0.5739 is the three-fold mean from a
different file. Both numbers are real, so a global value-set lookup accepts it --
`test_document_figures_resolve.py` passed it and its own docstring predicts
exactly that blind spot. Only per-claim provenance closes it.
**A32** corrects A31's linear-term spread, which quoted 16.0 as a maximum where
the stored values reach 28.0.
**F64 was selected then withdrawn** the same day on the team lead's reasoning: a
one-factor-at-a-time probe into an interaction space could return a true but
unimportant result, and proposal section 6 already presents the cell as
experiment 1 of six in an ordered program. Its pre-flight is preserved on the
card so Phase 2 starts measured.
**Process**: six findings were presented for approval and item 5 recommended
taking NO action; all six were approved as fixes and one was backed out. The
workflow now states that a list presented for approval contains only items to be
changed.
Retro: docs/sprints/SPRINT_13_RETROSPECTIVE.md (Very Good across all fourteen
rated categories; all six improvements applied).

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

**THE PHASE 1 ROADMAP IS COMPLETE (2026-09-12).** Every row above is [DONE] and
the submission is filed. The table described a run to a deadline; that deadline
has passed in our favour and the roadmap no longer describes any pending work.

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

**F68. Freeze the submitted artifacts the way the preregistration is frozen (~2h) Priority 1 -- SPRINT 14, FIRST**
- Phase: Finalize / governance (team lead, 2026-09-12)
- Platform: `.claude/hooks`, `.claude/settings.json`, `README.md`
- The three submission documents were JUDGED as filed on 2026-09-12. They are now a record, not a draft, and should be protected the way `PREREGISTRATION.md` is
- **A DEFECT FOUND WHILE PLANNING THIS CARD, and it is why the card goes first.** Both Edit-matcher hooks -- `block-unapproved-submission-edit.ps1` and `block-reactive-amendment.ps1` -- have NEVER RUN. `.claude/settings.json` registers them as `...\\hooks\block-...`, and the single backslash before `b` is a JSON backspace escape, so the path resolves to `hooks\x08lock-...` which does not exist. Claude Code skips a hook whose file is absent, silently. Broken since commit `7a57065`, the commit that created them
- Consequence, stated plainly: the Sprint 13 retrospective recorded "the Class 4 hook worked exactly as designed". That was FALSE. Every submission-document edit in Sprint 13 was unguarded. The process held because the team lead approved each change in conversation, not because anything enforced it
- This is F48's defect class -- a silent escape corruption -- in the file that registers the guard against it
- Scope: (1) fix both registrations and prove they fire by injection; (2) add a test asserting every registered hook path exists on disk and contains no control characters, so the class cannot return silently; (3) extend the submission-edit hook to cover history rewrites and tag moves affecting `prereg-freeze` and the submission commit; (4) document in the README how to find, fork and clone the repository exactly as submitted
- Acceptance: both hooks demonstrably block, verified by injection; a test fails if any registered hook path is unresolvable; README carries the as-submitted retrieval instructions
- Depends on: nothing

**F69. README rebuilt for a public repository (~2h) Priority 2 -- SPRINT 14**
- Phase: Finalize / documentation (team lead, 2026-09-12)
- Platform: `README.md`
- The repository has been public since 2026-09-11 and the README still reads as a private working note: it points at a `paper/` path that does not exist, and its "Immediate to-do" asks for the challenge PDFs that were staged weeks ago
- Required sections: where to find the key summary documents; a HOW TO REPRODUCE section (clone, environment setup, virtual environment, how to run one quick test, how to run each major test with its caveats -- notably that the pool-dependent tests need data that is not redistributed); and the as-submitted retrieval instructions from F68
- Style: standard open-source README conventions adapted to an evidence repository rather than a library -- what this is, what was submitted, how to verify a claim, how to reproduce, what is deliberately absent and why
- **The reproduce section must be TESTED by following it, not written from memory.** Appendix C claims every figure regenerates from this repository; a README that does not actually work makes that claim false for the first reader who tries
- Acceptance: a reader with no prior context can clone, set up, and run a test from the README alone
- Depends on: F68 for the as-submitted section

**F70. CHANGELOG backfilled and wired into the close-out (~1.5h) Priority 3 -- SPRINT 14**
- Phase: Finalize / process (team lead, 2026-09-12)
- Platform: `CHANGELOG.md`, `docs/SPRINT_EXECUTION_WORKFLOW.md`
- **MEASURED 2026-09-12: the CHANGELOG stops at 2026-09-04.** Eight days are missing (Sep 5 to 12), covering Sprints 7 through 13 -- the entire hardware campaign, all three external reviews, the page-limit work, the public-repository flip and the submission itself
- Backfill from what can be recovered: git history, the sprint summaries, the amendment log and the merged PRs. Where a day cannot be reconstructed with confidence, say so rather than inventing it
- **The process half matters more than the backfill.** Add the CHANGELOG update to the Phase 8 close-out, positioned after the PR merges and BEFORE backlog refinement, so the gap cannot silently reopen
- Acceptance: every day with commits from 2026-09-05 onward has an entry or an explicit note that it could not be reconstructed; the workflow names the step and its position
- Depends on: nothing

**F71. CHECKLIST restructured into three phases (~1.5h) Priority 4 -- SPRINT 14**
- Phase: Finalize / process (team lead, 2026-09-12)
- Platform: `CHECKLIST.md`
- The checklist is titled "Submission-Ready by Sep 8, 2026" and still carries 18 unchecked boxes against work that is finished or abandoned. It describes a deadline that has passed
- Restructure into three sections in this order: (1) PRE-PHASE 2, the live list covering the wait from 2026-09-12 to finalist notification in mid-November; (2) PHASE 2, populated from the proposal's own six-experiment programme and section 3 resourcing, to be filled out properly if selected; (3) CHALLENGE SUBMISSION, the completed Phase 1 list, corrected to reflect what actually happened and marked done
- The correction pass on section 3 is real work: items were added, dropped and re-scoped across thirteen sprints, and the checklist tracked none of it
- Acceptance: the first section is actionable today; the third reflects actuals rather than the original plan
- Depends on: nothing

**F72. Reference-paper library with retrieval, outside this repository (~4h investigation + design) Priority 5 -- SPRINT 14 (design only)**
- Phase: Phase 2 preparation / tooling (team lead, 2026-09-12)
- Platform: TBD, a separate repository
- The team lead wants deep-dive summaries of QML, quantum-computing and classical-ML papers -- analysed for applicability to Dirac-3, to gate-based work via Braket and Classiq, and to non-quantum tensor methods -- stored OUTSIDE this repository but referenceable FROM it, and searchable in a RAG-like way for future use
- **This card is investigation and design, not a build.** Deliverable is a proposal: where the library lives, what a paper record holds (citation, claim extracted, applicability verdict, confidence, link to any local artifact), how retrieval works, and how this repository cites into it without depending on it
- Design constraint that makes this non-trivial: a reference cited from a public evidence repository must resolve for a reader who does not have the other repository. Either the library is public too, or citations carry enough inline context to stand alone
- **Overlaps F39 deliberately.** Both are "structured records with provenance and confidence, retrievable, maintained outside prose". They should share a storage decision rather than making two, and F39 runs first because it has the concrete use case
- Acceptance: a written proposal the team lead can approve or reject, naming the storage tool and the maintenance model
- Depends on: F39's storage decision


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


**F67. Guard the pool-mechanism claim on a fresh clone (~1h) Priority 12**
- Phase: Experiments / tooling (Sprint 13 retrospective improvement 5, 2026-09-12)
- Platform: `experiments/src/test_pool_mechanism.py`, `experiments/results/pools/`
- `test_pool_mechanism.py` is the suite's ONLY skip. It skips because the pool `.npz` files are gitignored, so on a fresh clone it silently does not run
- What that leaves unguarded: the appendix A.4 claim that **80 to 84 of the 91 learners reproduce the training labels exactly and zero predict the negative class everywhere** (A20). The claim is TRUE -- it was recomputed from the raw pools during the Sprint 13 evidence walk, every seed landing in 80-84 -- but nothing in CI would notice if it stopped being true
- The decision this needs, which is why it is an hour and not ten minutes: either the pools belong in the repository (they are large, and Appendix C already promises the figures REGENERATE rather than ship), or a small committed fixture stands in for them. Those are different answers with different reproducibility stories
- Value: a skipped test reads as a passing suite. This is the one claim in the submission whose guard is present but inert
- Depends on: a team-lead decision on pools-versus-fixture


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

**F39. Evidence Based Database: investigation, design and ADR (~1-2 days) Priority 6 -- SPRINT 14 (design only, NOT a build)**
- **RENAMED 2026-09-13 (team lead): the card and the artifact are both the Evidence Based Database.** It was "fact database" from Sprint 8. The rename is not cosmetic: 0.7688 sat in four documents and was not a fact, and the unconverged solver produced figures that were not facts, so a store called a FACT database asserts the property it exists to check. Repository `EvidenceBasedDB`, private for now. Quotes below are left verbatim as they were written
- Phase: Post-submission / Phase 2 tooling (team lead, Sprint 8 retrospective 2026-09-07: "We need to create a 'fact database' ... It states facts that we can confirm with confidence intervals between 0.0% and 99.9%. There are likely over 1,000 and this makes it difficult to keep track of ... if we need to update the baseline facts it should be here and then all other sources use this as the basis")
- Platform: tooling
- **The problem it solves, with this sprint's evidence**: the same fact is currently restated in many documents with no link between the copies. Sprint 8 alone found the QCi letter asserting "twelve amendments" when the enclosed preregistration had seventeen; A15 corrected a k=6 AUPRC published as 0.7688 when the true value was 0.7629, a figure that had been carried from a five-seed run into a ten-seed writeup; and A17 forced recomputation of every A11/A13 figure across four documents. Each was caught by a human reading, or by a one-off script written for that one check
- **Scale**: the team lead estimates over 1,000 asserted facts. The current control is `score_gates.py` regenerating gate figures plus ad-hoc verification scripts; neither covers prose assertions, and nothing covers cross-document consistency
- **Design direction (team lead: research Cycorp/cyc.com, functionally representative, NOT a LISP reimplementation)**: each fact carries an identifier, a value, a provenance pointer to the results row or source that establishes it, an evidence tag ([HW]/[SIM]/[PROJ]), and a CONFIDENCE between 0.0% and 99.9%. Documents reference facts by identifier rather than restating values, and a build step resolves references and fails on an unresolved or stale one. The confidence field is the part worth taking from Cyc: it forces "how sure are we" to be recorded next to the claim rather than carried in someone's head
- **Why confidence intervals matter here specifically**: this project already distinguishes measured from projected via evidence tags, but not strong-measured from weak-measured. The score-degeneracy caveat, the single-seed spot checks, and the adversarial control that never converged are all facts we assert with genuinely different confidence, and today that distinction lives only in prose
- **Explicitly held until after submission** (team lead: "We may hold this until after submission"). It is infrastructure, and eight days out the risk of touching every document exceeds the benefit
- Acceptance: every numeric assertion in proposal, appendix and the QCi letter resolves to a fact record; the build fails on a stale reference; and a deliberate edit to one fact value propagates to every document that cites it
- **RESCOPED 2026-09-12 (team lead). This card is now PRE-BUILD INVESTIGATION AND DESIGN, ending in an ADR, not an implementation.** Deep-dive the problem and propose: which storage tool holds the database, how records are maintained and by whom, how documents cite into it, and how the build validates references. The hold condition ("until after submission") expired when the submission was filed
- **It may live in its OWN REPOSITORY** and be consumed by this one. This project becomes its first use case rather than its owner. That decision belongs in the ADR, and it should be made together with F72's storage decision rather than separately -- both are "structured records with provenance and confidence, retrievable, maintained outside prose"
- **SCOPE ADDED 2026-09-12 (team lead): the database covers vocabulary, not only figures.** Two record classes beyond the numeric assertions already described:
  - **Every acronym used in the repository** (CPU, KKT, AUPRC, MDE, BCa, QUBO, EQC, ...) with its expansion (Central Processing Unit, Karush-Kuhn-Tucker) and a description written at an **8th-grade math, science and English level**. Where a visual helps, a link to an image or short animation
  - **Every technical word and phrase in the proposal, appendix and repository** (machine learning, intellectual property, test-fold prevalence, metered fits, Spearman correlation, BCa intervals, Hamiltonian, KKT residual, ...) with a 1-3 sentence description at the same reading level, and a visual link where one helps
- **Cyc-derived scoring fields are carried on every record type**, including the ones not yet used, so the schema does not need widening later. The confidence field (0.0% to 99.9%) is the part worth taking from Cyc: it forces "how sure are we" to sit next to the claim
- **Why the glossary half is not decoration**: the submission is read by judges who are not all specialists, and the Guidelines say explicitly that a non-specialist reviewer must be able to follow the technical approach. A maintained glossary at a defined reading level is the mechanism for that, and it is reusable in Phase 2 where the audience widens again
- Acceptance for THIS card: an ADR the team lead can approve or reject, naming the storage tool, the record schema for all three classes (assertions, acronyms, terms), the maintenance model, the repository boundary, and how this project cites into it. No implementation
- **DONE 2026-09-13: ADR-0014 ACCEPTED.** The design card is complete. Scope was corrected during the review -- the HSBC glossary is use case ONE, not the boundary; the target is a domain knowledge base over QML, ML, QC and the major QC platforms. Building is a SEPARATE card and is not authorised by the ADR
- Depends on: nothing. Its storage decision gates F72

(F40 segment non-public material: COMPLETED in Sprint 10, merged via PR #58 (main PR #62); history in SPRINT_10_SUMMARY.md. Removed from candidates per convention.)

(F37 make the repository public: COMPLETED in Sprint 12, merged via PR #75. Verified
anonymously -- HTTP 200, freeze commit 95751b9 resolves, `prereg-freeze` tag intact.
Removed from candidates per convention.)

### Paper (Stages 4-6)

### Finalize (Stages 7-8)

(F35 interpretation-layer tests, F41 mechanism correction (A20), F42 review findings, F43 IEEE-CIS AUC-ROC, F44 figure resolution, F45 evidence guard, F46 QCi grant and ceiling probe (A21), F47 metered-call wrapper: ALL COMPLETED in Sprint 11, merged via PR #66 (main PR #70); history in SPRINT_11_SUMMARY.md. Removed from candidates per convention.)

- **MOTIVATING CASE ADDED 2026-09-12 (Sprint 13 evidence walk).** The strongest evidence yet for this card. Appendix A.5 quoted the IEEE matched-feature control as falling "from 0.5739 to 0.0734 ... fold 0". Both numbers are real and both are in the artifacts -- but 0.5739 is the THREE-FOLD MEAN from `ieee_classical.json` while the control is fold-0 to fold-0 and its baseline is 0.5424 in `ieee_cvqboost.json`. A global value-set lookup accepts it, because the number exists somewhere. `test_document_figures_resolve.py` passed it, and its own docstring predicts exactly this: "It does NOT catch a figure that exists in the store but is quoted in the wrong place." Only per-claim provenance -- this sentence cites THAT row -- closes it, which is what F39 is
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

(F10 verification, confidentiality scan, compliance walk and SUBMISSION: COMPLETED in
Sprint 13, merged via PR #82. The submission was filed 2026-09-12, three days before
the deadline; receipt and the four now-answered A5 unknowns in
docs/submission/SUBMISSION_RECEIPT.md. Removed from candidates per convention.)

### External (team-lead-owned, parallel)

(F11 QCi sponsorship letter send: COMPLETED by the team lead 2026-08-30. F12 portal verification and F15 best-practices/ADR review: COMPLETED in Sprint 2, merged via PR #2; history in SPRINT_2_SUMMARY.md. All three removed from candidates per convention.)

(F4 H6 representation arm, F14 eqc-models feedback package, and F16 minimal CI: COMPLETED in Sprint 9, merged via PR #53 (main PR #54); history in SPRINT_9_SUMMARY.md. All three removed from candidates per convention.)

### HOLD Items (post-submission)

**THE HOLD CONDITION EXPIRED 2026-09-12 when the submission was filed.** Every
item below was held for one reason -- it must not compete with the submission --
and that reason is gone. They are NOT automatically live: "no longer blocked" is
not "selected", and the team lead sets priority. But they should be read as
candidates at the next refinement rather than skipped as held, and the same
applies to F39, whose card still says "HOLD until after submission".

Flagged rather than re-prioritised: re-scoring nine cards is a scope decision,
not a sweep correction.


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

