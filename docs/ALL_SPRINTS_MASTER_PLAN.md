# All Sprints Master Plan

Adapted 2026-08-30 from spamfilter-multi's ALL_SPRINTS_MASTER_PLAN.md structure. This document is IN THE REPOSITORY and persists across conversations. Read it before every sprint (Phase 1/2), update it after every sprint (Phase 7.7/8.2).

## Maintenance Guide

- **After each sprint (Phase 7.7 / 8.2)**: update "Last Completed Sprint"; add the sprint's row to "Past Sprint Summary" once its SUMMARY doc exists; prune shipped items from "Next Sprint Candidates"; add retro Category-14 items with new F#s.
- **During Sprint N+1 planning (Phase 3.2.1)**: create `docs/sprints/SPRINT_N_SUMMARY.md` for the just-finished sprint and link it here.
- **IDs**: F# for all features/process/tech-debt items; next available number; never reuse.
- **Estimates**: minutes/hours from recorded actuals; `[no-history]` where uncalibrated.
- `CHECKLIST-Phase2-pre.md` is the LIVE deliverable ledger; this document is the sprint-scoping view over it. Keep them consistent; the checklist wins on deliverable truth, this file wins on sprint sequencing. (`CHECKLIST-Phase1.md` is the CLOSED Phase 1 record and is never updated; `CHECKLIST-Phase2.md` is dormant until selection. The repo-root `CHECKLIST.md` was split into those three on 2026-09-12 and no longer exists.)

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

## Last Completed Sprint

