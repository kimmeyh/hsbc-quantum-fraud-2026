<#
.SYNOPSIS
    PreToolUse hook blocking Python string literals that contain a Windows path
    escape outside a raw string. Sprint 10 retrospective improvement 1.

.DESCRIPTION
    This failure has recurred five-plus times across sprints, twice in Sprint 10
    alone. The shape is always the same: a heredoc'd Python snippet contains a
    Windows path in a normal quoted string, e.g.

        p = 'D:\Data\Harold\...'

    Python reads \D as an invalid escape (SyntaxWarning today, SyntaxError in a
    future version) and \x, \u, \N as hard errors. In Sprint 10 it produced a
    silent wrong value once (a \b became a backspace inside a JSON path, writing
    the file to the wrong directory) and an outright crash twice.

    A rule against it already exists and has not worked, because it depends on
    remembering at the moment of writing. The sibling hooks
    (block-carry-forward-stash, block-branch-from-develop) demonstrate that the
    mechanical check succeeds where the remembered rule fails. This is the same
    treatment for the same class of problem.

    THE FIX IS ALWAYS THE SAME: prefix the literal with r, or use forward
    slashes. Both are one keystroke.

.NOTES
    Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
    Bypass: literal token allow_unraw_escape, for the rare case where the
    escape is deliberate (writing an actual tab or newline into a path string).
    Only inspects python heredocs, so shell strings and prose are untouched.
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
if ($cmd -match 'allow_unraw_escape') { exit 0 }

# Only look at commands that actually run python.
# Anchor on an actual INVOCATION, not the bare substring. `-notmatch 'python'`
# turned the scanner on for any command merely containing those letters: a path
# like C:/Python312/..., a filename test_python_paths.sh, `pip show
# python-dateutil`, or prose. During review of PR #58 it blocked a `gh api` call
# whose only Python content was example text inside the comment being posted.
if ($cmd -notmatch '(?:^|[\s;&|(])python[0-9.]*(?:\.exe)?(?:\s|$)') { exit 0 }

# Only a DRIVE-LETTER path is unambiguous enough to block on. Legitimate
# newline and tab escapes, and raw strings, must pass untouched: a hook that
# blocks the correct fix is worse than no hook. The first version of this did
# exactly that, so the match is now anchored on a drive letter inside a
# non-raw quoted span.
#
# Written while hitting this very bug several times over: every attempt to
# build this PowerShell source THROUGH another language's string literal ate
# the backslashes or turned them into control characters. That is the whole
# point of the hook, demonstrated on itself. The file is written literally.
$bad = @()

foreach ($line in ($cmd -split "`n")) {
    if ($line.Trim().StartsWith('#')) { continue }

    foreach ($m in [regex]::Matches($line, '(?<prefix>[A-Za-z]*)(?<q>[''"])(?<body>[^''"]*)\k<q>')) {
        # EXACT Python string prefixes only. This was -match '[rR]', a
        # substring test over a [A-Za-z]* capture, so an adjacent identifier
        # ending in r -- str'...', dir'...', ptr'...' -- silenced the block.
        # Valid prefixes are only r/b/f/u combinations; anything else abutting
        # a quote is an identifier, not a prefix.
        if ($m.Groups['prefix'].Value -match '(?i)^(?:r|rb|br|rf|fr)$') { continue }
        $body = $m.Groups['body'].Value
        $probe = $body -replace '\\\\', ''
        if ($probe -match '[A-Za-z]:\\[A-Za-z]') { $bad += $m.Value }
    }
}

if ($bad.Count -gt 0) {
    $sample = ($bad | Select-Object -First 3) -join "`n    "
    $msg = @"
[BLOCKED] Python string with an unescaped Windows path (Sprint 10 retro item 1).

Found:
    $sample

Python reads \D, \H, \U as invalid escapes and \b, \x, \n as real control
characters, so this either warns, crashes, or -- worst -- silently produces the
wrong value. In Sprint 10 a \b inside a path became a backspace and wrote a
file to the wrong directory; the JSON looked fine.

FIX, one keystroke either way:
    r'D:\Data\Harold\...'      <- raw string, preferred
    'D:/Data/Harold/...'       <- forward slashes work on Windows

This has recurred five-plus times, twice in this sprint. The rule existed and
did not hold, which is why it is now mechanical.

If the escape is genuinely intended, re-run with the literal token
allow_unraw_escape in the command.
"@
    [Console]::Error.WriteLine($msg)
    exit 2
}

exit 0
