# Sprint 4 Summary: Proxy Tuning, Baseline Research, First Hardware Blocks, Results Memo

Archival record (three-doc rule). Dates: Sep 3-4, 2026. Branch `feature/20260903_Sprint_4` (carried forward from Sprint 3's head); PR #21 merged to develop 2026-09-04; develop merged to main via PR #22. Sources: SPRINT_4_PLAN.md, SPRINT_4_RETROSPECTIVE.md, gate_report.md, RESULTS_MEMO.md, git history, PR #21.

## Objective

Make the quantum arm real: tune CVQBoost on the proxy per the frozen section-6 protocol, research the ULB baseline-protocol gap behind G0, run the first metered hardware blocks on per-block approval, and close with the results memo Sprint 5's paper is written from. Scope: F22 + F21 + F2 + F7 (defined-scope rule).

## Delivered

1. **F22 section-6 proxy tuning**: 100 Optuna TPE trials under WSL with the A3 full-pair build, disk-cached pool matrices, free-tier/device pruning. The best trial reached 0.6873 validation AP against the preregistered starting config's 0.7232, so the validation-AP rule RETAINED the starting config. The best healthy config (logistic weak learners, class-balanced, k=9, 45 vars) lifted the Sprint 3 lg quarantine. Amendment A6 added score-health flags; the selected dct config carries a WARN on 10/10 seeds (mode share 0.951), which is reported rather than hidden. Deviations reported as-is: TPE spent 73/100 trials on lg; KNN weak learners excluded on proxy cost.
2. **F21 baseline-protocol research**: primary-source work established that G0's 0.85 threshold derived from a band no primary source corroborates. Its probable origin uses trapezoidal PR-AUC (banned by section 9), trains on 90% of data with no held-out test fold, and keeps duplicates; the clean-protocol equivalent is ~0.80-0.81 and a step-wise-AP benchmark reports 0.78. Our 0.8296 exceeds both. G0 stays FAIL as committed. Also found: no published work quantifies the dedupe effect on ULB, a genuine literature gap.
3. **F2 first metered hardware campaign** (team-lead approved, Criterion H honored): 27 Dirac-3 fits, **120 QPU s**, 0 failures, 0 retries, 4-5 s per fit at 25-91 variables. **G0b PASSED** (Spearman 0.900, p = 0.037) -- the first gate this project has passed, on real hardware. Every [HW] row carries billed seconds, both objective values, and the weight cosine.
4. **The structural finding**: hardware minus its exact classical proxy on identical Hamiltonians = **-0.0010 AUPRC** [CI -0.0032, +0.0012], weight cosine 0.975-0.999, hardware objective always 0.013-0.413% above the exact minimum. A zero-metered lambda sweep then showed the weights stay uniform even at lambda = 0, so the near-degeneracy comes from the simplex constraint over correlated +/-1 learners, not the ridge term. Labeled the H4 solver-fidelity COMPONENT; the two preregistered H4 controls remain unrun.
5. **H1b null as preregistered**: Dirac-3 CVQBoost minus CatBoost matched-13 = -0.0399 [CI -0.0571, -0.0227], exceeding the A5 MDE, trailing on 9 of 10 seeds. Also -0.0347 vs XGBoost and -0.0353 vs LightGBM.
6. **F7 results memo**: gate table scored as committed, per-arm summary, plain-terms reading, framing options. An independent review of the memo found 3 numeric errors and 4 overclaims, all corrected; the H4 row was relabeled PARTIAL and G0b footnoted (degenerate anchors, 0.0001 tie, competitive-only Spearman 0.5).
7. **Amendments A6, A7, A8**: score-health flags; the protocol-sensitivity ladder (S1 metric, S2 duplicates, S3 split ratio) approved as labeled exploratory cells with G0 unchanged; and the review-fix registration.
8. **Team-lead decisions recorded**: headline framing DECIDED as the production-bound program spine; A7 approved; F25 registered.
9. **Backlog registered mid-sprint**: F25 (non-convex cardinality-constrained CVQBoost, the direct consequence of the degeneracy finding), F26 (cost-based operating points), F27 (production-trial design), F28 (explainability thread).
10. **Reviews**: Copilot 2 findings, Claude 15 findings (Opus 5, evidence JSON excluded from scope), all 17 fixed, replied, and resolved. The most serious: unparseable billing read as zero spend, making the hardware budget guard blind. Fixed with a conservative charge, an audit flag, and regression tests (22 total).

## Estimated vs actual

Authored work 0.5-0.75 of estimate; the 100-trial study ran ~85 min against 120-240; the hardware block ~150 min wall against 240, with only 120 s billed. Key lesson recorded: the wall-clock cost of metered work is pool building and queueing, not the QPU.

## Key decisions

- G0 reported FAIL as committed despite F21 showing its threshold was miscalibrated; the research became an amendment rather than a goalpost move.
- Headline framing: production-bound program spine (deployable system, mapped search, stated expectation with reasons, explainability, concrete trial path).
- Standing rules added: generated evidence artifacts are out of code-review scope; merge-readiness requires all reviews complete and all findings resolved.

## Hardware

120 QPU s of ~500 s balance; ~380 s remain. B2/B3/B4/B5 still gated on the QCi grant.

## Links

PR #21 (merged), PR #22 (develop->main), issues #17-#20 (closed), docs/sprints/SPRINT_4_PLAN.md, SPRINT_4_RETROSPECTIVE.md, docs/RESULTS_MEMO.md, experiments/results/gate_report.md, docs/research-ulb-baseline-protocols.md, docs/HARDWARE_REQUEST_B1_G0b.md.
