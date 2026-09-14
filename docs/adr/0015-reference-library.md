# ADR-0015: Reference-paper library with retrieval, outside this repository

## Status

**Proposed.** Awaiting team-lead acceptance or rejection. **No implementation is
authorised by this document**; F72 is investigation and design only.

Depends on **ADR-0014** (Evidence Based Database) for its storage decision. If 0014 is
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

### 1. Lives in the Evidence Based DB

**Decided 2026-09-13**: the reference library is a record class inside
**`EvidenceBasedDB`** (ADR-0014), which is **private for now**. Papers are a
fourth class beside `assertion`, `acronym` and `term`.

While that repository is private, section 5's inline-citation rule is a hard
constraint rather than a preference: a pointer into a private repository does
not resolve for the public reader this repository has.

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

**Records are TIERED.** At 2,000-plus papers a single record shape is the
design's biggest risk; see section 2c. Fields are marked by the tier that first
requires them.

| Field | Tier | Meaning |
|---|---|---|
| `id` | seen | Stable, human-readable, e.g. `loke-2024-cvqboost` |
| `tier` | seen | `seen` \| `screened` \| `read` |
| `citation` | seen | Full bibliographic record plus DOI or arXiv id. **Pulled from an API, never hand-typed** |
| `access` | seen | Where the PDF lives. **Never the PDF itself** — see below |
| `context` | seen | Which context(s) it belongs to, from ADR-0014's list: `qml`, `platform:dirac-3`, `method`, ... |
| `disposition` | seen | One line: why this was worth recording, or why it was rejected. **A rejected paper is still a record** |
| `claim` | screened | What the paper claims, in its own terms, with section or page |
| `applicability` | screened | **Context ids** it bears on, plus a sentence saying why. Not a separate vocabulary — see 2d |
| `verdict` | screened | `use` \| `cite-only` \| `contradicts-us` \| `superseded` \| `unverified` |
| `certainty` | screened | `high` \| `moderate` \| `low` \| `very-low`. **DERIVED, not chosen** — see 2e |
| `certainty_reasons` | screened | **REQUIRED whenever certainty is not the starting level.** The named reasons that moved it |
| `evidence` | read | What it measured, on what data, with what controls |
| `citation_context` | read | The SENTENCE that makes the claim, quoted. Not just a page number |
| `supports` | read | Assertion ids this paper supports |
| `contradicts` | read | Assertion ids this paper contradicts |
| `fidelity` | read | `exact` \| `scoped` \| `consequence`, as ADR-0014 |
| `reading_level` | read | As ADR-0014; the escalation rule applies to summaries too |
| `checked_against_source` | read | **REQUIRED at this tier.** A date plus who or what checked it, or the literal `never`. See below |

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

### 2c. Tiers, because 2,000 papers is a screening problem

**Team lead, 2026-09-14: the library will eventually hold more than 2,000
papers, many of which we will reject but must look at first.**

### The correction that matters: our readers are agents, not people

My first draft of this section applied the prior art uncritically and got the
economics wrong. **Team lead, 2026-09-14: "ours is different. There are not
people looking at each paper, we are a single agent looking at each paper with
many running in parallel and at 1% of the speed or less."**

That is right, and it invalidates the argument I had built. I wrote "at 2,000
papers a ten-minute record is 333 hours" -- a figure that silently assumes a
HUMAN writing each record. The collector's fallacy literature is entirely about
human cognition: "the mistaken belief that having a text at hand increases our
knowledge" is false FOR A PERSON because a person must read it to know it. Its
named failure modes -- processing overhead as "a part-time job",
research-mode-as-procrastination, maintenance burden -- are all costs in human
attention, which is scarce, serial, and resents drudgery.

**An agent reading 2,000 papers has none of those properties.** It is parallel,
it does not procrastinate, and a thorough record costs nothing it minds
spending. So the premise "records are expensive, therefore most papers should
not get one" is mostly WRONG here. **Most papers can get a full record.**

### What still transfers, and it is not nothing

Three things survive the correction, and one gets WORSE at agent speed:

