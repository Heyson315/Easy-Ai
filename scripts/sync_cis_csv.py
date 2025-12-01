#!/usr/bin/env python3
"""
CIS Audit JSON to CSV Converter

Converts M365 CIS audit JSON files to CSV format with proper column ordering.

Usage:
    python scripts/sync_cis_csv.py
"""
import json
import sys
from pathlib import Path
from typing import Union

import pandas as pd

# Configuration
JSON_PATH = Path("output/reports/security/m365_cis_audit.json")
CSV_PATH = Path("output/reports/security/m365_cis_audit.csv")

# Expected column order
COLUMNS = ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]


def main() -> None:
    """Convert CIS audit JSON to CSV with proper column ordering."""
    if not JSON_PATH.exists():
        print(f"ERROR: JSON file not found: {JSON_PATH}", file=sys.stderr)
        sys.exit(1)

    try:
        # Load JSON data (can be single dict or list of dicts)
        data: Union[dict, list] = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))

        # Handle both single object and list formats
        if isinstance(data, dict):
            rows: list[dict] = [data]
        else:
            rows = data

        # Create DataFrame
        controls_dataframe = pd.DataFrame(rows)

        # Reorder columns: expected columns first, extras at the end
        cols = [c for c in COLUMNS if c in controls_dataframe.columns] + [
            c for c in controls_dataframe.columns if c not in COLUMNS
        ]
        controls_dataframe = controls_dataframe[cols]

        # Write CSV
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        controls_dataframe.to_csv(CSV_PATH, index=False, encoding="utf-8")

        print(f"✅ CSV synced from JSON: {CSV_PATH}")
        print(f"   Rows: {len(controls_dataframe)}, Columns: {len(controls_dataframe.columns)}")

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Conversion failed: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
