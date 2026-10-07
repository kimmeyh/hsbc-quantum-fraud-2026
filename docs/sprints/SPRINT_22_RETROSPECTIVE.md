# Sprint 22 Retrospective

**Sprint**: 22, Separate the Phases, Then Look for Better Numbers
**Date**: 2026-10-07
**Scope delivered**: F123, IMP-3, F124, F17, F20, F125 -- all six
**Effort**: 256 minutes recorded against 980 estimated, plus 45 minutes of
Manual Validation work (`.claude/sprint_status.json`, `task_actuals`)
**Metered Dirac-3 seconds**: **0**. Balance 1,022 s throughout.

## Scoring, both roles

The team lead scored every category **Very Good**. Claude scored four
lower. Where the two disagree both are recorded, and the improvements are
built from the lower score.

| Category | Team lead | Claude |
|---|---|---|
| Effective while as efficient as reasonably possible | Very Good | Good |
| Testing approach | Very Good | Good |
| Effort accuracy | Very Good | **Needs Improvement** |
| Planning quality | Very Good | **Needs Improvement** |
| Model assignments | Very Good | Very Good |
| Communication | Very Good | Good |
| Requirements clarity | Very Good | Good |
| Documentation | Very Good | Good |
| Process issues | Very Good | **Needs Improvement** |
| Risk management | Very Good | Good |
| Next sprint readiness | Very Good | Good |
| Architecture maintenance | Very Good | Good |
| Assigned coding agents quality | Very Good | Good |

Team lead: "Manual Validation complete"; minor function updates "none";
backlog additions "none"; questions before ending the sprint "none".

## Sprint 22 Retrospective Feedback

The team lead gave combined Product Owner, Scrum Master and Lead Developer
feedback, recorded verbatim under each of the three roles.

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. All six tasks done with zero
  metered seconds; F124's list was approved as written. Rework: the
  phase-separation recommendation (`PHASE_SEPARATION.md` section 4.1) was
  superseded across three validation rounds by a separate repository. The
  analysis behind 4.1 never checked what the filed documents point at.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every new guard was proven red.
  `test_requirements_complete.py` caught an undeclared import during
  validation. The sample-storage defect was found by testing, not by a
  reviewer. Against it: commit 63bc375 said the hook tests passed when one
  had failed (corrected in c62248a).

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. 256 minutes against
  980 estimated, 3.8 times over in total. One task ran the other way: F125
  took 45 minutes against 20. `docs/VELOCITY_LOG.md`, which exists to calibrate estimates, stops at
  Sprint 14.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. Three cards carried
  claims nobody checked at refinement: F17's acceptance test named B2 pools
  that were never stored; F124 named `batched_qboost_enabled`, which the
  installed eqc_models 0.21.0 does not have; F125's diagnosis was
  incomplete (a correct count alone still blocked).

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Main-loop work on the main
  model, the security review as a background agent, and the advisor before
  each approach.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every validation item was listed
  on screen. But D2, D4 and D5 were asked beside D3 although their options
  depended on D3's answer, so D2 was answered on a premise that changed one
  round later.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The full F123 requirement (the
  filed, public link shows what was filed; Phase 2 completely separate)
  surfaced only at Manual Validation.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every result has its document and
  evidence file. CHANGELOG entries were written at the end, not in each
  commit: the policy F70 restored failed again.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Needs Improvement. The CHANGELOG lapse;
  a test outcome stated wrongly in a commit message; the security review's
  fourth finding title never reached the main loop. The heredoc and
  metacharacter hooks blocked three commands and were right each time.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Zero spend held. One risk
  materialized: B2's full samples are lost (QCi returns 404), because B2's
  rows never stored a job id and only the truncated print kept one.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. F127 is first and starts with two
  team lead actions. The local pre-commit confidentiality hook is not
  tracked by git, so a new repository would not get it without a hand copy.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Phase 2 code imported Phase 1
  code read-only throughout; the storage defect is fixed at its cause; the
  phase boundary is now settled by repository, not by convention.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond the improvements below.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none new; F126 and F127 were carded
  during Manual Validation.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The security review found real
  issues, but its fourth title did not reach the main loop, so one finding
  is unaddressed. The advisor predicted near-uniform weights for boosted
  pools; the data showed otherwise and was reported as measured.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

## Improvements proposed (awaiting the team lead's decision)