1. **Your review time is still scarce and serial.** An agent can read the paper;
   only the team lead can decide a verdict is trustworthy. That cost does not
   parallelise.
2. **"No purpose, no feedback mechanism, produces nothing"** is agent-
   independent. A library nobody reaches for is useless however cheaply it was
   built -- and it gets there FASTER at agent speed.
3. **Maintenance decay** is agent-independent. `checked_against_source` going
   stale does not care who wrote the record.
4. **Volume without judgement gets worse.** Two thousand confident-sounding
   records nobody adjudicated is a MORE dangerous artifact than fifty
   hand-written ones: it looks authoritative and it scales the error. This
   project has met that failure at small scale already -- three published claims
   that were false and internally consistent.

### Tiers stay, but they mean adjudication depth, not drafting effort

| Tier | What it asserts | Whose cost |
|---|---|---|
| `seen` | An agent recorded it exists and why it was or was not pursued | Agent, negligible |
| `screened` | An agent extracted the claim and proposed a verdict | Agent, negligible |
| `read` | **A source was genuinely opened and the record adjudicated** | Team lead, real |

The tier is now a claim about **how far the record has been verified**, not a
budget. That makes `read` meaningful in a way a drafting-effort tier never was:
it is the tier at which `checked_against_source` must be non-`never`.

**Rejecting a paper still leaves a trace.** Cheap for an agent, and it prevents
re-screening the same paper in six months.

Systematic-review screening remains relevant for ORDERING -- which papers reach
the team lead first -- rather than for reducing how many get records. Their
practice automates exclusion and accepts roughly 5% recall loss [30-70% workload
reduction, and 65-85% with LLM screening, PMC12306261]. We do not need that
trade: exclusion stays adjudicated, because an automated wrong rejection is
invisible and we are not paying by the record.

### 2d. `applicability` points at contexts; it is not its own vocabulary

**Team lead, 2026-09-14: agreed, collapse it.**

The earlier draft gave `applicability` its own four values -- `dirac-3`,
`gate-based`, `classical`, `none` -- written before ADR-0014 established
contexts. Two lists then named the same things in different words, so adding a
platform meant remembering to add it in both places, and missing one would leave
them disagreeing.

That is precisely the defect this project keeps meeting: B1's variable count
read 78 in three documents and 91 in two, because the value was maintained in
five places instead of one.

**`applicability` now holds context ids from ADR-0014's list.** One vocabulary,
so it cannot drift from itself.

### 2e. `certainty` is DERIVED with named reasons, following GRADE

The earlier draft carried a 0.0-99.9% confidence number. **A percentage cannot
be argued with**, which makes it a worse instrument than it looks: `62%` is
unfalsifiable, and this project's whole posture is that claims should be
checkable.

GRADE, the standard clinical medicine uses to grade a body of evidence, is built
the other way round:

- Four levels: **high, moderate, low, very low**.
- **Starting level depends on study type** -- randomised trials start high,
  observational studies start low [Cochrane Handbook ch. 14].
- **Five named downgrade reasons**: risk of bias, inconsistency, indirectness,
  imprecision, publication bias. One level for serious concerns, two for very
  serious.
- **Three named upgrade reasons** for non-randomised work: large effect,
  dose-response, opposing plausible confounding.
- A floor: certainty cannot fall below very low however many reasons apply.

**The reasons are the audit trail, and they are the part worth having.** A
record saying *"started high, measured on hardware; downgraded one level for
imprecision, single seed"* can be checked, disputed and corrected. A record
saying `62%` cannot.

This maps onto machinery this project already has. Evidence tags set the
starting level -- `[HW]` starts higher than `[PROJ]` -- and our existing caveats
are downgrade reasons under other names: the score-degeneracy caveat is
imprecision, the single-seed spot checks are imprecision, the adversarial
control that never converged is risk of bias.

### 2f. `supports` and `contradicts` link to assertion ids

**Team lead, 2026-09-14: add the contradicts field and use it whenever
possible.** Adding a `supports` field alongside it, for a reason from the data.

