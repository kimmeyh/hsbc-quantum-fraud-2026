"""Blocks writes to sibling repositories from this repository's sessions.

Converted from PowerShell 2026-09-17 (F78, Sprint 16). Written 2026-09-15.

Team lead: work in hsbc-quantum-fraud-2026 never writes to spamfilter-multi or
EvidenceBasedDB. Reading them on request is fine.

The failure this guards: a Sprint 14 session reviewing PR #97 also examined
EvidenceBasedDB, found real defects, and fixed, committed and pushed them there
directly. Every finding was genuine and the boundary was still wrong. The
changes arrived in that repository with no review, no tests as gatekeeper and no
sprint record.

THE SIBLING MUST BE THE TARGET OF THE MUTATION, not merely mentioned. The first
version tested "is this mutating anywhere?" and "does it name a sibling
anywhere?" independently and ANDed the answers. That blocked two legitimate
read-only commands within minutes of shipping: a grep whose PATTERN contained
`New-Item|Remove-Item`, and a heredoc writing a file in THIS repository whose
text quoted both sibling names. A guard that blocks correct work trains bypass.

Cmdlets are anchored to a command position for the same reason, so a quoted grep
pattern cannot match.

Reads are deliberately NOT blocked: cat, grep, git log, git show, Read.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}

FORBIDDEN = ("spamfilter-multi", "EvidenceBasedDB")

GIT_WRITE = re.compile(
    r"git\s+(-C\s+\S*\s+)?(add|commit|push|mv|rm|checkout|switch|apply|restore|"
    r"reset|merge|rebase|tag|branch\s+-[dDmM])", re.IGNORECASE)


def message(what: str) -> str:
    return f"""BLOCKED: cross-repository write.

{what}

This repository's sessions never write to spamfilter-multi or EvidenceBasedDB
(CLAUDE.md standing rules; SPRINT_EXECUTION_WORKFLOW.md invariant 9). Reading
them on request is fine.

If a finding belongs to that repository, REPORT it -- file, line and fix -- and
hand it to a session running there, so it lands through that repository's own
review and tests."""


def check_path(path: str) -> str | None:
    norm = hooklib.normalize(path)
    for repo in FORBIDDEN:
        if re.search(re.escape(repo), norm, re.IGNORECASE):
            return f"Tool targets a path inside '{repo}':\n  {path}"
    return None


def check_command(cmd: str) -> str | None:
    for repo in FORBIDDEN:
        r = re.escape(repo)

        targets = [
            rf">>?\s*[\"']?[^\"'|;&]*{r}",
            rf"\b(cp|mv|rm|tee|touch|mkdir|rmdir)\b[^;&|]*{r}",
            rf"\bsed\s+-i[^;&|]*{r}",
            # Anchored to a command position, so a quoted grep PATTERN
            # containing these words cannot match.
            rf"(^|[;&|]\s*|\|\s*)(Set-Content|Out-File|Add-Content|New-Item|"
            rf"Remove-Item|Copy-Item|Move-Item)\s[^;&|]*{r}",
        ]
        for t in targets:
            if re.search(t, cmd, re.IGNORECASE | re.MULTILINE):
                return f"A write targets '{repo}':\n  {cmd}"

        # Git writes are scoped by the working directory, so a cd into the
        # sibling, or -C pointing at it, is the shape that matters.
        if GIT_WRITE.search(cmd):
            if (re.search(rf"cd\s+[\"']?[^\"';&|]*{r}", cmd, re.IGNORECASE) or
                    re.search(rf"git\s+-C\s+[\"']?[^\"';&|]*{r}", cmd, re.IGNORECASE)):
                return f"A git write runs inside '{repo}':\n  {cmd}"
    return None


def main() -> int:
    payload = hooklib.read_payload()
    tool = hooklib.tool_name(payload)

    if tool in EDIT_TOOLS:
        path = hooklib.file_path_of(payload)
        if path:
            found = check_path(path)
            if found:
                return hooklib.block(message(found))
        return hooklib.ALLOW

    if tool in SHELL_TOOLS:
        cmd = hooklib.command_of(payload)
        if cmd:
            found = check_command(cmd)
            if found:
                return hooklib.block(message(found))

    return hooklib.ALLOW


if __name__ == "__main__":
    sys.exit(main())
