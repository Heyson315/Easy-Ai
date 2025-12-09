import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd  # noqa: E402

from src.core.file_io import ensure_parent_dir, load_json_with_bom, normalize_audit_data  # noqa: E402

DEFAULT_JSON = Path("output/reports/security/m365_cis_audit.json")


def build_report(json_path: Path, xlsx_path: Path = None) -> None:
    if xlsx_path is None:
        # Auto-name Excel based on JSON filename
        xlsx_path = json_path.with_suffix(".xlsx")
    json_path = Path(json_path)
    xlsx_path = Path(xlsx_path)

    ensure_parent_dir(xlsx_path)
    audit_results_data = load_json_with_bom(json_path)
    normalized_audit_rows = normalize_audit_data(audit_results_data)
    controls_dataframe = pd.DataFrame(normalized_audit_rows)

    # Overview
    overview_summary = (
        controls_dataframe.groupby(["Status", "Severity"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Severity", "Status", "Count"], ascending=[True, True, False])
    )

    # By control
    controls_detail_sheet = controls_dataframe[
        ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]
    ]

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        overview_summary.to_excel(writer, sheet_name="Overview", index=False)
        controls_detail_sheet.to_excel(writer, sheet_name="Controls", index=False)

    print("Excel report written:", xlsx_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_JSON, help="Path to CIS audit JSON")
    parser.add_argument(
        "--output", type=Path, default=None, help="Path to Excel output (optional, auto-names from JSON if omitted)"
    )
    args = parser.parse_args()
    build_report(args.input, args.output)
