"""Convert an Outlook or Word HTML export to readable Markdown.

WHY THIS EXISTS. Correspondence that becomes a document of record arrives as
a Word HTML export: a .htm plus a `_files` sidecar. That export is a
RENDERING of the email, not its content. The QCi memo sent 2026-09-25 was
101,345 characters of which 16,542 were prose -- 81% markup, plus Office
conditional comments, VML namespaces and non-breaking-space padding in the
header block.

Three properties make a naive tag-strip wrong, and each is handled below:

  1. Office metadata hides in conditional comments and <xml> blocks, so
     `DocumentEmail`, `EN-US`, `X-NONE` and `MicrosoftInternetExplorer4` come
     out looking like body text.
  2. Word hard-wraps mid-sentence, so a phrase is split across markup and a
     substring search for it fails. Reflowing is part of the conversion, not
     cosmetic.
  3. The header block (From/Sent/To/Cc/Subject/Attachments) is aligned with
     `&nbsp;` runs, which render as long junk strings -- but the header
     itself is the provenance that makes the file a record. It is preserved,
     not stripped.

WHAT THIS IS NOT. It does not replace the .htm. The export and its `_files`
sidecar stay as the authoritative artifact; this produces the readable,
diffable copy beside it. A Markdown file can be reviewed in a PR and compared
against a later revision; an HTML export cannot.

Usage:
    python scripts/outlook_htm_to_md.py INPUT.htm
    python scripts/outlook_htm_to_md.py INPUT.htm -o OUTPUT.md
    python scripts/outlook_htm_to_md.py INPUT.htm --check "1,681" --check "9,000"

`--check` asserts a string survived the conversion, and exits non-zero if it
did not. Use it for every figure the document commits to: a conversion that
silently drops a number is worse than one that fails.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# Office noise that survives a tag-strip as bare words on their own line.
OFFICE_TOKENS = (
    "DocumentEmail", "MicrosoftInternetExplorer4", "X-NONE", "EN-US",
)

HEADER_FIELD = re.compile(r"^(From|Sent|To|Cc|Bcc|Subject|Attachments):",
                          re.I)


def strip_office(text: str) -> str:
    """Remove the blocks Word emits that are not content."""
    text = re.sub(r"<!--\[if[^>]*>.*?<!\[endif\]-->", " ", text,
                  flags=re.S | re.I)
    text = re.sub(r"<xml[^>]*>.*?</xml>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<(script|style|head)[^>]*>.*?</\1>", " ", text,
                  flags=re.S | re.I)
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def to_text(raw: str) -> str:
    """HTML to plain text, preserving block boundaries."""
    text = strip_office(raw)

    # Block boundaries become newlines BEFORE tags go, so the reflow below
    # cannot glue two paragraphs into one.
    text = re.sub(r"</(p|div|h[1-6]|tr|li)>", "\n\n", text, flags=re.I)
    text = re.sub(r"<br[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.I)

    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)

    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(ln.strip() for ln in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def reflow(text: str) -> str:
    """Rejoin Word's mid-sentence hard wraps.

    A line continues the previous one unless the previous ended a sentence,
    or this one opens a new block (bullet, heading, header field).
    """
    out: list[str] = []
    for line in text.split("\n"):
        continues = (
            out and out[-1] and line
            and not out[-1].endswith((".", ":", "?", "!", "—", "-"))
            and not line.startswith(("-", "•", "#"))
            and not HEADER_FIELD.match(line)
        )
        if continues:
            out[-1] = out[-1] + " " + line
        else:
            out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def drop_office_tokens(text: str) -> str:
    for token in OFFICE_TOKENS:
        text = re.sub(rf"^{re.escape(token)}\s*$", "", text, flags=re.M)
    # Word emits bare "false" / "0" lines from its document properties.
    text = re.sub(r"^(false|true|0)\s*$", "", text, flags=re.M | re.I)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def convert(raw: str) -> str:
    return drop_office_tokens(reflow(to_text(raw)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="the .htm export")
    ap.add_argument("-o", "--output", help="defaults to the source with .md")
    ap.add_argument("--check", action="append", default=[], metavar="TEXT",
                    help="assert this string survived; repeatable")
    ap.add_argument("--title", default="",
                    help="heading for the converted file")
    args = ap.parse_args(argv)

    src = Path(args.source)
    if not src.is_file():
        print(f"not a file: {src}")
        return 2

    raw = src.read_text(encoding="utf-8", errors="replace")
    body = convert(raw)

    missing = [c for c in args.check if c not in body]
    if missing:
        print("CONVERSION DROPPED CONTENT. These were not found in the "
              "result:")
        for m in missing:
            print(f"  {m!r}")
        print()
        print("Nothing was written. A conversion that silently loses a figure "
              "is worse than one that fails.")
        return 1

    dst = Path(args.output) if args.output else src.with_suffix(".md")
    header = ""
    if args.title:
        header = (f"# {args.title}\n\n"
                  f"Converted from `{src.name}` on "
                  f"{__import__('time').strftime('%Y-%m-%d')}. The export and "
                  f"its `_files` sidecar remain the authoritative artifact; "
                  f"this is the readable copy.\n\n---\n\n")

    dst.write_text(header + body + "\n", encoding="utf-8")

    pct = 100 * (1 - len(body) / len(raw)) if raw else 0
    print(f"wrote {dst}")
    print(f"  source: {len(raw):,} chars  ->  prose: {len(body):,} chars "
          f"({pct:.0f}% was markup)")
    if args.check:
        print(f"  verified {len(args.check)} string(s) survived")
    return 0


if __name__ == "__main__":
    sys.exit(main())
