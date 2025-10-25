# Microsoft 365 CIS Foundations Level 1 (v3.0) – Audit Toolkit

This repo includes a PowerShell-based audit for CIS Microsoft 365 Foundations v3.0 Level 1 controls. It connects to Microsoft 365 services, evaluates configurations, and produces JSON/CSV reports plus an interactive HTML dashboard.

**New in this version:** 15+ security controls (expanded from 9), Purview integration, safe remediation with -WhatIf, comparison reporting, automated scheduling, and interactive HTML dashboard.

Important: This toolkit provides technical checks and is not a substitute for a full compliance program. Always review results with your security and compliance teams.

## Prerequisites

- Windows PowerShell 5.1 or PowerShell 7+
- Modules installed (CurrentUser scope is fine):
  - ExchangeOnlineManagement (includes Security & Compliance cmdlets for Purview)
  - Microsoft.Graph (with Microsoft.Graph.DeviceManagement for Intune checks)
  - (Optional) Microsoft.Online.SharePoint.PowerShell (for SPO tenant checks)
- Appropriate admin roles/permissions:
  - Exchange Admin (EXO checks)
  - Global Reader / Security Reader (Graph queries)
  - SharePoint Admin (SPO tenant checks)
  - Compliance Administrator (Purview checks)
  - Intune Administrator (device compliance checks)

## Files

**Core Audit:**
- `scripts/powershell/modules/M365CIS.psm1` – audit functions (15+ controls)
- `scripts/powershell/Invoke-M365CISAudit.ps1` – orchestrator (connect + run + export)
- `config/benchmarks/cis_m365_foundations_v3_level1.json` – metadata for controls

**Remediation & Analysis:**
- `scripts/powershell/PostRemediateM365CIS.ps1` – safe remediation with -WhatIf support
- `scripts/powershell/Compare-M365CISResults.ps1` – compare before/after audit results

**Automation & Reporting:**
- `scripts/powershell/Setup-ScheduledAudit.ps1` – create scheduled task for automated audits
- `scripts/powershell/Remove-ScheduledAudit.ps1` – remove scheduled task
- `scripts/generate_security_dashboard.py` – generate interactive HTML dashboard
- `scripts/m365_cis_report.py` – builds Excel report from JSON output

**Configuration:**
- `config/audit_config.json` – centralized configuration template

**Output directory:** `output/reports/security/`

## Quick Start

### 1. Run Audit (read-only)

```powershell
# Basic audit
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\powershell\Invoke-M365CISAudit.ps1"

# Include SharePoint and Purview checks
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\powershell\Invoke-M365CISAudit.ps1" -SPOAdminUrl "https://<tenant>-admin.sharepoint.com"

# Generate timestamped outputs (recommended for tracking history)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\powershell\Invoke-M365CISAudit.ps1" -Timestamped

# Skip specific services if needed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\powershell\Invoke-M365CISAudit.ps1" -SkipPurview -SkipExchange
```

This generates:
- `output/reports/security/m365_cis_audit.json` (or timestamped version)
- `output/reports/security/m365_cis_audit.csv` (or timestamped version)

### 2. Generate Interactive Dashboard

```powershell
# Generate HTML dashboard from latest audit
python scripts/generate_security_dashboard.py

# Or specify a specific audit file
python scripts/generate_security_dashboard.py --input "output/reports/security/m365_cis_audit_20251025_120000.json"
```

Output: `output/reports/security/dashboard.html`

The dashboard includes:
- Summary cards (Pass/Fail/Manual counts, severity breakdown)
- Trend chart showing pass rate over time (if historical data exists)
- Filterable control status table
- Color-coded status indicators

### 3. Safe Remediation with -WhatIf

```powershell
# Preview changes without applying them
.\scripts\powershell\PostRemediateM365CIS.ps1 -WhatIf

# Apply remediations (with confirmation prompts)
.\scripts\powershell\PostRemediateM365CIS.ps1

# Apply remediations without prompts
.\scripts\powershell\PostRemediateM365CIS.ps1 -Force

# Include SharePoint remediation
.\scripts\powershell\PostRemediateM365CIS.ps1 -SPOAdminUrl "https://<tenant>-admin.sharepoint.com" -WhatIf
```

