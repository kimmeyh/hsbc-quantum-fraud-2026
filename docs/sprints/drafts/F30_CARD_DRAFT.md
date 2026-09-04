# F30 Sprint Card (DRAFT for team-lead review)

**Not yet a GitHub issue.** Drafted 2026-09-04 per team-lead request; created as a card only when a sprint selects F30.

---

**Title**: F30: Concurrent Dirac-3 submission with bounded in-flight requests and crash-safe recovery

**Sprint**: TBD (post-submission or Phase 2; see Scheduling)
**Category**: Infrastructure / Tooling
**Priority**: Medium now, High once Phase 2 volume begins
**Owner**: Claude (execution); team lead approves any metered call (Criterion H)
**Model assignment**: top tier (touches the metered path)
**Estimate**: ~4h build + ~1h dry-run validation + ~15m gated live vetting (2-3 calls)

## What and why

Dirac-3 runs one job at a time behind a queue. A fit billed at 4-5 QPU seconds took ~85 seconds of wall clock in Sprint 4, so nearly all elapsed time is queue wait, not computation. Today `run_hardware.py` submits one request, blocks until it returns, scores it, then submits the next. Twenty-two B1 fits therefore cost ~30 minutes of mostly idle waiting.

The queue does not prevent multiple requests from being *enqueued*. Several can be in flight while the client waits on all of them, either as separate processes or, better, as one process using asynchronous submission and completion handling.

**Why not simply fire everything at once**: metered calls cannot be wasted. A reboot, network drop, or client crash with 20 requests outstanding could bill the account for work whose results are never retrieved. The design point is therefore a small bounded window (about 4 in flight), topping up by one as each completes, so a crash risks at most the in-flight window rather than the whole block.

**Value**: with 4 in flight, a 22-fit block drops from roughly 30 minutes to under 10. That matters little today; it matters a great deal for the Phase 2 grid (81+ fits) and for any IEEE-CIS ladder work.

## Scope

1. **Discover the async surface (spike, no metered calls)**. Read `qci_client` for job submission, status polling, and result retrieval as separable steps. eqc-models' `fit()` couples submit-and-wait; determine whether a submit/poll/retrieve split is reachable through the underlying client, and if not, whether thread-based concurrency over `fit()` is safe (client thread-safety, credential reuse, connection limits). Written finding either way.
2. **Job-ledger persistence**. Before any submission, append an intent record (config hash, seed, block, submit timestamp, job id once known) to a durable ledger separate from results.json. On restart, the runner reads the ledger and attempts to retrieve results for any job that was in flight, so a crash costs at most the retrieval, not the spend.
3. **Bounded concurrent runner**. A window of N (default 4, configurable, hard-capped) in-flight submissions; on each completion, score the result, append its results.json row, and submit the next spec. Preserves every existing guard: block spend caps checked against projected spend including in-flight requests, the frozen identical-config retry rule, `verify_proxy_hashes()` before B1, and the unparseable-billing charge.
4. **Full offline test suite**. A fake client that simulates queue latency, out-of-order completion, a mid-run crash and restart, a failed job inside the window, and an unparseable billing field. Zero credentials, zero calls, runs in CI-time.
5. **Gated live vetting**. Only after the offline suite passes, and only on explicit team-lead approval: 2-3 real calls at window size 2, comparing results and billed seconds against the sequential path.

## Acceptance criteria

- Spike finding documented (async-capable or thread-capable, with evidence from the client source).
- Job ledger survives a simulated kill: after restart, an in-flight job's result is retrieved and written, and no duplicate submission occurs for it.
- Offline suite covers: normal completion, out-of-order completion, crash-restart recovery, failed job, unparseable billing, spend-cap trip with requests in flight. All green, no credentials required.
- Concurrent runner reproduces sequential results exactly on a replayed fixture (same rows, same config hashes).
- Spend cap accounts for in-flight requests: the window never lets projected spend reach the cap.
- Live vetting (if approved): 2-3 calls, results and billed seconds consistent with sequential behavior, recorded in the card.
- Zero metered seconds until the offline suite passes and approval is given.

## Risks

- **Wasted spend on crash**: the ledger plus the bounded window are the mitigation; window size is capped and configurable.
- **Client not thread-safe**: the spike answers this before any build; if neither async nor threads are safe, the item re-scopes to multi-process with a shared ledger, or is abandoned with the finding recorded.
- **Queue-position effects on billing**: verify in live vetting that concurrency does not change billed seconds per fit.
- **Complexity on the metered path**: the sequential runner remains the default; concurrency is opt-in by flag, so the audited path stays available.

## Preregistration touchpoints

None. This is execution infrastructure: it changes how requests are scheduled, never what is computed, which configs run, or how results are scored. Every row it writes uses the existing schema and the same fidelity records. Registered in the amendment log as an analysis-code addition when built, per section 11.

## Scheduling note

Not recommended before submission. The remaining Phase 1 hardware is grant-gated, and Sprint 5-8 are paper and evidence sprints where this would displace higher-value work. Its value arrives with Phase 2 volume, alongside F17 (simulator) and F25 (non-convex formulation).
