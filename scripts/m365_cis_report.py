import json
import argparse
from pathlib import Path
import pandas as pd

DEFAULT_JSON = Path('output/reports/security/m365_cis_audit.json')

def build_report(json_path: Path, xlsx_path: Path = None):
    if xlsx_path is None:
        # Auto-name Excel based on JSON filename
        xlsx_path = json_path.with_suffix('.xlsx')
    json_path = Path(json_path)
    xlsx_path = Path(xlsx_path)
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle potential UTF-8 BOM from PowerShell's UTF8 encoding
    data = json.loads(json_path.read_text(encoding='utf-8-sig'))
    if isinstance(data, dict):
        # In case it's a single object
        rows = [data]
    else:
        rows = data
    df = pd.DataFrame(rows)

    # Overview
    overview = (
        df.groupby(['Status','Severity']).size().reset_index(name='Count')
        .sort_values(['Severity','Status','Count'], ascending=[True, True, False])
    )

    # By control
    by_control = df[['ControlId','Title','Severity','Expected','Actual','Status','Evidence','Reference','Timestamp']]

    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        overview.to_excel(writer, sheet_name='Overview', index=False)
        by_control.to_excel(writer, sheet_name='Controls', index=False)

    print('Excel report written:', xlsx_path)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, default=DEFAULT_JSON, help='Path to CIS audit JSON')
    ap.add_argument('--output', type=Path, default=None, help='Path to Excel output (optional, auto-names from JSON if omitted)')
    args = ap.parse_args()
    build_report(args.input, args.output)
