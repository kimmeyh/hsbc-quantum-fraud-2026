"""PREREGISTRATION.md is FROZEN: amendments only, and only after verification.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Why this is a hook rather than a rule: in Sprint 12 a correction was written in
response to a review finding and published within hours. The correction was
false. Two external reviews caught it the same day, and A27 records the
withdrawal. The verification that would have prevented it took four minutes when
it was finally done.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
GUARDED_SUFFIX = "experiments/PREREGISTRATION.md"
APPROVAL_TOKEN = ".claude/.amendment-verified"

MESSAGE = """[BLOCKED] PREREGISTRATION.md is FROZEN. Amendments only, and only after the
finding behind them has been independently verified (workflow: VERIFY BEFORE
AMENDING, team lead 2026-09-11).

Before amending:

  1. Verify the finding against the CODE or the ARTIFACT it describes.
     Not against the reviewer's description of it.
  2. If a review is still arriving, WAIT and batch. Do not amend per finding.
  3. Record what you checked:

     .claude/.amendment-verified  <- write what was checked, and how

Do NOT create that file to unblock yourself.

Why this is a hook: in Sprint 12 a correction was written in response to a
review finding and published within hours. The correction was false. Two
external reviews caught it the same day, and A27 records the withdrawal. The
verification that would have prevented it took four minutes when it was finally
done."""


def main() -> int:
    payload = hooklib.read_payload()
    if hooklib.tool_name(payload) not in EDIT_TOOLS:
        return hooklib.ALLOW

    path = hooklib.file_path_of(payload)
    if not path:
        return hooklib.ALLOW

    # normalize() so a Windows-separator path still matches. A check that
    # matches only one separator style silently never fires on the other OS.
    if not hooklib.normalize(path).endswith(GUARDED_SUFFIX):
        return hooklib.ALLOW

    if hooklib.repo_file(*APPROVAL_TOKEN.split("/")).exists():
        return hooklib.ALLOW

    return hooklib.block(MESSAGE)


if __name__ == "__main__":
    sys.exit(main())
