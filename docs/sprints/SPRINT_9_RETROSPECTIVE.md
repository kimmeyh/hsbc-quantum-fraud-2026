# Sprint 9 Retrospective

Sprint 9: "Representation, and Paying What We Promised". Cards #50 (F4), #51
(F14), #52 (F16). Backlog: F40 registered.

Team lead feedback recorded VERBATIM as supplied 2026-09-08 (combined Product
Owner / Scrum Master / Lead Developer). Claude Code Development Team feedback
written after, and does not soften a rating the team lead gave.

## Sprint 9 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  All three scope items shipped: the last preregistered arm ran, the QCi
  feedback package exists as a document rather than a promise, and CI now
  guards every PR. Zero metered seconds.

  **The efficiency number is 18.9 hours of compute against a 10-minute
  estimate**, across three runs of the same arm, two of which were discarded
  for my own defects:

  | run | wall clock | outcome |
  |---|---|---|
  | 1 | 3h 12m | 8/20 cells, crashed on a spline basis refitted on test data |
  | 2 | 7h 42m | 20/20 cells, discarded -- twins never received the treatment |
  | 3 | 7h 57m | 20/20 cells, reported |

  Run 2 is the expensive one. It completed, produced plausible numbers, and
  would have been written up had I not inspected per-arm scores before
  drafting. Nothing failed; the arm was simply not the arm the preregistration
  specifies.

  What kept this from being worse: the team lead's "it can run all night"
  removed the pressure to salvage a compromised run, and per-cell checkpointing
  added after run 1 meant run 3 was auditable throughout.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The strongest work this sprint, and it was forced by failure rather than
  chosen.

  Run 1's crash produced two tests, one of which asserts the CORRECTNESS half
  (exactly one `BSplines()`, clipped raw values to `exog_smooth`) rather than
  just "it does not raise". Verified to fail against the pre-fix code.

  Run 2's defect produced four more, including one that pushes test rows ten
  units beyond every training column -- the fixture the original GAM test
  lacked, which is why that test passed against broken code.

  **The test that matters most reads the SHIPPED RESULTS FILE**, not the code:
  it fails if any twin scored identically across representations. Verified
  against the invalidated run, where it reports "gam scored identically under
  both representations in 10 of 10 seeds". Had it existed a day earlier it
  would have fired the moment run 2's results landed, instead of depending on
  me looking.

  That is the durable lesson: guarding the code caught neither defect. Guarding
  the ARTIFACT would have caught both.

  Suite 173 -> 178 plus 2 tracked xfails.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Implementation estimates were close: F14 and F16 landed near 90m and 30m.

  **The runtime estimate was wrong by 47x** (10 minutes planned, 7.9 hours
  actual per run) and I flagged it under Criterion 3 rather than absorbing it.
  The cause is precise and worth recording: Sprint 8 improvement 1 says size
  runtime from actual row counts, and I did -- for the twins and the GBDTs. I
  PILOTED the GAM twin specifically because I believed it was the risk. I never
  sized the CVQBoost pool build, which turned out to be 300 seconds of the 335
  per cell.

  So the improvement was followed and still missed, because I sized the
  components I was thinking about rather than enumerating all of them. The
  rule needs to name the dominant term explicitly, not just require "a"
  runtime estimate.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The plan applied both Sprint 8 improvements and the premise-falsifier rule
  earned its place: F4's falsifier was stated before any data, and the outcome
  it named -- a shift within seed noise -- is what happened. The write-up plan
  was likewise fixed before results, including the instruction that a POSITIVE
  shift would require the JOINT twin's score in the same paragraph.

  That mattered more than expected. Between four and nine seeds the shifts
  drifted monotonically negative and the ratio climbed to 0.70. With a
  pre-written frame I reported it as "worth watching, not concluding". Seed 46
  then broke the drift in both runs, to within 0.0003. Without the frame I
  would have been tempted to narrate a trend that was not there.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  All work on this model, no subagents. Correct for a sprint whose hard parts
  were diagnosing two silent correctness defects and deciding what a null
  result may honestly claim. Neither is throughput-bound.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Twenty-plus status reports over three runs, each with cells, deltas, process
  health and a healthy-or-stalled verdict. The per-cell twin check added to the
  status prompt after run 2 is what confirmed run 3's fix at 50 minutes rather
  than 7.7 hours.

  **One error, and I corrected it in the wrong direction first.** Told the
  letter was sent "around 10am", I found a 16:03 commit and reported the repo
  had diverged from what QCi holds -- correct. Then, misreading a later
  message as "9:59pm", I announced the opposite. The team lead had to say "read
  the file". The header said 09:59:03 -0400, confirming the original reading.

  I should have read the .msg the first time rather than reasoning from a
  remembered time.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Direction was unusually decisive where it mattered: "it can run all night",
  "do not worry about doc size", "removing them going forward is enough". Each
  closed a question I would otherwise have spent effort hedging.

  The sharpest was "for qci we can state that, but for the challenge we do not
  want to claim that". That distinction -- prior paid-tier work belongs in
  vendor correspondence, not a competition entry -- is a judgment I would not
  have made unprompted, and it is now enforced by a test.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  A.6 reports a null as a finding and states plainly that two earlier runs were
  discarded and why, because that bears on how much the third should be
  trusted. The QCi feedback package cites every claim to a file and line, and
  the citations were verified mechanically rather than asserted.

  The letter restructure put the ask, the goal and the return in the first half
  page. Both edits after that were team-lead corrections to framing rather than
  to fact, which suggests the facts were right and the emphasis was not.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  **I edited a document six hours after it was sent, without checking whether
  the send date had passed.** `qci_cover.md` carried a status comment naming
  its send date. I updated it with the H6 result at 16:03; it had gone at
  09:59. No harm resulted -- the change narrows the ask and the sent version
  was accurate -- but "what did we tell them" was briefly unanswerable. Fixed
  by tagging `qci-letter-sent-20260908` and recording the divergence.

  Second: I chased a gate-report "collision" through four width changes using a
  regex over extracted PDF text. pypdf drops the space between adjacent runs,
  so "full 10" extracts as "full10" in a perfectly good table. I was iterating
  against a false signal, and the team lead's landscape suggestion fixed the
  real problem.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Zero metered seconds across the sprint.

  Good: memory was watched from the first QFE cell, and when the process
  crossed 20 GB the monitor fired. It released cleanly at the cell boundary,
  which is what made an overnight run safe -- verified rather than assumed.

  Good: the F38 xfail is `strict=True`, so it FAILS once a document is back
  under limit and cannot outlive the card.

  The segmentation review before F37 found the right things by scanning
  structurally rather than reading team-lead files: contact details in one, and
  credential-shaped patterns in another that I deliberately did not open.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Four submission blockers registered with their measurements already taken:
  F40 (segment) -> F37 (public) in that order, F38 (page limits, now both
  documents), F10 (submission). The Finalize row states the F40/F37 ordering
  because publishing before segmenting cannot be undone.

  Carried: card #40 open pending QCi's substantive reply; H6 follow-up held by
  decision.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  `render-pdf.ps1` gained `-Landscape` and the page-size verifier learned the
  rotated pairs -- taught, not loosened, with an allowlist naming the one
  non-submission document permitted to rotate. The tabloid check still fires on
  an unrequested rotation, verified in both directions.

  `run_h6.py` follows the established shape: loader-enforced protocol,
  checkpointed results, smoke output separated from evidence. The A17 dedup
  guard caught this module twice -- once for genuinely missing deduplication,
  once for a comment that matched its regex -- and I conformed to the guard
  both times rather than teaching it exceptions.

