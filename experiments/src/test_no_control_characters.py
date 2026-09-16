"""No tracked text file may contain a raw control character.

FOUR TIMES IN TWO SPRINTS an escape has been eaten and written as a control
character, each time producing a plausible wrong result rather than an error:

1. Sprint 14: a lone backslash-b before `block-` in .claude/settings.json became
   U+0008, so two hooks pointed at nonexistent files and never ran for their
   entire life.
2. Sprint 14: a test left Windows separators after substitution, so a path check
   was always False on POSIX and CI went red on four consecutive commits.
3. Sprint 14: a heredoc doubled every backslash in a README, so the paths would
   not have worked if pasted.
4. Sprint 15: writing the CHANGELOG entry that DESCRIBES failure 1 put a literal
   U+0008 into the file, inside backticks. Caught by a stray SyntaxWarning, not
   by inspection and not by any existing guard.

The existing hooks cover shell metacharacters and non-raw Python strings. Neither
sees a Python heredoc writing markdown, which is what produced #4.

This test covers the CLASS: a control character in a committed text file is never
intentional, whatever produced it.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Tab, newline and carriage return are legitimate in text files.
ALLOWED = {0x09, 0x0A, 0x0D}

TEXT_SUFFIXES = {".md", ".json", ".py", ".txt", ".yml", ".yaml", ".ps1", ".toml", ".cfg"}

NEWLINE = chr(10)


def _tracked_text_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    files = []
    for line in out.stdout.splitlines():
        p = ROOT / line
        if p.suffix.lower() in TEXT_SUFFIXES and p.is_file():
            files.append(p)
    return files


FILES = _tracked_text_files()


def test_the_file_list_is_not_empty():
    """A guard that checks nothing passes trivially.

    If `git ls-files` fails or the suffix filter matches nothing, every
    parametrized case below silently vanishes and the suite stays green. That is
    the vacuous-guard shape this repository has shipped three times, so the
    population itself is asserted.
    """
    assert len(FILES) > 50, (
        f"expected many tracked text files, found {len(FILES)}. "
        "The guard below would be vacuous.")


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_raw_control_characters(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        pytest.skip(f"{path.name} is not valid UTF-8")

    offenders = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for col, ch in enumerate(line, 1):
            if ord(ch) < 32 and ord(ch) not in ALLOWED:
                offenders.append(
                    f"  line {lineno} col {col}: U+{ord(ch):04X} in {line[:70]!r}")

    assert not offenders, (
        f"{path.relative_to(ROOT)} contains raw control characters:"
        + NEWLINE
        + NEWLINE.join(offenders)
        + NEWLINE
        + "This is almost always an escape eaten by a shell or a JSON parser "
          "(a lone backslash-b becomes U+0008). Write the literal text instead, "
          "or use a raw string.")
