# Sprint 21 Plan: The SPECTRA Block, and a Bar That Can Read It

**Sprint**: 21 | **Branch**: `feature/20261004_Sprint_21`
**Planned**: 2026-10-05 | **Status**: awaiting team-lead approval
**Scope**: F90, F100, F101, F122 (the team lead's selection list, complete)
**Metered Dirac-3 seconds**: **B5 then B4, two separate Criterion H approvals.
Expected 1,099-1,297 s of the 1,681 remaining. Nothing runs without the stated
approval.**

## Objective

Run the SPECTRA block that can actually show an effect, and build the classical
bar that makes its result readable. F90 is the replication half of Experiment 5
(segment transfer, H5) and the most valuable work available. F100 is what keeps
a device win from being a feature-engineering win reported as a quantum one.

This is the first sprint since Sprint 18 to spend metered seconds, and it
commits 65-77% of the remaining balance.

## What the capability pre-flight found, before any estimate

Mandatory per `SPRINT_PLANNING.md`, and it changed the plan rather than
confirming it. Read: `docs/TROUBLESHOOTING.md` (which pointed at the right two
documents immediately, IMP-2 working), `docs/HARDWARE_REQUEST_B4.md`,
`docs/SPECTRA_BLOCK_RECONCILIATION.md`, `experiments/results/results.json`,
`experiments/results/spectra_proxy_dry_run.json`, and the code --
`data.qubo_vars`, `spectra_segment.FROZEN_CELLS`.

**1. F90's variable count was wrong: 816, not 833.** The card's formula
`n + C(n,2) + C(n,3)` is the `full` pair-build. `data.qubo_vars` (amendment A2)
caps pairs at `n(n-3)/2` for the `sequential` build, which
`HARDWARE_REQUEST_B4.md` states is **mandatory on Windows**. The dry run
already recorded 816 / 816 / 560. Corrected on the card 2026-10-05.

**2. B4 is three cells at two sizes**, not 15 fits at one. Pricing every fit at
the 833 rate overstated the block by about 150 s.

**3. A 2.4x COST CONFLICT IS OPEN AND IS THIS SPRINT'S LARGEST RISK.**
`HARDWARE_REQUEST_B4.md` line 43 prices B4 at **26-34 s/fit** from
FourierWall2's measured rollout at this exact `ns`/`rx`/`schedule`, totaling
~390-510 s, and cites the preregistration section 10 envelope of ~450 s. Our
own **B2 measured 76-91 s/fit** at a configuration that matches B4's exactly
(`num_samples=8`, `relaxation_schedule=2`, `weak_cls_schedule=3`; differing
only in `pair_build` and dataset). Both are described as measured. They cannot
both price B4, and the B4 request is the document QCi holds a plan against.

**4. telecom_churn is unscoreable on 2 of 5 seeds** at the frozen 50-positive
floor (seeds 42 and 45; 46 and 49 positives against the floor). Those two fits
still cost about 160 s. **They are not dropped** -- the cells are frozen and
the B4 request requires reporting unscoreable seeds per-seed rather than
backfilling. Dropping them would be a Class 1 protocol change and is not
proposed here.

## Tasks

| Task | Card | What | Owner | Est | Runtime | Depends on |
|---|---|---|---|---|---|---|
| A | F90 | Bring in the off-repository device result: configuration, fits, seeds, arm | **Team lead** (Claude verifies and records) | 45 | n/a | nothing |
| B | F122 | Four accurate-but-weak guards rewritten, each proven RED by a mutation it currently survives | Claude | 45 | n/a | nothing |
| C | F90 | B5 (12 fits), then B4 (15 fits) as `[HW]` rows | Claude | 240 | **see runtime** | A, and Criterion H twice |
| D | F100 | Complete classical bar: LogReg, GAM, GA2M, HGB, order-matched JOINT twin | Claude | 360 | **see runtime** | A |
| E | F101 | `in_pocket` provenance diagnostic, one model fit | Claude | 60 | ~5 min | A |

**Derived total: 750 minutes implementation (12.5 h)**, computed from the card
estimates above and not asserted. Plus allowances below: **872 minutes
(14.5 h)**.

**Allowances, named rather than absorbed** (`SPRINT_PLANNING.md`):
- **30% findings allowance on Task A, 14 min.** Task A is verification, and a
  verification task generates work the moment a check fails.
- **30% allowance on Task D, 108 min.** F100 is `[no-history]` and GAM/GA2M
  twins were the Sprint 9 7.9-hour surprise.
- If every check passes the allowance is returned and the sprint finishes
  early, which is the good outcome and is recorded as such.

### Runtime, estimated separately from implementation

**Task C, device time.** B5 first: 12 fits, **15-62 s**, provenance
`extrapolated` from B3's 5.2 s/fit. B4 second: 15 fits = 10 at 816 variables +
5 at 560, **about 1,084-1,235 s** at the B2 anchor rate, or **about 450 s** if
the FourierWall2 rate is the right one. That spread *is* finding 3 above, and
B5 exists partly to settle it before the expensive block commits.

**Task C, local time.** The dominant term is not the device. Each fit needs a
sequential weak-classifier pool build of 816 or 560 learners, mandatory on
Windows, 15 times. `[unbounded]` until measured, so **Task C opens with a
one-cell pilot** (`oilgas_gasturbine`, 560 variables, one seed, zero metered)
that measures the pool build and extrapolates to 15 cells before any metered
call is made.

**Task D.** Five classical lanes x 3 datasets x 5 seeds x repeated splits x
paired bootstrap, all `[no-history]`. The dominant term is unnamed, which by
the Sprint 9 rule means the sizing is not finished. **Task D therefore opens
with a pilot on one dataset**, measuring each lane separately, and the GAM and
GA2M lanes are measured before the full grid is launched. Any run over 30
minutes emits heartbeat progress to a file before it starts.

## Premise falsifiers

Required for any card justified by a measurement.

- **F90.** The premise is that the off-repository device run tested the arm this
  block replicates. **Falsifier**: Task A's configuration hash does not match
  any `FROZEN_CELLS` entry, or its schedule, sample count or relaxation
  schedule differ. Then it is a different experiment, F100's anchoring is
  re-pointed, and the claim is restated as unverified rather than carried.
- **F100.** The premise is that a complete classical bar can distinguish a
  quantum gain from a feature-engineering gain. **Falsifier**: every classical
  lane gains from the phase features too. That is outcome 3 on the card and it
  is reportable, not a failure.
- **F122.** The premise is that each of the four guards is weaker than its name.
  **Falsifier**: the mutation the card names already turns the guard red, in
  which case that item needs no change and is recorded as such.

## Sequencing, and what runs while Task A is outstanding

**Task A gates C, D and E.** It is yours, so the sprint cannot be fully
sequenced from here. What runs independently:

- **Task B (F122)** depends on nothing and runs first.
- **Task C's local pilot** and **B5** are independent of Task A: B5 is a
  different block and exercises the approval and ledger path before the
  expensive block.
- **A sequencing question is put to you below** rather than decided here:
  whether to build Task D's harness against the repository's own frozen cells
  now and re-point it when Task A lands. The F100 card says it depends on Task
  A, so changing that is yours, not mine to infer. Building early is also the
  config-provenance smoke test `SPRINT_PLANNING.md` requires.

## Risks

- **Allocation.** 1,099-1,297 s of 1,681 leaves 384-582 s. That does not cover
  Experiment 3, which depends on the additional 7,500 s asked of QCi and not
  yet granted.
- **The 2.4x cost conflict** (finding 3). If the B2 rate holds, the block costs
  4.0-4.6x the 270 s QCi was told for Experiment 5. **Telling QCi is your
  action, not Claude's**, and the reconciliation document says the gap stays
  externally visible whether or not the block is approved.
- **The off-repository result is `[UNVERIFIED -- OFF-REPOSITORY]`** until Task A
  lands. `CVQBoost_Findings.md` is planning-reference only and is not evidence
  in this repository.
- **Fragile wins.** The in-segment wins carry a train-to-test gap well above
  XGBoost's, one case 0.98 train to 0.59 test. Every win is reported with its
  gap beside it (F90 acceptance, added 2026-10-03).
- **Queue timing is unverified.** The stored note measures 2026-09-09 and its
  4-5 s/fit describes small-degree fits, not 816-variable ones. Not planned
  around.
- **Context/session continuity**: a 14.5 h sprint spans sessions. Task actuals
  are recorded as each task finishes, per Sprint 20's IMP-1.

## Model assignments

- Tasks A verification, C, and the F90/F100 analysis: top tier (this is
  statistical-methodology work touching the frozen preregistration's H5).
- Task B (F122): top tier for the mutation design, since three of the four are
  guard-discipline judgments.
- Task D lane implementation and Task E: Sonnet subagents acceptable under a
  stated interface; the paired-bootstrap and CI reporting stay top tier.

## Definition of Done

Per `SPRINT_PLANNING.md`, referenced not restated: acceptance criteria met with
evidence; suite green; every number in `results.json` with its evidence tag
(`[HW]` for B5/B4, `[SIM]`/`[PROJ]` elsewhere); docs updated in the same
commit; committed with the issue number.

Sprint-specific additions:
- Every metered row carries measured `metered_seconds` from the device
  response, never an estimate.
- The weight cosine is recorded for every B4 fit: forced sparsity under A31's
  ~200-learner resolution limit is the expected mechanism, not a defect.
- Every returned sample is stored, not only the lowest-energy one (F90
  acceptance (c)), which is what makes F20 cost zero further device time.
- Unscoreable seeds are reported per-seed, never averaged over or backfilled.
