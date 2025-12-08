# Architecture Documentation

**M365 Security & SharePoint Analysis Toolkit**  
**Last Updated**: December 2025

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Principles](#architecture-principles)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Integration Points](#integration-points)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Deployment Models](#deployment-models)
- [Future Architecture](#future-architecture)

---

## System Overview

### 30,000-Foot View

The M365 Security & SharePoint Analysis Toolkit is a **hybrid Python/PowerShell enterprise security solution** designed for CPA firms, MSPs, and security teams to automate Microsoft 365 security auditing and compliance reporting.

```
┌─────────────────────────────────────────────────────────────────┐
│                    M365 Security Toolkit                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  PowerShell  │  │    Python    │  │   GitHub Actions    │ │
│  │  Audit Core  │→→│  Processing  │→→│   CI/CD Pipeline    │ │
│  │  (M365 APIs) │  │  & Reporting │  │   (Published Action)│ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│         ↓                 ↓                      ↓              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Optional Extensions Layer                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  MCP Server  │  │   GPT-5 AI   │  │  Graph SDK   │  │   │
│  │  │  (Simple)    │  │  Integration │  │  Enhanced    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │  ┌──────────────┐                                       │   │
│  │  │  MCP Server  │                                       │   │
│  │  │ (Plugin-based)│                                      │   │
│  │  └──────────────┘                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                 ┌─────────────────────────┐
                 │   Microsoft 365 Cloud   │
                 │  - Exchange Online      │
                 │  - Microsoft Graph      │
                 │  - SharePoint Online    │
                 │  - Purview Compliance   │
                 └─────────────────────────┘
```

### Key Components

1. **Core Toolkit** (Required)
   - PowerShell M365CIS module for CIS Controls automation
   - Python processing engine for data transformation
   - Report generation (Excel, HTML dashboards)

2. **GitHub Action** (Optional)
   - Published reusable action (`Heyson315/Easy-Ai@v1`)
   - Zero-setup CI/CD integration
   - Automated compliance monitoring

3. **Extension System** (Optional)
   - Dual MCP server implementations
   - GPT-5 AI integration for analysis
   - Enhanced Microsoft Graph SDK features

---

## Architecture Principles

### 1. Hybrid Python/PowerShell Design

**Rationale**: Leverage strengths of each language for optimal results.

| Component | Language | Reason |
|-----------|----------|--------|
| M365 API Interaction | PowerShell | Native Microsoft modules, excellent admin tooling |
| Data Processing | Python | Superior data manipulation (pandas), faster iteration |
| Report Generation | Python | Rich ecosystem (openpyxl, jinja2) for outputs |
| AI Integration | Python | OpenAI SDK, better async support |

**Example Data Flow**:
```
PowerShell (Audit) → JSON → Python (Process) → Excel/HTML → Storage
```

### 2. Separation of Concerns

**Three-Layer Architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│  (Excel Reports, HTML Dashboards, JSON APIs)            │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   Business Logic Layer                   │
│  (Audit Controls, Data Aggregation, Compliance Scoring) │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Access Layer                      │
│  (Microsoft Graph, Exchange Online, SharePoint APIs)    │
└─────────────────────────────────────────────────────────┘
```

### 3. Optional Extensions Pattern

**Core works standalone**. Extensions add value but aren't required:

```python
# Core functionality always available
from scripts.clean_csv import clean_csv
from src.core.excel_generator import create_report

# Extensions gracefully degrade if not installed
try:
    from src.extensions.mcp import MCPServer
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Continue without MCP features
```

### 4. Security-First Design

**Every component implements**:
- Input validation (path traversal prevention)
- Secure credential management (Key Vault, environment variables)
- Audit logging (structured, PII-redacted)
- Least privilege access (minimal API permissions)
- Encryption at rest and in transit

See [SECURE_CODING_GUIDE.md](docs/SECURE_CODING_GUIDE.md) for details.

### 5. Testability & Maintainability

**Design for testing**:
- Pure functions where possible
- Dependency injection for external services
- Mock-friendly abstractions
- Comprehensive pytest and Pester test suites

---

## Component Architecture

### Core Components

#### 1. PowerShell M365CIS Module

**Location**: `scripts/powershell/modules/M365CIS.psm1`

**Responsibilities**:
- Connect to M365 services (Exchange, Graph, SharePoint, Purview)
- Execute CIS control tests
- Return standardized `[PSCustomObject]` results
- Handle API rate limiting and retries

**Key Functions**:
```powershell
Connect-M365CIS          # Establish connections
Test-CIS-*               # 15+ control test functions
Invoke-M365CISAudit      # Orchestrate full audit
New-CISResult            # Standardize result format
```

**Design Pattern**: Each control is an independent function for parallel execution potential.

#### 2. Python Processing Engine

**Location**: `src/core/`, `src/integrations/`

**Responsibilities**:
- Load and parse PowerShell JSON outputs
- Clean and transform CSV data
- Aggregate and analyze data
- Generate reports (Excel, HTML)

**Key Modules**:
```python
file_io.py           # JSON/CSV I/O with BOM handling
excel_generator.py   # Excel workbook generation
report_utils.py      # Report inspection utilities
profiler.py          # Performance benchmarking
```

**Design Pattern**: Pipeline architecture with pure functions for data transformation.

#### 3. Report Generation System

**Location**: `scripts/m365_cis_report.py`, `scripts/generate_security_dashboard.py`

**Responsibilities**:
- Convert JSON audit results to Excel
- Generate interactive HTML dashboards
- Calculate compliance scores and statistics
- Visualize trends with Chart.js

**Outputs**:
- Excel reports with multiple sheets (summary, controls, evidence)
- HTML dashboards with interactive charts
- CSV exports for data analysis

#### 4. GitHub Action

**Location**: `action.yml`

**Responsibilities**:
- Provide reusable workflow for CI/CD
- Handle multi-tenant batch processing
- Upload artifacts with retention
- Generate SARIF reports for Security tab

**Features** (v1.2.0):
- Risk scoring (severity-weighted 0-100)
- Compliance trending (baseline comparison)
- Automated remediation (WhatIf/Force modes)
- Security tab integration (SARIF uploads)

### Optional Extension Components

#### 5. MCP Servers

**Two Implementations**:

##### Simple MCP Server
**Location**: `src/extensions/mcp/`

**Design**: Monolithic server with all tools in one place.

**Use Case**: Quick setup, small projects, development.

##### Plugin-Based MCP Server
**Location**: `src/mcp/`

**Design**: Extensible plugin architecture.

```
src/mcp/
├── m365_mcp_server.py       # Core server
└── plugins/
    ├── sharepoint_tools/
    │   ├── plugin.json      # Metadata
    │   └── tools.py         # Tool implementations
    └── audit_tools/
        ├── plugin.json
        └── tools.py
```

**Use Case**: Production deployments, custom integrations.

#### 6. GPT-5 Integration

**Location**: `src/integrations/openai_gpt5.py`

**Responsibilities**:
- Azure OpenAI Service integration
- Chat completions API
- Reasoning API with configurable effort
- Specialized prompts for CPA tasks

**Features**:
- Cost tracking integration
- Entra ID authentication
- CPA-specific prompt templates

---

## Data Flow

### End-to-End Audit Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          1. Initiation                                   │
│  User/Schedule → GitHub Action / Local Script → Connect-M365CIS         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     2. Authentication                                    │
│  Service Principal / Certificate → Azure AD → Access Tokens             │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    3. Data Collection (PowerShell)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Exchange    │  │    Graph     │  │  SharePoint  │                  │
│  │   Online     │  │     API      │  │    Online    │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
│         └──────────────────┴──────────────────┘                         │
│                            ↓                                             │
│                   Test-CIS-* Functions                                   │
│                            ↓                                             │
│                  [PSCustomObject] Results                                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     4. Serialization                                     │
│  Invoke-M365CISAudit → ConvertTo-Json → audit.json                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    5. Processing (Python)                                │
│  load_json_with_bom() → DataFrame → Aggregations → Statistics           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     6. Report Generation                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  Excel Report    │  │  HTML Dashboard  │  │  SARIF Report    │     │
│  │  (openpyxl)      │  │  (Jinja2/Chart.js)│ │  (Security Tab) │     │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘     │
└───────────┴──────────────────────┴──────────────────────┴───────────────┘
            ↓                      ↓                      ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      7. Storage & Distribution                           │
│  Local Files / GitHub Artifacts / Azure Blob Storage / Email            │
└─────────────────────────────────────────────────────────────────────────┘
```

### SharePoint Analysis Flow

```
┌───────────────────────────────────────────────────────────────────┐
│  1. Export from SharePoint → Raw CSV (with BOM, comments, etc.)  │
└─────────────────────────────┬─────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│  2. Clean CSV (scripts/clean_csv.py)                             │
│     - Remove BOM                                                  │
│     - Strip comments                                              │
│     - Deduplicate headers                                         │
│     - Validate structure                                          │
└─────────────────────────────┬─────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│  3. Load & Analyze (src/integrations/sharepoint_connector.py)    │
│     - Read with pandas                                            │
│     - Build summaries (by_item_type, by_permission, top_users)   │
│     - Calculate statistics                                        │
└─────────────────────────────┬─────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│  4. Generate Excel Report                                         │
│     - Overview sheet                                              │
│     - Summary sheets                                              │
│     - Raw data sheet                                              │
│     - Formatted & auto-sized                                      │
└───────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **PowerShell** | PowerShell Core | 7.3+ | M365 API interaction, audit execution |
| **Python** | Python | 3.9-3.12 | Data processing, report generation |
| **pandas** | pandas | 2.1+ | Data manipulation and analysis |
| **openpyxl** | openpyxl | 3.1+ | Excel file generation |
| **jinja2** | Jinja2 | 3.1+ | HTML template rendering |
| **pytest** | pytest | 7.4+ | Python testing framework |
| **Pester** | Pester | 5.0+ | PowerShell testing framework |

### Microsoft 365 SDKs

| SDK | Purpose | Authentication |
|-----|---------|---------------|
| **ExchangeOnlineManagement** | Exchange configuration auditing | OAuth 2.0 |
| **Microsoft.Graph** | Azure AD, Policies, Users | OAuth 2.0 / Certificate |
| **Microsoft.Online.SharePoint.PowerShell** | SharePoint settings | OAuth 2.0 |
| **Microsoft Purview** | Compliance policies, DLP | OAuth 2.0 |

### Optional Dependencies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Azure OpenAI** | openai SDK | GPT-5 integration |
| **MCP SDK** | Model Context Protocol | AI assistant integration |
| **msgraph-sdk** | Microsoft Graph (Python) | Enhanced Graph features |
| **cryptography** | cryptography | File encryption utilities |

### CI/CD Tools

| Tool | Purpose |
|------|---------|
| **GitHub Actions** | Automated testing, audits, deployments |
| **Bandit** | Python security scanning |
| **Safety** | Python dependency vulnerability scanning |
| **PSScriptAnalyzer** | PowerShell code quality analysis |
| **CodeQL** | Security vulnerability detection |
| **Dependabot** | Automated dependency updates |

---

## Integration Points

### 1. Microsoft 365 Services

**Exchange Online**:
```powershell
Connect-ExchangeOnline -AppId $ClientId -Organization "tenant.onmicrosoft.com"
Get-OrganizationConfig
Get-TransportConfig
Get-MailboxAuditConfiguration
```

**Microsoft Graph**:
```powershell
Connect-MgGraph -ClientId $ClientId -TenantId $TenantId -CertificateThumbprint $Thumbprint
Get-MgOrganization
Get-MgIdentityConditionalAccessPolicy
Get-MgUser
```

**SharePoint Online**:
```powershell
Connect-SPOService -Url "https://tenant-admin.sharepoint.com"
Get-SPOTenant
Get-SPOSite
```

**Purview Compliance**:
```powershell
Connect-IPPSSession
Get-RetentionCompliancePolicy
Get-DlpCompliancePolicy
```

### 2. GitHub Integration

**GitHub Actions Workflow**:
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID }}
    client-id: ${{ secrets.M365_CLIENT_ID }}
    client-secret: ${{ secrets.M365_CLIENT_SECRET }}
```

**GitHub CLI Integration**:
```bash
gh workflow run m365-audit.yml
gh run view
gh run download
```

**GitHub API**:
- Create issues on audit failures
- Update PR with compliance scores
- Upload SARIF to Security tab

### 3. Azure Services

**Azure Key Vault**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

client = SecretClient(vault_url="https://vault.vault.azure.net", credential=DefaultAzureCredential())
secret = client.get_secret("M365-ClientSecret")
```

**Azure Blob Storage**:
```python
from azure.storage.blob import BlobServiceClient

blob_service = BlobServiceClient.from_connection_string(conn_str)
blob_client = blob_service.get_blob_client(container="audit-reports", blob="audit.json")
blob_client.upload_blob(data)
```

### 4. External Storage

**Local Files**:
```
output/
├── reports/
│   ├── security/       # Audit JSON/Excel/HTML
│   └── business/       # SharePoint analysis
└── logs/               # Execution logs
```

**OneDrive/SharePoint**:
- Direct upload via Graph API
- Automated sync for CPA firms

**Email Integration**:
```python
# Send via Microsoft Graph
from msgraph import GraphServiceClient

client = GraphServiceClient(credentials, scopes)
message = {
    "subject": "M365 Audit Report",
    "body": {"contentType": "HTML", "content": html_body},
    "toRecipients": [{"emailAddress": {"address": "admin@company.com"}}]
}
await client.users["me"].send_mail(message=message).post()
```

---

## Security Architecture

### Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    1. Application Registration                │
│  Azure Portal → App Registrations → Create Service Principal │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                  2. Permission Grant                          │
│  API Permissions → Grant Admin Consent → Save                │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                3. Credential Generation                       │
│  Client Secret OR Certificate → Store in Key Vault/Secrets   │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                    4. Token Acquisition                       │
│  ClientSecretCredential → OAuth Token Request → Azure AD     │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                      5. API Access                            │
│  Access Token → Bearer Authentication → M365 APIs            │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                    6. Token Refresh                           │
│  Token Expiry (60-90 min) → Auto Refresh → Continue          │
└──────────────────────────────────────────────────────────────┘
```

### Authorization Boundaries

**Principle of Least Privilege**:

| Component | Permissions Required |
|-----------|---------------------|
| **Audit Execution** | Organization.Read.All, Policy.Read.All, Directory.Read.All |
| **Report Generation** | File system: Write to output/, Read from config/ |
| **Dashboard Hosting** | Web server: Read-only access to HTML/CSS/JS |
| **MCP Server** | localhost only, no external network access |

**RBAC Implementation**:
```python
class Role(Enum):
    VIEWER = "viewer"      # Read reports
    AUDITOR = "auditor"    # Run audits, read reports
    ADMIN = "admin"        # Full access

@require_role(Role.AUDITOR)
def run_audit():
    # Only AUDITOR and ADMIN can execute
    pass
```

### Data Encryption

**At Rest**:
- Sensitive files encrypted with Fernet (symmetric encryption)
- Key stored in Azure Key Vault
- File permissions: owner read/write only (0600)

**In Transit**:
- All API calls use HTTPS/TLS 1.2+
- Certificate verification enforced
- No plaintext credential transmission

**Encryption Example**:
```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # Store in Key Vault
cipher = Fernet(key)

encrypted = cipher.encrypt(plaintext.encode())
output_path.write_bytes(encrypted)
```

### Audit Trail

**What is Logged**:
- User actions (who ran what, when)
- Authentication events (success/failure)
- Configuration changes
- Control test results (Pass/Fail/Manual)
- API rate limiting events

**What is NOT Logged**:
- Passwords, secrets, tokens
- Full stack traces (sanitized for errors)
- PII (email addresses redacted)

**Log Format (Structured JSON)**:
```json
{
  "timestamp": "2025-12-07T10:30:00Z",
  "level": "INFO",
  "user": "audit-service-principal",
  "action": "audit_executed",
  "tenant_id": "guid-123",
  "controls_checked": 42,
  "compliance_score": 85.7
}
```

---

## Scalability Considerations

### Multi-Tenant Support

**Architectural Patterns**:

1. **Matrix Strategy** (Recommended for CI/CD):
```yaml
strategy:
  matrix:
    tenant: [Client-A, Client-B, Client-C]
    
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ matrix.tenant }}
```

**Benefits**: Parallel execution, isolated failures, per-tenant artifacts.

2. **Batch Configuration**:
```json
{
  "tenants": [
    {"name": "Client-A", "tenantId": "guid-1"},
    {"name": "Client-B", "tenantId": "guid-2"}
  ]
}
```

**Benefits**: Single workflow run, consolidated reporting.

### Large Dataset Handling

**Chunked Processing**:
```python
# Process 100k+ row CSVs in chunks
for chunk in pd.read_csv(file, chunksize=10000):
    process(chunk)
```

**Memory Management**:
- Streaming parsers for large JSON files
- Incremental DataFrame writes
- Explicit garbage collection after heavy operations

**Performance Targets**:
- CSV cleaning: <0.1s per 5k rows
- Audit execution: <15 minutes per tenant
- Report generation: <1 second
- Dashboard rendering: <0.2 seconds

### Parallel Execution

**PowerShell Parallel Jobs**:
```powershell
$controls | ForEach-Object -Parallel {
    & $_
} -ThrottleLimit 5
```

**Python ThreadPoolExecutor**:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(audit_tenant, tenant_ids)
```

**Limitations**:
- API rate limits (throttle to 5 concurrent requests)
- Token refresh conflicts (use separate credentials per thread)

---

## Deployment Models

### 1. Local Development

**Architecture**:
```
Developer Workstation
├── PowerShell 7.3+
├── Python 3.11+
├── VS Code + Extensions
└── Local M365 Credentials
```

**Use Case**: Development, testing, ad-hoc audits.

### 2. GitHub Actions (Recommended)

**Architecture**:
```
GitHub Repository
├── .github/workflows/*.yml
├── Secrets (encrypted credentials)
└── Artifacts (audit reports, 90-365 days)
```

**Use Case**: Automated monthly audits, compliance gates, CI/CD.

### 3. Azure DevOps Pipelines

**Architecture**:
```
Azure DevOps Project
├── Pipelines (YAML)
├── Variable Groups (Azure Key Vault)
└── Artifacts (Azure Blob Storage)
```

**Use Case**: Enterprise integration with existing Azure infrastructure.

### 4. Docker Container

**Architecture**:
```
Docker Image
├── PowerShell Core 7.3
├── Python 3.11
├── All dependencies pre-installed
└── Entry point: Invoke-M365CISAudit
```

**Use Case**: Consistent execution environment, Kubernetes deployments.

**Dockerfile**:
```dockerfile
FROM mcr.microsoft.com/powershell:7.3-ubuntu-22.04

RUN apt-get update && apt-get install -y python3.11 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY scripts/ /app/scripts/
COPY src/ /app/src/

WORKDIR /app
ENTRYPOINT ["pwsh", "-File", "scripts/powershell/Invoke-M365CISAudit.ps1"]
```

### 5. Scheduled Task (Windows)

**Architecture**:
```
Windows Server
├── Task Scheduler (monthly schedule)
├── PowerShell script wrapper
└── Email notification on completion
```

**Use Case**: On-premises deployments, no cloud CI/CD.

---

## Future Architecture

### Planned Improvements

#### 1. Microservices Architecture

**Vision**: Break monolithic toolkit into independent services.

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
└───────────────┬──────────────┬──────────────┬───────────────┘
                ↓              ↓              ↓
┌───────────────────┐  ┌───────────────┐  ┌──────────────────┐
│ Audit Service     │  │ Report Service│  │ Analytics Service│
│ (PowerShell Core) │  │ (Python)      │  │ (GPT-5 + ML)     │
└───────────────────┘  └───────────────┘  └──────────────────┘
```

**Benefits**:
- Independent scaling
- Technology flexibility
- Fault isolation
- Easier testing

#### 2. Real-Time Monitoring

**Vision**: Continuous compliance monitoring instead of periodic audits.

```
M365 Event Stream → Azure Event Hub → Stream Processing → Alert Dashboard
                                       (Azure Functions)
```

**Features**:
- Instant detection of non-compliant changes
- Automated remediation triggers
- Real-time compliance score

#### 3. Machine Learning Integration

**Vision**: AI-powered anomaly detection and predictive analytics.

```
Historical Audit Data → ML Training → Anomaly Detection Model
                                               ↓
                                    Predict compliance drift
                                    Recommend proactive fixes
```

**Use Cases**:
- Predict which controls likely to fail
- Identify unusual permission patterns
- Forecast compliance score trends

#### 4. Multi-Cloud Support

**Vision**: Extend beyond M365 to Google Workspace, AWS, etc.

```
┌─────────────────────────────────────────────────────────┐
│              Unified Security Toolkit                    │
├─────────────────┬──────────────┬──────────────┬─────────┤
│    M365         │   Google     │     AWS      │  Azure  │
│  (Current)      │  Workspace   │   Security   │  (Infra)│
└─────────────────┴──────────────┴──────────────┴─────────┘
```

#### 5. Advanced Remediation

**Vision**: Safe automated remediation with rollback capabilities.

```
┌───────────────────────────────────────────────────────┐
│  1. Detect Non-Compliance → Generate Remediation Plan │
│  2. Simulate Changes (WhatIf Mode)                    │
│  3. Get Approval (Manual/Auto)                        │
│  4. Apply Changes → Snapshot Before/After             │
│  5. Verify Compliance → Rollback if Failed            │
└───────────────────────────────────────────────────────┘
```

### Technical Debt

**Current Known Issues**:

1. **PowerShell Module Path Handling**: OneDrive sync path hardcoded in Connect-M365CIS
   - **Resolution**: Make configurable via environment variable

2. **Rate Limiting**: Not all API calls have exponential backoff
   - **Resolution**: Implement `Invoke-M365APIWithRetry` wrapper

3. **Test Coverage**: ~70% coverage, need 90%+
   - **Resolution**: Add integration tests for all controls

4. **Documentation**: Some PowerShell functions lack XML help comments
   - **Resolution**: Add comment-based help to all functions

### Extensibility Points

**Plugin System**:
```python
# Future: Dynamic control loading
class ControlPlugin:
    def __init__(self, control_id, test_function):
        self.control_id = control_id
        self.test_function = test_function
    
    def execute(self):
        return self.test_function()

# Load custom controls from plugins/
for plugin_file in Path("plugins/").glob("*.py"):
    plugin = load_plugin(plugin_file)
    register_control(plugin)
```

**Custom Integrations**:
- Webhooks for external systems
- Custom report formats (PDF, DOCX)
- SIEM integration (Splunk, Sentinel)

---

## Related Documentation

### Internal Resources
- [Secure Coding Guide](docs/SECURE_CODING_GUIDE.md) - Security best practices
- [FAQ](docs/FAQ.md) - Common questions and troubleshooting
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines
- [Copilot Instructions](.github/copilot-instructions.md) - AI development patterns

### External Standards
- [CIS Microsoft 365 Benchmark](https://www.cisecurity.org/benchmark/microsoft_365)
- [Microsoft 365 Architecture Center](https://docs.microsoft.com/en-us/microsoft-365/solutions/)
- [Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)

---

**Last Updated**: December 2025  
**Maintained By**: Rahman Finance and Accounting P.L.LLC  
**Architecture Review Cycle**: Quarterly  
**Next Review**: March 2026
