# Paper libraries: what others found valuable

Research for ADR-0015, 2026-09-14, prompted by the team lead's note that the
library will eventually hold **more than 2,000 papers, many of which we will
reject but must look at first**.

That number changes the design. A 50-paper library is a reading list; a
2,000-paper library is a screening problem with a reading list inside it.

## Sources

- scite (smart citations): Nicholson et al., *Quantitative Science Studies* 2(3),
  and scite's own documentation. The MIT Press full text returned 403; figures
  below come from scite's documentation and the search summary of that paper,
  and are marked as such.
- GRADE: Cochrane Handbook ch. 14; CDC ACIP GRADE Handbook ch. 7; NHMRC
  guidance.
- Screening automation: *Systematic Reviews* 12 (2023) on active-learning
  prioritisation; ScienceDirect on certainty-based screening; PMC12306261 on LLM
  screening prompts in a living systematic review.
- Failure modes: zettelkasten.de, "The Collector's Fallacy".
- Tool landscape: comparisons of Elicit, Semantic Scholar, Connected Papers,
  Litmaps, ResearchRabbit, scite.

## 0. READ THIS FIRST: the prior art assumes human readers, and we do not have them

**Correction, team lead, 2026-09-14**, recorded at the top because it changes how
every section below should be read:

> "ours is different. There are not people looking at each paper, we are a
> single agent looking at each paper with many running in parallel and at 1% of
> the speed or less."

Nearly all the literature below -- the collector's fallacy, systematic-review
screening economics, workload-reduction percentages -- measures cost in HUMAN
ATTENTION. That is the scarce, serial, procrastination-prone resource those
findings are about. An agent has none of those properties, so the effort
arithmetic does not transfer, and my original "333 hours" framing in section 1
was wrong for exactly that reason.

**What still transfers** is anything not about attention cost:

- a library nobody reaches for is useless however cheaply it was built, and
  reaches uselessness FASTER at agent speed;
- maintenance decay does not care who wrote the record;
- **volume without judgment gets WORSE**: 2,000 confident-sounding
  unadjudicated records look authoritative and scale the error.

The surviving scarce resource is **team-lead adjudication**, not drafting. Read
the sections below with that substitution in mind.

## 1. The finding that should worry us most (AS WRITTEN; see section 0)

**The dominant failure of paper libraries is not bad records. It is collecting
instead of thinking.**

> "The Collector's Fallacy is the mistaken belief that having a text at hand
> increases our knowledge." [zettelkasten.de]

The reported failure modes are consistent across sources and none of them is
technical:

- **No purpose.** A system built with a vague notion of what it is for, with no
  feedback mechanism, producing nothing.
- **Processing overhead.** "What could be a 10-second capture becomes a
  10-minute processing session" -- a part-time job across dozens of captures.
- **Research mode as procrastination.** Collecting feels like progress and is
  not.
- **Maintenance burden** that never converts into usable output.

**This is the single biggest risk to a 2,000-paper library**, and ADR-0015 as
written does nothing about it. Every field I specified makes a record BETTER and
also makes it SLOWER to write. At 2,000 papers, a 10-minute record is 333 hours.

The mitigation is not a better schema. It is **tiering**: most papers should
never get a full record.

## 2. Tiered records, from systematic-review practice

Systematic reviews solved this exact problem. They screen thousands of titles to
include dozens, and they do it in stages where each stage is cheaper than the
next.

Reported workload reductions from screening automation:

- "a saving in workload of between 30% and 70% might be possible, though
  sometimes accompanied by the loss of 5% of relevant studies"
- LLM screening prompts in a living review: "100% sensitivity for studies
  ultimately included after full-text screening, with simulated workload
  reductions of 65-85%"
- Text-mining prioritisation "should be considered safe and ready for use in
  'live' reviews"

The 5% loss figure matters: **screening automation trades recall for effort, and
the trade should be explicit.** For us the stakes are low -- a missed paper is
not a missed treatment effect -- so a prioritisation ordering is safer than an
automated exclusion.

**Proposed tiers**, cheapest first:

| Tier | Fields required | Effort | Expected share of 2,000 |
|---|---|---|---|
| `seen` | id, citation, access, one-line why-not, date | < 1 min | most |
| `screened` | + claim, applicability, verdict, confidence | ~5 min | some |
| `read` | + evidence, checked_against_source, contradicts, notes | 20 min+ | few |

A record at `seen` is a legitimate record. **The point is that rejecting a paper
leaves a trace**, so the same paper is not re-screened in six months -- which is
the actual recurring cost at this scale.

## 3. Citation intent: scite's three classes, and what their distribution reveals

