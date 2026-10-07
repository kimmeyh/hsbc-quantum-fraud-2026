# Sprint 20 Summary: Make the Suite Readable Again

**Sprint**: 20 | **Dates**: 2026-09-30 to 2026-10-04
**Branch**: `feature/20260930_Sprint_20`
**PRs**: #146 to develop, #151 develop to main (both merged 2026-10-04)
**Cards**: F97, F93, F98, F99 delivered. F93 closed on the team lead's F90
decision. F5 and F2b's B4 line closed into F90. F122 registered.
**Metered Dirac-3 seconds**: **0**

Sources: `SPRINT_20_RETROSPECTIVE.md`, `SPRINT_20_VALIDATION.md`, git history,
PR #146. Written during Sprint 21 planning per the three-doc rule; the master
plan is not a source.

## The objective, and it was met

**The suite is green in a planning window for the first time.** That was the
point of the sprint. Six tests asserted that Phase 3 artifacts exist --- a
draft PR, task issues, a recorded approval, a plan document --- without
qualification, while Phase 3 is the phase that creates them. The suite was
therefore red for the whole of every planning window, which is exactly when
the next sprint's plan is being written and reviewed. A suite expected to be
red is a suite nobody reads.

A consolidation sprint: no new capability, no metered spend, no document that
went outside. F90, the most valuable work available, was deliberately excluded
because it would spend about 74% of the 1,681-second balance and deserved its
own sprint.

## What was delivered

**Task A (F97)** gated six tests on the recorded phase through an ordered
`PHASE_ORDER` tuple. An unknown slug returns True, so a phase name nobody has
thought of yet cannot silently disable a check --- the fail-safe direction.
Proven across nine sprint states with the same code, and proven to still go red
where an artifact is genuinely owed.

**Task B (F93)** put all four SPECTRA records side by side in
`docs/SPECTRA_BLOCK_RECONCILIATION.md` with their provenance, and surfaced the
tension the card did not know about: the hardware plan sent to QCi quotes 270
seconds while F90's configuration costs about 1,236. The team lead decided on
2026-10-03 to proceed on an off-repository device result, which is the decision
F93 had been waiting for. Five guards keep the four records from drifting apart
again.

**Task C (F98)** fixed a hook that a slow network could silence. The measured
mechanism: a Stop hook killed at its timeout produces **no exit code at all**,
so it cannot block --- a timeout fails OPEN whatever it would have decided. The
fail-open `gh` checks ran *before* the deliberately fail-closed CI check, so one
hanging `gh pr list` killed the hook before the guard it exists for ever ran.
Reordered, with internal timeouts cut from a 160-second worst case to 18 against
the budget. Proven by stubbing a hang: the CI violation still appears, in 0.9
seconds.

**Task D (F99)** recorded sha256 hashes for the three sent QCi artifacts in
`docs/QCI_CORRESPONDENCE_HASHES.md`. The `_files` sidecar is pinned by one
manifest hash over its sorted (name, sha256) pairs, so an added or removed file
is caught as well as an edited one. The guard skips **visibly** where the
gitignored artifacts are absent, because a skip that reads as a pass is this
repository's most-repeated defect. The ignore rule did not change and nothing
inside `docs/qci_package/` was written.

## Tooling added

- `docs/TROUBLESHOOTING.md` --- one symptom index for the repository, replacing
  "grep everything under `docs/`" in the Phase 2 pre-flight. Two items were
  ADDED, not moved, from spamfilter-multi where they apply here; the document
  also records what was deliberately not imported and why.
- `scripts/outlook_htm_to_md.py` --- converts Outlook and Word HTML exports to
  Markdown. Charset-aware, refuses to overwrite, and `--check` compares
  occurrence counts so a figure absent from the source fails rather than
  passing quietly.
- `block_heredoc_escape_loss.py` extended to **quoted** heredocs, verified
  across all 25 Python string-prefix combinations.
- `pytest.ini` gained `addopts = -rs`, so skip reasons print in CI. Silent
  skips were how several of this sprint's defects stayed invisible.

## Defects in this sprint's own work

**The PR #146 review round found ten, and the two worst were guards that
disabled themselves.** Both are in code shipped this sprint, and both are the
"could not check reads as clean" class --- inside guards written to prevent
exactly that.

