# F15 Research Findings: spamfilter-multi ADR and Best-Practice Review

**Purpose**: Raw material for Sprint 2 Task A (F15). Inventory of the spamfilter-multi ADR corpus, transferable practices, additional SE suggestions, and ML best-practice ADR candidates for this repository.
**Sources reviewed**: a prior private repository's `docs/ARCHITECTURE.md`, all 42 of its ADRs plus their `README.md`, `QUALITY_STANDARDS.md`, `TESTING_STRATEGY.md`, `LOGGING_CONVENTIONS.md` (headings). Target grounding: `experiments/PREREGISTRATION.md` v1.1 (FROZEN, sections 5-9 read in full), `docs/sprints/SPRINT_2_PLAN.md`, `experiments/src/` contents.
**Date**: 2026-08-30

---

## 1. ADR inventory

BLUF: 42 ADRs exist. Most record Flutter, email-protocol, or store-publication decisions with no carryover. About a dozen carry a transferable pattern. The strongest transfers are the ADR system itself, GitFlow with role-based PR policy, model tiering, changelog-per-commit, environment single-source-of-truth, secrets handling, and the demo-mode/synthetic-data pattern.

| ADR | Title | Status | Subject (one line) | Transferable? | Reason |
|-----|-------|--------|--------------------|---------------|--------|
| 0001 | Flutter/Dart Single Codebase for All Platforms | Accepted | One framework for five platforms | no | Platform framework choice; target is single-platform Python |
| 0002 | Adapter Pattern for Email Providers | Accepted | Common interface over heterogeneous provider APIs | adapt | Same pattern fits Dirac-3 hardware vs classical proxy solver backends |
| 0003 | Regex-Only Pattern Matching | Accepted | Kill dual pattern syntax, keep one | no | Domain-specific; no dual-syntax problem exists in target |
| 0004 | Dual-Write Storage (SQLite + YAML Export) | Superseded | Two storage formats written in parallel | no | Superseded in source itself; lesson is single source of truth |
| 0005 | Safe Senders Evaluated Before Rules | Accepted | Whitelist priority in rule evaluation | no | Email rule-engine semantics only |
| 0006 | Four Progressive Scan Modes | Accepted | Risk-tiered modes before destructive operations | adapt | Risk tiers map to smoke, proxy, then metered hardware runs |
| 0007 | Move-to-Trash, Not Permanent Delete | Accepted | Destructive actions recoverable by default | adapt | Principle maps to never overwriting results or raw data |
| 0008 | Platform-Native Secure Credential Storage | Accepted | Secrets in OS-native encrypted stores | adapt | QCi/Kaggle tokens belong outside the repo, gitignore-pinned |
| 0009 | Provider Pattern State Management | Accepted | Flutter reactive state architecture | no | UI state management; target has no UI |
| 0010 | Normalized Database Schema (9 Tables) | Accepted | Normalized SQLite schema design | no | Target result store is results.json, schema frozen by prereg |
| 0011 | Desktop OAuth Loopback Redirect + PKCE | Accepted | Desktop OAuth flow implementation | no | OAuth-specific; no equivalent in target |
| 0012 | AppPaths Platform Storage Abstraction | Accepted | Centralized per-platform path resolution | no | Single-platform target; paths are simple constants |
| 0013 | Per-Account Settings with Inheritance | Accepted | Default settings with per-account overrides | no | Multi-account configuration problem does not exist |
| 0014 | Windows Background Scanning via Task Scheduler | Accepted | Scheduled background execution on Windows | no | Long jobs in target run attended, in-session |
| 0015 | GitFlow Branching Strategy | Accepted | Three-tier branches with role-based PR policy | yes | Target already runs this model; should be recorded as ADR |
| 0016 | Sprint Model Tiering (Haiku/Sonnet/Opus) | Accepted | Complexity scoring assigns tasks to model tiers | yes | Target sprint process inherits this; scoring rubric reusable |
| 0017 | PowerShell Build Automation | Accepted | PowerShell-native scripts, never bash-wrapped | adapt | Same Windows host; run-launcher scripts should follow it |
| 0018 | Windows Toast Notifications via PowerShell | Accepted | Runtime-generated PowerShell for WinRT toasts | no | Niche; long-run completion notice is optional nicety |
| 0019 | Windows System Tray Integration | Accepted | Tray icon and window lifecycle | no | Desktop UI concern only |
| 0020 | Demo Mode with Synthetic Emails | Accepted | Synthetic data exercises full pipeline safely | adapt | Tiny fixture datasets exercise pipeline without metered spend |
| 0021 | YAML-to-Database One-Time Migration | Accepted | Atomic, idempotent, non-destructive migration | no | One-time migration problem absent; idempotency principle generic |
| 0022 | Throttled UI Progress Updates | Accepted | Dual-threshold throttling of progress events | adapt | Throttle progress logging in 100-trial Optuna sweeps |
| 0023 | In-Memory Pattern Caching | Accepted | Cache compiled regexes, measured 100x speedup | no | Measure-then-cache principle generic; no direct analog |
| 0024 | Canonical Folder Mapping | Accepted | Single source of truth for provider folder names | no | Email folder taxonomy only |
| 0025 | CHANGELOG Updated Per Commit Policy | Accepted | Changelog edited in same commit as change | yes | Directly adoptable; near-zero cost, high audit value |
| 0026 | Application Identity and Package Naming | Accepted | Permanent app ID and naming | no | Store publication concern |
| 0027 | Android Release Signing Strategy | Accepted | Keystore outside repo, policy-test pinned | adapt | Secrets-outside-repo plus policy-test-pin pattern transfers |
| 0028 | Android Permission Strategy | Accepted | Minimal manifest permissions | no | Android-specific |
| 0029 | Gmail API Scope and Verification Strategy | Accepted | Minimal OAuth scopes to ease verification | no | Google verification process specific |
| 0030 | Privacy and Data Governance Strategy | Accepted | Data inventory table, storage, compliance | adapt | Data inventory table format fits dataset licensing/provenance |
| 0031 | App Icon and Visual Identity | Accepted | Icon and branding assets | no | Branding only |
| 0032 | User Data Deletion Strategy | Accepted | Account and data deletion flows | no | Play policy compliance only |
| 0033 | Analytics and Crash Reporting Strategy | Accepted | Whether to collect analytics | no | Store disclosure concern |
| 0034 | Gmail Access Method for Production | Accepted | REST API vs IMAP for Gmail | no | Provider protocol choice |
| 0035 | Production/Development Side-by-Side | Accepted | Isolated data dirs, mutex, env-suffixed identity | adapt | Proxy-dev vs metered-hardware separation needs the same isolation |
| 0036 | MSIX Signing Strategy | Accepted | Store vs sideload signing | no | Windows Store packaging only |
| 0037 | UI/Accessibility Standards | Accepted | Semantics labels, touch targets, selectability | no | UI standard; no UI in target |
| 0038 | Content Management for Long Strings | Accepted | Long prose moved from code to assets | no | Threshold problem absent in analysis code |
| 0039 | Per-Account Background Scanning | Accepted | Per-account schedule replacing global toggle | no | App scheduling architecture |
| 0040 | Two E2E Test Harnesses | Accepted | Documented division of labor between harnesses | adapt | Pattern of writing down which harness proves what: proxy vs hardware |
| 0041 | Environment Propagation Single Source | Accepted | One flag drives every compiled env surface | adapt | One config source must drive evidence tags and run metadata |
| 0042 | Cross-Platform Parity and Platform Exceptions | Accepted | Same everywhere unless explicitly excepted | no | Two-platform parity problem does not exist |

