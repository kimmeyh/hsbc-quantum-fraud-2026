# Sprint 18 Plan: The First Phase 2 Evidence, and the Cost of the Ask

**Sprint**: 18
**Branch**: `feature/20260922_Sprint_18`
**Dates**: 2026-09-22 onward
**Scope**: F87, F64, F2b (B5 then B4), F88, F89
**Metered Dirac-3 seconds**: NON-ZERO. Three separate approval stops.

## Objective

Turn the two open outward commitments into measured numbers, and close the two
verification-defect cards that Sprint 17 paid for.

The QCi package cannot be sent while the hardware plan says "we are not quoting
a cost". Appendix B.3 cannot stop declining its own headline confound while the
k=17 order-2 cell is unrun. Both are single experiments. Everything else in this
sprint exists to make those two defensible.

## Audience-first statement (mandatory, SPRINT_PLANNING.md)

**F87 and F2b's reader is QCi's technical staff**, who will read a cost figure
and decide whether our estimates are measured or invented. Every number this
sprint produces about device time must carry its provenance as `measured` or
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
  same block from two angles. Task G reconciles them before B4 runs; F5's own
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

### Task E: Run B5 (F2b) (~45m + APPROVAL STOP) [METERED]

- **Block**: B5, QSVM sign-augmented. **12 calls.**
- **Expected: 15-62 s**, provenance **extrapolated** from B3's measured
  5.2 s/fit at comparable size.
- Runs before B4 deliberately: it is cheap, and it exercises the approval and
  ledger path before the expensive block.

### Task F: False-finding mechanism (F88) (~150m)

Design and build, with the two Sprint 17 instances as the acceptance test.

- Candidates named in the card: a guard recognising contradiction language that
  demands a named artifact citation; a `verify_claim.py` that reports every
  file mentioning a figure; a check that a claim naming an amendment has had
  the log read this session. **The spike picks one**; the card does not
  pre-commit.
- **Acceptance**: both Sprint 17 instances caught BEFORE the claim is
  committed. Proven by injection, not asserted.

### Task G: Reconcile B4 with F5, and fix F5's stale gate (~30m)

- F5's HOLD reason names a grant that has since arrived. Correct it.
- State plainly whether B4 and F5 are one block or two, and which this sprint
  runs. They must not both be scheduled.
- Zero metered seconds. **Blocks Task H.**

### Task H: Run B4 (F2b) (~60m + APPROVAL STOP) [METERED]

- **Block**: B4, SPECTRA. **15 calls at schedule 2, 153 variables.**
- **Expected: about 75 s**, provenance **extrapolated** from B3's measured rate
  at comparable size.
- **At schedule 3 this block would cost about 1,236 s — 63% of the remaining
  balance — to hit the resolution wall A31 already measured.** If the team lead
  wants schedule 3 anyway, that is a deliberate allocation decision and the
  block is re-quoted at that figure before it runs.
- Depends on: **Task G**.

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

- A 90 + B 30 + C 60 + D 120 + E 45 + F 150 + G 30 + H 60 + I 60 = **645 minutes**
- Verification-dominated portion (A, B, C, E, G, H): 315m -> 30% = **94m**
- **Total: 739 minutes, 12.3 hours**

Dependencies that constrain ordering, not cost: G blocks H; B follows A; I
follows B.

## Metered summary (Criterion H)

Three blocks, three separate approval stops. Nothing runs on this plan's
approval.

| Block | Calls | Expected | Provenance |
|---|---|---|---|
| Integer probe (Task B) | 2-3 | **unknown** | no comparable anchor; bounded by call count |
| B5 (Task E) | 12 | 15-62 s | extrapolated from B3 |
| B4 (Task H) | 15 | ~75 s at schedule 2 | extrapolated from B3 |

**Worst case if all three run: under 200 seconds of 1,961.** The figure that
would change this is schedule 3 on B4, at about 1,236 s.

## Premise falsifier (mandatory)

**Premise**: B4 at schedule 2 is the right block to run, and the resolution
limit makes schedule 3 a worse experiment rather than merely a costlier one.

**The check**: if the in-segment effect SPECTRA is meant to show depends on
three-feature interactions, schedule 2 cannot show it, and a null at schedule 2
would be a null about our configuration rather than about the device. Before
B4 runs, state what a schedule-2 null would and would not license.

**It can fail.** This is the most likely place for this sprint to be wrong.

## Risks

- **The integer probe's cost is unknown by construction.** Bounded by call
  count. If the first call is expensive, the second does not run without a new
  approval.
- **Task F may not converge on a mechanism.** It is a design spike with a build
  attached; if the spike shows no mechanical check is possible, that finding is
  the deliverable and the card returns to the backlog.
- **F64 may reopen a published figure.** If the decomposition changes what
  +0.0256 is attributable to, that is an amendment and B.3 changes. Planned for,
  not a surprise.
- **Three approval stops in one sprint** is more interruption than usual. They
  are separated by the zero-cost tasks deliberately.

## Definition of Done

- Integer path built, probed, and its cost stated as `measured`
- The QCi memo and hardware plan carry that figure; the no-quote sentence is
  gone and a test prevents its return
- The k=17 order-2 cell run; B.3 states the decomposition as a bound
- B5 complete; B4 complete or explicitly deferred with its cost quoted
- Six Sprint 17 injections replayed and reported as failures by the helper
- F88's mechanism catches both Sprint 17 false findings, or its spike result is
  recorded
- Suite green on both platforms; CHANGELOG updated; three-doc rule satisfied

## Out of scope

- **Sending the QCi package.** Assembled for the team lead; Claude never sends.
- **F25**, the full cardinality-constrained investigation. Task A and B build
  and size the path; they do not ask whether it beats a classical control.
- Retrofitting the 168 pre-A33 rows.
- Any schedule-3 SPECTRA block without a separate allocation decision.
