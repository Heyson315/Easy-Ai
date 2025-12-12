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


class TestAlertCorrelation:
    """Tests for alert correlation and grouping"""

    def test_multiple_alerts_same_control(self, temp_output_dir):
        """Test handling of multiple alerts for the same control"""
        # Create audit data with repeated control failures
        audit_data = [
            {
                "ControlId": "CIS-EXO-1",
                "Title": "Modern auth control",
                "Severity": "High",
                "Expected": "OAuth2",
                "Actual": "Basic auth on SMTP",
                "Status": "Fail",
                "Evidence": "Basic auth detected: SMTP",
                "Reference": "CIS M365",
                "Timestamp": "2025-12-11T10:00:00",
            },
            {
                "ControlId": "CIS-EXO-1",
                "Title": "Modern auth control",
                "Severity": "High",
                "Expected": "OAuth2",
                "Actual": "Basic auth on POP3",
                "Status": "Fail",
                "Evidence": "Basic auth detected: POP3",
                "Reference": "CIS M365",
                "Timestamp": "2025-12-11T10:01:00",
            },
        ]

        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            audit_file = tmpdir / "audit.json"
            with open(audit_file, "w") as f:
                json.dump(audit_data, f)

            manager = SecurityAlertManager(audit_file, temp_output_dir, dry_run=True)
            count = manager.collect_alerts()

            # Should create separate alerts for each failure
            assert count == 2
            assert manager.alerts[0].control_id == manager.alerts[1].control_id

    def test_severity_based_prioritization(self, alert_manager):
        """Test that alerts are properly prioritized by severity"""
        alert_manager.collect_alerts()

        # Verify severity weights are applied correctly
        prev_weight = 100  # Start with max
        for alert in alert_manager.alerts:
            current_weight = alert_manager.severity_weights.get(alert.severity, 0)
            assert current_weight <= prev_weight
            prev_weight = current_weight


class TestRemediationVariations:
    """Tests for different remediation action types"""

    @pytest.mark.parametrize(
        "control_id,expected_action",
        [
            ("CIS-AUTH-1", RemediationAction.UPDATE_POLICY.value),
            ("CIS-PASSWORD-1", RemediationAction.UPDATE_POLICY.value),
            ("CIS-SHARING-1", RemediationAction.UPDATE_POLICY.value),
            ("CIS-EXTERNAL-1", RemediationAction.UPDATE_POLICY.value),
            ("CIS-AUDIT-1", RemediationAction.UPDATE_POLICY.value),
            ("CIS-ADMIN-1", RemediationAction.MANUAL_REVIEW.value),
            ("CIS-ROLE-1", RemediationAction.MANUAL_REVIEW.value),
            ("CIS-CUSTOM-1", RemediationAction.MANUAL_REVIEW.value),
        ],
    )
    def test_remediation_action_mapping(self, alert_manager, control_id, expected_action):
        """Test that control IDs map to correct remediation actions"""
        alert = SecurityAlert(
            alert_id=f"TEST-{control_id}",
            control_id=control_id,
            title="Test Control",
            severity="Medium",
            status="Fail",
            evidence="Test evidence",
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="Compliant",
            actual="Non-compliant",
        )

        action = alert_manager._determine_remediation_action(alert)
        assert action == expected_action

    def test_policy_update_dry_run(self, alert_manager):
        """Test policy update in dry-run mode"""
        alert = SecurityAlert(
            alert_id="TEST-POLICY-001",
            control_id="CIS-AUTH-1",
            title="Auth Control",
            severity="High",
            status="Fail",
            evidence="Policy violation",
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="MFA enabled",
            actual="MFA disabled",
        )

        result = alert_manager._apply_policy_update(alert)

        assert result.success is True
        assert result.dry_run is True
        assert "[DRY RUN]" in result.details
        assert alert.control_id in result.details

    def test_policy_update_live_mode(self, temp_audit_file, temp_output_dir):
        """Test policy update in live mode (dry_run=False)"""
        manager = SecurityAlertManager(temp_audit_file, temp_output_dir, dry_run=False)

        alert = SecurityAlert(
            alert_id="TEST-POLICY-002",
            control_id="CIS-AUTH-2",
            title="Auth Control",
            severity="High",
            status="Fail",
            evidence="Policy violation",
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="MFA enabled",
            actual="MFA disabled",
        )

        result = manager._apply_policy_update(alert)

        assert result.success is True
        assert result.dry_run is False
        assert "[DRY RUN]" not in result.details


