param(
  [string]$OutJson = "output/reports/security/m365_cis_audit.json",
  [string]$OutCsv  = "output/reports/security/m365_cis_audit.csv",
  [switch]$SkipExchange,
  [switch]$SkipGraph,
  [string]$SPOAdminUrl,
  [switch]$Timestamped
)

# If -Timestamped, append timestamp to output filenames
if ($Timestamped) {
    $ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
    $OutJson = $OutJson -replace '\.json$', "_$ts.json"
    $OutCsv  = $OutCsv -replace '\.csv$', "_$ts.csv"
}

# Resolve output paths relative to repo root (two levels up from this script)
$repoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
if (-not [System.IO.Path]::IsPathRooted($OutJson)) { $OutJson = Join-Path $repoRoot $OutJson }
if (-not [System.IO.Path]::IsPathRooted($OutCsv)) { $OutCsv = Join-Path $repoRoot $OutCsv }

# Ensure output directories exist
$jsonDir = Split-Path -Parent $OutJson
$csvDir  = Split-Path -Parent $OutCsv
if ($jsonDir -and -not (Test-Path $jsonDir)) { New-Item -ItemType Directory -Path $jsonDir -Force | Out-Null }
if ($csvDir  -and -not (Test-Path $csvDir )) { New-Item -ItemType Directory -Path $csvDir  -Force | Out-Null }

# Import module
Import-Module -Force "$PSScriptRoot/modules/M365CIS.psm1"

Write-Host "[+] Connecting to Microsoft 365 services..."
Connect-M365CIS -SkipExchange:$SkipExchange -SkipGraph:$SkipGraph -SPOAdminUrl $SPOAdminUrl

Write-Host "[+] Running CIS Level 1 audit checks..."
$results = Invoke-M365CISAudit -OutputJson $OutJson -OutputCsv $OutCsv

Write-Host "[+] Audit complete. Results: $($results.Count) checks"
Write-Host "    JSON: $OutJson"
Write-Host "    CSV:  $OutCsv"
