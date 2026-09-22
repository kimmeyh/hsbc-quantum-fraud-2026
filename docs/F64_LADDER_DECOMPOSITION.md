# F64: decomposing the B2 confound

Run 2026-09-22 (Sprint 18 Task C). Zero metered seconds; classical proxy only.

## The question

B2's **+0.0256 AUPRC on ten of ten seeds** is the campaign's only positive
result at scale. Two factors moved together to produce it, and the submission
could not say which mattered:

| cell | k | subset order | variables | test AUPRC |
|---|---|---|---|---|
| free | 13 | 2 | 91 | 0.7681 (proxy) / 0.7671 [HW] |
| **mid** | **17** | **2** | **153** | **0.7682 (proxy, this run)** |
| full | 17 | 3 | 833 | 0.7928 [HW] |

Appendix B.3 states the disconfirming cell is unrun, about the one experiment
that would resolve its own headline claim's confound. This is that cell.

## The result

**k=17 at order 2 minus k=13 at order 2**, ten paired seeds (42-51), classical
proxy, full-pair build, stratified protocol:

| | |
|---|---|
| mean delta | **+0.00007** |
| 95% CI | **[-0.0024, +0.0026]** |
| excludes zero | **no** |
| positive seeds | 5 of 10 |
| MDE (A5) | 0.0268 |

The interval spans zero and is an order of magnitude tighter than the minimum
detectable effect. **Going from 13 to 17 features at order 2 moves the result by
essentially nothing.**

## What this licenses, and what it does not

**This is a BOUND, not an attribution.** The Sprint 13 withdrawal of this card
was methodologically right: a one-factor probe varies one axis with everything
else frozen at values chosen for a different configuration, so it measures the
axis it varies and is silent about interaction. That objection stands, and the
result is reported accordingly.

**What it licenses.** Feature count alone does not explain +0.0256. The middle
of the ladder sits on top of its lower rung, not between the rungs. Whatever
produces the gain requires the move to three-feature learners -- either the
richer learners themselves, or an interaction between them and the larger
feature set.

**What it does NOT license.** It does not show the gain is caused by subset
order *alone*. The design cannot separate "order 3 matters" from "order 3
matters given k=17", because no k=13 order-3 cell exists. A claim that the
+0.0256 is attributable to subset order would be exactly the over-reading the
Sprint 13 withdrawal warned about.

**What would settle it.** The fourth corner: k=13 at order 3 (13 + C(13,2) +
C(13,3) = 377 variables). With all four cells the interaction term is
identified. That is a separate card, not a silent extension of this one.

## Why the physics predicted this was worth running

A31 established that the device cannot spread weight over more than about 200
learners: with the sum constraint at 1, a uniform weight over n learners is
1/n, against a representable step near 1/200.

- At **153 variables** a uniform weight is 0.0065 -- representable.
- At **833 variables** it is 0.0012 -- below the floor, so the device must
  return something sparser.

So the two cells differ in whether the device can represent a diffuse optimum
at all. The proxy result above is the CLASSICAL half of that comparison and is
unaffected by the device limit; it establishes that the classical optimum does
not improve with feature count alone. The hardware half is already published:
B2's weight cosine of 0.83 measures a device solving a sparsified version of
the problem, and that sparsified answer outperformed.

**The two halves together say something sharper than either alone.** The gain
at 833 variables is not the classical optimum being better -- the classical
optimum at 153 is the same as at 91. It appears only where three-feature
learners enter, in the regime where the device is forced to select rather than
spread.

## Provenance

- 10 rows, `arm: cvqboost_proxy`, `config: mid`, `pair_build: full`,
  `protocol: stratified`, `evidence_tag: SIM`, `metered_seconds: 0`.
- Pools built under WSL/Linux (the full-pair build requires POSIX `fork`);
  solved and scored on Windows.
- Each row carries the A33 environment stamp, including the resolved BLAS.
  These are the first rows in the store to do so.
- Pool size 153 on every seed, matching `k + C(k,2)` for k=17 exactly.
- `lambda_coef = 2 x n_train` and `relaxation_schedule 2`, `num_samples 8`
  unchanged from the frozen configuration.