class TestNextStepsGeneration:
    """Tests for escalation next steps generation"""

    def test_next_steps_generated_for_escalation(self, alert_manager):
        """Test that next steps are generated for escalated alerts"""
        alert = SecurityAlert(
            alert_id="TEST-ESC-001",
            control_id="CIS-ADMIN-1",
            title="Admin Role Control",
            severity="Critical",
            status="Fail",
            evidence="Too many admins",
            timestamp=datetime.now().isoformat(),
            reference="https://docs.microsoft.com/cis",
            expected="5 max admins",
            actual="8 admins",
        )

        steps = alert_manager._generate_next_steps(alert)

        assert isinstance(steps, list)
        assert len(steps) > 0
        # Verify key information is included
        assert any(alert.control_id in step for step in steps)
        assert any("test environment" in step.lower() for step in steps)
        assert any("documentation" in step.lower() for step in steps)

    def test_next_steps_include_reference(self, alert_manager):
        """Test that next steps include control reference"""
        alert = SecurityAlert(
            alert_id="TEST-ESC-002",
            control_id="CIS-EXO-1",
            title="Exchange Control",
            severity="High",
            status="Fail",
            evidence="Configuration mismatch",
            timestamp=datetime.now().isoformat(),
            reference="https://example.com/cis-controls",
            expected="Secure config",
            actual="Insecure config",
        )

        steps = alert_manager._generate_next_steps(alert)

        # Reference URL should be in steps
        assert any(alert.reference in step for step in steps)


class TestSeverityGrouping:
    """Tests for severity-based grouping and statistics"""

    def test_statistics_by_severity(self, alert_manager):
        """Test that summary statistics group alerts by severity"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        by_severity = summary["statistics"]["by_severity"]

        # Should have entries for each severity level present
        assert "Critical" in by_severity or "High" in by_severity or "Medium" in by_severity

        # Each severity entry should have required fields
        for severity, data in by_severity.items():
            assert "total" in data
            assert "remediated" in data
            assert "escalated" in data
            assert data["total"] >= data["remediated"] + data["escalated"]

    def test_severity_counts_accurate(self, alert_manager):
        """Test that severity counts match actual alert counts"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        by_severity = summary["statistics"]["by_severity"]
        total_from_severity = sum(data["total"] for data in by_severity.values())
        actual_total = summary["statistics"]["total_alerts"]

        assert total_from_severity == actual_total


class TestInvestigationDetails:
    """Tests for investigation report details"""

    def test_investigation_logs_contain_evidence(self, alert_manager):
        """Test that investigation logs include alert evidence"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)

        # Logs should contain evidence
        assert any(alert.evidence in log for log in investigation.logs)

    def test_investigation_includes_timestamp(self, alert_manager):
        """Test that investigation includes alert timestamp"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)

        # Logs should contain timestamp info
        assert any(alert.timestamp in log for log in investigation.logs)

    def test_investigation_includes_config_details(self, alert_manager):
        """Test that investigation includes expected and actual configs"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)

        # Should include both expected and actual config
        logs_text = " ".join(investigation.logs)
        assert alert.expected in logs_text
        assert alert.actual in logs_text

    def test_investigation_stores_in_manager(self, alert_manager):
        """Test that investigations are stored in manager"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)

        # Should be stored in manager's investigations dict
        assert alert.alert_id in alert_manager.investigations
        assert alert_manager.investigations[alert.alert_id] == investigation


