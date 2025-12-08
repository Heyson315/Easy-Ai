"""
Tests for the GPT-5 Cost Tracker.
"""

from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.core import cost_tracker
from src.core.cost_tracker import GPT5CostTracker, get_tracker, track_gpt5_request


@pytest.fixture(autouse=True)
def reset_global_tracker():
    """Fixture to reset the global tracker instance before each test."""
    cost_tracker._global_tracker = None
    yield
    cost_tracker._global_tracker = None


class TestGPT5CostTracker:
    """Test suite for the GPT5CostTracker."""

    def setup_method(self):
        """Reset the global tracker before each test to ensure isolation."""
        global _global_tracker
        _global_tracker = None

    def test_initialization(self):
        """Test that the cost tracker initializes correctly."""
        with TemporaryDirectory() as td:
            log_file = Path(td) / "log.json"
            tracker = GPT5CostTracker(budget_limit=10.0, log_file=str(log_file))
            assert tracker.budget_limit == 10.0
            assert tracker.log_file == str(log_file)
            assert tracker.total_cost == 0.0
            assert tracker.total_tokens == {"input": 0, "cached_input": 0, "output": 0}

    def test_track_request_calculates_cost_correctly(self):
        """Test that a request is tracked and cost is calculated correctly."""
        tracker = GPT5CostTracker()
        result = tracker.track_request(
            model="gpt-5",
            prompt_tokens=10000,
            completion_tokens=20000,
            cached_tokens=5000,
            request_type="test",
        )

        assert result["request"]["cost"]["total"] == pytest.approx(0.29)
        assert tracker.total_cost == pytest.approx(0.29)
        assert tracker.total_tokens["input"] == 10000
        assert tracker.total_tokens["cached_input"] == 5000
        assert tracker.total_tokens["output"] == 20000

    def test_track_request_with_unknown_model(self):
        """Test that an unknown model defaults to gpt-5 pricing."""
        tracker = GPT5CostTracker()
        result = tracker.track_request("unknown-model", 1000, 1000)
        # Should be same as gpt-5: (1000/1M * 4) + (1000/1M * 12) = 0.004 + 0.012 = 0.016
        assert result["request"]["cost"]["total"] == pytest.approx(0.016)

    def test_budget_alert(self, capsys):
        """Test that a budget alert is printed when the daily limit is exceeded."""
        tracker = GPT5CostTracker(budget_limit=0.01)
        tracker.track_request("gpt-5", 10000, 1000)  # Cost > $0.01
        captured = capsys.readouterr()
        assert "BUDGET ALERT" in captured.out

    def test_history_loading_and_saving(self):
        """Test that usage history is loaded from and saved to a log file."""
        with TemporaryDirectory() as td:
            log_file = Path(td) / "history.json"

            # First session
            tracker1 = GPT5CostTracker(log_file=str(log_file))
            tracker1.track_request("gpt-5-mini", 1000, 500)

            # Second session
            tracker2 = GPT5CostTracker(log_file=str(log_file))
            assert len(tracker2.history) == 1
            assert tracker2.history[0]["model"] == "gpt-5-mini"

            tracker2.track_request("gpt-5-nano", 2000, 1000)
            assert len(tracker2.history) == 2

    def test_get_periodic_costs(self):
        """Test daily, weekly, and monthly cost calculations."""
        with TemporaryDirectory() as td:
            log_file = Path(td) / "log.json"
            tracker = GPT5CostTracker(log_file=str(log_file))

            # Mock history
            now = datetime.now()
            eight_days_ago = (now - timedelta(days=8)).isoformat()
            two_days_ago = (now - timedelta(days=2)).isoformat()
            last_month = (now - timedelta(days=35)).isoformat()

            tracker.history = [
                {"timestamp": now.isoformat(), "cost": {"total": 1.0}},
                {"timestamp": two_days_ago, "cost": {"total": 2.0}},
                {"timestamp": eight_days_ago, "cost": {"total": 3.0}},
                {"timestamp": last_month, "cost": {"total": 4.0}},
            ]

            assert tracker.get_daily_cost() == pytest.approx(1.0)
            assert tracker.get_weekly_cost() == pytest.approx(3.0)  # 1.0 + 2.0

            # The monthly cost should only include entries from the current calendar month.
            # Based on the mock data, this is the sum of `now` and `two_days_ago`.
            # The entry from `eight_days_ago` might be in the previous month.
            monthly_cost = 0.0
            if now.month == (now - timedelta(days=2)).month:
                monthly_cost += 2.0
            if now.month == now.month:
                monthly_cost += 1.0

            assert tracker.get_monthly_cost() == pytest.approx(monthly_cost)

    def test_get_cost_by_model_and_type(self):
        """Test cost aggregation by model and request type."""
        tracker = GPT5CostTracker()
        tracker.track_request("gpt-5", 1000, 1000, request_type="chat")
        tracker.track_request("gpt-5", 2000, 2000, request_type="analysis")
        tracker.track_request("gpt-5-mini", 3000, 3000, request_type="chat")

        by_model = tracker.get_cost_by_model()
        assert "gpt-5" in by_model
        assert "gpt-5-mini" in by_model
        assert by_model["gpt-5"] > by_model["gpt-5-mini"]

        by_type = tracker.get_cost_by_type()
        assert "chat" in by_type
        assert "analysis" in by_type
        assert by_type["chat"] > by_type["analysis"]

    def test_print_summary_and_report(self, capsys):
        """Test that summary and report printing functions execute without errors."""
        tracker = GPT5CostTracker(budget_limit=1.0)
        tracker.track_request("gpt-5", 1000, 1000)

        tracker.print_session_summary()
        captured_summary = capsys.readouterr()
        assert "Session Summary" in captured_summary.out
        assert "Budget Status" in captured_summary.out

        tracker.print_detailed_report()
        captured_report = capsys.readouterr()
        assert "GPT-5 Cost Report" in captured_report.out

    def test_export_to_csv(self):
        """Test exporting cost history to a CSV file."""
        with TemporaryDirectory() as td:
            csv_path = Path(td) / "costs.csv"
            # Use the global tracker to ensure state is clean
            tracker = get_tracker()
            tracker.history.clear()  # Explicitly clear history for this test
            tracker.track_request("gpt-5", 1000, 1000)
            tracker.track_request("gpt-5-mini", 2000, 2000)

            tracker.export_to_csv(output_path=str(csv_path))

            assert csv_path.exists()
            content = csv_path.read_text()
            assert "timestamp,model,request_type" in content
            assert "gpt-5" in content
            assert "gpt-5-mini" in content
            # 2 data rows + 1 header row
            assert len(content.strip().split("\n")) == 3

    def test_get_tracker_singleton(self):
        """Test that get_tracker returns a singleton instance."""
        tracker1 = get_tracker()
        tracker2 = get_tracker()
        assert tracker1 is tracker2

        tracker1.track_request("gpt-5", 100, 100)
        assert tracker2.total_cost > 0

    def test_track_gpt5_request_convenience_function(self):
        """Test the global track_gpt5_request convenience function."""
        usage = {"prompt_tokens": 100, "completion_tokens": 200, "cached_tokens": 50}
        track_gpt5_request(model="gpt-5", usage=usage, request_type="test_conv")

        tracker = get_tracker()
        assert tracker.total_cost > 0
        # The convenience function defaults to 'chat' if not specified, let's test that
        track_gpt5_request(model="gpt-5", usage=usage)
        assert tracker.history[-1]["request_type"] == "chat"

    def test_load_history_handles_errors(self):
        """Test that history loading handles JSON errors and missing files."""
        with TemporaryDirectory() as td:
            # Test with non-existent file
            tracker = GPT5CostTracker(log_file=str(Path(td) / "nonexistent.json"))
            assert tracker.history == []

            # Test with invalid JSON file
            invalid_json_path = Path(td) / "invalid.json"
            invalid_json_path.write_text("{invalid json}")
            tracker_invalid = GPT5CostTracker(log_file=str(invalid_json_path))
            assert tracker_invalid.history == []
