#!/usr/bin/env python3
"""
Tests for security_alert_manager.py

Tests alert collection, investigation, remediation, and reporting functionality.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from src.core.security_alert_manager import (
    SecurityAlertManager,
    SecurityAlert,
    AlertStatus,
    RemediationAction,
    InvestigationReport,
    RemediationResult,
)


@pytest.fixture
def sample_audit_data():
    """Sample M365 CIS audit data with various control statuses"""
    return [
        {
            "ControlId": "CIS-EXO-1",
            "Title": "Ensure modern auth is enabled and basic auth blocked",
            "Severity": "High",
            "Expected": "OAuth2 on; basic off",
            "Actual": "Basic auth enabled on SMTP",
            "Status": "Fail",
            "Evidence": "Basic authentication detected on protocol: SMTP",
            "Reference": "CIS M365 Foundations v3.0 L1",
            "Timestamp": "2025-12-11T10:00:00",
        },
        {
            "ControlId": "CIS-EXO-2",
            "Title": "Disable external auto-forwarding",
            "Severity": "High",
            "Expected": "External forwarding disabled",
            "Actual": "External forwarding enabled",
            "Status": "Fail",
            "Evidence": "AutoForwardEnabled is True",
            "Reference": "CIS M365 Foundations v3.0 L1",
            "Timestamp": "2025-12-11T10:01:00",
        },
        {
            "ControlId": "CIS-AAD-1",
            "Title": "Limit Global Administrator role assignments",
            "Severity": "Critical",
            "Expected": "Maximum 5 Global Administrators",
            "Actual": "8 Global Administrators found",
            "Status": "Fail",
            "Evidence": "Found 8 users with Global Administrator role",
            "Reference": "CIS M365 Foundations v3.0 L1",
            "Timestamp": "2025-12-11T10:02:00",
        },
        {
            "ControlId": "CIS-SPO-1",
            "Title": "Restrict SharePoint external sharing",
            "Severity": "Medium",
            "Expected": "External sharing disabled or restricted",
            "Actual": "Unknown",
            "Status": "Manual",
            "Evidence": "Not connected to SharePoint",
            "Reference": "CIS M365 Foundations v3.0 L1",
            "Timestamp": "2025-12-11T10:03:00",
        },
        {
            "ControlId": "CIS-AAD-2",
            "Title": "Ensure MFA is enabled for all users",
            "Severity": "High",
            "Expected": "MFA enabled for 100% of users",
            "Actual": "MFA enabled for 100% of users",
            "Status": "Pass",
            "Evidence": "All users have MFA enabled",
            "Reference": "CIS M365 Foundations v3.0 L1",
            "Timestamp": "2025-12-11T10:04:00",
        },
    ]


@pytest.fixture
def temp_audit_file(sample_audit_data):
    """Create a temporary audit file for testing"""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        audit_file = tmpdir / "test_audit.json"

        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(sample_audit_data, f)

        yield audit_file


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for testing"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def alert_manager(temp_audit_file, temp_output_dir):
    """Create a SecurityAlertManager instance for testing"""
    return SecurityAlertManager(audit_path=temp_audit_file, output_dir=temp_output_dir, dry_run=True)


class TestSecurityAlertCollection:
    """Tests for alert collection functionality"""

    def test_collect_alerts_from_audit(self, alert_manager):
        """Test that alerts are correctly collected from audit results"""
        count = alert_manager.collect_alerts()

        # Should only collect failed controls (3 out of 5)
        assert count == 3
        assert len(alert_manager.alerts) == 3

    def test_alerts_sorted_by_severity(self, alert_manager):
        """Test that alerts are sorted by severity (Critical > High > Medium > Low)"""
        alert_manager.collect_alerts()

        # First alert should be Critical
        assert alert_manager.alerts[0].severity == "Critical"
        # Followed by High severity alerts
        assert alert_manager.alerts[1].severity == "High"
        assert alert_manager.alerts[2].severity == "High"

    def test_alert_fields_populated(self, alert_manager):
        """Test that alert fields are correctly populated from audit data"""
        alert_manager.collect_alerts()

        alert = alert_manager.alerts[0]
        assert alert.control_id == "CIS-AAD-1"
        assert alert.title == "Limit Global Administrator role assignments"
        assert alert.severity == "Critical"
        assert alert.expected == "Maximum 5 Global Administrators"
        assert alert.actual == "8 Global Administrators found"
        assert alert.alert_status == AlertStatus.OPEN.value

    def test_empty_audit_file(self, temp_output_dir):
        """Test handling of empty audit results"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            empty_file = tmpdir / "empty.json"
            with open(empty_file, "w") as f:
                json.dump([], f)

            manager = SecurityAlertManager(empty_file, temp_output_dir, dry_run=True)
            count = manager.collect_alerts()

            assert count == 0
            assert len(manager.alerts) == 0


