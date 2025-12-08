# Output Directory

## Overview

The `output/` directory contains all generated reports, dashboards, and audit artifacts from M365 security audits. This directory is organized by report type and follows data retention policies for compliance with SOX/AICPA requirements.

**Directory Purpose:**
- Centralized location for all audit outputs
- Organized by report type (security vs. business)
- Supports automatic cleanup and archival
- Enables historical tracking and trending

## Directory Structure

```
output/
├── reports/                       # All generated reports
│   ├── security/                  # Security audit reports
│   │   ├── m365_cis_audit_YYYYMMDD_HHMMSS.json      # Detailed audit results
│   │   ├── m365_cis_audit_YYYYMMDD_HHMMSS.csv       # Tabular audit results
│   │   ├── m365_cis_audit_YYYYMMDD_HHMMSS.xlsx      # Excel report with formatting
│   │   ├── dashboard_YYYYMMDD_HHMMSS.html           # Interactive HTML dashboard
│   │   └── audit_summary.json                        # Latest audit summary
│   └── business/                  # Business-facing reports
│       ├── sharepoint_permissions_YYYYMMDD.xlsx     # SharePoint access reports
│       ├── user_activity_YYYYMMDD.xlsx              # User activity analysis
│       └── compliance_summary_YYYYMMDD.xlsx         # Executive compliance summary
├── logs/                          # Execution logs
│   ├── audit_YYYYMMDD_HHMMSS.log                   # PowerShell transcript logs
│   ├── scheduled_audit.log                          # Scheduled task logs
│   └── archive/                                     # Archived logs (90+ days)
└── archive/                       # Archived reports
    └── YYYY/                      # Year-based organization
        └── MM/                    # Month-based organization
            └── reports_YYYYMMDD.zip                # Compressed historical reports
```

## Report Formats

### JSON Reports (`*.json`)

**Purpose:** Machine-readable audit results for automation and integration.

**Structure:**
```json
{
  "metadata": {
    "auditDate": "2025-12-07T14:30:00Z",
    "tenantId": "12345678-1234-1234-1234-123456789abc",
    "tenantName": "Contoso Corporation",
    "auditVersion": "2.0",
    "controlsExecuted": 15,
    "executionTimeSeconds": 247
  },
  "summary": {
    "totalControls": 15,
    "passed": 10,
    "failed": 3,
    "manual": 2,
    "complianceScore": 66.67
  },
  "results": [
    {
      "controlId": "1.1.1",
      "title": "Ensure modern authentication is enabled",
      "status": "Pass",
      "severity": "High",
      "expected": "Modern authentication enabled",
      "actual": "OAuth2ClientProfileEnabled = True",
      "evidence": "Configuration verified on 2025-12-07",
      "reference": "https://docs.microsoft.com/...",
      "timestamp": "2025-12-07T14:32:15Z"
    }
  ]
}
```

**Use cases:**
- CI/CD pipeline integration
- Historical trending analysis
- Automated alerting systems
- Data lake ingestion

### CSV Reports (`*.csv`)

**Purpose:** Tabular data for Excel analysis and reporting.

**Format:**
```csv
ControlId,Title,Status,Severity,Expected,Actual,Evidence,Reference,Timestamp
1.1.1,Ensure modern authentication is enabled,Pass,High,Modern auth enabled,OAuth2ClientProfileEnabled = True,Configuration verified,https://docs.microsoft.com/...,2025-12-07T14:32:15Z
1.1.3,Ensure basic auth is disabled,Fail,High,Basic auth disabled,Basic auth still enabled,Found 3 protocols with basic auth,https://docs.microsoft.com/...,2025-12-07T14:33:20Z
```

**Use cases:**
- Quick Excel pivot tables
- Custom reporting templates
- Data analysis with pandas
- Import into Power BI

### Excel Reports (`*.xlsx`)

**Purpose:** Professionally formatted reports for stakeholders.

**Worksheets:**
1. **Executive Summary**
   - Compliance score gauge chart
   - Pass/Fail/Manual counts
   - Critical findings highlight
   - Trend comparison (if available)

