# Security Alert Investigation & Remediation System

## Overview

The Security Alert Investigation & Remediation System is a comprehensive solution for collecting, investigating, remediating, and tracking security alerts across multiple sources in the Easy-Ai M365 Security Toolkit.

## Features

### 🔍 Multi-Source Alert Aggregation
- **Bandit** - Python code security scanner
- **Safety** - Python dependency vulnerability scanner
- **CodeQL** - Advanced code analysis (SARIF format)
- **M365 CIS** - Microsoft 365 security compliance audits

### 🔎 Intelligent Investigation
- Automatic severity normalization (1-10 scale)
- False positive detection using heuristics
- Evidence gathering and context collection
- Alert lifecycle tracking (new → investigating → remediated/escalated → closed)

### 🔧 Automated Remediation
- Safe auto-remediation for common issues
- WhatIf mode for preview before applying changes
- Integration with M365 CIS remediation scripts
- Escalation workflow for manual review

### 📊 Compliance Reporting
- Executive summary reports
- Detailed breakdowns by status, severity, and source
- Multiple export formats (JSON, HTML, Excel)
- Historical tracking and trend analysis

## Installation

The security alert system is included in the Easy-Ai toolkit. No additional installation required beyond the core dependencies:

```bash
pip install -r requirements.txt
```

For development and testing:
```bash
pip install -r requirements-dev.txt
```

## Quick Start

### 1. Collect Alerts

```bash
# Collect alerts from all available sources
python scripts/investigate_security_alerts.py --collect
```

This will:
- Scan for Bandit security reports
- Scan for Safety vulnerability reports
- Scan for M365 CIS audit failures
- Scan for CodeQL SARIF reports
- Save all alerts to `data/security/alerts.json`

### 2. Investigate Alerts

```bash
# List all new alerts
python scripts/investigate_security_alerts.py --list --status new

# Investigate a specific alert
python scripts/investigate_security_alerts.py --investigate --alert-id <alert-id>

# List by severity
python scripts/investigate_security_alerts.py --list --severity HIGH
```

### 3. Remediate Alerts

```bash
# Preview remediation (WhatIf mode)
python scripts/remediate_security_alerts.py --alert-id <alert-id> --whatif

# Apply remediation with confirmation
python scripts/remediate_security_alerts.py --alert-id <alert-id>

# Auto-remediate without confirmation (for CI/CD)
python scripts/remediate_security_alerts.py --alert-id <alert-id> --auto

# Escalate for manual review
python scripts/remediate_security_alerts.py --escalate --alert-id <alert-id> --escalation-reason "Requires security team review"
```

### 4. Generate Reports

```bash
# Generate all report formats
python scripts/generate_alert_summary.py

# Generate specific format
python scripts/generate_alert_summary.py --format html
python scripts/generate_alert_summary.py --format json
python scripts/generate_alert_summary.py --format excel
```

## Architecture

### Alert Database Structure

The alert database (`data/security/alerts.json`) tracks all alerts and their lifecycle:

```json
{
  "alerts": {
    "alert-id": {
      "id": "unique-alert-id",
      "source": "bandit|safety|m365_cis|codeql",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "normalized_severity": 1-10,
      "title": "Brief description",
      "description": "Detailed description",
      "status": "new|investigating|remediated|escalated|closed",
      "is_false_positive": true|false,
      "created": "ISO8601 timestamp",
      "last_seen": "ISO8601 timestamp",
      "file_path": "path/to/file.py",
      "line_number": 42,
      "evidence": "Additional evidence",
      "reference": "https://documentation-url",
      ...source-specific fields...
    }
  },
  "metadata": {
    "created": "ISO8601 timestamp",
    "last_updated": "ISO8601 timestamp",
    "version": "1.0"
  }
}
```

### Remediation Log Structure

The remediation log (`output/reports/security/remediation_log.json`) tracks all remediation actions:

```json
[
  {
    "timestamp": "ISO8601 timestamp",
    "alert_id": "alert-id",
    "action": "remediate|escalate|close",
    "result": "success|error|preview",
    "details": {
      ...action-specific details...
    }
  }
]
```

## Alert Sources

### Bandit (Python Security)

**What it detects:**
- Hardcoded passwords/secrets
- SQL injection vulnerabilities
- Unsafe deserialization
- Weak cryptography
- Command injection risks

**Sample alert:**
```python
{
  "id": "bandit-B101-42",
  "source": "bandit",
  "severity": "LOW",
  "title": "Use of assert detected",
  "file_path": "src/module.py",
  "line_number": 42,
  "code_snippet": "assert x == y",
  "cwe": "703",
  "confidence": "HIGH",
  "reference": "https://bandit.readthedocs.io/..."
}
```

**Auto-remediation:** Limited to LOW severity with HIGH confidence

### Safety (Python Dependencies)

**What it detects:**
- Known CVEs in Python packages
- Vulnerable package versions
- Security advisories

