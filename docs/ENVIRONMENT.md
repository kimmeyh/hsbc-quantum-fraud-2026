# Environment: creating the venv and invoking the interpreter

The one place this repository records how to build its environment and how to
run Python in it. Everything else references this file rather than restating a
path.

**Why one place.** The interpreter path was written out in 21 places across 16
files, and it is not discoverable from the environment: a bare `python` on this
machine is a different interpreter from the one the project uses. I got that
wrong myself in Sprint 15, reported nine test modules as failing for a missing
`sklearn`, and the dependency was installed all along. The wrong interpreter
produces a plausible wrong answer rather than an error, which is the class this
repository keeps paying for (Sprint 15 retrospective, IMP-4).

## Create the environment

**Windows**

```
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r experiments/requirements-lock.txt
```

**Linux, including WSL**

```
python3.12 -m venv .venv
.venv/bin/python -m pip install -r experiments/requirements-lock.txt
```

The lock file pins all 18 dependencies. That is deliberate and load-bearing:
amendment A29(h) records that drift in the comparator stack is material to the
null result, so `numpy==1.26.4`, `scikit-learn==1.9.0` and `xgboost==3.4.1` are
not free to move. Changing them needs an amendment, not a `pip install -U`.

**A venv is per-OS and is NOT shared.** A Windows `.venv` has `Scripts/` and
`python.exe`; a Linux one has `bin/` and `python`. They are not interchangeable,
so anyone moving between Windows and WSL builds a second one. `.venv/` is
gitignored for that reason.

## Invoke the interpreter

| OS | Interpreter |
|---|---|
| Windows | `.venv\Scripts\python.exe` |
| Linux, WSL | `.venv/bin/python` |

So a test run is:

```
.venv\Scripts\python.exe -m pytest experiments/src -q      # Windows
.venv/bin/python -m pytest experiments/src -q              # Linux
```

**Do not use a bare `python`.** It resolves to whatever is first on PATH, which
on a developer machine is usually a system install with none of the pinned
dependencies. The failure is a plausible import error that reads like a broken
checkout.

## Verify the environment is the right one

```
.venv\Scripts\python.exe -c "import sys, numpy, sklearn, xgboost; print(sys.executable); print(numpy.__version__, sklearn.__version__, xgboost.__version__)"
```

Expect the path to end in `.venv`, and `1.26.4 1.9.0 3.4.1`. Any other numbers
mean the environment does not match the lock file and no result from it is
comparable to a committed one.

## CI

`.github/workflows/` runs on `ubuntu-latest` with `python-version: 3.12`. It
installs from the same lock file, so a green CI run and a green local run are
the same run.

Until Sprint 16 the repository's hooks were PowerShell and could not execute on
that runner at all, which meant every guard was Windows-only protection while CI
ran Linux. F78 converted them; `.claude/hooks/*.py` now run in both places.
