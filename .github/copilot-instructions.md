# Copilot Instructions: M365 Security & SharePoint Analysis Toolkit

**Last Updated**: 2025-12-05 (v1.2.0 - GitHub Action, Dependency Updates, Dual MCP Architecture)

> 🤖 **Quick Start for AI Agents**: New to this project? 
> - **Fast Track** (15 min): [AI Agent Quick Start](AI_AGENT_QUICKSTART.md)
> - **Complete Index**: [AI Development Index](AI_DEVELOPMENT_INDEX.md) - Navigate all AI resources

## Architecture Overview

This is a **hybrid Python/PowerShell enterprise security toolkit** with a **dual-track MCP extension system** for Microsoft 365 security auditing and SharePoint permissions analysis. The project is also **published as a GitHub Action** for seamless CI/CD integration.

### Core Architecture Principles

**Three-Layer Design:**
1. **Core Toolkit** (Required) - Foundational Python/PowerShell security auditing
2. **Extension System** (Optional) - Dual MCP implementations:
   - `src/extensions/mcp/` - Simplified MCP server
   - `src/mcp/` - Plugin-based MCP server with pluggable tools
3. **GitHub Action** (Optional) - Reusable workflow component for CI/CD

**Why This Matters:**
- Core toolkit works standalone without extensions
- Two MCP architectures support different use cases (simple vs. plugin-based)
- GitHub Action enables zero-setup auditing in CI/CD pipelines
- Clean separation enables independent development and testing
- Plugin architecture supports future extensibility (custom integrations)

### Data Flow Pipeline
```
M365 Services → PowerShell Audits → Python Processing → Reports → [Optional: MCP/AI Analysis]
     ↓               ↓                    ↓              ↓              ↓
  EXO, Graph,   CIS Controls      CSV Cleaning,   Excel/HTML     MCP Server,
  SPO, Purview   (M365CIS.psm1)  Data Transform   Dashboards    AI Insights
```

### Directory Structure
```
📦 Project Root
├── 📄 action.yml                   # 🆕 Published GitHub Action definition
├── 📂 scripts/                    # Standalone Python & PowerShell utilities
│   ├── clean_csv.py               # CSV sanitization (BOM, comments, duplicates)
│   ├── m365_cis_report.py         # JSON → Excel converter
│   ├── generate_security_dashboard.py  # Interactive HTML dashboards
│   └── 📂 powershell/
│       ├── Invoke-M365CISAudit.ps1     # Main audit orchestrator
│       ├── Compare-M365CISResults.ps1   # Audit trending
│       ├── PostRemediateM365CIS.ps1     # Safe remediation
│       └── 📂 modules/
│           └── M365CIS.psm1       # Core audit functions (27KB, 600+ lines)
├── 📂 src/                        # Python modules (proper package structure)
│   ├── 📂 core/                   # Core functionality
│   │   ├── excel_generator.py    # Report generation engine
│   │   ├── cost_tracker.py       # GPT-5 cost monitoring
│   │   ├── file_io.py            # File operations
│   │   ├── profiler.py           # Performance profiling
│   │   └── report_utils.py       # Report utilities
│   ├── �� integrations/           # External services
│   │   ├── sharepoint_connector.py  # SharePoint analysis
│   │   └── openai_gpt5.py        # GPT-5 client (now CORE dependency)
│   ├── 📂 extensions/             # Optional extensions
│   │   └── 📂 mcp/                # Simplified MCP server
│   │       ├── server.py          # Main MCP server (async)
│   │       ├── setup.py           # Interactive setup wizard
│   │       ├── 📂 tools/          # Tool definitions
│   │       └── README.md          # Extension documentation
│   └── 📂 mcp/                    # 🆕 Plugin-based MCP architecture
│       ├── m365_mcp_server.py     # Alternative MCP server
│       └── 📂 plugins/            # Pluggable tool system
│           └── 📂 sharepoint_tools/
│               ├── plugin.json    # Plugin metadata
│               └── tools.py       # SharePoint-specific tools
├── 📂 tests/                      # pytest-based testing
├── 📂 config/
│   ├── audit_config.json          # Tenant configuration
│   └── 📂 benchmarks/             # CIS control metadata (JSON)
├── 📂 output/reports/
│   ├── security/                  # JSON/CSV/XLSX audit results
│   └── business/                  # Excel/HTML domain reports
├── 📂 data/
│   ├── raw/                       # Unprocessed exports
│   ├── processed/                 # Cleaned CSVs
│   └── archive/                   # Historical snapshots
├── 📂 .github/workflows/          # CI/CD automation
│   ├── m365-security-ci.yml       # Quality gates & testing
│   ├── m365-automated-audit.yml   # Scheduled audits
│   ├── ci.yml                     # Test coverage with badge generation
│   └── [14+ other workflows]      # Security scanning, dependencies, etc.
├── requirements.txt               # Core dependencies (REQUIRED - includes AI)
├── requirements-extensions.txt    # Optional extensions (MCP, Graph SDK)
└── requirements-dev.txt           # Development tools

**Key Architectural Decisions:**
- `scripts/` contains **standalone utilities** with `__init__.py` for package support
- `src/` is a **proper Python package** for reusable modules
- **Dual MCP implementations**: Simple (`src/extensions/mcp/`) vs. Plugin-based (`src/mcp/`)
- **GitHub Action published**: Can be consumed by other repositories
- PowerShell modules in `scripts/powershell/modules/` for M365 API interaction
- Hybrid approach: PowerShell for M365 APIs (native), Python for data processing

## Recent Architectural Changes (Dec 2025)


### GitHub Action v1.2.0 - Enhanced Features

The published GitHub Action (Heyson315/Easy-Ai@v1) now includes **enterprise-grade capabilities**:

#### Advanced Outputs (25+ Variables)

**Risk Scoring (Severity-Weighted 0-100 Scale):**
- `risk-score`: Overall risk score (0-100, weighted by severity: Critical=10, High=7, Medium=4, Low=1)
- `critical-findings`: Count of critical severity failures
- `high-findings`: Count of high severity failures
- `medium-findings`: Count of medium severity failures
- `low-findings`: Count of low severity failures

**Compliance Trending (Historical Comparison):**
- `compliance-trend`: Percentage change vs baseline (e.g., "+5.2%", "-2.1%")
- `new-failures`: Count of newly failing controls since baseline
- `fixed-issues`: Count of controls fixed since baseline
- `trend-direction`: "improving", "stable", or "declining"

**Security Integration:**
- `sarif-report`: Path to SARIF 2.1.0 report for GitHub Security tab
- `security-findings-count`: Total findings uploaded to Security tab

**Automated Remediation:**
- `remediated-controls`: Comma-separated list of auto-fixed control IDs
- `remediation-report`: Path to detailed remediation log

#### Key Inputs

**Multi-Tenant Support:**
```yaml
tenant-config: |
  [
    {"name": "Client-A", "tenantId": "guid-1", "spoAdmin": "https://clienta-admin.sharepoint.com"},
    {"name": "Client-B", "tenantId": "guid-2", "spoAdmin": "https://clientb-admin.sharepoint.com"}
  ]
