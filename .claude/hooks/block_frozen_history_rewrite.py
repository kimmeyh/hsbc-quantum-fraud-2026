"""Refuse git operations that would rewrite published history or move the
frozen tags. F68, team lead 2026-09-12.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Two commits are load-bearing for claims this project has already PUBLISHED, and
both are cited in documents that were submitted and judged:

  95751b9  the preregistration freeze, tag `prereg-freeze`. Appendix B cites it
           by hash; Appendix C stakes "every figure regenerates from the public
           repository" on it resolving anonymously.
  the submission commit, from which the three judged PDFs were built and whose
           SHA-256 hashes are recorded in docs/submission/PACKAGE.md.

The repository has been public since 2026-09-11. A rewrite does not merely
inconvenience us: it breaks a citation in a document a judge may open during the
review window, and there is no way to correct a submitted PDF.

BLOCKS: force-pushes, history-rewriting commands (filter-branch, filter-repo,
hard reset against a remote ref), and any attempt to move, delete or re-point
`prereg-freeze`.

DOES NOT BLOCK: ordinary commits, merges, new tags, branch deletes, and local
rebases. Growing the repository forward is what a live project looks like.

If a rewrite is genuinely needed it almost certainly is not. A committed secret
is answered by rotation plus a forward commit, not a rewrite; the pre-flip scan
across all 259 commits found no secret ever committed. If the team lead
nevertheless directs one, record it at `.claude/.history-rewrite-approved`.
Creating that file to unblock yourself is the evasion this hook exists to
prevent, and unlike most such evasions it is not recoverable.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

APPROVAL_TOKEN = ".claude/.history-rewrite-approved"

PATTERNS = [
    ("force push",
     r"git\s+push\b[^|;&]*(--force\b|--force-with-lease\b|\s-f\b)"),
    ("filter-branch", r"git\s+filter-branch\b"),
    ("filter-repo", r"git\s+filter-repo\b"),
    ("hard reset to a remote ref", r"git\s+reset\s+--hard\s+origin/"),
    ("move or delete the freeze tag",
     r"git\s+tag\b[^|;&]*(-d|-f|--delete|--force)[^|;&]*prereg-freeze"),
    ("delete the freeze tag on the remote",
     r"git\s+push\b[^|;&]*(--delete|:refs/tags/)[^|;&]*prereg-freeze"),
]

COMPILED = [(name, re.compile(p, re.IGNORECASE)) for name, p in PATTERNS]


def message(what: str) -> str:
    return f"""[BLOCKED] This command would {what}.

The repository is PUBLIC and two commits are cited in documents that have
already been submitted and judged:

  - 95751b9 (tag prereg-freeze), cited by hash in Appendix B. Appendix C's
    claim that "every figure regenerates from the public repository" depends
    on it resolving anonymously.
  - the submission commit, from which the three judged PDFs were built; their
    SHA-256 hashes are in docs/submission/PACKAGE.md.

A rewrite breaks a citation in a document that cannot be corrected.

If a secret was committed, the answer is ROTATION plus a forward commit, not a
rewrite. Growing the repository forward is always available.

If the team lead has directed a rewrite, record the approval at
{APPROVAL_TOKEN} with the reason. Creating that file to unblock
yourself is the evasion this hook exists to prevent."""


def main() -> int:
    payload = hooklib.read_payload()
    cmd = hooklib.command_of(payload)
    if not cmd:
        return hooklib.ALLOW

    collapsed = re.sub(r"\s+", " ", cmd)

    hit = None
    for name, pattern in COMPILED:
        if pattern.search(collapsed):
            hit = name
            break
    if not hit:
        return hooklib.ALLOW

    if hooklib.repo_file(*APPROVAL_TOKEN.split("/")).exists():
        return hooklib.ALLOW

    return hooklib.block(message(hit))


if __name__ == "__main__":
    sys.exit(main())
