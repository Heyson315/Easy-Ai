# Custom M365 MCP Server Development Guide

## 🎯 Overview

This guide shows how to create custom Model Context Protocol (MCP) servers that integrate AI assistants directly with your Microsoft 365 environment, enabling intelligent automation and analysis.

> 🧠 **For AI Development**: This guide complements the comprehensive [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) which contains essential project architecture, patterns, and workflows for AI coding agents working on this toolkit.

## 🏗️ Architecture Overview

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐    Graph API    ┌─────────────────┐
│ AI Assistant    │ ←──────────────── │ Custom M365     │ ──────────────→ │ Microsoft 365   │
│ (GitHub Copilot,│                   │ MCP Server      │                 │ Services        │
│  Claude, etc.)  │                   │                 │                 │ • Exchange      │
└─────────────────┘                   └─────────────────┘                 │ • SharePoint    │
                                              │                           │ • Teams         │
                                              │                           │ • Azure AD      │
                                              ▼                           │ • Security      │
                                      ┌─────────────────┐                 └─────────────────┘
                                      │ Authentication  │
                                      │ • Service       │
                                      │   Principal     │
                                      │ • Certificate   │
                                      │ • Secure Vault  │
                                      └─────────────────┘
```

## 🔧 Implementation Strategy

### 1. MCP Server Foundation

Create a Python-based MCP server using the official MCP SDK:

```python
# m365_mcp_server.py
from mcp import Server, McpError
from mcp.types import Tool, TextContent
import asyncio
from microsoft.graph import GraphServiceClient
from azure.identity import ClientSecretCredential

class M365MCPServer:
    def __init__(self):
        self.server = Server("m365-security-server")
        self.graph_client = None
        self.setup_tools()

    def setup_tools(self):
        """Register all available M365 tools"""

        @self.server.tool("run_security_audit")
        async def run_security_audit(tenant_id: str) -> str:
            """Execute comprehensive M365 security audit"""
            try:
                # Connect to your existing M365CIS module
                audit_results = await self._execute_cis_audit(tenant_id)
                return f"Security audit completed. {audit_results}"
            except Exception as e:
                raise McpError(f"Audit failed: {str(e)}")

        @self.server.tool("analyze_sharepoint_permissions")  
        async def analyze_sharepoint_permissions(site_url: str) -> str:
            """Analyze SharePoint site permissions in real-time"""
            try:
                permissions = await self._get_sharepoint_permissions(site_url)
                analysis = await self._analyze_permission_risks(permissions)
                return f"Permission analysis: {analysis}"
            except Exception as e:
                raise McpError(f"Permission analysis failed: {str(e)}")

        @self.server.tool("get_security_alerts")
        async def get_security_alerts(severity: str = "high") -> str:
            """Retrieve current security alerts from Microsoft 365"""
            try:
                alerts = await self._fetch_security_alerts(severity)
                return f"Found {len(alerts)} {severity} severity alerts"
            except Exception as e:
                raise McpError(f"Alert retrieval failed: {str(e)}")

    async def _authenticate_graph(self):
        """Authenticate with Microsoft Graph using service principal"""
        credential = ClientSecretCredential(
            tenant_id=self.config['tenant_id'],
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret']
        )
        self.graph_client = GraphServiceClient(credential)
```

### 2. Microsoft Graph Integration

```python
# graph_integration.py
class M365GraphIntegration:
    def __init__(self, graph_client):
        self.client = graph_client

    async def get_security_score(self):
        """Retrieve Microsoft Secure Score"""
        secure_scores = await self.client.security.secure_scores.get()
        return {
            'current_score': secure_scores.value[0].current_score,
            'max_score': secure_scores.value[0].max_score,
            'percentage': (secure_scores.value[0].current_score /
                          secure_scores.value[0].max_score) * 100
        }

    async def analyze_risky_users(self):
        """Identify users with security risks"""
        risky_users = await self.client.identity_protection.risky_users.get()
        return [
            {
                'user': user.user_display_name,
                'risk_level': user.risk_level,
                'risk_detail': user.risk_detail
            }
            for user in risky_users.value
        ]

    async def audit_sharepoint_sites(self):
        """Comprehensive SharePoint security audit"""
        sites = await self.client.sites.get()
        security_findings = []

        for site in sites.value:
            # Check external sharing settings
            sharing_settings = await self._check_sharing_settings(site.id)

            # Analyze permissions
            permissions = await self._audit_site_permissions(site.id)

            # Check for sensitive content
            sensitive_content = await self._scan_sensitive_content(site.id)

            security_findings.append({
                'site': site.display_name,
                'sharing_risks': sharing_settings,
                'permission_issues': permissions,
                'sensitive_content': sensitive_content
            })

        return security_findings
