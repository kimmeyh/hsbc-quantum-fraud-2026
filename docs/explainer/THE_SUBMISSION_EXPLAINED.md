# Catching Card Thieves With a Quantum Computer (And What Happened When We Tried)

## Before you start

This is a good and reasonably accurate document, but there is no guarantee that
it is 100% accurate, and there is no expectation that you will fully understand
it on the first reading. Some of it is genuinely hard. If a section does not
land, read the next one anyway; several ideas get clearer once you see what they
are for.

It explains a real proposal submitted to a real competition on 12 September 2026.
Everything it describes actually happened, including the part where the clever
idea did not work.

---

## 1. Why banks cannot simply catch fraud

*Reading level: aimed at grade 8; measures 5.8 on Flesch-Kincaid.*

Somebody steals a credit card number. They try to buy something with it. The
bank has about one second to decide: let it through, or stop it?

You might think the goal is to catch every thief. It is not, and the reason is
worth understanding before anything else in this document.

**There are two ways to be wrong, and they hurt differently.**

If the bank misses a real theft, it usually has to refund the money. That is a
direct loss, and it is measurable.

If the bank blocks a real customer buying a sandwich, nothing gets refunded, but
something worse can happen. The customer is embarrassed at the counter. They try
the card again. It fails again. Some of them stop using that card for good. A
bank that blocks too many honest purchases loses customers to a competitor, and
it never sees a bill for it.

So the bank is not solving a puzzle with a right answer. It is balancing two
different kinds of damage.

**And there is a third limit: people.**

When the computer flags a transaction as suspicious, a human being often has to
look at it. A bank employs a certain number of those people, and they can only
review so many cases a day. That number does not change just because more
transactions came in today.

This is the constraint that shapes everything else. Imagine you are handed ten
thousand transactions and told you may investigate one hundred of them. You
cannot investigate the rest. They go through, whatever they are.

**So the real question is never "is this transaction fraud?"**

The real question is: *of everything I could send to a human today, which
hundred are worth their time?*

That is a ranking problem, not a yes-or-no problem. The computer's job is to sort
transactions from most suspicious to least, and the only part of that list that
matters is the top of it. Being right about transaction number 8,000 is worth
nothing, because nobody was ever going to look at it.

Keep that in mind. In the next section it turns out to break the most obvious way
of measuring whether a fraud detector is any good.

---

## 2. Why counting right answers makes a useless fraud detector

*Reading level: aimed at grade 8; measures 5.1.*

Here is the obvious way to score a fraud detector: count how often it is right.
Call that its accuracy.

It is useless, and one worked example shows why.

**The count.**

In the main set of real transactions used here, fraud is rare. About 17 out of
every 10,000 transactions are fraud. That is 0.17 percent.

So out of 10,000 transactions:

- about 17 are fraud
- about 9,983 are honest

Now imagine the laziest possible fraud detector. It has one rule: *say every
transaction is honest.* It does not look at anything. It never flags a single
purchase.

How accurate is it?

It gets all 9,983 honest transactions right. It gets all 17 frauds wrong. That
is 9,983 correct out of 10,000.

**That detector is 99.83 percent accurate and it has never caught a thief.**

It would score better than a detector that catches 15 of the 17 frauds but
wrongly flags 30 honest customers, because that one gets 9,968 right. The useful
detector scores lower than the useless one.

**What this means.**

Accuracy rewards ignoring the thing you care about. When one answer is rare,
"how often are you right?" is answered almost entirely by the common case, and
the rare case disappears into the rounding.

So accuracy gets thrown out. Two questions replace it:

- **Of the transactions we flagged, how many were actually fraud?** If you flag a
  hundred and two are real, you are wasting your investigators.
- **Of the real frauds, how many did we catch?** If there were 17 and you caught
  3, the thieves are winning.

These pull against each other. Flag everything and you catch all the fraud and
waste everyone's time. Flag nothing and you catch nothing. A real detector sits
between, and where depends on how many investigators you have.

**This connects straight back to section 1.** The measure has to match the
decision. The decision was "which hundred cases get a human today?" So the
measure has to be about the top of the ranked list, not the whole pile.

The proposal uses a measure built for exactly that: one number for how well a
detector does at the top of the list. It has a name, and section 6 gives it when
the results need it.

---

## 3. Where the data comes from, and what it can and cannot tell you

