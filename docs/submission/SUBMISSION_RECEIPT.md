# Submission Receipt

**Submitted 2026-09-12** by the team lead, three days before the 2026-09-15
deadline. Portal: `quantumaiportal.thequantuminsider.com`, HSBC track
(Financial services / QML).

Portal confirmation: **"Your submission received."** Counter moved from
"0 uploaded - 5 slots left" to **"3 uploaded - 2 slots left"**.

## What was uploaded

| Portal name | Source file | Pages | SHA-256 (first 12) |
|---|---|---|---|
| `proposal-1` | `docs/paper/out/proposal.pdf` | 6 | `66cbdefa459a` |
| `appendix-6` | `docs/paper/out/appendix.pdf` | 3 | `d1125998a7e8` |
| `team_profile` | `docs/paper/out/team_profile.pdf` | 1 | `b77eb3f26b60` |

Built from tracked sources at commit `004bb2a`. **As of 2026-09-18 the three
filed PDFs are COMMITTED**, so a reader can see the artifacts themselves rather
than only regenerate them -- the portal copies are invisible outside HSBC, which
left the repository as the only possible public record. The committed bytes are
the filed bytes, asserted against the hashes above by
`experiments/src/test_published_artifacts.py`. They also still regenerate from
the tracked markdown via `python scripts/render_all.py` (converted from
PowerShell in Sprint 16), which is the form Appendix C's reproducibility claim
requires.

**The portal renamed the files on ingest** -- `proposal.pdf` became `proposal-1`
and `appendix.pdf` became `appendix-6`, with the extension dropped from the
display name. The suffixes appear to be portal-side identifiers rather than
anything we supplied. Recorded because a later reader comparing the portal's
file list against this repository will otherwise see three names that match
nothing.

## Requirements-matrix row A5: the four residual unknowns, now answered

A5 recorded four things that could not be established without uploading. All
four are answered:

1. **Per-file size cap display**: NONE shown. The panel states allowed formats
   (PDF, PNG, JPG, WEBP, GIF, PY, JSON, JS, XLS, XLSX, CSV, DOC, DOCX) and the
   slot count, but no size limit. Academic at 62 / 49 / 28 KB.
2. **Post-upload metadata prompt**: NONE. No dialog, no form, no tagging step.
   Files move straight from staged to uploaded.
3. **Deadline timezone**: NOT DISPLAYED anywhere on the challenge page. The
   deadline is not shown at all in this view, so the timezone question is
   unresolved and unresolvable from the portal UI. Submitting three days early
   makes it moot for this entry.
4. **Does uploading mark the track submitted**: YES, and it is a TWO-STEP
   action. Selecting files stages them -- the counter still reads "0 uploaded"
   and each row offers Remove -- and clicking **Upload** commits. The
   confirmation "Your submission received." appears only after the commit.

The staging step is worth recording as a safety property: a mis-picked file can
be removed before anything leaves the machine.

## Still available

Two upload slots remain. Nothing further is planned, and the submission is
complete as it stands. If supplementary material were ever added, it would go
into those slots without disturbing the three files above.
