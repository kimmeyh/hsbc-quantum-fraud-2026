<#
.SYNOPSIS
    Block shell metacharacters inside a Python string that Bash will expand
    before Python ever sees it (F48, Sprint 11 retrospective improvement 4).

.DESCRIPTION
    The sibling hook block-unraw-escape.ps1 catches Windows path escapes in
    non-raw PYTHON strings. It does not catch SHELL metacharacters, and those
    are worse, because bash rewrites the command BEFORE python is invoked.

    Two constructs do this inside a double-quoted or unquoted span:

        `...`        command substitution, backticks
        $(...)       command substitution
        ${...}       parameter expansion

    OBSERVED IN SPRINT 11. Backticks inside a Python string in a Bash command
    were expanded as command substitution. Bash executed a source file as shell,
    and the backticked filenames were silently DELETED from a master-plan line.
    The edit reported success. The damage was only visible on inspection, and it
    was found by reading the file, not by any test.

    That is the defect signature worth blocking: the command succeeds, the
    output looks plausible, and the wrong thing happened. A crash would have
    been kinder.

    IT FIRED TWICE DURING SPRINT 14 PLANNING, correctly, while I was writing
    inline Python that referenced a backslash. Both times the fix was to write
    the script to a file instead of threading it through a shell string.

    THE FIX IS ALWAYS ONE OF THREE:
      1. Write the script to a .py file and run it. Best for anything non-trivial
      2. Use a SINGLE-QUOTED heredoc, which suppresses all expansion:
             python - <<'PYEOF'    (note the quotes around PYEOF)
      3. Escape the metacharacter for the shell, if it is genuinely wanted

.NOTES
    Exit 0 = allow. Exit 2 = block; stderr is fed back to Claude.
    Bypass: the literal token allow_shell_metachar, for the rare case where the
    expansion is deliberate.

    Deliberately NARROW. It inspects only commands that invoke python, and only
    spans that bash would actually expand. A single-quoted heredoc is exempt
    because it is the recommended fix, and blocking the fix would make the hook
    worse than useless -- the mistake the escape hook's first version made.
#>

$ErrorActionPreference = 'Stop'

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
    $payload = $raw | ConvertFrom-Json
} catch { exit 0 }   # fail open on malformed payload

$cmd = $null
if ($payload.tool_input -and $payload.tool_input.command) {
    $cmd = [string]$payload.tool_input.command
} elseif ($payload.command) {
    $cmd = [string]$payload.command
}
if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }
if ($cmd -match 'allow_shell_metachar') { exit 0 }

# A SINGLE-QUOTED heredoc suppresses every expansion below, and it is the fix
# this hook recommends. Exempt it, or the hook blocks its own advice.
if ($cmd -match "<<\s*'[A-Za-z_][A-Za-z0-9_]*'") { exit 0 }

# PER-LINE anchoring, not per-command. The first version tested the WHOLE
# command for a python invocation and then scanned every line, which blocked
# two correct commands within minutes of being written: a multi-line block
# whose last line ran python (flagging backticks in an unrelated earlier echo),
# and a command with no python at all, because the word appeared inside echoed
# prose. A hook that blocks correct commands gets disabled, and then it guards
# nothing -- the exact failure the sibling hook's comments warn about.
# python must sit at a COMMAND POSITION: line start, or just after a
# separator (; && || |) or an opening paren, optionally behind a path like
# .venv/Scripts/ or /usr/bin/. A bare word-match blocked
#     echo "backticks `here` but no python invocation"
# because the word appeared in the echoed prose. A hook that blocks a
# sentence mentioning python is a hook that gets switched off.
$invokes = '(?:^|[;&|(]|&&|\|\|)\s*(?:[^\s;&|()]*[/\\])?python[0-9.]*(?:\.exe)?(?:\s|$)'

$bad = @()

foreach ($line in ($cmd -split "`n")) {
    $t = $line.Trim()
    if ($t.StartsWith('#')) { continue }
    if ($line -notmatch $invokes) { continue }

    # Backtick command substitution. Bash expands it anywhere outside single
    # quotes; we flag it whenever it appears on a python invocation line.
    if ($line -match '`[^`]+`') {
        $bad += '`...` command substitution'
    }
    # $( ... ) command substitution.
    if ($line -match '\$\([^)]*\)') {
        $bad += '$(...) command substitution'
    }
    # ${ ... } parameter expansion.
    if ($line -match '\$\{[^}]*\}') {
        $bad += '${...} parameter expansion'
    }
}

if ($bad.Count -eq 0) { exit 0 }

$sample = ($bad | Select-Object -Unique | Select-Object -First 3) -join "`n    "
$msg = @"
[BLOCKED] Shell metacharacter in a python command; bash expands it BEFORE
python runs (F48, Sprint 11 retrospective improvement 4).

Found:
    $sample

Why this is blocked and not merely warned: in Sprint 11 backticks inside a
Python string were expanded as command substitution. Bash executed a source
file as shell and SILENTLY DELETED the backticked filenames from a master-plan
line. The command reported success and the damage was only visible on
inspection. A crash would have been kinder than a plausible-looking wrong
result.

FIX, in order of preference:

  1. Write the script to a .py file and run it. Best for anything non-trivial,
     and it makes the script reviewable and re-runnable.

  2. Use a SINGLE-QUOTED heredoc, which suppresses every expansion:

         python - <<'PYEOF'
         ...your code...
         PYEOF

     The quotes around PYEOF are the whole point. Without them bash expands
     the body.

  3. Escape it for the shell, if the expansion is genuinely intended.

If the expansion IS deliberate, re-run with the literal token
allow_shell_metachar in the command.
"@

[Console]::Error.WriteLine($msg)
exit 2
