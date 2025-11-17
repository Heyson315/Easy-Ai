# M365 CIS Security Toolkit - Scripts

This directory contains PowerShell and Python scripts for Microsoft 365 CIS security auditing, remediation, and reporting.

## PowerShell Scripts

### Audit Scripts
- **`Invoke-M365CISAudit.ps1`** - Main audit orchestrator
  - Connects to M365 services (Exchange, Graph, SharePoint, Purview)
  - Runs 15 CIS security controls
  - Outputs JSON and CSV results
  - Usage: `.\Invoke-M365CISAudit.ps1 -Timestamped -SPOAdminUrl "https://tenant-admin.sharepoint.com"`

### Remediation Scripts
- **`PostRemediateM365CIS.ps1`** - Safe remediation with -WhatIf support
  - Fixes common CIS control failures
  - Supports `-WhatIf` for preview mode
  - Color-coded output with summary report
  - Usage: `.\PostRemediateM365CIS.ps1 -WhatIf` (preview), `.\PostRemediateM365CIS.ps1 -Force` (apply)

### Analysis Scripts
- **`Compare-M365CISResults.ps1`** - Compare before/after audit results
  - Shows status changes (Fail→Pass, Pass→Fail)
  - Calculates improvement percentage
  - Exports to CSV and HTML
  - Usage: `.\Compare-M365CISResults.ps1 -BeforeFile before.json -AfterFile after.json -OutputHtml comparison.html`

### Automation Scripts
- **`Setup-ScheduledAudit.ps1`** - Create Windows scheduled task for automated audits
  - Supports Daily/Weekly/Monthly schedules
  - Runs with highest privileges
  - Logs to `output/logs/scheduled_audit.log`
  - Usage: `.\Setup-ScheduledAudit.ps1 -Schedule Weekly -DayOfWeek Monday -Time "09:00"` (requires Administrator)

- **`Remove-ScheduledAudit.ps1`** - Remove scheduled audit task
  - Usage: `.\Remove-ScheduledAudit.ps1 -Force` (requires Administrator)

### Modules
- **`modules/M365CIS.psm1`** - Core audit functions
  - 15 security control test functions
  - Connection helpers for M365 services
  - Purview integration with graceful fallback

## Python Scripts

### Reporting Scripts
- **`generate_security_dashboard.py`** - Generate interactive HTML dashboard
  - Summary cards with Pass/Fail counts
  - Trend chart for historical pass rate
  - Filterable control status table
  - Usage: `python scripts/generate_security_dashboard.py --input audit.json --output dashboard.html`

- **`m365_cis_report.py`** - Generate Excel report from JSON
  - Converts audit JSON to formatted Excel workbook
  - Usage: `python scripts/m365_cis_report.py --input audit.json`

### Utility Scripts
- **`clean_csv.py`** - CSV cleanup utilities
- **`sync_cis_csv.py`** - Sync CIS data with CSV
- **`inspect_*.py`** - Various inspection utilities

## Quick Start Workflow

### 1. Initial Audit
```powershell
.\scripts\powershell\Invoke-M365CISAudit.ps1 -Timestamped -SPOAdminUrl "https://tenant-admin.sharepoint.com"
```

### 2. Generate Dashboard
```bash
python scripts/generate_security_dashboard.py
```

### 3. Preview Remediation
```powershell
.\scripts\powershell\PostRemediateM365CIS.ps1 -WhatIf
```

### 4. Apply Remediation
```powershell
.\scripts\powershell\PostRemediateM365CIS.ps1 -Force
```

### 5. Re-audit and Compare
```powershell
# Run audit again
.\scripts\powershell\Invoke-M365CISAudit.ps1 -Timestamped

# Compare results
.\scripts\powershell\Compare-M365CISResults.ps1 `
    -BeforeFile "output/reports/security/m365_cis_audit_20251025_100000.json" `
    -AfterFile "output/reports/security/m365_cis_audit_20251025_110000.json" `
    -OutputHtml "improvement_report.html"
```

### 6. Setup Automation
```powershell
# Run as Administrator
.\scripts\powershell\Setup-ScheduledAudit.ps1 `
    -Schedule Weekly `
    -DayOfWeek Monday `
    -Time "09:00" `
    -SPOAdminUrl "https://tenant-admin.sharepoint.com"
```

## Prerequisites

### PowerShell Modules
```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser
Install-Module Microsoft.Graph -Scope CurrentUser
Install-Module Microsoft.Graph.DeviceManagement -Scope CurrentUser
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
```

### Python Packages
No external packages required! All scripts use Python standard library only.

## Documentation

For detailed documentation, see:
- `docs/SECURITY_M365_CIS.md` - Complete guide with troubleshooting
- `config/audit_config.json` - Configuration template
- `config/benchmarks/cis_m365_foundations_v3_level1.json` - Control metadata

## Support

For issues or questions:
1. Check the troubleshooting section in `docs/SECURITY_M365_CIS.md`
2. Review script help: `Get-Help .\script.ps1 -Full`
3. Check execution logs in `output/logs/`
