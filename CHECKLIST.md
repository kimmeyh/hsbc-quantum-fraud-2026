# Joint Checklist: Submission-Ready by Sep 8, 2026

Owners: **H** = Harold (only you can do it), **C** = Claude (I do it), **H+C** = decision or review done together.
Mark items `[x]` as they complete. This list is the working agenda; `docs/requirements-matrix.md` is the final acceptance gate.
Last reconciled: 2026-09-04 (Sprint 4 close).

## Standing rule: Dirac-3 hardware budget

All development and debugging runs use the local proxy (the classical solve of the identical QUBO; `USE_DIRAC_EQC=0` pattern). Every metered Dirac-3 run requires team-lead approval with the expected call count stated in advance. Hardware is reserved for the preregistered [HW] result rows in the run grid (PREREGISTRATION section 10).

## Stage 0 to 1: Requirements and thesis (Aug 29 to 30) - COMPLETE

- [x] **H**: Locate the four official PDFs (provided via D:\Data\Temp\Downloads, Aug 30)
- [x] **C**: PDFs copied to `docs/source/`; all four read in full; requirements matrix verified line by line (page limits confirmed: 6-page proposal + 3-page appendix, PDF, min 10pt, 20 MB; team profile is a separate portal component)
- [x] **C**: Braket question resolved: exec summary "asks" for Braket, scope allows any quantum/quantum-inspired framework, hardware optional and not penalized. Positioning: Dirac-3 as measured [HW] evidence + phase-active Braket-simulator arm + Phase 2 Braket plan
- [x] **H**: Team name decided: "Claude Shannon's Fraud Catchers" (docs/team-name.md, with Claude Code disclosure language)
- [x] **H+C**: Thesis decided (Aug 30): performance-first framing, scoped to provable wins; H1b promotion to blanket claim only on Stage 3 evidence (docs/thesis-candidates.md). Overall goal recorded: best predictions/inference, quantum or not
- [x] **H**: Winning QML results located: FourierWall2 repo (in-segment CVQBoost wins, tuned config); analyzed in docs/evidence-inventory.md 3a/3b; 42 evidence files copied to experiments/reference/fourierwall2/
- [x] **H**: Portal account confirmed (Sprint 2, F12): submission = 5-slot file upload; fields recorded in requirements-matrix A5/A5b; team profile ships as a one-page PDF; nothing uploaded until the final package

## QCi sponsorship (parallel track)

- [x] **C**: Sponsorship letter drafted, merged with H's draft (V3: two-account story, measured QPU costs, ~500 s balance, functional variable-limit ask); canonical in docs/qci-sponsorship-request.md
- [x] **C**: Outlook draft "[v3]" saved to Drafts folder (delete v1/v2 drafts)
- [x] **H**: QCi letter taken over and handled by team lead; declared completed 2026-08-30 (F11)
- [x] **C**: Phase 1 call-count arithmetic behind the ask (v1.1 run grid: 81 fits, ~2,300-2,600 QPU s vs ~3,000 requested); refresh the letter only if the frozen grid changes materially

## Stage 2: Experiment design (Aug 30 to 31)

