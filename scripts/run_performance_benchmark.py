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
from typing import Any, Callable, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules to benchmark
try:
    import pandas as pd
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def benchmark_operation(name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Benchmark a single operation with timing and memory tracking.

    Returns:
        Dict with operation name, time_seconds, memory_mb, and success status
    """
    print(f"\n🔬 Benchmarking: {name}")
    print("-" * 60)

    # Start memory tracking
    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        _ = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        print(f"❌ Error: {e}")
        _ = None
        success = False
        error = str(e)

    # End timing and memory tracking
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed = end_time - start_time
    memory_mb = peak / (1024 * 1024)

    print(f"⏱️  Time: {elapsed:.4f}s")
    print(f"💾 Peak Memory: {memory_mb:.2f}MB")
    print(f"✅ Status: {'Success' if success else 'Failed'}")

    return {
        "name": name,
        "time_seconds": elapsed,
        "memory_mb": memory_mb,
        "success": success,
        "error": error,
    }


def create_test_csv(path: Path, rows: int = 1000) -> None:
    """Create a test CSV file for benchmarking."""
    import csv

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Resource Path", "Item Type", "Permission", "User Name", "User Email"])
        for i in range(rows):
            writer.writerow(
                [
                    f"/sites/test/path{i}",
                    "File" if i % 2 == 0 else "Folder",
                    "Full Control" if i % 3 == 0 else "Read",
                    f"User {i}",
                    f"user{i}@example.com",
                ]
            )


def create_test_audit_json(path: Path, controls: int = 100) -> None:
    """Create a test audit JSON file for benchmarking."""
    import json

    data = []
    for i in range(controls):
        data.append(
            {
                "ControlId": f"CIS-{i + 1}",
                "Title": f"Test Control {i + 1}",
                "Severity": ["High", "Medium", "Low"][i % 3],
                "Status": ["Pass", "Fail", "Manual"][i % 3],
                "Expected": "Enabled",
                "Actual": "Enabled" if i % 3 == 0 else "Disabled",
                "Evidence": "Test evidence",
                "Reference": "https://example.com",
                "Timestamp": "2025-01-01T00:00:00Z",
            }
        )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_performance_benchmarks() -> Dict[str, Any]:
    """Run comprehensive performance benchmarks."""
    print("=" * 60)
    print("🚀 M365 Security Toolkit - Performance Benchmarks")
    print("=" * 60)

    results = []

    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 1. Benchmark CSV cleaning
        from scripts.clean_csv import clean_csv

        test_csv_input = tmp_path / "test_input.csv"
        test_csv_output = tmp_path / "test_output.csv"
        create_test_csv(test_csv_input, rows=5000)

        result = benchmark_operation(
            "CSV Cleaning (5000 rows)",
            clean_csv,
            test_csv_input,
            test_csv_output,
        )
        results.append(result)

        # 2. Benchmark M365 CIS report generation
        from scripts.m365_cis_report import build_report

        test_json = tmp_path / "test_audit.json"
        test_excel = tmp_path / "test_report.xlsx"
        create_test_audit_json(test_json, controls=200)

        result = benchmark_operation(
            "M365 CIS Excel Report (200 controls)",
            build_report,
            test_json,
            test_excel,
        )
        results.append(result)

        # 3. Benchmark statistics calculation
        import json

        from scripts.generate_security_dashboard import calculate_statistics

        with open(test_json, "r") as f:
            audit_data = json.load(f)

        result = benchmark_operation(
            "Statistics Calculation (200 controls)",
            calculate_statistics,
            audit_data,
        )
        results.append(result)

        # 4. Benchmark SharePoint summary generation
        try:
            from src.integrations.sharepoint_connector import build_summaries

            # Create test DataFrame
            df = pd.read_csv(test_csv_output)
            result = benchmark_operation(
                "SharePoint Summaries (5000 rows)",
                build_summaries,
                df,
            )
            results.append(result)
        except ImportError:
            print("⚠️  Skipping SharePoint benchmark (module not available)")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Benchmark Summary")
    print("=" * 60)

    total_time = sum(r["time_seconds"] for r in results)
    total_memory = max(r["memory_mb"] for r in results)
    success_count = sum(1 for r in results if r["success"])

    print(f"\nTotal Operations: {len(results)}")
    print(f"Successful: {success_count}/{len(results)}")
    print(f"Total Time: {total_time:.4f}s")
    print(f"Peak Memory: {total_memory:.2f}MB")

    print("\n📋 Detailed Results:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"{status} {r['name']:45} {r['time_seconds']:8.4f}s  {r['memory_mb']:8.2f}MB")

    # Check for performance issues
    print("\n🔍 Performance Analysis:")
    slow_operations = [r for r in results if r["time_seconds"] > 1.0]
    if slow_operations:
        print("⚠️  Slow operations detected (>1.0s):")
        for r in slow_operations:
            print(f"   - {r['name']}: {r['time_seconds']:.4f}s")
    else:
        print("✅ All operations completed in under 1 second")

    high_memory = [r for r in results if r["memory_mb"] > 100]
    if high_memory:
        print("⚠️  High memory usage detected (>100MB):")
        for r in high_memory:
            print(f"   - {r['name']}: {r['memory_mb']:.2f}MB")
    else:
        print("✅ All operations used less than 100MB")

    return {
        "results": results,
        "total_time": total_time,
        "peak_memory": total_memory,
        "success_rate": success_count / len(results) if results else 0,
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
