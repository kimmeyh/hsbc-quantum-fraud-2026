# Sprint 13 Manual Validation

Walked by the team lead, 2026-09-12. Phase 5. **All four items passed.**

| # | Item | Result |
|---|---|---|
| 1 | The three PDFs are what we intend to submit (6/3/1, US Letter, 10.0pt) | **Good** |
| 2 | The single REVIEW scan finding adjudicated (contact block, Guidelines 4.1) | **Good** |
| 3 | Two corrected claims spot-checked against their artifacts | **Good** |
| 4 | A32 reads correctly, including the log-was-wrong / paper-was-right ordering | **Good** |

## The one question raised, and its resolution

The team lead reported a `mailto:` hyperlink on the email address in
`team_profile.pdf`, which an earlier decision had ruled out (email displayed,
not clickable; LinkedIn hyperlinked).

Checked rather than acted on. The PDF's link annotations hold exactly one URI,
`https://linkedin.com/in/haroldkimmey`, and no `mailto:`. The source carries the
address in backticks, which pandoc renders as monospace and does not auto-link.
So the file was already correct.

Re-opening the PDF confirmed it: the link was the viewer's own auto-detection of
an email-shaped string, cached from a previous session. **No change was made and
none was needed.**

Recorded because the reflex would have been to "fix" a file that was not broken.
Removing the address would have touched a Guidelines 4.1 required field to
satisfy a rendering artifact in one viewer.

## State at validation

- Suite 321 passed, 1 skipped
- Confidentiality scan 0 HIGH, 1 REVIEW (the required contact block, adjudicated)
- Pages 6/3/1, US Letter, 10.0pt, 61 pt free on appendix p3
- 32 amendments, A1 to A32
- Issues #77, #78, #79, #80 closed; **#81 (portal submission) open, team-lead owned**
