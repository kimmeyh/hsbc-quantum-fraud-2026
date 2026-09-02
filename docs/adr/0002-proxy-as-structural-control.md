# ADR-0002: Proxy-as-structural-control dual-role design

## Status

Accepted

## Date

2026-08-30

## Context

Dirac-3 hardware is metered and gated (standing constraint: development on a local stand-in only). CVQBoost tuning therefore needs a proxy. Separately, hypothesis H4 needs a structural control that isolates the Dirac solve's contribution from the weak-learner ensemble's. Two review findings converged: the proxy must be behaviorally faithful (a fidelity question), and the control must be a strong classical solver of the same objective (a fairness question).

## Decision

One implementation serves both roles: the CVQBoost QUBO objective (non-negative weights on the simplex over the identical weak-learner output matrix) solved classically by non-negative ridge, with an L1-sparse variant as the second control. This single code path is deliberate: any divergence between "the thing we tuned on" and "the thing we attribute against" would silently poison both uses. The G0b fidelity gate (5 hardware fits, Spearman rank correlation between proxy and hardware AUPRC, threshold 0.5) is the preregistered check on this bet. Module boundary: the proxy/control lives beside the CVQBoost wrapper and consumes the same weak-learner matrix object; no separate feature path.

## Alternatives Considered

### XGBoost stand-in proxy (the ForrierWall `LocalQuantumProxyModel` pattern)
- **Description**: A classical GBDT pretends to be the quantum model during development.
- **Pros**: Trivial; already existed.
- **Cons**: Solves a different objective; rank-order fidelity to Dirac configurations is unknowable; useless as an H4 control.
- **Why Rejected**: It validates plumbing, not configurations. Retained only as a smoke-test stand-in.

### Separate proxy and control implementations
- **Description**: Tune on one classical solver, attribute against another.
- **Pros**: Independence of concerns.
- **Cons**: Divergence risk; doubles maintenance; the fairness reviewer asks why they differ.
- **Why Rejected**: The single-path design makes proxy fidelity and control strength the same measured property.

## Consequences

### Positive
- H4's attributable delta is against the BEST classical solve of the identical objective, the honest counterfactual.
- Proxy tuning results transfer to hardware exactly insofar as G0b certifies.
### Negative
- If G0b fails (rho < 0.5), tuning claims are voided wholesale and hardware results are single-config points; the bet is all-or-nothing by design.
### Neutral
- eqc-models' own solver comparison (Emami et al., SLSQP/Hexaly) is the precedent for classical solves of this objective.

## Preregistration touchpoints

Sections 3 (G0b, H4), 4 (model arms), 6 (tuning on the proxy). The preregistration governs methodology; this ADR records engineering decisions only.

## References

`docs/prereg-review-adjudication.md` item 4; `docs/evidence-inventory.md`; Emami et al. arXiv:2503.11273 section 3.5.
