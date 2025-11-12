# 🤖 MCP Tool Development Patterns for AI Agents

**Last Updated**: 2025-11-12

This guide provides practical patterns and examples for AI coding agents developing Model Context Protocol (MCP) tools for the M365 Security & SharePoint Analysis Toolkit.

---

## 🎯 What is MCP and Why It Matters

**Model Context Protocol (MCP)** enables AI assistants to interact with external systems through a standardized interface.

### Use Cases for M365 Toolkit

- **Natural Language Security Audits**: "Run a CIS security audit on our tenant"
- **Intelligent Analysis**: "Show me all SharePoint sites with external sharing enabled"
- **Automated Remediation**: "Preview security fixes for failed controls"
- **Trend Analysis**: "Compare this month's security posture to last month"

---

## 🏗️ MCP Architecture in This Project

```
┌─────────────────┐
│  AI Assistant   │  (GitHub Copilot, Claude, ChatGPT)
│  (User Prompt)  │
└────────┬────────┘
         │ MCP Protocol (JSON-RPC)
         ▼
┌─────────────────┐
│ MCP Server      │  src/extensions/mcp/server.py
│ - Tool Registry │
│ - Auth Handler  │
│ - Error Handler │
└────────┬────────┘
         │ Calls existing toolkit
         ▼
┌─────────────────────────────────────┐
│ Existing Toolkit Components         │
│ - PowerShell scripts                │
│ - Python modules                    │
│ - Configuration files               │
└─────────────────────────────────────┘
```

**Key Principle**: MCP tools **wrap** existing functionality, not replace it.

---

## 📋 MCP Tool Structure

### Basic MCP Tool Template

```python
# src/extensions/mcp/tools/my_tool.py
from typing import Dict, Any, List
from pathlib import Path
import json
import subprocess

async def tool_name(
    param1: str,
    param2: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Brief description of what this tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 100)
        **kwargs: Additional parameters from MCP client
        
    Returns:
        Dict containing:
            - success: bool
            - data: Any
            - message: str
            - error: Optional[str]
            
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If execution fails
        
    Example:
        result = await tool_name("value1", param2=200)
        if result['success']:
            print(result['data'])
    """
    try:
        # 1. Validate inputs
        if not param1:
            raise ValueError("param1 cannot be empty")
            
        # 2. Call existing toolkit component
        # Option A: Call Python module
        from src.core.my_module import my_function
        data = my_function(param1, param2)
        
        # Option B: Call PowerShell script
        # ps_script = Path("scripts/powershell/MyScript.ps1")
        # result = subprocess.run(
        #     ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
        #      "-File", str(ps_script), "-Param1", param1],
        #     capture_output=True,
        #     text=True,
        #     timeout=300
        # )
        # if result.returncode != 0:
        #     raise RuntimeError(f"Script failed: {result.stderr}")
        # data = json.loads(result.stdout)
        
        # 3. Return success response
        return {
            'success': True,
            'data': data,
            'message': f"Successfully processed {param1}"
        }
        
    except ValueError as e:
        return {
            'success': False,
            'data': None,
            'message': "Invalid input",
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': "Tool execution failed",
            'error': str(e)
        }
```

---

## 🔧 Pattern 1: Wrapping PowerShell Scripts

### Example: M365 Security Audit Tool

