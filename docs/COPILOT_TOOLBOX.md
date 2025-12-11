# Copilot Tools Toolbox

A secure, lightweight toolkit to help AI agents (Copilot, Claude, ChatGPT) and contributors discover repository assets, understand project structure, and run workspace health checks.

## Overview

The Copilot Tools Toolbox provides three core functions:

1. **`list-docs`** - Discover documentation files across the repository
2. **`show-prompts`** - Surface AI agent configuration and instruction files
3. **`check-workspace`** - Run basic health checks on the workspace

All outputs are JSON-formatted for easy consumption by automation tools and AI agents.

## Installation

No additional dependencies required! The toolbox uses Python standard library only.

```bash
# Already available if you have the repository
# No pip install needed
```

## Usage

### Command Line Interface

The toolbox can be used as a Python module with three commands:

```bash
# List all documentation files
python -m scripts.copilot_tools list-docs

# Show agent configuration files
python -m scripts.copilot_tools show-prompts

# Run workspace health check
python -m scripts.copilot_tools check-workspace

# Optional: Specify custom repository root
python -m scripts.copilot_tools list-docs --root /path/to/repo

# Optional: Pretty-print JSON for human readability
python -m scripts.copilot_tools list-docs --pretty
```

### Python API

Import and use functions directly in your Python code:

```python
from pathlib import Path
from scripts.copilot_tools import list_docs, show_agent_prompts, check_workspace

# Get repository root
repo_root = Path('/path/to/repository')

# List documentation files
docs = list_docs(repo_root)
print(f"Found {docs['count']} documentation files")
for doc in docs['docs']:
    print(f"  - {doc['name']}: {doc['path']}")

# Show agent prompts
prompts = show_agent_prompts(repo_root)
for prompt in prompts['prompts']:
    print(f"Agent file: {prompt['path']}")

# Check workspace health
health = check_workspace(repo_root)
print(f"Workspace status: {health['status']}")
if health['recommendations']:
    print("Recommendations:")
    for rec in health['recommendations']:
        print(f"  - {rec}")
```

## Command Reference

### `list-docs`

Discovers documentation files in common locations (docs/, .github/, root-level *.md).

**Output Structure:**
```json
{
  "docs": [
    {
      "name": "README.md",
      "path": "README.md",
      "type": "MD",
      "size_bytes": 1234
    }
  ],
  "count": 42,
  "directories": ["docs", "docs/api", ".github"]
}
```

**Supported Formats:** `.md`, `.rst`, `.txt`, `.adoc`

### `show-prompts`

Surfaces AI agent configuration files like copilot-instructions.md, agent-config.json, and AI-related documentation.

**Output Structure:**
```json
{
  "prompts": [
    {
      "name": "copilot-instructions.md",
      "path": ".github/copilot-instructions.md",
      "type": "Agent Instructions",
      "size_bytes": 5678
    }
  ],
  "count": 3,
  "locations": [".github", "docs"]
}
```

**Detection Methods:**
- Filename patterns: `copilot-*`, `ai-*`, `agent-*`
- Content detection: Files mentioning "copilot", "ai agent", "prompt"

### `check-workspace`

Runs lightweight health checks on the workspace to ensure it's ready for development.

**Output Structure:**
```json
{
  "status": "healthy",
  "summary": "Workspace appears healthy",
  "checks": [
    {
      "name": "Git Repository",
      "status": "pass",
      "message": "Valid git repository"
    },
    {
      "name": "Python Requirements",
      "status": "pass",
      "message": "Found 3 requirements file(s): requirements.txt, requirements-dev.txt, requirements-extensions.txt",
      "details": ["requirements.txt", "requirements-dev.txt", "requirements-extensions.txt"]
    }
  ],
  "recommendations": []
}
```

**Checks Performed:**
- ✅ Git repository (`.git` directory exists)
- ✅ Python requirements files present
- ✅ Key directories exist (scripts, tests, docs, src, .github)
- ✅ Python virtual environment detected
- ✅ Configuration files found (pyproject.toml, .flake8, etc.)
- ✅ CI/CD workflows present

**Status Values:**
- `healthy` - All checks pass
- `warning` - Some warnings but functional
- `error` - Critical issues found

## Security Features

The toolbox is designed with security as a priority:

### 🔒 No Secret Exposure
- **Environment files** (`.env`, `.env.*`) are automatically excluded
- **Sensitive directories** (`.git`, `__pycache__`, `.venv`) are skipped
- **Structured logging** prevents accidental secret exposure

### 🛡️ Safe Path Validation
All file operations validate that paths:
- Stay within the repository boundary
- Don't access sensitive system directories
- Skip hidden and cache directories

### 📝 Secure Logging
The `COPILOT_TOOLBOX_VERBOSE` environment variable can enable verbose logging:
```bash
export COPILOT_TOOLBOX_VERBOSE=true
python -m scripts.copilot_tools check-workspace
```

Verbose mode adds non-sensitive metadata (Python version, platform) but never logs:
- Environment variable values
- File contents
- Credentials or tokens

## Use Cases

### For AI Agents (Copilot, Claude, ChatGPT)

**Scenario 1: Understanding Repository Structure**
```bash
# Agent: "What documentation is available?"
python -m scripts.copilot_tools list-docs --pretty

# Response: Complete list of docs with paths and types
```

