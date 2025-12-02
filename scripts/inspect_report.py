from pathlib import Path

import pandas as pd

report_path = Path("output/reports/business/sharepoint_permissions_report.xlsx")
if not report_path.exists():
    print("Report not found:", report_path)
    raise SystemExit(1)

excel_file = pd.ExcelFile(report_path)
print("Report:", report_path)
print("Sheets:", excel_file.sheet_names)
for sheet_name in excel_file.sheet_names:
    sheet_dataframe = excel_file.parse(sheet_name)
    print(f"\nSheet: {sheet_name}  shape={sheet_dataframe.shape}")
    print(sheet_dataframe.head(5).to_string(index=False))
