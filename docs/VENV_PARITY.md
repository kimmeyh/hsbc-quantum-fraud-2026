# Cross-platform parity measurement (F83, Sprint 17 Task H)

Measured 2026-09-19. The card asked whether this repository reproduces on
Linux as well as on Windows, and whether Appendix C's environment claim is
accurate. Both were measured rather than argued.

## H1. The Appendix C claim is CORRECT, and enforced in code

`docs/paper/appendix.md` states the resolved environment as "eqc-models
0.21.0, qci-client 5.0.2, Python 3.12, Linux". The campaign was driven from a
Windows workstation, so this looked like it might be a submission-accuracy
defect. It is not.

**The hardware path refuses to run anywhere but POSIX.** Both entry points
that touch the device or the tuning ladder call `_require_wsl()`, which is a
hard `SystemExit`, not a warning:

- `experiments/src/run_hardware.py:142-144`, called at line 406
- `experiments/src/tune_proxy.py:58-60`, called at lines 164 and 237

```python
def _require_wsl():
    if os.name != "posix":
        raise SystemExit("run under WSL (full-pair build needs fork)")
```

The reason is the A3 full-pair pool build, which uses `multiprocessing` with
the fork start method. Windows has no `fork`. So every metered fit and every
tuning run in the campaign necessarily executed under WSL/Linux, and the
appendix records the environment that produced the figures.

`experiments/requirements-lock.txt` records the interpreter as Python 3.12.10,
as a comment rather than a requirement (a `python==3.12.10` line made the file
uninstallable until 2026-09-12, F69).

**Verdict: no correction needed, and no submitted document was touched.** What
the appendix says is what ran.

## H2. Suite parity, measured on both platforms

Same commit, same locked dependency versions, same test selection.

| | Windows | Linux (WSL2) |
|---|---|---|
| Python | 3.12.10 | 3.12.14 |
| Passed | 1,031 | 1,018 |
| Failed | **0** | **0** |
| Skipped | 71 | 86 |

**Zero failures on either platform.** Every test that runs on both produces
the same verdict. There is no behavioral divergence to report, which is the
result the card was written to establish.

### Accounting for the 15-test difference, which is the real finding

The gap is entirely one file. On Linux, `test_cross_repo_write_guard.py`
skipped 15 of its 17 cases:

```
SKIPPED [15] test_cross_repo_write_guard.py:111: powershell not on PATH (non-Windows CI)
```

**That skip condition was wrong.** The hook under test is
`.claude/hooks/block_cross_repo_write.py`, a Python file invoked through
`sys.executable`. PowerShell is not involved at any point. The `skipif` was a
leftover from before F78 converted the hooks from PowerShell to Python.

The cost is specific and it is not cosmetic. **CI runs on ubuntu-latest.** The
guard enforcing the team lead's cross-repository boundary -- the rule added on
2026-09-15 after a session working this repository wrote into EvidenceBasedDB
-- has never been exercised in CI. It passed by being skipped. The boundary was
protected on the team lead's workstation and nowhere else.

**Fixed**: the `skipif` is removed and the now-unused `shutil` import with it.
All 17 cases run on both platforms.

**Proven, not assumed**: neutering the hook's block call turns the suite RED on
Linux (2 failed, 15 passed), and restoring returns it to 17 passed. A test
newly enabled on a platform is worth nothing until it has been shown to fail
there.

### The remaining 71 skips are correct

They are `test_hook_parity.py` cases for the retired `.ps1` hooks. On Windows
they skip as "already removed"; on Linux as "powershell not on PATH". Both
readings are accurate and neither hides anything: the files are gone because
F78 deleted them.

## Environment used for the measurement

A minimal Linux venv at `~/.cache/hsbc_parity_venv` inside WSL2, **outside the
repository**, built from `experiments/requirements-lock.txt` at exactly the
pinned versions. It is a measurement instrument, not project infrastructure,
and nothing in the repository depends on it.

Worth recording for the ENVIRONMENT.md question the team lead raised: a second
full venv costs about 1.5 GB, against 1.1 GB for the Windows one. Nothing here
requires maintaining one permanently. The measurement above can be reproduced
by building it again from the lock file.

The dependency install order also produced a useful incidental result: **every
package in the lock file installs cleanly on Linux at its pinned version**,
including `eqc-models` 0.21.0 and `qci-client` 5.0.2. The reproducibility claim
in Appendix C holds on a machine that is not this one.

## What was NOT done, deliberately

Per the team lead's instruction, this task TESTS whether the post-results
record reproduces; it does not edit it.

- `results.json` and `results*.json`: **unchanged**. Not written, not
  regenerated.
- `experiments/results/gate_report.md`: **unchanged**. It is a generated
  evidence artifact owned by `score_gates.py`.
- `docs/paper/*` and `experiments/PREREGISTRATION.md`: **unchanged**. Frozen
  records of a filing made 2026-09-12.

The only production change from this task is the removal of a stale `skipif`
in a test file.
