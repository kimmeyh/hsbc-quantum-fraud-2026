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

# git checkout -b <name> [options] <base>   /   git switch -c <name> [options] <base>
#
# FOUR bypasses found in review of PR #58, all verified against the live hook:
#   1. an option between the name and the base captured group 2, so
#      `--track origin/develop`, `--no-track origin/develop` and `switch -c -t`
#      all sailed through while cutting from develop
#   2. quoting the branch name blanked the span, because the quote-stripping
#      for heredocs and prose runs BEFORE this match and eats the operand
#   3. [regex]::Match returns only the FIRST match, so the second command in
#      `git checkout -b tmp HEAD && git checkout -b feature/x origin/develop`
#      was never inspected
#   4. once (3) was fixed by looping, the operand pattern still swallowed the
#      `&&` separator as if it were an operand, so the chained case merged into
#      one match and the offending base was read as a mid-list token
#
# So: split on command separators FIRST, run the match per segment, take
# operands only up to the next separator, and strip quotes at the operand level
# on the ORIGINAL text rather than relying on the blanked copy.
# Heredoc BODIES are removed first (a commit message describing the rule must
# not trip it); quoted spans are NOT blanked here, because a quoted branch
# name is an operand this hook has to read.
$hd = [regex]::Replace($cmd, "(?s)<<-?\s*'?""?([A-Za-z_][A-Za-z0-9_]*)'?""?.*?^\s*\1\s*$", " ", "Multiline")
$hd = [regex]::Replace($hd, "@'(?s).*?'@", " ")
$segments = [regex]::Split($hd, '\s*(?:&&|\|\||;|\||\r?\n)\s*')

foreach ($seg in $segments) {
    # Heredoc bodies and prose still must not trip it, so a segment that is
    # clearly documentation (no leading git) is skipped by the pattern anyway.
    $m = [regex]::Match($seg, '(?:git\s+checkout\s+(?:-b|-B)|git\s+switch\s+(?:-c|-C))((?:\s+\S+)+)')
    if (-not $m.Success) { continue }

    $operands = $m.Groups[1].Value.Trim() -split '\s+'
    # Drop option tokens; strip surrounding quotes; what remains is <name> <base>.
    $positional = @($operands |
        Where-Object { $_ -notmatch '^-' } |
        ForEach-Object { $_ -replace '^["'']+|["'']+$', '' } |
        Where-Object { $_ -ne '' })
    if ($positional.Count -lt 2) { continue }

    $newBranch = $positional[0]
    $base      = $positional[1]

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
flow, so a clean git status is not evidence the cut was right. That is how
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
