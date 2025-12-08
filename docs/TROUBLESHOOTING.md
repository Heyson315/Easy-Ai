# Troubleshooting Guide - M365 Security Toolkit

## Overview
This document provides solutions to common issues encountered when developing and running the M365 Security & SharePoint Analysis Toolkit.

---

## CI/CD Pipeline Issues

### 1. Black Formatting Failures

**Error**: `would reformat <file>` with exit code 1

**Cause**: Python code doesn't comply with black formatting standards

**Solution**:
```bash
# Auto-fix formatting issues
black scripts/ src/ tests/

# Check formatting without making changes
black --check scripts/ src/ tests/
```

**Prevention**: Run black before committing:
```bash
# Add to pre-commit hook or run manually
black scripts/ src/ tests/
git add -u
git commit -m "fix: Apply black formatting"
```

---

### 2. PowerShell Script Analyzer Warnings

**Error**: PSScriptAnalyzer reports warnings about Write-Host usage

**Cause**: Write-Host is flagged as a warning, but it's acceptable for user-facing scripts

**Solution**: Created `.PSScriptAnalyzerSettings.psd1` to suppress acceptable warnings:
- `PSAvoidUsingWriteHost` - Write-Host is intentional for console output
- `PSUseShouldProcessForStateChangingFunctions` - Not needed for read-only functions
- `PSUseBOMForUnicodeEncodedFile` - UTF-8 without BOM is standard

**Configuration**:
```powershell
# .PSScriptAnalyzerSettings.psd1 excludes acceptable warnings
Invoke-ScriptAnalyzer -Path "scripts/powershell/" -Settings ".PSScriptAnalyzerSettings.psd1" -Recurse
```

---

### 3. Missing Configuration Files

**Error**: Config files referenced in workflows don't exist

**Issue**: Missing `.markdownlint.json`, `.markdown-link-check.json`

**Solution**: Configuration files created with sensible defaults:

**.markdownlint.json**:
```json
{
  "default": true,
  "MD013": {"line_length": 120, "code_blocks": false, "tables": false},
  "MD033": false,
  "MD041": false,
  "MD046": false
}
```

**.markdown-link-check.json**:
```json
{
  "ignorePatterns": [
    {"pattern": "^http://localhost"},
    {"pattern": "^https://tenant"}
  ],
  "timeout": "10s",
  "retryOn429": true,
  "retryCount": 3
}
```

---

### 4. Integration Test Missing Sample Data

**Error**: `data/raw/sample_audit.json` not found during integration tests

**Solution**: Copy sample audit data to expected location:
```bash
cp data/external/m365_cis_sample.json data/raw/sample_audit.json
```

**Prevention**: Sample data is now committed to repository for CI/CD use.

---

## Python Development Issues

### 1. Module Import Errors

**Error**: `ModuleNotFoundError` when running scripts

**Cause**: Python path not configured or dependencies not installed

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# For development tools
pip install -r requirements-dev.txt

# Run scripts from repository root
cd /path/to/Easy-Ai
python scripts/script_name.py
```

---

### 2. CSV Processing Errors

**Error**: Quoted fields with commas not parsed correctly

**Cause**: SharePoint exports include UTF-8 BOM and special formatting

**Solution**: Use `clean_csv.py` before processing:
```bash
python scripts/clean_csv.py --input "data/raw/file.csv" --output "data/processed/clean.csv"
```

**Pattern**: Always clean SharePoint exports before analysis:
1. Remove BOM with `encoding='utf-8-sig'`
2. Filter comments and blank lines
3. Skip repeated headers
4. Use `csv.reader/writer` to preserve quoted commas

---

### 3. Dashboard Generation Errors

**Error**: Dashboard generation fails with JSON decode error

**Cause**: Invalid or missing JSON audit file

**Solution**:
```bash
# Validate JSON first
python -c "import json; json.load(open('audit.json'))"

# Generate dashboard with explicit paths
python scripts/generate_security_dashboard.py \
  --input "path/to/audit.json" \
  --output "path/to/dashboard.html"
```

---

## PowerShell Development Issues

### 1. Module Loading Errors

**Error**: `Import-Module` fails to load M365CIS.psm1

**Cause**: PowerShell module path not configured correctly

**Solution**:
```powershell
# Fix OneDrive PSModulePath if needed (replace 'YourCompany' with your organization name)
$env:PSModulePath += ";$env:USERPROFILE\OneDrive - YourCompany\Documents\WindowsPowerShell\Modules"

# Import with full path
Import-Module "./scripts/powershell/modules/M365CIS.psm1" -Force
```

---

### 2. Authentication Failures

**Error**: Connection errors when running audit scripts

**Cause**: Not authenticated to M365 services or missing permissions

**Solution**:
```powershell
# Connect with interactive auth (supports MFA)
Connect-M365CIS

# Required permissions:
# - Exchange Admin
# - Global Reader or Security Reader
# - SharePoint Admin (optional)

# Test connectivity
Test-MgGraph
Get-ConnectionInformation  # Exchange Online
```

---

### 3. Audit Script Errors

**Error**: Individual control checks return "Manual" status

**Cause**: Connection failures or missing PowerShell modules

**Solution**:
```powershell
# Install required modules
Install-Module Microsoft.Graph.Authentication -Scope CurrentUser
Install-Module ExchangeOnlineManagement -Scope CurrentUser
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser

