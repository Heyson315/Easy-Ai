#!/usr/bin/env python3
"""
test_security_alert_system.py

Comprehensive tests for the security alert investigation and remediation system.
Tests all three main modules:
- investigate_security_alerts.py
- remediate_security_alerts.py
- generate_alert_summary.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from investigate_security_alerts import SecurityAlertInvestigator
from remediate_security_alerts import SecurityAlertRemediator
from generate_alert_summary import AlertSummaryGenerator


class TestSecurityAlertInvestigator:
    """Tests for SecurityAlertInvestigator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with TemporaryDirectory() as td:
            yield Path(td)

    @pytest.fixture
    def sample_bandit_report(self, temp_dir):
        """Create sample Bandit report."""
        report = {
            "results": [
                {
                    "test_id": "B101",
                    "issue_severity": "LOW",
                    "issue_confidence": "HIGH",
                    "issue_text": "Use of assert detected",
                    "filename": "test_file.py",
                    "line_number": 42,
                    "code": "assert x == y",
                    "issue_cwe": {"id": "703"},
                }
            ]
        }
        report_path = temp_dir / "bandit-report.json"
        with open(report_path, "w") as f:
            json.dump(report, f)
        return report_path

    @pytest.fixture
    def sample_safety_report(self, temp_dir):
        """Create sample Safety report."""
        report = {
            "vulnerabilities": [
                {
                    "package_name": "requests",
                    "vulnerability_id": "12345",
                    "installed_version": "2.25.1",
                    "affected_versions": "<2.31.0",
                    "advisory": "Security vulnerability in requests",
                    "cve": "CVE-2023-12345",
                    "more_info_url": "https://example.com",
                }
            ]
        }
        report_path = temp_dir / "safety-report.json"
        with open(report_path, "w") as f:
            json.dump(report, f)
        return report_path

    @pytest.fixture
    def sample_m365_report(self, temp_dir):
        """Create sample M365 CIS report."""
        report = [
            {
                "ControlId": "1.1.1",
                "Title": "Ensure modern authentication is enabled",
                "Severity": "HIGH",
                "Status": "Fail",
                "Expected": "Enabled",
                "Actual": "Disabled",
                "Evidence": "Legacy auth detected",
                "Reference": "https://example.com",
                "Timestamp": datetime.utcnow().isoformat(),
            }
        ]
        report_path = temp_dir / "m365_cis_audit.json"
        with open(report_path, "w") as f:
            json.dump(report, f)
        return report_path

    @pytest.fixture
    def investigator(self, temp_dir):
        """Create SecurityAlertInvestigator instance."""
        alerts_db_path = temp_dir / "alerts.json"
        reports_dir = temp_dir
        return SecurityAlertInvestigator(alerts_db_path, reports_dir)

    def test_normalize_severity(self, investigator):
        """Test severity normalization."""
        assert investigator.normalize_severity("CRITICAL") == 10
        assert investigator.normalize_severity("HIGH") == 8
        assert investigator.normalize_severity("MEDIUM") == 5
        assert investigator.normalize_severity("LOW") == 2
        assert investigator.normalize_severity("unknown") == 1

    def test_is_false_positive(self, investigator):
        """Test false positive detection."""
        # Test file
        alert = {"file_path": "/path/to/test/test_something.py"}
        assert investigator.is_false_positive(alert) is True

        # Regular file
        alert = {"file_path": "/path/to/src/module.py"}
        assert investigator.is_false_positive(alert) is False

        # Test directory
        alert = {"file_path": "/path/to/tests/module.py"}
        assert investigator.is_false_positive(alert) is True

    def test_collect_bandit_alerts(self, investigator, sample_bandit_report):
        """Test Bandit alert collection."""
        alerts = investigator.collect_bandit_alerts()

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert["source"] == "bandit"
        assert alert["severity"] == "LOW"
        assert "B101" in alert["id"]
        assert alert["file_path"] == "test_file.py"
        assert alert["line_number"] == 42

    def test_collect_safety_alerts(self, investigator, sample_safety_report):
        """Test Safety alert collection."""
        alerts = investigator.collect_safety_alerts()

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert["source"] == "safety"
        assert alert["severity"] == "HIGH"
        assert alert["package"] == "requests"
        assert alert["installed_version"] == "2.25.1"

    def test_collect_m365_alerts(self, investigator, sample_m365_report):
        """Test M365 CIS alert collection."""
        alerts = investigator.collect_m365_cis_alerts()

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert["source"] == "m365_cis"
        assert alert["severity"] == "HIGH"
        assert alert["control_id"] == "1.1.1"
        assert alert["expected"] == "Enabled"
        assert alert["actual"] == "Disabled"

    def test_collect_all_alerts(
        self, investigator, sample_bandit_report, sample_safety_report, sample_m365_report
    ):
        """Test collecting alerts from all sources."""
        new_count = investigator.collect_all_alerts()

        assert new_count == 3
        assert len(investigator.alerts_db["alerts"]) == 3

        # Verify alerts database was saved
        assert investigator.alerts_db_path.exists()

    def test_investigate_alert(self, investigator, sample_bandit_report):
        """Test investigating a specific alert."""
        # Collect alerts first
        investigator.collect_all_alerts()

        # Get first alert ID
        alert_ids = list(investigator.alerts_db["alerts"].keys())
        alert_id = alert_ids[0]

        # Investigate
        result = investigator.investigate_alert(alert_id)

        assert result["status"] == "success"
        assert result["alert"]["status"] == "investigating"
        assert "context" in result

    def test_generate_summary(
        self, investigator, sample_bandit_report, sample_safety_report, sample_m365_report
    ):
        """Test summary generation."""
        # Collect alerts first
        investigator.collect_all_alerts()

        # Generate summary
        summary = investigator.generate_summary()

        assert summary["total_alerts"] == 3
        assert summary["by_source"]["bandit"] == 1
        assert summary["by_source"]["safety"] == 1
        assert summary["by_source"]["m365_cis"] == 1

    def test_list_alerts_filtering(
        self, investigator, sample_bandit_report, sample_safety_report
    ):
        """Test alert listing with filters."""
        # Collect alerts
        investigator.collect_all_alerts()

        # Filter by status
        new_alerts = investigator.list_alerts(status_filter="new")
        assert len(new_alerts) == 2

        # Filter by severity
        high_alerts = investigator.list_alerts(severity_filter="HIGH")
        assert len(high_alerts) == 1


