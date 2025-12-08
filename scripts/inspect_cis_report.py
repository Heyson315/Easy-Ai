#!/usr/bin/env python3
"""
Inspect M365 CIS Audit Excel report for validation and debugging.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

DEFAULT_REPORT = Path("output/reports/security/m365_cis_audit.xlsx")


def inspect_cis_report(report_path: Path) -> None:
    """Inspect and display information about CIS audit Excel report."""
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        xf = pd.ExcelFile(report_path)
    except ValueError as e:
        print(f"ERROR: Invalid Excel file: {e}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, OSError) as e:
        print(f"ERROR: Failed to open Excel file {report_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Report: {report_path}")
    print(f"Sheets: {xf.sheet_names}")
    
    if not xf.sheet_names:
        print("WARNING: Excel file contains no sheets", file=sys.stderr)
        return
    
    for sheet in xf.sheet_names:
        try:
            df = xf.parse(sheet)
            print(f"\nSheet: {sheet}  shape={df.shape}")
            if not df.empty:
                print(df.head(10).to_string(index=False))
            else:
                print("  (Empty sheet)")
        except (pd.errors.ParserError, KeyError, ValueError) as e:
            print(f"ERROR: Failed to parse sheet '{sheet}': {e}", file=sys.stderr)
            continue


def main():
    ap = argparse.ArgumentParser(description="Inspect M365 CIS Audit Excel report")
    ap.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help="Path to m365_cis_audit Excel report",
    )
    args = ap.parse_args()
    
    inspect_cis_report(args.report)


if __name__ == "__main__":
    main()
