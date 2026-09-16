---
title: "eqc-models and Dirac-3: Integration Feedback"
subtitle: "From 37 metered fits and a sustained proxy build, September 2026"
date: "September 2026"
---

# Integration feedback for QCi

This is the package promised in our access request. It covers what we found
building against `eqc-models` 0.21.0 and `qci-client` 5.0.2 over five weeks,
across 37 metered Dirac-3 fits and several thousand classical solves of the
same Hamiltonian.

Every item states what we observed, what we expected, and what we did about it.
Each cites the file and line, or the results row, that establishes it, so you
can check any claim rather than take our word for it. Line references are to
the repository accompanying our submission.

Nothing here is a complaint. The device did what it said it would do on every
one of those 37 calls, with zero failures and zero retries. These are the
places where a competent user loses time, which is the part we can usefully
tell you about.

## 1. The free-tier variable ceiling is undocumented and differs from the
##    documented limit

**Observed.** A 312-variable continuous degree-2 job was refused server-side,
before billing, with:

> Number of variables '312' in problem is greater than the free-tier device
> limit '100'

**Expected.** The documented limit we could find is 949, described as a sum over
`num_levels`. We had sized our experiment against that number.

**The divergence.** The 949 figure applies to integer-encoded jobs. It does not
bind a continuous, sum-constrained run, which is instead capped at 100
variables on the free tier. Both limits are real; they apply to different job
classes, and only one of them is documented.

**Cost to us.** This was found empirically, by a rejected job, after the
experiment had been designed. It forced a preregistration amendment (A12) and
a reduction from k=13 to k=6 features, which is four families at 60 variables.
Every scaling statement we can currently make is bounded by a tier limit rather
than by the device.

**What we did.** Recorded the ceiling as a device constraint in
`run_hardware_f32.py:59-64`, and added a property test pinning the rejection
message so a future change surfaces as a test failure rather than a mystery
(`test_hardware_guards.py:68`).

**Suggested fix.** State the continuous-job variable ceiling in the free-tier
documentation next to the 949 figure, and say which job class each applies to.
One sentence would have saved us a redesign.

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
`SolutionResults`, and keep its name stable. Parsing a `repr()` is not a
contract either of us should rely on.

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

From 37 metered fits, all `status: ok`, zero failures, zero retries:

| Quantity | Value |
|---|---|
| Total metered device time | 163.0 s |
| Per-call billed time | 4.0 s min, 4.0 s median, 5.0 s max |
| Failures / retries | 0 / 0 |
| Identical draws across 8 samples | 0 of 27 fits |
| Within-fit energy spread | median 0.019%, max 0.343% |
| Hardware objective vs exact minimum | 0.013% to 0.413% above, never below |

Two things worth saying plainly. **The per-call rate is remarkably stable** --
a 1-second spread across 37 calls made budget forecasting straightforward, and
our block caps never came close to firing for the wrong reason. **The solver
never returned a solution better than the certified classical optimum**, which
is the correct behavior and is worth having measured by an outside party.

The stochasticity is real but small at this problem size: no fit returned
identical energies across its eight samples, yet the within-fit spread has a
median of 0.019%. Near a flat optimum, sampling variation barely moves the
answer.

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
also let us develop against the free tier while spending 163 metered seconds in
total.

**The ask.** We would value your correction on whether we have read the
Hamiltonian correctly. Our entire fidelity argument rests on that reading, and
you are the only ones who can confirm it.

## 6. Two questions we would run on approval

Both are single-fit experiments.

1. **Would relaxation schedule 4 close the residual?** We see hardware
   objective values 0.013% to 0.413% above the exact minimum on schedule 2.
2. **Would a larger sum constraint help?** Spreading 1.0 across 91 variables
   puts each weight near 0.011, which may approach the analog resolution floor.

## A note on what this is not

We are not reporting a defect in the device. Solver fidelity was excellent
throughout, and where our results are weak the cause was our own pool
construction, which we describe in the accompanying proposal. These are
integration findings: the places where the library's behavior and its
documentation diverge, and where a careful user can lose a day.
