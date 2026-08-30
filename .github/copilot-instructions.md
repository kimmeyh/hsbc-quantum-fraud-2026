# Copilot Review Instructions

Project: a preregistered benchmark study comparing CVQBoost (quantum-inspired boosting on QCi Dirac-3 hardware) against tuned classical baselines (XGBoost, LightGBM, CatBoost) on fraud-detection datasets, feeding a competition submission ("2026 Global Quantum + AI Challenge", HSBC track). Solo team lead plus Claude Code. Windows 11, PowerShell, Python 3.12 in `.venv`.

Authoritative documents a change must not contradict:
- `experiments/PREREGISTRATION.md` — the frozen protocol (gates, splits, budgets, statistics). Once its status line reads FROZEN, any change to gates, budgets, splits, arms, or statistics in code or docs is a protocol amendment and must reference a dated amendment in that file.
- `docs/SPRINT_PROCESS.md` — branch model (feature/YYYYMMDD_Sprint_N to develop; develop to main is team-lead-only) and the carry-forward rule.
- `docs/research-baselines-best-practices.md` — the methods standard the code implements.

## Review priorities, highest first

1. **Data leakage.** Every transform (scaling, encoding, imputation, feature selection, aggregation, whitening, calibration, threshold selection) must be fit on training data only, inside the fold, and applied to validation/test. Flag any fit/fit_transform on a full dataset before splitting, any resampling (SMOTE etc.) before splitting, any aggregate computed across the temporal split boundary, any test-set touch during tuning or threshold selection, and any identifier column (UID, card ids) entering a model as a raw feature.
2. **Secrets and confidentiality.** No credentials, API keys, tokens, `.env` content, or `kaggle.json` in any commit. No references to the team lead's employer, its repositories, or account-specific QPU balances. Flag any hardcoded absolute path that embeds information beyond this repository.
3. **Statistical correctness.** AUPRC must be computed as step-wise average precision (`average_precision_score`), never trapezoidal `auc(recall, precision)`. Confidence intervals: stratified BCa bootstrap with 2,000 resamples; paired comparisons must apply identical resample indices to both arms. Wilson intervals for precision/recall. Calibration measured with equal-mass binning, never Brier alone. Flag any cross-dataset averaging or comparison of AUPRC values.
4. **Fairness of comparison.** Equal tuning budgets across model families; early stopping on a validation fold, never test; matched feature sets where the protocol requires them; seeds and splits from the preregistered lists. Flag any arm-specific shortcut that gives one model family information or budget another lacks.
5. **Hardware cost safety.** Any code path that can submit a metered Dirac-3 job (`QBoostClassifier.fit`, `QSVMClassifier.fit` with cloud solver, `USE_DIRAC_EQC=1`) must be impossible to trigger by default, must never sit inside a tuning loop, and must log the expected call count before submitting.
6. **Results integrity.** Reported numbers must originate from `results.json` records carrying an evidence tag ([HW], [SIM], [PROJ]); flag any hardcoded metric value in docs or paper drafts that lacks a results.json counterpart.

## Conventions

- Python: match existing style in `experiments/src/` (type hints on signatures, module docstrings stating which preregistration section the file implements, no print-driven debugging left behind).
- Documentation: plain professional prose; no emoji; no em dashes; no contractions in formal docs.
- PowerShell for automation scripts, not bash.
- Do not suggest adding new model arms, metrics, or datasets; scope is fixed by the preregistration.
