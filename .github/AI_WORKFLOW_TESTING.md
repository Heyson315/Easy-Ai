# 🧪 AI Agent Workflow Testing Guide

**Last Updated**: 2025-11-12

This guide provides comprehensive testing strategies specifically for AI coding agents working on the M365 Security & SharePoint Analysis Toolkit.

---

## 🎯 Testing Philosophy

**Core Principle**: Every code change must be validated before committing.

### Testing Priorities

1. **Unit Tests** - Test individual functions in isolation
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Regression Tests** - Ensure existing functionality isn't broken
5. **Performance Tests** - Validate performance benchmarks

---

## 🚀 Quick Start Testing Workflow

### 1. Setup Test Environment

```bash
# From repository root
cd /home/runner/work/share-report/share-report

# Install test dependencies
pip install -r requirements-dev.txt

# Verify installation
python -m pytest --version
```

### 2. Run Existing Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=scripts --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_clean_csv.py -v

# Run specific test function
python -m pytest tests/test_clean_csv.py::test_clean_csv_basic -v
```

### 3. View Coverage Report

```bash
# Open HTML coverage report
firefox htmlcov/index.html  # Linux
start htmlcov/index.html     # Windows

# View in terminal
python -m pytest tests/ --cov=scripts --cov=src --cov-report=term
```

---

## 📝 Writing Tests for New Code

### Pattern 1: Testing Python Scripts with File I/O

**Example: Testing a CSV processing script**

```python
# tests/test_my_csv_processor.py
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
from scripts.my_csv_processor import process_csv

def test_process_csv_basic():
    """Test basic CSV processing functionality."""
    with TemporaryDirectory() as td:
        td = Path(td)
        
        # Setup test files
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Create test input
        test_data = "name,value\nAlice,100\nBob,200\n"
        input_file.write_text(test_data, encoding="utf-8")
        
        # Run the function
        stats = process_csv(input_file, output_file)
        
        # Validate return value
        assert stats['input_rows'] == 2
        assert stats['output_rows'] == 2
        assert stats['errors'] == 0
        
        # Validate output file
        assert output_file.exists()
        df = pd.read_csv(output_file)
        assert df.shape == (2, 2)
        assert list(df.columns) == ['name', 'value']
        assert df.iloc[0]['name'] == 'Alice'
        assert df.iloc[0]['value'] == 100

def test_process_csv_with_errors():
    """Test CSV processing with malformed data."""
    with TemporaryDirectory() as td:
        td = Path(td)
        
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Malformed CSV (missing value)
        test_data = "name,value\nAlice,100\nBob,\n"
        input_file.write_text(test_data, encoding="utf-8")
        
        # Should handle gracefully
        stats = process_csv(input_file, output_file)
        
        # Validate error handling
        assert stats['errors'] > 0 or stats['output_rows'] == 1
        assert output_file.exists()

def test_process_csv_empty_file():
    """Test CSV processing with empty file."""
    with TemporaryDirectory() as td:
        td = Path(td)
        
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Empty file
        input_file.write_text("", encoding="utf-8")
        
        # Should handle gracefully
        stats = process_csv(input_file, output_file)
        
        assert stats['input_rows'] == 0
        assert stats['output_rows'] == 0
```

### Pattern 2: Testing Excel Generation

```python
# tests/test_excel_generator.py
from pathlib import Path
from tempfile import TemporaryDirectory
from openpyxl import load_workbook
import pandas as pd
from src.core.excel_generator import generate_report

def test_generate_excel_report():
    """Test Excel report generation with formatting."""
    with TemporaryDirectory() as td:
        td = Path(td)
        output_file = td / "report.xlsx"
        
        # Test data
        data = {
            'category': ['A', 'B', 'A', 'C'],
            'value': [100, 200, 150, 300]
        }
        df = pd.DataFrame(data)
        
        # Generate report
        generate_report(df, output_file)
        
        # Validate file exists
        assert output_file.exists()
        
        # Validate workbook structure
        wb = load_workbook(output_file)
        assert 'Summary' in wb.sheetnames
        
        ws = wb['Summary']
        
        # Check headers
        assert ws.cell(1, 1).value == 'category'
        assert ws.cell(1, 2).value == 'value'
        
        # Check formatting
        assert ws.cell(1, 1).font.bold == True
        
        # Check data
        assert ws.cell(2, 1).value == 'A'
        assert ws.cell(2, 2).value == 100
        
        wb.close()

