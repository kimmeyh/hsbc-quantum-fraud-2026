# Submission Development Plan

Goal: a Phase 1 concept proposal strong enough to be selected as a finalist, scoring 4 to 5 on every rubric criterion, and competitive with the strongest public example found (TrueLoop Compute).

**Target: submission-ready September 8, 2026.** Official deadline is September 15. The Sep 9 to 15 window is buffer for portal issues, late requirement discoveries, and one final review pass. Today is August 29, so the working window is 10 days.

Governing principle: requirements, then thesis, then experiments, then results, then paper. Never paper first.

The joint task checklist with owners is in `CHECKLIST.md`. This file holds the stage logic and exit tests.

## Rubric weights (Phase 1)

| Criterion | Weight |
|---|---|
| Problem Relevance & Impact | 25% |
| Technical Approach & Innovation | 25% |
| Feasibility | 20% |
| Validation Plan | 15% |
| Team Capability | 10% |
| Hybrid / Cross-Domain Approach | 5% |

## Stages and dates

### Stage 0: Requirements lock (Aug 29 to 30)
- Complete `requirements-matrix.md` from the four official PDFs (Harold copies them into `docs/source/`).
- Verify page limits. TrueLoop's proposal implies 6 pages main plus 3 appendix. Confirm before drafting.
- Exit test: no requirement has status "unknown."

### Stage 1: Winning thesis (Aug 30)
- Choose one thesis from the candidate notes (held privately). State it in three sentences: problem, mechanism, evidence.
- Exit test: the thesis answers a question the HSBC statement explicitly asks, and does not collide head-on with TrueLoop's occupied lane (drift-adaptation training economics).

### Stage 2: Preregistered experiment design (Aug 30 to 31)
- Write hypotheses, gates, metrics, seeds, splits, and budgets before running anything. Commit the preregistration file with a date so provenance is provable.
- Primary dataset: ULB European Cardholder (fits the timeline). IEEE-CIS becomes a Phase 2 [PROJ] item unless time appears.
- Model matrix (decided Aug 29):
  - Classical arms: tuned XGBoost, LightGBM, and CatBoost on the prescribed datasets.
  - Quantum arm: `QBoostClassifier` (CVQBoost, Dirac-3 via eqc_models) with a heterogeneous weak-classifier pool (KNN, LDA, LG, shallow XGB), reproducing the Loke/Griffin et al. 2026 configuration that achieved AUC-PR 0.8108 on ULB (see docs/evidence-inventory.md 3a). Secondary cheap arm if useful: sign-augmented `QSVMClassifier` (n_features + 1 variables, about 1 metered second per fit).
  - Structural control: the same weak-classifier ensemble with classical weight selection (the ForrierWall proxy pattern, or logistic stacking over identical weak learners). This isolates what the Dirac QUBO solve itself contributes, which is the comparison a reviewer will demand.
  - Equal tuning budget per arm, stated in the preregistration (same search space size and wall-clock class for XGB, LGBM, CatBoost, and QBoost knobs).
- Mandatory design elements:
  - Tuned XGBoost baseline on full features and on the matched feature subset. Sanity target: TrueLoop's ULB reference numbers (AUPRC 0.8937 full, 0.8809 matched).
  - Matched-capacity classical control for every quantum arm (same features, same head).
  - Primary metric AUPRC; secondary AUC-ROC, tuned-threshold F1, precision, recall, confusion matrix. Bootstrap CIs on headline numbers.
  - Stratified split for the main comparison, temporal split for drift realism.
  - Classical-refit fairness control on any drift claim (the control TrueLoop omitted).
- Exit test: a skeptical reviewer reading the plan cannot name an unfair comparison.

### Stage 3: Experiments (Sep 1 to 4, the long pole)
- Classical baselines first. A weak baseline invalidates everything downstream.
- Quantum-arm experiments per the preregistered plan. Nulls get published as nulls.
- Tag every result [SIM], [HW], or [PROJ] from the start.
- Output: `experiments/results.json` plus a one-page results memo.
- Exit test: at least one preregistered gate passes with a CI excluding zero, or the thesis is revised now (allowed here, not after drafting).

### Stage 4: Submission architecture (Sep 4)
- Outline the paper with the seven required sections mapped one-to-one to the rubric: Problem Framing, Technical Approach, Feasibility and Resources, Expected Impact, Validation Plan, Hybrid Integration, Team Capability, plus appendices (results, preregistration registry, reproduction).
- Every rubric criterion gets a heading a reviewer finds in under 10 seconds.

### Stage 5: Draft V1 (Sep 5 to 6)
- Full draft, under the page limit (TrueLoop used 5 of 9 permitted pages). Density beats length.
- Reuse the title-block and team-table conventions from the prior GIC 2026 submission.

### Stage 6: Adversarial reviews (Sep 6 to 7)
Three passes, each producing findings and a revision:
1. Domain pass: would an HSBC fraud analyst believe the framing and impact numbers?
2. Quantum pass: is the quantum component essential, honestly bounded, and not classically trivial? Every number tagged and defensible?
3. Rubric pass: score 1 to 5 per criterion as a reviewer would; fix the lowest criterion first.

### Stage 7: Final optimization (Sep 7 to 8)
- BLUF every section. Verify every number against `results.json`. Freeze the reproducibility repo and link it in the appendix.

### Stage 8: Compliance and readiness (Sep 8)
- Walk `requirements-matrix.md` line by line against the final PDF.
- Check filename, format, contact details, eligibility, portal fields.
- Submission-ready end of day Sep 8. Submit Sep 8 or 9. Never later than Sep 14.

## Standing risks

| Risk | Mitigation |
|---|---|
| Stage 3 overruns | Scope frozen to ULB; cut secondary experiments before cutting baseline quality |
| Quantum arm shows nothing | Publish the null; the measured regime map and its boundaries are still the deliverable |
| Page limits differ from assumption | Resolved in Stage 0 before drafting |
| Solo-team capability score | Cite the prior GIC 2026 Phase 1 submission, public repos, reproducibility practice; state the fraud-domain gap honestly as TrueLoop did |
| Portal surprises | Ready by Sep 8 leaves 7 days of buffer |