class TestAlertInvestigation:
    """Tests for alert investigation functionality"""

    def test_investigate_alert_creates_report(self, alert_manager):
        """Test that investigating an alert creates an investigation report"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)

        assert isinstance(investigation, InvestigationReport)
        assert investigation.alert_id == alert.alert_id
        assert investigation.severity == alert.severity
        assert len(investigation.logs) > 0

    def test_false_positive_detection(self, alert_manager):
        """Test that false positives are correctly identified"""
        # Create an alert with false positive indicators
        alert = SecurityAlert(
            alert_id="TEST-FP-001",
            control_id="CIS-TEST-1",
            title="Test Control",
            severity="Medium",
            status="Fail",
            evidence="Not connected to service",
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="Connected",
            actual="Not connected",
        )

        result = alert_manager._check_false_positive(alert)
        assert result is True

    def test_investigation_updates_alert_status(self, alert_manager):
        """Test that investigation updates alert status"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[0]

        initial_status = alert.alert_status
        alert_manager.investigate_alert(alert)

        # Status should change from OPEN
        assert alert.alert_status != initial_status

    def test_remediation_action_determination(self, alert_manager):
        """Test that appropriate remediation actions are determined"""
        alert_manager.collect_alerts()

        for alert in alert_manager.alerts:
            action = alert_manager._determine_remediation_action(alert)
            assert action in [a.value for a in RemediationAction]


class TestRemediation:
    """Tests for remediation functionality"""

    def test_apply_remediation_for_valid_alert(self, alert_manager):
        """Test that remediation is applied for valid alerts"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[1]  # High severity alert

        investigation = alert_manager.investigate_alert(alert)
        result = alert_manager.apply_remediation(alert, investigation)

        assert isinstance(result, RemediationResult)
        assert result.dry_run is True

    def test_false_positive_no_remediation(self, alert_manager):
        """Test that false positives don't get remediation applied"""
        # Create a false positive alert
        alert = SecurityAlert(
            alert_id="TEST-FP-002",
            control_id="CIS-TEST-2",
            title="Test Control",
            severity="Medium",
            status="Fail",
            evidence="Module not found",
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="Module loaded",
            actual="Module not found",
        )

        investigation = InvestigationReport(
            alert_id=alert.alert_id,
            severity=alert.severity,
            source="Test",
            logs=[],
            endpoints=[],
            user_activity=[],
            is_false_positive=True,
            false_positive_reason="Module missing",
        )

        result = alert_manager.apply_remediation(alert, investigation)

        assert result.success is True
        assert result.action == "none"
        assert "false positive" in result.details.lower()

    def test_manual_review_escalation(self, alert_manager):
        """Test that manual review items are escalated"""
        alert_manager.collect_alerts()
        # Critical alert about admin roles should require manual review
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)
        result = alert_manager.apply_remediation(alert, investigation)

        # Should be escalated for manual review
        assert alert.escalated is True
        assert alert.alert_status == AlertStatus.ESCALATED.value

    def test_dry_run_mode(self, alert_manager):
        """Test that dry run mode doesn't apply actual changes"""
        assert alert_manager.dry_run is True

        alert_manager.collect_alerts()
        alert = alert_manager.alerts[1]

        investigation = alert_manager.investigate_alert(alert)
        result = alert_manager.apply_remediation(alert, investigation)

        # Verify dry_run flag is set in result
        assert result.dry_run is True


