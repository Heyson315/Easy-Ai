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


def clean_csv(input_csv_path: Path, output_csv_path: Path) -> dict:
    """
    Clean CSV file in a single pass for better performance.

    Optimizations:
    - Single-pass processing (no intermediate list storage)
    - Streaming I/O for memory efficiency
    - In-place cell stripping to reduce allocations
    """
    input_csv_path = Path(input_csv_path)
    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    processing_statistics = {
        "input_lines": 0,
        "output_rows": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "skipped_repeated_headers": 0,
        "header": None,
    }

    # Single-pass processing: filter and write simultaneously
    with input_csv_path.open("r", encoding="utf-8-sig", errors="replace") as input_file, output_csv_path.open(
        "w", encoding="utf-8", newline=""
    ) as output_file:

        csv_writer = csv.writer(output_file, lineterminator="\n")
        header_row = None

        # Create a generator that yields filtered lines
        def generate_filtered_lines():
            for raw_line in input_file:
                processing_statistics["input_lines"] += 1
                stripped_line = raw_line.strip()
                if not stripped_line:
                    processing_statistics["blank_lines"] += 1
                    continue
                if stripped_line.startswith("#"):
                    processing_statistics["comment_lines"] += 1
                    continue
                yield raw_line

        # Process CSV from filtered generator
        csv_reader = csv.reader(generate_filtered_lines())

        for current_row in csv_reader:
            # Normalize whitespace in each cell (in-place for efficiency)
            for cell_index in range(len(current_row)):
                current_row[cell_index] = current_row[cell_index].strip()

            if header_row is None:
                header_row = current_row
                # Strip potential BOM from first header col if still present
                if header_row and header_row[0].startswith("\ufeff"):
                    header_row[0] = header_row[0].lstrip("\ufeff")
                processing_statistics["header"] = header_row
                csv_writer.writerow(header_row)
                continue

            # Skip repeated header rows
            if current_row == header_row:
                processing_statistics["skipped_repeated_headers"] += 1
                continue

            # Guard against BOM in first data column
            if current_row and current_row[0].startswith("\ufeff"):
                current_row[0] = current_row[0].lstrip("\ufeff")

            csv_writer.writerow(current_row)
            processing_statistics["output_rows"] += 1

    return processing_statistics


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path")
    argument_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    parsed_args = argument_parser.parse_args()

    processing_statistics = clean_csv(parsed_args.input, parsed_args.output)

    print("CSV cleaned successfully:")
    print(f"  Input lines:            {processing_statistics['input_lines']}")
    print(f"  Comment lines removed:  {processing_statistics['comment_lines']}")
    print(f"  Blank lines removed:    {processing_statistics['blank_lines']}")
    print(f"  Repeated headers skip:  {processing_statistics['skipped_repeated_headers']}")
    print(f"  Output data rows:       {processing_statistics['output_rows']}")
    print(f"  Header:                 {processing_statistics['header']}")
    print(f"  Output file:            {parsed_args.output}")


if __name__ == "__main__":
    main()
