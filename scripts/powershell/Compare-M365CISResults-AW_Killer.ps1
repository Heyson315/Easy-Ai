<#
.SYNOPSIS
    Compare two M365 CIS audit results to show before/after differences

.DESCRIPTION
    Accepts two audit JSON files (before/after remediation) and generates a comparison showing:
    - Status changes (Fail → Pass, Pass → Fail)
    - New controls added/removed
    - Severity-based priority sorting
    - Statistics summary (total Pass/Fail counts, improvement percentage)

.PARAMETER BeforeFile
    Path to the "before" audit JSON file

.PARAMETER AfterFile
    Path to the "after" audit JSON file

.PARAMETER OutputCsv
    Optional path to export comparison results as CSV

.PARAMETER OutputHtml
    Optional path to export comparison results as HTML report

.EXAMPLE
    .\Compare-M365CISResults.ps1 -BeforeFile "before.json" -AfterFile "after.json"

.EXAMPLE
    .\Compare-M365CISResults.ps1 -BeforeFile "before.json" -AfterFile "after.json" -OutputCsv "comparison.csv" -OutputHtml "comparison.html"

.NOTES
    Requires PowerShell 5.1 or later
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({Test-Path $_})]
    [string]$BeforeFile,

    [Parameter(Mandatory=$true)]
    [ValidateScript({Test-Path $_})]
    [string]$AfterFile,

    [string]$OutputCsv,

    [string]$OutputHtml
)

