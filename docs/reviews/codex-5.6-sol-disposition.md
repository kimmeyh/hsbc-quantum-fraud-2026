# External review disposition: Codex 5.6 "Sol"

Received 2026-09-04, during Sprint 5 manual validation. 30 ranked findings.

Standing rule: we incorporate what improves the package. We do not accept a
finding because a reviewer asserted it, and we record where a reviewer is wrong.

## Already fixed before this review arrived

| # | Finding | Status |
|---|---|---|
| 1 | Proposal pages are 11x17 | FIXED. Word set PaperSize after opening the docx; the render is LaTeX-only now and verifies size AND count. All 9 PDFs are 612x792pt US Letter, proposal 6/6, appendix 3/3, team profile 1/1. The reviewer read a stale PDF. |
| 2 | Team profile lacks affiliation and lead contact | FIXED. Full legal name, "independent researcher (unaffiliated)", email, phone, LinkedIn. |

Both were real. Both were caught here first. No further action.

## Accepted: the reviewer found a genuine error in our data

### 13. "Exactly uniform" contradicts the AP difference (ACCEPTED, with a
### correction the reviewer did not reach)

The reviewer is right that the claim is false, and right that it is internally
inconsistent. We wrote "exactly uniform", "sits at 1/91 on every learner", and
"L1 distance 0.000000". The stored value is **8.0e-08** (range 7.2e-08 to
1.6e-07 over ten seeds). We printed six decimals, read "0.000000", and wrote
"exactly". That is our error, not a rounding convention.

The reviewer's proposed CAUSE is wrong, however. They suggest "rounding,
learner-order misalignment, different scoring code or another pipeline
difference" and ask for a reconstruction experiment. We ran the check directly
(seed 42):

- uniform weights produce **78 distinct scores** over 56,746 rows
- solved weights produce **151 distinct scores**
- AP uniform 0.804889, AP solved 0.807255, difference 0.002366
- rounding the solved scores to 6 decimals returns AP to 0.804312

The mechanism is **tie-breaking**, not a pipeline defect. 95.3% of test rows
share one score under uniform weights. Weight perturbations of order 1e-7 split
those ties. Average precision is rank-based, so it moves. The entire +0.0022 is
an artifact of tie-breaking among transactions the model cannot distinguish.

This STRENGTHENS our conclusion rather than weakening it. We previously said
optimization contributes +0.0022, an order of magnitude below the MDE. The
correct statement is that it contributes **nothing at all**, and the residual is
noise from splitting ties. Both documents updated.

### 7. The 2026 Loke et al. CVQBoost fraud study is missing (ACCEPTED, highest
### value finding in the review)

Verified: Loke, Sahoo, Guan, Xu, Verma, Griffin, "Improving credit card
transaction fraud detection using CVQBoosting", ICAART 2026, Marbella, 5-7 March
2026. Singapore Management University.
https://ink.library.smu.edu.sg/sis_research/11008/

Same hardware (Dirac-3), same algorithm (CVQBoost), same dataset family (Kaggle
credit card). Weak learners: **KNN, linear discriminant analysis, logistic
regression, XGBoost**. Reported mean AUC-PR above 0.8.

This is the closest prior work in existence and we did not cite it. Worse for us,
and better for the argument: their pool is heterogeneous where ours is 91
depth-limited decision trees. Their result is independent external evidence for
our own degeneracy diagnosis, and it makes the Phase 2 direction concrete rather
than speculative. Added to the proposal and appendix.

### 30. Duplicated sentence (ACCEPTED)

Verified: the 0.5% budget figures appear twice back to back in section 3.
Removed.

### 17. Exact software versions missing (ACCEPTED)

Recorded: Python 3.12.10, eqc-models 0.21.0, qci-client 5.0.2, scikit-learn
1.9.0, numpy 1.26.4, scipy 1.17.1, xgboost 3.4.1, catboost 1.2.10, lightgbm
4.7.0. Note the reviewer guessed 0.20.2 from PyPI; the actual pinned version is
0.21.0.

### 8. Dirac-3 called "quantum-inspired" (ACCEPTED)

Correct and we were inconsistent with ourselves. Section 2 said "entropy quantum
computing hardware" in one sentence and "quantum-inspired solver" in the next.
QCi's hardware paper (arXiv:2407.04512) describes a hybrid photonic-electronic
entropy quantum computer. Paradigm is now stated as hybrid classical-quantum,
with the advantage question left open. This is a terminology fix, not a claim
upgrade.

### 21. Top-k description is wrong (ACCEPTED)

We wrote "only the 0.5% column measures ranking rather than budget". Every
recall@k column is a ranking measure under a budget; the 0.5% column is simply
not capped by the positive count. Corrected.

### 6, 10, 11, 3. Overstated claims (ACCEPTED, narrowed)

- "The formulation where quantum optimization is necessary": NP-hardness does
  not establish necessity or advantage. Retitled and narrowed.
