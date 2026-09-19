"""Guards on scripts/render_all.py (Sprint 17, Tasks C and the two defects
found while doing it).

Three properties, each of which failed in Sprint 17 before it was fixed:

1. The three QCi outputs carry the EXACT names QCi sees, spaces included.
2. A missing source FAILS. It used to print SKIP and exit 0, so a renamed
   document would drop out of the package silently.
3. The script REFUSES to rebuild a tracked, submitted PDF, and offers no
   override flag. Sprint 16 lost the filed bytes this way and needed a backup
   restore; Sprint 17 did it twice more in one task, the second time by
   passing the override flag the first fix had added.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_all.py"


def _source() -> str:
    return SCRIPT.read_text(encoding="utf-8")


# The names are spelled out here rather than imported, on purpose: a test that
# imports the constant it checks passes whatever the constant becomes.
EXPECTED_OUTPUTS = [
    "docs/qci_package/Phase 1 - eqc_models Feedback.pdf",
    "docs/qci_package/Phase 1 - Hardware Plan for Phase 2.pdf",
    "docs/qci_package/Phase 1 - Results Against Preregistered Criteria.pdf",
]


def test_qci_outputs_have_their_exact_names():
    src = _source()
    for name in EXPECTED_OUTPUTS:
        assert name in src, f"QCi output name missing or altered: {name}"


def test_qci_output_names_contain_spaces():
    """Not decoration. The names contain spaces, so every consumer must quote
    them; a test that would still pass on underscored names guards nothing."""
    for name in EXPECTED_OUTPUTS:
        assert " " in Path(name).name


def test_sources_are_not_renamed():
    """gate_report.md is referenced by score_gates.py and several tests.
    Renaming it for a presentational reason would touch the evidence pipeline."""
    src = _source()
    assert "experiments/results/gate_report.md" in src
    assert "docs/QCI_EQC_MODELS_FEEDBACK.md" in src


def test_hardware_plan_source_is_the_phase_2_plan():
    """The Phase 1 request (HARDWARE_REQUEST_B1_G0b.md) is a dated record of
    blocks executed 2026-09-03. QCi needs the Phase 2 plan, which is a
    different document. Sending the executed request would describe work
    already finished as though it were the forward plan."""
    src = _source()
    assert "docs/HARDWARE_PLAN_PHASE_2.md" in src
    assert (ROOT / "docs" / "HARDWARE_PLAN_PHASE_2.md").exists()
    hardware_plan_line = [
        line for line in src.splitlines()
        if "Phase 1 - Hardware Plan for Phase 2.pdf" in line
    ]
    assert hardware_plan_line, "the hardware plan output is not rendered"
    assert "HARDWARE_REQUEST_B1_G0b" not in "\n".join(hardware_plan_line)


def test_missing_source_is_a_failure_not_a_skip():
    src = _source()
    assert "SKIP (missing source)" not in src, (
        "a missing source must fail, not print SKIP and continue")
    assert "missing.append(source)" in src
    assert "if missing or failures:" in src


def test_no_override_flag_exists():
    """An escape hatch easier to reach than the correct path is not a guard.
    The first version of this refusal had --allow-overwrite-submitted, and the
    next command in the same session passed it."""
    assert "allow-overwrite-submitted" not in _source()


def test_bare_invocation_refuses_to_rebuild_submitted_pdfs():
    r = subprocess.run([sys.executable, str(SCRIPT)],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 1, (
        f"bare render_all.py should refuse, got exit {r.returncode}")
    assert "REFUSING" in r.stdout
    for name in ("proposal.pdf", "appendix.pdf", "team_profile.pdf"):
        assert name in r.stdout


def test_qci_package_renders_only_the_package():
    """--qci-package must not pull CORE in. It used to mean 'CORE AND the
    package', which made overwriting the submitted PDFs unavoidable."""
    src = _source()
    assert "docs = QCI_PACKAGE if args.qci_package else CORE" in src
    assert "docs = CORE + (QCI_PACKAGE" not in src