The script shows color-coded output:
- 🟡 Yellow = Preview (what would change)
- 🟢 Green = Successfully applied
- 🔴 Red = Errors

And provides a summary report at the end showing counts of successful/failed/skipped remediations.

### 4. Compare Before/After Results

```powershell
# Compare two audit runs to see improvements
.\scripts\powershell\Compare-M365CISResults.ps1 `
    -BeforeFile "output/reports/security/m365_cis_audit_before.json" `
    -AfterFile "output/reports/security/m365_cis_audit_after.json"

# Export comparison to CSV and HTML
.\scripts\powershell\Compare-M365CISResults.ps1 `
    -BeforeFile "before.json" `
    -AfterFile "after.json" `
    -OutputCsv "comparison.csv" `
    -OutputHtml "comparison.html"
```

The comparison shows:
- Statistics: Pass/Fail counts before and after, improvement percentage
- Status changes: Fail → Pass (improved), Pass → Fail (degraded)
- New controls added or removed
- Severity-based prioritization

### 5. Setup Automated Audits

```powershell
# Setup weekly audit (requires Administrator privileges)
.\scripts\powershell\Setup-ScheduledAudit.ps1 `
    -Schedule Weekly `
    -DayOfWeek Monday `
    -Time "09:00" `
    -SPOAdminUrl "https://<tenant>-admin.sharepoint.com"

# Setup daily audit
.\scripts\powershell\Setup-ScheduledAudit.ps1 `
    -Schedule Daily `
    -Time "06:00"

# Remove scheduled audit
.\scripts\powershell\Remove-ScheduledAudit.ps1 -Force
```

The scheduled task:
- Runs with SYSTEM privileges
- Generates timestamped outputs automatically
- Logs to `output/logs/scheduled_audit.log`
- Can be managed through Windows Task Scheduler

## Controls Included (15 Total)

**Exchange Online (EXO) - 4 controls:**
- CIS-EXO-1: Modern auth enabled and basic auth blocked (Auth Policies) - **High**
- CIS-EXO-2: External auto-forwarding disabled - **High**
- CIS-EXO-3: Mailbox auditing enabled (org-level) - **Medium**
- CIS-EXO-4: Legacy protocols disabled per mailbox (POP/IMAP/MAPI - sample check) - **Medium**

**SharePoint Online (SPO) - 1 control:**
- CIS-SPO-1: Restrict external sharing at the tenant level - **High**

**Azure AD/Entra ID - 3 controls:**
- CIS-AAD-1: Limit Global Administrator assignments - **High**
- CIS-AAD-2: Azure AD Identity Protection risk policies configured - **High** ⭐ NEW
- CIS-AAD-3: Guest user access restrictions configured - **Medium** ⭐ NEW

**Microsoft Defender for Office 365 - 2 controls:**
- CIS-DEF-1: Safe Links policy enabled - **High**
- CIS-DEF-2: Safe Attachments policy enabled - **High**

**Conditional Access - 1 control:**
- CIS-CA-1: MFA policy exists for all users - **High**

**Purview Compliance - 3 controls:** ⭐ NEW
- CIS-PURVIEW-1: DLP policies enabled for data protection - **High**
- CIS-PURVIEW-2: Audit logs retained for compliance (90+ days) - **Medium**
- CIS-PURVIEW-3: Sensitivity labels published and enforced - **Medium**

**Intune Mobile Device Management - 1 control:** ⭐ NEW
- CIS-INTUNE-1: Device compliance policies exist and are enforced - **Medium**

## Purview Integration

The toolkit now includes Purview compliance checks. The `Connect-PurviewCompliance` function attempts to connect to Security & Compliance PowerShell using `Connect-IPPSSession`.

