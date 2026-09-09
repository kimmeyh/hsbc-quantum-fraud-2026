<#
.SYNOPSIS
    PreToolUse hook blocking a carry-forward branch cut from develop/main.
    Enforces the OTHER half of workflow 6.6: the next sprint branch is cut FROM
    THE CURRENT FEATURE BRANCH, never from develop after the merge.

.DESCRIPTION
    Written 2026-09-08 after Claude cut feature/20260909_Sprint_10 with
    `git checkout -b feature/20260909_Sprint_10 origin/develop` during the
    Sprint 9 close-out. No commits were lost that time -- the merge had already
    carried everything and the uncommitted work followed the checkout -- so the
    violation was invisible in the outcome and was caught only by re-reading
    6.6. That is exactly the failure a hook should catch: the rule's stated
    harm (losing uncommitted work) does not appear every time it is broken, so
    a clean result is not evidence the flow was right.

    The sibling hook block-carry-forward-stash.ps1 already enforces "never
    stash to carry forward". It fired correctly in the same sequence. This one
    covers the branch-source clause that had no guard.

    ALLOWED (the prescribed flow):   git checkout -b feature/<date>_Sprint_<N+1>
    BLOCKED (what went wrong):       git checkout -b <name> origin/develop

    A bare `checkout -b` inherits HEAD, which on a just-merged feature branch
    is the correct start point. Only an EXPLICIT develop/main start point is
    blocked.

.NOTES
    Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
    Bypass: literal token allow_branch_from_base (team-lead-sanctioned only),
    for the legitimate case of starting genuinely new work off develop that is
    not a sprint carry-forward.
    Matches INVOCATIONS, not text: quoted strings and heredoc bodies are
    stripped first, so commit messages and docs describing the rule do not
    trip it (spamfilter F130-S51 false-positive lesson).
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

if ($cmd -match 'allow_branch_from_base') { exit 0 }

# Strip data regions (heredocs, quoted spans) so text ABOUT the rule is safe.
$scan = $cmd
$scan = [regex]::Replace($scan, "(?s)<<-?\s*'?""?([A-Za-z_][A-Za-z0-9_]*)'?""?.*?^\s*\1\s*$", ' ', 'Multiline')
$scan = [regex]::Replace($scan, "@'(?s).*?'@", ' ')
$scan = [regex]::Replace($scan, "'[^']*'", ' ')
$scan = [regex]::Replace($scan, '"[^"]*"', ' ')

# git checkout -b <name> <base>   /   git switch -c <name> <base>
# The start point is the token AFTER the new branch name. A bare form has none.
$pattern = '(?:git\s+checkout\s+(?:-b|-B)|git\s+switch\s+(?:-c|-C))\s+(\S+)\s+(\S+)'
$m = [regex]::Match($scan, $pattern)

if ($m.Success) {
    $newBranch = $m.Groups[1].Value
    $base      = $m.Groups[2].Value

    # Only flag an explicit develop/main start point.
    if ($base -match '^(?:[A-Za-z0-9_.-]+/)?(?:develop|main|master)$') {
        $msg = @"
[BLOCKED] Carry-forward branch cut from '$base' (workflow 6.6; ADR-0004).

6.6 is explicit: on merge notification, create the next sprint branch FROM THE
CURRENT FEATURE BRANCH, and "never branch from develop after the merge".

Use:
  git checkout -b $newBranch
  (bare -- no start point; the working tree and HEAD both follow)

WHY THIS IS BLOCKED EVEN WHEN IT SEEMS TO WORK: cutting from develop drops any
uncommitted work and any feature-branch commit the merge did not carry. When
the merge HAS carried everything, the result looks identical to the correct
flow, so a clean `git status` is not evidence the cut was right. That is how
this slipped through at the Sprint 9 close-out.

Recovery for a branch already mis-cut is cherry-pick onto a correctly-cut
branch, never stash.

If this is genuinely new work off $base and NOT a sprint carry-forward, re-run
with the literal token allow_branch_from_base in the command.
"@
        [Console]::Error.WriteLine($msg)
        exit 2
    }
}

exit 0
