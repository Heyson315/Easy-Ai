"""
Inspect M365 CIS audit Excel report structure and content.

This utility script displays information about the sheets, columns, and data
in a CIS audit Excel report file.
"""

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_REPORT_PATH = Path("output/reports/security/m365_cis_audit.xlsx")


def main():
    """Main entry point for the CIS report inspector."""
    argument_parser = argparse.ArgumentParser(description="Inspect M365 CIS audit Excel report structure.")
    argument_parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to m365_cis_audit Excel report",
    )
    parsed_args = argument_parser.parse_args()

    report_path = Path(parsed_args.report)
    if not report_path.exists():
        print("Report not found:", report_path)
        raise SystemExit(1)

    excel_file = pd.ExcelFile(report_path)
    print("Report:", report_path)
    print("Sheets:", excel_file.sheet_names)

    for sheet_name in excel_file.sheet_names:
        sheet_dataframe = excel_file.parse(sheet_name)
        print(f"\nSheet: {sheet_name}  shape={sheet_dataframe.shape}")
        print(sheet_dataframe.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
