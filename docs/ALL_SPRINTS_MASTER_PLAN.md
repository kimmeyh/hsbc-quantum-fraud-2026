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
| 11 | Sep 10-11 | **F41, F42, F43** (correctness) then **F37 -> F38** (submission blockers); F44/F45 if they fit | correctness BEFORE page size, team-lead sequencing |
| Finalize | Sep 12-13 | F10, **F40 (segment non-public material)** -> **F37 (repo public)** in that order, **F38 (page limits)** -- all SUBMISSION BLOCKERS; submit Sep 13 | no new evidence after Sep 12; never later than Sep 14 |

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

**F38. Appendix to 3 pages AND proposal to 6 (~45m) Priority 1 -- SUBMISSION BLOCKER**
- Phase: Finalize (team lead 2026-09-07, accepting the overage for now: "can we leave it in the .md for now and we will address the overage later?")
- Platform: docs
- **State**: appendix.pdf is 4 of 3 pages. The B.1 compound-falsification statement was added deliberately and is worth its space: section 2 of the preregistration names its own falsification test, two of its three conditions (H1b NULL at -0.0399, H3 slope -0.006) are now measured AGAINST the theory, and a submission silent on that reads as avoidance. It stays; something else pays for it
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

**F35. Interpretation-layer tests (~2h) Priority 2**
- Phase: Experiments/tooling (Sprint 7 retrospective, Claude category 14)
- Platform: N/A
- **Why**: across three sprints the defects that travelled furthest were claims about what a number MEANS, not errors in the number. Sprint 5 reported a weight vector "exactly uniform" at 0.000000 when it was 8.0e-08, and the gain it implied was tie-breaking. Sprint 6 presented k=13 [SIM] mechanism evidence and k=6 [HW] hardware evidence as one narrative. Sprint 7 differenced a k=6 arm against k=13 comparators and compared sweep VALIDATION AP against TEST AP. Every one was caught by reading; none by a test
- **Already partly built**: `comparators.py` (improvement 1) refuses a difference whose arms mismatch on k, protocol, schedule or dataset, and refuses validation against test. F35 extends that from the computation to the DOCUMENT
- **Design**: assert that every quantitative claim in docs/paper/*.md that quotes a difference names its comparator's configuration; that no figure tagged [HW] appears in a sentence whose mechanism evidence is [SIM] without the distinction stated; that a difference quoted below the A5 MDE carries directional language rather than win language; and that rounding in prose never asserts more precision than the stored value supports (the Sprint 5 "0.000000" case)
- **Honest limit**: some of this is genuinely hard to test mechanically and will end up as a checklist rather than an assertion. The parts that CAN be asserted are worth asserting, and the parts that cannot belong in STATISTICAL_REVIEW_CHECKLIST where a human walks them
- Depends on: nothing (comparators.py already landed)

(F3 IEEE-CIS: COMPLETED in Sprint 8, all four tasks, merged via PR #47; history in SPRINT_8_SUMMARY.md. Removed from candidates per convention.)

### Paper (Stages 4-6)

### Finalize (Stages 7-8)

**F42. Correctness findings needing verification or reruns (~4h) Priority 4**
- Phase: Finalize (Fable 5.1 adversarial review 2026-09-09; card #60)
- Platform: docs + experiments/src
- Needs EXTERNAL SOURCE CHECKS: the hardware description against QCi's own paper (coherent states with shot noise, not Fock states; R/~200 weight resolution; 23 dB dynamic-range limit); the vendor accuracy claim against CVQBoost Table 1 (reportedly ~0.19 AUC below XGBoost at ratios 0.01-0.02, which would STRENGTHEN our null); the Loke et al. citation and venue; Equality Act 2010 scope (Great Britain, not Northern Ireland)
- Needs CLASSICAL RUNS: lambda=0 FISTA spread from 20 random simplex starts; decomposition of the +0.0319 gain, which currently confounds three simultaneous changes and selected on seed 42 then evaluated including seed 42; per-GBDT H1b deficits rather than against the max only
- **F11 of that review is the SAME lambda=0 degeneracy F41 found from the other side.** Do them together or one redoes the other's work
- Depends on: nothing; overlaps F41 (#59)

**F43. Report IEEE-CIS AUC-ROC against HSBC's named benchmark (~1h) Priority 5**
- Phase: Finalize (team-lead direction 2026-09-09; card #61)
- Platform: docs, experiments/src
- HSBC's problem statement names AUC-ROC 0.9459 on IEEE-CIS as the classical bar. We report AUPRC only. Problem Relevance & Impact is 25%, the largest single rubric weight
- **The classical half needs NO rerun**: `run_ieee.py` already computes and stores `auc_roc` per fold and `ieee_classical.json` holds all nine -- LightGBM 0.9139, CatBoost 0.8941, XGBoost 0.8640. Reportable from stored evidence today. (An earlier analysis called this a full rerun; it had read summary keys instead of per-fold rows.) Only the CVQBoost and ladder arms lack the metric
- Required caveat: the Kaggle leaderboard test set differs from our rolling-origin folds, so 0.9139 is NOT directly comparable to 0.9459. State it rather than inviting the comparison
- Depends on: nothing. Page cost lands against F38, which runs last

**F45. Guard evidence artifacts against diagnostic scripts (~1h) Priority 7**
- Phase: Finalize (Sprint 10 process note, team-lead approved 2026-09-09)
- Platform: experiments/src, scripts
- **What happened**: the script written to REPRODUCE the review's crash finding injected a fake failed row into `results.json`, ran `score_gates.py`, and restored the store in a `finally`. The store was restored correctly. But `score_gates.py` had already written `gate_report.md` from the polluted data, so a 158-row artifact reporting a nonexistent failed fit was briefly committed. Caught on the next diff, `results.json` verified never contaminated, report regenerated from the clean store
- **Why it is worth a card**: the restore was careful and still insufficient, because the derived artifact outlived the source it was derived from. Any future diagnostic that perturbs the store has the same hole, and the next one may not be noticed in the same turn
- **Options to weigh at planning** (do not pre-commit): (a) a `--dry-run`/`--out` flag on `score_gates.py` so a diagnostic can render without touching the committed artifact; (b) a context manager in a test helper that snapshots and restores BOTH the store and every artifact derived from it; (c) a pre-commit check that `gate_report.md` regenerates byte-identically from `results.json`, which catches the whole class regardless of cause
- **(c) is the strongest**: it does not depend on remembering to use a helper, and it would have caught this before the commit rather than after. It is also the same shape as the F44 consistency tests, so the two may share machinery
- Acceptance: a deliberate perturbation of `results.json` followed by a commit attempt fails; the guard runs in CI as well as pre-commit
- Depends on: nothing. Pairs with F44

**F44. Evidence-vs-document consistency tests (~3h) Priority 6**
- Phase: Finalize (Sprint 10 retrospective improvement 2, team-lead approved 2026-09-09)
- Platform: experiments/src
- **Why**: every defect found this sprint was a document disagreeing with the evidence, and OUR SUITE CAUGHT NONE OF THEM. Two external reviewers found four in a day: the gate report under-reporting the campaign total (27/120 against the store's 37/163), a GAM twin cited "at 0.26" that appears in no artifact, B.1 listing H3 and H6 as NOT RUN while A.5/A.6 reported them measured, and the amendment count reading ten in two files against nineteen in a third
- **What**: assert that every figure quoted in proposal.md, appendix.md and team_profile.md resolves to a value in results.json or a named results artifact. Extract decimals from the documents, match against the store, fail on any figure with no source
- **The one that would have caught the worst case**: the gate report is generated FROM the store, so a test comparing report to store catches a generator bug. That specific test now exists (test_gate_report_totals.py, added with the fix); this card generalizes it from one artifact to every document
- **Sequencing**: must land AFTER F41 and F42, so the tests encode the CORRECTED values rather than freezing the current wrong ones into an assertion
- Acceptance: a deliberate edit changing any quoted figure fails a test; every figure currently in the three documents either resolves or is explicitly registered as prose
- Depends on: F41 (#59), F42 (#60)

**F41. Correct the pool-degeneracy mechanism and the depth claim (~2h) Priority 2 -- SUBMISSION BLOCKER**
- Phase: Finalize (GPT-6 Astra adversarial review, 2026-09-08; every claim reproduced against the saved pools before carding)
- Platform: docs + experiments/src
- **Finding 1 -- the published mechanism is WRONG.** The proposal says "at 0.17% prevalence a depth-limited tree predicts the negative class almost everywhere, so the pool carries almost no diversity". Reproduced across all ten saved seed pools: **80-84 of 91 learners classify EVERY training row correctly, and exactly ZERO predict all-negative.** The Gram degeneracy is real (off-diagonal 170,234.4 vs diagonal 170,235) but its cause is in-sample MEMORIZATION, not majority-class collapse. Right observation, wrong explanation
- **Finding 2 -- "depth-limited" is FALSE.** `qubo_proxy.py` passes `weak_cls_params=dict(weak_params or {})`, empty by default, so eqc-models builds `DecisionTreeClassifier(**{})` -> `max_depth=None`, unbounded. The phrase appears in 4 places including the proposal mechanism paragraph and the Loke comparison
- **Finding 3 -- the zero-penalty sentence overstates.** "The optimum stays uniform even at zero penalty" is too strong. An independent SLSQP solve at lambda=0 from uniform reaches L1 distance **0.1978** from uniform (the reviewer's 0.198 reproduces exactly). BUT the objective improves by only **4.5e-08 relative** (-1.7023499227e5 -> -1.7023500000e5) and test AUPRC moves +0.0052, well inside the 0.0268 MDE. The defensible claim is numerical degeneracy, not a uniform optimum
- **What does NOT change**: no gate score, no headline figure. H1b's -0.0399 null, the Gram entries, and the hardware-vs-proxy agreement are measurements and stand. What changes is the EXPLANATION attached to them
- **The Loke comparison gets STRONGER, not weaker**: their heterogeneous learners (KNN, LDA, logistic, XGBoost) fail on different transactions; ours memorize the same rows. That is a cleaner contrast than the depth story
- **Steps**: (1) register A20 recording the corrected mechanism with the reproduction; (2) fix "depth-limited" -> unbounded in all 4 places; (3) re-word the zero-penalty sentence to state the degeneracy numerically; (4) add a regression test asserting the perfect-classifier count per pool so this cannot drift silently
- **Class 1 AND Class 2**: amends the FROZEN preregistration and changes a published claim. Needs explicit team-lead approval before the documents are touched
- Acceptance: A20 registered; no "depth-limited" left in any document; the zero-penalty sentence states the 4.5e-08 relative degeneracy; a test asserts 80-84 of 91 perfect classifiers across the saved pools; full suite green
- Reproduction is already done and recorded here, so the card starts from evidence rather than re-deriving it
- Depends on: nothing. Should precede F10 (final verification walk)

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

