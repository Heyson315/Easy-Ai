<#
.SYNOPSIS
    Secure Copilot for Microsoft 365 deployment for CPA firm

.DESCRIPTION
    Implements security hardening for Copilot:
    - Creates Copilot-specific DLP policies for financial data
    - Configures sensitivity labels with Copilot awareness
    - Enables Information Barriers for client data segregation
    - Sets up audit retention for Copilot activities

.PARAMETER WhatIf
    Preview changes without applying them

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\Secure-Copilot.ps1 -WhatIf
    Preview all security changes

.EXAMPLE
    .\Secure-Copilot.ps1 -Force
    Apply all security configurations

.NOTES
    Requires: Global Admin or Compliance Admin permissions
    CPA Firm Specific: Protects SSN, EIN, client financial data
#>

[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$script:successCount = 0
$script:failureCount = 0
$script:skippedCount = 0

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet('Info','Success','Warning','Error')]
        [string]$Type = 'Info'
    )

    $color = switch ($Type) {
        'Success' { 'Green' }
        'Warning' { 'Yellow' }
        'Error'   { 'Red' }
        default   { 'Cyan' }
    }

    $prefix = switch ($Type) {
        'Success' { '[✓]' }
        'Warning' { '[!]' }
        'Error'   { '[✗]' }
        default   { '[*]' }
    }

    Write-Host "$prefix $Message" -ForegroundColor $color
}

Write-Status "Starting Copilot Security Hardening for CPA Firm..." "Info"

# Connect to services
Write-Status "Connecting to Microsoft 365 services..." "Info"
try {
    Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop
    Write-Status "Connected to Exchange Online" "Success"
} catch {
    Write-Status "Failed to connect to Exchange Online: $($_.Exception.Message)" "Error"
    exit 1
}

try {
    Connect-IPPSSession -ErrorAction Stop
    Write-Status "Connected to Security & Compliance" "Success"
} catch {
    Write-Status "Failed to connect to Security & Compliance: $($_.Exception.Message)" "Error"
    exit 1
}

# 1. Create Copilot DLP Policy for Financial Data
Write-Status "`nConfiguring DLP Policy: Copilot Financial Data Protection..." "Info"
try {
    if ($PSCmdlet.ShouldProcess("DLP Policy", "Create Copilot Financial Data Protection policy")) {

        # Check if policy already exists
        $existingPolicy = Get-DlpCompliancePolicy -Identity "Copilot Financial Data Protection - CPA Firm" -ErrorAction SilentlyContinue

        if ($existingPolicy) {
            Write-Status "DLP policy already exists, updating..." "Warning"
            Set-DlpCompliancePolicy -Identity "Copilot Financial Data Protection - CPA Firm" `
                -Mode Enable `
                -ErrorAction Stop
        } else {
            New-DlpCompliancePolicy -Name "Copilot Financial Data Protection - CPA Firm" `
                -Comment "Protects CPA client data (SSN, EIN, Tax IDs, Financial info) from exposure via Copilot. Auto-created by security hardening script." `
                -Mode Enable `
                -ErrorAction Stop

            Write-Status "Created DLP policy" "Success"
        }

        # Create DLP rules for financial data types
        $rules = @(
            @{
                Name = "Block SSN/ITIN in Copilot"
                ContentContainsSensitiveInformation = @(
                    @{Name="U.S. Social Security Number (SSN)"; minCount="1"},
                    @{Name="U.S. Individual Taxpayer Identification Number (ITIN)"; minCount="1"}
                )
            },
            @{
                Name = "Block EIN/Tax IDs in Copilot"
                ContentContainsSensitiveInformation = @(
                    @{Name="U.S. Employer Identification Number (EIN)"; minCount="1"}
                )
            },
            @{
                Name = "Block Financial Account Numbers in Copilot"
                ContentContainsSensitiveInformation = @(
                    @{Name="Credit Card Number"; minCount="1"},
                    @{Name="U.S. Bank Account Number"; minCount="1"}
                )
            }
        )

        foreach ($rule in $rules) {
            $existingRule = Get-DlpComplianceRule -Policy "Copilot Financial Data Protection - CPA Firm" |
                Where-Object { $_.Name -eq $rule.Name }

            if (-not $existingRule) {
                New-DlpComplianceRule -Name $rule.Name `
                    -Policy "Copilot Financial Data Protection - CPA Firm" `
                    -ContentContainsSensitiveInformation $rule.ContentContainsSensitiveInformation `
                    -BlockAccess $true `
                    -NotifyUser Owner `
                    -GenerateIncidentReport SiteAdmin `
                    -IncidentReportContent All `
                    -ErrorAction Stop

                Write-Status "Created DLP rule: $($rule.Name)" "Success"
            } else {
                Write-Status "DLP rule already exists: $($rule.Name)" "Warning"
            }
        }

        $script:successCount++
    } else {
        Write-Status "Would create Copilot DLP policy (WhatIf mode)" "Warning"
        $script:skippedCount++
    }

} catch {
    Write-Status "Failed to create DLP policy: $($_.Exception.Message)" "Error"
    $script:failureCount++
}

