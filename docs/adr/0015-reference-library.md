# ADR-0015: Reference-paper library with retrieval, outside this repository

> **THE LIVE COPY IS NOT THIS ONE.** This ADR was MOVED to the
> `kimmeyh/EvidenceBasedDB` repository on 2026-09-14 and lives there as
> **ADR-0005**. That repository owns the design; this repository is a consumer
> of it. Amend it THERE. This copy is frozen as the record of when the decision
> was made and by whom, and it is deliberately byte-identical to the live copy
> as of the move. If the two ever differ, the EvidenceBasedDB copy wins.

## Status

**ACCEPTED 2026-09-14** by the team lead.

What acceptance covers, all of it decided in review rather than as first
drafted: **a paper is a source of assertions, not a record in itself**; tiers as
adjudication depth rather than drafting effort; `applicability` pointing at
ADR-0014's contexts instead of its own vocabulary; `certainty` derived
GRADE-style with named reasons rather than a percentage; `supports` and
`contradicts` as relations between assertions; records not PDFs; and full-text
search before embeddings.

What it does NOT cover: **no implementation is authorised by this document.**
F72 was scoped as investigation and design, and building is a separate card.

**Accepted does not mean settled**, exactly as in ADR-0014. See "Maturity"
below: the schema details are expected to move at the 20-paper checkpoint (F75),
and revisions are recorded as dated amendments rather than edits in place.

**Why this was accepted rather than left Proposed**, recorded because the
distinction caused confusion: early-innovation status governs how much a
document may CHANGE; ADR status governs whether a decision has been MADE. They
are independent, and ADR-0014 is both Accepted and early-innovation. Leaving
0015 at Proposed while building against its decisions would have produced the
gap this project keeps finding -- a practice that is settled and a record that
says otherwise.

Depends on **[ADR-0014](0014-fact-database.md)** (Evidence Based Database) for its storage decision. If
0014's storage changes, this ADR changes with it.

### What remains genuinely open

Narrow, and neither blocks anything:

1. **Does the library ship beyond internal use?** Currently internal, like the
   glossary. A Phase 2 appendix is plausible and would raise the review bar.
2. **What the record looks like after 20 papers have tested it.** The checkpoint
   in "Maturity" exists for exactly this, and F75 cards it.

## Date

2026-09-12

## Maturity: EARLY INNOVATION, revision expected

**Team lead, 2026-09-14: these ADRs and the database itself cannot be written in
stone. After importing roughly 20 papers we expect to find that some of this
works, some does not, and some fields need adding. That is expected, not
failure.**

This matters because "Accepted" on an ADR normally signals a settled decision --
the PDF toolchain, the results-store schema, the branch model. Those were
accepted after the practice had been exercised. **This design has not yet met a
single imported paper.** Reading it with the same finality would be a category
error, and would make the first necessary change feel like a defeat.

### The first checkpoint: 20 papers

At approximately 20 imported papers, review both ADRs against what actually
happened and record the answers:

| Question | What a bad answer looks like |
|---|---|
| Which fields were never filled? | A field nobody populated is dead weight; remove it |
| Which fields were filled with the same value every time? | Not carrying information; probably belongs in the context |
| What did we want to record and have nowhere to put? | The additions this checkpoint exists to find |
| How long did team-lead adjudication take per paper? | The number the whole design is constrained by (2c) |
| Did the tiers land where predicted? | If everything is `read`, tiering is theater |
| Did any `supports` or `contradicts` link get used? | scite's 0.8% says these are rare; zero at 20 papers is uninformative, zero at 200 is a finding |

**Revising after that review is the expected outcome, not an admission.** A
design that survives its first twenty papers unchanged has probably not been
tested against them.

### What revision does NOT mean

Two things stay stable through the early phase, because changing them costs more
than it saves:

1. **Provenance on every record.** The reason this system exists. A field can
   come or go; a record that cannot say where its value came from is the defect
   the whole thing is built against.
2. **Contexts as the partitioning mechanism.** Adding contexts is expected;
   replacing contexts with tags would undo the one structural idea taken from
   forty years of Cyc.

Everything else is provisional until the practice says otherwise.

### How revisions get recorded

