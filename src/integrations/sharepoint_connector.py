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
from pathlib import Path

import pandas as pd

DEFAULT_INPUT = Path("data/processed/sharepoint_permissions_clean.csv")
DEFAULT_OUTPUT = Path("output/reports/business/sharepoint_permissions_report.xlsx")


def build_summaries(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create summary DataFrames for the report."""
    summaries: dict[str, pd.DataFrame] = {}

    # Normalize some fields
    df = df.copy()
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
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 1) Counts by Item Type
    if "Item Type" in df.columns:
        summaries["by_item_type"] = (
            df.groupby("Item Type").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )

    # 2) Counts by Permission
    if "Permission" in df.columns:
        summaries["by_permission"] = (
            df.groupby("Permission").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )

    # 3) Top users by occurrences
    if "User Email" in df.columns:
        summaries["top_users"] = (
            df[df["User Email"].str.len() > 0]
            .groupby(["User Email", "User Name"])
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    # 4) Top resources by occurrences
    if "Resource Path" in df.columns:
        summaries["top_resources"] = (
            df[df["Resource Path"].str.len() > 0]
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
            for name, sdf in summaries.items():
                # Limit sheet name to 31 chars (Excel limitation)
                sheet = name[:31]
                sdf.to_excel(writer, sheet_name=sheet, index=False)
    except PermissionError as e:
        import sys
        print(f"ERROR: Cannot write to {output_path}: Permission denied. "
              f"Please close the file if it's open.", file=sys.stderr)
        raise
    except Exception as e:
        import sys
        print(f"ERROR: Failed to write Excel report: {e}", file=sys.stderr)
        raise


def main():
    import sys
    
    ap = argparse.ArgumentParser(description="Generate SharePoint permissions analysis report")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to cleaned SharePoint CSV")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to Excel report to write")
    args = ap.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(args.input)
    except pd.errors.EmptyDataError:
        print(f"ERROR: Input CSV is empty: {args.input}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"ERROR: Failed to parse CSV: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    if df.empty:
        print(f"WARNING: Input CSV contains no data rows", file=sys.stderr)
    
    try:
        summaries = build_summaries(df)
        
        if not summaries:
            print("WARNING: No summaries could be generated from the input data", file=sys.stderr)
        
        write_excel_report(summaries, args.output)
        print(f"✓ Report written: {args.output}")
        
    except Exception as e:
        print(f"ERROR: Failed to generate report: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
