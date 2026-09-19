# Sprint 16 Plan: Make the Guards Portable, and Close the Gate

**Sprint**: 16
**Branch**: `feature/20260916_Sprint_16`
**Dates**: 2026-09-16 onward
**Scope**: F79, F78, F80. DEFINED, not additive.
**Metered Dirac-3 seconds**: ZERO. No hardware in this sprint.

## Objective

Make this repository's protections work on the operating system its CI actually
runs, and close the gate that let Sprint 15 merge without a retrospective.

Both items are the same defect in different clothing: a control that exists,
that everyone believes is running, and that is not.

## Scope note

The team lead's selection IS the complete scope: F79, F78, F80.

**Removed from the backlog before planning**, at the team lead's instruction:
F77 (build the Evidence Based DB) and F75 (the 20-paper ADR checkpoint), both
moved to the `EvidenceBasedDB` repository. F76 (shared-vocabulary guard) was
raised as a question and confirmed for removal on the same grounds: its own card
names `EvidenceBasedDB` as its platform, it depended on F77, and the ADRs it
guards are frozen copies here whose live versions are ADR-0004 and ADR-0005
there.

## Audience-first statement (mandatory)

**F79 and F78's reader is a future session, including a future me, running on a
machine that is not this one.** Not a judge, not a reproducer.

That reader has no way to tell a guard that passed from a guard that never ran.
Both cards exist because this repository has now shipped the second kind five
times, and every single one was found by accident.

**F80's reader is a 13-year-old who has never seen the submission** -- the same
audience as Sprint 15, tested a different way.

## Capability pre-flight (run 2026-09-16 BEFORE estimating)

Per SPRINT_PLANNING.md, this inventories CODE and not only documents.

**F78:**
- 13 tracked `.ps1` files, 9 registered hook commands in `.claude/settings.json`
- **21 hardcoded `.venv\Scripts\python.exe` paths, not the 18 the card recorded.**
  The card counted markdown only. The true spread is 6 in the PowerShell guide,
  2 each in TESTING_STRATEGY and the master plan, 2 in `scripts/*.ps1`, and the
  rest in `experiments/src` docstrings
- CI is `ubuntu-latest` with `python-version: 3.12` already provisioned, so no
  new dependency is needed to run Python hooks there
- **SPIKE PASSED**: a Python process reading hook JSON from stdin and exiting 2
  behaves identically to the PowerShell version. The hook contract is portable;
  only the implementations are not

**F79:**
- `test_sprint_documents.py` already enforces the three-doc rule, and it did NOT
  fire for Sprint 15. The reason is deliberate and documented in the test: it
  **exempts the sprint in flight**, because a plan is written before its own
  retrospective can exist
- `verify-closeout-complete.ps1` checks the PREVIOUS sprint's retrospective, and
  only to infer whether a summary is missing. It never checks the current one
- **So the defect is not a missing check. It is an exemption that is never
  revoked.** The sprint in flight is exempt at plan time, correctly, and stays
  exempt through merge. That reframing is what this card builds against

**F80:**
- The original open prompt is recorded in FALSIFIER_RESULT.md
- **The document has changed in three commits since run 2**: the US English
  sweep and two rounds of CVQBoost rewrites, including a rewritten QBoost
  description. No falsifier has read the current text

## Tasks

### Task A: Revoke the three-doc exemption at merge time (F79) (~35m)

The test's current-sprint exemption is correct at plan time and wrong at merge
time. The fix is a second assertion that fires when the sprint is being closed,
not a change to the existing one.

Trigger: `sprint_status.json` reaching a close-out status, or the PR being
marked ready. The status field is preferred because it is already updated at
every phase transition and needs no GitHub call.

- **Acceptance (behavioral, not textual)**: with `SPRINT_15_RETROSPECTIVE.md`
  absent and status at a close-out value, the check FAILS and names the file.
  Restore it and the check passes. Proven by injection.
- **Acceptance**: the check does NOT fire at plan time, or it re-creates the
  Sprint 13 failure where the guard fired against a sprint's own plan.
- Model: Opus. Small but the failure mode is subtle.

### Task B: Extend verify-closeout-complete to the current sprint (F79) (~25m)

The hook already resolves sprint numbers and paths. It needs the current
sprint's retrospective added to what it refuses on.

- **Acceptance**: injection proves it refuses; the existing cases still pass.
- Depends on: Task A's decision about which signal marks close-out.

### Task C: Convert the four zero-OS-construct hooks (F78) (~90m)

`block-unraw-escape`, `block-shell-metachar-expansion`,
`block-carry-forward-stash`, `block-branch-from-develop`. These read stdin and
apply regexes, with no filesystem or environment calls, so they are the
pattern-setters.

**One at a time, each proven before the next.** A batch conversion that goes
quiet is unfalsifiable after the fact.

- **Acceptance per hook**: its existing test cases pass against the Python
  version, AND the injection that the PowerShell version blocked is still
  blocked. A converted hook that stops blocking is worse than no conversion.
- Model: Sonnet for the mechanical translation, Opus for the acceptance proof.

### Task D: A shared cross-OS helper (F78) (~60m)

One module the hooks and scripts import: path normalization, repo-root
resolution, interpreter discovery.

**Not thirteen scattered `if platform.system()` branches**, which is the outcome
the card explicitly names as the thing to avoid, because it drifts.