**Sample alert:**
```python
{
  "id": "safety-requests-12345",
  "source": "safety",
  "severity": "HIGH",
  "title": "Vulnerability in requests",
  "package": "requests",
  "installed_version": "2.25.1",
  "affected_versions": "<2.31.0",
  "cve": "CVE-2023-12345",
  "reference": "https://pyup.io/..."
}
```

**Auto-remediation:** Yes - package upgrades (with compatibility check recommended)

### M365 CIS (Microsoft 365 Compliance)

**What it detects:**
- CIS Benchmark failures
- Microsoft 365 misconfigurations
- Security policy violations

**Sample alert:**
```python
{
  "id": "m365-1.1.1",
  "source": "m365_cis",
  "severity": "HIGH",
  "title": "Ensure modern authentication is enabled",
  "control_id": "1.1.1",
  "expected": "Enabled",
  "actual": "Disabled",
  "evidence": "Legacy auth detected on 5 mailboxes",
  "reference": "https://docs.microsoft.com/..."
}
```

**Auto-remediation:** Selected safe controls only (delegates to `PostRemediateM365CIS.ps1`)

### CodeQL (Advanced Analysis)

**What it detects:**
- Code quality issues
- Security vulnerabilities
- Best practice violations

**Sample alert:**
```python
{
  "id": "codeql-sql-injection-main.py",
  "source": "codeql",
  "severity": "ERROR",
  "title": "SQL query built from user-controlled data",
  "file_path": "src/database.py",
  "line_number": 123,
  "rule_id": "py/sql-injection",
  "reference": "https://codeql.github.com/..."
}
```

**Auto-remediation:** No - requires code review

## False Positive Detection

The system applies heuristics to detect potential false positives:

### File Path Patterns
- Files in `/tests/` or `/test/` directories
- Files containing "example" or "documentation"
- Files in `__pycache__` or `.git/`
- Commented out code

### Custom Rules
Add custom false positive patterns in `investigate_security_alerts.py`:

```python
FALSE_POSITIVE_PATTERNS = [
    "test file",
    "example code",
    "documentation",
    # Add custom patterns here
]
```

## CI/CD Integration

### GitHub Actions Workflow

The system includes a comprehensive GitHub Actions workflow (`.github/workflows/security-alert-investigation.yml`) that:

1. **Collects** alerts daily at 2 AM UTC
2. **Investigates** all new alerts automatically
3. **Remediates** safe issues with approval gates
4. **Escalates** complex issues to security team
5. **Generates** compliance reports
6. **Notifies** on critical findings

**Trigger the workflow:**
```yaml
# Manual trigger with options
on:
  workflow_dispatch:
    inputs:
      auto_remediate: true
      severity_filter: HIGH
```

**Outputs:**
- `alerts-database` - Persistent alert tracking
- `security-reports` - Raw scanner outputs
- `remediation-log` - Action history
- `alert-summary-reports` - Compliance reports (JSON/HTML/Excel)

### Integration with Existing Workflows

The security alert system integrates with existing workflows:

```yaml
# Example: Add to security-scan.yml
- name: Collect and investigate alerts
  run: |
    python scripts/investigate_security_alerts.py --collect
    python scripts/investigate_security_alerts.py --summary
```

## Compliance Reporting

### Executive Summary

Provides high-level metrics for management:
- Total alerts investigated
- Remediation rate
- Open critical/high severity alerts
- Recommendations based on metrics

### Detailed Breakdown

Includes:
- Alerts by status (new, investigating, remediated, escalated, closed)
- Alerts by severity (critical, high, medium, low)
- Alerts by source (bandit, safety, m365_cis, codeql)

### Export Formats

#### JSON
Machine-readable format for integration:
```bash
python scripts/generate_alert_summary.py --format json
```

Output: `output/reports/security/alert_summary_YYYYMMDD_HHMMSS.json`

#### HTML
Interactive web dashboard:
```bash
python scripts/generate_alert_summary.py --format html
```

Output: `output/reports/security/alert_summary_YYYYMMDD_HHMMSS.html`

Features:
- Metric cards with color coding
- Severity-based highlighting
- Responsive design

#### Excel
Spreadsheet for offline analysis:
```bash
python scripts/generate_alert_summary.py --format excel
```

Output: `output/reports/security/alert_summary_YYYYMMDD_HHMMSS.xlsx`

Sheets:
- Summary - Key metrics
- Alerts - Full alert details

## Remediation Playbooks

### Safety Vulnerabilities

**Issue:** Outdated Python package with known CVE

**Remediation:**
1. Check package changelog for breaking changes
2. Test upgrade in development environment
3. Run full test suite
4. Apply upgrade:
   ```bash
   pip install --upgrade <package>
   pip freeze > requirements.txt
   ```
5. Commit changes and close alert

### M365 CIS Controls

**Issue:** Failed CIS control (e.g., 1.1.1 - Modern Auth)

**Remediation:**
1. Review M365 CIS documentation
2. Preview changes:
   ```powershell
   .\PostRemediateM365CIS.ps1 -Controls 1.1.1 -WhatIf
   ```
3. Apply remediation:
   ```powershell
   .\PostRemediateM365CIS.ps1 -Controls 1.1.1 -Force
   ```