Not by editing these ADRs in place. **A dated amendment section at the bottom**,
naming what changed and what observation forced it -- the same discipline the
preregistration uses, and for the same reason: a document that silently becomes
correct teaches nobody why it was wrong.

## Context

### What the team lead asked for

Deep-dive summaries of quantum-machine-learning, quantum-computing and classical
machine-learning papers, analyzed for applicability to:

- **Dirac-3** -- the continuous-variable optimizer this project has measured;
- **gate-based work** via Amazon Braket and Classiq, which the proposal commits
  to unconditionally for Phase 2;
- **non-quantum methods** (tensor decompositions and similar) that might carry
  the same structural idea without a device.

Stored **outside** this repository, **referenceable from** it, and searchable in
a RAG-like way for future use.

### Why this is worth building rather than keeping a folder of PDFs

This project has already been damaged twice by reading papers imprecisely, and
both times the error reached a submitted document:

- **F53** found the AutoXGB dataset misattributed -- a benchmark figure quoted
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
from a fact about a number -- which is the problem both cards exist to solve.

### 2. What a paper record holds

**Records are TIERED.** At 2,000-plus papers a single record shape is the
design's biggest risk; see section 2c. Fields are marked by the tier that first
requires them.

**The paper record is PROVENANCE plus screening state.** The claims themselves
are assertions (2b2), and they carry their own certainty, links and checks.

| Field | Tier | Meaning |
|---|---|---|
| `id` | seen | Stable, human-readable, e.g. `loke-2026-cvqboost` |
| `tier` | seen | `seen` \| `screened` \| `read` -- how far anyone has gone in mining it (2c) |
| `citation` | seen | Full bibliographic record plus DOI or arXiv id. **Pulled from an API, never hand-typed** |
| `access` | seen | Where the PDF lives. **Never the PDF itself** -- see below |
| `context` | seen | Context(s) from ADR-0014's list: `qml`, `platform:dirac-3`, `method`, ... |
| `disposition` | seen | One line: why it was worth recording, or why it was rejected. **A rejected paper is still a record** |
| `applicability` | screened | **Context ids** it bears on, plus a sentence saying why. Not a separate vocabulary -- see 2d |
| `yields` | screened | **The assertion ids extracted from it.** The field that makes this a source rather than a summary |
| `evidence` | read | What the paper measured, on what data, with what controls. A property of the STUDY, so it stays here |
| `mined_by` | read | Who or what extracted the assertions, and when |
| `checked_against_source` | read | **REQUIRED at this tier.** A date plus who or what checked it, or the literal `never` |

**Everything else moved to the assertion**, which is where ADR-0014 already
defines it: `claim` becomes the assertion's own text; `certainty` and
`certainty_reasons` attach per assertion, so Loke's 0.8108 and Loke's protocol
description are graded separately; `supports` and `contradicts` become relations
BETWEEN assertions with papers as provenance; `citation_context` -- the sentence
making the claim -- belongs to the assertion it supports; and `fidelity` and
`reading_level` are already assertion-level fields in ADR-0014.

There is no `verdict` on a paper any more. **A paper is not true or false; its
assertions are.** F53 is the proof: one extracted claim was misattributed while
the rest of that paper was fine, and a paper-level verdict could not have said
so.

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

The `contradicts` relation in section 2f is deliberate. A library that can only
record supporting work is a bibliography for a conclusion already reached.

### 2b2. A paper is a SOURCE OF ASSERTIONS, not a record in itself

**Team lead, 2026-09-14: "Just like we used the 5 or so papers in the challenge
submission, we will use each paper judicially to understand what is verifiable
about ML, QML and QC, then apply it to our DB, so each paper results in several
entries that are backed up or refuted or something in between."**

This is the structural correction to this ADR, and the submission already proves
it. I had a paper as one record with a `claim` field. **The submission never
used papers that way.**

Verified against the shipped documents. Four cited papers yielded at least eight
distinct checkable assertions:

| Assertion | From | What it is |
|---|---|---|
| KNN reaches 0.8108 on ULB | Loke et al. | A reproducible target |
| CAD reaches 0.7423 | Loke et al. | A comparator |
| target AUC-PR 0.80 | Loke et al. | The H1a replication bar, IN THE FREEZE |
| 23 of 24 cells favor the quantum arm | Emami et al. | A prior-work result |
| ADASYN 1:1 gives 0.8855 vs 0.8826 | Emami et al. | A specific measured pair |
| device limit 949 variables | QCi guide | **A constraint we designed against** |
| 23 dB dynamic-range limit | Emami et al. | The basis of the A31 resolution finding |
| "hybrid photonic-electronic ... non-convex optimization" | Nguyen et al. | How the vendor characterises the device |

