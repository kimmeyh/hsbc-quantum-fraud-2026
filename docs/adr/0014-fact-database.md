# ADR-0014: Fact database — storage, schema and repository boundary

## Status

**Proposed.** Awaiting team-lead acceptance or rejection. **No implementation is
authorised by this document**; F39 is investigation and design only.

## Date

2026-09-12

## Context

### The problem, in the project's own evidence

The same fact is restated across many documents with nothing linking the copies.
Every instance below is a real defect this project shipped or nearly shipped:

| Defect | What happened |
|---|---|
| **A15** | `0.7688` quoted in four places as the frozen pool's AUPRC at k=6. It appears in **no artifact** — the mean of an exploratory five-seed run carried into a ten-seed write-up. It was carrying a claim the true value inverts |
| **Sprint 8** | The QCi letter asserted "twelve amendments" while the enclosed preregistration had seventeen |
| **A19** | The amendment count changed and had to be corrected in every document that named it |
| **F52** | B1's variable count read **78** in three places and **91** in two, in the same submission |
| **Sprint 13** | `summarize_b2.py` wrote "78 vars" into the shipped evidence artifact, which A24 had already corrected in prose |
| **Sprint 13** | Appendix A.5 quoted `0.5739`, a real number from a different file, in a sentence about fold 0 whose real value is `0.5424` |

Each was caught by a human reading, or by a script written for that one check.

### Why the existing controls do not close it

`test_document_figures_resolve.py` (F44) already does the cheap half: every
number in the three documents must resolve to a stored value or be registered
with a reason. It carries **66 registered exemptions** and it works.

Its own docstring states the gap, and Sprint 13 then demonstrated it exactly:

> It does NOT catch a figure that exists in the store but is quoted in the wrong
> place.

That is the `0.5739` defect. Both numbers are real, so a global value-set lookup
accepts either anywhere. **Closing it needs per-claim provenance — this sentence
cites THAT row — which is what a fact database is.**

### The second and third record classes

The team lead has added vocabulary to the scope, and it is not decoration.
Guidelines §8 says a non-specialist reviewer must be able to follow the
technical approach, and §6 puts technical reviewers and enterprise
representatives on the same panel. A maintained glossary at a defined reading
level is the mechanism for that, and it becomes more valuable in Phase 2 when
the audience widens again.

### Scale, measured 2026-09-12 rather than estimated

An inventory of the three submitted documents, verified against them:

| Record class | Submitted package | Proposal only | All five documents |
|---|---|---|---|
| Acronyms | 57 | 43 | 94 |
| Technical terms | 126 | 108 | ~143 |
| **Glossary total** | **183** | **151** | **~237** |

Plus the assertion class: 168 result rows over 30 distinct keys, 66 registered
figure exemptions, and 32 amendments.

**Two findings from the inventory change the scope.**

**First, seven acronyms I had assumed were in scope are not in the submitted
package at all** -- QUBO, QPU, QFE, EQC, SHAP, ADR and T&C appear only in the
preregistration or the requirements matrix. Verified by grep, zero hits across
all three documents. Scoping the glossary to what a judge actually reads is a
real reduction, not a rounding.

**Second, 85% of the glossary burden sits in the proposal**: 43 of 57 acronyms
and 108 of 126 terms. The appendix adds almost no new vocabulary, only new
instances of the same vocabulary. Its 32 unique entries are the statistical
machinery -- BCa, Spearman, permutation p, seed SD, free-sign logistic stack --
which are simultaneously the hardest to simplify and the least likely to be
read first.

**Therefore: the 8th-grade target applies to the PROPOSAL set (151 records), and
the appendix-only statistical tail is allowed a higher register.** That is a
scope decision the inventory earned, and it makes the reading-level commitment
honest rather than aspirational.

## Decision

### 1. It starts OUTSIDE this repository

Team-lead direction, 2026-09-12. A separate repository, with this project as its
**first consumer rather than its owner**. Some or all may be brought in later as
a separate decision on the evidence.

Three reasons this is right rather than merely instructed:

