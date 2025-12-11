#!/usr/bin/env python3
"""
demo_security_alert_system.py

Demonstration of the Security Alert Investigation & Remediation System.
Creates sample security reports and shows the complete workflow.

Usage:
    python scripts/demo_security_alert_system.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from investigate_security_alerts import SecurityAlertInvestigator
from remediate_security_alerts import SecurityAlertRemediator
from generate_alert_summary import AlertSummaryGenerator


def create_sample_reports(reports_dir: Path):
    """
    Create sample security reports for demonstration.

    Args:
        reports_dir: Directory to create reports in
    """
    print("📝 Creating sample security reports...")

    # Sample Bandit report
    bandit_report = {
        "results": [
            {
                "test_id": "B101",
                "issue_severity": "LOW",
                "issue_confidence": "HIGH",
                "issue_text": "Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.",
                "filename": "src/utils.py",
                "line_number": 42,
                "code": "assert user is not None, 'User cannot be None'",
                "issue_cwe": {"id": "703"},
            },
            {
                "test_id": "B608",
                "issue_severity": "MEDIUM",
                "issue_confidence": "HIGH",
                "issue_text": "Possible SQL injection vector through string-based query construction.",
                "filename": "src/database.py",
                "line_number": 156,
                "code": "query = f'SELECT * FROM users WHERE id = {user_id}'",
                "issue_cwe": {"id": "89"},
            },
        ]
    }

    with open(reports_dir / "bandit-report.json", "w") as f:
        json.dump(bandit_report, f, indent=2)
    print("  ✅ Created Bandit report (2 issues)")

    # Sample Safety report
    safety_report = {
        "vulnerabilities": [
            {
                "package_name": "requests",
                "vulnerability_id": "51668",
                "installed_version": "2.25.1",
                "affected_versions": "<2.31.0",
                "advisory": "The urllib3 library used by Requests has a security vulnerability related to CRLF injection in the HTTP request path, which could allow an attacker to inject arbitrary HTTP headers via a crafted URL.",
                "cve": "CVE-2023-32681",
                "more_info_url": "https://pyup.io/v/51668/f17",
            }
        ]
    }

    with open(reports_dir / "safety-report.json", "w") as f:
        json.dump(safety_report, f, indent=2)
    print("  ✅ Created Safety report (1 vulnerability)")

    # Sample M365 CIS report
    m365_report = [
        {
            "ControlId": "1.1.1",
            "Title": "Ensure modern authentication for Exchange Online is enabled",
            "Severity": "HIGH",
            "Status": "Fail",
            "Expected": "Enabled",
            "Actual": "Disabled on 5 mailboxes",
            "Evidence": "Legacy authentication detected on user@domain.com, admin@domain.com, and 3 others",
            "Reference": "https://docs.microsoft.com/en-us/microsoft-365/enterprise/modern-auth-for-office-2013-and-2016",
            "Timestamp": datetime.utcnow().isoformat(),
        },
        {
            "ControlId": "2.1.3",
            "Title": "Ensure SharePoint external sharing is restricted",
            "Severity": "CRITICAL",
            "Status": "Fail",
            "Expected": "New and existing guests",
            "Actual": "Anyone",
            "Evidence": "SharePoint tenant allows sharing with anyone (including anonymous links)",
            "Reference": "https://docs.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off",
            "Timestamp": datetime.utcnow().isoformat(),
        },
    ]

    with open(reports_dir / "m365_cis_audit.json", "w") as f:
        json.dump(m365_report, f, indent=2)
    print("  ✅ Created M365 CIS report (2 failed controls)")
    print()


def demo_workflow():
    """Demonstrate the complete security alert workflow."""
    print("=" * 70)
    print("🛡️  Security Alert Investigation & Remediation System Demo")
    print("=" * 70)
    print()

    with TemporaryDirectory() as td:
        temp_dir = Path(td)
        reports_dir = temp_dir / "reports"
        reports_dir.mkdir()

        alerts_db_path = temp_dir / "alerts.json"
        remediation_log_path = temp_dir / "remediation_log.json"

        # Step 1: Create sample reports
        create_sample_reports(reports_dir)

        # Step 2: Collect alerts
        print("🔍 STEP 1: Collecting Security Alerts")
        print("-" * 70)
        investigator = SecurityAlertInvestigator(alerts_db_path, reports_dir)
        new_count = investigator.collect_all_alerts()
        print()

        # Step 3: List and investigate alerts
        print("🔎 STEP 2: Investigating Alerts")
        print("-" * 70)

        # List all alerts
        all_alerts = investigator.list_alerts()
        print(f"Found {len(all_alerts)} total alerts:\n")

        for i, alert in enumerate(all_alerts[:3], 1):  # Show first 3
            print(f"{i}. {alert['id']}")
            print(f"   Source: {alert['source']:15} | Severity: {alert['severity']:8}")
            print(f"   Title: {alert['title'][:60]}")
            print()

        # Investigate first alert
        if all_alerts:
            first_alert = all_alerts[0]
            print(f"📋 Detailed investigation of alert: {first_alert['id']}")
            print("-" * 70)
            investigator.investigate_alert(first_alert["id"])
            print()

        # Step 4: Remediation
        print("🔧 STEP 3: Remediating Alerts")
        print("-" * 70)
        remediator = SecurityAlertRemediator(alerts_db_path, remediation_log_path)

        # Check which alerts can be auto-remediated
        investigating_alerts = investigator.list_alerts(status_filter="investigating")
        print(f"Alerts under investigation: {len(investigating_alerts)}\n")

        for alert in investigating_alerts[:2]:  # Process first 2
            alert_id = alert["id"]
            can_auto = remediator.can_auto_remediate(alert)

            print(f"Alert: {alert_id}")
            print(f"  Can auto-remediate: {'✅ Yes' if can_auto else '❌ No (requires manual review)'}")

            if can_auto:
                print("  Action: Attempting auto-remediation...")
                # In demo, we just escalate to show the workflow
                remediator.escalate_alert(alert_id, "Demo: Would auto-remediate in production")
            else:
                print("  Action: Escalating to security team...")
                remediator.escalate_alert(alert_id, "Requires manual code review")
            print()

        # Step 5: Generate summary report
        print("📊 STEP 4: Generating Summary Report")
        print("-" * 70)
        generator = AlertSummaryGenerator(alerts_db_path, remediation_log_path)

        stats = generator.calculate_statistics()
        print(generator.generate_executive_summary(stats))
        print(generator.generate_detailed_breakdown(stats))

        # Export reports
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        json_path = output_dir / "summary.json"
        html_path = output_dir / "summary.html"

        generator.export_json(json_path)
        generator.export_html(html_path)
        print()

        # Step 6: Show file locations
        print("📁 STEP 5: Generated Files")
        print("-" * 70)
        print(f"Alerts Database:    {alerts_db_path}")
        print(f"Remediation Log:    {remediation_log_path}")
        print(f"Summary (JSON):     {json_path}")
        print(f"Summary (HTML):     {html_path}")
        print()

        # Show sample of alerts database
        print("📄 Sample of Alerts Database:")
        print("-" * 70)
        with open(alerts_db_path) as f:
            db = json.load(f)
            print(f"Total alerts: {len(db['alerts'])}")
            print(f"Last updated: {db['metadata']['last_updated']}")

            # Show one alert
            if db["alerts"]:
                sample_alert = next(iter(db["alerts"].values()))
                print(f"\nSample alert:")
                print(f"  ID: {sample_alert['id']}")
                print(f"  Source: {sample_alert['source']}")
                print(f"  Severity: {sample_alert['severity']}")
                print(f"  Status: {sample_alert['status']}")
                print(f"  Title: {sample_alert['title'][:60]}")
        print()

        print("=" * 70)
        print("✅ Demo Complete!")
        print("=" * 70)
        print()
        print("Next Steps:")
        print("1. Run with real security reports:")
        print("   python scripts/investigate_security_alerts.py --collect")
        print()
        print("2. View the HTML summary report:")
        print("   open output/reports/security/alert_summary_*.html")
        print()
        print("3. Set up automated CI/CD workflow:")
        print("   See .github/workflows/security-alert-investigation.yml")
        print()
        print("4. Read the documentation:")
        print("   docs/SECURITY_ALERT_SYSTEM.md")
        print()


if __name__ == "__main__":
    demo_workflow()
