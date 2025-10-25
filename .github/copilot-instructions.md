# Copilot Instructions: M365 Security & SharePoint Analysis Toolkit

## Architecture Overview

This is a **hybrid Python/PowerShell toolkit** for Microsoft 365 security auditing and SharePoint permissions analysis. The project follows a domain-driven structure with distinct workflows:

### Data Flow Pipeline
1. **PowerShell** → M365 services (EXO, Graph, SPO) → Raw JSON/CSV (`output/reports/security/`)
2. **Python scripts** → CSV cleaning/transformation → Processed data (`data/processed/`)
3. **Python modules** (`src/`) → Excel report generation (`output/reports/business/`)

### Directory Structure
- `scripts/` - Standalone utilities (Python CSV cleaners, PowerShell audit runners)
- `scripts/powershell/modules/M365CIS.psm1` - Core audit functions (read-only checks)
- `src/` - Domain modules organized by function:
  - `core/` - Excel generation (`excel_generator.py`)
  - `integrations/` - External service connectors (`sharepoint_connector.py`)
  - `academic/`, `analytics/`, `business/`, `financial/` - Domain-specific modules (currently empty, reserved for expansion)
- `tests/` - pytest-based tests using tempfiles and pandas validation
- `docs/` - Workflow documentation (`SECURITY_M365_CIS.md`, `USAGE_SHAREPOINT.md`)
- `config/benchmarks/` - CIS control metadata (JSON)

## Critical Workflows

### SharePoint Permissions Workflow
```powershell
# 1. Clean raw CSV (removes comments, BOM, repeated headers)
python scripts/clean_csv.py --input "data/raw/sharepoint/file.csv" --output "data/processed/sharepoint_permissions_clean.csv"

# 2. Generate Excel report with summaries
python -m src.integrations.sharepoint_connector --input "data/processed/sharepoint_permissions_clean.csv" --output "output/reports/business/sharepoint_permissions_report.xlsx"
```

### M365 CIS Security Audit Workflow
```powershell
# Run audit (connects to EXO, Graph, optionally SPO)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1" [-SPOAdminUrl "https://tenant-admin.sharepoint.com"] [-Timestamped]

# Convert JSON to Excel
python scripts/m365_cis_report.py [--input "output/reports/security/m365_cis_audit.json"]
```

## Project-Specific Conventions

### File Path Handling
- **Always use absolute paths** in PowerShell scripts (resolved from repo root via `Split-Path`)
- **Python uses Path objects** from `pathlib` with `.mkdir(parents=True, exist_ok=True)` for output dirs
- Default paths are constants at module top (`DEFAULT_INPUT`, `DEFAULT_OUTPUT`)

### CSV Processing Pattern
**Problem**: SharePoint exports include UTF-8 BOM, comments (`# ...`), blank lines, and repeated headers.

**Solution** (`scripts/clean_csv.py`):
1. Read with `encoding='utf-8-sig'` to strip BOM
2. Filter comments/blanks before CSV parsing
3. Use `csv.reader/writer` to preserve quoted commas (e.g., `"parent/path,with,comma"`)
4. Track duplicate headers and skip them
5. Return statistics dict for validation

### PowerShell Module Pattern
**`M365CIS.psm1` conventions**:
- Prefix all functions with verb (`Test-CIS-*`, `Connect-M365CIS`, `New-CISResult`)
- Return `[PSCustomObject]` with standard fields: `ControlId`, `Title`, `Severity`, `Expected`, `Actual`, `Status`, `Evidence`, `Reference`, `Timestamp`
- Always wrap in try/catch returning `Status='Manual'` on connection failures
- Explicitly import modules with `-ErrorAction Stop` and provide clear warnings
- Fix OneDrive PSModulePath: `$env:PSModulePath += ";$env:USERPROFILE\OneDrive - Rahman Finance and Accounting P.L.LC\Documents\WindowsPowerShell\Modules"`

### Excel Report Generation
**Pattern** (`src/core/excel_generator.py`, `src/integrations/sharepoint_connector.py`):
- Use `openpyxl` for multi-sheet workbooks with formatting
- Use `pandas` for data aggregation before writing (e.g., `groupby().size().reset_index()`)
- Apply styles: `Font(bold=True)`, `PatternFill(start_color='...')`, `Alignment(horizontal='center')`
- Auto-size columns: iterate `get_column_letter()` and set `column_dimensions[].width`

### Testing Pattern
- Use `TemporaryDirectory()` from tempfile for file I/O tests
- Validate with pandas: `df.shape`, `df.columns`, `df.iloc[0]['column']`
- Return stats dicts from functions for assertion checks

## External Dependencies & Integration Points

### PowerShell Modules (Install with `-Scope CurrentUser`)
- `ExchangeOnlineManagement` - EXO cmdlets (`Get-OrganizationConfig`, `Get-AuthenticationPolicy`)
- `Microsoft.Graph.Authentication` + `Microsoft.Graph.Identity.*` - Graph API
- `Microsoft.Online.SharePoint.PowerShell` (optional) - SPO tenant checks (`Connect-SPOService`)

### Python Packages
- `pandas` - CSV/Excel I/O, data aggregation
- `openpyxl` - Excel formatting
- `pytest` - Testing framework

### Authentication Flow
1. `Connect-M365CIS` → Interactive browser login (supports MFA)
2. Required scopes: `User.Read.All`, `Policy.Read.All`, `Directory.Read.All`, `Organization.Read.All`
3. Admin roles: Exchange Admin, Global Reader/Security Reader, SharePoint Admin

## Git Conventions

### Version Control Strategy (.gitignore)
- **Include**: JSON/CSV reports (`!output/reports/security/*.json`, `!output/reports/security/*.csv`)
- **Exclude**: Excel files (use Git LFS if needed), virtual envs (`.venv/`), `__pycache__/`
- **Rationale**: Text-based evidence is lightweight and diffable; Excel causes repo bloat

### Output Organization
- `output/reports/security/` - CIS audit results (JSON/CSV/XLSX)
- `output/reports/business/` - SharePoint/domain reports (XLSX)
- `data/raw/` - Unprocessed exports
- `data/processed/` - Cleaned CSVs
- `data/archive/` - Historical snapshots

## Debugging & Troubleshooting

### PowerShell Execution Issues
If modules aren't found, check PSModulePath includes OneDrive sync folder (automatically added by `Connect-M365CIS`).

### CSV Parsing Issues
If quoted fields are malformed, use `inspect_processed_csv.py` to validate output before reporting.

### Excel Generation
Always call `.parent.mkdir(parents=True, exist_ok=True)` before writing files to avoid `FileNotFoundError`.

## Common Pitfalls
- ❌ **Don't** use `python -m scripts.file` (scripts aren't a package) → Use `python scripts/file.py`
- ❌ **Don't** assume headers appear once in raw CSVs → Use `clean_csv.py` first
- ❌ **Don't** hardcode tenant URLs → Accept as parameters with defaults
- ✅ **Do** run PowerShell scripts with absolute paths (use full path to `.ps1` file)
- ✅ **Do** use `-Timestamped` flag for audit evidence versioning
- ✅ **Do** validate JSON structure before Excel conversion (`inspect_cis_report.py`)
