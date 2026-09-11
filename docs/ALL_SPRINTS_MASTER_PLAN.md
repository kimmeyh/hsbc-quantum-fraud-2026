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

## Last Completed Sprint

**Sprint 9: Representation, and Paying What We Promised** (Sep 7-8, 2026; PR #53).
Delivered **F4** (H6, the last preregistered experimental arm), **F14** (the
eqc-models feedback package QCi's letter had promised) and **F16** (minimal CI
with a dirty-tree gate). ZERO metered Dirac-3 seconds.
**The finding**: H6 is a measured null. The QFE phase representation shifts the
quantum-minus-classical delta by -0.0115 against a paired SD of 0.0135, which is
43% of our 0.0268 MDE and negative on 7 of 10 seeds. Reported as "a small
negative shift that does not reach claimable size" -- not "no effect", not
"widens the gap". The framing was fixed in writing BEFORE any result was seen,
which mattered: between four and nine seeds an apparent monotonic negative drift
reached ratio 0.70, and seed 46 broke it in both runs to within 0.0003.
**The sprint's defining fact**: the same arm ran THREE times and two runs were
discarded, 18.9 hours of compute against a 10-minute estimate. Run 1 crashed on
a spline basis refitted on TEST data. Run 2 completed 20/20 cells cleanly and
was discarded because two of three classical twins never received the
representation under test -- they ranked inputs by variance, and ULB's Time
column has variance 2.3e9 against whitened phase columns at 1.0. Both defects
share a shape: the code ran, the numbers were plausible, and the experiment was
not the experiment the preregistration specifies.
**What the fix bought**: not a different number -- a GBDT was the best classical
arm in all 20 cells either way -- but a different meaning. The corrected GAM
twin scores 0.7893 against the quantum arm's 0.7646, where before it scored
0.2590 and was noise. "Best classical" now denotes a bar that can exploit
periodic structure, which is what makes the comparison survive the Fourier Wall
objection.
Retro: docs/sprints/SPRINT_9_RETROSPECTIVE.md (15 categories all Very Good;
improvements 1, 2 and 4 applied, 3 declined; suite 173 -> 194).

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
| 12 | Sep 10-12 | **F37 -> F38 -> F10** in that order, plus the fresh-eyes review; Dirac-3 work only if the calendar allows | SUBMISSION SPRINT; evidence freeze Sep 12 |
| Finalize | Sep 12-13 | F10, **F40 (segment non-public material)** -> **F37 (repo public)** in that order, **F38 (page limits)** -- all SUBMISSION BLOCKERS; submit Sep 13 | no new evidence after Sep 12; never later than Sep 14 |

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
- **MEASURED 2026-09-10 (Sprint 12), B2 cost is no longer an estimate.** One fit at 833 variables, degree 3, seed 42 cost **91 metered seconds** -- not the ~40 s/fit the grid assumed. `ceil(sum(runtime))` predicted it exactly (runtime sum 90.152 s, balance 2929 -> 2838), which also validates the billing rule at degree 3 and 833 variables, far outside its degree-2 anchors. Per-sample cost is 11.27 s against B3's ~0.6 s, an **18.8x** step
- **RESULT of that fit: AUPRC 0.8231, AUC-ROC 0.9547 [HW]**, against B1's 0.7351 mean (78 vars, 22 fits) and full-feature CatBoost's 0.8368 (10 seeds). The closest CVQBoost has come to the production bar on ULB, in exactly the configuration A12's ceiling foreclosed. CAVEAT: tie_fraction 0.9248, so its threshold-dependent figures are weak evidence while its ranking metrics are sound
- **The remaining TEN fits would cost ~910 s**, over the 900 s sprint ceiling on their own. A partial block (3 or 5 seeds) gives a mean with some spread at proportional cost. Team-lead decision; the anchor now exists so it can be made on measured numbers
- **Runner gap found the same day**: `run_hardware.py` writes its block artifact only at block completion, so a process that dies after a billed call leaves no `b2_hardware.json`. The Sprint 12 B2 fit did exactly that (WSL teardown on parent-shell exit, no traceback). Nothing was lost -- the raw response, predictions `.npz` and a full `results.json` row with `metered_seconds: 91.0` all persisted first -- but a per-fit artifact write would make that guarantee structural rather than lucky

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

**F38. Appendix to 3 pages AND proposal to 6 (~3h, RE-ESTIMATED) Priority 1 -- SUBMISSION BLOCKER**
- **RE-MEASURED 2026-09-10 after the internal review: proposal 8 of 6 pages, appendix 7 of 3. The cut is now roughly 1,290pt + 2,550pt = ~3,840pt.** The review's corrections (confound disclosure, solver-fidelity caveat, job-id provenance) each added text, all of it load-bearing. 689 -> 2,028 -> 3,197 -> ~3,840pt in one day. Every growth step has been a correction that made the submission more honest, which is the tension this card now embodies: the accurate version does not fit. Earlier readings follow.
- **RE-MEASURED 2026-09-10 after the B2 block landed: the appendix must shed ~1,907pt and the proposal ~1,290pt, TOTAL ~3,197pt. The proposal is now 8 of 6 pages and the appendix 6 of 3.** B2's paired result is the campaign's one clean positive for CVQBoost and earned space in both documents; the cut grew accordingly. This card has gone 689pt -> 2,028pt -> 3,197pt in one day. It is no longer an editing task and cannot be done by trimming restatement: at this size it means removing or relocating whole sections. The team lead has deferred it until after the agent review. Earlier readings follow as the record of how fast it grows.
- **MEASURED 2026-09-10 at Sprint 12 close-out, AFTER the B3 write-up: appendix needs a 1,469pt cut, proposal needs 559pt. TOTAL 2,028pt.** The appendix is now 6 of 3 pages, not 4 of 3: A22 added the hardware ladder to A.5 and a new B.3 section for the unrun B2 block. THIS CARD HAS TRIPLED SINCE SPRINT 11 AND IS NO LONGER A 3-HOUR CARD -- re-estimate it before committing to a sprint. The earlier reading follows, kept as the record of how fast this grows: appendix 250pt, proposal 439pt.** The proposal figure was 81pt at Sprint 10 planning and 21pt before that: page 7 now carries 467pt where it carried 70pt, because two correctness sprints added roughly two-thirds of a page. THIS IS NO LONGER A 45-MINUTE CARD
- **RE-MEASURE BEFORE CUTTING (Sprint 11 improvement 3).** Run `python scripts/page-fill-report.py` on both PDFs as the FIRST action of this card. Every recorded figure has been stale by the time the card ran: 76pt became 158pt became 229pt, because each correctness sprint adds text. Cutting against a stale number is how this card grew twice. The figure in this card is a record of what was once true, not an instruction
- Phase: Finalize (team lead 2026-09-07, accepting the overage for now: "can we leave it in the .md for now and we will address the overage later?")
- Platform: docs
- **State (2026-09-10, Sprint 12)**: appendix.pdf is **6 of 3** pages and proposal.pdf is 7 of 6. Pages 4, 5 and 6 of the appendix must vanish entirely against only 10pt of slack on pages 1-3. A judgment call is now unavoidable and belongs to the team lead: at this size the cut cannot come from restatement alone, so it will have to drop or relocate whole subsections. The most likely candidates are the A.6 phase-representation write-up and the new B.3, both of which are real evidence -- which is why this is a decision, not an edit. Prior state, for the record: appendix.pdf was 4 of 3 pages. The B.1 compound-falsification statement was added deliberately and is worth its space: section 2 of the preregistration names its own falsification test, two of its three conditions (H1b NULL at -0.0399, H3 slope -0.006) are now measured AGAINST the theory, and a submission silent on that reads as avoidance. It stays; something else pays for it
- **Already measured, so this does not need rediscovering**: as of 2026-09-07, 100pt spills onto page 4 against only 24pt of reclaimable slack. `python scripts/page-fill-report.py docs/paper/out/appendix.pdf` now reports "genuine LENGTH problem: about 76pt of content has to go". NOTE the verdict CHANGED during Sprint 8: it read FIX THE BREAK (121pt reclaimable) until the Copilot review correction added the untuned-arms qualification, which consumed the slack. Re-run the report before acting; do not trust this line
- **Candidate, already drafted and reverted once**: condensing Appendix C's artifact list to one sentence recovers about 3 lines and was measured to work. It was reverted only because the team lead chose to defer rather than cut under time pressure
- **Do NOT cut**: any figure, control, caveat, the A15/A17/A12 disclosures, or the compound-criterion statement. The 2026-09-06 pass already removed all restatement that was free to remove; what remains is evidence
- Acceptance: `python scripts/check-page-limits.py` reports OK 3 of 3, AND a numeric diff against the current render shows no figure lost (the 2026-09-06 method: extract all decimals from both PDFs and compare as sets)
- **Sprint 9 update (2026-09-07)**: the H6 arm (F4) lands an A.5/A.6 write-up in the same appendix, so the cut is larger than 76pt by whatever H6 needs. Sequence matters: write H6 FIRST, then cut once against the real total, rather than cutting to 3 pages and immediately breaking it again
- **Sprint 9 update (2026-09-08)**: the H6 write-up landed, so BOTH documents are now over. appendix 4 of 3, proposal 7 of 6. Both page-limit cases are xfail(strict) tied to this card, so each FAILS once its document is back under limit and the markers cannot outlive the fix
- Risk: an over-limit appendix is a submission-rules failure independent of content quality. Must not reach Sep 13 unresolved
- Depends on: nothing

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

**F37. Make the repository public (~45m) Priority 1 -- SUBMISSION BLOCKER**
- Phase: Finalize (team lead 2026-09-06: "It must be public upon submission ... if not already in the backlog item for final submission, please add making the repository public")
- Platform: repo/admin
- **Why it blocks**: `docs/paper/appendix.md` Appendix C cites `github.com/kimmeyh/hsbc-quantum-fraud-2026` for the pinned environment, both dataset checksums, the preregistration in full, the full reference list, and all 37 QCi job identifiers with their raw responses and Dirac-3 parameters. That citation is what lets the appendix meet its hard 3-page limit: the material was moved OUT of the PDF and INTO the repository. An anonymous request to the GitHub API returned 404 on 2026-09-06, so the repository is private today and the citation is currently a dead link
- **Must happen BEFORE the confidentiality scan is meaningful**: the repo root holds team-lead `0*` working files, which CLAUDE.md says to commit but never read. Those and anything else not intended for publication have to be resolved before the visibility flip, not after
- Steps: (1) run `scripts/confidentiality-scan.ps1` over the full history, not just the tip; (2) resolve every `0*` root working file with the team lead -- remove, or confirm publishable; (3) confirm the QCi job records and any hardware-response payloads carry no account or credential material; (4) confirm both dataset licences permit redistribution of derived checksums and results (ULB and IEEE-CIS raw data are NOT redistributed, only checksums); (5) flip visibility; (6) verify anonymously -- `curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/kimmeyh/hsbc-quantum-fraud-2026` must return 200, and the appendix URL must resolve in a logged-out browser
- **Acceptance**: an anonymous fetch of the repository URL succeeds AND `experiments/requirements.txt`, `experiments/PREREGISTRATION.md` and the results store are all reachable without authentication. Verified logged out, not from an authenticated session
- Risk: history rewriting after publication is not reliable, so anything published is published. The scan and the `0*` resolution are the whole cost of this card; the visibility flip itself is one click
- Depends on: nothing. Can run any time before Sep 13, and EARLIER is safer -- it is the one submission step that cannot be undone


(F3 IEEE-CIS: COMPLETED in Sprint 8, all four tasks, merged via PR #47; history in SPRINT_8_SUMMARY.md. Removed from candidates per convention.)

### Paper (Stages 4-6)

### Finalize (Stages 7-8)

(F35 interpretation-layer tests, F41 mechanism correction (A20), F42 review findings, F43 IEEE-CIS AUC-ROC, F44 figure resolution, F45 evidence guard, F46 QCi grant and ceiling probe (A21), F47 metered-call wrapper: ALL COMPLETED in Sprint 11, merged via PR #66 (main PR #70); history in SPRINT_11_SUMMARY.md. Removed from candidates per convention.)

**F48. Extend the escape hook to shell metacharacters (~45m) Priority 9**
- Phase: Finalize / tooling (Sprint 11 retrospective improvement 4, backlogged 2026-09-09)
- Platform: .claude/hooks
- `block-unraw-escape.ps1` catches Windows path escapes in non-raw PYTHON strings and has fired correctly several times. It does not catch SHELL metacharacters: a backtick or `$(...)` inside a quoted string passed to Bash is expanded by bash before Python ever sees it
- **Observed in Sprint 11**: backticks inside a Python string in a Bash command were expanded as command substitution, executing a source file as shell and silently deleting the backticked filenames from a master-plan line. The edit "succeeded" and the damage was only visible on inspection
- The fix is the same shape as the existing hook: detect backticks or `$(` inside a quoted span destined for Bash, and require the single-quoted heredoc form that suppresses expansion
- Lower priority than the submission blockers, and real: the failure mode is SILENT corruption of a file that was edited successfully, which is worse than a crash
- Depends on: nothing

**F49. Solver optimality certificate, and regenerate every proxy-dependent figure (~1.5h) Priority 1 -- CRITICAL PATH**
- Phase: Experiments / correctness
- Platform: `experiments/src/mechanism_controls.py`, `qubo_proxy.py`
- **THE DEFECT, verified 2026-09-10.** `solve_weighted` is FISTA with a RELATIVE-OBJECTIVE stopping test (`abs(prev-cur) <= 1e-10*(1+abs(prev))`, 5000-iteration cap). The frozen objective is nearly flat near its optimum, so that test fires while the WEIGHTS are still moving. Measured KKT residual on the cached pools: reduced-gradient spread across the support is **0.344 absolute, 4.6e-05 relative**, where a true optimum gives ~0. The stopping rule certifies the OBJECTIVE, not the SOLUTION
- **WHAT IT INVALIDATES.** Every figure derived from the proxy solve: the "uniform to seven decimal places" claim (that is where FISTA stopped, not where the optimum is), the solved-minus-uniform AP gain, the weight-cosine fidelity numbers for B1/G0b/B2/B3, and the objective-gap percentages. Our own recomputation reproduces the published +0.002224 EXACTLY, which is the point -- both our figure and our error come from the same under-converged solver. The external reviewer's more accurate solve gives +0.003023 on the same pools
- **WHY IT MATTERS BEYOND THE NUMBER.** The submission's central structural control is "the device and an exact classical solve of the identical Hamiltonian agree". If the classical comparator is not converged, that control is weaker than claimed, and A22's solver-fidelity result -- the strongest statement the campaign makes about the device -- rests on it
- Fix: add a projected-gradient / KKT residual stopping test to `solve_weighted`, keep the iteration cap as a backstop, record the achieved residual in every artifact so the certificate ships with the number. Then regenerate: `score_gates.py`, both hardware summaries, and every quoted fidelity figure
- Acceptance: KKT residual recorded and below a stated tolerance for every solve; all regenerated figures differ from the published ones by a documented amount; the full suite green; a test asserts the residual is present and within tolerance
- **NO QPU SECONDS.** Pure classical recomputation, ~15-30 min compute plus implementation
- **This card GATES F52 and F56** -- their text quotes figures this card changes. Do them after, not in parallel
- Depends on: nothing

**F50. Withdraw the convexity claim and correct the lambda=0 mechanism (~1h) Priority 2**
- Phase: Finalize / correctness
- Platform: docs/paper, experiments/PREREGISTRATION.md
- **TWO FALSE CLAIMS, both currently published, both verified false 2026-09-10**
- (a) `appendix.md:340` says B2 differs "in the polynomial degree of the objective itself" and `:352` says "B2's objective is not the convex problem whose optimum is unique". A24 carries the same. BOTH ARE WRONG. `weak_cls_schedule=3` selects which feature SUBSETS each weak learner reads; it does not change the Hamiltonian's order. A three-feature tree is still ONE variable emitting a single vector in {-1,+1}. Verified on B2's own pool: H holds only -1 and +1, and the smallest eigenvalue of the 833x833 J = HH^T + lambda*I is exactly the lambda term (340,470). The submitted job carries the same `normalized_qudit_hamiltonian_optimization` type as every other block
- (b) `appendix.md` A.4 says a penalty sweep "leaves it uniform even at zero penalty" and the proposal says "the penalty is not what makes the solution uniform". FALSE. At lambda=0 the objective at equal weights over the 82 perfect learners is **-170235.0000** against uniform's **-170234.9923**. Uniform is NOT the zero-penalty optimum; the solver returns it because it STARTS there and the objective is nearly flat. The sweep script records the objective after solving FROM uniform, not AT uniform
- **THIS CARD IS THE RECORD OF A SELF-INFLICTED DEFECT.** Claim (a) was written on 2026-09-10 in response to an internal review, published within hours, and is false. Correcting under time pressure reproduced the exact defect class the correction was meant to remove. That belongs in the amendment, not just the fix
- Also correct: "rank-one to numerical precision" is defensible only relatively. The Gram's second eigenvalue is 15.8 against a largest of 1.55e7 (ratio 1.0e-06); an ABSOLUTE 1e-4 threshold counts 9 eigenvalues, not 1. State the threshold used
- Acceptance: no surviving text asserts non-convexity or zero-penalty uniformity; the replacement mechanism statement matches the measured numbers; ONE amendment covers both, and says plainly that (a) was our own correction gone wrong
- Depends on: nothing (independent of F49; the convexity facts do not move)

**F51. Disclose the protocol-history deviations (~45m) Priority 3**
- Phase: Finalize / integrity
- Platform: docs/paper, experiments/PREREGISTRATION.md
- **TWO HISTORY CLAIMS CONTRADICTED BY OUR OWN FROZEN RECORD, verified against commit 95751b9**
- (a) `proposal.md:56` says of Loke et al. "We did not find this paper before freezing." The freeze names the SMU/OCBC configuration as **H1a**, with its learner families, its 0.80 reproduction target, and its exact protocol (70/30 split, train-only SMOTE, 10 seeds). The paper was known before the freeze; what is unrun is its source-protocol reproduction. Say that instead
- (b) G0 is stated in the freeze as: below 0.85 AUPRC "the pipeline is presumed defective and **everything halts**". G0 scored FAIL and work continued. Reporting the FAIL honestly preserves the score, but it does not satisfy the stopping rule. The continuation decision, its date and its authorization must be recorded as a DEVIATION under section 11
- **Do NOT rewrite the historical gate.** Section 11 forbids it and the honesty of the gate table is the submission's main asset. Add the deviation record beside it
- This is the finding most damaging to the "protocol is the contribution" claim if a judge finds it unaided, and the cheapest to defuse by disclosing it ourselves
- Acceptance: both statements corrected; the G0 continuation appears as an explicit dated deviation; the gate table still shows G0 FAIL
- Depends on: nothing

**F52. Repair the document contradictions (~1.5h) Priority 4**
- Phase: Finalize / correctness
- Platform: docs/paper
- Seven internal disagreements a reviewer finds in one read. All EDIT ONLY, all verified:
- **B1 variable count**: 78 in `proposal.md:62`, `appendix.md` A.6 and B.3's closing sentence; 91 in A.1 and B.3's table. B1 ran the FULL pair build at k=13 = **91**. 78 is the SEQUENTIAL count and belongs to the IEEE-CIS arm. The B2/B1 ratio is 833/91 = 9.2x, not 10.7x
- **Stale ULB claims**: `proposal.md` section 6 says the ULB blocks were not re-run above the ceiling; section 2 says our later hardware "runs above it at 136 variables". B2 ran at 833. Both contradict B.3
- **Subset orders**: section 2 says "every run reported here used one- and two-feature subsets"; B2 has 680 three-feature learners
- **The 949 limit**: QCi documents 949 for continuous quadratic jobs too, not only integer sum-of-levels (three QCi pages, one saying 954, one giving 477 binary). Our sentence is disprovable by a QCi-literate judge
- **Protocol naming**: A.5 says "GroupKFold-by-month"; the code does rolling-origin on 30-day TransactionDT buckets with fold sizes 85,302 / 86,524 / 8,111. The bracketed classical values are fold RANGES, not confidence intervals
- **Tie statistics**: `tie_fraction` (1 - distinct/N) and `mode_share` (mass at the modal score) are different quantities quoted interchangeably. B2 is 92.24% tie_fraction but 85.7% mode share with ZERO warning rows -- less degenerate than B1's 94.9%/824, not more. Define both; drop the "does not improve with scale" conclusion
- **Campaign subtotal**: `proposal.md` section 3's 37 fits / 163 s is a valid EARLIER subtotal against A.3's 61 / 1,141. Label it as such
- Acceptance: one regenerated manifest reconciles every count, cost and status across all three PDFs
- Depends on: **F49** (fidelity figures move)

**F53. Correct the prior-work and benchmark interpretations (~1h) Priority 5**
- Phase: Finalize / correctness
- Platform: docs/paper
- **Loke et al.**: their 0.8108 comes from a KNN-based ensemble under a different protocol (70/30, training-fold SMOTE); their classical comparator is CAD at 0.7423, not a tuned GBDT. Our "heterogeneous pool explains our result" reading is not what their experiment shows. It is a replication target, not an explanation
- **CVQBoost paper**: "accuracy was never the claim" is disprovable -- the paper claims competitive AUC and an accuracy edge under ADASYN, and it does compare classical solvers (Hexaly, SLSQP). Restate as runtime-emphasis with competitive AUC
- **Benchmark bands**: the cited IEEE-CIS 0.64-0.67 study uses STRATIFIED RANDOM splitting, so it is not a temporal benchmark and our rolling-origin result should not be measured against it. The ULB "near 0.80" is an inference, not a reported equivalent
- **The 0.2143 subtraction**: A.5 displays 0.861 vs 0.574 (a gap of 0.287) then quotes 0.2143, which is a different pair (0.7961 - 0.5818) from an artifact whose own verdict reads NOT FOR PUBLICATION. Do not present four numbers as one controlled comparison
- **Uncited figures**: the 0.85-0.88 band, AutoXGB 0.782, "near 0.80". One citation each with a URL
- **FG22/5**: attribute para 11.11's actual wording (monitoring for worse outcomes among customers sharing protected characteristics), not "identifies algorithmic bias as a source of harm"
- Acceptance: every external claim traces to a primary source at the strength stated
- Depends on: nothing

**F54. Provenance the reviewer can actually check (~1h) Priority 6**
- Phase: Finalize / reproducibility
- Platform: experiments/, docs/paper
- **11 of 168 results rows have `config_hash: null`, all B2** -- against a submission that claims every row carries one. B2 has no proxy twin at 833 variables, which is WHY the hash is null; that is a reason to state the exception, not to leave the claim unqualified
- **Raw hardware responses live under `experiments/results/pools/`, which `.gitignore` excludes.** Appendix C says they "are retained there". They are retained locally and ship with nobody. Either commit them (~1 MB) or scope the sentence
- `hw_dispersion.json` is derived from those untracked responses, so its A.3 figure cannot be recomputed by a reviewer even though the derived file is tracked
- **Pinned versions**: `requirements.txt` uses ranges for most numerical dependencies. State the exact resolved versions used for the reported runs
- Acceptance: no claim about the delivered package exceeds what a fresh clone contains; the distinction between locally retained and delivered evidence is explicit
- Depends on: nothing

**F55. Add the two missing rubric sections (~2h) Priority 7**
- Phase: Finalize / scoring
- Platform: docs/paper/proposal.md
- Guidelines 4.3 requires **"Feasibility and Resource Requirements"** and **"Validation Plan"** as components. The proposal has neither heading. Together those criteria carry **35% of the Phase 1 weight** (feasibility 20%, validation 15%) with nothing for a judge to score against
- Most of the content already exists, scattered: acceptance criteria in sections 5 and 6, the MDE, the temporal protocol, the router lift. This is largely reorganisation under the required headings
- Feasibility must state plainly that **Dirac-3 access is via QCi allocation OUTSIDE the challenge** -- the challenge provides Braket and Classiq, not QCi -- and give measured per-block seconds (B2 at 82 s/fit) against the remaining balance
- Validation Plan must state how the 0.0268 MDE was derived (paired SD, alpha, power, n=10), since the same number is used to judge three different comparisons, and what number defines Phase 2 success
- **Tension with F38**: both documents are already over the page limit, and this ADDS content. The two cards must be planned together
- Acceptance: both headings present with the guidelines' wording; every rubric component has text under a matching heading
- Depends on: F38 sequencing decision

**F56. Presentation and framing corrections (~1h) Priority 8**
- Phase: Finalize / presentation
- Platform: docs/paper
- **MDE used inconsistently**: H6 is dismissed as "not a finding" below MDE while B2's +0.0256 -- also below 0.0268 -- is called "unambiguous". Same threshold, opposite treatment. State that MDE describes design power, not a significance boundary
- **Only the favourable interval is unqualified**: H1b's across-seed interval carries a caveat that it measures split dispersion rather than sampling error. B2's does not. Apply the same caveat in the same words
- **H6 bias direction is reversed**: handicapping the classical twin biases the delta UPWARD, not negative, when that comparator sets the maximum
- **The tuned optimizer-gain SD is 0.0028**, not the published 0.0038 (which belongs to the untuned mixed-pool comparison)
- **"Selection bias is 0.0006"** is a sensitivity check, not a bias estimate; selection optimism remains unestimated
- **Latency**: "CVQBoost meets the budget trivially" is unmeasured. Scope "4 to 5 seconds" to the small configurations -- the campaign spans 4 to 92 s/fit
- **"Shadow-mode trial"** gives the challenger live decisions on days 31-60. Rename it staged, and scope "within three percentage points" to the 0.1% budget (at 0.5% it is 3.6 points)
- **"Quantum feature engineering"**: say at first mention that the phase block is a classically computed Fourier map applied to every arm
- **Undefined internal labels**: Sprint 4/5, F32, ADR-0013, "section 10", "item-4 controls", `dct`. Define once or remove
- Acceptance: no claim stronger than its evidence; a non-specialist can follow every term
- Depends on: F49 (some figures move)

**F57. The 200:1 resolution argument: replace a false mechanism with a real one (~1.5h) Priority 1 -- HIGHEST VALUE**
- Phase: Experiments / correctness
- Platform: `docs/paper/proposal.md` s3, `appendix.md` A.4 and B.3; one classical script
- **THE DEFECT, verified 2026-09-10.** The proposal says "our hardware-versus-proxy agreement is a confirmation of [convexity] rather than a discovery", and A.4 says that agreement "bounds any effect of Dirac-3's continuous-variable resolution: quantization coarse enough to drive the flat optimum could not reproduce it". The second is BACKWARDS and the first is uninformative. Measured on our own frozen Hamiltonian: diagonal 510,705, off-diagonals spanning **12.0**, linear terms spanning 16.0, against QCi's documented resolvable difference of max/200 = **2,553**. Every coefficient difference sits ~200x BELOW what the device can distinguish
- **PROOF, run before writing this card.** Quantising J and C at max/200 leaves the off-diagonal with **one distinct value** and the linear terms with one. The simplex minimiser of that quantised problem is uniform to **2e-15**. So hardware returning uniform is FORCED by the device's resolution, not evidence about solver fidelity, and the agreement carries no information on this pool
- **THE SAME LIMIT EXPLAINS B2, which we currently leave unexplained.** Sum constraint 1 over 833 learners gives a mean weight of 0.0012, below the documented expected resolution of 1/200 = 0.005. A diffuse optimum is not representable, so the device must return something sparser -- and the retained responses show exactly that: weights of 0.0009 to 0.0028 with exact zeros, against a cosine of 0.828. B2's "weak fidelity" is not the device failing; it is the device solving a sparsified version of the objective it was given
- **THIS IS THE STRONGEST ARGUMENT IN THE SUBMISSION FOR THE PHASE 2 DIRECTION**, and it is currently absent. A device that cannot represent diffuse weight vectors over hundreds of learners is a device whose native problem is SPARSE selection -- which is precisely the cardinality-constrained formulation section 6 proposes. The physics motivates the plan instead of the plan being an assertion
- Work: (1) rewrite the proposal s3 sentence and the A.4 bound; (2) add the resolution explanation to B.3; (3) a committed script that computes, per submitted Hamiltonian, the coefficient dynamic range and the resolvable difference, and per retained response the count of exact zeros and the smallest nonzero weight -- so both halves ship as evidence rather than as argument; (4) connect it to section 6
- Acceptance: no surviving text claims hardware agreement confirms anything on the frozen pool; B2's cosine has a stated cause; the dynamic-range and sparsity figures are stored and quoted from the artifact
- **NO QPU SECONDS.** ~1 hour of classical work against the 48 retained responses
- Depends on: nothing. Do FIRST -- it is the only card that adds evidence rather than removing error

**F58. Correct four claims a judge can disprove in under a minute (~1h) Priority 2**
- Phase: Finalize / correctness
- Platform: `docs/paper/proposal.md`, `docs/paper/appendix.md`
- **(a) THE FALSIFIER LIST IS WRONG, AND IT IS MY ERROR FROM F55.** New section 8 names the three conditions as "a null on the primary endpoint, a negative feature-ladder slope, and a representation change that does not move the delta", then says "Two have now fired. The third, segment specialization...". B.1 has it right: the preregistration commits H1b, H3 and **H5** (segment transfer). I substituted H6 (representation) for H5 in the list and then described the third as H5 anyway, so the paragraph contradicts itself AND B.1. Under its own list all three have fired, which would mean the theory is retired -- a materially different claim from the one we intend. Correct to: H1b and H3 have fired; H5 is unrun; H6 fired its own separate falsifier
- **(b) THE ARXIV TITLE IS WRONG.** We cite arXiv:2407.04512 as "Entropy Computing, A Paradigm for Optimization in Open Photonic Systems". The paper is "Entropy Computing: A Paradigm for Optimization in an Open Quantum System". The quoted phrase we use IS verbatim from its abstract, so only the title is wrong -- one click to disprove. Note the vendor's own title says "open quantum system", so we should take no position on that framing rather than implying the device is classical
- **(c) THE INTEGER CAP IS 474, NOT 477.** Section 7 says "capped near 477"; section 2 says "949 on one page, 954 on another". 954 cannot be sourced -- the user guide and beginner guide both give 949. 949 levels at two per binary is 474. Drop 954
- **(d) MODE SHARE DISAGREES WITH ITSELF.** A.3 quotes 95.1% over 814 distinct values (the gate report's MEDIAN, 0.951/814); B.3 quotes 94.9% over 824 (the MEAN). Same store, two statistics, presented as one fact. Pick the median, since that is what the score-health table reports, and use it in both places. Same for B2: 4,412 vs 4,413
- Acceptance: each claim traces to one source with one value; the falsifier list matches B.1 exactly
- Depends on: nothing

**F59. Retire the figures F49 left behind in section 3 (~45m) Priority 3**
- Phase: Finalize / correctness
- Platform: `docs/paper/proposal.md` section 3
- F49 certified the solver and moved four figures, and F52/F56 caught most consumers. Section 3 still carries three that did not get updated, all of which a reviewer cross-checking the appendix will find:
- **"FISTA, convergence tolerance 1e-10 on the relative objective"** -- that stopping rule is exactly what F49 replaced, and A.4/A.5 now say "KKT residual below 1e-9". The proposal describes the defective solver while the appendix describes the fixed one
- **"solved-minus-uniform +0.0022"** in the tuned-pool comparison -- the certified value is +0.0028, already corrected elsewhere in the same section
- **"Two seed-42 controls show this is optimization rather than tie-breaking (Appendix A.4)"** -- A.4 says only "Its two mechanism controls are seed 42 only" and describes neither, so the citation points at nothing. Either state both controls with their numbers in A.4, or drop the parenthetical
- Acceptance: no figure in section 3 disagrees with its appendix counterpart; every cross-reference resolves to text that exists
- Depends on: **F57** (which rewrites adjacent sentences in the same paragraph)

**F60. Say what the device was actually asked to do (~45m) Priority 4**
- Phase: Finalize / presentation
- Platform: `docs/paper/*.md`
- **THE COLLISION.** We use "schedule 2" and "schedule 3" throughout to mean the POOL's feature-subset order. Dirac-3 has a job parameter literally named `relaxation_schedule` taking values 1 to 4, and the vendor guide discusses "schedule 2 and schedule 3" runs. A Dirac-3-literate judge reads our text as the device parameter and concludes we changed the solver setting between blocks. We did not: every fit ran `relaxation_schedule: 2`, including B2. This is the conflation the internal review flagged and we only half-fixed
- Fix: rename to "order-2 pool" and "order-3 pool" wherever the pool is meant, and state the device parameters ONCE -- `relaxation_schedule`, `sum_constraint`, `num_samples`, `solution_precision` -- which we currently never report despite them being the whole specification of what the hardware was asked to solve
- **This matters beyond naming.** Section 7 already tells a reviewer the resolution limit is load-bearing (F57); `sum_constraint` is what sets it. Reporting the parameters is what lets someone check F57's argument
- Acceptance: no ambiguous "schedule" reference survives; the four device parameters appear once, in the feasibility or appendix A.3
- Depends on: F57 (which introduces the resolution argument those parameters support)

**F61. Tighten the shuffled-label control's language and criterion (~45m) Priority 5**
- Phase: Finalize / statistical presentation
- Platform: `docs/paper/appendix.md` A.5, `experiments/src/run_ieee.py`
- **THE REVIEWER'S DIAGNOSIS IS WRONG BUT THE WORDING IS LOOSE.** They simulated a RANDOM scorer, found our values 7 to 17 SD below its band, and concluded the control is defective. Our control does something different and correct: it shuffles TRAINING labels only, trains a real LightGBM, and evaluates against TRUE eval labels. A model fitted to shuffled labels learns noise that can anti-correlate out of sample, so scoring BELOW prevalence is expected and is the direction that indicates no leakage. Verified by reading `run_ieee.py:211-218`
- What is genuinely loose: (1) "collapses on every fold" implies convergence TO the base rate, when the values sit at or below it for a different and better reason; (2) the pass criterion is `shuf_ap < base * 2.0`, which would pass a fold leaking at 0.068 against a 0.034 base rate. A criterion that generous is not much of a tripwire
- Fix: restate what the control does and why below-prevalence is the expected direction; tighten the criterion or state explicitly what it does and does not exclude
- **Worth doing even though the reviewer was wrong**, because the next reader will make the same objection and the text should pre-empt it
- Acceptance: the control's design is stated in one sentence; the criterion's strength is stated honestly
- Depends on: nothing

**F62. Small precision fixes across the documents (~1h) Priority 6**
- Phase: Finalize / presentation
- Platform: `docs/paper/*.md`
- **Allocation arithmetic.** Section 7 says 3,000 granted, 1,141 spent, 1,961 remaining. The live endpoint confirms 1,961, but the subtraction does not work as printed because 1,141 is the CAMPAIGN total including 163 pre-grant free-tier seconds. The true grant reconciliation is 10 (probe) + **61 (the withdrawn B3 run)** + 62 + 906 = 1,039, leaving 1,961. State it that way. The 61 seconds of withdrawn work is real spend that produced no reported evidence, and saying so is more honest than a total that does not reconcile
- **Per-fit cost.** Section 5 says the solve "bills 4 to 5 metered device seconds per fit". True at 91 variables; A.3 says 4 to 92 across the campaign and B2 averaged 82. As written it understates Phase 2 cost in the section about deployment
- **FG22/5 selective quotation.** Our para 5.12 quote drops the source's qualifier "unless differences in outcome can be justified objectively". Restore it -- omitting a qualifier that weakens our own point is the kind of thing that costs credibility disproportionately
- **Team profile.** "the one we withdrew and re-ran" describes no gate -- what was withdrawn was the A23 hardware ladder. And "raw device responses retained" reads as all 61 when Appendix C says 48
- **A.6 versus A.1.** A.6 gives XGBoost 0.8328 and CatBoost 0.8185 on the baseline representation; A.1 gives 0.8296 and 0.8368 for the same models and seeds, with no explanation. If A.6's arms are untuned, say so and call that bar a floor
- **Loke citation.** Add the title; mark the page range unverified or drop it
- **AWS, not Braket.** The programme page promises AWS compute credits and Classiq tooling, not Amazon Braket by name
- Acceptance: every number reconciles from its own stated inputs; no quotation omits a qualifier that cuts against us
- Depends on: nothing

**F63. A key for the internal labels (~30m) Priority 7**
- Phase: Finalize / presentation
- Platform: `docs/paper/*.md`
- The documents cite "Sprint 4", "Sprint 5", "F32", "ADR-0013", "item-4 leakage controls", "section 10", and roughly thirty A-numbers, none defined. The guidelines ask that a non-specialist can follow the logic
- Fix: replace internal labels with plain descriptions where they appear once, and add a short key for the amendments actually cited (A11, A12, A13, A17, A20, A21, A22, A23, A26, A27, A28)
- **Sequencing note**: do this LAST among the content cards. Every card above adds or moves amendment references, so a key written earlier would be stale by the time the batch lands
- Acceptance: no undefined internal label survives; every cited amendment appears in the key
- Depends on: F57, F58, F59, F60, F61, F62 (all of which touch amendment references)










**F10. Verification, confidentiality scan, compliance walk, submission (~0.5 day) Priority 40**
- Phase: Finalize
- Platform: docs
- Every number vs results.json; repo-wide confidential-string scan (the fourierwall2 reference files were moved OUT of the repository at Sprint 10 F40, so the scan covers what remains rather than re-verifying them in place); requirements-matrix walk; public reproducibility repo; team-lead final PDF + portal submission, receipt archived
- Depends on: F8, F9

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