```

**Automated Remediation:**
```yaml
enable-auto-remediation: true
auto-approve-remediation: false  # Requires approval gate
remediation-controls: '1.1.1,1.1.3,2.1.1'  # Target specific controls
```

**Security Tab Integration:**
```yaml
upload-to-security-tab: true
security-severity-threshold: high  # Only upload high/critical findings
```

**Compliance Trending:**
```yaml
compare-with-baseline: true
baseline-artifact-name: 'compliance-baseline'  # Saved for 365 days
```

#### Real-World Workflow Examples

See **[WORKFLOW_EXAMPLES.md](.github/WORKFLOW_EXAMPLES.md)** for 6 production-ready scenarios:

1. **Basic Audit with Security Tab** - Monthly scheduled scan uploading SARIF to Security tab
2. **Automated Remediation with Approval** - WhatIf/Force mode with GitHub Environments approval gates
3. **Multi-Tenant Batch Audit** - Matrix strategy for MSPs managing multiple M365 tenants
4. **PR Compliance Gate** - Block PRs if compliance drops below 80% or risk score > 70
5. **Teams Notification** - Alert Microsoft Teams on critical/high findings
6. **Continuous Monitoring** - Update compliance badge every 6 hours, trigger incident response

#### Risk Scoring Algorithm

```powershell
# Severity weights
$weights = @{ "Critical" = 10; "High" = 7; "Medium" = 4; "Low" = 1 }

# Calculate weighted risk
$totalRiskPoints = ($criticalCount * 10) + ($highCount * 7) + ($mediumCount * 4) + ($lowCount * 1)
$maxRiskPoints = $totalControlsCount * 10
$riskScore = ($totalRiskPoints / $maxRiskPoints) * 100
```

**Example:** 100 controls, 5 critical failures, 10 high failures:
- Risk Points: (5×10) + (10×7) = 120
- Max Points: 100×10 = 1000
- **Risk Score: 12.0/100** ✅

#### SARIF Format for Security Tab

Generated SARIF 2.1.0 reports include:
- **Rules**: One per CIS control with full descriptions
- **Results**: Failed controls mapped to SARIF violations
- **Severity Mapping**: Critical=9.0, High=7.0, Medium=5.0, Low=3.0
- **Locations**: M365 tenant URIs for context
- **Fixes**: Remediation suggestions when available

Upload via `github/codeql-action/upload-sarif@v3` with `security-events: write` permission.

#### Compliance Trending

```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    compare-with-baseline: true
```

**How it works:**
1. First run saves baseline artifact (365-day retention)
2. Subsequent runs compare against baseline
3. Outputs:
   - `compliance-trend`: "+5.2%" (5.2% improvement)
   - `new-failures`: 3 (controls that started failing)
   - `fixed-issues`: 8 (controls that are now passing)
   - `trend-direction`: "improving"

**Use cases:**
- Fail PR if `trend-direction = "declining"`
- Generate charts showing compliance over time
- Alert security team on negative trends

#### Multi-Tenant Architecture

**Option A: Matrix Strategy (Recommended)**
```yaml
strategy:
  matrix:
    tenant: [Client-A, Client-B, Client-C]
steps:
  - uses: Heyson315/Easy-Ai@v1
    with:
      tenant-id: ${{ secrets[format('TENANT_ID_{0}', matrix.tenant)] }}
```

**Option B: Batch Configuration**
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-config: ${{ secrets.TENANT_BATCH_CONFIG }}
```

**Benefits for MSPs:**
- Audit 10+ clients in parallel
- Aggregate results across tenants
- Generate per-client reports
- Centralized compliance dashboard



## Development & Testing Workflow

### Python Development Pattern
- **Code Quality**: Black formatter (120 chars), flake8 linting, mypy type checking in `pyproject.toml`
- **Testing**: `pytest` with `TemporaryDirectory()` for file I/O, pandas validation
- **Dependencies**:
  - `requirements.txt` - Core toolkit + AI (openai, azure-identity) 🆕 UPDATED
  - `requirements-extensions.txt` - Optional plugins (MCP, msgraph-sdk)
  - `requirements-dev.txt` - Development tools
- **Performance**: Built-in benchmarking via `scripts/run_performance_benchmark.py --baseline`
- **Module Execution**:
  - ❌ `python -m scripts.file` (scripts recently became package but use direct execution)
  - ✅ `python scripts/file.py` (preferred for scripts)
  - ✅ `python -m src.integrations.sharepoint_connector` (proper for src/ modules)

### PowerShell Development Pattern
- **Module Pattern**: All functions prefixed with verb (`Test-CIS-*`, `Connect-M365CIS`, `New-CISResult`)
- **Return Standard**: `[PSCustomObject]` with fields: `ControlId`, `Title`, `Severity`, `Expected`, `Actual`, `Status`, `Evidence`, `Reference`, `Timestamp`
- **Error Handling**: Always wrap in try/catch returning `Status='Manual'` on failures
- **Path Handling**: Use absolute paths resolved from repo root via `Split-Path`
- **Testing**: Pester v5 with `Should -Be` (not `Should Be`), `-TestCases` for parameterized tests


### GitHub Action v1.2.0 - Enhanced Features

The published GitHub Action (Heyson315/Easy-Ai@v1) now includes **enterprise-grade capabilities**:

#### Advanced Outputs (25+ Variables)

**Risk Scoring (Severity-Weighted 0-100 Scale):**
- `risk-score`: Overall risk score (0-100, weighted by severity: Critical=10, High=7, Medium=4, Low=1)
- `critical-findings`: Count of critical severity failures
- `high-findings`: Count of high severity failures
- `medium-findings`: Count of medium severity failures
- `low-findings`: Count of low severity failures

**Compliance Trending (Historical Comparison):**
- `compliance-trend`: Percentage change vs baseline (e.g., "+5.2%", "-2.1%")
- `new-failures`: Count of newly failing controls since baseline
- `fixed-issues`: Count of controls fixed since baseline
- `trend-direction`: "improving", "stable", or "declining"

**Security Integration:**
- `sarif-report`: Path to SARIF 2.1.0 report for GitHub Security tab
- `security-findings-count`: Total findings uploaded to Security tab

**Automated Remediation:**
- `remediated-controls`: Comma-separated list of auto-fixed control IDs
- `remediation-report`: Path to detailed remediation log

