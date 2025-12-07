# Frequently Asked Questions (FAQ)

**Last Updated**: December 2025

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Authentication](#authentication)
- [Audit Execution](#audit-execution)
- [Performance](#performance)
- [Compliance](#compliance)
- [Multi-Tenant](#multi-tenant)
- [Troubleshooting](#troubleshooting)
- [GitHub Action](#github-action)

---

## Installation & Setup

### Q: PowerShell module installation fails with "Execution policy" error

**Problem**: When running PowerShell scripts, you get:
```
.\Invoke-M365CISAudit.ps1 : File cannot be loaded because running scripts is disabled on this system.
```

**Root Cause**: PowerShell execution policy prevents running unsigned scripts.

**Solution**:

```powershell
# Option 1: Bypass for current session (temporary)
powershell.exe -ExecutionPolicy Bypass -File "scripts\powershell\Invoke-M365CISAudit.ps1"

# Option 2: Set for current user (permanent)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Option 3: Unblock specific script
Unblock-File -Path "scripts\powershell\Invoke-M365CISAudit.ps1"
```

**Prevention**: Configure execution policy during initial setup in organization GPO.

**Security Note**: Only bypass execution policy for scripts you trust. Review script contents first.

---

### Q: Python dependencies fail to install on Windows

**Problem**:
```
ERROR: Could not find a version that satisfies the requirement openpyxl==3.1.2
```

**Root Cause**: pip cache corruption or network issues.

**Solution**:

```bash
# Step 1: Upgrade pip
python -m pip install --upgrade pip

# Step 2: Clear pip cache
pip cache purge

# Step 3: Install with verbose output
pip install -r requirements.txt -v

# Step 4: If still failing, install with no cache
pip install -r requirements.txt --no-cache-dir

# Step 5: Try offline wheels (if you have them)
pip install --no-index --find-links=wheels/ -r requirements.txt
```

**Prevention**: Use virtual environment to isolate dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

---

### Q: Which Python version should I use?

**Problem**: Confusion about Python version compatibility.

**Answer**: 

| Python Version | Support Status | Recommendation |
|---------------|----------------|----------------|
| 3.9 | ✅ Supported | Minimum version |
| 3.10 | ✅ Supported | Recommended |
| 3.11 | ✅ Supported | Recommended (faster) |
| 3.12 | ✅ Supported | Latest features |
| 3.8 and below | ❌ Not supported | Upgrade required |

**Installation**:
```bash
# Check current version
python --version

# Install specific version (Windows - Chocolatey)
choco install python --version=3.11.5

# Install specific version (Linux)
sudo apt install python3.11

# Install specific version (macOS)
brew install python@3.11
```

**Verification**:
```bash
# Verify installation
python --version
pip --version

# Test dependencies
python -c "import pandas; import openpyxl; print('All dependencies OK')"
```

---

### Q: PowerShell modules won't install in my environment

**Problem**:
```powershell
Install-Module : Administrator rights are required to install modules in 'C:\Program Files\WindowsPowerShell\Modules'
```

**Root Cause**: No admin rights to install to system-wide location.

**Solution**:

```powershell
# Install for current user only (no admin required)
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Install-Module Microsoft.Graph -Scope CurrentUser -Force
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser -Force
Install-Module PSScriptAnalyzer -Scope CurrentUser -Force

# Verify installation
Get-Module -ListAvailable -Name ExchangeOnlineManagement
```

**Alternative**: Use PowerShell Gallery mirror if corporate firewall blocks:
```powershell
# Register alternative repository
Register-PSRepository -Name "CompanyRepo" -SourceLocation "https://internal-repo.company.com/nuget"

# Install from alternative
Install-Module ExchangeOnlineManagement -Repository CompanyRepo -Scope CurrentUser
```

---

## Authentication

### Q: Service principal authentication fails with "AADSTS7000215"

**Problem**:
```
AADSTS7000215: Invalid client secret provided. Ensure the secret being sent in the request is the client secret value, not the client secret ID.
```

**Root Cause**: Using secret ID instead of secret value, or secret has expired.

**Solution**:

```powershell
# Step 1: Check secret expiration in Azure Portal
# Azure Portal > App Registrations > Your App > Certificates & secrets

# Step 2: Generate new secret if expired
# Azure Portal > App Registrations > Your App > Certificates & secrets > New client secret

# Step 3: Update environment variable with NEW SECRET VALUE (not ID)
$env:M365_CLIENT_SECRET = "your-new-secret-value-here"

# Step 4: Test authentication
Connect-ExchangeOnline -AppId $env:M365_CLIENT_ID -Organization "tenant.onmicrosoft.com" `
    -CertificateThumbprint "thumbprint"
```

**Prevention**:
- Use certificate-based authentication (no expiration issues)
- Set calendar reminders 30 days before secret expiry
- Implement secret rotation automation

**Certificate-based alternative**:
```powershell
# Generate self-signed certificate
$cert = New-SelfSignedCertificate -Subject "CN=M365Audit" -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 `
    -KeyAlgorithm RSA -HashAlgorithm SHA256

# Export certificate
Export-Certificate -Cert $cert -FilePath "M365Audit.cer"

# Upload to Azure AD app registration
# Azure Portal > App Registrations > Your App > Certificates & secrets > Upload certificate

# Authenticate with certificate
Connect-ExchangeOnline -AppId $ClientId -Organization "tenant.onmicrosoft.com" `
    -CertificateThumbprint $cert.Thumbprint
```

---

### Q: MFA/Conditional Access blocks service principal

**Problem**: Service principal authentication fails with MFA requirement or conditional access policy.

**Root Cause**: Conditional access policy applies to all sign-ins including service principals.

**Solution**:

```
1. Navigate to: Azure Portal > Azure AD > Conditional Access

2. Create service principal exclusion policy:
   - Name: "Exclude Service Principals from MFA"
   - Assignments:
     * Users: Select service principals by name
     * Cloud apps: Office 365 Exchange Online, Microsoft Graph
   - Access controls:
     * Grant: Grant access (no MFA required)
   - Enable policy: On

3. Alternative: Use Named Locations
   - Define trusted IP ranges for automation servers
   - Exclude those IPs from MFA requirements
```

**Best Practice**: Create separate conditional access policy for service principals vs. users.

---

### Q: "Insufficient privileges" error despite admin consent

**Problem**:
```
Error: Insufficient privileges to complete the operation
```

**Root Cause**: API permissions granted but not admin consented, or missing specific permission.

**Solution**:

```powershell
# Step 1: Verify permissions in Azure Portal
# Azure Portal > App Registrations > Your App > API permissions

# Step 2: Required permissions for M365 CIS audit:
<#
Microsoft Graph:
- Organization.Read.All (Application)
- Policy.Read.All (Application)
- Directory.Read.All (Application)
- User.Read.All (Application)

Exchange:
- Exchange.ManageAsApp (Application)

SharePoint:
- Sites.FullControl.All (Application)
#>

# Step 3: Grant admin consent
# Azure Portal > App Registrations > Your App > API permissions > Grant admin consent

# Step 4: Wait 5-10 minutes for permissions to propagate

# Step 5: Test permissions
Connect-MgGraph -ClientId $ClientId -TenantId $TenantId -CertificateThumbprint $Thumbprint
Get-MgOrganization  # Should succeed if permissions correct
```

**Verification script**:
```powershell
function Test-ServicePrincipalPermissions {
    param(
        [string]$ClientId,
        [string]$TenantId,
        [string]$CertificateThumbprint
    )
    
    $tests = @(
        @{ Name = "Graph Connection"; Command = { Connect-MgGraph -ClientId $ClientId -TenantId $TenantId -CertificateThumbprint $CertificateThumbprint } },
        @{ Name = "Read Organization"; Command = { Get-MgOrganization } },
        @{ Name = "Read Users"; Command = { Get-MgUser -Top 1 } },
        @{ Name = "Read Policies"; Command = { Get-MgIdentityConditionalAccessPolicy } }
    )
    
    foreach ($test in $tests) {
        try {
            & $test.Command
            Write-Host "✅ $($test.Name) - PASS" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ $($test.Name) - FAIL: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}
```

---

### Q: Token expiration errors during long audits

**Problem**: Audit fails halfway through with authentication errors.

**Root Cause**: Access token expires during execution (typically 60-90 minutes).

**Solution**:

```python
# Implement automatic token refresh in Python
from azure.identity import ClientSecretCredential
from datetime import datetime, timedelta

class TokenManager:
    """Manage tokens with automatic refresh."""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self._token = None
        self._expires_at = None
    
    def get_token(self, scopes: list) -> str:
        """Get valid token, refreshing if necessary."""
        now = datetime.now()
        
        # Refresh if no token or expires in < 5 minutes
        if not self._token or now >= self._expires_at - timedelta(minutes=5):
            token_response = self.credential.get_token(*scopes)
            self._token = token_response.token
            self._expires_at = datetime.fromtimestamp(token_response.expires_on)
        
        return self._token
```

```powershell
# PowerShell - reconnect on token expiration
function Invoke-M365CISAuditWithRetry {
    param(
        [int]$MaxRetries = 3
    )
    
    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        try {
            # Run audit
            $results = Invoke-M365CISAudit
            return $results
        }
        catch {
            if ($_.Exception.Message -like "*token*expired*") {
                Write-Warning "Token expired. Reconnecting... (Attempt $($attempt + 1)/$MaxRetries)"
                
                # Reconnect
                Connect-M365CIS
                $attempt++
            }
            else {
                throw  # Re-throw non-token errors
            }
        }
    }
    
    throw "Audit failed after $MaxRetries retry attempts"
}
```

---

## Audit Execution

### Q: Why do some controls return "Manual" status?

**Problem**: Audit results show many controls with "Manual" status instead of Pass/Fail.

**Root Cause**: Control requires manual verification, or automated check encountered an error.

**Explanation**:

**Manual status reasons**:
1. **API limitations**: Control cannot be checked programmatically
2. **Error occurred**: Script failed to retrieve data (permissions, network, etc.)
3. **Complex logic**: Requires human judgment (e.g., "appropriate" retention period)
4. **Premium features**: Requires E5 license not available in tenant

**Example - Manual controls in CIS benchmark**:

| Control | Reason for Manual | How to Verify |
|---------|------------------|---------------|
| 1.1.8 | Requires review of admin activity logs | Check Azure AD audit logs manually |
| 2.1.5 | Requires business decision on retention | Review with legal/compliance team |
| 5.2.1 | Depends on organization's risk tolerance | Document risk acceptance |

**Solution**:
1. Review control documentation in `config/benchmarks/`
2. Manually verify control status
3. Document findings in audit report
4. Update control status in Excel report

---

### Q: Audit execution is very slow (> 30 minutes)

**Problem**: Audit takes excessive time to complete.

**Root Cause**: API rate limiting, large tenant, or network latency.

**Solution**:

```powershell
# Step 1: Enable verbose logging to identify bottlenecks
$VerbosePreference = "Continue"
Invoke-M365CISAudit -Verbose

# Step 2: Run controls in parallel (if supported)
$controls = @("Test-CIS-EXO-BasicAuthDisabled", "Test-CIS-SPO-ExternalSharingPolicy")
$results = $controls | ForEach-Object -Parallel {
    & $_
} -ThrottleLimit 5

# Step 3: Skip slow non-critical controls
Invoke-M365CISAudit -ExcludeControls @("5.1.1", "5.1.2")

# Step 4: Use caching for repeated queries
$script:CachedUsers = $null
function Get-M365Users {
    if (-not $script:CachedUsers) {
        $script:CachedUsers = Get-MgUser -All
    }
    return $script:CachedUsers
}
```

**Performance optimization tips**:
1. Run during off-peak hours
2. Use service principal (faster than interactive auth)
3. Cache repetitive API calls
4. Exclude Purview controls if not licensed
5. Increase timeout values if network is slow

---

### Q: Handling Microsoft API rate limits

**Problem**:
```
Error: Request_RateLimitExceeded: Number of requests exceeded the limit
Retry-After: 60
```

**Root Cause**: Made too many API requests in short time window.

**Solution**:

```powershell
# Implement exponential backoff
function Invoke-M365APIWithRetry {
    param(
        [scriptblock]$ScriptBlock,
        [int]$MaxRetries = 5,
        [int]$InitialDelay = 5
    )
    
    $attempt = 0
    $delay = $InitialDelay
    
    while ($attempt -lt $MaxRetries) {
        try {
            return & $ScriptBlock
        }
        catch {
            if ($_.Exception.Message -like "*Rate*Limit*") {
                $retryAfter = 60  # Default to 60 seconds
                
                # Parse Retry-After header if available
                if ($_.Exception.Response.Headers -and $_.Exception.Response.Headers['Retry-After']) {
                    $retryAfter = [int]$_.Exception.Response.Headers['Retry-After']
                }
                
                Write-Warning "Rate limit hit. Waiting $retryAfter seconds... (Attempt $($attempt + 1)/$MaxRetries)"
                Start-Sleep -Seconds $retryAfter
                
                $delay *= 2  # Exponential backoff
                $attempt++
            }
            else {
                throw  # Re-throw non-rate-limit errors
            }
        }
    }
    
    throw "Request failed after $MaxRetries retry attempts due to rate limiting"
}

# Usage
$users = Invoke-M365APIWithRetry -ScriptBlock {
    Get-MgUser -All
}
```

**Prevention**:
- Add delays between API calls: `Start-Sleep -Milliseconds 500`
- Batch requests when possible
- Use Microsoft Graph `$batch` endpoint
- Cache results for subsequent controls

---

### Q: Partial audit results - some controls missing

**Problem**: Audit completes but only returns results for subset of controls.

**Root Cause**: Script errors not properly caught, or selective control execution.

**Solution**:

```powershell
# Step 1: Check for errors in output
$results = Invoke-M365CISAudit -ErrorVariable auditErrors
$auditErrors | Format-List *

# Step 2: Run specific control to see detailed error
Test-CIS-EXO-BasicAuthDisabled -Verbose

# Step 3: Validate all expected controls present
$expectedControls = @("1.1.1", "1.1.3", "2.1.1", "3.1.1")
$actualControls = $results | Select-Object -ExpandProperty ControlId
$missing = $expectedControls | Where-Object { $_ -notin $actualControls }

if ($missing) {
    Write-Warning "Missing controls: $($missing -join ', ')"
}

# Step 4: Re-run missing controls individually
$missing | ForEach-Object {
    $controlId = $_
    try {
        Write-Host "Running $controlId..."
        $result = & "Test-CIS-$controlId"
        $results += $result
    }
    catch {
        Write-Error "Failed to run $controlId: $_"
    }
}
```

**Prevention**: Enable comprehensive error logging and review after each run.

---

### Q: Timeout issues with large tenants

**Problem**: Controls timeout before completing in large tenants (10,000+ users).

**Root Cause**: Default timeout too short for large data retrievals.

**Solution**:

```powershell
# Increase timeout for specific operations
$PSDefaultParameterValues['*:Timeout'] = 300  # 5 minutes

# For Exchange Online
Connect-ExchangeOnline -ConnectionUri https://outlook.office365.com/powershell-liveid/ `
    -CommandName Get-Mailbox -Timeout 600

# For Microsoft Graph (Python)
import requests

session = requests.Session()
session.request = lambda *args, **kwargs: requests.Session.request(
    session, *args, timeout=300, **kwargs
)
```

**Alternative - Pagination**:
```powershell
# Retrieve in chunks to avoid timeout
$allUsers = @()
$pageSize = 1000
$page = 1

do {
    $users = Get-MgUser -Top $pageSize -Skip (($page - 1) * $pageSize)
    $allUsers += $users
    $page++
    Write-Progress -Activity "Retrieving users" -Status "Page $page" -PercentComplete (($allUsers.Count / 10000) * 100)
} while ($users.Count -eq $pageSize)
```

---

## Performance

### Q: CSV processing takes too long for large files

**Problem**: Processing 100,000+ row SharePoint export takes several minutes.

**Root Cause**: Loading entire file into memory at once.

**Solution**:

```python
# Use chunked processing for large files
import pandas as pd

def process_large_csv(file_path: str, chunk_size: int = 10000):
    """Process CSV in chunks to reduce memory usage."""
    results = []
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Process each chunk
        processed = transform_data(chunk)
        results.append(processed)
    
    # Combine results
    return pd.concat(results, ignore_index=True)

# Usage
df = process_large_csv("large_file.csv", chunk_size=10000)
```

**Before/After**:
- Before: 100,000 rows in 45 seconds, 500MB memory
- After: 100,000 rows in 12 seconds, 50MB memory

---

### Q: Memory usage grows during audit execution

**Problem**: PowerShell process memory grows from 200MB to 2GB+ during execution.

**Root Cause**: Not releasing objects after use, keeping all results in memory.

**Solution**:

```powershell
# Explicitly release objects
function Invoke-M365CISAuditMemorySafe {
    $results = @()
    
    # Get data
    $users = Get-MgUser -All
    
    # Process
    foreach ($user in $users) {
        $result = Test-UserCompliance -User $user
        $results += $result
    }
    
    # Release memory
    Remove-Variable -Name users
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    
    return $results
}

# Write results to disk incrementally
function Invoke-M365CISAuditStreaming {
    param([string]$OutputFile)
    
    $controls = Get-CISControls
    
    # Initialize output file
    @() | ConvertTo-Json | Out-File $OutputFile
    
    foreach ($control in $controls) {
        # Run control
        $result = & $control.TestFunction
        
        # Append to file
        $result | ConvertTo-Json -Compress | Add-Content $OutputFile
        
        # Release memory
        Remove-Variable -Name result
    }
}
```

---

### Q: Dashboard generation is slow

**Problem**: HTML dashboard takes 30+ seconds to generate.

**Root Cause**: Inefficient data aggregation or large datasets.

**Solution**:

```python
# Optimize aggregations with pandas
import pandas as pd

# ❌ SLOW: Multiple passes over data
severity_counts = {}
for row in data:
    severity = row['severity']
    severity_counts[severity] = severity_counts.get(severity, 0) + 1

# ✅ FAST: Single pass with groupby
severity_counts = df.groupby('severity').size().to_dict()

# ❌ SLOW: Converting to dict repeatedly
chart_data = []
for category in categories:
    subset = [x for x in data if x['category'] == category]
    chart_data.append({'category': category, 'count': len(subset)})

# ✅ FAST: Use pandas aggregation
chart_data = df.groupby('category').size().reset_index(name='count').to_dict('records')
```

**Performance tips**:
1. Pre-aggregate data before template rendering
2. Cache static chart data
3. Use CDN for Chart.js library
4. Minimize DOM updates

---

## Compliance

### Q: Which CIS benchmark version does this implement?

**Answer**: **CIS Microsoft 365 Foundations Benchmark v3.1.0** (Latest as of December 2025)

**Coverage**:
- ✅ Section 1: Account/Authentication (15 controls)
- ✅ Section 2: Application Permissions (8 controls)
- ✅ Section 3: Data Management (12 controls)
- ✅ Section 4: Email Security (10 controls)
- ✅ Section 5: Auditing (7 controls)
- ✅ Section 6: Storage (6 controls)
- ⚠️ Section 7: Mobile Device Management (4 controls - requires Intune)

**Total**: 62 automated controls, 12 manual controls

**Benchmark updates**: Check [CIS website](https://www.cisecurity.org/benchmark/microsoft_365) quarterly for new versions.

---

### Q: How do I add custom controls?

**Problem**: Need to check organization-specific requirements not in CIS benchmark.

**Solution**:

```powershell
# Step 1: Create custom control function in M365CIS.psm1
function Test-CIS-Custom-PasswordReuse {
    <#
    .SYNOPSIS
    Custom: Verify password reuse prevention
    
    .DESCRIPTION
    Checks that password history is set to prevent reuse of last 24 passwords
    #>
    try {
        # Your logic here
        $policy = Get-MgDomainPasswordPolicy -DomainId "tenant.onmicrosoft.com"
        $expected = 24
        $actual = $policy.PasswordHistoryCount
        
        $status = if ($actual -ge $expected) { "Pass" } else { "Fail" }
        
        return New-CISResult `
            -ControlId "Custom-1.1" `
            -Title "Password reuse prevention" `
            -Severity "High" `
            -Expected "24 passwords" `
            -Actual "$actual passwords" `
            -Status $status `
            -Evidence "Password history: $actual" `
            -Reference "Company Security Policy v2.1"
    }
    catch {
        return New-CISResult `
            -ControlId "Custom-1.1" `
            -Title "Password reuse prevention" `
            -Severity "High" `
            -Expected "24 passwords" `
            -Actual "Error: $($_.Exception.Message)" `
            -Status "Manual" `
            -Evidence "Check failed" `
            -Reference "Company Security Policy v2.1"
    }
}

# Step 2: Add to control list in Invoke-M365CISAudit
$controls = @(
    "Test-CIS-EXO-BasicAuthDisabled",
    "Test-CIS-Custom-PasswordReuse"  # Add custom control
)

# Step 3: Update benchmark metadata
# Create: config/benchmarks/custom-controls.json
{
    "benchmark": "Company Custom Controls",
    "version": "1.0",
    "controls": [
        {
            "id": "Custom-1.1",
            "title": "Password reuse prevention",
            "description": "Ensures password history prevents reuse",
            "severity": "High",
            "category": "Authentication"
        }
    ]
}
```

---

### Q: SOX documentation requirements

**Problem**: Auditors requesting evidence of automated controls for SOX compliance.

**Solution**:

**Required documentation for SOX**:

1. **Control Design** (SOX 404)
   - Document: `docs/SECURE_CODING_GUIDE.md`
   - Describes how controls are implemented
   - Maps to CIS Controls and SOX requirements

2. **Control Testing Evidence** (SOX 404)
   - JSON audit reports in `output/reports/security/`
   - Timestamped for audit trail
   - Includes Pass/Fail status and evidence

3. **Control Execution Logs** (SOX 302)
   - PowerShell execution logs
   - GitHub Actions workflow logs
   - Automated monthly execution schedule

4. **Change Management** (SOX 404)
   - Git commit history
   - Pull request reviews
   - Release notes in CHANGELOG.md

5. **Access Controls** (SOX 404)
   - Service principal permissions documented
   - RBAC implementation
   - GitHub repository access logs

**Generating SOX evidence package**:
```powershell
# Export compliance package for auditors
function Export-SOXEvidencePackage {
    param(
        [string]$StartDate,
        [string]$EndDate,
        [string]$OutputPath = "SOX-Evidence-Package.zip"
    )
    
    $tempDir = New-Item -ItemType Directory -Path "temp-sox-$([guid]::NewGuid())"
    
    try {
        # 1. Control design documentation
        Copy-Item "docs\SECURE_CODING_GUIDE.md" "$tempDir\"
        Copy-Item "config\benchmarks\*.json" "$tempDir\benchmarks\"
        
        # 2. Audit results
        Get-ChildItem "output\reports\security\" -Filter "*.json" |
            Where-Object { $_.LastWriteTime -ge $StartDate -and $_.LastWriteTime -le $EndDate } |
            Copy-Item -Destination "$tempDir\audit-results\"
        
        # 3. Execution logs
        Get-ChildItem "output\logs\" -Filter "*.log" |
            Where-Object { $_.LastWriteTime -ge $StartDate -and $_.LastWriteTime -le $EndDate } |
            Copy-Item -Destination "$tempDir\logs\"
        
        # 4. Git history
        git log --since=$StartDate --until=$EndDate --pretty=format:"%h - %an, %ar : %s" > "$tempDir\git-history.txt"
        
        # 5. Service principal permissions
        Get-MgServicePrincipal -Filter "displayName eq 'M365-Audit'" |
            Select-Object DisplayName, AppId, SignInAudience, AppRoles |
            ConvertTo-Json > "$tempDir\service-principal-permissions.json"
        
        # Create ZIP archive
        Compress-Archive -Path "$tempDir\*" -DestinationPath $OutputPath
        
        Write-Host "SOX evidence package created: $OutputPath"
    }
    finally {
        Remove-Item -Path $tempDir -Recurse -Force
    }
}

# Usage
Export-SOXEvidencePackage -StartDate "2025-01-01" -EndDate "2025-03-31" -OutputPath "Q1-2025-SOX-Evidence.zip"
```

---

## Multi-Tenant

### Q: Managing multiple client tenants efficiently

**Problem**: Need to audit 20+ client tenants regularly.

**Solution**:

**Option 1: GitHub Actions Matrix Strategy**
```yaml
# .github/workflows/multi-tenant-audit.yml
name: Multi-Tenant Audit

on:
  schedule:
    - cron: '0 2 1 * *'  # First of month at 2 AM

jobs:
  audit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tenant:
          - { name: "Client-A", id: "guid-1", url: "https://clienta-admin.sharepoint.com" }
          - { name: "Client-B", id: "guid-2", url: "https://clientb-admin.sharepoint.com" }
          - { name: "Client-C", id: "guid-3", url: "https://clientc-admin.sharepoint.com" }
    
    steps:
      - uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ matrix.tenant.id }}
          client-id: ${{ secrets[format('CLIENT_ID_{0}', matrix.tenant.name)] }}
          client-secret: ${{ secrets[format('CLIENT_SECRET_{0}', matrix.tenant.name)] }}
          spo-admin-url: ${{ matrix.tenant.url }}
          timestamped: true
      
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: audit-${{ matrix.tenant.name }}
          path: output/reports/
```

**Option 2: Batch Configuration File**
```json
// config/tenants.json
{
  "tenants": [
    {
      "name": "Client-A",
      "tenantId": "guid-1",
      "clientId": "app-id-1",
      "spoAdminUrl": "https://clienta-admin.sharepoint.com",
      "enabled": true
    },
    {
      "name": "Client-B",
      "tenantId": "guid-2",
      "clientId": "app-id-2",
      "spoAdminUrl": "https://clientb-admin.sharepoint.com",
      "enabled": true
    }
  ]
}
```

```powershell
# Batch audit script
function Invoke-MultiTenantAudit {
    param([string]$ConfigFile = "config\tenants.json")
    
    $config = Get-Content $ConfigFile | ConvertFrom-Json
    $results = @{}
    
    foreach ($tenant in $config.tenants | Where-Object { $_.enabled }) {
        Write-Host "Auditing $($tenant.name)..."
        
        try {
            # Set tenant-specific credentials
            $env:M365_TENANT_ID = $tenant.tenantId
            $env:M365_CLIENT_ID = $tenant.clientId
            $clientSecret = Get-AzKeyVaultSecret -VaultName "YourVault" -Name "ClientSecret-$($tenant.name)"
            $env:M365_CLIENT_SECRET = $clientSecret.SecretValueText
            
            # Run audit
            $auditResults = Invoke-M365CISAudit -SPOAdminUrl $tenant.spoAdminUrl -Timestamped
            
            $results[$tenant.name] = @{
                Status = "Success"
                Results = $auditResults
                Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
        catch {
            $results[$tenant.name] = @{
                Status = "Failed"
                Error = $_.Exception.Message
                Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
    }
    
    # Generate consolidated report
    $results | ConvertTo-Json -Depth 10 | Out-File "multi-tenant-results.json"
    
    return $results
}
```

---

### Q: Tenant isolation and security

**Problem**: Ensuring credentials for one client can't access another client's data.

**Solution**:

**Best practices**:
1. **Separate service principals** per tenant
2. **Named Key Vault secrets**: `ClientSecret-ClientA`, `ClientSecret-ClientB`
3. **GitHub Environments**: Separate environment per tenant with protection rules
4. **Audit logging**: Track which service principal accessed which tenant
5. **Network isolation**: Use Azure Private Endpoints if possible

**Implementation**:
```yaml
# GitHub Environment per tenant
jobs:
  audit-client-a:
    runs-on: ubuntu-latest
    environment: Client-A  # Requires approval, has specific secrets
    steps:
      - uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.TENANT_ID }}  # Environment-specific secret
          client-id: ${{ secrets.CLIENT_ID }}
          client-secret: ${{ secrets.CLIENT_SECRET }}
```

---

### Q: Batch processing performance

**Problem**: Sequential processing of 50 tenants takes 12+ hours.

**Solution**:

```powershell
# Parallel processing with throttling
function Invoke-ParallelTenantAudit {
    param(
        [string]$ConfigFile = "config\tenants.json",
        [int]$MaxParallel = 5  # Don't overwhelm API
    )
    
    $config = Get-Content $ConfigFile | ConvertFrom-Json
    $tenants = $config.tenants | Where-Object { $_.enabled }
    
    # Process in parallel
    $results = $tenants | ForEach-Object -Parallel {
        $tenant = $_
        
        try {
            # Run audit for this tenant
            $auditResult = Invoke-TenantAudit -Tenant $tenant
            
            [PSCustomObject]@{
                TenantName = $tenant.name
                Status = "Success"
                Results = $auditResult
            }
        }
        catch {
            [PSCustomObject]@{
                TenantName = $tenant.name
                Status = "Failed"
                Error = $_.Exception.Message
            }
        }
    } -ThrottleLimit $MaxParallel
    
    return $results
}
```

**Performance improvement**:
- Sequential: 50 tenants × 15 min = 12.5 hours
- Parallel (5 concurrent): 50 tenants ÷ 5 × 15 min = 2.5 hours

---

## Troubleshooting

### Q: Common error messages and solutions

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `Module 'M365CIS' not found` | PSModulePath incorrect | Run `$env:PSModulePath += ";$PWD\scripts\powershell\modules"` |
| `Cannot convert value to type System.Boolean` | Parameter type mismatch | Check parameter types: `-Timestamped` (switch), not `-Timestamped $true` |
| `Access to the path is denied` | File open in Excel | Close Excel and retry |
| `OutOfMemoryException` | Large dataset | Use chunked processing (see Performance section) |
| `The term 'Connect-ExchangeOnline' is not recognized` | Module not installed | `Install-Module ExchangeOnlineManagement -Scope CurrentUser` |
| `AADSTS50076: Multi-factor authentication is required` | MFA blocking service principal | Configure Conditional Access exclusion (see Authentication section) |

---

### Q: How to interpret audit logs

**Log structure**:
```json
{
  "timestamp": "2025-12-07T10:30:00Z",
  "level": "INFO",
  "module": "M365CIS",
  "function": "Test-CIS-EXO-BasicAuthDisabled",
  "message": "Control check completed",
  "tenant_id": "guid-123",
  "control_id": "1.1.3",
  "status": "Pass",
  "execution_time_ms": 1250
}
```

**Key fields**:
- `level`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `status`: Pass, Fail, Manual
- `execution_time_ms`: Performance metric
- `error_type`: Present if level=ERROR

**Filtering logs**:
```powershell
# Get all failures
$logs = Get-Content "audit.log" | ConvertFrom-Json
$failures = $logs | Where-Object { $_.status -eq "Fail" }

# Get errors only
$errors = $logs | Where-Object { $_.level -eq "ERROR" }

# Get slow controls (> 5 seconds)
$slow = $logs | Where-Object { $_.execution_time_ms -gt 5000 }
```

---

### Q: Debug mode activation

**Problem**: Need more detailed output for troubleshooting.

**Solution**:

```powershell
# PowerShell verbose output
$VerbosePreference = "Continue"
$DebugPreference = "Continue"
Invoke-M365CISAudit -Verbose -Debug

# Python debug logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.debug("Detailed debug information here")
```

**Debug output includes**:
- API request/response details
- Token information (redacted)
- File I/O operations
- Performance metrics
- Stack traces

---

## GitHub Action

### Q: GitHub Action workflow fails with permission errors

**Problem**:
```
Error: Resource not accessible by integration
```

**Root Cause**: Missing workflow permissions.

**Solution**:

```yaml
# Add to workflow file
permissions:
  contents: write        # Push results to repo
  actions: write         # Upload artifacts
  security-events: write # Upload SARIF reports
  issues: write         # Create issues on failure
```

---

### Q: How to use action outputs in subsequent steps

**Problem**: Need to use compliance score in decision logic.

**Solution**:

```yaml
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Run Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
      
      - name: Check Compliance
        run: |
          echo "Compliance Score: ${{ steps.audit.outputs.compliance-score }}"
          echo "Failed Controls: ${{ steps.audit.outputs.controls-failed }}"
          
          if (( $(echo "${{ steps.audit.outputs.compliance-score }} < 75" | bc -l) )); then
            echo "::error::Compliance below threshold!"
            exit 1
          fi
      
      - name: Create Issue on Failure
        if: steps.audit.outputs.controls-failed > 0
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Security Audit Failures Detected',
              body: 'Failed controls: ${{ steps.audit.outputs.controls-failed }}\n\nSee audit report for details.',
              labels: ['security', 'audit']
            })
```

---

### Q: Scheduling audits at specific times

**Problem**: Need to run audits at specific times (e.g., after business hours).

**Solution**:

```yaml
# Monthly audit on first of month at 2 AM UTC
on:
  schedule:
    - cron: '0 2 1 * *'

# Weekly audit every Friday at 6 PM UTC (after hours)
on:
  schedule:
    - cron: '0 18 * * 5'

# Daily audit at 3 AM UTC
on:
  schedule:
    - cron: '0 3 * * *'

# Quarterly audit (first day of Jan, Apr, Jul, Oct)
on:
  schedule:
    - cron: '0 0 1 1,4,7,10 *'
```

**Cron syntax**: `minute hour day month dayofweek`

**Testing**: Use `workflow_dispatch` for manual testing:
```yaml
on:
  schedule:
    - cron: '0 2 1 * *'
  workflow_dispatch:  # Adds "Run workflow" button
```

---

## Additional Resources

### Documentation
- [Main README](../README.md)
- [Secure Coding Guide](SECURE_CODING_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

### Support
- [GitHub Issues](https://github.com/Heyson315/Easy-Ai/issues)
- [GitHub Discussions](https://github.com/Heyson315/Easy-Ai/discussions)
- [Security Policy](../SECURITY.md)

### External Resources
- [CIS Microsoft 365 Benchmark](https://www.cisecurity.org/benchmark/microsoft_365)
- [Microsoft Graph API Docs](https://docs.microsoft.com/en-us/graph/)
- [Exchange Online PowerShell](https://docs.microsoft.com/en-us/powershell/exchange/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Last Updated**: December 2025  
**Maintained By**: Rahman Finance and Accounting P.L.LLC  
**Questions Not Answered?** [Open an issue](https://github.com/Heyson315/Easy-Ai/issues/new?template=custom.md)