- [x] **C**: PREREGISTRATION drafted (v1.0) with hypotheses, gates, metrics, splits, seeds, budgets
- [x] **C**: Independent reviews run (Sonnet + Opus) plus methods research (docs/research-baselines-best-practices.md); all 45+ proposals adjudicated (docs/prereg-review-adjudication.md); v1.1 produced with single primary endpoint, G0 recalibrated to the honest ULB band, proxy=structural-control design, de-personalized language
- [x] **C**: Reference library complete: all six methodology papers read IN FULL, summaries and design implications in docs/references.md; PDFs in docs/papers/
- [x] **C**: Environment set up and smoke-tested: .venv (Python 3.12.10), XGBoost 3.4.1, LightGBM 4.7.0, CatBoost 1.2.10, scikit-learn 1.9.0, Optuna, SHAP, imbalanced-learn, eqc-models 0.21.0, qci-client 5.0.2; QBoostClassifier weak_cls knobs verified
- [x] **C**: Harness skeleton written and smoke-tested on synthetic data only (experiments/src: data.py, tune.py, metrics.py)
- [x] **C**: ULB data located on disk (`XGBvHQXGB\datasets\creditcard.csv` + x1 split); no download needed
- [x] **H+C**: PREREGISTRATION v1.1 FROZEN (H approved 2026-08-30; commit 95751b9, tag prereg-freeze, amendment A1)
- [x] **C**: metrics.py at v1.1 spec, 11 known-answer tests passing (BCa vs scipy, Wilson vs statsmodels)
- [x] **C**: Pilot variance run complete: ULB 10-seed untuned-XGB mean AP 0.8268, seed SD 0.0243, MDE(10) 0.0242 (experiments/PILOT_VARIANCE.md)
- [x] **C**: Sprint 1 closed with all acceptance criteria evidenced (docs/sprints/SPRINT_1_PLAN.md); PR #1 ready for merge to develop
- [x] **C**: SPECTRA datasets downloaded and staged into `experiments/data/spectra/` (all four CSVs, filenames match the FourierWall2 pipeline)
- [x] **H**: Kaggle OAuth completed and IEEE-CIS rules accepted (Aug 30); legacy env-var credentials removed after they were found shadowing the OAuth cache
- [x] **C**: IEEE-CIS downloaded and staged into `experiments/data/ieee-cis/` (train_transaction 651.7 MB, train_identity, test files, 1.3 GB total)
- [x] **C**: Sprint process adopted (docs/SPRINT_PROCESS.md); private GitHub remote live at github.com/kimmeyh/hsbc-quantum-fraud-2026 with main/develop branches; Sprint 1 plan drafted awaiting approval

## Stage 3: Experiments (Sep 1 to 4)

- [x] **C**: Tuned classical arms: XGBoost, LightGBM, CatBoost, full features, 100 Optuna trials each (Sprint 3); G0 scored as committed = FAIL (tuned-XGB mean AP 0.8296 vs 0.85; no leakage flag); framing decided at F7 gate review; F21 researches the protocol gap
- [x] **C**: Matched-feature classical arms and logistic control (MI top-13 on train per seed; Sprint 3, 40 rows)
- [x] **C**: Pilot seed-variance run and minimum-detectable-effect statement (done Sprint 1: mean AP 0.8268, seed SD 0.0243, MDE(10) 0.0242; experiments/PILOT_VARIANCE.md)
- [x] **C**: CVQBoost arm tuned entirely on the proxy: pipeline + exact-Hamiltonian solve (Sprint 3), section-6 100-trial tuning (Sprint 4, F22); starting config retained by the validation-AP rule; tuned lg config lifts the score-health quarantine
- [ ] **C**: QFE phase-representation arms (Fourier Wall recipe) for every model, including trained-frequency GAM/GA2M/JOINT twins in H6 cells
- [ ] **C**: IEEE-CIS reduced Deotte recipe implemented per prereg section 5 (UID excluded, named aggregates, leakage controls, shuffled-label positive control)
- [ ] **C**: Temporal protocols: IEEE-CIS GroupKFold-by-month rolling origin; ULB temporal sensitivity split; classical-refit fairness control on any drift claim
- [x] **H+C**: B1 + G0b approved and executed 2026-09-03 (27 fits, 120 QPU s, 0 failures; G0b PASS Spearman 0.900). B2/B3/B4/B5 remain gated on the QCi grant, spend priority B3 > B2 > H3 ladder > B4
- [x] **C**: results.json per schema (147 rows: 120 [SIM], 27 [HW]), CIs per spec, one-page results memo (docs/RESULTS_MEMO.md, Sprint 4)
- [x] **H+C**: Gate review done 2026-09-03/04: G0 FAIL as committed, G0b PASS (0.900), H1b null, H4 partial; headline framing DECIDED (production-bound program spine). Gate table refreshes with each later evidence sprint

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
