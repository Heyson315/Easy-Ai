# SharePoint permissions workflow

This guide shows how to clean a raw SharePoint permissions CSV and generate an Excel report.

## 1) Clean the raw CSV

Removes comment and blank lines, handles quoted commas correctly, strips UTF-8 BOM, and de-duplicates repeated headers.

```powershell
python scripts/clean_csv.py
```

Defaults:

- Input: `data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv`
- Output: `data/processed/sharepoint_permissions_clean.csv`

Pass explicit paths if needed:

```powershell
python scripts/clean_csv.py --input "path/to/input.csv" --output "path/to/output.csv"
```

## 2) Inspect the cleaned CSV (optional)

```powershell
python scripts/inspect_processed_csv.py
```

## 3) Generate the Excel report

```powershell
python -m src.integrations.sharepoint_connector --input "data/processed/sharepoint_permissions_clean.csv" --output "output/reports/business/sharepoint_permissions_report.xlsx"
```

## 4) Inspect the report (optional)

```powershell
python scripts/inspect_report.py
```

Outputs are saved under `output/reports/business/`.
