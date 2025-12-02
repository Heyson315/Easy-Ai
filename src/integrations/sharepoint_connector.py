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
    summary_dataframes: dict[str, pd.DataFrame] = {}

    # Normalize string columns efficiently (only those that exist and need normalization)
    string_column_names = [
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
    existing_string_columns = [col for col in string_column_names if col in permissions_dataframe.columns]

    if existing_string_columns:
        # Create a copy only if we need to modify
        permissions_dataframe = permissions_dataframe.copy()
        for column_name in existing_string_columns:
            permissions_dataframe[column_name] = permissions_dataframe[column_name].astype(str).str.strip()

    # 1) Counts by Item Type
    if "Item Type" in permissions_dataframe.columns:
        summary_dataframes["by_item_type"] = (
            permissions_dataframe.groupby("Item Type")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

    # 2) Counts by Permission
    if "Permission" in permissions_dataframe.columns:
        summary_dataframes["by_permission"] = (
            permissions_dataframe.groupby("Permission")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

    # 3) Top users by occurrences
    if "User Email" in permissions_dataframe.columns:
        summary_dataframes["top_users"] = (
            permissions_dataframe[permissions_dataframe["User Email"].str.len() > 0]
            .groupby(["User Email", "User Name"])
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    # 4) Top resources by occurrences
    if "Resource Path" in permissions_dataframe.columns:
        summary_dataframes["top_resources"] = (
            permissions_dataframe[permissions_dataframe["Resource Path"].str.len() > 0]
            .groupby("Resource Path")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    return summary_dataframes


def write_excel_report(summary_dataframes: dict[str, pd.DataFrame], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as excel_writer:
        # Overview sheet
        overview_rows = []
        for summary_name, summary_df in summary_dataframes.items():
            overview_rows.append(
                {
                    "Summary": summary_name,
                    "Rows": len(summary_df),
                    "Columns": len(summary_df.columns),
                }
            )
        pd.DataFrame(overview_rows).to_excel(excel_writer, sheet_name="Overview", index=False)

        # Individual sheets
        for summary_name, summary_dataframe in summary_dataframes.items():
            # Limit sheet name to 31 chars
            sheet_name = summary_name[:31]
            summary_dataframe.to_excel(excel_writer, sheet_name=sheet_name, index=False)


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to cleaned SharePoint CSV")
    argument_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to Excel report to write")
    parsed_args = argument_parser.parse_args()

    permissions_dataframe = pd.read_csv(parsed_args.input)
    summary_dataframes = build_summaries(permissions_dataframe)
    write_excel_report(summary_dataframes, parsed_args.output)

    print("Report written:", parsed_args.output)


if __name__ == "__main__":
    main()
