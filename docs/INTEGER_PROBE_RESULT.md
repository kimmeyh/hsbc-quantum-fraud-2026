# The Dirac-3 integer path: first measured cost

Run 2026-09-23 (Sprint 18 Task B, F87). **16 metered seconds.** This is the
first cost data this project has for the integer solver; Phase 1 ran only the
continuous relaxation.

## What it replaces

The QCi hardware plan currently reads:

> **Cost**: **UNKNOWN, and we will not quote a number.** We have never run your
> integer solver on this problem, so no comparable anchor exists.

That was the correct thing to write with no measurement behind it, and it was
the weakest sentence in a package whose argument is that our estimates come
from measured usage rather than projection.

## The measurement

| probe | variables | level budget | metered seconds |
|---|---|---|---|
| probe_small | 8 | 32 | **4** |
| probe_mid | 24 | 96 | **8** |

Both `status: ok`, zero failures, zero retries. `relaxation_schedule 2`,
`num_samples 8`, frozen. Cost from the allocation balance delta per F47:
1961 to 1957 to 1953 to 1945.

**The level budget is what binds**, not the variable count. `solve()` computes
`num_levels = [upper_bound + 1]` per variable, so the device sees
`sum(upper_bound + 1)` against the documented 949 ceiling. The F87 card assumed
`num_levels` was a solve parameter; it is not.

## The scaling basis, and its limits

Tripling the level budget (32 to 96) **doubled** the cost (4 to 8 s). Fitted
linearly across the two points: **0.0625 s per level plus a 2 s floor.**

Extrapolated, and labeled **extrapolated** rather than measured:

| level budget | seconds per fit |
|---|---|
| 200 | 14 |
| 500 | 33 | 
| 949 (ceiling) | 61 |

**Two points define a line by construction, so linearity is NOT established.**
The continuous path is the reason to be careful: between 136 and 833 variables
it showed an **18.8x** per-sample step, far from linear. A third point near the
ceiling is needed before any large integer block is quoted, and this document
must not be read as licensing one.

What the two points do establish honestly: a small integer job costs single
digit seconds, and the cost does not explode between 32 and 96 levels. That is
enough to replace "we will not quote a number" with a measured figure and a
stated basis.

## An over-spend, recorded

**The approved block was two calls. Three were made, costing 16 seconds instead
of 12.**

The second invocation passed `--max-calls 2` after a `--max-calls 1` run. The
runner had no memory of what it had already submitted, so it started from the
top and re-ran `probe_small` before proceeding to `probe_mid`. The duplicate
cost 4 seconds.

No result is affected: the duplicate is a second measurement of the same
configuration and it returned the same 4 seconds, which is itself a small
repeatability check. But the approval was for two calls and three were made.

**Fixed in the runner.** It now reads its own ledger and skips any label
already completed, and refuses to submit at all if the ledger is unreadable --
because a metered runner that cannot tell what it has already spent is one bad
re-invocation away from spending it twice, and the allocation has no undo.
Verified: a re-run now submits nothing.

## Allocation

| | seconds |
|---|---|
| before | 1,961 |
| spent | 16 |
| **remaining** | **1,945** |

Confirmed against the live allocations endpoint after the run.