#### Key Inputs

**Multi-Tenant Support:**
```yaml
tenant-config: |
  [
    {"name": "Client-A", "tenantId": "guid-1", "spoAdmin": "https://clienta-admin.sharepoint.com"},
    {"name": "Client-B", "tenantId": "guid-2", "spoAdmin": "https://clientb-admin.sharepoint.com"}
  ]
```

**Automated Remediation:**
```yaml
enable-auto-remediation: true
auto-approve-remediation: false  # Requires approval gate
remediation-controls: '1.1.1,1.1.3,2.1.1'  # Target specific controls
```

**Security Tab Integration:**
```yaml
upload-to-security-tab: true
security-severity-threshold: high  # Only upload high/critical findings
```

**Compliance Trending:**
```yaml
compare-with-baseline: true
baseline-artifact-name: 'compliance-baseline'  # Saved for 365 days
```

#### Real-World Workflow Examples

See **[WORKFLOW_EXAMPLES.md](.github/WORKFLOW_EXAMPLES.md)** for 6 production-ready scenarios:

1. **Basic Audit with Security Tab** - Monthly scheduled scan uploading SARIF to Security tab
2. **Automated Remediation with Approval** - WhatIf/Force mode with GitHub Environments approval gates
3. **Multi-Tenant Batch Audit** - Matrix strategy for MSPs managing multiple M365 tenants
4. **PR Compliance Gate** - Block PRs if compliance drops below 80% or risk score > 70
5. **Teams Notification** - Alert Microsoft Teams on critical/high findings
6. **Continuous Monitoring** - Update compliance badge every 6 hours, trigger incident response

#### Risk Scoring Algorithm

```powershell
# Severity weights
$weights = @{ "Critical" = 10; "High" = 7; "Medium" = 4; "Low" = 1 }

# Calculate weighted risk
$totalRiskPoints = ($criticalCount * 10) + ($highCount * 7) + ($mediumCount * 4) + ($lowCount * 1)
$maxRiskPoints = $totalControlsCount * 10
$riskScore = ($totalRiskPoints / $maxRiskPoints) * 100
```

**Example:** 100 controls, 5 critical failures, 10 high failures:
- Risk Points: (5×10) + (10×7) = 120
- Max Points: 100×10 = 1000
- **Risk Score: 12.0/100** ✅

#### SARIF Format for Security Tab

Generated SARIF 2.1.0 reports include:
- **Rules**: One per CIS control with full descriptions
- **Results**: Failed controls mapped to SARIF violations
- **Severity Mapping**: Critical=9.0, High=7.0, Medium=5.0, Low=3.0
- **Locations**: M365 tenant URIs for context
- **Fixes**: Remediation suggestions when available

Upload via `github/codeql-action/upload-sarif@v3` with `security-events: write` permission.

#### Compliance Trending

```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    compare-with-baseline: true
```

**How it works:**
1. First run saves baseline artifact (365-day retention)
2. Subsequent runs compare against baseline
3. Outputs:
   - `compliance-trend`: "+5.2%" (5.2% improvement)
   - `new-failures`: 3 (controls that started failing)
   - `fixed-issues`: 8 (controls that are now passing)
   - `trend-direction`: "improving"

**Use cases:**
- Fail PR if `trend-direction = "declining"`
- Generate charts showing compliance over time
- Alert security team on negative trends

#### Multi-Tenant Architecture

**Option A: Matrix Strategy (Recommended)**
```yaml
strategy:
  matrix:
    tenant: [Client-A, Client-B, Client-C]
steps:
  - uses: Heyson315/Easy-Ai@v1
    with:
      tenant-id: ${{ secrets[format('TENANT_ID_{0}', matrix.tenant)] }}
```

**Option B: Batch Configuration**
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-config: ${{ secrets.TENANT_BATCH_CONFIG }}
```

**Benefits for MSPs:**
- Audit 10+ clients in parallel
- Aggregate results across tenants
- Generate per-client reports
- Centralized compliance dashboard



## Critical Workflows

### 1. M365 CIS Security Audit (Core Workflow)
```powershell
# Full audit with timestamping
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/Invoke-M365CISAudit.ps1" `
  -Timestamped `
  -SPOAdminUrl "https://tenant-admin.sharepoint.com"

# Convert JSON to Excel
python scripts/m365_cis_report.py

# Generate interactive dashboard
python scripts/generate_security_dashboard.py
```

**What This Does:**
- Connects to EXO, Graph, SPO, Purview, Intune
- Executes 15+ CIS controls via `M365CIS.psm1` functions
- Outputs timestamped JSON for audit trail
- Generates Excel reports with formatting
- Creates HTML dashboards with Chart.js visualizations

### 2. SharePoint Permissions Analysis
```powershell
# Step 1: Clean raw CSV (critical - SharePoint exports are messy)
python scripts/clean_csv.py `
  --input "data/raw/sharepoint/export.csv" `
  --output "data/processed/sharepoint_clean.csv"

# Step 2: Generate business report
python -m src.integrations.sharepoint_connector `
  --input "data/processed/sharepoint_clean.csv" `
  --output "output/reports/business/sharepoint_permissions.xlsx"
```

**CSV Cleaning Handles:**
- UTF-8 BOM removal (`encoding='utf-8-sig'`)
- Comment lines (`# ...`)
- Blank lines
- Duplicate headers (common in SharePoint exports)
- Quoted commas (preserves paths like `"parent/path,with,comma"`)

### 3. GitHub Action Workflow (NEW v1.2.0) 🆕
**Use in Your Repository:**

```yaml
# .github/workflows/m365-audit.yml
name: Monthly M365 Security Audit

on:
  schedule:
    - cron: '0 2 1 * *'  # 2 AM on 1st of month
  workflow_dispatch:
  pull_request:
    paths:
      - '.github/workflows/**'
      - 'infrastructure/**'

jobs:
  security-audit:
    name: M365 CIS Compliance Check
    runs-on: ubuntu-latest

    steps:
      - name: Run Security Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          spo-admin-url: ${{ secrets.SPO_ADMIN_URL }}
          generate-dashboard: true
          timestamped: true
          output-path: 'audit-reports'
          artifact-retention-days: 90

      - name: Evaluate Compliance
        run: |
          echo "Compliance Score: ${{ steps.audit.outputs.compliance-score }}%"
          echo "Passed: ${{ steps.audit.outputs.controls-passed }}"
          echo "Failed: ${{ steps.audit.outputs.controls-failed }}"

          # Fail if below threshold
          if (( $(echo "${{ steps.audit.outputs.compliance-score }} < 75" | bc -l) )); then
            echo "::error::Compliance score below 75% threshold!"
            exit 1
          fi

      - name: Upload Dashboard to Pages
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/Primary'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./audit-reports
          destination_dir: security-dashboard

      - name: Notify Teams
        if: steps.audit.outputs.controls-failed > 0
        uses: aliencube/microsoft-teams-actions@v0.8.0
        with:
          webhook_uri: ${{ secrets.TEAMS_WEBHOOK }}
          title: '⚠️ M365 Security Audit - Issues Found'
          text: 'Failed controls: ${{ steps.audit.outputs.controls-failed }}'
```

