---
title: "Dirac-3 in Phase 2: What We Would Run and What It Costs"
subtitle: "Measured costs from the Phase 1 campaign, September 2026"
date: "September 2026"
---

# Phase 2 hardware plan

**Content current to 2026-09-12**, the date our Phase 1 entry was filed.
Nothing later has been added.

This is the hardware half of the Phase 2 plan in section 5 of our proposal,
extracted for QCi. It states what we would run on Dirac-3, what each block
costs, and why one of the six experiments is the one that actually needs the
device.

Every cost below is **measured on your hardware during Phase 1**, not
projected. Where we have no measurement, we say so and bound the block by call
count instead of quoting a number.

## Allocation position

| | Seconds |
|---|---|
| Granted 2026-09-09 | 3,000 |
| Drawn during the Phase 1 campaign | 1,039 |
| **Remaining** | **1,961** |

The campaign total reported in our submission is 1,141 metered seconds over 61
fits. That figure and the 1,039 above differ for two reasons, both of which we
would rather state than have you reconcile: 163 of the 1,141 seconds ran on the
free tier before the grant existed, and 61 seconds of grant time went to a B3
run we withdrew and re-ran the same day after finding that its pools were built
on more data than the arm it was quoted against. The withdrawn run is excluded
from the campaign total because its result is not ours to claim; the seconds
were still spent, so they are included in the draw.

## Measured per-fit cost

From 61 fits, all `status: ok`, zero failures, zero retries:

| Problem size | Seconds per fit | Basis |
|---|---|---|
| 833 variables (order-3 pool) | 82 mean, 71 to 92 | 11 fits, B2 |
| 136 variables | 4 to 9 | B3 ladder |
| 91 variables | 4 to 5 | B1, free tier |

Cost tracks problem size and is stable within a size. That is what made block
budgeting practical for us, and it is the single most useful operational fact
we can pass on to another customer sizing a problem.

## What we would run

Six experiments, in priority order. **Four of the six cost zero device
seconds**, because the classical proxy solves the identical Hamiltonian and
a convex problem has nothing for a solver to win.

### Experiment 3 is the one that needs Dirac-3

Choosing the best sparse subset of weak learners under a cardinality constraint
is NP-hard in general, and it is the native problem class of your integer
solver. Everything we ran in Phase 1 was the continuous relaxation, which is
convex: an exact classical solve returns the global optimum in milliseconds,
and no device can beat it. That is why our Phase 1 hardware result is a
fidelity measurement rather than a performance claim, and it is why Phase 2
moves to the formulation where the optimizer has real work to do.

- **Controls, stated before the block runs**: a time-capped commercial MIQP
  solve, greedy selection, and simulated annealing. A win against a
  certified-optimal classical solve is a result; a win against no control is
  not.
- **Cost**: **UNKNOWN, and we will not quote a number.** We have never run your
  integer solver on this problem, so no comparable anchor exists. The block
  would be bounded by call count and opened with a single probe fit to
  establish the rate before anything larger is committed. This is the same
  discipline we used for every Phase 1 block.

### The blocks with measured costs

- **Experiment 5, segment transfer (H5).** Replicates a prior Dirac-3
  campaign's in-segment wins with proper seeds and intervals, then tests
  transfer against a matched random-segment control. Sized in the 91 to 136
  variable range, so 4 to 9 seconds per fit.
- **Experiment 6, the scaling claim.** End-to-end training time against sample
  count, including Hamiltonian construction. This one is partly about your
  runtime claim and partly about ours: at 833 variables, pool construction
  costs about 12 minutes of CPU per fit against 82 seconds of device time, so
  the device is not the bottleneck and we would like to publish that ratio.

### The blocks that cost you nothing

Experiments 1, 2 and 4 run entirely on the classical proxy: isolating the
feature-count confound in our one positive result, the rolling-origin temporal
test that the ULB benchmark's two-day span cannot support, and a replication
under a source paper's own protocol.

We mention them because they explain the shape of the ask. A Phase 2 campaign
at these scales is a few thousand seconds, not tens of thousands, because the
proxy absorbs everything that does not require the device.

## What would retire the approach

Our preregistration names three conditions that together retire it. Two have
already fired: the confirmatory endpoint returned a null, and the feature
ladder's slope is negative. The third, H5 segment transfer, is unrun and is
experiment 5 above.

If H5 also fails, the honest conclusion is that this formulation does not
belong in a fraud stack, and we will say so in public with the same evidence
tags we used for everything else. We would rather tell you that now than have
you discover it in our Phase 2 report.

## Protocol, unchanged from Phase 1

- All usage of Dirac-3 is after testing all code outside of the Dirac-3 calls
  to ensure they run without error, estimated call counts and expected seconds,
  calls are tracked so that if a call is made and a computer goes down we can
  recover everything needed after connection is re-established (no need for
  repeat runs), most runs happen in the evenings and runs are approved by me
  after reviewing the plan.
- Every fit is exactly one metered call, landing as an `[HW]` row with
  `metered_seconds` from your response and the same configuration hash as its
  matching classical proxy row.

That last point is what makes the fidelity comparison meaningful.
