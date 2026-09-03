# ADR-0008: Single results.json store, append-only rows, schema-complete at write

## Status

Accepted

## Date

2026-09-02

## Context

PREREGISTRATION section 11 fixes the row schema (arm, dataset, protocol, seed, config_hash, features_used, metrics, evidence_tag, metered_seconds, retry_count, timestamps) and the standing rule says every reported number originates in results.json with an evidence tag. Multiple writers (classical runner, proxy runner, later hardware runner) need one authoritative store.

## Decision

One file: `experiments/results/results.json`, shape `{"meta": {...}, "rows": [...]}`. Rows are append-only and schema-complete at write time -- a row is written once, after scoring, never patched. Dataset-level facts (dedupe counts) live in `meta`. Writers append via atomic read-modify-replace; the checkpoint key is the row's identifying tuple, so writers are idempotent. Aggregations (gate scoring, CIs across seeds, the A3 comparison) are computed FROM rows by readers, never stored back into rows; derived artifacts (gate table, memos) cite row config_hashes. The file is committed at sprint boundaries (results are small JSON, no dataset content).

## Alternatives Considered

### SQLite results database
- **Description**: Proper DB with transactions.
- **Pros**: Concurrent-writer safety, queries.
- **Cons**: Not diffable in PRs; harder for reviewers of the public package; our writers are already serialized by track.
- **Why Rejected**: Reviewability of the evidence store outweighs transactional niceties at ~200 rows.

### One JSON file per run
- **Why Rejected**: Scatters the evidence base; the single file IS the auditable artifact the paper cites.

## Consequences

### Positive
grep-able, diffable, committed evidence base; the "every number traces to results.json" rule is mechanically checkable.
### Negative
Concurrent writers could race on the read-modify-replace window; mitigated by running one writer per track and atomic replace (last-writer-wins on disjoint keys).
### Neutral
Hardware rows (F2) add metered_seconds > 0 and [HW] tags to the same store.

## Preregistration touchpoints

Section 11 (schema, evidence tags, failed-run reporting). The preregistration governs methodology; this ADR records engineering decisions only.

## References

experiments/src/run_classical.py (_atomic_write, stage_refit), qubo_proxy.py (_atomic_append_row); CHECKLIST.md standing rules; card #15.
