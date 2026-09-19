"""The submitted documents are Class 4: approval BEFORE the edit, not after.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Guards `proposal.md`, `appendix.md` and `team_profile.md` under `docs/paper/`.
The rendered PDFs under `docs/paper/out/` are OUTPUTS and are deliberately not
matched: regenerating them is how a change reaches the reader, and blocking that
would block the fix rather than the mistake.

Why this is a hook and not a note: by Sprint 12 these three files were the
product, and they were still being edited at the speed of code. A rule in a
document depends on someone reading the document.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

GUARDED = (
    "docs/paper/proposal.md",
    "docs/paper/appendix.md",
    "docs/paper/team_profile.md",
)
GUARDED_LEAVES = {"proposal.md", "appendix.md", "team_profile.md"}

APPROVAL_TOKEN = ".claude/.submission-edit-approved"


def message(leaf: str) -> str:
    return f"""[BLOCKED] {leaf} is a SUBMITTED document. Class 4 (workflow, team lead 2026-09-12)
requires Product Owner approval BEFORE the edit, not after.

Present the change for approval first:

  - text BEFORE
  - text AFTER
  - pros
  - cons
  - recommendation, and why

Then, once the team lead has approved, record it:

  {APPROVAL_TOKEN}  <- write what was approved

Do NOT create that file to unblock yourself. It records an approval that
happened; creating it without one is the evasion this hook exists to prevent.

Why this is a hook and not a note: by Sprint 12 these three files were the
product, and they were still being edited at the speed of code. A rule in a
document depends on someone reading the document."""


def main() -> int:
    payload = hooklib.read_payload()
    if hooklib.tool_name(payload) not in EDIT_TOOLS:
        return hooklib.ALLOW

    path = hooklib.file_path_of(payload)
    if not path:
        return hooklib.ALLOW

    norm = hooklib.normalize(path)
    if not any(norm.endswith(g) for g in GUARDED):
        return hooklib.ALLOW

    # The leaf check is what keeps docs/paper/out/proposal.pdf allowed: the
    # rendered output is not the frozen source.
    leaf = norm.rsplit("/", 1)[-1]
    if leaf not in GUARDED_LEAVES:
        return hooklib.ALLOW

    if hooklib.repo_file(*APPROVAL_TOKEN.split("/")).exists():
        return hooklib.ALLOW

    return hooklib.block(message(leaf))


if __name__ == "__main__":
    sys.exit(main())
