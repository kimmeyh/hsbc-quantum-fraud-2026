<#
.SYNOPSIS
    Refuse git operations that would rewrite published history or move the
    frozen tags (F68, team lead 2026-09-12).

.DESCRIPTION
    Two commits are load-bearing for claims this project has already PUBLISHED,
    and both are cited in documents that were submitted and judged:

      95751b9  the preregistration freeze, tag `prereg-freeze`. Appendix B cites
               it by hash; Appendix C stakes "every figure regenerates from the
               public repository" on it resolving anonymously.

      the submission commit, from which the three judged PDFs were built and
      whose SHA-256 hashes are recorded in docs/submission/PACKAGE.md.

    The repository has been public since 2026-09-11. A rewrite does not just
    inconvenience us: it breaks a citation in a document a judge may open during
    the review window, and there is no way to correct the submitted PDF.

    WHAT THIS BLOCKS. Force-pushes, history-rewriting commands (filter-branch,
    filter-repo, rebase onto published history, reset --hard against a remote
    ref), and any attempt to move, delete or re-point `prereg-freeze`.

    WHAT IT DOES NOT BLOCK. Ordinary commits, merges, new tags, branch deletes,
    and rebases of local feature work that has never been pushed. Growing the
    repository forward is expected and is what a live project looks like.

    HOW TO PROCEED IF A REWRITE IS GENUINELY NEEDED. It almost certainly is not.
    If a secret were committed, the right answer is rotation plus a forward
    commit, not a rewrite -- the pre-flip scan across all 259 commits found no
    secret ever committed, so this case is hypothetical. If the team lead
    nevertheless directs a rewrite, record it:

        .claude/.history-rewrite-approved

    Creating that file to unblock yourself is the evasion this hook exists to
    prevent, and unlike most such evasions this one is not recoverable.
#>
$ErrorActionPreference = 'Stop'

try { $raw = [Console]::In.ReadToEnd() } catch { exit 0 }
if (-not $raw) { exit 0 }

try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }

$cmd = $payload.tool_input.command
if (-not $cmd) { exit 0 }

# Normalise whitespace so spacing variations cannot slip past the patterns.
$c = ($cmd -replace '\s+', ' ')

$patterns = @(
    @{ Name = 'force push';        Pattern = 'git\s+push\b[^|;&]*(--force\b|--force-with-lease\b|\s-f\b)' },
    @{ Name = 'filter-branch';     Pattern = 'git\s+filter-branch\b' },
    @{ Name = 'filter-repo';       Pattern = 'git\s+filter-repo\b' },
    @{ Name = 'hard reset to a remote ref'; Pattern = 'git\s+reset\s+--hard\s+origin/' },
    @{ Name = 'move or delete the freeze tag'; Pattern = 'git\s+tag\b[^|;&]*(-d|-f|--delete|--force)[^|;&]*prereg-freeze' },
    @{ Name = 'delete the freeze tag on the remote'; Pattern = 'git\s+push\b[^|;&]*(--delete|:refs/tags/)[^|;&]*prereg-freeze' }
)

$hit = $null
foreach ($p in $patterns) {
    if ($c -match $p.Pattern) { $hit = $p.Name; break }
}
if (-not $hit) { exit 0 }

$root = $env:CLAUDE_PROJECT_DIR
if (-not $root) { $root = (Get-Location).Path }
if (Test-Path (Join-Path $root '.claude/.history-rewrite-approved')) { exit 0 }

$msg = @"
[BLOCKED] This command would $hit.

The repository is PUBLIC and two commits are cited in documents that have
already been submitted and judged:

  - 95751b9 (tag prereg-freeze), cited by hash in Appendix B. Appendix C's
    claim that "every figure regenerates from the public repository" depends
    on it resolving anonymously.
  - the submission commit, from which the three judged PDFs were built; their
    SHA-256 hashes are in docs/submission/PACKAGE.md.

A rewrite breaks a citation inside a PDF that cannot be corrected.

Ordinary commits, merges, new tags and unpushed local rebases are all fine and
are NOT blocked. Move the repository forward instead of rewriting it.

If the team lead has genuinely directed a rewrite:

  Set-Content .claude/.history-rewrite-approved "<who directed it, and why>"

Do NOT create that file to unblock yourself. Unlike most such evasions, this
one cannot be undone.
"@

[Console]::Error.WriteLine($msg)
exit 2
