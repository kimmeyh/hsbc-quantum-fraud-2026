# Sprint 22 Manual Validation

**Sprint**: 22, Separate the Phases, Then Look for Better Numbers
**Branch**: `feature/20261006_Sprint_22` | **PR**: #159 (draft)
**Scope**: F123 (A), IMP-3 (B), F124 (C), F17 (D), F20 (E), F125 (F)
**Metered Dirac-3 seconds spent: 0.** The balance read 1,022 s before and
after the read-only sample recovery.

This file is the durable copy. The same items are listed to the screen at
handover (team lead, 2026-10-03): a pointer to a file is not a handover.

---

## 1. Task C (F124): the ranked list -- YOUR APPROVAL GATES EVERY DEVICE RUN

Read `docs/phase2/SPECTRA_IMPROVEMENT_RESEARCH.md`, section 2.

- **Rank 1: leaf regularization (`min_samples_leaf=20`).** energy_steel
  0.902 to 0.973 AUPRC, 5 seeds; parity with HGB (+0.0085, CI includes
  zero). Native eqc_models parameter. Proposed device test: a 1-seed
  energy_steel pilot, about 82 s; 5 seeds about 410 s.
- **Rank 2: Laplace soft votes.** Mostly the same lever as rank 1: +0.006 on
  top of it.
- **Rank 3: KNN weak learners.** The only lever positive on all three
  datasets in the screen; matches an EvidenceBasedDB lead of low certainty.
- **Rank 4: boosted weak learners.** Parity on energy_steel, worse elsewhere.
  Not recommended for the device.
- **Ranks 5-6: feature engineering, pool size.** Not yet measured; proxy
  tests proposed.
- **Nothing closes the gap on telecom (about -0.10) or oilgas (about
  -0.03).** No lever beats HGB with a CI that excludes zero anywhere.
- **NeuraWave, from QCi's own releases**: edge time-series and signal
  hardware on a PCIe card. Not a fit for tabular SPECTRA, and not on the
  cloud allocation.
- **Card correction**: `batched_qboost_enabled` is not in the installed
  eqc_models 0.21.0.

Spot-check: `experiments/phase2/results/f124_lever_confirm_energy_steel.json`,
`summary.dct_min_leaf_20`.

## 2. Task A (F123): Phase 1 / Phase 2 separation -- decisions owed

Read `docs/PHASE_SEPARATION.md`, section 8. Provisional at approval
("could be adjusted during Manual Validation").

- All Sprint 22 work went to the Phase 2 tree: `experiments/phase2/src/`,
  `experiments/phase2/results/`, `docs/phase2/`. No group B file was edited
  by Tasks C, D or E.
- **Not yet done, waiting for you**: the MOVE of the post-filing files listed
  in section 3 (`run_hardware_b4.py`, `run_hardware_b5.py`, `eqc_submit.py`,
  the F100/F101 files and the B4/B5 summaries) into the Phase 2 tree.
- **Note**: `run_hardware_b4.py`, `run_hardware_b5.py` and `eqc_submit.py`
  were edited in place this sprint to fix the sample-storage defect (item 5).
  They are post-filing files, so this is not a group B edit, but they still
  sit in a Phase 1 directory until the move.

## 3. Task B (IMP-3): the suite may not change committed evidence

- `conftest.py` hashes every tracked and untracked non-ignored file under
  `experiments/results/` and `experiments/phase2/results/` before and after
  the run. Any change fails the run.
- Hardened after a background security review flagged four issues. Three
  were addressed from their titles: fail-open when git is missing, new files
  unseen, and the guard bypassable without trace. **The fourth finding's
  title was not shown to me and is not claimed as addressed.**
- Proven red: a created file, git missing, `--noconftest`, a modify without
  restore.

## 4. Task F (F125): the close-out hook's false block

- The hook now counts against `origin/develop`, then `develop`, then `HEAD`.
- The card's diagnosis was incomplete: a correct count alone still blocked,
  because the true count was 1. The fix is a plan-existence gate: with no plan,
  only docs and status files may change.
- My commit 63bc375 said the hook tests passed. One failed. Corrected in
  c62248a.

## 5. A Sprint 21 defect found this sprint: device samples were truncated

- The B4 and B5 runners stored each response's PRINTED form, and numpy
  truncates long arrays. Every B4 sample was saved as its first and last three
  values. The B4 rows record `n_samples_returned` = 0.
- No scored figure changed: scoring used the in-memory fit.
- All 22 responses recovered by job id, read-only, balance unchanged, into
  `experiments/phase2/results/device_samples/`. Root cause fixed: the offline
  stand-in returned a dict, so dry runs never saw the real response type.