```

### 3. Integration with Existing M365 Toolkit

```python
# toolkit_integration.py
import subprocess
import json
from pathlib import Path

class ToolkitIntegration:
    def __init__(self, toolkit_path: Path):
        self.toolkit_path = toolkit_path

    async def run_powershell_audit(self, tenant_id: str):
        """Execute existing PowerShell CIS audit"""
        script_path = self.toolkit_path / "scripts/powershell/Invoke-M365CISAudit.ps1"

        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script_path),
            "-TenantId", tenant_id,
            "-Timestamped"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Parse the JSON output
            output_file = self.toolkit_path / "output/reports/security/m365_cis_audit.json"
            if output_file.exists():
                return json.loads(output_file.read_text())
        else:
            raise Exception(f"PowerShell audit failed: {result.stderr}")

    async def generate_enhanced_report(self, audit_data, graph_data):
        """Combine audit results with real-time Graph data"""
        enhanced_report = {
            'audit_timestamp': audit_data.get('timestamp'),
            'cis_compliance': audit_data,
            'realtime_security': graph_data,
            'recommendations': await self._generate_ai_recommendations(audit_data, graph_data)
        }

        return enhanced_report
```

## 🚀 Advanced Use Cases

### 1. Intelligent Security Monitoring

```python
# AI Assistant Query: "What's our current security posture?"

async def comprehensive_security_analysis():
    """Multi-dimensional security analysis"""

    # Get CIS compliance status
    cis_results = await run_powershell_audit(tenant_id)

    # Get real-time security data
    security_score = await get_security_score()
    risky_users = await analyze_risky_users()
    security_alerts = await get_security_alerts("high")

    # Analyze SharePoint security
    sharepoint_audit = await audit_sharepoint_sites()

    # Generate AI-powered insights
    insights = await analyze_security_trends(cis_results, security_score)

    return {
        'overall_status': 'CRITICAL' if security_score['percentage'] < 70 else 'GOOD',
        'cis_compliance': cis_results,
        'security_score': security_score,
        'immediate_risks': risky_users + security_alerts,
        'sharepoint_security': sharepoint_audit,
        'ai_insights': insights,
        'recommended_actions': await generate_remediation_plan()
    }
```

### 2. Automated Incident Response

```python
# AI Assistant Query: "Investigate and respond to the latest security incident"

async def incident_response_workflow(incident_id: str):
    """Automated security incident investigation"""

    # Get incident details
    incident = await get_security_incident(incident_id)

    # Gather related data
    affected_users = await get_affected_users(incident)
    related_alerts = await get_related_alerts(incident)

    # Perform automated analysis
    threat_analysis = await analyze_threat_indicators(incident)
    impact_assessment = await assess_business_impact(affected_users)

    # Generate response recommendations
    response_plan = await generate_response_plan(threat_analysis, impact_assessment)

    # Execute safe automated responses
    if response_plan['auto_actions']:
        await execute_safe_responses(response_plan['auto_actions'])

    return {
        'incident_summary': incident,
        'threat_analysis': threat_analysis,
        'impact_assessment': impact_assessment,
        'response_plan': response_plan,
        'actions_taken': response_plan.get('executed_actions', [])
    }
```

### 3. Continuous Compliance Monitoring

```python
# AI Assistant Query: "Monitor our compliance status and alert on any issues"

