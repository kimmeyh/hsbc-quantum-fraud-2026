---
title: "eqc-models and Dirac-3: Integration Feedback"
subtitle: "From 61 metered fits and a sustained proxy build, September 2026"
date: "September 2026"
---

# Integration feedback for QCi

**Content current to 2026-09-12**, the date our Phase 1 entry was filed.
Nothing later has been added.

This is the package promised in our access request. It covers what we found
building against `eqc-models` 0.21.0 and `qci-client` 5.0.2 over five weeks,
across 61 metered Dirac-3 fits and several thousand classical solves of the
same Hamiltonian.

Every item states what we observed, what we expected, and what we did about it.
Each cites the file and line, or the results row, that establishes it, so you
can check any claim rather than take our word for it. Line references are to
the repository accompanying our submission.

Nothing here is a complaint. The device did what it said it would do on every
one of those 61 calls, with zero failures and zero retries. These are the
places where a competent user loses time, which is the part we can usefully
tell you about.

## 1. The free-tier variable ceiling is undocumented and differs from the
##    documented limit

**Observed.** A 312-variable continuous degree-2 job was refused server-side,
before billing, with:

> Number of variables '312' in problem is greater than the free-tier device
> limit '100'

**Expected.** The documented limit is 949, described as a sum over
`num_levels`. That is the figure a reader sizing an experiment from the
documentation will use.

**The divergence.** The 949 figure applies to integer-encoded jobs. It does not
bind a continuous, sum-constrained run, which is instead capped at 100
variables on the free tier. Both limits are real; they apply to different job
classes, and only one of them is documented.

**Cost to us.** The ceiling is confirmable only empirically, by a rejected job.
It forced a preregistration amendment (A12) and a reduction from k=13 to k=6
features, which is four families at 60 variables. Every scaling statement we
could make at the time was bounded by a tier limit rather than by the device.

**What we did.** Recorded the ceiling as a device constraint in
`run_hardware_f32.py:59-64`, and refuse an oversized job locally before it is
submitted (`check_free_tier_size`), so the limit surfaces as a sizing decision
at planning time rather than as an HTTP error mid-campaign. The refusal states
the limit it enforced, and a test exercises both the refusal and the boundary
case at exactly the limit.

**Suggested fix.** State the continuous-job variable ceiling in the free-tier
documentation next to the 949 figure, and say which job class each applies to.
One sentence would have saved time.

## 2. The billed-seconds field is not reachable as a dictionary key

**Observed.** `eqc-models` returns a `SolutionResults` object, not a dictionary.
The billed field `device_usage_s` is present in its `repr()` but is not
retrievable by key or attribute access on the returned object.

**Expected.** A billing figure retrievable programmatically, since any metered
workload needs to track spend.

**Why this matters more than it looks.** A caller that cannot read the billing
field has two options, and one of them is dangerous: treat an unreadable
response as zero spend. Do that and a spend cap goes blind exactly when it is
most needed, because the calls it cannot parse are the anomalous ones.

**What we did.** `_metered()` (`run_hardware.py:113-133`) walks the response for
any of five plausible key spellings, then falls back to a regular expression
over `repr(resp)` for `'device_usage_s': N`. When that also fails, the call is
charged a conservative `UNPARSEABLE_CALL_CHARGE_S = 10.0` seconds against the
block cap and the row is flagged for audit (`run_hardware.py:243-249`) --
roughly twice our measured per-call rate, chosen so an unreadable response can
never under-report spend. A property test asserts that a response in an
unrecognised vendor format still charges rather than zeroing
(`test_hardware_guards.py:43`).

**Suggested fix.** Expose `device_usage_s` as an attribute or mapping key on
`SolutionResults`, and keep its name stable.

## 3. Pool construction requires `fork` and fails on Windows

**Observed.** The full-pair weak-learner build uses multiprocessing in a mode
that requires `fork`, which Windows does not provide. The failure appears
during pool construction rather than at import, so it surfaces after setup
work is already done.

**What we did.** Split the workflow: `build` runs inside WSL, writing the
H-matrix to a `.npz`, and `solve` runs on Windows from that file
(`qubo_proxy.py:13-22`). It works, but it means a Windows user cannot run the
pipeline end to end in one environment.

**Suggested fix.** Either select a spawn-compatible start method on platforms
without `fork`, or document the Windows limitation prominently. The current
behavior reads as a bug in the user's setup rather than a platform constraint.

## 4. Measured cost and dispersion, which you may find useful

From 61 metered fits, all `status: ok`, zero failures, zero retries:

| Quantity | Value |
|---|---|
| Total metered device time | 1,141.0 s |
| Fits | 61 |
| Per-call billed time | 4.0 s min, 5.0 s median, 92.0 s max |
| Failures / retries | 0 / 0 |
| Within-fit energy spread | median 0.020%, max 0.343% (48 fits) |
| Hardware objective vs exact minimum | 0.013% to 0.413% above, never below |

