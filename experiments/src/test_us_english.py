"""Tracked markdown uses US English spellings.

Team lead, 2026-09-16: "they will expect US English coming from me, even if HSBC
is based in England."

WHAT IS DELIBERATELY EXEMPT, and the exemption matters more than the rule:

  - `docs/paper/`          the submitted proposal, appendix and cover letter
  - `experiments/PREREGISTRATION.md`   FROZEN, amendments only
  - `docs/submission/`     the submitted package record

Those are documents of record for a filing made 2026-09-12. Editing them now to
fix a spelling would alter a submitted artifact after the fact, which is a worse
defect than an inconsistent spelling. If they ever need correcting, that is an
amendment, not a sweep.

Proper nouns keep their own spelling: "Database Contents License" is the NAME of
a license and is protected explicitly.

`scripts/us_english_fix.py` applies the conversion this test enforces.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

EXCLUDE_PREFIXES = ("docs/paper/", "docs/submission/")
EXCLUDE_FILES = ("experiments/PREREGISTRATION.md",)

# Spans that legitimately carry a non-US spelling, checked before the word scan.
PROTECTED = (
    "Database Contents License",
    "Open Data Commons",
)

BRITISH = (
    "behaviour", "behaviours", "colour", "colours", "favour", "favours",
    "favoured", "favourable", "favourite", "labour", "neighbour", "neighbours",
    "honour", "honoured", "rumour", "organise", "organised", "organising",
    "organisation", "organisations", "recognise", "recognised", "recognising",
    "realise", "realised", "minimise", "minimised", "maximise", "maximised",
    "optimise", "optimised", "optimising", "optimisation", "emphasise",
    "emphasised", "prioritise", "prioritised", "prioritising", "summarise",
    "summarised", "categorise", "categorised", "apologise", "analyse",
    "analysed", "analysing", "paralyse", "centre", "centres", "centred",
    "metre", "metres", "theatre", "licence", "licences", "defence", "offence",
    "pretence", "travelling", "travelled", "modelling", "modelled",
    "labelling", "labelled", "cancelled", "cancelling", "signalling",
    "fulfil", "fulfilment", "enrol", "skilful", "wilful", "aluminium",
    "programme", "programmes", "whilst", "amongst", "learnt", "spelt",
    "burnt", "dreamt", "judgement", "judgements", "acknowledgement",
    "acknowledgements", "ageing", "cheque", "storey", "tyre", "kerb",
    "plough", "draught", "sceptical", "sceptic", "sceptics", "scepticism",
    "manoeuvre", "artefact", "artefacts",
)

PATTERN = re.compile(r"\b(" + "|".join(BRITISH) + r")\b", re.IGNORECASE)


def _tracked_markdown() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    files = []
    for rel in out.stdout.splitlines():
        if rel in EXCLUDE_FILES:
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        p = ROOT / rel
        if p.is_file():
            files.append(p)
    return files


FILES = _tracked_markdown()


def test_the_file_list_is_not_empty():
    """A guard with an empty population passes trivially.

    If `git ls-files` fails, every parametrized case below vanishes and the
    suite stays green while checking nothing. That is the vacuous-guard shape
    this repository has shipped three times.
    """
    assert len(FILES) > 50, (
        f"expected many tracked markdown files, found {len(FILES)}. "
        "The guard below would be vacuous.")


def test_the_frozen_documents_are_actually_excluded():
    """The exemption must hold, or a sweep could rewrite a submitted document."""
    rels = {str(p.relative_to(ROOT)).replace("\\", "/") for p in FILES}
    leaked = [r for r in rels
              if r.startswith(EXCLUDE_PREFIXES) or r in EXCLUDE_FILES]
    assert not leaked, (
        f"frozen or submitted documents are in scope: {leaked}. These are "
        "documents of record and must never be swept.")


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_british_spellings(path: Path):
    text = path.read_text(encoding="utf-8")

    for span in PROTECTED:
        text = text.replace(span, " " * len(span))

    offenders = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in PATTERN.finditer(line):
            offenders.append(f"  line {lineno}: {m.group(0)!r} in {line.strip()[:70]!r}")

    assert not offenders, (
        f"{path.relative_to(ROOT)} uses British spellings; this repository "
        "writes US English (team lead, 2026-09-16):\n"
        + "\n".join(offenders[:10])
        + "\n\nRun scripts/us_english_fix.py to convert.")