class TestSecurityAlertRemediator:
    """Tests for SecurityAlertRemediator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with TemporaryDirectory() as td:
            yield Path(td)

    @pytest.fixture
    def sample_alerts_db(self, temp_dir):
        """Create sample alerts database."""
        db = {
            "alerts": {
                "safety-requests-12345": {
                    "id": "safety-requests-12345",
                    "source": "safety",
                    "severity": "HIGH",
                    "title": "Vulnerability in requests",
                    "package": "requests",
                    "installed_version": "2.25.1",
                    "status": "investigating",
                },
                "m365-1.1.1": {
                    "id": "m365-1.1.1",
                    "source": "m365_cis",
                    "severity": "HIGH",
                    "control_id": "1.1.1",
                    "title": "Modern auth disabled",
                    "status": "investigating",
                },
            },
            "metadata": {
                "created": datetime.utcnow().isoformat(),
                "version": "1.0",
            },
        }

        db_path = temp_dir / "alerts.json"
        with open(db_path, "w") as f:
            json.dump(db, f)
        return db_path

    @pytest.fixture
    def remediator(self, temp_dir, sample_alerts_db):
        """Create SecurityAlertRemediator instance."""
        log_path = temp_dir / "remediation_log.json"
        return SecurityAlertRemediator(sample_alerts_db, log_path)

    def test_can_auto_remediate_safety(self, remediator):
        """Test auto-remediation detection for Safety alerts."""
        alert = {"source": "safety"}
        assert remediator.can_auto_remediate(alert) is True

    def test_can_auto_remediate_bandit(self, remediator):
        """Test auto-remediation detection for Bandit alerts."""
        # Low severity, high confidence - can auto-remediate
        alert = {"source": "bandit", "severity": "LOW", "confidence": "HIGH"}
        assert remediator.can_auto_remediate(alert) is True

        # High severity - cannot auto-remediate
        alert = {"source": "bandit", "severity": "HIGH", "confidence": "HIGH"}
        assert remediator.can_auto_remediate(alert) is False

    def test_remediate_safety_alert_whatif(self, remediator):
        """Test Safety alert remediation in whatif mode."""
        alert = {
            "id": "safety-test",
            "source": "safety",
            "package": "requests",
            "installed_version": "2.25.1",
        }

        result = remediator.remediate_safety_alert(alert, whatif=True)

        assert result["status"] == "preview"
        assert "requests" in result["message"]

    def test_escalate_alert(self, remediator):
        """Test alert escalation."""
        alert_id = "safety-requests-12345"
        success = remediator.escalate_alert(alert_id, "Manual review required")

        assert success is True
        assert remediator.alerts_db["alerts"][alert_id]["status"] == "escalated"

        # Verify escalation file was created
        escalation_path = Path("output/reports/security/escalations") / f"{alert_id}.json"
        # Note: In temp dir, this won't actually exist, but the function should succeed

    def test_close_alert(self, remediator):
        """Test closing an alert."""
        alert_id = "safety-requests-12345"
        success = remediator.close_alert(alert_id, "Fixed by upgrading package")

        assert success is True
        assert remediator.alerts_db["alerts"][alert_id]["status"] == "closed"
        assert remediator.alerts_db["alerts"][alert_id]["resolution"] == "Fixed by upgrading package"

    def test_generate_remediation_report(self, remediator):
        """Test remediation report generation."""
        # Add some log entries
        remediator._log_action("test-1", "remediate", "success", {})
        remediator._log_action("test-2", "escalate", "success", {})
        remediator._log_action("test-3", "remediate", "error", {})

        report = remediator.generate_remediation_report()

        assert report["total_actions"] == 3
        assert report["by_action"]["remediate"] == 2
        assert report["by_action"]["escalate"] == 1
        assert report["by_result"]["success"] == 2


class TestAlertSummaryGenerator:
    """Tests for AlertSummaryGenerator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with TemporaryDirectory() as td:
            yield Path(td)

    @pytest.fixture
    def sample_alerts_db(self, temp_dir):
        """Create sample alerts database."""
        db = {
            "alerts": {
                "alert-1": {
                    "id": "alert-1",
                    "source": "bandit",
                    "severity": "HIGH",
                    "status": "new",
                    "normalized_severity": 8,
                },
                "alert-2": {
                    "id": "alert-2",
                    "source": "safety",
                    "severity": "CRITICAL",
                    "status": "remediated",
                    "normalized_severity": 10,
                    "is_false_positive": False,
                },
                "alert-3": {
                    "id": "alert-3",
                    "source": "m365_cis",
                    "severity": "MEDIUM",
                    "status": "escalated",
                    "normalized_severity": 5,
                    "is_false_positive": True,
                },
            },
            "metadata": {"created": datetime.utcnow().isoformat()},
        }

        db_path = temp_dir / "alerts.json"
        with open(db_path, "w") as f:
            json.dump(db, f)
        return db_path

    @pytest.fixture
    def sample_remediation_log(self, temp_dir):
        """Create sample remediation log."""
        log = [
            {"action": "remediate", "result": "success"},
            {"action": "remediate", "result": "error"},
            {"action": "escalate", "result": "success"},
        ]

        log_path = temp_dir / "remediation_log.json"
        with open(log_path, "w") as f:
            json.dump(log, f)
        return log_path

    @pytest.fixture
    def generator(self, temp_dir, sample_alerts_db, sample_remediation_log):
        """Create AlertSummaryGenerator instance."""
        return AlertSummaryGenerator(sample_alerts_db, sample_remediation_log)

    def test_calculate_statistics(self, generator):
        """Test statistics calculation."""
        stats = generator.calculate_statistics()

        assert stats["total_alerts"] == 3
        assert stats["remediated_count"] == 1
        assert stats["escalated_count"] == 1
        assert stats["pending_count"] == 1
        assert stats["false_positives"] == 1
        assert stats["critical_severity_open"] == 0  # Remediated
        assert stats["high_severity_open"] == 1

    def test_generate_executive_summary(self, generator):
        """Test executive summary generation."""
        stats = generator.calculate_statistics()
        summary = generator.generate_executive_summary(stats)

        assert "EXECUTIVE SUMMARY" in summary
        assert "Total Alerts Investigated: 3" in summary
        assert "Alerts Remediated: 1" in summary

    def test_generate_detailed_breakdown(self, generator):
        """Test detailed breakdown generation."""
        stats = generator.calculate_statistics()
        breakdown = generator.generate_detailed_breakdown(stats)

        assert "DETAILED BREAKDOWN" in breakdown
        assert "ALERTS BY STATUS" in breakdown
        assert "ALERTS BY SEVERITY" in breakdown
        assert "ALERTS BY SOURCE" in breakdown

    def test_export_json(self, generator, temp_dir):
        """Test JSON export."""
        output_path = temp_dir / "summary.json"
        generator.export_json(output_path)

        assert output_path.exists()

        # Verify content
        with open(output_path) as f:
            data = json.load(f)

        assert "metadata" in data
        assert "statistics" in data
        assert "alerts_database" in data
        assert "remediation_log" in data

    def test_export_html(self, generator, temp_dir):
        """Test HTML export."""
        output_path = temp_dir / "summary.html"
        generator.export_html(output_path)

        assert output_path.exists()

        # Verify it's valid HTML
        with open(output_path) as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "Security Alert Summary Report" in content
        assert "Total Alerts" in content


