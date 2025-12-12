# 🎯 Test Coverage Improvement Plan

**Target**: Increase coverage from **47%** to **80%**

**Date**: December 11, 2025  
**Current Coverage**: 47% (1,578 / 3,327 lines)  
**Target Coverage**: 80% (2,662 / 3,327 lines)  
**Lines to Cover**: **1,084 additional lines**

---

## 📊 Coverage Analysis by Category

### ✅ Already Excellent (>90%)
These modules are well-tested and don't need additional coverage:
- `src/core/excel_generator.py` - 100%
- `src/core/file_io.py` - 100%
- `src/core/console_utils.py` - 100%
- `src/integrations/sharepoint_connector.py` - 100%
- `src/api/validators.py` - 98%
- `src/api/models.py` - 97%
- `src/core/cost_tracker.py` - 95%
- `scripts/m365_cis_report.py` - 95%
- `scripts/clean_csv.py` - 98%

### 🎯 Priority 1: High Impact (60-89%)
These files have good coverage but need minor improvements:

| File | Current | Target | Lines to Add |
|------|---------|--------|--------------|
| `src/api/auth_routes.py` | 80% | 90% | ~7 lines |
| `scripts/investigate_security_alerts.py` | 69% | 85% | ~40 lines |
| `src/core/security_alert_manager.py` | 66% | 85% | ~41 lines |
| `scripts/generate_security_dashboard.py` | 66% | 85% | ~24 lines |
| `src/api/app.py` | 63% | 85% | ~8 lines |

**Sub-Total: ~120 lines** (11% of target)

### 🔥 Priority 2: Medium Coverage (30-59%)
These files need significant test additions:

| File | Current | Target | Lines to Add |
|------|---------|--------|--------------|
| `scripts/generate_alert_summary.py` | 57% | 75% | ~42 lines |
| `scripts/remediate_security_alerts.py` | 46% | 70% | ~55 lines |
| `scripts/run_performance_benchmark.py` | 43% | 70% | ~29 lines |

**Sub-Total: ~126 lines** (12% of target)

### ⚠️ Priority 3: Low Coverage (0-29%)
These files are mostly untested:

| File | Current | Target | Strategy |
|------|---------|--------|----------|
| `src/mcp/m365_mcp_server.py` | 44% | 70% | Add MCP server tests |
| `scripts/copilot_tools/__main__.py` | 28% | 60% | Add CLI tests |
| `src/mcp/plugins/sharepoint_tools/tools.py` | 13% | 50% | Add plugin tests |

**Sub-Total: ~200 lines** (18% of target)

### ❌ Exclude from Coverage (Demo/Scripts)
These files are **intentionally excluded** (demo scripts, one-off utilities):
- `scripts/demo_*.py` - 0% (demo files, not meant to be tested)
- `scripts/inspect_*.py` - 0% (debugging utilities)
- `scripts/test_cost_tracking.py` - 0% (manual test script)
- `scripts/sync_cis_csv.py` - 0% (one-time migration script)

**Excluded Lines: ~639 lines**

---

## 🎯 Adjusted Target Calculation

```
Total Lines:           3,327
Excluded Lines:         -639 (demo/debug scripts)
Testable Lines:        2,688
Current Coverage:      1,578 (47%)
Target (80%):          2,150 lines (80% of testable)
Lines Needed:            572 lines
```

**Revised Goal: Add 572 lines of coverage (achievable!)**

---

## 📝 Implementation Plan

### Phase 1: Quick Wins (Week 1) - Target: +200 lines

#### 1.1 Complete API Coverage (+15 lines)
**File**: `src/api/auth_routes.py`
**Current**: 80% → **Target**: 90%

```python
# tests/test_auth_api.py additions
def test_register_missing_fields():
    """Test registration with missing required fields"""
    
def test_login_missing_credentials():
    """Test login with missing username or password"""
    
def test_invalid_json_request():
    """Test endpoints with malformed JSON"""
    
def test_cors_headers():
    """Test CORS headers are properly set"""
```

**File**: `src/api/app.py`
**Current**: 63% → **Target**: 85%

