# Submission Package

Built 2026-09-12 (Sprint 13, F10, Task D / issue #80) from tracked sources at
commit `dfbca40`. Rendered by `scripts/render-all.ps1`; page counts and
geometry read back from the rendered PDFs, not assumed from the sources.

## The three files

| File | Pages | Size | SHA-256 |
|---|---|---|---|
| `proposal.pdf` | 6 / 6 | 62.0 KB | `4a7df8cc57e520aae008f4c80902b1327631f6d2e4fc74e521165e78552159b3` |
| `appendix.pdf` | 3 / 3 | 49.2 KB | `c893cbcbe3b5c25badfa6f60eb8be600e3be65d434a6119263151c0ccfe2f449` |
| `team_profile.pdf` | 1 / 1 | 27.8 KB | `7e9a53559cfa78db8c66deec522f5d7a7a6b1117d0363f9a8d546d1b0ae31437` |

All US Letter, 10.0pt dominant with nothing smaller, English. Total 139 KB
against a 20 MB per-file cap. Three files into five upload slots.

The PDFs are build outputs and are deliberately NOT tracked in git. They
regenerate byte-for-byte from the tracked markdown by running
`scripts/render-all.ps1`, which is what Appendix C's reproducibility claim
requires. Re-render before uploading if any source has changed since the commit
above.

## Page fill at build time

    proposal    p1 674/679  p2 635/635  p3 632/635  p4 637/645  p5 636/645  p6 82/635
    appendix    p1 713/713  p2 640/647  p3 572/645
    team_profile p1 632/632

Appendix p3 carries 73 pt free, which is 6.1 lines at the measured 12.0 pt
pitch, and it is the tightest constraint in the package. Proposal p6 carries
553 pt, so insertions anywhere before section 7 are absorbed there.

## Upload order (team lead)

Portal: quantumaiportal.thequantuminsider.com, HSBC track.

1. `proposal.pdf` -- the concept proposal, Guidelines s4.3
2. `appendix.pdf` -- appendices, Guidelines s4.3 (max 3 additional pages)
3. `team_profile.pdf` -- Guidelines s4.1; no portal form was found for this at
   the 2026-08-30 walkthrough, so it ships as its own upload

Problem-statement selection is implicit: the upload lives on the HSBC track
page. The team lead accepts the T&C at the point of submission (A3).

## Recorded at upload time

Archive the receipt or confirmation in this directory, and record: the
timestamp, the deadline timezone as the portal displays it, whether uploading
immediately marked the track "submitted", and any post-upload metadata prompt.
Those four are the residual unknowns in requirements-matrix row A5 and can only
be answered by doing it.

## Verification behind this package

- `docs/submission/COMPLIANCE_WALK.md` -- format, originality, confidentiality
- Evidence walk (Task A): every figure resolves; campaign totals reconcile to
  1,141.0 s and 61 fits from three independent artifacts
- Requirements matrix (Task B): all 92 rows walked against the CURRENT documents
- Suite: 321 passed, 1 skipped
