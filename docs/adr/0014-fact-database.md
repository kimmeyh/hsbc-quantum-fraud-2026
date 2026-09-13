# ADR-0014: Evidence Based DB — storage, schema and repository boundary

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
cites THAT row — which is what an evidence base is.**

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

### 0. It is called the Evidence Based DB, and it is PRIVATE for now

**Team lead, 2026-09-13.** Name: **Evidence Based DB**. Repository:
**`EvidenceBasedDB`**. Visibility: **private**.

The name was chosen over "fact database", which this project had used since
Sprint 8, and the reason is this repository's own record. `0.7688` appeared in
four documents and was not a fact. The unconverged solver produced figures that
were not facts. A store called a *fact* database asserts the very property it
exists to check; "evidence base" is the term whose established usage -- graded
findings, quality levels attached, revision expected -- matches what this
actually holds. It also reuses vocabulary already in the project, since
`[HW]`/`[SIM]`/`[PROJ]` are *evidence* tags.

**Superseded 2026-09-13:** the CARD is renamed too. F39 is the Evidence Based
Database card everywhere it is live. CHANGELOG entries keep their original
wording, because rewriting a dated record is the retroactive edit this project
now forbids.

**PRIVATE HAS A CONSEQUENCE, stated here so it is a decision and not a
surprise.** This repository is public and judged. While `EvidenceBasedDB` is
private, **no citation from this repository may depend on it resolving** -- a
reader following a pointer into a private repository gets a 404, which is the
dangling-reference defect this project keeps finding, in a new place.

So for as long as it is private, the rule in section 5 is not a preference but a
constraint: citations carry their claim and provenance inline, and the library id
is an identifier for someone who already has access. Revisit if and when it
goes public.

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
| `fidelity` | `exact` \| `scoped` \| `consequence` -- how FAITHFUL the definition is. See section 5 |
| `reading_level` | US grade level the definition actually achieves, 8 to 20. How HARD it is. See section 5 |
| `prerequisites` | Ids of records a reader needs first. The escalation ladder's rungs |
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

### 5. Reading level ESCALATES one grade at a time, and the target is a path not a term

**Team lead, 2026-09-12.** Start every definition at 8th grade. Where an honest
definition is not achievable at that level, go up ONE grade and try again.
Repeat until it is achievable. Record the level that worked.

**The ceiling is PhD (grade 20), and reaching it is not a failure.** The purpose
is that a reader can follow along and grow what they understand: if everything
AROUND a hard term is explained lower, almost all of it is understandable well
before the hard term, and the hard term becomes reachable rather than a wall.

Grades 13 to 16 are college freshman through senior and are **acceptable, not
deficient** -- a motivated reader reaches them. The level that warrants attention
is **postgraduate, 17 and above**, and specifically a CLUSTER of it: that is
where a reader cannot climb without prior specialist training, which is the one
case the ladder cannot fix.

That reframing matters more than it first appears. Reading level is a property
of a **path**, not of a term in isolation. A grade-11 term sitting in grade-9
surroundings is climbable. The same term surrounded by other grade-11 terms is
not. **This is why `prerequisites` is part of the schema and not a nicety**: it
records the rungs, so the ladder can be checked for gaps rather than assumed.

#### The escalation, worked on the terms that failed at 8

Tested rather than asserted. The earlier draft of this ADR declared seven terms
unachievable; escalation rescues most of them.

| Term | 8 | 9 | 10 | 11 | Achieved |
|---|---|---|---|---|---|
| convex | NO | **yes** | | | **9** |
| BCa interval | NO | **yes** | | | **9** |
| simplex | NO | **yes** | | | **9** |
| split dispersion, not sampling error | NO | **yes** | | | **9** |
| step-wise average precision | NO | | **yes** | | **10** |
| effective analog resolution (200:1) | **yes** | | | | **8** |
| 23 dB dynamic range | NO | NO | NO | **yes** | **11** |
| rank-one to numerical precision | NO | NO | NO | **yes** | **11** |