**Secret Configuration (Repository Settings):**
```yaml
M365_TENANT_ID: "your-tenant-id-guid"
M365_CLIENT_ID: "your-app-client-id-guid"
M365_CLIENT_SECRET: "your-app-client-secret"
SPO_ADMIN_URL: "https://tenant-admin.sharepoint.com"
```

**Action Outputs Available:**
```yaml
${{ steps.audit.outputs.audit-report-json }}     # Path to JSON report
${{ steps.audit.outputs.audit-report-excel }}    # Path to Excel report
${{ steps.audit.outputs.dashboard-html }}        # Path to HTML dashboard
${{ steps.audit.outputs.compliance-score }}      # e.g., "85.3"
${{ steps.audit.outputs.controls-passed }}       # e.g., "42"
${{ steps.audit.outputs.controls-failed }}       # e.g., "8"
${{ steps.audit.outputs.controls-manual }}       # e.g., "5"
```

**Common Use Cases:**
1. **Pull Request Gates**: Block PRs that would degrade security posture
2. **Scheduled Audits**: Monthly compliance reports with artifact retention
3. **Multi-Tenant**: Matrix strategy to audit multiple clients
4. **Notification Integration**: Teams/Slack alerts on failures

### 4. MCP Server Integration (Optional Extension)
```bash
# Install optional dependencies first
pip install -r requirements-extensions.txt

# Option A: Simple MCP Server
python -m src.extensions.mcp.setup     # Interactive wizard
python -m src.extensions.mcp.server    # Run server

# Option B: Plugin-Based MCP Server (recommended for production)
python -m src.mcp.m365_mcp_server
```

**Available MCP Tools:**
- `run_security_audit` - Execute CIS compliance audit
- `analyze_sharepoint_permissions` - Permission analysis
- `get_security_dashboard` - Generate HTML dashboard
- `remediate_security_issues` - Safe remediation with preview
- `get_compliance_status` - Current compliance metrics

### 5. Safe Remediation Workflow
```powershell
# Preview changes (SAFE - no modifications)
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/PostRemediateM365CIS.ps1" -WhatIf

# Apply changes (CAUTION - modifies tenant)
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/PostRemediateM365CIS.ps1" -Force
```

**Best Practice:** Always run `-WhatIf` first in production!

### 6. Audit Comparison & Trending
```powershell
# Compare two audit runs
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/Compare-M365CISResults.ps1" `
  -BeforeFile "before.json" `
  -AfterFile "after.json" `
  -OutputHtml "comparison.html"
```

## Project-Specific Conventions

### File Path Handling
**PowerShell:**
```powershell
# ✅ Always use absolute paths
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$scriptPath = Join-Path $repoRoot "scripts\powershell\MyScript.ps1"
```

**Python:**
```python
# ✅ Use pathlib.Path with automatic directory creation
from pathlib import Path

output_path = Path("output/reports/security/report.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
```

### CSV Processing Pattern
**Problem:** SharePoint exports contain:
- UTF-8 BOM
- Comment lines (`# Export date: ...`)
- Blank lines
- Repeated headers (when data spans multiple pages)
- Quoted commas in paths

**Solution (`scripts/clean_csv.py`):**
```python
# 1. Read with BOM handling
content = input_path.read_text(encoding='utf-8-sig')

# 2. Filter comments and blanks
lines = [line for line in content.splitlines()
         if line.strip() and not line.startswith('#')]

# 3. Use csv.reader to preserve quoted commas
reader = csv.reader(lines)

# 4. Track and skip duplicate headers
# 5. Return stats dict for validation
```

### PowerShell Module Pattern (`M365CIS.psm1`)
**Conventions (27KB, 600+ lines of production code):**
```powershell
function Test-CIS-X.Y.Z {
    <#
    .SYNOPSIS
    Brief control description
    #>
    try {
        # Get actual configuration
        $actual = Get-SomeM365Config
        $expected = "Required Value"

        # Determine status
        $status = if ($actual -eq $expected) { "Pass" } else { "Fail" }

        # Return standardized result
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control Title" `
            -Severity "Medium" `
            -Expected $expected `
            -Actual $actual `
            -Status $status `
            -Evidence "Detailed evidence" `
            -Reference "https://docs.microsoft.com/..."
    }
    catch {
        # Always return Manual status on errors
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control Title" `
            -Severity "Medium" `
            -Expected "N/A" `
            -Actual "Error: $($_.Exception.Message)" `
            -Status "Manual" `
            -Evidence "Error occurred" `
            -Reference "https://docs.microsoft.com/..."
    }
}
```

**Critical Features:**
- Multi-service connection (EXO, Graph, SPO, Purview) with graceful fallbacks
- Auto-fix OneDrive PSModulePath for synced modules
- Explicit module imports with `-ErrorAction Stop`

### Excel Report Generation Pattern
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import pandas as pd

# 1. Aggregate data with pandas
df = pd.DataFrame(data)
summary = df.groupby('category').size().reset_index(name='count')

# 2. Create workbook
wb = Workbook()
ws = wb.active

# 3. Write headers with formatting
ws.append(list(summary.columns))
for col in range(1, len(summary.columns) + 1):
    cell = ws.cell(1, col)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color='4472C4', fill_type='solid')
    cell.alignment = Alignment(horizontal='center')

# 4. Write data rows
for _, row in summary.iterrows():
    ws.append(list(row))

# 5. Auto-size columns
for col in range(1, len(summary.columns) + 1):
    ws.column_dimensions[get_column_letter(col)].width = 15

# 6. Save with directory creation
output_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(output_path)
```

### Docker Development Pattern
**Start Development Environment:**
```bash
# Start all services
docker-compose up -d

# Run tests in container
docker-compose exec mcp-server python -m pytest tests/ -v

# Run audit in container (requires M365 credentials in .env)
docker-compose exec mcp-server powershell -File scripts/powershell/Invoke-M365CISAudit.ps1

# Stop environment
docker-compose down
```

**Conventions:**
- ✅ Mount workspace as volume for live development
- ✅ Use `.dockerignore` to exclude `.venv/`, `__pycache__/`, `output/`
- ✅ Run CI/CD tests in same container as local development
- ✅ Store credentials in `.env` file (never commit!)

### Performance Optimization Pattern
**Chunked CSV Processing:**
```python
import pandas as pd
from pathlib import Path

