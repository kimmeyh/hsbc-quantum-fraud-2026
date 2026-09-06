# Sprint 7 Retrospective: Claude Code Development Team draft

Sprint 7: "Direction into Result". Cards #38, #39, #40. PR #41.

### 1. Effective while as Efficient as Reasonably Possible

The right outcome: F33 answered its question, F34 closed the gap that three
sprint defects had opened, and the QCi letter carries a finding worth a vendor's
attention. The two-stage design (sweep on one seed, then ten seeds on the
selection) was the correct shape and kept the expensive stage to one run.

The waste was again page limits, and this time it was worse than Sprint 6
because the tool that diagnoses it correctly already existed. `page-fill-report`
said "FIX THE BREAK, not the prose" and named the underfilled page on the FIRST
run. I then trimmed prose four more times before acting on it. The actual cause
was pandoc's `\maketitle` band wasting ~1400 characters of page 1 while ~300
spilled. Building the tool and then ignoring its output is a worse failure than
not having it.

### 2. Testing Approach

F34 is the strongest testing work of the project: eight property tests where
each asserts the property whose violation caused a real defect, and I verified
they FAIL on the originals rather than trusting that they would. Re-introducing
the 60s cap and the first-found billing each broke its test.

The gap: nothing tested the interpretation layer. The feature-count mismatch
(k=6 tuned against k=13 comparators) and the validation-versus-test confusion
were both caught by reading, not by any check. A comparator-matching assertion
in the analysis modules would have caught the first mechanically.

### 3. Effort Accuracy

Task A estimated 150 m and ran close to it once the pre-flight had sized it;
Task B estimated 60 m and came in near that. Task C estimated 90 m and overran,
entirely on page-limit cycles that were not in the estimate and should have
been, since the same overrun happened last sprint.

The pre-flight continues to be the highest-leverage 20 minutes in the process:
it confirmed per-family hyperparameters pass through before any estimate was
committed.

### 4. Planning Quality

The plan was written to the workflow's own template this time, with a pre-flight
section, quantifiable acceptance criteria and a risk register that stated in
advance what a null result would mean. That last part earned its place: when the
sweep pointed one way and the ten-seed run went the other, the plan already said
which readings were legitimate.

One planning miss: the plan named "absolute AUPRC against the frozen pool
(0.7681)" as an acceptance criterion without noticing that the frozen figure is
k=13 and the tuned arm would be k=6. The criterion as written invited the
mismatched comparison. Caught in execution, but it belonged in planning.

### 5. Model Assignments

Main loop throughout, no subagents. Correct: F33 is the decisive experiment and
its result rewrites the paper, F34 needed knowledge of three specific defects
from prior sprints, and Task C is document work where context continuity
matters. Nothing here was parallelisable prep of the kind Sprint 6 delegated.

### 6. Communication

Better than Sprint 6 on findings: the F33 result went to the team lead with its
caveats attached in the same message rather than as a follow-up, and both
corrections to my own interpretation were stated plainly.

One lapse worth naming. I told the team lead "every candidate's validation AP
sits below the frozen pool's level, so the ten-seed result is unlikely to clear
0.7681" and framed it as a prediction recorded for honesty. It was an
apples-to-oranges comparison, and presenting it confidently made it worse than
saying nothing.

### 7. Requirements Clarity

The team lead's approval arrived on a slate rather than a plan document, and I
noted that explicitly before proceeding rather than treating the slate as the
plan. That was the right call and cost nothing.

### 8. Documentation

A13 was registered BEFORE the ten-seed run with its scope limits stated in
advance, which is the discipline working as intended. A14 records the matched
comparator and both of my interpretation errors, so they survive in the
amendment log rather than in a conversation.

The Phase 2 deferral is recorded with the actual argument on both sides, so
whoever picks it up after submission does not re-derive it.

### 9. Process Issues

- Python edit scripts with escaped LaTeX in string literals fail on
  `unicodeescape`. Third occurrence of a variant of this. The fix that works is
  writing the script to a file rather than heredoc-ing it, which I did after the
  second failure this sprint but not the first.
- The page-limit cycle needs a rule, not just a tool: run `page-fill-report`
  FIRST and act on its verdict before touching prose.

### 10. Risk Management

The metered path was untouched this sprint (zero seconds), and F34 hardened it
for the next campaign. Deadline risk is now the live one: 10 days, and the
submission is in good shape but the QCi letter is still open pending team-lead
feedback.

The risk that materialised was interpretive rather than operational: two
comparison errors in one sprint, both mine, both caught before publication but
neither caught by a test. That is the same class as Sprint 5's "exactly uniform"
and Sprint 6's conflated configurations. Three sprints running, the defects that
reach furthest are claims about what a number MEANS, not the numbers themselves.

### 11. Next Sprint Readiness

Ready. Sprint 8 takes F3, whose scaffolding was built and tested in Sprint 6, so
it should move fast. The QCi letter needs the team lead's feedback before the
Monday send. Card #40 stays open for that.

### 12. Architecture Maintenance

No protocol drift. A13 and A14 change no gate criterion and no gate was
rescored. The tuned pool is a new exploratory arm reported alongside the frozen
one, never replacing it.

### 13. Minor Function Updates for the Next Sprint Plan

- [DEV] Add a comparator-matching assertion to the analysis modules: any
  reported difference between two arms must carry matching k and protocol, or
  fail -- target: Sprint 8 plan, est: 30m
- [DEV] Make `page-fill-report` the mandatory FIRST step when a document is over
  limit, recorded in QUALITY_STANDARDS -- target: Sprint 8 plan, est: 10m
- [DEV] Write edit scripts to the scratchpad rather than heredoc when they carry
  LaTeX or regex escapes -- target: Sprint 8 plan, est: 5m

### 14. Function Updates for the Future Backlog

- [DEV] F35: Interpretation-layer tests -- assert that a claimed comparison uses
  matched configurations, that validation and test figures are never compared
  across arms, and that any quoted difference names its comparator's parameters
  -- estimated: 2h, priority 2, depends on: nothing

### 15. Assigned Coding Agents Quality

No agents assigned this sprint, so nothing to assess. Worth noting for contrast:
Sprint 6's three agents produced no rework, while the two defects this sprint
were both mine, in the interpretation layer that no agent touched.

### 16. Questions to be discussed before ending the sprint

1. Sprint 8 is F3 per the roadmap. Does the F33 result change anything about how
   F3 should be run -- specifically, should the IEEE-CIS arms use the tuned pool
   configuration rather than the frozen one, given that tuning is now measured as
   where the accuracy lives?
2. The QCi letter is held for team-lead feedback before the Monday send. Is
   there anything in the F33 account that should be framed differently for a
   vendor audience?
