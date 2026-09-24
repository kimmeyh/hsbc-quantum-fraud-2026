# The Dirac-3 integer path: first measured cost

Rounds 1 and 2, 2026-09-23 (Sprint 18 Task B, F87). **280 metered seconds
across six calls**, five distinct designs plus one duplicate submission of the
smallest (4 s), recorded in "Two approval stops, one over-spend" below. This is the first cost data this project has for the
integer solver; Phase 1 ran only the continuous relaxation.

## What it replaces

The QCi hardware plan read:

> **Cost**: **UNKNOWN, and we will not quote a number.** We have never run your
> integer solver on this problem, so no comparable anchor exists.

That was the correct thing to write with no measurement behind it, and it was
the weakest sentence in a package whose argument is that our estimates come
from measured usage rather than projection.

## The measurements

| probe | variables | level budget | metered seconds |
|---|---|---|---|
| probe_small | 8 | 32 | 4 |
| probe_mid | 24 | 96 | 8 |
| probe_mid_hi | 60 | 240 | 28 |
| probe_high | 150 | 600 | 165 |
| probe_deep | 60 | 840 | 71 |

All `status: ok`, zero failures, zero retries. `relaxation_schedule 2`,
`num_samples 8`, frozen throughout. Cost from the allocation balance delta per
F47: 1961 to 1681.

## The headline finding: cost tracks VARIABLES, not the level budget

`probe_high` and `probe_deep` were designed as a controlled pair, and they
settle a question the earlier points could not:

| | variables | levels | seconds |
|---|---|---|---|
| probe_high | 150 | 600 | **165** |
| probe_deep | **60** | **840** | **71** |

**probe_deep carries 1.4x MORE levels and 2.5x FEWER variables, and cost 2.3x
LESS.** If the level budget drove cost, it would have been the more expensive
of the two. It was not, by a wide margin.

This matters because **the device ceiling is stated in levels** -- 949, as
`sum(upper_bound + 1)` -- **while the cost is driven by the variable count.**
Those are different quantities, and a block sized against the ceiling alone
would be quoted wrongly. Rounds 1 and 2's first four probes could not separate
them, because every one used `upper_bound = 3` and so moved levels and
variables together.

A two-factor fit over all five points gives roughly `vars^0.75 x levels^0.52`
(R^2 0.953), but individual points miss by up to 45%, so that formula is
**indicative only**. The controlled comparison above is the finding; the
exponents are not.

## Why the round-1 line was wrong

Round 1 fitted 32 and 96 levels and produced 0.0625 s per level plus a 2 s
floor, extrapolating to **61 s at the ceiling**. Round 2 falsified it
immediately:

| levels | round-1 prediction | actual | over |
|---|---|---|---|
| 240 | 17 s | 28 s | 1.6x |
| 600 | 40 s | 165 s | **4.1x** |

The cost is superlinear in variables. A single additional far point would NOT
have caught this cleanly: with two points plus one, a line and a parabola both
pass through all three exactly, so the shape would have stayed unidentified.
Two far points made it testable, which is why round 2 was designed as four
calls rather than one.

**The caution in the round-1 write-up was right and the number in it was
wrong.** The continuous path's 18.8x per-sample step between 136 and 833
variables was the stated reason not to trust the line, and that is exactly how
it failed.

## What can now be quoted, and what cannot

**Can be quoted, as measured:** an integer fit at 60 variables costs about
71 s at 840 levels and 28 s at 240 levels; at 150 variables, 165 s at 600
levels.

**Can be quoted, as extrapolated:** cost grows faster than linearly in the
variable count, so a Phase 2 block should be sized on variables, not on the
level budget.

**Cannot be quoted:** a figure at the 949-level ceiling with a high variable
count. `probe_ceiling` (210 variables, 840 levels) was designed and NOT run --
the revised estimate after round 2's first two calls put it near 181 s, well
above the envelope that had been approved, so it stopped for a fresh decision
and the team lead approved only `probe_deep`. Any document quoting a
high-variable ceiling figure would be extrapolating past the data.

## Two approval stops, one over-spend

**Round 1 over-spent.** The approved block was two calls; three were made, 16
seconds instead of 12. A second invocation with a higher `--max-calls` re-ran
the first probe, because the runner had no memory of what it had submitted.
The duplicate returned the same 4 seconds, so no result is affected, but the
approval was for two calls. Fixed: the runner now reads its own ledger, skips
completed labels, and refuses to submit if the ledger is unreadable.

**Round 2 stopped itself.** After two of four approved calls, the measured
points showed the remaining two would cost roughly 3x what had been quoted.
Rather than spend against a number known to be wrong, the block stopped and
re-quoted. The team lead then approved one of the two.

## Allocation

| | seconds |
|---|---|
| before round 1 | 1,961 |
| round 1 | 16 |
| round 2 | 264 |
| **remaining** | **1,681** |

Confirmed against the live allocations endpoint after each run.
