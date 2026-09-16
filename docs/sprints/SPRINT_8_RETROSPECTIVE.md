# Sprint 8 Retrospective

Sprint 8: "The Second Dataset". Cards #43, #44, #45, #46, #48. Plus F37, F38, F39
registered to the backlog.

Team lead feedback recorded VERBATIM as supplied 2026-09-07 (combined Product
Owner / Scrum Master / Lead Developer response). Claude Code Development Team
feedback written after, and it does not soften a rating the team lead gave.

## Sprint 8 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The sprint produced what it set out to: a second dataset run under its
  preregistered protocol, three arms measured, an H3 ladder that is scoreable,
  and three findings that complicate our own story rather than support it. The
  matched-feature control is the single most valuable thing built here, because
  without it 0.0571 reads as a hardware failure instead of a starved feature
  budget.

  Two efficiency failures, both mine and both expensive.

  **Task C ran 84 minutes without finishing one fold and was killed by my own
  timeout.** The cause was a KNN H-matrix build that is O(n_train x n_query) at
  495,902 rows. I audited that task for protocol compliance and never once
  sized its runtime. Compliance and feasibility are different questions and I
  only asked one of them.

  **F36 spent a full card on a problem that did not exist.** I built a pandoc
  Lua filter to reclaim page space that was never wasted, on the strength of a
  measurement my own tool produced. Worse than the wasted time: the card's dry
  run could not have failed. Removing five tables removes their content AND
  their space, so the document was always going to shrink. I designed a check
  that could only confirm.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The strongest testing habit this sprint was verifying that a new test FAILS
  against the code it is meant to catch, rather than trusting that it would.
  Done for the master-plan section test (verified against the deletion), the
  IEEE dedup guard, and all four `test_page_fill_report.py` tests (verified
  against the previous implementation, which has neither `text_extent` nor
  `UNDERFILL_SLACK_PT`).

  **The gap is that a smoke test PASSED on code with four protocol defects.**
  No class weighting anywhere, TransactionID and TransactionDT entering the
  model as raw features, the shuffled-label control never actually run, and a
  minimum detectable effect borrowed from a different experimental design. The
  smoke test asserted the pipeline completes. It asserted nothing about whether
  the pipeline was doing the right thing. Those four were found only because
  the team lead asked for a full sweep before re-running.

  That is the lesson worth carrying: a test that only proves code runs will
  pass on code that is wrong, and it will do so confidently.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Planning estimated 420 minutes across four tasks and named explicitly that
  this exceeded the card's "~1 day" because Task A had not existed in the
  original card. Being honest about an estimate rising is better than absorbing
  the difference silently, and the sprint delivered all four tasks.

  Two estimates were wrong in the same way: **I estimated code-writing time and
  called it task time.** Task C's 120m covered writing the runner, not running
  it, and the run alone consumed 84 minutes before failing. F36's 75m covered
  building the filter, not discovering the premise was false.

  Any task whose output requires a long compute run needs its runtime sized
  separately from its implementation, at planning, on the actual row count.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The task ordering was correct and it mattered: Task A (protocol compliance)
  first, with the stated fallback that C and D compress before B, because a
  classical baseline on a non-compliant protocol is worth less than no baseline.
  That reasoning held when the schedule came under pressure.

  The planning defect is that F36 was planned in detail from an unverified
  premise. The card has seven falsifiable acceptance criteria, a stated
  completion-is-effectiveness rule, and a dry run. All of that rigor was applied
  downstream of a number I did not check. Card quality does not compensate for a
  wrong premise; it makes a wrong premise more expensive by making it look
  examined.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Work stayed on this model throughout, which suited a sprint that was mostly
  protocol reasoning, failure diagnosis and writing under a page limit. No
  subagents were spawned. Given that the two big errors were both errors of
  judgment rather than of throughput, delegation would not have helped.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The heartbeat mechanism worked: JSON progress files plus flushed prints gave
  real evidence of liveness during long runs, and the 20-minute status cadence
  answered "is this working" without interrupting the work.

  Two communication errors. **I diagnosed Task C as possibly hung when it was
  merely slow**, and projected completion times from an incomplete picture.
  **I mistook a stale results file for a completed run**, caught only by
  comparing file mtime against run start. Both were cases of reporting an
  inference as an observation.

  I also stated after Task C that the variable ceiling was the binding
  constraint, and H3 then contradicted it. Recording the contradiction
  explicitly was right; making the claim from one task's evidence was not.

### 7. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  No subagents were used. Self-assessment of my own code: the IEEE runners are
  sound and the controls module is a genuine improvement (replacing
  `permutation_importance` with a rank-based top-feature check cut about three
  CPU-hours to 46 seconds without weakening the control).

  The recurring defect is mine and it is now on its third occurrence: **heredocs
  mangling LaTeX and regex escapes.** It happened again this sprint on the Lua
  filter, leaving a literal newline inside a string. The standard requiring a
  scratchpad file for escape-heavy content was already written, by me, and I did
  not follow it until after the failure.

### 8. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Direction was clear throughout, including the reframing that our participation
  is exploratory and nothing now determines the final outcome, which correctly
  changed how the IEEE results were written up.

  Where I needed clarity I mostly got it by asking at the right moment rather
  than blocking: the Appendix C repository question was worth asking because the
  repo being private changed what could be written. The deferred page overage
  was resolved the same way.

