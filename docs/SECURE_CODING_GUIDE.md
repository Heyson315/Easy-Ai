# Secure Coding Guide for M365 Security Toolkit

**Target Audience**: CPA firms, audit professionals, and finance automation developers  
**Compliance Focus**: SOX, AICPA standards, and CIS Controls  
**Last Updated**: December 2025

## Table of Contents

1. [Overview](#overview)
2. [SOX & AICPA Compliance Mapping](#sox--aicpa-compliance-mapping)
3. [Credential Management](#credential-management)
4. [Input Validation](#input-validation)
5. [Authentication & Authorization](#authentication--authorization)
6. [Audit Logging](#audit-logging)
7. [Error Handling](#error-handling)
8. [API Security](#api-security)
9. [Data Protection](#data-protection)
10. [Security Checklist](#security-checklist)
11. [Tools Integration](#tools-integration)

---

## Overview

### Why Secure Coding Matters in CPA Environments

CPA firms handle highly sensitive financial data and are subject to strict regulatory requirements. Secure coding practices are essential for:

- **Client Confidentiality**: Protecting sensitive financial records (SOX 404, AICPA Trust Services)
- **Data Integrity**: Ensuring audit trails are tamper-proof (SOX 302)
- **Regulatory Compliance**: Meeting AICPA, PCAOB, and state board requirements
- **Professional Liability**: Reducing malpractice risk from data breaches
- **Reputation Management**: Maintaining client trust and professional standing

**Key Principle**: Security is not optional—it's a professional responsibility.

---

## SOX & AICPA Compliance Mapping

### SOX (Sarbanes-Oxley) Requirements

| SOX Section | Requirement | Implementation in Toolkit |
|------------|-------------|---------------------------|
| **302** | Management certification of controls | Audit logging, immutable reports |
| **404** | Internal control assessment | CIS Controls automation, compliance scoring |
| **409** | Real-time disclosure | Dashboard generation, automated alerts |
| **802** | Record retention | Timestamped outputs, artifact retention |
| **906** | Criminal penalties for fraud | Authentication, authorization, audit trails |

### AICPA Trust Services Criteria

| Criterion | Description | Toolkit Implementation |
|-----------|-------------|------------------------|
| **CC6.1** | Logical and physical access controls | Service principal authentication, RBAC |
| **CC6.2** | System operations | Automated audit execution, error handling |
| **CC6.6** | Vulnerability management | Security scanning (Bandit, Safety), dependency updates |
| **CC6.7** | Security incidents | Structured logging, error tracking |
| **CC7.2** | Confidentiality protection | Encrypted secrets, secure credential storage |

### CIS Controls Implementation

This toolkit implements **CIS Controls v8** for Microsoft 365:

- **Control 1**: Inventory management (automated tenant enumeration)
- **Control 5**: Account management (admin count monitoring)
- **Control 6**: Access control (MFA enforcement checks)
- **Control 8**: Audit log management (retention validation)
- **Control 16**: Application software security (Defender policies)

---

## Credential Management

### ✅ CORRECT: Environment Variables

**Pattern**: Use environment variables for sensitive credentials.

```python
# Python - CORRECT
import os
from azure.identity import ClientSecretCredential

# Load from environment
tenant_id = os.environ.get("M365_TENANT_ID")
client_id = os.environ.get("M365_CLIENT_ID")
client_secret = os.environ.get("M365_CLIENT_SECRET")

if not all([tenant_id, client_id, client_secret]):
    raise ValueError("Missing required M365 credentials in environment variables")

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)
```

```powershell
# PowerShell - CORRECT
function Connect-M365CIS {
    param(
        [Parameter(Mandatory=$false)]
        [string]$TenantId = $env:M365_TENANT_ID,
        
        [Parameter(Mandatory=$false)]
        [string]$ClientId = $env:M365_CLIENT_ID,
        
        [Parameter(Mandatory=$false)]
        [SecureString]$ClientSecret
    )
    
    if (-not $TenantId) {
        throw "Tenant ID not provided. Set M365_TENANT_ID environment variable."
    }
    
    # Use SecureString for sensitive data
    if (-not $ClientSecret) {
        $secureSecret = ConvertTo-SecureString $env:M365_CLIENT_SECRET -AsPlainText -Force
    }
    
    $credential = New-Object System.Management.Automation.PSCredential($ClientId, $ClientSecret)
}
```

### ✅ CORRECT: Azure Key Vault Integration

**Pattern**: Store secrets in Azure Key Vault, retrieve at runtime.

```python
# Python - Azure Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_m365_credentials(vault_url: str) -> dict:
    """
    Retrieve M365 credentials from Azure Key Vault.
    
    Args:
        vault_url: Azure Key Vault URL (e.g., "https://mykeyvault.vault.azure.net")
    
    Returns:
        Dictionary with tenant_id, client_id, client_secret
    """
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    return {
        "tenant_id": client.get_secret("M365-TenantId").value,
        "client_id": client.get_secret("M365-ClientId").value,
        "client_secret": client.get_secret("M365-ClientSecret").value
    }
```

### ✅ CORRECT: GitHub Encrypted Secrets

**Pattern**: Use GitHub repository secrets for CI/CD workflows.

```yaml
# .github/workflows/audit.yml
jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Run M365 Audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
```

### ❌ NEVER: Hardcoded Secrets

**Anti-Pattern**: DO NOT hardcode credentials in code.

```python
# ❌ WRONG - NEVER DO THIS
tenant_id = "12345678-1234-1234-1234-123456789012"
client_secret = "my-super-secret-password"  # EXPOSED IN VERSION CONTROL
```

```powershell
# ❌ WRONG - NEVER DO THIS
$TenantId = "12345678-1234-1234-1234-123456789012"
$ClientSecret = "my-super-secret-password"  # EXPOSED IN LOGS
```

**Why**: Credentials in code are visible in:
- Git history (forever, even if deleted)
- CI/CD logs
- Error messages
- Memory dumps
- Shared repositories

---

## Input Validation

### Path Traversal Prevention

**Risk**: Attackers can access files outside intended directories using `../` sequences.

```python
# ✅ CORRECT: Validate and resolve paths
from pathlib import Path
import os

def safe_file_access(user_input: str, base_dir: Path) -> Path:
    """
    Safely resolve file path within allowed directory.
    
    Args:
        user_input: User-provided file path
        base_dir: Allowed base directory
    
    Returns:
        Resolved safe path
    
    Raises:
        ValueError: If path is outside base_dir
    """
    # Resolve absolute path
    base_dir = base_dir.resolve()
    target_path = (base_dir / user_input).resolve()
    
    # Ensure target is within base_dir
    if not target_path.is_relative_to(base_dir):
        raise ValueError(f"Access denied: {user_input} is outside allowed directory")
    
    return target_path

# Usage
base = Path("output/reports")
try:
    safe_path = safe_file_access(user_input="../../etc/passwd", base_dir=base)
except ValueError as e:
    print(f"Security error: {e}")  # Logs attempt
```

```powershell
# ✅ CORRECT: PowerShell path validation
function Get-SafeFilePath {
    param(
        [Parameter(Mandatory=$true)]
        [string]$UserInput,
        
        [Parameter(Mandatory=$true)]
        [string]$BaseDirectory
    )
    
    $basePath = Resolve-Path $BaseDirectory
    
    # Disallow absolute user input paths
    if ([System.IO.Path]::IsPathRooted($UserInput)) {
        throw "Access denied: Absolute paths are not allowed"
    }
    
    $targetPath = Join-Path $basePath $UserInput
    $resolvedTarget = Resolve-Path $targetPath -ErrorAction SilentlyContinue
    
    # Ensure the resolved target is within the base directory (not just prefix match)
    $basePathStr = $basePath.Path.TrimEnd('\')
    $resolvedTargetStr = $resolvedTarget.Path
    $basePathWithSep = $basePathStr + '\'
    if (
        -not $resolvedTarget -or (
            ($resolvedTargetStr -ne $basePathStr) -and
            (-not $resolvedTargetStr.StartsWith($basePathWithSep))
        )
    ) {
        throw "Access denied: Path is outside allowed directory"
    }
    
    return $resolvedTarget
}
```

### Email/User Input Sanitization

**Risk**: Malicious input can cause injection attacks or data corruption.

```python
# ✅ CORRECT: Validate email addresses
import re
from typing import Optional

def validate_email(email: str) -> Optional[str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Sanitized email or None if invalid
    """
    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    email = email.strip().lower()
    
    if not re.match(pattern, email):
        return None
    
    # Additional checks
    if len(email) > 254:  # RFC 5321
        return None
    
    return email

# ✅ CORRECT: Sanitize tenant/domain names
def validate_tenant_name(tenant: str) -> str:
    """
    Validate and sanitize M365 tenant name.
    
    Args:
        tenant: Tenant name or domain
    
    Returns:
        Sanitized tenant name
    
    Raises:
        ValueError: If tenant name is invalid
    """
    # Allow only alphanumeric, hyphens, periods
    pattern = r'^[a-zA-Z0-9.-]+$'
    
    if not re.match(pattern, tenant):
        raise ValueError(f"Invalid tenant name: {tenant}")
    
    if len(tenant) > 255:
        raise ValueError("Tenant name too long")
    
    return tenant.lower()
```

### File Upload Validation

```python
# ✅ CORRECT: Validate file uploads
import mimetypes
from pathlib import Path

ALLOWED_EXTENSIONS = {'.csv', '.json', '.xlsx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def validate_upload(file_path: Path) -> bool:
    """
    Validate uploaded file is safe to process.
    
    Args:
        file_path: Path to uploaded file
    
    Returns:
        True if file is valid
    
    Raises:
        ValueError: If file is invalid
    """
    # Check extension
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {file_path.suffix} not allowed")
    
    # Check size
    if file_path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE} bytes")
    
    # Verify MIME type matches extension
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and not mime_type.startswith(('text/', 'application/')):
        raise ValueError(f"MIME type {mime_type} not allowed")
    
    return True
```

### XSS Prevention in Web Templates

**Risk**: Cross-site scripting attacks through untrusted data in HTML output.

```python
# ✅ CORRECT: Escape HTML output
import html
from markupsafe import escape

def safe_html_output(user_data: str) -> str:
    """
    Safely escape user data for HTML output.
    
    Args:
        user_data: Untrusted user input
    
    Returns:
        HTML-escaped string
    """
    return html.escape(user_data, quote=True)

# ✅ CORRECT: Use template engine with auto-escaping
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('web-templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('dashboard.html')
output = template.render(
    tenant_name=user_input,  # Automatically escaped
    compliance_score=score
)
```

---

## Authentication & Authorization

### Service Principal Best Practices

**Pattern**: Use Azure AD service principals for unattended automation.

```python
# ✅ CORRECT: Service principal authentication
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

def create_graph_client(tenant_id: str, client_id: str, client_secret: str) -> GraphServiceClient:
    """
    Create Microsoft Graph client with service principal.
    
    Args:
        tenant_id: Azure AD tenant ID
        client_id: Application (client) ID
        client_secret: Client secret value
    
    Returns:
        Authenticated Graph client
    """
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    scopes = ["https://graph.microsoft.com/.default"]
    client = GraphServiceClient(credentials=credential, scopes=scopes)
    
    return client
```

### Least Privilege Access

**Principle**: Grant only the minimum permissions required.

**Required API Permissions** (for M365 CIS audit):

| API | Permission | Type | Justification |
|-----|-----------|------|---------------|
| Microsoft Graph | `Organization.Read.All` | Application | Read tenant configuration |
| Microsoft Graph | `Policy.Read.All` | Application | Read conditional access policies |
| Microsoft Graph | `Directory.Read.All` | Application | Read user and group information |
| Exchange Online | `Exchange.ManageAsApp` | Application | Read Exchange configuration |
| SharePoint | `Sites.FullControl.All` | Application | Read SharePoint settings |

**Documentation**: See [`docs/M365_SERVICE_PRINCIPAL_SETUP.md`](M365_SERVICE_PRINCIPAL_SETUP.md) for detailed setup.

```powershell
# ✅ CORRECT: Request only required permissions
$permissions = @(
    "Organization.Read.All",
    "Policy.Read.All",
    "Directory.Read.All"
)

# Create app registration with minimal permissions
New-AzADApplication -DisplayName "M365-Audit-ReadOnly" `
    -RequiredResourceAccess $permissions
```

### RBAC Implementation

**Pattern**: Implement role-based access control for multi-user scenarios.

```python
# ✅ CORRECT: Role-based authorization
from enum import Enum
from typing import Set

class Role(Enum):
    VIEWER = "viewer"          # Read audit reports
    AUDITOR = "auditor"        # Run audits, read reports
    ADMIN = "admin"            # Full access including remediation

class User:
    def __init__(self, username: str, roles: Set[Role]):
        self.username = username
        self.roles = roles
    
    def has_permission(self, required_role: Role) -> bool:
        """Check if user has required role."""
        role_hierarchy = {
            Role.ADMIN: {Role.ADMIN, Role.AUDITOR, Role.VIEWER},
            Role.AUDITOR: {Role.AUDITOR, Role.VIEWER},
            Role.VIEWER: {Role.VIEWER}
        }
        
        for user_role in self.roles:
            if required_role in role_hierarchy.get(user_role, set()):
                return True
        return False

def require_role(role: Role):
    """Decorator to enforce role-based access."""
    def decorator(func):
        def wrapper(user: User, *args, **kwargs):
            if not user.has_permission(role):
                raise PermissionError(f"User {user.username} lacks required role: {role.value}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@require_role(Role.AUDITOR)
def run_security_audit(user: User, tenant_id: str):
    """Run security audit - requires AUDITOR role."""
    print(f"Running audit for tenant {tenant_id}")
```

### Token Management

**Pattern**: Handle access tokens securely and refresh before expiry.

```python
# ✅ CORRECT: Token caching and refresh
from azure.identity import ClientSecretCredential
from datetime import datetime, timedelta

class TokenManager:
    """Manage OAuth tokens with automatic refresh."""
    
    def __init__(self, credential: ClientSecretCredential):
        self.credential = credential
        self._token = None
        self._expires_at = None
    
    def get_token(self, scopes: list[str]) -> str:
        """
        Get valid access token, refreshing if necessary.
        
        Args:
            scopes: Required OAuth scopes
        
        Returns:
            Valid access token
        """
        # Refresh if token expired or expires in < 5 minutes
        if not self._token or datetime.now() >= self._expires_at - timedelta(minutes=5):
            token_response = self.credential.get_token(*scopes)
            self._token = token_response.token
            self._expires_at = datetime.fromtimestamp(token_response.expires_on)
        
        return self._token
```

---

## Audit Logging

### What to Log (and What NOT to Log)

**✅ DO Log**:
- User actions (audit executed, report generated)
- Authentication attempts (success/failure)
- Permission changes
- Configuration modifications
- Error conditions
- Performance metrics

**❌ DO NOT Log**:
- Passwords or secrets
- Access tokens
- PII without business justification
- Full stack traces to user-facing logs

### Structured Logging Pattern

```python
# ✅ CORRECT: Structured logging
import logging
import json
from datetime import datetime
from typing import Optional

# Configure structured JSON logging
class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add custom fields if present
        if hasattr(record, "user"):
            log_data["user"] = record.user
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
        
        return json.dumps(log_data)

# Setup logger
logger = logging.getLogger("m365_audit")
handler = logging.FileHandler("output/logs/audit.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
def run_audit(user: str, tenant_id: str):
    """Run audit with structured logging."""
    logger.info(
        "Audit started",
        extra={"user": user, "tenant_id": tenant_id, "action": "audit_start"}
    )
    
    try:
        # Perform audit
        results = perform_audit(tenant_id)
        
        logger.info(
            f"Audit completed: {len(results)} controls checked",
            extra={
                "user": user,
                "tenant_id": tenant_id,
                "action": "audit_complete",
                "control_count": len(results)
            }
        )
    except Exception as e:
        # Log error without sensitive details
        logger.error(
            f"Audit failed: {type(e).__name__}",
            extra={
                "user": user,
                "tenant_id": tenant_id,
                "action": "audit_failed",
                "error_type": type(e).__name__
            }
        )
        raise
```

### PII Redaction

```python
# ✅ CORRECT: Redact PII in logs
import re

def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information from log messages.
    
    Args:
        text: Log message that may contain PII
    
    Returns:
        Redacted log message
    """
    # Redact email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Redact phone numbers (US format)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Redact SSN (US format)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Redact credit card numbers
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD]', text)
    
    return text

# Usage
sensitive_message = "User john.doe@company.com called 555-123-4567"
logger.info(redact_pii(sensitive_message))
# Logs: "User [EMAIL] called [PHONE]"
```

### Log Retention Requirements

**Compliance Standards**:

| Standard | Retention Period | Implementation |
|----------|------------------|----------------|
| **SOX** | 7 years | Archive to Azure Blob Storage with immutability |
| **AICPA** | 5-7 years | Timestamped exports, encrypted storage |
| **CIS** | 90 days minimum | GitHub Actions artifacts (90-365 days) |

```yaml
# ✅ CORRECT: Artifact retention in GitHub Actions
- name: Upload Audit Logs
  uses: actions/upload-artifact@v4
  with:
    name: audit-logs-${{ github.run_id }}
    path: output/logs/
    retention-days: 365  # 1 year retention for compliance
```

---

## Error Handling

### Never Expose Stack Traces to Users

```python
# ✅ CORRECT: User-friendly error messages
import logging
import traceback

logger = logging.getLogger(__name__)

def audit_tenant(tenant_id: str) -> dict:
    """
    Run security audit for tenant.
    
    Args:
        tenant_id: M365 tenant ID
    
    Returns:
        Audit results dictionary
    """
    try:
        # Perform audit operations
        results = perform_audit(tenant_id)
        return results
    
    except ConnectionError as e:
        # Log full details for debugging
        logger.error(f"Connection failed for tenant {tenant_id}", exc_info=True)
        
        # Return user-friendly message
        return {
            "status": "error",
            "message": "Unable to connect to Microsoft 365. Please check network connectivity.",
            "error_code": "CONN_001"
        }
    
    except PermissionError as e:
        logger.error(f"Permission denied for tenant {tenant_id}", exc_info=True)
        
        return {
            "status": "error",
            "message": "Insufficient permissions. Verify service principal has required API permissions.",
            "error_code": "PERM_001"
        }
    
    except Exception as e:
        # Catch-all for unexpected errors
        logger.critical(f"Unexpected error in audit: {type(e).__name__}", exc_info=True)
        
        return {
            "status": "error",
            "message": "An unexpected error occurred. Contact support with error code.",
            "error_code": "GEN_001"
        }
```

### Structured Error Responses

```python
# ✅ CORRECT: Consistent error structure
from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorResponse:
    """Standardized error response."""
    error_code: str
    message: str
    details: Optional[str] = None
    remediation: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "remediation": self.remediation
            }
        }

# Usage
error = ErrorResponse(
    error_code="AUTH_001",
    message="Authentication failed",
    details="Token has expired",
    remediation="Refresh authentication tokens and retry"
)
```

### Logging Errors Without Sensitive Data

```python
# ✅ CORRECT: Safe error logging
def safe_log_exception(e: Exception, context: dict):
    """
    Log exception with context, excluding sensitive data.
    
    Args:
        e: Exception to log
        context: Contextual information (will be sanitized)
    """
    # Redact sensitive keys
    sensitive_keys = {"password", "secret", "token", "key", "credential"}
    
    safe_context = {
        k: "[REDACTED]" if k.lower() in sensitive_keys else v
        for k, v in context.items()
    }
    
    logger.error(
        f"Error: {type(e).__name__}",
        extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "context": safe_context
        }
    )
```

---

## API Security

### TLS Certificate Verification

```python
# ✅ CORRECT: Always verify TLS certificates
import requests

def call_api(url: str, token: str) -> dict:
    """
    Make authenticated API call with TLS verification.
    
    Args:
        url: API endpoint URL
        token: Access token
    
    Returns:
        API response as dictionary
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Verify TLS certificate (default behavior, but explicit is better)
    response = requests.get(url, headers=headers, verify=True, timeout=30)
    response.raise_for_status()
    
    return response.json()

# ❌ WRONG: Never disable certificate verification
# response = requests.get(url, verify=False)  # SECURITY VULNERABILITY
```

### Request Timeout Enforcement

```python
# ✅ CORRECT: Always set timeouts
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries() -> requests.Session:
    """
    Create requests session with timeout and retry logic.
    
    Returns:
        Configured requests session
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    
    # Set default timeout
    session.request = lambda *args, **kwargs: requests.Session.request(
        session, *args, timeout=kwargs.get('timeout', 30), **kwargs
    )
    
    return session
```

### Rate Limiting Considerations

```python
# ✅ CORRECT: Implement rate limiting and backoff
import time
from typing import Callable, Any

def retry_with_exponential_backoff(
    func: Callable,
    max_retries: int = 5,
    initial_delay: float = 1.0
) -> Any:
    """
    Retry function with exponential backoff for rate limits.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
    
    Returns:
        Function return value
    
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                retry_after = int(e.response.headers.get('Retry-After', delay))
                logger.warning(f"Rate limited. Retrying after {retry_after}s")
                time.sleep(retry_after)
                delay *= 2  # Exponential backoff
            else:
                raise
    
    # Final attempt
    return func()
```

### Response Validation

```python
# ✅ CORRECT: Validate API responses
from typing import TypedDict, List

class AuditControlResponse(TypedDict):
    """Expected API response structure."""
    control_id: str
    status: str
    severity: str
    evidence: str

def validate_response(response_data: dict) -> List[AuditControlResponse]:
    """
    Validate API response structure and types.
    
    Args:
        response_data: Raw API response
    
    Returns:
        List of validated audit controls
    
    Raises:
        ValueError: If response structure is invalid
    """
    if not isinstance(response_data, dict):
        raise ValueError("Response must be a dictionary")
    
    if "controls" not in response_data:
        raise ValueError("Response missing 'controls' field")
    
    controls = response_data["controls"]
    if not isinstance(controls, list):
        raise ValueError("Controls must be a list")
    
    validated_controls = []
    for control in controls:
        # Validate required fields
        required_fields = {"control_id", "status", "severity"}
        if not required_fields.issubset(control.keys()):
            raise ValueError(f"Control missing required fields: {required_fields - set(control.keys())}")
        
        # Validate field types
        if not isinstance(control["control_id"], str):
            raise ValueError("control_id must be a string")
        
        validated_controls.append(control)
    
    return validated_controls
```

---

## Data Protection

### Encryption at Rest

**Pattern**: Encrypt sensitive data before storing.

```python
# ✅ CORRECT: Encrypt sensitive files
from cryptography.fernet import Fernet
from pathlib import Path

class FileEncryptor:
    """Encrypt/decrypt files using Fernet symmetric encryption."""
    
    def __init__(self, key: bytes):
        """
        Initialize encryptor with key.
        
        Args:
            key: 32-byte encryption key (use Fernet.generate_key())
        """
        self.cipher = Fernet(key)
    
    def encrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Encrypt file contents.
        
        Args:
            input_path: Path to plaintext file
            output_path: Path to encrypted output file
        """
        plaintext = input_path.read_bytes()
        encrypted = self.cipher.encrypt(plaintext)
        output_path.write_bytes(encrypted)
    
    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Decrypt file contents.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to decrypted output file
        """
        encrypted = input_path.read_bytes()
        plaintext = self.cipher.decrypt(encrypted)
        output_path.write_bytes(plaintext)

# Usage
key = Fernet.generate_key()  # Store securely (Key Vault)
encryptor = FileEncryptor(key)

encryptor.encrypt_file(
    Path("sensitive_data.csv"),
    Path("sensitive_data.csv.encrypted")
)
```

### Encryption in Transit

**Pattern**: Use HTTPS/TLS for all network communication.

```python
# ✅ CORRECT: Enforce HTTPS
def validate_url(url: str) -> str:
    """
    Ensure URL uses HTTPS protocol.
    
    Args:
        url: URL to validate
    
    Returns:
        Validated HTTPS URL
    
    Raises:
        ValueError: If URL is not HTTPS
    """
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS URLs are allowed")
    
    return url
```

### Secure File Handling

```python
# ✅ CORRECT: Secure temporary file handling
import tempfile
import os
from pathlib import Path

def process_sensitive_file(data: bytes) -> dict:
    """
    Process sensitive data using secure temporary file.
    
    Args:
        data: Sensitive data bytes
    
    Returns:
        Processing results
    """
    # Create temporary file with restricted permissions
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.tmp') as tmp_file:
        tmp_path = Path(tmp_file.name)
        
        # Restrict permissions (owner read/write only)
        os.chmod(tmp_path, 0o600)
        
        # Write sensitive data
        tmp_file.write(data)
    
    try:
        # Process file
        results = process_file(tmp_path)
        return results
    finally:
        # Securely delete temporary file
        if tmp_path.exists():
            # Overwrite with zeros before deleting
            tmp_path.write_bytes(b'\x00' * tmp_path.stat().st_size)
            tmp_path.unlink()
```

### Temporary File Cleanup

```python
# ✅ CORRECT: Automatic cleanup with context manager
from contextlib import contextmanager
from pathlib import Path
import tempfile
import shutil

@contextmanager
def temporary_directory():
    """
    Create temporary directory with automatic cleanup.
    
    Yields:
        Path to temporary directory
    """
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        yield tmp_dir
    finally:
        # Recursively delete directory and contents
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

# Usage
with temporary_directory() as tmp_dir:
    # Create temporary files
    temp_file = tmp_dir / "report.csv"
    temp_file.write_text("sensitive,data")
    
    # Process files
    process_report(temp_file)
    
# Directory automatically deleted after context exits
```

---

## Security Checklist

### Pre-Commit Security Validation

Use this checklist before committing code:

- [ ] **Credentials**: No hardcoded secrets (run `git secrets --scan`)
- [ ] **Input Validation**: All user inputs validated and sanitized
- [ ] **Error Handling**: No stack traces exposed to users
- [ ] **Logging**: No PII or secrets in log messages
- [ ] **Authentication**: Service principals use least privilege
- [ ] **API Calls**: TLS verification enabled, timeouts set
- [ ] **File Operations**: Path traversal prevention implemented
- [ ] **Dependencies**: No known vulnerabilities (run `safety check`)
- [ ] **Code Quality**: Passes linters (Bandit, PSScriptAnalyzer)
- [ ] **Documentation**: Security considerations documented

### Code Review Security Focus

When reviewing code, check for:

1. **Secret Management**
   - Environment variables used correctly
   - No hardcoded credentials
   - Key Vault integration for production

2. **Input Validation**
   - All external inputs validated
   - Path traversal prevention
   - Email/domain validation

3. **Authentication/Authorization**
   - Service principal permissions minimal
   - RBAC implemented where needed
   - Token management secure

4. **Error Handling**
   - User-friendly error messages
   - Detailed logging for debugging
   - No sensitive data in errors

5. **API Security**
   - TLS verification enabled
   - Timeouts configured
   - Rate limiting handled
   - Response validation

6. **Data Protection**
   - Sensitive files encrypted
   - HTTPS enforced
   - Temporary files cleaned up

---

## Tools Integration

### Bandit (Python Security Scanner)

**Configuration**: `.bandit` file

```yaml
# .bandit
exclude_dirs:
  - /tests/
  - /venv/
  - /.venv/

tests:
  - B201  # flask_debug_true
  - B301  # pickle usage
  - B302  # marshal usage
  - B303  # insecure MD5/SHA1
  - B304  # insecure cipher usage
  - B305  # insecure cipher modes
  - B306  # insecure mktemp usage
  - B307  # eval usage
  - B308  # mark_safe usage
  - B310  # urllib.urlopen
  - B401  # telnetlib usage
  - B501  # request with verify=False
  - B502  # ssl with bad defaults
  - B503  # ssl with bad version
  - B504  # ssl with no version
  - B505  # weak cryptographic key
  - B506  # yaml.load usage
  - B601  # paramiko usage
  - B602  # shell injection
  - B603  # subprocess without shell=False
  - B604  # call with shell=True
  - B605  # start_process_with_a_shell
  - B606  # start_process_with_no_shell
  - B607  # start_process_with_partial_path
```

**Usage**:

```bash
# Run Bandit security scan
bandit -r scripts/ src/ -f json -o bandit-report.json

# Run with high severity only
bandit -r scripts/ src/ -ll

# Check specific file
bandit scripts/clean_csv.py
```

### Safety (Dependency Vulnerability Scanner)

```bash
# Check all dependencies
safety check --json

# Check with specific file
safety check -r requirements.txt

# Auto-update vulnerable packages
safety check --apply-updates
```

### PSScriptAnalyzer (PowerShell)

**Configuration**: `.PSScriptAnalyzerSettings.psd1`

```powershell
# .PSScriptAnalyzerSettings.psd1
@{
    IncludeRules = @(
        'PSAvoidUsingPlainTextForPassword',
        'PSAvoidUsingConvertToSecureStringWithPlainText',
        'PSAvoidUsingWMICmdlet',
        'PSAvoidUsingEmptyCatchBlock',
        'PSUseDeclaredVarsMoreThanAssignments'
    )
    
    ExcludeRules = @(
        'PSAvoidUsingWriteHost'  # Allowed for user-facing scripts
    )
    
    Severity = @('Error', 'Warning')
}
```

**Usage**:

```powershell
# Scan PowerShell scripts
Invoke-ScriptAnalyzer -Path scripts/powershell/ -Recurse -Settings .PSScriptAnalyzerSettings.psd1

# Fix automatically (where possible)
Invoke-ScriptAnalyzer -Path script.ps1 -Fix
```

### Pre-Commit Hooks

**Configuration**: `.pre-commit-config.yaml`

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: bandit
        name: Bandit Security Scan
        entry: bandit
        args: ['-r', 'scripts/', 'src/', '-ll']
        language: system
        pass_filenames: false
      
      - id: safety
        name: Safety Dependency Check
        entry: safety
        args: ['check']
        language: system
        pass_filenames: false
      
      - id: git-secrets
        name: Git Secrets Scan
        entry: git secrets --scan
        language: system
        pass_filenames: false
```

**Setup**:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### GitHub Actions Integration

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [ Primary, develop ]
  pull_request:
    branches: [ Primary, develop ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install bandit safety
      
      - name: Run Bandit
        run: bandit -r scripts/ src/ -f json -o bandit-report.json
      
      - name: Run Safety
        run: safety check --json
      
      - name: Upload Security Reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: bandit-report.json
```

---

## Additional Resources

### Internal Documentation

- [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) - Complete project architecture and patterns
- [`docs/M365_SERVICE_PRINCIPAL_SETUP.md`](M365_SERVICE_PRINCIPAL_SETUP.md) - Service principal configuration
- [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - Common issues and solutions
- [`SECURITY.md`](../SECURITY.md) - Security policy and vulnerability reporting
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) - Contribution guidelines including code quality

### External Standards

- [CIS Microsoft 365 Foundations Benchmark](https://www.cisecurity.org/benchmark/microsoft_365)
- [AICPA Trust Services Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/trustservicesprinciples.html)
- [SOX Compliance Guide](https://www.soxlaw.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Microsoft Security Best Practices](https://docs.microsoft.com/en-us/security/compass/compass)

### Security Training

- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Microsoft Security Development Lifecycle](https://www.microsoft.com/en-us/securityengineering/sdl)
- [SANS Secure Coding](https://www.sans.org/secure-coding/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 2025 | Initial secure coding guide for CPA environments |

---

**Document Owner**: Rahman Finance and Accounting P.L.LLC  
**Review Cycle**: Quarterly  
**Last Review**: December 2025  
**Next Review**: March 2026
