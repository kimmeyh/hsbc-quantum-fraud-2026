# How Cyc represents and maintains knowledge

Research for the Evidence Based Database (F39, ADR-0014), 2026-09-13.

**Every claim below is cited to a primary source and was read directly.** Where
I could not verify something, it is in the "What I could not establish" section
rather than stated with false confidence. Two of my prior beliefs were WRONG and
are corrected here.

## Sources

- Lenat, D. and Marcus, G., *Getting from Generative AI to Trustworthy AI: What
  LLMs might learn from Cyc*, arXiv:2308.04445, 31 July 2023. Read in full,
  pages 1-16. Cited below as **[LM23]** with page numbers.
- Cycorp glossary, <https://cyc.com/glossary/> and
  <https://cyc.com/archives/glossary/truth-value/>. Cited as **[Glossary]**.

## Corrections to what I previously believed

**1. There are FOUR composite truth values, not five.** I had said five,
including "unknown". [Glossary, truth-value] gives four: `monotonically true`,
`monotonically false`, `default true`, `default false`.

They are not a scale. They are the cross-product of two independent
epistemological properties:

> "'Truth value' is a heuristic level property; it is a combination of what are
> 2 separate properties at the epistemological level: strength (exception
> status: having them, vs. not) and negation status (whether or not a formula
> begins with #$not)." [Glossary]

An assertion starts monotonically true and **moves to default true when an
exception is found**:

> "Assertions that gain exceptions will have their HL truth value changed to
> 'default true' ... and will have their truth value reported in the Browser as
> 'has exceptions'." [Glossary]

**2. Cyc does NOT carry numeric confidence on assertions.** I had been unsure.
The glossary has no entry for confidence, probability or certainty, and the
paper never mentions a per-assertion numeric degree of belief. The closest thing
is the four-value truth lattice plus argument preference (below).

This matters directly: **the 0.0-99.9% confidence field in F39 is OUR design,
not something inherited from Cyc.** It should be justified on its own merits.

## The architecture, and the one idea worth stealing

### Epistemological Level versus Heuristic Level

This is the central engineering move, and it is the answer to "how do you reason
over millions of assertions without stalling":

> "Cyc addresses this by separating the *epistemological* problem -- what does
> the system know? -- from the *heuristic* problem -- how can it reason
> efficiently? Every Cyc assertion is expressed in a nice, clean, expressive,
> higher order logic language -- the Epistemological Level (EL) language, CycL
> -- on which, in principle, a general theorem prover could operate. Slowly.
> Very very slowly. But Cyc also allows multiple redundant representations for
> each assertion, and in practice it uses multiple redundant, specialized
> reasoners -- Heuristic Level (HL) modules -- each of which is much faster than
> general theorem-proving when it applies." [LM23 p13]

**By 1989 Cyc had 20 such reasoners; today it has over 1,100.** [LM23 p13]

How they interact:

> "When confronted with a problem, all 1,100 reasoners are effectively brought
> to bear, and the most efficient one which can make progress on it does so, and
> the process repeats, over and over again ... until the problem has been fully
> dealt with or resource bounds have been exceeded." [LM23 p14]

And resource budgeting is explicit:

> "it budgets resources, depending on the application (e.g., acceptable wait
> times during a conversation with a person), and interrupts reasoners who
> exceeded their bid on how long they would take, and simply won't bother
> calling on reasoners who know they will take too long." [LM23 p14]

### The admission in footnote 9, which is the most useful thing in the paper

Lenat, in his own voice:

> "Something we don't often talk about: We noticed empirically that the general
> theorem-proving reasoner actually took so long that over a million queries in
> a row that called on it, as a last resort, just timed out. Going back farther,
> we saw that that had happened for decades. So, about one decade ago, we
> quietly turned the general theorem prover off, so it never gets called on!"
> [LM23 p14, footnote 9]

**The fully general reasoner was never once useful in a million consecutive
queries.** Everything Cyc actually does is done by specialised shortcuts. That
is the strongest possible evidence for designing heuristics in from the start
rather than treating them as an optimisation over a "proper" general method.

### How a heuristic gets created

Not by theory. By watching a human who is faster:

> "When Cyc is applied to a new practical application, it is sometimes the case
> that even when it gets the right answers, its current battery of reasoners
> turns out to be unacceptably slow. In that case, the Cyc team shows to the
> human experts ... Cyc's step by step reasoning chain and asks them to
> introspect and explain how they are able to avoid such cumbersome reasoning.
> The result is often a new special-purpose Heuristic-Level reasoner, possibly
> with its own new, redundant representation which enables it to run so
> quickly." [LM23 p14]

### The trap they name themselves

> "The trap the Cyc team fell into was assuming that there would be just one
> representation for knowledge ... Committing to that meant vainly searching for
> some fast general-purpose reasoning algorithm over HOL, which probably doesn't
> exist." [LM23 p14]

**Redundant representations of the same fact are a feature, not duplication.**

## Contexts (microtheories)

> "Each Cyc context, also called a Microtheory, has a set of domain assumptions
> which can be thought of as conjuncts for each of the assertions in that
> context. Because the common assumptions are factored out, the assertions in
> that context turn out to be much terser, and the reasoners are thereby able to
> operate very efficiently within the same context. E.g., consider the 2023
> context: every assertion and rule doesn't need to start out 'In the year
> 2023,...'." [LM23 p15]

- **About 10,000 named contexts** today, kept down by functions that COMPUTE
  contexts (e.g. `IntersectContexts`) rather than reifying every combination.
  [LM23 p15]
- Contexts are **first-class terms**: you can assert rules *about* contexts.
  [LM23 p15]
- Each microtheory must be internally consistent; the KB as a whole need not be.
  [Glossary]

