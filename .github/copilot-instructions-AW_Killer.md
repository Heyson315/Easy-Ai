# Copilot Instructions: M365 Security & SharePoint Analysis Toolkit

## Architecture Overview

This is a **hybrid Python/PowerShell toolkit** for Microsoft 365 security auditing and SharePoint permissions analysis. The project follows a domain-driven structure with distinct workflows:

### Data Flow Pipeline

1. **PowerShell** → M365 services (EXO, Graph, SPO, Purview, Intune) → Raw JSON/CSV (`output/reports/security/`)
2. **Python scripts** → CSV cleaning/transformation → Processed data (`data/processed/`)
3. **Python modules** (`src/`) → Excel report generation + **Interactive HTML dashboards** (`output/reports/business/`)

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
- `config/audit_config.json` - Tenant configuration template with scheduling/notification settings
- `.github/workflows/` - CI/CD automation (quality checks, monthly audits, dependency updates)

## Development & Testing Workflow

### Python Development Pattern

- **Code Quality**: Black formatter (120 chars), flake8 linting, mypy type checking configured in `pyproject.toml`
- **Testing**: `pytest` with coverage reporting to `tests/` directory using `TemporaryDirectory()` for file I/O
- **Dependencies**: Split into `requirements.txt` (runtime) and `requirements-dev.txt` (development tools)
- **Performance**: Built-in benchmarking via `scripts/run_performance_benchmark.py --baseline`

### GitHub Actions CI/CD (`main` branch: `evidence/2025-10-25`)

```yaml
# Trigger: Push to evidence/2025-10-25, feature/* branches, PR, manual dispatch
# Jobs: python-quality-checks, powershell-security-scan, monthly-automated-audit
```

- **Quality Gates**: Python linting, code formatting checks, performance benchmarks, security scanning
- **Automated Audits**: Monthly M365 security assessments with artifact preservation
- **Dependency Management**: Automated dependency scanning and updates

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
# Run audit (connects to EXO, Graph, optionally SPO/Purview/Intune)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1" [-SPOAdminUrl "https://tenant-admin.sharepoint.com"] [-Timestamped] [-SkipPurview]

# Convert JSON to Excel
python scripts/m365_cis_report.py [--input "output/reports/security/m365_cis_audit.json"]

# Generate Interactive HTML Dashboard (NEW)
python scripts/generate_security_dashboard.py [--input "output/reports/security/m365_cis_audit.json"] [--output "output/reports/security/dashboard.html"]
```

### Safe Remediation Workflow (NEW v1.0.0)

```powershell
# Preview remediation actions (safe mode)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/PostRemediateM365CIS.ps1" -WhatIf

# Apply remediation actions
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/PostRemediateM365CIS.ps1" -Force
```

### Audit Comparison & Trending (NEW v1.0.0)

```powershell
# Compare before/after audit results
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Compare-M365CISResults.ps1" -BeforeFile "before.json" -AfterFile "after.json" -OutputHtml "comparison.html"

# Setup automated scheduling
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Setup-ScheduledAudit.ps1" -Schedule Weekly -DayOfWeek Monday -Time "09:00"
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

**`M365CIS.psm1` conventions** (483+ lines of production audit functions):

- Prefix all functions with verb (`Test-CIS-*`, `Connect-M365CIS`, `New-CISResult`)
- Return `[PSCustomObject]` with standard fields: `ControlId`, `Title`, `Severity`, `Expected`, `Actual`, `Status`, `Evidence`, `Reference`, `Timestamp`
- Always wrap in try/catch returning `Status='Manual'` on connection failures
- Explicitly import modules with `-ErrorAction Stop` and provide clear warnings
- **Critical**: Auto-fix OneDrive PSModulePath in `Connect-M365CIS` for synced modules
- **Authentication**: Multi-service connection (EXO, Graph, SPO Admin, Purview) with graceful fallbacks

### Module Execution Pattern

**Scripts vs Modules**:

- ❌ **Don't** use `python -m scripts.file` (scripts aren't a package) → Use `python scripts/file.py`
- ✅ **Do** use `python -m src.integrations.sharepoint_connector` (src/ is a proper package)
- ✅ **Do** use absolute paths for PowerShell: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1"`

### Excel Report Generation

**Pattern** (`src/core/excel_generator.py`, `src/integrations/sharepoint_connector.py`):

- Use `openpyxl` for multi-sheet workbooks with formatting
- Use `pandas` for data aggregation before writing (e.g., `groupby().size().reset_index()`)
- Apply styles: `Font(bold=True)`, `PatternFill(start_color='...')`, `Alignment(horizontal='center')`
- Auto-size columns: iterate `get_column_letter()` and set `column_dimensions[].width`

### Error Handling Pattern (NEW v1.0.0)

**Problem**: Generic `Exception` handlers make debugging difficult.

**Solution**: Use specific exception types with detailed error messages:

```python
try:
    data = json.loads(json_path.read_text(encoding='utf-8-sig'))
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
    sys.exit(1)
except (PermissionError, UnicodeDecodeError) as e:
    print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
    sys.exit(1)
```

Applied to: `scripts/m365_cis_report.py`, `scripts/generate_security_dashboard.py`

### Dashboard Generation Pattern (NEW v1.0.0)

**HTML Dashboard** (`scripts/generate_security_dashboard.py`):

- Zero external dependencies (uses CDN for Chart.js)
- Historical trend analysis from timestamped audit files
- Responsive design with filtering/sorting
- Security summary cards and control status table

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
- ❌ **Don't** use generic `Exception` handlers → Use specific types (`json.JSONDecodeError`, `PermissionError`)
- ✅ **Do** run PowerShell scripts with absolute paths (use full path to `.ps1` file)
- ✅ **Do** use `-Timestamped` flag for audit evidence versioning
- ✅ **Do** validate JSON structure before Excel conversion (`inspect_cis_report.py`)
- ✅ **Do** use `-WhatIf` for safe remediation previews before applying changes
- ✅ **Do** leverage historical trending with multiple timestamped audit runs
- ✅ **Do** configure development tools via `pyproject.toml` (Black 120 chars, pytest coverage)
- ✅ **Do** use `TemporaryDirectory()` for all file I/O tests to avoid cleanup issues
