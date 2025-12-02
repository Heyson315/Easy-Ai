import json
from pathlib import Path

import pandas as pd

JSON_PATH = Path("output/reports/security/m365_cis_audit.json")
CSV_PATH = Path("output/reports/security/m365_cis_audit.csv")

EXPECTED_COLUMNS = [
    "ControlId",
    "Title",
    "Severity",
    "Expected",
    "Actual",
    "Status",
    "Evidence",
    "Reference",
    "Timestamp",
]


def main():
    audit_data = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
    if isinstance(audit_data, dict):
        control_records = [audit_data]
    else:
        control_records = audit_data
    controls_dataframe = pd.DataFrame(control_records)
    # Reorder columns if present; include any extras at the end
    ordered_columns = [col for col in EXPECTED_COLUMNS if col in controls_dataframe.columns] + [
        col for col in controls_dataframe.columns if col not in EXPECTED_COLUMNS
    ]
    controls_dataframe = controls_dataframe[ordered_columns]
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    controls_dataframe.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print("CSV synced from JSON:", CSV_PATH)


if __name__ == "__main__":
    main()