- Braket arm "specified": it is named, not specified. Narrowed to a
  conditional Phase 2 candidate gated on a classical feasibility screen.
- Router "specified rather than speculative": no segment is shown where
  CVQBoost beats the champion. Restated as a Phase 2 hypothesis with an
  acceptance criterion.
- "Deploy today" / "production detector": the ULB PCA transform is not
  published, so no ULB-fitted model maps onto bank traffic. Restated as
  benchmark champion with the onboarding work named.

### 16. Multiplicity rationale (ACCEPTED)

"Not yet applicable: exploratory family incomplete" is not a correct rationale.
H1b is the sole confirmatory endpoint and is reported unadjusted; everything
else is exploratory. Restated.

### 23, 25, 15, 28, 27. Overstatements (ACCEPTED, small edits)

- AUPRC > 0.95 is a tripwire, not evidence of leakage.
- Exact additive decomposition over anonymized PCA components is an audit
  decomposition, not a business-meaningful explanation.
- Equality Act and Consumer Duty do not mandate a named disparate-impact test;
  disparity testing is our proposed control.
- AutoXGB 0.782 is an illustrative external number, not like-for-like.
- Drift and label-delay timings vary by portfolio; stated as such.

### 18. "Exact" without a certificate (ACCEPTED, partially)

Reserving "exact" for a symbolic solution is the stricter convention and we
adopt it: "high-accuracy numerical solution" with the tolerance stated. The
underlying claim (strict convexity, unique minimizer for positive
regularization) is correct and the reviewer agrees.

### 5, 22. Overlapping-resplit inference (ACCEPTED, already partly stated)

We already labelled these "split dispersion, not sampling error". The reviewer
is right that we then used a sign test across the same overlapping seeds and
called p=0.021 support. Both documents now say the seed-level sign test and the
interval are descriptive.

## Rejected or already correct

### 14. Class weighting does not rule out imbalance effects (PARTIALLY REJECTED)

The reviewer says our class-weighted control does not rule out imbalance
effects during LEARNER FITTING, only in the final objective. That distinction is
correct and we adopt the narrower wording. But the reviewer frames it as an
error in the conclusion, and it is not: we independently measured the Gram
matrix (off-diagonal 170,234.4 vs diagonal 170,235), which is a DIRECT
measurement of pool degeneracy at the learner level, not an inference from the
objective. The conclusion stands on that measurement. Wording narrowed;
conclusion unchanged.

### 19. Dirac-3 continuous resolution (REJECTED as stated, noted as a limitation)

The reviewer computes a resolution of ~0.005 against a mean weight of ~0.011 and
suggests quantization could explain the near-uniform result. Our measured data
contradicts this: hardware weights agree with the classical solution to cosine
0.975-0.999, and hardware objective values sit 0.013%-0.413% ABOVE the exact
minimum. If quantization to ~2 increments were driving the result, that
agreement could not hold. The classical proxy also reproduces the flat optimum
with no quantization at all. Retained as a stated hardware characteristic worth
testing in Phase 2, not adopted as an explanation.

### 20, 24, 26. Experiments requiring metered time or substantial runs (DEFERRED)

Hardware prediction persistence, per-cutoff tie analysis, and latency
percentiles are all legitimate. They need QPU seconds or hours of runs that the
remaining schedule does not hold. The proposal already says operating points are
[SIM] and stay [SIM] until a hardware run persists predictions. Registered as
backlog, named in the Phase 2 plan.

### 29. Retag [SIM] as [CLASSICAL] (REJECTED)

The tag vocabulary is fixed in the FROZEN preregistration. Renaming tags
post hoc across a preregistered document to satisfy a style preference is
exactly the kind of change the freeze exists to prevent, and it would invalidate
the tag on every historical results row. The appendix already defines what each
tag means. "QPU seconds" is replaced with "metered device seconds", which is a
wording fix that touches no tag.

### 4, 12. Repository URL and resource plan (ACCEPTED where true)

The repository is currently private and becomes public at submission; the
proposal cannot cite a working URL until then. Version pins, dataset checksum
and job-manifest description added. A compact resource line added to Phase 2.
Full costed resource table does not fit the 6-page limit and is not required by
section 4.3.

## Two things the reviewer got wrong about the submission

1. Findings 1 and 2 describe defects already fixed. The reviewer was working
   from PDFs generated before the fix.
2. Finding 13's diagnosis ("rounding, learner-order misalignment, different
   scoring code") is not the cause. It is tie-breaking, which we measured.

Both are recorded because a disposition that only lists agreements is not a
disposition.

## Note on citing Loke et al.

The team lead has spoken with Paul R. Griffin and another author. **They have
not agreed to be named beyond the citation**, so nothing in the package claims
contact, input, endorsement or collaboration. The published work is cited as
published work, which needs no permission.

Do not add a "we have been in contact with the authors" sentence unless they
agree in writing. A judge may verify it, sponsors have access to submissions,
and the team lead is responsible for every claim in the entry.
