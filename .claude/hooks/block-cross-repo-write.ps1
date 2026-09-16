# Blocks writes to sibling repositories from this repository's sessions.
#
# Team lead, 2026-09-15: work in hsbc-quantum-fraud-2026 never writes to
# spamfilter-multi or EvidenceBasedDB. Reading them on request is fine.
#
# The failure this guards: a Sprint 14 session reviewing PR #97 also examined
# EvidenceBasedDB, found real defects, and fixed/committed/pushed them there
# directly. Every finding was genuine and the boundary was still wrong. The
# changes arrived in that repository with no review, no tests as gatekeeper and
# no sprint record.
#
# Reads are deliberately NOT blocked: cat, grep, git log, git show, Read.

$ErrorActionPreference = 'Stop'
$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }

try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }

$tool = $payload.tool_name
$ti   = $payload.tool_input

# Sibling repositories, matched case-insensitively anywhere in the text.
$forbidden = @('spamfilter-multi', 'EvidenceBasedDB')

function Deny($what) {
    $msg = @"
BLOCKED: cross-repository write.

$what

This repository's sessions never write to spamfilter-multi or EvidenceBasedDB
(CLAUDE.md standing rules; SPRINT_EXECUTION_WORKFLOW.md invariant 9). Reading
them on request is fine.

If a finding belongs to that repository, REPORT it -- file, line and fix -- and
hand it to a session running there, so it lands through that repository's own
review and tests.
"@
    [Console]::Error.WriteLine($msg)
    exit 2
}

switch -Regex ($tool) {
    '^(Edit|Write|NotebookEdit)$' {
        $path = $ti.file_path
        if ($path) {
            foreach ($repo in $forbidden) {
                if ($path -imatch [regex]::Escape($repo)) {
                    Deny "Tool $tool targets a path inside '$repo':`n  $path"
                }
            }
        }
    }
    '^(Bash|PowerShell)$' {
        $cmd = $ti.command
        if (-not $cmd) { break }

        # The sibling must be the TARGET of the mutation, not merely mentioned.
        #
        # An earlier version tested "is this mutating anywhere?" and "does it
        # name a sibling anywhere?" independently, and ANDed the answers. That
        # blocked two legitimate read-only commands within minutes of shipping:
        # a grep whose PATTERN contained `New-Item|Remove-Item`, and a heredoc
        # writing a file in THIS repository whose text quoted both sibling
        # names. A guard that blocks correct work trains people to bypass it.
        foreach ($repo in $forbidden) {
            $r = [regex]::Escape($repo)

            # A redirect, copy, move or delete whose destination is the sibling.
            $targets = ">>?\s*[""']?[^""'|;&]*$r",
                       "\b(cp|mv|rm|tee|touch|mkdir|rmdir)\b[^;&|]*$r",
                       "\bsed\s+-i[^;&|]*$r",
                       "(^|[;&|]\s*|\|\s*)(Set-Content|Out-File|Add-Content|New-Item|Remove-Item|Copy-Item|Move-Item)\s[^;&|]*$r"

            foreach ($t in $targets) {
                if ($cmd -imatch $t) { Deny "A write targets '$repo':`n  $cmd" }
            }

            # Git writes are scoped by the working directory, so a `cd` into the
            # sibling (or -C pointing at it) followed by a writing subcommand is
            # the shape that matters.
            $gitWrite = 'git\s+(-C\s+\S*\s+)?(add|commit|push|mv|rm|checkout|switch|apply|restore|reset|merge|rebase|tag|branch\s+-[dDmM])'
            if ($cmd -imatch $gitWrite) {
                if ($cmd -imatch "cd\s+[""']?[^""';&|]*$r" -or
                    $cmd -imatch "git\s+-C\s+[""']?[^""';&|]*$r") {
                    Deny "A git write runs inside '$repo':`n  $cmd"
                }
            }
        }
    }
}

exit 0