scite classifies 1.6 billion citing statements as supporting, contrasting or
mentioning. The distribution:

> **92.6% mentioning, 6.5% supporting, 0.8% contrasting** [scite]

**Fewer than one citation in a hundred contests what it cites.** Not because
papers rarely conflict, but because contesting is costly to write and easy to
omit. So an explicit `contradicts` link does work that no citation count does,
and it will be rare and disproportionately valuable.

`supports` earns its place separately: "which papers back this claim" is the
question we will actually ask when writing Phase 2 documents.

Both link to assertion ids in the Evidence Based DB, which is the transitive
query that would fire ADR-0014's **graph-store trigger** -- "what depends on
this assertion if it changes". Noted there, not built here.

### 2b. Contexts, and the first record

**Team lead, 2026-09-13: arXiv:2308.04445 enters the library, and it is NOT
associated with the HSBC challenge.** That is the first record, and it is a
useful test because it is the first one whose context is not `hsbc-2026`.

It also surfaces something the two-context sketch (`hsbc-2026` versus `world`)
did not cover. This paper is neither: it is not evidence for a fraud-detection
claim, and it is not a general world fact. It is **methodology for the library
itself** -- we are building an evidence base partly from what it says about how
Cyc does it.

So the initial contexts are three, not two:

| Context | Holds | Example |
|---|---|---|
| `hsbc-2026` | Assertions specific to this project | amendment count, campaign totals, B2's +0.0256 |
| `world` | Facts true independent of any project | 2+2=4, E=mc^2, standard acronym expansions |
| `method` | How we build and reason, including about the library | arXiv:2308.04445 |

Cyc's lesson applies here directly: contexts factor out shared assumptions
rather than tagging records, so assertions inside one get terser and reasoning
within it gets faster. About 10,000 named contexts exist in Cyc, kept down by
COMPUTING contexts rather than reifying every combination [LM23 p15]. Three is
the right number to start with, and the rule is to add a context only when
assertions genuinely share an assumption that the existing ones do not.

**A paper record is scoped by context, not by project tag.** A future project
reusing the library gets `world` and `method` for free and adds its own context.

#### The first record, as it would be written

    id:                       lenat-marcus-2023-trustworthy-ai
    tier:                     read
    context:                  method
    citation:                 Lenat, D. and Marcus, G., "Getting from Generative
                              AI to Trustworthy AI: What LLMs might learn from
                              Cyc", arXiv:2308.04445, 31 July 2023
    access:                   arXiv:2308.04445
    disposition:              Methodology for this library. Read in full for
                              ADR-0014; it corrected two beliefs we had recorded
    claim:                    16 desiderata for trustworthy AI; Cyc addresses
                              them via EL/HL separation, contexts,
                              argumentation-not-proof, and 1,100 specialised
                              reasoners
    applicability:            method
    verdict:                  use
    certainty:                moderate
    certainty_reasons:        Started LOW -- position paper, no experiment.
                              UPGRADED one level for admission against interest:
                              footnote 9 concedes the general theorem prover
                              timed out on a million consecutive queries and was
                              switched off, which is costly to disclose and
                              therefore credible. NOT upgraded further: claims
                              about Cyc's behaviour are first-author testimony,
                              independently unverifiable, and the paper is
                              advocacy by Cyc's creator
    evidence                  Position paper. No experiment, no measurement. All
                              claims about Cyc are reported by its creator
    citation_context:         "we quietly turned the general theorem prover off,
                              so it never gets called on!" [p14, footnote 9]
    supports:                 heuristics-over-general-reasoning
    contradicts:              (none recorded)
    fidelity:                 exact
    reading_level:            13
    checked_against_source:   2026-09-13, Claude, read pp. 1-16 directly
    notes:                    Footnote 9 is the load-bearing finding and the
                              reason certainty is moderate rather than low

**Note what `certainty_reasons` is doing there, because it is the whole
argument for the GRADE model.** The record does not assert a number. It says
where the level started, what moved it, and what deliberately did not move it
further. A reader can disagree with the upgrade -- is an admission against
interest really worth a level? -- and that disagreement is possible only because
the reason is written down.

