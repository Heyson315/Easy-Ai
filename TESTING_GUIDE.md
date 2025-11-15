# How to Test All Workflows

This guide explains how to use the workflow testing tools in this repository.

## Quick Start

Run all workflow tests with a single command:

```bash
python test_all_workflows.py
```

This will:
- Test all Python scripts for syntax and dependencies
- Test all PowerShell scripts for syntax
- Validate Python module structure
- Check documentation completeness
- Generate detailed reports in `output/reports/`

## Test Output Files

After running tests, you'll find:

1. **Console Output** - Immediate feedback with ✓/✗ status
2. **workflow_test_results.json** - Machine-readable results in `output/reports/`
3. **WORKFLOW_TEST_REPORT.md** - Detailed analysis with recommendations
4. **WORKFLOW_TEST_SUMMARY.md** - Quick reference summary

## Understanding Test Results

### Test Categories

| Category | What's Tested |
|----------|---------------|
| **Python Scripts** | Syntax validation, import checks, help text availability |
| **PowerShell Scripts** | Syntax validation (requires PowerShell installed) |
| **Python Modules** | Structure validation (__init__.py presence, file syntax) |
| **Documentation** | File existence and completeness |

### Status Indicators

- **✓ PASS** - Test passed successfully
- **✗ FAIL** - Test failed, see reason for details
- **⊘ SKIP** - Test was skipped (e.g., file not found)

## Common Test Failures

### Missing Dependencies

If you see failures like:
```
✗ FAIL - Missing dependencies: pandas
```

**Solution:**
```bash
pip install -r requirements.txt
```

This installs:
- pandas>=1.3.0
- openpyxl>=3.0.0

### PowerShell Not Available

If PowerShell tests show:
```
✗ FAIL - PowerShell not available
```

**Solution:**
- **Windows:** PowerShell is pre-installed
- **Linux/Mac:** Install PowerShell Core
  ```bash
  # macOS
  brew install --cask powershell
  
  # Ubuntu/Debian
  wget https://aka.ms/install-powershell.sh
  bash install-powershell.sh
  ```

### Module Structure Issues

If you see:
```
✗ FAIL - Missing __init__.py
```

**Solution:**
```bash
touch src/<module_name>/__init__.py
```

## Test Script Features

The `test_all_workflows.py` script includes:

- ✓ **Comprehensive Coverage** - Tests all Python and PowerShell components
- ✓ **Dependency Detection** - Identifies missing external packages
- ✓ **Module Validation** - Checks Python package structure
- ✓ **Documentation Checks** - Verifies workflow documentation exists
- ✓ **JSON Export** - Generates machine-readable test results
- ✓ **Exit Codes** - Returns 0 on success, 1 if failures detected

## Interpreting Results

### Successful Run (Example)

```
================================================================================
SUMMARY
================================================================================
Total Tests: 34
✓ Passed: 34
✗ Failed: 0
⊘ Skipped: 0
```

All workflows are ready to use!

### Failed Run (Example)

```
================================================================================
SUMMARY
================================================================================
Total Tests: 34
✓ Passed: 26
✗ Failed: 8
⊘ Skipped: 0

FAILURES:
--------------------------------------------------------------------------------
  ✗ python_scripts/m365_cis_report.py:imports
    Reason: Missing dependencies: pandas
```

8 workflows need attention - see FAILURES section for details.

## Automated Testing

### In CI/CD Pipelines

Add to your GitHub Actions workflow:

```yaml
- name: Test All Workflows
  run: python test_all_workflows.py
```

### Pre-Commit Hook

Test before committing:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python test_all_workflows.py
exit $?
```

## Advanced Usage

### Test Individual Components

You can modify `test_all_workflows.py` to test specific components:

```python
# Test only Python scripts
tester = WorkflowTester()
# Comment out unwanted test sections in run_all_tests()
tester.run_all_tests()
```

### Custom Test Reports

Generate custom reports from the JSON output:

```python
import json

with open('output/reports/workflow_test_results.json') as f:
    results = json.load(f)

# Filter for failures only
failures = {
    k: v for k, v in results['python_scripts'].items()
    if isinstance(v, dict) and v.get('passed') == False
}
print(f"Found {len(failures)} Python script failures")
```

## Troubleshooting

### Tests Hang or Timeout

- Increase timeout values in `test_all_workflows.py`
- Check for interactive prompts in tested scripts

### False Positives

- Some scripts may require specific input files
- Review individual test logic in the script

### Permission Errors

- Ensure execute permissions: `chmod +x test_all_workflows.py`
- Run with appropriate user permissions

## Next Steps After Testing

1. **Fix Failures** - Install dependencies, fix syntax errors
2. **Re-test** - Run `python test_all_workflows.py` again
3. **Integration Testing** - Test with real M365 connections
4. **Unit Tests** - Run full test suite: `pytest tests/`

## Support

For issues with the testing framework:
1. Check this guide for common solutions
2. Review test output in `output/reports/workflow_test_results.json`
3. See detailed analysis in `WORKFLOW_TEST_REPORT.md`

---

**Note:** This testing framework validates syntax and structure. For full workflow validation, you'll need:
- M365 admin access for PowerShell scripts
- Actual data files for processing scripts
- Complete test coverage via pytest
