<#
.SYNOPSIS
    Render a Markdown source to submission-grade PDF (ADR-0012 toolchain).
.DESCRIPTION
    Markdown -> PDF via pandoc + xelatex (MiKTeX). Page size is set through the
    LaTeX geometry package, so the document is laid out at that size from the
    start.

    HISTORY, so this is not reintroduced: an earlier version routed through Word
    (pandoc -> docx -> Word SaveAs) and set PageSetup.PaperSize AFTER opening the
    document. Word did not reflow, so it emitted 11x17 TABLOID pages while
    reporting plausible page counts. Page size and page count are both submission
    requirements (requirements-matrix B1), so this script verifies BOTH after
    rendering and fails loudly on either.
.EXAMPLE
    .\scripts\render-pdf.ps1 -Source docs\paper\proposal.md -Out docs\paper\out\proposal.pdf
#>
param(
    [Parameter(Mandatory)][string]$Source,
    [Parameter(Mandatory)][string]$Out,
    [ValidateSet('letter','a4')][string]$Paper = 'letter',
    [string]$Margin = '1in',
    # Opt-in pandoc Lua filters, passed straight through. F36 uses this for
    # float-tables.lua. Kept as a parameter rather than hard-wired so that
    # removing one line in render-all.ps1 reverts to the previous behaviour,
    # which matters eight days from the deadline.
    [string[]]$LuaFilter = @(),
    # Landscape is for WIDE-TABLE documents that are NOT part of the challenge
    # submission -- the gate report, whose widest table needs a 37-character
    # Cell column beside six numeric columns and overprints at portrait width.
    # Submission documents (proposal, appendix, team profile) stay portrait.
    [switch]$Landscape
)
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$src = (Resolve-Path $Source).Path
$outDir = Split-Path -Parent $Out
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }

# A PDF open in a viewer holds a write lock; name the cause rather than failing opaquely.
if (Test-Path $Out) {
    try {
        $probe = [System.IO.File]::Open((Resolve-Path $Out).Path, 'Open', 'ReadWrite', 'None')
        $probe.Close()
    } catch {
        throw ("Output PDF is LOCKED by another process: {0}. Close it (a PDF viewer is the usual cause) and re-run." -f $Out)
    }
}

# MiKTeX puts xelatex on the USER PATH, which a shell started before the install
# (or a non-login shell) does not inherit. Resolve it explicitly rather than
# failing with "xelatex not found" in an environment where it is installed.
$xelatex = (Get-Command xelatex -ErrorAction SilentlyContinue).Source
if (-not $xelatex) {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\xelatex.exe",
        "$env:ProgramFiles\MiKTeX\miktex\bin\x64\xelatex.exe",
        "C:\miktex\miktex\bin\x64\xelatex.exe"
    )
    $xelatex = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $xelatex) {
    throw "xelatex not found. Install MiKTeX, or add its bin directory to PATH. Checked PATH and the standard MiKTeX locations."
}

# MiKTeX enumerates every PATH entry at startup and ABORTS if one cannot be
# read ("MiKTeX cannot retrieve attributes for the directory ..."). This machine
# has stale entries, so xelatex died on a bare "Hello world" while the failure
# looked like a document problem. Run it with a minimal PATH holding only what
# the toolchain needs.
$pandoc = (Get-Command pandoc -ErrorAction SilentlyContinue).Source
if (-not $pandoc) { throw "pandoc not found on PATH." }
$texBin = Split-Path -Parent $xelatex
$safePath = @($texBin, "$env:SystemRoot\system32", $env:SystemRoot) -join ';'
$origPath = $env:PATH

$geom = if ($Paper -eq 'a4') { 'a4paper' } else { 'letterpaper' }
$orientArgs = if ($Landscape) { @('-V', 'geometry:landscape') } else { @() }
try {
    $env:PATH = $safePath
    $filterArgs = @()
    foreach ($f in $LuaFilter) {
        $fp = if ([System.IO.Path]::IsPathRooted($f)) { $f } else { Join-Path $root $f }
        if (-not (Test-Path $fp)) { throw "Lua filter not found: $f" }
        $filterArgs += "--lua-filter=$fp"
    }
    & $pandoc $src -o $Out --pdf-engine=$xelatex @filterArgs @orientArgs -V "geometry:$geom" -V "geometry:margin=$Margin" -V fontsize=10pt
} finally {
    $env:PATH = $origPath
}
if ($LASTEXITCODE -ne 0) { throw "pandoc/xelatex failed on $Source" }

# Verify what was actually produced: page size AND page count.
$py = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$abs = (Resolve-Path $Out).Path
$result = & $py -c "from pypdf import PdfReader; r=PdfReader(r'$abs'); b=r.pages[0].mediabox; w,h=round(float(b.width)),round(float(b.height)); n={(612,792):'US Letter',(595,842):'A4',(792,1224):'TABLOID 11x17',(792,612):'US Letter landscape',(842,595):'A4 landscape'}.get((w,h), 'OTHER %dx%dpt'%(w,h)); print('%d|%s'%(len(r.pages), n))"
$pages, $size = $result -split '\|'
$expected = if ($Paper -eq 'a4') { 'A4' } else { 'US Letter' }
if ($Landscape) { $expected = "$expected landscape" }
if ($size -ne $expected) { throw "WRONG PAGE SIZE: produced $size, expected $expected, for $Out" }
Write-Host "PDF written: $Out ($pages pages, $size)"
