# Explainability: CVQBoost ensemble versus the GBDT baseline

**Purpose**: measured evidence on how inspectable each arm is, for the deployment question that actually gates adoption in banking: can a decline be explained to a customer, a disputes team, and a regulator.
**Audience**: team lead; paper section (F28).
**Last Updated**: 2026-09-04

All figures below are computed from the committed pool and the exact proxy solve (seed 42, free config, full-pair build, 91 weak learners over 13 features). Zero metered seconds. Reproduce with `python experiments/src/explainability.py`.

## 1. The structural argument

A CVQBoost ensemble is a weighted vote over small classifiers, each fit on ONE, TWO or THREE features. Two consequences follow directly, without any attribution model:

- **Every learner is readable on its own.** A depth-limited tree over two named features is inspectable by a human analyst; there is no hidden interaction depth to unwind.
- **The score decomposes exactly.** The ensemble score is the sum of weight times vote over learners, so each learner's contribution to a specific decision is an exact arithmetic term, not an approximation. SHAP and similar methods exist precisely because boosted-tree ensembles do NOT decompose this way; here the decomposition is the model.

By contrast the tuned CatBoost baseline uses up to 2,000 trees; explaining one decision requires a post-hoc attribution method whose output is an estimate of the model, not the model itself.

## 2. The measured counter-finding, stated first

Weight is spread almost uniformly across the pool: 91 of 91 learners carry non-negligible weight, and it takes **46 learners to reach 50%** of the total weight, 73 to reach 80%, and 87 to reach 95%. The maximum single weight is 0.0110 against a uniform value of 0.0110.

This is the Sprint 4 near-degeneracy finding seen from the explainability side, and it cuts BOTH ways. It weakens any claim that a handful of learners explain the model: they do not, at this configuration. It does not weaken the exact-decomposition property, which holds regardless of how weight is distributed. The honest summary is that CVQBoost gives **exact** attribution over **many** simple terms, while the GBDT gives **approximate** attribution over a smaller number of complex ones.

## 3. A worked decision

Test transaction index 10390 (seed 42 test fold), a true fraud, scored highest by the CVQBoost arm. The decision decomposes exactly into learner contributions:

| Rank | Learner features | Weight | Vote | Contribution |
|---|---|---|---|---|
| 1 | V2 + V21 | 0.0110 | +1 | +0.0110 |
| 2 | V4 + V21 | 0.0110 | +1 | +0.0110 |
| 3 | V7 + V21 | 0.0110 | +1 | +0.0110 |
| 4 | V3 + V18 | 0.0110 | +1 | +0.0110 |
| 5 | V3 + V7 | 0.0110 | +1 | +0.0110 |
| 6 | V3 + V21 | 0.0110 | +1 | +0.0110 |
| 7 | V4 + V9 | 0.0110 | +1 | +0.0110 |
| 8 | V4 + V18 | 0.0110 | +1 | +0.0110 |

Total score +0.9121 (range -1 to +1); the eight terms above account for 8.8% of the absolute contribution. Every remaining term is available and readable in the same form.

**The same decision under CatBoost** requires SHAP or an equivalent post-hoc method: the explanation is a fitted approximation of the ensemble's behavior near this point, valid locally, and it changes if the attribution method changes. Both explanations are usable in practice; only one of them is the model itself.

## 4. What this means for deployment

- **Dispute handling**: a declined transaction can be explained as a list of named feature-pair rules that voted against it, with exact weights.
- **Regulatory review**: the model is a linear combination of inspectable terms with published weights, so model documentation does not depend on an attribution library.
- **The caveat that must travel with the claim**: at the current configuration the decision is spread across many small terms rather than a few large ones, so an analyst reads a longer explanation. A sparser formulation (F25, cardinality-constrained selection) would concentrate weight and shorten it, which is one more reason that formulation is the Phase 2 direction.