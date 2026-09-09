"""Every third-party import must be declared in requirements.txt.

CI failed on its first real run with `ModuleNotFoundError: No module named
'pypdf'`. The package is imported by three modules including a test, and it
worked locally only because it had been installed into the venv ad hoc and
never written down. Auditing the rest of the tree then found scipy in the same
state -- `score_gates.py` imports it, so the gate report could not have been
regenerated from a clean environment either.

That is a hole in the exact document appendix C and the QCi letter point at for
reproduction: "the repository carries the pinned environment". Anyone building
from requirements.txt would have hit the same wall we did.

CI catches this now, but only on push, and only for packages some test happens
to import. This runs locally in milliseconds and covers every module.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[1]
REQS = ROOT / "experiments" / "requirements.txt"

# import name -> distribution name, where they differ.
ALIASES = {
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "eqc_models": "eqc-models",
    "qci_client": "qci-client",
    "PIL": "pillow",
}

# Imports that are legitimately absent from requirements.txt.
EXEMPT = {
    "pytest",          # declared, but also the runner itself
}


def _declared() -> set[str]:
    out = set()
    for line in REQS.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            out.add(re.split(r"[><=\[!]", line)[0].strip().lower())
    return out


def _local_modules() -> set[str]:
    return {p.stem for p in SRC.glob("*.py")}


def _imports() -> dict[str, set[str]]:
    """{distribution name: {files importing it}} for third-party imports.

    Parsed from the AST, not matched with a regex. A line-anchored regex reads
    prose inside docstrings as code -- the first version of this scan reported
    packages named "the", "a" and "months", because sentences in module
    docstrings begin with words like "import the ...". The AST sees only real
    import statements.
    """
    import ast

    stdlib = set(sys.stdlib_module_names)
    local = _local_modules()
    found: dict[str, set[str]] = {}

    files = list(SRC.glob("*.py")) + list((ROOT / "scripts").glob("*.py"))
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        mods: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                # level > 0 is a relative import, always local
                if node.level == 0 and node.module:
                    mods.add(node.module.split(".")[0])
        for mod in mods:
            if mod in stdlib or mod in local or mod.startswith("_"):
                continue
            dist = ALIASES.get(mod, mod).lower()
            if dist in EXEMPT:
                continue
            found.setdefault(dist, set()).add(f.name)
    return found


def test_every_third_party_import_is_declared():
    """A package the code imports but requirements.txt omits is a build that
    only works on the machine where someone happened to pip install it."""
    declared = _declared()
    used = _imports()
    missing = {k: sorted(v) for k, v in used.items() if k not in declared}
    assert not missing, (
        f"imported but NOT in requirements.txt: {missing}. CI found pypdf this "
        f"way after it had been missing for weeks; anyone building from the "
        f"pinned environment appendix C promises would hit the same wall.")


def test_the_scan_sees_the_packages_we_know_are_used():
    """Guard the guard: a broken regex must not pass vacuously."""
    used = _imports()
    for expected in ("numpy", "pypdf", "scipy"):
        assert expected in used, (
            f"{expected} not detected by the import scan; the regex has "
            f"probably drifted and this test would pass on anything")