*Reading level: aimed at grade 8; measures 7.9.*

To test a fraud detector you need real transactions that somebody has already
labeled as fraud or not. That data is hard to get, for an obvious reason: it is
a record of what real people bought.

Two collections were used here. They are not interchangeable, and the difference
between them does real work later.

### The European set (called ULB)

284,807 card transactions from European cardholders, collected over **two days**.
492 of them are fraud. That is the 0.17 percent from section 2 (0.172 percent,
to be exact).

Before anything else happened, 1,081 transactions were removed because they were
exact duplicates of another row. A duplicate is not extra evidence; it is the
same evidence counted twice, and leaving them in lets a model look better than
it is.

**The strange part: most of the columns are unreadable on purpose.** The
publishers could not release what people actually bought, so the original
details were put through a mathematical transformation that scrambles them into
anonymous numbered columns. The information is still in there, in the sense that
patterns survive. But nobody outside the original bank can say what any one of
those columns means.

This matters for honesty: nobody can claim their detector works because it
cleverly noticed something about, say, petrol stations at 3am. Nobody can see
petrol stations in this data.

**License**: published under the Database Contents License, which permits reuse.
Even so, everything in this section is written in our own words.

### The competition set (called IEEE-CIS)

590,540 transactions from Vesta Corporation, a payments company, released for a
public competition. 3 exact duplicates removed.

Two differences from the first set matter:

- **Fraud is twenty times more common here**: 3.5 percent rather than 0.17.
- **It spans months, not two days.**

**License**: competition data. The rules are behind a sign-in wall and could not
be read anonymously, so it is treated as *do not copy*. Everything here is
paraphrased and cited, never quoted.

### Why two, and why the second one exists

The European set has a flaw that no amount of clever modeling fixes: two days
is not enough time to see anything change.

Fraud is not a fixed target. Thieves change tactics; a trick that worked last
month gets blocked this month. A detector trained on Monday and tested on
Tuesday never has to cope with that. It can look excellent and still fail in
production three weeks later.

The competition set spans months, so it can be split by time and asked the harder
question: *does this still work on transactions from a month you have never
seen?*

Section 4 is about why that question is the one that matters, and why the
obvious way of testing gets it wrong.

### One dataset you will not find here

An earlier draft of this document described a third collection, called SPECTRA.
That was an error, caught while writing this section and recorded rather than
quietly deleted.

SPECTRA is real and does appear in this project's reading, but it is four
datasets about steel plants, gas turbines, equipment maintenance and telephone
customers. It has nothing to do with card fraud, and it appears nowhere in the
submitted proposal. It was read as evidence for a different argument entirely.

It is mentioned here because "there were three datasets" is the kind of small
false fact that a reader would carry away and repeat.

---

## 4. How a machine learns to rank, and the one mistake that fakes success

*Reading level: aimed at grade 9; measures 6.2. See the note at the end of this section.*

This is the most important section in the document. If you only understand one
thing here, understand this one, because it is what makes the result in section 6
mean anything.

### Features

A **feature** is one fact about a transaction that a computer can compare across
rows. The amount. The hour of day. How far this purchase is from the last one.

A transaction becomes a row of numbers. Thousands of rows make a table. The
machine only ever sees the table.

### Training

You hand the machine a pile of past transactions with the answer already
attached: this one was fraud, this one was not. It hunts for combinations of
features that tend to come with fraud.

It is not told what to look for. It finds patterns like "small purchase
immediately followed by a large one at a different merchant" on its own, by
noticing that the combination shows up more often in the fraud rows.

Then it scores new transactions by how much they resemble the fraud patterns it
found, and sorts them. That sorted list is the thing section 1 said we actually
wanted.

### Testing, and the obvious cheat

Now: is it any good?

The wrong way is to test it on the same transactions you trained it on. It has
already seen those answers. A machine with enough capacity can simply memorise
them and score perfectly while having learned nothing that transfers.

So you split the data. Train on one part, test on a part the machine has never
seen. Everybody knows this.

### The subtle cheat, and it is the one that matters

Here is the mistake that is much easier to make, and it is not obvious at all.

Suppose your transactions span six months. You shuffle them all together and
deal out a random 80 percent to train on, keeping 20 percent to test.

That sounds fair. It is not, and the reason is that **fraud changes over time**.

