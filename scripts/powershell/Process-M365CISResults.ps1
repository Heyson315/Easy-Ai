param(
    [string]$JsonPath,
    [bool]$CompareWithBaseline,
    [string]$BaselineArtifactName
)

# Helper function to set action outputs
function Set-ActionOutput {
    param ([string]$Name, [string]$Value)
    echo "::set-output name=$Name::$Value"
}

# 1. Read and parse the audit JSON
if (-not (Test-Path $JsonPath)) {
    Write-Error "Audit JSON not found at $JsonPath"
    exit 1
}
$auditData = Get-Content $JsonPath | ConvertFrom-Json
$controls = $auditData.Controls

# 2. Calculate Compliance and Basic Stats
$totalControls = $controls.Count
$passed = ($controls | Where-Object { $_.Status -eq 'Pass' }).Count
$failed = ($controls | Where-Object { $_.Status -eq 'Fail' }).Count
$manual = ($controls | Where-Object { $_.Status -eq 'Manual' }).Count
$complianceScore = if ($totalControls -gt 0) { [math]::Round(($passed / $totalControls) * 100, 2) } else { 0 }

Set-ActionOutput -Name "compliance-score" -Value $complianceScore
Set-ActionOutput -Name "controls-passed" -Value $passed
Set-ActionOutput -Name "controls-failed" -Value $failed
Set-ActionOutput -Name "controls-manual" -Value $manual

# 3. Calculate Severity-Weighted Risk Score
$weights = @{ "Critical" = 10; "High" = 7; "Medium" = 4; "Low" = 1 }
$criticalCount = ($controls | Where-Object { $_.Status -eq 'Fail' -and $_.Severity -eq 'Critical' }).Count
$highCount = ($controls | Where-Object { $_.Status -eq 'Fail' -and $_.Severity -eq 'High' }).Count
$mediumCount = ($controls | Where-Object { $_.Status -eq 'Fail' -and $_.Severity -eq 'Medium' }).Count
$lowCount = ($controls | Where-Object { $_.Status -eq 'Fail' -and $_.Severity -eq 'Low' }).Count

$totalRiskPoints = ($criticalCount * $weights.Critical) + ($highCount * $weights.High) + ($mediumCount * $weights.Medium) + ($lowCount * $weights.Low)
$maxRiskPoints = $totalControls * $weights.Critical # Max risk is if all controls were critical and failed
$riskScore = if ($maxRiskPoints -gt 0) { [math]::Round(($totalRiskPoints / $maxRiskPoints) * 100, 2) } else { 0 }

Set-ActionOutput -Name "risk-score" -Value $riskScore
Set-ActionOutput -Name "critical-findings" -Value $criticalCount
Set-ActionOutput -Name "high-findings" -Value $highCount
Set-ActionOutput -Name "medium-findings" -Value $mediumCount
Set-ActionOutput -Name "low-findings" -Value $lowCount

# 4. Generate SARIF Report
$sarifReportPath = "$([System.IO.Path]::GetDirectoryName($JsonPath))/m365-audit.sarif"
$rules = @()
foreach ($control in $controls) {
    $rules += @{
        id               = $control.ControlId
        name             = $control.Title
        shortDescription = @{
            text = $control.Title
        }
        fullDescription  = @{
            text = "CIS Control: $($control.ControlId) - $($control.Title)"
        }
        help             = @{
            text = "Reference: $($control.Reference)"
        }
        properties       = @{
            severity = $control.Severity
        }
    }
}

$results = @()
$failedControls = $controls | Where-Object { $_.Status -eq 'Fail' }
foreach ($failure in $failedControls) {
    $severityLevel = switch ($failure.Severity) {
        "Critical" { "error" }
        "High" { "error" }
        "Medium" { "warning" }
        "Low" { "note" }
        default { "note" }
    }
    $results += @{
        ruleId    = $failure.ControlId
        level     = $severityLevel
        message   = @{
            text = "Control Failed: $($failure.Title). Expected: '$($failure.Expected)', Actual: '$($failure.Actual)'."
        }
        locations = @(
            @{
                physicalLocation = @{
                    artifactLocation = @{
                        uri = "https://portal.azure.com" # Generic location
                    }
                    region           = @{
                        startLine = 1
                    }
                }
            }
        )
    }
}

$sarif = @{
    version = "2.1.0"
    `$schema` = "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json"
    runs = @(
        @{
            tool    = @{
                driver = @{
                    name  = "M365 Security Toolkit"
                    rules = $rules
                }
            }
            results = $results
        }
    )
}

$sarif | ConvertTo-Json -Depth 10 | Out-File -FilePath $sarifReportPath -Encoding utf8
Set-ActionOutput -Name "sarif-report" -Value $sarifReportPath
Set-ActionOutput -Name "security-findings-count" -Value $results.Count

# 5. Compliance Trending
if ($CompareWithBaseline) {
    # Download baseline artifact
    try {
        # This is a placeholder for artifact download logic.
        # In a real GitHub Action, you'd use an action like actions/download-artifact
        Write-Host "Attempting to download baseline artifact: $BaselineArtifactName"
        # $baselineJson = Get-Content "./baseline/$BaselineArtifactName.json" | ConvertFrom-Json
        # For local testing, we'll just create a dummy baseline.
        $baselineJson = $null
    }
    catch {
        $baselineJson = $null
        Write-Host "No baseline artifact found. This run will be saved as the new baseline."
    }

    if ($baselineJson) {
        $baselineControls = $baselineJson.Controls
        $currentControlIds = $controls | Select-Object -ExpandProperty ControlId

        $newFailures = $controls | Where-Object {
            $c = $_
            $c.Status -eq 'Fail' -and (($baselineControls | Where-Object { $_.ControlId -eq $c.ControlId }).Status -ne 'Fail')
        }
        $fixedIssues = $controls | Where-Object {
            $c = $_
            $c.Status -eq 'Pass' -and (($baselineControls | Where-Object { $_.ControlId -eq $c.ControlId }).Status -eq 'Fail')
        }

        $baselinePassed = ($baselineControls | Where-Object { $_.Status -eq 'Pass' }).Count
        $baselineCompliance = if ($baselineControls.Count -gt 0) { ($baselinePassed / $baselineControls.Count) * 100 } else { 0 }
        $trend = $complianceScore - $baselineCompliance
        
        $trendDirection = "stable"
        if ($trend -gt 0.5) { $trendDirection = "improving" }
        if ($trend -lt -0.5) { $trendDirection = "declining" }

        Set-ActionOutput -Name "new-failures" -Value $newFailures.Count
        Set-ActionOutput -Name "fixed-issues" -Value $fixedIssues.Count
        Set-ActionOutput -Name "compliance-trend" -Value ("{0:N2}" -f $trend)
        Set-ActionOutput -Name "trend-direction" -Value $trendDirection
    }
    else {
        # No baseline, set defaults and save current as baseline
        Set-ActionOutput -Name "new-failures" -Value 0
        Set-ActionOutput -Name "fixed-issues" -Value 0
        Set-ActionOutput -Name "compliance-trend" -Value "0.00"
        Set-ActionOutput -Name "trend-direction" -Value "stable"
        
        # This is a placeholder for artifact upload logic
        Write-Host "Saving current results as baseline artifact: $BaselineArtifactName"
        # New-Item -Path "./baseline" -ItemType Directory -Force
        # Get-Content $JsonPath | Out-File -FilePath "./baseline/$BaselineArtifactName.json"
    }
}

Write-Host "Processing complete."