| # | Title | Source | Type | Effort | Recommendation |
|---|---|---|---|---|---|
| IMP-1 | Check every card claim against what exists before scheduling | Cat 4 | Prevention, extends the capability pre-flight (Sprint 21 IMP-1) | 15m | now |
| IMP-2 | Ask a dependent decision after the one it depends on | Cat 6 | Prevention, extends the CLAUDE.md one-decision-per-question rule | 10m | now |
| IMP-3 | Track the pre-commit hook and add a CHANGELOG check to it | Cat 8, 9, 11 | Prevention, extends the confidentiality pre-commit hook | 45m | now |
| IMP-4 | Commit messages state no test outcome | Cat 2, 9 | Prevention, extends the CLAUDE.md restated-number rule | 5m | now |
| IMP-5 | Background reviews write findings to a file read in full | Cat 9, 15 | Prevention, extends the review step in `SPRINT_EXECUTION_WORKFLOW.md` | 30m | now |
| IMP-6 | Every device row carries its job id | Cat 10 | Detection, extends `test_row_schema.py` | 20m | backlog, on F127 |
| IMP-7 | Restart the velocity log and calibrate estimates from it | Cat 3 | Prevention, extends `VELOCITY_LOG.md` and the planning estimate step | 30m | now |

## Improvement Decisions

Team lead, 2026-10-07: "1" (apply all as recommended: IMP-1, 2, 3, 4, 5 and
7 now; IMP-6 to the backlog on F127).

| # | Decision | Where |
|---|---|---|
| IMP-1 | **now** (applied) | `SPRINT_PLANNING.md`, capability pre-flight: a card's claims checked against files on disk and the installed package |
| IMP-2 | **now** (applied) | `CLAUDE.md`, under the one-decision-per-question rule |
| IMP-3 | **now** (applied) | `.githooks/pre-commit` (tracked), `.gitattributes`, `docs/ENVIRONMENT.md`, `test_pre_commit_hook.py` |
| IMP-4 | **now** (applied) | `CLAUDE.md`, under the restated-number rule |
| IMP-5 | **now** (applied) | `SPRINT_EXECUTION_WORKFLOW.md` Phase 5; the Task B security review re-run under it |
| IMP-6 | **backlog**, on F127 | `ALL_SPRINTS_MASTER_PLAN.md`, F127 card |
| IMP-7 | **now** (applied) | `VELOCITY_LOG.md` rows 15-22; `SPRINT_PLANNING.md` estimation; `SPRINT_RETROSPECTIVE.md` step 7 |

**Applied.**

- **IMP-3** is the only one with code. The confidentiality gate lived in
  `.git/hooks/pre-commit`, which git does not track. It now lives in
  `.githooks/pre-commit`, carries the same two confidentiality checks, and
  blocks a commit that stages code under `experiments/**.py`, `scripts/`,
  `.claude/hooks/` or `.githooks/` without `CHANGELOG.md`. Enabled with
  `git config core.hooksPath .githooks`. `.gitattributes` pins it to LF, since
  a CRLF checkout breaks the shebang. 8 tests run the real hook in a scratch
  repository. **Proven red** against two mutations: the CHANGELOG check
  emptied (4 failed) and an early `exit 0` (5 failed).
- **IMP-7** found the velocity log had stopped at Sprint 14; per-task actuals
  for Sprints 15-19 were never recorded and are marked so, not reconstructed.

**IMP-5's rerun of the Task B security review: 12 findings, all addressed
now** (team lead, 2026-10-07: no technical debt into the next sprint;
address now unless a full card would be more effective). The agent wrote
`FINDINGS: 12` to a file; all 12 entries were read. None high; four medium.
The guard moved from `experiments/src/conftest.py` to the root `conftest.py`.

- **1 (medium) the guard did nothing for `pytest experiments -k x`**: fixed.
  At the root it is an initial conftest for every invocation, and a session
  with no snapshot fails. Proven end to end: a probe that rewrote
  `gate_report.md` under `pytest experiments -k probe` and `pytest . -k probe`
  exits 1 and names the file.
- **2 (medium) a bypass is traced only when the liveness test is selected**:
  covered by CI's existing "Test run must leave the tree clean" step, which
  no pytest flag skips. The local limit is documented in the docstring.
- **3 (medium) a test that could not fail**: every source-text test replaced
  by behavioral tests that drive the hooks with a stand-in session and
  scratch git repositories (18 tests).