- **It is older than Sprint 21: all 11 stored B2 responses are truncated
  too.** B2 has 833 variables, so its print crossed numpy's 1,000-element
  limit. B1, G0b, f32 and B5 are intact (small arrays print in full). The
  B2 sparsity figures in the QCi feedback document ("printed nonzero weights
  from 0.0007 to 0.0029") were read from about 6 visible values per sample.
  That document is locked and was not touched (D8).
- **Decision needed (item D2 below)**: I added a dated correction note to
  `docs/B4_B5_HARDWARE_RESULT.md`. That file post-dates the filing, so it is
  Phase 2 by `PHASE_SEPARATION.md`'s rule, and the note is additive like the
  `HARDWARE_REQUEST_B4.md` precedent. But it describes Phase 1 grid blocks.

## 6. Task E (F20): soft votes and ensembling

Read `docs/phase2/F20_SOFT_VOTES_RESULT.md`.

- Soft votes as the card specified are degenerate: raw `predict_proba` is
  exactly 0 or 1.
- Laplace-smoothed soft votes: better on all 15 cells. energy_steel +0.074
  AUPRC; telecom +0.030; oilgas +0.005. Only energy_steel clears the plan's
  0.05 falsifier.
- Soft-vote CVQBoost against HGB: parity on energy_steel (CI includes zero),
  clear losses on telecom and oilgas.
- Multi-sample ensembling: not evaluable on device samples (rebuilt pools do
  not reproduce, 0 of 10). On emulated samples +0.0014: fails the falsifier.

## 7. Task D (F17): the Dirac-3 emulator

Read `docs/phase2/F17_EMULATOR.md`.

- One tool, two modes (`exact`, `emulate`). It imports `qubo_proxy.py`
  unchanged. This answers your design question.
- **The plan's falsifier is met for AUPRC**: the emulator reproduces the
  proxy as closely as the device does. So it is no-go as an AUPRC predictor.
  Its value is device-seconds estimates and multiple samples per fit.
- Metric caveat: validated on overall test AUPRC, not in-pocket AUPRC as the
  falsifier is worded.
- **The card's own acceptance test FAILS: the emulator does not reproduce the
  device's sparsity.** Device exact-zero fraction 0.14-0.16 (oilgas) and
  0.35-0.38 (telecom); emulator 0.002-0.004 and 0.14-0.17. Tested on B4,
  because the card's B2 test cannot run (pools not stored, B2 samples
  truncated).
- The device's smallest nonzero weights are about 0.00001, far below the
  ~0.005 resolvable step. "Weights below the step are zeroed" is not what the
  device does.
- Recommendation: keep the emulator for cost estimates and samples; do not
  use it to size Experiment 3 until a sparsity model is built and validated
  on held-out data (D9).

---

## Decisions for the team lead

D1. **Approve, amend or reject the F124 ranked list** (section 1). Nothing
    on it reaches Dirac-3 without this, and each device block still needs its
    own Criterion H approval.

D2. **The correction note in `docs/B4_B5_HARDWARE_RESULT.md`**: keep it, or
    move it to a Phase 2 document and revert the file.

D3. **F123 section 4.1**: freeze group B in place (recommended), or
    section 4.3, relocate all post-filing evidence.

D4. **The F123 MOVE** of the post-filing files listed in section 3 of
    `PHASE_SEPARATION.md` into the Phase 2 tree: approve, or keep them where
    they are.

D5. **The `spectra_segment.py` record**: the dated note in
    `PHASE_SEPARATION.md` (recommended), or something else.

D6. **IMP-4 and the placement check** as designed in `PHASE_SEPARATION.md`
    section 6: approve for a later sprint, amend, or drop.

D7. **Phase 2 results format.** The layout says Phase 2 evidence goes in its
    own `results.json` with the section-11 row schema. This sprint wrote one
    JSON file per experiment instead (generator, card, evidence tag SIM,
    metered seconds 0, eqc_models version, rows, summary). No Phase 2
    `results.json` exists yet. Recommendation: keep per-experiment files for
    exploratory proxy work, and require schema rows in a Phase 2
    `results.json` from the first run under the Phase 2 preregistration
    (F102) or the first device run, whichever comes first.

D8. **Recover B2's 11 device responses by job id**, read-only, as was done
    for B4 (zero spend, balance checked before and after), into
    `experiments/phase2/results/device_samples/`. It would give the full
    B2 samples and test the sparsity figures sent to QCi. It is a read of
    filed Phase 1 evidence from QCi's servers, so it waits for you.

D9. **F17 sparsity model**: card it as follow-up work (build and validate a
    model of the device's zeroing on held-out data), or stop F17 at cost
    estimates.

## Definition of Done, walked

- **Acceptance met with evidence**: each task's document names its result
  file. F17 and F20 falsifiers are reported as they came out, including the
  F17 falsifier that was met.
- **Suite green**: full suite passed on the final code; the IMP-3 guard did
  not fire.
- **Every number in a results file with its evidence tag**: yes, in the
  per-experiment files (see D7 for the format gap).
- **No Phase 1 file changed by this sprint's tasks**: checked with
  `git diff origin/develop...HEAD` against the filing commit `f35699c`. Files
  that existed at the filing and changed: `.claude/sprint_status.json`,
  `CHANGELOG.md`, `docs/ALL_SPRINTS_MASTER_PLAN.md` and one test. None is in
  group L or group B. No file under `experiments/results/`, `docs/paper/`,
  `docs/submission/` or `PREREGISTRATION.md` changed. The only non-test code
  changed under `experiments/src/` is the three post-filing runner files
  (item 5).
- **Every new results file where F123's layout says**: all under
  `experiments/phase2/results/`.
- **Zero metered seconds**: yes.

## Effort

Wall-clock minutes from `.claude/sprint_status.json`, recorded as each task
finished:

- Task A (F123): 30 (estimate 120)
- Task B (IMP-3): 32, including hardening (estimate 30)
- Task F (F125): 45 (estimate 20)
- Tasks D (F17) and E (F20): 34 together. They ran in parallel and are not
  separable (estimates 390 and 180)
- Task C (F124): 95, overlapping E (estimate 240)
- Task D follow-up, the card's sparsity acceptance test: 20, overlapping C
- **Total recorded: 256 minutes against 980 estimated.** The overlaps mean
  the sum exceeds elapsed time.
- Device seconds: 0.
