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

**F90 carries the measured COST and names the configuration.** Its cost
anchor is solid. Its *accuracy* case is not: it says schedule 2 lost overall 8
of 8 to the classical arm with only about 3 in-segment metrics won, while
schedule 3 reached in-segment ROC 5 of 7, PR 6 of 7, and an overall win on
`energy_steel`.

**Those accuracy figures are PROXY figures, not device figures** (checked
2026-10-03). They ARE sourced: `experiments/results/spectra_proxy_dry_run.json`
shows 13 of 13 scored in-segment cells with a negative edge, and the
preregistration names the origin at line 46 (FourierWall2, 2026-08-04). But
every row carries `evidence_tag: PROJ` and `metered_seconds: 0`.

So "schedule 2 lost 8 of 8" describes the CLASSICAL PROXY losing in-segment.
It says nothing about the device, which this repository has never run on
SPECTRA. Reading it as a device result -- which my original wording invited --
is the same error as A31's inverted reading in Sprint 18: taking a proxy
behavior for a device prediction. The cost anchor is unusually strong: the schedule-3 QUBO is
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

**MADE 2026-10-03: proceed. Team lead, on evidence from outside this
repository.**

> "I have run this on another computer and QCi Dirac-3 on SPECTRA won in
> almost all cases so we will proceed regardless of the current analysis."

He also directs that **the SPECTRA analysis matching prior Dirac-3 work on
quantum-enhanced datasets runs in the next sprint.**

### This repository already held the answer, in a document I did not open

**The most useful finding here is about my own process, so it goes first.**

`docs/HARDWARE_REQUEST_B4.md` line 89 already states, in this repository,
tracked, that the 13 negative proxy edges are expected and are "not a red flag
for B4" -- because the effect being replicated is a CVQBoost hard-vote
advantage, not a ridge-proxy advantage. It also already carries the tuned
configuration's measured per-fit costs.

I built this document's analysis without reading it. I searched
`results.json`, found no SPECTRA rows, and reasoned from absence -- which is
the CLAUDE.md rule about not stating what an external system contains without
opening it, applied to my own repository. The team lead's correction was
needed only because I had not looked.

### There is no conflict. The two results are from different ARMS

My first reading of this was wrong, and the correction is the useful part.

I checked `results.json`, found zero SPECTRA rows, and concluded the
repository's "schedule 2 lost" claim was an uncited recollection. **Both halves
of that were wrong.** The evidence is in
`experiments/results/spectra_proxy_dry_run.json` -- 15 rows carrying
configuration hashes, seeds and evidence tags -- and the preregistration names
the origin at line 46, a prior exploratory sweep from the FourierWall2
campaign of 2026-08-04. I looked in one file and generalized to the whole
repository.

**The data supports the claim rather than undermining it**: 13 of 13 scored
in-segment cells show a NEGATIVE edge, at 560 and 816 variables, across all
three datasets tested.

**But every one of those rows is `evidence_tag: PROJ`, `metered_seconds: 0`.
They are the CLASSICAL PROXY. This repository has never run SPECTRA on
Dirac-3.**

That dissolves the conflict. The team lead ran the **device**; this repository
ran the **proxy**. A device win where the proxy loses does not contradict our
evidence -- it is the most interesting result this block can produce, and it
is the same shape as B2, where the device's sparsified answer outperformed the
exact classical solve at 833 variables.

It also removes the main argument against spending here, and for a second
reason found on 2026-10-03.

**MY "SCHEDULE 2 LOST 8 OF 8" WAS THE BASELINE CONFIGURATION, NOT THE TUNED
ONE.** Consulted for planning (a prior-campaign findings document held outside
this repository, team lead's reference, not cited here as evidence): the 8-of-8
overall loss is the schedule-2 baseline. The TUNED configuration -- schedule
3, 8 samples, relaxation schedule 2, and a ridge of about twice the record
count -- moves CVQBoost from uniformly behind to in-segment leader, winning
in-segment ROC on 5 of 7 cells and PR on 6 of 7, and winning OVERALL on
`energy_steel`.

So Option 2's "confirmed negative" was confirmed about a configuration nobody
proposed running. F90 already specified schedule 3, which is the configuration
that wins. The team lead's device result is consistent with that prior work
rather than in tension with anything.

**ONE CAVEAT THE NEXT SPRINT MUST CARRY, and it is not in any card yet.** Those
in-segment wins come with a severe generalization gap: in the prior campaign
CVQBoost's in-segment train-to-test drop was three to eight times XGBoost's on
every `target` cell, with one case falling from 0.98 train to 0.59 test. The
test-set wins are real, and they are fragile. Any Phase 2 claim from this block
reports the train-test gap beside the win, or it overstates what was found.

### What is now recorded, and what is still open

**Recorded**: the block proceeds. Dirac-3 won in almost all cases on SPECTRA
in a run on another machine, 2026-10-03, reported by the team lead.

**`[UNVERIFIED -- OFF-REPOSITORY]`**, and labeled that way deliberately
until it is brought in: the configuration used (schedule and variable count),
the fit and seed counts, the metric, and whether it ran on Dirac-3 hardware
or a proxy. None of that is knowable from inside this repository, and a
Phase 2 claim cannot rest on a figure nobody here can check.

**Still open, and it is a sizing question rather than a go/no-go**: which
configuration the next sprint runs, and therefore whether it costs nearer the
sent plan's 270 s or F90's ~1,236 s. The 4.6x gap against what QCi was told
does not disappear because the block is approved -- if the spend lands well
above 270 s, that difference is still externally visible and still needs
stating to QCi rather than being discovered by them.

### Consequently

- F2b's B4 line and F5 are closed into F90, the surviving card
- F90 is unblocked and scheduled for the next sprint, carrying this decision
- The next sprint's card records the off-repository result as its motivation
  and brings the configuration into the repository as its first task, so the
  claim stops being unverifiable