**Sprint 14: Make the Record Durable** (Sep 12-14, 2026; PR #94 to develop, PR
#95 to main). Delivered **F68-F72** plus the four carried tooling cards **F48,
F65, F66, F67**, and the Evidence Based DB design that followed them. Zero
metered seconds.

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

**The finding that reordered the sprint**: BOTH Edit-matcher hooks had NEVER
RUN. A single backslash before `block-` in `.claude/settings.json` is a JSON
backspace escape, so the path resolved to a file that does not exist and Claude
Code skipped it silently, since the commit that created them. The Sprint 13
retrospective had recorded one of them as working. Every submission-document
edit that sprint was unguarded.

**Every task found something its card did not anticipate.**
`requirements-lock.txt` was UNINSTALLABLE, so the documented reproduction
command failed at step one for every reader. A test crashed on a clean checkout
where twenty peers skipped. A dry run OVERWROTE the committed b3_hardware.json
during verification, and the check that missed it had run before the background
job finished: a mistimed verification reads exactly like a passing one.

**The guard that failed its own test**: the CHANGELOG currency guard was written
with a 14-day threshold and PASSED on the eight-day lapse it existed to catch.

**Two reviews found 20 defects, all addressed.** Copilot's first was LIVE, not
hypothetical: Windows backslashes in resolved paths meant 0 of 7 hooks resolved
on POSIX, and CI had been red on four consecutive commits unnoticed. The
adversarial Claude review found a merge blocker that is the sharpest comment on
the sprint: the dry-run guard was VACUOUS and its replacement was vacuous too,
both defeated by the same injection. **A sprint whose theme was eliminating
guards that cannot fail shipped a flagship guard that could not fail, twice.**

**The design half**: ADR-0014 and ADR-0015 both ACCEPTED with early-innovation
status and a 20-paper checkpoint; neither authorises implementation. Four
team-lead corrections changed the design materially -- the scope is a domain
knowledge base rather than one project's glossary, agent economics invalidate
the collector's-fallacy arithmetic, `applicability` collapses into contexts, and
a paper is a SOURCE OF ASSERTIONS rather than a record. Primary-source research
corrected two things this project had recorded as fact about Cyc.

Retro: docs/sprints/SPRINT_14_RETROSPECTIVE.md (Very Good across all rated
categories; all six improvements applied).

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
- Acceptance: the cell runs on the same seeds and protocol as its two neighbors; B.3 states the decomposition instead of declining it; if the result changes what the +0.0256 is attributable to, that is an amendment
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


(F65 per-fit artifact write: COMPLETED in Sprint 14. Also fixed a dry run that
overwrote committed evidence. Removed from candidates per convention.)

(F77 build the Evidence Based DB, F75 the 20-paper ADR checkpoint, and F76 the
shared-vocabulary guard: MOVED to the `kimmeyh/EvidenceBasedDB` repository
2026-09-16 by the team lead. All three are that repository's work, not this
one's. F77 builds its store; F75 reviews its schema against its own papers; F76
guards ITS ADR-0004 and ADR-0005, whose live copies live there. The copies here
are frozen and carry a banner saying so. Tracked in that repository's own
backlog. Removed from candidates per convention.)

**F78. Convert every PowerShell script to Python so the repository is OS agnostic (~8-12h) Priority 8**
- Phase: Finalize / tooling (team lead, 2026-09-15)
- Platform: `.claude/hooks` (9 files), `scripts/` (4 files), plus 18 hardcoded interpreter paths across 12 tracked files
- **`.venv` is generated, so it is not converted -- but it IS recreated per OS, and that is a scope item, not a footnote** (team lead, 2026-09-15, from experience). A Windows venv has `Scripts/activate.ps1` and `Scripts/python.exe`; a Linux one has `bin/activate` and `bin/python`. They are not interchangeable, so anyone moving to WSL rebuilds it. `docs/WINDOWS_POWERSHELL_GUIDE.md` already states the Windows venv is unusable from Linux, so the knowledge exists and the tooling ignores it
- **What it is**: replace all 13 tracked `.ps1` files with Python that runs unmodified on Windows 11 AND Linux (current WSL is sufficient). Most Python is already portable; the exceptions are real and are the whole point of the card -- path separators, line endings, `%USERPROFILE%` against `$HOME`, executable discovery, and subprocess invocation
- **Each script must DETERMINE the OS and handle it**, rather than assuming. The team lead's preferred shape: find an existing package that does this, or write one shared cross-OS helper module that every script imports. A per-script `if platform.system()` scattered thirteen times is the outcome to avoid, because it drifts
- **Measured scope, 2026-09-15**: about 1,260 lines across the 13. Four hooks (`block-unraw-escape`, `block-shell-metachar-expansion`, `block-carry-forward-stash`, `block-branch-from-develop`) contain ZERO OS-specific constructs -- they read stdin and apply regexes -- so they are near-mechanical ports and should go first as the pattern-setters. `scripts/render-pdf.ps1` has 12 and is the hard one; it shells out to pandoc and a PDF engine, whose discovery differs per OS
- **The registration is as important as the code.** `.claude/settings.json` invokes each hook through `powershell -NoProfile -ExecutionPolicy Bypass -File`. Every entry has to change to a `python` invocation, and that file is exactly where two hooks were silently killed by a lone backslash-b JSON escape. Rewrite it STRUCTURALLY with `json.dump`, never by hand, and assert afterwards that every registered path resolves and holds no control character
- **Acceptance is behavioural, not textual**: each converted hook keeps its own test cases and still BLOCKS what it blocked and ALLOWS what it allowed, proven by running the cases through the new hook on both operating systems. A conversion that leaves a guard inert is worse than no conversion, and this repository has shipped inert guards three times
- **Do not convert the tests' invocation path and the hooks in the same commit.** Convert one hook, prove it fires, then the next; a batch conversion that goes quiet is unfalsifiable after the fact
- **The hardcoded interpreter is the widest part of the card.** `git grep` finds
  `.venv\Scripts\python.exe` in 18 places across 12 tracked files: 8 in
  `experiments/src` docstrings ("Run: ..."), 2 in `scripts/`, 2 in `docs/`
  including `TESTING_STRATEGY.md` and the PowerShell guide. Every one is a
  Windows-only instruction a Linux reader cannot follow. These are cheap to fix
  and easy to miss precisely because most are comments rather than code
- **The venv bootstrap should be one documented command per OS**, not prose
  scattered through a guide. Whatever replaces it states how to create the venv
  and how to invoke the interpreter on each OS, and `README.md` and
  `TESTING_STRATEGY.md` reference that one place rather than restating a path
- **Why it is worth doing**: the repository currently cannot run its own guards on Linux. CI runs `ubuntu-latest`, so every hook is Windows-only protection today, and a contributor or agent on Linux gets none of it
- Depends on: nothing. Best done when no other sprint is touching `.claude/`

(F67 pool-mechanism guard: COMPLETED in Sprint 14. Runs on a fresh clone against a
committed 0.83 MB int8 fixture, chosen from three measured options. Removed from
candidates per convention.)

**F79. Gate the retrospective so a sprint cannot merge without one (~1h) Priority 3**
- Phase: Finalize / process (Sprint 15 retrospective category 13, 2026-09-16)
- Platform: `.claude/hooks`, `experiments/src`
- **Sprint 15 merged to develop AND to main with no `SPRINT_15_RETROSPECTIVE.md`.** Phase 7 is an exit gate in the workflow and the three-doc rule is unconditional, and neither stopped it. I marked the PR ready while naming the retrospective as outstanding, which was not enough
- `test_sprint_documents.py` already enforces the three-doc rule, so the gap is not the test: it is that nothing checks it at the moment a PR is marked ready. The check has to run where the decision is made
- Options: extend `verify-closeout-complete` to refuse when the current sprint's retrospective is absent, or add a pre-`gh pr ready` check. The first is preferred because the hook already exists and already runs at close-out
- **Acceptance is behavioural**: with the retrospective deleted, the gate must FIRE. Proven by injection, not by a green run
- Value: this is the second consecutive sprint where a Phase 7 deliverable was missed (Sprint 14 left `CHECKLIST-Phase2-pre.md` unreconciled). A phase that depends on remembering is the class this workflow keeps replacing with a step
- Depends on: nothing

**F80. Re-run the explainer falsifier with OPEN questions (~1h) Priority 9**
- Phase: Finalize / verification (Sprint 15 retrospective category 13, 2026-09-16)
- Platform: `docs/explainer/`
- Run 2 of the Sprint 15 falsifier asked questions aimed at exactly where run 1 tripped. That confirms the four fixes landed; it CANNOT find gaps elsewhere, and the record says so explicitly
- This card runs a third reader with the original open prompt against the revised document, so the revision is tested the way the original was
- **The honest limit that no re-run fixes**: every reader so far has been a language model. That is a fresh-context check, not an audience test. Where a real 13-year-old stumbles is unknown, and that belongs to F81 rather than here
- Depends on: nothing

**F81. Put the explainer in front of a real 8th-grade reader (~unknown) Priority 11**
- Phase: Finalize / verification (Sprint 15 retrospective category 14, 2026-09-16)
- Platform: external, team-lead owned
- Both falsifier runs used language models with no repository context. They found six real gaps, so the mechanism works, but a model reading at grade 8 is not a person reading at grade 8
- The card's own falsifier names the test: someone who has not read the submission explains back what CVQBoost is and why the result is a null
- **Effort is unknown because it depends on finding a reader**, which is the team lead's to arrange, not mine. Sized as unknown rather than guessed
- Value: the document's entire purpose is an audience it has never actually met
- Depends on: nothing, but best after F80

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
- **Measured queue behavior, 2026-09-09**: the F46 probe submitted at 14:33 local was still queued 52 minutes later, having spent ~97 CPU-seconds on its local pool build. Flat CPU against growing wall clock is the signature of queue wait, not computation. The team lead reports the queue is ALMOST ALWAYS EMPTY AFTER 5PM LOCAL, so wall-clock cost is a function of WHEN a block runs, not what it computes
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