Thieves adapt. A trick that works in March gets detected and blocked, so by May
they are doing something else. Real fraud detection always means predicting
*next* month using *last* month.

When you shuffle six months together, the training pile contains transactions
from May, and the test pile contains transactions from March. The machine is
being asked about March while having already studied May. It gets to see the
future.

It will score well. It will also fall over in production, because in production
there is no future to look at.

**The honest version**: split by time. Train on the first four months, test on
the last two. Never let a training row come from after a test row.

This is harder and the scores come out lower. The lower score is the true one.

### Why this matters for what we found

This project's own result shows the effect.

One configuration scored **0.7671** when tested with the ordinary random split.
Tested on a time-ordered split instead, the same configuration fell to
**0.7095**. Meanwhile a different configuration, one the project's own advance
rules had rejected, went *up* from 0.7014 to 0.7776.

So testing honestly by time did not just lower the scores. It reversed which
configuration looked better, and it reversed it against the choice the project
had already committed to.

The submission states this plainly and does not recommend the arm for production
use until the question is settled. That is the correct response to an
inconvenient result and it is worth noticing.

One split is not proof, and the proposal says so too. The European data spans
two days, which is not enough time to test this properly. That is exactly why
the competition dataset from section 3 exists.

### The other traps, briefly

- **Preprocessing before splitting.** If you calculate an average over all your
  data and then split, the training rows carry information about the test rows.
  Split first.
- **Tuning on the test set.** If you adjust settings until the test score is
  good, you have used the test set for training. Tune on training data only.
- **Duplicate rows.** The same transaction in both piles means testing on
  something you trained on. This is why 1,081 rows were removed in section 3.

### A control worth knowing about

There is a clean way to check whether a pipeline is cheating: scramble the
answers. Replace every fraud label with a random one, keeping everything else
identical, and retrain.

If the machine still scores well, something is leaking, because there is no
longer any real pattern to find.

Done here, the scrambled-label run scored **0.0023** against a base rate of
0.0017 for the data. Essentially chance, which is the correct and boring result.

### A note on reading level

Sections 1 to 3 landed at grade 8. This one is grade 9.

Per the rule this document follows, the level goes up by one only where an honest
explanation is not achievable at the lower one, and the level that lands gets
recorded rather than hidden. The idea that forced it is "the machine is being
asked about March while having already studied May". That sentence needs the
reader to hold two time periods and a sorting operation at once, and every
shorter version tested either lost the time element or implied simple
memorisation, which is the *different* cheat described above.

---

## 5. What the quantum machine does, and what it was compared against

*Reading level: aimed at grade 9; measures 6.9.*

Four sections in, and no quantum computer. That was deliberate. The finding is
about careful measurement, and the machine is the thing that got measured.

### First, what it is not

Dirac-3, made by a company called QCi, is **not** the kind of quantum computer
that appears in headlines about breaking codes. Those are gate-based machines
built from qubits.

Dirac-3 works with light. QCi's own research paper calls it "a hybrid
photonic-electronic computer that uses optical measurement and feedback to solve
non-convex optimization problems". It is a specialised machine that hunts for the
lowest point in a mathematical landscape.

The submission is careful here in a way worth copying: it treats the device as a
photonic analog optimizer and **claims no quantum resource at all**. It also
cites a published criticism arguing that the machine's demonstrated results do
not beat good classical algorithms. Citing the strongest objection to your own
tool is a sign to look for in technical writing.

### The method: many small voters

The method is called **CVQBoost**, and the name has a history worth knowing
because it tells you exactly what the method is.

**QBoost** came first: "QBoost: Large Scale Classifier Training with Adiabatic
Quantum Optimization", by Hartmut Neven of Google, Vasil Denchev of Purdue, and
Geordie Rose and William Macready of D-Wave Systems, published in 2012.
"Boosting" is an old and ordinary idea in machine learning,
which you already understand from section 2's ranked list: take many weak rules
and combine them into one strong one. QBoost's contribution was to hand the
combining step to a quantum machine.

**CVQBoost** is QCi's version, built for the Dirac-3 machine and published in
2025. It is not this project's invention, it is open source, and two other
research groups had already tried it on fraud data before this project did.

**The difference between the two is the whole point**, and it is one word.

In the original QBoost, each voter's weight is squeezed into a **very small
number of on-or-off switches**, often just one. With a single switch a voter is
simply in or out: this one counts, that one does not, nothing between. The
paper's own reason is the hardware it targeted, which "can handle a maximum of
512 binary variables".

