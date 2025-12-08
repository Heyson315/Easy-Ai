# Testing Guide

[![pytest](https://img.shields.io/badge/pytest-7.0+-blue.svg)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-green.svg)](../coverage.svg)
[![Pester](https://img.shields.io/badge/Pester-5.0+-blue.svg)](https://pester.dev/)

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov=scripts --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_clean_csv.py -v

# Run tests matching pattern
pytest tests/ -k "test_sharepoint" -v
```

## Overview

This directory contains the test suite for the M365 Security & SharePoint Analysis Toolkit. We use **pytest** for Python tests and **Pester v5** for PowerShell tests, maintaining a minimum **80% code coverage** requirement.

**Testing Philosophy:**
- **Unit Tests:** Test individual functions and classes in isolation
- **Integration Tests:** Test interactions between modules and external services
- **Mocking:** Mock M365 API calls to avoid requiring live tenant access
- **Performance Tests:** Validate performance benchmarks and optimization claims
- **Security Tests:** Verify input validation and security controls

## Test Structure

```
tests/
├── test_clean_csv.py              # CSV cleaning utilities
├── test_file_io.py                # File I/O operations
├── test_report_utils.py           # Report generation utilities
├── test_performance_optimizations.py  # Performance benchmarks
├── test_mcp_plugins.py            # MCP plugin system
└── powershell/                    # PowerShell tests (Pester v5)
    ├── M365CIS.Tests.ps1          # M365 CIS module tests
    ├── Invoke-M365CISAudit.Tests.ps1  # Audit script tests
    └── PostRemediateM365CIS.Tests.ps1  # Remediation tests
```

**Naming Conventions:**
- Python: `test_<module_name>.py`
- PowerShell: `<ScriptName>.Tests.ps1`
- Test functions: `test_<functionality>_<scenario>()`
- Test classes: `Test<ClassName>`

## Running Tests

### Python Tests (pytest)

**Basic execution:**
```bash
# All tests with verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Run in parallel (faster)
pytest tests/ -n auto
```

**Coverage reporting:**
```bash
# Terminal coverage report
pytest tests/ --cov=src --cov=scripts --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=src --cov=scripts --cov-report=html
open htmlcov/index.html

# XML coverage report (for CI/CD)
pytest tests/ --cov=src --cov=scripts --cov-report=xml
```

**Filtering tests:**
```bash
# By marker
pytest tests/ -m "not slow"          # Skip slow tests
pytest tests/ -m "integration"       # Only integration tests

# By keyword
pytest tests/ -k "sharepoint"        # Tests with "sharepoint" in name
pytest tests/ -k "not performance"   # Exclude performance tests

# By file
pytest tests/test_clean_csv.py -v   # Single test file
```

**Test markers:**
```python
import pytest

@pytest.mark.slow
def test_large_dataset_processing():
    """Test marked as slow"""
    pass

@pytest.mark.integration
def test_sharepoint_api_connection():
    """Test marked as integration"""
    pass

@pytest.mark.skipif(sys.platform == "linux", reason="Windows-only test")
def test_windows_specific_feature():
    """Test skipped on Linux"""
    pass
```

### PowerShell Tests (Pester v5)

**Basic execution:**
```powershell
# Install Pester v5 (if not already installed)
Install-Module -Name Pester -MinimumVersion 5.0 -Scope CurrentUser -Force

# Run all PowerShell tests
Invoke-Pester tests/powershell/ -Output Detailed

# Run specific test file
Invoke-Pester tests/powershell/M365CIS.Tests.ps1 -Output Detailed

# Run with code coverage
Invoke-Pester tests/powershell/ -CodeCoverage 'scripts/powershell/modules/*.psm1'
```

**Pester v5 test structure:**
```powershell
BeforeAll {
    # Import module to test
    Import-Module "$PSScriptRoot/../../scripts/powershell/modules/M365CIS.psm1" -Force
}

Describe "Test-CIS-Function" {
    Context "When input is valid" {
        It "Should return Pass status" {
            # Arrange
            Mock Get-SomeM365Config { return "ExpectedValue" }
            
            # Act
            $result = Test-CIS-EXO-1-1-1
            
            # Assert
            $result.Status | Should -Be "Pass"
            $result.ControlId | Should -Be "1.1.1"
        }
    }
    
    Context "When input is invalid" {
        It "Should return Fail status" {
            # Arrange
            Mock Get-SomeM365Config { return "WrongValue" }
            
            # Act
            $result = Test-CIS-EXO-1-1-1
            
            # Assert
            $result.Status | Should -Be "Fail"
        }
    }
    
    Context "When API call fails" {
        It "Should return Manual status" {
            # Arrange
            Mock Get-SomeM365Config { throw "API Error" }
            
            # Act
            $result = Test-CIS-EXO-1-1-1
            
            # Assert
            $result.Status | Should -Be "Manual"
            $result.Actual | Should -Match "Error"
        }
    }
}
```

**Important Pester v5 syntax changes:**
- ✅ Use `Should -Be` (with dash)
- ❌ Don't use `Should Be` (without dash - Pester v4 syntax)
- ✅ Use `BeforeAll` and `AfterAll` (not `BeforeEach`)
- ✅ Use `-TestCases` for parameterized tests

## Test Coverage

### Coverage Requirements

**Minimum coverage targets:**
- **Overall:** 80% code coverage
- **Critical modules:** 90% coverage (file_io.py, security functions)
- **Integration modules:** 70% coverage (external API dependencies)
- **Utility scripts:** 60% coverage (simple helper scripts)

**Coverage enforcement in CI/CD:**
```yaml
# .github/workflows/ci.yml
- name: Run tests with coverage
  run: |
    pytest tests/ --cov=src --cov=scripts --cov-report=term --cov-report=xml
    
- name: Check coverage threshold
  run: |
    coverage report --fail-under=80
```

### Coverage Reports

**Generate coverage badge:**
```bash
# Run tests with coverage
pytest tests/ --cov=src --cov=scripts --cov-report=term --cov-report=xml

# Generate badge (requires coverage-badge)
pip install coverage-badge
coverage-badge -o coverage.svg -f
```

**View detailed coverage:**
```bash
# HTML report with line-by-line coverage
pytest tests/ --cov=src --cov=scripts --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest tests/ --cov=src --cov=scripts --cov-report=term-missing
```

**Example coverage report:**
```
---------- coverage: platform linux, python 3.11.5-final-0 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/core/excel_generator.py              145      8    94%   89-92, 156-159
src/core/file_io.py                       78      3    96%   45, 67, 89
src/integrations/sharepoint_connector.py  234     42    82%   123-145, 234-256
scripts/clean_csv.py                      156     12    92%   89-92, 145-152
---------------------------------------------------------------------
TOTAL                                     613     65    89%
```

## Mocking M365 Services

### Why Mock External Services?

**Reasons to mock:**
- ✅ **No credentials required:** Tests run without M365 tenant access
- ✅ **Faster execution:** No network latency or API rate limits
- ✅ **Consistent results:** No dependency on external service state
- ✅ **CI/CD friendly:** Tests run in any environment
- ✅ **Test error scenarios:** Simulate API failures and edge cases

### Mocking Patterns (Python)

**Mock with `unittest.mock`:**
```python
from unittest.mock import patch, MagicMock, Mock
import pytest

# Mock external API call
@patch('src.integrations.sharepoint_connector.SharePointClient')
def test_sharepoint_connection(mock_client):
    """Test SharePoint API connection"""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.get_site_permissions.return_value = {
        "users": ["user1@example.com"],
        "groups": ["Owners"]
    }
    mock_client.return_value = mock_instance
    
    # Call function that uses SharePoint API
    from src.integrations.sharepoint_connector import fetch_permissions
    result = fetch_permissions("https://example.sharepoint.com")
    
    # Verify
    assert "user1@example.com" in result["users"]
    mock_instance.get_site_permissions.assert_called_once()
```

**Mock file operations:**
```python
from unittest.mock import mock_open, patch
from pathlib import Path

@patch('pathlib.Path.read_text')
def test_read_config(mock_read):
    """Test configuration file reading"""
    # Mock file content
    mock_read.return_value = '{"key": "value"}'
    
    # Call function
    from src.core.file_io import safe_read_json
    config = safe_read_json(Path("config.json"))
    
    # Verify
    assert config["key"] == "value"
```

**Mock environment variables:**
```python
@patch.dict('os.environ', {
    'OPENAI_API_KEY': 'test-key-123',
    'M365_TENANT_ID': 'test-tenant-id'
})
def test_api_client_initialization():
    """Test API client with environment variables"""
    from src.integrations.openai_gpt5 import GPT5Client
    
    client = GPT5Client()
    assert client.api_key == 'test-key-123'
```

### Mocking Patterns (PowerShell)

**Mock with Pester:**
```powershell
Describe "Connect-M365CIS" {
    It "Should connect to Exchange Online" {
        # Mock the Connect-ExchangeOnline cmdlet
        Mock Connect-ExchangeOnline { return $true }
        
        # Call function
        $result = Connect-M365CIS -Service ExchangeOnline
        
        # Verify
        $result | Should -Be $true
        Should -Invoke Connect-ExchangeOnline -Times 1
    }
}

Describe "Test-CIS-EXO-BasicAuth" {
    It "Should return Pass when basic auth is disabled" {
        # Mock Exchange Online cmdlet
        Mock Get-OrganizationConfig {
            return @{
                OAuth2ClientProfileEnabled = $true
                DefaultAuthenticationPolicy = "Block Basic Auth"
            }
        }
        
        # Call test function
        $result = Test-CIS-EXO-1-1-1
        
        # Verify
        $result.Status | Should -Be "Pass"
        $result.ControlId | Should -Be "1.1.1"
    }
}
```

**Mock return values:**
```powershell
Mock Get-AzureADUser {
    return @{
        DisplayName = "Test User"
        UserPrincipalName = "test@example.com"
        ObjectId = "12345678-1234-1234-1234-123456789abc"
    }
}
```

**Mock with parameters:**
```powershell
Mock Get-AzureADUser -ParameterFilter { $ObjectId -eq "specific-id" } {
    return @{ DisplayName = "Specific User" }
}

Mock Get-AzureADUser -ParameterFilter { $ObjectId -eq "another-id" } {
    return @{ DisplayName = "Another User" }
}
```

## CI/CD Integration

### GitHub Actions Workflows

**Test workflow (`.github/workflows/ci.yml`):**
```yaml
name: CI Tests

on:
  push:
    branches: [ Primary, develop ]
  pull_request:
    branches: [ Primary, develop ]

jobs:
  test-python:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          pytest tests/ --cov=src --cov=scripts --cov-report=xml --cov-report=term
      
      - name: Check coverage threshold
        run: |
          coverage report --fail-under=80
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests

  test-powershell:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Pester
        shell: pwsh
        run: |
          Install-Module -Name Pester -MinimumVersion 5.0 -Scope CurrentUser -Force
      
      - name: Run PowerShell tests
        shell: pwsh
        run: |
          Invoke-Pester tests/powershell/ -Output Detailed
```

### Pre-commit Hooks

**Setup pre-commit (.pre-commit-config.yaml already exists):**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Hooks included:**
- **black:** Code formatting
- **flake8:** Linting
- **mypy:** Type checking
- **pytest:** Run fast unit tests
- **markdownlint:** Markdown formatting

## Writing New Tests

### Test-Driven Development (TDD)

**TDD workflow:**
1. **Write failing test:** Define expected behavior
2. **Run test:** Verify it fails (red)
3. **Write minimal code:** Make test pass (green)
4. **Refactor:** Improve code while keeping tests passing
5. **Repeat:** Add more test cases

**Example TDD cycle:**
```python
# Step 1: Write failing test
def test_calculate_compliance_score():
    """Test compliance score calculation"""
    results = [
        {"Status": "Pass"},
        {"Status": "Pass"},
        {"Status": "Fail"}
    ]
    
    score = calculate_compliance_score(results)
    
    assert score == 66.67  # 2/3 = 66.67%

# Step 2: Run test - it fails (function doesn't exist)
# pytest tests/test_report_utils.py -k test_calculate_compliance_score

# Step 3: Write minimal implementation
def calculate_compliance_score(results):
    """Calculate compliance score percentage"""
    if not results:
        return 0.0
    
    passed = sum(1 for r in results if r["Status"] == "Pass")
    total = len(results)
    
    return round((passed / total) * 100, 2)

# Step 4: Run test again - it passes!
```

### Test Template (Python)

```python
"""
Tests for <module_name>

This module tests [functionality].

Author: [Your Name]
Date: [YYYY-MM-DD]
"""

import sys
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.my_module import MyClass


class TestMyClass:
    """Tests for MyClass"""
    
    def test_initialization(self):
        """Test class initialization"""
        obj = MyClass(config={"key": "value"})
        assert obj.config["key"] == "value"
    
    def test_process_valid_input(self):
        """Test processing with valid input"""
        obj = MyClass()
        result = obj.process({"data": "test"})
        
        assert result["status"] == "success"
        assert "data" in result
    
    def test_process_invalid_input(self):
        """Test processing with invalid input"""
        obj = MyClass()
        
        with pytest.raises(ValueError, match="Data cannot be empty"):
            obj.process({})
    
    @patch('src.core.my_module.external_api_call')
    def test_process_with_mocked_api(self, mock_api):
        """Test processing with mocked external API"""
        # Setup mock
        mock_api.return_value = {"api_result": "success"}
        
        # Call function
        obj = MyClass()
        result = obj.process({"data": "test"})
        
        # Verify
        assert result["status"] == "success"
        mock_api.assert_called_once_with({"data": "test"})


def test_standalone_function():
    """Test standalone function"""
    from src.core.my_module import helper_function
    
    result = helper_function("input")
    assert result == "expected_output"


@pytest.mark.slow
def test_large_dataset_processing():
    """Test with large dataset (marked as slow)"""
    obj = MyClass()
    
    # Create large dataset
    large_data = {"items": [{"id": i} for i in range(10000)]}
    
    result = obj.process(large_data)
    assert result["status"] == "success"


def test_file_operations():
    """Test file I/O operations"""
    with TemporaryDirectory() as td:
        td = Path(td)
        
        # Create test file
        test_file = td / "test.json"
        test_file.write_text('{"key": "value"}', encoding="utf-8")
        
        # Test function
        obj = MyClass()
        result = obj.read_config(test_file)
        
        # Verify
        assert result["key"] == "value"
```

### Test Template (PowerShell)

```powershell
<#
.SYNOPSIS
    Tests for <ScriptName>.ps1

.DESCRIPTION
    This test suite validates [functionality].

.AUTHOR
    [Your Name]

.DATE
    [YYYY-MM-DD]
#>

BeforeAll {
    # Import module or script to test
    $ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Import-Module "$ProjectRoot/scripts/powershell/modules/M365CIS.psm1" -Force
}

Describe "Test-CIS-MyFunction" {
    Context "When configuration is compliant" {
        BeforeAll {
            # Setup common mocks
            Mock Get-OrganizationConfig {
                return @{
                    Setting1 = "ExpectedValue"
                    Setting2 = $true
                }
            }
        }
        
        It "Should return Pass status" {
            # Act
            $result = Test-CIS-EXO-1-1-1
            
            # Assert
            $result.Status | Should -Be "Pass"
            $result.ControlId | Should -Be "1.1.1"
            $result.Severity | Should -Be "High"
        }
        
        It "Should have correct evidence" {
            $result = Test-CIS-EXO-1-1-1
            
            $result.Evidence | Should -Not -BeNullOrEmpty
            $result.Evidence | Should -Match "Setting1.*ExpectedValue"
        }
    }
    
    Context "When configuration is non-compliant" {
        BeforeAll {
            Mock Get-OrganizationConfig {
                return @{
                    Setting1 = "WrongValue"
                    Setting2 = $false
                }
            }
        }
        
        It "Should return Fail status" {
            $result = Test-CIS-EXO-1-1-1
            
            $result.Status | Should -Be "Fail"
        }
        
        It "Should have detailed actual value" {
            $result = Test-CIS-EXO-1-1-1
            
            $result.Actual | Should -Not -BeNullOrEmpty
            $result.Actual | Should -Match "WrongValue"
        }
    }
    
    Context "When API call fails" {
        BeforeAll {
            Mock Get-OrganizationConfig {
                throw "API connection failed"
            }
        }
        
        It "Should return Manual status on error" {
            $result = Test-CIS-EXO-1-1-1
            
            $result.Status | Should -Be "Manual"
            $result.Actual | Should -Match "Error"
        }
    }
}

Describe "Helper Functions" {
    Context "Connect-M365CIS" {
        It "Should handle connection errors gracefully" {
            Mock Connect-ExchangeOnline { throw "Connection failed" }
            
            { Connect-M365CIS -Service ExchangeOnline } | Should -Throw "Connection failed"
        }
    }
}
```

### Best Practices for Test Writing

**DO:**
- ✅ Use descriptive test names: `test_sharepoint_analysis_with_external_users()`
- ✅ Test one thing per test function
- ✅ Use `TemporaryDirectory()` for file I/O tests
- ✅ Mock external API calls (M365, OpenAI)
- ✅ Test edge cases (empty input, null values, large datasets)
- ✅ Include docstrings for complex tests
- ✅ Use `pytest.mark` for categorization
- ✅ Clean up resources in teardown/finally blocks

**DON'T:**
- ❌ Don't test library code (e.g., pandas internals)
- ❌ Don't write tests that depend on external services
- ❌ Don't use hardcoded paths (use `Path(__file__).parent`)
- ❌ Don't share state between tests
- ❌ Don't skip assertions (every test must verify something)
- ❌ Don't commit disabled tests without explanation
- ❌ Don't test private methods directly (test through public API)

## Security Testing

### Input Validation Testing

**Test for injection vulnerabilities:**
```python
def test_sql_injection_prevention():
    """Test SQL injection prevention (if using SQL)"""
    malicious_input = "'; DROP TABLE users; --"
    
    # Should sanitize or reject
    with pytest.raises(ValueError, match="Invalid input"):
        process_user_input(malicious_input)


def test_path_traversal_prevention():
    """Test path traversal prevention"""
    malicious_path = Path("../../etc/passwd")
    allowed_dir = Path("/app/data")
    
    is_safe = validate_input_path(malicious_path, allowed_dir)
    
    assert is_safe == False


def test_command_injection_prevention():
    """Test command injection prevention"""
    malicious_command = "test; rm -rf /"
    
    # Should sanitize or reject
    with pytest.raises(ValueError, match="Invalid command"):
        execute_safe_command(malicious_command)
```

### Authentication/Authorization Testing

```python
@patch('os.getenv')
def test_missing_api_key(mock_getenv):
    """Test behavior when API key is missing"""
    mock_getenv.return_value = None
    
    with pytest.raises(ValueError, match="API key not configured"):
        client = GPT5Client()


def test_invalid_credentials():
    """Test handling of invalid credentials"""
    with pytest.raises(AuthenticationError):
        client = GPT5Client(api_key="invalid-key")
        client.authenticate()
```

### Data Sanitization Testing

```python
def test_email_redaction():
    """Test email address redaction in reports"""
    data = {
        "user": "john.doe@example.com",
        "message": "Contact me at john.doe@example.com"
    }
    
    sanitized = redact_pii(data)
    
    assert "@" not in sanitized["user"]
    assert sanitized["user"] == "j***@e***.com"


def test_credential_removal():
    """Test credential removal from logs"""
    log_entry = "Connecting with password: SecretPassword123"
    
    sanitized = sanitize_log(log_entry)
    
    assert "SecretPassword123" not in sanitized
    assert "***REDACTED***" in sanitized
```

## Performance Testing

### Benchmark Tests

```python
import time

@pytest.mark.slow
def test_csv_cleaning_performance():
    """Test CSV cleaning performance meets benchmarks"""
    # Create test file with 5000 rows
    test_data = generate_test_csv(rows=5000)
    
    start = time.time()
    clean_csv(test_data, output_path)
    elapsed = time.time() - start
    
    # Should complete in under 0.1 seconds (100ms)
    assert elapsed < 0.1, f"CSV cleaning took {elapsed:.3f}s, expected < 0.1s"


@pytest.mark.slow
def test_memory_usage():
    """Test memory usage stays within limits"""
    import tracemalloc
    
    tracemalloc.start()
    
    # Process large dataset
    process_large_dataset(rows=50000)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Should use less than 10MB
    assert peak < 10 * 1024 * 1024, f"Peak memory: {peak / 1024 / 1024:.2f}MB"
```

### Load Testing

```python
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.slow
def test_concurrent_processing():
    """Test concurrent report generation"""
    def generate_report(index):
        return create_report(f"report_{index}")
    
    # Process 10 reports concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(generate_report, range(10)))
    
    # All should succeed
    assert len(results) == 10
    assert all(r["status"] == "success" for r in results)
```

## Troubleshooting

### Common Test Failures

**Import errors:**
```bash
# Error: ModuleNotFoundError: No module named 'src'
# Solution: Ensure tests run from project root
cd /path/to/Easy-Ai
pytest tests/ -v

# Or add to conftest.py:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Fixture not found:**
```python
# Error: fixture 'tmp_path' not found
# Solution: Use pytest built-in fixtures or define in conftest.py

# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Fixture providing test data directory"""
    return Path(__file__).parent / "test_data"
```

**Mock not working:**
```python
# Issue: Mock doesn't affect function call
# Solution: Patch at the point of use, not definition

# ❌ Wrong
@patch('src.core.file_io.open')
def test_read_file(mock_open):
    pass

# ✅ Correct (patch where it's used)
@patch('src.integrations.sharepoint_connector.open')
def test_read_file(mock_open):
    pass
```

**Pester v5 syntax errors:**
```powershell
# Error: Should : The term 'Should' is not recognized
# Solution: Use Pester v5 syntax with dash

# ❌ Wrong (Pester v4)
$result.Status | Should Be "Pass"

# ✅ Correct (Pester v5)
$result.Status | Should -Be "Pass"
```

### Debugging Tests

**Python debugging:**
```bash
# Run with debugger
pytest tests/test_clean_csv.py --pdb

# Drop to debugger on failure
pytest tests/ -x --pdb

# Set breakpoint in test
import pdb; pdb.set_trace()  # Python 3.6
breakpoint()  # Python 3.7+
```

**PowerShell debugging:**
```powershell
# Run with verbose output
Invoke-Pester tests/powershell/ -Output Diagnostic

# Debug specific test
Set-PSBreakpoint -Script tests/powershell/M365CIS.Tests.ps1 -Line 45
Invoke-Pester tests/powershell/M365CIS.Tests.ps1
```

**Verbose output:**
```bash
# Show print statements
pytest tests/ -s

# Show full diff on assertion failure
pytest tests/ -vv

# Show summary of all tests
pytest tests/ --tb=short
```

## Cross-References

### Related Documentation

- **Source Code Guide:** [`../src/README.md`](../src/README.md) - Module documentation and APIs
- **Parent README:** [`../README.md`](../README.md) - Project overview
- **AI Development Guide:** [`../.github/copilot-instructions.md`](../.github/copilot-instructions.md) - Testing patterns for AI agents
- **Contributing Guide:** [`../CONTRIBUTING.md`](../CONTRIBUTING.md) - Development workflow
- **CI/CD Workflows:** [`../.github/workflows/README.md`](../.github/workflows/README.md) - CI/CD documentation

### External Resources

- **pytest Documentation:** [pytest.org](https://docs.pytest.org/)
- **Pester Documentation:** [pester.dev](https://pester.dev/)
- **unittest.mock:** [Python Mock](https://docs.python.org/3/library/unittest.mock.html)
- **Coverage.py:** [coverage.readthedocs.io](https://coverage.readthedocs.io/)
- **pytest Plugins:** [pytest-dev plugins](https://docs.pytest.org/en/latest/reference/plugin_list.html)

---

**🧪 Testing Standards:** Maintain minimum 80% code coverage. All new features require tests. Mock external M365 services to enable testing without credentials.

**🔐 Security Testing:** Validate input sanitization, test authentication/authorization, verify credential handling, and check for injection vulnerabilities.

**🤖 CI/CD Integration:** Tests run automatically on PR creation. Coverage reports upload to Codecov. Pre-commit hooks enforce code quality.
