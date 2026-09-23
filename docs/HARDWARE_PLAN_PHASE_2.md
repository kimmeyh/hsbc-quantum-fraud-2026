---
title: "Dirac-3 in Phase 2: What We Would Run and What It Costs"
subtitle: "Measured costs from the Phase 1 campaign, September 2026"
date: "September 2026"
---

# Phase 2 hardware plan

**The Phase 1 campaign figures below are current to 2026-09-12**, the date
our entry was filed. One section is NEWER and says so: the integer-solver
cost in experiment 3 was measured on 2026-09-23, after the filing, because we
would rather send you a measured number than a placeholder.

This is the hardware half of the Phase 2 plan in section 5 of our proposal,
extracted for QCi.

**The ask, up front: 9,000 Dirac-3 seconds for Phase 2.** We hold 1,681 of
those already, so the additional request is **7,500 seconds**. That figure is
built from rates we measured on your hardware, not from a projection:

**This is well below what we originally told you Phase 2 might need.** Our
sponsorship request estimated 2,000 seconds for the preregistered runs plus
20,000 to 40,000 for the full benchmark grid, tuning ladder and scaling study
-- both marked TBD, because at the time we had no measured cost at scale and
said so. We now do, and three things shrank the number:

- **The classical proxy absorbs four of the six experiments.** It solves the
  identical Hamiltonian, so anything that does not need the device does not
  touch it. That was the single largest reduction.
- **The null result narrowed the grid.** A full benchmark sweep made sense when
  the question was open. It is not, on the continuous formulation, so Phase 2
  runs the one formulation where the optimizer has real work to do rather than
  a ladder across configurations we can already predict.
- **Measured costs came in below the estimate that sized the original ask.**
  That estimate used 26 to 34 seconds per tuned fit from a prior campaign; our
  own fits ran 4 to 9 seconds at 91 to 136 variables.

We mention it because a request that shrinks by a factor of three to five
deserves an explanation, and because the reason is evidence rather than a
reduction in ambition.

| | seconds |
|---|---|
| Experiment 3, integer solver, 60-variable cells (20 fits) | 1,420 |
| Experiment 3, integer solver, 150-variable cells (10 fits) | 1,650 |
| Experiment 5, segment transfer (30 fits) | 270 |
| Experiment 6, scaling claim (12 fits at 833 variables) | 984 |
| Experiments 1, 2 and 4 | **0** -- classical proxy |
| **subtotal, at measured rates** | **4,324** |
| Estimation contingency, 50% | 2,162 |
| Discovery buffer, 40% | 2,594 |
| **total** | **~9,000** |

**Why two separate buffers, rather than one round number.** They cover
different risks and we would rather name them than bury them.

The **50% estimation contingency** is calibrated on our own error. Our opening
two-point estimate for the integer solver was wrong by 4.1x by the time we
reached 600 levels. We corrected it with more measurement rather than more
confidence, but 50% is the minimum honest allowance on a path we have now
sampled five times and not twenty.

The **40% discovery buffer** is for avenues we cannot name yet. Phase 1's most
useful result -- that your device's resolution limit forces sparse selection,
and that the sparsified answer outperformed -- was not in any plan we wrote. It
came out of a failure analysis. If Phase 2 turns up something comparable we
would like to be able to follow it within the grant rather than stopping to
re-ask, which costs both of us time and usually arrives after the context has
gone cold.

Everything below states what we would run, what each block costs, and why one
of the six experiments is the one that actually needs the device.

Every cost below is **measured on your hardware during Phase 1**, not
projected. Where we have no measurement, we say so and bound the block by call
count instead of quoting a number.

## Allocation position

| | Seconds |
|---|---|
| Granted 2026-09-09 | 3,000 |
| Drawn during the Phase 1 campaign | 1,039 |
| Drawn by the integer sizing probes, 2026-09-23 | 280 |
| **Remaining** | **1,681** |

The campaign total reported in our submission is 1,141 metered seconds over 61
fits. That figure and the 1,039 above differ for two reasons, both of which we
would rather state than have you reconcile: 163 of the 1,141 seconds ran on the
free tier before the grant existed, and 61 seconds of grant time went to a run
we withdrew and re-ran the same day after finding that its pools were built
on more data than the arm it was quoted against. The withdrawn run is excluded
from the campaign total because its result is not ours to claim; the seconds
were still spent, so they are included in the draw.

## Measured per-fit cost

From 61 fits, all `status: ok`, zero failures, zero retries:

| Problem size | Seconds per fit | Basis |
|---|---|---|
| 833 variables (order-3 pool) | 82 mean, 71 to 92 | 11 fits |
| 136 variables | 4 to 9 | 12 fits |
| 91 variables | 4 to 5 | 22 fits, free tier |

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
- **Cost**: **measured, on your integer solver, across five sizing calls.**

  | variables | level budget | metered seconds |
  |---|---|---|
  | 8 | 32 | 4 |
  | 24 | 96 | 8 |
  | 60 | 240 | 28 |
  | 150 | 600 | 165 |
  | 60 | 840 | 71 |

  All `status: ok`, zero failures, `relaxation_schedule 2`, `num_samples 8`.

  **The finding we think is most useful to you: cost tracks the VARIABLE
  COUNT, not the level budget.** The last two rows are a controlled pair. The
  60-variable job carries 1.4x more levels than the 150-variable one and cost
  2.3x LESS. Your documented ceiling is expressed in levels --
  `sum(upper_bound + 1)` against 949 -- but sizing a block on levels alone
  would misprice it, and our own first estimate made exactly that mistake.

  Cost is also superlinear in variables. We first fitted two small points and
  got 0.0625 s per level, extrapolating to about 61 s at the ceiling. The next
  two calls came in at 1.6x and 4.1x that line, so we discarded it. A
  two-factor fit over all five points gives roughly `vars^0.75 x levels^0.52`,
  but individual points miss by up to 45%, so we offer it as indicative rather
  than as a formula.

  **What that means for the Phase 2 block, stated per run.** Experiment 3 is
  the one that needs your integer solver, and it is the expensive half of the
  request:

  | cell | fits | rate | seconds |
  |---|---|---|---|
  | 60-variable cardinality cells | 20 | 71 s (measured) | 1,420 |
  | 150-variable cardinality cells | 10 | 165 s (measured) | 1,650 |

  Both rates are measured, not fitted: they are `probe_deep` and `probe_high`
  above. We have deliberately NOT extrapolated to a high-variable job at the
  ceiling, because we did not run one -- the revised estimate put it beyond
  what we had budgeted for the sizing exercise, so we stopped and took the
  cheaper of the two remaining designs. Any number we quoted there would be
  past our own data.

  The other two metered experiments are sized from the Phase 1 campaign:
  experiment 5 at 30 fits in the 91-136 variable range (about 270 s at the
  upper rate), and experiment 6 at 12 fits of the 833-variable configuration
  (about 984 s at the measured 82 s per fit for that size).

### The blocks with measured costs

- **Experiment 5, segment transfer.** Replicates a prior Dirac-3
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
