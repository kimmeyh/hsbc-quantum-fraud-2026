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

*Reading level achieved: grade 8.*

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

*Reading level achieved: grade 8.*

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

*Reading level achieved: grade 8.*

To test a fraud detector you need real transactions that somebody has already
labelled as fraud or not. That data is hard to get, for an obvious reason: it is
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

**Licence**: published under the Database Contents License, which permits reuse.
Even so, everything in this section is written in our own words.

### The competition set (called IEEE-CIS)

590,540 transactions from Vesta Corporation, a payments company, released for a
public competition. 3 exact duplicates removed.

Two differences from the first set matter:

- **Fraud is twenty times more common here**: 3.5 percent rather than 0.17.
- **It spans months, not two days.**

**Licence**: competition data. The rules are behind a sign-in wall and could not
be read anonymously, so it is treated as *do not copy*. Everything here is
paraphrased and cited, never quoted.

### Why two, and why the second one exists

The European set has a flaw that no amount of clever modelling fixes: two days
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
