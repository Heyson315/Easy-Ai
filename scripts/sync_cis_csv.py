import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd  # noqa: E402

from src.core.file_io import (  # noqa: E402
    CIS_AUDIT_COLUMNS,
    ensure_parent_dir,
    load_json_with_bom,
    normalize_audit_data,
)

JSON_PATH = Path("output/reports/security/m365_cis_audit.json")
CSV_PATH = Path("output/reports/security/m365_cis_audit.csv")


def main():
    data = load_json_with_bom(JSON_PATH)
    rows = normalize_audit_data(data)
    controls_dataframe = pd.DataFrame(rows)
    # Reorder columns if present; include any extras at the end
    cols = [c for c in CIS_AUDIT_COLUMNS if c in controls_dataframe.columns] + [
        c for c in controls_dataframe.columns if c not in CIS_AUDIT_COLUMNS
    ]
    controls_dataframe = controls_dataframe[cols]
    ensure_parent_dir(CSV_PATH)
    controls_dataframe.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print("CSV synced from JSON:", CSV_PATH)


if __name__ == "__main__":
    main()
