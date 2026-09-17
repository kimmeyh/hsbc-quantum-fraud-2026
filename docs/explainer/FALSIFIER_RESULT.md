# Falsifier result: the explain-back test

Task H of Sprint 15 (F73, GitHub issue #108). Run 2026-09-16.

## What the test is, and why it is not "is this clear?"

From the F73 card: *give it to someone who has not read the submission and ask
them to explain back what CVQBoost is and why the result is a null. If they
cannot, the document has not worked, however good it reads.*

**This test cannot be performed by the document's author.** I know what every
sentence means because I wrote it, and fourteen sprints of project context make
"clear" unreadable to me as a signal.

The prompt asked for **explain-back**, not critique. A reviewer asked "is this
clear?" says yes. A reviewer asked "what is CVQBoost?" either knows or does not.

## How it was run

A fresh-context reader with **no repository access beyond the one file**. The
prompt forbade opening the proposal, the appendix, results files, ADRs, or
running any search, and stated that wanting context from elsewhere IS the test.

Seven questions, plus a mandatory "where I got stuck" section naming concrete
passages, plus a self-rated confidence.

## Verdict: PASSED, with six named gaps

The reader answered all seven questions correctly and unaided. Confidence:
**medium-high**.

Correct without help, including the parts that were hardest to write:

- CVQBoost as a crowd of weak voters whose weighting is the only quantum step
- The null's cause located at the voters, not the optimizer: 80 to 84 of 91
  reproduce the training answers exactly, so they are one opinion repeated
- **The clinching measurement, unprompted**: optimizing beat equal weighting by
  0.0028 while meaningless reshuffling of tied voters swung 0.0120, so it is
  tie-breaking rather than improvement
- Why the device could not beat the exact solver, and why ruling that out in
  advance makes the design sharp rather than rigged
- The temporal-split cheat, correctly distinguished from simple memorisation
- Two datasets, with the time span named as the difference that matters
- Both positive results WITH their catches, including the confound

The reader also volunteered the distinction that the machine worked while the
problem was not worth solving, which is the section's hardest point.

## The six gaps, and what was done about each

### 1. CVQBoost was never attributed or expanded. FIXED.

> "Section 5 introduces 'CVQBoost works like this' with no expansion of the
> acronym and no statement of whether it is QCi's product, the project's own
> construction, or a published method from elsewhere. Dirac-3 gets a clear
> attribution to QCi; CVQBoost does not get the equivalent sentence."

Correct and a real omission. The document now says it is an existing published
method that QCi's hardware runs, and that two other groups had tried it on fraud
data first.

**A second error was caught while fixing the first.** My first correction
asserted that CV stands for "continuous variable". The submission never says
that. It says the DEVICE handles "quasi-continuous variables", which is not the
same claim. The text now says the submission does not spell out the letters,
offers the likely derivation explicitly as a guess, and flags that "probably" is
doing real work. This is the third unsourced claim caught in this sprint by
checking rather than by recall.

### 2. Two classical comparisons were never distinguished. FIXED.

> "I had to re-read to convince myself these are two different things... The
> document never puts them side by side and never names the second one."

Correct, and this is the most consequential of the six: a reader who conflates
them cannot tell what the experiment proved. Section 5 now separates them
explicitly. The exact solver tests the DEVICE; an ordinary fraud model tests the
APPROACH. Yes and no, in that order.

### 3. The headline 0.7671 is a random-split number. FIXED.

> "if I am right it is an important qualifier on the headline. I flag it as my
> inference, not something the text says."

The reader was right, and the document had left them to infer it. Section 6 now
states that 0.7671 is the same random-split figure from section 4, that it falls
to 0.7095 under honest time-ordered testing, and that the headline compares two
random-split numbers.

### 4. The 0.8296 gate was unattributed. FIXED.

> "I could not tell whether that measure is AUPRC, and if so which model that
> 0.8296 belongs to, or how it relates to the 0.8070 in section 6. The numbers
> are close enough that I wanted to connect them and could not."

A reader drawing a false connection between two unrelated numbers is worse than
one who is merely confused. It is now named as tuned XGBoost at 0.85 AUPRC, and
explicitly distinguished from the 0.8070 CatBoost.

### 5. Why the rejected configuration was rejected. NOT FIXED, deliberately.

> "left me unsure what it was rejected for, and whether 0.7776 beating the
> 0.8070 classical baseline would change the null."

The answer requires the preregistered selection rule, which needs the frozen
protocol to explain properly. Adding it would cost more comprehension than the
gap does, and the reader still answered question 5 correctly. Recorded as a
known limit rather than patched.

### 6. "Rank-one to numerical precision" as linear algebra. NOT FIXED, by design.

> "I understand the plain-English gloss... I would not be able to explain the
> linear-algebra meaning."

That is the intended outcome. The document promises the gloss, not the linear
algebra. Explaining matrix rank to an 8th grader would be a different document.

## What the result actually establishes

The four fixed gaps share one shape: **the reader understood every mechanism and
tripped on every place two similar numbers were left to be told apart.** Not one
gap was about an idea being too hard. All four were about identity, which of
several similar things a number belonged to.

That is worth recording because it is not what I would have predicted. I flagged
sections 5 and 6 as the hard cases in the sprint plan, expecting the difficulty
to be conceptual. The reader found the concepts fine and the bookkeeping unclear.

## Honest limits of this test

- **Two readers, both language models, neither a 13-year-old.** This is a
  fresh-context check, which is what was available. It is not an audience test. A
  genuine 8th-grade reader would probably stumble in different places, and where
  they stumble remains unknown. That limit is not fixed by running more models.
- **Medium-high both times, not high.** The remaining limit is one the document
  cannot close from its own sources: the submission names no author or citation
  for CVQBoost, so a reader can describe its mechanics but cannot place it in the
  literature.
- **The second run tested where the first one tripped.** That confirms the fixes
  landed; it does not prove the revised text is free of gaps elsewhere, because
  the questions were aimed rather than open.

## Re-test: RUN, and all four fixes confirmed

A second fresh reader, same constraints, questions aimed squarely at where the
first one tripped. All four fixes landed:

- **The two classical comparisons**: answered correctly and unprompted, including
  "yes and no, in that order", plus the third model (XGBoost) correctly set aside
  as not one of the two.
- **The headline 0.7671**: "Random split. The document tells me directly; I did
  not have to infer it." That was the gap the first reader called the one that
  would most embarrass them.
- **The 0.8296 gate**: correctly attributed to tuned XGBoost on AUPRC, correctly
  distinguished from the 0.8070 CatBoost. The reader noted it still cost a
  re-read before reaching the clarifying parenthesis.
- **CVQBoost**: correctly reported as an existing published method QCi's hardware
  runs, correctly reported that the letters are not expanded, and correctly
  treated the CV guess AS a guess. The hedge survived contact with a reader,
  which is what a hedge is for.

Confidence again **medium-high**, now limited by something the document cannot
fix: it names no author or citation for CVQBoost, so the reader could describe
its mechanics but not place it in the literature.

### Two new findings from the re-test, both fixed

**1. "61 runs, 1,141 seconds" and "4 to 5 seconds per fit" do not divide.**

> "61 times 5 is 305, not 1,141. The document does not reconcile these."

The reader was right to stop. Checked against
`experiments/results/qpu_cost_ledger.json`: both figures are true and describe
different things. The ledger's own note validates 4-to-5 as the free-tier
distribution (15 calls at 4.0s, 12 at 5.0s); the campaign average is 18.7 s per
fit because larger problems bill more. Two true numbers adjacent had implied a
false third one. The document now says so explicitly and gives the average.

**2. The two 0.0028 values are unrelated.**

> "I am not certain whether that 0.0028 is the same 0.0028 as the equal-weights
> gap earlier in the section or a coincidental repeat."

Coincidental. One is the gap between solved and uniform weights on the frozen
pool; the other is the standard deviation of the optimizer's contribution on the
rebuilt pool. Same digits, different quantities, and the document now says so.

### What both runs agree on

Every gap either reader found was about **identity**, never about difficulty.
Which model does this number belong to; are these two numbers the same number;
does this figure describe the same thing as the one beside it. Not one reader
said an idea was too hard.

That is the opposite of what the sprint plan predicted. Sections 5 and 6 were
flagged as the hard cases on the expectation that QUBOs and detection thresholds
would be the obstacle. Both readers handled those and tripped on bookkeeping.

**The lesson for the next document of this kind**: budget the care for
disambiguating similar numbers, not for simplifying hard ideas.


---

# Run 3: OPEN questions, 2026-09-17

F80, Sprint 16. IMP-5 from the Sprint 15 retrospective: **aimed runs verify,
open runs discover.** Run 2 asked questions pointed at where run 1 tripped,
which confirms fixes and cannot find anything new. This run used the original
open prompt.

It was also a FIRST reading, not a re-confirmation. The document changed in
three commits after run 2 (the US English sweep and two rounds of CVQBoost
rewrites, including a rewritten QBoost description), so no falsifier had read
the current text.

## Verdict: PASSED at HIGH confidence, the first time

Runs 1 and 2 both landed at medium-high. Run 3 is the first to say high.

The reader answered all seven unaided, and volunteered several things the
document works hardest at: that the machine was not broken and the problem was
not worth solving; that the convex proof makes the device unable to win by
construction; that honest time-splitting reversed the ranking against the
project's own committed choice; and the full QBoost-to-CVQBoost lineage with the
binary-versus-continuous difference and the hardware reason behind it.

It also reported the CV expansion correctly as an inference rather than a fact,
which is the third reader to survive that hedge.

## Four new gaps, three fixed

**1. The 833-voter setup was a dangling forward reference. FIXED.**

> "Section 5 mentions it as 'the large ones (the 833-voter setup in section 6)'.
> Section 6 never mentions 833... If someone asked me 'what was the 833-voter
> run?' I would have to say I am guessing."

Verified: `833` appears in section 5 and NOT in section 6. Section 5 pointed
forward to a number the destination never states. Section 6 now names it and
says what it was: 833 voters looking at three features each, against 91 looking
at one or two.

**2. The three appearances of 0.0017 were never connected. FIXED.**

> "I believe the AUPRC chance baseline equals the base rate, and that is why the
> same digits appear, but the document never says so... The document is
> scrupulous about flagging coincidental digits elsewhere (it does it for the two
> 0.0028s) and does not flag this one, which made me LESS sure rather than more."

That last clause is the sharp observation. Having flagged one digit coincidence,
silence on another reads as significance. And the reader's reasoning was right:
0.17 percent IS 0.0017, and for this measure the guessing floor equals the base
rate. Section 6 now says so, and says explicitly that unlike the two 0.0028s
these really are the same quantity.

**3. The rejected configuration was never described. FIXED.**

Run 1 raised this too and it was recorded as NOT FIXED, on the grounds that
explaining the preregistered selection rule would cost more than the gap. Two
independent readers naming it moves it. The fix turned out to be one clause
rather than a paragraph: it used **nine features instead of thirteen**, and was
rejected because it scored lower on the random split. Verified against the
submission, which says "the rejected 9-feature configuration rose from 0.7014 to
0.7776".

**4. The two classical comparisons resolve retroactively. NOT FIXED.**

> "The bullet pair beginning 'Two different classical comparisons are now in
> play' resolves it, but it arrives after several paragraphs that discuss only
> one of them, so the resolution is retroactive rather than pre-emptive."

Correct, and deliberate. Announcing both comparisons before either is explained
costs more than the re-read: the second comparison only makes sense once the
first has established what "solving the identical problem" means. The reader
resolved it unaided and still reached high confidence. Recorded as a known
shape rather than patched.

## What three runs establish

Run 1 open: six gaps. Run 2 aimed: confirmed four fixes, found two more. Run 3
open: four gaps, three new.

**Every gap across all three runs was about IDENTITY, never difficulty.** Which
model owns this number; are these two numbers the same; does this figure
describe the thing beside it. Not one reader in three said an idea was too hard,
and all three handled the QUBO and detection-threshold material the sprint plan
predicted would be the obstacle.

IMP-5 is confirmed by the evidence: the aimed run found two gaps, both in
territory it was pointed at. The open runs found ten between them, in territory
nobody knew to look at.

## Limits, restated

Three readers, all language models, none a 13-year-old. This is a fresh-context
check and not an audience test. F81 remains the real one and is team-lead owned.
