# F36 outcome: the filter works, the card fails, and the measuring tool was wrong

Card #48, Sprint 8. Written 2026-09-06.

**Verdict: FAILED on its own acceptance criteria.** The Lua filter does exactly
what it was specified to do. The problem it was built to solve did not exist.

The appendix nevertheless reached 3 pages in the same sitting, by a different
route the team lead proposed. Both halves are recorded below, because the useful
output of this card is the correction to how we measure, not the filter.

## What the card claimed

The appendix "content FITS three pages and renders on four". Evidence: page
character counts of 2,695 / 3,807 / 2,550 / 1,788. Pages 1 and 3 were held to be
roughly 1,100 characters short of page 2, the shortfall attributed to
`longtable` refusing to float and pushing content forward.

## What was actually true

Every page of the appendix was full. Measured as vertical extent of the text
block rather than as character count:

| Page | Text block used | Free space |
|---|---|---|
| 1 | 724pt | 0pt |
| 2 | 680pt | 0pt |
| 3 | 680pt | 0pt |
| 4 | 682pt | 0pt |

The text block at a 0.9in margin on US Letter is about 680pt of a 792pt page.
Every page reached the bottom margin. There was no white space anywhere in the
document, on any page, in either the baseline or the filtered render.

The appendix was over its limit because it had too much content. It was a
length problem throughout.

## Why the original measurement was wrong

Character count is the wrong instrument whenever pages differ in composition.

A table spends a lot of vertical space on few characters: short cells, wide
rows, rules and padding. Prose spends very little vertical space per character.
So a table-heavy page will always show fewer extracted characters than a
prose-heavy page of identical height, whether or not one point of space is
actually free.

Appendix pages 1 and 3 carried the tables. Page 2 was mostly prose. The "1,100
character deficit" was the difference between tables and prose, not between full
and empty.

## The filter itself

`scripts/pandoc/float-tables.lua` is correct and is retained, unregistered. Of
seven acceptance criteria:

| # | Criterion | Result |
|---|---|---|
| 1 | Appendix 3 pages with filter, 4 without | **FAIL** -- 4 and 4 |
| 2 | No table row lost | PASS |
| 3 | Numbering sequential from 1 | PASS -- 1..5, no gaps |
| 4 | No unresolved `??` references | PASS |
| 5 | Idempotent | PASS -- byte identical |
| 6 | Other documents unchanged | **FAIL** -- gate_report 3 -> 4 pages |
| 7 | No numeric value changed | PASS |

Criterion 6 is the more serious failure. Floating the tables in a table-dense
document COSTS a page: `gate_report.pdf` grew from 3 pages to 4. A float that
cannot fit the remaining space defers to the next page and leaves the gap it was
supposed to fill. In a document that is mostly tables, that happens often.

So the filter is not merely ineffective here. Enabled by default it would make a
submission document worse, eight days before the deadline.

## What DID work

The team lead, looking at the rendered tables rather than at the numbers,
observed that cells were wrapping: "CVQBoost on / Dirac-3", "Logistic /
regression", and a four-line row in the gate table. Every wrapped cell is a line
of vertical space bought back by widening that column at the expense of a column
with slack.

pandoc sets pipe-table column widths from the dash count in the separator row.
Every table here used `|---|---|`, giving equal widths, so columns holding "30"
or "[SIM]" had the same share as columns holding a sentence.

Measured effect of setting widths from the longest cell each column must hold:

| Table | Wrapped lines before | After |
|---|---|---|
| A.1 detection quality | 2 | 0 |
| A.3 quantities | 4 | 1 |
| B.1 gates | 7 | 3 |

That recovered 9 of the 20 lines on page 4 with no content change at all. The
remainder came from the team lead's second suggestion -- move to the public
repository anything that does not have to be in the document -- which took the
environment inventory, dataset checksums, amendment taxonomy and reference list
out of Appendix C, and from compressing restatement in A.4 and B.1.

Result: **appendix.pdf at 3 of 3 pages.** No figure, control, caveat or
disclosure was cut. The three figure-changing amendments (A15, A17, A12) remain
in full, as does the statement that no gate was rescored after observation.

Verified: of 140 decimal figures in the baseline render, the only ones absent
are package version numbers and an arXiv identifier, all of which moved to the
repository by design. `99.999%` also left the appendix but appears twice in the
proposal with fuller supporting context.

## Consequence for the submission

Appendix C now cites `github.com/kimmeyh/hsbc-quantum-fraud-2026`. That
repository was private on 2026-09-06 (anonymous API request returned 404), so
**F37 is registered as a submission blocker**: the repository must be public
before submission or the appendix cites a dead link and its reproducibility
claim is unverifiable.

## Disposition

- The filter stays in the repository, unregistered. It is a working tool for a
  problem we do not currently have.
- `render-pdf.ps1` keeps the opt-in `-LuaFilter` parameter. It is inert unless
  passed and is how the filter would be enabled if a genuinely break-bound
  document ever appears.
- `render-all.ps1` is NOT changed. No document renders with the filter.

## The correction that outlasts the card

`scripts/page-fill-report.py` produced the false premise. It was introduced by
the Sprint 6 retrospective specifically to stop us trimming prose when the real
cause was structural, and it has reported "FIX THE BREAK" several times. At
least once -- here -- that verdict was wrong, and it cost a card.

Two defects were fixed:

1. It counted characters. It now measures the vertical extent of each page's
   text block in points and reports free space against the deepest text block in
   the document.
2. It counted the page-number folio as text. Because the folio sits at the same
   depth on every page, it WAS the deepest baseline everywhere, so every page
   reported zero free space -- including a nearly empty final page, the one case
   the tool exists to flag.

`experiments/src/test_page_fill_report.py` covers both, including a direct
regression for the table-versus-prose shape that caused the false positive. All
four tests fail against the previous implementation.

## Process note

The card required a dry run before building: render the appendix with the tables
removed, and if it drops to 3 pages the tables are the problem. That dry run was
performed, reported 3 pages, and was read as confirmation.

It was not confirmation. Deleting five tables removes their content AND their
vertical space, so the document was always going to shrink. The dry run needed
to distinguish "the tables take up room" -- true, and unavoidable -- from "the
tables WASTE room", which is the only thing floats can recover. It could not,
so it confirmed nothing.

A dry run has to be able to fail. This one could not, and a check that cannot
fail is not evidence.
