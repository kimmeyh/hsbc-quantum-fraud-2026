# Sprint 5 Retrospective

Sprint 5: "The Paper and the QCi Package". Cards #23-#28. PR #29 merged to
develop; PR #30 merged develop to main.

Team lead feedback recorded VERBATIM as supplied on 2026-09-04 (combined
Product Owner / Scrum Master / Lead Developer response). Claude Code
Development Team feedback drafted in parallel per protocol step 2, before the
team lead's response was received.

## Sprint 5 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Six cards closed and the submission package reached a defensible state, but the
  efficiency story is mixed and the honest summary is that external reviewers did
  work I should have done. Three separate AI reviews found defects in my output:
  the prediction-key collision (Claude app), the reproducibility and stochasticity
  gaps (Codex 5.5), and the uniform-weight overstatement plus the missing Loke et
  al. citation (Codex 5.6). Each was real. None was caught by my own verification.

  The page-size failure is the sharpest instance. Nine PDFs were 11x17 tabloid for
  an unknown number of days, and the defect surfaced only because the team lead
  asked a direct question. My page-count checks had been reporting "within limits"
  against reflowed Word output the whole time, so the verification I had built was
  actively producing false assurance rather than no assurance.

  Rework counted: the render toolchain was rewritten once (Word path deleted), the
  appendix was trimmed across roughly eight render cycles to hold 3 pages, and the
  QCi cover needed a second correction pass after a failed edit batch silently
  rolled back.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  28 tests pass and they did their job on the code paths they cover: the metered
  billing guard, the store keying, the gate scoring. The gap is that **not one
  test covers a submission artifact**. Page size, page count, required-field
  presence, and stale-claim detection are all properties of the deliverable, and
  all four were verified by ad-hoc commands I happened to write, not by anything
  that runs on its own.

  The page-size defect would have been caught on day one by a five-line test
  asserting mediabox == 612x792 on every PDF in `docs/paper/out/`. I wrote that
  assertion eventually, but as a throwaway inside the render script rather than as
  a test. `check-page-limits.py` exists but is not in the pytest suite, so it only
  runs when I remember to run it.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Estimates were poor in one specific direction: I estimated document work as if
  it were writing, and it was mostly verification and rework. The appendix
  3-page fit was estimated at minutes and consumed roughly an hour across repeated
  render-measure-trim cycles, because I trimmed prose repeatedly before checking
  where the page break actually fell. Measuring first would have found the wasted
  half-page on page 1 immediately.

  Hardware estimates remain accurate: zero metered seconds were spent this sprint,
  as planned.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The plan held. Scope (F8, F9, F27, F19, F26, F28) was delivered without
  de-scoping, and the outline-first approach for the paper worked well. What the
  plan did not anticipate was the volume of external-review response work, which
  arrived mid-sprint and was larger than any planned task. That is not a planning
  defect exactly, but a plan that assumes no external input will always be wrong
  in this project, since the team lead is actively soliciting it.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  No subagents were used this sprint; all work ran in the main loop. That was
  correct for document work, where context continuity matters more than
  parallelism. The one place delegation would have helped is the fresh-eyes
  review the workflow already mandates (Phase 5): I did not run it, and the
  external reviewers filled that role instead. The process document already
  requires this and I skipped it.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Two failures worth naming. First, I reported "OK 3 of 3 pages" for the appendix
  from a stale PDF and would have handed that to the team lead as verified had I
  not re-rendered. Second, when the render failed with "xelatex not found" and
  then died mid-page, I reported progress before diagnosing, which produced two
  turns of noise before the actual cause (an unreadable PATH entry) surfaced.

  Commit messages were good: each records what changed, why, what was rejected and
  what was verified, which is the form that survives into a summary.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The submission guidelines were read carefully and the requirements matrix was
  current, yet section 4.1 (team profile: contact details, affiliation) was
  unmet until a reviewer flagged it. The requirement was known and written down in
  `requirements-matrix.md` line A5b. It was a tracking failure, not a
  comprehension failure: an item marked TODO in the matrix never became a task.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Strong. ADR-0012 was corrected in place rather than superseded, recording both
  Word-path defects and later the PATH and margin issues, so the reasoning
  survives. The review dispositions (`docs/reviews/`) record where each reviewer
  was right AND where each was wrong, which is the part that will matter if a
  finding resurfaces. Prereg amendments A9 and A10 were logged properly.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  - MiKTeX aborts if any PATH entry is unreadable. A stale `C:\devtools\cursor`
    entry killed xelatex on a bare "Hello world" while the console output looked
    like a mid-document LaTeX error. Fixed by running pandoc with a minimal PATH.
  - A Python edit script that asserts on several anchors and writes at the end
    loses ALL edits when one anchor fails. This bit twice, and the second time I
    did not notice until a stale-claim scan caught it in the rendered PDF.
    Rule: write after each successful edit, or verify the file after the script.
  - Bash loops piping render output through `grep` swallowed failures and returned
    a misleading exit code; individual invocations were needed to see the truth.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The deadline risk is now the dominant one: 11 days remain and the submission
  package is complete but unsent. Hardware budget risk did not materialize (zero
  metered seconds). Confidentiality risk is controlled (0 HIGH findings, and the
  personal-email REVIEW line is intentional and reviewed).

  The risk that did materialize and was NOT on the register: **verification that
  reports success while measuring the wrong artifact**. Both the page-count
  failure and the stale-PDF reading are instances. This deserves a register entry
  of its own, because it defeats the mitigation rather than merely failing.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Ready. Carry-forward branch `feature/20260905_Sprint_6` created from the Sprint 5
  branch per 6.6. Master plan needs the Sprint 5 roll and the summary doc is due
  during Sprint 6 planning per the three-doc rule.

  The open decision for Sprint 6 is whether the diverse-pool experiment (now
  strongly motivated by Loke et al.) fits before submission, or whether Sprint 6
  holds to F3 and paper polish as the targeted plan says.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  No protocol drift. The preregistration remains frozen; A9 and A10 are logged
  with rationale; no gate was rescored. Results.json schema adherence held, and
  the store's arm-keyed prediction paths (the A9 fix) are now covered by a test.

  One deliberate inconsistency to note: "QPU seconds" was changed to "metered
  device seconds" in the submission documents but NOT in PREREGISTRATION.md,
  because the latter is frozen and its wording is part of the record. That is the
  correct call but it will look like an oversight to a future reader, so it is
  recorded here.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:

  - [DEV] Add `check-page-limits.py` assertions into the pytest suite so page size
    and count are verified on every run, not on demand -- target: Sprint 6 plan,
    est: 20m
  - [DEV] Add a stale-claim scan (assert corrected phrasings absent from all
    rendered PDFs) as a test -- target: Sprint 6 plan, est: 20m
  - [DEV] Add a submission-requirements test asserting each guidelines 4.1/4.3
    required element appears in the rendered PDFs -- target: Sprint 6 plan,
    est: 30m
  - [DEV] Record the appendix 0.9in margin in the render invocation itself (a
    per-document config) so a default rebuild cannot silently produce 4 pages --
    target: Sprint 6 plan, est: 15m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:

  - [DEV] F31: Diverse weak-learner pool experiment (KNN, LDA, logistic
    regression, boosted variants) replicating Loke et al.'s pool construction --
    estimated: 6-10h classical, priority 1, depends on: nothing (classical only)
  - [DEV] F32: Hardware prediction persistence run, so operating-point tables
    carry [HW] rather than [SIM] -- estimated: 2h plus 40-50 metered device
    seconds, priority 2, depends on: team-lead hardware approval (Criterion H)
  - [DEV] F33: Artifact-verification test module covering page geometry, required
    fields, stale claims and confidentiality patterns -- estimated: 2h,
    priority 2, depends on: nothing

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  No subagents were assigned this sprint, so there is nothing to assess on
  delegated output. The relevant observation is the inverse: the Phase 5
  fresh-eyes review that the workflow mandates was not run, and external human-
  initiated reviews substituted for it. That is a process skip on my part, not an
  agent-quality issue.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:

  1. Does the diverse-pool experiment (F31) enter Sprint 6, given that Loke et al.
     now provides both the motivation and a published target number? It is the
     single highest-value technical item, it is classical-only, and it directly
     addresses the weakness every external reviewer identified.
  2. Should the proposal be trimmed below 6 pages? The guidelines state a
     well-structured 4-page proposal outperforms a rambling 6-page one, and the
     document is currently at exactly 6 of 6 with no headroom.
  3. Is the QCi package sent this sprint or held? It has been ready across two
     sprints and the sending decision is the team lead's alone.

