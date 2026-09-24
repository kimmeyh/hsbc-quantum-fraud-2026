# Sprint 18 Plan: The First Phase 2 Evidence, and the Cost of the Ask

**Sprint**: 18
**Branch**: `feature/20260922_Sprint_18`
**Dates**: 2026-09-22 onward
**Scope**: F87, F64, F88, F89
**Metered Dirac-3 seconds**: NON-ZERO. ONE approval stop.
**F2b DEFERRED** to its own sprint (F90); see the scope note.

## Objective

Turn the two open outward commitments into measured numbers, and close the two
verification-defect cards that Sprint 17 paid for.

The QCi package cannot be sent while the hardware plan says "we are not quoting
a cost". Appendix B.3 cannot stop declining its own headline confound while the
k=17 order-2 cell is unrun. Both are single experiments. Everything else in this
sprint exists to make those two defensible.

## Scope note: F2b is deferred, and the reason is evidence, not cost

The team lead selected F2b for this sprint. **It is deferred to F90 after the
pre-flight invalidated the configuration this plan first proposed for it.**

The first draft ran B4 at schedule 2 (153 variables, about 75 s) on the
argument that A31's resolution limit made schedule 3 a worse experiment rather
than merely a costlier one. **That argument was wrong, and the team lead caught
it.**

- **Schedule 2 is a configuration already shown to lose.** In the prior SPECTRA
  work, at schedule 2 the classical arm swept overall 8 of 8 and CVQBoost won
  only about 3 in-segment metrics. At schedule 3 CVQBoost leads in-segment on
  ROC 5 of 7 and PR 6 of 7, and wins overall on energy_steel. Schedule 3, which
  adds three-feature interactions, is the accuracy lever. Spending 75 seconds
  to reproduce a losing configuration is not a cheap experiment; it is a
  worthless one.
- **The A31 argument was inverted.** A31 predicts the MECHANISM -- weight over
  more than about 200 learners is not representable, so the device returns
  something sparser. It does not predict a bad OUTCOME. B2 ran at exactly 833
  variables with weight cosine 0.83 and produced the campaign's only positive
  result at scale, +0.0256 on ten of ten seeds. The sparsified answer was
  BETTER. Using A31 to argue against 833 variables contradicts our own headline
  evidence, and it is the same inversion the team lead corrected in the
  833-variable paragraph at Sprint 17 Manual Validation.

**So B4 belongs at schedule 3, which costs about 1,236 s -- 63% of the 1,961
remaining.** That is an allocation decision deserving its own sprint and its own
approval, not a task bundled behind eight others. F90 carries it with the cost
quoted.

Deferring costs little: B4 and B5 are post-submission work on the current
calendar and block nothing.

## Audience-first statement (mandatory, SPRINT_PLANNING.md)

**F87's reader is QCi's technical staff**, who will read a cost figure and
decide whether our estimates are measured or invented. Every number this sprint
produces about device time must carry its provenance as `measured` or
`extrapolated`, never `unknown`.

**F64's reader is a reviewer of Appendix B.3**, who currently reads that the
disconfirming cell was not run.

**F88 and F89's reader is a future session on a machine that is not this one.**

## Capability pre-flight (run 2026-09-22 BEFORE estimating)

**F87 — the integer path does not exist yet, and that changes the shape.**
- `Dirac3IntegerCloudSolver` exists in `eqc_models.solvers` with a clean API:
  `solve(model, relaxation_schedule, num_samples, ...)`.
- **`num_levels` is NOT a solve parameter.** It comes from the model's
  `upper_bound`, which sets the integer encoding. The card assumed it was a
  solve knob. Sizing the block means choosing `upper_bound`, not passing a
  number to `solve()`.
- No integer-solver path exists anywhere in `experiments/src/`. This card
  BUILDS a submission path and then probes it. That is the estimate driver,
  not the probe.

**F64 — runtime is small and the physics prediction is live.**
- Pool construction grows with the square of pool size: measured 12 min/fit at
  833 variables, so 153 variables is roughly 25 s/fit. Ten seeds is minutes.
- Zero metered seconds. Classical proxy only.
- **THE CARD CARRIES ITS OWN WITHDRAWAL and it is not stale.** F64 was selected
  for Sprint 13 and withdrawn the same day on methodological grounds: it varies
  ONE axis with everything else frozen at values chosen for a different
  configuration, so it measures the axis it varies and is silent about the
  interaction. That objection still stands and is addressed in Task C's design,
  not ignored.

