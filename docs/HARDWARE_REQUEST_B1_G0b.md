# Hardware Request: Blocks B1 + G0b (EXECUTED 2026-09-03)

**Purpose**: The written request for the first metered Dirac-3 blocks, per PREREGISTRATION section 10 and Criterion H. Nothing in this document authorizes execution; each block runs only on explicit team-lead approval of this request (or its amended successor).
**Audience**: Team lead (approver); the F2 execution session.
**Last Updated**: 2026-09-03 (EXECUTED on team-lead approval: 27 fits, 120 QPU s, 0 failures, 0 retries; G0b PASS at Spearman 0.900)

## Standing conditions (all blocks)

- Explicit per-block team-lead approval quoting this document; approval of one block never covers another.
- Retry rule (frozen): an errored solve retries at most TWICE with identical config and seed; retries counted in the row; third failure = cell reported failed. NO config-mutating backoff (F18 disposition 5); `fail_fast_on_variable_limit` behavior applies.
- Every fit = exactly one metered call; results land as [HW] rows in results.json with `metered_seconds` from the response and the same config_hash as the matching proxy row.
- Credentials per ADR-0011 (gitignored .env, QCI_API_URL=https://api.qci-prod.com + QCI_TOKEN, never printed).
- Pre-request sizing check: variable counts below computed with the A2-corrected `data.qubo_vars`; documented device limit 949; free-tier limit ~100.

## Block B1: ULB free-tier configs

| Item | Value |
|---|---|
| Config | A3-selected FULL-PAIR build (executed from WSL). Variant 1 = preregistered starting config: top-13, schedule 2, dct, lambda=2*n_train, **91 variables**, config_hash `640ed4cf9c46ea4b`. Variant 2 = F22 best-healthy lg config: top-9, schedule 2, lg class-balanced, lambda=0.5*n_train, **45 variables**, config_hash `bf9e473250b773fa`. ns=8, rx=2 fixed |
| Pool variants | dct (starting config) and lg (tuned) -- the two B1 pool variants, team-lead decision 2026-09-02 "keep both" |
| Cells | per variant: 10-seed stratified primary (seeds 42-51) + 1 temporal-sensitivity split |
| **Call count** | **22 fits = 22 metered calls** (2 variants x 11 cells) |
| Cost basis | measured FourierWall2: sched2/ns4/rx2 at 105 vars = 3 QPU s/fit; at ns=8: ~4-6 QPU s/fit for 91 vars, ~3-4 for 45 vars |
| **Expected total** | **~80-110 QPU s** (prereg envelope ~300-600 s remains the committed ceiling) |
| Gated on | current ~500 s balance; team-lead approval |
| Seeds | primary 42-51 per variant (20 calls) + 1 temporal-sensitivity split per variant (2 calls) |

## Block G0b: proxy-fidelity fits

| Item | Value |
|---|---|
| Design | top-3 + bottom-2 configs from the PROXY config ranking, one hardware fit each, seed 42; gate = Spearman(proxy rank, hardware rank) >= 0.5 |
| Config list (proxy_ranking.json, seed 42) | top-3: `640ed4cf9c46ea4b` (dct k13 s2 a2, 91 vars, val AP 0.7232), `bf9e473250b773fa` (lg k9 s2 a0.5, 45 vars, 0.6873), `39a4716aaf9e6691` (lg k9 s2 a4, 45 vars, 0.6872); bottom-2: `17fda8858bcd2010` (lg k5 s3 a1, 25 vars, 0.4898), `5945e713dc7c54ba` (xgb k9 s1 a2, 9 vars, 0.0017) |
| **Call count** | **5 fits = 5 metered calls** |
| Cost basis | free-tier-sized fits, ~4-6 QPU s each |
| **Expected total** | **~20-35 QPU s** (prereg envelope ~100 s) |
| Gated on | current balance; team-lead approval (ranking present: experiments/results/proxy_ranking.json) |

## Validation notes (2026-09-02, team lead)

- Both pool variants KEPT in B1 per team-lead decision ("keep both"); no amendment.
- F22 COMPLETE (2026-09-03): ranking present; lg quarantine lifted by the tuned healthy config. Expectation to state up front: because the Hamiltonian is strictly convex, hardware should reproduce the proxy optimum (G0b Spearman expected high); the blocks buy [HW] evidence tags and the fidelity gate, not a performance jump. READY FOR APPROVAL.

## Not in this request

B2 (ULB full config, 816 vars, 11 fits, ~450 s), B3 (IEEE-CIS + ladder, 16 fits, ~650 s), B4 (SPECTRA, 15 fits, ~450 s), B5 (QSVM, 12 fits, ~15 s): all wait on the QCi grant per the frozen spend priority (B3 > B2 > ladder > B4) and their own approvals.

## Approval protocol

To approve, the team lead states which block(s), e.g. "approve B1" / "approve B1 + G0b". The execution session then states, immediately before running: block name, call count, expected seconds, and the exact config hashes -- and runs ONLY on that stated basis.