function Write-ColorOutput {
    [CmdletBinding()]
    param(
        [string]$Message,
        [ConsoleColor]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

# Load audit results
Write-ColorOutput "`n[+] Loading audit results..." "Cyan"
try {
    $beforeResults = Get-Content -Path $BeforeFile -Raw | ConvertFrom-Json
    $afterResults = Get-Content -Path $AfterFile -Raw | ConvertFrom-Json
    Write-ColorOutput "    Before: $BeforeFile ($($beforeResults.Count) controls)" "Gray"
    Write-ColorOutput "    After:  $AfterFile ($($afterResults.Count) controls)" "Gray"
} catch {
    Write-ColorOutput "ERROR: Failed to load audit files: $($_.Exception.Message)" "Red"
    exit 1
}

# Create lookup dictionaries
$beforeLookup = @{}
foreach ($control in $beforeResults) {
    $beforeLookup[$control.ControlId] = $control
}

$afterLookup = @{}
foreach ($control in $afterResults) {
    $afterLookup[$control.ControlId] = $control
}

# Get all control IDs
$allControlIds = ($beforeLookup.Keys + $afterLookup.Keys) | Select-Object -Unique | Sort-Object

# Build comparison results
$comparisons = @()
foreach ($controlId in $allControlIds) {
    $before = $beforeLookup[$controlId]
    $after = $afterLookup[$controlId]

    $statusChange = "N/A"
    $changeType = "No Change"

    if (-not $before -and $after) {
        $statusChange = "New → $($after.Status)"
        $changeType = "Added"
    } elseif ($before -and -not $after) {
        $statusChange = "$($before.Status) → Removed"
        $changeType = "Removed"
    } elseif ($before.Status -ne $after.Status) {
        $statusChange = "$($before.Status) → $($after.Status)"
        if ($before.Status -eq 'Fail' -and $after.Status -eq 'Pass') {
            $changeType = "Improved"
        } elseif ($before.Status -eq 'Pass' -and $after.Status -eq 'Fail') {
            $changeType = "Degraded"
        } else {
            $changeType = "Changed"
        }
    }

    $comparison = [PSCustomObject]@{
        ControlId = $controlId
        Title = if ($after) { $after.Title } elseif ($before) { $before.Title } else { "Unknown" }
        Severity = if ($after) { $after.Severity } elseif ($before) { $before.Severity } else { "Unknown" }
        BeforeStatus = if ($before) { $before.Status } else { "N/A" }
        AfterStatus = if ($after) { $after.Status } else { "N/A" }
        StatusChange = $statusChange
        ChangeType = $changeType
        BeforeActual = if ($before) { $before.Actual } else { "N/A" }
        AfterActual = if ($after) { $after.Actual } else { "N/A" }
    }

    $comparisons += $comparison
}

# Sort by severity (High → Medium → Low) then by change type
$severityOrder = @{
    'High' = 1
    'Medium' = 2
    'Low' = 3
    'Unknown' = 4
}

$changeTypeOrder = @{
    'Degraded' = 1
    'Improved' = 2
    'Added' = 3
    'Removed' = 4
    'Changed' = 5
    'No Change' = 6
}

$comparisons = $comparisons | Sort-Object {$severityOrder[$_.Severity]}, {$changeTypeOrder[$_.ChangeType]}

# Calculate statistics
$beforeStats = @{
    Pass = ($beforeResults | Where-Object {$_.Status -eq 'Pass'}).Count
    Fail = ($beforeResults | Where-Object {$_.Status -eq 'Fail'}).Count
    Manual = ($beforeResults | Where-Object {$_.Status -eq 'Manual'}).Count
    Error = ($beforeResults | Where-Object {$_.Status -eq 'Error'}).Count
}

$afterStats = @{
    Pass = ($afterResults | Where-Object {$_.Status -eq 'Pass'}).Count
    Fail = ($afterResults | Where-Object {$_.Status -eq 'Fail'}).Count
    Manual = ($afterResults | Where-Object {$_.Status -eq 'Manual'}).Count
    Error = ($afterResults | Where-Object {$_.Status -eq 'Error'}).Count
}

$beforeTotal = $beforeStats.Pass + $beforeStats.Fail + $beforeStats.Manual + $beforeStats.Error
$afterTotal = $afterStats.Pass + $afterStats.Fail + $afterStats.Manual + $afterStats.Error

$beforePassRate = if ($beforeTotal -gt 0) { [math]::Round(($beforeStats.Pass / $beforeTotal) * 100, 2) } else { 0 }
$afterPassRate = if ($afterTotal -gt 0) { [math]::Round(($afterStats.Pass / $afterTotal) * 100, 2) } else { 0 }
$improvement = $afterPassRate - $beforePassRate

# Display summary
Write-ColorOutput "`n============================================" "Cyan"
Write-ColorOutput "    M365 CIS AUDIT COMPARISON SUMMARY" "Cyan"
Write-ColorOutput "============================================" "Cyan"

Write-ColorOutput "`nBEFORE (from $($BeforeFile | Split-Path -Leaf)):" "Yellow"
Write-ColorOutput "  Pass:   $($beforeStats.Pass)" "Green"
Write-ColorOutput "  Fail:   $($beforeStats.Fail)" "Red"
Write-ColorOutput "  Manual: $($beforeStats.Manual)" "Gray"
Write-ColorOutput "  Error:  $($beforeStats.Error)" "Magenta"
Write-ColorOutput "  Pass Rate: $beforePassRate%" "Yellow"

Write-ColorOutput "`nAFTER (from $($AfterFile | Split-Path -Leaf)):" "Yellow"
Write-ColorOutput "  Pass:   $($afterStats.Pass)" "Green"
Write-ColorOutput "  Fail:   $($afterStats.Fail)" "Red"
Write-ColorOutput "  Manual: $($afterStats.Manual)" "Gray"
Write-ColorOutput "  Error:  $($afterStats.Error)" "Magenta"
Write-ColorOutput "  Pass Rate: $afterPassRate%" "Yellow"

Write-ColorOutput "`nCHANGE SUMMARY:" "Cyan"
Write-ColorOutput "  Improvement: $(if ($improvement -gt 0) {"+$improvement%"} else {"$improvement%"})" $(if ($improvement -gt 0) {"Green"} elseif ($improvement -lt 0) {"Red"} else {"Gray"})
Write-ColorOutput "  Improved:  $(($comparisons | Where-Object {$_.ChangeType -eq 'Improved'}).Count)" "Green"
Write-ColorOutput "  Degraded:  $(($comparisons | Where-Object {$_.ChangeType -eq 'Degraded'}).Count)" "Red"
Write-ColorOutput "  Added:     $(($comparisons | Where-Object {$_.ChangeType -eq 'Added'}).Count)" "Cyan"
Write-ColorOutput "  Removed:   $(($comparisons | Where-Object {$_.ChangeType -eq 'Removed'}).Count)" "Yellow"
Write-ColorOutput "  Changed:   $(($comparisons | Where-Object {$_.ChangeType -eq 'Changed'}).Count)" "Gray"
Write-ColorOutput "  No Change: $(($comparisons | Where-Object {$_.ChangeType -eq 'No Change'}).Count)" "DarkGray"

Write-ColorOutput "`n============================================" "Cyan"

# Display detailed changes
Write-ColorOutput "`n[+] Detailed Changes:" "Cyan"
$importantChanges = $comparisons | Where-Object {$_.ChangeType -ne 'No Change'}
if ($importantChanges.Count -gt 0) {
    $importantChanges | Format-Table ControlId, Title, Severity, StatusChange, ChangeType -AutoSize
} else {
    Write-ColorOutput "  No status changes detected." "Gray"
}

# Export to CSV if requested
if ($OutputCsv) {
    try {
        $comparisons | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8
        Write-ColorOutput "`n[+] Comparison exported to CSV: $OutputCsv" "Green"
    } catch {
        Write-ColorOutput "ERROR: Failed to export CSV: $($_.Exception.Message)" "Red"
    }
}

# Export to HTML if requested
if ($OutputHtml) {
    try {
        $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>M365 CIS Audit Comparison</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }
        h1 { color: #0078d4; }
        h2 { color: #323130; margin-top: 30px; }
        .summary { background-color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
        .stat-card { background-color: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { margin-top: 0; color: #605e5c; font-size: 14px; }
        .stat-value { font-size: 32px; font-weight: bold; }
        .pass { color: #107c10; }
        .fail { color: #d13438; }
        .manual { color: #797775; }
        .improved { color: #107c10; }
        .degraded { color: #d13438; }
        table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th { background-color: #0078d4; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #edebe9; }
        tr:hover { background-color: #f3f2f1; }
        .severity-high { color: #d13438; font-weight: bold; }
        .severity-medium { color: #f7630c; }
        .severity-low { color: #797775; }
        .change-improved { background-color: #dff6dd; }
        .change-degraded { background-color: #fde7e9; }
        .change-added { background-color: #deecf9; }
    </style>
</head>
<body>
    <h1>M365 CIS Audit Comparison Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Before File:</strong> $(Split-Path -Leaf $BeforeFile)</p>
        <p><strong>After File:</strong> $(Split-Path -Leaf $AfterFile)</p>
        <p><strong>Comparison Date:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <h3>BEFORE Status</h3>
            <div class="stat-value pass">$($beforeStats.Pass) Pass</div>
            <div class="stat-value fail">$($beforeStats.Fail) Fail</div>
            <div class="stat-value manual">$($beforeStats.Manual) Manual</div>
            <p><strong>Pass Rate:</strong> $beforePassRate%</p>
        </div>
        <div class="stat-card">
            <h3>AFTER Status</h3>
            <div class="stat-value pass">$($afterStats.Pass) Pass</div>
            <div class="stat-value fail">$($afterStats.Fail) Fail</div>
            <div class="stat-value manual">$($afterStats.Manual) Manual</div>
            <p><strong>Pass Rate:</strong> $afterPassRate%</p>
        </div>
    </div>

    <div class="stat-card">
        <h3>Change Summary</h3>
        <p><strong>Improvement:</strong> <span class="$(if ($improvement -gt 0) {'improved'} else {'degraded'})">$(if ($improvement -gt 0) {"+$improvement%"} else {"$improvement%"})</span></p>
        <p><strong>Improved:</strong> <span class="improved">$(($comparisons | Where-Object {$_.ChangeType -eq 'Improved'}).Count)</span> |
           <strong>Degraded:</strong> <span class="degraded">$(($comparisons | Where-Object {$_.ChangeType -eq 'Degraded'}).Count)</span> |
           <strong>Added:</strong> $(($comparisons | Where-Object {$_.ChangeType -eq 'Added'}).Count) |
           <strong>Removed:</strong> $(($comparisons | Where-Object {$_.ChangeType -eq 'Removed'}).Count)</p>
    </div>

    <h2>Detailed Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Control ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status Change</th>
                <th>Change Type</th>
            </tr>
        </thead>
        <tbody>
"@

        foreach ($comp in $comparisons) {
            $severityClass = "severity-$($comp.Severity.ToLower())"
            $changeClass = "change-$($comp.ChangeType.ToLower())"
            $htmlContent += @"
            <tr class="$changeClass">
                <td>$($comp.ControlId)</td>
                <td>$($comp.Title)</td>
                <td class="$severityClass">$($comp.Severity)</td>
                <td>$($comp.StatusChange)</td>
                <td>$($comp.ChangeType)</td>
            </tr>
"@
        }

        $htmlContent += @"
        </tbody>
    </table>
</body>
</html>
"@

        $htmlContent | Out-File -FilePath $OutputHtml -Encoding UTF8
        Write-ColorOutput "[+] Comparison exported to HTML: $OutputHtml" "Green"
    } catch {
        Write-ColorOutput "ERROR: Failed to export HTML: $($_.Exception.Message)" "Red"
    }
}

Write-ColorOutput "`n[+] Comparison complete!`n" "Green"
