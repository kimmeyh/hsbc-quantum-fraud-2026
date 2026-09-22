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

---

# WITHDRAWN: "the linear-term span disagrees between two documents"

Raised 2026-09-19 during Sprint 17 Task D. **Withdrawn the same day, in Task I,
before it reached any outward document.** It was not a finding. It was my own
incomplete reading of an artifact, and the repository had already fixed the
real version of it a week earlier.

## What I claimed

That `PREREGISTRATION.md` A31 (16.0) and `docs/paper/appendix.md` A.4 (28.0)
disagreed on the linear-term span, and that `device_resolution.json` recorded
neither figure nor the 510,705 diagonal both documents quote.

## What is actually true

`device_resolution.json` has a `per_pool` array carrying every figure per pool:
`diagonal`, `linear_spread`, `off_diagonal_spread`, `resolvable_difference`.
I read only the `frozen_pool` summary block, saw the fields were not there, and
concluded they existed nowhere. They were one level down in the same file.

Checked against the artifact:

- `linear_spread` over the ten pools: 12.0 x6, 16.0 x2, **28.0 x2**. The
  maximum is 28.0, which is exactly what the appendix says.
- `diagonal`: 510,705.0 on every pool, exactly as both documents quote.

**And the discrepancy was already found and corrected**, by amendment A32 on
2026-09-12, before submission: A31's 16.0 was the seed-42 value quoted as
though it were the maximum across ten pools; the appendix was corrected to
28.0 in the same commit so the log and the shipped document agree. A32 states
this in terms, including that it was found by walking the shipped appendix
against `device_resolution.json` -- the exact check I thought I was doing
first.

## Consequence, and why this is recorded rather than deleted

**No outward document carried the error.** The QCi feedback document quotes
only 20.0 and 2,553.5 with the artifact named, which is correct and remains
correct. Nothing needs changing there. No submitted document was edited at any
point.

The cost was a recommended backlog item that would have asked someone to add
fields that already exist.

Two things worth keeping from it:

1. **"Not in the artifact" requires reading the whole artifact.** I checked the
   summary block and a keyword grep, and both missed a nested array in the same
   file. That is the same shape as the CLAUDE.md rule about not stating what an
   external system contains without opening it -- I opened it and still did not
   read it.

2. **Check the amendment log before reporting a contradiction between
   documents.** Thirty-two dated amendments exist precisely because these get
   found and fixed. A contradiction that looks new is often one that was
   already resolved, and A32 is dated the day of submission.
