# F101: `in_pocket` is almost perfectly predictable from the phase features

Sprint 21 Task E. Zero metered seconds. Evidence tag `[SIM]`; rows in
`experiments/results/f101_in_pocket_provenance.json`.

## The question

Route-and-blend requires the router's gate to be independent of the
specialist's features. If `in_pocket` can be predicted from the same SPECTRA
phase features the specialist consumes, the gate is dependent and routing
re-correlates the pocket rather than partitioning it.

## The answer

**The gate is not independent. It is nearly deterministic in the features.**

Two model classes, three seeds, all three frozen cells, predicting
`in_pocket` on a held-out test fold from the phase features alone:

| Cell | Seed | LogReg AUC | HGB AUC |
|---|---|---|---|
| telecom_churn | 42 | 0.9907 | 0.9906 |
| telecom_churn | 43 | 0.9927 | 0.9924 |
| telecom_churn | 44 | 0.9947 | 0.9945 |
| energy_steel | 42 | 0.9930 | 0.9921 |
| energy_steel | 43 | 0.9928 | 0.9923 |
| energy_steel | 44 | 0.5911 (see note) | 0.9935 |
| oilgas_gasturbine | 42 | 0.9405 | 0.9387 |
| oilgas_gasturbine | 43 | 0.9410 | 0.9384 |
| oilgas_gasturbine | 44 | 0.9342 | 0.9307 |

**Note on energy_steel seed 44.** The logistic-regression AUC of 0.5911 is a
convergence failure, not a finding: the solver reported
"TOTAL NO. OF ITERATIONS REACHED LIMIT" at `max_iter=3000` on unscaled
features. HGB on the identical split returns 0.9935. The row is kept rather
than deleted, with its cause named, because a single anomalous number silently
dropped is worse than one explained. It is not evidence of a different regime
on that seed.

## Reading

**`in_pocket` is a function of the features, recoverable at AUC 0.93-0.99.**
The two tree-and-linear classes agree closely everywhere the linear solver
converged, so this is not an artifact of one model's inductive bias.

**Consequence for the routing architecture.** A gate this predictable cannot
serve as an independent router over these features. Two readings follow, and
they are not equivalent:

1. **The pocket is a feature-space region, by construction.** If SPECTRA's
   pocket was *defined* by a rule over these covariates, then perfect
   predictability is definitional and tells us nothing new — but it also means
   routing on a learned gate adds nothing a feature interaction could not do.
2. **The pocket is independently defined and merely correlates.** Then the
   correlation is an empirical property of this data, and a router trained on
   it will re-correlate the pocket rather than partition it, which is the
   failure mode this card was written to detect.

**Which of the two holds is not decidable from this repository**, and the
distinction changes what any Phase 2 routing claim is allowed to say. The F101
card already names what settles it: the SPECTRA author's construction details,
which the team lead is to ask for. This diagnostic is what makes that question
worth asking, and it narrows it to one sentence: **was `in_pocket` derived from
the covariates, or assigned independently of them?**

## What this does not say

It says nothing about whether CVQBoost beats a classical arm in-segment. That
is F90 and F100. A dependent gate is a problem for the *routing* claim
(proposal section 7's architecture), not for the in-segment replication (H5).
