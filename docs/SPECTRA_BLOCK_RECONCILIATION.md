# The SPECTRA block: four records, one decision needed

**F93, Sprint 20.** Four records in this repository describe the same SPECTRA
hardware block and disagree about its size, its schedule and its cost. One of
them has been sent to QCi. This document puts them side by side so the
configuration can be chosen once, and records the choice.

**This document does not pick.** The configuration is a Class 3 decision
(allocation spend against a fixed 1,681-second balance), so it is the team
lead's. What follows is the evidence.

## The four records

| Record | Block | Fits | Variables | Schedule | Cost | Provenance |
|---|---|---|---|---|---|---|
| **F2b** | B4 | 15 | not stated | not stated | ~450 s | original grid |
| **F90** | B4 | 15 | 833 | **3** | **~1,236 s** | measured at this exact size |
| **F5** (HOLD) | B4 | 3 cells x 5 seeds | not stated | not stated | not stated | — |
| **Sent hardware plan** | Experiment 5, segment transfer | 30 | 91–136 | not stated | **270 s** | measured rates |

Verified 2026-10-02 against the sent PDF with `pypdf`: it contains "Experiment
5, segment transfer (30 fits)", "270", and "91 to 136". It does not contain
"schedule 4" or any schedule number for this block.

## Why they disagree

They were written at different times against different knowledge, and none was
retired when the next arrived.

**F2b's ~450 s is from the original grid**, which Sprint 12 proved wrong by
2.3x at 833 variables: the grid assumed about 40 s per fit and the measurement
came in at 91 s. The schedule underneath that estimate was never stated, which
is why the number cannot be repaired — there is no way to tell what it was
costing.

**F90 carries the measured figure and names the configuration.** Its case for
schedule 3 is evidence rather than preference: in the prior SPECTRA work,
schedule 2 lost overall 8 of 8 to the classical arm with only about 3
in-segment metrics won, while schedule 3 — which adds three-feature
interactions — reached in-segment ROC 5 of 7, PR 6 of 7, and an overall win on
`energy_steel`. The cost anchor is unusually strong: the schedule-3 QUBO is
`n + C(n,2) + C(n,3)`, which for `energy_steel`'s 17 features is exactly 833
variables — our own B2 size — so B2's measured 82.4 s per fit is a direct
anchor rather than an extrapolation.

**F5 is the same block from a third angle**, in-segment replication at 3 cells
x 5 seeds. Its HOLD reason was stale (the grant arrived 2026-09-09) and was
corrected in the Sprint 18 sweep to the real one: it overlaps F90 and must be
reconciled before either is scheduled.

**The sent hardware plan sizes this as 30 fits at 91–136 variables for 270 s.**
That is a schedule-2-scale configuration: 136 variables is nowhere near the 833
that schedule 3 produces at 17 features.

## The tension, stated plainly

**QCi has been told 270 seconds. F90's configuration costs about 1,236.**

That is 4.6x the figure in the vendor's hands, and 74% of the entire remaining
1,681-second balance. The hardware plan is final and was sent on 2026-09-25, so
it cannot be edited to match — F96 was closed as overtaken for exactly this
reason.

This does not forbid running schedule 3. It means that choosing it is a
decision made *knowing* what the vendor holds, and that the difference should
be stated to QCi rather than discovered by them. The memo's own standard was
that every figure traces; a block costing 4.6x its quoted figure without
comment would fail that standard.

The honest counter-argument is F90's, and it is strong: a schedule-2 block
would spend real seconds reproducing a configuration already measured to lose
8 of 8. That is not a cheap experiment, it is a worthless one. Spending 270
seconds to confirm a known negative is worse value than spending 1,236 on the
configuration that showed an effect.

## The options

**Option 1 — schedule 3 at 833 variables, as F90 specifies.** 15 fits, about
1,236 s, 74% of the balance. Cost is measured at this exact variable count.
Runs the configuration that showed an in-segment effect. Requires telling QCi
that Experiment 5 costs more than the plan quoted, and why.

**Option 2 — schedule 2 at 91–136 variables, as the sent plan quotes.** 30
fits, about 270 s, 16% of the balance. Matches what QCi holds exactly. Runs a
configuration that lost 8 of 8 overall in the prior work, so the likely result
is a confirmed negative.

**Option 3 — a reduced schedule-3 block.** Fewer than 15 fits at 833
variables, sized to fit a chosen fraction of the balance. Keeps the
configuration that can show an effect while leaving room for F95 and any
Phase 2 work. Weakens the statistical claim in proportion to the fits dropped.

**Option 4 — defer the block entirely** until Phase 2 allocation is known, and
spend the 1,681 on F95's schedule-4 check (~60 s, promised in the sent memo)
plus Phase 2 preparation that needs no device.

## Decision

**RECORDED 2026-10-02: not yet made.** This is a Class 3 allocation decision
and the sprint reached it as the last task, as planned. Until it is made, F2b
and F5 remain open and F90 remains unscheduled.

When the decision is made, this section records it with the reason, and:

- F2b's B4 line and F5 are closed into the surviving card
- the survivor's cost is labeled `measured` or `extrapolated`
- where the survivor differs from the sent plan's 270 s, that difference is
  written down here, because it is externally visible
