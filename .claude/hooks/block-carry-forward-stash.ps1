<#
.SYNOPSIS
    PreToolUse hook blocking `git stash` (carry-forward protection).
    Ported 2026-09-02 from spamfilter-multi per the Sprint 2 retro disposition
    (WINDOWS_POWERSHELL_GUIDE hooks assessment). Enforces workflow 6.6 and
    ADR-0004: NEVER stash to carry forward; create the branch, then COMMIT.

.NOTES
    Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
    Bypass: literal token allow_stash in the command (team-lead-sanctioned only).
    Matches INVOCATIONS, not text: quoted strings and heredoc bodies are
    stripped before matching (spamfilter F130-S51 false-positive lesson).
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

if ($cmd -match 'allow_stash') { exit 0 }

# Strip data regions (heredocs, quoted spans) so docs ABOUT stash do not trip it.
$scan = $cmd
$scan = [regex]::Replace($scan, "(?s)<<-?\s*'?""?([A-Za-z_][A-Za-z0-9_]*)'?""?.*?^\s*\1\s*$", ' ', 'Multiline')
$scan = [regex]::Replace($scan, "@'(?s).*?'@", ' ')
$scan = [regex]::Replace($scan, "'[^']*'", ' ')
$scan = [regex]::Replace($scan, '"[^"]*"', ' ')

if ($scan -match 'git\s+stash\s+(list|show)\b') { exit 0 }

if ($scan -match 'git\s+stash\b') {
    $msg = @"
[BLOCKED] git stash is disallowed (workflow 6.6 carry-forward rule; ADR-0004).

Use the DETERMINISTIC flow instead:
  1. Create the next branch:  git checkout -b <next-branch>
  2. COMMIT the uncommitted files on that branch -- the working tree follows
     a checkout -b; stashing is never needed for carry-forward.

Recovery for a mis-cut branch is cherry-pick, never stash. If the team lead
has sanctioned a genuine non-carry-forward stash, re-run with the literal
token allow_stash in the command.
"@
    [Console]::Error.WriteLine($msg)
    exit 2
}

exit 0
