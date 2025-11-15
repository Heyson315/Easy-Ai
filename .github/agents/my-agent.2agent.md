---
name: killa
description: Agent description here
---

# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config
# My Agent

This agent assists with development of the M365 Security & SharePoint Analysis Toolkit. It understands the hybrid Python/PowerShell architecture, project conventions, and common development patterns. See the complete guide below for detailed usage instructions.
.github/copilot-instructions.md
# 🤖 AI Agent Quick Start Guide

**Last Updated**: 2025-11-12

This guide is specifically for AI coding agents (GitHub Copilot, Claude, ChatGPT, etc.) to quickly understand and contribute to the M365 Security & SharePoint Analysis Toolkit.

---

## 🎯 Essential Reading (Read First!)

Before starting any task, **read these in order**:

1. **[Copilot Instructions](.github/copilot-instructions.md)** ⭐ **MOST IMPORTANT**
   - Complete project architecture
   - Critical workflows and data pipelines
   - Project-specific conventions
   - Common pitfalls and solutions

2. **[README.md](../README.md)** - Project overview and features

3. **[This Guide](#common-ai-agent-tasks)** - Task-specific patterns below

---

## 🏗️ Project Architecture at a Glance

```
Hybrid Python/PowerShell Toolkit
├── PowerShell → M365 Services → Raw JSON/CSV (output/reports/security/)
├── Python Scripts → CSV Cleaning → Processed Data (data/processed/)
└── Python Modules (src/) → Excel Reports + HTML Dashboards (output/reports/business/)
```

**Key Directories:**
- `scripts/` - Standalone utilities (Python + PowerShell)
- `scripts/powershell/modules/M365CIS.psm1` - Core audit functions (483+ lines)
- `src/core/` - Excel generation
- `src/integrations/` - SharePoint connector
- `tests/` - pytest-based tests
- `docs/` - Comprehensive documentation

---

## 🚀 Common AI Agent Tasks

### Task 1: Add a New Python Script

**Pattern:**
```python
#!/usr/bin/env python
"""
Brief description of what this script does.

Usage:
    python scripts/my_script.py --input "data/input.csv" --output "output/result.csv"
"""
from pathlib import Path
import sys

# Constants at top
DEFAULT_INPUT = Path("data/raw/input.csv")
DEFAULT_OUTPUT = Path("output/reports/result.csv")

def main():
    """Main entry point."""
    # Ensure output directory exists
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Your logic here
    pass

if __name__ == "__main__":
    main()
```

**Key Conventions:**
- ❌ Don't use `python -m scripts.my_script` → ✅ Use `python scripts/my_script.py`
- Use `pathlib.Path` for file paths
- Create output directories with `.parent.mkdir(parents=True, exist_ok=True)`
- Use specific exceptions: `json.JSONDecodeError`, `PermissionError`, not generic `Exception`

**Testing Pattern:**
```python
# tests/test_my_script.py
from tempfile import TemporaryDirectory
from pathlib import Path
import pandas as pd
from scripts.my_script import my_function

def test_my_function():
    with TemporaryDirectory() as td:
        td = Path(td)
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Write test input
        input_file.write_text("test,data\n1,2", encoding="utf-8")
        
        # Run function
        result = my_function(input_file, output_file)
        
        # Validate output
        assert output_file.exists()
        df = pd.read_csv(output_file)
        assert df.shape[0] > 0
```

---

### Task 2: Add a New PowerShell Function to M365CIS Module

**Pattern:**
```powershell
# In scripts/powershell/modules/M365CIS.psm1

function Test-CIS-X.Y.Z {
    <#
    .SYNOPSIS
    Brief description of control
    
    .DESCRIPTION
    Detailed description
    
    .EXAMPLE
    Test-CIS-X.Y.Z
    #>
    try {
        # Your test logic
        $actual = Get-SomeM365Config
        $expected = "Required Value"
        $status = if ($actual -eq $expected) { "Pass" } else { "Fail" }
        
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control Title" `
            -Severity "Medium" `
            -Expected $expected `
            -Actual $actual `
            -Status $status `
            -Evidence "Detailed evidence" `
            -Reference "https://docs.microsoft.com/..."
    }
    catch {
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control Title" `
            -Severity "Medium" `
            -Expected "N/A" `
            -Actual "Error: $($_.Exception.Message)" `
            -Status "Manual" `
            -Evidence "Error occurred" `
            -Reference "https://docs.microsoft.com/..."
    }
}
```

**Key Conventions:**
- Prefix: `Test-CIS-*` for audit functions
- Always return `New-CISResult` PSCustomObject
- Wrap in try/catch returning `Status='Manual'` on error
- Use absolute paths resolved from repo root

---

### Task 3: Process CSV with Special Characters

**Problem:** SharePoint exports have UTF-8 BOM, comments, blank lines, repeated headers.

**Solution:** Always use `scripts/clean_csv.py` first:

```python
from scripts.clean_csv import clean_csv
from pathlib import Path

# Clean the raw CSV
stats = clean_csv(
    input_path=Path("data/raw/sharepoint/export.csv"),
    output_path=Path("data/processed/clean.csv")
)

print(f"Removed {stats['comment_lines']} comments")
print(f"Output {stats['output_rows']} clean rows")
```

**Pattern inside clean_csv:**
```python
# Read with UTF-8 BOM handling
content = input_path.read_text(encoding='utf-8-sig')

# Filter out comments and blanks
lines = [line for line in content.splitlines() if line.strip() and not line.startswith('#')]

# Use csv.reader to preserve quoted commas
reader = csv.reader(lines)
```

---

### Task 4: Generate Excel Report with Formatting

**Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import pandas as pd

# Prepare data with pandas
df = pd.DataFrame(data)
summary = df.groupby('category').size().reset_index(name='count')

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Summary"

# Write headers
ws.append(list(summary.columns))
for col in range(1, len(summary.columns) + 1):
    cell = ws.cell(1, col)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    cell.alignment = Alignment(horizontal='center')

# Write data
for _, row in summary.iterrows():
    ws.append(list(row))

# Auto-size columns
for col in range(1, len(summary.columns) + 1):
    ws.column_dimensions[get_column_letter(col)].width = 15

# Save
output_path = Path("output/reports/business/report.xlsx")
output_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(output_path)
```

---

### Task 5: Run and Validate Your Changes

**Step-by-step:**

```bash
# 1. Run tests
cd /home/runner/work/share-report/share-report
python -m pytest tests/ -v --cov=scripts --cov=src

# 2. Run linters (if code changes)
black --check --line-length 120 scripts/ src/
flake8 scripts/ src/ --max-line-length 120

# 3. Test your specific script
python scripts/your_script.py --help
python scripts/your_script.py --input "test_data.csv"

# 4. Verify output files
ls -lh output/reports/

# 5. Check git status
git status
```

**Before committing:**
- ✅ All tests pass
- ✅ Linters pass (Black, flake8)
- ✅ Script runs without errors
- ✅ Output files generated correctly
- ✅ No unintended files staged (check .gitignore)

---

## 🧪 Testing Best Practices

### Use TemporaryDirectory for File I/O Tests

```python
from tempfile import TemporaryDirectory
from pathlib import Path

def test_file_processing():
    with TemporaryDirectory() as td:
        td = Path(td)
        # All file operations in td
        # Automatically cleaned up after test
```

### Validate with Pandas

```python
import pandas as pd

df = pd.read_csv(output_file)
assert df.shape == (expected_rows, expected_cols)
assert list(df.columns) == expected_columns
assert df.iloc[0]['column_name'] == expected_value
```

### Return Stats for Validation

```python
def process_data(input_path, output_path):
    # ... processing logic ...
    
    return {
        'input_rows': len(input_data),
        'output_rows': len(output_data),
        'errors': error_count
    }

# In test
stats = process_data(input_file, output_file)
assert stats['output_rows'] > 0
assert stats['errors'] == 0
```

---

## 🔧 Tool Configuration

### Black (Python Formatter)

```toml
# pyproject.toml
[tool.black]
line-length = 120
target-version = ['py38', 'py39', 'py310', 'py311']
```

**Usage:**
```bash
black --line-length 120 scripts/my_script.py
black --check scripts/  # Dry run
```

### Pytest (Testing)

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=scripts --cov=src"
```

**Usage:**
```bash
python -m pytest tests/ -v
python -m pytest tests/test_my_script.py -v
python -m pytest tests/ --cov-report=html  # Generate HTML coverage report
```

---

## 📋 Common Pitfalls (Must Read!)

### ❌ DON'T Do This

```python
# Generic exception handler
try:
    data = json.loads(file.read())
except Exception as e:  # Too broad!
    print(f"Error: {e}")

# Module execution for scripts
python -m scripts.my_script  # Scripts aren't a package!

# Hardcoded paths
output_path = "C:\\Users\\Me\\output.xlsx"  # Not portable!

# Assume clean CSV headers
df = pd.read_csv("raw_export.csv")  # Might have BOM, comments!
```

### ✅ DO This Instead

```python
# Specific exception handlers
try:
    data = json.loads(file.read_text(encoding='utf-8-sig'))
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)
except (PermissionError, UnicodeDecodeError) as e:
    print(f"Cannot read file: {e}", file=sys.stderr)
    sys.exit(1)

# Correct script execution
python scripts/my_script.py

# Portable paths
output_path = Path("output/reports/business/report.xlsx")
output_path.parent.mkdir(parents=True, exist_ok=True)

# Clean CSV first
from scripts.clean_csv import clean_csv
clean_csv(raw_path, clean_path)
df = pd.read_csv(clean_path)
```

---

## 🎯 Quick Reference Commands

```bash
# Setup
pip install -r requirements-dev.txt

# Testing
python -m pytest tests/ -v
python -m pytest tests/ --cov=scripts --cov=src --cov-report=html

# Linting
black --check --line-length 120 scripts/ src/
flake8 scripts/ src/ --max-line-length 120

# Run scripts (note: from repo root)
python scripts/clean_csv.py --input "data/raw/file.csv" --output "data/processed/clean.csv"
python -m src.integrations.sharepoint_connector --input "data/processed/clean.csv"

# PowerShell (note: absolute paths)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1" -Timestamped

# Git workflow
git status
git add .
git commit -m "Brief description of changes"
git push origin branch-name
```

---

## 🆘 When Things Go Wrong

### "Module not found" Error

```bash
# Ensure you're in repo root
cd /home/runner/work/share-report/share-report

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### "File not found" Error

```python
# Always check file exists
from pathlib import Path

input_path = Path("data/input.csv")
if not input_path.exists():
    print(f"ERROR: {input_path} not found")
    sys.exit(1)
```

### "CSV parsing error"

```bash
# Use clean_csv.py first!
python scripts/clean_csv.py --input "raw.csv" --output "clean.csv"

# Then process the clean CSV
python scripts/process_data.py --input "clean.csv"
```

---

## 📚 Additional Resources

- **[Copilot Instructions](.github/copilot-instructions.md)** - Complete project reference
- **[Contributing Guide](../../CONTRIBUTING.md)** - Development standards
- **[Scripts README](../../scripts/README.md)** - Script usage guide
- **[Documentation Index](../docs/README.md)** - All documentation

---

## 🎓 Learning Path for New AI Agents

1. **Start Here**: Read [Copilot Instructions](.github/copilot-instructions.md) (5 min)
2. **Understand Structure**: Review [Project Architecture](#project-architecture-at-a-glance) (2 min)
3. **Pick a Task**: Choose from [Common AI Agent Tasks](#common-ai-agent-tasks) (2 min)
4. **Follow the Pattern**: Copy-paste relevant code pattern (1 min)
5. **Test Your Work**: Run tests and linters (2 min)
6. **Review Pitfalls**: Check [Common Pitfalls](#common-pitfalls-must-read) (3 min)

**Total Time to Productivity: ~15 minutes**

---

**🤖 This guide helps AI agents contribute effectively to enterprise M365 security toolkit!**
