# Sprint 21 Manual Validation

**Sprint**: 21, The SPECTRA Block and a Bar That Can Read It
**Branch**: `feature/20261004_Sprint_21` | **PR**: #152 (draft)
**Scope**: F90, F100, F101, F122
**Metered Dirac-3 seconds spent: 0 at the time of writing.** B5 and B4 are
pre-approved and wait for the 18:00 window.

This document is the durable copy. **The items are also listed to the screen**
as the last step before validation begins, per the team lead's instruction of
2026-10-03 — a pointer to a file is not a handover.

---

## 1. Task B (F122): four guards rewritten, each proven RED

Check: `experiments/src/test_ci_status.py`,
`test_spectra_reconciliation.py`, `test_sent_correspondence.py`

- **(a)** The ordering guard anchored on `ci.evaluate(` and the `gh pr list`
  subprocess instead of comment text. Renaming a comment no longer fails it;
  moving the code no longer passes it. Call-site counts asserted so a second
  call site cannot make the ordering ambiguous.
- **(b)** The decision guard accepts two legitimate states — deferred, or
  decided **with attribution and a date** — and rejects a choice with nobody's
  name on it. It no longer goes red on the day a decision is correctly
  recorded.
- **(c)** The options guard now requires a figure in seconds inside each
  option's own body. **It found a real gap on its first run**: Option 3 in the
  reconciliation carried no cost. Now 9 fits ≈740 s, 6 ≈494 s, 3 ≈247 s.
- **(d)** The sidecar manifest descends with `rglob` and keys on POSIX
  relative paths, so a file added in a subdirectory is caught and same-named
  files in different directories cannot collide.

**Evidence to spot-check**: the proof scripts showed, for (a), comment-rename
GREEN and fail-open-probe-moved-first RED; for (d), the same added file RED
under new code and GREEN under old. One of my rewrites — (b) — was itself
vacuous on the first attempt (it searched the whole file for an attribution the
options section already contains) and the proof caught it before commit.

## 2. Task E (F101): the router gate is not independent

Check: `docs/F101_IN_POCKET_PROVENANCE.md`,
`experiments/results/f101_in_pocket_provenance.json`

- `in_pocket` is predictable from the SPECTRA phase features at **AUC
  0.93–0.99**, across two model classes, three seeds, all three frozen cells.
- One anomalous number is **kept with its cause named**: energy_steel seed 44
  logreg reads 0.5911 because the solver hit its iteration limit on unscaled
  features; HGB on the identical split gives 0.9935.
- The document states what this does **not** settle: whether the pocket is
  defined by a rule over these covariates (predictability is then
  definitional) or independently defined and merely correlated (a router would
  re-correlate it). **That is a question for the SPECTRA author**, narrowed to
  one sentence in the document.

## 3. The Criterion 7 finding and how it was resolved

Check: `docs/SPECTRA_CONTROL_FEASIBILITY.md`

- H5(ii)'s rate-matched control is **arithmetically impossible on
  energy_steel, all five seeds**: the pocket holds 918–950 of the test fold's
  positives, the complement holds 832–864. **5 of 15 frozen cells affected.**
- The committed dry run hides it: those rows predate the complement-pool
  correction (`775942b`) and report controls of 927–950 positives — an
  impossible draw — so they overlapped the segment they controlled for.
- **`experiments/PREREGISTRATION.md` is NOT amended and NOT edited.** Section
  11 forbids an amendment that changes a gate's pass/fail criterion; H5(ii)'s
  control is that criterion, so the change would be a reported DEVIATION. My
  "Class 1 amendment" framing was wrong; the team lead corrected it.
- Phase 1 reports energy_steel **`unscoreable`**, an outcome the gate table
  already has a column for.
- `evaluate_in_segment` now reports rather than raises, so the 10 feasible
  cells still score in the same run. `matched_random_segment` **still raises**
  — the library contract is unchanged; only the scoring path routes around it.

**Verify the correction reached all three citing documents** — "13 of 13" is
now 8 of 13 in `ALL_SPRINTS_MASTER_PLAN.md` and
`SPECTRA_BLOCK_RECONCILIATION.md` (both places), and in
`HARDWARE_REQUEST_B4.md` it is **additive**, leaving the sent text standing,
because that document records what went to QCi.

The conclusion survives: all 8 feasible cells are still negative.

## 4. Option 5 specified for Phase 2, not retrofitted to Phase 1

Check: the F102 card in `docs/ALL_SPRINTS_MASTER_PLAN.md`

