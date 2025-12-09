# Copilot Toolbox

A secure, lightweight CLI toolkit for Copilot agents and contributors to discover repository assets, surface agent prompts, and run workspace health checks.

## Overview

The Copilot Toolbox provides three core commands to help agents and developers quickly understand and navigate the repository structure:

1. **`list-docs`** - List all documentation files in `docs/` and `.github/`
2. **`show-agent-prompts`** - Display summaries of agent prompt files in `.github/agents/`
3. **`check-workspace`** - Verify key files exist and report workspace health status

## Installation

The toolbox is included with the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Commands

Run any command using Python's module execution:

```bash
# List documentation files
python -m scripts.copilot_tools list-docs

# Show agent prompts
python -m scripts.copilot_tools show-agent-prompts

# Check workspace health
python -m scripts.copilot_tools check-workspace
```

### Output Formats

All commands support both text (human-readable) and JSON (machine-readable) output formats:

```bash
# Human-readable text output (default)
python -m scripts.copilot_tools list-docs

# Machine-readable JSON output
python -m scripts.copilot_tools list-docs --format json
python -m scripts.copilot_tools show-agent-prompts --format json
python -m scripts.copilot_tools check-workspace --format json
```

### Verbose Logging

Enable verbose logging using the `COPILOT_TOOLBOX_VERBOSE` environment variable:

```bash
# Unix/Linux/macOS
COPILOT_TOOLBOX_VERBOSE=true python -m scripts.copilot_tools check-workspace

# Windows (PowerShell)
$env:COPILOT_TOOLBOX_VERBOSE="true"
python -m scripts.copilot_tools check-workspace

# Windows (CMD)
set COPILOT_TOOLBOX_VERBOSE=true
python -m scripts.copilot_tools check-workspace
```

## Command Details

### list-docs

Lists all documentation files in the `docs/` and `.github/` directories (excluding workflow files for cleaner output).

**Text output example:**
```
=== Documentation Files ===

docs/ (15 files):
  - API_REFERENCE.md
  - FAQ.md
  - README.md
  - SECURITY_M365_CIS.md
  ...

.github/ (8 files, excluding workflows/):
  - AI_AGENT_QUICKSTART.md
  - AI_DEVELOPMENT_INDEX.md
  - COPILOT_INSTRUCTIONS_VALIDATION.md
  ...
```

**JSON output example:**
```json
{
  "docs": [
    "API_REFERENCE.md",
    "FAQ.md",
    "README.md"
  ],
  "github": [
    "AI_AGENT_QUICKSTART.md",
    "AI_DEVELOPMENT_INDEX.md"
  ]
}
```

### show-agent-prompts

Displays summaries of agent prompt files in `.github/agents/`, extracting the first meaningful description from each file.

**Text output example:**
```
=== Agent Prompts ===

Found 3 agent prompt(s):

📄 code-quality.patrol_agent.md
   Path: .github/agents/code-quality.patrol_agent.md
   Summary: Provides code quality and security improvements.
   Lines: 45

📄 my-agent.agent.md
   Path: .github/agents/my-agent.agent.md
   Summary: Reviews code for quality, security risks, and performance
   Lines: 68
```

**JSON output example:**
```json
{
  "agents": {
    "code-quality.patrol_agent.md": {
      "file": ".github/agents/code-quality.patrol_agent.md",
      "summary": "Provides code quality and security improvements.",
      "lines": 45
    },
    "my-agent.agent.md": {
      "file": ".github/agents/my-agent.agent.md",
      "summary": "Reviews code for quality, security risks, and performance",
      "lines": 68
    }
  },
  "count": 2
}
```

### check-workspace

Verifies that key repository files and directories exist, providing a health score and detailed status report.

**Checks performed:**
- `README.md` - Repository documentation
- `docs/` - Documentation directory
- `.github/workflows/` - CI/CD workflows
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules
- `pyproject.toml` - Python project configuration

