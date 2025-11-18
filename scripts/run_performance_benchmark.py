#!/usr/bin/env python3
"""
Performance benchmark script for M365 Security & SharePoint Analysis Toolkit.

This script benchmarks the performance of key operations:
1. CSV cleaning (clean_csv.py)
2. SharePoint report generation (sharepoint_connector.py)
3. M365 CIS report generation (m365_cis_report.py)

Usage:
    python scripts/run_performance_benchmark.py
    python scripts/run_performance_benchmark.py --size large
    python scripts/run_performance_benchmark.py --output benchmark_results.json
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Any
import csv

# Import the functions to benchmark
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.clean_csv import clean_csv
from scripts.m365_cis_report import build_report

# Dataset size configuration
CSV_ROWS_BY_SIZE = {"small": 100, "medium": 1000, "large": 10000}
CIS_CONTROLS_BY_SIZE = {"small": 15, "medium": 50, "large": 150}


def generate_test_csv(path: Path, num_rows: int = 1000) -> None:
    """Generate a test CSV file for benchmarking."""
    headers = [
        "Resource Path",
        "Item Type",
        "Permission",
        "User Name",
        "User Email",
        "User Or Group Type",
        "Link ID",
        "Link Type",
        "AccessViaLinkID",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # Add some comment lines and blank lines to test cleaning
        f.write("# This is a comment line\n")
        f.write("\n")

        # Write header
        writer.writerow(headers)

        # Write data rows
        for i in range(num_rows):
            row = [
                f"sites/dept{i % 10}/documents/file{i}.pdf",
                "pdf" if i % 3 == 0 else "docx" if i % 3 == 1 else "xlsx",
                "Contribute" if i % 2 == 0 else "Read",
                f"User {i % 100}",
                f"user{i % 100}@example.com",
                "Internal" if i % 4 != 0 else "External",
                f"link{i}" if i % 5 == 0 else "",
                "Direct" if i % 5 == 0 else "",
                f"access{i}" if i % 7 == 0 else "",
            ]
            writer.writerow(row)

            # Add some duplicate headers to test cleaning
            if i > 0 and i % 500 == 0:
                writer.writerow(headers)


def generate_test_cis_json(path: Path, num_controls: int = 15) -> None:
    """Generate a test CIS audit JSON file for benchmarking."""
    controls = []

    statuses = ["Pass", "Fail", "Manual", "Not Applicable"]
    severities = ["Critical", "High", "Medium", "Low"]

    for i in range(num_controls):
        control = {
            "ControlId": f"CIS-{i+1}.{(i % 5) + 1}",
            "Title": f"Test Control {i+1}: Security Configuration Check",
            "Severity": severities[i % len(severities)],
            "Expected": f"Expected configuration value for control {i+1}",
            "Actual": f"Actual configuration value for control {i+1}",
            "Status": statuses[i % len(statuses)],
            "Evidence": f"Evidence data for control {i+1}" * 10,  # Make it longer
            "Reference": f"https://docs.microsoft.com/cis-control-{i+1}",
            "Timestamp": f"2025-10-26T09:00:{i:02d}Z",
        }
        controls.append(control)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(controls, f, indent=2)


def benchmark_csv_cleaning(size: str) -> Dict[str, Any]:
    """Benchmark CSV cleaning operation."""
    num_rows = CSV_ROWS_BY_SIZE.get(size, 1000)

    with TemporaryDirectory() as td:
        td_path = Path(td)
        input_csv = td_path / "test_input.csv"
        output_csv = td_path / "test_output.csv"

        # Generate test data
        generate_test_csv(input_csv, num_rows)

        # Benchmark
        start_time = time.perf_counter()
        stats = clean_csv(input_csv, output_csv)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        return {
            "operation": "csv_cleaning",
            "size": size,
            "rows": num_rows,
            "elapsed_seconds": round(elapsed_time, 4),
            "rows_per_second": round(num_rows / elapsed_time, 2),
            "stats": stats,
        }


def benchmark_cis_report_generation(size: str) -> Dict[str, Any]:
    """Benchmark M365 CIS report generation."""
    num_controls = CIS_CONTROLS_BY_SIZE.get(size, 15)

    with TemporaryDirectory() as td:
        td_path = Path(td)
        input_json = td_path / "test_audit.json"
        output_xlsx = td_path / "test_report.xlsx"

        # Generate test data
        generate_test_cis_json(input_json, num_controls)

        # Benchmark
        start_time = time.perf_counter()
        build_report(input_json, output_xlsx)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        # Get file size
        file_size = output_xlsx.stat().st_size

        return {
            "operation": "cis_report_generation",
            "size": size,
            "controls": num_controls,
            "elapsed_seconds": round(elapsed_time, 4),
            "controls_per_second": round(num_controls / elapsed_time, 2),
            "output_file_size_kb": round(file_size / 1024, 2),
        }


def benchmark_sharepoint_processing(size: str) -> Dict[str, Any]:
    """Benchmark SharePoint CSV processing and report generation."""
    num_rows = CSV_ROWS_BY_SIZE.get(size, 1000)

    with TemporaryDirectory() as td:
        td_path = Path(td)
        input_csv = td_path / "test_sharepoint.csv"
        cleaned_csv = td_path / "test_sharepoint_clean.csv"

        # Generate test data
        generate_test_csv(input_csv, num_rows)

        # Benchmark cleaning + processing
        start_time = time.perf_counter()
        clean_csv(input_csv, cleaned_csv)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        return {
            "operation": "sharepoint_processing",
            "size": size,
            "rows": num_rows,
            "elapsed_seconds": round(elapsed_time, 4),
            "rows_per_second": round(num_rows / elapsed_time, 2),
        }


def run_all_benchmarks(size: str = "medium", iterations: int = 3) -> List[Dict[str, Any]]:
    """Run all benchmarks multiple times and collect results."""
    all_results = []

    benchmarks = [
        ("CSV Cleaning", benchmark_csv_cleaning),
        ("CIS Report Generation", benchmark_cis_report_generation),
        ("SharePoint Processing", benchmark_sharepoint_processing),
    ]

    print(f"Running performance benchmarks (size={size}, iterations={iterations})...\n")

    for name, benchmark_func in benchmarks:
        print(f"Benchmarking: {name}")
        iteration_results = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")
            result = benchmark_func(size)
            iteration_results.append(result)
            print(f"✓ {result['elapsed_seconds']}s")

        # Calculate statistics
        elapsed_times = [r["elapsed_seconds"] for r in iteration_results]
        avg_time = sum(elapsed_times) / len(elapsed_times)
        min_time = min(elapsed_times)
        max_time = max(elapsed_times)

        summary = {
            "benchmark": name,
            "operation": iteration_results[0]["operation"],
            "size": size,
            "iterations": iterations,
            "avg_elapsed_seconds": round(avg_time, 4),
            "min_elapsed_seconds": round(min_time, 4),
            "max_elapsed_seconds": round(max_time, 4),
            "all_iterations": iteration_results,
        }

        all_results.append(summary)
        print(f"  Average: {avg_time:.4f}s (min: {min_time:.4f}s, max: {max_time:.4f}s)\n")

    return all_results


def print_summary(results: List[Dict[str, Any]]) -> None:
    """Print a summary table of benchmark results."""
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"{'Benchmark':<30} {'Avg Time':<15} {'Min Time':<15} {'Max Time':<15}")
    print("-" * 80)

    for result in results:
        print(
            f"{result['benchmark']:<30} "
            f"{result['avg_elapsed_seconds']:<15.4f} "
            f"{result['min_elapsed_seconds']:<15.4f} "
            f"{result['max_elapsed_seconds']:<15.4f}"
        )

    print("=" * 80)


def save_results(results: List[Dict[str, Any]], output_path: Path) -> None:
    """Save benchmark results to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")


def main():
    """Main entry point for the benchmark script."""
    parser = argparse.ArgumentParser(
        description="Performance benchmark for M365 Security & SharePoint Analysis Toolkit"
    )
    parser.add_argument(
        "--size",
        choices=["small", "medium", "large"],
        default="medium",
        help="Dataset size to use for benchmarking (default: medium)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations per benchmark (default: 3)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/benchmark_results.json"),
        help="Output file for benchmark results (default: output/benchmark_results.json)",
    )

    args = parser.parse_args()

    # Run benchmarks
    results = run_all_benchmarks(size=args.size, iterations=args.iterations)

    # Print summary
    print_summary(results)

    # Save results
    save_results(results, args.output)

    print("\nBenchmark completed successfully!")


if __name__ == "__main__":
    main()
