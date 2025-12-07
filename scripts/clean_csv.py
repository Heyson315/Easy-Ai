#!/usr/bin/env python3
"""
Clean a CSV file by removing comment lines (# ...), blank lines, and repeated headers.
Also normalizes whitespace around commas and trims field whitespace.

Usage (PowerShell):
  python scripts/clean_csv.py --input "data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv" \\
    --output "data/processed/sharepoint_permissions_clean.csv"

If --input/--output are omitted, defaults will be used for the SharePoint CSV.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

DEFAULT_INPUT = Path("data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv")
DEFAULT_OUTPUT = Path("data/processed/sharepoint_permissions_clean.csv")


def clean_csv(in_path: Path, out_path: Path) -> dict:
    """
    Clean CSV file in a single pass for better performance.

    Optimizations:
    - Single-pass processing (no intermediate list storage)
    - Streaming I/O for memory efficiency
    - In-place cell stripping to reduce allocations
    """
    in_path = Path(in_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stats = {
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

        # Create a generator that yields filtered lines
        def filtered_lines_gen():
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    args = parser.parse_args()

    stats = clean_csv(args.input, args.output)

    print("CSV cleaned successfully:")
    print(f"  Input lines:            {stats['input_lines']}")
    print(f"  Comment lines removed:  {stats['comment_lines']}")
    print(f"  Blank lines removed:    {stats['blank_lines']}")
    print(f"  Repeated headers skip:  {stats['skipped_repeated_headers']}")
    print(f"  Output data rows:       {stats['output_rows']}")
    print(f"  Header:                 {stats['header']}")
    print(f"  Output file:            {args.output}")


if __name__ == "__main__":
    main()
