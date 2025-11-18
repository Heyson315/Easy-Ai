"""
Test performance benchmarking script and optimizations.

These tests validate that performance optimizations work correctly
and maintain expected behavior.
"""

import json
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_benchmark_script_imports():
    """Test that all benchmark dependencies can be imported."""
    try:
        from scripts.run_performance_benchmark import benchmark_operation, create_test_csv, create_test_audit_json

        assert callable(benchmark_operation)
        assert callable(create_test_csv)
        assert callable(create_test_audit_json)
    except ImportError as e:
        pytest.fail(f"Failed to import benchmark modules: {e}")


def test_create_test_csv():
    """Test test CSV creation for benchmarking."""
    from scripts.run_performance_benchmark import create_test_csv

    with TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test.csv"
        create_test_csv(test_path, rows=100)

        assert test_path.exists()

        # Verify structure
        with open(test_path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert len(header) == 5
            assert "Resource Path" in header

            # Count rows
            row_count = sum(1 for _ in reader)
            assert row_count == 100


def test_create_test_audit_json():
    """Test test audit JSON creation for benchmarking."""
    from scripts.run_performance_benchmark import create_test_audit_json

    with TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test.json"
        create_test_audit_json(test_path, controls=50)

        assert test_path.exists()

        # Verify structure
        with open(test_path, "r") as f:
            data = json.load(f)

        assert len(data) == 50
        assert "ControlId" in data[0]
        assert "Title" in data[0]
        assert "Severity" in data[0]
        assert "Status" in data[0]


def test_benchmark_operation():
    """Test benchmark_operation function."""
    from scripts.run_performance_benchmark import benchmark_operation

    def simple_function():
        """Simple test function."""
        return sum(range(1000))

    result = benchmark_operation("Test Operation", simple_function)

    assert result["name"] == "Test Operation"
    assert result["success"] is True
    assert result["time_seconds"] >= 0
    assert result["memory_mb"] >= 0
    assert result["error"] is None


def test_benchmark_operation_with_error():
    """Test benchmark_operation with failing function."""
    from scripts.run_performance_benchmark import benchmark_operation

    def failing_function():
        """Function that raises an error."""
        raise ValueError("Test error")

    result = benchmark_operation("Failing Operation", failing_function)

    assert result["name"] == "Failing Operation"
    assert result["success"] is False
    assert result["error"] is not None
    assert "Test error" in result["error"]


def test_clean_csv_optimization():
    """Test that optimized clean_csv maintains functionality."""
    from scripts.clean_csv import clean_csv

    with TemporaryDirectory() as tmpdir:
        # Create test CSV with comments and blank lines
        input_path = Path(tmpdir) / "input.csv"
        output_path = Path(tmpdir) / "output.csv"

        with open(input_path, "w", encoding="utf-8") as f:
            f.write("# Comment line\n")
            f.write("Header1,Header2,Header3\n")
            f.write("\n")  # Blank line
            f.write("Value1,Value2,Value3\n")
            f.write("# Another comment\n")
            f.write("Value4,Value5,Value6\n")

        stats = clean_csv(input_path, output_path)

        # Verify stats
        assert stats["input_lines"] == 6
        assert stats["comment_lines"] == 2
        assert stats["blank_lines"] == 1
        assert stats["output_rows"] == 2  # Data rows only
        assert stats["header"] == ["Header1", "Header2", "Header3"]

        # Verify output file
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) == 3  # Header + 2 data rows
        assert rows[0] == ["Header1", "Header2", "Header3"]
        assert rows[1] == ["Value1", "Value2", "Value3"]
        assert rows[2] == ["Value4", "Value5", "Value6"]


def test_sharepoint_connector_optimization():
    """Test that optimized sharepoint_connector maintains functionality."""
    import pandas as pd
    from src.integrations.sharepoint_connector import build_summaries

    # Create test DataFrame
    data = {
        "Resource Path": ["/path1", "/path2", "/path3"],
        "Item Type": ["File", "Folder", "File"],
        "Permission": ["Read", "Write", "Read"],
        "User Name": ["User1", "User2", "User1"],
        "User Email": ["user1@test.com", "user2@test.com", "user1@test.com"],
    }
    df = pd.DataFrame(data)

    summaries = build_summaries(df)

    # Verify summaries
    assert "by_item_type" in summaries
    assert "by_permission" in summaries
    assert "top_users" in summaries
    assert "top_resources" in summaries

    # Check by_item_type
    assert len(summaries["by_item_type"]) == 2  # File and Folder

    # Check by_permission
    assert len(summaries["by_permission"]) == 2  # Read and Write

    # Check top_users
    assert len(summaries["top_users"]) == 2  # Two users


def test_dashboard_statistics_calculation():
    """Test that dashboard statistics calculation is correct."""
    from scripts.generate_security_dashboard import calculate_statistics

    results = [
        {"Status": "Pass", "Severity": "High"},
        {"Status": "Fail", "Severity": "High"},
        {"Status": "Fail", "Severity": "Medium"},
        {"Status": "Manual", "Severity": "Low"},
        {"Status": "Pass", "Severity": "Low"},
    ]

    stats = calculate_statistics(results)

    assert stats["total"] == 5
    assert stats["pass"] == 2
    assert stats["fail"] == 2
    assert stats["manual"] == 1
    assert stats["pass_rate"] == 40.0
    assert stats["fail_rate"] == 40.0
    assert stats["by_severity"]["High"] == 2
    assert stats["by_severity"]["Medium"] == 1
    assert stats["by_severity"]["Low"] == 2
    assert stats["failed_by_severity"]["High"] == 1
    assert stats["failed_by_severity"]["Medium"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
