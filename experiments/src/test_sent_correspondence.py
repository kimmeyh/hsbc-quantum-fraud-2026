"""The sent QCi correspondence has a recorded hash, so alteration is visible.

F99, Sprint 20. `docs/qci_package/` is wholly gitignored (`.gitignore:62`) and
correctly so: it holds private commercial correspondence that must not be
published. The consequence was that the artifacts sent to QCi on 2026-09-25
existed on one workstation with NO recorded hash anywhere, so a silent
alteration was invisible.

The team lead confirmed 2026-09-29 that laptop backups cover RECOVERY. That is
why the original "unrecoverable and undetectable" framing was half wrong, and
why this file exists for the half that stands: a backup restores a file that
was lost, but it does not reveal that the copy on disk stopped matching what
was sent.

Contrast `test_published_artifacts.py`, which pins the three filed PDFs by
sha256 precisely so a rebuild is caught. That guard exists because a rebuild
DID change already-filed bytes, twice. Same class of artifact, and until now
different protection.

TWO THINGS THIS FILE DOES NOT DO. It does not change the ignore rule, and it
never writes inside `docs/qci_package/`. CLAUDE.md forbids re-rendering or
overwriting a sent artifact to prove a tool works, so every mutation here
happens on a scratch copy.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "docs" / "qci_package"

_STEM = ("Request and Results Phase 1 submission summary of results updated "
         "requests through Phase 2 Phase 2 goals and activities")

SENT_HTM = PKG / f"{_STEM}.htm"
SENT_SIDECAR = PKG / f"{_STEM}_files"
SENT_MD = PKG / "Phase 1 - QCi memo AS SENT 2026-09-25.md"

# Recorded 2026-10-02 from the artifacts as sent 2026-09-25 at 12:23 PM.
# These are the bytes QCi received. They do not change; if one of these
# assertions fires, the copy on disk moved, not the record.
SENT_SHA256 = {
    "htm": "cec3bc1e9e3b35b5c2ec7a8fc86fd96f4ddf0cf3a25a8b1ac477a4cfbeeb0c4e",
    "md": "05d922369ef788fb555fa5d106e41cd17d8a88d638b0d95497f613831cdc59ba",
}

# ONE manifest hash over the sidecar's sorted (name, sha256) pairs, rather
# than a hash per file. A manifest also catches a file ADDED or DELETED, which
# per-file hashes cannot: three entries today, and a fourth appearing is
# exactly the kind of drift worth knowing about.
SIDECAR_MANIFEST_SHA256 = (
    "06a2d25122c01d1df42676da110442a391c3048dc2fc803314b3994f9264aa5b")
SIDECAR_FILES = ("colorschememapping.xml", "filelist.xml", "themedata.thmx")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def manifest_hash(d: Path) -> str:
    pairs = sorted((f.name, sha256_file(f)) for f in d.iterdir() if f.is_file())
    blob = "\n".join(f"{n} {h}" for n, h in pairs).encode("utf-8")
    return sha256_bytes(blob)


def _require(p: Path, what: str) -> None:
    """Skip VISIBLY when the artifact is absent, never silently.

    These files are gitignored, so they are genuinely absent in CI and on any
    machine but the team lead's. That is a legitimate skip -- but a skip that
    reads as a pass is this repository's most-repeated defect, so the reason
    is stated rather than swallowed.
    """
    if not p.exists():
        pytest.skip(
            f"SKIPPED, NOT PASSED: {what} is absent at {p.name}. It is "
            "gitignored private correspondence, so it exists only where the "
            "team lead holds it. Nothing about its integrity was checked here.")


def test_the_sent_htm_matches_the_bytes_qci_received():
    _require(SENT_HTM, "the sent .htm export")
    got = sha256_file(SENT_HTM)
    assert got == SENT_SHA256["htm"], (
        "the sent .htm no longer matches what was sent to QCi on 2026-09-25.\n"
        f"  recorded {SENT_SHA256['htm']}\n"
        f"  on disk  {got}\n"
        "This file is a record of correspondence. If the change was "
        "deliberate it is a NEW document with a new name; the sent one does "
        "not get edited.")


def test_the_as_sent_markdown_matches_its_recorded_hash():
    _require(SENT_MD, "the AS SENT markdown copy")
    got = sha256_file(SENT_MD)
    assert got == SENT_SHA256["md"], (
        "the AS SENT markdown no longer matches its recorded hash.\n"
        f"  recorded {SENT_SHA256['md']}\n"
        f"  on disk  {got}\n"
        "It is the readable copy of a sent record, so it is as fixed as the "
        ".htm it was converted from.")


def test_the_sidecar_manifest_is_unchanged():
    """One hash over the sorted (name, sha256) pairs, so an added or deleted
    file is caught as well as an edited one."""
    _require(SENT_SIDECAR, "the _files sidecar directory")
    got = manifest_hash(SENT_SIDECAR)
    assert got == SIDECAR_MANIFEST_SHA256, (
        "the _files sidecar changed: a file was edited, added or removed.\n"
        f"  recorded {SIDECAR_MANIFEST_SHA256}\n"
        f"  on disk  {got}\n"
        f"  expected contents: {', '.join(SIDECAR_FILES)}\n"
        f"  found:             "
        f"{', '.join(sorted(f.name for f in SENT_SIDECAR.iterdir() if f.is_file()))}")


def test_the_manifest_hash_detects_an_added_file(tmp_path):
    """GUARD THE GUARD, on a SCRATCH COPY. A manifest that did not notice an
    addition would be weaker than the per-file hashes it replaced, and the
    whole reason for choosing it is that it notices."""
    d = tmp_path / "sidecar"
    d.mkdir()
    for name in ("a.xml", "b.xml"):
        (d / name).write_text(f"content of {name}", encoding="utf-8")
    before = manifest_hash(d)

    (d / "c.xml").write_text("a file that was not sent", encoding="utf-8")
    assert manifest_hash(d) != before, "an added file did not change the hash"


def test_the_manifest_hash_detects_an_edit(tmp_path):
    d = tmp_path / "sidecar"
    d.mkdir()
    f = d / "a.xml"
    f.write_text("original", encoding="utf-8")
    before = manifest_hash(d)

    f.write_text("altered", encoding="utf-8")
    assert manifest_hash(d) != before, "an edited file did not change the hash"


def test_the_manifest_hash_detects_a_removal(tmp_path):
    d = tmp_path / "sidecar"
    d.mkdir()
    for name in ("a.xml", "b.xml"):
        (d / name).write_text(f"content of {name}", encoding="utf-8")
    before = manifest_hash(d)

    (d / "b.xml").unlink()
    assert manifest_hash(d) != before, "a removed file did not change the hash"


def test_a_single_byte_change_is_detected(tmp_path):
    """The headline property, proven on a COPY of the real artifact where one
    exists, and on a synthetic file otherwise. The real file is never
    written to."""
    if SENT_MD.exists():
        original = SENT_MD.read_bytes()
    else:
        original = b"# A record\n\nSome sent content.\n"

    scratch = tmp_path / "copy.md"
    scratch.write_bytes(original)
    assert sha256_file(scratch) == sha256_bytes(original)

    # flip one byte
    mutated = bytearray(original)
    mutated[len(mutated) // 2] ^= 0x01
    scratch.write_bytes(bytes(mutated))
    assert sha256_file(scratch) != sha256_bytes(original), (
        "a one-byte change did not change the hash")


def test_the_ignore_rule_still_covers_the_package():
    """F99 does NOT change the ignore rule. The correspondence stays private;
    only its hashes are tracked. Sprint 16 IMP-2 nearly published this
    directory by relocating it out from under its parent rule."""
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "docs/qci_package/" in gitignore, (
        "the ignore rule on docs/qci_package/ is gone. That directory holds a "
        "private commercial negotiation; recording its hashes was never a "
        "reason to publish its contents.")

def test_the_tracked_record_and_this_file_cannot_drift():
    """The hashes live in TWO places, so they can disagree.

    `docs/QCI_CORRESPONDENCE_HASHES.md` records them for a human reader and
    this file enforces them. CLAUDE.md bans restating a number another file
    owns, and two copies of a sha256 is exactly that -- so rather than delete
    one copy and lose either the enforcement or the readable record, this
    guard makes a drift impossible to commit.
    """
    import re

    doc = ROOT / "docs" / "QCI_CORRESPONDENCE_HASHES.md"
    assert doc.exists(), f"{doc.name} is missing; it is the tracked record"

    in_doc = set(re.findall(r"[0-9a-f]{64}", doc.read_text(encoding="utf-8")))
    enforced = set(SENT_SHA256.values()) | {SIDECAR_MANIFEST_SHA256}

    assert in_doc == enforced, (
        "the recorded hashes and the enforced hashes have drifted. "
        f"Only in {doc.name}: {sorted(in_doc - enforced)}. "
        f"Only enforced here: {sorted(enforced - in_doc)}.")
