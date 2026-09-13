# ADR-0015: Reference-paper library with retrieval, outside this repository

## Status

**Proposed.** Awaiting team-lead acceptance or rejection. **No implementation is
authorised by this document**; F72 is investigation and design only.

Depends on **ADR-0014** (fact database) for its storage decision. If 0014 is
rejected or its storage changed, this ADR changes with it.

## Date

2026-09-12

## Context

### What the team lead asked for

Deep-dive summaries of quantum-machine-learning, quantum-computing and classical
machine-learning papers, analysed for applicability to:

- **Dirac-3** — the continuous-variable optimizer this project has measured;
- **gate-based work** via Amazon Braket and Classiq, which the proposal commits
  to unconditionally for Phase 2;
- **non-quantum methods** (tensor decompositions and similar) that might carry
  the same structural idea without a device.

Stored **outside** this repository, **referenceable from** it, and searchable in
a RAG-like way for future use.

### Why this is worth building rather than keeping a folder of PDFs

This project has already been damaged twice by reading papers imprecisely, and
both times the error reached a submitted document:

- **F53** found the AutoXGB dataset misattributed — a benchmark figure quoted
  against the wrong dataset entirely.
- **A28** corrected "we did not find this paper before freezing" about Loke et
  al., which the freeze itself names as H1a with its exact protocol. We had read
  it, and the claim that we had not was false.

A third case ran the other way and is the model to preserve: during Sprint 12 a
review agent **flagged its own reviewer's claim as wrong** about FG22/5 §5.12,
having checked the source text. That is what a reference library should make
routine rather than exceptional.

### The constraint that shapes the design

**A citation from a public evidence repository must resolve for a reader who
does not have the other repository.** This repository is public, judged, and its
Appendix C stakes a reproducibility claim on things resolving. A dangling
cross-repository pointer would be a new instance of the defect class this
project keeps finding.

That gives two honest options, and only two: the library is public as well, or
every citation into it carries enough inline context to stand alone.

## Decision

### 1. Same repository as the fact database, or a sibling under the same decision

F39 and F72 are the same shape: **structured records carrying provenance and
confidence, retrievable, maintained outside prose.** They should share the
storage decision rather than making two.

Concretely: **SQLite store of record plus a committed deterministic export**, as
ADR-0014 specifies. A paper record is a fourth record class alongside
`assertion`, `acronym` and `term`.

That is not a tidiness argument. Two stores mean two schemas, two export
formats, two retrieval paths and two places for a fact about a paper to drift
from a fact about a number — which is the problem both cards exist to solve.

### 2. What a paper record holds

| Field | Meaning |
|---|---|
| `id` | Stable, human-readable, e.g. `loke-2024-cvqboost` |
| `citation` | Full bibliographic record, plus DOI or arXiv id |
| `access` | Where the PDF lives. **Never the PDF itself** — see below |
| `claim` | What the paper actually claims, in its own terms, with section or page |
| `evidence` | What it measured, on what data, with what controls |
| `applicability` | `dirac-3` \| `gate-based` \| `classical` \| `none`, with a sentence saying why |
| `verdict` | `use` \| `cite-only` \| `contradicts-us` \| `superseded` \| `unverified` |
| `confidence` | 0.0–99.9%, as ADR-0014 |
| `fidelity` | `exact` \| `scoped` \| `consequence`, as ADR-0014 |
| `checked_against_source` | **REQUIRED.** A date plus who or what checked it, or the literal `never`. See below |

The last field is the one that earns the build, and it is **required with an
explicit `never` rather than left blank** (team lead, 2026-09-12). Blank is
ambiguous: it cannot distinguish *nobody has checked this* from *someone forgot
to fill the field*, and those call for opposite responses. `never` is a
statement a person made; a blank is an absence a reader has to interpret, which
is the same reasoning that makes a skipped test worse than a failing one.

F53 and A28 were both failures of nobody having checked the source recently
enough. A record that says `never` out loud is visible in a way a confident
summary is not.

It also carries `reading_level`, `fidelity` and `prerequisites` from ADR-0014.
A paper summary is subject to the same escalation rule as a glossary term:
start at 8th grade, climb one grade at a time until honest, record where it
landed.

`contradicts-us` is a deliberate verdict value. A library that can only record
supporting work is a bibliography for a conclusion already reached.