**Text output example:**
```
=== Workspace Health Check ===

Health Score: 100.0% (6/6 checks passed)

✅ README.md
✅ docs/
   └─ 20 documentation file(s)
✅ .github/workflows/
   └─ 15 workflow file(s)
✅ requirements.txt
✅ .gitignore
✅ pyproject.toml

✨ Workspace is healthy! All critical files are present.
```

**JSON output example:**
```json
{
  "health_score": 100.0,
  "passed": 6,
  "total": 6,
  "checks": {
    "README.md": {
      "exists": true,
      "path": "README.md",
      "type": "file"
    },
    "docs/": {
      "exists": true,
      "path": "docs",
      "type": "directory",
      "file_count": 20
    },
    ".github/workflows/": {
      "exists": true,
      "path": ".github/workflows",
      "type": "directory",
      "workflow_count": 15
    }
  }
}
```

## Security & Design Principles

### Security Features

1. **No Secret Exposure**: The toolbox never prints sensitive environment variables or secrets
2. **Structured Logging**: All logging goes to stderr with structured format, avoiding accidental secret leakage
3. **Read-Only Operations**: All commands are read-only; no files are modified
4. **Path Safety**: Uses `pathlib` for safe path handling and traversal
5. **Input Validation**: All inputs are validated and sanitized

### Design Principles

1. **Zero External Dependencies**: Uses only Python standard library (except for testing)
2. **Synchronous Operations**: No async complexity; deterministic execution
3. **No Network Calls**: All operations are local filesystem reads
4. **Structured Output**: JSON format for programmatic use, text format for humans
5. **Graceful Degradation**: Missing files/directories are reported but don't cause failures

## Testing

Run the test suite:

```bash
# Run all copilot toolbox tests
pytest tests/test_copilot_toolbox.py -v

# Run with coverage
pytest tests/test_copilot_toolbox.py --cov=scripts.copilot_tools --cov-report=html
```

## CI/CD Integration

The toolbox includes automated testing via GitHub Actions. See `.github/workflows/copilot-tools-ci.yml` for the CI configuration.

The CI pipeline runs:
- **Linting**: flake8 for code quality
- **Security Scanning**: bandit for security issues, pip-audit for dependency vulnerabilities
- **Testing**: pytest with coverage reporting

## For Copilot Agents

When using this toolbox in agent workflows:

1. **Start with `check-workspace`** to verify the repository structure is healthy
2. **Use `list-docs`** to discover available documentation
3. **Use `show-agent-prompts`** to understand available agent capabilities
4. **Always use `--format json`** for programmatic parsing
5. **Parse JSON output** for reliable, structured data access

Example agent workflow:

```bash
# Check workspace health
python -m scripts.copilot_tools check-workspace --format json | jq '.health_score'

# Get list of documentation files
python -m scripts.copilot_tools list-docs --format json | jq -r '.docs[]'

# Get available agent prompts
python -m scripts.copilot_tools show-agent-prompts --format json | jq -r '.agents | keys[]'
```

## Future Enhancements (TODOs)

- [ ] Add semantic code search integration (using embeddings for intelligent doc search)
- [ ] Create MCP server hooks for direct agent integration
- [ ] Auto-generate README sections from discovered documentation
- [ ] Add support for filtering docs by category/tags
- [ ] Include dependency version checking in workspace health
- [ ] Add report generation for missing/outdated documentation
- [ ] Support custom workspace check configurations
- [ ] Add interactive mode for guided repository exploration

## Contributing

When adding new commands:

1. Add function to `scripts/copilot_tools/__main__.py`
2. Add corresponding tests to `tests/test_copilot_toolbox.py`
3. Update this documentation with usage examples
4. Ensure security principles are followed (no secrets, structured logging)
5. Add type hints and docstrings
6. Verify CI passes all checks

## License

This toolbox is part of the Easy-Ai project and follows the same license terms.
