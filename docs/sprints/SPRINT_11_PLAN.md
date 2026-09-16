# Sprint 11 Plan: Correctness Before Compression

**Dates**: 2026-09-10 to 2026-09-11 (evidence freeze Sep 12, target submit Sep 13, hard deadline Sep 15)
**Branch**: `feature/20260910_Sprint_11`
**Scope** (DEFINED, team lead 2026-09-09): F41, F42, F43, F37, F44, F45, F35.

**EXTENDED mid-sprint** by team-lead direction: **F46** (#67, QCi grant landed 2026-09-09) and **F47** (#68). F47 is a HARD GATE -- the team lead's direction is that no further Dirac-3 job runs until it is done.

**DEFERRED to Sprint 12** by team-lead direction 2026-09-09, after the F47 gate
cleared: **F37** (#56, make the repository public) and the **fresh-eyes evidence
review** Phase 5 normally requires. Both are Class 3 scope decisions, made
explicitly rather than inferred.

Consequence, flagged rather than buried: Sprint 12 carries F37, F38, F10, the
fresh-eyes review, and any approved Dirac-3 work, against a Sep 12 evidence
freeze. That is the heaviest sprint of the project against the least calendar.

## Objective

Make every claim in the submission true, and make the tooling catch the next
untrue one. Sprint 10 shipped four defects that two outside readers found and
our own suite did not; three of this sprint's seven cards exist so that cannot
happen again.

**Explicitly NOT this sprint**: F38 (page limits) and F10 (submission), both
planned for Sprint 12. Page size runs after all correctness work so the cut
happens once, against final content.

## Audience-first statement (mandatory, Sprint 4 retro improvement 3)

**F41/F42/F43 reader**: the HSBC judging panel and any reviewer who checks a
number against the repository. They must find that every stated mechanism
matches the evidence, and that a claim we corrected says so plainly rather than
quietly changing.

**F37 reader**: anyone following Appendix C's citation. They must reach the
pinned environment, both checksums, the preregistration and 37 job identifiers
without authenticating.

**F44/F45/F35 reader**: whoever runs this suite next, including us in Sprint 12.
They must get a failing test rather than a reviewer's comment.

## Capability pre-flight (mandatory, run 2026-09-09 BEFORE estimating)

Every number measured today. Two findings changed the plan.

| Check | Card said | Measured now | Consequence |
|---|---|---|---|
| "depth-limited" occurrences | 4 places | **10 across 4 files** | 3 are in the FROZEN preregistration and 3 in the SENT QCi letter. Effort up |
| Tuned arm depth | (implied unbounded too) | **`max_depth` 2/3/4 at `tuned_pool.py:81`** | Only the FROZEN arm is unbounded. The card overgeneralized; the correction must not |
| Next amendment | A20 | A1..A19 contiguous, next is A20 | Confirmed |
| F43 classical AUC-ROC | already stored | LightGBM 0.9139, CatBoost 0.8941, XGBoost 0.8640 | No rerun for the classical half |
| F43 quantum/ladder AUC-ROC | unknown | **absent** from both artifacts | Needs a run, or scope to classical only |
| F42 lambda=0 sweep | "classical run, minutes" | **<1s per start**; 20 starts x 10 seeds is seconds | Gram matrices already saved in `results/pools/` |
| F42 +0.0319 decomposition | "one to a few CPU hours" | **24.0s per seed/fold -> 8 min** for 10 seeds x 2 variants | Measured via `tuned_pool._fold(42, 6)` |
| F37 repo visibility | private | anonymous API 404 | Still private; F40 prerequisite is DONE |
| F44 surface | unknown | 106 decimals in proposal, 174 in appendix | Sizes the consistency-test work |


### Overlap audit (2026-09-09): none of A-G was done in Sprint 10

Checked each task against the repository rather than against its card, because
Sprint 10 fixed correctness findings from the same two reviews and overlap was
plausible.

| Task | Check run | Result |
|---|---|---|
| A F41 | A20 in prereg; "depth-limited" sites; majority-class sentence | **Outstanding** -- 0 A20, 10 sites, claim present |
| B F42 | each Fable finding grepped individually | **Outstanding** -- F6, F7, F9, F13, F16, F17 all still present |
| C F43 | AUC-ROC in proposal/appendix | **Outstanding** -- 0 in proposal, 1 unrelated in appendix |
| D F37 | anonymous API | **Outstanding** -- 404, still private |
| E F45 | hooks dir, pre-commit, CI | **Outstanding** -- no regeneration check anywhere |
| F F44 | test_submission_artifacts.py contents | **Outstanding** -- it tests structure (page size, sections, amendment count), not figure-to-evidence resolution |
| G F35 | full test list | **Outstanding** -- no interpretation-layer test exists |

One item WAS fixed in Sprint 10 and is deliberately NOT re-done: the B.1
registry contradiction listing H3/H6 as NOT RUN. Verified corrected.

## Tasks

Order matters: F41 and F42 share the same lambda=0 analysis, and F44 must
encode corrected values, so it follows them.

| # | Task | Est | Runtime | Dominant cost | Model |
|---|---|---|---|---|---|
| A | **F41** Mechanism + depth correction (#59) | 90m | ~1m | A20 drafting; 10 text sites | Opus |
| B | **F42** Verification + reruns (#60) | 150m | ~10m | +0.0319 decomposition, 8 min measured | Opus |
| C | **F43** IEEE-CIS AUC-ROC (#61) | 45m | ~0m | none for the classical half | Opus |
| D | **F37** Repository public (#56) | 45m | ~2m | full-history confidentiality scan | Opus + **team lead** |
| E | **F45** Evidence-artifact guard (#63) | 60m | ~2m | pre-commit hook + CI wiring | Opus |
| F | **F44** Evidence-vs-document tests | 180m | ~1m | 280 decimals to resolve or register | Opus |
| G | **F35** Interpretation-layer tests | 120m | ~1m | designing what "meaning" tests assert | Opus |
| H | **F46** QCi grant + ceiling probe (#67) | 45m | 1 metered call | queue wait, not compute | Opus + **team lead** |
| I | **F47** Job-id capture and unbuffered logging (#68) | 120m | ~0m | no metered call needed to verify | Opus |

**Total estimate 11h50m against a 2-day sprint.** That is tight but the runtime
risk is now small: the two items the cards called "hours" are measured at 8
minutes and seconds respectively. The residual risk is drafting time on A and F,
not compute.

### Task A -- F41: mechanism and depth correction (90m)

1. Register **A20** recording the corrected mechanism: in-sample memorization by
   unbounded trees, not majority-class collapse. Cite the reproduction (80-84 of
   91 perfect classifiers, 0 all-negative, all ten seeds)
2. Correct "depth-limited" in **10 places across 4 files** -- and state the
   distinction the pre-flight found: the FROZEN arm is unbounded
   (`DecisionTreeClassifier(**{})`), while the TUNED arm sets `max_depth` 2/3/4.
   A blanket "unbounded" would be a new false claim
3. The Loke comparison gets STRONGER: their heterogeneous learners fail on
   different rows; ours memorize the same rows
4. Regression test asserting the perfect-classifier count per saved pool

**Acceptance**: A20 registered; no "depth-limited" claim that contradicts the
code; a test asserts 80-84 of 91 across the ten saved pools; suite green.

**Premise falsifier**: the premise is that memorization explains the Gram
degeneracy. Falsifier: a pool whose perfect-classifier count is low while its
off-diagonal Gram ratio stays at 0.9988. Check before writing A20.

**CLASS 1 AND CLASS 2.** Amends the FROZEN preregistration and changes a
published claim. Team-lead approval of this plan authorizes Phases 4-7, but the
A20 text is shown before it is committed.

### Task B -- F42: verification and reruns (150m)

External source checks (no run): QCi hardware description vs the vendor paper;
CVQBoost Table 1 at ratios 0.01-0.02; Loke's classical bar; Equality Act scope.
Each either confirms our text or produces a correction with a citation.

Classical runs, both measured: the lambda=0 FISTA/SLSQP spread from 20 random
simplex starts across the 10 saved pools (seconds), and the +0.0319
decomposition -- a 4-family k=6 pool with NO class weighting on the same ten
seeds, plus the 9-seed result excluding the selection seed 42 (8 minutes).

**Its convexity finding is the same lambda=0 degeneracy F41 addresses**, so the
sweep runs once and feeds both cards.

**Scope of Task B, made explicit after the overlap audit.** F42's card groups
some findings as "presentation, deferred with F38". Two of those are corrections,
not layout, so they land HERE and not in Sprint 12:

- **F6**: the title says "Quantum-Enhanced" while section 2 says "we do not use
  the phrase quantum-enhanced". A document contradicting itself is a correctness
  defect whatever its cause; also pick ONE paradigm label (section 1 says
  "quantum-inspired candidate", section 2 "hybrid classical-quantum")
- **F16**: "cited requirement. the benchmark's" -- a lowercase sentence start,
  verified still present and introduced in 16618bb, before Sprint 10
- **F13**: "falls from 0.5424 to 0.0734" quotes a bracket BOUND as if it were
  the mean (0.5739). Verified still present. This one misstates a number

Only **F18** (team-capability hours) is genuinely presentation and defers.

**Verified outstanding before planning** (none fixed by Sprint 10): F6, F7, F9,
F13, F16, F17 all still present in the documents. F3 (the B.1 registry
contradiction) WAS fixed in Sprint 10 and is not re-done.

**Acceptance**: every external claim either verified with a citation or
corrected; the lambda=0 spread reported as L1 and objective range; the
decomposition reported as a paired per-seed table; the 9-seed figure stated
alongside the 10-seed one; F6, F13 and F16 corrected in the documents.

**Premise falsifier**: the premise is that the +0.0319 gain survives excluding
seed 42. Falsifier: a materially different mean on 9 seeds. If it moves, that is
a finding to report, not a number to bury.

### Task C -- F43: IEEE-CIS AUC-ROC (45m)

Report the stored classical figures with the leaderboard-mismatch caveat.
**Scope decision to confirm at execution**: the CVQBoost and ladder arms have no
stored AUC-ROC. Options are (a) report classical only and say so, or (b) re-run
those arms. Recommend (a) at T-3; (b) is a Sprint 12 item if wanted.

**Acceptance**: AUC-ROC reported per classical arm; the caveat that the Kaggle
leaderboard test set differs from our rolling-origin folds is stated, not
implied; the figures trace to `ieee_classical.json`.

### Task D -- F37: make the repository public (45m, TEAM-LEAD ACTION)

Full-history scan (history was deliberately not rewritten), confirm no
credential material, confirm licenses permit redistributing derived checksums,
**team lead flips visibility**, verify anonymously logged out.

**Acceptance**: anonymous fetch returns 200 and requirements.txt,
PREREGISTRATION.md and the results store are reachable unauthenticated.

**Premise falsifier**: the scan finds nothing publishable-sensitive after F40.
Any hit outside the known-and-accepted history exposure stops the flip.

**IRREVERSIBLE.** Claude never flips visibility.

### Task E -- F45: evidence-artifact guard (60m)

Pre-commit check that `gate_report.md` regenerates byte-identically from
`results.json`, plus the same check in CI. Chosen over a test helper because it
does not depend on remembering to use one.

**Acceptance**: a deliberate perturbation of `results.json` fails a commit;
the check runs in CI; the existing suite still passes.

### Task F -- F44: evidence-vs-document tests (180m)

Assert every figure quoted in proposal, appendix and team profile resolves to a
value in `results.json` or a named artifact. 280 decimals total; those that are
prose (page counts, dates, percentages of a rubric) get explicitly registered
rather than silently skipped.

**Acceptance**: a deliberate edit to any quoted figure fails a test; every
current figure resolves or is registered; the registration list is short enough
to review by eye.

**Depends on A and B**: must encode CORRECTED values, or it freezes today's
wrong ones into assertions.

### Task G -- F35: interpretation-layer tests (120m)

Three consecutive sprints where the defect that traveled furthest was a claim
about what a number MEANS, not an arithmetic error. Tests that assert the
interpretation: an evidence tag matches the arm that produced it, a "measured"
claim has a results row, a gate marked PASS has its criterion recorded.

**Acceptance**: at least one test that would have caught the B.1 NOT-RUN
contradiction, and one that would have caught the stale 0.26.

### Task I -- F47: job-id capture and unbuffered logging (120m)

**Why it is a gate.** The F46 probe spent an approved metered call and its job id
was never captured, so its runtime is unrecoverable and its cost is known only
from the allocation balance. A metered call whose outcome cannot be retrieved is
the worst case under Criterion H: the safe response to ambiguity is not to
re-run, which stalls the sprint. The team lead's direction is that no further
Dirac-3 work runs until this is fixed.

**What already exists**: `job_query.py` (built 2026-09-09) retrieves status,
metrics and results by id, verified against all 27 retained ids six days on.
That is the RETRIEVAL half. This task is the CAPTURE half.

1. **Capture the job id at submission, before waiting.** This is the whole point:
   it turns a lost connection from a lost call into a re-read. `eqc-models`
   drives the submission internally, so find the seam -- a client hook, a
   response callback, or reading the client's own job record immediately after
   `fit()` starts. If no clean seam exists, wrap `QciClient.submit_job` for the
   duration of the call and record what it returns
2. **Exploit the ObjectId structure as a fallback.** Ids are MongoDB ObjectIds:
   4-byte timestamp, 5-byte per-process random, 3-byte counter. Within ONE
   client process the random field is constant and the counter increments, so
   capturing the FIRST id of a block plus the call count recovers every id in
   that block. Verified against the 27-job campaign, which shares
   `08442f441b` and runs `bb6d1f` to `bb6d3f`. This does NOT recover an id from a
   different process, which is why capture at submission is still primary.
   **Measured, not assumed**: a job_id and the polynomial_file_id from the SAME
   job, created in the same second, carry different random fields
   (`08442f441b` against `ff2f309fb9`). An account-wide or date-derived value
   would match. So the field is per generator, the search space for a foreign
   process is 2^40, and running a fresh job reveals only that job's field --
   the F46 probe's id is permanently unrecoverable, which is the cost this
   card exists to stop repeating
3. **Unbuffered append log per call.** Write each line as received, flushed, so a
   kill or a lost tool result leaves everything up to that instant. The team
   lead's framing: like a terminal capturing keystrokes
4. **Durable ledger recording INTENT before the call**: timestamp, config hash,
   variable count, degree, sample count, expected cost from
   `qpu_cost_model.estimate_for`, then the job id, then the outcome. The existing
   `hw_job_ids.json` records ids only AFTER success, which is the wrong order
5. **Record the measured cost from the allocation balance**, before and after,
   since the paid tier dropped the `device_usage_s` field the repr scrape relied
   on. Feed it back into `qpu_cost_ledger.json` so estimates improve with use

**Acceptance**: killing a submission mid-flight leaves the job id and partial
output on disk; a job id alone retrieves the result afterwards; every metered
request appears in the ledger whether or not it completed; the ObjectId
reconstruction is unit-tested against the 27-job campaign.

**Premise falsifier: RUN 2026-09-09, DID NOT FIRE.** The seam exists and is
better than assumed. Call chain, traced offline:

    QBoostClassifier.fit -> ClassifierBase.solve -> Dirac3CloudSolver.solve
      -> QciClientSolver.solve -> QciClient.process_job(job_body, wait=wait)

`process_job` ALREADY reads the allocation balance before the call, extracts
`submit_job_response["job_id"]`, logs `Job submitted: job_id='...'` under
`verbose`, polls to completion, reads the balance again, and returns
`get_job_results(job_id)`. With `wait=False` it returns the submit response --
containing the job id -- before any result exists.

We never passed `verbose=True` and never captured either value. **The build is
therefore smaller than planned**: drive `process_job` directly with balance
reads around it, rather than wrapping or monkeypatching `submit_job`. That also
retires the repr scrape that produced the F46 probe's wrong 5.0-second figure,
since balance-before minus balance-after is the authoritative cost.

**No metered call is needed to verify this.** The 27 historical ids exercise
retrieval and reconstruction; a fake client exercises capture and crash
behavior. Verification uses zero QPU seconds by construction.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **F41's correction is larger than carded** | **Materialized already** | 10 sites not 4, including the frozen prereg and the sent letter. Estimate raised to 90m |
| A20 wording is wrong in a new way | Medium | The tuned/frozen depth distinction is now explicit in the plan; A20 text shown before commit |
| F44 finds figures that resolve to nothing | Medium-high | That IS the finding. Each becomes a correction or an explicit registration; neither is silent |
| Seven cards in two days at T-3 | Medium | F44/F45/F35 are the droppable tail; blockers F41/F42/F43/F37 come first in order |
| F37 publishes something unintended | Low | F40 shipped; full-history scan precedes the flip; irreversibility respected by sequencing early |
| Hardware budget (Criterion H) | None | Zero metered seconds planned |
| Grant timing | None | F5 held; card #40 awaits QCi independently |

## Decision-Class checkpoints (invariant 7)

- **Class 1**: Task A registers A20 against the FROZEN preregistration. Approved
  in principle by this plan; the A20 TEXT is shown before it is committed
- **Class 2**: Tasks A, B and C change published claims. Any correction that
  moves a reported figure is surfaced, not applied silently
- **Class 3**: if the F44/F45/F35 tail cannot fit, that is a team-lead decision.
  Claude does not drop approved scope on time pressure

## Definition of Done

All seven acceptance blocks met; suite green with the 2 F38 page-limit xfails
still xfail (F38 is Sprint 12); repository anonymously reachable; A20 registered;
tree clean; PR updated and still DRAFT until 7.7.

## Handoff to Sprint 12

F38 and F10. Per team-lead direction, F38 will be informed by ChatGPT 6 and
Fable 5.1 input on (a) the highest-priority MUST HAVE content and (b) how to fit
it into 6 + 3 pages. Current measured gap: appendix needs 229pt cut, proposal
81pt -- and this sprint's corrections will add to both.
