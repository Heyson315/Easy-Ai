# Workflow Test Results Summary

**Date:** 2025-11-14  
**Repository:** Heyson315/share-report  
**Branch:** copilot/list-failing-workflows  

---

## Quick Summary

| Category | Total | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
| **Python Scripts** | 22 | 14 | 8 | 63.6% |
| **PowerShell Scripts** | 6 | 6 | 0 | 100% |
| **Python Modules** | 3 | 3 | 0 | 100% |
| **Documentation** | 3 | 3 | 0 | 100% |
| **Overall** | 34 | 26 | 8 | 76.5% |

---

## Critical Findings

### ✗ 8 Failures Identified

All failures are related to **missing pandas dependency**:

1. `inspect_cis_report.py` - imports fail
2. `inspect_processed_csv.py` - imports fail
3. `inspect_report.py` - imports fail
4. `m365_cis_report.py` - imports fail, help text fails
5. `run_performance_benchmark.py` - help text fails (chain dependency)
6. `sync_cis_csv.py` - imports fail, help text fails

### ✓ Key Successes

- **All PowerShell scripts** have valid syntax ✓
- **All documentation** is present and complete ✓
- **Core Python utilities** (`clean_csv.py`, `generate_security_dashboard.py`) work without external dependencies ✓
- **Module structure** is now correct (fixed missing `__init__.py`) ✓

---

## Resolution Required

To make all workflows pass:

```bash
pip install pandas>=1.3.0 openpyxl>=3.0.0
```

---

## Testing Artifacts

1. **Test Script:** `test_all_workflows.py` - Comprehensive workflow tester
2. **JSON Results:** `output/reports/workflow_test_results.json` - Machine-readable results
3. **Detailed Report:** `WORKFLOW_TEST_REPORT.md` - Full analysis with recommendations
4. **This Summary:** `WORKFLOW_TEST_SUMMARY.md` - Quick reference

---

## Next Steps

1. ✓ **Fixed:** Module structure issue (`src/core/__init__.py` created)
2. ⧗ **Pending:** Install pandas dependency (requires internet access or offline package)
3. ⧗ **Pending:** Run integration tests with M365 connectivity
4. ⧗ **Pending:** Execute unit test suite with pytest

---

## Test Command

```bash
python test_all_workflows.py
```

**Exit Code:** 1 (failures detected)

---

*For detailed failure analysis, see WORKFLOW_TEST_REPORT.md*