```python
# src/extensions/mcp/tools/audit_tools.py
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

async def run_m365_security_audit(
    spo_admin_url: Optional[str] = None,
    timestamped: bool = True,
    skip_purview: bool = False
) -> Dict[str, Any]:
    """
    Run M365 CIS security audit.
    
    This wraps scripts/powershell/Invoke-M365CISAudit.ps1
    
    Args:
        spo_admin_url: SharePoint admin URL (e.g., https://tenant-admin.sharepoint.com)
        timestamped: Add timestamp to output filename
        skip_purview: Skip Purview compliance checks
        
    Returns:
        Audit results with pass/fail status for each control
    """
    try:
        # Build command
        script_path = Path("scripts/powershell/Invoke-M365CISAudit.ps1")
        if not script_path.exists():
            raise FileNotFoundError(f"Audit script not found: {script_path}")
        
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script_path.absolute())
        ]
        
        if spo_admin_url:
            cmd.extend(["-SPOAdminUrl", spo_admin_url])
        if timestamped:
            cmd.append("-Timestamped")
        if skip_purview:
            cmd.append("-SkipPurview")
        
        # Execute with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=Path.cwd()
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'data': None,
                'message': "Audit script failed",
                'error': result.stderr
            }
        
        # Find output JSON
        output_dir = Path("output/reports/security")
        json_files = sorted(output_dir.glob("m365_cis_audit*.json"))
        
        if not json_files:
            return {
                'success': False,
                'data': None,
                'message': "No audit output found",
                'error': "Expected JSON output in output/reports/security/"
            }
        
        # Read latest result
        latest_json = json_files[-1]
        audit_data = json.loads(latest_json.read_text(encoding='utf-8-sig'))
        
        # Calculate summary
        controls = audit_data.get('Controls', [])
        summary = {
            'total': len(controls),
            'passed': sum(1 for c in controls if c.get('Status') == 'Pass'),
            'failed': sum(1 for c in controls if c.get('Status') == 'Fail'),
            'manual': sum(1 for c in controls if c.get('Status') == 'Manual'),
            'output_file': str(latest_json)
        }
        
        return {
            'success': True,
            'data': {
                'summary': summary,
                'controls': controls,
                'timestamp': audit_data.get('Timestamp')
            },
            'message': f"Audit complete: {summary['passed']}/{summary['total']} controls passed"
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'data': None,
            'message': "Audit timed out after 10 minutes",
            'error': "Consider running audit manually for detailed progress"
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"Audit failed: {type(e).__name__}",
            'error': str(e)
        }
```

---

## 🐍 Pattern 2: Wrapping Python Modules

### Example: SharePoint Permissions Analysis Tool

```python
# src/extensions/mcp/tools/sharepoint_tools.py
from pathlib import Path
from typing import Dict, Any
import pandas as pd

async def analyze_sharepoint_permissions(
    input_csv: str,
    generate_report: bool = True
) -> Dict[str, Any]:
    """
    Analyze SharePoint permissions from CSV export.
    
    This wraps:
    1. scripts/clean_csv.py - CSV cleaning
    2. src/integrations/sharepoint_connector.py - Analysis
    
    Args:
        input_csv: Path to raw SharePoint permissions CSV
        generate_report: Whether to generate Excel report
        
    Returns:
        Analysis summary with risk indicators
    """
    try:
        from scripts.clean_csv import clean_csv
        from src.integrations.sharepoint_connector import analyze_permissions
        
        # Validate input
        input_path = Path(input_csv)
        if not input_path.exists():
            raise FileNotFoundError(f"Input CSV not found: {input_csv}")
        
        # Step 1: Clean CSV
        clean_path = Path("data/processed") / f"clean_{input_path.name}"
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        
        clean_stats = clean_csv(input_path, clean_path)
        
        if clean_stats['output_rows'] == 0:
            return {
                'success': False,
                'data': None,
                'message': "No valid data in input CSV",
                'error': f"Removed {clean_stats['comment_lines']} comments, {clean_stats['blank_lines']} blank lines"
            }
        
        # Step 2: Analyze permissions
        report_path = None
        if generate_report:
            report_path = Path("output/reports/business") / f"sharepoint_analysis_{input_path.stem}.xlsx"
            report_path.parent.mkdir(parents=True, exist_ok=True)
        
        analysis = analyze_permissions(clean_path, report_path)
        
        # Step 3: Generate insights
        insights = generate_security_insights(analysis)
        
        return {
            'success': True,
            'data': {
                'summary': analysis,
                'insights': insights,
                'clean_stats': clean_stats,
                'report_path': str(report_path) if report_path else None
            },
            'message': f"Analyzed {analysis['total_users']} users across {analysis['total_sites']} sites"
        }
        
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"Analysis failed: {type(e).__name__}",
            'error': str(e)
        }

def generate_security_insights(analysis: Dict[str, Any]) -> list:
    """Generate security insights from analysis data."""
    insights = []
    
    # Check for external users
    if analysis.get('external_users', 0) > 0:
        insights.append({
            'type': 'warning',
            'category': 'External Access',
            'message': f"{analysis['external_users']} external users detected",
            'recommendation': "Review external user access and ensure appropriate permissions"
        })
    
    # Check for overprivileged users
    full_control_count = analysis.get('full_control_users', 0)
    if full_control_count > analysis.get('total_users', 1) * 0.2:
        insights.append({
            'type': 'warning',
            'category': 'Privilege Escalation',
            'message': f"{full_control_count} users have Full Control",
            'recommendation': "Review and apply principle of least privilege"
        })
    
    # Check for stale permissions
    if analysis.get('stale_permissions', 0) > 0:
        insights.append({
            'type': 'info',
            'category': 'Access Review',
            'message': f"{analysis['stale_permissions']} permissions haven't been reviewed recently",
            'recommendation': "Implement periodic access reviews"
        })
    
    return insights
```

