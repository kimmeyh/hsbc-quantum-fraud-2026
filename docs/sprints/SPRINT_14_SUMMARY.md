# Sprint 14 Summary

**Dates**: 2026-09-12 to 2026-09-14. **Branch**: `feature/20260912_Sprint_14`.
**PRs**: #94 (to develop), #95 (develop to main).

Sources: SPRINT_14_PLAN.md, SPRINT_14_RETROSPECTIVE.md, git history, PR #94 and
its two reviews, ADR-0014 and ADR-0015. Not the master plan.

## Scope, as delivered

Planned as **F68 to F72** plus four carried tooling cards (**F48, F65, F66,
F67**). All ten delivered. The Evidence Based DB design conversation that
followed F39 and F72 ran well past their carded scope and produced two accepted
ADRs and three research documents.

Zero metered seconds. The submission was already filed; this sprint made the
repository durable for the two audiences that arrive next -- a judge who may
open it during the review window, and us in mid-November with two months of
forgotten context.

## The finding that reordered the sprint

**Both Edit-matcher hooks had NEVER RUN.** `.claude/settings.json` registered
them as `...\\hooks\block-...`, where the single backslash before `b` is a JSON
backspace escape, so the path resolved to a file that does not exist. Claude
Code skips a missing hook silently.

Broken since the commit that created them. **The Sprint 13 retrospective
recorded one of them as working.** Every submission-document edit that sprint
was unguarded; the process held because the team lead approved each change in
conversation, not because anything enforced it.

It is also F48's defect class -- a silent escape corruption -- sitting in the
file that registers the guard against it, and F48 was in the same sprint.

## Every task found something its card did not anticipate

**F69 found two defects a fresh clone could see and this working tree could
not.** `requirements-lock.txt` was UNINSTALLABLE: a `python==3.12.10` line made
pip resolve `python` as a package, find none, and abort before installing
anything, so the documented reproduction command failed at step one for every
reader. And one test crashed with `FileNotFoundError` on a clean checkout where
its twenty data-dependent peers skipped cleanly, making the suite red for an
absent dataset rather than a defect.

**F70's own guard passed on the lapse it was written for.** The CHANGELOG had
stopped at 2026-09-04, eight days and seven sprints earlier. The currency guard
was written with a 14-day threshold and stayed GREEN on the injected eight-day
gap. Caught only by running the injection. Threshold now 5 days.

**F71 uncovered a dry run that overwrote committed evidence.** Verifying F65
replaced `b3_hardware.json` -- 12 real fits and 62 metered seconds of [HW]
evidence -- with three placeholder rows. `git checkout` restored it. The
"artifact untouched" check that missed it had run BEFORE the background job
finished: **a mistimed verification reads exactly like a passing one.**

**F48 took three iterations**, each correction driven by a false positive
against a real command. The final anchor requires python at a command position
rather than anywhere on the line.

**F67 measured three storage options** rather than arguing them: full pools
2.38 MB, needed arrays 1.42 MB, int8 signs 0.83 MB. The int8 fixture is lossless
because every H_tr holds only -1 and +1, asserted at build time rather than
assumed.

## What a stranger gets now

A fresh public clone runs the suite green. The pool-mechanism guard, previously
the suite's only skip, now RUNS against a committed fixture, so appendix A.4's
A20 claim is checked for anyone who clones rather than only on a machine that
happens to hold the pools.

Exact counts are deliberately not restated here; run the suite.

## The reviews found more than the sprint did

Two reviews on PR #94: Copilot (3 findings) and an adversarial Claude review
(17). All 20 addressed, none deferred.

**Copilot's first finding was live, not hypothetical.** `test_hook_registration.py`
left Windows backslashes in the path after substitution, which POSIX reads as
literal filename characters. Verified on real Linux: **0 of 7 hook paths
resolved before the fix, 7 of 7 after.** CI had been RED on four consecutive
commits and nobody had looked.

**The Claude review found a merge blocker that is the sharpest comment on this
sprint.** `test_a_dry_run_cannot_overwrite_the_evidence_file` was VACUOUS, and
the replacement written for it was vacuous too.

- Version 1 asserted a substring that occurs TWICE in the runner -- once in the
  real redirect, once in a cosmetic console-message line added in the same
  commit. The second satisfies it alone, so the redirect could be deleted
  entirely and the test stayed green.
- Version 2 called the JSON writer directly, testing the writer rather than the
  runner's decision about where to write.
- Version 3 asserts STRUCTURE via AST, including that the conditional's two
  branches must DIFFER. That clause kills the injection both earlier versions
  survived.

**A sprint whose theme was eliminating guards that cannot fail shipped a
flagship guard that could not fail, twice.** Neither was caught by the injection
claimed in its docstring.

The review's closing observation is the one worth carrying: findings 1, 2, 6 and
12 are all the same defect -- a value or pointer maintained in two places where
one moved. That is what the PR was written to close, and it recurred four times
inside the closing. The durable fix is structural: assert against structure
rather than substrings, and cite rather than restate.

## The design half

**ADR-0014 (Evidence Based DB) and ADR-0015 (reference library) both ACCEPTED**,
with early-innovation status and a 20-paper checkpoint. Neither authorises
implementation.

Four team-lead corrections changed the design materially, and each arrived
before much had been built on the wrong assumption:

- **The scope is not one project's glossary.** 151 records is use case ONE; the
  target is a domain knowledge base over QML, ML, QC and the major platforms.
  That weakened the "we are not Cyc" defence and moved authorship economics from
  a footnote to the central question.
- **Agent economics invalidate the collector's-fallacy arithmetic.** That
  literature measures human attention. The surviving scarce resource is
  team-lead adjudication, not drafting, so tiers mean adjudication depth.
- **`applicability` collapses into contexts** rather than carrying a parallel
  vocabulary that would drift.
- **A paper is a SOURCE OF ASSERTIONS, not a record.** Verified against the
  submission: four cited papers yielded at least eight separately checkable
  assertions, and `949` alone appears nine times in the preregistration.

**Primary-source research on Cyc corrected two things this project had recorded
as fact**: there are four composite truth values rather than five, and Cyc
carries NO numeric confidence on assertions. The confidence percentage was
therefore our own design, not inherited, and ADR-0015 replaced it with GRADE's
derived certainty plus named reasons.

Lenat's footnote 9 is the finding worth keeping: Cyc's general theorem prover
timed out on over a million consecutive queries and was switched off a decade
ago. Everything Cyc does is done by 1,100 specialised shortcuts.

## Numbers

| | |
|---|---|
| Tasks | 10 of 10 |
| Commits | 33 |
| Review findings | 20 (Copilot 3, Claude 17), all addressed |
| Metered seconds | 0; allocation unchanged at 1,961 of 3,000 |
| ADRs | 0014 and 0015, both Accepted, early innovation |
| Research documents | 3, each recording what could NOT be established |
| Guards that were vacuous | 2, both found by review rather than by us |

## What carries forward

- **F73**, the 8th-grade explanatory document, Priority 1 for the next sprint,
  with the outline folded in and the dataset licensing pre-flight already done
- **F75**, action the 20-paper ADR checkpoint, once EvidenceBasedDB holds ~20
- **F76**, guard the shared vocabulary between the two ADRs
- F64 as Phase 2 experiment 1, F65's siblings, F2b's B4 and B5
- The three open questions neither ADR settles: whether the glossary ships
  beyond internal use, who authors the definitions at what pace, and what the
  record looks like once 20 papers have tested it
