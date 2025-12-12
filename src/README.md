# Source Code Architecture

[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/downloads/)
[![Type Hints](https://img.shields.io/badge/Type%20Hints-Enabled-blue.svg)](https://docs.python.org/3/library/typing.html)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

## Overview

The `src/` directory contains the core Python modules that power the M365 Security & SharePoint Analysis Toolkit. This is a **proper Python package** with organized modules for security auditing, report generation, AI integration, and optional extensions.

**Architecture Philosophy:**
- **Core Modules** (`src/core/`) - Required functionality for report generation and file operations
- **Integration Modules** (`src/integrations/`) - External service connectors (SharePoint, OpenAI GPT-5)
- **Optional Extensions** (`src/extensions/`) - Add-on features like MCP servers for AI assistants
- **Plugin System** (`src/mcp/`) - Alternative plugin-based MCP architecture

> 📋 **For AI Agents:** See [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) for complete development guidelines

## Directory Structure

```
src/
├── __init__.py
├── core/                          # Core functionality (REQUIRED)
│   ├── __init__.py
│   ├── excel_generator.py         # Excel report generation with formatting
│   ├── cost_tracker.py            # GPT-5 API cost monitoring
│   ├── file_io.py                 # File operations with error handling
│   ├── profiler.py                # Performance profiling utilities
│   └── report_utils.py            # Report generation helpers
├── integrations/                  # External service connectors
│   ├── __init__.py
│   ├── sharepoint_connector.py    # SharePoint permissions analysis
│   └── openai_gpt5.py            # GPT-5 client (CORE dependency)
├── extensions/                    # Optional add-ons
│   ├── __init__.py
│   └── mcp/                       # Simplified MCP server
│       ├── server.py              # Async MCP server implementation
│       ├── setup.py               # Interactive setup wizard
│       ├── tools/                 # Tool definitions
│       └── README.md              # Extension documentation
└── mcp/                          # Plugin-based MCP architecture
    ├── m365_mcp_server.py         # Alternative MCP server
    └── plugins/                   # Pluggable tool system
        └── sharepoint_tools/
            ├── plugin.json        # Plugin metadata
            └── tools.py           # SharePoint-specific tools
```

## Core Modules (`src/core/`)

### `excel_generator.py` - Report Generation Engine

Generates professionally formatted Excel workbooks with multiple worksheets, styling, and charts.

**Key Features:**
- Multi-worksheet support with automatic formatting
- Color-coded headers and status indicators
- Auto-sizing columns for readability
- Chart generation for data visualization
- Memory-efficient for large datasets

**Usage Example:**
```python
from pathlib import Path
from src.core.excel_generator import create_project_management_workbook

# Generate a basic workbook
output_path = Path("output/reports/business/report.xlsx")
output_path.parent.mkdir(parents=True, exist_ok=True)
create_project_management_workbook(str(output_path))
```

**Security Considerations:**
- ❌ **Don't:** Include sensitive data in Excel files without encryption
- ✅ **Do:** Use Azure Rights Management for sensitive reports
- ✅ **Do:** Validate file paths to prevent directory traversal
- ✅ **Do:** Set appropriate file permissions (read-only for reports)

### `cost_tracker.py` - GPT-5 Cost Monitoring

Tracks OpenAI API usage and costs for budget management.

**Key Features:**
- Real-time cost calculation for GPT-5 API calls
- Per-request and cumulative cost tracking
- Token usage monitoring (prompt + completion)
- Cost alerts and budget enforcement

**Usage Example:**
```python
from src.core.cost_tracker import CostTracker

tracker = CostTracker(monthly_budget=100.0)

# Track API call
cost = tracker.track_request(
    model="gpt-4",
    prompt_tokens=500,
    completion_tokens=200
)

print(f"Request cost: ${cost:.4f}")
print(f"Total spent: ${tracker.total_cost:.2f}")
print(f"Budget remaining: ${tracker.remaining_budget:.2f}")
```

**Security Considerations:**
- ✅ **Do:** Store API keys in environment variables or Azure Key Vault
- ✅ **Do:** Implement rate limiting to prevent abuse
- ✅ **Do:** Log all API calls for audit trails
- ❌ **Don't:** Commit API keys to source control

### `file_io.py` - File Operations

Provides secure file I/O operations with validation and error handling.

**Key Features:**
- Automatic directory creation
- UTF-8-BOM handling for CSV files
- Path validation and sanitization
- Atomic write operations (write to temp, then rename)
- Comprehensive error handling

**Usage Example:**
```python
from pathlib import Path
from src.core.file_io import safe_read_json, safe_write_json

# Read JSON with error handling
data = safe_read_json(Path("config/audit_config.json"))

# Write JSON with atomic operations
safe_write_json(
    Path("output/reports/security/results.json"),
    data,
    ensure_parents=True
)
```

**Security Considerations:**
- ✅ **Do:** Validate file paths against allowed directories
- ✅ **Do:** Use absolute paths to prevent directory traversal
- ✅ **Do:** Set restrictive file permissions (600 for sensitive files)
- ❌ **Don't:** Trust user-supplied file paths without validation

### `profiler.py` - Performance Profiling

Built-in performance monitoring and benchmarking utilities.

**Key Features:**
- Execution time tracking
- Memory usage profiling
- Function-level profiling decorators
- Benchmark comparison against baselines

**Usage Example:**
```python
from src.core.profiler import profile_execution, benchmark

@profile_execution
def process_large_dataset(data):
    # Processing logic
    return processed_data

# Or use context manager
with benchmark("Data Processing"):
    result = process_large_dataset(data)
```

### `report_utils.py` - Report Utilities

Helper functions for generating consistent reports across modules.

**Key Features:**
- Common formatting functions
- Status badge generation
- Timestamp utilities
- Report metadata generation

**Usage Example:**
```python
from src.core.report_utils import generate_report_header, format_timestamp

header = generate_report_header(
    title="M365 Security Audit",
    tenant_id="12345678-1234-1234-1234-123456789abc",
    timestamp=format_timestamp()
)
```

## Integration Modules (`src/integrations/`)

### `sharepoint_connector.py` - SharePoint Analysis

Analyzes SharePoint permissions, generates reports, and identifies security risks.

**Key Features:**
- CSV-based permissions analysis
- User access reporting by site/folder/file
- External sharing detection
- Permission inheritance tracking
- Business-friendly Excel reports

**Usage Example:**
```python
from pathlib import Path
from src.integrations.sharepoint_connector import analyze_permissions

# Analyze SharePoint permissions
input_csv = Path("data/processed/sharepoint_clean.csv")
output_xlsx = Path("output/reports/business/permissions.xlsx")

stats = analyze_permissions(
    input_csv=input_csv,
    output_xlsx=output_xlsx,
    include_external=True
)

print(f"Total users analyzed: {stats['total_users']}")
print(f"External users found: {stats['external_users']}")
```

**Security Considerations:**
- ✅ **Do:** Sanitize CSV data before processing (use `scripts/clean_csv.py`)
- ✅ **Do:** Redact email addresses in reports shared externally
- ✅ **Do:** Encrypt reports containing user data
- ❌ **Don't:** Process untrusted CSV files without validation

### `openai_gpt5.py` - GPT-5 Client

OpenAI GPT-5 API client with retry logic, error handling, and cost tracking.

**Key Features:**
- Async API calls with retry logic
- Streaming support for long responses
- Token counting and cost calculation
- Contextual embeddings generation
- Rate limiting and backoff

**Usage Example:**
```python
from src.integrations.openai_gpt5 import GPT5Client
import os

# Initialize client
client = GPT5Client(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

# Generate completion
response = await client.complete(
    prompt="Analyze this M365 security audit result...",
    max_tokens=500,
    temperature=0.7
)

print(response.text)
print(f"Cost: ${response.cost:.4f}")
```

**Security Considerations:**
- ✅ **Do:** Store API keys in Azure Key Vault or environment variables
- ✅ **Do:** Sanitize data before sending to OpenAI (remove PII)
- ✅ **Do:** Implement request logging for audit compliance
- ❌ **Don't:** Send confidential audit findings to external APIs without approval
- ❌ **Don't:** Include customer names or credentials in prompts

## Optional Extensions (`src/extensions/`)

### MCP Server (`src/extensions/mcp/`)

Simplified Model Context Protocol (MCP) server for AI assistants like Claude Desktop.

**Purpose:** Enable AI assistants to directly interact with M365 security auditing tools.

**Key Features:**
- Tool definitions for security audits
- Async request handling
- JSON-RPC 2.0 protocol
- Interactive setup wizard

**Installation:**
```bash
# Install optional dependencies
pip install -r requirements-extensions.txt

# Run setup wizard
python -m src.extensions.mcp.setup

# Start MCP server
python -m src.extensions.mcp.server
```

**Security Considerations:**
- ✅ **Do:** Use localhost-only connections in production
- ✅ **Do:** Implement authentication tokens
- ✅ **Do:** Audit all tool invocations
- ❌ **Don't:** Expose MCP server to public internet

📖 **Full Documentation:** See [`src/extensions/mcp/README.md`](extensions/mcp/README.md)

## Plugin-Based MCP (`src/mcp/`)

Alternative MCP architecture with pluggable tools for extensibility.

**Purpose:** Support custom tool development and third-party integrations.

**Key Features:**
- Plugin discovery system
- Dynamic tool loading
- Plugin metadata validation
- Hot-reload support (development mode)

**Plugin Structure:**
```
src/mcp/plugins/my_tool/
├── plugin.json        # Metadata (name, version, dependencies)
├── tools.py          # Tool implementation
└── README.md         # Plugin documentation
```

**Creating a Plugin:**
```python
# src/mcp/plugins/my_tool/tools.py
class MyToolPlugin:
    """Custom MCP tool for specific auditing task"""
    
    def __init__(self):
        self.name = "my_tool"
        self.description = "Performs custom security analysis"
    
    def execute(self, params: dict) -> dict:
        """
        Execute the tool
        
        Args:
            params: Tool parameters from MCP client
            
        Returns:
            dict: Result with status, data, and message
        """
        try:
            # Tool logic here
            result = perform_analysis(params)
            
            return {
                "status": "success",
                "data": result,
                "message": "Analysis completed"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Error: {str(e)}"
            }
```

**Security Considerations:**
- ✅ **Do:** Validate all plugin inputs
- ✅ **Do:** Sandbox plugin execution
- ✅ **Do:** Code-sign trusted plugins
- ❌ **Don't:** Load plugins from untrusted sources

## Module Import Patterns

### Standard Import (Recommended)
```python
# Import from src package
from src.core.excel_generator import create_project_management_workbook
from src.integrations.sharepoint_connector import analyze_permissions
from src.core.file_io import safe_read_json
```

### Module Execution
```python
# ✅ DO: Execute modules with python -m
python -m src.integrations.sharepoint_connector --input data.csv --output report.xlsx

# ❌ DON'T: Use -m with scripts directory
python -m scripts.clean_csv  # This won't work

# ✅ DO: Execute scripts directly
python scripts/clean_csv.py --input raw.csv --output clean.csv
```

### Type Hints Best Practices
```python
from pathlib import Path
from typing import Dict, List, Optional

def generate_report(
    input_path: Path,
    output_path: Path,
    options: Optional[Dict[str, any]] = None
) -> Dict[str, int]:
    """
    Generate security audit report
    
    Args:
        input_path: Path to JSON audit results
        output_path: Path for output Excel file
        options: Optional configuration dictionary
        
    Returns:
        Statistics dictionary with counts
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input JSON is invalid
    """
    # Implementation
    pass
```

## API Usage Examples

### End-to-End Security Audit Workflow

```python
from pathlib import Path
from src.core.excel_generator import create_project_management_workbook
from src.core.file_io import safe_read_json, safe_write_json
from src.integrations.sharepoint_connector import analyze_permissions

# 1. Read audit configuration
config = safe_read_json(Path("config/audit_config.json"))

# 2. Process SharePoint data (after PowerShell audit)
sharepoint_csv = Path("data/processed/sharepoint_clean.csv")
sharepoint_report = Path("output/reports/business/sharepoint_permissions.xlsx")

stats = analyze_permissions(
    input_csv=sharepoint_csv,
    output_xlsx=sharepoint_report,
    tenant_name=config["tenantConfig"]["spoAdminUrl"]
)

# 3. Generate summary report
summary = {
    "audit_date": stats["audit_date"],
    "total_users": stats["total_users"],
    "external_users": stats["external_users"],
    "high_risk_permissions": stats["high_risk_count"]
}

safe_write_json(
    Path("output/reports/security/audit_summary.json"),
    summary,
    ensure_parents=True
)
```

## Security & Compliance

### Input Validation

**Always validate and sanitize inputs:**

```python
from pathlib import Path

def validate_input_path(path: Path, allowed_dir: Path) -> bool:
    """
    Validate that path is within allowed directory
    
    Args:
        path: Path to validate
        allowed_dir: Allowed parent directory
        
    Returns:
        bool: True if path is safe
    """
    try:
        # Resolve to absolute path
        abs_path = path.resolve()
        abs_allowed = allowed_dir.resolve()
        
        # Check if path is within allowed directory
        return abs_path.is_relative_to(abs_allowed)
    except (ValueError, OSError):
        return False
```

### Error Handling

**Use specific exceptions and provide context:**

```python
import sys
from pathlib import Path

def process_audit_file(file_path: Path) -> dict:
    """Process audit file with comprehensive error handling"""
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Audit file not found: {file_path}")
        
        if file_path.stat().st_size == 0:
            raise ValueError(f"Audit file is empty: {file_path}")
        
        # Process file
        data = safe_read_json(file_path)
        
        if not data.get("results"):
            raise ValueError("No audit results found in file")
        
        return data
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: Invalid audit file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error - {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
```

### Logging for Audit Compliance

**Log security-relevant operations:**

```python
import logging
from datetime import datetime

# Configure audit logging
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# File handler with rotation
handler = logging.handlers.RotatingFileHandler(
    "logs/audit.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
))
audit_logger.addHandler(handler)

# Log security operations
def process_sensitive_data(user: str, operation: str):
    audit_logger.info(
        f"User={user} Operation={operation} Timestamp={datetime.utcnow().isoformat()}"
    )
```

### SOX/AICPA Compliance Considerations

**For CPA firms and financial auditors:**

1. **Access Controls:** Implement role-based access to audit data
2. **Audit Trails:** Log all data access and modifications
3. **Data Retention:** Retain audit logs for 7 years (SOX requirement)
4. **Change Management:** Version control all configuration changes
5. **Backup & Recovery:** Regular backups with tested restore procedures

```python
# Example: Audit trail decorator
from functools import wraps

def audit_trail(operation_type: str):
    """Decorator to log security operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log operation start
            audit_logger.info(f"START - {operation_type} - {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                audit_logger.info(f"SUCCESS - {operation_type} - {func.__name__}")
                return result
            except Exception as e:
                audit_logger.error(f"FAILED - {operation_type} - {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

@audit_trail("DATA_EXPORT")
def export_audit_results(output_path: Path):
    """Export with audit logging"""
    # Implementation
    pass
```

## Testing

### Unit Testing with pytest

**Test structure mirrors source structure:**
```
tests/
├── test_clean_csv.py         # Tests for scripts/clean_csv.py
├── test_file_io.py           # Tests for src/core/file_io.py
├── test_report_utils.py      # Tests for src/core/report_utils.py
└── powershell/               # PowerShell tests (Pester)
```

**Example test:**
```python
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd

from src.integrations.sharepoint_connector import analyze_permissions

def test_sharepoint_analysis_basic():
    """Test basic SharePoint permissions analysis"""
    with TemporaryDirectory() as td:
        td = Path(td)
        
        # Create test CSV
        input_csv = td / "input.csv"
        input_csv.write_text(
            "User,Email,Permission,SiteUrl\n"
            "John Doe,john@example.com,Contribute,https://site1\n",
            encoding="utf-8"
        )
        
        output_xlsx = td / "output.xlsx"
        
        # Run analysis
        stats = analyze_permissions(input_csv, output_xlsx)
        
        # Assertions
        assert output_xlsx.exists()
        assert stats["total_users"] == 1
        assert "john@example.com" in stats["users"]
```

### Test Coverage Requirements

**Minimum 80% code coverage:**

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Mocking M365 Services

**Use `unittest.mock` for external API calls:**

```python
from unittest.mock import patch, MagicMock
import pytest

@patch('src.integrations.sharepoint_connector.SharePointClient')
def test_sharepoint_connection(mock_client):
    """Test SharePoint connection with mocked API"""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.get_site_permissions.return_value = {
        "users": ["user1@example.com"],
        "permissions": ["Contribute"]
    }
    mock_client.return_value = mock_instance
    
    # Test function that uses SharePoint API
    result = fetch_site_permissions("https://example.sharepoint.com")
    
    # Verify
    assert "user1@example.com" in result["users"]
    mock_instance.get_site_permissions.assert_called_once()
```

📖 **Full Testing Guide:** See [`../tests/README.md`](../tests/README.md)

## Contributing

### Code Style

**Follow PEP 8 with Black formatter (120 char line length):**

```bash
# Format code
black src/ --line-length 120

# Check style
flake8 src/ --max-line-length 120

# Type checking
mypy src/ --strict
```

### Development Workflow

1. **Create feature branch:** `git checkout -b feature/my-feature`
2. **Make changes with tests:** Add tests for new functionality
3. **Run tests locally:** `pytest tests/ -v`
4. **Format code:** `black src/ --line-length 120`
5. **Commit changes:** `git commit -m "feat: add new feature"`
6. **Push and create PR:** Target `Primary` branch (not `main`)

### Adding New Modules

**Module template:**

```python
"""
Module description

This module provides [functionality] for [purpose].

Security Considerations:
    - List security requirements
    - Authentication/authorization needs
    - Data sensitivity level

Usage:
    from src.core.my_module import MyClass
    
    obj = MyClass()
    result = obj.process(data)

Author: [Your Name]
Date: [YYYY-MM-DD]
"""

from pathlib import Path
from typing import Dict, Optional

import logging

logger = logging.getLogger(__name__)


class MyClass:
    """
    Brief class description
    
    Attributes:
        attribute_name: Description
        
    Example:
        >>> obj = MyClass()
        >>> result = obj.process({"key": "value"})
        >>> print(result)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the class
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        logger.info("MyClass initialized")
    
    def process(self, data: Dict) -> Dict:
        """
        Process input data
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed data dictionary
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Implementation
        return {"status": "success", "data": data}
```

## Cross-References

### Related Documentation

- **Parent README:** [`../README.md`](../README.md) - Project overview and quick start
- **AI Development Guide:** [`../.github/copilot-instructions.md`](../.github/copilot-instructions.md) - Complete AI agent guide
- **Testing Guide:** [`../tests/README.md`](../tests/README.md) - Test structure and best practices
- **Security Policy:** [`../SECURITY.md`](../SECURITY.md) - Security reporting and policies
- **Contributing Guide:** [`../CONTRIBUTING.md`](../CONTRIBUTING.md) - Development guidelines
- **Scripts Documentation:** [`../scripts/README.md`](../scripts/README.md) - PowerShell and Python scripts
- **MCP Server Guide:** [`extensions/mcp/README.md`](extensions/mcp/README.md) - MCP server setup

### External Resources

- **Python Style Guide:** [PEP 8](https://peps.python.org/pep-0008/)
- **Type Hints:** [PEP 484](https://peps.python.org/pep-0484/)
- **Black Formatter:** [Black Documentation](https://black.readthedocs.io/)
- **pytest:** [pytest Documentation](https://docs.pytest.org/)
- **CIS Controls:** [CIS Microsoft 365 Benchmark](https://www.cisecurity.org/benchmark/microsoft_365)

---

**🔐 Security Focus:** This toolkit handles sensitive M365 tenant data. Always follow security best practices, validate inputs, log operations, and comply with SOX/AICPA standards for CPA environments.

**🧪 Testing Required:** All new modules must include tests with minimum 80% coverage. See [`../tests/README.md`](../tests/README.md).

**🤖 AI-Ready:** Optimized for GitHub Copilot and other AI assistants. See [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) for development patterns.
