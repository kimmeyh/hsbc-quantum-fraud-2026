# F18 Findings: Dirac-3 Integration Notes Mined (qml-unlocked/DIRAC3.md)

**Purpose**: dispositions for every F18 checklist item (Sprint 3 Task A, card #14).
**Audience**: team lead; the F1/F2 implementation.
**Last Updated**: 2026-09-02

Source read in full plus the three ForrierWall reference points (line numbers in DIRAC3.md have drifted; content located by symbol: `_resolve_qci_credentials_once` main.py:50, `dirac_params` :92, `_fit_qboost_component_with_backoff` :1078, plus ForrierWall CLAUDE.md). Binding constraint honored: the frozen preregistration is unchanged; every disposition below is adopt/reject at the tooling level or a surfaced proposal; **zero amendments required**.

## Dispositions

| # | Item | Disposition | Detail |
|---|---|---|---|
| 1 | Variable-count math | DONE (pre-sprint) | Amendment A2 applied 2026-09-02: sequential totals C(n,2) / C(n,2)+C(n,3), verified vs measured runs; 949 documented ceiling |
| 2 | QSVM sign augmentation | DONE (pre-sprint) | Already frozen in section 4 ("sign-augmented primal"); B5 implementation must apply `np.hstack([X, -X])` at fit AND predict |
| 3 | {-1,+1} label mapping | ADOPT (B5 spec) | `fit` asserts `set(y) == {-1, 1}`; pipeline maps {0,1}->{-1,+1} before fit, uses `predict_raw` for AP scoring; round-trips covered by a known-answer test |
| 4 | `weak_cls_strategy="sequential"` | ADOPT (B5 spec) | Constructor-passed explicitly on every platform (Windows requirement; also keeps the model identical if anything ever runs on Linux, incl. the A3 WSL2 side-by-side's sequential arm) |
| 5 | Free-tier backoff pattern | ADOPT detection, REJECT mutation | Error DETECTION adopted: rejection contains "number of variables" + "free-tier device limit"; wording change silently breaks string-matching, so log the raw error too. Config-MUTATING backoff (ForrierWall ladder: schedule-1 -> schedule 1/ns<=2 -> schedule 1/ns=1) is REJECTED for preregistered cells: the frozen rule is retry at most twice with IDENTICAL config, and a variable-limit rejection is a sizing error prevented ex ante by A2's exact formula, not a transient. If it fires anyway, the cell FAILS per protocol; it never silently runs a different model. ForrierWall's own default agrees (`fail_fast_on_variable_limit=True`) |
| 6 | Credentials pattern | ADOPT (ADR-0011 practice) | Gitignored `.env` with `QCI_API_URL=https://api.qci-prod.com` (verified working) + `QCI_TOKEN`; both REQUIRED, no default URL; resolve once at startup, export to env, never print/log the key. Note: eqc-models prints the full solve response to stdout on every fit -- capture to the run log, it contains job/energy data, not secrets |
| 7 | Constructor-knob cross-check | ADOPT + 1 new invariant | Frozen config (schedule=3, num_samples=8, relaxation_schedule=2, lambda_coef=2*n_train, sequential) uses only real eqc-models 0.21.0 parameter names -- verified against the installed source. NEW INVARIANT from ForrierWall gotcha: QBoostClassifier kwargs there were filtered through `inspect.signature`, so a misspelled param is silently dropped; our pipeline constructs the classifier and then ASSERTS each configured attribute round-trips (`getattr(clf, k) == v`) before any fit, so a config hash can never describe a model that was not actually built |
| 8 | Cost-control rules | ADOPT (already aligned) | One metered call per fit; never loop fit inside a grid on hardware; proxy-first dev (= ADR-0002, USE_DIRAC_EQC pattern). Cost drivers confirmed: num_samples linear; rx 2->4 ~3.8x for zero measured benefit (frozen rx=2 stands); ~0.58 s/sample at 105 vars -> ~3.9 s at 560. B5 QSVM ~1 s/fit measured on hardware supports the frozen ~15 s estimate for 12 fits |
| 9 | Below-4-features guard / H3 low rung | RESOLVED, no impact | `topNPairs` asserts pairs <= n(n-3)/2 (empty message when it fires); impossible for n<4. H3 ladder minimum is k=5: schedule 2 -> 10 vars, schedule 3 -> 20 vars, both clear. Guard adopted anyway: pipeline refuses schedule>=2 for n<4 with a real error message |
| 10 | Findings memo | THIS DOCUMENT | Presented at Phase 5 validation |

## Items feeding B5/B7 implementation directly

Label mapping (+ mapping test), explicit sequential strategy, attribute round-trip assert, error-string detection with raw-error logging, fail-fast on variable limit, credentials resolve-once, n<4 guard, and the A2 exact variable formula as the pre-request sizing check (B7 states per-block variable counts computed with `qubo_vars`).

## Amendment candidates

None. Every adoption is tooling-level; the frozen retry rule, configs, budgets, and gates are untouched.
