# Sprint 20 Plan: Make the Suite Readable Again

**Sprint**: 20 | **Branch**: `feature/20260930_Sprint_20`
**Planned**: 2026-10-02 | **Status**: awaiting team-lead approval
**Scope**: F97, F93, F98, F99 (the team lead's selection list, complete)
**Metered Dirac-3 seconds**: **0**. Nothing in this sprint touches the device.

## Objective

The test suite is red right now, in the planning window, and will be red at
every future planning window. Fix that, then clear the three smaller findings
the Sprint 19 reviews left: a hook whose timeout budget cannot cover its own
subprocess calls, correspondence with no recorded hash, and a SPECTRA block
described four different ways.

A consolidation sprint. No new capability, no metered spend, no document that
goes outside.

## Why this scope and not the valuable experiment

F90 is Priority 5 and the most valuable work available, and it is deliberately
NOT here. It would spend about 74% of the 1,681-second balance, so it deserves
a sprint where the allocation decision is the main event rather than one item
among four. F95 is promised to QCi and cheap, but it is metered with a
low-confidence extrapolated estimate, so it belongs with F90.

The case for fixing F97 first is that every one of those decisions gets
reviewed against a suite that currently cannot be trusted to be green, and
this repository has already paid for CI that was red on every commit of a
sprint. The lesson recorded then was that a red check nobody reads is worse
than no check.

## Tasks

### Task A: F97 -- five tests stop reading live sprint state (~40m)

**Pre-flight, done 2026-10-02 (code, not only docs).** Five files reference
`.claude/sprint_status.json`: `test_ci_status.py`, `test_phase3_artifacts.py`,
`test_sprint_documents.py`, `test_premature_turn_end.py`,
`test_status_footer.py`. **The last two are already safe** -- they build
fixtures under `tmp_path` and never read the live file -- so the pattern this
task needs already exists in the repository and should be copied rather than
invented.

The five failing tests, measured: `test_the_hook_allows_a_closeout_when_ci_is_green`,
`test_current_sprint_records_its_draft_pr`,
`test_current_sprint_records_its_task_issues`,
`test_plan_approval_is_recorded`, `test_sprint_status_points_at_a_real_sprint`.

- Each supplies a pinned status payload instead of reading the live file, or
  asserts only what holds in every phase
- `test_the_hook_allows_a_closeout_when_ci_is_green` is the awkward one: it
  asserts `rc == 0`, which requires EVERY other violation to be empty,
  including a live `gh pr list` network call. It should assert the absence of
  CI-specific strings in stderr rather than a clean exit
- **Acceptance**: the full suite is green in a Phase 1 planning window, proven
  by running it against the CURRENT `sprint_status.json` (sprint 20, no plan,
  no PR, `plan_approved: false`); and still green against a completed-sprint
  status, proven by running it against the Sprint 19 record. Both states, both
  green, same code
- **Model**: Lead Developer (top tier). Five tests across three files with a
  state-coupling pattern to get right, not a mechanical edit

### Task B: F93 -- one SPECTRA configuration, one cost (~60m)

**Pre-flight finding that changes this task, 2026-10-02.** The card's
acceptance says the hardware plan's Experiment 5 row should "either match the
survivor or be flagged for F92". Neither is possible now: the plan is FINAL
and its PDF was sent on 2026-09-25, and F92 is delivered. Read with `pypdf`,
the sent PDF commits to **"Experiment 5, segment transfer (30 fits), 270
seconds"** at 91 to 136 variables.

So the configuration choice is no longer open in the way the card assumed.
QCi has been told a number. That does not force the answer, but it makes any
other answer a thing we chose knowing what the vendor holds, which must be
recorded as such.

- Four records disagree: F2b (B4 at 15 fits, ~450 s), F90 (schedule 3, 833
  variables, ~1,236 s), F5 on HOLD (3 cells x 5 seeds), and the sent plan (30
  fits, 91-136 variables, 270 s)
- **This task does NOT pick the configuration.** The choice is the team lead's
  (Class 3). The task presents the four records side by side with what the
  sent plan commits, and records the decision
- **Acceptance**: a single configuration recorded with its reason; F2b and F5
  closed into the survivor; the survivor's cost labeled measured or
  extrapolated; and where the survivor differs from the sent plan's 270 s, a
  written note saying so and why, because that difference is now externally
  visible
- **Model**: Lead Developer (top tier). Reconciling four records against an
  external commitment is judgment, not editing
- **Depends on**: a team-lead decision mid-task. This task will stop and ask

### Task C: F98 -- the hook's timeout budget (~30m)

**Pre-flight, done 2026-10-02.** `settings.json` gives
`verify_closeout_complete.py` `"timeout": 20`; every other hook gets 15. Its
internal worst case: `gh pr list` 20 s + `gh issue list` 20 s + `gh auth
status` 60 s + `gh run list` 60 s = **160 s**. A single hanging `gh pr list`
exceeds the whole budget alone.

- **The ordering is the real defect.** The fail-OPEN issues check (`except
  Exception: pass`) runs BEFORE the deliberately fail-CLOSED CI check, so a
  hung `gh` kills the hook before the CI guard ever runs -- precisely when
  GitHub is slow, which is when the guard matters
- **Settle the unverified question first**: whether a killed Stop hook blocks
  or allows. A scratch Stop hook containing `time.sleep(25)` answers it in one
  run. The fix does not depend on the answer, but the severity does, and
  CLAUDE.md forbids stating what an external system does without opening it
- Bring the sum of internal timeouts under the budget (or raise the budget
  above the worst case), and move the fail-closed CI check ahead of the
  fail-open `gh` checks
- **Acceptance**: the kill semantics recorded with the evidence that settled
  them; the internal timeout sum under the configured budget, shown
  arithmetically; the CI check demonstrably reached when a `gh` call hangs,
  proven by stubbing a hang rather than by reasoning
- **Model**: Lead Developer (top tier). Hook ordering and fail-open/fail-closed
  asymmetry

### Task D: F99 -- a tracked hash for the sent correspondence (~20m)

**Pre-flight, done 2026-10-02.** Three artifacts exist to pin:
`Request and Results ... activities.htm`, its `_files` sidecar directory, and
`Phase 1 - QCi memo AS SENT 2026-09-25.md`. All are untracked by design
(`.gitignore:62`, private commercial correspondence), and no tracked file
records a hash for any of them.

Rescoped 2026-09-29: the team lead confirmed laptop backups cover recovery, so
the remaining gap is narrower -- a backup restores a lost file but does not
reveal that the copy on disk stopped matching what was sent.

- The ignore rule does NOT change
- A tracked file records sha256 per artifact; a guard fails when a named
  artifact is present and its hash has moved, and **skips visibly** when it is
  absent, never silently
- The `_files` directory needs a decision: hash each file, or a manifest hash
  over the sorted set. The second is one value and catches additions and
  deletions as well as edits
- **Acceptance**: hashes recorded in a tracked file; the guard proven RED by
  altering a byte of a SCRATCH COPY, never the record itself; proven to skip
  rather than fail where the files are absent, with the skip visible in output
- **Model**: Senior Developer (Sonnet) is adequate -- the pattern already
  exists in `test_published_artifacts.py` and can be followed
- **Risk, stated up front**: this task reads and hashes a sent artifact.
  CLAUDE.md forbids re-rendering or overwriting one to prove a tool works. Hash
  in place, mutate only copies

## Estimate

Derived from the card estimates recorded during refinement on 2026-09-30 and
2026-10-02. This plan reports the computed total; it does not originate one.

- A (F97): 40m
- B (F93): 60m
- C (F98): 30m
- D (F99): 20m
- **Card sum: 150m**

Allowances, by the pattern used in Sprint 19: 30% findings allowance on the
verification-heavy tasks (A and C, 70m) = **21m**.

- **Total: 171 minutes (2.9 hours)**

**Dependencies: none between tasks.** All four are independent, so any order
works and elapsed time equals the sum. Task B will pause for a team-lead
decision, so it should start early rather than last.

**Calibration caveat, stated rather than hidden.** The only recorded actuals
are Sprint 19's two documentation tasks: 2 minutes against 30 estimated, and 6
against 40. That ratio is NOT applied here, because those were edits to
wording already drafted and approved, which does not calibrate test and hook
work. These four estimates are uncalibrated in the same way Sprint 19's were,
and recording actuals at completion (IMP-1) is how that gets fixed.

## Risks

- **Task B stops for a decision.** If the team lead is unavailable, B stalls
  while A, C and D proceed. No other task depends on it
- **Task C's kill semantics may turn out to make the defect harmless.** If a
  killed Stop hook ALLOWS, the fail-open ordering is less severe than the card
  claims. The fix is still right, but the priority was argued from a premise
  that would then be wrong, and the card should say so
- **Task A could be done shallowly.** Pinning a payload so the five tests pass
  today is easy; making them pass in EVERY phase is the actual requirement, and
  the acceptance criterion is written to catch the shallow version by requiring
  both states green with the same code
- **No metered risk.** Zero device seconds, so Criterion H does not apply

## Out of scope, by the defined-scope rule

F90, F95, F94, F17, F6, F2b and every HOLD item. The selection list above is
the complete scope. F94, F17 and F6 were rewritten on 2026-10-02 and are
explicitly not in this sprint by the team lead's direction.