In CVQBoost, each voter gets a **smoothly varying** amount of say. Not in or out,
but 0.03 of a vote, or 0.11, with all the weights adding up to 1.

The paper states the reason plainly: they did not need to force the weights into
on-or-off form, because the Dirac-3 machine natively works with smoothly varying
quantities. **The method was shaped by what the hardware could do.**

That matters for section 6. When you read that the weights came out nearly equal
and that nudging them barely changed anything, remember that smoothly adjustable
weights are the entire reason this version of the method exists. The one thing
it added over its predecessor is the thing that turned out not to matter here.

(A note on the name: "CV" is the only part nobody will tell you. The paper uses
the name 84 times and never once says what the letters stand for. It introduces
the name in a sentence about hardware that "encodes into continuous variables",
and QCi's own source code calls the file `cvqboost_hamiltonian`, so "continuous
variable" is the near-certain reading. It is still an inference. Search engines
will state it as fact; they cannot show you where it was written down either.)

It works like this.

Build a large collection of very simple classifiers. Each one looks at just one
or two or three features, and each votes on every transaction: guilty or
innocent. Nothing subtle. One voter might only ever consider the amount.

The main configuration used **91 voters looking at 13 features**.

Now, no single voter is any good. The trick is combining them. Some voters
deserve more say than others, so each gets a weight, and the final score is the
weighted sum of all the votes.

**Choosing those weights is the entire maths problem**, and it is the only place
the quantum device is involved.

### What the landscape means

Picture a landscape where your position is one particular set of weights, and
the altitude is how badly that combination performs. You want the lowest point.

With 91 weights, the landscape has 91 dimensions, which nobody can picture. But
the search is the same idea: find the bottom.

Dirac-3 does this with light rather than arithmetic. It sets up a physical
system whose lowest-energy state corresponds to the best set of weights, then
lets physics settle and reads the answer.

### The control that turns this into an experiment

Here is the part that makes the whole project worth reading.

Alongside every quantum run, an ordinary computer solved **the identical maths
problem** using a standard method. Not a similar problem. Not an approximation.
The same one.

That matters because of a mathematical property of this particular landscape: it
is what mathematicians call convex. It has exactly one lowest point, with no
misleading dips elsewhere, and there are classical methods that find it and then
**prove** they have found it. The proof here is a check whose error came out
below 0.000000001.

So the comparison is not "quantum versus some other guess". It is "quantum
versus an answer already proven to be the best one available".

**Two different classical comparisons are now in play, and it is worth
keeping them apart.**

- **The exact solver**, described here. It solves the same weight-choosing
  problem the device solves, and proves its answer optimal. This is the
  control that tests the *device*.
- **An ordinary fraud model**, which does not use this method at all. It is a
  conventional detector of the kind banks already run. This is what tests the
  *approach*, and it is the 0.8070 in section 6.

The first asks "did the device solve the problem correctly?" The second asks
"was this whole approach worth taking?" The answers came out yes and no, in
that order.

### Which makes the question answerable

This is the sharpest thing about the design. Because the classical solver can
prove it found the true best answer, the quantum device **cannot beat it**. Not
"probably will not". Cannot, in the way you cannot score higher than full marks.

The submission says so outright and rules out the corresponding claim in advance:
"the device found a better answer" is not available on this formulation and they
will not make it.

So the questions become measurable:

- Does the device find the *same* answer the proven method found?
- Does it get there faster or cheaper?
- And underneath both: was this problem ever worth solving with special hardware?

### What it cost

61 runs on the real machine. 1,141 seconds of billed time. Zero failures, zero
retries.

A small fit bills 4 to 5 seconds on the device. The exact classical solve of the
same problem takes milliseconds.

**Those two numbers do not divide into each other, and that is not a mistake.**
61 runs at 5 seconds would be about 305 seconds, not 1,141. The difference is
that bigger problems cost more time: the 4-to-5-second figure is what the small
runs cost, while the large ones (the 833-voter setup in section 6) bill far more.
Across the whole campaign the average is about 19 seconds a run.

It is flagged here because two true numbers sitting next to each other can
suggest a third thing that is false.

Hold on to that comparison. Section 6 explains why it turned out to be the whole
story.

---

## 6. What we found, and why "it did not help" is a real result

