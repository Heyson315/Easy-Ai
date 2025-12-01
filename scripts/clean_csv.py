#!/usr/bin/env python3
"""
CSV Cleaning Utility

Removes comment lines, blank lines, and repeated headers from CSV files.
Normalizes whitespace and handles UTF-8 BOM from various sources.

Usage:
    python scripts/clean_csv.py --input "raw.csv" --output "clean.csv"

Optimizations:
    - Single-pass streaming processing
    - Memory-efficient generator-based filtering
    - In-place cell normalization
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Generator

DEFAULT_INPUT = Path("data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv")
DEFAULT_OUTPUT = Path("data/processed/sharepoint_permissions_clean.csv")


def clean_csv(in_path: Path, out_path: Path) -> dict:
    """
    Clean CSV file using single-pass streaming processing.

    Args:
        in_path: Input CSV file path
        out_path: Output CSV file path

    Returns:
        Dictionary containing cleaning statistics

    Optimizations:
        - Single-pass processing (no intermediate list storage)
        - Streaming I/O for memory efficiency
        - In-place cell stripping to reduce allocations
    """
    stats: dict = {
        "input_lines": 0,
        "output_rows": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "skipped_repeated_headers": 0,
        "header": None,
    }

    # Single-pass processing: filter and write simultaneously
    with in_path.open("r", encoding="utf-8-sig", errors="replace") as fin, out_path.open(
        "w", encoding="utf-8", newline=""
    ) as fout:

        writer = csv.writer(fout, lineterminator="\n")
        header = None

        # Generator for filtered lines (memory-efficient)
        def filtered_lines_gen() -> Generator[str, None, None]:
            for raw_line in fin:
                stats["input_lines"] += 1
                stripped = raw_line.strip()
                if not stripped:
                    stats["blank_lines"] += 1
                    continue
                if stripped.startswith("#"):
                    stats["comment_lines"] += 1
                    continue
                yield raw_line

        # Process CSV from filtered generator
        reader = csv.reader(filtered_lines_gen())

        for row in reader:
            # Normalize whitespace in each cell (in-place for efficiency)
            for i in range(len(row)):
                row[i] = row[i].strip()

            if header is None:
                header = row
                # Strip potential BOM from first header col if still present
                if header and header[0].startswith("\ufeff"):
                    header[0] = header[0].lstrip("\ufeff")
                stats["header"] = header
                writer.writerow(header)
                continue

            # Skip repeated header rows
            if row == header:
                stats["skipped_repeated_headers"] += 1
                continue

            # Guard against BOM in first data column
            if row and row[0].startswith("\ufeff"):
                row[0] = row[0].lstrip("\ufeff")

            writer.writerow(row)
            stats["output_rows"] += 1

    return stats


def main() -> None:
    """Parse arguments and execute CSV cleaning."""
    parser = argparse.ArgumentParser(description="Clean CSV file by removing comments, blank lines, and BOM")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV file path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV file path")
    args = parser.parse_args()

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    stats = clean_csv(args.input, args.output)

    print("✅ CSV cleaned successfully:")
    print(f"  Input lines:            {stats['input_lines']}")
    print(f"  Comment lines removed:  {stats['comment_lines']}")
    print(f"  Blank lines removed:    {stats['blank_lines']}")
    print(f"  Repeated headers skip:  {stats['skipped_repeated_headers']}")
    print(f"  Output data rows:       {stats['output_rows']}")
    print(f"  Header:                 {stats['header']}")
    print(f"  Output file:            {args.output}")


if __name__ == "__main__":
    main()