async def continuous_compliance_monitoring():
    """Real-time compliance monitoring with intelligent alerting"""

    while True:
        # Run periodic checks
        compliance_status = await check_compliance_policies()
        data_governance = await audit_data_governance()
        retention_compliance = await check_retention_policies()

        # Detect compliance drift
        issues = await detect_compliance_issues(compliance_status)

        if issues:
            # Generate intelligent alerts
            alert = await generate_compliance_alert(issues)

            # Notify stakeholders
            await send_compliance_notification(alert)

            # Suggest remediation
            remediation = await suggest_auto_remediation(issues)

            if remediation['safe_to_auto_fix']:
                await execute_compliance_fixes(remediation['actions'])

        # Wait for next check cycle
        await asyncio.sleep(3600)  # Check hourly
```

## 🔐 Security Considerations

### Authentication & Authorization
```python
# secure_authentication.py
class SecureM365Authentication:
    def __init__(self):
        self.vault_client = self._setup_key_vault()

    async def get_secure_credentials(self):
        """Retrieve credentials from Azure Key Vault"""
        credentials = {
            'tenant_id': await self.vault_client.get_secret('m365-tenant-id'),
            'client_id': await self.vault_client.get_secret('m365-client-id'),
            'client_secret': await self.vault_client.get_secret('m365-client-secret')
        }
        return credentials

    def _setup_key_vault(self):
        """Configure secure credential storage"""
        # Implementation for Azure Key Vault or similar
        pass
```

### Audit Logging
```python
# audit_logging.py
class MCPAuditLogger:
    def __init__(self):
        self.logger = self._setup_secure_logging()

    async def log_mcp_action(self, action: str, user: str, result: str):
        """Log all MCP server actions for audit trail"""
        audit_entry = {
            'timestamp': datetime.utcnow(),
            'action': action,
            'user': user,
            'result': result,
            'session_id': self._get_session_id()
        }

        await self.logger.info(json.dumps(audit_entry))
```

## 🚀 Deployment Strategy

### 1. Development Environment
```bash
# Setup development MCP server
git clone https://github.com/your-org/m365-mcp-server
cd m365-mcp-server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Configure authentication
cp config/auth.template.json config/auth.json
# Edit config/auth.json with your service principal details

# Start development server
python -m m365_mcp_server --dev
```

### 2. Production Deployment
```yaml
# docker-compose.yml for production deployment
version: '3.8'
services:
  m365-mcp-server:
    build: .
    environment:
      - AZURE_KEY_VAULT_URL=${KEY_VAULT_URL}
      - TENANT_ID=${TENANT_ID}
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
```

## 📊 Benefits of Custom M365 MCP Servers

### For Your Organization:
- **Real-time Security Intelligence** - AI assistants with live M365 data
- **Automated Compliance** - Continuous monitoring with intelligent alerts
- **Incident Response** - AI-powered investigation and response
- **Operational Efficiency** - Automated routine tasks and analysis
- **Custom Workflows** - AI assistants tailored to your specific processes

### For IT Teams:
- **Proactive Security** - Identify issues before they become incidents
- **Reduced Manual Work** - Automation of repetitive security tasks
- **Better Insights** - AI analysis of complex security data
- **Faster Response** - Immediate access to comprehensive security data

### For Business Users:
- **Natural Language Queries** - "Show me our SharePoint security risks"
- **Intelligent Recommendations** - AI-powered optimization suggestions
- **Simplified Compliance** - Easy access to compliance status and reports
- **Self-Service Analytics** - Business users can get insights without IT intervention

## 🎯 Next Steps

1. **Prototype Development** - Start with basic MCP server framework
2. **Authentication Setup** - Configure service principal and secure storage
3. **Core Tool Development** - Implement essential M365 integration tools
4. **Testing & Validation** - Thorough testing with your M365 environment
5. **Production Deployment** - Secure deployment with monitoring and logging
6. **User Training** - Train teams on AI assistant capabilities
7. **Continuous Enhancement** - Add new tools based on user feedback

## 📚 Resources

- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Microsoft Graph API Reference](https://docs.microsoft.com/en-us/graph/)
- [Azure Service Principal Setup](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
- [Your Existing M365 Security Toolkit](../README.md)

---

**This represents the cutting edge of AI-powered M365 administration - where AI assistants become intelligent partners in managing and securing your Microsoft 365 environment!** 🚀
