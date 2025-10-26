"""Tests for the performance benchmark script."""

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_performance_benchmark import (
    generate_test_csv,
    generate_test_cis_json,
    benchmark_csv_cleaning,
    benchmark_cis_report_generation,
    benchmark_sharepoint_processing,
    run_all_benchmarks,
    save_results,
)


def test_generate_test_csv():
    """Test CSV generation for benchmarking."""
    with TemporaryDirectory() as td:
        td_path = Path(td)
        csv_path = td_path / "test.csv"

        generate_test_csv(csv_path, num_rows=50)

        assert csv_path.exists()
        content = csv_path.read_text()

        # Should have comment line
        assert "# This is a comment line" in content
        # Should have headers
        assert "Resource Path" in content
        # Should have data rows
        assert "user" in content.lower()


def test_generate_test_cis_json():
    """Test CIS JSON generation for benchmarking."""
    with TemporaryDirectory() as td:
        td_path = Path(td)
        json_path = td_path / "test.json"

        generate_test_cis_json(json_path, num_controls=10)

        assert json_path.exists()
        data = json.loads(json_path.read_text())

        assert len(data) == 10
        assert "ControlId" in data[0]
        assert "Title" in data[0]
        assert "Severity" in data[0]


def test_benchmark_csv_cleaning():
    """Test CSV cleaning benchmark."""
    result = benchmark_csv_cleaning("small")

    assert result["operation"] == "csv_cleaning"
    assert result["size"] == "small"
    assert result["rows"] == 100
    assert "elapsed_seconds" in result
    assert "rows_per_second" in result
    assert result["elapsed_seconds"] > 0
    assert result["rows_per_second"] > 0


def test_benchmark_cis_report_generation():
    """Test CIS report generation benchmark."""
    result = benchmark_cis_report_generation("small")

    assert result["operation"] == "cis_report_generation"
    assert result["size"] == "small"
    assert result["controls"] == 15
    assert "elapsed_seconds" in result
    assert "controls_per_second" in result
    assert "output_file_size_kb" in result
    assert result["elapsed_seconds"] > 0


def test_benchmark_sharepoint_processing():
    """Test SharePoint processing benchmark."""
    result = benchmark_sharepoint_processing("small")

    assert result["operation"] == "sharepoint_processing"
    assert result["size"] == "small"
    assert result["rows"] == 100
    assert "elapsed_seconds" in result
    assert "rows_per_second" in result
    assert result["elapsed_seconds"] > 0


def test_run_all_benchmarks():
    """Test running all benchmarks."""
    results = run_all_benchmarks(size="small", iterations=1)

    assert len(results) == 3
    assert all("benchmark" in r for r in results)
    assert all("avg_elapsed_seconds" in r for r in results)
    assert all("min_elapsed_seconds" in r for r in results)
    assert all("max_elapsed_seconds" in r for r in results)


def test_save_results():
    """Test saving benchmark results."""
    with TemporaryDirectory() as td:
        td_path = Path(td)
        output_path = td_path / "results.json"

        test_results = [
            {"benchmark": "Test", "avg_elapsed_seconds": 1.0, "min_elapsed_seconds": 0.9, "max_elapsed_seconds": 1.1}
        ]

        save_results(test_results, output_path)

        assert output_path.exists()
        saved_data = json.loads(output_path.read_text())
        assert len(saved_data) == 1
        assert saved_data[0]["benchmark"] == "Test"