*Reading level: aimed at grade 9; measures 6.6.*

### The headline

The quantum-inspired method scored **0.7671**. A well-tuned ordinary model,
looking at the same 13 features, scored **0.8070**.

The quantum arm lost by 0.0399. It lost on **nine of the ten** attempts.

That number, 0.7671, is the measure section 2 described without naming: how well
the detector does at the top of the ranked list. Its name is AUPRC. One means
perfect, and the number you would get by guessing here is about 0.0017.

**One qualifier the reader should carry forward**: 0.7671 is the same number
section 4 used. It is a random-split score. Tested honestly by time it falls
to 0.7095. So the headline comparison is between two random-split numbers,
which is the fair way to compare them against each other, but neither is what
either method would score in production.

This was the main question the project committed to in advance. The answer is no.

### Why, and this is the part that matters

A disappointing result is only useful if you can say *why*. Otherwise the next
person repeats it.

The cause was measured, not guessed, and it is at the voters.

Remember the 91 simple voters from section 5. It turns out that **80 to 84 of
them reproduce the training answers exactly**. Each one, alone, already "gets
every training transaction right".

They are not 91 different opinions. They are nearly the same opinion, 91 times.

When every voter says the same thing, **how you weight them cannot matter.**
Give one a bigger say, give another a smaller say: the weighted total barely
moves, because they are all voting the same way.

Mathematically the submission puts it precisely: the relationships between voters
form a pattern that is "rank-one to numerical precision", which is the technical
way of saying there is really only one opinion in the room.

So the optimizer, quantum or classical, was being asked to solve a problem whose
answer does not depend much on the solving.

### The measurement that clinches it

Here is the check that makes this airtight rather than a story.

Compare two things: the carefully optimized weights, and simply giving every
voter an equal say. The difference was **0.0028**.

Then ask how much the score moves for a reason that is definitely meaningless:
just reshuffling voters that were exactly tied with each other. That produced
swings of **0.0120**.

**The "improvement" from optimizing is four times smaller than the noise from
meaningless reshuffling.** So it is not an improvement. It is tie-breaking.

### Did the machine at least work?

Yes, and this distinction matters.

The device's answers agreed with the proven-optimal classical answers to within
0.0010. It solved the problem faithfully.

**The problem just was not worth solving.** That is a different finding from "the
machine is broken", and confusing the two would be the easiest mistake to make
here.

There is also no speed argument at this size. A device fit bills 4 to 5 seconds;
the exact classical solve takes milliseconds.

### Where the real gain was

The project then rebuilt the voters properly: different kinds of voter, and a
correction for how rare fraud is.

That gained **+0.0319**, on ten attempts out of ten.

Broken down, nearly all of it came from the rare-fraud correction (+0.0328). The
optimizer's own contribution was **+0.0047**, with a spread of 0.0028.

(That 0.0028 is a coincidence of value, not the same quantity as the 0.0028
earlier in this section. The earlier one is a gap between two scores on the
original voters. This one measures how much the +0.0047 wobbled between
attempts on the rebuilt voters. Same digits, unrelated things.)

Now, the design was only sensitive enough to detect differences of about 0.0268.
So +0.0047 is well below what this experiment can even distinguish from nothing.

**The gain came from building better voters, not from better optimization.**

### The one positive result, reported with its caveat

One configuration did gain: a larger setup using three-feature voters scored
**+0.0256** on ten of ten attempts.

That is honestly reported, and so is the problem with it: **two things changed at
once.** The number of features went up *and* the voters got more complex. With
both moving together you cannot say which caused the gain.

The submission names the specific experiment that would separate them, states
that it has not been run, and says the gain cannot be attributed until it is.

That is what an honest positive result looks like. A less careful write-up would
have led with +0.0256 and left the confound out.

### So why publish a null at all?

Four reasons, and they are not consolation prizes.

**Somebody else would have spent the months.** Another team would have tried
this, because it sounds promising. A measured, traceable null saves them.

**It says where to look next.** The finding is not "quantum is useless for
fraud". It is much more specific: *on a problem with exactly one findable best
answer, a machine that finds best answers adds nothing.* That points at problems
where finding the answer is genuinely hard, which is the project's next step.

**The diagnosis is reusable even where the conclusion is not.** "Check whether
your voters are all saying the same thing before optimizing how to combine them"
applies far beyond this project.

