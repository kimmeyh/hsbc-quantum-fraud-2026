# Windows PowerShell Guide

**Purpose**: PowerShell and Windows-environment practices for this repository: shell selection, error patterns observed in this project's own sprints, and conventions adapted from spamfilter-multi's WINDOWS_DEVELOPMENT_GUIDE.md and TROUBLESHOOTING.md (Sprint 2 retro improvement 1).
**Audience**: Claude Code sessions executing commands on this Windows 11 host.
**Last Updated**: 2026-09-17

> **The interpreter paths below are WINDOWS paths, and that is correct for
> this document.** For the Linux and WSL equivalents, and for how the venv
> is created on each OS, see **docs/ENVIRONMENT.md**, which is the single
> place either is written down. The two venvs are not interchangeable: a
> Windows one has `Scripts/`, a Linux one has `bin/`.

## Shell selection

PowerShell 7+ is the primary shell. Bash (Git Bash POSIX sh) is available for POSIX-only tooling. Decision rule: PowerShell by default; bash only when a tool demands POSIX syntax. Never mix syntaxes (`&&` works in PowerShell 7 but heredocs, `[ -f x ]`, and backslash-path handling do not transfer between shells). Never wrap PowerShell in bash or vice versa (ADR-0017 lesson: wrapping loses toolchain context on this exact host).

## Error patterns OBSERVED IN THIS PROJECT (with fixes)

1. **Cmdlet failures poison the exit code even when suppressed.** `Get-ChildItem <empty-or-missing> -ErrorAction SilentlyContinue` still exits 1 (observed listing empty `datasets/` dirs). Fix: promote to terminating and swallow: `try { Get-ChildItem $p -ErrorAction Stop } catch {}` , or end the command with an expression that always succeeds (a summary string).
2. **`Select-String` with zero matches** contributes a failure-looking result. Fix: capture to a variable and test `if ($m) {...}`; never let a possibly-empty match be the last statement of a command whose exit code matters.
3. **NEVER edit JSON with `-replace`.** sprint_status.json was regex-edited in Sprint 2 (fragile, ordering-dependent). Fix: `scripts/update-sprint-status.ps1` (ConvertFrom-Json round-trip) or a Python one-liner. Applies to any structured file: parse, mutate, serialize.
4. **uv-created venvs have no pip.** `python -m pip` fails with "No module named pip". Fix: `uv pip install <pkg> --python .venv\Scripts\python.exe`.
5. **Here-string closers must sit at column 0.** `'@` indented is a parse error. Git commit messages use `git commit -m @'... '@` with the closer unindented; `--%` stop-parsing token for arguments containing `%` or `@`.
6. **Legacy vs new credentials shadowing** (Kaggle incident): user-level env vars silently override OAuth caches. One credential system per service (ADR-0011); when auth misbehaves, print key NAMES present in the environment first.
7. **Python Unicode on the Windows console** (cp1252): set `$env:PYTHONIOENCODING = 'utf-8'` before any Python that prints non-ASCII; better, keep script output ASCII with bracketed markers ([OK]/[FAIL]) per QUALITY_STANDARDS.

## Adapted spamfilter practices

- **Quote every path** (spaces in this tree are real); `cd "D:\..."` quoted always.
- **Command chaining**: `;` for sequence, `&&` only in PowerShell 7 contexts; separate dependent steps into separate calls when exit codes matter.
- **Process management**: `Stop-Process -Name x -Force -ErrorAction SilentlyContinue` then `Start-Sleep -Seconds 2` before rebuilding anything file-locked.
- **Long-running work**: background execution with output files; per-unit persistence (per Optuna trial, per fit) so interruption loses one unit; never edit a job's inputs while it runs.
- **Known-failure triage**: before investigating a failing script, read its header and this guide; the failure may be documented (workflow invariant; headers land per disposition item 18).

## WSL interop (Sprint 3 retro improvement 3)

- **Never pass complex commands inline through `wsl.exe -e bash -lc "..."`**: PowerShell and bash quoting interact destructively (variables expand empty, quotes glue arguments; two silent failures in Sprint 3). Write a `.sh` script file in the repo, run `wsl.exe -e bash /mnt/d/...`.
- **Per-distro venv**: the Windows .venv is unusable from Linux; create a venv inside WSL (python3.12 via dnf on OracleLinux) and pin the same critical library versions (sklearn matched at 1.9.0 in Sprint 3 for pool comparability).
- **Windows paths in frozen code**: set `HSBC_ULB_CSV` to the WSL path (`/mnt/d/...`); `data.ulb_csv()` reads it on every call. The former advice was to shim at the consumer by rebinding `data.ULB_CSV`, and the `qubo_proxy.py` shim it pointed at was deleted in Sprint 10 along with that constant. Rebinding now fails SILENTLY: the assignment creates an attribute `load_ulb()` never reads, so the loader quietly falls back to the repo-relative default. Several arms must run under WSL (`run_hardware.py`, `tune_proxy.py`, the A3 full-pair build), so this matters.
- **Default WSL user may be root**: `~` resolves differently per user; use absolute paths in scripts.

## Hooks (assessment from spamfilter .claude/hooks)

| Source hook | Purpose there | Applicability here | Plan |
|---|---|---|---|
| block-carry-forward-stash.ps1 | Hard-block `git stash` (carry-forward protection) | Direct: stash is banned here too | Port in F1 sprint |
| verify-closeout-complete.ps1 | Stop hook blocking completion claims contradicted by artifacts | High value once sprint cadence is steady | Port in F1 sprint (adapted to our checklist paths) |
| require-sprint-cards.ps1 | Blocks task work before cards exist | Concept adopted in workflow 3.4; hook port optional | Backlog |
| sprint-auto-advance.ps1 | Enforces the auto-advance window bounds | Tied to spamfilter's status schema; ours differs | Backlog, revisit Phase 2 |

The pre-commit confidentiality hook (this repo's own, `.git/hooks/pre-commit`) remains active and verified.

## Quick reference for this repo

```powershell
# Venv python and tools
.\.venv\Scripts\python.exe -m pytest experiments\src -q
uv pip install <pkg> --python .venv\Scripts\python.exe

# Manifest verify (before hardware blocks; on the statistical checklist)
.\.venv\Scripts\python.exe scripts\manifest.py verify

# Sprint status (never regex)
.\scripts\update-sprint-status.ps1 -Set status=phase_4_execution
```

## Background python: always pass `-u` (Sprint 6 retro improvement 1)

Python buffers stdout when its output is piped or redirected, which every
`run_in_background` invocation does. A long-running job therefore writes NOTHING
to its output file until it exits, so the file looks empty while the job is
healthy. Sprint 6 lost four check cycles to this before diagnosing it: a
20-minute mixed-pool run showed an empty output file the whole time and looked
dead.

```powershell
# WRONG: output invisible until exit
.\.venv\Scripts\python.exe experiments\src\mixed_pool.py

# RIGHT: line-buffered, progress visible as it happens
.\.venv\Scripts\python.exe -u experiments\src\mixed_pool.py
```

Use `-u` for anything that runs longer than a few seconds, and especially for
metered hardware blocks, where watching progress is the difference between
catching a problem at fit 1 and finding it at fit 10.
