# M365 Security Toolkit - MCP Server Extension

🤖 **Optional Extension**: Model Context Protocol server for AI assistant integration

## 🎯 Overview

The MCP server extension enables AI assistants (GitHub Copilot, Claude, ChatGPT, etc.) to directly interact with your M365 security toolkit through natural language queries.

**What it does:**
- Provides AI assistants with tools to run security audits
- Analyzes SharePoint permissions via AI commands
- Generates compliance reports on-demand
- Enables automated security remediation workflows

**What it's NOT:**
- Not required for core toolkit functionality
- Not a replacement for PowerShell scripts
- Not a standalone product - it's a wrapper/interface layer

---

## 🚀 Quick Start

### 1. Install Extension Dependencies

From the repository root:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install MCP and GPT-5 extensions
pip install -r requirements-extensions.txt
```

### 2. Configure Environment

```powershell
# Run setup wizard
python src/extensions/mcp/setup.py --configure-env

# Edit .env with your Azure credentials
notepad .env
```

See [`docs/M365_SERVICE_PRINCIPAL_SETUP.md`](../../../docs/M365_SERVICE_PRINCIPAL_SETUP.md) for Azure authentication setup.

### 3. Start MCP Server

```powershell
# Test the server
python src/extensions/mcp/server.py
```

### 4. Register with AI Assistant

Add to your AI assistant configuration (e.g., VS Code settings or Claude Desktop config):

```json
{
  "mcpServers": {
    "m365-security": {
      "command": "python",
      "args": ["C:/path/to/share-report/src/extensions/mcp/server.py"],
      "env": {
        "M365_TENANT_ID": "your-tenant-id",
        "M365_CLIENT_ID": "your-client-id",
        "M365_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

---

## 🛠️ Available MCP Tools

| Tool | Purpose | Example AI Query |
|------|---------|------------------|
| `run_security_audit` | Execute M365 CIS compliance audit | "Run a security audit on our M365 tenant" |
| `analyze_sharepoint_permissions` | Analyze SharePoint access patterns | "Check SharePoint permissions for risks" |
| `get_security_dashboard` | Generate interactive HTML dashboard | "Show me our security dashboard" |
| `remediate_security_issues` | Preview/apply security fixes | "Preview available security remediations" |
| `get_compliance_status` | Current compliance metrics | "What's our M365 compliance status?" |

---

## 📁 Directory Structure

```
src/extensions/mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server implementation (504 lines)
├── setup.py             # Setup and configuration wizard (176 lines)
├── tools/               # Individual MCP tool definitions
│   ├── audit_tools.py   # Security audit tools
│   ├── sharepoint_tools.py  # SharePoint analysis tools
│   └── compliance_tools.py  # Compliance reporting tools
└── README.md            # This file
```

---

## 🔐 Security Considerations

**Credential Management:**
- Uses `.env` file for secure credential storage
- Never hardcodes secrets in code
- Supports Azure Key Vault integration
- Service principal authentication recommended

**Audit Logging:**
- All MCP actions logged to `~/.aitk/logs/m365_mcp_server.log`
- Includes timestamp, action, user, result
- Enables compliance audit trails

**Safe Remediation:**
- Preview mode (`-WhatIf`) enabled by default
- Explicit confirmation required for changes
- Rollback procedures documented

---

## 🔄 Integration with Core Toolkit

The MCP server **wraps existing toolkit functionality**:

```python
# MCP calls existing PowerShell scripts
run_security_audit() → scripts/powershell/Invoke-M365CISAudit.ps1

# MCP uses existing Python modules
analyze_sharepoint() → scripts/clean_csv.py → src/integrations/sharepoint_connector.py

# MCP leverages existing reporting
get_dashboard() → scripts/generate_security_dashboard.py
```

**Benefits:**
- No duplicate code - reuses proven functionality
- Maintains single source of truth
- Updates to core toolkit automatically benefit MCP
- Can run scripts directly OR via AI assistant

---

## 📚 Additional Documentation

- **Comprehensive Guide**: [`docs/CUSTOM_MCP_SERVER_GUIDE.md`](../../../docs/CUSTOM_MCP_SERVER_GUIDE.md) (418 lines)
- **Azure Setup**: [`docs/M365_SERVICE_PRINCIPAL_SETUP.md`](../../../docs/M365_SERVICE_PRINCIPAL_SETUP.md) (500+ lines)
- **AI Development**: [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md)

---

## 🧪 Testing

```powershell
# Test MCP server configuration
python src/extensions/mcp/setup.py --test-connection

# Test individual tools (requires Azure auth)
python -c "from src.extensions.mcp.server import M365SecurityMCPServer; import asyncio; asyncio.run(M365SecurityMCPServer().start())"
```

---

## 🤝 Contributing

This is an **optional extension** - contributions should:
- Maintain backward compatibility with core toolkit
- Not introduce required dependencies to core
- Follow existing code patterns and conventions
- Include comprehensive documentation

---

## 📊 When to Use This Extension

**Use MCP Server when:**
✅ You want AI assistants to run security audits  
✅ You need natural language queries for M365 data  
✅ You want to automate multi-step security workflows  
✅ You're integrating with GitHub Copilot/Claude/ChatGPT  

**Use Core Toolkit directly when:**
✅ Running scheduled/automated scripts  
✅ CI/CD pipeline integration  
✅ Custom PowerShell workflows  
✅ No AI assistant integration needed  

---

## 🆘 Troubleshooting

**"MCP SDK not installed"**
```powershell
pip install -r requirements-extensions.txt
```

**"Authentication failed"**
- Verify `.env` file has correct Azure credentials
- Check service principal permissions
- See `docs/M365_SERVICE_PRINCIPAL_SETUP.md`

**"Tool not found"**
- Ensure all PowerShell scripts exist in `scripts/powershell/`
- Verify Python modules in `src/core/` and `src/integrations/`
- Run from repository root directory

---

**🎯 This extension transforms your M365 security toolkit into an AI-powered platform!**
