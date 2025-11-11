<#
.SYNOPSIS
    Audit Copilot for Microsoft 365 security and usage configuration

.DESCRIPTION
    Comprehensive audit for Copilot for Microsoft 365 deployment:
    - License assignments and usage
    - Data protection policies (DLP, sensitivity labels)
    - Information barriers configuration
    - Copilot-specific security settings
    - Audit log retention for Copilot activities

.PARAMETER OutputPath
    Path to save audit results (default: output/reports/copilot/)

.EXAMPLE
    .\Audit-CopilotSecurity.ps1
    
.EXAMPLE
    .\Audit-CopilotSecurity.ps1 -OutputPath "C:\CopilotAudits\"

.NOTES
    Requires: Microsoft.Graph, ExchangeOnlineManagement modules
    Permissions: Global Reader, Compliance Admin
#>

[CmdletBinding()]
param(
    [string]$OutputPath = "output\reports\copilot\"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = Join-Path $OutputPath "copilot_security_audit_$timestamp.json"

# Ensure output directory exists
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

$results = @{
    Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    TenantInfo = @{}
    Licenses = @{}
    DataProtection = @{}
    InformationBarriers = @{}
    AuditSettings = @{}
    Recommendations = @()
}

Write-Host "[+] Starting Copilot for M365 Security Audit..." -ForegroundColor Cyan

# Connect to services
try {
    Write-Host "[*] Connecting to Microsoft Graph..." -ForegroundColor Yellow
    Connect-MgGraph -Scopes "User.Read.All","Directory.Read.All","Organization.Read.All" -NoWelcome -ErrorAction Stop
    $results.TenantInfo.GraphConnected = $true
} catch {
    Write-Host "[!] Failed to connect to Microsoft Graph: $($_.Exception.Message)" -ForegroundColor Red
    $results.TenantInfo.GraphConnected = $false
}

try {
    Write-Host "[*] Connecting to Exchange Online..." -ForegroundColor Yellow
    Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop
    $results.TenantInfo.ExchangeConnected = $true
} catch {
    Write-Host "[!] Failed to connect to Exchange Online: $($_.Exception.Message)" -ForegroundColor Red
    $results.TenantInfo.ExchangeConnected = $false
}

# 1. Check Copilot Licenses
Write-Host "`n[+] Checking Copilot License Assignments..." -ForegroundColor Cyan
try {
    $copilotSkus = Get-MgSubscribedSku | Where-Object {
        $_.SkuPartNumber -like "*COPILOT*" -or 
        $_.SkuPartNumber -like "*M365_COPILOT*" -or
        $_.ServicePlans.ServicePlanName -like "*COPILOT*"
    }
    
    $results.Licenses.TotalCopilotSkus = $copilotSkus.Count
    $results.Licenses.Details = @()
    
    foreach ($sku in $copilotSkus) {
        $skuInfo = @{
            SkuPartNumber = $sku.SkuPartNumber
            SkuId = $sku.SkuId
            ConsumedUnits = $sku.ConsumedUnits
            PrepaidUnits = $sku.PrepaidUnits.Enabled
            AvailableUnits = $sku.PrepaidUnits.Enabled - $sku.ConsumedUnits
        }
        $results.Licenses.Details += $skuInfo
        
        Write-Host "  [✓] Found: $($sku.SkuPartNumber)" -ForegroundColor Green
        Write-Host "      Assigned: $($sku.ConsumedUnits) / $($sku.PrepaidUnits.Enabled)" -ForegroundColor Gray
    }
    
    # Get users with Copilot licenses
    $copilotUsers = Get-MgUser -All -Property DisplayName,UserPrincipalName,AssignedLicenses | 
        Where-Object { 
            $_.AssignedLicenses.SkuId -in $copilotSkus.SkuId 
        }
    
    $results.Licenses.AssignedUsers = $copilotUsers.Count
    $results.Licenses.UserList = $copilotUsers | Select-Object DisplayName, UserPrincipalName
    
    Write-Host "  [✓] Copilot assigned to $($copilotUsers.Count) users" -ForegroundColor Green
    
} catch {
    Write-Host "  [!] License check failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.Licenses.Error = $_.Exception.Message
}

# 2. Check DLP Policies for Copilot
Write-Host "`n[+] Checking DLP Policies for Copilot Protection..." -ForegroundColor Cyan
try {
    $dlpPolicies = Get-DlpCompliancePolicy
    $copilotDlpPolicies = $dlpPolicies | Where-Object { 
        $_.Name -like "*Copilot*" -or 
        $_.Name -like "*AI*" -or
        $_.Comment -like "*Copilot*"
    }
    
    $results.DataProtection.DLPPolicies = @{
        Total = $dlpPolicies.Count
        CopilotSpecific = $copilotDlpPolicies.Count
        Details = $copilotDlpPolicies | Select-Object Name, Mode, Enabled
    }
    
    Write-Host "  [✓] Total DLP policies: $($dlpPolicies.Count)" -ForegroundColor Green
    Write-Host "  [✓] Copilot/AI-specific DLP: $($copilotDlpPolicies.Count)" -ForegroundColor Green
    
    if ($copilotDlpPolicies.Count -eq 0) {
        $results.Recommendations += @{
            Priority = "HIGH"
            Category = "Data Protection"
            Finding = "No Copilot-specific DLP policies found"
            Recommendation = "Create DLP policy to protect sensitive data (SSN, EIN, client financials) from Copilot interactions"
            Impact = "Client data could be exposed through Copilot responses"
        }
    }
    
} catch {
    Write-Host "  [!] DLP check failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.DataProtection.DLPError = $_.Exception.Message
}

# 3. Check Sensitivity Labels
Write-Host "`n[+] Checking Sensitivity Labels Configuration..." -ForegroundColor Cyan
try {
    $labels = Get-Label
    $labelPolicies = Get-LabelPolicy
    
    $results.DataProtection.SensitivityLabels = @{
        TotalLabels = $labels.Count
        PublishedPolicies = $labelPolicies.Count
        MandatoryLabelingEnabled = ($labelPolicies | Where-Object { $_.Settings -like "*Mandatory*" }).Count
    }
    
    Write-Host "  [✓] Sensitivity labels: $($labels.Count)" -ForegroundColor Green
    Write-Host "  [✓] Published policies: $($labelPolicies.Count)" -ForegroundColor Green
    
    # Check if labels support Copilot blocking
    $copilotAwareLabels = $labels | Where-Object { 
        $_.Settings -like "*copilot*" -or 
        $_.AdvancedSettings.Keys -like "*copilot*"
    }
    
    if ($copilotAwareLabels.Count -eq 0) {
        $results.Recommendations += @{
            Priority = "MEDIUM"
            Category = "Data Protection"
            Finding = "Sensitivity labels not configured for Copilot awareness"
            Recommendation = "Update labels with Copilot-specific settings (e.g., block Copilot access to highly confidential files)"
            Impact = "Copilot may access files that should be restricted"
        }
    }
    
} catch {
    Write-Host "  [!] Sensitivity label check failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.DataProtection.LabelsError = $_.Exception.Message
}

# 4. Check Information Barriers
Write-Host "`n[+] Checking Information Barriers Configuration..." -ForegroundColor Cyan
try {
    $orgConfig = Get-OrganizationConfig
    $ibEnabled = $orgConfig.InformationBarriersManagementEnabled
    
    $results.InformationBarriers.Enabled = $ibEnabled
    
    if ($ibEnabled) {
        $ibPolicies = Get-InformationBarrierPolicy
        $results.InformationBarriers.Policies = $ibPolicies.Count
        Write-Host "  [✓] Information Barriers: ENABLED" -ForegroundColor Green
        Write-Host "  [✓] Active policies: $($ibPolicies.Count)" -ForegroundColor Green
    } else {
        Write-Host "  [!] Information Barriers: DISABLED" -ForegroundColor Red
        $results.Recommendations += @{
            Priority = "CRITICAL"
            Category = "Data Segregation"
            Finding = "Information Barriers not enabled"
            Recommendation = "Enable Information Barriers to prevent Copilot from mixing data across client segments"
            Impact = "High risk of client data cross-contamination in Copilot responses"
        }
    }
    
} catch {
    Write-Host "  [!] Information Barriers check failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.InformationBarriers.Error = $_.Exception.Message
}

# 5. Check Audit Log Configuration
Write-Host "`n[+] Checking Audit Log Configuration for Copilot..." -ForegroundColor Cyan
try {
    $auditConfig = Get-AdminAuditLogConfig
    $retentionPolicies = Get-UnifiedAuditLogRetentionPolicy
    
    $results.AuditSettings.AuditEnabled = -not $orgConfig.AuditDisabled
    $results.AuditSettings.UnifiedAuditLogEnabled = $auditConfig.UnifiedAuditLogIngestionEnabled
    $results.AuditSettings.RetentionPolicies = $retentionPolicies.Count
    
    # Check for Copilot-specific retention
    $copilotRetention = $retentionPolicies | Where-Object { 
        $_.Name -like "*Copilot*" -or 
        $_.RecordTypes -contains "MicrosoftCopilot"
    }
    
    Write-Host "  [✓] Audit enabled: $($results.AuditSettings.AuditEnabled)" -ForegroundColor Green
    Write-Host "  [✓] Retention policies: $($retentionPolicies.Count)" -ForegroundColor Green
    
    if ($copilotRetention.Count -eq 0) {
        $results.Recommendations += @{
            Priority = "MEDIUM"
            Category = "Auditing"
            Finding = "No Copilot-specific audit retention policy"
            Recommendation = "Ensure your 3-year audit retention policy covers Copilot activities (CopilotInteraction events)"
            Impact = "May not have audit trail for Copilot usage in case of investigations"
        }
    }
    
} catch {
    Write-Host "  [!] Audit config check failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.AuditSettings.Error = $_.Exception.Message
}

# 6. Check Copilot-Specific Settings
Write-Host "`n[+] Checking Copilot-Specific Organization Settings..." -ForegroundColor Cyan
try {
    # Check if Copilot is enabled/disabled at org level
    $copilotSettings = @{
        ConnectorsEnabled = $orgConfig.ConnectorsEnabled
        WebPushNotificationsDisabled = $orgConfig.WebPushNotificationsDisabled
        OutlookTextPredictionDisabled = $orgConfig.OutlookTextPredictionDisabled
    }
    
    $results.DataProtection.CopilotOrgSettings = $copilotSettings
    
    Write-Host "  [✓] Connectors (required for Copilot): $($copilotSettings.ConnectorsEnabled)" -ForegroundColor Green
    
} catch {
    Write-Host "  [!] Copilot settings check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Generate Recommendations Summary
Write-Host "`n[+] Generating Recommendations..." -ForegroundColor Cyan
$criticalCount = ($results.Recommendations | Where-Object { $_.Priority -eq "CRITICAL" }).Count
$highCount = ($results.Recommendations | Where-Object { $_.Priority -eq "HIGH" }).Count
$mediumCount = ($results.Recommendations | Where-Object { $_.Priority -eq "MEDIUM" }).Count

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "    COPILOT SECURITY AUDIT SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Licenses Assigned:      $($results.Licenses.AssignedUsers)" -ForegroundColor White
Write-Host "DLP Policies (AI):      $($results.DataProtection.DLPPolicies.CopilotSpecific)" -ForegroundColor White
Write-Host "Information Barriers:   $(if ($results.InformationBarriers.Enabled) { 'ENABLED' } else { 'DISABLED' })" -ForegroundColor $(if ($results.InformationBarriers.Enabled) { 'Green' } else { 'Red' })
Write-Host "Audit Retention:        $($results.AuditSettings.RetentionPolicies) policies" -ForegroundColor White
Write-Host "`nRecommendations:" -ForegroundColor Yellow
Write-Host "  CRITICAL:             $criticalCount" -ForegroundColor Red
Write-Host "  HIGH:                 $highCount" -ForegroundColor Yellow
Write-Host "  MEDIUM:               $mediumCount" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan

# Display detailed recommendations
if ($results.Recommendations.Count -gt 0) {
    Write-Host "`n[!] Action Items:" -ForegroundColor Yellow
    foreach ($rec in $results.Recommendations | Sort-Object @{Expression={
        switch ($_.Priority) {
            "CRITICAL" { 1 }
            "HIGH" { 2 }
            "MEDIUM" { 3 }
            default { 4 }
        }
    }}) {
        Write-Host "`n[$($rec.Priority)] $($rec.Category)" -ForegroundColor $(
            switch ($rec.Priority) {
                "CRITICAL" { "Red" }
                "HIGH" { "Yellow" }
                "MEDIUM" { "Gray" }
                default { "White" }
            }
        )
        Write-Host "  Finding: $($rec.Finding)" -ForegroundColor Gray
        Write-Host "  Action:  $($rec.Recommendation)" -ForegroundColor White
    }
}

# Save results
Write-Host "`n[+] Saving audit results to: $reportFile" -ForegroundColor Cyan
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "[✓] Audit complete!" -ForegroundColor Green

# Generate CSV summary for easy review
$csvFile = $reportFile -replace ".json$", ".csv"
if ($results.Recommendations.Count -gt 0) {
    $results.Recommendations | Select-Object Priority, Category, Finding, Recommendation, Impact | 
        Export-Csv -Path $csvFile -NoTypeInformation
    Write-Host "[✓] Recommendations exported to: $csvFile" -ForegroundColor Green
}

Write-Host "`n[+] Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review recommendations in: $reportFile" -ForegroundColor White
Write-Host "  2. Address CRITICAL and HIGH priority items first" -ForegroundColor White
Write-Host "  3. Re-run audit after implementing changes" -ForegroundColor White
Write-Host "  4. Schedule monthly audits for ongoing monitoring" -ForegroundColor White
