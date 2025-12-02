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

DEFAULT_INPUT_PATH = Path("data/processed/sharepoint_permissions_clean.csv")
DEFAULT_OUTPUT_PATH = Path("output/reports/business/sharepoint_permissions_report.xlsx")

# Column names used for normalization
PERMISSION_COLUMNS_TO_NORMALIZE = [
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


def build_summaries(permissions_dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Create summary DataFrames for the SharePoint permissions report.

    Args:
        permissions_dataframe: DataFrame containing SharePoint permissions data.

    Returns:
        Dictionary mapping summary names to their respective DataFrames:
        - by_item_type: Count of permissions by item type
        - by_permission: Count of each permission level
        - top_users: Top 25 users by number of permissions
        - top_resources: Top 25 resources by permission count
    """
    summary_dataframes: dict[str, pd.DataFrame] = {}

    # Check which columns need normalization (only existing columns)
    existing_columns_to_normalize = [
        column_name for column_name in PERMISSION_COLUMNS_TO_NORMALIZE if column_name in permissions_dataframe.columns
    ]

    # Only create a copy if we need to normalize columns
    if existing_columns_to_normalize:
        working_dataframe = permissions_dataframe.copy()
        for column_name in existing_columns_to_normalize:
            working_dataframe[column_name] = working_dataframe[column_name].astype(str).str.strip()
    else:
        # No normalization needed, use original DataFrame directly
        working_dataframe = permissions_dataframe

    # 1) Counts by Item Type
    if "Item Type" in working_dataframe.columns:
        summary_dataframes["by_item_type"] = (
            working_dataframe.groupby("Item Type")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

    # 2) Counts by Permission
    if "Permission" in working_dataframe.columns:
        summary_dataframes["by_permission"] = (
            working_dataframe.groupby("Permission")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

    # 3) Top users by occurrences
    if "User Email" in working_dataframe.columns:
        users_with_email = working_dataframe[working_dataframe["User Email"].str.len() > 0]
        summary_dataframes["top_users"] = (
            users_with_email.groupby(["User Email", "User Name"])
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    # 4) Top resources by occurrences
    if "Resource Path" in working_dataframe.columns:
        resources_with_path = working_dataframe[working_dataframe["Resource Path"].str.len() > 0]
        summary_dataframes["top_resources"] = (
            resources_with_path.groupby("Resource Path")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(25)
        )

    return summary_dataframes


def write_excel_report(summary_dataframes: dict[str, pd.DataFrame], output_report_path: Path) -> None:
    """
    Write summary DataFrames to an Excel workbook.

    Args:
        summary_dataframes: Dictionary mapping sheet names to DataFrames.
        output_report_path: Path where the Excel report will be saved.
    """
    output_report_path = Path(output_report_path)
    output_report_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_report_path, engine="openpyxl") as excel_writer:
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

        # Individual sheets for each summary
        for summary_name, summary_df in summary_dataframes.items():
            # Limit sheet name to Excel's 31-character maximum
            truncated_sheet_name = summary_name[:31]
            summary_df.to_excel(excel_writer, sheet_name=truncated_sheet_name, index=False)


def main():
    """Main entry point for the SharePoint permissions report generator."""
    argument_parser = argparse.ArgumentParser(description="Generate Excel report from SharePoint permissions CSV.")
    argument_parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to cleaned SharePoint CSV",
    )
    argument_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to Excel report to write",
    )
    parsed_args = argument_parser.parse_args()

    permissions_dataframe = pd.read_csv(parsed_args.input)
    summary_dataframes = build_summaries(permissions_dataframe)
    write_excel_report(summary_dataframes, parsed_args.output)

    print("Report written:", parsed_args.output)


if __name__ == "__main__":
    main()