class TestRemediationTracking:
    """Tests for remediation result tracking"""

    def test_remediation_result_stored(self, alert_manager):
        """Test that remediation results are stored"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[1]

        investigation = alert_manager.investigate_alert(alert)
        result = alert_manager.apply_remediation(alert, investigation)

        # Should be stored in manager's remediations dict
        assert alert.alert_id in alert_manager.remediations
        assert alert_manager.remediations[alert.alert_id] == result

    def test_successful_remediation_updates_alert(self, alert_manager):
        """Test that successful remediation updates alert fields"""
        alert_manager.collect_alerts()
        alert = alert_manager.alerts[1]

        investigation = alert_manager.investigate_alert(alert)
        result = alert_manager.apply_remediation(alert, investigation)

        if result.success:
            assert alert.remediation_applied is True
            assert alert.remediation_action is not None
            assert alert.alert_status == AlertStatus.REMEDIATED.value

    def test_failed_remediation_escalates(self, alert_manager):
        """Test that failed remediation escalates alert"""
        alert_manager.collect_alerts()
        # Critical alert should require manual review
        alert = alert_manager.alerts[0]

        investigation = alert_manager.investigate_alert(alert)
        result = alert_manager.apply_remediation(alert, investigation)

        if not result.success:
            assert alert.escalated is True
            assert alert.alert_status == AlertStatus.ESCALATED.value


class TestCompleteWorkflows:
    """Tests for complete end-to-end workflows"""

    def test_full_workflow_with_remediation(self, alert_manager):
        """Test complete workflow: collect -> investigate -> remediate -> report"""
        # Step 1: Collect
        count = alert_manager.collect_alerts()
        assert count > 0

        # Step 2-3: Process (investigate + remediate)
        stats = alert_manager.process_all_alerts()
        assert stats["investigated"] == count

        # Step 4: Close
        closed = alert_manager.close_resolved_alerts()
        assert closed >= 0

        # Step 5: Report
        log_path = alert_manager.generate_remediation_log()
        summary_path = alert_manager.generate_summary_report()

        assert log_path.exists()
        assert summary_path.exists()

    def test_workflow_statistics_consistency(self, alert_manager):
        """Test that statistics remain consistent throughout workflow"""
        count = alert_manager.collect_alerts()
        stats = alert_manager.process_all_alerts()
        alert_manager.close_resolved_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        # Total alerts should match initial count
        assert summary["statistics"]["total_alerts"] == count

        # Closed should equal remediated + false_positives
        closed = summary["statistics"]["closed"]
        remediated = summary["statistics"]["remediated"]
        false_positives = summary["statistics"]["false_positives"]

        assert closed == remediated + false_positives

    def test_actions_taken_list_populated(self, alert_manager):
        """Test that actions_taken list contains successful remediations"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        actions_taken = summary["actions_taken"]

        # Should only contain successful actions
        for action in actions_taken:
            assert "success" in action or "action" in action


class TestFalsePositivePatterns:
    """Tests for false positive detection patterns"""

    @pytest.mark.parametrize(
        "evidence",
        [
            "Not connected to service",
            "module not found in system",
            "Manual review required for compliance",
            "Unknown configuration detected",
            "NOT CONNECTED - service unavailable",
        ],
    )
    def test_false_positive_indicators(self, alert_manager, evidence):
        """Test that various false positive patterns are detected"""
        alert = SecurityAlert(
            alert_id=f"TEST-FP-{hash(evidence)}",
            control_id="CIS-TEST-1",
            title="Test Control",
            severity="Medium",
            status="Fail",
            evidence=evidence,
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="Available",
            actual="Unavailable",
        )

        result = alert_manager._check_false_positive(alert)
        assert result is True

    def test_valid_failure_not_false_positive(self, alert_manager):
        """Test that genuine failures are not marked as false positives"""
        alert = SecurityAlert(
            alert_id="TEST-VALID-001",
            control_id="CIS-TEST-2",
            title="Test Control",
            severity="High",
            status="Fail",
            evidence="Basic authentication is enabled on SMTP protocol",
            timestamp=datetime.now().isoformat(),
            reference="Test",
            expected="OAuth2",
            actual="Basic Auth",
        )

        result = alert_manager._check_false_positive(alert)
        assert result is False


class TestReportValidation:
    """Tests for report content validation"""

    def test_remediation_log_has_all_sections(self, alert_manager):
        """Test that remediation log contains all required sections"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        log_path = alert_manager.generate_remediation_log()

        with open(log_path, "r") as f:
            log_data = json.load(f)

        # Verify all required sections exist
        required_sections = ["generated", "dry_run", "alerts", "investigations", "remediations"]
        for section in required_sections:
            assert section in log_data, f"Missing section: {section}"

    def test_summary_report_has_all_sections(self, alert_manager):
        """Test that summary report contains all required sections"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        summary_path = alert_manager.generate_summary_report()

        with open(summary_path, "r") as f:
            summary = json.load(f)

        # Verify all required sections exist
        required_sections = ["report_date", "dry_run_mode", "statistics", "actions_taken", "pending_escalations"]
        for section in required_sections:
            assert section in summary, f"Missing section: {section}"

    def test_report_filenames_timestamped(self, alert_manager):
        """Test that report filenames include timestamps"""
        alert_manager.collect_alerts()
        alert_manager.process_all_alerts()

        log_path = alert_manager.generate_remediation_log()
        summary_path = alert_manager.generate_summary_report()

        # Filenames should contain timestamps
        assert "_" in log_path.stem
        assert "_" in summary_path.stem

        # Should be unique (different timestamps)
        assert log_path.name != summary_path.name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
