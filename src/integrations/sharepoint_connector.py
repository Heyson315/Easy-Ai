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


def build_summaries(permissions_dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
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
    existing_str_cols = [column_name for column_name in str_columns if column_name in permissions_dataframe.columns]

    if existing_str_cols:
        # Create a copy only if we need to modify
        permissions_dataframe = permissions_dataframe.copy()
        for column_name in existing_str_cols:
            permissions_dataframe[column_name] = permissions_dataframe[column_name].astype(str).str.strip()

    # 1) Counts by Item Type
    if "Item Type" in permissions_dataframe.columns:
        summaries["by_item_type"] = (
            permissions_dataframe.groupby("Item Type").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )

    # 2) Counts by Permission
    if "Permission" in permissions_dataframe.columns:
        summaries["by_permission"] = (
            permissions_dataframe.groupby("Permission").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )

    # 3) Top users by occurrences
    if "User Email" in permissions_dataframe.columns:
        summaries["top_users"] = (
            permissions_dataframe[permissions_dataframe["User Email"].str.len() > 0]
            .groupby(["User Email", "User Name"])
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    # 4) Top resources by occurrences
    if "Resource Path" in permissions_dataframe.columns:
        summaries["top_resources"] = (
            permissions_dataframe[permissions_dataframe["Resource Path"].str.len() > 0]
            .groupby("Resource Path")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    return summaries


def write_excel_report(summaries: dict[str, pd.DataFrame], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Overview sheet
        overview_rows = []
        for summary_name, summary_dataframe in summaries.items():
            overview_rows.append(
                {
                    "Summary": summary_name,
                    "Rows": len(summary_dataframe),
                    "Columns": len(summary_dataframe.columns),
                }
            )
        pd.DataFrame(overview_rows).to_excel(writer, sheet_name="Overview", index=False)

        # Individual sheets
        for summary_name, summary_dataframe in summaries.items():
            # Limit sheet name to 31 chars
            sheet = summary_name[:31]
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
