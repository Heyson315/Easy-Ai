#!/usr/bin/env python3
"""
investigate_security_alerts.py

Comprehensive security alert investigation and triage system.
Aggregates alerts from multiple sources (Bandit, Safety, CodeQL, M365 CIS),
validates severity, gathers evidence, and prepares for remediation or escalation.

Features:
- Multi-source alert aggregation (Bandit, Safety, CodeQL SARIF, M365 CIS audits)
- Severity validation and normalization
- False positive detection heuristics
- Evidence gathering and context collection
- Alert lifecycle tracking (new, investigating, remediated, escalated, closed)
- Compliance-ready reporting

Usage:
    python scripts/investigate_security_alerts.py --collect
    python scripts/investigate_security_alerts.py --investigate --alert-id <id>
    python scripts/investigate_security_alerts.py --summary
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SecurityAlertInvestigator:
    """Main class for investigating security alerts across the environment."""

    # Severity mapping for normalization
    SEVERITY_MAP = {
        "CRITICAL": 10,
        "HIGH": 8,
        "MEDIUM": 5,
        "LOW": 2,
        "INFO": 1,
        "WARNING": 3,
        "ERROR": 9,
    }

    # False positive patterns (expandable)
    FALSE_POSITIVE_PATTERNS = [
        "test file",
        "example code",
        "documentation",
        "commented out",
        "__pycache__",
        ".git/",
    ]

    def __init__(self, alerts_db_path: Path, reports_dir: Path):
        """
        Initialize the investigator.

        Args:
            alerts_db_path: Path to alerts tracking database (JSON)
            reports_dir: Directory containing security reports
        """
        self.alerts_db_path = alerts_db_path
        self.reports_dir = reports_dir
        self.alerts_db: Dict[str, Any] = self._load_alerts_db()

    def _load_alerts_db(self) -> Dict[str, Any]:
        """Load or initialize the alerts tracking database."""
        if self.alerts_db_path.exists():
            with open(self.alerts_db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "alerts": {},
                "metadata": {
                    "created": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                    "version": "1.0",
                },
            }

    def _save_alerts_db(self):
        """Save the alerts database to disk."""
        self.alerts_db["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self.alerts_db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.alerts_db_path, "w", encoding="utf-8") as f:
            json.dump(self.alerts_db, f, indent=2, default=str)
        print(f"✅ Alerts database saved to {self.alerts_db_path}")

    def normalize_severity(self, severity: str) -> int:
        """
        Normalize severity to numeric scale (1-10).

        Args:
            severity: Original severity string

        Returns:
            Numeric severity (1-10)
        """
        severity_upper = severity.upper()
        return self.SEVERITY_MAP.get(severity_upper, 1)

    def is_false_positive(self, alert: Dict[str, Any]) -> bool:
        """
        Apply heuristics to detect false positives.

        Args:
            alert: Alert dictionary

        Returns:
            True if likely false positive
        """
        # Check file path patterns
        file_path = alert.get("file_path", "").lower()
        for pattern in self.FALSE_POSITIVE_PATTERNS:
            if pattern in file_path:
                return True

        # Check if in test directory
        if "/tests/" in file_path or "/test/" in file_path:
            return True

        # Additional heuristics can be added here
        return False

    def collect_bandit_alerts(self) -> List[Dict[str, Any]]:
        """
        Collect alerts from Bandit security scanner.

        Returns:
            List of standardized alert dictionaries
        """
        bandit_report = self.reports_dir / "bandit-report.json"
        if not bandit_report.exists():
            print(f"⚠️  Bandit report not found: {bandit_report}")
            return []

        with open(bandit_report, "r", encoding="utf-8") as f:
            data = json.load(f)

        alerts = []
        for result in data.get("results", []):
            alert = {
                "id": f"bandit-{result.get('test_id')}-{result.get('line_number')}",
                "source": "bandit",
                "severity": result.get("issue_severity", "MEDIUM"),
                "title": result.get("issue_text", "Unknown issue"),
                "description": result.get("issue_text", ""),
                "file_path": result.get("filename", ""),
                "line_number": result.get("line_number", 0),
                "code_snippet": result.get("code", ""),
                "cwe": result.get("issue_cwe", {}).get("id", ""),
                "confidence": result.get("issue_confidence", "MEDIUM"),
                "reference": f"https://bandit.readthedocs.io/en/latest/plugins/{result.get('test_id', '')}.html",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "new",
            }
            alerts.append(alert)

        print(f"✅ Collected {len(alerts)} alerts from Bandit")
        return alerts

    def collect_safety_alerts(self) -> List[Dict[str, Any]]:
        """
        Collect alerts from Safety dependency scanner.

        Returns:
            List of standardized alert dictionaries
        """
        safety_report = self.reports_dir / "safety-report.json"
        if not safety_report.exists():
            print(f"⚠️  Safety report not found: {safety_report}")
            return []

        try:
            with open(safety_report, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️  Invalid JSON in Safety report: {safety_report}")
            return []

        alerts = []
        vulnerabilities = data.get("vulnerabilities", [])
        if not isinstance(vulnerabilities, list):
            # Handle alternative format
            vulnerabilities = data if isinstance(data, list) else []

        for vuln in vulnerabilities:
            # Handle different Safety output formats
            package = vuln.get("package_name") or vuln.get("package") or "unknown"
            vuln_id = vuln.get("vulnerability_id") or vuln.get("id") or "unknown"

            alert = {
                "id": f"safety-{package}-{vuln_id}",
                "source": "safety",
                "severity": "HIGH",  # Safety vulnerabilities are generally high severity
                "title": f"Vulnerability in {package}",
                "description": vuln.get("advisory") or vuln.get("description", "No description"),
                "package": package,
                "installed_version": vuln.get("installed_version") or vuln.get("version", "unknown"),
                "affected_versions": vuln.get("affected_versions") or vuln.get("specs", []),
                "cve": vuln.get("cve") or "",
                "reference": vuln.get("more_info_url") or "",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "new",
            }
            alerts.append(alert)

        print(f"✅ Collected {len(alerts)} alerts from Safety")
        return alerts

    def collect_m365_cis_alerts(self) -> List[Dict[str, Any]]:
        """
        Collect failed controls from M365 CIS audits.

        Returns:
            List of standardized alert dictionaries
        """
        # Look for latest M365 CIS audit
        cis_reports = sorted(self.reports_dir.glob("m365_cis_audit*.json"), reverse=True)
        if not cis_reports:
            print(f"⚠️  No M365 CIS audit reports found in {self.reports_dir}")
            return []

        latest_report = cis_reports[0]
        print(f"📋 Using M365 CIS report: {latest_report.name}")

        with open(latest_report, "r", encoding="utf-8") as f:
            data = json.load(f)

        alerts = []
        for control in data:
            if control.get("Status") == "Fail":
                severity = control.get("Severity", "MEDIUM")
                alert = {
                    "id": f"m365-{control.get('ControlId', 'unknown')}",
                    "source": "m365_cis",
                    "severity": severity,
                    "title": control.get("Title", "Unknown control"),
                    "description": f"CIS Control {control.get('ControlId')}: {control.get('Title')}",
                    "control_id": control.get("ControlId", ""),
                    "expected": control.get("Expected", ""),
                    "actual": control.get("Actual", ""),
                    "evidence": control.get("Evidence", ""),
                    "reference": control.get("Reference", ""),
                    "timestamp": control.get("Timestamp", datetime.utcnow().isoformat()),
                    "status": "new",
                }
                alerts.append(alert)

        print(f"✅ Collected {len(alerts)} failed controls from M365 CIS audit")
        return alerts

    def collect_codeql_alerts(self) -> List[Dict[str, Any]]:
        """
        Collect alerts from CodeQL SARIF reports.

        Returns:
            List of standardized alert dictionaries
        """
        sarif_report = self.reports_dir / "codeql-results.sarif"
        if not sarif_report.exists():
            print(f"⚠️  CodeQL SARIF report not found: {sarif_report}")
            return []

        with open(sarif_report, "r", encoding="utf-8") as f:
            data = json.load(f)

        alerts = []
        for run in data.get("runs", []):
            for result in run.get("results", []):
                rule_id = result.get("ruleId", "unknown")
                location = result.get("locations", [{}])[0]
                physical_location = location.get("physicalLocation", {})
                artifact_location = physical_location.get("artifactLocation", {})

                alert = {
                    "id": f"codeql-{rule_id}-{artifact_location.get('uri', 'unknown')}",
                    "source": "codeql",
                    "severity": result.get("level", "warning").upper(),
                    "title": result.get("message", {}).get("text", "Unknown issue"),
                    "description": result.get("message", {}).get("text", ""),
                    "file_path": artifact_location.get("uri", ""),
                    "line_number": physical_location.get("region", {}).get("startLine", 0),
                    "rule_id": rule_id,
                    "reference": result.get("help", {}).get("text", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "new",
                }
                alerts.append(alert)

        print(f"✅ Collected {len(alerts)} alerts from CodeQL")
        return alerts

    def collect_all_alerts(self) -> int:
        """
        Collect alerts from all available sources.

        Returns:
            Total number of new alerts collected
        """
        print("\n🔍 Collecting security alerts from all sources...")
        print("=" * 70)

        all_alerts = []
        all_alerts.extend(self.collect_bandit_alerts())
        all_alerts.extend(self.collect_safety_alerts())
        all_alerts.extend(self.collect_m365_cis_alerts())
        all_alerts.extend(self.collect_codeql_alerts())

        # Add alerts to database
        new_count = 0
        updated_count = 0

        for alert in all_alerts:
            alert_id = alert["id"]

            # Check if alert already exists
            if alert_id in self.alerts_db["alerts"]:
                # Update if status is not closed
                existing = self.alerts_db["alerts"][alert_id]
                if existing.get("status") != "closed":
                    existing["last_seen"] = datetime.utcnow().isoformat()
                    updated_count += 1
            else:
                # Add new alert
                alert["created"] = datetime.utcnow().isoformat()
                alert["last_seen"] = datetime.utcnow().isoformat()
                alert["normalized_severity"] = self.normalize_severity(alert["severity"])
                alert["is_false_positive"] = self.is_false_positive(alert)
                self.alerts_db["alerts"][alert_id] = alert
                new_count += 1

        self._save_alerts_db()

        print("\n" + "=" * 70)
        print(f"📊 Summary:")
        print(f"   - New alerts: {new_count}")
        print(f"   - Updated alerts: {updated_count}")
        print(f"   - Total alerts in database: {len(self.alerts_db['alerts'])}")

        return new_count

    def investigate_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Investigate a specific alert in detail.

        Args:
            alert_id: Alert identifier

        Returns:
            Investigation results dictionary
        """
        if alert_id not in self.alerts_db["alerts"]:
            print(f"❌ Alert {alert_id} not found in database")
            return {"status": "error", "message": "Alert not found"}

        alert = self.alerts_db["alerts"][alert_id]
        print(f"\n🔍 Investigating Alert: {alert_id}")
        print("=" * 70)

        # Display alert details
        print(f"Source:      {alert['source']}")
        print(f"Severity:    {alert['severity']} (normalized: {alert.get('normalized_severity', 'N/A')}/10)")
        print(f"Title:       {alert['title']}")
        print(f"Description: {alert['description'][:100]}...")
        print(f"Status:      {alert['status']}")
        print(f"Created:     {alert.get('created', 'N/A')}")
        print(f"Last Seen:   {alert.get('last_seen', 'N/A')}")

        # Check for false positive
        if alert.get("is_false_positive"):
            print("\n⚠️  POTENTIAL FALSE POSITIVE detected")
            print("    This alert may be a false positive based on file path patterns.")

        # Gather additional context based on source
        context = self._gather_context(alert)

        # Update status to investigating
        alert["status"] = "investigating"
        alert["investigation_started"] = datetime.utcnow().isoformat()
        self._save_alerts_db()

        print("\n✅ Investigation complete. Alert status updated to 'investigating'")
        print("=" * 70)

        return {
            "status": "success",
            "alert": alert,
            "context": context,
        }

    def _gather_context(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather additional context for an alert.

        Args:
            alert: Alert dictionary

        Returns:
            Context dictionary with logs, related files, etc.
        """
        context = {
            "logs": [],
            "related_files": [],
            "recommendations": [],
        }

        # Source-specific context gathering
        if alert["source"] == "bandit":
            context["recommendations"].append("Review code snippet for security vulnerabilities")
            context["recommendations"].append(f"Check CWE-{alert.get('cwe', 'N/A')} for details")

        elif alert["source"] == "safety":
            context["recommendations"].append(f"Update {alert.get('package', 'package')} to safe version")
            context["recommendations"].append("Run 'pip install --upgrade <package>' after verifying compatibility")

        elif alert["source"] == "m365_cis":
            context["recommendations"].append("Review M365 tenant configuration")
            context["recommendations"].append(f"Expected: {alert.get('expected', 'N/A')}")
            context["recommendations"].append(f"Actual: {alert.get('actual', 'N/A')}")

        elif alert["source"] == "codeql":
            context["recommendations"].append("Review CodeQL analysis results")
            context["recommendations"].append(f"Rule: {alert.get('rule_id', 'N/A')}")

        return context

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary report of all alerts.

        Returns:
            Summary statistics dictionary
        """
        print("\n📊 Security Alerts Summary Report")
        print("=" * 70)

        total = len(self.alerts_db["alerts"])
        by_status = {}
        by_severity = {}
        by_source = {}
        false_positives = 0

        for alert in self.alerts_db["alerts"].values():
            # Count by status
            status = alert.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

            # Count by severity
            severity = alert.get("severity", "UNKNOWN")
            by_severity[severity] = by_severity.get(severity, 0) + 1

            # Count by source
            source = alert.get("source", "unknown")
            by_source[source] = by_source.get(source, 0) + 1

            # Count false positives
            if alert.get("is_false_positive"):
                false_positives += 1

        summary = {
            "total_alerts": total,
            "by_status": by_status,
            "by_severity": by_severity,
            "by_source": by_source,
            "false_positives": false_positives,
            "generated": datetime.utcnow().isoformat(),
        }

        # Display summary
        print(f"\nTotal Alerts: {total}")
        print(f"False Positives: {false_positives}")

        print("\n📋 By Status:")
        for status, count in sorted(by_status.items()):
            print(f"   {status:15} : {count:3}")

        print("\n⚠️  By Severity:")
        for severity, count in sorted(by_severity.items(), key=lambda x: -self.SEVERITY_MAP.get(x[0].upper(), 0)):
            print(f"   {severity:15} : {count:3}")

        print("\n🔍 By Source:")
        for source, count in sorted(by_source.items()):
            print(f"   {source:15} : {count:3}")

        print("\n" + "=" * 70)

        return summary

    def list_alerts(self, status_filter: Optional[str] = None, severity_filter: Optional[str] = None) -> List[Dict]:
        """
        List alerts with optional filtering.

        Args:
            status_filter: Filter by status (new, investigating, remediated, escalated, closed)
            severity_filter: Filter by severity

        Returns:
            List of filtered alerts
        """
        filtered_alerts = []

        for alert_id, alert in self.alerts_db["alerts"].items():
            # Apply filters
            if status_filter and alert.get("status") != status_filter:
                continue

            if severity_filter and alert.get("severity", "").upper() != severity_filter.upper():
                continue

            filtered_alerts.append(alert)

        # Sort by normalized severity (descending) and created date
        filtered_alerts.sort(
            key=lambda x: (
                -x.get("normalized_severity", 0),
                x.get("created", ""),
            )
        )

        return filtered_alerts


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Investigate and triage security alerts from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Collect all alerts from security scanners
    python scripts/investigate_security_alerts.py --collect

    # Investigate a specific alert
    python scripts/investigate_security_alerts.py --investigate --alert-id bandit-B101-42

    # Generate summary report
    python scripts/investigate_security_alerts.py --summary

    # List all open alerts
    python scripts/investigate_security_alerts.py --list --status new

    # List high severity alerts
    python scripts/investigate_security_alerts.py --list --severity HIGH
        """,
    )

    parser.add_argument(
        "--collect",
        action="store_true",
        help="Collect alerts from all security scanners",
    )

    parser.add_argument(
        "--investigate",
        action="store_true",
        help="Investigate a specific alert",
    )

    parser.add_argument(
        "--alert-id",
        type=str,
        help="Alert ID to investigate",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate summary report",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List alerts with optional filtering",
    )

    parser.add_argument(
        "--status",
        type=str,
        choices=["new", "investigating", "remediated", "escalated", "closed"],
        help="Filter alerts by status",
    )

    parser.add_argument(
        "--severity",
        type=str,
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
        help="Filter alerts by severity",
    )

    parser.add_argument(
        "--alerts-db",
        type=Path,
        default=Path("data/security/alerts.json"),
        help="Path to alerts tracking database (default: data/security/alerts.json)",
    )

    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("output/reports/security"),
        help="Directory containing security reports (default: output/reports/security)",
    )

    args = parser.parse_args()

    # Initialize investigator
    investigator = SecurityAlertInvestigator(
        alerts_db_path=args.alerts_db,
        reports_dir=args.reports_dir,
    )

    # Execute requested action
    if args.collect:
        investigator.collect_all_alerts()

    elif args.investigate:
        if not args.alert_id:
            print("❌ Error: --alert-id required for investigation", file=sys.stderr)
            sys.exit(1)
        investigator.investigate_alert(args.alert_id)

    elif args.summary:
        summary = investigator.generate_summary()
        # Optionally save summary to file
        summary_path = args.reports_dir / "alert_summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n📄 Summary report saved to {summary_path}")

    elif args.list:
        alerts = investigator.list_alerts(
            status_filter=args.status,
            severity_filter=args.severity,
        )

        print(f"\n📋 Filtered Alerts ({len(alerts)} found)")
        print("=" * 70)

        for alert in alerts:
            print(f"\n{alert['id']}")
            print(f"  Source: {alert['source']:15} | Severity: {alert['severity']:8} | Status: {alert['status']}")
            print(f"  {alert['title'][:60]}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