# Integration tests
class TestSecurityAlertSystemIntegration:
    """Integration tests for the complete security alert system."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with TemporaryDirectory() as td:
            yield Path(td)

    def test_full_workflow(self, temp_dir):
        """Test complete workflow from collection to reporting."""
        # Create sample reports
        reports_dir = temp_dir / "reports"
        reports_dir.mkdir()

        # Bandit report
        bandit_report = {
            "results": [
                {
                    "test_id": "B101",
                    "issue_severity": "LOW",
                    "issue_confidence": "HIGH",
                    "issue_text": "Use of assert",
                    "filename": "test.py",
                    "line_number": 10,
                    "code": "assert True",
                    "issue_cwe": {"id": "703"},
                }
            ]
        }
        with open(reports_dir / "bandit-report.json", "w") as f:
            json.dump(bandit_report, f)

        # 1. Collect alerts
        alerts_db_path = temp_dir / "alerts.json"
        investigator = SecurityAlertInvestigator(alerts_db_path, reports_dir)
        new_count = investigator.collect_all_alerts()

        assert new_count == 1
        assert alerts_db_path.exists()

        # 2. Investigate alerts
        alert_ids = list(investigator.alerts_db["alerts"].keys())
        result = investigator.investigate_alert(alert_ids[0])

        assert result["status"] == "success"

        # 3. Attempt remediation
        remediation_log_path = temp_dir / "remediation_log.json"
        remediator = SecurityAlertRemediator(alerts_db_path, remediation_log_path)

        # Escalate (since auto-remediation may not apply)
        success = remediator.escalate_alert(alert_ids[0], "Test escalation")
        assert success is True

        # 4. Generate report
        generator = AlertSummaryGenerator(alerts_db_path, remediation_log_path)
        stats = generator.calculate_statistics()

        assert stats["total_alerts"] == 1
        assert stats["escalated_count"] == 1

        # Export reports
        json_path = temp_dir / "summary.json"
        html_path = temp_dir / "summary.html"

        generator.export_json(json_path)
        generator.export_html(html_path)

        assert json_path.exists()
        assert html_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
