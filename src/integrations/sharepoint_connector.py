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

from src.core.file_io import ensure_parent_dir

DEFAULT_INPUT = Path("data/processed/sharepoint_permissions_clean.csv")
DEFAULT_OUTPUT = Path("output/reports/business/sharepoint_permissions_report.xlsx")


def build_summaries(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Create summary DataFrames for the report.

    Optimizations:
    - Avoid unnecessary DataFrame copy by working with view
    - Use .astype() only on columns that need it
    """
    summaries: dict[str, pd.DataFrame] = {}

    # Normalize string columns efficiently (only those that exist and need normalization)
    str_columns = [
        "Resource Path",
        "Item Type",
        "Permission",
        "User Name",
        "User Email",
        "User Or Group Type",
        "Link ID",
        "Link Type",
        "AccessViaLinkID",
    ]

    # Only normalize columns that exist in the DataFrame
    existing_str_cols = [col for col in str_columns if col in df.columns]

    if existing_str_cols:
        # Create a copy only if we need to modify
        df = df.copy()
        for col in existing_str_cols:
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
    output_path = Path(output_path)
    ensure_parent_dir(output_path)

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
        pd.DataFrame(overview_rows).to_excel(writer, sheet_name="Overview", index=False)

        # Individual sheets
        for name, summary_dataframe in summaries.items():
            # Limit sheet name to 31 chars
            sheet = name[:31]
            summary_dataframe.to_excel(writer, sheet_name=sheet, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to cleaned SharePoint CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to Excel report to write")
    args = parser.parse_args()

    permissions_dataframe = pd.read_csv(args.input)
    summaries = build_summaries(permissions_dataframe)
    write_excel_report(summaries, args.output)

    print("Report written:", args.output)


if __name__ == "__main__":
    main()
