# Security Alert Investigation and Remediation System

## Overview

The Security Alert Investigation and Remediation System is a comprehensive solution for managing M365 security alerts throughout their lifecycle: collection, investigation, remediation, and reporting.

## Features

- **Automated Alert Collection**: Collects security alerts from M365 CIS audit results
- **Intelligent Investigation**: Validates severity, detects false positives, gathers context
- **Safe Remediation**: Applies fixes with dry-run mode and rollback support
- **Escalation Workflow**: Generates detailed escalation reports with full context
- **Comprehensive Reporting**: Produces remediation logs and compliance summaries
- **M365 Integration**: PowerShell script for Microsoft 365 Security Center integration

## Quick Start

### Basic Usage

```bash
# Run investigation on audit results (dry-run mode)
python -m src.core.security_alert_manager \
    --audit-file output/reports/security/m365_cis_audit.json

# Apply actual remediations
python -m src.core.security_alert_manager \
    --audit-file output/reports/security/m365_cis_audit.json \
    --apply-remediation

# Collect alerts from M365 Security Center
powershell.exe -NoProfile -ExecutionPolicy Bypass \
    -File scripts/powershell/Collect-M365SecurityAlerts.ps1 \
    -Severity High -Status Active -DaysBack 7
```

## Architecture

### Alert Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                   Alert Lifecycle                            │
│                                                              │
│  1. Collection    2. Investigation   3. Remediation         │
│     ↓                  ↓                  ↓                  │
│  Audit Data  →  Validate  →  Apply Fix / Escalate           │
│                  Severity                                    │
│                  Detect FP                                   │
│                                                              │
│  4. Reporting     5. Closure                                │
│     ↓                  ↓                                     │
│  Generate  →  Update Tickets                                │
│  Logs/Summary   Close Resolved                              │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **SecurityAlertManager** - Core alert lifecycle management
2. **Alert Collection** - Converts CIS audit failures to security alerts
3. **Investigation Engine** - Validates alerts, detects false positives
4. **Remediation Engine** - Applies fixes with safety controls
5. **Reporting System** - Generates detailed logs and summaries

## Alert Collection

### From M365 CIS Audit Results

The system treats failed CIS controls as security alerts:

```python
from src.core.security_alert_manager import SecurityAlertManager

manager = SecurityAlertManager(
    audit_path="output/reports/security/m365_cis_audit.json",
    output_dir="output/reports/security",
    dry_run=True
)

# Collect alerts from audit
alert_count = manager.collect_alerts()
print(f"Found {alert_count} security alerts")
```

### From M365 Security Center

Use the PowerShell script to collect alerts:

```powershell
# Collect high-severity active alerts from last 7 days
.\scripts\powershell\Collect-M365SecurityAlerts.ps1 `
    -Severity High `
    -Status Active `
    -DaysBack 7 `
    -OutputPath "output/reports/security/m365_security_alerts.json"
```

## Investigation Workflow

### Automatic Investigation

Each alert is automatically investigated:

```python
# Investigate all collected alerts
stats = manager.process_all_alerts()

print(f"Investigated: {stats['investigated']}")
print(f"False Positives: {stats['false_positives']}")
print(f"Escalated: {stats['escalated']}")
```

### False Positive Detection

The system automatically detects common false positive patterns:

- "Not connected" - Service not available during audit
- "Module not found" - Missing PowerShell modules
- "Manual review required" - Controls requiring manual verification
- "Unknown configuration" - Unable to determine status

### Investigation Report

For each alert, the system generates:

- **Severity validation** - Confirms alert severity is correct
- **Source information** - Identifies the control/source
- **Log collection** - Gathers relevant audit logs
- **Endpoint data** - Lists affected systems (when available)
- **User activity** - Tracks user actions (when available)
- **Recommended action** - Suggests remediation approach

## Remediation

### Remediation Actions

The system supports multiple remediation types:

- **UPDATE_POLICY** - Modify security policies
- **REVOKE_CREDENTIALS** - Revoke compromised credentials
- **ISOLATE_ENDPOINT** - Isolate affected systems
- **PATCH_VULNERABILITY** - Apply security patches
- **DISABLE_ACCOUNT** - Disable compromised accounts
- **BLOCK_IP** - Block malicious IP addresses
- **MANUAL_REVIEW** - Escalate for manual intervention

### Dry-Run Mode (Default)

By default, the system runs in dry-run mode:

```python
# Dry-run mode (safe, no changes applied)
manager = SecurityAlertManager(
    audit_path="audit.json",
    output_dir="reports",
    dry_run=True  # Default
)
```

All remediation results include `dry_run=True` flag and are logged but not applied.

### Apply Remediations

To apply actual remediations:

```bash
python -m src.core.security_alert_manager \
    --audit-file output/reports/security/m365_cis_audit.json \
    --apply-remediation
```