scite classifies every citing statement as **supporting**, **contrasting**, or
**mentioning**, over 1.6 billion citation statements.

The distribution is the interesting part:

> **92.6% mentioning, 6.5% supporting, 0.8% contrasting**

**Disagreement is almost never recorded in the literature.** Less than one
citation in a hundred contests what it cites. That is not because papers rarely
conflict; it is because contesting is costly to write and easy to omit.

**Direct implication for us.** ADR-0015 has `contradicts-us` as a verdict, and
the team lead has asked for a `contradicts` link to specific assertion ids.
scite's distribution says such links will be **rare and disproportionately
valuable** -- they are the records that do work no citation count can do.

It also suggests a second link type. scite has three classes and we have one.
**A `supports` link is worth having alongside `contradicts`**, because "which
papers back this claim" is the question we will actually ask when writing Phase
2 documents.

## 4. GRADE: certainty as a derived value with named reasons

GRADE is how clinical medicine grades a body of evidence, and its structure is
better than a bare confidence number.

- Four levels: **high, moderate, low, very low**.
- **Different starting points by study type**: randomized trials start HIGH,
  observational studies start LOW.
- **Five named downgrade reasons**: risk of bias, inconsistency, indirectness,
  imprecision, publication bias. One level for serious concerns, two for very
  serious.
- **Three named upgrade reasons** for non-randomized work: large effect,
  dose-response, opposing plausible confounding.
- A floor: "regardless of how many reasons there are to downgrade, the certainty
  of the evidence cannot fall below very low".

**Why this is better than a percentage.** A record saying `confidence: 62%`
cannot be argued with. A record saying *started high because measured on
hardware; downgraded one level for imprecision, single seed* can be checked,
disputed, and corrected. **The reasons are the audit trail.**

This maps onto what this project already does. Our evidence tags set the
starting point -- `[HW]` measured on hardware starts higher than `[PROJ]`
projected -- and our existing caveats are downgrade reasons in all but name: the
score-degeneracy caveat is imprecision, the single-seed spot checks are
imprecision, the adversarial control that never converged is risk of bias.

**Recommendation: keep `confidence` but make it DERIVED and require the
reasons.** Not a number someone picks.

## 5. Features worth stealing from the tool landscape

| Feature | Seen in | Worth it? |
|---|---|---|
| Structured extraction into named columns | Elicit | **Yes.** This is exactly our `claim` / `evidence` / `applicability` fields |
| Citation-graph traversal to find foundational work | Connected Papers, Litmaps, ResearchRabbit | **Later.** This is the graph-store trigger from ADR-0014, and it is the likeliest to fire |
| AI-generated TLDR per paper | Semantic Scholar | **Yes**, as a draft. Agent-drafted, human-adjudicated is already our model |
| Citation context stored with the citation | scite | **Yes.** Store the SENTENCE that makes the claim, not just the id |
| Free well-documented API for metadata | Semantic Scholar (200M+ papers) | **Yes.** Never hand-type a citation that an API can supply |
| Research feeds tracking new publications | Semantic Scholar, Litmaps | **Later.** Only once the library is maintained rather than built |

The last row is the discipline: features that help you FIND more papers are
worthless until the intake problem is solved, and actively harmful if they feed
the collector's fallacy.

## 6. What I did NOT find, and would want before building

- **No source establishes that a private, hand-curated paper library outperforms
  just searching Semantic Scholar when you need something.** That is the honest
  null hypothesis for this whole card, and it deserves a stated falsifier.
- **No evidence on maintenance decay** -- how quickly such libraries go stale
  once the initial burst ends. This is the failure I would bet on.
- The scite paper's own stated limitations. The full text returned 403, so the
  accuracy figures for the classifier come from secondary summaries and should
  be treated as approximate.

## 7. Recommendations for ADR-0015

1. **Add tiers** (`seen` / `screened` / `read`). The single most important
   change. Without it, 2,000 papers is 333 hours.
2. **Make `confidence` derived**, GRADE-style: a starting level from the
   evidence tag, plus named downgrade and upgrade reasons. Reasons are required;
   the level is computed.
3. **Add `supports` alongside `contradicts`**, both linking to assertion ids.
   scite's 0.8% says these will be rare and valuable.
4. **Store the citation CONTEXT** -- the sentence making the claim -- not just
   the identifier.
5. **Pull metadata from an API**, never by hand.
6. **State a falsifier for the whole card**: if, after N papers, we are not
   reaching for the library when writing, it is not working and should be
   scrapped rather than maintained out of sunk cost.
7. **Defer citation-graph traversal** to the ADR-0014 graph trigger.
