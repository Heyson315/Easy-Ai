#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Benchmark Script for M365 Security Toolkit

Tests key functionality with timing and memory monitoring to identify bottlenecks.
Run with: python scripts/run_performance_benchmark.py [--baseline]

Features:
- Benchmarks critical operations (CSV cleaning, report generation, dashboard creation)
- Measures execution time and memory usage
- Compares against baseline if available
- Generates performance report
"""

import sys
import time
import tracemalloc
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules to benchmark
try:
    import pandas as pd
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def benchmark_operation(operation_name: str, operation_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Benchmark a single operation with timing and memory tracking.

    Returns:
        Dict with operation name, time_seconds, memory_mb, and success status
    """
    print(f"\n🔬 Benchmarking: {operation_name}")
    print("-" * 60)

    # Start memory tracking
    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        _operation_result = operation_func(*args, **kwargs)
        operation_succeeded = True
        error_message = None
    except Exception as operation_error:
        print(f"❌ Error: {operation_error}")
        _operation_result = None
        operation_succeeded = False
        error_message = str(operation_error)

    # End timing and memory tracking
    end_time = time.perf_counter()
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_time = end_time - start_time
    peak_memory_mb = peak_memory / (1024 * 1024)

    print(f"⏱️  Time: {elapsed_time:.4f}s")
    print(f"💾 Peak Memory: {peak_memory_mb:.2f}MB")
    print(f"✅ Status: {'Success' if operation_succeeded else 'Failed'}")

    return {
        "name": operation_name,
        "time_seconds": elapsed_time,
        "memory_mb": peak_memory_mb,
        "success": operation_succeeded,
        "error": error_message,
    }


def create_test_csv(file_path: Path, rows: int = 1000) -> None:
    """Create a test CSV file for benchmarking."""
    import csv

    with open(file_path, "w", encoding="utf-8", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Resource Path", "Item Type", "Permission", "User Name", "User Email"])
        for row_index in range(rows):
            csv_writer.writerow(
                [
                    f"/sites/test/path{row_index}",
                    "File" if row_index % 2 == 0 else "Folder",
                    "Full Control" if row_index % 3 == 0 else "Read",
                    f"User {row_index}",
                    f"user{row_index}@example.com",
                ]
            )


def create_test_audit_json(file_path: Path, controls: int = 100) -> None:
    """Create a test audit JSON file for benchmarking."""
    import json

    audit_data = []
    for control_index in range(controls):
        audit_data.append(
            {
                "ControlId": f"CIS-{control_index+1}",
                "Title": f"Test Control {control_index+1}",
                "Severity": ["High", "Medium", "Low"][control_index % 3],
                "Status": ["Pass", "Fail", "Manual"][control_index % 3],
                "Expected": "Enabled",
                "Actual": "Enabled" if control_index % 3 == 0 else "Disabled",
                "Evidence": "Test evidence",
                "Reference": "https://example.com",
                "Timestamp": "2025-01-01T00:00:00Z",
            }
        )

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(audit_data, json_file, indent=2)


def run_performance_benchmarks() -> Dict[str, Any]:
    """Run comprehensive performance benchmarks."""
    print("=" * 60)
    print("🚀 M365 Security Toolkit - Performance Benchmarks")
    print("=" * 60)

    benchmark_results = []

    with TemporaryDirectory() as temp_directory:
        temp_path = Path(temp_directory)

        # 1. Benchmark CSV cleaning
        from scripts.clean_csv import clean_csv

        test_csv_input_path = temp_path / "test_input.csv"
        test_csv_output_path = temp_path / "test_output.csv"
        create_test_csv(test_csv_input_path, rows=5000)

        benchmark_result = benchmark_operation(
            "CSV Cleaning (5000 rows)",
            clean_csv,
            test_csv_input_path,
            test_csv_output_path,
        )
        benchmark_results.append(benchmark_result)

        # 2. Benchmark M365 CIS report generation
        from scripts.m365_cis_report import build_report

        test_json_path = temp_path / "test_audit.json"
        test_excel_path = temp_path / "test_report.xlsx"
        create_test_audit_json(test_json_path, controls=200)

        benchmark_result = benchmark_operation(
            "M365 CIS Excel Report (200 controls)",
            build_report,
            test_json_path,
            test_excel_path,
        )
        benchmark_results.append(benchmark_result)

        # 3. Benchmark statistics calculation
        from scripts.generate_security_dashboard import calculate_statistics

        import json

        with open(test_json_path, "r") as json_file:
            audit_data = json.load(json_file)

        benchmark_result = benchmark_operation(
            "Statistics Calculation (200 controls)",
            calculate_statistics,
            audit_data,
        )
        benchmark_results.append(benchmark_result)

        # 4. Benchmark SharePoint summary generation
        try:
            from src.integrations.sharepoint_connector import build_summaries

            # Create test DataFrame
            permissions_dataframe = pd.read_csv(test_csv_output_path)
            benchmark_result = benchmark_operation(
                "SharePoint Summaries (5000 rows)",
                build_summaries,
                permissions_dataframe,
            )
            benchmark_results.append(benchmark_result)
        except ImportError:
            print("⚠️  Skipping SharePoint benchmark (module not available)")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Benchmark Summary")
    print("=" * 60)

    total_execution_time = sum(result["time_seconds"] for result in benchmark_results)
    max_peak_memory = max(result["memory_mb"] for result in benchmark_results)
    successful_operations_count = sum(1 for result in benchmark_results if result["success"])

    print(f"\nTotal Operations: {len(benchmark_results)}")
    print(f"Successful: {successful_operations_count}/{len(benchmark_results)}")
    print(f"Total Time: {total_execution_time:.4f}s")
    print(f"Peak Memory: {max_peak_memory:.2f}MB")

    print("\n📋 Detailed Results:")
    for result in benchmark_results:
        status_indicator = "✅" if result["success"] else "❌"
        print(f"{status_indicator} {result['name']:45} {result['time_seconds']:8.4f}s  {result['memory_mb']:8.2f}MB")

    # Check for performance issues
    print("\n🔍 Performance Analysis:")
    slow_operations = [result for result in benchmark_results if result["time_seconds"] > 1.0]
    if slow_operations:
        print("⚠️  Slow operations detected (>1.0s):")
        for result in slow_operations:
            print(f"   - {result['name']}: {result['time_seconds']:.4f}s")
    else:
        print("✅ All operations completed in under 1 second")

    high_memory_operations = [result for result in benchmark_results if result["memory_mb"] > 100]
    if high_memory_operations:
        print("⚠️  High memory usage detected (>100MB):")
        for result in high_memory_operations:
            print(f"   - {result['name']}: {result['memory_mb']:.2f}MB")
    else:
        print("✅ All operations used less than 100MB")

    return {
        "results": benchmark_results,
        "total_time": total_execution_time,
        "peak_memory": max_peak_memory,
        "success_rate": successful_operations_count / len(benchmark_results) if benchmark_results else 0,
    }


if __name__ == "__main__":
    try:
        benchmark_data = run_performance_benchmarks()

        # Exit with success if all benchmarks passed
        if benchmark_data["success_rate"] == 1.0:
            print("\n✅ All benchmarks passed!")
            sys.exit(0)
        else:
            print(f"\n⚠️  Some benchmarks failed ({benchmark_data['success_rate']:.0%} success rate)")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Benchmark suite failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
