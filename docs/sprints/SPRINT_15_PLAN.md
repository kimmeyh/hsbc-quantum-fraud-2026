# Sprint 15 Plan: The Submission, Explained

**Sprint**: 15
**Branch**: `feature/20260916_Sprint_15`
**Dates**: 2026-09-16 onward
**Scope**: F73 only
**Metered Dirac-3 seconds**: ZERO. No hardware in this sprint.

## Objective

Produce a learning document that explains the proposal and appendix submitted
2026-09-12 to an 8th grader working alone or in a group of three, structured
like a paper rather than a FAQ.

The submission is 5,847 words written for reviewers who already know what AUPRC
means. This sprint writes the document that makes it reachable by someone who
does not.

## Audience-first statement (mandatory)

**The reader is a 13-year-old who has never heard of quantum computing, machine
learning, or fraud detection, working alone or in a small group.** Not a judge,
not a reproducer, not us in November. They have curiosity and a reading level,
and nothing else.

This matters because every instinct built over fourteen sprints points the wrong
way. The repository's entire quality apparatus rewards precision, hedging, and
traceability to a results row. This reader needs a straight line from "banks
lose money to stolen cards" to "we tried a quantum machine and it did not help,
and here is why that is still worth knowing". Precision that costs
comprehension is a defect in THIS document, which is the opposite of the rule
everywhere else in the repository.

## What already exists, verified 2026-09-16

- `docs/paper/proposal.md` -- 3,653 words, the submitted proposal
- `docs/paper/appendix.md` -- 2,194 words, the submitted appendix
- `docs/research/dataset-reference-licensing.md` -- the F73 licensing pre-flight,
  DONE 2026-09-14
- `experiments/results/*.json` -- every figure the submission quotes
- ADR-0014 section on reading level -- the escalation mechanism this reuses

Nothing here needs to be created before writing can start. This card has no
blocking dependency, which is why it was Priority 1.

## The reading-level rule is borrowed, not invented

ADR-0014 already defines it: start at 8th grade; where an honest explanation is
not achievable at that level, go up ONE grade and retry; record the level that
landed. F73 is a new APPLICATION of an existing mechanism.

**Recording the level is not decoration.** A section that silently drifted to
grade 12 looks identical to one that succeeded at grade 8 unless the number is
written down. The per-section level is the evidence that the rule was followed.

## Tasks

### Task A: Outline, from the three challenge documents (~45m)

F74 was folded into this card, so the outline is Task A rather than a separate
item. Order: the challenge as written, then each dataset, then how ML is done
against each, then what we actually did and found.

Acceptance: an outline whose every heading names what a reader learns there, not
what topic it covers.

### Task B: The problem, before any technique (~60m)

What card fraud is, why it is hard, and why "just catch the fraud" is not a
solvable instruction. Introduces class imbalance WITHOUT the term: 0.17%
prevalence means about 17 frauds in 10,000 transactions. (Verified 2026-09-16:
0.17% of 1,000 is 1.7, not 2, so the example uses 10,000 to stay exact. A
rounded number in the section whose whole purpose is explaining a rate honestly
would undercut the section.)

Acceptance: explains why accuracy is the wrong measure, using a worked count, in
under 400 words and with no jargon.

### Task C: The three datasets (~90m)

ULB, IEEE-CIS, SPECTRA: what each is, how it was gathered, what it represents,
why we used it, and what its key features are.

**Licensing is settled and constrains the writing**: ULB is DbCL v1.0 and may be
copied. IEEE-CIS is Vesta competition data and must be paraphrased and cited,
never copied. SPECTRA is unverified. Per the pre-flight's own conclusion, every
dataset explanation is written in our own words regardless, because one reuse
right out of three is not worth the inconsistency.

Acceptance: each dataset attributed with its licence; no copied text from any of
the three; a reader can say what each dataset contains.

### Task D: How machine learning predicts from a table (~90m)

Features, training, testing, and why testing on data you trained on is cheating.
Then the temporal split, which is the part the submission treats as obvious and
a new reader will not.

Acceptance: a reader can explain why a random split on time-ordered data
flatters the result. This is the single idea most load-bearing for understanding
our null.

### Task E: What CVQBoost is and what we measured (~90m)

The quantum part, last rather than first. What the Dirac-3 machine does, what a
QUBO is in plain terms, and what "the classical proxy solves the identical
Hamiltonian" means and why it is the whole experiment.

Acceptance: a reader can state what was compared against what.

### Task F: The null result, and why a null is worth publishing (~60m)

The result is that it did not help. This section has to land that as a finding
rather than a failure, without overclaiming in either direction.

Acceptance: a reader can explain why a null is useful.

### Task G: Disclaimer, level recording, and assembly (~45m)

The team lead's required wording: a good and reasonably accurate document, with
no guarantee of 100% accuracy and no expectation that the reader will fully
understand it on first reading.

Acceptance: disclaimer present; every section states the grade level it achieved.

### Task H: Run the falsifier (~30m)

See below. Not optional and not self-assessed.

## Premise falsifier (mandatory)

**Premise**: the document explains the submission to someone who has not read it.

**The check cannot be performed by its author.** I know what every sentence
means because I wrote it, and fourteen sprints of context make "clear" unreadable
to me as a signal. Self-assessment here is structurally worthless.

**The test, from the card**: give it to someone who has not read the submission
and ask them to explain back what CVQBoost is and why the result is a null. If
they cannot, the document has not worked, however good it reads.

**How it gets executed**: a fresh-context reader with NO repository access --
the same mechanism as the Sprint 3 fresh-eyes evidence review, which caught the
score degeneracy precisely because it lacked context. The prompt asks for
explain-back, not for a critique. A reviewer asked "is this clear?" says yes; a
reviewer asked "what is CVQBoost?" either knows or does not.

**A measurable grade level is not the falsifier.** A readability score measures
sentence length and syllables. It cannot detect a paragraph that is short, simple
and meaningless. Both checks run; only the explain-back can fail for the right
reason.

## Risks

- **The author cannot judge the outcome.** Mitigated by Task H, which is why it
  is a task rather than a closing step.
- **Precision instinct fights the audience.** Every other document in this
  repository is graded on traceability. Here, a hedge that costs comprehension is
  the defect.
- **Scope creep into a textbook.** The document explains THIS submission, not
  machine learning generally. The outline is the boundary.
- **The disclaimer gets softened in editing.** It is the team lead's wording and
  is quoted, not paraphrased.

## Definition of Done

- Every section states the grade level it achieved
- The disclaimer is present in the team lead's wording
- Every dataset is attributed with its licence, none copied
- The falsifier has been RUN, with its result recorded including a failure
- A reader with no quantum or ML background can follow the argument from problem
  to null result
- Suite green; CHANGELOG updated; three-doc rule satisfied at close-out

## Out of scope

- Any Dirac-3 hardware run. Zero metered seconds this sprint.
- F78 (PowerShell to Python). Real and separately scoped; it touches `.claude/`
  and should not share a sprint with a writing task.
- Re-opening any submitted figure. The submission is filed and frozen; this
  document explains what was submitted, and a discrepancy found while writing is
  a FINDING to report, not an edit to make.

## Estimate

8 tasks, ~8.5 hours. The card estimated 6-10h and the task breakdown lands
inside it.
