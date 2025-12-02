import argparse
import json
import sys
from pathlib import Path

import pandas as pd

DEFAULT_JSON = Path("output/reports/security/m365_cis_audit.json")


def build_report(json_path: Path, xlsx_path: Path = None) -> None:
    if xlsx_path is None:
        # Auto-name Excel based on JSON filename
        xlsx_path = json_path.with_suffix(".xlsx")
    json_path = Path(json_path)
    xlsx_path = Path(xlsx_path)

    # Validate input file exists
    if not json_path.exists():
        print(f"ERROR: Input file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle potential UTF-8 BOM from PowerShell's UTF8 encoding
    try:
        audit_data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as json_error:
        print(f"ERROR: Invalid JSON in {json_path}: {json_error}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, UnicodeDecodeError) as file_error:
        print(f"ERROR: Cannot read {json_path}: {file_error}", file=sys.stderr)
        sys.exit(1)
    except Exception as unexpected_error:
        print(f"ERROR: Unexpected error reading {json_path}: {unexpected_error}", file=sys.stderr)
        sys.exit(1)
    if isinstance(audit_data, dict):
        # In case it's a single object
        control_records = [audit_data]
    else:
        control_records = audit_data
    controls_dataframe = pd.DataFrame(control_records)

    # Overview
    status_severity_summary = (
        controls_dataframe.groupby(["Status", "Severity"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Severity", "Status", "Count"], ascending=[True, True, False])
    )

    # By control
    controls_detail = controls_dataframe[
        ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]
    ]

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as excel_writer:
        status_severity_summary.to_excel(excel_writer, sheet_name="Overview", index=False)
        controls_detail.to_excel(excel_writer, sheet_name="Controls", index=False)

    print("Excel report written:", xlsx_path)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", type=Path, default=DEFAULT_JSON, help="Path to CIS audit JSON")
    argument_parser.add_argument(
        "--output", type=Path, default=None, help="Path to Excel output (optional, auto-names from JSON if omitted)"
    )
    parsed_args = argument_parser.parse_args()
    build_report(parsed_args.input, parsed_args.output)