- **4 (medium) the baseline is the disk, not the commit**: evidence already
  modified at session start is named in a warning banner; CI's clean-tree
  step fails it.
- **5** names git would quote: `-z`, decoded as UTF-8. **6** wrong tree or
  index: inherited `GIT_*` variables removed, and a listing without
  `results.json` fails. **7** writes after the session: CI's clean-tree step;
  documented. **8** nested `.gitignore`: only the root `.gitignore` decides
  scope; ignored files documented as out of scope. **9** symlinks hashed as
  their target path. **10** case-only renames are a change. **11** the
  failure is also written to stderr. **12** docstrings corrected.
- **Proven red**: ten mutations of the guard, each with the bytes checked
  before the run; every one turned at least one test red. One of my
  mutations was malformed on the first pass (a syntax error, not a test
  result) and was rerun correctly. The repository already has a mutation
  helper (`experiments/src/injection.py`); I wrote a scratch script instead,
  which is the hand-rolled-tool pattern CLAUDE.md warns about. It checked the
  bytes of every mutation, so the result stands, but the helper was the
  right tool.
- **Found while fixing**: IMP-3's CHANGELOG check matched `experiments/**.py`
  but not the new root `conftest.py`; it now matches any `.py` file. A sed
  mutation meant to prove that test red silently failed to apply; a byte
  check caught it, and the rerun went red.

**PR #159 reviews.** Copilot: no findings, no inline comments; it flagged
the PR for final human review because it touches safety infrastructure. A
code review agent wrote `FINDINGS: 15` to a file; all 15 entries were read,
and all 15 were addressed now (team lead's PR review instructions: no
technical debt into the next sprint).

- **1 (critical) and 2 (important): the confidentiality scan in the new
  tracked pre-commit hook missed a renamed-and-edited file and a file name
  with a space.** Both were reproduced by the reviewer. The hook now scans
  the whole staged diff, never a list of names, and blocks if git cannot
  produce the diff. This was a defect in IMP-3, applied this sprint.
- **3**: hook tests now cover rename, space, and one path per pattern
  alternative, and assert the CHANGELOG message itself.
- **4 (important)**: the F125 test passed on a crashing hook; it now asserts
  the hook ran to completion (exit 0 or 2, no traceback).
- **5 (important)**: F20 compared overall test-AUPRC gains with the plan's
  in-pocket oilgas spread (0.05). Now compared with the measured overall
  seed SD from the same result file; "35 times" became "7 to 22 times" in
  both documents. Conclusions unchanged; telecom's gain now reads as about
  equal to its spread.
- **6 (important)**: F17's "2.5 to 40 times" corrected to about 2.4 and 47
  times on the means (2.2 to 85 per seed).
- **7-10, 14, 15**: Phase 2 READMEs updated for D7 and section 9; the
  validator's docstring names the recovered samples; the cost floor's count
  is 27 (filter stated); the emulator's dict return is documented and the
  claim that it tests response-handling code is withdrawn; the velocity row
  includes D's 20 minutes (0.09) and three missing unplanned rows are added;
  the CHANGELOG test count is removed.
- **11-13**: the two source-text "never writes" tests are behavioral (the
  module's real write path runs, and the evidence directories are hashed
  before and after); the `_count` call count matches any argument; the
  no-plan diff uses the ref the commit count resolved against.
- **Proven red**, with the repository's own helper `injection.assert_can_fail`
  this time (green before, red under mutation, green after): six hook
  mutations, two close-out hook mutations, one call-count mutation, two
  write-path mutations.
- **Found while doing it: `injection.py` itself rewrote LF files as CRLF on
  Windows** and passed its own restore check, because `read_text` folds the
  CRLF back. It now reads and writes with `newline=""`; a byte-level test
  fails on the old helper. Two of my own mutations were also wrong on the
  first attempt (one reproduced a skip the old hook did not have; one kept
  the target inside its replacement). The helper refused the second; the
  first was caught by asking why the test stayed green.

**Completion updates.** Master plan: Sprint 22 in Last Completed Sprint,
Sprint 21 demoted; the Past Sprint Summary row is added when the SUMMARY doc
is written. `CHECKLIST-Phase2.md` reconciled: F124 added and ticked; "Decide
where Phase 2 work lives" ticked; experiment 3 progress for F17.