---

## 2. Practices to copy and adapt

1. **The ADR system itself** (numbered files, index table, immutability, supersession lifecycle). Lives in `docs/adr/README.md` (source): sequential 4-digit numbering, `NNNN-short-title.md` lowercase-hyphen naming, status lifecycle Proposed -> Accepted -> Deprecated/Superseded, accepted ADRs never edited (a change means a new superseding ADR). Target mapping: create `docs/adr/README.md` with the same index table, template (section 5 below), and conventions. This is the core F15 deliverable. The immutability convention is a natural sibling of the preregistration's amendment-only rule, so the two governance systems reinforce each other.

2. **Architecture doc that cross-references ADRs inline.** `ARCHITECTURE.md` (source) names the relevant ADR at every section where a decision applies ("Adapter Pattern (ADR-0002)", "Pattern Caching (ADR-0023)"), plus a closing "Architecture Decision Records" section. Target mapping: when the target grows an `ARCHITECTURE.md` for `experiments/src/` (data.py, metrics.py, tune.py, the coming CVQBoost/proxy modules), annotate each component section with its governing ADR and prereg section number. Keep it lean; the prereg carries the methodology.

3. **Document header and structure conventions.** `QUALITY_STANDARDS.md` (source) "Documentation Standards": every doc opens with Purpose, Audience, Last Updated; 40,000-character file cap with extract-and-cross-reference as the remedy; table of contents required above 20k characters; no contractions; no emoji, bracketed text markers ([OK], [FAIL], [WARNING]) instead. Target mapping: apply to all new docs in `docs/`; the target's sprint docs already inherited the style. The 40k cap matters doubly here because these docs are read by Claude every session.