- **Acceptance**: the helper is imported by every converted hook; no converted
  file contains its own platform branch.

### Task E: Convert the remaining five hooks (F78) (~120m)

`block-frozen-history-rewrite`, `block-reactive-amendment`,
`block-unapproved-submission-edit`, `block-cross-repo-write`,
`verify-closeout-complete`. These touch the filesystem and git, so they exercise
the helper from Task D.

- **Acceptance**: same per-hook proof as Task C.

### Task F: Rewrite settings.json STRUCTURALLY (F78) (~45m)

Every registration changes from a `powershell -File` invocation to a `python`
one.

**This file is where two hooks silently died in Sprint 14, and where I
reproduced the same U+0008 bug in Sprint 15 while writing a guard against it.**
Written with `json.dump`, never by hand.

- **Acceptance**: every registered path resolves on disk; zero control
  characters; all nine hooks fire. `test_hook_registration.py` already asserts
  the first two and must stay green.

### Task G: Convert the four scripts (F78) (~90m)

`confidentiality-scan`, `render-all`, `render-pdf`, `update-sprint-status`.
`render-pdf` is the hard one: it shells out to pandoc and a PDF engine whose
discovery differs per OS.

- **Acceptance**: `confidentiality-scan` produces the same findings on the same
  input; `render-pdf` produces a PDF whose page count matches the current one.

### Task H: The 21 hardcoded interpreter paths (F78) (~45m)

Six in the PowerShell guide, two each in TESTING_STRATEGY and the master plan,
two in `scripts/`, the rest in `experiments/src` docstrings.

The venv bootstrap becomes **one documented command per OS**, referenced rather
than restated.

- **Acceptance**: `git grep` for the hardcoded path returns only the
  bootstrap doc. Every other file references it.

### Task I: Run CI on the converted hooks (F78) (~30m)

The point of the card. Until this runs, "it works on Linux" is a claim.

- **Acceptance**: the guard suite passes on `ubuntu-latest`, and at least one
  hook is proven to FIRE there, not merely to be present.

### Task J: Falsifier run 3, OPEN questions (F80) (~45m)

A fresh reader, one file, no repository access, asked the original open prompt
rather than questions aimed at known gaps.

**This is not a re-confirmation.** The document has changed in three commits
since run 2, including a rewritten QBoost description that no falsifier has ever
read.

- **Acceptance**: the run happens and its result is recorded INCLUDING a
  failure. New gaps are findings, not defects in the card.
- Model: a fresh general-purpose agent, deliberately not this session.

## Findings allowance (SPRINT_PLANNING.md, Sprint 13 improvement 2)

Tasks A, B, I and J are verification: they check whether something is true. Per
the rule, this plan carries a stated **30% findings allowance** on the
verification portion (135m of the 585m total), which is 40 minutes.

If the checks all pass, the allowance is returned and the sprint finishes early.
That is the good outcome and gets recorded as such.

## Premise falsifier (mandatory)

**Premise**: this repository's guards protect it.

**Already disproved five times**, and every one was found by accident rather
than by a control: two hooks registered at nonexistent paths, a changelog guard
whose threshold exceeded the lapse it existed to catch, a vacuous substring
assertion, a guard resolving one directory above the repo, and a U+0008 written
into the CHANGELOG entry describing the first failure.

**The check cannot merely confirm.** Task I runs the guards on Linux, where they
have never run, and requires one to FIRE rather than merely load. Task A's
injection deletes a real retrospective. Both can fail, and if F78's conversion
leaves a hook inert, Task I is what says so.

## Risks

- **A converted hook that stops blocking is worse than no conversion.** Mitigated
  by per-hook injection proof and by converting one at a time.
- **settings.json is the highest-risk file in the repository.** Two hooks died
  there silently in Sprint 14; I reproduced the bug in Sprint 15. Structural
  writes only, plus the existing registration test.
- **`render-pdf` may not be cleanly portable.** If pandoc discovery cannot be
  made to work on both, the honest outcome is a documented limitation, not a
  silent Windows-only script. Say so rather than claim success.
- **F80 may find new gaps**, which is the point. The findings allowance covers
  small fixes; anything large becomes a card rather than scope creep.

## Definition of Done

- All nine hooks run on Windows AND on `ubuntu-latest`, with at least one proven
  to fire on Linux
- Every hook conversion carries an injection proof, not a green run
- `settings.json` written structurally; every path resolves; zero control chars
- A missing retrospective FAILS at close-out, proven by deleting one
- The exemption still holds at plan time, so a sprint's own plan does not trip it
- Falsifier run 3 complete with its result recorded, including a failure
- Suite green; CHANGELOG updated; three-doc rule satisfied

## Out of scope

- Sprint 15's retrospective. It is outstanding and needs the team lead's three
  roles; it is not a Sprint 16 task.
- F81, a real 8th-grade reader. Team-lead owned and unscheduled.
- Any Dirac-3 run. Zero metered seconds.
- Anything in the `EvidenceBasedDB` repository. This repository's sessions do not
  write there.

## Estimate

10 tasks, 585 minutes, plus a 40 minute findings allowance: 625 minutes, or
10.4 hours. (Verified by summing the task estimates rather than asserting a
total; the draft said 590 and was wrong by 5.) F78 alone was carded at 8-12h and the pre-flight raised its true path
count from 18 to 21, so this sits at the upper half of that range.
