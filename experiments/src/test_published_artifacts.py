"""The three submitted PDFs are public; the QCi correspondence is not.

Team lead, 2026-09-18. Appendix C stakes the submission's reproducibility claim
on this being a PUBLIC repository, and until Sprint 16 a reader could regenerate
the PDFs but could not see the artifacts actually filed on 2026-09-12. The
portal holds the judges' copies and nobody outside HSBC can read them, so the
repository was the only possible public record and did not carry it.

At the same time `docs/paper/out/qci_package/` holds private commercial
correspondence with QCi -- a request for 30,000 QPU seconds and the case for it.
That must never be published.

Both facts live in one directory, which is why this test asserts BOTH
directions. An ignore rule that drifts in either direction is a defect: one way
breaks a submission claim, the other publishes a private negotiation.

THE RULE'S SHAPE MATTERS. `docs/paper/out/` (trailing slash) excludes the
directory itself, and git cannot re-include anything beneath an excluded
directory. The rule is `docs/paper/out/*` plus three negations -- the same
contents-not-directory shape .gitignore already warns about for
`experiments/results/predictions/`.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "paper" / "out"

PUBLISHED = ("proposal.pdf", "appendix.pdf", "team_profile.pdf")

# Moved to docs/qci_package/ on 2026-09-18: correspondence is not build output
# and does not belong under a rendered-PDF directory. The move REMOVED its
# protection -- under docs/paper/out/ the parent rule covered it whatever else
# said; under docs/ nothing else does. The ignore rule was written and verified
# BEFORE the files were moved, and these paths are relative to the repo root
# rather than to out/ so the check cannot silently follow a stale parent.
MUST_STAY_PRIVATE = (
    "docs/qci_package/qci_cover.md",
    "docs/qci_package/qci-sponsorship-email.html",
    "docs/qci_package/qci-sponsorship-request.md",
    "docs/qci_package/DRAFT_proposal.pdf",
    "docs/qci_package/DRAFT_qci_cover.pdf",
)

# Recorded in docs/submission/PACKAGE.md and SUBMISSION_RECEIPT.md.
SUBMITTED_SHA256 = {
    "proposal.pdf":
        "66cbdefa459a81c41f7f8a21fd5dc29b82c7e86f72415aa72229ac5e9d777e11",
    "appendix.pdf":
        "d1125998a7e8209c36d9dbe1edeea65276de5bfa4e5f4186cb648a24b670c242",
    "team_profile.pdf":
        "b77eb3f26b60a5d3a2b5c8e5a1245eb97039454fbc4812f5e65c407957ce5fdc",
}


def _ignored(rel: str) -> bool:
    """True when git would refuse to track this path."""
    r = subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT)
    return r.returncode == 0


@pytest.mark.parametrize("name", PUBLISHED)
def test_the_submitted_documents_are_publishable(name):
    rel = f"docs/paper/out/{name}"
    assert not _ignored(rel), (
        f"{rel} is ignored, so the public repository cannot show the document "
        "that was actually filed. Appendix C's reproducibility claim depends "
        "on a reader being able to see it.")


@pytest.mark.parametrize("rel", MUST_STAY_PRIVATE)
def test_the_qci_correspondence_stays_private(rel):
    assert _ignored(rel), (
        f"{rel} is NOT ignored. This is private commercial correspondence "
        "with QCi and must never reach a public repository.")


def test_no_qci_file_is_tracked():
    """Ignoring is not enough: a file already in the index stays tracked.

    That trap bit during the Sprint 16 move -- `git mv` relocated qci_cover.md
    and KEPT it tracked, so the ignore rule did nothing and the letter would
    still have been published. `git rm --cached` was needed.
    """
    tracked = []
    for folder in ("docs/qci_package/", "docs/paper/out/qci_package/"):
        r = subprocess.run(["git", "ls-files", folder],
                           cwd=ROOT, capture_output=True, text=True)
        tracked += [ln for ln in r.stdout.splitlines() if ln.strip()]
    assert not tracked, (
        f"private QCi files are TRACKED despite being ignored: {tracked}. "
        "An ignore rule does not untrack; use `git rm --cached`.")


@pytest.mark.parametrize("name", PUBLISHED)
def test_published_pdfs_match_the_submitted_hashes(name):
    """The published bytes must be the FILED bytes, or the record is wrong.

    PACKAGE.md and SUBMISSION_RECEIPT.md both name these hashes. If a rebuild
    ever replaces a published PDF, this fails and says so rather than letting
    the repository quietly disagree with its own submission record.
    """
    p = OUT / name
    if not p.is_file():
        pytest.skip(f"{name} is not present (build outputs are not committed "
                    "until published)")

    # A file git does not track is a local build artifact, not a published
    # one, and holding the suite red over it would be a false alarm. The
    # assertion binds the moment the file is COMMITTED, which is exactly when
    # the repository starts making a claim about it.
    #
    # This matters right now: Sprint 16 re-rendered these three while proving
    # render_all.py reproduced them, so the working copies differ from the
    # filed bytes in the PDF /ID trailer. They are being restored from backup.
    import subprocess as _sp
    tracked = _sp.run(["git", "ls-files", "--error-unmatch",
                       f"docs/paper/out/{name}"],
                      cwd=ROOT, capture_output=True).returncode == 0
    if not tracked:
        pytest.skip(f"{name} is not tracked yet; the hash binds once it is "
                    "committed as a published artifact")

    got = hashlib.sha256(p.read_bytes()).hexdigest()
    assert got == SUBMITTED_SHA256[name], (
        f"{name} does not match the hash recorded at submission.\n"
        f"  recorded {SUBMITTED_SHA256[name]}\n"
        f"  on disk  {got}\n"
        "A re-render changes the PDF /ID trailer even when the content is "
        "identical, so a rebuilt file is NOT the filed artifact. Restore the "
        "submitted bytes, or record both hash sets explicitly in PACKAGE.md.")