---

## 🔐 Pattern 3: Secure Authentication

### Service Principal Authentication Tool

```python
# src/extensions/mcp/tools/auth_tools.py
from typing import Dict, Any, Optional
import os
from pathlib import Path

async def authenticate_m365(
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    use_env: bool = True
) -> Dict[str, Any]:
    """
    Authenticate to M365 using service principal.
    
    Security: Credentials loaded from environment or .env file, never hardcoded.
    
    Args:
        tenant_id: Azure AD tenant ID (from .env if not provided)
        client_id: Application (client) ID (from .env if not provided)
        client_secret: Client secret (from .env if not provided)
        use_env: Load credentials from environment/.env
        
    Returns:
        Authentication status and token info
    """
    try:
        # Load from environment if requested
        if use_env:
            from dotenv import load_dotenv
            load_dotenv()
            
            tenant_id = tenant_id or os.getenv('M365_TENANT_ID')
            client_id = client_id or os.getenv('M365_CLIENT_ID')
            client_secret = client_secret or os.getenv('M365_CLIENT_SECRET')
        
        # Validate credentials present
        if not all([tenant_id, client_id, client_secret]):
            return {
                'success': False,
                'data': None,
                'message': "Missing required credentials",
                'error': "Provide tenant_id, client_id, client_secret or configure .env file"
            }
        
        # Authenticate (example with msal)
        from msal import ConfidentialClientApplication
        
        app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )
        
        # Acquire token
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        
        if "access_token" in result:
            # Never return the actual token in MCP response!
            return {
                'success': True,
                'data': {
                    'authenticated': True,
                    'tenant_id': tenant_id,
                    'expires_in': result.get('expires_in'),
                    'scope': result.get('scope')
                    # Note: NOT including access_token
                },
                'message': "Successfully authenticated to M365"
            }
        else:
            return {
                'success': False,
                'data': None,
                'message': "Authentication failed",
                'error': result.get('error_description', 'Unknown error')
            }
            
    except ImportError:
        return {
            'success': False,
            'data': None,
            'message': "Missing dependency: msal",
            'error': "Install with: pip install msal"
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"Authentication error: {type(e).__name__}",
            'error': str(e)
        }
```

---

## 📊 Pattern 4: Data Aggregation and Reporting

### Dashboard Generation Tool

