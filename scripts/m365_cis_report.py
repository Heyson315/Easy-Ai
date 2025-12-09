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
        data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, UnicodeDecodeError) as e:
        print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    if isinstance(data, dict):
        # In case it's a single object
        rows = [data]
    else:
        rows = data
    audit_df = pd.DataFrame(rows)

    # Overview
    overview = (
        audit_df.groupby(["Status", "Severity"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Severity", "Status", "Count"], ascending=[True, True, False])
    )

    # By control
    by_control = audit_df[
        ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]
    ]

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        overview.to_excel(writer, sheet_name="Overview", index=False)
        by_control.to_excel(writer, sheet_name="Controls", index=False)

    print("Excel report written:", xlsx_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_JSON, help="Path to CIS audit JSON")
    parser.add_argument(
        "--output", type=Path, default=None, help="Path to Excel output (optional, auto-names from JSON if omitted)"
    )
    args = parser.parse_args()
    build_report(args.input, args.output)