def test_generate_excel_multiple_sheets():
    """Test Excel report with multiple sheets."""
    with TemporaryDirectory() as td:
        td = Path(td)
        output_file = td / "report.xlsx"
        
        data = {'sheet1': pd.DataFrame({'a': [1, 2]}),
                'sheet2': pd.DataFrame({'b': [3, 4]})}
        
        generate_report(data, output_file)
        
        wb = load_workbook(output_file)
        assert len(wb.sheetnames) == 2
        assert 'sheet1' in wb.sheetnames
        assert 'sheet2' in wb.sheetnames
        wb.close()
```

### Pattern 3: Testing JSON Processing

```python
# tests/test_json_processor.py
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from scripts.process_audit_json import parse_audit_results

def test_parse_valid_json():
    """Test parsing valid audit JSON."""
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "audit.json"
        
        # Create test JSON
        test_data = {
            "controls": [
                {
                    "ControlId": "1.1.1",
                    "Status": "Pass",
                    "Severity": "High"
                },
                {
                    "ControlId": "1.1.2",
                    "Status": "Fail",
                    "Severity": "Medium"
                }
            ]
        }
        json_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        # Parse
        results = parse_audit_results(json_file)
        
        # Validate
        assert len(results) == 2
        assert results[0]['ControlId'] == "1.1.1"
        assert results[0]['Status'] == "Pass"

def test_parse_invalid_json():
    """Test parsing invalid JSON with proper error handling."""
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "audit.json"
        
        # Invalid JSON
        json_file.write_text("{invalid json", encoding="utf-8")
        
        # Should raise specific exception
        with pytest.raises(json.JSONDecodeError):
            parse_audit_results(json_file)

def test_parse_missing_file():
    """Test parsing non-existent file."""
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "nonexistent.json"
        
        # Should raise specific exception
        with pytest.raises(FileNotFoundError):
            parse_audit_results(json_file)
```

### Pattern 4: Testing Data Transformations

```python
# tests/test_data_transformer.py
import pandas as pd
from scripts.transform_data import aggregate_by_category, filter_high_risk

def test_aggregate_by_category():
    """Test data aggregation by category."""
    # Input data
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C', 'B'],
        'value': [10, 20, 15, 30, 25]
    })
    
    # Transform
    result = aggregate_by_category(df)
    
    # Validate
    assert result.shape == (3, 2)
    assert list(result.columns) == ['category', 'total']
    assert result[result['category'] == 'A']['total'].iloc[0] == 25
    assert result[result['category'] == 'B']['total'].iloc[0] == 45

def test_filter_high_risk():
    """Test filtering high-risk items."""
    df = pd.DataFrame({
        'item': ['Item1', 'Item2', 'Item3'],
        'risk_score': [85, 45, 92]
    })
    
    result = filter_high_risk(df, threshold=80)
    
    assert result.shape == (2, 2)
    assert 'Item1' in result['item'].values
    assert 'Item3' in result['item'].values
    assert 'Item2' not in result['item'].values
```

---

## 🔄 Integration Testing

### Testing Multi-Step Workflows

```python
# tests/test_sharepoint_workflow.py
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
from scripts.clean_csv import clean_csv
from src.integrations.sharepoint_connector import analyze_permissions

