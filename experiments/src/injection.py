"""Break the thing, CHECK THE BYTES, then run the guard.

F89, Sprint 18 Task D. The rule "prove a guard FAILS, do not claim it works
because the suite is green" has been in CLAUDE.md since Sprint 16. Sprint 17
violated it SIX TIMES, every one by its own author, and in each case the
injection reported success while proving nothing:

  1. A `delim in quoted` branch in the F82 hook was unreachable dead code, so
     deleting it broke no test.
  2. `test_bypass_token_allows` passed for two different wrong reasons in
     succession -- first a body the hook allows anyway, then a trailing comment
     that defeated the opener pattern.
  3. The gate report's `0.7671` appears THREE times; `replace(..., 1)` left two
     behind and the assertion still found it.
  4. The missing-phase marker asserted a phrase `build()` supplies as a
     fallback anyway.
  5. The frozen-clock mutation hit `main()` while the test called `build()`.
  6. A hook payload of `{}` exited at an early gate, so all four cases read as
     ALLOW.

Cases 3 and 6 are what this module makes impossible. Cases 1, 2, 4 and 5 are
test-design faults that no helper can catch, and `assert_can_fail` addresses
them differently: by insisting the baseline is green, the mutation is real, and
the suite goes RED, rather than by trusting any one of those.

THE RULE THIS ENCODES: a mutation must be verified THROUGH THE SAME ACCESSOR
THE TEST USES. It is not enough that the file changed on disk; what matters is
that the value the assertion reads is gone.
"""
from __future__ import annotations

import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator


class InjectionError(RuntimeError):
    """The injection itself was invalid, so its result means nothing.

    Deliberately distinct from a test failure. A test that fails tells you
    something about the code; an injection that could not be applied tells you
    only that you learned nothing, and must never be reported as a pass.
    """


@dataclass
class Mutation:
    """One edit to one file, with the checks that make its result meaningful."""

    path: Path
    old: str
    new: str
    expect_occurrences: int | None = None

    def apply(self) -> str:
        """Replace EVERY occurrence and verify none survives.

        `replace(old, new, 1)` is banned here by construction. The gate
        report's 0.7671 case failed exactly that way: three occurrences, one
        replaced, the assertion still satisfied by the other two, and the
        injection reported as a passing guard.
        """
        original = self.path.read_text(encoding="utf-8")
        count = original.count(self.old)

        if count == 0:
            raise InjectionError(
                f"injection target not found in {self.path.name}: "
                f"{self.old[:70]!r}. The target moved; this injection would "
                "have reported success while changing nothing.")
        if self.expect_occurrences is not None and count != self.expect_occurrences:
            raise InjectionError(
                f"expected {self.expect_occurrences} occurrence(s) of the "
                f"target in {self.path.name}, found {count}. Either the file "
                "changed or the injection is aimed at the wrong thing.")

        mutated = original.replace(self.old, self.new)
        if mutated == original:
            raise InjectionError(
                f"the mutation changed nothing in {self.path.name}; old and "
                "new are equivalent")

        self.path.write_text(mutated, encoding="utf-8")

        on_disk = self.path.read_text(encoding="utf-8")
        remaining = on_disk.count(self.old)
        if remaining:
            raise InjectionError(
                f"{remaining} occurrence(s) of the target SURVIVE in "
                f"{self.path.name} after the write. The guard may still read "
                "one of them, which is how an injection passes while proving "
                "nothing.")
        return original


@contextmanager
def injected(*mutations: Mutation) -> Iterator[None]:
    """Apply mutations, yield, then restore and VERIFY the restore.

    A test that mutates a tracked file and dies without restoring leaves the
    repository in the broken state. Restoration is asserted, not assumed.
    """
    if not mutations:
        raise InjectionError("no mutations supplied")

    originals: list[tuple[Path, str]] = []
    try:
        for m in mutations:
            originals.append((m.path, m.apply()))
        yield
    finally:
        for path, text in reversed(originals):
            path.write_text(text, encoding="utf-8")
            if path.read_text(encoding="utf-8") != text:
                raise InjectionError(
                    f"FAILED TO RESTORE {path}. The working tree is dirty and "
                    "the file it guards may be unprotected.")


def assert_can_fail(mutations: list[Mutation],
                    run: Callable[[], bool],
                    label: str = "") -> None:
    """Assert the guard is GREEN, goes RED under mutation, and returns GREEN.

    `run` returns True for pass. All three legs are checked because any one of
    them alone is satisfiable by a vacuous test: a guard that is already red
    proves nothing by going red, and one that stays red after restoration has
    been left broken.
    """
    what = f" [{label}]" if label else ""

    if not run():
        raise InjectionError(
            f"the guard is ALREADY FAILING before any mutation{what}; its "
            "behaviour under injection would mean nothing")

    with injected(*mutations):
        if run():
            raise AssertionError(
                f"VACUOUS GUARD{what}: the suite stayed GREEN with the thing "
                "it guards broken. A test that cannot fail is worse than no "
                "test, because it buys false confidence.")

    if not run():
        raise InjectionError(
            f"the guard did not return to GREEN after restoration{what}; the "
            "working tree may still be mutated")


def run_pytest(target: str, root: Path | None = None) -> bool:
    """True when the target passes. The usual `run` for assert_can_fail.

    Takes a node id, not a whole suite: pointing this at everything makes a
    green result meaningless, because an unrelated failure elsewhere would
    read as the guard firing.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider"],
        cwd=str(root or Path.cwd()), capture_output=True, text=True)
    return r.returncode == 0