**"Convex" is the case that proves the rule.** At 8th grade the natural gloss is
"bowl-shaped, so there is one lowest point" -- which CONTRADICTS our own appendix,
where the minimiser set is a face of the simplex, a flat region rather than a
point. At 9th grade it works: *"The problem has no false bottoms. Any lowest
point you find is genuinely the lowest, so there is no risk of getting stuck
somewhere that only looks best."* That drops the false uniqueness and keeps the
property that actually matters -- it is why a classical solve is a valid check on
the device.

A flat `fidelity: consequence` would have written that term off. One grade of
escalation recovered an honest definition. **The measured failure is worth more
than the binary one**, and the earlier draft was simply wrong to give up.

#### The distribution is itself a finding

Grade levels across the glossary say something about the submission that no
individual entry does: a cluster of grade-13-and-above terms in one section is
evidence that the SECTION is over-jargoned, not merely that its vocabulary is
hard. That is a document-quality signal, available for free once the field
exists, and it is worth watching in Phase 2 where the audience widens.

#### `fidelity` and `reading_level` are different axes, and both are kept

- `reading_level` answers **how hard**.
- `fidelity` answers **how faithful**.

They are independent. "Hamiltonian" reaches 8th grade comfortably and is still
`scoped`: the definition is true for this paper's usage -- a table of costs the
machine minimises -- and would be wrong as a general physics definition. A
physics-literate judge must not read it as an error, so the record says so.

Keeping only one of the two fields would lose real information either way.

#### Why this survives contact with the project's standards

The submission's credibility rests on not overclaiming. A glossary that quietly
overclaimed about its own definitions -- shipping a comfortable falsehood because
the honest version was harder -- would undercut the thing it exists to support.
Escalation is what makes the honest version reachable instead of abandoned.

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

1. ~~Repository name and visibility.~~ **DECIDED 2026-09-13**: named
   **Evidence Based DB**, repository `EvidenceBasedDB`, **private for now**. See
   section 0, including the citation constraint that privacy imposes.
2. ~~Does the glossary ship?~~ **DECIDED 2026-09-13: INTERNAL for now.** A
   repository asset, not a submission appendix. Consequence: the review bar is
   ours rather than a judge's, so entries may be drafted and improved in place
   instead of needing to be right before they appear. Revisit for Phase 2, where
   a glossary is a plausible appendix and the audience widens.
3. ~~Who authors the 151 proposal-set definitions?~~ **DECIDED 2026-09-13:
   source them from existing dictionaries and references wherever possible, and
   Claude drafts the rest for the team lead to review.**

   This changes the cost materially. Most of the 43 acronyms have standard
   expansions that need no invention -- AUPRC, GBDT, PCA, KNN, LDA are defined
   in any ML reference. The work concentrates in two places: terms this project
   uses in a SCOPED sense (see `fidelity`), where a general dictionary
   definition would be wrong for our usage, and the grade-11-and-above tail
   where no source writes at that level.

   **A sourced definition carries its source in `provenance`, exactly like an
   asserted number.** A definition with no source and no author is the same
   defect class as a figure with no artifact.
4. ~~Is a grade-13-or-higher cluster a trigger to revise the document?~~
   **DECIDED 2026-09-13: no. The threshold is POSTGRADUATE, grade 17 and above.**

   The team lead's reasoning, and it corrects mine: grades 13 to 16 are college
   freshman through senior. A term that lands there is not a problem, because a
   motivated reader reaches it -- which is the whole point of the escalation
   ladder. **A cluster at POSTGRADUATE level is the signal worth addressing**,
   because that is where the reader cannot climb without prior specialist
   training.

   | Grade | Level | Verdict |
   |---|---|---|
   | 8-12 | Middle and high school | Target range |
   | 13-16 | College freshman to senior | Acceptable; reachable |
   | 17+ | Postgraduate | **Cluster here is a finding** |

   Still a review signal and never an automatic edit. The Phase 1 documents are
   frozen; this applies to Phase 2 writing.

## References

- F39 (this card, the Evidence Based Database), F44 (`test_document_figures_resolve.py`), F72 (reference
  library, gated on this storage decision)
- Amendments A15, A19, A24; findings F52, and the Sprint 13 evidence walk
- `docs/sprints/SPRINT_13_SUMMARY.md`, `docs/sprints/SPRINT_8_RETROSPECTIVE.md`
- Cycorp (cyc.com), for the confidence-scoring idea only