2. **Detailed Results**
   - All control results
   - Color-coded status (Green/Red/Yellow)
   - Sortable/filterable table
   - Evidence and references

3. **Failed Controls**
   - Only failed controls for focus
   - Remediation recommendations
   - Severity prioritization

4. **Compliance Trends**
   - Historical compliance scores
   - Chart showing improvement over time
   - Month-over-month comparison

**Use cases:**
- Board presentations
- Client deliverables
- Audit documentation
- Compliance reporting

### HTML Dashboards (`*.html`)

**Purpose:** Interactive web-based security dashboard.

**Features:**
- Summary cards (Pass/Fail/Manual counts)
- Compliance score gauge
- Historical trend chart (Chart.js)
- Filterable control table
- Drill-down details
- Export to PDF functionality
- Mobile-responsive design

**Access:**
```bash
# Open in browser
start output/reports/security/dashboard_20251207_143000.html

# Or serve via Python
python -m http.server 8000 --directory output/reports/security/
# Navigate to: http://localhost:8000/dashboard_20251207_143000.html
```

**Use cases:**
- Real-time monitoring
- Security team dashboards
- Stakeholder demos
- SharePoint embedding

## Artifact Management

### Timestamped Outputs

**Enable timestamping:**
```powershell
# PowerShell audit
.\Invoke-M365CISAudit.ps1 -Timestamped -SPOAdminUrl "https://contoso-admin.sharepoint.com"
```

**Configuration:**
```json
{
  "outputConfig": {
    "timestampedOutputs": true
  }
}
```

**Benefits:**
- Preserve historical audits
- Track changes over time
- Prevent accidental overwrites
- Enable before/after comparisons

**Naming convention:**
- Format: `<type>_YYYYMMDD_HHMMSS.<ext>`
- Example: `m365_cis_audit_20251207_143000.json`
- Timezone: UTC

### Latest Outputs

**Symlinks to latest reports:**
```
output/reports/security/
├── audit_latest.json -> m365_cis_audit_20251207_143000.json
├── audit_latest.csv -> m365_cis_audit_20251207_143000.csv
├── audit_latest.xlsx -> m365_cis_audit_20251207_143000.xlsx
└── dashboard_latest.html -> dashboard_20251207_143000.html
```

**Usage:**
```bash
# Always get latest report
python scripts/analyze_audit.py --input output/reports/security/audit_latest.json
```

### File Size Considerations

**Typical file sizes:**
- JSON: 50-200 KB (15-50 controls)
- CSV: 10-50 KB
- Excel: 100-500 KB (with formatting/charts)
- HTML: 200-800 KB (includes Chart.js embedded)
- Logs: 50-500 KB per audit

**Large tenant considerations:**
- JSON files can reach 1-5 MB for 100+ controls
- SharePoint reports can be 5-50 MB for 10,000+ users
- Consider compression for archival

## Data Retention

### Retention Policies

**Default retention:**
```json
{
  "outputConfig": {
    "retentionDays": 90
  }
}
```

**CPA/SOX compliance:**
```json
{
  "outputConfig": {
    "retentionDays": 2555  // 7 years
  }
}
```

**Retention by file type:**
- **Security audit reports:** 7 years (SOX requirement)
- **Business reports:** 3 years (typical)
- **Execution logs:** 90 days
- **HTML dashboards:** 30 days (regeneratable from JSON)

### Cleanup Automation

**PowerShell cleanup script:**
```powershell
# scripts/powershell/Cleanup-OldReports.ps1
param(
    [int]$RetentionDays = 90,
    [switch]$WhatIf
)

$cutoffDate = (Get-Date).AddDays(-$RetentionDays)
$reportsPath = "output/reports/security"

Get-ChildItem $reportsPath -Recurse -File | 
    Where-Object { 
        $_.LastWriteTime -lt $cutoffDate -and 
        $_.Name -notmatch "audit_latest"  # Don't delete symlinks
    } | 
    ForEach-Object {
        if ($WhatIf) {
            Write-Host "Would delete: $($_.FullName)" -ForegroundColor Yellow
        } else {
            Write-Host "Deleting: $($_.FullName)" -ForegroundColor Red
            Remove-Item $_.FullName -Force
        }
    }
```

