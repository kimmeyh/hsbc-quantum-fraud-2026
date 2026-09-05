# ADR-0012: PDF rendering toolchain is pandoc to docx to Word

## Status

Accepted

## Date

2026-09-04

## Context

The submission is delivered as PDFs through a 5-slot portal upload: a concept proposal (max 6 pages plus a 3-page appendix, A4 or US Letter, minimum 10pt), a one-page team profile, and optional supplementary material. Paper sources are authored as Markdown under `docs/paper/` so they diff, review, and version like the rest of the repository.

A Sprint 5 capability pre-flight established what is actually available on this machine:
- pandoc IS installed, but has NO PDF engine (neither xelatex nor pdflatex), so `pandoc -o file.pdf` fails outright.
- WeasyPrint installs but cannot run: it needs GTK system libraries (`libgobject-2.0-0`) that are absent.
- wkhtmltopdf, prince, typst, and tectonic are all absent.
- Microsoft Word IS installed and its COM automation converts docx to PDF successfully (verified end to end).

## Decision

**Superseded 2026-09-04 (same ADR, corrected in place before any submission):** render Markdown to PDF in ONE step with pandoc plus xelatex (MiKTeX), setting page size through the LaTeX geometry package. `scripts/render-pdf.ps1` verifies both the page size and the page count of what it produced and throws if either is wrong.

The original decision routed through Word (pandoc to docx, then Word SaveAs) because no LaTeX engine was installed. Two defects made that unusable for a submission:

1. **It produced the wrong page size.** The script set `PageSetup.PaperSize` AFTER opening the document; Word did not reflow, so it emitted 11x17 TABLOID pages. The proposal, team profile, and three package documents were all tabloid and nobody would have noticed from the file names.
2. **Its page counts were wrong.** Word's `ComputeStatistics` reflows a PDF on open, reporting 4 pages for an appendix that was actually 6, against a hard 3-page limit that is an explicit rejection criterion.

Both were caught by the team lead asking whether the pages were US Letter. `scripts/check-page-limits.py` now reads counts from the PDF itself with pypdf, and the render script refuses to emit a file whose page size is not what was requested.

## Alternatives Considered

### Install a LaTeX distribution (MiKTeX or TeX Live)
- **Pros**: best typographic control; the conventional academic path; scriptable with no COM dependency.
- **Cons**: multi-gigabyte install days before a deadline; new failure surface at exactly the wrong time.
- **Why Rejected**: cost and timing outweigh the benefit for a 6-page business-facing proposal. Reconsider for Phase 2.

### Install GTK libraries for WeasyPrint
- **Pros**: pure-Python, CSS-controlled layout.
- **Cons**: system-library installation with its own failure modes; CSS print layout for tables is fiddly under time pressure.
- **Why Rejected**: Word already works and is already installed.

### Author directly in Word
- **Pros**: no toolchain at all.
- **Cons**: binary sources do not diff or review; breaks the traceability chain from results.json through the documents.
- **Why Rejected**: reviewability of the submission's claims is a core project value.

## Consequences

### Positive
Zero new installs; reliable output with tables and fonts intact; page count reported automatically for the limit check; sources stay Markdown and reviewable.
### Negative
Windows-and-Word specific, so the render step is not reproducible on a bare Linux checkout. The public reproducibility package ships Markdown sources plus the rendered PDFs, not the render step, so this does not affect reproducibility of the RESULTS.
### Neutral
A reference docx can be added later for typography without changing the pipeline.

## Preregistration touchpoints

None. This is document production; it touches no methodology, no data, and no result. The preregistration governs methodology; this ADR records an engineering decision only.

## References

`scripts/render-pdf.ps1`; docs/requirements-matrix.md rows B1 (page limit, format) and A5/A5b (portal upload slots); Sprint 5 plan capability pre-flight.

## Amendment, 2026-09-04: per-document margins

The appendix renders at `-Margin 0.9in`; the proposal and team profile at the
1in default. The appendix carries four tables in three pages and spilled 230
characters onto a fourth against a hard 3-page limit. 0.9in is a conventional
margin and the guidelines set no margin requirement, only a 10pt font minimum
(body text is 10pt, unchanged).

Rebuild commands, so a rebuild does not silently produce a 4-page appendix:

    .\scripts\render-pdf.ps1 -Source docs\paper\proposal.md     -Out docs\paper\out\proposal.pdf
    .\scripts\render-pdf.ps1 -Source docs\paper\appendix.md     -Out docs\paper\out\appendix.pdf -Margin 0.9in
    .\scripts\render-pdf.ps1 -Source docs\paper\team_profile.md -Out docs\paper\out\team_profile.pdf

Then `python scripts/check-page-limits.py`, which reads the PDFs rather than
trusting the render.

## Amendment, 2026-09-04: xelatex resolution and PATH isolation

Two environment defects made a valid document look broken:

1. MiKTeX installs to the USER PATH. A shell started before the install does
   not inherit it, so `--pdf-engine=xelatex` failed with "not found" on a
   machine where xelatex was installed. The script now resolves the executable
   itself before falling back to standard install locations.
2. MiKTeX enumerates every PATH entry at startup and ABORTS if one cannot be
   read: "MiKTeX cannot retrieve attributes for the directory ...". A stale
   `C:\devtools\cursor` entry killed xelatex on a bare "Hello world" while the
   console output looked like a mid-document LaTeX error. The script now runs
   pandoc with a minimal PATH (TeX bin plus system32) and restores it after.