```python
# src/extensions/mcp/tools/reporting_tools.py
from pathlib import Path
from typing import Dict, Any, Optional
import json

async def generate_security_dashboard(
    input_json: Optional[str] = None,
    output_html: Optional[str] = None,
    include_trends: bool = True
) -> Dict[str, Any]:
    """
    Generate interactive HTML security dashboard.
    
    This wraps scripts/generate_security_dashboard.py
    
    Args:
        input_json: Path to audit JSON file (latest if not specified)
        output_html: Output HTML path (default: output/reports/security/dashboard.html)
        include_trends: Include historical trend analysis
        
    Returns:
        Dashboard info with summary metrics
    """
    try:
        # Find latest audit result if not specified
        if not input_json:
            output_dir = Path("output/reports/security")
            json_files = sorted(output_dir.glob("m365_cis_audit*.json"))
            if not json_files:
                return {
                    'success': False,
                    'data': None,
                    'message': "No audit results found",
                    'error': "Run an audit first with run_m365_security_audit"
                }
            input_json = str(json_files[-1])
        
        # Set default output
        if not output_html:
            output_html = "output/reports/security/dashboard.html"
        
        output_path = Path(output_html)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Call generation script
        from scripts.generate_security_dashboard import generate_dashboard
        
        dashboard_info = generate_dashboard(
            input_json=input_json,
            output_html=output_html,
            include_trends=include_trends
        )
        
        # Read audit data for summary
        audit_data = json.loads(Path(input_json).read_text(encoding='utf-8-sig'))
        controls = audit_data.get('Controls', [])
        
        summary = {
            'total_controls': len(controls),
            'passed': sum(1 for c in controls if c.get('Status') == 'Pass'),
            'failed': sum(1 for c in controls if c.get('Status') == 'Fail'),
            'pass_rate': round(sum(1 for c in controls if c.get('Status') == 'Pass') / len(controls) * 100, 1) if controls else 0,
            'dashboard_path': str(output_path.absolute()),
            'input_audit': input_json
        }
        
        return {
            'success': True,
            'data': {
                'summary': summary,
                'dashboard_info': dashboard_info
            },
            'message': f"Dashboard generated: {summary['pass_rate']}% pass rate"
        }
        
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"Dashboard generation failed: {type(e).__name__}",
            'error': str(e)
        }
```

---

## 🧪 Pattern 5: Testing MCP Tools

### Unit Testing MCP Tools

```python
# tests/test_mcp_tools.py
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

@pytest.mark.asyncio
async def test_sharepoint_tool():
    """Test SharePoint analysis MCP tool."""
    from src.extensions.mcp.tools.sharepoint_tools import analyze_sharepoint_permissions
    
    with TemporaryDirectory() as td:
        td = Path(td)
        
        # Create test CSV
        test_csv = td / "sharepoint_export.csv"
        test_csv.write_text(
            "Resource Path,Permission,User Name,User Email\n"
            "site1,Contribute,Alice,alice@example.com\n"
            "site2,Read,Bob,bob@example.com\n",
            encoding="utf-8"
        )
        
        # Call MCP tool
        result = await analyze_sharepoint_permissions(
            input_csv=str(test_csv),
            generate_report=False
        )
        
        # Validate response structure
        assert result['success'] == True
        assert 'data' in result
        assert 'summary' in result['data']
        assert result['data']['summary']['total_users'] == 2

@pytest.mark.asyncio
async def test_audit_tool_error_handling():
    """Test audit tool handles missing script gracefully."""
    from src.extensions.mcp.tools.audit_tools import run_m365_security_audit
    
    # Temporarily rename script to simulate missing file
    script_path = Path("scripts/powershell/Invoke-M365CISAudit.ps1")
    backup_path = script_path.with_suffix(".ps1.bak")
    
    try:
        if script_path.exists():
            script_path.rename(backup_path)
        
        result = await run_m365_security_audit()
        
        assert result['success'] == False
        assert 'not found' in result['message'].lower()
        
    finally:
        if backup_path.exists():
            backup_path.rename(script_path)
```

---

## 🔄 Pattern 6: Tool Registration

### Registering Tools with MCP Server

