# Sprint 6 Retrospective

Sprint 6: "The Diverse Pool". Cards #31-#35. PR #36. Four concurrent tracks.

Team lead feedback recorded VERBATIM as supplied 2026-09-05 (combined Product
Owner / Scrum Master / Lead Developer response). Claude Code Development Team
feedback drafted per protocol step 2.

## Sprint 6 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The best sprint of the project on outcome: the central open question got a
  measured answer, three prep tracks landed in parallel, and the metered block
  came in at 43 s of a 40-50 s approval. The capability pre-flight is why. Twenty
  minutes of spike work answered F31's core question and cut its estimate from
  6-10 hours to 180 minutes, because it found that eqc-models takes one
  `weak_cls_type` per build and that all four families build in under ten seconds.
  Without it I would have estimated blind and probably built the wrong thing.

  The inefficiency was concentrated in one place: I burned roughly eight
  render-measure-trim cycles on page limits AGAIN, exactly as in Sprint 5, and for
  the same reason -- trimming prose before measuring where the page break falls. A
  table was forcing an early break and wasting most of page 1 both times. The fix
  is to measure first, and I did not carry that forward from the last
  retrospective even though I wrote it down there.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The artifact tests written at the end of Sprint 5 paid for themselves within a
  day: both the proposal (7/6) and the appendix (4/3) went over limit during the
  section 3 rewrite, and the tests caught both before the team lead saw them. That
  is the first time this project's automation caught a submission defect rather
  than a human question catching it.

  The known-answer tests for the mixed pool were the right investment. Two of them
  fail if the diversity metric cannot separate a degenerate pool from a diverse
  one, which is the load-bearing claim of the whole sprint. Writing a metric and
  trusting it would have been the easy path.

  What the tests did NOT catch: three schema defects in my own F32 runner
  (`config` vs `config_hash`, missing `feature_set`, missing `pair_build`). Each
  would have raised KeyError in a consumer. I found two by reading the consumer
  code and one by running the suite. A row-schema contract test would have found
  all three at once.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Best of the project. F31 estimated 180 m after the pre-flight and ran close to
  it. The three agent tracks came in at 13, 13 and 43 minutes of wall time against
  120, 150 and 150 minute estimates -- so agent work is roughly 0.2-0.3 of
  estimate, consistent with Sprint 4's research-agent ratio of 0.2. I should
  estimate agent tasks at a third of what I would estimate for main-loop work.

  F32 was estimated 90 m and consumed far more, because it failed three times
  before succeeding. None of those failures was in the estimate: a schema defect,
  a device refusal, and a spend-accounting bug. Metered work needs a contingency
  multiplier that authored work does not.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The plan held and the defined-scope rule was respected. The pre-flight section
  in the plan document was new this sprint and was the single most valuable part
  of it: it turned an unknown into a sized task before any commitment.

  One planning gap: the plan assumed F32 would run on the k=13 mixed pool and
  never asked whether 312 variables would fit the tier we are actually on. A
  sizing check against the FREE tier, not the documented device limit, belonged in
  the plan. The mandatory capability pre-flight is designed to catch exactly this
  and I ran it for the pool build, not for the submission size.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Correct. Three Sonnet agents on bounded prep tasks with hard constraints, main
  loop (Fable) on the decisive experiment, the metered spend and the paper. The
  division held: nothing needed escalation, and the agent output needed no rework.
  Keeping F31 in the main loop was right, since its result rewrote the proposal.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Improved. Each finding went to the team lead with its counter-evidence attached
  in the same message: the mixed-pool win came with the absolute-AUPRC drop, the
  B4 request came with its own negative dry run, and the ADR questions came with
  pros, cons and a recommendation rather than an open-ended ask.

  Two lapses. I reported "6 fits, 25.0 seconds" alongside a "STOP at 50.0s"
  message in the same output and did not immediately flag the contradiction as a
  bug -- I investigated, but a reader would have seen an inconsistency I had not
  named. And I told the team lead F32 was "running" three times for what were
  three different runs after two failures; the status was accurate each time but
  the sequence was not made clear.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The free-tier ceiling is the finding of the sprint on this axis. We had a
  documented 949 limit, an amendment (A2) reasoning about it, and a sentence in
  the proposal drawing a conclusion from it -- and the actual binding constraint
  was a different limit we had never tested. The requirement was not unclear; our
  inference from it was wrong, and nothing in the process tested the inference
  because the frozen pool sat under the ceiling by accident.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Strong. A11 and A12 both registered before the work they cover was used
  anywhere. ADR-0013 recorded both decisions with the reasoning, so Sprint 7 does
  not re-derive them. B4's deferral is recorded AT THE TOP OF THE REQUEST ITSELF
  with re-present conditions, so the reasoning travels with the artifact rather
  than living in a conversation.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  - Python's stdout buffering makes `run_in_background` output invisible until
    exit. I checked empty files four times before diagnosing it. `-u` fixes it and
    should be default for every long-running run.
  - An edit script that asserts on several anchors and writes at the end loses ALL
    edits when one anchor fails. This bit me again (the QCi cover), the second
    sprint running. Write after each edit, or verify the file after.
  - Bash loops piping render output through `grep` swallow failures and return
    misleading exit codes. Cost me a false "3 of 3 pages" reading.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  The metered-spend risk was well managed in the end -- 43 s of 40-50 approved,
  every failure caught before billing, zero wasted seconds across three failed
  attempts. But the guard itself had two defects: a cap I initially set at 60 s
  when 50 was approved, and a double-count that halted the block at half its real
  spend. A spend guard whose own arithmetic is wrong is a risk, not a mitigation.
  Both were mine and both were found by reading rather than by a test.

  The deadline risk is now acute: 10 days, and the proposal is at 6/6 with a
  finding that may still change.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Ready. Carry-forward branch is due at merge. F31's result is registered and the
  team lead has deferred the framing decision to Sprint 7 deliberately. F3, F4 and
  F5 all have tested scaffolding waiting.

  The open question for Sprint 7 planning: whether to extend F31 (tune the mixed
  pool toward Loke et al.'s >0.8) or execute F3 as the roadmap says. F31 currently
  buys optimizer headroom without accuracy, and closing that gap is the difference
  between "a direction" and "a result".

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  No protocol drift. A11 and A12 are analysis and measurement amendments that
  change no gate criterion, and I verified this rather than asserting it: the
  regenerated gate report is byte-identical to the previous one, so no frozen
  figure moved despite 10 new hardware rows entering the store.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:

  - [DEV] Add `-u` to every long-running background python invocation, and note it
    in WINDOWS_POWERSHELL_GUIDE -- target: Sprint 7 plan, est: 10m
  - [DEV] Add a results.json row-schema contract test asserting every row carries
    the fields its consumers read (config_hash, feature_set, pair_build, arm,
    evidence_tag) -- target: Sprint 7 plan, est: 30m
  - [DEV] Add a free-tier sizing pre-check to the hardware runner that computes
    variable count and refuses to submit above 100 locally, so the device never
    has to refuse -- target: Sprint 7 plan, est: 20m
  - [DEV] Measure page-break positions BEFORE trimming prose when a document is
    over limit; add a helper that reports per-page fill -- target: Sprint 7 plan,
    est: 20m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:

  - [DEV] F33: Tune the mixed pool toward the Loke et al. configuration (their
    learner families at their hyperparameters), to test whether the 0.7565-to-0.8
    gap is tuning rather than composition -- estimated: 4-6h classical, priority 1,
    depends on: F31 (done)
  - [DEV] F34: Spend-guard property tests (cap never exceeds approval;
    double-counting impossible; unparseable billing charged conservatively) --
    estimated: 1h, priority 3, depends on: nothing

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**:

  Excellent, and better than I expected. All three delivered working, tested code
  with no rework, and all three respected hard constraints I could verify
  independently: results.json stayed at exactly 147 rows across all three, no arm
  was fit, no metered call was made. Agent C additionally caught and corrected its
  own false-positive file path with three independent tools before relying on the
  result, and reported the check rather than hiding it.

  The reports were honest about judgment calls -- six documented for F3 prep, two
  flagged for team-lead review in F23 -- rather than presenting choices as
  inevitable. Agent B's A2 variable-count finding was the most valuable single
  piece of agent output this project has had, and I verified its arithmetic
  independently rather than taking it.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:

  1. Sprint 7 scope: extend F31 toward the Loke configuration (F33), or execute F3
     as the roadmap says? F33 is the higher-value item if the goal is a result
     rather than a direction, but F3 is the roadmap commitment.
  2. The proposal is at 6/6 with a 5-page target the team lead called desirable
     but not required. Worth one deliberate trim pass in Sprint 7, or leave it?

## Improvement Decisions

Proposed after the combined feedback (step 5); disposed by the team lead
2026-09-05 (step 6): "improvements all now".

| # | Improvement | Type | Effort | Disposition | Status |
|---|---|---|---|---|---|
| 1 | `-u` on every long-running background python invocation | Tooling | 10m | APPLY NOW | Done: WINDOWS_POWERSHELL_GUIDE, with the failure it caused |
| 2 | results.json row-schema contract test | Testing | 30m | APPLY NOW | Done: `test_row_schema.py`, 6 tests |
| 3 | Free-tier sizing pre-check in the hardware runner | Safety | 20m | APPLY NOW | Done: `check_free_tier_size`, refuses >100 vars locally |
| 4 | Measure page-break positions before trimming prose | Tooling | 20m | APPLY NOW | Done: `scripts/page-fill-report.py` |
| 5 | F33 tune the mixed pool toward Loke et al. | Experiment | 4-6h | BACKLOG, priority 1 | Registered; team lead selected for Sprint 7 |
| 6 | F34 spend-guard property tests | Testing | 1h | BACKLOG, priority 3 | Registered |

Improvement 2 immediately found a real gap on first run: 27 Sprint 4 hardware
rows lack the `metered_seconds_parsed` audit flag, which arrived with amendment
A8. Their spend IS fully recorded (120.0 s, verified), so this is a provenance
gap in historical rows rather than an accounting failure, and the test is scoped
to blocks written after A8 with that reasoning recorded in the code.

Improvement 4 immediately produced a finding the two previous trim cycles had
missed: proposal page 1 sits at 70% of median fill because the title block ends
it early, so roughly 1,400 characters are reclaimable there without cutting any
prose.

## Team lead answers to Category 16

1. **Sprint 7 scope, F33 or F3?** F33 in Sprint 7, F3 in Sprint 8: "we get both
   done easily as we are doing > 1 sprint per day". The roadmap is renumbered
   accordingly rather than treating the two as competing for one sprint.
2. **Trim the proposal below 6 pages?** "leave for now."