def process_large_sharepoint_export(csv_path: Path, chunk_size: int = 10000):
    """Process SharePoint exports >100k rows without memory issues."""
    results = []

    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        # Process each chunk independently
        processed = transform_permissions(chunk)
        results.append(processed)

    # Combine results
    return pd.concat(results, ignore_index=True)
```

**Parallel Tenant Audits:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def audit_multiple_tenants(tenant_ids: list[str], max_workers: int = 5):
    """Audit multiple M365 tenants concurrently (max 5 to avoid rate limits)."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_audit, tid): tid
            for tid in tenant_ids
        }

        results = {}
        for future in as_completed(futures):
            tenant_id = futures[future]
            try:
                results[tenant_id] = future.result(timeout=600)
            except Exception as e:
                results[tenant_id] = {'error': str(e), 'status': 'failed'}

        return results
```

**Performance Targets:**
- CSV cleaning: <2s for 10k rows
- Excel generation: <5s for 100 controls
- Dashboard generation: <3s
- Full M365 audit: <10 minutes

### CI/CD Error Resolution Pattern
**Common Failures:**

**Issue 1: PowerShell Module Import in GitHub Actions**
```yaml
- name: Run M365 Audit
  run: |
    # Fix: Explicitly set PSModulePath
    $env:PSModulePath += ";$PWD/scripts/powershell/modules"
    Import-Module M365CIS -Force
    ./scripts/powershell/Invoke-M365CISAudit.ps1 -Timestamped
  shell: pwsh
```

**Issue 2: Python Dependencies Installation**
```yaml
- name: Install all dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    # Optional: Only install if MCP features needed
    pip install -r requirements-extensions.txt || echo "MCP extensions skipped"
```

**Issue 3: Artifact Upload Safety**
```yaml
- name: Upload test reports
  if: always()  # Upload even on test failures
  uses: actions/upload-artifact@v4
  with:
    name: test-reports
    path: output/reports/
    if-no-files-found: warn  # Don't fail if no files generated
```

**Issue 4: Test Timeout**
```python
import pytest

@pytest.mark.timeout(300)  # 5 minute timeout
@pytest.mark.integration
def test_full_m365_audit():
    """Full audit can take several minutes."""
    result = run_audit()
    assert result['status'] == 'success'
```

### Multi-Root Workspace Pattern
**VS Code Multi-Root Setup** (`Easy-Ai.code-workspace`):

```json
{
  "folders": [
    {
      "path": ".",
      "name": "Easy-Ai"
    },
    {
      "path": "../venv",
      "name": "Python Environment"
    }
  ],
  "settings": {
    "python.defaultInterpreterPath": "${workspaceFolder:venv}/Scripts/python.exe"
  }
}
```

**Why Multi-Root?**
- Keeps `.venv/` out of primary workspace (cleaner file explorer)
- Prevents accidental commits of virtual environment
- Faster file search and indexing

**Conventions:**
- ✅ Run terminal commands from `Easy-Ai` root, not `venv` folder
- ✅ Git operations only affect `Easy-Ai` folder (`.git` is there)
- ✅ Python interpreter: `../venv/Scripts/python.exe` (Windows) or `../venv/bin/python` (Linux/Mac)

### Error Handling Pattern
**❌ Bad (Generic Exception):**
```python
try:
    data = json.loads(file.read())
except Exception as e:  # Too broad!
    print(f"Error: {e}")
```

**✅ Good (Specific Exceptions):**
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

### Testing Pattern
**Python (pytest with tempfile):**
```python
from tempfile import TemporaryDirectory
from pathlib import Path
import pandas as pd

def test_process_csv():
    with TemporaryDirectory() as td:
        td = Path(td)
        input_file = td / "input.csv"
        output_file = td / "output.csv"

        # Write test input
        input_file.write_text("col1,col2\n1,2", encoding="utf-8")

        # Run function
        stats = process_csv(input_file, output_file)

        # Validate with pandas
        assert output_file.exists()
        df = pd.read_csv(output_file)
        assert df.shape == (1, 2)
        assert stats['output_rows'] == 1
```

**PowerShell (Pester v5):**
```powershell
Describe "Test-CIS-Function" {
    It "Should return Pass status when compliant" {
        # Arrange
        Mock Get-SomeConfig { return "ExpectedValue" }

        # Act
        $result = Test-CIS-X.Y.Z

        # Assert
        $result.Status | Should -Be "Pass"
    }
}
```

## External Dependencies & Integration Points

### PowerShell Modules (Install with `-Scope CurrentUser`)
```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Authentication -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Identity.DirectoryManagement -Scope CurrentUser
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
```

### Python Packages
**Core (Required):**
- `pandas` - CSV/Excel I/O, data aggregation
- `openpyxl` - Excel formatting
- `openai` - GPT-5 integration (NOW CORE) 🆕
- `azure-identity` - Azure AD authentication (NOW CORE) 🆕
- `pytest` - Testing framework

**Extensions (Optional):**
- `mcp` - Model Context Protocol SDK
- `msgraph-sdk` - Microsoft Graph real-time access
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management

### Authentication Flow
1. **Interactive (Default):** `Connect-M365CIS` → Browser login with MFA support
2. **Service Principal (CI/CD):** Environment variables for unattended automation
3. **Required Scopes:** `User.Read.All`, `Policy.Read.All`, `Directory.Read.All`, `Organization.Read.All`
4. **Admin Roles:** Exchange Admin, Global Reader/Security Reader, SharePoint Admin

## Git Conventions & Output Organization

### Version Control Strategy (.gitignore)
- **✅ Include:** JSON/CSV reports (text-based, diffable, lightweight)
- **❌ Exclude:** Excel files (binary, causes bloat - use Git LFS if needed)
- **❌ Exclude:** Virtual envs (`.venv/`), `__pycache__/`, coverage HTML
- **Branch:** Default is `Primary` (not `main`) 🆕

### Output Organization
```
output/reports/
├── security/           # CIS audit results (JSON/CSV/XLSX/HTML)
├── business/           # SharePoint/domain reports (XLSX)
data/
├── raw/                # Unprocessed exports (not in git)
├── processed/          # Cleaned CSVs (git-tracked)
└── archive/            # Historical snapshots (timestamped)
```

## Common Pitfalls & Solutions

### ❌ Wrong Branch References
```yaml
# ❌ DON'T: Reference 'main' branch
branches: [ main, develop ]

# ✅ DO: Use 'Primary' as default branch
branches: [ Primary, develop ]
```

