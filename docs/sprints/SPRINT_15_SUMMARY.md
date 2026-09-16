# Sprint 15 Summary: The Submission, Explained

**Sprint**: 15
**Branch**: `feature/20260916_Sprint_15`
**PR**: #100 to develop
**Dates**: 2026-09-16
**Scope**: F73 (and F74, folded in)
**Metered Dirac-3 seconds**: ZERO

## What shipped

`docs/explainer/THE_SUBMISSION_EXPLAINED.md`: the proposal and appendix
submitted 2026-09-12, explained for an 8th grader working alone or in a group of
three. Seven sections, structured like a paper rather than a FAQ.

Alongside it:

- `docs/explainer/OUTLINE.md`, the structure and the reasoning behind it
- `docs/explainer/FALSIFIER_RESULT.md`, what two independent fresh readers
  understood and where they tripped
- `docs/research/cvqboost-name-and-lineage.md`, what CVQBoost is, sourced

## The one structural decision

**The quantum device appears in section 5 of 7. The submission puts it in
section 2 of 7.**

A reader who meets Dirac-3 before understanding why fraud detection is hard files
the whole document under "quantum computing", which is the wrong shelf. The
finding is about measurement discipline; the quantum device is the thing that got
measured.

The test of whether the ordering is right: a reader who stops after section 4
still learns something true and useful.

## The falsifier, which is the part that produced the real findings

The card required an explain-back test by someone who has not read the
submission. **That test cannot be run by the document's author**, who knows what
every sentence means because he wrote it.

Two runs, each a fresh reader with access to one file and nothing else, asked to
explain back rather than to critique. A reviewer asked "is this clear?" says yes.

Both passed at medium-high confidence. Six gaps were found and six resolved: four
fixed, two recorded as deliberate limits.

**Every gap either reader found was about IDENTITY, never difficulty.** Which
model does this number belong to; are these two numbers the same number; does
this figure describe the same thing as the one beside it.

That is the opposite of what the plan predicted. Sections 5 and 6 were flagged as
the hard cases on the expectation that QUBOs and detection thresholds would be
the obstacle. Both readers handled those and tripped on bookkeeping.

**The lesson recorded for the next document of this kind**: budget the care for
disambiguating similar numbers, not for simplifying hard ideas.

## Findings that came out of writing it

**The outline claimed three datasets; the submission used two.** `grep` finds
SPECTRA zero times in the proposal and appendix. It is four datasets about steel
plants, gas turbines, maintenance and telecom churn, read as prior art for a
different argument. Corrected in the document rather than deleted silently,
because "there were three datasets" is exactly the small false fact a reader
carries away and repeats.

**Five unsourced or over-confident claims were caught by checking rather than
recalling.** "September 2013" and "V1 through V28" for ULB; "the American set"
for IEEE-CIS; "CV stands for continuous variable" as a fact; "researchers at
Google and D-Wave" for QBoost; and 2012 asserted as QBoost's date while two QCi
sources disagreed. None appears in the shipped document as written.

**"61 runs, 1,141 seconds" beside "4 to 5 seconds per fit" does not divide.**
The second reader stopped on it. Checked against `qpu_cost_ledger.json`: both
are true and describe different things, since the 4-to-5 figure is the validated
free-tier distribution while the campaign average is 18.7 s per fit. Two true
numbers adjacent had implied a false third.

**A fifth control-character defect, already committed and pushed.** Writing the
CHANGELOG entry that DESCRIBES the Sprint 14 dead-hooks bug put a literal U+0008
into the file. The new class guard found a sixth instance on its first run, in
the master plan, inside the sentence warning about that exact bug.

## Team-lead feedback, actioned the same day

**US English.** 90 replacements across 35 tracked markdown files, with
`scripts/us_english_fix.py` committed and `test_us_english.py` guarding it. The
submitted documents and the FROZEN preregistration are EXEMPT, and the guard
asserts that exclusion holds so a later sweep cannot reach them.

The guard immediately caught its own rule: the first CLAUDE.md entry spelled out
counter-examples and failed the test that scans CLAUDE.md.

**CVQBoost, researched to primary sources.** The team lead was right on every
count that could be checked. QBoost encodes weights as low-bit-depth binary
expansions solved as a QUBO; CVQBoost uses continuous positive weights summing to
1. Both encodings were dictated by the machine, not chosen for statistical
reasons, which is the point the explainer now makes.

**What "CV" stands for is still NOT ESTABLISHED**, after three independent
primary sources: the arXiv paper (84 uses), QCi's shipped source code, and QCi's
own white paper (40+ uses). None expands it. "Continuous variable" is the
near-certain reading from adjacency and is labeled an inference wherever it
appears. Search summaries assert it as fact and cannot be traced to a source.

**The QBoost paper is in the library.** ACML 2012, pages 333-348, open access,
16 pages. The citation was ambiguous between two QCi sources and was settled from
CVQBoost's own bibliography.

## Guards added this sprint

- `test_no_control_characters.py`: every tracked text file, tab/newline/CR only
- `test_us_english.py`: US spellings, with the frozen-file exclusion asserted
- `test_cross_repo_write_guard.py`: 17 cases, 7 of which assert the guard ALLOWS

All three verified by injection rather than by a green run.

## Numbers

Counts are deliberately not restated here. Run the suite. PR #100 carries the
commit list; CHANGELOG.md carries the per-change record.

## Carried forward

- **PR #99 is fully contained in PR #100**, verified two ways. Merging #100 loses
  nothing from it.
- **F78** (convert 13 `.ps1` files to Python for Windows and Linux) is on the
  backlog at Priority 8, scoped from measurement. CI runs ubuntu-latest, so every
  hook in this repository is Windows-only protection today.