**F2b — B4's cost is a 16x decision, and the physics picks the side.**

The schedule-3 QUBO size is `n + C(n,2) + C(n,3)`:

| dataset | n | schedule 2 | schedule 3 | fits the ~940 ceiling? |
|---|---|---|---|---|
| maintenance_ai4i | 12 | 78 | 298 | yes |
| oilgas_gasturbine | 15 | 120 | 575 | yes |
| energy_steel | 17 | **153** | **833** | yes |
| telecom_churn | 18 | 171 | 987 | **no** |

- **`energy_steel` at schedule 3 is EXACTLY 833 variables — our B2 size.** B2's
  measured 82.4 s/fit is therefore a direct anchor, not an extrapolation.
- 15 fits at that rate is **1,236 s, which is 63% of the 1,961 remaining**.
- At schedule 2 (153 vars) B3's rate applies: about **75 s, or 4%**.
- **A31 decides it.** At 833 variables a uniform weight is 0.0012, below the
  ~1/200 representable floor, so the device must return something sparser --
  which is exactly what produced B2's 0.83 weight cosine. At 153 variables the
  weight is 0.0065 and IS representable. Schedule 3 would pay 16x more to hit
  the same wall we have already measured and published.
- **B4 therefore runs at schedule 2 unless the team lead directs otherwise.**
- B5 (QSVM, 12 fits) sizes like B3: **15-62 s**. Cheap under any balance.
- **B4 overlaps F5** (SPECTRA in-segment replication, on HOLD). They are the
  same block from two angles. F90 reconciles them before B4 runs; F5's own
  HOLD reason ("needs the QCi grant, which has only been acknowledged") is
  stale, since the grant arrived 2026-09-09.

**F88** — the two Sprint 17 false findings are both reproducible from committed
artifacts, so the acceptance test has real inputs.

**F89** — the six green injections are all documented with their exact
mutations, so the helper has six regression cases on day one.

## Tasks

Order is deliberate: zero-cost evidence first, then the cheap metered block,
then the expensive one, with the tooling cards between the approval stops.

### Task A: Build and classically verify the integer path (F87) (~90m)

`Dirac3IntegerCloudSolver` against a local model, end to end, with NO metered
call. Establish the `upper_bound` to `num_levels` relationship and the variable
budget against the documented 949 limit.

- **Acceptance**: the path runs to completion classically or against the
  simulator, with a stated variable count and encoding. A probe that fails on
  the device because of a bug in our own submission code costs seconds and buys
  nothing.
- Zero metered seconds.

### Task B: Probe the integer solver (F87) (~30m + APPROVAL STOP) [METERED]

- **Block**: integer sizing probe. **2-3 calls.**
- **Expected seconds: UNKNOWN, bounded by call count.** We have never run this
  solver on this problem and no comparable anchor exists. Per Criterion H the
  estimate is classified `unknown` and the block is bounded by calls, not by a
  quoted figure. That figure is what the card exists to establish.
- **Acceptance**: seconds per fit at a named variable count and `num_levels`,
  landing as `[HW]` rows; plus a scaling basis across two sizes if the first
  call's cost permits a second.

### Task C: The k=17 order-2 cell (F64) (~60m)

Ten seeds at 153 variables, same protocol as its two neighbors.

- **THE WITHDRAWAL OBJECTION IS ADDRESSED, NOT IGNORED.** The Sprint 13
  withdrawal was right that a one-factor probe is silent about interaction. The
  cell is therefore reported as **a bound, not an attribution**: if the gain
  appears at 153 variables, k explains at least part of it; if it does not,
  three-feature learners are necessary. Neither outcome claims the interaction
  is absent, and the write-up says so.
- **A31 predicts the answer**, which is what makes it a test: at 153 variables
  the optimum IS representable, at 833 it is not.
- Zero metered seconds.
- **Acceptance**: B.3 states the decomposition as a bound instead of declining
  it. If the result changes what +0.0256 is attributable to, that is an
  amendment.

### Task D: Injection helper (F89) (~120m)

A shared helper that mutates, **re-reads through the same accessor the test
uses**, and fails loudly if the target value is still reachable.

- `replace()` without a count, plus an assertion that the occurrence count went
  to zero. The `0.7671` case failed because three occurrences existed and one
  was replaced.
- **Acceptance**: all six Sprint 17 green injections replayed through the
  helper and each reported as a FAILED injection rather than a passing guard.

### Task F: False-finding mechanism (F88) (~150m)