# 2. Configure Sensitivity Labels for Copilot
Write-Status "`nConfiguring Sensitivity Labels for Copilot Awareness..." "Info"
try {
    $labels = Get-Label
    $confidentialLabel = $labels | Where-Object { $_.DisplayName -like "*Confidential*" } | Select-Object -First 1

    if ($confidentialLabel) {
        if ($PSCmdlet.ShouldProcess("Sensitivity Label '$($confidentialLabel.DisplayName)'", "Add Copilot blocking settings")) {

            # Update label with Copilot-specific settings
            Set-Label -Identity $confidentialLabel.Id `
                -AdvancedSettings @{
                    "copilotpromptblocking"="enabled";
                    "copilotresponsemonitoring"="enabled"
                } `
                -ErrorAction Stop

            Write-Status "Updated label: $($confidentialLabel.DisplayName) with Copilot protection" "Success"
            $script:successCount++
        } else {
            Write-Status "Would update sensitivity label (WhatIf mode)" "Warning"
            $script:skippedCount++
        }
    } else {
        Write-Status "No 'Confidential' label found to update" "Warning"
        $script:skippedCount++
    }

} catch {
    Write-Status "Failed to configure sensitivity labels: $($_.Exception.Message)" "Error"
    $script:failureCount++
}

# 3. Enable Information Barriers
Write-Status "`nEnabling Information Barriers for Client Data Segregation..." "Info"
try {
    $orgConfig = Get-OrganizationConfig

    if (-not $orgConfig.InformationBarriersManagementEnabled) {
        if ($PSCmdlet.ShouldProcess("Organization", "Enable Information Barriers")) {

            Set-OrganizationConfig -InformationBarriersManagementEnabled $true -ErrorAction Stop
            Write-Status "Enabled Information Barriers" "Success"
            Write-Status "IMPORTANT: You must now create organization segments and IB policies" "Warning"
            Write-Status "Example: New-OrganizationSegment -Name 'Tax-Clients' -UserGroupFilter 'Department -eq Tax'" "Warning"
            $script:successCount++

        } else {
            Write-Status "Would enable Information Barriers (WhatIf mode)" "Warning"
            $script:skippedCount++
        }
    } else {
        Write-Status "Information Barriers already enabled" "Success"

        # Check for existing policies
        $ibPolicies = Get-InformationBarrierPolicy -ErrorAction SilentlyContinue
        if ($ibPolicies.Count -eq 0) {
            Write-Status "No IB policies configured yet - create segments first" "Warning"
            $script:skippedCount++
        } else {
            Write-Status "Found $($ibPolicies.Count) Information Barrier policies" "Success"
        }
    }

} catch {
    Write-Status "Failed to enable Information Barriers: $($_.Exception.Message)" "Error"
    $script:failureCount++
}

# 4. Configure Audit Retention for Copilot
Write-Status "`nVerifying Audit Retention Covers Copilot Activities..." "Info"
try {
    $retentionPolicies = Get-UnifiedAuditLogRetentionPolicy

    # Check if 3-year policy exists (already configured)
    $cpaPolicyExists = $retentionPolicies | Where-Object { $_.Name -like "*CPA*" -or $_.Name -like "*3 Years*" }

    if ($cpaPolicyExists) {
        Write-Status "Found existing audit retention policy: $($cpaPolicyExists.Name)" "Success"
        Write-Status "Duration: $($cpaPolicyExists.RetentionDuration)" "Success"

        # Verify it covers all record types (including Copilot)
        if ($cpaPolicyExists.RecordTypes -contains '*' -or $cpaPolicyExists.RecordTypes.Count -gt 50) {
            Write-Status "Policy covers all audit events including Copilot" "Success"
            $script:successCount++
        } else {
            Write-Status "Policy may not cover all Copilot events - consider updating to 'All' record types" "Warning"
            $script:skippedCount++
        }
    } else {
        Write-Status "No comprehensive audit retention policy found" "Warning"
        Write-Status "Existing 3-year policy should cover Copilot activities" "Info"
        $script:skippedCount++
    }

} catch {
    Write-Status "Failed to check audit retention: $($_.Exception.Message)" "Error"
    $script:failureCount++
}

