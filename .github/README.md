# 🤖 AI Development Resources

Welcome to the AI development documentation for the M365 Security & SharePoint Analysis Toolkit!

## 🎯 Start Here

**New to this project?** → Read [AI Agent Quick Start](AI_AGENT_QUICKSTART.md) (15 minutes)

**Looking for something specific?** → See [AI Development Index](AI_DEVELOPMENT_INDEX.md) (Complete navigation)

## 📚 Core Documentation

| Guide | Purpose | When to Read |
|-------|---------|--------------|
| **[AI Agent Quick Start](AI_AGENT_QUICKSTART.md)** | Fast onboarding with practical examples | First time contributing |
| **[Copilot Instructions](copilot-instructions.md)** | Complete architecture reference | Need deep understanding |
| **[AI Workflow Testing](AI_WORKFLOW_TESTING.md)** | Testing patterns and strategies | Writing or debugging tests |
| **[MCP Tool Patterns](MCP_TOOL_PATTERNS.md)** | MCP tool development | Building AI integrations |
| **[AI Development Index](AI_DEVELOPMENT_INDEX.md)** | Navigation hub for all resources | Finding specific information |

## 🚀 Quick Links by Task

- **Adding Python Script** → [Quick Start: Task 1](AI_AGENT_QUICKSTART.md#task-1-add-a-new-python-script)
- **Adding PowerShell Function** → [Quick Start: Task 2](AI_AGENT_QUICKSTART.md#task-2-add-a-new-powershell-function-to-m365cis-module)
- **Processing CSV Files** → [Quick Start: Task 3](AI_AGENT_QUICKSTART.md#task-3-process-csv-with-special-characters)
- **Generating Excel Reports** → [Quick Start: Task 4](AI_AGENT_QUICKSTART.md#task-4-generate-excel-report-with-formatting)
- **Writing Tests** → [Workflow Testing: Patterns](AI_WORKFLOW_TESTING.md#writing-tests-for-new-code)
- **Building MCP Tools** → [MCP Patterns: Structure](MCP_TOOL_PATTERNS.md#mcp-tool-structure)

## 🐛 Issue Templates

- **[AI Development Enhancement](ISSUE_TEMPLATE/ai_development.md)** - Propose improvements to AI agent support
- **[Bug Report](ISSUE_TEMPLATE/bug_report.md)** - Report bugs in the toolkit
- **[Feature Request](ISSUE_TEMPLATE/feature_request.md)** - Request new features

> ⚠️ **Important**: Do not file empty issue templates. See [How to Write Good Enhancement Issues](AI_DEVELOPMENT_INDEX.md#filing-enhancement-requests).

## 🔧 Quick Command Reference

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v --cov=scripts --cov=src

# Format code
black --line-length 120 scripts/ src/

# Lint code
flake8 scripts/ src/ --max-line-length 120

# Run Python script
python scripts/my_script.py --help

# Run PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/MyScript.ps1"
```

## 📖 Documentation Philosophy

This project is built with **AI-first development** in mind:

1. **Comprehensive Patterns**: Every common task has documented patterns
2. **Copy-Paste Ready**: Examples are production-ready, not pseudocode
3. **Error Handling**: Common pitfalls are documented with solutions
4. **Testing Focus**: Every pattern includes testing examples
5. **Quick Navigation**: Multiple entry points for different needs

## 🎓 Learning Paths

### For Python Developers (55 min)
1. [AI Agent Quick Start → Python Tasks](AI_AGENT_QUICKSTART.md#task-1-add-a-new-python-script)
2. [Workflow Testing → File I/O Tests](AI_WORKFLOW_TESTING.md#pattern-1-testing-python-scripts-with-file-io)
3. [Copilot Instructions → Full Reference](copilot-instructions.md)

### For PowerShell Developers (50 min)
1. [AI Agent Quick Start → PowerShell Functions](AI_AGENT_QUICKSTART.md#task-2-add-a-new-powershell-function-to-m365cis-module)
2. [Copilot Instructions → PowerShell Patterns](copilot-instructions.md#powershell-module-pattern)

### For MCP Tool Developers (80 min)
1. [MCP Patterns → Architecture](MCP_TOOL_PATTERNS.md#mcp-architecture-in-this-project)
2. [MCP Patterns → All Patterns](MCP_TOOL_PATTERNS.md#mcp-tool-structure)
3. [Workflow Testing → Testing MCP Tools](AI_WORKFLOW_TESTING.md#pattern-5-testing-mcp-tools)

### For Test Engineers (60 min)
1. [Workflow Testing → Quick Start](AI_WORKFLOW_TESTING.md#quick-start-testing-workflow)
2. [Workflow Testing → All Patterns](AI_WORKFLOW_TESTING.md#writing-tests-for-new-code)

## 🆘 Getting Help

- **Quick Questions**: Check [AI Agent Quick Start](AI_AGENT_QUICKSTART.md#when-things-go-wrong)
- **Testing Issues**: See [Workflow Testing: Troubleshooting](AI_WORKFLOW_TESTING.md#troubleshooting-test-failures)
- **Architecture Questions**: Read [Copilot Instructions](copilot-instructions.md)
- **File an Issue**: Use [AI Development Enhancement template](ISSUE_TEMPLATE/ai_development.md)

## 📊 Documentation Quality

- ✅ **Onboarding Time**: <15 minutes for common tasks
- ✅ **Code Examples**: Every pattern has working examples
- ✅ **Test Coverage**: All patterns have test examples
- ✅ **Error Handling**: Common errors documented with solutions
- ✅ **Cross-Referenced**: Easy navigation between related topics

---

**🤖 These resources ensure AI agents can quickly understand and contribute to the M365 Security & SharePoint Analysis Toolkit!**

For the complete navigation guide, see [AI Development Index](AI_DEVELOPMENT_INDEX.md).
