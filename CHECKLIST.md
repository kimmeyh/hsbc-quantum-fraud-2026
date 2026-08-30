# Joint Checklist: Submission-Ready by Sep 8, 2026

Owners: **H** = Harold (only you can do it), **C** = Claude (I do it), **H+C** = decision or review done together.
Mark items `[x]` as they complete. This list is the working agenda; `docs/requirements-matrix.md` is the final acceptance gate.
Last reconciled: 2026-08-30 evening.

## Standing rule: Dirac-3 hardware budget

All development and debugging runs use the local proxy (the classical solve of the identical QUBO; `USE_DIRAC_EQC=0` pattern). Every metered Dirac-3 run requires team-lead approval with the expected call count stated in advance. Hardware is reserved for the preregistered [HW] result rows in the run grid (PREREGISTRATION section 10).

## Stage 0 to 1: Requirements and thesis (Aug 29 to 30) - COMPLETE

- [x] **H**: Locate the four official PDFs (provided via D:\Data\Temp\Downloads, Aug 30)
- [x] **C**: PDFs copied to `docs/source/`; all four read in full; requirements matrix verified line by line (page limits confirmed: 6-page proposal + 3-page appendix, PDF, min 10pt, 20 MB; team profile is a separate portal component)
- [x] **C**: Braket question resolved: exec summary "asks" for Braket, scope allows any quantum/quantum-inspired framework, hardware optional and not penalized. Positioning: Dirac-3 as measured [HW] evidence + phase-active Braket-simulator arm + Phase 2 Braket plan
- [x] **H**: Team name decided: "Claude Shannon's Fraud Catchers" (docs/team-name.md, with Claude Code disclosure language)
- [x] **H+C**: Thesis decided (Aug 30): performance-first framing, scoped to provable wins; H1b promotion to blanket claim only on Stage 3 evidence (docs/thesis-candidates.md). Overall goal recorded: best predictions/inference, quantum or not
- [x] **H**: Winning QML results located: FourierWall2 repo (in-segment CVQBoost wins, tuned config); analyzed in docs/evidence-inventory.md 3a/3b; 42 evidence files copied to experiments/reference/fourierwall2/
- [ ] **H**: Confirm portal account works and note required submission fields

## QCi sponsorship (parallel track)

- [x] **C**: Sponsorship letter drafted, merged with H's draft (V3: two-account story, measured QPU costs, ~500 s balance, functional variable-limit ask); canonical in docs/qci-sponsorship-request.md
- [x] **C**: Outlook draft "[v3]" saved to Drafts folder (delete v1/v2 drafts)
- [ ] **H**: Add recipient name and address, confirm Phase 2 [TBD] ranges, send; log the send date here
- [x] **C**: Phase 1 call-count arithmetic behind the ask (v1.1 run grid: 81 fits, ~2,300-2,600 QPU s vs ~3,000 requested); refresh the letter only if the frozen grid changes materially

## Stage 2: Experiment design (Aug 30 to 31)

- [x] **C**: PREREGISTRATION drafted (v1.0) with hypotheses, gates, metrics, splits, seeds, budgets
- [x] **C**: Independent reviews run (Sonnet + Opus) plus methods research (docs/research-baselines-best-practices.md); all 45+ proposals adjudicated (docs/prereg-review-adjudication.md); v1.1 produced with single primary endpoint, G0 recalibrated to the honest ULB band, proxy=structural-control design, de-personalized language
- [x] **C**: Reference library complete: all six methodology papers read IN FULL, summaries and design implications in docs/references.md; PDFs in docs/papers/
- [x] **C**: Environment set up and smoke-tested: .venv (Python 3.12.10), XGBoost 3.4.1, LightGBM 4.7.0, CatBoost 1.2.10, scikit-learn 1.9.0, Optuna, SHAP, imbalanced-learn, eqc-models 0.21.0, qci-client 5.0.2; QBoostClassifier weak_cls knobs verified
- [x] **C**: Harness skeleton written and smoke-tested on synthetic data only (experiments/src: data.py, tune.py, metrics.py)
- [x] **C**: ULB data located on disk (`XGBvHQXGB\datasets\creditcard.csv` + x1 split); no download needed
- [ ] **H+C**: Review and FREEZE `experiments/PREREGISTRATION.md` v1.1 (IN PROGRESS: H reading now; target Aug 31)
- [ ] **C**: On freeze: `git init`, commit protocol + code, record commit hash in the prereg by amendment
- [ ] **C**: Update `experiments/src/metrics.py` to the v1.1 statistical spec (stratified BCa 2,000 resamples, Wilson intervals, equal-mass ECE, dual operating points, paired-delta machinery) before any Stage 3 run
- [x] **C**: SPECTRA datasets downloaded and staged into `experiments/data/spectra/` (all four CSVs, filenames match the FourierWall2 pipeline)
- [ ] **H**: Kaggle competitions auth: run `kaggle auth login` (OAuth) or set the new-style KAGGLE_API_TOKEN from kaggle.com/settings/api; then accept IEEE-CIS competition rules in browser
- [ ] **C**: Download and stage IEEE-CIS into `experiments/data/ieee-cis/` once competitions auth works