### 3. Copyright: store records, never redistribute papers

The `access` field holds a DOI, an arXiv id, or a local path **outside version
control**. Published papers are under copyright and most are not redistributable;
this repository already declines to redistribute its datasets for the same
reason, and the README says so.

**Summaries and extracted claims are our own writing and are ours to store.**
Verbatim quotation stays short and attributed.

### 4. Retrieval: start with search over the export, not a vector database

**Phase one: full-text search over the committed export.** At the tens-to-low-
hundreds of records this will hold for a long time, `grep` and a small index are
genuinely sufficient, and they are inspectable — a retrieval that returns the
wrong paper is visible in a way an embedding-similarity miss is not.

**Phase two, only on evidence it is needed: embeddings.** The trigger is a
recorded instance of search failing to surface a paper that was in the library.
Not before.

This ordering is deliberate. "RAG-like search" names a technology; the
requirement is *finding the right paper again*, and this project has repeatedly
found the simpler instrument sufficient once the problem was measured rather
than assumed.

### 5. How this repository cites into it

Inline, self-contained, with a pointer: the citation carries the claim and its
provenance in the sentence, and the library id is an identifier for the reader
who wants more. **This repository never requires the library to be resolvable.**

Phase 2 documents, written under a different confidentiality posture (T&C §7
binds on receipt of non-public material), may depend on it more directly. That
decision waits for acceptance.

## Alternatives considered

### A folder of PDFs with a README
- **Description**: what most projects do.
- **Pros**: zero build; zero schema.
- **Cons**: no provenance, no verdict, no record of whether anyone checked the source. It is exactly the state that produced F53 and A28.
- **Why rejected**: the failure mode is already on record, twice.

### A reference manager (Zotero, Mendeley)
- **Description**: adopt an existing tool.
- **Pros**: mature; handles citation formats; already has PDF management.
- **Cons**: its data model is bibliographic, not analytical. There is no natural home for `applicability`, `verdict`, or `checked_against_source`, which are the fields that would have prevented our actual defects. Exporting into our own schema means maintaining two systems.
- **Why rejected**: it solves citation formatting, which is not the problem.

### A separate store from the fact database
- **Description**: build F72 independently.
- **Pros**: each can move at its own pace.
- **Cons**: two schemas, two exports, two retrieval paths, and two places for the same fact to drift.
- **Why rejected**: the shapes are identical; the duplication would be the defect.

### Vector database from day one
- **Description**: embed everything, semantic search immediately.
- **Pros**: handles paraphrase; scales.
- **Cons**: opaque failure. A miss returns plausible wrong papers with no signal that it missed, which is the same class as a green suite that asserts nothing.
- **Why rejected**: premature at this scale. Kept as phase two, gated on measured need.

## Consequences

### Positive
- Paper claims become checkable, with a visible record of whether anyone checked.
- `contradicts-us` gives disconfirming work a place to live.
- Shares one storage decision with F39 instead of inventing a second.
- Phase 2 starts with a searchable body of prior work rather than a folder.

### Negative
- A second cross-repository dependency, and the same provisional-boundary caveat.
- Writing a good paper record is slow; a bad one is worse than none because it
  looks authoritative.
- **A summary can be confidently wrong.** `checked_against_source` and
  `confidence` are the mitigations, and neither is automatic.

### Neutral
- Adds a fourth record class to a schema designed for extension.

## Preregistration touchpoints

None. This is tooling outside the frozen methodology and requires no amendment.

## Open questions for the team lead

1. **Does this share ADR-0014's repository, or sit beside it?** Recommendation:
   same repository, separate table. One decision, one export pipeline.
2. **Which papers seed it?** The submission's own reference list is the obvious
   start, and it is already the set most likely to be re-read during judging.
3. **Is `checked_against_source` a hard gate for `verdict: use`?** Recommendation:
   yes, and now enforceable: `never` is an explicit value, so the gate is a
   comparison rather than a null check. An unverified paper can be cited as
   `unverified`, but should not support a decision.

## References

- ADR-0014 (fact database), F39, F72
- F53 (AutoXGB dataset misattribution), A28 (the Loke et al. prior-work claim)
- Sprint 12: the review agent that correctly rejected its own reviewer's FG22/5 claim
- `docs/references.md`, `docs/research-baselines-best-practices.md`
