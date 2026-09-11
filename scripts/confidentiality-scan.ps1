<#
.SYNOPSIS
    Pre-send / pre-publication confidentiality scan (Stage 7; F19, F10).
.DESCRIPTION
    Scans the MARKDOWN SOURCES of an outgoing package for content that must
    never leave this repository, and reports findings with file and line so a
    human can adjudicate each one. Exits 1 on any HIGH finding.

    Categories:
      HIGH   employer references; credential values; account identifiers;
             QPU balances tied to a named account; .env content
      (the private-repo-URL rule was retired 2026-09-11 when the repository
       was made public; see the commented rule below for how to restore it)
      REVIEW absolute local paths; personal email addresses; anything naming
             a specific machine

    This is a scan, not a guarantee. The team lead walks every HIGH and REVIEW
    finding before sending, per the F19 acceptance criteria.
.EXAMPLE
    .\scripts\confidentiality-scan.ps1 -Paths docs\paper\proposal.md,docs\paper\appendix.md
#>
param(
    [Parameter(Mandatory)][string[]]$Paths
)
$ErrorActionPreference = 'Stop'

$high = @(
    @{ Name = 'Employer name';            Pattern = '(?i)progressive' },
    @{ Name = 'Employer repo/remote';     Pattern = '(?i)github\.com/(?!kimmeyh)[A-Za-z0-9_.-]+' },
    @{ Name = 'API token value';          Pattern = '(?i)(api[_-]?(key|token)|QCI_TOKEN|QCI_API_KEY)\s*[=:]\s*[''"]?[A-Za-z0-9._\-]{16,}' },
    # RETIRED 2026-09-11 (F37). This rule matched the repository's own name and
    # was correct while the repository was private: citing a URL a reader cannot
    # open is a defect, and the submission's reproducibility claims rested on it.
    # The repository is public as of 2026-09-11 (anonymous API returns 200), so
    # the citation is now REQUIRED rather than forbidden -- Appendix C's "every
    # figure regenerates from the public repository" depends on it. Leaving the
    # rule in place blocked a correct document on every scan.
    # If visibility is ever reverted, restore this line AND re-check every
    # document that cites the URL:
    #     @{ Name = 'Private repo URL';    Pattern = '(?i)hsbc-quantum-fraud-2026' },
    @{ Name = 'QPU balance (account)';    Pattern = '(?i)(balance|remaining)[^.\n]{0,40}\d{3,}\s*(QPU|second)' },
    @{ Name = 'dotenv content';           Pattern = '(?m)^\s*(QCI_API_URL|QCI_TOKEN|QCI_API_KEY)\s*=' }
)
$review = @(
    @{ Name = 'Absolute local path';      Pattern = '(?i)[A-Z]:\\(Data|Users)\\' },
    @{ Name = 'WSL mount path';           Pattern = '/mnt/[a-z]/' },
    @{ Name = 'Personal email';           Pattern = '[A-Za-z0-9._%+-]+@(aol|gmail|yahoo|outlook|hotmail)\.com' },
    @{ Name = 'Named machine';            Pattern = '(?i)\bkimme\b' }
)

$nHigh = 0; $nReview = 0
foreach ($p in $Paths) {
    if (-not (Test-Path $p)) { Write-Host "MISSING: $p"; $nHigh++; continue }
    $lines = Get-Content -LiteralPath $p
    for ($i = 0; $i -lt $lines.Count; $i++) {
        foreach ($rule in $high) {
            if ($lines[$i] -match $rule.Pattern) {
                Write-Host ("HIGH   {0}:{1}  [{2}]  {3}" -f $p, ($i + 1), $rule.Name, $lines[$i].Trim())
                $nHigh++
            }
        }
        foreach ($rule in $review) {
            if ($lines[$i] -match $rule.Pattern) {
                Write-Host ("REVIEW {0}:{1}  [{2}]  {3}" -f $p, ($i + 1), $rule.Name, $lines[$i].Trim())
                $nReview++
            }
        }
    }
}

Write-Host ""
Write-Host ("Scanned {0} file(s): {1} HIGH, {2} REVIEW" -f $Paths.Count, $nHigh, $nReview)
if ($nHigh -gt 0) {
    Write-Host "RESULT: BLOCKED. Resolve every HIGH finding before this package leaves the repository."
    exit 1
}
Write-Host "RESULT: no HIGH findings. The team lead still walks each REVIEW line before sending."
exit 0