**Usage:**
```powershell
# Preview deletion (safe)
.\Cleanup-OldReports.ps1 -RetentionDays 90 -WhatIf

# Delete old reports
.\Cleanup-OldReports.ps1 -RetentionDays 90
```

**Scheduled cleanup:**
```powershell
# Create scheduled task to run weekly
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File 'C:\path\to\Cleanup-OldReports.ps1' -RetentionDays 90"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am

Register-ScheduledTask -TaskName "M365-Audit-Cleanup" `
    -Action $action `
    -Trigger $trigger `
    -Description "Clean up old M365 audit reports"
```

## Archive Strategies

### Manual Archival

**Compress old reports:**
```powershell
# Archive reports older than 90 days
$archiveDate = (Get-Date).AddDays(-90)
$archivePath = "output/archive/$(Get-Date -Format 'yyyy/MM')"

New-Item -ItemType Directory -Path $archivePath -Force

Get-ChildItem "output/reports/security" -File | 
    Where-Object { $_.LastWriteTime -lt $archiveDate } |
    Compress-Archive -DestinationPath "$archivePath/reports_$(Get-Date -Format 'yyyyMMdd').zip"
```

### Automated Archival

**Configuration:**
```json
{
  "outputConfig": {
    "retentionDays": 90,
    "compressArchive": true,
    "archivePath": "output/archive/{year}/{month}/"
  }
}
```

**GitHub Actions workflow:**
```yaml
name: Archive Old Reports

on:
  schedule:
    - cron: '0 3 * * 0'  # Weekly on Sunday at 3 AM

jobs:
  archive:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Archive old reports
        shell: pwsh
        run: |
          $archiveDate = (Get-Date).AddDays(-90)
          $archivePath = "output/archive/$(Get-Date -Format 'yyyy/MM')"
          
          New-Item -ItemType Directory -Path $archivePath -Force
          
          Get-ChildItem "output/reports" -Recurse -File |
            Where-Object { $_.LastWriteTime -lt $archiveDate } |
            Compress-Archive -DestinationPath "$archivePath/archive_$(Get-Date -Format 'yyyyMMdd').zip"
      
      - name: Upload archived reports
        uses: actions/upload-artifact@v4
        with:
          name: archived-reports
          path: output/archive/
          retention-days: 365
```

### Cloud Backup

**Azure Blob Storage:**
```powershell
# Install Azure PowerShell module
Install-Module -Name Az.Storage -Scope CurrentUser

# Upload to Azure Blob
Connect-AzAccount
$storageAccount = Get-AzStorageAccount -ResourceGroupName "RG" -Name "StorageAccount"
$ctx = $storageAccount.Context

Get-ChildItem "output/reports/security" -File |
    Where-Object { $_.Name -match "\.json$" } |
    ForEach-Object {
        Set-AzStorageBlobContent -File $_.FullName `
            -Container "audit-reports" `
            -Blob "$(Get-Date -Format 'yyyy/MM')/$($_.Name)" `
            -Context $ctx `
            -Force
    }