**Publishing only what works poisons the record.** If every team that tried this
and failed stayed quiet, the published literature would show only the successes,
and it would look like the method works. The nulls that never get written are
invisible, and their absence is itself a distortion.

A result you did not want is still information. Withholding it is the only way
to make the months genuinely wasted.

---

## 7. How to know whether to believe any of this

*Reading level: aimed at grade 8; measures 7.4.*

You should not take the last six sections on trust. This one is about how to
check, and the habits it describes work on any technical claim, not just this
one.

### Decide what counts as success before you look

The single most important thing this project did happened before any experiment
ran.

They wrote down what they would test, what result would count as success, how
many attempts they would make, and how they would measure. Then they froze it,
with a timestamp and a code that identifies the exact version.

**Why this matters more than it sounds.** If you run the experiment first and
decide afterwards what counted, you will find something. There are always
several ways to slice a result, and the human brain is excellent at noticing the
flattering one and calling it the plan all along. Nobody is lying. It simply is
not a test any more.

Deciding first makes it a test again, because the result can come back *no*.

### Changing the plan is fine. Hiding the change is not

Plans do need to change. Thirty-two changes were made and dated here, each with
its reason.

What makes that honest rather than convenient is that the original stays
readable. Anyone can see what was planned, what changed, when, and why.

Three of those corrections were made *after* figures had already been published.
And one of the corrections was itself wrong and had to be corrected again. That
is recorded too, which is more telling than the other thirty-one.

### Look for the failures

A report with no failures in it has usually had the failures removed.

This one has a gate that failed. The project committed in advance that one of
its ordinary models, a tuned XGBoost, should reach 0.85 AUPRC. It reached
**0.8296**. (That is a third model, separate from the 0.8070 CatBoost in
section 6 and from the quantum arm; several ordinary models were tried.) They
recorded it as failed and said they were continuing anyway, along with the reason
they later found the threshold itself was poorly founded.

They also describe an earlier hardware run that appeared to *triple* the method's
score. It was traced the same day to a setup mistake, withdrawn and re-run, and
the wrong figures appear nowhere in the submission.

**When you read any technical claim, look for the part where something went
wrong.** If it is missing entirely, that is information about the report, not
about the work.

### Say where every number came from

Every number in the submission carries a tag saying whether it was measured on
the real quantum hardware, produced by ordinary computers, or projected as an
estimate.

That sounds bureaucratic. It prevents a specific and common trick: quoting a
projected number beside a measured one so the reader assumes both were measured.

### Make it possible to be proved wrong

The whole repository is public, including the frozen plan, all thirty-two
changes, the per-attempt values and the scripts that regenerate every figure.

That is the strongest available signal. Someone who publishes the means to
contradict themselves is more likely to have checked their own work.

### What you can actually do with this

You do not need a quantum computer or a statistics course to use any of this.
Next time you meet a confident technical claim, ask:

- Was the success criterion set before or after the result came in?
- Where are the failures?
- Which numbers were measured, and which were estimated?
- Can anyone else check it?

Those four questions do most of the work, and this project would rather you
asked them about its own submission than took it on faith.

---

## About the reading levels in this document

Each section shows two numbers. They mean different things and it is worth
knowing why they disagree.

**"Aimed at grade N"** is the target. The rule this project uses: start at grade
8, and go up by one grade only where an honest explanation cannot be given at the
lower level. Sections 4, 5 and 6 aim at 9 because the ideas in them genuinely
need more of the reader, not because the writing got lazier.

**"Measures N"** is Flesch-Kincaid, a formula that counts syllables per word and
words per sentence. Every section measures between 5.1 and 7.9, which is lower
than every target.

**The gap is the interesting part, and it is not a mistake in either number.**

Flesch-Kincaid cannot see difficulty. It counts "the machine is being asked about
March while having already studied May" as easy, because the words are short. A
reader holding two time periods, a sorted list and a comparison in their head at
once is doing grade-9 work with grade-6 vocabulary.

So the formula is a floor, not a verdict. It catches writing that is needlessly
dense. It cannot catch an idea that is simply hard, and it would score a short
meaningless sentence as excellent.

This is why the real test of this document is not either number. It is whether
someone who has not read the submission can explain back what CVQBoost is and why
the result is a null. That test is being run separately, and its result is
recorded whether it passes or fails.
