# M6 review - surface ONLY played-and-unreviewed decisions (result set, reviewed empty).
# Mirrors src/decisionlog.played_unreviewed. Usage:  pwsh predictions/review.ps1 [-Path <csv>]
param([string]$Path = "$PSScriptRoot/decisions.csv")

if (-not (Test-Path $Path)) {
    Write-Host "no decisions.csv yet ($Path) - nothing logged."
    exit 0
}

$rows = Import-Csv $Path | Where-Object { $_.result -and -not $_.reviewed }
if (-not $rows) {
    Write-Host "nothing to review (no played-and-unreviewed matches)."
    exit 0
}

Write-Host "PLAYED & UNREVIEWED ($($rows.Count)):"
$rows | Format-Table utc, home, away, pick, result, ev, source -AutoSize
