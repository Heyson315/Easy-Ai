"""
SharePoint permissions analysis and report generator.

Reads the cleaned CSV produced by scripts/clean_csv.py and writes an Excel report
with useful summaries.

Usage (PowerShell):
  python -m src.integrations.sharepoint_connector \
    --input "data/processed/sharepoint_permissions_clean.csv" \
    --output "output/reports/business/sharepoint_permissions_report.xlsx"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

DEFAULT_INPUT = Path("data/processed/sharepoint_permissions_clean.csv")
DEFAULT_OUTPUT = Path("output/reports/business/sharepoint_permissions_report.xlsx")


def generate_permission_summaries(permissions_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create summary DataFrames for the report."""
    summaries: dict[str, pd.DataFrame] = {}

    # Normalize some fields
    permissions_df = permissions_df.copy()
    # Ensure consistent types
    for col in [
        "Resource Path",
        "Item Type",
        "Permission",
        "User Name",
        "User Email",
        "User Or Group Type",
        "Link ID",
        "Link Type",
        "AccessViaLinkID",
    ]:
        if col in permissions_df.columns:
            permissions_df[col] = permissions_df[col].astype(str).str.strip()

    # 1) Counts by Item Type
    if "Item Type" in permissions_df.columns:
        summaries["by_item_type"] = (
            permissions_df.groupby("Item Type").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )

    # 2) Counts by Permission
    if "Permission" in permissions_df.columns:
        summaries["by_permission"] = (
            permissions_df.groupby("Permission").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )

    # 3) Top users by occurrences
    if "User Email" in permissions_df.columns:
        summaries["top_users"] = (
            permissions_df[permissions_df["User Email"].str.len() > 0]
            .groupby(["User Email", "User Name"])
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    # 4) Top resources by occurrences
    if "Resource Path" in permissions_df.columns:
        summaries["top_resources"] = (
            permissions_df[permissions_df["Resource Path"].str.len() > 0]
            .groupby("Resource Path")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    return summaries


def write_excel_report(summaries: dict[str, pd.DataFrame], output_path: Path) -> None:
    """Write summary DataFrames to Excel report."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Overview sheet
            overview_rows = []
            for key, df in summaries.items():
                overview_rows.append(
                    {
                        "Summary": key,
                        "Rows": len(df),
                        "Columns": len(df.columns),
                    }
                )

            if overview_rows:
                pd.DataFrame(overview_rows).to_excel(writer, sheet_name="Overview", index=False)
            else:
                # Create empty overview if no summaries
                pd.DataFrame({"Message": ["No summaries generated"]}).to_excel(
                    writer, sheet_name="Overview", index=False
                )

            # Individual sheets
            for name, summary_df in summaries.items():
                # Limit sheet name to 31 chars (Excel limitation)
                sheet = name[:31]
                summary_df.to_excel(writer, sheet_name=sheet, index=False)
    except PermissionError:
        print(
            f"ERROR: Cannot write to {output_path}: Permission denied. Please close the file if it's open.",
            file=sys.stderr,
        )
        raise
    except OSError as e:
        print(f"ERROR: OS error writing to {output_path}: {e}", file=sys.stderr)
        raise
    except ValueError as e:
        print(f"ERROR: Invalid data for Excel: {e}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Generate SharePoint permissions analysis report")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to cleaned SharePoint CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to Excel report to write")
    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        permissions_df = pd.read_csv(args.input)
    except pd.errors.EmptyDataError:
        print(f"ERROR: Input CSV is empty: {args.input}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"ERROR: Failed to parse CSV: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"ERROR: Failed to decode input file (encoding issue): {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: Input file not found: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: I/O error while reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    if permissions_df.empty:
        print("WARNING: Input CSV contains no data rows", file=sys.stderr)

    try:
        summaries = generate_permission_summaries(permissions_df)
    except Exception as e:
        print(f"ERROR: Failed to build summaries: {e}", file=sys.stderr)
        sys.exit(1)

    if not summaries:
        print("WARNING: No summaries could be generated from the input data", file=sys.stderr)

    # Let exceptions from write_excel_report propagate; it already prints detailed errors
    write_excel_report(summaries, args.output)
    print(f"✓ Report written: {args.output}")


if __name__ == "__main__":
    main()