# Verify modules are loaded
Get-Module -ListAvailable | Where-Object {$_.Name -like "*Graph*"}
```

---

## Git and Version Control Issues

### 1. Accidentally Committed Build Artifacts

**Error**: `.coverage`, `htmlcov/`, `__pycache__/` files in commits

**Solution**:
```bash
# Remove from git but keep locally
git rm --cached .coverage
git rm --cached -r htmlcov/
git rm --cached -r __pycache__/

# Update .gitignore
echo ".coverage" >> .gitignore
echo "htmlcov/" >> .gitignore
echo "__pycache__/" >> .gitignore

# Commit changes
git add .gitignore
git commit -m "chore: Update .gitignore to exclude build artifacts"
```

**Prevention**: Verify `.gitignore` includes:
```
.coverage
.coverage.*
htmlcov/
.pytest_cache/
__pycache__/
*.py[cod]
data/test/
```

---

### 2. Submodule Errors in CI

**Warning**: `fatal: No url found for submodule path 'Easy-Ai'`

**Cause**: Invalid submodule configuration (can be ignored if not using submodules)

**Solution**: If warning only (not failing builds), no action needed. If using submodules:
```bash
# Check submodule config
git config --file .gitmodules --get-regexp url

# Remove invalid submodule
git submodule deinit Easy-Ai
git rm Easy-Ai
git commit -m "Remove invalid submodule"
```

---

## Testing Issues

### 1. Test Failures After Code Changes

**Error**: Pytest assertions fail unexpectedly

**Cause**: Changes to data structures or logic

**Solution**:
```bash
# Run tests with verbose output
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_clean_csv.py::test_clean_csv_basic -v

# Check coverage
python -m pytest tests/ --cov=scripts --cov=src --cov-report=html
```

---

### 2. Performance Benchmark Failures

**Error**: Benchmark exceeds expected thresholds

**Cause**: System resources or data size variations

**Solution**:
```bash
# Run baseline benchmark
python scripts/run_performance_benchmark.py --baseline

# Validate against baseline
python scripts/run_performance_benchmark.py --validate-against-baseline
```

---

## Documentation Issues

### 1. Markdown Linting Failures

**Error**: markdownlint reports line length violations

**Solution**: Configure `.markdownlint.json` with appropriate limits:
```json
{
  "MD013": {
    "line_length": 120,
    "code_blocks": false,
    "tables": false
  }
}
```

---

### 2. Broken Links in Documentation

**Error**: markdown-link-check reports 404 errors

**Solution**: Use `.markdown-link-check.json` to ignore patterns:
```json
{
  "ignorePatterns": [
    {"pattern": "^http://localhost"},
    {"pattern": "^https://yourtenant"}
  ]
}
```
Note: Replace 'yourtenant' with patterns matching your environment (e.g., tenant-specific URLs).

---

## Best Practices

### Pre-Commit Checklist
1. ✅ Run black formatting: `black scripts/ src/ tests/`
2. ✅ Run linting: `flake8 scripts/ src/ tests/`
3. ✅ Run tests: `python -m pytest tests/ -v`
4. ✅ Check git status: `git status` (ensure no unwanted files)
5. ✅ Review changes: `git diff`

### Debugging Workflow
1. **Check logs**: Review GitHub Actions logs for specific errors
2. **Reproduce locally**: Run failing commands on local machine
3. **Isolate issue**: Test individual components
4. **Check dependencies**: Verify all required modules installed
5. **Validate data**: Ensure input files are correctly formatted

### Documentation Standards
- Keep README.md up to date with new features
- Document all new scripts in appropriate docs/ files
- Include usage examples in docstrings
- Update CHANGELOG.md with notable changes

---

## Getting Help

### Resources
- **Documentation**: `docs/` directory
- **GitHub Issues**: Report bugs and feature requests
- **Code Examples**: Check existing scripts for patterns
- **CI/CD Logs**: Review workflow runs for detailed error messages

### Common Commands Reference
```bash
# Python development
pip install -r requirements-dev.txt
black scripts/ src/ tests/
flake8 scripts/ src/ tests/
python -m pytest tests/ -v

# PowerShell development
Import-Module "./scripts/powershell/modules/M365CIS.psm1"
Invoke-ScriptAnalyzer -Path "scripts/powershell/" -Settings ".PSScriptAnalyzerSettings.psd1"

# CSV processing
python scripts/clean_csv.py --input "raw.csv" --output "clean.csv"

# Audit workflow
powershell -File "scripts/powershell/Invoke-M365CISAudit.ps1" -Timestamped
python scripts/m365_cis_report.py
python scripts/generate_security_dashboard.py
```

---

## Changelog of Fixes

### October 2025: CI/CD Configuration Issues
- Fixed black formatting in `tests/test_clean_csv.py`
- Created `.markdownlint.json` for markdown linting
- Created `.markdown-link-check.json` for link validation
- Created `.PSScriptAnalyzerSettings.psd1` to suppress acceptable PowerShell warnings
- Added `data/raw/sample_audit.json` for integration tests
- Updated `.gitignore` to exclude test artifacts (`.coverage`, `htmlcov/`, etc.)
- Updated CI workflow to use PSScriptAnalyzer settings file

**Result**: All CI/CD checks now pass successfully ✅