### 9. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  `docs/reviews/f36-float-tables-outcome.md` documents a failure in full, with
  the false premise preserved as written and labeled, so nobody rebuilds it.
  The F36 card in the master plan carries its verdict at the top for the same
  reason. Recording a failed card properly is worth more than the card was.

  The B.1 compound-falsification statement closed a real gap: our
  preregistration names its own falsification test, two of three conditions are
  now measured against us, and the submission was silent on it. That silence
  would have read as avoidance.

  The documentation defect: I let the QCi letter carry "twelve amendments" when
  the enclosed preregistration had seventeen. A letter enclosing a document and
  miscounting it undercuts the accuracy it claims. This is exactly the class of
  error the team lead's fact-database proposal (F39) targets.

### 10. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  **The master-plan roadmap section was destroyed by my own prune script for a
  second time**, and had been missing since commit c40038d, a full sprint. The
  script walked from a card header to the next card header and consumed a `##`
  section heading in the span. Recovered from be1198c; the prune now stops at
  any `##` and a test was added and verified to fail on the deletion.

  A destructive script that has damaged the same file twice should have been
  fixed the first time. It was not, and the second loss went unnoticed for a
  sprint.

### 11. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Zero metered seconds were spent this sprint, all results tagged [SIM]. Given
  a constrained QCi balance and no grant, running the entire second dataset on
  the classical proxy was the right call and it cost nothing.

  Risk work I would call good: the F36 filter was left opt-in rather than wired
  into `render-all.ps1`, which is why discovering it costs `gate_report.pdf` a
  page was a finding rather than an incident. Registering F37 (repo public) and
  F38 (appendix to 3 pages) as explicit submission BLOCKERS rather than
  ordinary cards reflects that both are binary submission failures.

  Risk I underweighted: I let a task run for 84 minutes without a runtime
  estimate against it, eight days from a deadline.

### 12. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Sprint 9 is well defined: F4, paper updates, and the QCi package send, now
  moved from Sep 7. Two submission blockers are registered with their
  measurements already recorded, so neither needs rediscovering. The one failing
  test is the tracked appendix overage, failing by design.

  Carried debt into Sprint 9: the appendix at 4 of 3 pages (F38), the repository
  still private (F37), and the team lead's remaining QCi letter feedback
  outstanding.

### 13. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The IEEE work followed the established shape: a loader that enforces protocol,
  controls as testable functions, runners that write tagged results. A17 is the
  standing warning here -- three fold builders written as standalone modules
  bypassed the shared loader and therefore inherited none of its protocol
  enforcement. The IEEE code was written through the loader for exactly that
  reason.

  `render-pdf.ps1` gained one optional parameter, and `render-all.ps1` was left
  untouched, so the default render path is byte-identical to before the sprint.

### 14. Minor function updates needed in the next sprint plan

- **Team lead**: none
- **Claude Code Development Team**: none beyond the registered blockers F37 and
  F38, both already in the Finalize row.

### 15. Function updates for the backlog

- **Team lead**: A fact database. A simple table (json, sqlite or simpler) that
  we can rely on for creating the content in all the documents. It states facts
  that we can confirm with confidence intervals between 0.0% and 99.9%. There
  are likely over 1,000 and this makes it difficult to keep track of and ensure
  all of them are correct every time; if we need to update the baseline facts it
  should be here and then all other sources use this as the basis. Research
  Cycorp / cyc.com for how they do it; functionally representative rather than a
  duplicate (we do not have to use LISP). May be held until after submission.

  **Registered as F39, Priority 2, HOLD until after submission.**

- **Claude Code Development Team**: F39 is the correct diagnosis of a real
  failure mode, and this sprint supplied three instances of it: the "twelve
  amendments" error, A15 (a five-seed mean carried into a ten-seed writeup), and
  A17 (every A11/A13 figure recomputed across four documents). Each was caught by
  a human reading or a one-off script.

  The confidence field is the part I would emphasize. This project already
  separates measured from projected via evidence tags, but not strong-measured
  from weak-measured. The score-degeneracy caveat, the single-seed spot checks
  and the adversarial control that never converged are asserted with genuinely
  different confidence, and today that lives only in prose.

### 16. Questions to be discussed before ending the sprint

- **Team lead**: none
- **Claude Code Development Team**: none. The remaining QCi letter feedback is
  expected in Sprint 9 and the send has moved there.

## Summary

Sprint 8 delivered its scope. IEEE-CIS ran under its preregistered protocol,
three arms were measured, the H3 ladder is scoreable at 12 cells, and the
results were written up including the parts that work against us. Zero metered
seconds were spent. All 16 categories rated Very Good by the team lead.

The sprint's two failures share one cause: **I acted on numbers I had not
verified, and designed checks that could not fail.**

- F36 built a filter for wasted page space that did not exist. The premise came
  from my own tool counting characters, which makes any table-heavy page look
  short. The card's dry run could only confirm.
- The Task C smoke test passed on code with four protocol defects, because it
  asserted the pipeline completes rather than that it is correct.

Both were found by the team lead asking for verification, not by any check I had
built. The corrections are in place: `page-fill-report.py` now measures vertical
extent and excludes the folio, with four regression tests that fail against the
previous implementation.

The best work this sprint was the matched-feature control, the decision to run
everything classically at zero cost, and recording the F36 failure fully enough
that nobody repeats it.