**Each of those is separately checkable, separately citable, and separately
capable of being wrong.** F53 proved the last point: the AutoXGB dataset
misattribution was ONE assertion extracted from one paper being wrong, while
everything else about that paper was fine. A paper-level `verdict` field could
not have expressed that.

And `949` appears NINE TIMES in the preregistration alone, plus the proposal.
That is the duplication problem this whole system exists to solve, and it is
paper-derived.

#### What this changes in the schema

**The assertion is the unit. The paper record becomes provenance for
assertions**, plus the screening state that says whether anyone has mined it
yet.

    paper record          -- bibliographic, access, tier, disposition
      |
      +-- yields --> assertion (context: qc,  "Dirac-3 device limit is 949 variables")
      +-- yields --> assertion (context: qml, "KNN reaches 0.8108 AUPRC on ULB")
      +-- yields --> assertion (context: qc,  "effective analog resolution ~23 dB")

Consequences, each of which simplifies something I had made complicated:

1. **`claim` moves off the paper record.** A paper does not have *a* claim; it
   has several, and they belong in the assertion class ADR-0014 already defines.
2. **`supports` and `contradicts` become relations between ASSERTIONS**, with
   papers as their provenance. That is what "backed up or refuted or something
   in between" means: our assertion that Dirac-3 resolves ~200 levels is
   supported by Emami's 23 dB and by our own A31 measurement, from two
   independent sources.
3. **`certainty` attaches to the assertion, not the paper.** This is strictly
   better: Loke's 0.8108 and Loke's protocol description do not deserve the same
   certainty just because they share a source.
4. **"Something in between" gets a home.** Not every extracted assertion is
   supported or refuted. Most are simply *recorded and unchecked* -- which is
   what `checked_against_source: never` already says, now at the right
   granularity.
5. **The paper `tier` still matters** and means what 2c says: how far anyone has
   gone in mining it. `seen` = we know it exists. `screened` = an agent pulled
   the assertions out. `read` = the team lead adjudicated them.

#### Why this is the right unit, in one line

**We do not cite papers in our documents. We cite claims.** The submission's
appendix does not say "see Loke et al."; it says the H1a replication target is
AUC-PR 0.80 and names where that came from. The database should store what the
documents actually reference.

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
4. **Volume without judgment gets worse.** Two thousand confident-sounding
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

THE PAPER RECORD -- provenance and screening state only:

    id:                       lenat-marcus-2023-trustworthy-ai
    tier:                     read
    context:                  method
    citation:                 Lenat, D. and Marcus, G., "Getting from Generative
                              AI to Trustworthy AI: What LLMs might learn from
                              Cyc", arXiv:2308.04445, 31 July 2023
    access:                   arXiv:2308.04445
    disposition:              Methodology for this library. Mined in full for
                              ADR-0014; it corrected two beliefs we had recorded
    applicability:            method
    evidence:                 Position paper. No experiment, no measurement. All
                              claims about Cyc are reported by its creator
    yields:                   cyc-truth-values-four
                              cyc-no-numeric-confidence
                              cyc-general-prover-disabled
                              cyc-hl-module-count
                              cyc-context-count
    mined_by:                 2026-09-13, Claude, pp. 1-16
    checked_against_source:   2026-09-13, Claude, read pp. 1-16 directly

ONE OF THE ASSERTIONS IT YIELDS -- the interesting one:

    id:                       cyc-general-prover-disabled
    class:                    assertion
    context:                  method
    value:                    Cyc's general resolution theorem prover was
                              switched off about a decade before 2023, after
                              timing out on over a million consecutive queries
                              where it was called as a last resort
    provenance:               lenat-marcus-2023-trustworthy-ai, p14 footnote 9
    citation_context:         "we quietly turned the general theorem prover off,
                              so it never gets called on!"
    certainty:                moderate
    certainty_reasons:        Started LOW -- position paper, first-author
                              testimony about the author's own system, no
                              independent verification possible. UPGRADED one
                              level for admission against interest: this concedes
                              that the system's most general component never
                              worked, which is costly to disclose and therefore
                              credible. NOT upgraded further: still unverifiable
    supports:                 heuristics-over-general-reasoning
    contradicts:              (none recorded)
    fidelity:                 exact
    reading_level:            11
    checked_against_source:   2026-09-13, Claude, read p14 directly

