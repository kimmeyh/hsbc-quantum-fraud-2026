# Sprint 18 Summary: The First Phase 2 Evidence, and the Cost of the Ask

**Sprint**: 18
**Branch**: `feature/20260922_Sprint_18`
**Dates**: 2026-09-22 to 2026-09-23
**Scope**: F87, F64, F88, F89. F2b deferred to F90 before execution began.
**Metered Dirac-3 seconds**: **16** (approved as 2 calls; 3 were made -- see below).

## What shipped

All six tasks.

**F87 -- the integer path has a measured cost.** Phase 1 ran only the
continuous relaxation, which is convex and therefore unwinnable for any device.
The integer solver is the formulation where the optimizer has real work to do,
and it now has a number attached:

| probe | variables | level budget | metered seconds |
|---|---|---|---|
| probe_small | 8 | 32 | 4 |
| probe_mid | 24 | 96 | 8 |

Tripling the budget doubled the cost: about 0.0625 s per level plus a 2 s
floor, **labeled extrapolated rather than measured** because two points define
a line by construction.

**F64 -- the missing middle moves nothing.** k=17 at order 2 (153 variables)
minus k=13 at order 2 (91 variables), ten paired seeds: **+0.00007, CI
[-0.0024, +0.0026]**, spanning zero and an order of magnitude tighter than the
MDE. B2's +0.0256 is **not** explained by feature count.

**F89 -- an injection that cannot silently prove nothing**, which caught two
vacuous guards on its first real use.

**F88 -- `verify_claim.py`**, tested against both Sprint 17 false findings
verbatim.

## The pre-flight changed two cards before any work started

**F87 was bigger than "a probe".** No integer-solver path existed in
`experiments/src/`. The card also assumed `num_levels` was a solve parameter.
It is not: `solve()` computes `[upper_bound + 1]` per variable, so the device
budget is `sum(upper_bound + 1)`, not the variable count. Sizing a block on the
variable count would have quoted QCi a number the device does not agree with --
the exact failure F87 exists to prevent.

**F2b was deferred, and the reason is evidence rather than cost.** The first
plan ran B4 at schedule 2 on an argument that A31's resolution limit made
schedule 3 a worse experiment. The team lead challenged it from memory and was
right. A31 predicts the MECHANISM -- forced sparsity above ~200 learners -- not
a bad OUTCOME, and B2 at exactly 833 variables with weight cosine 0.83 produced
the campaign's only positive result at scale. Schedule 2 is a configuration
already shown to lose 8 of 8 overall, so a 75-second schedule-2 block would not
have been a cheap experiment but a worthless one. F90 carries B4 at schedule 3,
about 1,236 s, as its own allocation decision.

## The over-spend

**Three calls were made against a two-call approval: 16 metered seconds instead
of 12.**

The second invocation passed `--max-calls 2` after a `--max-calls 1` run, and
the runner had no memory of what it had already submitted, so it started from
the top and re-ran `probe_small`. The duplicate cost 4 seconds.

No result is affected -- the duplicate returned the same 4 seconds, which is a
small repeatability check -- but the approval was for two calls and three were
made. The runner now reads its own ledger, skips completed labels, and refuses
to submit at all if the ledger is unreadable.

## The numbers

| | |
|---|---|
| Tests | grew across six new guard files; counts are not restated here -- run the suite |
| Both platforms | zero failures |
| Amendments | A33, unchanged |
| Metered seconds | **280** across six calls, in two approved rounds |
| Grant position | 1,319 of 3,000 drawn, **1,681 remaining** |

## What PR #139 review found

Three reviews ran: Copilot, test coverage, comment accuracy. Every finding was
reproduced before it was acted on, and every fix carries a test proven to fail
without it. The pattern across them is one class.

**Two wrong figures in a vendor-facing document.** The Phase 2 ask stated
9,000 - 1,681 = 7,500 (it is 7,319), and labeled two compounding buffers as
parallel percentages, so the column summed to 8,216 against a stated ~9,000.
The guards on that section pinned the old WORDING and went red on the
correction; they now re-derive the subtraction.

**A claim to QCi that a test pins the sizing rejection message.** That test
re-implemented the matcher inline and never imported production code, so
nothing could fail it -- and no production matcher exists at all. Replaced
with a test of the real pre-submission size check, and the claim rewritten to
describe what the code does.

**Four more vacuous guards**, on top of the four already recorded above. Two
could not fail (confirmed by mutation), and the F64 decomposition guard
checked only that figures were PRESENT -- so it passed while the interaction
read +0.0011, which is B2's [HW]-vs-proxy gain substituted for a
corner-to-corner subtraction. Tenfold inflation, in a results document. The
true value is +0.0001, which strengthens the conclusion rather than weakening
it.

**A design nobody approved was reachable by raising a flag.** probe_ceiling,
estimated near 181 s and explicitly not approved, sat in the designs file with
no marker. The ledger skip does not protect a design that never ran.

**Two scripts that conflated "clean" with "could not check."** Both now fail
closed.

THE COMMON THREAD: presence is not correctness. A figure that appears, a test
that runs, a path that is scanned -- each was treated as evidence of the thing
it was supposed to prove. Six of the eight findings are that substitution.
IMP-2 was held this sprint pending recurrence; it recurred within the day.

## Defects found in this sprint's own work

- **The over-spend above**, and the missing idempotency check behind it.
- **`test_the_168_existing_rows_are_not_retrofitted` asserted no row carries an
  environment field.** Right when written, wrong the moment A33 did its job and
  Task C wrote ten stamped rows. Pinned to the boundary rather than deleted: a
  guard that fails on correct behavior gets deleted instead of fixed.
- **Two vacuous guards in `verify_claim`**, both caught by the F89 helper on
  its first real use. One search path was redundant; the other meant the
  amendment log could have dropped out of the search while every assertion
  still passed.
- **An injection that passed for a sloppier reason than designed.** While
  writing F89's own acceptance test, a `chr(34)` construction whose `.replace()`
  never matched injected `"numpy-None"` instead of the intended value. The test
  passed. Simplified.
- **Two internal inconsistencies in the hardware plan**, caught while
  reconciling: the allocation table still said 1,961 remaining, and the header
  claimed content "current to 2026-09-12" while carrying a 2026-09-23
  measurement.

## Deliberately not done

- **F25**, the cardinality-constrained investigation. This sprint built and
  sized the integer path; it did not ask whether that path beats a classical
  control.
- **A third probe point near the ceiling.** Needed before any large integer
  block is quoted, and stated as such in every document carrying the
  extrapolation.
- **The fourth ladder corner** (k=13 at order 3, 377 variables), which would
  identify the interaction term F64 leaves open. A separate card, not a silent
  extension.
- **Sending the QCi package.** Assembled for the team lead; Claude never sends.
- No submitted document was edited; all verified byte-identical at close.
