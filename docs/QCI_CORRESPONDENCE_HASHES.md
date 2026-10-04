# Sent QCi correspondence: recorded hashes

**What this is.** The sha256 of each artifact sent to QCi on **2026-09-25 at
12:23 PM**, recorded 2026-10-02 (F99, Sprint 20). The artifacts themselves are
NOT in this repository and must not be: `docs/qci_package/` is gitignored
(`.gitignore:62`) because it holds a private commercial negotiation. Only the
hashes are tracked.

**Why it exists.** Until now the sent artifacts lived on one workstation with
no recorded hash anywhere, so a silent alteration was invisible. The team lead
confirmed 2026-09-29 that laptop backups cover **recovery** — a lost file can
be restored. What a backup cannot tell you is that the copy on disk stopped
matching what was sent. That is the gap this closes.

The precedent is `test_published_artifacts.py`, which pins the three filed
submission PDFs by sha256 so a rebuild is caught. That guard exists because a
rebuild did change already-filed bytes, twice. The sent correspondence is the
same class of artifact and had none of that protection.

## The hashes

| Artifact | Bytes | sha256 |
|---|---|---|
| `Request and Results ... activities.htm` | 103,594 | `cec3bc1e9e3b35b5c2ec7a8fc86fd96f4ddf0cf3a25a8b1ac477a4cfbeeb0c4e` |
| `Phase 1 - QCi memo AS SENT 2026-09-25.md` | 17,850 | `05d922369ef788fb555fa5d106e41cd17d8a88d638b0d95497f613831cdc59ba` |

The `.htm` is the authoritative artifact, exactly as sent. The `.md` is its
readable, diffable conversion, produced by `scripts/outlook_htm_to_md.py`.

### The `_files` sidecar

Word emits a sidecar directory beside an HTML export. It is pinned by **one
manifest hash** over its sorted `(name, sha256)` pairs rather than a hash per
file, because a manifest also catches a file **added or removed**, which
per-file hashes cannot.

| | sha256 |
|---|---|
| manifest over 3 files | `06a2d25122c01d1df42676da110442a391c3048dc2fc803314b3994f9264aa5b` |

Contents at recording time: `colorschememapping.xml`, `filelist.xml`,
`themedata.thmx`.

## What enforces this

`experiments/src/test_sent_correspondence.py`. It compares each artifact
against the hash above, and **skips visibly** where the artifact is absent —
which is every machine but the team lead's, since the files are gitignored. A
skip that read as a pass would make the guard worse than none, so the skip
message states plainly that nothing was checked.

Proven 2026-10-02: a mismatched hash goes red, an added, edited or removed
sidecar file changes the manifest, and a one-byte change to a copy is detected.
Every mutation ran on a scratch copy; the sent artifacts were opened for
reading only, per the standing rule that a sent artifact is evidence rather
than a test fixture.

## If one of these assertions fires

The record did not change — the copy on disk did. A sent document is not
edited: if a revision is genuinely wanted, it is a **new** document with a new
name and its own hash recorded here. The four QCi package documents were
declared final by the team lead on 2026-09-27.