4. Re-run audit to verify
5. Close alert

### Bandit Code Issues

**Issue:** Security vulnerability in Python code

**Remediation:**
1. Review Bandit documentation for the specific test ID
2. Analyze code context
3. Apply fix (varies by issue type)
4. Run Bandit again to verify
5. Run tests to ensure no breakage
6. Close alert

## Best Practices

### 1. Regular Collection
Run alert collection daily to stay current:
```bash
# Add to crontab or CI/CD
0 2 * * * python scripts/investigate_security_alerts.py --collect
```

### 2. Investigate Promptly
Review new alerts within 24 hours:
- Critical: Immediate action
- High: Within 24 hours
- Medium: Within 1 week
- Low: Within 1 month

### 3. Use WhatIf Mode
Always preview changes before applying:
```bash
python scripts/remediate_security_alerts.py --alert-id <id> --whatif
```

### 4. Document Escalations
Provide context when escalating:
```bash
python scripts/remediate_security_alerts.py --escalate \
  --alert-id <id> \
  --escalation-reason "Requires approval from security team"
```

### 5. Track Metrics
Monitor trends over time:
- Closure rate
- Time to remediation
- False positive rate

### 6. False Positive Tuning
If false positive rate exceeds 20%, review and tune detection rules.

## Troubleshooting

### No alerts collected

**Cause:** Security scanner reports not found

**Solution:**
```bash
# Verify reports exist
ls -la output/reports/security/

# Run scanners manually
bandit -r src/ -f json -o output/reports/security/bandit-report.json
safety check --file requirements.txt --output json > output/reports/security/safety-report.json
```

### Remediation fails

**Cause:** Insufficient permissions or M365 connection issues

**Solution:**
1. Check error message in remediation log
2. Verify M365 credentials
3. Ensure sufficient API permissions
4. Escalate if issue persists

### Reports not generating

**Cause:** Missing dependencies (pandas, openpyxl)

**Solution:**
```bash
pip install pandas openpyxl
```

## API Reference

### investigate_security_alerts.py

```python
# Collect all alerts
python scripts/investigate_security_alerts.py --collect

# Investigate specific alert
python scripts/investigate_security_alerts.py --investigate --alert-id <id>

# List alerts with filtering
python scripts/investigate_security_alerts.py --list [--status <status>] [--severity <severity>]

# Generate summary
python scripts/investigate_security_alerts.py --summary
```

### remediate_security_alerts.py

```python
# Remediate with confirmation
python scripts/remediate_security_alerts.py --alert-id <id>

# Auto-remediate (no confirmation)
python scripts/remediate_security_alerts.py --alert-id <id> --auto

# Preview only
python scripts/remediate_security_alerts.py --alert-id <id> --whatif

# Escalate
python scripts/remediate_security_alerts.py --escalate --alert-id <id> [--escalation-reason <reason>]

# Close
python scripts/remediate_security_alerts.py --close --alert-id <id> [--resolution <notes>]

# Generate report
python scripts/remediate_security_alerts.py --report
```

### generate_alert_summary.py

```python
# Generate all formats
python scripts/generate_alert_summary.py

# Specific format
python scripts/generate_alert_summary.py --format [json|html|excel]

# Custom paths
python scripts/generate_alert_summary.py \
  --alerts-db <path> \
  --remediation-log <path> \
  --output-dir <path>
```

## Security Considerations

### Sensitive Data
- Alerts database may contain sensitive information (file paths, package versions)
- Remediation logs track actions taken on production systems
- Escalation files may include evidence of vulnerabilities

**Recommendations:**
- Restrict access to `data/security/` and `output/reports/security/`
- Add to `.gitignore` if containing proprietary information
- Use encrypted storage for compliance reports
- Implement RBAC for alert management

### Auto-Remediation Risks
- Auto-remediation only applies to pre-approved safe changes
- WhatIf mode always runs first for safety
- M365 changes delegate to reviewed PowerShell scripts
- Code changes are never applied automatically (requires manual review)

**Safety Features:**
- Approval gates in CI/CD workflows
- Detailed audit logging
- Rollback capability for M365 changes
- Test environment validation recommended

## Contributing

To extend the security alert system:

1. **Add new alert source:**
   - Implement `collect_<source>_alerts()` in `investigate_security_alerts.py`
   - Follow the standardized alert format
   - Add tests in `test_security_alert_system.py`

2. **Add remediation logic:**
   - Implement `remediate_<source>_alert()` in `remediate_security_alerts.py`
   - Update `can_auto_remediate()` if applicable
   - Add safety checks and WhatIf support

3. **Enhance false positive detection:**
   - Add patterns to `FALSE_POSITIVE_PATTERNS`
   - Implement source-specific heuristics in `is_false_positive()`

## License

Part of the Easy-Ai M365 Security Toolkit.
See LICENSE file for details.

## Support

For issues or questions:
- GitHub Issues: https://github.com/Heyson315/Easy-Ai/issues
- Documentation: See README.md and COPILOT_INSTRUCTIONS.md