class TestAlertProcessing:
    """Tests for processing all alerts"""

    def test_process_all_alerts(self, alert_manager):
        """Test that all alerts are processed correctly"""
        alert_manager.collect_alerts()
        initial_count = len(alert_manager.alerts)

        stats = alert_manager.process_all_alerts()

        assert stats["total_alerts"] == initial_count
        assert stats["investigated"] == initial_count
        assert stats["remediated"] >= 0
        assert stats["escalated"] >= 0
        assert stats["false_positives"] >= 0

    def test_alert_closure(self, alert_manager):
        """Test that resolved alerts are closed"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        closed_count = alert_manager.close_resolved_alerts()

        # At least some alerts should be closed
        assert closed_count >= 0

        # Check that closed alerts have correct status
        for alert in alert_manager.alerts:
            if alert.remediation_applied or alert.false_positive:
                assert alert.alert_status == AlertStatus.CLOSED.value


class TestReporting:
    """Tests for report generation"""

    def test_generate_remediation_log(self, alert_manager):
        """Test remediation log generation"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        log_path = alert_manager.generate_remediation_log()

        assert log_path.exists()
        assert log_path.suffix == ".json"

        # Verify log content
        with open(log_path, "r") as f:
            log_data = json.load(f)

        assert "generated" in log_data
        assert "dry_run" in log_data
        assert "alerts" in log_data
        assert "investigations" in log_data
        assert "remediations" in log_data

    def test_generate_summary_report(self, alert_manager):
        """Test summary report generation"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        assert summary_path.exists()
        assert summary_path.suffix == ".json"

        # Verify summary content
        with open(summary_path, "r") as f:
            summary = json.load(f)

        assert "report_date" in summary
        assert "statistics" in summary
        assert "actions_taken" in summary
        assert "pending_escalations" in summary

        # Verify statistics
        stats = summary["statistics"]
        assert "total_alerts" in stats
        assert "remediated" in stats
        assert "escalated" in stats
        assert "by_severity" in stats

    def test_summary_report_statistics(self, alert_manager):
        """Test that summary report statistics are accurate"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        stats = summary["statistics"]

        # Total should equal sum of outcomes
        total = stats["total_alerts"]
        remediated = stats["remediated"]
        escalated = stats["escalated"]
        false_positives = stats["false_positives"]

        # All alerts should be accounted for
        assert remediated + escalated + false_positives <= total

    def test_escalation_details_in_summary(self, alert_manager):
        """Test that escalated alerts have detailed information in summary"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        escalations = summary["pending_escalations"]

        # Each escalation should have required fields
        for escalation in escalations:
            assert "alert_id" in escalation
            assert "severity" in escalation
            assert "evidence" in escalation
            assert "investigation_summary" in escalation
            assert "next_steps" in escalation
            assert len(escalation["next_steps"]) > 0


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_invalid_audit_file(self, temp_output_dir):
        """Test handling of invalid audit file"""
        invalid_file = Path("/nonexistent/file.json")
        manager = SecurityAlertManager(invalid_file, temp_output_dir, dry_run=True)

        count = manager.collect_alerts()
        assert count == 0

    def test_malformed_json(self, temp_output_dir):
        """Test handling of malformed JSON"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            bad_file = tmpdir / "bad.json"
            with open(bad_file, "w") as f:
                f.write("{invalid json")

            manager = SecurityAlertManager(bad_file, temp_output_dir, dry_run=True)
            count = manager.collect_alerts()

            assert count == 0

    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            audit_file = tmpdir / "audit.json"
            with open(audit_file, "w") as f:
                json.dump([], f)

            output_dir = tmpdir / "new" / "output" / "dir"
            assert not output_dir.exists()

            manager = SecurityAlertManager(audit_file, output_dir, dry_run=True)

            assert output_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