A failing or slow `git` silently skipped all three Phase 3 close-out checks.
`hooklib.git` returns `(1, "")` on any exception including a timeout, so the
commit count came back None, "work started" became False, and the checks were
skipped with **no violation recorded**. That is the Sprint 17 failure --- nine
tasks, a full retrospective, `pr: null` --- reproduced invisibly. The explicit
`timeout=2` added earlier in the same review made it more reachable.

The ignore-rule guard passed on a **commented-out** rule. It asserted that
`docs/qci_package/` appeared in `.gitignore`, and a substring cannot tell an
active rule from a commented one. Measured: with the rule commented,
`git check-ignore` said the private QCi correspondence **would be published**
and the test stayed green. CLAUDE.md already named `git check-ignore` as the
right tool for this exact directory, and the test did not call it.

Also found: budget arithmetic claiming 18 seconds against a real worst case of
98, with the enforcing test repeating the same undercount so it passed on its
own defect; SPECTRA figures inflatable tenfold unnoticed, because `"270"` is a
substring of `"2700"`; `rf""` blocked despite being raw; and a displaced
decorator leaving a test passing vacuously.

**Presence-as-correctness appeared four times in one sprint**, including inside
a guard written to catch it. Three consecutive sprints now. It is the single
most frequent defect in this work.

**The SPECTRA analysis for Task B was built without reading
`docs/HARDWARE_REQUEST_B4.md`**, whose line 89 already held the answer. Three
of my conclusions needed correcting: "no traceable source" was wrong, the data
is PROJ/proxy rather than device, and 8-of-8 was the baseline, not the tuned
configuration.

**The 6.6 carry-forward branch was cut late.** Workflow 6.6 requires
`feature/<date>_Sprint_<N+1>` to be created from the current feature branch
**on merge notification**. It was not created then; it was created at the start
of the Phase 8 sweep, after both merges had landed. Nothing was lost, because
the merges had carried everything and the tree was clean --- which is precisely
what 6.6's own note warns about: "a clean result does not mean the cut was
right. Verify the flow, not the outcome." The first attempt at the late cut was
`git checkout -b ... origin/develop`, which `block_branch_from_develop.py`
blocked correctly; the hook caught the wrong form of a step that should already
have happened.

**IMP-3 was built, tested and removed.** A static check for unanchored presence
assertions caught **zero** of the four failures it was written for: they used
`assert fact in row` over a loop variable, which an AST check for string
constants cannot see. It passed its own suite while catching none of its cases,
so it was removed rather than shipped as false confidence.

## Improvements

Three proposed, two applied now, one reduced on the team lead's challenge.

- **IMP-1 (applied)**: extend the existing escape hook to quoted heredocs.
- **IMP-2 (applied, reduced)**: the team lead asked why the pre-flight should
  grep all of `docs/` when a troubleshooting document would serve. No such
  document existed, though category 9 had asked for one since Sprint 2. Created,
  with four named file patterns instead of a directory sweep.
- **IMP-3 (removed)**: see above.

**Both lower retrospective scores have the same shape: the prevention existed
and did not reach the failure.** The escape hook was written for this exact
class and could not fire. The capability pre-flight rule was followed, and the
evidence it needed was in a document rather than in code. In both cases a new
mechanism would have been the wrong response --- the reach of the existing one
needed extending instead.

A CI-failure checkpoint was also added to the workflow at the team lead's
request, then reduced on his judgment that the four-phase version was too much.
Two non-blocking checks remain: one about five minutes after the draft PR
exists, one on the final HEAD before `gh pr ready`.

## Effort

- Task A: 52 minutes
- Task B: 47 minutes
- Task C: 34 minutes
- Task D: 28 minutes
- **Total: 161 minutes against 171 estimated**

**This is the first sprint with a complete set of per-task actuals**, recorded
as each task finished rather than reconstructed afterwards. That makes it the
first calibration basis this repository has for estimating tooling work.

## Next sprint readiness

The branch `feature/20261004_Sprint_21` is cut from the Sprint 20 branch per
the 6.6 carry-forward rule, though late --- see the defects section. Four cards
pruned from the master plan; F122 registered from the review round and
re-scored to 20, since its 22 paired it with F97 and F97 shipped.

**F90 is the recommended next scope** and the team lead has already said the
SPECTRA analysis matching prior Dirac-3 against quantum-enhanced datasets runs
next. It is metered, so it stops for per-block approval with the call count and
expected seconds stated, per Criterion H.
