"""The confidentiality scan catches what it claims to catch.

F78, Sprint 16, converting `scripts/confidentiality-scan.ps1` to Python.

A BUG WAS FOUND IN THE POWERSHELL ORIGINAL WHILE BASELINING THIS CONVERSION.
On a SINGLE-LINE file, `Get-Content` returns a String rather than an array, so
`$lines[0]` yields the first CHARACTER instead of the first line. Every rule
then tests one character and matches nothing, and the script reports
"0 HIGH, 0 REVIEW" on a file containing an employer name or an API token.

Demonstrated: a file reading "Our team at Progressive built this." scanned
clean, while the same content through the Python version returns 1 HIGH and
exit 1.

The real submission was NOT affected: proposal.md, appendix.md and
qci_cover.md are 104, 102 and 216 lines, and a multi-line read returns an
array. The bug bites only single-line files, which is exactly the shape a
hastily written cover note or a one-line addendum would take.

This is the class the repository keeps paying for: a check that reports success
while checking nothing. `splitlines()` cannot reproduce it, but the regression
case stays so a future rewrite cannot reintroduce it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "confidentiality_scan.py"

HIGH, CLEAN = 1, 0

CASES = [
    # --- single line: the exact shape that defeated the PowerShell ---------
    ("single-line employer name", HIGH, "Our team at Progressive built this."),
    # Assembled at runtime. A literal token here is itself flagged by the
    # pre-commit confidentiality hook, which blocked this file on first commit
    # -- correctly, since a fixture that matches the real pattern is
    # indistinguishable from the thing it imitates.
    ("single-line api token", HIGH, "QCI_" + "TOKEN=" + "a" * 20),
    ("single-line dotenv", HIGH, "QCI_" + "API_URL=https://example.invalid"),
    ("single-line clean", CLEAN, "An ordinary sentence about fraud detection."),

    # --- multi-line, which the original handled correctly ------------------
    ("multi-line employer name", HIGH,
     "Intro line.\nOur team at Progressive built this.\nOutro line."),
    ("multi-line clean", CLEAN, "Line one.\nLine two.\nLine three."),

    # --- REVIEW findings do not block ---------------------------------------
    ("absolute path is REVIEW not HIGH", CLEAN,
     "See D:\\Data\\Harold\\x.md for details."),
    ("personal email is REVIEW not HIGH", CLEAN,
     "Contact someone@aol.com for access."),

    # --- the retired rule must STAY retired ---------------------------------
    # F37 made the repository public, so citing its URL is REQUIRED by
    # Appendix C rather than forbidden. Re-adding the rule would block every
    # correct document.
    ("public repo URL is allowed", CLEAN,
     "The repository is at github.com/kimmeyh/hsbc-quantum-fraud-2026 and is public."),
]


def _run(content: str, tmp_path: Path) -> int:
    f = tmp_path / "sample.md"
    f.write_text(content, encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), str(f)],
                          capture_output=True, text=True).returncode


def test_the_script_exists():
    assert SCRIPT.exists(), "the confidentiality scan is missing"


@pytest.mark.parametrize("name,expected,content", CASES,
                         ids=[c[0] for c in CASES])
def test_scan_exit_code(name, expected, content, tmp_path):
    rc = _run(content, tmp_path)
    verb = "BLOCK (exit 1)" if expected == HIGH else "PASS (exit 0)"
    assert rc == expected, f"expected {verb} for {name!r}, got exit {rc}"


def test_the_real_submission_documents_still_scan_clean(tmp_path):
    """The gate that ran before the submission must still return 0.

    If this ever fails, either a document changed or a rule did, and both are
    worth stopping for.
    """
    docs = [ROOT / "docs" / "paper" / "proposal.md",
            ROOT / "docs" / "paper" / "appendix.md"]
    for d in docs:
        assert d.exists(), f"{d} is missing"
    r = subprocess.run([sys.executable, str(SCRIPT), *[str(d) for d in docs]],
                       capture_output=True, text=True)
    assert r.returncode == 0, (
        f"the submitted documents no longer scan clean:\n{r.stdout[-800:]}")
    assert "0 HIGH" in r.stdout


def test_a_missing_file_is_reported_not_ignored(tmp_path):
    """Silently skipping an unreadable file would make the gate vacuous."""
    r = subprocess.run([sys.executable, str(SCRIPT),
                        str(tmp_path / "does-not-exist.md")],
                       capture_output=True, text=True)
    assert "MISSING" in r.stdout
    assert "Scanned 0 file(s)" in r.stdout