**Prerequisites:**
- ExchangeOnlineManagement module installed
- Compliance Administrator or equivalent role
- Security & Compliance PowerShell access

**What happens if Purview is not available:**
- Purview controls will return Status='Manual' instead of failing
- The audit will continue with other checks
- You can skip Purview checks with `-SkipPurview` parameter

**To check Purview cmdlets manually:**
```powershell
# Test Purview connection
Connect-IPPSSession
Get-DlpCompliancePolicy
Get-UnifiedAuditLogRetentionPolicy
Get-LabelPolicy
```

## Build Excel summary (optional)

```powershell
# Use Python to convert JSON → Excel (auto-names Excel from JSON filename)
python scripts/m365_cis_report.py

# Or for a specific timestamped JSON
python scripts/m365_cis_report.py --input "output/reports/security/m365_cis_audit_20251025_073705.json"
```

It writes: `output/reports/security/m365_cis_audit.xlsx` (or timestamped equivalent)

## Versioning audit evidence

- Recommended to keep text-based evidence (JSON/CSV) under version control and exclude large Excel files to avoid repo bloat.
- This repo includes a `.gitignore` that:
  - Excludes `output/**` by default
  - Re-includes `output/reports/security/*.json` and `*.csv`
  - Keeps `*.xlsx` ignored (consider Git LFS if you need to track Excel)

Suggested commit flow:

```powershell
# Commit code/docs updates separately
git add scripts/powershell/modules/M365CIS.psm1 scripts/powershell/Invoke-M365CISAudit.ps1 docs/SECURITY_M365_CIS.md .gitignore
git commit -m "fix(security): M365 CIS audit improvements"

# Commit audit evidence (JSON/CSV)
git add output/reports/security/m365_cis_audit_YYYYMMDD_HHMMSS.json output/reports/security/m365_cis_audit_YYYYMMDD_HHMMSS.csv
git commit -m "chore(audit): add M365 CIS audit evidence YYYY-MM-DD HH:MM:SS"

# Optionally tag and push
git tag -a audit-YYYYMMDD-HHMMSS -m "M365 CIS audit evidence"
git push --follow-tags
```

## Configuration File

A template configuration file is provided at `config/audit_config.json`:

```json
{
  "tenantConfig": {
    "spoAdminUrl": "https://tenant-admin.sharepoint.com",
    "scheduleFrequency": "Weekly",
    "scheduleDay": "Monday",
    "scheduleTime": "09:00"
  },
  "notificationConfig": {
    "enabled": false,
    "smtpServer": "",
    "recipients": []
  },
  "controlsConfig": {
    "skipExchange": false,
    "skipGraph": false,
    "skipPurview": false,
    "includeIntune": true
  }
}
```

This configuration can be used as a reference for audit parameters. Update it with your tenant-specific values.

## Troubleshooting

### Connection Issues

**Problem:** "Not connected to Graph" or "Not connected to EXO"
- **Solution:** Run `Connect-MgGraph` or `Connect-ExchangeOnline` manually first to diagnose connection issues
- Check that required modules are installed: `Get-Module -ListAvailable`
- Verify you have appropriate admin roles in M365

**Problem:** "ExchangeOnlineManagement module not found"
- **Solution:** Install the module: `Install-Module ExchangeOnlineManagement -Scope CurrentUser`

**Problem:** SharePoint checks show "Manual" status
- **Solution:** Install SPO module and provide `-SPOAdminUrl` parameter:
  ```powershell
  Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
  ```

### Purview/Compliance Issues

**Problem:** Purview checks return Status='Manual'
- **Solution:** This is expected if:
  - Purview module is not available
  - You don't have Compliance Administrator role
  - You used `-SkipPurview` parameter
- To enable: Ensure ExchangeOnlineManagement is installed and run `Connect-IPPSSession`

**Problem:** "DLP cmdlets unavailable"
- **Solution:** Verify you have the correct permissions and licenses for Purview DLP
- Check your role assignments include Compliance Administrator

### Intune/Device Management Issues