- This repository is a **submitted, judged artifact**. Its history is frozen and
  its hooks refuse rewrites. A tool under active design does not belong inside
  something that must not churn.
- The glossary is **reusable across projects**; the fraud submission is one use.
- If it fails, it fails **somewhere that does not touch the evidence record**.

**Boundary status: PROVISIONAL.** Revisit once there is a working store and real
usage, not before.

### 2. Storage: SQLite, with a text export committed alongside

**SQLite** as the store of record. **A deterministic text export** (JSON or
Markdown per record class) regenerated from it and committed, so:

- the store is queryable, transactional and enforces a schema;
- the **diff is reviewable** — a fact changing value shows up in review, which is
  the entire point given that the defects above were all silent;
- a consumer needs no database to read a fact, only the export.

The export is generated, never hand-edited. This is the same shape as
`b2_hardware.json` regenerating from `results.json`, which this project already
relies on.

### 3. Three record classes, one schema spine

Every record, regardless of class, carries:

| Field | Meaning |
|---|---|
| `id` | Stable, human-readable. Documents cite this, not the value |
| `class` | `assertion` \| `acronym` \| `term` |
| `value` | The number, the expansion, or the definition |
| `provenance` | Pointer to what establishes it: a `results.json` row + config hash, an artifact path, an amendment, an external citation |
| `evidence_tag` | `HW` \| `SIM` \| `PROJ` \| `N/A` — reuses the existing vocabulary rather than inventing one |
| `confidence` | 0.0 to 99.9 percent (Cyc-derived; see below) |
| `fidelity` | `exact` \| `scoped` \| `consequence` -- how faithful the plain definition is. See section 5 |
| `updated` | Date, and the amendment or issue that moved it |

Class-specific fields:

- **`assertion`**: `units`, `rounding`, and the `documents` that cite it.
- **`acronym`**: `expansion`, `plain_definition` (8th-grade), `visual` (link to
  an image or short animation where one genuinely helps).
- **`term`**: `plain_definition` (1–3 sentences, 8th-grade), `visual`,
  `see_also`.

**Cyc-derived scoring fields are carried on every class from the start**, even
where unused today, so the schema does not need widening later. The one that
earns its place immediately is `confidence`: this project already separates
measured from projected via evidence tags, but **not strong-measured from
weak-measured**. The score-degeneracy caveat, the single-seed spot checks, and
the adversarial control that never converged are asserted with genuinely
different confidence, and today that lives only in prose.

### 4. Citation and validation

Documents cite by id — concrete syntax deferred to implementation, since it must
survive pandoc to PDF and that constraint is empirical. A build step resolves
every citation and **fails on an unresolved or stale one**. This is the
mechanism that would have caught A15, the amendment-count drift, and the 78/91
split.

### 5. The reading-level target is a constraint, and a `fidelity` field keeps it honest

`plain_definition` targets 8th-grade math, science and English for the proposal
set. The inventory tested this by writing sample definitions, and the target is
achievable for the large majority -- the pattern that works is: say what the
thing does or answers, then anchor it with one real number from our own results,
and never define jargon with more jargon.

**But it is NOT achievable for every term without distorting the meaning, and
the schema must admit that rather than paper over it.** Every record carries a
`fidelity` field:

| Value | Meaning |
|---|---|
| `exact` | The plain definition is simply correct |
| `scoped` | True for THIS paper's usage; would be wrong as a general definition |
| `consequence` | States what the term implies for our result, not what it means |

Seven terms were identified where a naive simplification would be actively
false, and they are the ones a careful reader would catch:

- **convex** -- "bowl-shaped, one lowest point" is wrong in 833 dimensions where
  the minimiser set is a flat face, which is exactly what our own appendix says.
  The easy gloss contradicts the document.
- **simplex** -- "weights sum to 1" is right but cannot reach "the minimiser set
  is a face of the simplex", which is the load-bearing use.
- **split dispersion, not sampling error** -- the whole point is that the
  interval does NOT mean what a reader assumes. A friendly paraphrase destroys
  the honesty this phrase exists to provide.
