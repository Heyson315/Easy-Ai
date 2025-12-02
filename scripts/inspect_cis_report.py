import argparse
from pathlib import Path

import pandas as pd


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/reports/security/m365_cis_audit.xlsx"),
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