Of the 1,141 seconds, 163 ran on the free tier across 37 fits before your
grant and 978 drew against the allocation. The allocation itself shows 1,039
drawn: the extra 61 seconds went to a run we withdrew and re-ran the same
day, after finding its pools were built on more data than the arm it was
quoted against. That run is excluded from the campaign total because its
result is not ours to claim; the seconds were still spent, so they count
against the grant.

Two things worth saying plainly. **The per-call rate is stable and predictable
within a problem size** -- on the free-tier configurations it held a 1-second
spread across 37 calls, and our block caps never came close to firing for the
wrong reason. The 92-second maximum is the 833-variable arm, an order of
magnitude larger problem; the cost tracked size rather than varying at a given
size, which is what makes forecasting practical. **The solver never returned a
solution better than the certified classical optimum**, which is the correct
behavior and is worth having measured by an outside party.

The stochasticity is real but small at this problem size: the within-fit
spread has a median of 0.020% across 48 fits. Near a flat optimum, sampling
variation barely moves the answer.

## 5. The classical proxy, and an ask

We built an exact classical solver for the Hamiltonian `eqc-models` actually
constructs: `J = HH^T + lambda*I`, `C = -2Hy`, sum constraint 1.0, `w >= 0`,
solved by accelerated projected gradient on the simplex (`qubo_proxy.py`).

Because it builds its pools through `eqc-models`' own builders, the problem it
solves is the same problem rather than a reimplementation that has drifted.
That is what let us measure hardware-minus-exact at **-0.0010 AUPRC** with
weight cosine 0.975 to 0.999: without an exact solve of the *same* Hamiltonian,
a device result has nothing to be compared against.

It is yours to use. For QCi it is a regression oracle for CVQBoost changes and
a way for an evaluating customer to size a problem before spending on it. It
also let us build and debug the entire pipeline against the free tier for 163
metered seconds, so that the allocation you granted went to the experiments
that needed hardware rather than to development.

**The ask.** We would value your correction on whether we have read the
Hamiltonian correctly. Our entire fidelity argument rests on that reading, and
you are the only ones who can confirm it.

## 6. Two questions we posed, and what the campaign answered

We listed these as single-fit experiments we would run on approval. The
allocation let us answer the second one properly, and it turned into the most
useful thing we learned about your device.

1. **Would relaxation schedule 4 close the residual?** Still open. Every fit in
   the campaign ran schedule 2, which was frozen in the preregistration before
   the grant, and we did not spend allocation seconds changing a frozen
   protocol variable mid-campaign.

2. **Would a larger sum constraint help?** We suspected the analog resolution
   floor. It is the floor, and the effect is larger than we guessed.

### The 200:1 resolution finding

Your user guide documents an effective analog resolution of about 200:1 (Emami
et al. cite a 23 dB dynamic-range limit). We had never checked our own
Hamiltonians against that number. When we did:

- Across all ten frozen pools, off-diagonal entries differ by at most **20.0**,
  against a resolvable difference of **2,553.5**
  (`device_resolution.json`).
- **No coefficient difference in this problem is visible to the device.**
  Quantized at that resolution, the off-diagonal collapses to a single distinct
  value and the simplex minimizer of what remains is uniform to 2e-15.

This has two consequences we think you will want.

**It explained our 833-variable arm.** With the sum constraint at 1, a diffuse
optimum over 833 learners averages 0.0012 per weight, against a representable
step near 1/200 = 0.005. Not representable, so the device must return something
sparser. Every one of those eleven fits contains exact zeros, with printed
nonzero weights from 0.0007 to 0.0029 -- all below the resolution. The weight
cosine of 0.83 measures a device solving a sparsified version of the problem it
was given, not a device failing to solve the problem.

**In one sentence: we asked the device to spread weight across 833 learners, it
could only represent about 200, so it picked a subset instead -- and that
subset was our best result at scale, gaining +0.0256 AUPRC on ten of ten
seeds.** We are not reporting this as a limitation we worked around. The device
answered a sparse-selection problem we had not meant to ask, and the answer was
better than the one we did ask for. That is the whole reason Phase 2 asks it
deliberately.

**It corrected a claim of ours that was backwards.** We had written that
hardware agreeing with the classical proxy bounded any resolution effect. It
does not: the agreement *is* a resolution effect, and carries no information
about solver fidelity on that pool. We withdrew the claim as a dated
preregistration amendment (A31) and pinned both halves with tests. An external
reviewer found it by reading our mechanism paragraph against your
specification, which is a check we had never run against any claim in the
submission.

**Why we think this is a result about the device rather than a limitation of
it.** A machine that cannot represent diffuse weight over more than about two
hundred learners is not a machine that is bad at this problem. It is a machine
whose native problem is sparse selection under a cardinality constraint, which
is NP-hard and is exactly what your integer mode is for. That is the Phase 2
formulation, and it now follows from your device's documented physics rather
than from our preference.

## A note on what this is not

We are not reporting a defect in the device. Solver fidelity was excellent
throughout, and where our results are weak the cause was our own pool
construction, which we describe in the accompanying proposal. These are
integration findings: the places where the library's behavior and its
documentation diverge, and where a careful user can lose a day.
