# Security Alert Investigation and Remediation

## Quick Reference

This document provides a quick reference for the Security Alert Investigation and Remediation System.

## One-Liner Commands

```bash
# Investigate alerts from audit (dry-run mode - safe)
python -m src.core.security_alert_manager --audit-file output/reports/security/m365_cis_audit.json

# Apply actual remediations (CAUTION - modifies environment)
python -m src.core.security_alert_manager --audit-file output/reports/security/m365_cis_audit.json --apply-remediation

# Run example workflow
python scripts/example_security_alert_workflow.py

# Collect alerts from M365 Security Center
powershell.exe -File scripts/powershell/Collect-M365SecurityAlerts.ps1 -Severity High -Status Active
```

## Common Tasks

### Investigate Latest Audit

```bash
# Find latest audit file
LATEST=$(ls -t output/reports/security/m365_cis_audit_*.json | head -1)

# Investigate alerts
python -m src.core.security_alert_manager --audit-file "$LATEST" --verbose
```

### View Summary Report

```bash
# Generate and view summary
python -m src.core.security_alert_manager --audit-file output/reports/security/m365_cis_audit.json
cat output/reports/security/security_alert_summary_*.json | python -m json.tool | less
```

### Check for Escalations

```bash
# Extract escalation count from summary
jq '.statistics.escalated' output/reports/security/security_alert_summary_*.json
```

### Generate Reports Only

```python
from pathlib import Path
from src.core.security_alert_manager import SecurityAlertManager

manager = SecurityAlertManager(
    audit_path=Path("output/reports/security/m365_cis_audit.json"),
    output_dir=Path("output/reports/security"),
    dry_run=True
)

# Load existing investigation data
manager.collect_alerts()
manager.process_all_alerts()

# Generate fresh reports
log_path = manager.generate_remediation_log()
summary_path = manager.generate_summary_report()

print(f"Reports generated: {log_path}, {summary_path}")
```

## Alert Statuses

| Status | Description |
|--------|-------------|
| `open` | Alert collected, not yet investigated |
| `investigating` | Investigation in progress |
| `remediated` | Fix successfully applied |
| `escalated` | Requires manual intervention |
| `false_positive` | Not a real security issue |
| `closed` | Resolved (remediated or false positive) |

## Remediation Actions

| Action | Description |
|--------|-------------|
| `update_policy` | Modify security policies |
| `revoke_credentials` | Revoke compromised credentials |
| `isolate_endpoint` | Isolate affected systems |
| `patch_vulnerability` | Apply security patches |
| `disable_account` | Disable compromised accounts |
| `block_ip` | Block malicious IP addresses |
| `manual_review` | Escalate for manual intervention |

## Safety Checklist

Before applying remediations:

- [ ] Tested in dry-run mode
- [ ] Reviewed escalated alerts
- [ ] Verified remediation actions
- [ ] Have rollback plan ready
- [ ] Notified stakeholders
- [ ] Scheduled during maintenance window
- [ ] Created backup/snapshot

## Output Files

| File | Description |
|------|-------------|
| `remediation_log_*.json` | Detailed log of all actions |
| `security_alert_summary_*.json` | High-level compliance summary |
| `m365_security_alerts.json` | Alerts from M365 Security Center |

## For More Information

- **Full Documentation**: [SECURITY_ALERT_INVESTIGATION.md](SECURITY_ALERT_INVESTIGATION.md)
- **API Reference**: [SECURITY_ALERT_INVESTIGATION.md#api-reference](SECURITY_ALERT_INVESTIGATION.md#api-reference)
- **Integration Examples**: [SECURITY_ALERT_INVESTIGATION.md#integration-examples](SECURITY_ALERT_INVESTIGATION.md#integration-examples)
- **Troubleshooting**: [SECURITY_ALERT_INVESTIGATION.md#troubleshooting](SECURITY_ALERT_INVESTIGATION.md#troubleshooting)