### ❌ Module Execution Errors
```bash
# ❌ DON'T: Use -m with scripts
python -m scripts.clean_csv

# ✅ DO: Direct execution for scripts
python scripts/clean_csv.py

# ✅ DO: Use -m for src/ modules
python -m src.integrations.sharepoint_connector
```

### ❌ CSV Header Assumptions
```python
# ❌ DON'T: Assume clean headers
df = pd.read_csv("raw_export.csv")  # May have BOM, comments!

# ✅ DO: Always clean first
from scripts.clean_csv import clean_csv
clean_csv(raw_path, clean_path)
df = pd.read_csv(clean_path)
```

### ❌ Hardcoded Paths
```python
# ❌ DON'T: Hardcode tenant URLs or file paths
output = "C:\\Users\\Me\\output.xlsx"

# ✅ DO: Use parameters with defaults
output_path = Path(output_param or "output/reports/business/report.xlsx")
```

### ❌ Missing GitHub Action Secrets
```yaml
# ❌ DON'T: Hardcode credentials
client-secret: 'my-secret-value'

# ✅ DO: Use GitHub secrets
client-secret: ${{ secrets.M365_CLIENT_SECRET }}
```

**Setup GitHub Secrets:**
1. Repository → Settings → Secrets and variables → Actions
2. New repository secret:
   - `M365_TENANT_ID`
   - `M365_CLIENT_ID`
   - `M365_CLIENT_SECRET`
   - `SPO_ADMIN_URL`

### ✅ Best Practices Summary
- Use `-Timestamped` flag for audit evidence versioning
- Validate JSON structure before Excel conversion
- Use `-WhatIf` for safe remediation previews
- Leverage GitHub Action for CI/CD integration 🆕
- Configure tools via `pyproject.toml`
- Use `TemporaryDirectory()` for all file I/O tests
- Reference `Primary` branch, not `main` 🆕

## Quick Reference for AI Agents

| Task | Command | Location |
|------|---------|----------|
| Run M365 Audit | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1" -Timestamped` | `scripts/powershell/` |
| Clean CSV | `python scripts/clean_csv.py --input "raw.csv" --output "clean.csv"` | `scripts/` |
| Generate Excel Report | `python scripts/m365_cis_report.py` | `scripts/` |
| Generate HTML Dashboard | `python scripts/generate_security_dashboard.py` | `scripts/` |
| Analyze SharePoint | `python -m src.integrations.sharepoint_connector --input "clean.csv"` | `src/integrations/` |
| Run Tests | `pytest --cov=scripts --cov=src --cov-report=html` | `tests/` |
| Code Formatting | `black --line-length 120 scripts/ src/` | Root |
| Linting | `flake8 scripts/ src/ tests/ --max-line-length 120` | Root |
| MCP Server (Simple) | `python -m src.extensions.mcp.server` | `src/extensions/mcp/` |
| MCP Server (Plugin) | `python -m src.mcp.m365_mcp_server` | `src/mcp/` |
| Performance Benchmark | `python scripts/run_performance_benchmark.py --baseline` | `scripts/` |
| Use as GitHub Action 🆕 | `uses: Heyson315/Easy-Ai@v1` | In workflows |

## AI Development Resources

**Essential Guides for AI Coding Agents:**
- 📘 **[AI Agent Quick Start](AI_AGENT_QUICKSTART.md)** - 15-minute onboarding with common tasks
- 🧪 **[AI Workflow Testing](AI_WORKFLOW_TESTING.md)** - Testing patterns and automation
- 🤖 **[MCP Tool Patterns](MCP_TOOL_PATTERNS.md)** - Model Context Protocol development
- 📖 **[AI Development Index](AI_DEVELOPMENT_INDEX.md)** - Complete navigation hub
- 🎨 **[Web Design Guide](../docs/WEB_DESIGN_GUIDE.md)** - SharePoint/GoDaddy patterns

**When to Use Each Guide:**
- �� **Starting new task?** → [AI Agent Quick Start](AI_AGENT_QUICKSTART.md)
- 🧪 **Writing tests?** → [AI Workflow Testing](AI_WORKFLOW_TESTING.md)
- 🤖 **Building MCP tools?** → [MCP Tool Patterns](MCP_TOOL_PATTERNS.md)
- 🎨 **Designing web interfaces?** → [Web Design Guide](../docs/WEB_DESIGN_GUIDE.md)
- 🏗️ **Understanding architecture?** → This document

## Extension Development Patterns

### Adding GitHub Action to Another Repo
**Minimal Configuration:**
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID }}
    client-id: ${{ secrets.M365_CLIENT_ID }}
    client-secret: ${{ secrets.M365_CLIENT_SECRET }}
```

**Full Configuration:**
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID }}
    client-id: ${{ secrets.M365_CLIENT_ID }}
    client-secret: ${{ secrets.M365_CLIENT_SECRET }}
    spo-admin-url: 'https://tenant-admin.sharepoint.com'
    timestamped: true
    skip-purview: false
    generate-dashboard: true
    output-path: 'custom/output/path'
    artifact-retention-days: 90
```

### Adding New MCP Plugin (Plugin-Based Architecture)
```python
# src/mcp/plugins/my_tool/tools.py
class MyNewToolPlugin:
    """Custom MCP tool"""

    def execute(self, param1: str, param2: int = 100) -> dict:
        """Execute the tool"""
        try:
            result = process_task(param1, param2)

            return {
                "status": "success",
                "data": result,
                "message": f"Successfully processed {param1}"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Tool failed: {type(e).__name__}",
                "error": str(e)
            }
```

```json
# src/mcp/plugins/my_tool/plugin.json
{
  "name": "my_new_tool",
  "version": "1.0.0",
  "description": "Executes custom task",
  "author": "Your Name",
  "tools": [
    {
      "name": "execute_custom_task",
      "class": "MyNewToolPlugin",
      "description": "Executes custom task with parameters",
      "parameters": {
        "param1": {
          "type": "string",
          "description": "First parameter",
          "required": true
        },
        "param2": {
          "type": "integer",
          "description": "Second parameter",
          "required": false,
          "default": 100
        }
      }
    }
  ]
}
```

## Debugging & Troubleshooting

### PowerShell Module Path Issues
**Symptom:** `Import-Module M365CIS.psm1` fails even though file exists

**Solution:** `Connect-M365CIS` auto-fixes OneDrive PSModulePath:
```powershell
# Automatically added by Connect-M365CIS
$oneDrivePath = Join-Path $env:USERPROFILE "OneDrive\PowerShell\Modules"
if (-not ($env:PSModulePath -split ';' -contains $oneDrivePath)) {
    $env:PSModulePath += ";$oneDrivePath"
}
```

