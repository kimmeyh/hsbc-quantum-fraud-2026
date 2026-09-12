# Compliance Walk: Phase 1 Submission

Walked 2026-09-12 (Sprint 13, F10, Task C / issue #79) against the three
governing documents archived in `docs/source/`, each byte-identical (SHA-256) to
the copies re-downloaded from the logged-in portal on 2026-09-04.

Every row below was verified against the RENDERED PDFs, not against the markdown
sources and not against intent. Where a check is scripted, the script is named so
the walk can be repeated.

## The package

| File | Pages | Limit | Size |
|---|---|---|---|
| `out/proposal.pdf` | 6 | 6 | 62.0 KB |
| `out/appendix.pdf` | 3 | 3 | 49.2 KB |
| `out/team_profile.pdf` | 1 | 1 | 27.8 KB |

Total 144 KB against a 20 MB per-file cap. Three files into five upload slots.

## Format (Guidelines s4.3 to s5)

| # | Requirement | Verified | Method |
|---|---|---|---|
| B1 | Proposal max 6 pages, PDF, A4 or US Letter, min 10pt | **6/6, US Letter, 10.0pt** | `page-fill-report.py`; page geometry and font size read from the PDFs |
| B2 | Appendices max 3 additional pages | **3/3** | same |
| B3 | English; file max 20 MB | **English; 62 KB max** | inspection |
| B4 | Over-limit may be returned or judged on first 6 pages | **not triggered** | B1 holds |
| B5 | Public code repository link allowed | **public, HTTP 200** | anonymous fetch; freeze commit 95751b9 resolves; `prereg-freeze` tag intact |
| B6 | Seven required sections | **all seven, correctly ordered** | headings 1-7 in `proposal.md` |
| B7 | Paradigm specified | **hybrid classical-quantum**, stated in section 2 | inspection |

The 10.0pt figure is exactly at the minimum with nothing smaller anywhere in any
of the three documents. That is a deliberate margin of zero, so any future font
change is a conformance risk and not a style choice.

## Originality and confidentiality (T&C s3, s4)

`scripts/confidentiality-scan.ps1` over all three sources: **0 HIGH, 1 REVIEW**.

- **Employer references**: zero occurrences in all three documents.
- **NDA-covered material**: zero. The team lead holds QCi correspondence under
  mutual NDA; none of it reached the submission, and no claim in the documents
  rests on it.
- **Credential values, account identifiers, `.env` content**: zero.
- **The single REVIEW finding** is the team lead's own contact block in
  `team_profile.md:11` -- name, email, phone, LinkedIn. Guidelines s4.1 REQUIRES
  these. This is an intended disclosure, not a leak, and it is the one REVIEW
  line the team lead adjudicates before upload.

## Evidence integrity (walked in Tasks A and B)

- Every figure in the three documents resolves to a committed artifact.
- Campaign totals reconcile exactly from three independent artifacts:
  1069.0 s (results.json HW rows) + 62.0 s (b3_hardware.json) + 10.0 s (A21
  ceiling probe) = **1,141.0 s**, and 48 + 12 + 1 = **61 fits** with job
  identifiers retained for **60**.
- 31 dated amendments A1-A31; both documents state 31.
- 48 raw device responses tracked in git, matching the claimed 48.

## Outstanding at walk time

**Portal behaviour**, recorded as residual unknowns in requirements-matrix row
A5 and not resolvable without uploading: per-file size cap display, any
post-upload metadata prompt, deadline timezone, and whether uploading
immediately marks the track "submitted". The team lead walks these live. Nothing
is uploaded until the package is final.

**A3** (team lead accepts T&C at the point of submission) and **A5/A5b** (the
upload itself) are team-lead actions by construction. Claude verifies and records
completion evidence; Claude never uploads and never submits.