A record saying `confidence: 72%` would have been unarguable and therefore
weaker. This is the same distinction the project has met repeatedly: a figure
with provenance can be checked; a figure without one can only be believed.

### 3. Copyright: store records, never redistribute papers

The `access` field holds a DOI, an arXiv id, or a local path **outside version
control**. Published papers are under copyright and most are not redistributable;
this repository already declines to redistribute its datasets for the same
reason, and the README says so.

**Summaries and extracted claims are our own writing and are ours to store.**
Verbatim quotation stays short and attributed.

### 4. Retrieval: start with search over the export, not a vector database

**Phase one: full-text search over the committed export.** Inspectable in a way
an embedding-similarity miss is not: a search that returns the wrong paper shows
you why.

**REVISED 2026-09-14.** I wrote "tens-to-low-hundreds of records ... for a long
time" when the scope was one project's references. At 2,000-plus papers that is
wrong, and the embeddings trigger should be expected to fire EARLY rather than
treated as a distant possibility. The trigger itself is unchanged -- a recorded
instance of search failing to surface a paper that was in the library -- but the
expectation is not.

The tiering in 2c helps here too: `seen` records carry a one-line disposition,
so even the rejected majority is searchable for "did we already look at this".

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

## The falsifier for this whole card

**The honest null hypothesis: a private, hand-curated paper library may not beat
simply searching Semantic Scholar when you need something.** The prior-art
research found no source establishing that it does, and that absence is worth
stating rather than glossing.

This project requires a premise falsifier on any card justified by a measurement
(Sprint 8 improvement 2), and the same discipline applies here.

**Falsifier, to be checked at 100 records and again at 500:** if we are not
REACHING FOR the library when writing -- if the honest answer to "where did you
get that" is still a fresh search -- then it is not working, and it should be
scrapped rather than maintained out of sunk cost.

The measurable version: **count how many library records are cited in the next
document we write.** Zero at 100 records is a strong signal. It would mean the
library is a collection rather than a tool, which is the collector's fallacy
arriving on schedule.

**The second thing to watch is maintenance decay.** The research found no
evidence on how quickly such libraries go stale once the initial burst ends, and
that is the failure I would bet on. `checked_against_source` makes it visible:
if the median age of that field grows monotonically, the library is being
collected and not used.

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

1. ~~Does this share ADR-0014's repository, or sit beside it?~~ **DECIDED
   2026-09-13**: same repository (`EvidenceBasedDB`), separate record class. One
   decision, one export pipeline.
2. ~~Which papers seed it?~~ **DECIDED 2026-09-13**: the submission's own
   reference list seeds it. That is the set most likely to be re-read during
   judging, and the set where a misreading has already cost us twice (F53, A28).
3. ~~Is `checked_against_source` a hard gate for `verdict: use`?~~ **DECIDED
   2026-09-13: YES, adopted provisionally -- try it and watch for trouble.**

   Enforceable because `never` is explicit, so the gate is a comparison rather
   than a null check. An unverified paper may be cited as `unverified` but
   cannot support a decision.

   **Adopted with the expectation that it might chafe**, and the failure mode to
   watch for is a specific one: if the gate makes people record a perfunctory
   check just to clear it, it has made things worse rather than better -- a
   date in a field that nobody honoured is weaker evidence than an honest
   `never`. If that starts happening, the right response is to relax the gate,
   not to tighten the wording. Revisit after the seed set is loaded.

## References

- ADR-0014 (Evidence Based Database), F39, F72
- F53 (AutoXGB dataset misattribution), A28 (the Loke et al. prior-work claim)
- Sprint 12: the review agent that correctly rejected its own reviewer's FG22/5 claim
- `docs/research/paper-library-prior-art.md` -- prior-art research, 2026-09-14: the
  collector's fallacy, systematic-review screening tiers, scite's citation-intent
  distribution, and GRADE's derived-certainty model. It is the source for sections
  2c, 2e and 2f, and for the falsifier above
- `docs/references.md`, `docs/research-baselines-best-practices.md`
