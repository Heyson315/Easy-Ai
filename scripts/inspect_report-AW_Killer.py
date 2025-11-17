from pathlib import Path

import pandas as pd

report = Path("output/reports/business/sharepoint_permissions_report.xlsx")
if not report.exists():
    print("Report not found:", report)
    raise SystemExit(1)

xf = pd.ExcelFile(report)
print("Report:", report)
print("Sheets:", xf.sheet_names)
for sheet in xf.sheet_names:
    df = xf.parse(sheet)
    print(f"\nSheet: {sheet}  shape={df.shape}")
    print(df.head(5).to_string(index=False))
