#!/usr/bin/env python3
"""
Example: Security Alert Investigation Workflow

Demonstrates a complete end-to-end workflow for investigating and
remediating M365 security alerts.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports (must be before src import)
sys.path.insert(0, str(Path(__file__).parent.parent))  # noqa: E402

from src.core.security_alert_manager import SecurityAlertManager  # noqa: E402


def main():
    """Run example security alert investigation workflow"""

    print("=" * 70)
    print("Security Alert Investigation Example")
    print("=" * 70)
    print()

    # Configuration
    audit_file = Path("output/reports/security/m365_cis_audit_20251111_121438.json")
    output_dir = Path("output/reports/security")

    # Verify audit file exists
    if not audit_file.exists():
        print(f"ERROR: Audit file not found: {audit_file}")
        print("Please run M365 CIS audit first:")
        print("  powershell.exe -File scripts/powershell/Invoke-M365CISAudit.ps1")
        return 1

    print(f"Audit file: {audit_file}")
    print(f"Output directory: {output_dir}")
    print()

    # Step 1: Initialize Security Alert Manager (dry-run mode)
    print("Step 1: Initializing Security Alert Manager (dry-run mode)")
    print("-" * 70)
    manager = SecurityAlertManager(
        audit_path=audit_file, output_dir=output_dir, dry_run=True  # Safe mode - no actual changes
    )
    print("✓ Manager initialized in dry-run mode")
    print()

    # Step 2: Collect alerts from audit results
    print("Step 2: Collecting security alerts from audit results")
    print("-" * 70)
    alert_count = manager.collect_alerts()
    print(f"✓ Collected {alert_count} security alerts")

    if alert_count == 0:
        print()
        print("No security alerts found. System is compliant!")
        return 0

    # Display collected alerts
    print()
    print("Collected Alerts:")
    for i, alert in enumerate(manager.alerts, 1):
        print(f"  {i}. [{alert.severity}] {alert.title}")
        print(f"     Control: {alert.control_id}")
        print(f"     Expected: {alert.expected}")
        print(f"     Actual: {alert.actual[:50]}...")
    print()

    # Step 3: Investigate and remediate all alerts
    print("Step 3: Investigating and remediating alerts")
    print("-" * 70)
    stats = manager.process_all_alerts()

    print(f"✓ Investigated: {stats['investigated']} alerts")
    print(f"✓ Remediated: {stats['remediated']} alerts")
    print(f"✓ Escalated: {stats['escalated']} alerts (require manual intervention)")
    print(f"✓ False Positives: {stats['false_positives']} alerts")
    print()

    # Step 4: Close resolved alerts
    print("Step 4: Closing resolved alerts")
    print("-" * 70)
    closed = manager.close_resolved_alerts()
    print(f"✓ Closed {closed} resolved alerts")
    print()

    # Step 5: Generate reports
    print("Step 5: Generating reports")
    print("-" * 70)

    # Remediation log
    log_path = manager.generate_remediation_log()
    print(f"✓ Remediation log: {log_path}")

    # Summary report
    summary_path = manager.generate_summary_report()
    print(f"✓ Summary report: {summary_path}")
    print()

    # Display summary statistics
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    with open(summary_path) as f:
        summary = json.load(f)

    stats = summary["statistics"]
    print(f"Total Alerts: {stats['total_alerts']}")
    print(f"Remediated: {stats['remediated']}")
    print(f"Escalated: {stats['escalated']}")
    print(f"False Positives: {stats['false_positives']}")
    print(f"Closed: {stats['closed']}")
    print()

    # Breakdown by severity
    print("By Severity:")
    for severity, counts in stats["by_severity"].items():
        print(
            f"  {severity}: {counts['total']} total, "
            f"{counts['remediated']} remediated, "
            f"{counts['escalated']} escalated"
        )
    print()

    # Show escalations requiring manual intervention
    if summary["pending_escalations"]:
        print("Pending Escalations (require manual intervention):")
        for esc in summary["pending_escalations"]:
            print(f"  • [{esc['severity']}] {esc['title']}")
            print(f"    Control: {esc['control_id']}")
            print(f"    Next steps:")
            for step in esc["next_steps"][:3]:  # Show first 3 steps
                print(f"      - {step}")
        print()

    # Dry-run notice
    if manager.dry_run:
        print("=" * 70)
        print("⚠️  DRY RUN MODE")
        print("=" * 70)
        print("No actual remediations were applied.")
        print("To apply changes, run with --apply-remediation flag:")
        print()
        print("  python -m src.core.security_alert_manager \\")
        print(f"    --audit-file {audit_file} \\")
        print("    --apply-remediation")
        print()

    print("✓ Investigation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
