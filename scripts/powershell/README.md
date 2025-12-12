# PowerShell Scripts & Modules

[![PowerShell](https://img.shields.io/badge/PowerShell-5.1+-blue.svg)](https://docs.microsoft.com/en-us/powershell/)
[![Pester](https://img.shields.io/badge/Pester-5.0+-blue.svg)](https://pester.dev/)
[![PSScriptAnalyzer](https://img.shields.io/badge/PSScriptAnalyzer-Enabled-green.svg)](https://github.com/PowerShell/PSScriptAnalyzer)

## Overview

This directory contains PowerShell scripts and modules for Microsoft 365 security auditing, CIS benchmark compliance testing, and automated remediation. The core module `M365CIS.psm1` implements 15+ security controls based on the CIS Microsoft 365 Foundations Benchmark.

**PowerShell Components:**
- **Audit Scripts:** Main orchestration and execution scripts
- **Remediation Scripts:** Safe remediation with WhatIf support
- **Analysis Scripts:** Compare audit results and track improvements
- **Automation Scripts:** Scheduled task management
- **Core Module:** M365CIS.psm1 with Test-CIS-* functions

## Directory Structure

```
scripts/powershell/
├── Invoke-M365CISAudit.ps1          # Main audit orchestrator
├── PostRemediateM365CIS.ps1         # Safe remediation script
├── Compare-M365CISResults.ps1        # Audit comparison and trending
├── Setup-ScheduledAudit.ps1         # Create scheduled tasks
├── Remove-ScheduledAudit.ps1        # Remove scheduled tasks
├── Audit-CopilotSecurity.ps1        # Copilot-specific security checks
├── Secure-Copilot.ps1               # Copilot hardening script
└── modules/
    └── M365CIS.psm1                 # Core audit module (27KB, 600+ lines)
```

## M365CIS Module Reference

### Module Overview

**M365CIS.psm1** - Core security audit module implementing CIS Microsoft 365 Foundations Benchmark controls.

**Key Features:**
- 15+ security control test functions
- Standardized result objects for consistency
- Connection helpers for M365 services
- Purview integration with graceful fallback
- Error handling with Manual status on failures
- Comprehensive logging and evidence collection

**Module Size:** 27KB (600+ lines of PowerShell)

### Function Naming Convention

All test functions follow the pattern: `Test-CIS-<Service>-<Section>-<Control>`

**Examples:**
- `Test-CIS-EXO-1-1-1` - Exchange Online, Section 1.1, Control 1
- `Test-CIS-AAD-2-1-3` - Azure AD, Section 2.1, Control 3
- `Test-CIS-SPO-3-2-1` - SharePoint Online, Section 3.2, Control 1

### Core Functions

#### Connection Functions

```powershell
function Connect-M365CIS {
    <#
    .SYNOPSIS
    Connect to M365 services for CIS auditing
    
    .DESCRIPTION
    Establishes connections to Exchange Online, Microsoft Graph, 
    SharePoint Online, and optionally Purview for audit execution.
    
    .PARAMETER Service
    Specific service to connect to (ExchangeOnline, Graph, SharePoint, Purview)
    
    .PARAMETER UseServicePrincipal
    Use service principal authentication (for automation)
    
    .PARAMETER TenantId
    Azure AD tenant ID (required for service principal)
    
    .PARAMETER ClientId
    App registration client ID (required for service principal)
    
    .PARAMETER ClientSecret
    App registration client secret (required for service principal)
    
    .EXAMPLE
    # Interactive authentication
    Connect-M365CIS
    
    .EXAMPLE
    # Service principal authentication
    Connect-M365CIS -UseServicePrincipal `
        -TenantId "12345678-1234-1234-1234-123456789abc" `
        -ClientId "87654321-4321-4321-4321-cba987654321" `
        -ClientSecret "your-client-secret"
    
    .EXAMPLE
    # Connect to specific service
    Connect-M365CIS -Service ExchangeOnline
    
    .NOTES
    Requires the following PowerShell modules:
    - ExchangeOnlineManagement
    - Microsoft.Graph.Authentication
    - Microsoft.Online.SharePoint.PowerShell (for SharePoint)
    - ExchangeOnlineManagement (for Purview)
    #>
}

function Disconnect-M365CIS {
    <#
    .SYNOPSIS
    Disconnect from M365 services
    
    .DESCRIPTION
    Cleanly disconnects from all M365 services to free resources.
    
    .EXAMPLE
    Disconnect-M365CIS
    #>
}
```

#### Result Helper Functions

```powershell
function New-CISResult {
    <#
    .SYNOPSIS
    Create standardized CIS control result object
    
    .DESCRIPTION
    Returns a PSCustomObject with standardized fields for CIS control results.
    Used by all Test-CIS-* functions to ensure consistent output format.
    
    .PARAMETER ControlId
    CIS control ID (e.g., "1.1.1", "2.1.3")
    
    .PARAMETER Title
    Control title/description
    
    .PARAMETER Severity
    Control severity: Critical, High, Medium, Low
    
    .PARAMETER Expected
    Expected/compliant configuration
    
    .PARAMETER Actual
    Actual observed configuration
    
    .PARAMETER Status
    Control status: Pass, Fail, Manual
    
    .PARAMETER Evidence
    Detailed evidence supporting the result
    
    .PARAMETER Reference
    Reference URL (usually Microsoft Docs)
    
    .EXAMPLE
    return New-CISResult `
        -ControlId "1.1.1" `
        -Title "Ensure modern authentication is enabled" `
        -Severity "High" `
        -Expected "Modern authentication enabled" `
        -Actual "OAuth2ClientProfileEnabled = True" `
        -Status "Pass" `
        -Evidence "OAuth2ClientProfileEnabled: True" `
        -Reference "https://docs.microsoft.com/..."
    
    .OUTPUTS
    PSCustomObject with fields:
    - ControlId (string)
    - Title (string)
    - Severity (string)
    - Expected (string)
    - Actual (string)
    - Status (string: Pass, Fail, Manual)
    - Evidence (string)
    - Reference (string)
    - Timestamp (datetime)
    #>
}
```

### CIS Control Functions

#### Exchange Online Controls

```powershell
function Test-CIS-EXO-1-1-1 {
    <#
    .SYNOPSIS
    Ensure modern authentication for Exchange Online is enabled
    
    .DESCRIPTION
    Tests CIS Control 1.1.1 - Modern authentication provides more secure 
    authentication methods including MFA and reduces exposure to password spray attacks.
    
    .EXAMPLE
    $result = Test-CIS-EXO-1-1-1
    $result.Status  # Returns: Pass, Fail, or Manual
    
    .OUTPUTS
    PSCustomObject with control test results
    #>
}

function Test-CIS-EXO-1-1-3 {
    <#
    .SYNOPSIS
    Ensure basic authentication for Exchange Online is disabled
    
    .DESCRIPTION
    Tests CIS Control 1.1.3 - Basic authentication is vulnerable to 
    credential theft and should be disabled in favor of modern authentication.
    
    .EXAMPLE
    $result = Test-CIS-EXO-1-1-3
    #>
}

function Test-CIS-EXO-2-1-1 {
    <#
    .SYNOPSIS
    Ensure mail transport rules do not forward to external domains
    
    .DESCRIPTION
    Tests CIS Control 2.1.1 - Prevents automatic forwarding of emails 
    to external domains which could lead to data exfiltration.
    
    .EXAMPLE
    $result = Test-CIS-EXO-2-1-1
    #>
}

function Test-CIS-EXO-2-1-3 {
    <#
    .SYNOPSIS
    Ensure external sender warnings are enabled
    
    .DESCRIPTION
    Tests CIS Control 2.1.3 - Displays warnings on emails from external 
    senders to help users identify potential phishing attempts.
    
    .EXAMPLE
    $result = Test-CIS-EXO-2-1-3
    #>
}
```

#### Azure AD Controls

```powershell
function Test-CIS-AAD-1-1-1 {
    <#
    .SYNOPSIS
    Ensure multi-factor authentication is enabled for all users
    
    .DESCRIPTION
    Tests CIS Control 1.1.1 (Azure AD) - MFA adds an extra layer of security 
    and is critical for protecting privileged accounts.
    
    .EXAMPLE
    $result = Test-CIS-AAD-1-1-1
    #>
}

function Test-CIS-AAD-1-2-1 {
    <#
    .SYNOPSIS
    Ensure security defaults are enabled
    
    .DESCRIPTION
    Tests CIS Control 1.2.1 (Azure AD) - Security defaults provide baseline 
    security features including MFA requirements for administrators.
    
    .EXAMPLE
    $result = Test-CIS-AAD-1-2-1
    #>
}

function Test-CIS-AAD-2-1-3 {
    <#
    .SYNOPSIS
    Ensure guest users are reviewed regularly
    
    .DESCRIPTION
    Tests CIS Control 2.1.3 (Azure AD) - Regular review of guest accounts 
    ensures only authorized external users have access.
    
    .EXAMPLE
    $result = Test-CIS-AAD-2-1-3
    #>
}
```

#### SharePoint Online Controls

```powershell
function Test-CIS-SPO-3-1-1 {
    <#
    .SYNOPSIS
    Ensure external sharing is configured appropriately
    
    .DESCRIPTION
    Tests CIS Control 3.1.1 (SharePoint) - Controls external sharing to 
    prevent unauthorized access to sensitive documents.
    
    .EXAMPLE
    $result = Test-CIS-SPO-3-1-1
    #>
}

function Test-CIS-SPO-3-2-1 {
    <#
    .SYNOPSIS
    Ensure SharePoint Online anonymous sharing links expire
    
    .DESCRIPTION
    Tests CIS Control 3.2.1 (SharePoint) - Anonymous links should have 
    expiration dates to limit exposure of shared content.
    
    .EXAMPLE
    $result = Test-CIS-SPO-3-2-1
    #>
}
```

#### Microsoft Defender Controls

```powershell
function Test-CIS-Defender-1-1-1 {
    <#
    .SYNOPSIS
    Ensure Microsoft Defender for Office 365 is enabled
    
    .DESCRIPTION
    Tests CIS Control 1.1.1 (Defender) - Defender provides advanced threat 
    protection against phishing, malware, and zero-day attacks.
    
    .EXAMPLE
    $result = Test-CIS-Defender-1-1-1
    #>
}

function Test-CIS-Defender-2-1-1 {
    <#
    .SYNOPSIS
    Ensure Safe Links policy is enabled
    
    .DESCRIPTION
    Tests CIS Control 2.1.1 (Defender) - Safe Links scans URLs in emails 
    and Office documents to protect against malicious links.
    
    .EXAMPLE
    $result = Test-CIS-Defender-2-1-1
    #>
}

function Test-CIS-Defender-2-2-1 {
    <#
    .SYNOPSIS
    Ensure Safe Attachments policy is enabled
    
    .DESCRIPTION
    Tests CIS Control 2.2.1 (Defender) - Safe Attachments scans email 
    attachments in a sandbox environment before delivery.
    
    .EXAMPLE
    $result = Test-CIS-Defender-2-2-1
    #>
}
```

## Audit Scripts

### Invoke-M365CISAudit.ps1

**Main audit orchestrator script.**

**Purpose:** Execute comprehensive M365 CIS security audit and generate reports.

**Parameters:**
```powershell
param(
    [string]$SPOAdminUrl,              # SharePoint admin URL (required)
    [switch]$Timestamped,              # Add timestamp to output files
    [switch]$SkipPurview,              # Skip Purview compliance checks
    [string]$OutJson,                  # Output JSON file path
    [string]$OutCSV,                   # Output CSV file path
    [string]$ConfigFile                # Configuration file path
)
```

**Usage:**
```powershell
# Basic audit
.\Invoke-M365CISAudit.ps1 -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Timestamped audit (recommended for tracking)
.\Invoke-M365CISAudit.ps1 `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com" `
    -Timestamped

# Custom output paths
.\Invoke-M365CISAudit.ps1 `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com" `
    -OutJson "output/reports/security/my_audit.json" `
    -OutCSV "output/reports/security/my_audit.csv"

# Skip Purview (if not licensed)
.\Invoke-M365CISAudit.ps1 `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com" `
    -SkipPurview

# Use configuration file
.\Invoke-M365CISAudit.ps1 -ConfigFile "config/audit_config.json"
```

**Output:**
- JSON file with detailed results
- CSV file for Excel analysis
- Summary statistics in console
- Color-coded output (Green=Pass, Red=Fail, Yellow=Manual)

**Exit codes:**
- `0` - Success (audit completed)
- `1` - Error (connection failure, missing dependencies)

### PostRemediateM365CIS.ps1

**Safe remediation script with WhatIf support.**

**Purpose:** Apply remediation actions for failed CIS controls with preview mode.

**Parameters:**
```powershell
param(
    [switch]$WhatIf,                   # Preview changes without applying
    [switch]$Force,                    # Apply changes without confirmation
    [string]$ControlId,                # Remediate specific control only
    [string]$InputFile                 # Audit results file to remediate
)
```

**Usage:**
```powershell
# Preview remediation (SAFE - no changes)
.\PostRemediateM365CIS.ps1 -WhatIf

# Apply remediation (requires confirmation)
.\PostRemediateM365CIS.ps1

# Apply without confirmation (use with caution)
.\PostRemediateM365CIS.ps1 -Force

# Remediate specific control
.\PostRemediateM365CIS.ps1 -ControlId "1.1.1" -Force

# Remediate from specific audit file
.\PostRemediateM365CIS.ps1 `
    -InputFile "output/reports/security/audit_20251207.json" `
    -Force
```

**Safety Features:**
- **WhatIf mode:** Shows what would change without making modifications
- **Confirmation prompts:** Asks before each remediation action (unless -Force)
- **Backup:** Creates backup of current configuration before changes
- **Rollback:** Can revert changes if needed
- **Detailed logging:** Logs all remediation actions

**Supported remediations:**
- Enable modern authentication (1.1.1)
- Disable basic authentication (1.1.3)
- Configure external sender warnings (2.1.3)
- Set anonymous link expiration (3.2.1)
- Enable Safe Links (Defender 2.1.1)
- Enable Safe Attachments (Defender 2.2.1)

**Security considerations:**
- ✅ **Do:** Always run with `-WhatIf` first
- ✅ **Do:** Test in non-production tenant if possible
- ✅ **Do:** Review changes in console output
- ❌ **Don't:** Run `-Force` without understanding impact
- ❌ **Don't:** Remediate during business hours (may cause disruption)

### Compare-M365CISResults.ps1

**Audit comparison and trending script.**

**Purpose:** Compare two audit results to track improvements and identify regressions.

**Parameters:**
```powershell
param(
    [string]$BeforeFile,               # First audit file (required)
    [string]$AfterFile,                # Second audit file (required)
    [string]$OutputHtml,               # Output HTML report path
    [string]$OutputCsv                 # Output CSV report path
)
```

**Usage:**
```powershell
# Compare two audits
.\Compare-M365CISResults.ps1 `
    -BeforeFile "output/reports/security/audit_before.json" `
    -AfterFile "output/reports/security/audit_after.json"

# Generate HTML report
.\Compare-M365CISResults.ps1 `
    -BeforeFile "audit_before.json" `
    -AfterFile "audit_after.json" `
    -OutputHtml "comparison_report.html"

# Generate CSV for analysis
.\Compare-M365CISResults.ps1 `
    -BeforeFile "audit_before.json" `
    -AfterFile "audit_after.json" `
    -OutputCsv "comparison.csv"
```

**Output includes:**
- Controls that changed status (Fail→Pass, Pass→Fail)
- New failures since last audit
- Fixed issues since last audit
- Compliance score improvement percentage
- Detailed change report

**Use cases:**
- Track post-remediation improvements
- Monitor compliance trends over time
- Identify configuration drift
- Validate security posture improvements

## Automation Scripts

### Setup-ScheduledAudit.ps1

**Create Windows scheduled task for automated audits.**

**Parameters:**
```powershell
param(
    [ValidateSet("Daily","Weekly","Monthly")]
    [string]$Schedule = "Weekly",      # Schedule frequency
    
    [ValidateSet("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")]
    [string]$DayOfWeek = "Monday",     # Day for weekly schedule
    
    [string]$Time = "09:00",           # Time to run (24-hour format)
    [string]$SPOAdminUrl,              # SharePoint admin URL
    [switch]$UseServicePrincipal,      # Use service principal auth
    [string]$LogPath                   # Log file path
)
```

**Usage:**
```powershell
# Weekly audit on Monday at 9 AM (requires Administrator)
.\Setup-ScheduledAudit.ps1 `
    -Schedule Weekly `
    -DayOfWeek Monday `
    -Time "09:00" `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Daily audit at 2 AM
.\Setup-ScheduledAudit.ps1 `
    -Schedule Daily `
    -Time "02:00" `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Monthly audit on 1st at midnight with service principal
.\Setup-ScheduledAudit.ps1 `
    -Schedule Monthly `
    -Time "00:00" `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com" `
    -UseServicePrincipal
```

**Requirements:**
- Must run as Administrator
- Service principal credentials stored in Windows Credential Manager (if using)
- Sufficient permissions to create scheduled tasks

**Task properties:**
- Runs with highest privileges
- Wakes computer if asleep
- Runs whether user is logged in or not
- Logs to `output/logs/scheduled_audit.log`

### Remove-ScheduledAudit.ps1

**Remove scheduled audit task.**

**Usage:**
```powershell
# Remove task (requires Administrator)
.\Remove-ScheduledAudit.ps1 -Force
```

## Service Principal Setup

### Creating Service Principal

**For unattended automation:**

```powershell
# Connect to Azure
Connect-AzAccount

# Create app registration
$app = New-AzADApplication -DisplayName "M365-CIS-Audit-ServicePrincipal"

# Create service principal
$sp = New-AzADServicePrincipal -ApplicationId $app.AppId

# Create client secret
$secret = New-AzADAppCredential -ObjectId $app.Id -EndDate (Get-Date).AddYears(2)

# Display credentials
Write-Host "Tenant ID: $((Get-AzContext).Tenant.Id)"
Write-Host "Client ID: $($app.AppId)"
Write-Host "Client Secret: $($secret.SecretText)"
```

**Required API permissions:**
- **Microsoft Graph:**
  - Directory.Read.All (Application)
  - User.Read.All (Application)
  - Policy.Read.All (Application)
- **Exchange Online:**
  - Exchange.ManageAsApp (Application)
- **SharePoint Online:**
  - Sites.FullControl.All (Application)

**Grant admin consent:**
```powershell
# In Azure Portal
# Go to: App Registrations → Your App → API Permissions → Grant Admin Consent
```

📖 **Full Setup Guide:** See [`../../docs/M365_SERVICE_PRINCIPAL_SETUP.md`](../../docs/M365_SERVICE_PRINCIPAL_SETUP.md)

### Using Service Principal in Scripts

```powershell
# Set environment variables (or use .env file)
$env:M365_TENANT_ID = "your-tenant-id"
$env:M365_CLIENT_ID = "your-client-id"
$env:M365_CLIENT_SECRET = "your-client-secret"

# Run audit with service principal
Connect-M365CIS -UseServicePrincipal `
    -TenantId $env:M365_TENANT_ID `
    -ClientId $env:M365_CLIENT_ID `
    -ClientSecret $env:M365_CLIENT_SECRET

# Execute audit
.\Invoke-M365CISAudit.ps1 -SPOAdminUrl "https://contoso-admin.sharepoint.com"
```

## Common Issues

### Connection Errors

**Issue:** `Connect-ExchangeOnline: Access Denied`

**Causes:**
- Missing required permissions
- MFA not configured for account
- Conditional Access policies blocking access

**Solutions:**
```powershell
# Solution 1: Use MFA-enabled account
Connect-M365CIS  # Follow MFA prompts

# Solution 2: Use service principal
Connect-M365CIS -UseServicePrincipal `
    -TenantId "tenant-id" `
    -ClientId "client-id" `
    -ClientSecret "secret"

# Solution 3: Check permissions
Get-MsolUserRole -UserPrincipalName "your-account@contoso.com"
```

**Issue:** `Module not found: ExchangeOnlineManagement`

**Solution:**
```powershell
# Install required modules
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Authentication -Scope CurrentUser -Force
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser -Force
```

### PSModulePath Issues

**Issue:** `Import-Module M365CIS.psm1: Module not found`

**Cause:** OneDrive syncing changes PSModulePath

**Solution:**
```powershell
# Connect-M365CIS auto-fixes this
Import-Module "./scripts/powershell/modules/M365CIS.psm1" -Force

# Or manually fix PSModulePath
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$modulePath = Join-Path $repoRoot "scripts\powershell\modules"
$env:PSModulePath += ";$modulePath"
```

### Permission Errors

**Issue:** `Get-OrganizationConfig: Access Denied`

**Cause:** Insufficient Exchange Online permissions

**Required roles:**
- Exchange Administrator
- Global Reader (minimum)
- Security Administrator (recommended)

**Solution:**
```powershell
# In Microsoft 365 Admin Center:
# Users → Active Users → Select User → Roles → Assign Role

# Or via PowerShell:
Connect-MsolService
Add-MsolRoleMember -RoleName "Exchange Administrator" -RoleMemberEmailAddress "user@contoso.com"
```

### Purview Errors

**Issue:** `Purview cmdlets not available`

**Cause:** Purview not licensed or not configured

**Solution:**
```powershell
# Skip Purview checks
.\Invoke-M365CISAudit.ps1 -SkipPurview -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Or configure in audit_config.json:
{
  "controlsConfig": {
    "skipPurview": true
  }
}
```

## Security Best Practices

### Credential Management

**DO:**
- ✅ Use service principals for automation
- ✅ Store secrets in Azure Key Vault or Windows Credential Manager
- ✅ Use environment variables for sensitive values
- ✅ Rotate secrets every 90 days
- ✅ Use separate accounts for auditing (not Global Admin)

**DON'T:**
- ❌ Hardcode credentials in scripts
- ❌ Commit secrets to source control
- ❌ Use personal accounts for automation
- ❌ Share service principal secrets via email/chat
- ❌ Use never-expiring secrets

### Audit Logging

**Enable comprehensive logging:**
```powershell
# Configure transcript logging
Start-Transcript -Path "output/logs/audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Your audit code here
.\Invoke-M365CISAudit.ps1 -SPOAdminUrl "https://contoso-admin.sharepoint.com"

Stop-Transcript
```

**Log rotation:**
```powershell
# scripts/powershell/Rotate-AuditLogs.ps1
function Rotate-AuditLogs {
    param([int]$RetentionDays = 90)
    
    $logPath = "output/logs"
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    
    Get-ChildItem $logPath -Filter "*.log" | 
        Where-Object { $_.LastWriteTime -lt $cutoffDate } |
        ForEach-Object {
            Write-Host "Archiving old log: $($_.Name)"
            Compress-Archive -Path $_.FullName -DestinationPath "$logPath/archive/$($_.Name).zip"
            Remove-Item $_.FullName
        }
}
```

### Least Privilege

**Use minimum required permissions:**

```powershell
# Azure AD roles for auditing (choose one):
# 1. Global Reader (recommended for auditing only)
# 2. Security Reader (for security-focused audits)
# 3. Exchange Administrator (if remediation needed)

# Service principal permissions (minimum):
# - Directory.Read.All (read user/group info)
# - User.Read.All (read user properties)
# - Policy.Read.All (read security policies)
# - Exchange.ManageAsApp (read Exchange config)
# - Sites.FullControl.All (read SharePoint config - can be scoped to specific sites)
```

### Input Validation

**Always validate inputs:**
```powershell
function Invoke-SafeAudit {
    param(
        [Parameter(Mandatory)]
        [ValidatePattern('^https://[a-z0-9-]+-admin\.sharepoint\.com$')]
        [string]$SPOAdminUrl
    )
    
    # Validate URL format
    if ($SPOAdminUrl -notmatch '^https://[a-z0-9-]+-admin\.sharepoint\.com$') {
        throw "Invalid SharePoint admin URL format"
    }
    
    # Continue with audit
}
```

## Module Development

### Creating New CIS Control Functions

**Template for new control:**
```powershell
function Test-CIS-XXX-Y-Z-N {
    <#
    .SYNOPSIS
    Brief description of what this control tests
    
    .DESCRIPTION
    Detailed description of the security requirement and why it matters.
    Include references to CIS benchmark documentation.
    
    .EXAMPLE
    $result = Test-CIS-XXX-Y-Z-N
    $result.Status  # Returns: Pass, Fail, or Manual
    
    .OUTPUTS
    PSCustomObject with standardized CIS control result
    
    .NOTES
    CIS Control: X.Y.Z
    Severity: [Critical|High|Medium|Low]
    Service: [Exchange Online|Azure AD|SharePoint Online|Defender|Teams]
    #>
    
    try {
        # Get actual configuration
        $actual = Get-ServiceConfiguration
        $expected = "Required secure configuration"
        
        # Determine status
        $status = if ($actual -eq $expected) { "Pass" } else { "Fail" }
        
        # Build evidence
        $evidence = "Configuration details: $actual"
        
        # Return standardized result
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control title" `
            -Severity "High" `
            -Expected $expected `
            -Actual $actual `
            -Status $status `
            -Evidence $evidence `
            -Reference "https://docs.microsoft.com/..."
    }
    catch {
        # Always return Manual status on errors
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control title" `
            -Severity "High" `
            -Expected "Manual verification required" `
            -Actual "Error: $($_.Exception.Message)" `
            -Status "Manual" `
            -Evidence "Error occurred during automated check" `
            -Reference "https://docs.microsoft.com/..."
    }
}
```

### Testing New Functions

```powershell
# Test function manually
Import-Module ./scripts/powershell/modules/M365CIS.psm1 -Force
Connect-M365CIS

$result = Test-CIS-XXX-Y-Z-N
$result | Format-List

# Verify output structure
$result.ControlId     # Should be string
$result.Status        # Should be Pass, Fail, or Manual
$result.Timestamp     # Should be datetime
```

### Adding to Module

```powershell
# 1. Add function to M365CIS.psm1
# 2. Export function (add to Export-ModuleMember at end of file)
Export-ModuleMember -Function @(
    'Connect-M365CIS',
    'Test-CIS-EXO-1-1-1',
    'Test-CIS-XXX-Y-Z-N',  # Your new function
    # ... other functions
)

# 3. Add to CIS benchmark JSON
# config/benchmarks/service_name.json
{
  "controls": [
    {
      "id": "X.Y.Z",
      "title": "Control title",
      "implementationFunction": "Test-CIS-XXX-Y-Z-N"
    }
  ]
}

# 4. Add Pester test
# tests/powershell/M365CIS.Tests.ps1
Describe "Test-CIS-XXX-Y-Z-N" {
    It "Should return Pass when compliant" {
        Mock Get-ServiceConfiguration { return "ExpectedValue" }
        $result = Test-CIS-XXX-Y-Z-N
        $result.Status | Should -Be "Pass"
    }
}
```

## Cross-References

### Related Documentation

- **Parent README:** [`../../README.md`](../../README.md) - Project overview
- **Scripts Overview:** [`../README.md`](../README.md) - All scripts documentation
- **Source Code:** [`../../src/README.md`](../../src/README.md) - Python modules
- **Testing Guide:** [`../../tests/README.md`](../../tests/README.md) - Test patterns
- **Configuration Guide:** [`../../config/README.md`](../../config/README.md) - Configuration files
- **Service Principal Setup:** [`../../docs/M365_SERVICE_PRINCIPAL_SETUP.md`](../../docs/M365_SERVICE_PRINCIPAL_SETUP.md) - Authentication setup
- **AI Development Guide:** [`../../.github/copilot-instructions.md`](../../.github/copilot-instructions.md) - AI agent patterns

### External Resources

- **CIS Microsoft 365 Benchmark:** [CIS Benchmarks](https://www.cisecurity.org/benchmark/microsoft_365)
- **PowerShell Documentation:** [Microsoft Docs](https://docs.microsoft.com/en-us/powershell/)
- **Exchange Online PowerShell:** [Exchange Online Management](https://docs.microsoft.com/en-us/powershell/exchange/exchange-online-powershell)
- **Microsoft Graph PowerShell:** [Graph PowerShell SDK](https://docs.microsoft.com/en-us/powershell/microsoftgraph/)
- **Pester v5:** [Pester Documentation](https://pester.dev/)

---

**🔐 Security Focused:** All scripts implement secure coding practices, input validation, and comprehensive error handling for CPA/audit compliance.

**🤖 Automation Ready:** Support for service principal authentication enables unattended execution in CI/CD pipelines and scheduled tasks.

**✅ Quality Assured:** All functions return standardized result objects and include Pester v5 tests for reliability.
