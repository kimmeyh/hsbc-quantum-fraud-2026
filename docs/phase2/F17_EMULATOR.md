# F17: Dirac-3 emulator

Sprint 22, Task D (#163). Phase 2. Zero metered seconds. Evidence tag SIM.

## Bottom line

- The emulator is **one tool with two modes**: `exact` and `emulate`. It does
  **not** replace the proxy. It imports `qubo_proxy.py` and does not change it.
- It runs a real `QBoostClassifier` or `QSVMClassifier` fit end to end and
  spends no device time.
- Against the 10 stored B4 device fits, it matches the device on test AUPRC to
  within about 0.006. Its cost estimate is within about 7% of the block means.
- **The plan's falsifier is met for AUPRC**: it reproduces the exact proxy as
  closely as the device does, so it predicts no AUPRC the proxy does not.
  Its value is cost estimates and multiple samples, not AUPRC.
- It does **not** match the device's solution shape on oilgas: weight cosine
  0.83 emulated against 0.89-0.90 on the device. Use it to rank ideas and to
  size runs. Do not use it as a substitute for device evidence.

Code: `experiments/phase2/src/dirac3_emulator.py`.
Validation: `experiments/phase2/src/validate_emulator.py`, which writes
`experiments/phase2/results/f17_emulator_validation.json`.
Tests: `experiments/src/test_dirac3_emulator.py`.

## The design question: replace, extend, or one tool with two functions

The team lead asked at plan approval (2026-10-06) which of these it should be.

- **Replace the proxy: no.** `qubo_proxy.py` produced Phase 1's filed
  evidence (`docs/PHASE_SEPARATION.md`, group B). Replacing it would change
  the tool that the filed numbers came from.
- **Extend the proxy in place: no**, for the same reason. An edit to a group B
  file is an edit to Phase 1.
- **One tool, two modes: yes.**
  - `exact` runs the proxy's own algorithm (FISTA projected gradient on the
    simplex, using `qubo_proxy._project_simplex` unchanged). A test pins that
    it returns the same weights as `qubo_proxy.solve_simplex_qp`.
  - `emulate` adds the three device behaviors this repository has measured.

## What `emulate` models

Each piece is anchored to a measurement.

1. **Resolution.** The device resolves coefficients to about 200:1 (amendment
   A31, about 23 dB). J and C are quantized to steps of max|coefficient| / 200.
2. **Samples.** Each of `num_samples` answers starts from a random point on
   the simplex and stops after a fixed iteration budget. This gives a spread
   of answers, as the device's 8 samples have.
3. **Cost.** `max(4.4, c * n_vars^2) * num_samples / 8`, times 3.8 at
   relaxation schedule 4. The value of c (about 1.227e-4) is fitted to every
   metered CVQBoost fit in `results.json`. Provenance is FITTED, not measured,
   for any other size.

It implements the `solve(model, ...)` interface of eqc_models'
`Dirac3CloudSolver`. The context manager `emulated_solver()` swaps it in for
the one network object. This is the same seam that `eqc_submit.offline_solver`
uses for dry runs.

## Calibration: the iteration budget

The budget sets how far each sample gets from its random start. The budget
was chosen to match the device's mean weight cosine against the exact
solution (0.8674 over the 10 B4 fits).

- Budget 25: mean cosine 0.8383, mean absolute gap to the device 0.0402.
- Budget 100: mean cosine 0.9214, gap 0.0540.
- Budget 400: mean cosine 0.9284, gap 0.0610.

**Calibrated budget: 25.** A larger budget converges further than the device
does.

## Validation against B4 (budget 25)

Per cell, from `f17_emulator_validation.json`:

- oilgas_gasturbine, 560 variables, 5 seeds:
  - device cosine 0.892-0.901; emulated 0.828-0.835.
  - device AUPRC is within 0.0010 of exact; emulated is within 0.0020.
  - cost: device 34-46 s (mean 41.2); estimate 38.5 s.
- telecom_churn, 816 variables, 5 seeds:
  - device cosine 0.832-0.850; emulated 0.835-0.852.
  - device AUPRC is within 0.0034 of exact; emulated is within 0.0054.
  - cost: device 84-90 s (mean 86.8); estimate 81.7 s.

## The plan's falsifier: met, for AUPRC

`SPRINT_22_PLAN.md` set this falsifier: "on B4's 10 cells, a resolution- and
sampling-aware simulator reproduces the proxy as closely as the device did
(within 0.0072 in-pocket AUPRC). Then the recommendation is no-go."

- It does. Emulated test AUPRC is within 0.0054 of exact on all 10 cells.
  Note the metric: the validation measured overall test AUPRC, not in-pocket
  AUPRC as the falsifier is worded. In-pocket AUPRC was not computed for the
  emulator. The conclusion is not expected to change, because the device's
  in-pocket gap to the proxy was also small (0.0072), but that is an
  inference, not a measurement.
- So, by the plan's own test, the emulator adds **no information about
  AUPRC** beyond the exact proxy. Its AUPRC is the proxy's AUPRC. This is
  expected, because the device also returns the proxy's answer.
- **Recommendation: no-go as an AUPRC predictor.** Rank levers by AUPRC with
  the exact proxy, which is cheaper.
- What it adds and the proxy does not:
  - a device-seconds estimate for any size (Criterion H statements);
  - several distinct samples per fit, so ideas that use samples can be tested
    (F20's top-k ensembling, `docs/phase2/F20_SOFT_VOTES_RESULT.md`);
  - an end-to-end code path through a real eqc_models fit.

## Limits

- **Oilgas shape miss.** The device lands closer to the exact answer on
  oilgas than the emulator does. One budget cannot fit both datasets. A
  per-size budget would fit these 10 fits and predict nothing new, so it was
  not done.
- **Cost depends on more than size.** 816 variables cost more than 833
  (86.8 s against 82.4 s). A size-only model cannot explain that. The test
  therefore checks each block mean within 10%, not a single curve.
- **It is not physics.** It reproduces observed behavior: resolution, sample
  spread and cost. A result that depends on how the device searches is not
  testable here.
- **Not gate evidence.** Results from it carry the SIM tag. No figure from it
  goes into a Phase 1 document.

## How to use it

- To rank candidate levers before any device run (F124).
- To size a run: `estimate_cost_s(n_vars, num_samples, relaxation_schedule)`.
  This gives the number that a Criterion H approval statement needs.
- To test code paths that a real response exercises, together with
  `eqc_submit.offline_solver`.