- **BCa interval** -- there is no honest 8th-grade rendering of "accelerated".
- **rank-one to numerical precision** -- eigenvalues have no 8th-grade handle;
  only the consequence is expressible.
- **effective analog resolution / 23 dB** -- 200:1 simplifies; decibels do not.
- **step-wise average precision** -- calling it "the standard way" erases a
  deliberate methodological commitment.

This matters beyond tidiness. The submission's credibility rests on not
overclaiming, and a glossary that quietly overclaims about its own definitions
would undercut the thing it is meant to support.

## Alternatives considered

### Extend the F44 registry in place
- **Description**: grow the `REGISTERED` dict in `test_document_figures_resolve.py` into the fact store.
- **Pros**: zero new infrastructure; already works; already in CI.
- **Cons**: it is a Python literal in a test file. No provenance, no confidence, no vocabulary classes, and it cannot express "this sentence cites that row" — the exact gap. It would also put a growing data structure inside a frozen repository.
- **Why rejected**: it solves the half already solved and cannot reach the half that matters.

### Plain JSON or YAML files, no database
- **Description**: one file per class, hand-edited, validated by a script.
- **Pros**: no dependency; trivially diffable; no export step.
- **Cons**: no referential integrity, no query, and hand-editing a thousand records invites exactly the drift the store exists to prevent.
- **Why rejected**: at ~1,000 records the failure mode returns in a new place. Kept as the **export format**, which is where its diffability is worth having.

### A real Cyc or an ontology engine
- **Description**: adopt Cyc, or an RDF/OWL triple store.
- **Pros**: genuine inference; the confidence model is native.
- **Cons**: enormously heavier than the problem. The team lead's own framing was "functionally representative, NOT a LISP reimplementation".
- **Why rejected**: we need provenance and a confidence field, not a reasoner.

### Do nothing; keep verifying by hand
- **Description**: continue as Sprints 8 through 13 did.
- **Pros**: no build cost.
- **Cons**: it has failed six times on record, and the last one reached a judge-facing document.
- **Why rejected**: the failure rate is the argument.

## Consequences

### Positive
- The `0.5739` defect class becomes detectable rather than luck-dependent.
- Confidence becomes explicit and reviewable instead of living in prose.
- The glossary serves the non-specialist reviewer the Guidelines describe.
- Built outside, it cannot destabilise a submitted artifact.

### Negative
- A cross-repository dependency, which is a real cost and the reason the
  boundary is provisional.
- Citation-by-id makes documents less readable in raw Markdown.
- ~1,000 records is genuine authorship, and the glossary half especially.
- **A fact database can be confidently wrong.** It centralises the value and
  therefore centralises the error. The provenance field is what keeps it
  checkable; a record without one is worse than no record.

### Neutral
- The export is another generated artifact, on the pattern already in use.

## Preregistration touchpoints

Section 11 (analysis-code and results-store rules) governs how results rows are
written; this ADR consumes those rows and changes nothing about them. The
preregistration governs methodology; this is an engineering decision around it.
**No amendment is required to adopt this ADR.**

## Open questions for the team lead

1. **Repository name and visibility.** Public makes citations resolvable for a
   reader of this public repository; private keeps an unfinished tool private.
   Recommendation: **public once it holds anything worth citing**, private
   before that.
2. **Does the glossary ship?** It could be a repository asset only, or become a
   Phase 2 submission appendix. That changes the register and the review bar.
3. **Who authors the 151 proposal-set definitions**, and at what pace? Measured,
   not estimated, and materially smaller than the "over 1,000" working figure
   once scoped to the submitted documents. It remains the largest single cost
   here.

## References

- F39 (this card), F44 (`test_document_figures_resolve.py`), F72 (reference
  library, gated on this storage decision)
- Amendments A15, A19, A24; findings F52, and the Sprint 13 evidence walk
- `docs/sprints/SPRINT_13_SUMMARY.md`, `docs/sprints/SPRINT_8_RETROSPECTIVE.md`
- Cycorp (cyc.com), for the confidence-scoring idea only
