# Hardware Request: Blocks B1 + G0b (PREPARED, NOT EXECUTED)

**Purpose**: The written request for the first metered Dirac-3 blocks, per PREREGISTRATION section 10 and Criterion H. Nothing in this document authorizes execution; each block runs only on explicit team-lead approval of this request (or its amended successor).
**Audience**: Team lead (approver); the F2 execution session.
**Last Updated**: 2026-09-02 (Sprint 3, B7)

## Standing conditions (all blocks)

- Explicit per-block team-lead approval quoting this document; approval of one block never covers another.
- Retry rule (frozen): an errored solve retries at most TWICE with identical config and seed; retries counted in the row; third failure = cell reported failed. NO config-mutating backoff (F18 disposition 5); `fail_fast_on_variable_limit` behavior applies.
- Every fit = exactly one metered call; results land as [HW] rows in results.json with `metered_seconds` from the response and the same config_hash as the matching proxy row.
- Credentials per ADR-0011 (gitignored .env, QCI_API_URL=https://api.qci-prod.com + QCI_TOKEN, never printed).
- Pre-request sizing check: variable counts below computed with the A2-corrected `data.qubo_vars`; documented device limit 949; free-tier limit ~100.

## Block B1: ULB free-tier configs

| Item | Value |
|---|---|
| Config | top-13 matched features, schedule 2, sequential build = **78 variables** (A2); ns=8, rx=2, lambda=2*n_train |
| Pool variants | dct and lg (the two B1 pool variants) |
| Cells | per variant: 10-seed stratified primary (seeds 42-51) + 1 temporal-sensitivity split |
| **Call count** | **22 fits = 22 metered calls** (2 variants x 11 cells) |
| Cost basis | measured FourierWall2: sched2/ns4/rx2 at 105 vars = 3 QPU s/fit; scaling to ns=8 at 78 vars ~= 4-6 QPU s/fit |
| **Expected total** | **~90-140 QPU s** (prereg envelope ~300-600 s remains the committed ceiling) |
| Gated on | current ~500 s balance; team-lead approval |
| Pair build | per the A3 selection recorded in gate_report.md at execution time (validation-only choice, made before any test evaluation) |

## Block G0b: proxy-fidelity fits

| Item | Value |
|---|---|
| Design | top-3 + bottom-2 configs from the PROXY config ranking, one hardware fit each, seed 42; gate = Spearman(proxy rank, hardware rank) >= 0.5 |
| Config list | filled from the proxy ranking table at execution time (free-tier-sized configs, <= 100 vars each); listed by config_hash in the approval message |
| **Call count** | **5 fits = 5 metered calls** |
| Cost basis | free-tier-sized fits, ~4-6 QPU s each |
| **Expected total** | **~20-35 QPU s** (prereg envelope ~100 s) |
| Gated on | current balance; team-lead approval; proxy ranking table present in results.json |

## Validation notes (2026-09-02, team lead)

- Both pool variants KEPT in B1 per team-lead decision ("keep both"); no amendment.
- EXECUTION RECOMMENDATION: hold both blocks until F22 (preregistered proxy tuning) completes -- it produces the config ranking G0b requires, and it addresses the score degeneracy found at validation (lg quarantined from reporting; dct operating points weak evidence until tuned). Request size and structure unchanged.

## Not in this request

B2 (ULB full config, 816 vars, 11 fits, ~450 s), B3 (IEEE-CIS + ladder, 16 fits, ~650 s), B4 (SPECTRA, 15 fits, ~450 s), B5 (QSVM, 12 fits, ~15 s): all wait on the QCi grant per the frozen spend priority (B3 > B2 > ladder > B4) and their own approvals.

## Approval protocol

To approve, the team lead states which block(s), e.g. "approve B1" / "approve B1 + G0b". The execution session then states, immediately before running: block name, call count, expected seconds, and the exact config hashes -- and runs ONLY on that stated basis.
