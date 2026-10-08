# B4 and B5 on Dirac-3: the result

Run 2026-10-06 from 07:30 local, Sprint 21 (F90). Evidence tag `[HW]`. Every
figure below is in `experiments/results/results.json` (block `B4` or `B5`),
summarized in `b4_hardware.json`, `b5_hardware.json` and the regenerated
`gate_report.md`. Full device responses, every returned sample included, are in
`experiments/results/pools/hw_responses/`.

> **Correction, 2026-10-06 (Sprint 22).** The sentence above is false for
> the stored files. The runners saved each response with
> `json.dumps(resp, default=str)`. A real solve returns a `SolutionResults`
> object, so its printed form was stored, and numpy prints long arrays
> truncated: each 560- and 816-value sample was saved as its first and last
> three values. The B4 rows in `results.json` also record
> `n_samples_returned` = 0, because the runner looked for a dict; the device
> did return 8 samples per fit. No AUPRC figure in this document is affected:
> scoring used the in-memory response, not the stored file. All samples were
> recovered by job id, read-only, with the allocation balance unchanged
> (1,022 s before and after), into
> `experiments/phase2/results/device_samples/`
> (`experiments/phase2/src/recover_device_samples.py`). The runners are fixed
> and `test_response_serialization.py` pins the fix. The stored files and the
> B4 rows are left as they are: they are Phase 1 evidence
> (`docs/PHASE_SEPARATION.md`). The sentence above stands beneath this note.

## Spend

| Block | Fits | Failed | Metered s | Per fit |
|---|---|---|---|---|
| B5, QSVM on ULB | 12 | 0 | 13 | ~1 s |
| B4, CVQBoost on SPECTRA | 10 | 0 | 640 | 34-90 s |
| **Total** | **22** | **0** | **653** | |

Reconciled against the device, not inferred: allocation balance 1,675 s before,
1,022 s after. Every job id is retained.

**The B4 cost conflict is settled by measurement.** telecom_churn cost 84-90 s
per fit at 816 variables and oilgas_gasturbine 34-46 s at 560. B2's measured
82.4 s/fit anchor was right. The 26-34 s/fit quoted in `HARDWARE_REQUEST_B4.md`
line 43 was about 2.4x low at 816 variables.

## B4: the in-segment replication does not reproduce on the device

The replication half of Experiment 5 (H5). Ten cells: telecom_churn and
oilgas_gasturbine, seeds 42-46. energy_steel is `unscoreable` because its
matched control cannot be drawn (`docs/SPECTRA_CONTROL_FEASIBILITY.md`).

**The in-segment edge against the matched random-segment control is negative on
every one of the 8 scoreable cells.**

| Cell | Seed | Test AUPRC | In-segment edge (AUPRC) | Proxy's edge | Weight cosine | Train-test gap |
|---|---|---|---|---|---|---|
| oilgas_gasturbine | 42 | 0.8526 | -0.1830 | -0.1498 | 0.895 | +0.147 |
| oilgas_gasturbine | 43 | 0.8408 | -0.1867 | -0.1421 | 0.901 | +0.159 |
| oilgas_gasturbine | 44 | 0.8234 | -0.2241 | -0.1665 | 0.899 | +0.177 |
| oilgas_gasturbine | 45 | 0.8342 | -0.1839 | -0.1474 | 0.892 | +0.166 |
| oilgas_gasturbine | 46 | 0.8440 | -0.1722 | -0.1319 | 0.901 | +0.156 |
| telecom_churn | 42 | 0.7621 | unscoreable | unscoreable | 0.850 | +0.238 |
| telecom_churn | 43 | 0.7396 | -0.1447 | -0.0971 | 0.832 | +0.260 |
| telecom_churn | 44 | 0.7664 | -0.0335 | -0.1400 | 0.833 | +0.234 |
| telecom_churn | 45 | 0.6966 | unscoreable | unscoreable | 0.835 | +0.303 |
| telecom_churn | 46 | 0.7025 | -0.0725 | -0.1368 | 0.836 | +0.297 |

**CORRECTION 2026-10-06: the "Proxy's edge" column is NOT like-for-like.** The
proxy rows in `spectra_proxy_dry_run.json` predate the complement-pool
correction (`775942b`), so their controls were drawn from the full pool and
could overlap the pocket they controlled for. The device's controls are drawn
from the complement. The device's edges are valid; comparing them with that
column is not. The clean device-versus-proxy comparison is inside the pocket
itself, where both arms score the identical rows:

