# Submission Package

Built 2026-09-12 (Sprint 13, F10, Task D / issue #80) from tracked sources at
commit `6f6ccc0`, AFTER the six approved evidence-walk corrections. Rendered by `scripts/render-all.ps1`; page counts and
geometry read back from the rendered PDFs, not assumed from the sources.

## The three files

| File | Pages | Size | SHA-256 |
|---|---|---|---|
| `proposal.pdf` | 6 / 6 | 62.1 KB | `66cbdefa459a81c41f7f8a21fd5dc29b82c7e86f72415aa72229ac5e9d777e11` |
| `appendix.pdf` | 3 / 3 | 49.3 KB | `d1125998a7e8209c36d9dbe1edeea65276de5bfa4e5f4186cb648a24b670c242` |
| `team_profile.pdf` | 1 / 1 | 27.8 KB | `b77eb3f26b60a5d3a2b5c8e5a1245eb97039454fbc4812f5e65c407957ce5fdc` |

All US Letter, 10.0pt dominant with nothing smaller, English. Total 139 KB
against a 20 MB per-file cap. Three files into five upload slots.

**These three PDFs ARE tracked in git, as of 2026-09-18.** They were not
before, and the change is deliberate.

Appendix C stakes the submission's reproducibility claim on this being a PUBLIC
repository. A reader could regenerate the PDFs from the tracked markdown, but
could not see the artifacts actually filed on 2026-09-12: the portal holds the
judges' copies and nobody outside HSBC can read them. The repository was
therefore the only possible public record of what was submitted, and it did not
carry it. Publishing the three files closes that gap.

**The tracked bytes are the FILED bytes**, not a rebuild. The SHA-256 values in
the table above are asserted by `experiments/src/test_published_artifacts.py`,
so a re-render that silently replaces a published PDF fails the suite rather
than letting the repository disagree with its own submission record.

That assertion exists because the failure happened. Sprint 16 re-rendered all
three while proving the converted renderer reproduced them, which it did:
identical text, identical page counts, identical sizes. But a PDF carries a
per-build `/ID` trailer, so the bytes differed and the rebuilt files were no
longer the filed artifacts. They were recovered from a 2026-09-16 backup and
verified against these hashes before being committed.

They still regenerate from the tracked markdown: `python scripts/render_all.py`
(converted from PowerShell in Sprint 16; `render-all.ps1` is retired). Content
reproduces exactly; the `/ID` trailer will not, which is why the filed copies
are kept rather than rebuilt.

## Page fill at build time

    appendix    p1 713  p2 682  p3 584  (3 pages, 96 pt free on p3)
    proposal 6 pages, team_profile 1 page

Appendix p3 carries 61 pt free, about 5 lines at the measured 12.0 pt pitch, and
it is the tightest constraint in the package. The six approved evidence-walk
corrections spent 12 pt of the 73 pt it had before them. Proposal p6 carries
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
- Suite: 321 passed, 1 skipped (322 collected)
- Amendments: 32 (A1-A32); A32 corrects the linear-term spread quoted in A31