```python
# tests/test_api_app.py (NEW FILE)
def test_app_configuration():
    """Test Flask app is configured correctly"""
    
def test_error_handlers():
    """Test custom error handlers (404, 500)"""
    
def test_app_with_custom_config():
    """Test app creation with custom config"""
```

#### 1.2 Security Alert Coverage (+80 lines)
**Files**: `scripts/investigate_security_alerts.py`, `src/core/security_alert_manager.py`

```python
# tests/test_security_alert_system.py additions
def test_alert_prioritization():
    """Test alerts are prioritized by severity"""
    
def test_alert_correlation():
    """Test related alerts are correlated"""
    
def test_alert_deduplication():
    """Test duplicate alerts are merged"""
    
def test_remediation_suggestion():
    """Test remediation suggestions are generated"""
    
def test_alert_export_formats():
    """Test alert export to JSON/CSV/Excel"""
```

#### 1.3 Dashboard Coverage (+25 lines)
**File**: `scripts/generate_security_dashboard.py`

```python
# tests/test_generate_security_dashboard.py additions
def test_historical_data_handling():
    """Test dashboard with historical trend data"""
    
def test_empty_results():
    """Test dashboard generation with no results"""
    
def test_large_dataset():
    """Test dashboard with 1000+ controls"""
```

#### 1.4 Alert Summary Coverage (+80 lines)
**File**: `scripts/generate_alert_summary.py`

```python
# tests/test_generate_alert_summary.py (NEW FILE)
def test_summary_generation():
    """Test basic summary generation"""
    
def test_summary_with_filters():
    """Test summary with severity filters"""
    
def test_summary_export():
    """Test summary export to multiple formats"""
    
def test_summary_aggregation():
    """Test alert aggregation by type/severity"""
```

---

### Phase 2: Medium Coverage (Week 2) - Target: +200 lines

#### 2.1 Remediation System (+55 lines)
**File**: `scripts/remediate_security_alerts.py`

```python
# tests/test_remediate_security_alerts.py (NEW FILE)
def test_remediation_whatif_mode():
    """Test safe preview mode (no changes)"""
    
def test_remediation_apply():
    """Test actual remediation (mocked M365 calls)"""
    
def test_remediation_rollback():
    """Test rollback on failure"""
    
def test_remediation_logging():
    """Test remediation actions are logged"""
```

#### 2.2 Performance Benchmarks (+29 lines)
**File**: `scripts/run_performance_benchmark.py`

```python
# tests/test_performance_benchmark.py (NEW FILE)
def test_benchmark_csv_cleaning():
    """Test CSV cleaning performance"""
    
def test_benchmark_excel_generation():
    """Test Excel generation performance"""
    
def test_benchmark_comparison():
    """Test baseline vs current comparison"""
    
def test_benchmark_regression_detection():
    """Test performance regression detection"""
```

#### 2.3 Copilot Tools Coverage (+116 lines)
**File**: `scripts/copilot_tools/__main__.py`

```python
# tests/test_copilot_tools_cli.py (NEW FILE)
def test_cli_help():
    """Test CLI help text"""
    
def test_repo_discovery():
    """Test repository discovery"""
    
def test_workspace_health_check():
    """Test workspace health validation"""
    
def test_cli_error_handling():
    """Test CLI error messages"""
```

---

### Phase 3: MCP & Plugins (Week 3) - Target: +172 lines

#### 3.1 MCP Server Coverage (+150 lines)
**File**: `src/mcp/m365_mcp_server.py`

```python
# tests/test_mcp_server.py (NEW FILE)
import pytest
from unittest.mock import Mock, patch

def test_server_initialization():
    """Test MCP server initializes correctly"""
    
def test_server_tool_registration():
    """Test tools are registered properly"""
    
def test_server_request_handling():
    """Test MCP request/response flow"""
    
def test_server_error_handling():
    """Test server handles errors gracefully"""
    
@pytest.mark.asyncio
async def test_async_tool_execution():
    """Test async tool execution"""
```

#### 3.2 SharePoint Plugin Coverage (+22 lines)
**File**: `src/mcp/plugins/sharepoint_tools/tools.py`