def test_complete_sharepoint_workflow():
    """Test complete SharePoint analysis workflow."""
    with TemporaryDirectory() as td:
        td = Path(td)
        
        # Step 1: Create raw SharePoint export (with issues)
        raw_file = td / "raw_export.csv"
        raw_data = """# Comment line
        
Resource Path,Permission,User Name
site1,Contribute,Alice
Resource Path,Permission,User Name
site2,Read,Bob
"""
        raw_file.write_text(raw_data, encoding="utf-8")
        
        # Step 2: Clean CSV
        clean_file = td / "clean.csv"
        stats = clean_csv(raw_file, clean_file)
        
        assert stats['output_rows'] == 2
        assert stats['comment_lines'] == 1
        
        # Step 3: Analyze permissions
        report_file = td / "report.xlsx"
        summary = analyze_permissions(clean_file, report_file)
        
        assert report_file.exists()
        assert summary['total_users'] == 2
        assert summary['total_sites'] == 2
```

---

## ⚡ Performance Testing

### Benchmark Testing Pattern

```python
# tests/test_performance.py
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
from scripts.process_large_csv import process_csv

def test_performance_small_dataset():
    """Test processing performance on small dataset (<1000 rows)."""
    with TemporaryDirectory() as td:
        td = Path(td)
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Generate small dataset
        df = pd.DataFrame({
            'col1': range(500),
            'col2': ['data'] * 500
        })
        df.to_csv(input_file, index=False)
        
        # Time the operation
        start = time.time()
        process_csv(input_file, output_file)
        elapsed = time.time() - start
        
        # Should complete in under 2 seconds
        assert elapsed < 2.0
        assert output_file.exists()

def test_performance_medium_dataset():
    """Test processing performance on medium dataset (1000-10000 rows)."""
    with TemporaryDirectory() as td:
        td = Path(td)
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Generate medium dataset
        df = pd.DataFrame({
            'col1': range(5000),
            'col2': ['data'] * 5000
        })
        df.to_csv(input_file, index=False)
        
        start = time.time()
        process_csv(input_file, output_file)
        elapsed = time.time() - start
        
        # Should complete in under 5 seconds
        assert elapsed < 5.0
        assert output_file.exists()
```

---

## 🔍 Code Quality Testing

### Linting Tests

```bash
# Run Black formatter check
black --check --line-length 120 scripts/ src/

# Apply Black formatting
black --line-length 120 scripts/ src/

# Run Flake8 linter
flake8 scripts/ src/ --max-line-length 120 --ignore=E203,W503

# Run Pylint
pylint scripts/ src/ --max-line-length=120

# Run Mypy type checker
mypy scripts/ src/ --ignore-missing-imports
```

### Adding Linting to Tests

```python
# tests/test_code_quality.py
import subprocess
from pathlib import Path

def test_black_formatting():
    """Test that code is formatted with Black."""
    result = subprocess.run(
        ['black', '--check', '--line-length', '120', 'scripts/', 'src/'],
        cwd=Path(__file__).parent.parent,
        capture_output=True
    )
    assert result.returncode == 0, "Code is not formatted with Black"

def test_flake8_linting():
    """Test that code passes Flake8 linting."""
    result = subprocess.run(
        ['flake8', 'scripts/', 'src/', '--max-line-length=120'],
        cwd=Path(__file__).parent.parent,
        capture_output=True
    )
    assert result.returncode == 0, "Code has Flake8 violations"
```

---

## 🛡️ Security Testing

### Testing for Common Vulnerabilities

```python
# tests/test_security.py
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.secure_file_handler import read_secure_config

def test_no_hardcoded_secrets():
    """Ensure no hardcoded secrets in config loading."""
    with TemporaryDirectory() as td:
        td = Path(td)
        config_file = td / "config.json"
        
        # Config without secrets
        config_file.write_text('{"setting": "value"}', encoding="utf-8")
        
        config = read_secure_config(config_file)
        
        # Should not contain sensitive keys
        assert 'password' not in str(config).lower()
        assert 'secret' not in str(config).lower()
        assert 'api_key' not in str(config).lower()

def test_safe_file_path_handling():
    """Test that file paths are validated against directory traversal."""
    from scripts.safe_file_ops import validate_path
    
    # Safe paths
    assert validate_path("data/file.csv")
    assert validate_path("output/report.xlsx")
    
    # Unsafe paths
    assert not validate_path("../../../etc/passwd")
    assert not validate_path("C:\\Windows\\System32\\config")
