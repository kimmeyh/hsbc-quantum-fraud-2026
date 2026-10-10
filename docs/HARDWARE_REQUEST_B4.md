# Hardware Request: Block B4 (SPECTRA replication)

> **STATUS: NOT APPROVED, deferred (team lead, 2026-09-05).** The request was
> presented with its own dry-run findings and declined for now, on sequencing
> rather than science. Three reasons: (1) every scored proxy cell shows a
> NEGATIVE edge, in-segment trailing its matched control by 0.05-0.17 AP, so the
> proxy cannot forecast the hardware result and the 450 seconds would buy an
> untested expectation; (2) telecom_churn's test pocket is fragile, with 2 of 5
> seeds below the 50-positive floor, so that cell reports unscoreable on 40% of
> its seeds before measuring anything; (3) 450 seconds is 2.8x the entire
> metered campaign to date (163 s over 37 fits) for a block that does not touch
> the HSBC submission, in its final ten days.
>
> **Re-present when either condition changes**: telecom_churn's floor problem is
> fixed (a larger pocket or a substitute cell) and some signal survives to
> hardware; or the QCi 30,000-second grant lands, at which point B4 costs 1.5%
> of the budget and the calculus changes. H5 remains a preregistered hypothesis
> and the machinery is built and tested; only the timing is deferred.