4. **Policy tests that pin critical configuration.** Source: `test/policy/msix_config_test.dart` and `test/policy/android_signing_test.dart` are build-failing tests that assert a config invariant whose silent violation once shipped a broken release (the `windows_build_args` typo, ADR-0041 context). Target mapping: add `experiments/src/test_policy.py` pinning prereg-fixed constants: `average_precision_score` (step-wise, never trapezoidal) is the only AP implementation imported; seed lists {42..51} and {42..46}; the required results.json keys from prereg section 11; lambda_coef formula; the ban on resampling in house protocol. A frozen protocol only protects you if drift is mechanically detected.

5. **Test quality rules: AAA structure, test independence, isolated-branch guard tests, scratch probes out of the repo.** `TESTING_STRATEGY.md` (source) "Test Quality Standards": every safety-critical branch gets one isolated test where that branch is the only possible decider (shared fixtures mask deletable clauses, Sprint 63 escape); throwaway probe tests go to the scratchpad or a gitignored `test/scratch/`, never promoted by accident. Target mapping: apply the isolated-branch rule to leakage controls in `data.py` (for example, one test where the only thing that can fail is "scaler was fit on train only") and keep exploratory probe scripts out of `experiments/src/`.

6. **Pre-commit enforcement hooks.** Source: `.claude/hooks/` scripts registered in `.claude/settings.json` run analyzer, full test suite, file-size warning, and formatter before commits; sprint acceptance requires 0 analyzer errors and 100% test pass. Target mapping: a hook (or simply the sprint checklist) that runs `pytest experiments/src` and `ruff check` before any commit touching `experiments/src/`, with the extra rule that post-freeze changes to frozen analysis files must carry a prereg amendment line in the same commit.

7. **CHANGELOG updated in the same commit as the change** (ADR-0025 plus `CHANGELOG_POLICY.md`). Format `- **type**: Description (Issue #N)` under `[Unreleased]`, grouped by date. Target mapping: add `CHANGELOG.md` at the repo root with the same policy. For a submission with evidence requirements, this doubles as a dated audit trail of when each analysis capability appeared relative to the freeze.