⚠️ **WARNING**: This will apply actual changes to your M365 environment. Always test in a non-production environment first.

### Remediation Safety

The system includes multiple safety controls:

1. **Dry-run mode by default** - Must explicitly enable remediation
2. **Action logging** - All actions are logged with timestamps
3. **Rollback support** - Remediations can be reversed
4. **Escalation for critical items** - High-risk items require manual review
5. **Audit trail** - Full history of all remediation attempts

## Escalation Workflow

### Automatic Escalation

Alerts are escalated when:

- Remediation requires manual intervention
- Alert severity is Critical
- Recommended action is MANUAL_REVIEW
- Remediation attempt fails

### Escalation Report

Each escalated alert includes:

```json
{
  "alert_id": "ALERT-CIS-AAD-1-20251211042420",
  "control_id": "CIS-AAD-1",
  "title": "Limit Global Administrator role assignments",
  "severity": "Critical",
  "evidence": "Found 8 users with Global Administrator role",
  "investigation_summary": {
    "logs": [...],
    "recommended_action": "manual_review"
  },
  "remediation_details": "Requires manual review - escalating to security team",
  "next_steps": [
    "Review control CIS-AAD-1: Limit Global Administrator role assignments",
    "Verify current configuration: 8 Global Administrators found",
    "Implement recommended configuration: Maximum 5 Global Administrators",
    "Reference: CIS M365 Foundations v3.0 L1",
    "Validate changes in test environment before production",
    "Update security documentation with changes made"
  ]
}
```

## Reporting

### Remediation Log

Detailed log of all actions:

```python
log_path = manager.generate_remediation_log()
# Output: output/reports/security/remediation_log_20251211_042420.json
```

Contains:

- All alerts with full details
- Investigation results for each alert
- Remediation actions taken
- Timestamps and audit trail

### Summary Report

High-level compliance summary:

```python
summary_path = manager.generate_summary_report()
# Output: output/reports/security/security_alert_summary_20251211_042420.json
```

Contains:

- **Statistics**: Total, remediated, escalated, false positives
- **By Severity**: Breakdown of alerts by severity level
- **Actions Taken**: List of successful remediations
- **Pending Escalations**: Alerts requiring manual intervention

### Sample Summary Report

```json
{
  "report_date": "2025-12-11T04:24:20.917536",
  "dry_run_mode": true,
  "statistics": {
    "total_alerts": 15,
    "remediated": 8,
    "escalated": 5,
    "false_positives": 2,
    "closed": 10,
    "by_severity": {
      "Critical": {"total": 3, "remediated": 1, "escalated": 2},
      "High": {"total": 8, "remediated": 5, "escalated": 3},
      "Medium": {"total": 4, "remediated": 2, "escalated": 0}
    }
  },
  "actions_taken": [...],
  "pending_escalations": [...]
}
```

## Integration Examples

### Automated Workflow

Complete end-to-end workflow:

```bash
#!/bin/bash

# 1. Run M365 CIS audit
powershell.exe -NoProfile -ExecutionPolicy Bypass \
    -File scripts/powershell/Invoke-M365CISAudit.ps1 -Timestamped

# 2. Process alerts (dry-run first)
python -m src.core.security_alert_manager \
    --audit-file output/reports/security/m365_cis_audit.json \
    --output-dir output/reports/security

# 3. Review results
cat output/reports/security/security_alert_summary_*.json | python -m json.tool

# 4. Apply remediations if safe
python -m src.core.security_alert_manager \
    --audit-file output/reports/security/m365_cis_audit.json \
    --apply-remediation
```

### GitHub Actions Integration

```yaml
name: Security Alert Investigation

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  investigate-alerts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run M365 Audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
      
      - name: Investigate Alerts
        run: |
          python -m src.core.security_alert_manager \
            --audit-file output/reports/security/m365_cis_audit.json \
            --output-dir output/reports/security \
            --verbose
      
      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: output/reports/security/
          retention-days: 90
      
      - name: Check Escalations
        run: |
          escalations=$(jq '.statistics.escalated' output/reports/security/security_alert_summary_*.json)
          if [ "$escalations" -gt 0 ]; then
            echo "::warning::$escalations alerts require manual intervention"
          fi
```

### Ticketing System Integration

Example integration with ServiceNow:

```python
import json
import requests
from src.core.security_alert_manager import SecurityAlertManager

# Run investigation
manager = SecurityAlertManager(
    audit_path="audit.json",
    output_dir="reports",
    dry_run=False
)

manager.collect_alerts()
manager.process_all_alerts()
summary_path = manager.generate_summary_report()

# Create tickets for escalated alerts
with open(summary_path) as f:
    summary = json.load(f)

for escalation in summary['pending_escalations']:
    # Create ServiceNow incident
    incident = {
        'short_description': f"Security Alert: {escalation['title']}",
        'description': f"""
Alert ID: {escalation['alert_id']}
Severity: {escalation['severity']}
Evidence: {escalation['evidence']}

Next Steps:
{chr(10).join(f'- {step}' for step in escalation['next_steps'])}
        """,
        'urgency': '1' if escalation['severity'] == 'Critical' else '2',
        'category': 'Security',
        'assignment_group': 'Security Operations'
    }
    
    # Submit to ServiceNow (example)
    # response = requests.post(
    #     'https://your-instance.service-now.com/api/now/table/incident',
    #     auth=('username', 'password'),
    #     json=incident
    # )
```

