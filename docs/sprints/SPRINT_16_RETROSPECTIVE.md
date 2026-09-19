# Sprint 16 Retrospective

**Sprint**: 16, "Make the Guards Portable, and Close the Gate"
**Scope**: F79, F78, F80
**PR**: #120 to develop, 22 commits
**Issues**: #110-#119, all closed
**Metered Dirac-3 seconds**: ZERO

Team lead feedback recorded verbatim 2026-09-19 as combined Product Owner,
Scrum Master and Lead Developer. Claude Code Development Team feedback drafted
against the same categories.

## Sprint 16 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ten tasks, all delivered, zero metered
  seconds. The conversion work was mechanical and went to plan; the value came
  from what baselining found along the way, which was not planned for.
  The inefficiency worth naming is mine: I ended turns three times announcing
  work I had not started, and the team lead had to ask twice whether it was
  actually happening. That is not a small waste -- it cost two round trips and
  it happened after the rule was already written down in three places.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every guard added this sprint was verified
  by injection rather than by a green run, and the practice paid twice: the
  control-character guard found a sixth instance already committed, and the
  interpreter-path guard caught its own stale allowance when the F78 card was
  pruned. 143 parity cases ran against BOTH implementations and required
  agreement, which is stronger than either matching a written expectation.
  **The failure mode this sprint was verification, not code.** Three of four
  errors were defects in the checking rather than the thing checked: an
  injection that injected nothing while printing 77 passed, a baseline that
  looked like a live bug and was a malformed payload, and a test case whose
  data contradicted its own name. Each looked exactly like a real defect.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Estimated 585 minutes plus a 40-minute
  findings allowance. The tasks themselves landed close; the allowance was
  consumed and then some, entirely by findings the tasks surfaced -- the
  confidentiality-scan bug, the three-doc exemption reframing, the
  turn-end hook port. That is the allowance working as designed rather than an
  estimate miss.
  Not estimated at all, and larger than any single task: the PDF recovery and
  the QCi relocation, both of which arrived mid-sprint from Manual Validation.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The capability pre-flight earned its place
  twice. It corrected F78's own card (21 hardcoded paths, not 18) and it
  reframed F79 entirely: the card said "missing check", and the pre-flight
  found the check already existed with an exemption that was never revoked.
  Planning a fix for the wrong defect would have shipped something that did not
  close the gap.
  The plan's task ordering held: converting the four zero-construct hooks first
  as pattern-setters meant the harder five had a proven shape to follow.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: One subagent, for falsifier run 3, where
  lack of context is the entire mechanism. It returned the sprint's sharpest
  single observation -- that silence about one digit coincidence, having
  flagged another, reads as significance rather than as nothing.
  Everything else was main-loop work that would have cost more to delegate than
  to do, since it depended on repository context throughout.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Commit messages carried the reasoning, not
  just the change, which mattered for the findings that outlived their cards.
  The failure is the same one as category 1: three turns ended on a promise.
  The team lead's "are you really doing task E?" was a fair question and I had
  given him reason to ask it.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The three cards were unambiguous. Where
  clarity mattered more was mid-sprint: "do not touch frozen submission
  documents" and "the PowerShell should not be fixed as we will never use it
  again" each closed a question I would otherwise have had to guess at, and
  both became rules rather than one-off decisions.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: `docs/ENVIRONMENT.md` is the one document
  this sprint should be judged on: it replaced 21 scattered copies of a fact
  that is not discoverable from the environment, and a guard keeps it single.
  Three documents claiming the PDFs were not tracked were corrected together
  rather than one at a time, because the search found all three at once.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: **The escape-eaten class appeared seven
  times this sprint**, in injections, in test fixtures, in a protected-span
  string, and in my own tooling. It is now the most frequently recurring defect
  in this repository's history and the existing hooks do not cover the shapes
  that keep biting, because they guard commands rather than the strings I
  construct inside heredocs.
  Second: the turn-ending rule was already written in three places and failed
  three times. A hook now enforces it, ported from spamfilter-multi.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan's stated risk was "a converted
  hook that stops blocking is worse than no conversion", and it was mitigated
  correctly with per-hook injection proof.
  **The risk that materialized was not on the list**: that a task would
  silently damage a submitted artifact. Task G re-rendered the three filed PDFs
  to prove the renderer worked, which it did, and in doing so replaced the
  bytes that were actually submitted. Recoverable only because a backup existed
  and the hashes were recorded.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The backlog is thin on this-repository
  work. F81 is team-lead owned, F64 is withdrawn, F2b is metered. The venv
  parity question and the `.ps1` deletion are both live decisions rather than
  cards.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Nothing in code diverges from the frozen
  preregistration and no amendment was needed. The hook layer changed
  language but not contract: stdin JSON in, exit 0 or 2 out, verified identical
  across 143 cases. `hooklib` is the one new abstraction and it is deliberately
  thin -- four functions, because the measured OS-specific surface was four
  needs and not more.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none. The two candidates I would have
  raised are improvements below rather than cards, because both are rules
  rather than work.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: One, and it is a decision rather than a
  card: the nine `.ps1` files are retired but not deleted. The parity tests
  skip rather than fail once they are gone, so removal is safe whenever the
  team lead wants it. Keeping them costs nothing except the chance that someone
  edits the wrong file.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: One agent, first-pass correct, no rework.
  It answered all seven questions unaided at high confidence and volunteered
  four gaps, three of which were real and fixed. It also correctly reported the
  CVQBoost acronym as an inference rather than a fact, which is the third
  reader to survive that hedge.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: Two open items, both raised and neither
  blocking: the gate-report rename (recommendation: `Results Against
  Preregistered Criteria`, PDF output only), and the venv parity question
  (recommendation: measure divergence before switching, and settle whether
  Appendix C's "Python 3.12, Linux" is accurate).

## Combined summary

**Sixteen categories, four roles, no placeholders.** The team lead rated all
thirteen assessed categories Very Good and returned `none` for 13, 14 and 16.

Sprint 16 delivered F79, F78 and F80 in ten tasks with zero metered seconds,
and closed a gap that had been open since Sprint 5: **every guard in this
repository was Windows-only protection while CI ran Linux.** Nine hooks and
four scripts are now Python, with 143 parity cases requiring agreement between
both implementations and a CI step proving a guard fires on Linux rather than
merely loading.

**The sprint's pattern is that checking found more than building did.**
Baselining the confidentiality scan found it reporting clean on any single-line
file. The F79 pre-flight found the defect was an exemption never revoked rather
than a missing check. Falsifier run 3 reached high confidence for the first
time and still found four gaps. The interpreter-path guard caught its own stale
allowance an hour after being written.

**Two things went wrong that were not on any risk list.** Task G re-rendered
the three submitted PDFs to prove the converted renderer worked -- it did, byte
comparison confirmed the content -- and thereby replaced the artifacts that were
actually filed. And relocating the QCi correspondence to `docs/` would have
published it, because its protection came entirely from the parent directory it
was leaving.

Both were caught, both recovered, and both by a check rather than by noticing.

**The escape-eaten class appeared seven times**, which makes it the most
frequently recurring defect in this repository's history. Every instance was in
something I constructed inside a heredoc rather than in committed code, which is
exactly where the existing hooks do not look.

## Improvement Decisions

Proposed 2026-09-19. Each carries Title, Source, Type, Effort and
Recommendation. The team lead disposes each as now, backlog or skip.

### IMP-1: Never re-render a submitted artifact to prove a tool works

- **Source**: Category 10; Task G
- **Type**: Behavioral, with a mechanical backstop
- **Effort**: 0m for the rule; the guard already exists
- **What**: Task G re-rendered `proposal.pdf`, `appendix.pdf` and
  `team_profile.pdf` in place to demonstrate that `render_all.py` reproduced
  them. It did. The proof also destroyed the filed bytes, recoverable only
  because a backup existed and the hashes were recorded in two places.
  The correct form is to render to a scratch path and compare, which costs one
  extra argument. `test_published_artifacts.py` now fails on any rebuild of a
  tracked PDF, so the backstop is in place; the rule is what prevents needing it.
- **Recommendation**: ADOPT NOW as a CLAUDE.md NOT-do line. "A submitted
  artifact is evidence, not a test fixture. Render elsewhere and compare."

### IMP-2: A move out of a protected directory needs its rule written FIRST

- **Source**: Category 10; the QCi relocation
- **Type**: Process
- **Effort**: 0m, an ordering rule
- **What**: Moving `qci_package/` from `docs/paper/out/` to `docs/` removed its
  protection entirely -- the parent rule was doing all the work, and nothing
  under `docs/` replaced it. `git check-ignore` on the destination returned
  "not ignored" BEFORE the move, which is the only reason it was caught.
  The general shape: a file's protection often comes from its location, so
  relocating it silently revokes that protection. The check is one command and
  takes seconds.
- **Recommendation**: ADOPT NOW. Before moving any ignored file, run
  `git check-ignore` on the DESTINATION path and write the rule if it returns
  nothing.

### IMP-3: Hook the escape-eaten class where it actually happens

- **Source**: Category 9; seven occurrences this sprint
- **Type**: Tooling
- **Effort**: ~1h, worth a card
- **What**: The class has now appeared in a JSON registration, a CHANGELOG
  entry, a master-plan card, two injection scripts, a test fixture and two
  protected-span strings. `block_unraw_escape` catches Windows paths in
  non-raw Python strings and `block_shell_metachar_expansion` catches shell
  expansion, and neither sees a backslash sequence I write INSIDE a heredoc
  that then lands in a file.
  `test_no_control_characters` catches the result after the fact, which is how
  the sixth instance was found. What is missing is a check at write time.
- **Recommendation**: BACKLOG as a card. It is the highest-frequency defect in
  the repository and the two existing hooks demonstrably do not cover it.

### IMP-4: Record what a verification actually proved, not that it passed

- **Source**: Category 2; three of four errors were in verification
- **Type**: Behavioral
- **Effort**: 0m
- **What**: Two injections reported success while injecting nothing. A baseline
  reported a live bug that was a malformed payload. A test case passed for the
  opposite of its stated reason. In each case the output was indistinguishable
  from a real result.
  What caught them was asserting the PRECONDITION: the abort-if-target-absent
  check in the injection script, and reading the actual bytes rather than
  trusting a replace. The rule is to make the injection prove it landed before
  trusting what the suite then says.
- **Recommendation**: ADOPT NOW. Every injection asserts the mutation is
  present before running the check it is meant to trip.

### IMP-5: Retire the .ps1 files, or state why not

- **Source**: Category 14
- **Type**: Housekeeping
- **Effort**: 15m
- **What**: Nine PowerShell hooks and four scripts are retired but present. The
  parity tests skip rather than fail once they are gone, so deletion is safe.
  Keeping them costs one thing: someone edits the wrong file and the edit has
  no effect, which is the dead-hook shape this repository has paid for twice.
- **Recommendation**: TEAM LEAD DECISION. I lean toward deleting them now that
  CI proves the Python versions run, but the parity tests lose their
  cross-check the moment the PowerShell is gone, and that cross-check is
  currently the strongest evidence the conversion is faithful.


## Dispositions (team lead, 2026-09-19)

**All five approved: "all now".** IMP-5 resolved as a MOVE rather than a
deletion.

| Item | Disposition | Where it landed |
|---|---|---|
| IMP-1 re-rendering a submitted artifact | ADOPTED | CLAUDE.md NOT-do list |
| IMP-2 ignore rule before a move | ADOPTED | CLAUDE.md NOT-do list |
| IMP-3 hook the escape-eaten class | CARDED | F82, Priority 4 |
| IMP-4 assert the injection landed | ADOPTED | CLAUDE.md NOT-do list |
| IMP-5 retire the .ps1 files | MOVED, not deleted | `D:\Data\Harold\hsbc-quantum-fraud-2026\OldPowerShellScripts` |

**On IMP-5**: the team lead chose to move all 13 files outside the repository
rather than delete them, which keeps the originals recoverable without leaving
them where someone can edit the wrong file. The archive carries a README
mapping each file to its Python successor, explaining why the conversion
happened, and warning that `confidentiality-scan.ps1` holds an unfixed
single-line-file bug and must not be restored into service.

The parity tests now skip their PowerShell half rather than failing, which was
the designed behavior. That does end the strongest evidence the conversion is
faithful -- 143 cases requiring agreement between two implementations -- so the
archive exists to reconstruct that comparison if it is ever disputed.
