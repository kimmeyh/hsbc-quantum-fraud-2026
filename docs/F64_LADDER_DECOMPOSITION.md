# F64 + F91: what actually produced B2's +0.0256

Runs 2026-09-22 and 2026-09-23 (Sprint 18, Tasks C and F91). Zero metered
seconds; classical proxy throughout.

## BLUF

**B2's +0.0256 AUPRC comes from three-feature learners, not from having more
features.** Going from 13 features to 17 at the same subset order moves the
result by **+0.0001** (CI [-0.0024, +0.0026], spanning zero). Going from
two-feature to three-feature learners at the same feature count moves it by
**+0.0245** (CI [+0.0187, +0.0302], excluding zero). The interaction between
the two is about **+0.0011** -- small.

Practically: **the pool's expressiveness carries the gain, and the feature
budget does not.** A Phase 2 configuration should spend its variable budget on
richer learners over the features it already has, rather than on admitting more
features at the same order.

This also sharpens what the device contributes. Three-feature learners are what
push the problem past the ~200-learner resolution boundary A31 established, so
the configuration that wins is precisely the one the device must solve by
selecting rather than by spreading weight. B2's weight cosine of 0.83 is that
mechanism operating, and the result at that corner is the campaign's best.

## The four corners

| | order 2 | order 3 |
|---|---|---|
| **k=13** | 0.7681 (91 vars) | **0.7926 (377 vars)** |
| **k=17** | 0.7682 (153 vars) | 0.7928 (833 vars) [HW] |

Ten paired seeds (42-51), classical proxy, full-pair build, stratified
protocol. The k=17 order-3 corner is the published [HW] figure from B2.

Both new cells were run in Sprint 18: the k=17 order-2 cell under F64, and the
k=13 order-3 cell under F91 to identify the interaction F64 could not.

## The decomposition

| effect | estimate | 95% CI | excludes zero |
|---|---|---|---|
| k, 13 to 17, at order 2 | **+0.0001** | [-0.0024, +0.0026] | no |
| subset order, 2 to 3, at k=13 | **+0.0245** | [+0.0187, +0.0302] | **yes** |
| sum of main effects | +0.0245 | | |
| observed corner-to-corner [HW] | +0.0256 | | |
| implied interaction | +0.0011 | | |

The k effect is not merely non-significant; it is an order of magnitude smaller
than the MDE (0.0268) and its interval is tight. That is a positive statement
about the size of the effect, not an absence of evidence.

## What this licenses, and what it does not

**What it licenses.** Subset order carries the gain. Feature count contributes
nothing measurable at order 2, and the interaction is small enough that the two
main effects nearly account for the whole observed difference.

**What it does NOT license.** The fourth corner is the published **[HW]**
figure, while the other three are proxy. So the interaction term is *implied*
across arms rather than measured within one. A fully within-arm 2x2 would need
the proxy twin of k=17 at order 3 -- 833 variables, which is buildable but was
not run here. The implied +0.0011 is small enough that it is unlikely to change
the conclusion, and that is an expectation rather than a measurement.

**What changed since the first version of this document.** F64 alone reported a
BOUND, not an attribution: it showed feature count did not explain the gain but
could not say what did, because no k=13 order-3 cell existed. The Sprint 13
withdrawal of F64 was right about that limitation. F91 ran the missing corner,
and the attribution is now a subtraction rather than an inference.

## Why the physics predicted this was worth running

A31 established that the device cannot spread weight over more than about 200
learners: with the sum constraint at 1, a uniform weight over n learners is
1/n, against a representable step near 1/200.

| corner | variables | uniform weight | representable? |
|---|---|---|---|
| k=13, order 2 | 91 | 0.0110 | yes |
| k=17, order 2 | 153 | 0.0065 | yes |
| k=13, order 3 | 377 | 0.0027 | **no** |
| k=17, order 3 | 833 | 0.0012 | **no** |

The two corners that win are exactly the two the device cannot represent
diffusely. The proxy results above are the CLASSICAL half and are unaffected by
any device limit -- they establish that the classical optimum genuinely improves
with subset order, so the gain is a property of the pool rather than an artifact
of forced sparsification.

Put together: the classical optimum improves with three-feature learners, and
the device solves that regime by selecting a subset rather than spreading
weight. On B2 the sparsified answer outperformed. That is the argument for
cardinality-constrained selection as the Phase 2 formulation, and it now rests
on four corners rather than two.

## Provenance

- 20 new rows: 10 `config: mid` (F64) and 10 `config: deep` (F91), all
  `arm: cvqboost_proxy`, `pair_build: full`, `protocol: stratified`,
  `evidence_tag: SIM`, `metered_seconds: 0`.
- Pools built under WSL/Linux (the full-pair build requires POSIX `fork`);
  solved and scored on Windows.
- Pool sizes 153 and 377 on every seed, matching `k + C(k,2)` and
  `k + C(k,2) + C(k,3)` exactly.
- Every row carries the A33 environment stamp, including the resolved BLAS.
- `lambda_coef = 2 x n_train`, `relaxation_schedule 2`, `num_samples 8`,
  unchanged from the frozen configuration.
- `docs/paper/appendix.md` is UNCHANGED. B.3 says the k=17 order-2 cell "is
  Phase 2 experiment 1", which was true at filing; it is a frozen submitted
  document and these results live here instead.
