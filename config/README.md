# Configuration Guide

[![JSON Schema](https://img.shields.io/badge/JSON-Schema-lightgrey.svg)](https://json-schema.org/)
[![YAML Support](https://img.shields.io/badge/YAML-Supported-blue.svg)](https://yaml.org/)

## Overview

The `config/` directory contains configuration files for M365 security audits, CIS benchmark definitions, and tenant-specific settings. All configurations support **JSON** and **YAML** formats with schema validation.

**Configuration Philosophy:**
- **Tenant-agnostic defaults:** Works out-of-the-box for most M365 tenants
- **Easy customization:** Simple JSON/YAML editing for specific requirements
- **Multi-tenant support:** Configure multiple tenants in a single file
- **CIS compliance:** Pre-configured with CIS Microsoft 365 Foundations Benchmark controls
- **Validation:** Automatic schema validation prevents configuration errors

## Configuration Files

```
config/
├── audit_config.json          # Main audit configuration
├── benchmarks/                # CIS control definitions
│   ├── exchange_online.json   # Exchange Online CIS controls
│   ├── azure_ad.json          # Azure AD CIS controls
│   ├── sharepoint_online.json # SharePoint Online CIS controls
│   ├── teams.json            # Microsoft Teams CIS controls
│   └── defender.json         # Microsoft Defender CIS controls
└── .env.template             # Environment variables template (secrets)
```

## Audit Configuration (`audit_config.json`)

### Structure

The main configuration file controls audit behavior, scheduling, notifications, and output options.

**Full example:**
```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://tenant-admin.sharepoint.com",
    "tenantId": "12345678-1234-1234-1234-123456789abc",
    "tenantName": "Contoso Corporation",
    "scheduleFrequency": "Weekly",
    "scheduleDay": "Monday",
    "scheduleTime": "09:00"
  },
  "notificationConfig": {
    "enabled": false,
    "smtpServer": "smtp.office365.com",
    "smtpPort": 587,
    "smtpFrom": "audit@contoso.com",
    "smtpUsername": "audit@contoso.com",
    "recipients": [
      "security-team@contoso.com",
      "compliance@contoso.com"
    ]
  },
  "controlsConfig": {
    "skipExchange": false,
    "skipGraph": false,
    "skipPurview": false,
    "skipSharePoint": false,
    "includeIntune": true,
    "includeAzureAD": true,
    "includeDefender": true,
    "customControls": []
  },
  "outputConfig": {
    "timestampedOutputs": true,
    "retentionDays": 90,
    "generateDashboard": true,
    "dashboardPath": "output/reports/security/dashboard.html",
    "exportFormats": ["json", "csv", "xlsx", "html"]
  },
  "advancedConfig": {
    "parallelExecution": false,
    "retryAttempts": 3,
    "retryDelaySeconds": 5,
    "timeoutSeconds": 300,
    "cacheResults": true,
    "cacheDurationMinutes": 60
  }
}
```

### Configuration Sections

#### `tenantConfig` - Tenant Settings

**Required for all audits:**
```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://tenant-admin.sharepoint.com",
    "tenantId": "12345678-1234-1234-1234-123456789abc",
    "tenantName": "Contoso Corporation"
  }
}
```

**Fields:**
- `spoAdminUrl` (string, required): SharePoint Online admin URL
  - **Format:** `https://<tenant>-admin.sharepoint.com`
  - **Find:** Microsoft 365 Admin Center → SharePoint → Settings
- `tenantId` (string, optional): Azure AD tenant ID (GUID)
  - **Find:** Azure Portal → Azure Active Directory → Properties
- `tenantName` (string, optional): Friendly tenant name for reports
- `scheduleFrequency` (string, optional): `"Daily"`, `"Weekly"`, or `"Monthly"`
- `scheduleDay` (string, optional): Day of week for weekly audits (`"Monday"` through `"Sunday"`)
- `scheduleTime` (string, optional): Time for scheduled audits (`"HH:MM"` format, 24-hour)

**Example configurations:**

**Daily audits:**
```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://contoso-admin.sharepoint.com",
    "scheduleFrequency": "Daily",
    "scheduleTime": "02:00"
  }
}
```

**Weekly audits on Monday at 9 AM:**
```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://contoso-admin.sharepoint.com",
    "scheduleFrequency": "Weekly",
    "scheduleDay": "Monday",
    "scheduleTime": "09:00"
  }
}
```

#### `notificationConfig` - Email Notifications

**Email alerts for audit results:**
```json
{
  "notificationConfig": {
    "enabled": true,
    "smtpServer": "smtp.office365.com",
    "smtpPort": 587,
    "smtpFrom": "audit@contoso.com",
    "smtpUsername": "audit@contoso.com",
    "recipients": [
      "security-team@contoso.com",
      "compliance@contoso.com"
    ],
    "sendOnFailureOnly": true,
    "includeDashboard": true
  }
}
```

**Fields:**
- `enabled` (boolean): Enable/disable email notifications
- `smtpServer` (string): SMTP server hostname
- `smtpPort` (integer): SMTP port (typically 587 for TLS, 25 for non-TLS)
- `smtpFrom` (string): From email address
- `smtpUsername` (string): SMTP authentication username
- `recipients` (array): List of email addresses to notify
- `sendOnFailureOnly` (boolean, optional): Only send emails when failures detected
- `includeDashboard` (boolean, optional): Attach HTML dashboard to email

**Security considerations:**
- ❌ **Don't:** Store SMTP password in `audit_config.json`
- ✅ **Do:** Use environment variable `SMTP_PASSWORD` or Azure Key Vault
- ✅ **Do:** Use service accounts with limited permissions
- ✅ **Do:** Enable MFA on notification accounts

#### `controlsConfig` - Control Selection

**Enable/disable specific control categories:**
```json
{
  "controlsConfig": {
    "skipExchange": false,
    "skipGraph": false,
    "skipPurview": false,
    "skipSharePoint": false,
    "includeIntune": true,
    "includeAzureAD": true,
    "includeDefender": true,
    "severityFilter": ["Critical", "High"],
    "customControls": [
      "CUSTOM-001",
      "CUSTOM-002"
    ]
  }
}
```

**Fields:**
- `skipExchange` (boolean): Skip Exchange Online controls
- `skipGraph` (boolean): Skip Microsoft Graph controls
- `skipPurview` (boolean): Skip Purview compliance controls
- `skipSharePoint` (boolean): Skip SharePoint Online controls
- `includeIntune` (boolean): Include Intune mobile device controls
- `includeAzureAD` (boolean): Include Azure AD identity controls
- `includeDefender` (boolean): Include Microsoft Defender controls
- `severityFilter` (array, optional): Only run controls with these severities
  - Values: `"Critical"`, `"High"`, `"Medium"`, `"Low"`
- `customControls` (array, optional): Custom control IDs to include

**Use cases:**

**Quick audit (Exchange and Azure AD only):**
```json
{
  "controlsConfig": {
    "skipExchange": false,
    "skipGraph": true,
    "skipPurview": true,
    "skipSharePoint": true,
    "includeIntune": false,
    "includeAzureAD": true,
    "includeDefender": false
  }
}
```

**Critical and high severity only:**
```json
{
  "controlsConfig": {
    "severityFilter": ["Critical", "High"]
  }
}
```

#### `outputConfig` - Output Options

**Control report generation:**
```json
{
  "outputConfig": {
    "timestampedOutputs": true,
    "retentionDays": 90,
    "generateDashboard": true,
    "dashboardPath": "output/reports/security/dashboard.html",
    "exportFormats": ["json", "csv", "xlsx", "html"],
    "compressArchive": false,
    "uploadToSharePoint": false,
    "sharePointSiteUrl": ""
  }
}
```

**Fields:**
- `timestampedOutputs` (boolean): Add timestamp to output filenames
  - `true`: `audit_20251207_143000.json`
  - `false`: `audit.json` (overwrites previous)
- `retentionDays` (integer): Days to keep old reports (0 = keep forever)
- `generateDashboard` (boolean): Generate interactive HTML dashboard
- `dashboardPath` (string): Output path for dashboard
- `exportFormats` (array): Formats to generate (`"json"`, `"csv"`, `"xlsx"`, `"html"`)
- `compressArchive` (boolean, optional): Compress old reports to ZIP
- `uploadToSharePoint` (boolean, optional): Upload reports to SharePoint
- `sharePointSiteUrl` (string, optional): SharePoint site URL for uploads

#### `advancedConfig` - Advanced Options

**Performance and behavior tuning:**
```json
{
  "advancedConfig": {
    "parallelExecution": false,
    "maxParallelThreads": 5,
    "retryAttempts": 3,
    "retryDelaySeconds": 5,
    "timeoutSeconds": 300,
    "cacheResults": true,
    "cacheDurationMinutes": 60,
    "verboseLogging": false,
    "debugMode": false
  }
}
```

**Fields:**
- `parallelExecution` (boolean): Run controls in parallel (experimental)
- `maxParallelThreads` (integer): Max concurrent control tests
- `retryAttempts` (integer): Number of retries for failed API calls
- `retryDelaySeconds` (integer): Delay between retries
- `timeoutSeconds` (integer): Timeout for individual control tests
- `cacheResults` (boolean): Cache API responses to reduce calls
- `cacheDurationMinutes` (integer): Cache validity duration
- `verboseLogging` (boolean): Enable verbose logging
- `debugMode` (boolean): Enable debug mode (very verbose)

**Performance notes:**
- Parallel execution can reduce audit time by 40-60%
- Caching reduces API calls but may show stale data
- Recommended for large tenants: `parallelExecution: true`, `maxParallelThreads: 5`
- Recommended for small tenants: `parallelExecution: false` (simpler debugging)

## CIS Benchmark Customization

### Benchmark File Structure

**CIS control definition format:**
```json
{
  "controls": [
    {
      "id": "1.1.1",
      "title": "Ensure modern authentication for Exchange Online is enabled",
      "description": "Modern authentication provides more secure authentication methods including MFA.",
      "rationale": "Basic authentication is vulnerable to password spray and brute force attacks.",
      "severity": "High",
      "category": "Identity and Access Management",
      "service": "Exchange Online",
      "remediationSteps": [
        "1. Navigate to Exchange Admin Center",
        "2. Go to Settings > Modern Authentication",
        "3. Enable Modern Authentication for all protocols"
      ],
      "automatedRemediation": true,
      "references": [
        "https://docs.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/enable-or-disable-modern-authentication-in-exchange-online"
      ],
      "cisVersion": "2.0",
      "implementationFunction": "Test-CIS-EXO-1-1-1"
    }
  ]
}
```

### Adding Custom Controls

**Create custom control file:**
```json
// config/benchmarks/custom_controls.json
{
  "controls": [
    {
      "id": "CUSTOM-001",
      "title": "Ensure guest access is reviewed quarterly",
      "description": "Regular review of guest accounts ensures only authorized external users have access.",
      "severity": "Medium",
      "category": "Custom Compliance",
      "service": "Azure AD",
      "implementationFunction": "Test-Custom-GuestReview",
      "customControl": true
    }
  ]
}
```

**Implement test function:**
```powershell
# scripts/powershell/modules/CustomControls.psm1
function Test-Custom-GuestReview {
    <#
    .SYNOPSIS
    Verify guest account review is current
    #>
    try {
        # Check last review date
        $lastReview = Get-GuestReviewDate
        $daysSinceReview = (Get-Date) - $lastReview
        
        $status = if ($daysSinceReview.Days -le 90) { "Pass" } else { "Fail" }
        
        return New-CISResult `
            -ControlId "CUSTOM-001" `
            -Title "Ensure guest access is reviewed quarterly" `
            -Severity "Medium" `
            -Expected "Last review within 90 days" `
            -Actual "Last review: $($lastReview.ToString('yyyy-MM-dd'))" `
            -Status $status `
            -Evidence "Days since review: $($daysSinceReview.Days)" `
            -Reference "Internal Policy DOC-123"
    }
    catch {
        return New-CISResult `
            -ControlId "CUSTOM-001" `
            -Title "Ensure guest access is reviewed quarterly" `
            -Severity "Medium" `
            -Expected "Manual verification required" `
            -Actual "Error: $($_.Exception.Message)" `
            -Status "Manual"
    }
}
```

**Enable custom controls:**
```json
// config/audit_config.json
{
  "controlsConfig": {
    "customControls": ["CUSTOM-001", "CUSTOM-002"]
  }
}
```

### Modifying Existing Controls

**Override control severity:**
```json
// config/benchmarks/overrides.json
{
  "controlOverrides": {
    "1.1.1": {
      "severity": "Critical",  // Changed from "High"
      "reason": "Company policy requires Critical classification"
    },
    "2.1.3": {
      "enabled": false,  // Disable this control
      "reason": "Not applicable to our environment"
    }
  }
}
```

## Multi-Tenant Setup

### Configuration Patterns

**Pattern 1: Separate configuration files**
```
config/
├── tenants/
│   ├── client-a.json
│   ├── client-b.json
│   └── client-c.json
```

**Pattern 2: Single file with tenant array**
```json
// config/multi_tenant_config.json
{
  "tenants": [
    {
      "name": "Client A",
      "tenantId": "aaaaaaaa-1234-1234-1234-123456789abc",
      "spoAdminUrl": "https://clienta-admin.sharepoint.com",
      "outputPath": "output/reports/client-a/"
    },
    {
      "name": "Client B",
      "tenantId": "bbbbbbbb-1234-1234-1234-123456789abc",
      "spoAdminUrl": "https://clientb-admin.sharepoint.com",
      "outputPath": "output/reports/client-b/"
    }
  ]
}
```

### Batch Audit Execution

**PowerShell script for multi-tenant audits:**
```powershell
# scripts/powershell/Invoke-MultiTenantAudit.ps1
param(
    [string]$ConfigFile = "config/multi_tenant_config.json"
)

$config = Get-Content $ConfigFile | ConvertFrom-Json

foreach ($tenant in $config.tenants) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Auditing Tenant: $($tenant.name)" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Run audit for this tenant
    & ./scripts/powershell/Invoke-M365CISAudit.ps1 `
        -SPOAdminUrl $tenant.spoAdminUrl `
        -Timestamped `
        -OutputPath $tenant.outputPath
    
    # Generate dashboard
    python scripts/generate_security_dashboard.py `
        --input "$($tenant.outputPath)/audit.json" `
        --output "$($tenant.outputPath)/dashboard.html"
}

Write-Host "`nAll tenant audits complete!" -ForegroundColor Green
```

**GitHub Action workflow:**
```yaml
# .github/workflows/multi-tenant-audit.yml
name: Multi-Tenant Audit

on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly
  workflow_dispatch:

jobs:
  audit:
    runs-on: windows-latest
    strategy:
      matrix:
        tenant: [client-a, client-b, client-c]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Audit for ${{ matrix.tenant }}
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets[format('TENANT_ID_{0}', matrix.tenant)] }}
          client-id: ${{ secrets[format('CLIENT_ID_{0}', matrix.tenant)] }}
          client-secret: ${{ secrets[format('CLIENT_SECRET_{0}', matrix.tenant)] }}
          output-path: output/reports/${{ matrix.tenant }}/
```

## Environment Variables

### Variables Reference

**Required environment variables:**
```bash
# M365 Authentication
M365_TENANT_ID="12345678-1234-1234-1234-123456789abc"
M365_CLIENT_ID="87654321-4321-4321-4321-cba987654321"
M365_CLIENT_SECRET="your-client-secret-here"
SPO_ADMIN_URL="https://tenant-admin.sharepoint.com"

# OpenAI Integration (optional)
OPENAI_API_KEY="sk-..."
OPENAI_ORG_ID="org-..."

# SMTP Notifications (optional)
SMTP_SERVER="smtp.office365.com"
SMTP_PORT="587"
SMTP_USERNAME="audit@contoso.com"
SMTP_PASSWORD="smtp-password-here"
SMTP_FROM="audit@contoso.com"
```

**Optional environment variables:**
```bash
# Output Configuration
OUTPUT_PATH="output/reports/security/"
RETENTION_DAYS="90"
GENERATE_DASHBOARD="true"

# Advanced Configuration
PARALLEL_EXECUTION="false"
RETRY_ATTEMPTS="3"
CACHE_RESULTS="true"
VERBOSE_LOGGING="false"
DEBUG_MODE="false"

# Multi-Tenant
ACTIVE_TENANT="client-a"
```

### Using .env Files

**Create `.env` file (DO NOT COMMIT):**
```bash
# Copy template
cp config/.env.template .env

# Edit with your values
nano .env
```

**Load in PowerShell:**
```powershell
# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}
```

**Load in Python:**
```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
tenant_id = os.getenv("M365_TENANT_ID")
client_id = os.getenv("M365_CLIENT_ID")
```

## Secrets Management

### Azure Key Vault (Recommended for Production)

**Store secrets in Azure Key Vault:**
```powershell
# Install Azure PowerShell module
Install-Module -Name Az.KeyVault -Scope CurrentUser

# Connect to Azure
Connect-AzAccount

# Store secrets
$vaultName = "m365-audit-vault"
Set-AzKeyVaultSecret -VaultName $vaultName -Name "M365-ClientSecret" -SecretValue (ConvertTo-SecureString "your-secret" -AsPlainText -Force)
Set-AzKeyVaultSecret -VaultName $vaultName -Name "SMTP-Password" -SecretValue (ConvertTo-SecureString "smtp-pass" -AsPlainText -Force)
```

**Retrieve secrets in scripts:**
```powershell
# Connect and retrieve
Connect-AzAccount -Identity  # For managed identity
$clientSecret = Get-AzKeyVaultSecret -VaultName "m365-audit-vault" -Name "M365-ClientSecret" -AsPlainText
$smtpPassword = Get-AzKeyVaultSecret -VaultName "m365-audit-vault" -Name "SMTP-Password" -AsPlainText

# Use in audit
& ./scripts/powershell/Invoke-M365CISAudit.ps1 `
    -ClientId $env:M365_CLIENT_ID `
    -ClientSecret $clientSecret `
    -SPOAdminUrl $env:SPO_ADMIN_URL
```

### GitHub Secrets (For GitHub Actions)

**Store secrets in GitHub repository:**
1. Navigate to repository **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add secrets:
   - `M365_TENANT_ID`
   - `M365_CLIENT_ID`
   - `M365_CLIENT_SECRET`
   - `SPO_ADMIN_URL`

**Use in workflows:**
```yaml
- name: Run M365 Audit
  uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID }}
    client-id: ${{ secrets.M365_CLIENT_ID }}
    client-secret: ${{ secrets.M365_CLIENT_SECRET }}
    spo-admin-url: ${{ secrets.SPO_ADMIN_URL }}
```

### Local Development (Environment Variables)

**Windows (PowerShell):**
```powershell
# Set for current session
$env:M365_TENANT_ID = "your-tenant-id"
$env:M365_CLIENT_ID = "your-client-id"

# Set permanently (user-level)
[Environment]::SetEnvironmentVariable("M365_TENANT_ID", "your-tenant-id", "User")
```

**Linux/macOS (Bash):**
```bash
# Set for current session
export M365_TENANT_ID="your-tenant-id"
export M365_CLIENT_ID="your-client-id"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export M365_TENANT_ID="your-tenant-id"' >> ~/.bashrc
```

## Validation

### Schema Validation

**Validate configuration files:**
```bash
# Install JSON schema validator
pip install jsonschema

# Validate audit config
python -c "
import json
import jsonschema

with open('config/audit_config.json') as f:
    config = json.load(f)

with open('config/schemas/audit_config_schema.json') as f:
    schema = json.load(f)

jsonschema.validate(config, schema)
print('✅ Configuration valid!')
"
```

**PowerShell validation:**
```powershell
function Test-AuditConfiguration {
    param([string]$ConfigPath)
    
    try {
        $config = Get-Content $ConfigPath | ConvertFrom-Json
        
        # Validate required fields
        if (-not $config.tenantConfig.spoAdminUrl) {
            throw "Missing required field: tenantConfig.spoAdminUrl"
        }
        
        # Validate URL format
        if ($config.tenantConfig.spoAdminUrl -notmatch '^https://[a-z0-9-]+-admin\.sharepoint\.com$') {
            throw "Invalid SharePoint admin URL format"
        }
        
        Write-Host "✅ Configuration valid!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Configuration error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Usage
Test-AuditConfiguration -ConfigPath "config/audit_config.json"
```

### Pre-flight Checks

**Verify configuration before audit:**
```powershell
# scripts/powershell/Test-AuditPrerequisites.ps1
function Test-AuditPrerequisites {
    Write-Host "Running pre-flight checks..." -ForegroundColor Cyan
    
    # Check configuration
    if (-not (Test-Path "config/audit_config.json")) {
        Write-Host "❌ Missing audit_config.json" -ForegroundColor Red
        return $false
    }
    
    # Check environment variables
    $required = @("M365_TENANT_ID", "M365_CLIENT_ID", "M365_CLIENT_SECRET")
    foreach ($var in $required) {
        if (-not [Environment]::GetEnvironmentVariable($var)) {
            Write-Host "❌ Missing environment variable: $var" -ForegroundColor Red
            return $false
        }
    }
    
    # Check PowerShell modules
    $modules = @("ExchangeOnlineManagement", "Microsoft.Graph.Authentication")
    foreach ($module in $modules) {
        if (-not (Get-Module -ListAvailable -Name $module)) {
            Write-Host "❌ Missing PowerShell module: $module" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "✅ All pre-flight checks passed!" -ForegroundColor Green
    return $true
}
```

## Examples

### Basic Configuration (Single Tenant)

**Minimal configuration for testing:**
```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://contoso-admin.sharepoint.com"
  },
  "outputConfig": {
    "timestampedOutputs": true,
    "generateDashboard": true
  }
}
```

### Production Configuration (MSP/Multi-Tenant)

**Full-featured configuration for managed service providers:**
```json
{
  "tenants": [
    {
      "name": "Client A - Healthcare",
      "tenantId": "aaaaaaaa-1234-1234-1234-123456789abc",
      "spoAdminUrl": "https://clienta-admin.sharepoint.com",
      "controlsConfig": {
        "severityFilter": ["Critical", "High"],
        "includeDefender": true
      },
      "outputConfig": {
        "outputPath": "output/reports/client-a/",
        "uploadToSharePoint": true,
        "sharePointSiteUrl": "https://msp.sharepoint.com/sites/client-a"
      },
      "notificationConfig": {
        "enabled": true,
        "recipients": ["client-a-it@example.com"],
        "sendOnFailureOnly": true
      }
    },
    {
      "name": "Client B - Finance",
      "tenantId": "bbbbbbbb-1234-1234-1234-123456789abc",
      "spoAdminUrl": "https://clientb-admin.sharepoint.com",
      "controlsConfig": {
        "includeDefender": true,
        "includePurview": true,
        "customControls": ["SOX-001", "SOX-002"]
      },
      "outputConfig": {
        "outputPath": "output/reports/client-b/",
        "retentionDays": 2555,
        "compressArchive": true
      },
      "notificationConfig": {
        "enabled": true,
        "recipients": ["client-b-security@example.com", "compliance@clientb.com"],
        "includeDashboard": true
      }
    }
  ]
}
```

### CPA Firm Configuration (SOX/AICPA Compliance)

**Compliance-focused configuration for CPA audits:**
```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://cpafirm-admin.sharepoint.com",
    "tenantName": "CPA Firm - SOX Compliance Audit"
  },
  "controlsConfig": {
    "severityFilter": ["Critical", "High"],
    "includeAzureAD": true,
    "includeDefender": true,
    "includePurview": true,
    "customControls": ["SOX-302", "SOX-404", "AICPA-SOC2"]
  },
  "outputConfig": {
    "timestampedOutputs": true,
    "retentionDays": 2555,
    "exportFormats": ["json", "xlsx", "html"],
    "compressArchive": true,
    "dashboardPath": "output/reports/security/sox_compliance_dashboard.html"
  },
  "notificationConfig": {
    "enabled": true,
    "recipients": [
      "audit-team@cpafirm.com",
      "partner@cpafirm.com"
    ],
    "sendOnFailureOnly": false,
    "includeDashboard": true
  },
  "advancedConfig": {
    "verboseLogging": true,
    "cacheResults": false,
    "retryAttempts": 5
  }
}
```

## Cross-References

### Related Documentation

- **Parent README:** [`../README.md`](../README.md) - Project overview
- **Source Code Guide:** [`../src/README.md`](../src/README.md) - Module documentation
- **Scripts Documentation:** [`../scripts/README.md`](../scripts/README.md) - Script usage
- **PowerShell Guide:** [`../scripts/powershell/README.md`](../scripts/powershell/README.md) - PowerShell modules
- **Service Principal Setup:** [`../docs/M365_SERVICE_PRINCIPAL_SETUP.md`](../docs/M365_SERVICE_PRINCIPAL_SETUP.md) - Authentication configuration
- **AI Development Guide:** [`../.github/copilot-instructions.md`](../.github/copilot-instructions.md) - AI agent patterns

### External Resources

- **CIS Microsoft 365 Benchmark:** [CIS Benchmarks](https://www.cisecurity.org/benchmark/microsoft_365)
- **Azure Key Vault:** [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- **JSON Schema:** [JSON Schema Specification](https://json-schema.org/)
- **YAML Specification:** [YAML 1.2 Spec](https://yaml.org/spec/1.2/spec.html)

---

**🔐 Security Warning:** Never commit secrets (passwords, API keys, client secrets) to source control. Use environment variables, Azure Key Vault, or GitHub Secrets.

**✅ Validation Required:** Always validate configuration files before running audits. Use schema validation or the provided `Test-AuditConfiguration` function.

**🏢 CPA Compliance:** For SOX/AICPA compliance, set `retentionDays: 2555` (7 years) and enable `verboseLogging` for complete audit trails.
