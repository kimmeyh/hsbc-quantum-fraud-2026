# Sprint 21 Manual Validation

**Sprint**: 21, The SPECTRA Block, and a Bar That Can Read It
**Branch**: `feature/20261004_Sprint_21` | **PR**: #152 (draft)
**Scope**: F90, F100, F101, F122
**Metered Dirac-3 seconds spent: 653** (B5 13 + B4 640), reconciled against the
device balance, 1,675 s to 1,022 s.

This file is the durable copy. The same items are listed to the screen at
handover (team lead, 2026-10-03): a pointer to a file is not a handover.

---

## 1. B4 and B5 ran: check the result and the spend

Read `docs/B4_B5_HARDWARE_RESULT.md`.

- **B4 (H5 replication), 10 feasible cells:** the device matches its proxy
  within 0.004 AUPRC overall. **The in-segment edge against the matched
  control is negative on all 8 scoreable cells** (oilgas -0.17 to -0.22,
  telecom -0.03 to -0.14). telecom seeds 42 and 45 are unscoreable at the
  50-positive floor, as the B4 request predicted. energy_steel stays
  unscoreable (control infeasible).
- **B5 (QSVM on ULB), 12 fits:** test AUPRC mean 0.212 against B1 CVQBoost's
  0.767; 11 of 12 Hamiltonians exceed A31's ~23 dB resolution limit.
- **Spend:** 653 s, and the device balance moved by exactly that. All 22 job
  ids are retained; every device response is committed.
- **Cost conflict settled:** B2's 82.4 s/fit anchor was right (telecom 84-90
  s/fit at 816 variables).

Spot-check one row: `experiments/results/results.json`, block `B4`, any seed.
Confirm `evidence_tag: HW`, a `job_id`, `metered_seconds`, `in_segment.edge`,
`dynamic_range_db` and `weight_cosine_vs_classical`.

## 2. Why the runners were rebuilt the night before

- The first B4 and B5 runners **hand-built the request to QCi with invented
  field names**. The accidental B5 call was rejected with a 400. They now
  submit through `eqc_models` exactly as B2 and B3 did (`eqc_submit.py`).
- My claim that they were "built, guarded and proven" was wrong: the dry run
  stopped before the request was built. The dry run now runs everything except
  the HTTP call, and it caught a scoring bug the old one could not reach.
- A guard forbids any runner from building part of a job body (proven red).

## 3. Safety fixes around metered runs

- **My own tests submitted two real jobs on 2026-10-05; nothing was billed, by
  luck.** Runners now refuse inside any test process, before anything else.
- **A test was rewriting the committed gate report** without restoring it.
  That made 4 failures appear on one suite run and vanish on the next. It now
  restores byte-for-byte, proven with a probe line.
- A canceled CI run now reads UNDETERMINED, not RED.

## 4. Task D (F100): the classical bar

Read `docs/F100_CLASSICAL_BAR.md`. HGB and GA2M beat the CVQBoost proxy on
all three SPECTRA cells, 5 of 5 seeds, CIs excluding zero. Measured 3.77 s per
cell against a ~6 hour estimate.

## 5. Task E (F101): the router gate

Read `docs/F101_IN_POCKET_PROVENANCE.md`. `in_pocket` is predictable from the
phase features at AUC 0.93-0.99, so a gate on those features is not
independent. Whether the pocket is DEFINED by those features is a question for
the SPECTRA author.

## 6. The energy_steel control finding

Read `docs/SPECTRA_CONTROL_FEASIBILITY.md`. The matched control is impossible
on energy_steel, all five seeds. "13 of 13" was corrected to 8 of 13 in three
documents; `HARDWARE_REQUEST_B4.md` was corrected additively, leaving the sent
text standing. `PREREGISTRATION.md` is untouched; the repaired control is
specified for Phase 2 in F102.

## 7. Task B (F122): four guards rewritten

Each was proven red against a mutation the original survived. Guard (c) found
a real gap on its first run: Option 3 in the reconciliation had no cost.

---

## Decisions for the team lead

1. **The gate report omits B5's 13 s and 12 fits** from its hardware spend
   line, because `score_gates.is_metered_arm()` counts only `cvqboost_hw*`
   arms. Fixing it changes frozen analysis code, which section 11 makes a
   dated amendment. You have ruled out Phase 1 amendments, so it is left as is
   unless you decide otherwise.
2. **QCi was told Experiment 5 costs 270 s.** B4 cost 640 s for 10 of the 15
   cells. Telling QCi is your action; nothing was sent.

## Effort

- Task A: 0 min (closed as already satisfied)
- Task B: 58 min (estimate 45)
- Task C: 42 pilot + 112 runners + 39 rebuild + 36 verification = 229 min,
  plus 653 device seconds (estimate 240)
- Task D: 47 pilot + 86 grid = 133 min (estimate 360)
- Task E: 34 min (estimate 60)
- **Total: 454 minutes against 750 estimated**