```

**SharePoint:**
```json
{
  "outputConfig": {
    "uploadToSharePoint": true,
    "sharePointSiteUrl": "https://contoso.sharepoint.com/sites/AuditReports",
    "sharePointFolder": "M365 Security Audits"
  }
}
```

## Compliance Considerations

### SOX Compliance

**Requirements:**
- **Retention:** 7 years (2555 days)
- **Immutability:** Once written, reports should not be modified
- **Audit trail:** Log all access to reports
- **Access control:** Restrict access to authorized personnel

**Implementation:**
```json
{
  "outputConfig": {
    "retentionDays": 2555,
    "immutableReports": true,
    "logAccess": true,
    "encryptAtRest": true
  }
}
```

### AICPA Standards

**Requirements:**
- **Documentation:** Complete audit trails
- **Availability:** Reports accessible for review
- **Accuracy:** Timestamped and version-controlled
- **Security:** Encrypted and access-controlled

### Data Privacy (GDPR/CCPA)

**PII in reports:**
- User principal names (emails)
- Display names
- IP addresses (in logs)

**Compliance measures:**
```powershell
# Redact PII in reports
function Redact-PIIInReport {
    param([string]$JsonPath)
    
    $report = Get-Content $JsonPath | ConvertFrom-Json
    
    # Redact email addresses
    $report.results | ForEach-Object {
        if ($_.evidence -match '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b') {
            $_.evidence = $_.evidence -replace '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.com'
        }
    }
    
    $report | ConvertTo-Json -Depth 10 | Set-Content "$JsonPath.redacted"
}
```

## Cleanup Scripts

### Basic Cleanup

```powershell
# Clean reports older than 90 days
$retentionDays = 90
$cutoffDate = (Get-Date).AddDays(-$retentionDays)

Get-ChildItem "output/reports" -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $cutoffDate } |
    Remove-Item -Force -Verbose
```

### Selective Cleanup

```powershell
# Keep JSON, delete HTML/CSV
Get-ChildItem "output/reports" -Recurse -File |
    Where-Object { 
        $_.LastWriteTime -lt (Get-Date).AddDays(-30) -and
        $_.Extension -in @('.html', '.csv')
    } |
    Remove-Item -Force -Verbose
```

### Archive and Cleanup

```powershell
# Archive then cleanup
$archiveDate = (Get-Date).AddDays(-90)
$archiveName = "reports_$(Get-Date -Format 'yyyyMMdd').zip"
$archivePath = "output/archive/$(Get-Date -Format 'yyyy/MM')"

# Create archive directory
New-Item -ItemType Directory -Path $archivePath -Force

# Compress old files
$oldFiles = Get-ChildItem "output/reports" -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $archiveDate }

if ($oldFiles) {
    $oldFiles | Compress-Archive -DestinationPath "$archivePath/$archiveName" -Force
    $oldFiles | Remove-Item -Force
    Write-Host "Archived $($oldFiles.Count) files to $archivePath/$archiveName"
}
```

## Best Practices

**DO:**
- ✅ Enable timestamped outputs for historical tracking
- ✅ Implement automated cleanup based on retention policy
- ✅ Archive reports to cloud storage for disaster recovery
- ✅ Encrypt sensitive reports at rest
- ✅ Log all report access for audit trails
- ✅ Use JSON as source of truth (regenerate Excel/HTML as needed)

**DON'T:**
- ❌ Manually edit JSON reports (breaks integrity)
- ❌ Delete reports without archiving first
- ❌ Share reports via email (use secure links)
- ❌ Store reports on personal drives
- ❌ Ignore retention policies for compliance

## Cross-References

### Related Documentation

- **Parent README:** [`../README.md`](../README.md) - Project overview
- **Configuration Guide:** [`../config/README.md`](../config/README.md) - Output configuration
- **Scripts Documentation:** [`../scripts/README.md`](../scripts/README.md) - Report generation scripts
- **Data Processing:** [`../data/README.md`](../data/README.md) - Data workflow

### External Resources

- **SOX Compliance:** [Sarbanes-Oxley Act](https://www.sox-online.com/)
- **AICPA Standards:** [AICPA Trust Services](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/trustdataintegritytaskforce.html)
- **GDPR:** [GDPR Data Protection](https://gdpr.eu/)
- **Azure Blob Storage:** [Azure Storage Documentation](https://docs.microsoft.com/en-us/azure/storage/)

---

**🔐 Compliance Required:** For CPA firms and SOX compliance, set retention to 7 years (2555 days) and enable encryption and access logging.

**📊 Report Hierarchy:** JSON is source of truth → CSV for analysis → Excel for stakeholders → HTML for dashboards

**🗄️ Archive Strategy:** Compress reports older than 90 days, upload to cloud storage, maintain 7-year retention for compliance.
