"""Convert an Outlook or Word HTML export to readable Markdown.

WHY THIS EXISTS. Correspondence that becomes a document of record arrives as
a Word HTML export: a .htm plus a `_files` sidecar. That export is a
RENDERING of the email, not its content. The QCi memo sent 2026-09-25 was
101,345 characters of which 16,542 were prose, plus Office
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
    """Remove Office's document-property tokens ONLY from the preamble.

    The first version deleted any line that was exactly `0`, `true` or `false`
    ANYWHERE in the document, case-insensitively. Measured: the input
    `<p>Answer:</p><p>0</p><p>true</p>` converted to just `Answer:`. A memo
    line whose entire content is the figure 0 was silently deleted, and no
    --check could catch it, because "0" is a substring of nearly every other
    number on the page.

    That is this script's own stated failure mode -- "a conversion that
    silently drops a number is worse than one that fails" -- committed by the
    cleanup step. Found by the PR #141 review.

    Word emits those property lines in a block at the very top, before any
    prose, so the fix is positional: only strip them from the preamble, and
    stop at the first line that is real content.
    """
    for token in OFFICE_TOKENS:
        text = re.sub(rf"^{re.escape(token)}\s*$", "", text, flags=re.M)

    lines = text.split("\n")
    cut = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            cut = i + 1
            continue
        if s.lower() in ("false", "true", "0"):
            lines[i] = ""
            cut = i + 1
            continue
        break                      # first real content line: stop stripping
    del cut
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def convert(raw: str) -> str:
    return drop_office_tokens(reflow(to_text(raw)))


def read_source(src: Path) -> str:
    """Decode by the DECLARED charset, and fail rather than mangle.

    Word and Outlook export as windows-1252. The first version read with
    `encoding="utf-8", errors="replace"`, which on the real sent memo produced
    **269 replacement characters** -- two curly apostrophes, four smart quotes,
    five en and em dashes, an accented letter, and 259 non-breaking spaces.
    Decoded as cp1252 the same file yields zero.

    The damage is invisible to `--check`, because a figure it was told to watch
    is ASCII and survives while the prose around it is corrupted. A guard that
    passes over a mangled document is the class this script exists to close.
    Found by the PR #141 review.
    """
    data = src.read_bytes()
    declared = re.search(rb"charset=([A-Za-z0-9_-]+)", data[:4096])
    encodings = []
    if declared:
        encodings.append(declared.group(1).decode("ascii", "ignore"))
    encodings += ["utf-8", "cp1252"]

    last: UnicodeDecodeError | None = None
    for enc in encodings:
        try:
            return data.decode(enc)                  # strict, by design
        except (UnicodeDecodeError, LookupError) as exc:
            if isinstance(exc, UnicodeDecodeError):
                last = exc
    raise last if last else UnicodeDecodeError(
        "unknown", b"", 0, 1, "no candidate encoding decoded this file")


def dst_path(src: Path, output: str | None) -> Path:
    return Path(output) if output else src.with_suffix(".md")


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

    try:
        raw = read_source(src)
    except UnicodeDecodeError as exc:
        print(f"CANNOT DECODE {src.name}: {exc}")
        print()
        print("Nothing was written. Converting with replacement characters "
              "would silently destroy punctuation.")
        return 2
    body = convert(raw)

    # REFUSE TO OVERWRITE. The destination may be a record of correspondence
    # that is gitignored and untracked, so an overwrite has no recovery path.
    # Deliberately no --force: an escape hatch shipped with its own guard gets
    # used, and this repository has paid for that twice.
    if dst_path(src, args.output).exists():
        d = dst_path(src, args.output)
        print(f"REFUSING to overwrite {d}")
        print()
        print("That file already exists. If it is a sent or filed artifact, an "
              "overwrite is unrecoverable. Choose another -o, or delete the "
              "existing file deliberately first.")
        return 2

    # PRESENCE IS NOT SURVIVAL. The first version tested `c in body`, so a
    # figure appearing twice in the source that lost one copy still passed.
    # Count occurrences in the source's own text instead, and require the
    # conversion to preserve every one.
    #
    # The source count comes from a tag-strip of the raw HTML rather than from
    # `convert()`, so the comparison is against what was THERE, not against
    # the pipeline being checked.
    src_text = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"<[^>]+>", " ", strip_office(raw))))
    out_text = re.sub(r"\s+", " ", body)

    # A FIGURE ABSENT FROM BOTH IS A FAILURE, NOT A PASS. `got < want` is
    # False when both are zero, so naming a figure that was never in the
    # document -- a typo, or the wrong file -- reported success. You name a
    # figure with --check precisely because you expect it to be there, so
    # "it was in neither" answers a question you did not ask.
    lost = []
    for c in args.check:
        want, got = src_text.count(c), out_text.count(c)
        if want == 0 or got < want:
            lost.append((c, want, got))

    if lost:
        print("CONVERSION DROPPED CONTENT:")
        for c, want, got in lost:
            if want == 0:
                print(f"  {c!r}: NOT IN THE SOURCE at all. Check the spelling "
                      "and the file -- this is not a pass.")
            elif got == 0:
                print(f"  {c!r}: present in the source, ABSENT from the result")
            else:
                print(f"  {c!r}: {want} occurrence(s) in the source, "
                      f"only {got} survived")
        print()
        print("Nothing was written. A conversion that silently loses a figure "
              "is worse than one that fails.")
        return 1

    dst = dst_path(src, args.output)
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
