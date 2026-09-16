# What CVQBoost is, and what "CV" stands for

Research run 2026-09-16, prompted by the team lead during Sprint 15 Manual
Validation: *"CVQBoost is explained by QCi. QBoost stands for Quantum Boosting,
an algorithm described in prior papers and a published open source algorithm. CV
stands for 2 words and is the difference between CVQBoost and QBoost."*

The team lead was right on every count that could be checked. One part could not
be verified from any primary source, and that is recorded here rather than
papered over.

## Short answer

| Question | Answer | Status |
|---|---|---|
| What distinguishes CVQBoost from QBoost? | QBoost uses BINARY weights (each weak learner in or out); CVQBoost uses CONTINUOUS positive weights summing to 1 | **VERIFIED**, quoted below |
| What does CV stand for? | Almost certainly "continuous variable" | **NOT VERIFIED.** No primary source expands it |
| Is it open source? | Yes, Apache-2.0, two locations | **VERIFIED** |
| Who wrote QBoost? | Neven et al., 2012 | **VERIFIED** via citation |

## The difference, verified

From arXiv:2503.11273 (Emami, Dyk, Haycraft, Spear, Nguyen, Chancellor;
submitted 14 March 2025), section 2.2, quoted exactly:

> "Note that this is similar to the formulation in the QBoost (Neven et al.,
> 2012) algorithm. The key difference is that we do not need to encode the
> weights into binary variables since the Dirac machine we use is based on a
> native continuum encoding."

And section 2.1, on what the device solves:

> "w_i are continuous variables subject to w_i > 0 and an overall sum constraint
> sum w_i = 1."

**The constraint comes from the hardware, not from a design choice.** Weights are
forced onto the unit simplex because that is the only mode Dirac-3 offers. A
consequence worth noting: the weights are determined only up to overall scale.

A second, smaller difference: CVQBoost regularizes with an L2 term while QCi's
QBoost formulation page uses an L0 sparsity count.

## What "CV" stands for: NOT ESTABLISHED

Checked, and no expansion found in any of:

- arXiv:2503.11273 full text. The name appears **84 times** and is never expanded
- the arXiv HTML version
- QCi's `eqc-models` package source, v0.21.0, across every `.py`, `.pyx`, `.c`, `.h`
- QCi's QBoost formulation doc and entropy-quantum-optimization index
- the GitHub study README and the PyPI package description

**The strongest available evidence** is adjacency. The paper's introduction
writes:

> "we further extend this concept to CVQBoost, an algorithm which can naturally
> be applied to the Dirac optical computing hardware ... which encodes into
> continuous variables."

Plus QCi's own filenames: `eqc_models/ml/cvqboost_hamiltonian.pyx`.

So "Continuous Variable QBoost" is the near-certain reading. It remains an
inference.

**A warning worth recording**: web search summaries assert "CVQBoost (Continuous
Variable QBoost)" confidently, and that assertion could not be traced to any
source document. This is the plausible-wrong-result class. A confident secondary
source is not a primary source.

**What would settle it**: the peer-reviewed Springer version
(10.1007/978-981-95-7829-0_18, behind an auth redirect), the OpenReview
discussion (browser-verification wall), or a QCi webinar or press release.

## Open source, verified

- **Study code**: `github.com/qci-github/eqc-studies/tree/main/CVQBoost`,
  Apache-2.0, named in the paper's acknowledgments for reproducibility
- **The implementation**: ships in QCi's `eqc-models` PyPI package (v0.21.0,
  released 2026-08-13)

**A naming trap.** The shipped class is called `QBoostClassifier`, NOT CVQBoost:
`from eqc_models.ml.classifierqboost import QBoostClassifier`. QCi's own code
calls the continuous-variable algorithm "QBoost"; the name CVQBoost survives only
in filenames. Anyone reading the code expecting a `CVQBoost` class will not find
one.

The code was checked against the paper: `get_hamiltonian` computes `J = h·hᵀ +
λI` and `C = -2 h·y`, matching the paper's equations 5 and 6, and returns a
trailing `1.0` which is the simplex sum constraint. That is confirmation from
running code, not only from prose.

## What could not be established

1. **The literal expansion of "CV"**, as above.
2. The Springer version's abstract and keywords: auth redirect.
3. The OpenReview reviewer discussion: browser-verification wall.
4. QCi's "Profiling of CVQBoost Algorithm: Fraud Detection" page body: JavaScript
   rendered, returned only a title.
5. Whether Neven et al. 2012 itself used a sum constraint. The binary-weight
   claim was verified from QCi's restatement, not from the Neven paper directly.

## Note on authorship

The arXiv version lists Emami, Dyk, Haycraft, Spear, Nguyen and Chancellor. The
GitHub README lists an additional author, Raouf Dridi, who is not on the arXiv
version.

## How this was used

`docs/explainer/THE_SUBMISSION_EXPLAINED.md` section 5 now explains the QBoost
lineage and the binary-versus-continuous difference, and states explicitly that
the CV expansion is an inference rather than a sourced fact. The document also
points out that continuous weights are the one thing CVQBoost adds over its
predecessor, and that this project measured that addition contributing +0.0047,
below what the design could resolve.