### 13. Minor function updates needed in the next sprint plan

- **Team lead**: none
- **Claude Code Development Team**: none beyond the four registered blockers.

### 14. Function updates for the backlog

- **Team lead**: none
- **Claude Code Development Team**: F40 was registered mid-sprint at the team
  lead's direction and covers the segmentation work. Nothing further.

### 15. Questions to be discussed before ending the sprint

- **Team lead**: none
- **Claude Code Development Team**: none. The H6 follow-up decision is made
  (hold); card #40 stays open pending QCi.

## Summary

Sprint 9 delivered all three scope items with zero metered seconds. H6, the
last preregistered arm, returned a measured null: the phase representation
shifts the quantum-minus-classical delta by -0.0115 against a paired SD of
0.0135, which is 43% of our MDE. The falsifier fired, as predicted before the
final cells by exhaustive search.

**The sprint's defining fact is that the same arm ran three times, and two runs
were discarded for defects that did not announce themselves.** Run 1 crashed,
which was lucky -- the underlying error was a spline basis refitted on test
data, silently wrong long before it raised. Run 2 completed cleanly with
plausible numbers and was caught only because I inspected per-arm scores before
writing.

Both defects share a shape: **the code ran, the numbers looked reasonable, and
the experiment was not the experiment the preregistration specifies.** Neither
was caught by a test of the code. The test that would have caught both reads
the shipped results file, and now exists.

The best work: the twin fix that raised GAM from 0.2590 to 0.7893 and turned
the classical bar from two straw men into genuine competition; the write-up
plan fixed before any result, which held through a four-seed apparent trend
that turned out to be seed ordering; and reporting a null as a finding rather
than a failure.