**Manual Fix (if needed):**
```powershell
# Import with full path
Import-Module "./scripts/powershell/modules/M365CIS.psm1" -Force

# Or fix PSModulePath permanently
$env:PSModulePath += ";$PWD\scripts\powershell\modules"
```

### CSV Parsing Failures
**Symptom:** `pandas.errors.ParserError: Error tokenizing data`

**Root Cause:** SharePoint exports contain:
- UTF-8 BOM (Byte Order Mark)
- Comment lines starting with `#`
- Repeated headers across pages
- Quoted commas in file paths

**Solution:** Use `scripts/clean_csv.py` first - handles all these issues

**Validation:**
```bash
# Inspect cleaned CSV before processing
python scripts/inspect_processed_csv.py data/processed/clean.csv

# Or manually validate
python -c "import pandas as pd; print(pd.read_csv('clean.csv').info())"
```

**Performance Impact:**
- Cleaning 5,000 rows: ~0.06s, 0.21MB memory
- Cleaning 50,000 rows: ~0.6s, 2.1MB memory
- Memory scales linearly with file size

### Excel Generation Errors
**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory`

**Root Cause:** Parent directory doesn't exist

**Solution:** Always create parent directories:
```python
output_path = Path("output/reports/business/report.xlsx")
output_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(output_path)
```

**Related Error:** `PermissionError: [Errno 13] Permission denied`
- **Cause:** File is open in Excel
- **Solution:** Close Excel or use a different output filename

### MCP Extension Not Found
**Symptom:** `ImportError: No module named 'mcp'`

**Root Cause:** Extensions are optional and not installed by default

**Solution:** Extensions are optional - install separately:
```bash
pip install -r requirements-extensions.txt
```

**Check What's Installed:**
```bash
pip list | grep -E "(mcp|msgraph|azure-identity)"
```

**Graceful Degradation Pattern:**
```python
try:
    from mcp import MCPServer
    USE_MCP = True
except ImportError:
    USE_MCP = False
    print("MCP extensions not installed. Continuing without AI features.")
```


### GitHub Action v1.2.0 - Enhanced Features

The published GitHub Action (Heyson315/Easy-Ai@v1) now includes **enterprise-grade capabilities**:

#### Advanced Outputs (25+ Variables)

**Risk Scoring (Severity-Weighted 0-100 Scale):**
- `risk-score`: Overall risk score (0-100, weighted by severity: Critical=10, High=7, Medium=4, Low=1)
- `critical-findings`: Count of critical severity failures
- `high-findings`: Count of high severity failures
- `medium-findings`: Count of medium severity failures
- `low-findings`: Count of low severity failures

**Compliance Trending (Historical Comparison):**
- `compliance-trend`: Percentage change vs baseline (e.g., "+5.2%", "-2.1%")
- `new-failures`: Count of newly failing controls since baseline
- `fixed-issues`: Count of controls fixed since baseline
- `trend-direction`: "improving", "stable", or "declining"

**Security Integration:**
- `sarif-report`: Path to SARIF 2.1.0 report for GitHub Security tab
- `security-findings-count`: Total findings uploaded to Security tab

**Automated Remediation:**
- `remediated-controls`: Comma-separated list of auto-fixed control IDs
- `remediation-report`: Path to detailed remediation log

#### Key Inputs

**Multi-Tenant Support:**
```yaml
tenant-config: |
  [
    {"name": "Client-A", "tenantId": "guid-1", "spoAdmin": "https://clienta-admin.sharepoint.com"},
    {"name": "Client-B", "tenantId": "guid-2", "spoAdmin": "https://clientb-admin.sharepoint.com"}
  ]
```

**Automated Remediation:**
```yaml
enable-auto-remediation: true
auto-approve-remediation: false  # Requires approval gate
remediation-controls: '1.1.1,1.1.3,2.1.1'  # Target specific controls
```

**Security Tab Integration:**
```yaml
upload-to-security-tab: true
security-severity-threshold: high  # Only upload high/critical findings
```

**Compliance Trending:**
```yaml
compare-with-baseline: true
baseline-artifact-name: 'compliance-baseline'  # Saved for 365 days
```

#### Real-World Workflow Examples

See **[WORKFLOW_EXAMPLES.md](.github/WORKFLOW_EXAMPLES.md)** for 6 production-ready scenarios:

1. **Basic Audit with Security Tab** - Monthly scheduled scan uploading SARIF to Security tab
2. **Automated Remediation with Approval** - WhatIf/Force mode with GitHub Environments approval gates
3. **Multi-Tenant Batch Audit** - Matrix strategy for MSPs managing multiple M365 tenants
4. **PR Compliance Gate** - Block PRs if compliance drops below 80% or risk score > 70
5. **Teams Notification** - Alert Microsoft Teams on critical/high findings
6. **Continuous Monitoring** - Update compliance badge every 6 hours, trigger incident response

#### Risk Scoring Algorithm

```powershell
# Severity weights
$weights = @{ "Critical" = 10; "High" = 7; "Medium" = 4; "Low" = 1 }

# Calculate weighted risk
$totalRiskPoints = ($criticalCount * 10) + ($highCount * 7) + ($mediumCount * 4) + ($lowCount * 1)
$maxRiskPoints = $totalControlsCount * 10
$riskScore = ($totalRiskPoints / $maxRiskPoints) * 100
```

**Example:** 100 controls, 5 critical failures, 10 high failures:
- Risk Points: (5×10) + (10×7) = 120
- Max Points: 100×10 = 1000
- **Risk Score: 12.0/100** ✅

#### SARIF Format for Security Tab

Generated SARIF 2.1.0 reports include:
- **Rules**: One per CIS control with full descriptions
- **Results**: Failed controls mapped to SARIF violations
- **Severity Mapping**: Critical=9.0, High=7.0, Medium=5.0, Low=3.0
- **Locations**: M365 tenant URIs for context
- **Fixes**: Remediation suggestions when available

Upload via `github/codeql-action/upload-sarif@v3` with `security-events: write` permission.

#### Compliance Trending

```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    compare-with-baseline: true
```

**How it works:**
1. First run saves baseline artifact (365-day retention)
2. Subsequent runs compare against baseline
3. Outputs:
   - `compliance-trend`: "+5.2%" (5.2% improvement)
   - `new-failures`: 3 (controls that started failing)
   - `fixed-issues`: 8 (controls that are now passing)
   - `trend-direction`: "improving"

**Use cases:**
- Fail PR if `trend-direction = "declining"`
- Generate charts showing compliance over time
- Alert security team on negative trends

#### Multi-Tenant Architecture

**Option A: Matrix Strategy (Recommended)**
```yaml
strategy:
  matrix:
    tenant: [Client-A, Client-B, Client-C]
steps:
  - uses: Heyson315/Easy-Ai@v1
    with:
      tenant-id: ${{ secrets[format('TENANT_ID_{0}', matrix.tenant)] }}