```python
# src/extensions/mcp/server.py
from mcp import Server
from .tools import audit_tools, sharepoint_tools, reporting_tools

class M365SecurityMCPServer:
    def __init__(self):
        self.server = Server("m365-security-toolkit")
        self.register_tools()
    
    def register_tools(self):
        """Register all available MCP tools."""
        
        # Security audit tools
        self.server.register_tool(
            name="run_m365_security_audit",
            description="Run comprehensive M365 CIS security compliance audit",
            function=audit_tools.run_m365_security_audit,
            parameters={
                "spo_admin_url": {
                    "type": "string",
                    "description": "SharePoint admin URL (optional)",
                    "required": False
                },
                "timestamped": {
                    "type": "boolean",
                    "description": "Add timestamp to output filename",
                    "required": False,
                    "default": True
                },
                "skip_purview": {
                    "type": "boolean",
                    "description": "Skip Purview compliance checks",
                    "required": False,
                    "default": False
                }
            }
        )
        
        # SharePoint analysis tools
        self.server.register_tool(
            name="analyze_sharepoint_permissions",
            description="Analyze SharePoint permissions from CSV export",
            function=sharepoint_tools.analyze_sharepoint_permissions,
            parameters={
                "input_csv": {
                    "type": "string",
                    "description": "Path to SharePoint permissions CSV",
                    "required": True
                },
                "generate_report": {
                    "type": "boolean",
                    "description": "Generate Excel report",
                    "required": False,
                    "default": True
                }
            }
        )
        
        # Reporting tools
        self.server.register_tool(
            name="generate_security_dashboard",
            description="Generate interactive HTML security dashboard",
            function=reporting_tools.generate_security_dashboard,
            parameters={
                "input_json": {
                    "type": "string",
                    "description": "Path to audit JSON (latest if not specified)",
                    "required": False
                },
                "output_html": {
                    "type": "string",
                    "description": "Output HTML path",
                    "required": False
                },
                "include_trends": {
                    "type": "boolean",
                    "description": "Include historical trends",
                    "required": False,
                    "default": True
                }
            }
        )
```

---

## 📚 Best Practices for MCP Tool Development

### 1. Always Wrap, Never Duplicate

✅ **Good**: Call existing PowerShell script or Python module
```python
result = subprocess.run(["powershell", "-File", "existing_script.ps1"])
```

❌ **Bad**: Reimplement logic in MCP tool
```python
# Don't duplicate 500 lines of audit logic here!
```

### 2. Consistent Return Structure

All tools should return:
```python
{
    'success': bool,      # Operation succeeded or failed
    'data': Any,          # Actual result data (None on error)
    'message': str,       # Human-readable message
    'error': Optional[str] # Error details (only on failure)
}
```

### 3. Comprehensive Error Handling

```python
try:
    # Tool logic
    return {'success': True, 'data': result, 'message': "Success"}
except SpecificError as e:
    return {'success': False, 'data': None, 'message': "Failed", 'error': str(e)}
```

### 4. Security First

- ❌ Never log or return credentials
- ✅ Load secrets from environment variables
- ✅ Validate all inputs
- ✅ Use minimum required permissions

### 5. Documentation and Examples

Every tool must have:
- Docstring with description
- Parameter documentation
- Return value documentation
- Example usage

---

## 🎯 Quick Reference

### Common Patterns Cheat Sheet

| Task | Pattern | File |
|------|---------|------|
| Wrap PowerShell | `subprocess.run(["powershell", "-File", "script.ps1"])` | Pattern 1 |
| Call Python module | `from module import function; result = function()` | Pattern 2 |
| Authenticate | Load from .env, use msal | Pattern 3 |
| Generate reports | Call existing report generators | Pattern 4 |
| Test tools | `@pytest.mark.asyncio async def test_tool()` | Pattern 5 |
| Register tool | `server.register_tool(name, desc, function, params)` | Pattern 6 |

---

## 🆘 Troubleshooting MCP Tools

### Tool Not Found
- Check tool registration in `server.py`
- Verify tool function is `async def`
- Ensure proper import path

### PowerShell Script Fails
- Use absolute paths: `Path("script.ps1").absolute()`
- Check execution policy: `-ExecutionPolicy Bypass`
- Increase timeout for long-running scripts

### Authentication Issues
- Verify `.env` file exists with credentials
- Check service principal permissions
- Review error messages in `error` field

---

**🤖 These patterns enable rapid MCP tool development for enterprise M365 security automation!**