## Improvement Decisions

Proposed after the combined feedback (protocol step 5); disposed by the team
lead 2026-09-04 (protocol step 6): "all as recommended".

| # | Improvement | Type | Effort | Disposition | Status |
|---|---|---|---|---|---|
| 1 | Artifact-verification tests in the pytest suite (page geometry, page count) | Testing | 20m | APPLY NOW | Done: `experiments/src/test_submission_artifacts.py` |
| 2 | Stale-claim scan as a test | Testing | 20m | APPLY NOW | Done: `test_no_retired_claims` |
| 3 | Submission-requirements test (guidelines 4.1 and 4.3 elements) | Testing | 30m | APPLY NOW | Done: `test_team_profile_has_required_fields`, `test_proposal_covers_every_required_section` |
| 4 | Per-document render config so the appendix margin cannot be lost | Tooling | 15m | APPLY NOW | Done: `scripts/render-all.ps1` |
| 5 | F31 diverse weak-learner pool experiment | Experiment | 6-10h | BACKLOG, priority 1 | Registered; team lead approved Sprint 6 entry |
| 6 | F32 hardware prediction persistence | Experiment | 2h + 40-50 metered s | BACKLOG, priority 2 | Registered; needs Criterion H approval |
| 7 | Risk/defect class: verification that measures the wrong artifact | Process | 10m | APPLY NOW | Done: `docs/QUALITY_STANDARDS.md` |

The new tests were verified to FAIL on the defects they cover before being
trusted to pass: a deliberately re-rendered 11x17 team profile failed the
geometry assertion, and its LaTeX-hyphenated phone number failed the
required-fields assertion. Suite went from 28 to 50 passing.

## Team lead answers to Category 16

1. **Does F31 enter Sprint 6?** Yes.
2. **Trim the proposal below 6 pages?** "I am OK with 5 as a goal but 6 is
   acceptable as all the content is valuable." So a 5-page target, not a
   requirement, and no content is cut merely to hit it.
3. **Is the QCi package sent?** "Consider it sent."