**Problem:** "Intune cmdlets unavailable or insufficient permissions"
- **Solution:** Install the required Graph module:
  ```powershell
  Install-Module Microsoft.Graph.DeviceManagement -Scope CurrentUser
  ```
- Verify you have Intune Administrator or equivalent role

### Scheduled Task Issues

**Problem:** "This script must be run as Administrator"
- **Solution:** Right-click PowerShell and select "Run as Administrator"

**Problem:** Scheduled task runs but produces no output
- **Solution:** Check the log file at `output/logs/scheduled_audit.log`
- Verify the task is configured with correct working directory
- Test manually: `Start-ScheduledTask -TaskName "M365-CIS-Audit"`

### Dashboard Generation Issues

**Problem:** "No audit JSON files found"
- **Solution:** Run the audit first: `.\scripts\powershell\Invoke-M365CISAudit.ps1 -Timestamped`

**Problem:** Chart.js not loading in dashboard
- **Solution:** The dashboard requires internet connection to load Chart.js from CDN
- If you need offline support, download Chart.js and update the script reference

### Comparison Script Issues

**Problem:** "Failed to load audit files"
- **Solution:** Verify both JSON files exist and are valid JSON format
- Check file paths are correct (use absolute paths if needed)

**Problem:** Comparison shows no changes when changes were made
- **Solution:** Ensure you're comparing files from different times (before/after remediation)
- Check that control IDs match in both files

## Common Workflow Examples

### Initial Audit and Baseline

```powershell
# 1. Run initial audit
.\scripts\powershell\Invoke-M365CISAudit.ps1 -Timestamped -SPOAdminUrl "https://tenant-admin.sharepoint.com"

# 2. Generate dashboard
python scripts/generate_security_dashboard.py

# 3. Review results and document baseline
```

### Remediation and Validation

```powershell
# 1. Preview what changes would be made
.\scripts\powershell\PostRemediateM365CIS.ps1 -WhatIf

# 2. Apply remediations
.\scripts\powershell\PostRemediateM365CIS.ps1 -Force

# 3. Wait a few minutes, then run audit again
.\scripts\powershell\Invoke-M365CISAudit.ps1 -Timestamped -SPOAdminUrl "https://tenant-admin.sharepoint.com"

# 4. Compare results
.\scripts\powershell\Compare-M365CISResults.ps1 `
    -BeforeFile "output/reports/security/m365_cis_audit_20251025_090000.json" `
    -AfterFile "output/reports/security/m365_cis_audit_20251025_093000.json" `
    -OutputHtml "comparison_report.html"
```

### Automated Monitoring Setup

```powershell
# 1. Setup weekly automated audit
.\scripts\powershell\Setup-ScheduledAudit.ps1 `
    -Schedule Weekly `
    -DayOfWeek Monday `
    -Time "09:00" `
    -SPOAdminUrl "https://tenant-admin.sharepoint.com"

# 2. After first automated run, generate dashboard
python scripts/generate_security_dashboard.py

# 3. Schedule dashboard generation (optional - can add to scheduled task)
# Create a batch file or additional scheduled task to run the Python script
```

## GLBA note

GLBA is a legal and regulatory framework, not a technical benchmark. Many CIS controls support GLBA safeguards (e.g., access control, authentication, logging). Use this toolkit as a technical input into your GLBA compliance efforts, but coordinate with your legal/compliance teams for scoping, documentation, and risk management.

## Safety and change control

- The audit scripts are read-only by default (no changes made)
- Always use `-WhatIf` with remediation scripts before applying changes
- Test in a non-production tenant first if possible
- Review all changes before applying in production
- Keep audit evidence for compliance tracking
- Document all remediation activities

## Support and Contributions

For issues, feature requests, or contributions, please use the repository's issue tracker. When reporting issues, include:
- PowerShell version: `$PSVersionTable.PSVersion`
- Module versions: `Get-Module ExchangeOnlineManagement, Microsoft.Graph* -ListAvailable`
- Error messages and stack traces
- Redacted audit output showing the issue
