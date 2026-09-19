# Sprint 16 Summary: Make the Guards Portable, and Close the Gate

**Sprint**: 16
**Branch**: `feature/20260916_Sprint_16`
**PR**: #120 to develop
**Dates**: 2026-09-16 to 2026-09-17
**Scope**: F79, F78, F80
**Metered Dirac-3 seconds**: ZERO

## What shipped

**F79, the retrospective gate.** A sprint can no longer merge without its
retrospective, enforced from two directions: a suite-time test and the close-out
hook.

**F78, the PowerShell-to-Python conversion.** All nine hooks and all four
scripts, plus a shared cross-OS helper, plus a CI step that proves a guard fires
on Linux.

**F80, falsifier run 3.** Recorded in `docs/explainer/FALSIFIER_RESULT.md`.

## The finding that reframed F79

The card said the defect was a missing check. It was not.

`test_sprint_documents.py` already enforced the three-doc rule and
**deliberately exempted the sprint in flight**, because a plan exists before its
own retrospective can. An earlier version of that guard fired against Sprint
13's own plan, which is why the exemption is there.

So the defect was an exemption that was never **revoked**. And it was worse than
that: the exemption followed `sprint_status.json`, a hand-rolled field, so
writing the Sprint 16 plan before rolling it made **Sprint 16** look completed.
The guard demanded documents that cannot exist while the real gap, Sprint 15's
retrospective, stayed hidden behind the stale exemption. The field was wrong in
both directions at once.

Completion is now judged on evidence: a sprint is complete when a later sprint
has a plan. Nobody can forget to update that, because the next sprint cannot
start without it.

**The close-out hook had a circular bug.** Its check read
`if (retrospective exists) and (summary missing)`. It demanded the summary, and
only when the retrospective was already present, so a missing retrospective
triggered nothing. Sprint 15 merged twice straight past it.

## The measured case for F78

CI runs `ubuntu-latest`. The hooks were PowerShell. **None of them had ever
executed where CI runs**, so every guard in this repository was Windows-only
protection while the build that gates merges ran Linux.

The conversion is proven by 143 parity cases, each run against **both**
implementations and required to agree. Agreement between two implementations is
stronger than either matching a written expectation, and while both exist a
drift shows up as a disagreement rather than a stale test.

CI now asserts both directions on Linux: `git stash push` must exit 2, and
`git stash list` must exit 0. A guard that does not fire is indistinguishable
from no guard; a guard that blocks reads gets switched off.

## A real bug found in a submission-gating control

`scripts/confidentiality-scan.ps1` reported **"0 HIGH, 0 REVIEW" on any
single-line file**. `Get-Content` returns a String rather than an array for a
one-line file, so `$lines[0]` yielded the first *character* and every rule
matched nothing. A file containing an employer name or an API token scanned
clean.

The submission was not affected, verified rather than assumed: its documents are
104, 102 and 216 lines, and multi-line reads return arrays. The bug bites only
single-line files, which is the shape a cover note takes.

Team lead ruled the PowerShell will not be fixed, since it is retired. The
Python cannot reproduce it and carries regression cases anyway.

## The turn-ending failures, and what was done about them

Three times in two sprints a turn ended announcing work that had not started.
The rule against it is fifteen sprints old and existed in three places.

The team lead noted that `sprint-auto-advance.ps1` exists in spamfilter-multi
and had been requested here. Porting it was clearly right; writing my own was
not. **But its four commitment patterns matched none of the three real
failures** -- they require "I'll continue" or "proceeding to", and a bare
participle opening slips through all four. Verified by running its regexes
against the exact strings before porting. A participle pattern was added.

## Errors worth recording

- **An injection proof that proved nothing.** Two attempts reported 77 passed on
  a hook I believed was broken; the replace target never matched, so nothing was
  injected. Caught only because attempt 3 added an abort-if-absent assertion.
- **A baseline that looked like a live bug.** The cross-repo guard appeared not
  to block `cd <sibling> && git push`. Three theories tested and discarded
  before finding the cause: my payloads omitted `tool_name`, so no branch ran.
- **A test case that contradicted its own name.** "promise before approval" ran
  with `plan_approved` hardcoded true, so it passed for the wrong reason.
- **A fixture that was itself a secret.** The pre-commit hook blocked a test
  containing a literal token pattern. Correct: a fixture imitating a credential
  is indistinguishable from one.

Each was caught by a check rather than by inspection, and three of the four were
defects in verification rather than in the thing verified.

## Guards added

`test_hook_parity.py`, `test_hooklib.py`, `test_premature_turn_end.py`,
`test_interpreter_paths.py`, `test_confidentiality_scan.py`,
`test_render_scripts.py`. Every one verified by injection.

## Numbers

Counts are deliberately not restated here. Run the suite; `CHANGELOG.md` carries
the per-change record and PR #120 the commit list.

## Carried forward

- F81 (a real 8th-grade reader for the explainer) remains team-lead owned.
- The `.ps1` files are retired but not deleted. Removing them is a separate
  decision, and the parity tests skip rather than fail once they are gone.