## API Reference

### SecurityAlertManager

Main class for alert lifecycle management.

#### Constructor

```python
SecurityAlertManager(
    audit_path: Path,
    output_dir: Path,
    dry_run: bool = True
)
```

**Parameters:**
- `audit_path` - Path to M365 CIS audit JSON file
- `output_dir` - Directory for output reports
- `dry_run` - If True, don't apply actual remediations (default: True)

#### Methods

##### collect_alerts()

Collect security alerts from M365 CIS audit results.

**Returns:** `int` - Number of alerts collected

```python
alert_count = manager.collect_alerts()
```

##### investigate_alert(alert)

Investigate a single security alert.

**Parameters:**
- `alert` - SecurityAlert object to investigate

**Returns:** `InvestigationReport` - Investigation findings

```python
investigation = manager.investigate_alert(alert)
```

##### apply_remediation(alert, investigation)

Apply remediation for a security alert.

**Parameters:**
- `alert` - SecurityAlert object
- `investigation` - InvestigationReport from investigation

**Returns:** `RemediationResult` - Remediation outcome

```python
result = manager.apply_remediation(alert, investigation)
```

##### process_all_alerts()

Process all collected alerts: investigate and remediate.

**Returns:** `dict` - Summary statistics

```python
stats = manager.process_all_alerts()
# {
#   'total_alerts': 10,
#   'investigated': 10,
#   'remediated': 6,
#   'escalated': 3,
#   'false_positives': 1
# }
```

##### close_resolved_alerts()

Close alerts that have been remediated or identified as false positives.

**Returns:** `int` - Number of alerts closed

```python
closed_count = manager.close_resolved_alerts()
```

##### generate_remediation_log()

Generate detailed remediation log.

**Returns:** `Path` - Path to the remediation log file

```python
log_path = manager.generate_remediation_log()
```

##### generate_summary_report()

Generate summary report for compliance and security.

**Returns:** `Path` - Path to the summary report file

```python
summary_path = manager.generate_summary_report()
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/test_security_alert_manager.py -v

# Run specific test class
pytest tests/test_security_alert_manager.py::TestSecurityAlertCollection -v

# Run with coverage
pytest tests/test_security_alert_manager.py --cov=src.core.security_alert_manager
```

Test coverage: 69% of security_alert_manager.py
All 21 tests passing

## Troubleshooting

### No Alerts Collected

If no alerts are collected:

1. Verify audit file exists and is valid JSON
2. Check that audit contains failed controls (Status='Fail')
3. Ensure audit file path is correct

```bash
# Verify audit file
cat output/reports/security/m365_cis_audit.json | python -m json.tool
```

### Remediations Not Applied

If remediations aren't being applied:

1. Check that dry-run mode is disabled (`--apply-remediation`)
2. Verify remediation action is not MANUAL_REVIEW
3. Check remediation log for error details

### PowerShell Script Fails

If PowerShell script fails:

1. Install required module:
   ```powershell
   Install-Module Microsoft.Graph.Security -Scope CurrentUser
   ```

2. Verify permissions: `SecurityEvents.Read.All`

3. Check tenant connection

## Best Practices

1. **Always test in dry-run mode first**
2. **Review escalations before applying remediations**
3. **Keep audit trails for compliance**
4. **Regular testing of remediation procedures**
5. **Document all manual remediations**
6. **Schedule regular alert investigations**
7. **Monitor false positive rate**
8. **Update remediation logic based on learnings**

## Security Considerations

- Store credentials securely (use Key Vault or environment variables)
- Limit permissions to minimum required
- Enable audit logging for all remediation actions
- Review escalated alerts promptly
- Test remediations in non-production first
- Maintain rollback procedures
- Regular security reviews of remediation logic

## Future Enhancements

- [ ] Machine learning for false positive detection
- [ ] Integration with SIEM systems (Sentinel, Splunk)
- [ ] Automated rollback on failed remediation
- [ ] Real-time alert monitoring
- [ ] Custom remediation workflows
- [ ] Advanced analytics and trending
- [ ] Integration with Microsoft Defender
- [ ] Automated incident response playbooks

## Support

For issues or questions:

- GitHub Issues: https://github.com/Heyson315/Easy-Ai/issues
- Documentation: See README.md and ARCHITECTURE.md
- Security: See SECURITY.md
