# API Reference

**M365 Security & SharePoint Analysis Toolkit**  
**Last Updated**: December 2025

Complete API documentation for Python modules, PowerShell functions, and MCP tools.

## Table of Contents

- [Python Modules](#python-modules)
  - [src.core.excel_generator](#srccore-excel_generator)
  - [src.core.cost_tracker](#srccore-cost_tracker)
  - [src.core.file_io](#srccore-file_io)
  - [src.core.profiler](#srccore-profiler)
  - [src.core.report_utils](#srccore-report_utils)
  - [src.integrations.sharepoint_connector](#srcintegrations-sharepoint_connector)
  - [src.integrations.openai_gpt5](#srcintegrations-openai_gpt5)
- [PowerShell Functions](#powershell-functions)
  - [M365CIS Module](#m365cis-module)
- [MCP Tools](#mcp-tools)
- [Type Definitions](#type-definitions)
- [Error Handling](#error-handling)

---

## Python Modules

### src.core.excel_generator

**Module**: `src/core/excel_generator.py`

Excel workbook generation utilities for project management and reporting.

#### Functions

##### `create_project_management_workbook(filename=None)`

Create a project management Excel workbook with multiple sheets.

**Parameters**:
- `filename` (str, optional): Output filename for the workbook. Defaults to `'Project_Management.xlsx'`.

**Returns**: None (writes file to disk)

**Sheets Created**:
1. **Financial Transactions**: Date, Description, Category, Income, Expense, Balance
2. **Project Tasks**: Task ID, Task Name, Start Date, Due Date, Status, Assigned To, Notes
3. **Budget Summary**: Category, Budgeted, Spent, Remaining, Percent Spent

**Example**:
```python
from src.core.excel_generator import create_project_management_workbook

# Create with default name
create_project_management_workbook()

# Create with custom name
create_project_management_workbook(filename="Q4-2025-Report.xlsx")
```

**Security Notes**:
- Creates file in current working directory - ensure directory is trusted
- Validates file path before writing
- Uses openpyxl for Excel generation (no macro support - safer)

---

### src.core.cost_tracker

**Module**: `src/core/cost_tracker.py`

GPT-5 cost monitoring and token usage tracking for AI-powered features.

#### Classes

##### `GPT5CostTracker`

Track and manage GPT-5 API costs for development and testing.

**Constructor**:
```python
GPT5CostTracker(budget_limit=None, log_file=None)
```

**Parameters**:
- `budget_limit` (float, optional): Daily budget limit in USD (triggers warnings)
- `log_file` (str, optional): Path to JSON log file for tracking usage history

**Pricing** (estimated, subject to change):

| Model | Input (per 1M tokens) | Cached Input | Output (per 1M tokens) |
|-------|----------------------|--------------|------------------------|
| gpt-5 | $4.00 | $2.00 | $12.00 |
| gpt-5-mini | $1.50 | $0.75 | $4.50 |
| gpt-5-nano | $0.75 | $0.375 | $2.25 |

**Methods**:

###### `track_request(model, input_tokens, output_tokens, cached_tokens=0)`

Track a GPT-5 API request and calculate costs.

**Parameters**:
- `model` (str): Model name (e.g., "gpt-5", "gpt-5-mini")
- `input_tokens` (int): Number of input tokens
- `output_tokens` (int): Number of output tokens
- `cached_tokens` (int, optional): Number of cached input tokens (50% discount)

**Returns**: `dict` with cost breakdown

**Example**:
```python
from src.core.cost_tracker import GPT5CostTracker

tracker = GPT5CostTracker(budget_limit=100.0, log_file="gpt5_usage.json")

# Track a request
cost_info = tracker.track_request(
    model="gpt-5",
    input_tokens=1500,
    output_tokens=500,
    cached_tokens=200
)

print(f"Request cost: ${cost_info['total_cost']:.4f}")
print(f"Daily total: ${tracker.get_daily_total():.2f}")
```

###### `get_daily_total()`

Get total cost for current day.

**Returns**: `float` - Total USD cost for current day

###### `get_statistics(days=7)`

Get usage statistics for recent days.

**Parameters**:
- `days` (int): Number of days to analyze (default: 7)

**Returns**: `dict` with statistics including:
- `total_cost`: Total cost for period
- `total_requests`: Total API requests
- `total_tokens`: Total tokens (input + output)
- `average_cost_per_request`: Average cost per request
- `peak_day`: Day with highest cost

###### `export_report(output_path)`

Export detailed usage report to JSON.

**Parameters**:
- `output_path` (str): Path to output file

**Returns**: None (writes file to disk)

###### `check_budget_alert()`

Check if budget limit exceeded and return alert.

**Returns**: `tuple` - (bool: is_exceeded, str: alert_message)

**Example Usage**:
```python
tracker = GPT5CostTracker(budget_limit=50.0)

# Track multiple requests
for i in range(10):
    tracker.track_request("gpt-5-mini", input_tokens=1000, output_tokens=300)

# Check budget
exceeded, message = tracker.check_budget_alert()
if exceeded:
    print(f"WARNING: {message}")

# Get statistics
stats = tracker.get_statistics(days=7)
print(f"7-day cost: ${stats['total_cost']:.2f}")
print(f"Average per request: ${stats['average_cost_per_request']:.4f}")

# Export report
tracker.export_report("gpt5_usage_report.json")
```

---

### src.core.file_io

**Module**: `src/core/file_io.py`

Shared file I/O utilities with UTF-8 BOM handling and consistent error handling.

#### Constants

##### `CIS_AUDIT_COLUMNS`

Standard column ordering for CIS audit data:
```python
[
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
```

#### Functions

##### `load_json_with_bom(json_path, exit_on_error=True)`

Load JSON file with UTF-8 BOM handling for PowerShell-generated files.

**Parameters**:
- `json_path` (Path): Path to the JSON file
- `exit_on_error` (bool, optional): If True, print error and exit on failure. If False, raise exception. Default: True

**Returns**: Parsed JSON data (dict or list)

**Raises** (when `exit_on_error=False`):
- `json.JSONDecodeError`: If JSON is invalid
- `FileNotFoundError`: If file doesn't exist
- `PermissionError`: If file can't be read

**Example**:
```python
from pathlib import Path
from src.core.file_io import load_json_with_bom

# Default behavior - exits on error
data = load_json_with_bom(Path("output/reports/security/audit.json"))

# Exception handling mode
try:
    data = load_json_with_bom(Path("audit.json"), exit_on_error=False)
except FileNotFoundError:
    print("File not found, using defaults")
    data = {"controls": []}
```

**Security Notes**:
- Automatically handles UTF-8 BOM from PowerShell output
- Validates file exists before reading
- Catches encoding errors from malformed files

##### `normalize_audit_data(data)`

Normalize audit data to a list of dictionaries.

Handles both single object and array formats from audit JSON files.

**Parameters**:
- `data` (Any): Parsed JSON data (can be dict or list)

**Returns**: `List[dict]` - List of audit result dictionaries

**Example**:
```python
from src.core.file_io import load_json_with_bom, normalize_audit_data

data = load_json_with_bom(Path("audit.json"))
results = normalize_audit_data(data)  # Always returns list

for result in results:
    print(f"{result['ControlId']}: {result['Status']}")
```

##### `ensure_parent_dir(path)`

Ensure the parent directory of a path exists.

**Parameters**:
- `path` (Path): File path whose parent directory should exist

**Returns**: `Path` - The original path (for method chaining)

**Example**:
```python
from pathlib import Path
from src.core.file_io import ensure_parent_dir

# Create parent directories if needed
output_file = ensure_parent_dir(Path("output/reports/security/audit.json"))
output_file.write_text('{"data": "value"}')

# Method chaining
Path("nested/dir/file.txt").pipe(ensure_parent_dir).write_text("content")
```

---

### src.core.profiler

**Module**: `src/core/profiler.py`

Performance profiling utilities for benchmarking and optimization.

#### Functions

##### `profile_function(func, *args, **kwargs)`

Profile a function's execution time and memory usage.

**Parameters**:
- `func` (callable): Function to profile
- `*args`: Positional arguments to pass to function
- `**kwargs`: Keyword arguments to pass to function

**Returns**: `tuple` - (result, execution_time_seconds, peak_memory_mb)

**Example**:
```python
from src.core.profiler import profile_function
import pandas as pd

def process_large_csv(file_path):
    return pd.read_csv(file_path)

result, exec_time, memory = profile_function(
    process_large_csv,
    "data/large_file.csv"
)

print(f"Execution time: {exec_time:.3f}s")
print(f"Peak memory: {memory:.2f}MB")
```

##### `benchmark_operations(operations, iterations=100)`

Benchmark multiple operations and compare performance.

**Parameters**:
- `operations` (dict): Dictionary mapping operation names to callables
- `iterations` (int, optional): Number of iterations per operation. Default: 100

**Returns**: `pd.DataFrame` - Benchmark results with columns:
  - `operation`: Operation name
  - `mean_time`: Average execution time (seconds)
  - `std_time`: Standard deviation of execution time
  - `min_time`: Minimum execution time
  - `max_time`: Maximum execution time

**Example**:
```python
from src.core.profiler import benchmark_operations

operations = {
    "list_comprehension": lambda: [x**2 for x in range(1000)],
    "map_function": lambda: list(map(lambda x: x**2, range(1000))),
    "generator": lambda: list(x**2 for x in range(1000)),
}

results = benchmark_operations(operations, iterations=1000)
print(results.sort_values("mean_time"))
```

---

### src.core.report_utils

**Module**: `src/core/report_utils.py`

Shared report inspection utilities.

#### Functions

##### `inspect_excel_report(report_path, head_rows=5)`

Inspect an Excel report by printing sheet information and sample data.

**Parameters**:
- `report_path` (Path): Path to the Excel file
- `head_rows` (int, optional): Number of rows to display from each sheet. Default: 5

**Returns**: None (prints to stdout)

**Raises**:
- `SystemExit(1)`: If report file not found

**Example**:
```python
from pathlib import Path
from src.core.report_utils import inspect_excel_report

# Inspect SharePoint permissions report
inspect_excel_report(
    Path("output/reports/business/sharepoint_permissions.xlsx"),
    head_rows=10
)
```

**Output Format**:
```
Report: output/reports/business/sharepoint_permissions.xlsx
Sheets: ['Overview', 'by_item_type', 'by_permission', 'top_users', 'top_resources', 'raw_data']

Sheet: Overview  shape=(4, 2)
              Summary                          Value
         Total Records                         5,234
    Unique Resources                           812
         Unique Users                          156
  Permission Types                             8

Sheet: by_item_type  shape=(5, 2)
   Item Type    Count
        File    3,421
      Folder    1,234
        Site      412
         ...      ...
```

---

### src.integrations.sharepoint_connector

**Module**: `src/integrations/sharepoint_connector.py`

SharePoint permissions analysis and report generator.

#### Functions

##### `build_summaries(df)`

Create summary DataFrames for the report.

**Parameters**:
- `df` (pd.DataFrame): Input DataFrame with SharePoint permissions data

**Returns**: `dict[str, pd.DataFrame]` - Dictionary of summary DataFrames:
  - `by_item_type`: Counts by Item Type
  - `by_permission`: Counts by Permission level
  - `top_users`: Top 25 users by permission occurrences
  - `top_resources`: Top 25 resources by permission count

**Expected Input Columns**:
- `Resource Path`
- `Item Type`
- `Permission`
- `User Name`
- `User Email`
- `User Or Group Type`
- `Link ID`
- `Link Type`
- `AccessViaLinkID`

**Example**:
```python
import pandas as pd
from src.integrations.sharepoint_connector import build_summaries

# Load cleaned CSV
df = pd.read_csv("data/processed/sharepoint_permissions_clean.csv")

# Generate summaries
summaries = build_summaries(df)

# Access specific summaries
print(summaries["by_item_type"])
print(summaries["top_users"].head(10))
```

**Performance Notes**:
- Optimized to avoid unnecessary DataFrame copying
- Efficient string normalization only for columns that exist
- Handles missing columns gracefully

##### `write_excel_report(summaries, output_path)`

Write summary DataFrames to Excel report with formatting.

**Parameters**:
- `summaries` (dict[str, pd.DataFrame]): Dictionary of summary DataFrames from `build_summaries()`
- `output_path` (Path): Path to output Excel file

**Returns**: None (writes file to disk)

**Generated Sheets**:
1. **Overview**: High-level statistics
2. **by_item_type**: Breakdown by item type (File, Folder, Site, etc.)
3. **by_permission**: Breakdown by permission level (Full Control, Contribute, Read, etc.)
4. **top_users**: Top 25 users with most permissions
5. **top_resources**: Top 25 resources with most permission entries

**Excel Formatting**:
- Bold headers with colored backgrounds
- Auto-sized columns for readability
- Numeric formatting for counts

**Example**:
```python
from pathlib import Path
from src.integrations.sharepoint_connector import build_summaries, write_excel_report

# Build and write report
summaries = build_summaries(df)
write_excel_report(summaries, Path("output/reports/business/sharepoint_report.xlsx"))
```

#### Command-Line Usage

**Module Execution**:
```bash
python -m src.integrations.sharepoint_connector \
    --input "data/processed/sharepoint_permissions_clean.csv" \
    --output "output/reports/business/sharepoint_permissions_report.xlsx"
```

**Parameters**:
- `--input`: Path to cleaned CSV file (default: `data/processed/sharepoint_permissions_clean.csv`)
- `--output`: Path to output Excel report (default: `output/reports/business/sharepoint_permissions_report.xlsx`)

**Prerequisites**: Run `scripts/clean_csv.py` first to clean raw SharePoint export.

**Full Workflow**:
```bash
# Step 1: Clean raw CSV
python scripts/clean_csv.py \
    --input "data/raw/sharepoint/export.csv" \
    --output "data/processed/sharepoint_clean.csv"

# Step 2: Generate report
python -m src.integrations.sharepoint_connector \
    --input "data/processed/sharepoint_clean.csv" \
    --output "output/reports/business/sharepoint_permissions.xlsx"
```

---

### src.integrations.openai_gpt5

**Module**: `src/integrations/openai_gpt5.py`

OpenAI GPT-5 integration via Azure OpenAI Service with reasoning capabilities.

#### Classes

##### `GPT5Client`

Client for OpenAI GPT-5 models with Azure OpenAI Service integration.

**Constructor**:
```python
GPT5Client(
    azure_endpoint=None,
    api_key=None,
    use_entra_id=False,
    model="gpt-5"
)
```

**Parameters**:
- `azure_endpoint` (str, optional): Azure OpenAI endpoint (e.g., `https://your-resource.openai.azure.com`)
- `api_key` (str, optional): Azure OpenAI API key (if not using Entra ID)
- `use_entra_id` (bool, optional): Use Azure Entra ID authentication (keyless). Default: False
- `model` (str, optional): Model deployment name. Default: "gpt-5"

**Environment Variables**:
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

**Example**:
```python
from src.integrations.openai_gpt5 import GPT5Client

# Option 1: API key authentication
client = GPT5Client(
    azure_endpoint="https://myresource.openai.azure.com",
    api_key="your-api-key",
    model="gpt-5"
)

# Option 2: Environment variables
import os
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://myresource.openai.azure.com"
os.environ["AZURE_OPENAI_API_KEY"] = "your-api-key"
client = GPT5Client()

# Option 3: Entra ID authentication (recommended for production)
client = GPT5Client(
    azure_endpoint="https://myresource.openai.azure.com",
    use_entra_id=True
)
```

**Methods**:

###### `chat_completion(prompt, system_message=None, max_tokens=5000, temperature=None)`

Send a chat completion request to GPT-5.

**Parameters**:
- `prompt` (str): User prompt/question
- `system_message` (str, optional): Optional system message for context
- `max_tokens` (int, optional): Maximum completion tokens. Default: 5000
- `temperature` (float, optional): Temperature (0.0-2.0). Default: model default

**Returns**: `dict` with response data including:
  - `choices`: List of completion choices
  - `usage`: Token usage statistics
  - `model`: Model used
  - `id`: Response ID

**Example**:
```python
client = GPT5Client()

response = client.chat_completion(
    prompt="Explain the CIS Controls framework for Microsoft 365",
    system_message="You are a cybersecurity expert specializing in CPA firm compliance.",
    max_tokens=1000,
    temperature=0.7
)

# Extract response text
answer = response["choices"][0]["message"]["content"]
print(answer)

# Check token usage
print(f"Tokens used: {response['usage']['total_tokens']}")
```

###### `reasoning_response(prompt, reasoning_effort="medium", reasoning_summary="auto", text_verbosity="medium", tools=None)`

Send a request using the Responses API with reasoning capabilities.

**Parameters**:
- `prompt` (str): Input prompt/question
- `reasoning_effort` (Literal["low", "medium", "high"], optional): Reasoning effort level. Default: "medium"
- `reasoning_summary` (Literal["auto", "detailed"], optional): Reasoning summary detail. Default: "auto"
- `text_verbosity` (Literal["low", "medium", "high"], optional): Text generation verbosity. Default: "medium"
- `tools` (List[dict], optional): Optional list of tools (e.g., MCP servers)

**Returns**: `dict` with response data including:
  - `output`: Generated response
  - `reasoning`: Reasoning trace (if requested)
  - `usage`: Token usage statistics

**Reasoning Effort Levels**:
- `low`: Fast, basic reasoning (1-2 seconds)
- `medium`: Balanced reasoning (5-10 seconds)
- `high`: Deep reasoning (30-60 seconds)

**Example**:
```python
client = GPT5Client(model="gpt-5")

response = client.reasoning_response(
    prompt="Analyze this audit finding and recommend remediation steps: Basic authentication is enabled for Exchange Online mailboxes.",
    reasoning_effort="high",
    reasoning_summary="detailed",
    text_verbosity="high"
)

# View reasoning process
if "reasoning" in response:
    print("Reasoning:", response["reasoning"])

# View final answer
print("Answer:", response["output"]["content"])
```

###### `cpa_tax_analysis(prompt, tax_year=2025)`

Specialized prompt for CPA tax analysis tasks.

**Parameters**:
- `prompt` (str): Tax analysis question
- `tax_year` (int, optional): Tax year for analysis. Default: current year

**Returns**: `dict` - Chat completion response

**Example**:
```python
client = GPT5Client()

response = client.cpa_tax_analysis(
    prompt="Calculate depreciation for office equipment purchased in Q1 2025",
    tax_year=2025
)
```

###### `audit_finding_analysis(finding, severity="medium")`

Analyze audit finding and provide remediation recommendations.

**Parameters**:
- `finding` (str): Description of audit finding
- `severity` (str, optional): Severity level. Default: "medium"

**Returns**: `dict` - Reasoning response with remediation steps

**Example**:
```python
response = client.audit_finding_analysis(
    finding="10 mailboxes have forwarding rules to external domains",
    severity="high"
)

print(response["output"]["content"])
```

**Cost Tracking**:

When `src.core.cost_tracker` is installed, all requests are automatically tracked:

```python
from src.core.cost_tracker import GPT5CostTracker

tracker = GPT5CostTracker(budget_limit=100.0)

# Requests automatically tracked
client = GPT5Client()
response = client.chat_completion(prompt="Test")

# Check costs
print(f"Daily cost: ${tracker.get_daily_total():.2f}")
```

---

## PowerShell Functions

### M365CIS Module

**Module**: `scripts/powershell/modules/M365CIS.psm1`

CIS Controls automation for Microsoft 365 security auditing.

#### Connection Functions

##### `Connect-M365CIS`

Connect to Microsoft 365 services for CIS audit.

**Syntax**:
```powershell
Connect-M365CIS
    [-SkipExchange]
    [-SkipGraph]
    [-SPOAdminUrl <string>]
    [-SkipPurview]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| SkipExchange | Switch | No | Skip Exchange Online connection |
| SkipGraph | Switch | No | Skip Microsoft Graph connection |
| SPOAdminUrl | String | No | SharePoint Admin URL (e.g., `https://tenant-admin.sharepoint.com`) |
| SkipPurview | Switch | No | Skip Purview compliance connection |

**Returns**: None

**Example**:
```powershell
# Connect to all services
Connect-M365CIS -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Connect only to Exchange and Graph
Connect-M365CIS -SkipPurview -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Connect only to Graph (for Azure AD controls)
Connect-M365CIS -SkipExchange -SkipPurview
```

**Prerequisites**:
- ExchangeOnlineManagement module
- Microsoft.Graph modules
- Microsoft.Online.SharePoint.PowerShell module
- Appropriate admin permissions

**Error Handling**: Non-fatal errors are logged but don't stop execution. Check output for warnings.

##### `Connect-PurviewCompliance`

Connect to Microsoft Purview Compliance Center.

**Syntax**:
```powershell
Connect-PurviewCompliance
```

**Returns**: None

**Example**:
```powershell
Connect-PurviewCompliance
Get-RetentionCompliancePolicy  # Test connection
```

---

#### Control Test Functions

All control test functions follow the same pattern and return standardized `[PSCustomObject]` results.

##### `New-CISResult`

Create standardized CIS control result object.

**Syntax**:
```powershell
New-CISResult
    -ControlId <string>
    -Title <string>
    -Severity <string>
    -Expected <string>
    -Actual <string>
    -Status <string>
    -Evidence <string>
    -Reference <string>
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ControlId | String | Yes | CIS control ID (e.g., "1.1.3") |
| Title | String | Yes | Control title/description |
| Severity | String | Yes | Severity level: Critical, High, Medium, Low |
| Expected | String | Yes | Expected configuration value |
| Actual | String | Yes | Actual configuration value |
| Status | String | Yes | Control status: Pass, Fail, Manual |
| Evidence | String | Yes | Supporting evidence/details |
| Reference | String | Yes | CIS benchmark reference URL |

**Returns**: `[PSCustomObject]` with control result

**Example**:
```powershell
$result = New-CISResult `
    -ControlId "1.1.3" `
    -Title "Ensure modern authentication for Exchange Online is enabled" `
    -Severity "High" `
    -Expected "True" `
    -Actual "True" `
    -Status "Pass" `
    -Evidence "OAuth2ClientProfileEnabled: True" `
    -Reference "https://workbench.cisecurity.org/..."

$result | ConvertTo-Json
```

##### `Test-CIS-EXO-BasicAuthDisabled`

Test if basic authentication is disabled for Exchange Online.

**CIS Control**: 1.1.3 - Ensure modern authentication for Exchange Online is enabled

**Syntax**:
```powershell
Test-CIS-EXO-BasicAuthDisabled
```

**Returns**: `[PSCustomObject]` with control result

**Example**:
```powershell
$result = Test-CIS-EXO-BasicAuthDisabled

if ($result.Status -eq "Fail") {
    Write-Host "FAILED: $($result.Title)" -ForegroundColor Red
    Write-Host "  Evidence: $($result.Evidence)"
}
```

##### `Test-CIS-EXO-ExternalForwardingDisabled`

Test if automatic forwarding to external domains is disabled.

**CIS Control**: 1.2.1 - Ensure external forwarding is disabled

**Syntax**:
```powershell
Test-CIS-EXO-ExternalForwardingDisabled
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-EXO-MailboxAuditingEnabled`

Test if mailbox auditing is enabled for all mailboxes.

**CIS Control**: 5.1.1 - Ensure mailbox auditing is enabled

**Syntax**:
```powershell
Test-CIS-EXO-MailboxAuditingEnabled
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-SPO-ExternalSharingPolicy`

Test SharePoint external sharing policy configuration.

**CIS Control**: 6.1.1 - Ensure external sharing is restricted

**Syntax**:
```powershell
Test-CIS-SPO-ExternalSharingPolicy
```

**Returns**: `[PSCustomObject]` with control result

**Example**:
```powershell
$result = Test-CIS-SPO-ExternalSharingPolicy

switch ($result.Status) {
    "Pass" { Write-Host "✅ $($result.Title)" -ForegroundColor Green }
    "Fail" { Write-Host "❌ $($result.Title)" -ForegroundColor Red }
    "Manual" { Write-Host "⚠️ $($result.Title) - Manual review required" -ForegroundColor Yellow }
}
```

##### `Test-CIS-AAD-GlobalAdminCount`

Test that global administrator count is minimized (≤4).

**CIS Control**: 1.1.1 - Ensure administrative accounts are properly secured

**Syntax**:
```powershell
Test-CIS-AAD-GlobalAdminCount
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-Defender-SafeLink`

Test Microsoft Defender Safe Links configuration.

**CIS Control**: 4.2.1 - Ensure Safe Links policy is enabled

**Syntax**:
```powershell
Test-CIS-Defender-SafeLink
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-Defender-SafeAttachment`

Test Microsoft Defender Safe Attachments configuration.

**CIS Control**: 4.2.2 - Ensure Safe Attachments policy is enabled

**Syntax**:
```powershell
Test-CIS-Defender-SafeAttachment
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-CA-MFAEnabled`

Test that Multi-Factor Authentication is enabled via Conditional Access.

**CIS Control**: 1.1.4 - Ensure MFA is enabled for all users

**Syntax**:
```powershell
Test-CIS-CA-MFAEnabled
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-EXO-LegacyProtocolsPerMailbox`

Test legacy protocols (IMAP, POP3) are disabled per mailbox.

**CIS Control**: 1.1.5 - Ensure legacy protocols are disabled

**Syntax**:
```powershell
Test-CIS-EXO-LegacyProtocolsPerMailbox
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-Purview-DLPPoliciesEnabled`

Test that Data Loss Prevention policies are enabled.

**CIS Control**: 3.1.1 - Ensure DLP policies are configured

**Syntax**:
```powershell
Test-CIS-Purview-DLPPoliciesEnabled
```

**Returns**: `[PSCustomObject]` with control result

**Requires**: Purview compliance connection

##### `Test-CIS-AAD-RiskPoliciesEnabled`

Test that Azure AD Identity Protection risk policies are enabled.

**CIS Control**: 1.1.6 - Ensure risk-based policies are enabled

**Syntax**:
```powershell
Test-CIS-AAD-RiskPoliciesEnabled
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-Intune-CompliancePolicy`

Test that Intune device compliance policies are configured.

**CIS Control**: 7.1.1 - Ensure device compliance policies exist

**Syntax**:
```powershell
Test-CIS-Intune-CompliancePolicy
```

**Returns**: `[PSCustomObject]` with control result

**Requires**: Intune license

##### `Test-CIS-AAD-GuestUserRestriction`

Test that guest user permissions are restricted.

**CIS Control**: 1.2.2 - Ensure guest user restrictions are configured

**Syntax**:
```powershell
Test-CIS-AAD-GuestUserRestriction
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-Purview-AuditLogRetention`

Test that audit log retention is configured (≥180 days).

**CIS Control**: 5.1.2 - Ensure audit log retention is sufficient

**Syntax**:
```powershell
Test-CIS-Purview-AuditLogRetention
```

**Returns**: `[PSCustomObject]` with control result

##### `Test-CIS-Purview-SensitivityLabelsPublished`

Test that sensitivity labels are published.

**CIS Control**: 3.1.2 - Ensure sensitivity labels are configured

**Syntax**:
```powershell
Test-CIS-Purview-SensitivityLabelsPublished
```

**Returns**: `[PSCustomObject]` with control result

---

#### Main Audit Function

##### `Invoke-M365CISAudit`

Execute complete CIS Microsoft 365 security audit.

**Syntax**:
```powershell
Invoke-M365CISAudit
    [-OutJson <string>]
    [-Timestamped]
    [-SPOAdminUrl <string>]
    [-SkipPurview]
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| OutJson | String | No | `output/reports/security/m365_cis_audit.json` | Output JSON file path |
| Timestamped | Switch | No | - | Append timestamp to output filename |
| SPOAdminUrl | String | No | - | SharePoint Admin URL |
| SkipPurview | Switch | No | - | Skip Purview compliance controls |

**Returns**: `array` of `[PSCustomObject]` - All control results

**Example**:
```powershell
# Basic audit
$results = Invoke-M365CISAudit

# Timestamped audit with custom output
$results = Invoke-M365CISAudit `
    -OutJson "audits/monthly-audit.json" `
    -Timestamped `
    -SPOAdminUrl "https://contoso-admin.sharepoint.com"

# Audit without Purview (if not licensed)
$results = Invoke-M365CISAudit -SkipPurview

# Filter failed controls
$failures = $results | Where-Object { $_.Status -eq "Fail" }
$failures | Format-Table ControlId, Title, Severity -AutoSize

# Generate compliance score
$total = $results.Count
$passed = ($results | Where-Object { $_.Status -eq "Pass" }).Count
$score = ($passed / $total) * 100
Write-Host "Compliance Score: $score%"
```

**Output Format**:

JSON file with array of control results:
```json
[
  {
    "ControlId": "1.1.3",
    "Title": "Ensure modern authentication for Exchange Online is enabled",
    "Severity": "High",
    "Expected": "True",
    "Actual": "True",
    "Status": "Pass",
    "Evidence": "OAuth2ClientProfileEnabled: True",
    "Reference": "https://workbench.cisecurity.org/...",
    "Timestamp": "2025-12-07T10:30:00Z"
  }
]
```

**Performance**: Full audit typically takes 8-12 minutes for standard M365 tenant.

---

#### Utility Functions

##### `Write-CISLog`

Write log message with timestamp and level.

**Syntax**:
```powershell
Write-CISLog
    [-Message] <string>
    [[-Level] <string>]
```

**Parameters**:
- `Message` (String, Required): Log message
- `Level` (String, Optional): Log level (Info, Warn, Error). Default: Info

**Example**:
```powershell
Write-CISLog "Starting audit execution" "Info"
Write-CISLog "Rate limit hit, retrying..." "Warn"
Write-CISLog "Connection failed" "Error"
```

---

## MCP Tools

### MCP Server Architecture

The toolkit includes two MCP (Model Context Protocol) server implementations:

1. **Simple MCP Server**: `src/extensions/mcp/server.py`
2. **Plugin-Based MCP Server**: `src/mcp/m365_mcp_server.py`

Both servers expose tools for AI agents to interact with the M365 Security Toolkit.

### Available MCP Tools

#### `run_m365_audit`

Execute M365 CIS security audit.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "tenant_id": {
      "type": "string",
      "description": "M365 tenant ID (GUID)"
    },
    "timestamped": {
      "type": "boolean",
      "description": "Append timestamp to output filename",
      "default": true
    },
    "skip_purview": {
      "type": "boolean",
      "description": "Skip Purview compliance controls",
      "default": false
    }
  },
  "required": ["tenant_id"]
}
```

**Output Format**:
```json
{
  "status": "success",
  "audit_file": "output/reports/security/m365_cis_audit_20251207_103000.json",
  "controls_checked": 42,
  "controls_passed": 35,
  "controls_failed": 5,
  "controls_manual": 2,
  "compliance_score": 83.3,
  "execution_time": "8m 34s"
}
```

**Error Codes**:
- `AUTH_001`: Authentication failed
- `CONN_001`: Connection error
- `PERM_001`: Insufficient permissions
- `EXEC_001`: Execution error

#### `generate_security_dashboard`

Generate interactive HTML security dashboard.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "audit_file": {
      "type": "string",
      "description": "Path to audit JSON file"
    },
    "output_path": {
      "type": "string",
      "description": "Path to output HTML file",
      "default": "output/reports/security/dashboard.html"
    }
  },
  "required": ["audit_file"]
}
```

**Output Format**:
```json
{
  "status": "success",
  "dashboard_file": "output/reports/security/dashboard.html",
  "dashboard_url": "file:///path/to/dashboard.html"
}
```

#### `analyze_sharepoint_permissions`

Analyze SharePoint permissions and generate Excel report.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "csv_file": {
      "type": "string",
      "description": "Path to SharePoint permissions CSV export"
    },
    "output_path": {
      "type": "string",
      "description": "Path to output Excel report",
      "default": "output/reports/business/sharepoint_permissions.xlsx"
    }
  },
  "required": ["csv_file"]
}
```

**Output Format**:
```json
{
  "status": "success",
  "report_file": "output/reports/business/sharepoint_permissions.xlsx",
  "total_records": 5234,
  "unique_users": 156,
  "unique_resources": 812
}
```

---

## Type Definitions

### Python TypedDict Definitions

```python
from typing import TypedDict, Literal

class CISControlResult(TypedDict):
    """CIS control test result."""
    ControlId: str
    Title: str
    Severity: Literal["Critical", "High", "Medium", "Low"]
    Expected: str
    Actual: str
    Status: Literal["Pass", "Fail", "Manual"]
    Evidence: str
    Reference: str
    Timestamp: str

class AuditSummary(TypedDict):
    """Audit summary statistics."""
    total_controls: int
    passed: int
    failed: int
    manual: int
    compliance_score: float
    execution_time: str
    timestamp: str

class TokenUsage(TypedDict):
    """GPT-5 token usage."""
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    total_tokens: int

class CostBreakdown(TypedDict):
    """GPT-5 cost breakdown."""
    input_cost: float
    output_cost: float
    cached_cost: float
    total_cost: float
    model: str
```

### PowerShell Type Definitions

```powershell
# CIS Control Result Object
[PSCustomObject]@{
    ControlId  = [string]  # e.g., "1.1.3"
    Title      = [string]  # Control description
    Severity   = [string]  # "Critical", "High", "Medium", "Low"
    Expected   = [string]  # Expected value/configuration
    Actual     = [string]  # Actual value found
    Status     = [string]  # "Pass", "Fail", "Manual"
    Evidence   = [string]  # Supporting evidence
    Reference  = [string]  # CIS benchmark URL
    Timestamp  = [string]  # ISO 8601 timestamp
}

# Token Usage (from Microsoft Graph)
[PSCustomObject]@{
    Value    = [string]  # Access token
    ExpiresOn = [DateTime]  # Token expiration
    Scopes   = [string[]]  # Granted scopes
}
```

---

## Error Handling

### Python Exception Classes

#### `SecurityAuditError`

Base exception for security audit errors.

```python
class SecurityAuditError(Exception):
    """Base exception for security audit operations."""
    pass

class AuthenticationError(SecurityAuditError):
    """Authentication failed."""
    pass

class PermissionError(SecurityAuditError):
    """Insufficient permissions."""
    pass

class RateLimitError(SecurityAuditError):
    """API rate limit exceeded."""
    pass

class ValidationError(SecurityAuditError):
    """Input validation failed."""
    pass
```

**Example**:
```python
try:
    client.run_audit(tenant_id="invalid-guid")
except ValidationError as e:
    print(f"Invalid input: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except PermissionError as e:
    print(f"Insufficient permissions: {e}")
except SecurityAuditError as e:
    print(f"Audit error: {e}")
```

### PowerShell Error Handling

**Standard Pattern**:
```powershell
try {
    # Operation
    $result = Test-CIS-Control
    
    if ($result.Status -eq "Fail") {
        # Handle failure
    }
}
catch [System.Net.WebException] {
    Write-Error "Network error: $($_.Exception.Message)"
    
    # Return Manual status
    return New-CISResult `
        -ControlId "X.Y.Z" `
        -Status "Manual" `
        -Actual "Error: $($_.Exception.Message)"
}
catch {
    Write-Error "Unexpected error: $($_.Exception.Message)"
    
    # Log full exception for debugging
    $_ | Format-List * -Force | Out-File "error.log" -Append
    
    throw  # Re-throw for caller to handle
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| AUTH_001 | Authentication failed | Verify credentials, check token expiration |
| AUTH_002 | MFA required | Configure Conditional Access exclusion |
| PERM_001 | Insufficient permissions | Grant required API permissions |
| PERM_002 | Admin consent required | Admin consent via Azure Portal |
| CONN_001 | Connection timeout | Check network connectivity, increase timeout |
| CONN_002 | Service unavailable | Retry after delay, check Microsoft 365 status |
| RATE_001 | Rate limit exceeded | Implement exponential backoff |
| VAL_001 | Invalid input | Validate input format |
| VAL_002 | File not found | Check file path exists |
| EXEC_001 | Execution error | Check logs for details |

---

## Additional Resources

### Documentation
- [Secure Coding Guide](SECURE_CODING_GUIDE.md) - Security best practices
- [FAQ](FAQ.md) - Common questions and solutions
- [Architecture Documentation](../ARCHITECTURE.md) - System architecture
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Debugging tips

### External References
- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Exchange Online PowerShell](https://docs.microsoft.com/en-us/powershell/exchange/)
- [CIS Microsoft 365 Benchmark](https://www.cisecurity.org/benchmark/microsoft_365)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/)

---

**Last Updated**: December 2025  
**Maintained By**: Rahman Finance and Accounting P.L.LLC  
**Questions?** [Open an issue](https://github.com/Heyson315/Easy-Ai/issues/new?template=custom.md)