## Stage 3: Experiments (Sep 1 to 4)

- [ ] **C**: Tuned classical arms: XGBoost, LightGBM, CatBoost, full features, 100 Optuna trials each; G0 gate = mean AUPRC >= 0.85 across 10 ULB seeds (the corroborated clean-protocol floor)
- [ ] **C**: Matched-feature classical arms and logistic control (MI top-k inside folds)
- [ ] **C**: Pilot seed-variance run and minimum-detectable-effect statement (required before hardware approval)
- [ ] **C**: CVQBoost arm tuned entirely on the proxy (non-negative ridge over identical weak-learner outputs, which doubles as the H4 structural control); free-tier config (top-13, schedule 2) and full config (top-17, schedule 3) frozen
- [ ] **C**: QFE phase-representation arms (Fourier Wall recipe) for every model, including trained-frequency GAM/GA2M/JOINT twins in H6 cells
- [ ] **C**: IEEE-CIS reduced Deotte recipe implemented per prereg section 5 (UID excluded, named aggregates, leakage controls, shuffled-label positive control)
- [ ] **C**: Temporal protocols: IEEE-CIS GroupKFold-by-month rolling origin; ULB temporal sensitivity split; classical-refit fairness control on any drift claim
- [ ] **H+C**: Approve hardware run list per block (B1 + G0b on current balance; B2/B3/B4 gated on QCi grant; spend priority B3 > B2 > H3 ladder > B4); execute once
- [ ] **C**: results.json per schema, CIs per spec, one-page results memo
- [ ] **H+C**: Gate review Sep 4: score gates as committed; decide headline promotion per the thesis decision rule

## Stages 4 to 5: Outline and draft (Sep 4 to 6)

- [ ] **C**: Paper outline, seven sections mapped to rubric plus appendices (results, preregistration registry with gate table, reproduction, references from docs/references.md)
- [ ] **H+C**: Approve outline
- [ ] **C**: Draft V1 with [HW]/[SIM]/[PROJ] tags on every number; prevalence beside every AUPRC
- [ ] **H**: Write or approve Team Capability content (education, GIC 2026 entry, repos, honest gaps, Claude Code disclosure)

## Stage 6: Adversarial reviews (Sep 6 to 7)

- [ ] **C**: Domain-reviewer pass, findings, revision V2
- [ ] **C**: Quantum-reviewer pass (including: is the gate-based arm phase-active, are the encoding diagnostics reported, does any claim exceed its evidence tag), findings, revision V3
- [ ] **C**: Rubric-scoring pass, fix lowest criterion
- [ ] **H**: Independent read-through as the reviewer; flag anything unclear or unconvincing

## Stages 7 to 8: Finalize (Sep 7 to 8)

- [ ] **C**: Verify every number in the paper against `results.json`
- [ ] **C**: Pre-publication confidentiality scan of the entire repo and paper: no employer-repo URLs or org names in remotes/links, no account identifiers, no API keys or .env content, no QPU balance figures tied to a named account. Grep for the known-sensitive strings plus "github.com" and "sandbox" before anything goes public. Re-verify experiments/reference/fourierwall2/ file by file
- [ ] **C**: Freeze and publish the reproducibility repo (public GitHub under kimmeyh); link in appendix as supplementary material
- [ ] **C**: Compliance walk of `requirements-matrix.md` against the final PDF (every A/B/C/D/E row)
- [ ] **H**: Final approval of PDF
- [ ] **H**: Produce final PDF with correct filename and title block ("Claude Shannon's Fraud Catchers", HSBC track)
- [ ] **H**: Submit via portal (Sep 8 or 9, never later than Sep 14); save confirmation receipt into `docs/`