**Purpose**: The written request for the B4 metered Dirac-3 block, per PREREGISTRATION section 10 and Criterion H. Nothing in this document authorizes execution; the block runs only on explicit team-lead approval of this request (or its amended successor). This document is DRAFTED ONLY (Sprint 6 Task D / F24, card #34); no metered second has been spent against it.
**Audience**: Team lead (approver); the future execution session (F5, Sprint 8).
**Last Updated**: 2026-09-05 (drafted; awaiting the QCi grant and team-lead approval per the frozen spend priority B3 > B2 > H3 ladder > B4)

## Standing conditions (all blocks; identical to HARDWARE_REQUEST_B1_G0b.md)

- Explicit per-block team-lead approval quoting this document; approval of one block never covers another.
- Retry rule (frozen): an errored solve retries at most TWICE with identical config and seed; retries counted in the row; third failure = cell reported failed. NO config-mutating backoff (F18 disposition 5); `fail_fast_on_variable_limit` behavior applies.
- Every fit = exactly one metered call; results land as [HW] rows in results.json with `metered_seconds` from the response and the same config_hash as the matching proxy row.
- Credentials per ADR-0011 (gitignored .env, QCI_API_URL=https://api.qci-prod.com + QCI_TOKEN, never printed).
- Pre-request sizing check: variable counts below computed with the A2-corrected `data.qubo_vars` (sequential-build formula, mandatory on Windows); documented device limit 949; free-tier limit ~100. All three B4 cells run on the paid/device tier (560-816 vars each), not free tier.
- Provenance precondition (ADR-0003): `scripts/manifest.py verify` must report VERIFY OK, and the SPECTRA files must be independently confirmed to match the FourierWall2-era source before this block runs (done for this draft; see Provenance section below -- re-verify at execution time since the manifest reflects the CURRENT checkout, not a permanent proof).

## Block B4: SPECTRA replication, 3 strongest in-segment cells x 5 seeds

| Item | Value |
|---|---|
| Design | H5(i): replicate the SPECTRA in-segment result with 5 seeds (42-46, house stratified 60/20/20 split, label=`target`) on the 3 FROZEN strongest in-segment cells identified from the FourierWall2 tuned rollout (2026-08-04). Each cell reports in-segment metrics AND a matched random-segment control (same size, same base rate) per H5(ii)'s machinery, applied here since the same small-sample risk exists. The >=50-test-positives-per-cell rule is enforced in code (`spectra_segment.evaluate_in_segment`); a seed/cell falling short is reported `unscoreable`, never silently dropped or imputed. |
| Frozen cells (config_hash from `spectra_segment.FROZEN_CELLS`) | `spectra_energy_steel` (`d82b1280000c175d`, 17 features, schedule 3, 816 vars); `spectra_oilgas_gasturbine` (`3f963271f7dbeb08`, 15 features, schedule 3, 560 vars); `spectra_telecom_churn` (`fa22671e965a8b46`, 17 features after dropping `age`, schedule 3, 816 vars) |
| Fixed config (all 3 cells) | `weak_cls_schedule=3`, `num_samples=8`, `relaxation_schedule=2`, `lambda_coef = 2 * n_train` (adaptive per dataset, `LAMBDA_COEF_ALPHA=2.0`), `weak_cls_params={}` (default weak-learner depth), leak-free features (`target`/`target_real`/`in_pocket` excluded; contract enforced by `spectra_segment.assert_no_label_leak` and a dedicated test), sequential weak-classifier build (mandatory on Windows) |
| Cells | per frozen dataset: 5-seed stratified primary (seeds 42-46) |
| **Call count** | **15 fits = 15 metered calls** (3 datasets x 5 seeds) |
| Cost basis | measured FourierWall2 (CVQBoost_Findings.md section 4, section 9/10 rollout notes): schedule=3, ns=8, rx=2 measured at 26-34 QPU s/fit on oilgas_gasturbine (~560 vars); the tuned 8-cell rollout (7 successes + 1 retried) totaled ~262 QPU s for cells at 298-987 vars, i.e. roughly 26-40 QPU s/fit at this ns/rx/schedule setting across the variable-count range this block spans (560-816 vars) |
| **Expected total** | **~390-510 QPU s** (5 seeds x 3 cells x ~26-34 s/fit central estimate ~450 s; prereg section 10 envelope for B4 is ~450 QPU s, cited as-is) |
| Gated on | QCi grant + SPECTRA re-download per prereg section 10 (re-download requirement: see Provenance section -- this draft's finding is that no re-download is in fact needed, the staged copies already match; re-verify at execution time regardless) |
| Seeds | primary 42-46 per dataset (15 calls total; no temporal-sensitivity variant -- SPECTRA carries no time-ordered protocol in the preregistration) |

## Provenance (ADR-0003 precondition; this draft's finding)

`scripts/manifest.py verify` reports **VERIFY OK** against the currently staged `experiments/data/spectra/*.csv` files (SHA-256, byte count, line count all match `experiments/data/MANIFEST.json`, generated 2026-09-01).

Independently, the staged files were compared byte-for-byte (SHA-256) against an earlier private copy of the same four files (staged 2026-08-02, predating both the FourierWall2 2026-08-04 tuned rollout this block replicates and this repo's 2026-09-01 manifest generation). **All four hashes match exactly**:

| Dataset | SHA-256 (staged == FourierWall2-era copy) |
|---|---|
| spectra_energy_steel.csv | `b07007b5db6b619b31073e46ea802dc575f6eb617d71a048a2775ad481020142` |
| spectra_maintenance_ai4i.csv | `979db538a6458471fc862bf9ffd5658260d188f577cd12244d1f9b86672c0d55` |
| spectra_oilgas_gasturbine.csv | `2c78870bd3400b9f8cbb522ed36e09309f087f0fd2fdd804043cf092ea308801` |
| spectra_telecom_churn.csv | `71dff0dbf95f019e8eefbac0efdb16075553ee80e948a3a72101fbb9a0b90334` |

Row counts also match `data.SPECTRA_ROWS` exactly (35040/36733/10000/3150 data rows + header). **Conclusion: the staged SPECTRA files are byte-identical to the FourierWall2-era files.** Prereg section 10's stated gate "QCi grant + SPECTRA re-download" is satisfied without a re-download; re-download was a hedge against possible drift, and this draft found none. Re-verify with `scripts/manifest.py verify` immediately before executing B4, since a later re-stage could still introduce drift between this finding and execution time.

## Proxy dry run (zero metered; sets this request's expected values)

`spectra_segment.proxy_dry_run()` reproduces the FourierWall2 preprocessing (`main.py::_coerce_features_to_numeric`, ported verbatim for the few non-numeric raw covariates energy_steel carries) and solves the identical Hamiltonian classically (ADR-0002 non-negative ridge, the same solver `qubo_proxy.py` uses for ULB), across all 5 H5(i) seeds (42-46, house stratified split), zero Dirac-3 calls:

| Dataset | vars | seed | overall test AP | in-segment test AP | matched-control AP | edge (seg - ctrl) |
|---|---|---|---|---|---|---|
| spectra_telecom_churn | 816 | 42 | 0.7628 | **unscoreable** (46 test pos < 50) | not computed | -- |
| spectra_telecom_churn | 816 | 43 | 0.7367 | 0.7613 | 0.8567 | -0.0953 |
| spectra_telecom_churn | 816 | 44 | 0.7636 | 0.8095 | 0.9414 | -0.1319 |
| spectra_telecom_churn | 816 | 45 | 0.6985 | **unscoreable** (49 test pos < 50) | not computed | -- |
| spectra_telecom_churn | 816 | 46 | 0.7040 | 0.7540 | 0.8960 | -0.1420 |
| spectra_energy_steel | 816 | 42 | 0.9009 | 0.9324 | 0.9858 | -0.0533 |
| spectra_energy_steel | 816 | 43 | 0.8929 | 0.9252 | 0.9766 | -0.0514 |
| spectra_energy_steel | 816 | 44 | 0.8921 | 0.9080 | 0.9854 | -0.0773 |
| spectra_energy_steel | 816 | 45 | 0.9101 | 0.9299 | 0.9839 | -0.0540 |
| spectra_energy_steel | 816 | 46 | 0.9144 | 0.9318 | 0.9892 | -0.0574 |
| spectra_oilgas_gasturbine | 560 | 42 | 0.8523 | 0.7923 | 0.9412 | -0.1489 |
| spectra_oilgas_gasturbine | 560 | 43 | 0.8416 | 0.7900 | 0.9308 | -0.1408 |
| spectra_oilgas_gasturbine | 560 | 44 | 0.8236 | 0.7578 | 0.9252 | -0.1674 |
| spectra_oilgas_gasturbine | 560 | 45 | 0.8327 | 0.7932 | 0.9407 | -0.1475 |
| spectra_oilgas_gasturbine | 560 | 46 | 0.8437 | 0.8002 | 0.9324 | -0.1323 |

Read with the caveat this IS a proxy (classical, non-negative-ridge solve of the same Hamiltonian, evidence_tag PROJ), not the Dirac-3 hardware result B4 buys: G0b already established the hardware should reproduce the proxy optimum closely (Spearman 0.900) for the ULB configuration, but B4's config differs (schedule 3 vs B1's schedule 2, and a different data family entirely), so this table sets EXPECTED ORDERS OF MAGNITUDE for the hardware AP values and confirms the pipeline runs end to end on all 3 frozen cells, all 5 seeds, without error -- it does not itself supply H5(i)'s in-segment claim, which requires the actual Dirac-3 CVQBoost weak-classifier ensemble (hard {-1,+1} votes on the simplex), not this ridge proxy.

Two things this dry run flags for the team lead up front, so B4's outcome is not a surprise:
1. **telecom_churn's test-fold pocket is fragile against the 50-positive floor.** Confirmed across all 5 seeds: seeds 43/44/46 clear it (test-pocket positives 52/52/57) while seeds 42/45 fall short (46/49) -- 2 of 5 H5(i) seeds are unscoreable for this cell under the frozen rule. Report this pattern honestly per-seed; do not average over or backfill the unscoreable seeds, and do not treat the 3 scored seeds as if they were the full 5-seed replication.
2. **The proxy solve shows NO in-segment edge over the matched control on any of the 13 scored (dataset, seed) proxy cells** -- every single edge is negative, ranging -0.051 to -0.077 (energy_steel), -0.095 to -0.142 (telecom_churn, where scoreable), -0.141 to -0.167 (oilgas_gasturbine). This is consistent and expected, not a red flag for B4: the FourierWall2 result being replicated is a CVQBoost (hard-vote, Dirac-solved) advantage specifically, not a ridge-proxy advantage -- CVQBoost_Findings.md documents that shallow/soft alternatives to the tuned CVQBoost configuration lose the in-segment edge entirely (section 3, `weak_cls_params` finding: default-depth weak learners plus the simplex-constrained hard-vote combination is what carries the in-segment signal, not the ridge relaxation this proxy solves). The proxy dry run's role here is pipeline validation (all 3 cells x 5 seeds run to completion, correct variable counts, leak-free features) and expected-magnitude-setting, not an early read on H5(i)'s answer -- only the actual Dirac-3 hardware fit can supply that.

## Not in this request

B1 (executed 2026-09-03, 27 fits, 120 QPU s), B2 (ULB full config, 816 vars, 11 fits, ~450 s), B3 (IEEE-CIS + ladder, 16 fits, ~650 s), B5 (QSVM, 12 fits, ~15 s): all wait on the QCi grant per the frozen spend priority (B3 > B2 > H3 ladder > B4) and their own approvals. Per that priority, B4 is the LAST block funded if the grant is partial; if no grant arrives, prereg section 10's fallback applies and B4 enters the proposal as [PROJ] with this document cited as the committed plan.

## Approval protocol

To approve, the team lead states which block(s), e.g. "approve B4". The execution session then states, immediately before running: block name, call count, expected seconds, and the exact config hashes -- and runs ONLY on that stated basis.