- The downsized matched pair with repeated draws is written into F102, with
  the arithmetic **verified not asserted**: 855 positives + 278 negatives per
  side on seed 42, 88–94% of pocket positives retained across the five seeds,
  interval ~4% wider, and the 50-positive floor cleared on all five.
- The card states why this is specification rather than a retrofit, because a
  reviewer will ask: the design follows from a structural property of the
  dataset, not from any observed result, and Phase 2's data does not exist
  yet.
- Confirmed with the team lead: a Phase 2 preregistration binds only from its
  November filing, so F102 stays revisable until then.

## 5. B5 and B4 runners: built, guarded, awaiting the window

Check: `experiments/src/run_hardware_b5.py`, `run_hardware_b4.py`
and their test files

- **B5 was fully specified all along** — frozen preregistration section 10
  (12 fits, ~15 s), section 4 (sign-augmented primal QSVM), and the Sprint 3
  F18 notes resolved every implementation question. **Only the code was
  missing.** I reported "no definition in this repository" after grepping
  `*.py` and the hardware docs without opening the preregistration; that was
  the same reasoning-from-absence as Sprint 20's F93 miss.
- **Cost provenance corrected**: F90's card said "15–62 s" extrapolated from
  B3's 5.2 s/fit, a CVQBoost rate at a different variable count. The frozen
  grid's own figure is ~15 s for 12 fits.
- **B4 runs 10 of 15 cells**, derived from live feasibility — an AST guard
  forbids a hardcoded cell name or skip list, proven RED against both.
- **B4's Criterion H statement quotes a BAND, 250–680 s, and names the
  conflict**: `HARDWARE_REQUEST_B4.md` line 43 says 26–34 s/fit (~450 s,
  matching the frozen envelope); our B2 measured 76–91 s/fit at a
  configuration matching B4's exactly. Both are described as measured.
- **Three matrix-orientation bugs in B4, all mine**, found by checking
  `h_matrix`'s real shape: a train-score axis, a `J` build that would have
  allocated 3.6 GB at 22,039 rows, and a weak-learner count reading 22,039 for
  a 560-variable cell.
- Safety verified without submitting: dry runs spend nothing, **both runners
  refuse before 18:00 and exit 3** (not 0 — a guard that refuses while
  reporting success is this repository's most-repeated defect), failed rows
  stay retryable, an unreadable ledger refuses to submit, another block's
  seconds are not charged, and the artifact is written after **every** fit.

## 6. Task D (F100) pilot: sized, and the bar is higher than the proxy

Check: `docs/F100_LANE_PILOT.md`,
`experiments/results/f100_lane_pilot.json`

- Estimated ~6 hours `[no-history]`; **measured 3.77 seconds per cell.**
  Dominant lane named with its measurement: HGB at 2.34 s. All 15 cells is
  under a minute.
- **HGB (0.8871 AUPRC) and GA2M (0.8699) both beat the CVQBoost proxy
  (0.8520)** on this cell. The classical bar is not a formality.
- The document states the limits and a guard enforces that it keeps doing so:
  one cell, one seed, **overall** metrics, comparator is `[PROJ]` — nothing
  here is about Dirac-3 or about H5.

## 7. CI went red from my own test, and local green did not show it

- The datasets are not redistributed, so CI has no ULB CSV. My feasibility and
  B4 guards skip correctly; the **B5 dry-run fixture** asserted
  `returncode == 0`, and a module-scoped fixture failing **errors** every
  dependent test (2 errors against 1,495 passed).
- Fixed to skip **visibly** with its reason, which `addopts = -rs` prints.
  Verified by hiding the dataset locally: 13 passed, 2 skipped, zero errors.
- This is exactly what `SPRINT_EXECUTION_WORKFLOW.md` warns about: do not
  treat a local green suite as evidence that CI is green.

---

## What is NOT done, and why

- **Task A (F90 first task) is yours**: bringing in the off-repository device
  result with its configuration, fits, seeds and arm. It gates the metered run
  and Task D's full grid.
- **Task C's metered run waits for 18:00**, by your instruction. Both blocks
  are pre-approved; the runners refuse before the window.
- **Task D's full grid waits on Task A**, because the card's purpose is to read
  F90's result and the anchoring configuration must match what the device ran.

## Effort so far

- Task B: 58 min (estimate 45)
- Task E: 34 min (estimate 60)
- Task C pilot: 42 min; Task C runners: 112 min (estimate 240 total)
- Task D pilot: 47 min (estimate 360 for the full task)
- **293 minutes of 750 estimated**, with the metered run and Task D's grid
  outstanding.