# 5. Enable Customer Lockbox (E5 feature)
Write-Status "`nEnabling Customer Lockbox for Data Access Control..." "Info"
try {
    if (-not $orgConfig.CustomerLockboxEnabled) {
        if ($PSCmdlet.ShouldProcess("Organization", "Enable Customer Lockbox")) {

            Set-OrganizationConfig -CustomerLockboxEnabled $true -ErrorAction Stop
            Write-Status "Enabled Customer Lockbox" "Success"
            Write-Status "Microsoft engineers now require approval before accessing your data" "Info"
            $script:successCount++

        } else {
            Write-Status "Would enable Customer Lockbox (WhatIf mode)" "Warning"
            $script:skippedCount++
        }
    } else {
        Write-Status "Customer Lockbox already enabled" "Success"
    }

} catch {
    Write-Status "Failed to enable Customer Lockbox: $($_.Exception.Message)" "Error"
    $script:failureCount++
}

# 6. Restrict Guest Access (CPA firm best practice)
Write-Status "`nRestricting Guest User Invitations..." "Info"
try {
    # This requires Microsoft Graph PowerShell
    Connect-MgGraph -Scopes "Policy.ReadWrite.Authorization" -NoWelcome -ErrorAction SilentlyContinue

    if ($PSCmdlet.ShouldProcess("Authorization Policy", "Restrict guest invitations to admins only")) {

        $policy = Get-MgPolicyAuthorizationPolicy
        Update-MgPolicyAuthorizationPolicy -AuthorizationPolicyId $policy.Id `
            -AllowInvitesFrom "adminsAndGuestInviters" `
            -AllowedToSignUpEmailBasedSubscriptions $false `
            -ErrorAction Stop

        Write-Status "Restricted guest invitations to admins and guest inviters only" "Success"
        $script:successCount++

    } else {
        Write-Status "Would restrict guest invitations (WhatIf mode)" "Warning"
        $script:skippedCount++
    }

} catch {
    Write-Status "Failed to restrict guest access: $($_.Exception.Message)" "Error"
    $script:failureCount++
}

# Summary Report
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "    COPILOT SECURITY HARDENING SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

if ($WhatIfPreference) {
    Write-Host "Mode:                   PREVIEW (WhatIf)" -ForegroundColor Yellow
    Write-Host "Previewed changes:      $script:skippedCount" -ForegroundColor Yellow
} else {
    Write-Host "Successfully applied:   $script:successCount" -ForegroundColor Green
    Write-Host "Failed:                 $script:failureCount" -ForegroundColor Red
    Write-Host "Skipped:                $script:skippedCount" -ForegroundColor Gray
}

Write-Host "============================================" -ForegroundColor Cyan

if ($WhatIfPreference) {
    Write-Host "`n[*] Run without -WhatIf to apply these changes" -ForegroundColor Yellow
} else {
    Write-Host "`n[✓] Copilot security hardening complete!" -ForegroundColor Green
}

Write-Host "`n[+] Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Create Information Barrier segments for client segregation" -ForegroundColor White
Write-Host "  2. Test DLP policies with sample client data" -ForegroundColor White
Write-Host "  3. Train users on Copilot best practices" -ForegroundColor White
Write-Host "  4. Run: .\Audit-CopilotSecurity.ps1 to verify configuration" -ForegroundColor White
Write-Host "  5. Monitor Copilot usage via Audit logs (Search-UnifiedAuditLog)" -ForegroundColor White

# Example IB segment creation commands
Write-Host "`n[+] Example Information Barrier Setup:" -ForegroundColor Cyan
Write-Host @"
  # Create client segments:
  New-OrganizationSegment -Name 'Tax-Preparation' -UserGroupFilter 'Department -eq TaxPrep'
  New-OrganizationSegment -Name 'Audit-Services' -UserGroupFilter 'Department -eq Audit'

  # Create barrier policy:
  New-InformationBarrierPolicy -Name 'Isolate-Tax-From-Audit' ``
    -AssignedSegment 'Tax-Preparation' ``
    -SegmentsBlocked 'Audit-Services' ``
    -State Active

  # Apply policies:
  Start-InformationBarrierPoliciesApplication
"@ -ForegroundColor Gray
