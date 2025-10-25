import json
from pathlib import Path
import pandas as pd

JSON_PATH = Path('output/reports/security/m365_cis_audit.json')
CSV_PATH = Path('output/reports/security/m365_cis_audit.csv')

COLUMNS = ['ControlId','Title','Severity','Expected','Actual','Status','Evidence','Reference','Timestamp']

def main():
    data = json.loads(JSON_PATH.read_text(encoding='utf-8-sig'))
    if isinstance(data, dict):
        rows = [data]
    else:
        rows = data
    df = pd.DataFrame(rows)
    # Reorder columns if present; include any extras at the end
    cols = [c for c in COLUMNS if c in df.columns] + [c for c in df.columns if c not in COLUMNS]
    df = df[cols]
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')
    print('CSV synced from JSON:', CSV_PATH)

if __name__ == '__main__':
    main()