A SECOND ASSERTION FROM THE SAME PAPER, graded differently:

    id:                       cyc-hl-module-count
    value:                    Cyc had 20 heuristic-level reasoners in 1989 and
                              over 1,100 by 2023
    provenance:               lenat-marcus-2023-trustworthy-ai, p13
    certainty:                low
    certainty_reasons:        Started LOW -- position paper. NOT upgraded: a
                              round self-reported count with no definition of
                              what counts as a module and no way to check it.
                              Unlike footnote 9 this is favorable to the
                              author, so the admission-against-interest upgrade
                              does not apply

**Two assertions, one paper, different certainty.** That is the whole argument
for making the assertion the unit. A paper-level `certainty` field would have
had to average an admission against interest with a self-flattering statistic,
and the average would have been wrong about both.

**Note what `certainty_reasons` is doing, because it is the whole argument for
the GRADE model.** Neither record asserts a number. Each says where the level
started, what moved it, and what deliberately did not move it further. A reader
can disagree -- is an admission against interest really worth a level? -- and
that disagreement is possible only because the reason is written down.

`confidence: 72%` would have been unarguable and therefore weaker. Same
distinction this project has met repeatedly: a figure with provenance can be
checked; a figure without one can only be believed.

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
- **Cons**: no provenance, no extracted assertions, no record of whether anyone checked the source. It is exactly the state that produced F53 and A28.
- **Why rejected**: the failure mode is already on record, twice.

### A reference manager (Zotero, Mendeley)
- **Description**: adopt an existing tool.
- **Pros**: mature; handles citation formats; already has PDF management.
- **Cons**: its data model is bibliographic, not analytical. There is no natural home for `applicability`, `yields`, or `checked_against_source`, which are the fields that would have prevented our actual defects. Exporting into our own schema means maintaining two systems.
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
- The `contradicts` relation gives disconfirming work a place to live.
- Shares one storage decision with F39 instead of inventing a second.
- Phase 2 starts with a searchable body of prior work rather than a folder.

### Negative
- A second cross-repository dependency, and the same provisional-boundary caveat.
- Writing a good paper record is slow; a bad one is worse than none because it
  looks authoritative.
- **A summary can be confidently wrong.** `checked_against_source` and
  `certainty_reasons` are the mitigations, and neither is automatic.

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

   **RE-EXPRESSED 2026-09-14**, because the restructure in section 2b2 deleted
   `verdict` from the paper record: a paper is not true or false, its assertions
   are. The gate is now on **tier**, which section 2c already defines: a paper
   reaches `read` only when `checked_against_source` is not `never`, and an
   assertion may not be cited in one of our documents unless the paper that
   yields it has reached `read`. Same rule, expressed against a field that
   exists.

   Enforceable because `never` is explicit, so the gate is a comparison rather
   than a null check. An unverified paper may be cited as `unverified` but
   cannot support a decision.

   **Adopted with the expectation that it might chafe**, and the failure mode to
   watch for is a specific one: if the gate makes people record a perfunctory
   check just to clear it, it has made things worse rather than better -- a
   date in a field that nobody honored is weaker evidence than an honest
   `never`. If that starts happening, the right response is to relax the gate,
   not to tighten the wording. Revisit after the seed set is loaded.

## References

- ADR-0014 (Evidence Based Database), F39, F72
- F53 (AutoXGB dataset misattribution), A28 (the Loke et al. prior-work claim)
- Sprint 12: the review agent that correctly rejected its own reviewer's FG22/5 claim
- [`../research/paper-library-prior-art.md`](../research/paper-library-prior-art.md) -- prior-art research, 2026-09-14: the
  collector's fallacy, systematic-review screening tiers, scite's citation-intent
  distribution, and GRADE's derived-certainty model. It is the source for sections
  2c, 2e and 2f, and for the falsifier above
- `docs/references.md`, `docs/research-baselines-best-practices.md`