```

**Option B: Batch Configuration**
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-config: ${{ secrets.TENANT_BATCH_CONFIG }}
```

**Benefits for MSPs:**
- Audit 10+ clients in parallel
- Aggregate results across tenants
- Generate per-client reports
- Centralized compliance dashboard



## Performance Benchmarks

### Real-World Performance Metrics

**Test Environment:**
- CPU: Intel i7-10700K (8 cores)
- RAM: 32GB DDR4
- Storage: NVMe SSD
- OS: Windows 11 Pro
- Python: 3.11.5
- PowerShell: 7.4.0

**Benchmark Results (5,000 row dataset):**
```
Operation                               Time        Memory      Status
========================================================================
CSV Cleaning (5,000 rows)               0.060s      0.21MB      ✅ FAST
CSV Cleaning (50,000 rows)              0.620s      2.10MB      ✅ FAST
M365 CIS Report (200 controls)          0.411s      6.07MB      ✅ FAST
Statistics Calculation (200 controls)   <0.001s     0.00MB      ✅ FAST
SharePoint Summary (5,000 rows)         0.029s      1.16MB      ✅ FAST
SharePoint Summary (50,000 rows)        0.285s      11.60MB     ✅ FAST
Dashboard Generation (200 controls)     0.150s      2.50MB      ✅ FAST
Full M365 Audit (15 controls)           8-12 min    50MB        ⏱️ LONG
========================================================================
```

**Memory Usage by Operation:**
| Operation | Small (5k) | Medium (50k) | Large (500k) | Notes |
|-----------|------------|--------------|--------------|-------|
| CSV Cleaning | 0.21MB | 2.1MB | 21MB | Linear scaling |
| Excel Generation | 6MB | 15MB | 60MB | Includes formatting |
| SharePoint Analysis | 1.16MB | 12MB | 120MB | DataFrame overhead |
| Dashboard Creation | 2.5MB | 5MB | 15MB | Chart.js minimal |

**Performance Targets (All Met ✅):**
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| CSV Cleaning Time | < 0.1s (5k rows) | 0.060s | ✅ 40% faster |
| CSV Cleaning Memory | < 1MB | 0.21MB | ✅ 79% less |
| CIS Report Time | < 0.5s | 0.411s | ✅ 18% faster |
| CIS Report Memory | < 10MB | 6.07MB | ✅ 39% less |
| Statistics Time | < 0.01s | <0.001s | ✅ 10x faster |
| SharePoint Summary | < 0.05s | 0.029s | ✅ 42% faster |
| Dashboard Generation | < 0.2s | 0.150s | ✅ 25% faster |
| Full Audit | < 15 min | 8-12 min | ✅ 20-47% faster |

**Optimization Impact:**
- **CSV Cleaning:** 50% memory reduction through single-pass streaming
- **Dashboard Generation:** 50% fewer file I/O operations via early validation
- **SharePoint Analysis:** Conditional DataFrame copying only when needed
- **Overall:** All operations complete in <1s except full audit (API-bound)

### Scaling Characteristics

**Linear Scaling (Good):**
- CSV cleaning: O(n) time and memory
- Statistics calculation: O(n) time, O(1) memory
- SharePoint summaries: O(n) time and memory

**Sub-Linear Scaling (Excellent):**
- Dashboard generation: O(n log n) due to sorting
- Excel formatting: O(n) with fixed overhead

**API-Bound Operations (External Factors):**
- Full M365 audit: 8-12 minutes (depends on Microsoft API latency)
- Individual control tests: 1-30 seconds each
- Rate limiting: Up to 60s delays if throttled

### Performance Monitoring

**Built-in Benchmarking:**
```bash
# Run performance benchmarks
python scripts/run_performance_benchmark.py --baseline

# Compare after optimization
python scripts/run_performance_benchmark.py --compare

# Profile specific operation
python -m cProfile -o profile.stats scripts/clean_csv.py
python -m pstats profile.stats
>>> sort cumtime
>>> stats 20
```

**Memory Profiling:**
```python
import tracemalloc

tracemalloc.start()
# ... your code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f}MB, Peak: {peak / 1024 / 1024:.2f}MB")
tracemalloc.stop()
```

**GitHub Actions Performance:**
- Average CI/CD run: 3-5 minutes
- Cached dependencies: ~30s saved per run
- Parallel jobs: 2x faster than sequential
- Artifact upload: <1 minute for 50MB reports

### Performance Best Practices

**For Large Datasets (>100k rows):**
```python
# ✅ Use chunked processing
for chunk in pd.read_csv(file, chunksize=10000):
    process(chunk)

# ✅ Use generators for filtering
def filtered_lines(file):
    for line in file:
        if condition(line):
            yield line

# ✅ Process in parallel for independent operations
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(process, data_chunks)
```

**For API-Heavy Operations:**
```python
# ✅ Use batch requests
batch = graph_client.new_batch_request_builder()
batch.add_request(request1)
batch.add_request(request2)
response = await batch.post()

# ✅ Cache expensive calls
from functools import lru_cache

@lru_cache(maxsize=128)
def get_tenant_info(tenant_id):
    return expensive_api_call(tenant_id)

# ✅ Implement exponential backoff for rate limits
```

**For Excel Generation:**
```python
# ✅ Batch cell writes
ws.append(row_data)  # Faster than individual cell writes

# ✅ Avoid excessive formatting
# Apply styles to ranges instead of individual cells

# ✅ Use openpyxl's write_only mode for large files
wb = Workbook(write_only=True)
```

### When to Optimize Further

**Don't Optimize If:**
- Operation completes in <1 second
- Memory usage <100MB
- Code readability would suffer significantly

**Do Optimize If:**
- User-facing operations take >5 seconds
- Memory usage causes OOM errors
- Blocking other operations (async opportunities)
- Repeated in tight loops (caching opportunities)

**Future Optimization Opportunities:**
- Async PowerShell for parallel M365 API calls
- Caching Graph API responses locally
- Pre-compiled Pester tests
- Incremental audit updates (only changed controls)

---

**🎯 Architecture Summary:** Hybrid Python/PowerShell enterprise security toolkit with dual MCP implementations and published GitHub Action. Core auditing works standalone; extensions enhance with AI integration; GitHub Action enables zero-setup CI/CD workflows.

**🚀 Quick Start Paths:**
1. **Local Development:** Clone → Install deps → Run audit scripts
2. **CI/CD Integration:** Add GitHub Action → Configure secrets → Automated audits
3. **AI Extensions:** Install MCP deps → Choose simple or plugin-based → Integrate with AI assistants
4. **Multi-Repository:** Consume published action → Centralized security monitoring