**Scenario 2: Finding Configuration**
```bash
# Agent: "Where are the agent instructions?"
python -m scripts.copilot_tools show-prompts

# Response: All agent-related configuration files
```

**Scenario 3: Pre-flight Check**
```bash
# Agent: "Is the workspace ready?"
python -m scripts.copilot_tools check-workspace

# Response: Health status with recommendations
```

### For Contributors

**Before starting work:**
```bash
# Check workspace health
python -m scripts.copilot_tools check-workspace --pretty

# Find relevant documentation
python -m scripts.copilot_tools list-docs
```

**During development:**
```bash
# Verify CI setup
python -m scripts.copilot_tools check-workspace | jq '.checks[] | select(.name == "CI/CD Workflows")'
```

### For Automation/CI

**In GitHub Actions:**
```yaml
- name: Workspace Health Check
  run: |
    python -m scripts.copilot_tools check-workspace > workspace-status.json
    
    # Parse and act on status
    STATUS=$(jq -r '.status' workspace-status.json)
    if [ "$STATUS" == "error" ]; then
      echo "Workspace health check failed"
      exit 1
    fi
```

## Design Decisions

### Why Standard Library Only?
- **Zero dependencies** - Works immediately without pip install
- **Fast execution** - No import overhead from large libraries
- **Universal compatibility** - Works with any Python 3.8+ environment

### Why JSON Output?
- **Machine-readable** - Easy parsing for automation
- **Language-agnostic** - Can be consumed by any tool (bash, node, etc.)
- **Structured** - Consistent format across all commands

### Why These Three Commands?
Based on common agent workflows:
1. **Discovery phase** - What docs exist? (`list-docs`)
2. **Context gathering** - How should I behave? (`show-prompts`)
3. **Safety check** - Is workspace ready? (`check-workspace`)

## Future Enhancements (TODOs)

### Planned Features
- [ ] **Semantic code search** - Integrate with vector databases for code search
- [ ] **MCP server integration** - Expose as Model Context Protocol tools
- [ ] **README generation** - Auto-generate repo summaries
- [ ] **Dependency graph** - Visualize project dependencies
- [ ] **Code quality metrics** - Integration with coverage/lint reports
- [ ] **Performance profiling** - Track command execution times

### Integration Opportunities
- **GitHub Copilot** - Use in `.github/copilot-instructions.md`
- **VS Code Extensions** - Command palette integration
- **Pre-commit hooks** - Validate workspace before commits
- **Documentation generators** - Auto-update docs based on scanning

### Advanced Use Cases
- **Multi-repo analysis** - Scan multiple repositories
- **Diff detection** - Compare workspace state between runs
- **Custom checks** - Plugin system for domain-specific validations

## Contributing

The toolbox follows the repository's standard contribution guidelines.

**Adding new checks:**
1. Add check logic to `check_workspace()` in `__init__.py`
2. Add tests to `test_copilot_toolbox.py`
3. Update this documentation

**Adding new commands:**
1. Create new function in `__init__.py`
2. Add CLI argument in `__main__.py`
3. Write comprehensive tests
4. Document usage and output format

## Testing

Run the test suite:
```bash
# Run all toolbox tests
pytest tests/test_copilot_toolbox.py -v

# Run with coverage
pytest tests/test_copilot_toolbox.py --cov=scripts.copilot_tools --cov-report=html

# Run security checks
bandit -r scripts/copilot_tools
flake8 scripts/copilot_tools
pip-audit
```

## Troubleshooting

### Issue: "Module not found"
```bash
# Ensure PYTHONPATH includes repository root
export PYTHONPATH=/path/to/Easy-Ai:$PYTHONPATH
python -m scripts.copilot_tools list-docs
```

### Issue: "Permission denied"
The toolbox only reads files, never writes. If you see permission errors:
- Check file/directory permissions
- Ensure you have read access to the repository
- Run without sudo (not needed)

### Issue: "Empty results"
If commands return empty results:
- Verify you're running from correct directory
- Use `--root` to specify repository path explicitly
- Check that documentation/config files exist

## Examples

### Example 1: Generate Documentation Index
```bash
# Generate a JSON index of all docs
python -m scripts.copilot_tools list-docs > docs-index.json

# Convert to markdown
jq -r '.docs[] | "- [\(.name)](\(.path)) - \(.type)"' docs-index.json > DOCS_INDEX.md
```

### Example 2: Health Check in CI
```yaml
# .github/workflows/health-check.yml
name: Workspace Health
on: [push, pull_request]

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Check Workspace
        run: |
          python -m scripts.copilot_tools check-workspace --pretty
          
          # Fail on errors
          STATUS=$(python -m scripts.copilot_tools check-workspace | jq -r '.status')
          if [ "$STATUS" == "error" ]; then
            exit 1
          fi
```

### Example 3: Agent Context Loading
```python
# For AI agent to load context
from scripts.copilot_tools import list_docs, show_agent_prompts

# Load all agent instructions
prompts = show_agent_prompts(repo_root)
for prompt in prompts['prompts']:
    content = (repo_root / prompt['path']).read_text()
    agent.load_context(content)

# Discover available documentation
docs = list_docs(repo_root)
agent.set_available_docs(docs['docs'])
```

## License

Same as parent repository (MIT License).

## Support

- **Issues**: File on GitHub issue tracker
- **Questions**: See main repository README
- **Security concerns**: Follow repository security policy

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-09  
**Maintained by**: Easy-Ai Contributors