| Cell | Seed | Device in-pocket AUPRC | Proxy in-pocket AUPRC | Difference |
|---|---|---|---|---|
| oilgas_gasturbine | 42 | 0.7918 | 0.7908 | +0.0010 |
| oilgas_gasturbine | 43 | 0.7889 | 0.7884 | +0.0004 |
| oilgas_gasturbine | 44 | 0.7571 | 0.7591 | -0.0019 |
| oilgas_gasturbine | 45 | 0.7950 | 0.7941 | +0.0009 |
| oilgas_gasturbine | 46 | 0.7999 | 0.8010 | -0.0011 |
| telecom_churn | 43 | 0.7562 | 0.7591 | -0.0029 |
| telecom_churn | 44 | 0.8101 | 0.8066 | +0.0035 |
| telecom_churn | 46 | 0.7528 | 0.7600 | -0.0072 |

The device is better on 4 of 8 cells, with a mean difference of -0.0009 and
no difference larger than 0.0072. Inside the pocket, the device and its
classical proxy are indistinguishable.

Every B4 fit used the full QFE phase representation the SPECTRA files carry:
all five `_phase` columns per dataset plus the raw covariates, the same
columns the proxy used. telecom_churn drops only `age`, by the frozen cell's
design. `in_pocket` and the two `target` columns are excluded as labels.

telecom_churn seeds 42 and 45 fall below the 50-positive floor (46 and 49 test
positives in the pocket), exactly as the B4 request predicted in advance. They
are reported per seed and are not averaged over or backfilled.

**What it says.**

- **Overall, the device reproduces its classical proxy almost exactly.** Test
  AUPRC differs from the proxy by at most 0.004 on every cell, with weight
  cosine 0.83-0.90 and every Hamiltonian at 8.1-8.4 dB, inside A31's ~23 dB
  resolution limit. Whatever the device does here, it does not differ from the
  classical solve of the same problem.
- **In-segment, there is no advantage.** The pocket scores worse than a random
  segment of the same size and fraud rate on all 8 scoreable cells. On
  oilgas_gasturbine the device's edge is slightly *more* negative than the
  proxy's; on telecom_churn it is less negative on 2 of 3 seeds. Neither is a
  positive edge.
- **It sits below the classical bar.** F100's HistGradientBoosting reaches
  0.874 on oilgas_gasturbine and 0.867 on telecom_churn
  (`docs/F100_CLASSICAL_BAR.md`); the device reaches 0.839 and 0.733.
- **Train-test gap +0.15 to +0.30 on every cell**, the fragility the prior work
  warned about, now measured on the device.

**What it does not say.** It does not refute the off-repository result the team
lead ran on 2026-10-03. That result is `[UNVERIFIED -- OFF-REPOSITORY]` here.
This block tests the frozen cells' configuration on this repository's splits,
seeds and matched control. It also says nothing about energy_steel, the cell
where the prior work reported its overall win, because that cell cannot be
scored under the frozen control. The Phase 2 design in F102 (a downsized
matched pair, repeated over draws) is what would score it.

## B5: the QSVM arm is cheap and weak

Sign-augmented primal QSVM on ULB, B1's top-13 features, 12 fits (ten
stratified seeds, one temporal, one repeat).

- **Test AUPRC 0.068-0.260, mean 0.212** (gate report t-95% CI [0.177,
  0.246]). The temporal fit is the 0.068. B1's CVQBoost on the same data reaches
  0.767.
- **11 of 12 Hamiltonians exceed A31's ~23 dB resolution limit** (20.8-42.3 dB,
  recorded per row). The device cannot resolve the smallest coefficients, which
  is a plausible contributor to the weak score. This is not established as the
  cause, and nothing in this sprint tested it.
- It cost what the frozen grid priced: 13 s for 12 fits.

## Known gap in the gate report, not fixed

`score_gates.is_metered_arm()` counts only `cvqboost_hw*` arms, so the
regenerated report's hardware section omits B5's 12 fits and 13 s, and its
header still names two arms as `[HW]`. `score_gates.py` is analysis code, and
PREREGISTRATION section 11 makes any change to it a dated amendment. The team
lead has ruled that no Phase 1 document is amended, so this is left as written
and put to him as a decision. The B5 rows themselves are complete and correctly
tagged.
