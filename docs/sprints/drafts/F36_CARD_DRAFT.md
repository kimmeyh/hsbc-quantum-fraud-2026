# F36. Pandoc Lua filter: floating tables for the submission PDFs

Drafted 2026-09-06 at the team lead's direction ("register the pandoc Lua filter
now - believe it is worth it now"), as a full card rather than an inline fix.

## The problem, measured

The appendix content FITS three pages and renders on four. Measured directly:

| Page | Characters |
|---|---|
| 1 | 2,695 |
| 2 | 3,807 |
| 3 | 2,550 |
| 4 | 1,788 |
| total | 10,840 |

At page 2's density, three pages hold 11,421 characters. The content is 10,840 --
**581 characters UNDER capacity**, yet it needs a fourth page.

The cause is that pandoc 3.1.2 emits pipe tables as bare `longtable`
environments. `longtable` can break across pages but never FLOATS: it begins
exactly where it is written. When a table does not fit the remaining space,
LaTeX defers the table AND everything after it, leaving the page short. Five
tables totalling 35 rows leave pages 1 and 3 roughly 1,100 characters below page
2's density.

`ltablex` was tried and does nothing here, because a float must be wrapped in
`\begin{table}` and `longtable` cannot legally sit inside one. There is no float
for LaTeX to move.

## Cost to date

Roughly two hours across Sprints 5 through 8 spent trimming prose to satisfy page
limits, repeatedly cutting content that did not need to go. `page-fill-report.py`
(Sprint 6 improvement 4) diagnoses whether an overflow is a length problem or a
break problem, and has correctly reported "FIX THE BREAK" several times -- but
until now there was no way to act on that verdict except to delete text.

## Design

A Lua filter, `scripts/pandoc/float-tables.lua`, rewriting each `Table` node into
a floating `table` environment:

1. Wrap the rendered table in `\begin{table}[htbp] ... \end{table}` so LaTeX may
   place it on the page before or after the prose that introduces it.
2. Give every table a `\caption{}` and a `\label{}` so it is numbered and
   referenceable, since a float that has moved needs a name.
3. Convert `longtable` to `tabular` inside the float. A float cannot contain a
   longtable, and our tables are 6-9 rows -- none needs to break across pages.
4. Leave a table already carrying an explicit caption untouched.

Prose changes from "the table below" to "Table 3", which is the convention a
reviewer expects and which survives the table moving.

## Acceptance criteria, all falsifiable

1. **Effectiveness, the point of the card.** appendix.pdf renders at **3 pages**
   with the filter and 4 without, from identical markdown. Asserted by a test
   that renders both ways and compares.
2. **No content lost.** Every table row present in the markdown appears in the
   rendered PDF text. Asserted by extracting each table's first and last cell
   from the source and searching the PDF.
3. **Numbering is correct.** Tables are numbered sequentially from 1 with no
   gaps or repeats.
4. **Cross-references resolve.** No `??` appears in any rendered PDF, which is
   how LaTeX reports an unresolved `\ref`.
5. **Idempotent.** Running the filter twice produces byte-identical output.
6. **The other documents still render.** proposal 6/6, team profile 1/1, and all
   six QCi package PDFs build at US Letter with unchanged page counts.
7. **No figure changes.** Every numeric value in the rendered PDFs is identical
   before and after, checked by extracting all numbers from both and diffing.

## Guarantee of effectiveness before completion

The card is NOT complete on "the filter runs". It is complete when criterion 1
holds -- the appendix at 3 pages -- because that is the outcome the filter
exists to produce. If the filter works correctly and the appendix still needs 4
pages, the card FAILS and the honest conclusion is that floats were not the
binding constraint, which is worth knowing before more time goes into layout.

A dry-run measurement establishes the answer before the filter is finished:
render the appendix with all five tables temporarily removed. If it drops to 3
pages, the tables are the whole problem and floats will fix it. If it does not,
they are not, and the card is re-scoped rather than built.

## Estimate

75 minutes: 15 for the dry-run measurement, 30 for the filter, 20 for the tests,
10 to update the render script and prose references.

## Risk

The Lua filter runs on every submission render, eight days before the deadline.
Mitigation: the filter is opt-in via a `--lua-filter` flag in `render-pdf.ps1`,
so removing one line reverts to today's behaviour, and criterion 6 checks every
other document explicitly.
