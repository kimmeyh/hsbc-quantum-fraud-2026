# Sprint 19 Summary: Send the QCi Package Clean

**Sprint**: 19 | **Dates**: 2026-09-23 to 2026-09-30
**Branch**: `feature/20260923_Sprint_19`
**PRs**: #141 to develop, #145 develop to main (both merged 2026-09-30)
**Cards**: F92 delivered. F96 closed as overtaken. F98, F99 registered.
**Metered Dirac-3 seconds**: **0**

Sources: `SPRINT_19_RETROSPECTIVE.md`, git history, PR #141. Written during
Sprint 20 planning per the three-doc rule; the master plan is not a source.

## The objective, and it was met

**The QCi package was sent 2026-09-25 at 12:23 PM.** Four documents went to
QCi: the memo, the hardware plan for Phase 2, the results against
preregistered criteria, and the eqc_models feedback, with the three SUBMITTED
PDFs attached exactly as filed on 2026-09-12.

The ask in it: **9,000 Dirac-3 seconds from now through the end of Phase 2**,
of which 1,681 are already held, so the additional request is 7,319 rounded up
to **7,500**. That is down from the 20,000 to 40,000 the original sponsorship
request estimated, because the classical proxy absorbs three of the six Phase 2
experiments and the null result narrowed the grid.

## What was delivered

**Task A** applied the six approved memo passages, plus four corrections
(M1-M4) that the Task D review surfaced.

**Task B** added six guards pinning the corrected passages, each proven RED
against the old text with the F89 injection helper before it was accepted.

**Task D** was the highest-value work in the sprint. A fresh-context reviewer
with no sight of the plan read all four package documents and reported
**fourteen disagreements** where a figure or claim appeared in two documents
and they differed. Each was verified against the documents and `results.json`
before it reached the team lead. Dispositions: **eight fixed** (M1-M4, P1, P3,
P4, P6), **four left with a reason** (M5, P2, P5, F1), **one answered without a
change** (G1), and three where no action was recommended and none taken.

The plan predicted zero or few disagreements. Fourteen arrived. That is the
premise falsifier working rather than a formality.

## The four package documents are now FINAL

Team lead, 2026-09-27: they will never change again.

That reclassified them mid-sprint. The memo is preserved as its `.htm` export
with the `_files` sidecar (exactly as sent) and as
`Phase 1 - QCi memo AS SENT 2026-09-25.md` for readability; the draft `.txt`
was deleted. Its **thirteen wording guards were retired** -- six from Task B,
the rest from the Task D extension -- because the file they read no longer
exists and a guard pinned to a superseded draft protects nothing.

The guards on `QCI_EQC_MODELS_FEEDBACK.md` and `HARDWARE_PLAN_PHASE_2.md` were
**kept** on different reasoning: both sources are present, so on frozen text
those guards are the only thing that would notice an accidental edit. A byte
pin may be the better successor, which is F99.

**Known and permanent**: the memo commits to a ~60 s schedule-4 check against
the remaining 1,681 seconds, and the attached hardware plan does not mention
it. Verified with `pypdf`: the sent PDF contains 1,681, 7,319, 7,500 and 9,000
and does not contain "schedule 4". Both documents are final, so this is
recorded rather than fixed.

## Tooling added

**`scripts/outlook_htm_to_md.py`** converts Word and Outlook HTML exports to
Markdown. It exists because the sent record arrived as a 101,345-character
export holding 16,542 characters of prose, undiffable and unreviewable.

It shipped with no tests and the PR reviews found five defects in it, all now
fixed and pinned by 16 tests: it read every source as UTF-8 with
`errors="replace"` (the real cp1252 export lost 269 characters -- smart
quotes, em dashes, an accented letter -- while `--check` passed because the
figure it watched was ASCII); it overwrote existing files silently; its Office
cleanup deleted any line whose whole content was `0`, `true` or `false`; and
`--check` tested substring presence rather than occurrence counts, and passed
when a figure was in neither source nor output.

## Defects in this sprint's own work

- **`check_ci_status.py` reported "CI is green" for a commit whose every job
  was SKIPPED.** The pass condition was the absence of failures, never the
  presence of a success, so no test result had to be read. Reachable: a
  path-filtered workflow completes exactly that way. This was in the script
  written to prevent that class, and its existing test paired `skipped` WITH a
  `success`, so it made the guard look covered.
- **A silent skip left in `test_qci_document_requirements.py`.** `_read()`
  called `pytest.skip` on a missing file. Measured: moving
  `HARDWARE_PLAN_PHASE_2.md` aside gave "8 passed, 22 skipped", exit 0 -- 22
  guards vanished and the suite reported success. The same commit removed this
  exact pattern from the sibling file with a written rationale and left it
  here. After the fix, the same experiment gives 22 failed.
- **Presence treated as correctness, three times**, including inside a test
  written to catch it: `test_no_force_flag_exists` grepped the source for
  `--force` and matched the comment saying there deliberately is none.
- **Two confident wrong answers from tools I built** rather than the ones the
  repository already had: a hand-rolled PDF extractor that reported "9,000
  ABSENT" from the document whose headline is the 9,000-second ask, and a cost
  estimate of ~2,000 seconds for work the backlog had already scoped at ~60.
  Both became CLAUDE.md entries (IMP-3, IMP-4).
- **A heredoc wrote a literal null byte** into a test file and corrupted it --
  the F82 escape class, in a file that was untracked so git could not restore
  it.
- **Task D's actual was not recorded.** It spanned an approval stop of several
  hours, so wall clock does not measure the work. IMP-1 shipped in Sprint 18
  to make actuals a completion-time habit and captured two of three tasks on
  its first real use.

## Improvements

Five proposed, two applied (IMP-3 and IMP-4, both CLAUDE.md entries), three
declined. The team lead's reason for declining is worth keeping: *"It worked
well and helped a great deal in getting to the final results. It is hard to
plan meandering needs and requirements and that is what this was."*

That corrected a claim of mine. I had scored three categories down for failing
to plan a document's lifecycle; the freeze happened when the work converged,
which is not a date anyone could have entered at planning time.

## Effort

Approved scope 105 minutes (A, B, D). Task C was not approved and became F96.

- A: 2 minutes (wording drafted and approved during planning)
- B: 6 minutes (includes a 4-minute suite run)
- D: **NOT RECORDED**, with the reason above

Substantial post-validation work -- the validation document, the guard
retirement, the converter, the BLUF compressions, and eleven review findings
-- was requested and unestimated, so the recorded effort understates the
sprint.

## Next sprint readiness

- **F95 unblocked**: its hold was "until the QCi memo is sent". The sent memo
  commits to it, so it is promised work now. Four fits at schedule 4, ~60 s
  extrapolated, against the 1,681 balance.
- **F90**: schedule 3 at 833 variables, ~1,236 s, which would spend about 74%
  of the remaining balance and needs its own allocation decision.
- **F98**: the close-out hook's 20 s budget against up to 160 s of internal
  `gh` timeouts, with the fail-open check running before the fail-closed one.
- **F99**: no tracked hash for the sent correspondence. Rescoped 2026-09-29
  when the team lead confirmed backups cover recovery; the detection gap
  stands.

Allocation: **1,681 seconds remaining** of the 3,000 granted 2026-09-09.
