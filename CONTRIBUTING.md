# Contributing to Share Report M365 Security Toolkit

Thank you for your interest in contributing to the Share Report M365 Security Toolkit! This document provides guidelines for contributing to the project.

## 🧠 AI-Assisted Development

**For AI coding agents**: Please read [`.github/copilot-instructions.md`](.github/copilot-instructions.md) first for comprehensive project context, architecture patterns, and development workflows specific to this hybrid Python/PowerShell enterprise security toolkit.

## 🌳 Git Branch Strategy

**Before contributing**: Read [`docs/GIT_BRANCH_STRATEGY.md`](docs/GIT_BRANCH_STRATEGY.md) to understand our Git Flow workflow.

**Quick Reference**:

- Start features from `develop` branch
- Use `feature/*` naming for new features
- Use `copilot/*` naming for AI-generated code
- Create PRs to `develop` branch (not `main`)
- `main` branch is for production releases only

## Table of Contents

- [AI-Assisted Development](#ai-assisted-development)
- [Git Branch Strategy](#git-branch-strategy)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PowerShell 7.0 or higher (for PowerShell scripts)
- Git

### Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Heyson315/Easy-Ai.git
   cd Easy-Ai
   ```

2. **Checkout develop branch**

   ```bash
   git checkout develop
   git pull origin develop
   ```

   ```

2. **Install Python dependencies**

   ```bash
   # Production dependencies
   pip install -r requirements.txt

   # Development dependencies (includes testing and linting tools)
   pip install -r requirements-dev.txt
   ```

3. **Install PowerShell modules** (if working with PowerShell scripts)

   ```powershell
   Install-Module ExchangeOnlineManagement -Scope CurrentUser
   Install-Module Microsoft.Graph -Scope CurrentUser
   Install-Module Microsoft.Graph.DeviceManagement -Scope CurrentUser
   Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
   Install-Module PSScriptAnalyzer -Scope CurrentUser
   ```

4. **Verify installation**

   ```bash
   # Run tests
   pytest

   # Check code quality
   pylint scripts/ src/
   flake8 scripts/ src/ tests/
   black --check scripts/ src/ tests/
   ```

## Code Style Guidelines

### Python Code Style

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length:** Maximum 120 characters
- **Formatting:** Use [Black](https://black.readthedocs.io/) for automatic formatting
- **Linting:** Use [Pylint](https://pylint.org/) and [Flake8](https://flake8.pycqa.org/) for code quality checks
- **Type hints:** Use type hints for function signatures

**Example:**

```python
from typing import Dict, List
from pathlib import Path

def process_data(input_path: Path, options: Dict[str, str]) -> List[Dict[str, any]]:
    """
    Process data from input file.

    Args:
        input_path: Path to input file
        options: Processing options

    Returns:
        List of processed data dictionaries
    """
    # Implementation here
    pass
```

### PowerShell Code Style

- Follow [PowerShell best practices](https://poshcode.gitbook.io/powershell-practice-and-style/)
- Use **PascalCase** for function names
- Use **approved verbs** (Get-, Set-, New-, etc.)
- Include **comment-based help** for all functions
- Use **PSScriptAnalyzer** for linting

**Example:**

```powershell
<#
.SYNOPSIS
    Gets M365 security audit results.
.DESCRIPTION
    Retrieves security audit results from Microsoft 365 tenant.
.PARAMETER TenantId
    The tenant ID to audit
.EXAMPLE
    Get-M365AuditResults -TenantId "contoso.onmicrosoft.com"
#>
function Get-M365AuditResults {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$TenantId
    )
    # Implementation here
}
```

## Testing

### Python Tests

We use [pytest](https://pytest.org/) for Python testing.

**Running tests:**

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=scripts --cov=src --cov-report=html

# Run specific test file
pytest tests/test_clean_csv.py

# Run specific test
pytest tests/test_clean_csv.py::test_clean_csv_basic
```

**Writing tests:**

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested

**Example:**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.clean_csv import clean_csv

def test_clean_csv_removes_comments():
    """Test that clean_csv removes comment lines starting with #"""
    with TemporaryDirectory() as td:
        td = Path(td)
        input_file = td / "input.csv"
        output_file = td / "output.csv"

        input_file.write_text("# Comment\nHeader\nData", encoding="utf-8")
        stats = clean_csv(input_file, output_file)

        assert stats["comment_lines"] == 1
        assert stats["output_rows"] == 1
```

### PowerShell Tests

Use [Pester](https://pester.dev/) for PowerShell testing.

```powershell
# Run all Pester tests
Invoke-Pester

# Run specific test file
Invoke-Pester -Path tests/M365CIS.Tests.ps1
```

## Submitting Changes

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Commit Message Guidelines

- Use clear, descriptive commit messages
- Start with a verb in present tense (Add, Fix, Update, etc.)
- Keep the first line under 72 characters
- Add detailed description if needed

**Good examples:**

```
Add error handling to m365_cis_report.py

Fix JSON parsing issue in dashboard generator

Update README with new installation instructions
```

### Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**

   ```bash
   # Format code
   black scripts/ src/ tests/

   # Run linter
   pylint scripts/ src/

   # Run tests
   pytest

   # Check type hints
   mypy scripts/ src/
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all CI checks pass
   - Request review from maintainers

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated for changes
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No linting errors
- [ ] Code reviewed by at least one maintainer

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Clear title** describing the issue
- **Steps to reproduce** the bug
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, PowerShell version)
- **Error messages** or logs (if applicable)

**Example:**

```markdown
### Bug: Dashboard generation fails with malformed JSON

**Steps to reproduce:**
1. Run audit: `Invoke-M365CISAudit.ps1 -Timestamped`
2. Generate dashboard: `python scripts/generate_security_dashboard.py`
3. Error occurs

**Expected:** Dashboard should be generated
**Actual:** JSONDecodeError thrown

**Environment:**
- OS: Windows 11
- Python: 3.10.5
- Error: `json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
```

### Feature Requests

When requesting features, please include:

- **Clear description** of the feature
- **Use case** explaining why it's needed
- **Proposed solution** (if you have one)
- **Alternatives considered**

## Code Review Process

All submissions require review. Reviewers will check:

- Code quality and adherence to style guidelines
- Test coverage
- Documentation completeness
- Security considerations
- Performance implications

## Questions?

If you have questions about contributing:

- Open an issue with your question
- Tag it with the `question` label
- We'll respond as soon as possible

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to the Share Report M365 Security Toolkit! 🎉