8. **GitFlow with role-based PR policy** (ADR-0015 plus source CLAUDE.md branch policy). Claude PRs feature -> develop only; the team lead alone merges develop -> main. Target mapping: already practiced (Sprint 2 runs on a feature branch with PR #2, carry-forward model in use); record it as one of the "decisions already made" ADRs so the convention survives context loss.

9. **Sprint model tiering by complexity score** (ADR-0016). A 0-40 point rubric (file impact, novelty, risk) assigns each task to Haiku/Sonnet/Opus. Target mapping: the target's `docs/SPRINT_PLANNING.md` already inherits this; keep the rubric but reweight for research code, where statistical-correctness risk, not file count, is the dominant complexity driver (a 10-line metrics change is top-tier work here).

10. **Synthetic/fixture data exercises the full pipeline with zero risk** (ADR-0020, demo mode). Source generates 55 synthetic emails in 5 categories so every workflow runs without credentials. Target mapping: extend `experiments/src/smoke_test.py` with a committed tiny fixture (a few hundred rows, both classes) that runs the entire split-tune-fit-score-serialize path in seconds, so pipeline changes are validated without touching real datasets or metered seconds. This is also the Dirac-3 constraint honored: dev on the local proxy, hardware only with explicit approval.

11. **PowerShell-native automation, never bash-wrapped** (ADR-0017). The source learned that wrapping PowerShell in bash loses toolchain context on this exact Windows 11 machine. Target mapping: run-launcher and environment scripts for the uv venv should be `.ps1`, executed natively; document the activation incantation once in README.

12. **Environment identity from a single source, verified two-sided** (ADR-0041). The source shipped two defective releases because two compiled surfaces read the environment independently; the fix was one flag driving every surface plus a probe that prints both for verification. Target mapping: the evidence tag ([HW]/[SIM]/[PROJ]) and solver-backend selection must derive from one config object that is also serialized into results.json, so a row can never claim [HW] while the proxy actually ran. A startup log line printing backend, config_hash, and tag is the analog of the source's `--print-env` probe.

13. **Known-failure documentation before re-investigation.** Source CLAUDE.md rule (Sprint 52 IMP-3): before investigating a failing test/script, grep the runner and its header for the failure, which may be documented as known/excluded. Target mapping: give each long-running script in `experiments/src/` a header listing known failure modes (for example, Dirac solve error classes and the prereg retry rule) so a failed cell is triaged against known behavior first.

14. **Data governance inventory table** (ADR-0030). A table of every data type: how used, where stored, encrypted, shared. Target mapping: a per-dataset table in the data ADR (section 4, candidate 3): source URL, license, citation obligations (prereg section 2 requires citing SPECTRA plus original UCI substrates), checksum, local path, allowed uses (for example, Sparkov is pipeline-correctness only).

---

## 3. Additional SE best-practice suggestions

These are not in the source repo (or exist only in app-specific form) but are warranted by the target's nature: research code making statistical claims, a solo maintainer, metered hardware, and a hard Sep 8 deadline.

1. **Reproducibility pinning with a lockfile plus per-run environment capture.** The prereg (section 12) requires a "pinned environment" because library versions shift GBDT results measurably; the source repo has no equivalent (Flutter pins via pubspec.lock implicitly). Concretely: commit `uv.lock` (or a fully pinned `requirements.txt` with hashes) and have every run serialize `sys.version`, the output of `importlib.metadata` for xgboost/lightgbm/catboost/sklearn/optuna/qci-client, plus the git commit hash, into its results.json row or a sibling `env.json`. Pinning the declared environment is necessary but not sufficient; capturing the executed environment per run is what lets a reviewer (or you, on Sep 6 at midnight) prove which library produced which number.

2. **Experiment configuration as versioned, hashed artifacts.** The prereg already mandates `config_hash` in results.json (section 11) but nothing yet defines what is hashed. Concretely: every arm/protocol/seed cell is fully described by a config file (YAML or JSON) under `experiments/configs/`, the hash is computed over its canonical serialization, and code takes a config path, never ad-hoc CLI flags for methodology-bearing parameters. This makes "what exactly ran" a content-addressed fact, makes the frozen CVQBoost starting configuration (prereg section 4) a reviewable file rather than folklore, and prevents the classic solo-maintainer failure of editing a constant in code for one run and forgetting.

3. **Results immutability: append-only, timestamped, never edited in place.** `experiments/results/` currently holds one mutable file (`pilot_variance.json`). Concretely: one results file or directory per run keyed by timestamp plus config_hash; completed run outputs are never rewritten (fixes produce a new run with a new timestamp, and the prereg amendment log explains why); an aggregator script builds report tables by reading, never writing, run files. Optionally set completed files read-only on disk. This is the engineering enforcement of prereg section 11's "never silently dropped" rule, and it is what makes the gate table auditable: any number in the submission traces to an immutable file that predates the claim.

4. **Code review discipline for analysis code: adversarial self-review targeted at statistical validity.** A solo maintainer has no second reviewer, and the failure modes that matter here (leakage, seed reuse across cells, test-set contamination, metric implementation drift) do not crash; they produce plausible wrong numbers. Concretely: before any result is recorded as gate evidence, run a fixed review checklist derived from prereg sections 5-9 (transforms fit inside folds; selection inside CV; correct seed list; prevalence beside AUPRC; correct paired-resample indices), and use a fresh-context model review (the pattern the prereg itself used: "two independent model reviews") for any new analysis module before it freezes. The checklist lives in the repo so it is the same every time, not reconstructed from memory under deadline pressure.

5. **Error handling and checkpointing in long-running jobs.** A 100-trial Optuna sweep per arm per dataset, and later metered hardware blocks, will run for hours on a machine that also does everything else. Concretely: Optuna studies use SQLite storage (`optuna.storages`) so an interrupted sweep resumes instead of restarting; every trial writes its own record at completion (crash loses one trial, not the sweep); hardware-run wrappers catch and classify errors, implement the prereg's retry-at-most-twice-with-identical-config rule (section 11) mechanically with retry_count recorded, and fail loudly to a log plus console rather than silently continuing. No bare `except:`; an errored cell is a recorded outcome, not a skipped iteration. Wall-clock and metered_seconds are recorded per fit because H1c and the budget table need them.

6. **Logging conventions for pipeline stages.** The source has Dart-specific `LOGGING_CONVENTIONS.md` (keyword-prefixed AppLogger categories, filterable, no sensitive data); the target needs a Python equivalent. Concretely: `logging.getLogger` with a fixed namespace per stage (`frd.data`, `frd.tune`, `frd.fit`, `frd.metrics`, `frd.hw`), console at INFO plus a per-run file at DEBUG under the run's results directory, every run banner logging config_hash, seed, dataset, arm, evidence tag, and progress throttled (per Optuna trial, not per fold). Never log dataset rows (ULB is real cardholder data); log shapes, counts, and hashes.

7. **Data provenance manifest with checksums.** Datasets live in `experiments/data/` outside git. Concretely: a committed `experiments/data/MANIFEST.md` (or JSON) with per-file SHA-256, row counts, source URL, download date, and license; a small verifier script run at sprint start and before any hardware block. This protects against the silent-corruption and wrong-version failure modes (the prereg's B4 even requires a SPECTRA re-download, which must provably match or provably differ from the FourierWall2-era copies), and it is cheap: one script, one table.

8. **Minimal CI as a safety net.** The source added GitHub Actions CI (analyze plus test on every PR) as additive to manual verification. Target already has `.github/`; concretely: a workflow running `pytest experiments/src` plus a lint pass on every PR to the integration branch, using the smoke fixture from practice 10 above, with no dataset access and no metered anything. For a solo maintainer sprinting to a deadline, CI is the only reviewer that never gets tired; keep it under a minute so it never gets skipped.

---

## 4. ML best-practice ADR candidates

Grounding rule: `experiments/PREREGISTRATION.md` v1.1 is FROZEN and governs methodology. Sections 5-9 already fix leakage controls, tuning budgets, imbalance handling, splits/protocols, and metrics/statistics. ADRs must record engineering decisions around the frozen protocol (how the machinery enforces it, where things live, how runs are launched and stored), never restate or alter it. Where a candidate touches prereg content, the overlap is flagged and the ADR should cite the prereg section as the governing authority. The Sprint 2 acceptance criteria already name four "decisions already made" (protocol freeze governance, proxy=structural-control design, data handling, branch/carry-forward model); candidates 1, 2, 3, and 10 cover those.

1. **ADR: Preregistration freeze governance and amendment mechanics.** Records: the freeze is implemented as commit `95751b9` / tag `prereg-freeze`; amendments are dated log lines in the frozen file itself; analysis code in `experiments/src/` freezes at the same commit; post-freeze changes to frozen files require an amendment line in the same commit; deviations vs amendments distinction is operationalized in the gate table. Why it matters: this is the single mechanism the whole submission's credibility hangs on, and it must survive context loss across sessions. Overlap: prereg sections 11-12 define the policy; the ADR records only the git/tag/commit mechanics and the sprint-process touchpoints. Effort: 30-40 min.

2. **ADR: Proxy-as-structural-control dual-role design.** Records: one implementation (non-negative ridge and L1 over the identical weak-learner output matrix) serves as both the CVQBoost tuning proxy (prereg section 6) and the H4 attribution control (section 3), why a single code path is deliberate (any proxy/control divergence would poison both uses), and the G0b fidelity gate as the check on that bet. Why it matters: it is the central engineering wager of the study; if it is not written down, a future refactor could fork the two uses and silently invalidate H4. Overlap: high with prereg sections 3, 4, 6 on the what; the ADR records the single-implementation decision and module boundaries, citing the prereg for all methodology. Effort: 30 min.

3. **ADR: Dataset acquisition, storage, and provenance handling.** Records: raw data lives under `experiments/data/` outside git, treated read-only; per-dataset inventory table (source, license, checksum, citation obligations including SPECTRA's original UCI substrates per `docs/references.md`, allowed uses such as Sparkov being pipeline-correctness only); the manifest-plus-verifier mechanism (section 3.7 above); duplicate-removal counts as a recorded preprocessing artifact. Why it matters: dataset mix-ups are the cheapest way to invalidate months of work, and the competition requires clean licensing. Overlap: prereg section 2 fixes which datasets and their roles; the ADR records only handling and storage. Effort: 30 min.

4. **ADR: Leakage prevention enforced by pipeline architecture, not discipline.** Records: all transforms are sklearn `Pipeline`/`ColumnTransformer` objects fit per fold (the only permitted pattern); no module exposes a fit-on-full-data path; the shuffled-label positive control and the time-consistency/adversarial-validation filters are implemented as reusable, tested functions; policy tests pin the pattern (a grep-style test asserting no `fit(` call on pre-split frames in analysis modules, plus the isolated-branch guard tests from section 2.5). Why it matters: prereg section 5 is the strictest part of the protocol and the easiest to violate accidentally under deadline pressure; architecture that makes the wrong thing unwritable beats vigilance. Overlap: section 5 fixes every rule; the ADR records only the enforcement machinery. Effort: 45 min.

5. **ADR: Feature engineering as a versioned, hashed recipe registry.** Records: each preregistered recipe (ULB G0c handling of Time/Amount; the IEEE-CIS reduced recipe's D-normalization, UID aggregates, V-column reduction; the QFE phase representation) is one named, parameterized, tested function or config; recipes are selected by name in run configs and included in config_hash; no inline feature code in run scripts. Why it matters: H6 gives the QFE representation to every arm, so a recipe drifting between arms would manufacture exactly the fake quantum win the Fourier Wall paper warns about; a registry makes identical-recipe-across-arms structurally true. Overlap: prereg sections 5.3 and 3/H6 fix recipe content exactly; the ADR records only implementation shape and hashing. Effort: 40 min.

6. **ADR: Training discipline for long-running and metered jobs.** Records: Optuna SQLite storage with resumable studies; per-trial persistence; timing capture (1-core and all-core GBDT timings, CVQBoost wall-clock including weak-learner construction and Hamiltonian build, Dirac solve time broken out, per prereg H1c); the hardware run-launcher's approval gate (each block of the section 10 grid requires explicit team-lead approval; this is also the standing Dirac-3 usage constraint), mechanical retry-at-most-twice with retry_count recorded, and metered_seconds accounting against the budget table. Why it matters: metered seconds are the scarcest resource in the project and an unhandled crash mid-block burns them silently. Overlap: prereg sections 10-11 fix budgets, retries, and approvals as policy; the ADR records the launcher and accounting implementation. Effort: 45 min.

7. **ADR: Results store: append-only results.json with the frozen schema.** Records: one record per fit with the prereg section 11 required keys (arm, dataset, protocol, seed, config_hash, features_used, metrics, evidence_tag, metered_seconds, retry_count, timestamps); append-only, timestamped run directories, no in-place edits; aggregation is read-only; failed cells are recorded as failed, never absent. Why it matters: the gate table and every published interval must trace to immutable records; this is the difference between "trust me" and "audit me" in the submission. Overlap: section 11 fixes the schema and the never-dropped rule; the ADR records file layout, immutability enforcement, and the aggregator boundary. Effort: 30 min.

8. **ADR: Single-implementation metrics with evidence-tag propagation.** Records: `experiments/src/metrics.py` is the sole implementation of every section 9 metric (step-wise `average_precision_score`, BCa bootstrap with identical resample indices for paired comparisons, Wilson intervals, ECE with equal-mass binning); the tie-frequency check and the second-implementation cross-check exist as callable functions; evidence tags flow from the run config through results.json into report tables with no manual retagging; prevalence is emitted beside every AUPRC by the reporting code so it cannot be forgotten. Why it matters: a metric implementation bug is a silent falsifier of every hypothesis at once, and metrics code froze with the prereg, so its correctness argument must be written down now. Overlap: section 9 fixes all definitions; the ADR records the single-source rule, test strategy, and tag plumbing. Effort: 30 min.

9. **ADR: Split and seed management centralized in one module.** Records: `data.py` (or a dedicated `splits.py`) is the only code that produces train/validation/test indices; the seed lists ({42..51} primary, {42..46} exploratory) live in one constants block imported everywhere; temporal splits (IEEE-CIS GroupKFold by month, ULB time-ordered 70/10/20, Sparkov shipped split) are named protocol objects; identical test rows for paired deltas are guaranteed by construction because both arms receive indices from the same call. Why it matters: H1b's decision statistic is per-seed paired delta-AP on identical test rows; two arms deriving their own splits from "the same seed" is a classic subtle break of pairedness. Overlap: prereg section 8 fixes protocols and seeds; the ADR records the sole-provider module decision. Effort: 25 min.

10. **ADR: Branch and carry-forward model for sprint work.** Records: the GitFlow adaptation already in use (feature branch per sprint, PR to the integration branch, team-lead-only merges to main), the carry-forward rule for blocked team-lead-owned items (Sprint 2's F12 pattern under Criterion 2), and the rule that the frozen `experiments/src/` files change only with amendment lines regardless of branch. Why it matters: process decisions evaporate fastest for a solo maintainer working across many sessions; the source repo's experience (ADR-0015) shows writing the branch policy down is what makes an AI-assisted workflow safe. Overlap: none with the prereg; pure process. Effort: 25 min.

11. **ADR: Class-imbalance handling location of record (deliberately NOT an ADR subject).** Recommendation to record inside candidate 4 or as a one-paragraph note, not a standalone ADR: prereg section 7 fixes imbalance handling completely (weighting only, exactly one mechanism per library, no resampling ever, H1a SMOTE isolated) and an ADR restating it would create a second document that could drift from the frozen authority. The engineering decision worth one line in candidate 4 is that the per-library weighting mechanism is set in the arm config schema so "exactly one mechanism" is enforced by construction. Effort: 10 min (as a note). Overlap: total, which is exactly why it should not be a separate ADR.

Suggested authoring order under deadline: 1, 3, 10 first (decisions already made, cheap, named in Sprint 2 acceptance criteria), then 2, 7, 8 (protect the evidence chain), then 4, 5, 6, 9 as their modules are built in the sprint that implements them. Total estimated effort for all: about 5.5 hours; the first six about 3 hours.

---

## 5. Source ADR template

The source repo's template, reproduced verbatim from that repository's ADR `README.md` ("Template" section):

```markdown
# ADR-NNNN: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-NNNN]

## Date

[YYYY-MM-DD when the decision was made, or best estimate with ~ prefix]

## Context

[What problem or need motivated this decision? What forces, constraints,
and requirements were in play? Include relevant project history.]

## Decision

[What was decided? State the decision clearly and concisely.]

## Alternatives Considered

### [Alternative 1 Name]
- **Description**: [What this alternative would look like]
- **Pros**: [Benefits]
- **Cons**: [Drawbacks]
- **Why Rejected**: [Specific reason it was not chosen]

### [Alternative 2 Name]
(same structure)

## Consequences

### Positive
- [What becomes easier, better, or possible]

### Negative
- [What becomes harder, more complex, or limited]

### Neutral
- [Trade-offs that are neither clearly positive nor negative]

## References
- [Links to issues, PRs, docs, code files, external resources]
```

Accompanying conventions from the same README, for adoption alongside the template:

- Numbering: sequential 4-digit numbers (0001, 0002, ...)
- File naming: `NNNN-short-title.md` using lowercase and hyphens
- Status lifecycle: Proposed -> Accepted -> (optionally) Deprecated or Superseded
- Immutability: once accepted, ADRs are not modified; a changed decision gets a new superseding ADR and the old one's status is updated to "Superseded by ADR-NNNN"
- Date format: exact dates when known, `~` prefix for approximate dates
- Index: `docs/adr/README.md` maintains a table of ADR, Title, Status, Date; new ADRs add a row and are committed with the related code changes

Recommended target-repo addition to the template (not in the source): a `## Preregistration touchpoints` section listing the prereg sections the ADR operates around, with the sentence "The preregistration governs methodology; this ADR records engineering decisions only." This makes the non-contradiction rule self-enforcing in every future ADR.
