"""The converter must not silently drop a figure or mangle the prose.

`scripts/outlook_htm_to_md.py` converts a Word or Outlook HTML export to
Markdown. Its own docstring states the contract: "a conversion that silently
drops a number is worse than one that fails." It shipped in Sprint 19 with NO
tests, and the PR #141 reviews found five ways it broke that contract:

  1. The Office-junk cleanup deleted ANY line whose entire content was `0`,
     `true` or `false`, anywhere in the document. Measured:
     `<p>Answer:</p><p>0</p><p>true</p>` converted to just `Answer:`.
  2. `--check` tested substring PRESENCE, so a figure appearing twice that lost
     one copy still passed.
  3. `--check` passed when the named figure was in NEITHER source nor output,
     because `got < want` is False when both are zero. A typo'd argument
     reported success.
  4. The source was read as UTF-8 with `errors="replace"`. Word exports
     windows-1252, so the real sent memo lost 269 characters -- smart quotes,
     em dashes, an accented letter -- and `--check` still passed because the
     figure it watched was ASCII.
  5. It overwrote an existing destination without a word. That destination may
     be a record of correspondence that is gitignored and untracked, so the
     overwrite has no recovery path.

All five are fixed and pinned below. Each guard has a companion asserting the
opposite case, because a guard that fires on everything is as useless as one
that fires on nothing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "outlook_htm_to_md.py"

sys.path.insert(0, str(ROOT / "scripts"))

# Built rather than literal: a heredoc writing this test file turned an escaped
# null into a real one and corrupted the file, which is the F82 escape class.
CP1252_DASH = bytes([0x96])
CP1252_OPEN = bytes([0x93])
CP1252_CLOSE = bytes([0x94])


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=str(ROOT), capture_output=True, text=True)


def _html(body: str) -> str:
    return f"<html><body>{body}</body></html>"


def test_the_converter_exists():
    assert SCRIPT.exists()


# ------------------------------------------------- content is never discarded

def test_a_line_whose_whole_content_is_zero_survives():
    """THE FIRST DEFECT. The cleanup deleted any line that was exactly `0`,
    `true` or `false`, so a figure on its own line was lost.

    `--check "0"` could not have caught it: "0" appears inside almost every
    other number on the page, so the substring test passed while the line was
    gone."""
    import outlook_htm_to_md as conv
    out = conv.convert(_html("<p>Answer:</p><p>0</p><p>true</p>"))
    assert "0" in out.split(), f"a bare 0 line was eaten: {out!r}"
    assert "true" in out.split(), f"a bare true line was eaten: {out!r}"


def test_the_office_property_preamble_is_still_stripped():
    """The companion. Preserving every `0`/`false` line unconditionally would
    satisfy the test above while leaving Word's document-property block in the
    output, which is what the cleanup was written for."""
    import outlook_htm_to_md as conv
    out = conv.convert(_html(
        "<p>false</p><p>0</p><p>EN-US</p><p>Real prose here.</p>"))
    assert out.strip() == "Real prose here.", (
        f"the Office preamble survived: {out!r}")


def test_the_header_block_is_preserved():
    """From/Sent/To/Subject is the provenance that makes a converted export a
    document of record. Stripping it would leave prose with no attribution."""
    import outlook_htm_to_md as conv
    out = conv.convert(_html(
        "<p>From: someone@example.com</p><p>Subject: A thing</p>"
        "<p>Body text.</p>"))
    assert "From:" in out and "Subject:" in out


# ------------------------------------------------------- --check fails closed

def test_check_refuses_to_write_when_a_figure_is_absent(tmp_path):
    """The gate. A conversion that lost a named figure must produce NO file --
    a partial output is worse than none, because it looks finished."""
    src = tmp_path / "in.htm"
    src.write_text(_html("<p>Total 1,681 seconds.</p>"), encoding="utf-8")
    dst = tmp_path / "out.md"

    r = _run(str(src), "-o", str(dst), "--check", "9,999")
    assert r.returncode != 0, "a missing figure did not fail the conversion"
    assert not dst.exists(), "it wrote a file despite the check failing"
    assert "DROPPED CONTENT" in r.stdout


def test_check_passes_and_writes_when_the_figure_survives(tmp_path):
    """The companion. Without it, failing unconditionally would satisfy the
    test above and the tool would never convert anything.

    Document-wide presence is the right assertion here, unlike the Sprint 20
    cases IMP-3 guards: this fixture contains the figure exactly once, by
    construction, so there is no prose mention it could be confused with.
    """
    src = tmp_path / "in.htm"
    src.write_text(_html("<p>Total 1,681 seconds.</p>"), encoding="utf-8")
    dst = tmp_path / "out.md"

    r = _run(str(src), "-o", str(dst), "--check", "1,681")
    assert r.returncode == 0, r.stdout + r.stderr
    assert dst.exists()
    assert "1,681" in dst.read_text(encoding="utf-8")


def test_check_counts_occurrences_not_mere_presence(tmp_path):
    """THE SECOND DEFECT. `--check` tested `figure in body`, so a document
    where a figure appeared twice and lost one copy passed."""
    import outlook_htm_to_md as conv

    src = tmp_path / "in.htm"
    src.write_text(_html("<p>We hold 1,681 today.</p>"
                         "<p>The balance is 1,681 exactly.</p>"),
                   encoding="utf-8")
    full = conv.convert(src.read_text(encoding="utf-8"))
    assert full.count("1,681") == 2, "fixture does not have two occurrences"

    lossy = full.replace("The balance is 1,681 exactly.", "")
    assert "1,681" in lossy, "the presence check would still pass"
    assert lossy.count("1,681") == 1


def test_a_figure_absent_from_the_source_also_fails(tmp_path):
    """THE THIRD DEFECT. `got < want` is False when both are zero, so naming a
    figure that was never in the document -- a typo, or the wrong file --
    reported success. You name a figure precisely because you expect it."""
    src = tmp_path / "in.htm"
    src.write_text(_html("<p>Total 1,681 seconds.</p>"), encoding="utf-8")
    dst = tmp_path / "out.md"

    r = _run(str(src), "-o", str(dst), "--check", "1,861")
    assert r.returncode != 0, "a transposed digit passed as verified"
    assert not dst.exists()
    assert "NOT IN THE SOURCE" in r.stdout


def test_a_missing_source_is_reported_not_silently_skipped(tmp_path):
    assert _run(str(tmp_path / "nope.htm")).returncode != 0


def test_an_empty_source_does_not_report_success_with_a_check(tmp_path):
    """An empty file converts to nothing. With a figure named, that must fail:
    "I produced no output" is not "the figure survived"."""
    src = tmp_path / "empty.htm"
    src.write_text("", encoding="utf-8")
    r = _run(str(src), "-o", str(tmp_path / "o.md"), "--check", "1,681")
    assert r.returncode != 0


# ------------------------------------------- the encoding must not be guessed

def test_a_cp1252_export_is_not_mangled(tmp_path):
    """THE FOURTH DEFECT, and it was live against a real vendor document.

    Word and Outlook export windows-1252. Reading as UTF-8 with
    errors="replace" destroyed 269 characters in the sent memo -- two curly
    apostrophes, four smart quotes, five dashes, an accented letter -- and
    `--check` still passed, because the figure it watched was ASCII and
    survived while the prose around it was corrupted.
    """
    import outlook_htm_to_md as conv

    src = tmp_path / "word.htm"
    src.write_bytes(
        b'<html><head><meta charset="windows-1252"></head><body><p>Cost '
        + CP1252_DASH + b'83 s, ' + CP1252_OPEN + b'quoted' + CP1252_CLOSE
        + b' of 1,681</p></body></html>')

    text = conv.read_source(src)
    assert "�" not in text, "the cp1252 export was mangled"
    assert "–" in text or "—" in text, "the dash was lost"
    assert "“" in text, "the smart quote was lost"


def test_a_utf8_source_still_decodes(tmp_path):
    """The companion. Decoding everything as cp1252 would satisfy the test
    above and corrupt genuine UTF-8 exports instead."""
    import outlook_htm_to_md as conv
    src = tmp_path / "u.htm"
    src.write_text(_html("<p>Café — 1,681</p>"), encoding="utf-8")
    text = conv.read_source(src)
    assert "Café" in text and "—" in text


def test_the_real_sent_memo_decodes_without_replacement_characters():
    """The live case. This is the artifact the defect was found against."""
    import outlook_htm_to_md as conv
    memo = (ROOT / "docs" / "qci_package" /
            ("Request and Results Phase 1 submission summary of results "
             "updated requests through Phase 2 Phase 2 goals and "
             "activities.htm"))
    if not memo.exists():
        import pytest
        pytest.skip("the sent memo is gitignored and absent on this machine")
    text = conv.read_source(memo)
    assert text.count("�") == 0, (
        f"{text.count(chr(0xFFFD))} characters were destroyed by the decode")


# ------------------------------------------------ an existing file is sacred

def test_it_refuses_to_overwrite_an_existing_destination(tmp_path):
    """THE FIFTH DEFECT. The destination may be a record of correspondence
    that is gitignored and untracked, so an overwrite has no recovery path.

    Deliberately no --force: this repository has twice paid for a guard
    shipped with its own escape hatch, and the second time it destroyed filed
    PDF bytes."""
    src = tmp_path / "in.htm"
    src.write_text(_html("<p>New content 1,681.</p>"), encoding="utf-8")
    dst = tmp_path / "out.md"
    dst.write_text("THE EXISTING RECORD\n", encoding="utf-8")

    r = _run(str(src), "-o", str(dst))
    assert r.returncode != 0, "it overwrote an existing file"
    assert dst.read_text(encoding="utf-8") == "THE EXISTING RECORD\n", (
        "the existing record was modified")
    assert "REFUSING" in r.stdout


def test_a_fresh_destination_is_still_written(tmp_path):
    """The companion. Refusing unconditionally would satisfy the test above
    and the tool would never convert anything."""
    src = tmp_path / "in.htm"
    src.write_text(_html("<p>Content 1,681.</p>"), encoding="utf-8")
    dst = tmp_path / "fresh.md"
    r = _run(str(src), "-o", str(dst), "--check", "1,681")
    assert r.returncode == 0, r.stdout + r.stderr
    assert dst.exists()


def test_no_force_flag_exists():
    """An escape hatch easier to reach than the correct path is not a guard.
    If one is genuinely needed it arrives later, in its own commit, with its
    own justification."""
    # CHECK THE PARSER, NOT THE TEXT. The first version grepped the source for
    # "--force" and matched the comment that says there deliberately is none --
    # presence is not correctness, the same error this sprint has now made
    # three times. Inspect the registered arguments instead.
    import argparse

    import outlook_htm_to_md as conv

    registered = set()

    real_add = argparse.ArgumentParser.add_argument

    def spy(self, *args, **kwargs):
        registered.update(a for a in args if isinstance(a, str))
        return real_add(self, *args, **kwargs)

    argparse.ArgumentParser.add_argument = spy
    try:
        try:
            conv.main(["--help"])
        except SystemExit:
            pass
    finally:
        argparse.ArgumentParser.add_argument = real_add

    for flag in ("--force", "--overwrite", "-f"):
        assert flag not in registered, (
            f"{flag} was added to the converter. An escape hatch easier to "
            "reach than the correct path is not a guard.")
    assert "--check" in registered, "the spy did not observe the real parser"
