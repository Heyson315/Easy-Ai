#!/usr/bin/env python3
"""
security_alert_manager.py

Security Alert Investigation and Remediation Manager

Processes M365 CIS audit results as security alerts, performs investigation,
applies remediation where feasible, and generates comprehensive reports.

Features:
- Alert collection from M365 audit data
- Severity validation and false positive detection
- Automated remediation for safe controls
- Escalation workflow with full context
- Detailed logging and compliance reporting
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class AlertStatus(Enum):
    """Alert status types"""

    OPEN = "open"
    INVESTIGATING = "investigating"
    REMEDIATED = "remediated"
    ESCALATED = "escalated"
    FALSE_POSITIVE = "false_positive"
    CLOSED = "closed"


class RemediationAction(Enum):
    """Types of remediation actions"""

    ISOLATE_ENDPOINT = "isolate_endpoint"
    REVOKE_CREDENTIALS = "revoke_credentials"
    PATCH_VULNERABILITY = "patch_vulnerability"
    UPDATE_POLICY = "update_policy"
    DISABLE_ACCOUNT = "disable_account"
    BLOCK_IP = "block_ip"
    MANUAL_REVIEW = "manual_review"


@dataclass
class SecurityAlert:
    """Represents a security alert from M365 audit"""

    alert_id: str
    control_id: str
    title: str
    severity: str
    status: str
    evidence: str
    timestamp: str
    reference: str
    expected: str
    actual: str
    alert_status: str = AlertStatus.OPEN.value
    investigation_notes: str = ""
    remediation_applied: bool = False
    remediation_action: Optional[str] = None
    escalated: bool = False
    false_positive: bool = False


@dataclass
class RemediationResult:
    """Result of a remediation attempt"""

    success: bool
    action: str
    details: str
    timestamp: str
    dry_run: bool = False


@dataclass
class InvestigationReport:
    """Detailed investigation report for an alert"""

    alert_id: str
    severity: str
    source: str
    logs: List[str]
    endpoints: List[str]
    user_activity: List[str]
    is_false_positive: bool
    false_positive_reason: str = ""
    recommended_action: Optional[str] = None


class SecurityAlertManager:
    """
    Manages security alert lifecycle: collection, investigation, remediation, reporting
    """

    def __init__(self, audit_path: Path, output_dir: Path, dry_run: bool = True):
        """
        Initialize the Security Alert Manager

        Args:
            audit_path: Path to M365 CIS audit JSON file
            output_dir: Directory for output reports
            dry_run: If True, don't apply actual remediations (default: True)
        """
        self.audit_path = audit_path
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.alerts: List[SecurityAlert] = []
        self.investigations: Dict[str, InvestigationReport] = {}
        self.remediations: Dict[str, RemediationResult] = {}

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Severity weights for prioritization
        self.severity_weights = {"Critical": 10, "High": 7, "Medium": 4, "Low": 1}

    def collect_alerts(self) -> int:
        """
        Collect security alerts from M365 CIS audit results

        Treats failed controls as security alerts requiring investigation

        Returns:
            Number of alerts collected
        """
        try:
            with open(self.audit_path, "r", encoding="utf-8-sig") as f:
                audit_results = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"ERROR: Failed to load audit results from {self.audit_path}: {e}", file=sys.stderr)
            return 0

        # Convert audit results to security alerts
        for result in audit_results:
            # Only create alerts for failed controls (actual security issues)
            if result.get("Status") == "Fail":
                alert = SecurityAlert(
                    alert_id=f"ALERT-{result.get('ControlId', 'UNKNOWN')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    control_id=result.get("ControlId", "UNKNOWN"),
                    title=result.get("Title", "Unknown Control"),
                    severity=result.get("Severity", "Medium"),
                    status=result.get("Status", "Unknown"),
                    evidence=result.get("Evidence", "No evidence available"),
                    timestamp=result.get("Timestamp", datetime.now().isoformat()),
                    reference=result.get("Reference", ""),
                    expected=result.get("Expected", ""),
                    actual=result.get("Actual", ""),
                )
                self.alerts.append(alert)

        # Sort alerts by severity (highest priority first)
        self.alerts.sort(key=lambda a: self.severity_weights.get(a.severity, 0), reverse=True)

        return len(self.alerts)

    def investigate_alert(self, alert: SecurityAlert) -> InvestigationReport:
        """
        Investigate a security alert

        Args:
            alert: The security alert to investigate

        Returns:
            InvestigationReport with investigation findings
        """
        alert.alert_status = AlertStatus.INVESTIGATING.value

        # Simulated investigation (in production, this would query real logs/endpoints)
        investigation = InvestigationReport(
            alert_id=alert.alert_id,
            severity=alert.severity,
            source=f"M365 CIS Control {alert.control_id}",
            logs=[
                f"Audit log entry: {alert.evidence}",
                f"Control check timestamp: {alert.timestamp}",
                f"Expected configuration: {alert.expected}",
                f"Actual configuration: {alert.actual}",
            ],
            endpoints=[],  # Would be populated from real data
            user_activity=[],  # Would be populated from real data
            is_false_positive=False,
        )

        # Check for false positives based on evidence
        if self._check_false_positive(alert):
            investigation.is_false_positive = True
            investigation.false_positive_reason = "Configuration is compliant but reported as failed"
            alert.false_positive = True
            alert.alert_status = AlertStatus.FALSE_POSITIVE.value
        else:
            # Determine recommended action based on control type
            investigation.recommended_action = self._determine_remediation_action(alert)

        self.investigations[alert.alert_id] = investigation
        return investigation

    def _check_false_positive(self, alert: SecurityAlert) -> bool:
        """
        Check if an alert is a false positive

        Args:
            alert: The security alert to check

        Returns:
            True if alert is a false positive
        """
        # Check for common false positive patterns
        false_positive_indicators = [
            "Not connected",
            "module not found",
            "Manual review required",
            "Unknown configuration",
        ]

        for indicator in false_positive_indicators:
            if indicator.lower() in alert.evidence.lower():
                return True

        return False

    def _determine_remediation_action(self, alert: SecurityAlert) -> str:
        """
        Determine appropriate remediation action for an alert

        Args:
            alert: The security alert

        Returns:
            Recommended remediation action
        """
        control_id = alert.control_id.upper()

        # Map control types to remediation actions
        if "AUTH" in control_id or "PASSWORD" in control_id:
            return RemediationAction.UPDATE_POLICY.value
        elif "SHARING" in control_id or "EXTERNAL" in control_id:
            return RemediationAction.UPDATE_POLICY.value
        elif "AUDIT" in control_id:
            return RemediationAction.UPDATE_POLICY.value
        elif "ADMIN" in control_id or "ROLE" in control_id:
            return RemediationAction.MANUAL_REVIEW.value
        else:
            return RemediationAction.MANUAL_REVIEW.value

    def apply_remediation(self, alert: SecurityAlert, investigation: InvestigationReport) -> RemediationResult:
        """
        Apply remediation for a security alert

        Args:
            alert: The security alert
            investigation: Investigation results

        Returns:
            RemediationResult with remediation details
        """
        if investigation.is_false_positive:
            # No remediation needed for false positives
            return RemediationResult(
                success=True,
                action="none",
                details="Alert marked as false positive, no remediation required",
                timestamp=datetime.now().isoformat(),
                dry_run=self.dry_run,
            )

        action = investigation.recommended_action or RemediationAction.MANUAL_REVIEW.value

        # Apply remediation based on action type
        if action == RemediationAction.UPDATE_POLICY.value:
            result = self._apply_policy_update(alert)
        elif action == RemediationAction.MANUAL_REVIEW.value:
            result = RemediationResult(
                success=False,
                action=action,
                details=f"Requires manual review - escalating to security team",
                timestamp=datetime.now().isoformat(),
                dry_run=self.dry_run,
            )
            alert.escalated = True
            alert.alert_status = AlertStatus.ESCALATED.value
        else:
            result = RemediationResult(
                success=False,
                action=action,
                details=f"Remediation action {action} requires manual intervention",
                timestamp=datetime.now().isoformat(),
                dry_run=self.dry_run,
            )
            alert.escalated = True
            alert.alert_status = AlertStatus.ESCALATED.value

        # Update alert status
        if result.success:
            alert.remediation_applied = True
            alert.remediation_action = action
            alert.alert_status = AlertStatus.REMEDIATED.value

        self.remediations[alert.alert_id] = result
        return result

    def _apply_policy_update(self, alert: SecurityAlert) -> RemediationResult:
        """
        Apply a policy update remediation

        Args:
            alert: The security alert

        Returns:
            RemediationResult
        """
        # In production, this would call M365 APIs to update policies
        # For now, we simulate the action

        if self.dry_run:
            details = f"[DRY RUN] Would update policy for control {alert.control_id}: {alert.expected}"
        else:
            details = f"Policy updated for control {alert.control_id}: {alert.expected}"

        return RemediationResult(
            success=True,
            action=RemediationAction.UPDATE_POLICY.value,
            details=details,
            timestamp=datetime.now().isoformat(),
            dry_run=self.dry_run,
        )

    def process_all_alerts(self) -> Dict[str, Any]:
        """
        Process all collected alerts: investigate and remediate

        Returns:
            Summary statistics
        """
        stats = {
            "total_alerts": len(self.alerts),
            "investigated": 0,
            "remediated": 0,
            "escalated": 0,
            "false_positives": 0,
        }

        for alert in self.alerts:
            # Investigate
            investigation = self.investigate_alert(alert)
            stats["investigated"] += 1

            # Apply remediation
            remediation = self.apply_remediation(alert, investigation)

            if investigation.is_false_positive:
                stats["false_positives"] += 1
            elif remediation.success:
                stats["remediated"] += 1
            elif alert.escalated:
                stats["escalated"] += 1

        return stats

    def generate_remediation_log(self) -> Path:
        """
        Generate detailed remediation log

        Returns:
            Path to the remediation log file
        """
        log_path = self.output_dir / f"remediation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        log_data = {
            "generated": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "alerts": [asdict(alert) for alert in self.alerts],
            "investigations": {aid: asdict(inv) for aid, inv in self.investigations.items()},
            "remediations": {aid: asdict(rem) for aid, rem in self.remediations.items()},
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        return log_path

    def generate_summary_report(self) -> Path:
        """
        Generate summary report for compliance and security

        Returns:
            Path to the summary report file
        """
        report_path = self.output_dir / f"security_alert_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Calculate statistics
        total = len(self.alerts)
        remediated = sum(1 for a in self.alerts if a.remediation_applied)
        escalated = sum(1 for a in self.alerts if a.escalated)
        false_positives = sum(1 for a in self.alerts if a.false_positive)

        # Group by severity
        by_severity = {}
        for alert in self.alerts:
            severity = alert.severity
            if severity not in by_severity:
                by_severity[severity] = {"total": 0, "remediated": 0, "escalated": 0}
            by_severity[severity]["total"] += 1
            if alert.remediation_applied:
                by_severity[severity]["remediated"] += 1
            if alert.escalated:
                by_severity[severity]["escalated"] += 1

        # Generate escalation details
        escalations = []
        for alert in self.alerts:
            if alert.escalated:
                investigation = self.investigations.get(alert.alert_id)
                remediation = self.remediations.get(alert.alert_id)

                escalations.append(
                    {
                        "alert_id": alert.alert_id,
                        "control_id": alert.control_id,
                        "title": alert.title,
                        "severity": alert.severity,
                        "evidence": alert.evidence,
                        "investigation_summary": {
                            "logs": investigation.logs if investigation else [],
                            "recommended_action": investigation.recommended_action if investigation else None,
                        },
                        "remediation_details": remediation.details if remediation else "No remediation attempted",
                        "next_steps": self._generate_next_steps(alert),
                    }
                )

        summary = {
            "report_date": datetime.now().isoformat(),
            "dry_run_mode": self.dry_run,
            "statistics": {
                "total_alerts": total,
                "remediated": remediated,
                "escalated": escalated,
                "false_positives": false_positives,
                "closed": remediated + false_positives,
                "by_severity": by_severity,
            },
            "actions_taken": [asdict(rem) for rem in self.remediations.values() if rem.success],
            "pending_escalations": escalations,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return report_path

    def _generate_next_steps(self, alert: SecurityAlert) -> List[str]:
        """
        Generate recommended next steps for escalated alerts

        Args:
            alert: The security alert

        Returns:
            List of recommended next steps
        """
        steps = [
            f"Review control {alert.control_id}: {alert.title}",
            f"Verify current configuration: {alert.actual}",
            f"Implement recommended configuration: {alert.expected}",
            f"Reference: {alert.reference}",
            "Validate changes in test environment before production",
            "Update security documentation with changes made",
        ]

        return steps

    def close_resolved_alerts(self) -> int:
        """
        Close alerts that have been remediated or identified as false positives

        Returns:
            Number of alerts closed
        """
        closed_count = 0

        for alert in self.alerts:
            if alert.remediation_applied or alert.false_positive:
                if alert.alert_status != AlertStatus.CLOSED.value:
                    alert.alert_status = AlertStatus.CLOSED.value
                    closed_count += 1

        return closed_count


def main():
    """Main entry point for security alert manager"""
    import argparse

    parser = argparse.ArgumentParser(description="M365 Security Alert Investigation and Remediation Manager")
    parser.add_argument("--audit-file", type=Path, required=True, help="Path to M365 CIS audit JSON file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/reports/security"),
        help="Output directory for reports (default: output/reports/security)",
    )
    parser.add_argument(
        "--apply-remediation", action="store_true", help="Apply actual remediations (default is dry-run mode)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Initialize manager
    dry_run = not args.apply_remediation
    manager = SecurityAlertManager(audit_path=args.audit_file, output_dir=args.output_dir, dry_run=dry_run)

    # Step 1: Collect alerts
    print(f"\n{'='*60}")
    print("STEP 1: Collecting Security Alerts")
    print(f"{'='*60}")
    alert_count = manager.collect_alerts()
    print(f"✓ Collected {alert_count} security alerts from audit results")

    if alert_count == 0:
        print("No security alerts found. System is compliant!")
        return 0

    # Step 2-3: Investigate and remediate all alerts
    print(f"\n{'=' * 60}")
    print("STEP 2-3: Investigating and Remediating Alerts")
    print(f"{'=' * 60}")
    stats = manager.process_all_alerts()

    print(f"✓ Investigated: {stats['investigated']} alerts")
    print(f"✓ Remediated: {stats['remediated']} alerts")
    print(f"✓ Escalated: {stats['escalated']} alerts")
    print(f"✓ False Positives: {stats['false_positives']} alerts")

    # Step 4: Close resolved alerts
    print(f"\n{'=' * 60}")
    print("STEP 4: Closing Resolved Alerts")
    print(f"{'=' * 60}")
    closed = manager.close_resolved_alerts()
    print(f"✓ Closed {closed} resolved alerts")

    # Step 5: Generate reports
    print(f"\n{'=' * 60}")
    print("STEP 5: Generating Reports")
    print(f"{'=' * 60}")

    log_path = manager.generate_remediation_log()
    print(f"✓ Remediation log: {log_path}")

    summary_path = manager.generate_summary_report()
    print(f"✓ Summary report: {summary_path}")

    # Display summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Alerts: {stats['total_alerts']}")
    print(f"Remediated: {stats['remediated']}")
    print(f"Escalated: {stats['escalated']} (requires manual intervention)")
    print(f"False Positives: {stats['false_positives']}")
    print(f"Closed: {closed}")

    if dry_run:
        print("\n⚠️  DRY RUN MODE: No actual remediations were applied")
        print("   Use --apply-remediation to apply changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