```

---

## 📊 Test Coverage Requirements

### Coverage Targets

- **Overall Coverage**: >70%
- **Critical Paths**: >90% (authentication, data processing)
- **New Code**: 100% (all new functions must have tests)

### Checking Coverage

```bash
# Generate coverage report
python -m pytest tests/ --cov=scripts --cov=src --cov-report=html --cov-report=term

# View coverage by file
python -m pytest tests/ --cov=scripts --cov=src --cov-report=term-missing

# View uncovered lines
python -m pytest tests/ --cov=scripts --cov=src --cov-report=html
# Open htmlcov/index.html to see line-by-line coverage
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

---

## 🔄 Continuous Testing Workflow

### Pre-Commit Testing

```bash
# Run before every commit
python -m pytest tests/ -v
black --check --line-length 120 scripts/ src/
flake8 scripts/ src/ --max-line-length 120
```

### CI/CD Integration

Tests run automatically on:
- Push to any branch
- Pull request creation
- Pull request update

See `.github/workflows/m365-security-ci.yml` for details.

---

## 🎯 Test-Driven Development (TDD) Workflow

### 1. Write the Test First

```python
# tests/test_new_feature.py
def test_new_feature():
    """Test the new feature I'm about to implement."""
    from scripts.new_feature import process_data
    
    result = process_data(input_data)
    assert result == expected_output
```

### 2. Run the Test (It Should Fail)

```bash
python -m pytest tests/test_new_feature.py -v
# Expected: FAILED (module not found or function not implemented)
```

### 3. Write Minimal Code to Pass

```python
# scripts/new_feature.py
def process_data(input_data):
    # Minimal implementation
    return expected_output
```

### 4. Run Test Again (Should Pass)

```bash
python -m pytest tests/test_new_feature.py -v
# Expected: PASSED
```

### 5. Refactor and Enhance

```python
# scripts/new_feature.py
def process_data(input_data):
    # Better implementation
    validated_data = validate(input_data)
    processed = transform(validated_data)
    return processed
```

### 6. Run All Tests

```bash
python -m pytest tests/ -v
# Ensure no regression
```

---

## 🆘 Troubleshooting Test Failures

### Common Issues and Solutions

#### Issue: "No module named 'scripts'"

```bash
# Solution: Run from repository root
cd /home/runner/work/share-report/share-report
python -m pytest tests/ -v
```

#### Issue: "TemporaryDirectory not cleaned up"

```python
# Bad: Using td after context exits
with TemporaryDirectory() as td:
    td = Path(td)
    file = td / "test.csv"

print(file)  # ERROR: td already deleted

# Good: All operations inside context
with TemporaryDirectory() as td:
    td = Path(td)
    file = td / "test.csv"
    # ... do all operations ...
    print(file)  # OK: td still exists
```

#### Issue: "Fixture not found"

```python
# Add conftest.py for shared fixtures
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def temp_csv_file(tmp_path):
    """Fixture providing temporary CSV file."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2\n1,2", encoding="utf-8")
    return csv_file

# Use in test
def test_with_fixture(temp_csv_file):
    assert temp_csv_file.exists()
```

---

## 📚 Additional Resources

- **[Pytest Documentation](https://docs.pytest.org/)** - Official pytest guide
- **[Coverage.py Documentation](https://coverage.readthedocs.io/)** - Coverage tool guide
- **[Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)** - General testing guide

---

## ✅ Testing Checklist for AI Agents

Before committing code:

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage >70% (>90% for critical paths)
- [ ] Tests use `TemporaryDirectory()` for file I/O
- [ ] Tests validate return values and output files
- [ ] Tests handle error cases
- [ ] Black formatting applied
- [ ] Flake8 linting passes
- [ ] No hardcoded paths or secrets in tests
- [ ] Tests are documented with docstrings
- [ ] Tests follow existing patterns in `tests/` directory

---

**🧪 Comprehensive testing ensures reliable, maintainable code for enterprise M365 security toolkit!**
