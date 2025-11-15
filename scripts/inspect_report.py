#!/usr/bin/env python3
"""
Inspect SharePoint permissions Excel report for validation and debugging.
"""
import sys
from pathlib import Path

import pandas as pd

DEFAULT_REPORT = Path("output/reports/business/sharepoint_permissions_report.xlsx")


def inspect_report(report_path: Path) -> None:
    """Inspect and display information about Excel report."""
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        xf = pd.ExcelFile(report_path)
    except ValueError as e:
        print(f"ERROR: Invalid Excel file: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: File not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"ERROR: Permission denied accessing {report_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: I/O error opening Excel file: {e}", file=sys.stderr)
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
                print(df.head(5).to_string(index=False))
            else:
                print("  (Empty sheet)")
        except pd.errors.ParserError as e:
            print(f"ERROR: ParserError while parsing sheet '{sheet}': {e}", file=sys.stderr)
            continue
        except (KeyError, ValueError) as e:
            print(f"ERROR: Data access error in sheet '{sheet}': {e}", file=sys.stderr)
            continue
        except MemoryError as e:
            print(f"ERROR: MemoryError while parsing sheet '{sheet}': {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    import argparse
    
    ap = argparse.ArgumentParser(description="Inspect SharePoint permissions Excel report")
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Path to Excel report")
    args = ap.parse_args()
    
    inspect_report(args.report)
