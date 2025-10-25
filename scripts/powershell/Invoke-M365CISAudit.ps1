param(
  [string]$OutJson = "output/reports/security/m365_cis_audit.json",
  [string]$OutCsv  = "output/reports/security/m365_cis_audit.csv",
  [switch]$SkipExchange,
  [switch]$SkipGraph,
  [switch]$Timestamped
)

# If -Timestamped, append timestamp to output filenames
if ($Timestamped) {
    $ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
    $OutJson = $OutJson -replace '\.json$', "_$ts.json"
    $OutCsv  = $OutCsv -replace '\.csv$', "_$ts.csv"
}

# Import module
Import-Module -Force "$PSScriptRoot/modules/M365CIS.psm1"

Write-Host "[+] Connecting to Microsoft 365 services..."
Connect-M365CIS -SkipExchange:$SkipExchange -SkipGraph:$SkipGraph

Write-Host "[+] Running CIS Level 1 audit checks..."
$results = Invoke-M365CISAudit -OutputJson $OutJson -OutputCsv $OutCsv

Write-Host "[+] Audit complete. Results: $($results.Count) checks"
Write-Host "    JSON: $OutJson"
Write-Host "    CSV:  $OutCsv"
