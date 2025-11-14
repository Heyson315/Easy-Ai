#!/usr/bin/env python3
"""
Synchronize CIS audit results from JSON to CSV format.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

DEFAULT_JSON = Path("output/reports/security/m365_cis_audit.json")
DEFAULT_CSV = Path("output/reports/security/m365_cis_audit.csv")

COLUMNS = ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]


def sync_json_to_csv(json_path: Path, csv_path: Path) -> None:
    """Convert JSON audit results to CSV format."""
    # Validate input file exists
    if not json_path.exists():
        print(f"ERROR: Input file not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    
    # Read and parse JSON
    try:
        data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, UnicodeDecodeError) as e:
        print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize data structure
    if isinstance(data, dict):
        rows = [data]
    elif isinstance(data, list):
        rows = data
    else:
        print(f"ERROR: Unexpected data type in JSON: {type(data)}", file=sys.stderr)
        sys.exit(1)
    
    if not rows:
        print(f"WARNING: No data found in {json_path}", file=sys.stderr)
    
    # Create DataFrame
    try:
        df = pd.DataFrame(rows)
    except Exception as e:
        print(f"ERROR: Failed to create DataFrame: {e}", file=sys.stderr)
        sys.exit(1)
    
    if df.empty:
        print(f"WARNING: DataFrame is empty, no data to export", file=sys.stderr)
    
    # Reorder columns if present; include any extras at the end
    cols = [c for c in COLUMNS if c in df.columns] + [c for c in df.columns if c not in COLUMNS]
    df = df[cols]
    
    # Write CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"✓ CSV synced from JSON: {csv_path}")
        print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
    except PermissionError as e:
        print(f"ERROR: Permission denied writing to {csv_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to write CSV: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Sync M365 CIS audit JSON to CSV")
    ap.add_argument("--input", type=Path, default=DEFAULT_JSON, help="Path to input JSON file")
    ap.add_argument("--output", type=Path, default=DEFAULT_CSV, help="Path to output CSV file")
    args = ap.parse_args()
    
    sync_json_to_csv(args.input, args.output)


if __name__ == "__main__":
    main()
