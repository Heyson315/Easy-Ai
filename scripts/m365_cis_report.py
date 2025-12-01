#!/usr/bin/env python3
"""
M365 CIS Audit Report Generator

Converts M365 CIS audit JSON results to formatted Excel reports.
Includes overview and detailed control sheets with proper error handling.

Usage:
    python scripts/m365_cis_report.py --input "audit.json" --output "report.xlsx"
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Union

import pandas as pd

DEFAULT_JSON = Path("output/reports/security/m365_cis_audit.json")


def build_report(json_path: Path, xlsx_path: Path | None = None) -> None:
    """
    Build Excel report from CIS audit JSON.

    Args:
        json_path: Path to input JSON file
        xlsx_path: Optional path to output Excel file (auto-generated if None)

    Raises:
        SystemExit: If input file not found or invalid
    """
    if xlsx_path is None:
        # Auto-name Excel based on JSON filename
        xlsx_path = json_path.with_suffix(".xlsx")
    json_path = Path(json_path)
    xlsx_path = Path(xlsx_path)

    # Validate input file exists
    if not json_path.exists():
        print(f"ERROR: Input file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle potential UTF-8 BOM from PowerShell's UTF8 encoding
    try:
        # Load JSON data (can be single dict or list of dicts)
        data: Union[dict, list] = json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, UnicodeDecodeError) as e:
        print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error reading {json_path}: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle both single object and list formats
    if isinstance(data, dict):
        rows: list[dict] = [data]
    else:
        rows = data
    # Create DataFrame from audit results
    controls_dataframe = pd.DataFrame(rows)

    # Generate overview summary (grouped by Status and Severity)
    overview = (
        controls_dataframe.groupby(["Status", "Severity"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Severity", "Status", "Count"], ascending=[True, True, False])
    )

    # Extract detailed control information
    by_control = controls_dataframe[
        ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]
    ]

    # Write to Excel with multiple sheets
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        overview.to_excel(writer, sheet_name="Overview", index=False)
        by_control.to_excel(writer, sheet_name="Controls", index=False)

    print(f"✅ Excel report written: {xlsx_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert M365 CIS audit JSON to Excel report")
    parser.add_argument("--input", type=Path, default=DEFAULT_JSON, help="Path to CIS audit JSON file")
    parser.add_argument(
        "--output", type=Path, default=None, help="Path to Excel output (auto-named from input if omitted)"
    )
    args = parser.parse_args()
    build_report(args.input, args.output)