Design and build, with the two Sprint 17 instances as the acceptance test.

- Candidates named in the card: a guard recognizing contradiction language that
  demands a named artifact citation; a `verify_claim.py` that reports every
  file mentioning a figure; a check that a claim naming an amendment has had
  the log read this session. **The spike picks one**; the card does not
  pre-commit.
- **Acceptance**: both Sprint 17 instances caught BEFORE the claim is
  committed. Proven by injection, not asserted.

### Task I: Update the QCi package with the measured figures (~60m)

The card is not done until both documents carry the number.

- `Phase 1 - QCi memo.txt`: the "how the remaining seconds get used" section
  currently lists the probe as item 1.
- `Phase 1 - Hardware Plan for Phase 2.pdf`: replace the no-quote paragraph.
- **Acceptance**: `test_qci_document_requirements.py` extended so the no-quote
  sentence cannot return, and the new figure traces to a results row.

## Estimate

Derived from the cards and their dependencies, then recorded (SPRINT_PLANNING.md,
Sprint 17 improvement 1). The plan reports this total; it does not originate it.

- A 90 + B 30 + C 60 + D 120 + F 150 + I 60 = **510 minutes**
- Verification-dominated portion (A, B, C): 180m -> 30% = **54m**
- **Total: 564 minutes, 9.4 hours**

Dependencies that constrain ordering, not cost: B follows A; I follows B.

(Was 739 minutes across nine tasks before F2b was deferred. Computed by
summing, not asserted -- the first draft of this plan said 95m of allowance
against an actual 94m.)

## Metered summary (Criterion H)

ONE block, one approval stop. Nothing runs on this plan's approval.

| Block | Calls | Expected | Provenance |
|---|---|---|---|
| Integer probe (Task B) | 2-3 | **unknown** | no comparable anchor; bounded by call count |

The block is bounded by CALL COUNT rather than by a quoted second figure,
because that figure is what the card exists to establish. If the first call is
expensive, the second does not run without a new approval.

B5 and B4 moved to F90 with B4 quoted at about 1,236 s (schedule 3).

## Premise falsifier (mandatory)

**Premise**: the integer path can be built and exercised end to end
classically, so the metered probe measures the DEVICE rather than a bug in our
own submission code.

**The check**: Task A must run the full path to completion with no metered
call. If it cannot -- if the only way to exercise the path is to submit a job
-- then the probe is not a probe, it is a first attempt, and its cost is
unpredictable in a way the card does not allow for.

**It can fail**, and that is the most likely place for this sprint to be wrong.
`Dirac3IntegerCloudSolver` is a CLOUD solver; whether a local or simulated
exercise of the same model is possible is unverified. Task A's first job is to
find out, and if the answer is no, Task B stops for a re-scoped approval rather
than proceeding.

(The previous falsifier here concerned B4 at schedule 2. It was retired with
the task: the premise it tested turned out to be false before the sprint
started, which is the falsifier doing its job early rather than the plan
surviving unchallenged.)

## Risks

- **The integer probe's cost is unknown by construction.** Bounded by call
  count. If the first call is expensive, the second does not run without a new
  approval.
- **The integer path may not be exercisable without the device.** See the
  falsifier. This is the risk that would reshape the sprint.
- **Task F may not converge on a mechanism.** It is a design spike with a build
  attached; if the spike shows no mechanical check is possible, that finding is
  the deliverable and the card returns to the backlog.
- **F64 may reopen a published figure.** If the decomposition changes what
  +0.0256 is attributable to, that is an amendment and B.3 changes. Planned for,
  not a surprise.

## Definition of Done

- Integer path built, probed, and its cost stated as `measured`
- The QCi memo and hardware plan carry that figure; the no-quote sentence is
  gone and a test prevents its return
- The k=17 order-2 cell run; B.3 states the decomposition as a bound
- Six Sprint 17 injections replayed and reported as failures by the helper
- F88's mechanism catches both Sprint 17 false findings, or its spike result is
  recorded
- Suite green on both platforms; CHANGELOG updated; three-doc rule satisfied

## Out of scope

- **Sending the QCi package.** Assembled for the team lead; Claude never sends.
- **F25**, the full cardinality-constrained investigation. Task A and B build
  and size the path; they do not ask whether it beats a classical control.
- Retrofitting the 168 pre-A33 rows.
- **F2b entirely** -- blocks B4 and B5. Carded as F90 with B4 quoted at
  schedule 3, about 1,236 s, which is 63% of the remaining balance and needs
  its own approval.