**This is the mechanism for the project-versus-world-facts separation.** It is
not a tag on a record; it is a context with factored-out assumptions, which is
both cleaner and faster.

## Defeasibility and argumentation

> "Almost all knowledge in Cyc's KB is merely true-by-default. ... What this
> means is that Cyc typically can find multiple 'proofs' for an answer, and even
> multiple 'disproofs' for the same answer. Those are in quotes because these
> are really just alternative lines of reasoning, pro- and con- arguments. That
> means that **Cyc reasoning is based around argumentation, not proof**."
> [LM23 p15, emphasis added]

And how competing arguments are resolved -- note there is no arithmetic here:

> "Cyc gathers all the pro- and con- arguments it can find for all the answers
> that have at least one pro- or con- argument, and then applies meta-level
> rules to decide which arguments to prefer over which others. E.g., more
> specific ones trump more general ones." [LM23 p16]

The desiderata list gives the heuristics people use for the same job:

> "prefer recent ones to stale ones, short ones to long ones, expert ones to
> novice ones, constructive ones to nonconstructive ones" [LM23 p5, item 10]

## Provenance and explanation

Desideratum 1 is *Explanation*, and it sets a bar this project should recognise:

> "A trustworthy AI should be able to recount its line of reasoning behind any
> answer it gives. Asking a series of repeated *Why is that?* follow-up
> questions should elicit increasingly fundamental knowledge and 'given' ground
> truths. Each piece of evidence, knowledge, rule of thumb, etc. invoked in that
> reasoning chain should also have its source or provenance known. **This is a
> higher standard than people hold each other to, most of the time, but is
> expected in science** and whenever there is a very important decision such as
> one involving family healthcare, finance, and so on." [LM23 p3]

Delivered as:

> "The Cyc reasoner produces a complete, auditable, step-by-step trace of its
> chain of reasoning behind each pro- and con- argument it makes, including the
> full provenance of every fact and rule which was in any way used in each
> argument." [LM23 p13]

Desideratum 12, *Meta-knowledge*, is the one that names our exact failure mode:

> "**Wild guesses should not be advanced as blithely as those supported by
> strong arguments.**" [LM23 p6]

## Scale and authorship

- **"Tens of millions of assertions"**, essentially all hand-authored.
  [LM23 p11, p12]
- **2,000 person-years** over four decades. [LM23 p13]
- Larger teams made it WORSE: "Cycorp's experiments with larger-sized teams
  generally showed a net *decrease* in total productivity, due to lack of
  coherence, deeper reporting chains". [LM23 p13]
- Each axiom is hand-checked "for default correctness, generality, and best
  placement into the microtheories (contexts) it applies to". [LM23 p11]
- **Most "facts" are deliberately NOT in the KB**: "most of the 'facts' Cyc
  knows are ones that it can just look up on the internet much as a person
  would, or access in databases where the schema of the database has been
  aligned to Cyc's ontology". [LM23 p11]

That last point is a direct argument about scope: Cyc stores *rules of thumb*,
not a fact dump, and looks the facts up.

## Generalisation before entry

The authoring discipline is worth copying:

> "it was important that they *generalize* each nugget before entering into
> Cyc's knowledge base. Suppose the original axiom they jot down is 'different
> horses don't share a leg'; a good default-true generalization of that might be
> 'different physical objects don't share physical parts'. Further
> generalization is questionable." [LM23 p12]

And contradiction-on-entry is treated as informative, not as an error:

> "Another useful Cyc-powered tool calls the ontologist's attention to any
> existing knowledge Cyc has that appears to contradict this new assertion.
> That's usually a good thing to happen, not a bad one: it points the ontologist
> to tease apart the *contexts* in which each axiom applies." [LM23 p12]

## What I could not establish

- **Whether any numeric confidence exists anywhere in Cyc.** Absent from the
  glossary and from this paper. I did not find a contradicting source, but
  absence of evidence is not proof; a Cycorp technical manual might say more.
- **Truth maintenance mechanics.** How a retraction propagates to conclusions
  already derived from it. The paper says arguments are recomputed rather than
  cached as truths, but does not describe the machinery.
- **Anything after mid-2023.** This paper is the most recent primary source I
  read. OpenCyc was discontinued around 2017 and Cyc is proprietary.
- **The 0.0-99.9% confidence range** in the Sprint 8 note appears to be the team
  lead's framing, not Cyc's. I found no Cyc source for those bounds.

## What this means for the Evidence Based Database

Seven things worth carrying, and two worth deliberately NOT carrying.

**Carry:**

1. **EL/HL separation.** Store the honest, expensive form; add fast redundant
   representations for the queries that actually get asked. A precomputed
   answer is not a cache hack, it is the architecture.
2. **Contexts over tags** for project-versus-world facts. Factor the shared
   assumptions out rather than stamping every record with a label.
3. **Argumentation over proof.** Records can support AND oppose a claim, and
   the resolution is meta-rules, not averaging.
4. **Preference heuristics by name** (specific over general, recent over stale,
   expert over novice) rather than a single score.
5. **Provenance on every step**, which this project already half-does via
   evidence tags.
6. **Generalise before entering**, and treat a contradiction on entry as a
   context question rather than an error.
7. **Look facts up rather than storing them** where a lookup is reliable. Our
   amendment count should be COMPUTED from the preregistration, never stored.

**Do not carry:**

8. **The general theorem prover.** Turned off for a decade after a million
   consecutive timeouts. Do not build the general case first.
9. **Hand-authoring at Cyc's scale.** 2,000 person-years is the cost of
   world-modelling. Our scope is 151 records and a bounded set of assertions,
   which is why this is tractable at all.
