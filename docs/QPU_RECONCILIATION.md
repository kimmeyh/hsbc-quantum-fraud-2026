# QPU cost reconciliation (Sprint 17, Task A)

Written 2026-09-19. Establishes, from committed artifacts only, the three
figures the QCi memo states: total metered seconds, grant size, and seconds
remaining.

This file exists because the Sprint 17 plan's own pre-flight got it wrong, and
because a reviewer got a version of it wrong in Sprint 12. The numbers look
like they should subtract and they do not.

## The answer

- **Campaign total, as submitted**: 1,141.0 metered seconds over 61 fits
- **Grant**: 3,000 seconds
- **Drawn against the grant**: 1,039 seconds
- **Remaining**: **1,961 seconds**

## Why 3,000 - 1,141 is the wrong sum

It gives 1,859 and it is wrong in both directions at once:

- The campaign total **includes 163 seconds that never touched the grant**.
  They ran on the free tier before the allocation existed.
- The campaign total **excludes 61 seconds that did draw on it**. That was the
  withdrawn first B3 run. The result was withdrawn; the seconds were still
  spent.

A reviewer made this subtraction in Sprint 12, computed 1,859, and reported our
1,961 as an error. It was not. The live allocations endpoint confirmed 1,961.

## Pre-grant / free tier: 163 s, 27 fits

| Block | Seconds | Fits | Source |
|---|---|---|---|
| G0b | 21.0 | 5 | `results.json`, HW rows, block G0b |
| B1 | 99.0 | 22 | `results.json`, HW rows, block B1 |
| F32 | 43.0 | 10 | `results.json`, HW rows, block F32 (Sprint 6, Sep 5) |

G0b + B1 = 120.0 s, which matches the 27 free-tier calls in
`qpu_cost_ledger.json` exactly. F32 ran on Sep 5, before the grant's first draw
on 2026-09-10, so it is also pre-grant.

## Grant draw: 1,039 s

| Item | Seconds | Fits | Source |
|---|---|---|---|
| A21/F47 ceiling probe | 10.0 | 1 | ledger row, `cost_source` "allocation balance 3000->2990" |
| B3, first run | 61.0 | 12 | ledger, batch 1 of 2026-09-10. **Withdrawn (A22, A23)** |
| B3, published run | 62.0 | 12 | `b3_hardware.json`, `total_metered_seconds` |
| B2 | 906.0 | 11 | `results.json`, HW rows, block B2 |

163 + 1,039 - 61 = **1,141**, and the fit counts reconcile the same way. The
submission's own `COMPLIANCE_WALK.md` states it as 1069.0 + 62.0 + 10.0 across
three independent artifacts, which is the same total grouped differently.

## Two artifact quirks that make this look broken

Both cost real time to run down, so they are recorded rather than left for the
next reader to rediscover.

1. **`qpu_cost_ledger.json` was built 2026-09-09**, before B2 ran. It therefore
   holds 52 calls and no B2. It is not a campaign ledger and reading it as one
   understates the campaign by 906 seconds.

2. **24 of its 25 paid rows carry no `billed_s`.** They carry `measured_seconds`
   with `cost_source` "allocation balance before minus after", because the runner
   did not capture job identifiers (F47). Counting only `billed_s` yields 130 s
   and looks like a reconciliation failure. It is a different field, not a
   missing cost.

3. The ledger's per-call deltas sum to 133 s while the balance moved 224 s
   (3,000 to 2,776). The 91 s difference is the withdrawn B3 run plus the probe,
   visible as a jump from `balance_after` 2929 to `balance_before` 2838 between
   the two B3 batches.

## What the memo may state

Every figure above traces to a named artifact. The memo may state 1,141 metered
seconds, 61 fits, and 1,961 seconds remaining. It should not state a remaining
balance derived by subtracting the campaign total from the grant.

**Currency**: the 1,961 figure was endpoint-confirmed during Sprint 12 and no
metered run has occurred since. It remains correct unless a run has happened
outside this repository's record.