```python
# tests/test_sharepoint_plugin.py (NEW FILE)
def test_plugin_loading():
    """Test SharePoint plugin loads correctly"""
    
def test_plugin_tool_registration():
    """Test plugin tools are registered"""
    
def test_sharepoint_analysis_tool():
    """Test SharePoint permissions analysis tool"""
```

---

## 🛠️ New Test Files to Create

### High Priority
1. `tests/test_api_app.py` - Flask app configuration tests
2. `tests/test_generate_alert_summary.py` - Alert summary generation
3. `tests/test_remediate_security_alerts.py` - Remediation system
4. `tests/test_performance_benchmark.py` - Performance benchmarking
5. `tests/test_copilot_tools_cli.py` - CLI tools
6. `tests/test_mcp_server.py` - MCP server
7. `tests/test_sharepoint_plugin.py` - SharePoint MCP plugin

### Medium Priority
8. `tests/test_alert_correlation.py` - Alert correlation logic
9. `tests/test_dashboard_edge_cases.py` - Dashboard edge cases
10. `tests/test_purview_action_plan.py` - Purview integration

---

## 📈 Expected Coverage Progression

```
Current:    47% (1,578 lines)
Phase 1:    60% (1,778 lines) - Week 1
Phase 2:    70% (2,000 lines) - Week 2  
Phase 3:    80% (2,150 lines) - Week 3
```

---

## 🧪 Testing Best Practices

### Use Fixtures for Common Setup
```python
@pytest.fixture
def mock_m365_connection():
    """Mock Microsoft 365 API connections"""
    with patch('src.api.auth_routes.DatabaseManager'):
        yield

@pytest.fixture
def sample_audit_data():
    """Provide sample audit data for tests"""
    return [
        {"ControlId": "1.1.1", "Status": "Pass", ...},
        {"ControlId": "1.1.2", "Status": "Fail", ...},
    ]
```

### Use Parameterized Tests
```python
@pytest.mark.parametrize("severity,expected_count", [
    ("High", 5),
    ("Medium", 10),
    ("Low", 15),
])
def test_alert_filtering(severity, expected_count):
    """Test alert filtering by severity"""
    ...
```

### Mock External Dependencies
```python
@patch('scripts.investigate_security_alerts.requests.get')
def test_api_call(mock_get):
    """Test external API calls are mocked"""
    mock_get.return_value.json.return_value = {"alerts": []}
    ...
```

---

## ✅ Success Criteria

- [ ] Overall coverage ≥ 80%
- [ ] No file below 50% (except excluded demos)
- [ ] All new tests pass
- [ ] CI/CD pipeline updated with coverage checks
- [ ] Coverage badge updated in README

---

## 📝 Notes for AI Agents

### When Creating Tests:
1. Use `TemporaryDirectory()` for file I/O tests
2. Mock all M365 API calls (don't hit real APIs)
3. Use `@pytest.mark.asyncio` for async tests
4. Add docstrings explaining what each test validates
5. Keep tests isolated (no dependencies between tests)

### File Naming Convention:
- Test file: `tests/test_<module_name>.py`
- Test class: `TestModuleName` (CamelCase)
- Test function: `test_<what_is_tested>` (snake_case)

### Coverage Commands:
```sh
# Run tests with coverage
pytest --cov=src --cov=scripts --cov-report=html

# Check specific file
pytest tests/test_specific.py --cov=src.module --cov-report=term-missing

# Update coverage badge
# (Automated via .github/workflows/ci.yml)
```

---

## 🚀 Quick Start

### Step 1: Run Baseline Coverage
```sh
cd E:\source\Heyson315\DjangoWebProject1\Heyson315\Easy-Ai
pytest --cov=src --cov=scripts --cov-report=html --cov-report=term-missing
```

### Step 2: Create First New Test File
```sh
# Start with high-impact file
code tests/test_api_app.py
```

### Step 3: Implement Tests from Phase 1
```sh
# Follow the plan above
# Run tests after each addition
pytest tests/test_api_app.py -v
```

### Step 4: Monitor Progress
```sh
# Check coverage after each phase
pytest --cov=src --cov=scripts --cov-report=term | grep "TOTAL"
```

---

**Last Updated**: December 11, 2025  
**Author**: AI Development Team  
**Status**: Ready for Implementation
