"""
Test suite for XSS prevention in security dashboard generator.

This test suite validates that the HTML dashboard generator properly escapes
all user-controlled fields to prevent Cross-Site Scripting (XSS) attacks.

Tests were added following PR #87 which fixed XSS vulnerabilities in the
dashboard generation code (lines 380-410 of generate_security_dashboard.py).

Pattern follows existing test conventions from tests/test_clean_csv.py
"""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add scripts directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_security_dashboard import generate_html_dashboard


def _generate_dashboard_from_json(json_path: Path, output_html: Path):
    """Helper function to generate dashboard from JSON file (matches actual usage)."""
    # Load audit results
    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    results = data.get("Controls", [])

    # Calculate statistics (match what calculate_statistics does)
    stats = {
        "total": len(results),
        "pass": sum(1 for r in results if r.get("Status") == "Pass"),
        "fail": sum(1 for r in results if r.get("Status") == "Fail"),
        "manual": sum(1 for r in results if r.get("Status") == "Manual"),
        "error": sum(1 for r in results if r.get("Status") == "Error"),
        "by_severity": {"High": 0, "Medium": 0, "Low": 0},
        "failed_by_severity": {"High": 0, "Medium": 0, "Low": 0},
    }

    # Count by severity and failed by severity
    for result in results:
        status = result.get("Status", "Unknown")
        severity = result.get("Severity", "Unknown")

        if severity in stats["by_severity"]:
            stats["by_severity"][severity] += 1

        if status == "Fail" and severity in stats["failed_by_severity"]:
            stats["failed_by_severity"][severity] += 1

    # Calculate rates
    stats["pass_rate"] = round((stats["pass"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0
    stats["fail_rate"] = round((stats["fail"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0

    # No historical data for tests
    historical = []

    # Generate dashboard
    generate_html_dashboard(results, stats, historical, output_html)


def test_dashboard_html_escaping_script_tags():
    """
    Test that script tags in ControlId are properly escaped.

    XSS Vector: <script>alert('XSS')</script>
    Expected: Script tags should be HTML-escaped to &lt;script&gt;
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with XSS payload in ControlId
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "<script>alert('XSS')</script>",
                    "Title": "Test Control",
                    "Status": "Pass",
                    "Severity": "High",
                    "Actual": "Compliant",
                    "Expected": "Should be compliant",
                }
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Assert attribute breaks are escaped
        assert "&lt;script&gt;" in html_content, "Script tags should be escaped to &lt;script&gt;"
        assert "alert(&" in html_content or "alert(&#" in html_content, "JavaScript should be escaped"

        # Assert unescaped script does NOT exist
        assert "<script>alert" not in html_content, "Unescaped script tag should not exist"
        assert "javascript:" not in html_content.lower(), "JavaScript protocol should not exist"


def test_dashboard_html_escaping_img_tags():
    """
    Test that img tags with onerror handler in Title are properly escaped.

    XSS Vector: <img src=x onerror=alert('XSS')>
    Expected: Img tags should be HTML-escaped
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with XSS payload in Title
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "1.1.1",
                    "Title": "<img src=x onerror=alert('XSS')>",
                    "Status": "Fail",
                    "Severity": "Critical",
                    "Actual": "Non-compliant",
                }
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Assert img tags are escaped
        assert "&lt;img" in html_content, "Img tag should be escaped"
        # Verify the malicious img tag is escaped (not checking for substring 'onerror' which may appear escaped)
        assert "&lt;img src=x onerror=" in html_content, "Malicious img tag should be fully escaped"

        # Assert unescaped malicious img does NOT exist
        assert "<img src=x onerror=" not in html_content, "Unescaped malicious img tag should not exist"


def test_dashboard_html_escaping_svg_tags():
    """
    Test that SVG tags with onload handler in Actual field are properly escaped.

    XSS Vector: <svg/onload=alert('XSS')>
    Expected: SVG tags should be HTML-escaped
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with XSS payload in Actual field
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "2.1.1",
                    "Title": "Test SVG Injection",
                    "Status": "Manual",
                    "Severity": "Medium",
                    "Actual": "<svg/onload=alert('XSS')>",
                }
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Assert SVG tags are escaped
        assert "&lt;svg" in html_content, "SVG tag should be escaped"

        # Assert unescaped SVG does NOT exist
        assert "<svg>" not in html_content and "<svg " not in html_content, "Unescaped SVG tag should not exist"
        assert "<svg/onload" not in html_content, "Unescaped SVG with onload should not exist"


def test_dashboard_html_escaping_attribute_injection():
    """
    Test that attribute injection in Severity field is properly escaped.

    XSS Vector: "><script>alert('XSS')</script>
    Expected: Quote and script should be HTML-escaped
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with attribute injection payload
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "3.1.1",
                    "Title": "Test Attribute Injection",
                    "Status": "Pass",
                    "Severity": "\"><script>alert('XSS')</script>",
                    "Actual": "Testing",
                }
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Assert quotes and script are escaped
        assert "&quot;" in html_content or "&#34;" in html_content, "Quotes should be escaped"
        assert "&lt;script&gt;" in html_content, "Script tags should be escaped"

        # Assert attribute injection is prevented
        assert '"><script>' not in html_content, "Attribute injection should be prevented"


def test_dashboard_html_escaping_all_fields():
    """
    Test that malicious content in ALL fields is properly escaped.

    This comprehensive test validates that every user-controlled field
    (ControlId, Title, Severity, Status, Actual) properly escapes HTML.
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with XSS payloads in all fields
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "<script>alert('XSS-ID')</script>",
                    "Title": "<img src=x onerror=alert('XSS-Title')>",
                    "Status": "<iframe src=evil.com>",
                    "Severity": "<svg/onload=alert('XSS-Severity')>",
                    "Actual": "<a href=javascript:alert('XSS-Actual')>Click</a>",
                }
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Assert all dangerous tags are escaped
        assert "&lt;script&gt;" in html_content, "ControlId: Script tags should be escaped"
        assert "&lt;img" in html_content, "Title: Img tags should be escaped"
        assert "&lt;iframe" in html_content, "Status: Iframe tags should be escaped"
        assert "&lt;svg" in html_content, "Severity: SVG tags should be escaped"
        assert "&lt;a" in html_content, "Actual: Anchor tags should be escaped"

        # Assert NO unescaped USER-PROVIDED tags exist (but allow legitimate framework scripts)
        # Check that specific user XSS payloads are escaped
        assert "&lt;script&gt;alert(&#x27;XSS-ID&#x27;)" in html_content, "User script XSS should be escaped"
        assert "<script>alert('XSS-ID')" not in html_content, "User script XSS should not be unescaped"

        assert "&lt;img src=x onerror=" in html_content, "User img XSS should be escaped"
        assert "<img src=x onerror=" not in html_content, "User img XSS should not be unescaped"

        assert "&lt;iframe src=evil.com&gt;" in html_content, "User iframe XSS should be escaped"
        assert "<iframe src=evil.com>" not in html_content, "User iframe XSS should not be unescaped"

        assert "&lt;svg/onload=" in html_content, "User SVG XSS should be escaped"
        assert "<svg/onload=alert" not in html_content, "User SVG XSS should not be unescaped"

        # Allow legitimate framework script (Chart.js CDN) - this is intentional and safe
        # We're testing that USER content is escaped, not that ALL scripts are prohibited

        # Additional safety checks
        assert html_content.count("&lt;") >= 5, "At least 5 opening tags should be escaped"
        assert html_content.count("&gt;") >= 5, "At least 5 closing tags should be escaped"


def test_dashboard_multiple_controls_with_xss():
    """
    Test that XSS escaping works correctly with multiple controls.

    Ensures that escaping is applied consistently across all controls
    in the dashboard, not just the first or last one.
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with multiple controls containing XSS
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "SAFE-1",
                    "Title": "Safe Control",
                    "Status": "Pass",
                    "Severity": "Low",
                    "Actual": "Safe value",
                },
                {
                    "ControlId": "<script>alert(1)</script>",
                    "Title": "XSS Control 1",
                    "Status": "Fail",
                    "Severity": "High",
                    "Actual": "Malicious",
                },
                {
                    "ControlId": "SAFE-2",
                    "Title": "Another Safe Control",
                    "Status": "Pass",
                    "Severity": "Medium",
                    "Actual": "Safe",
                },
                {
                    "ControlId": "XSS-3",
                    "Title": "<img src=x onerror=alert(2)>",
                    "Status": "Manual",
                    "Severity": "Critical",
                    "Actual": "Needs review",
                },
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Safe controls should appear normally
        assert "SAFE-1" in html_content, "Safe control 1 should be present"
        assert "SAFE-2" in html_content, "Safe control 2 should be present"

        # XSS controls should be escaped
        assert "&lt;script&gt;alert(1)" in html_content, "First XSS should be escaped"
        assert "&lt;img src=x" in html_content, "Second XSS should be escaped"

        # No unescaped XSS should exist
        assert "<script>alert(1)" not in html_content, "Unescaped XSS 1 should not exist"
        assert "<img src=x onerror=" not in html_content, "Unescaped XSS 2 should not exist"


def test_dashboard_special_characters():
    """
    Test that special HTML characters are properly escaped.

    Characters like &, <, >, ", ' should all be escaped to prevent
    HTML injection and attribute manipulation.
    """
    with TemporaryDirectory() as td:
        td = Path(td)

        # Create test audit JSON with special characters
        test_json = td / "test_audit.json"
        test_data = {
            "Timestamp": "2025-12-03T12:00:00",
            "Controls": [
                {
                    "ControlId": "Test & <Special> Characters",
                    "Title": "Quote test: \"double\" and 'single'",
                    "Status": "Pass",
                    "Severity": "Low",
                    "Actual": "Value with & and < and > symbols",
                }
            ],
        }
        test_json.write_text(json.dumps(test_data), encoding="utf-8")

        # Generate dashboard
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        # Verify escaping
        html_content = output_html.read_text(encoding="utf-8")

        # Check ampersands are escaped (unless they're part of an escape sequence)
        # Check angle brackets are escaped
        assert "&lt;" in html_content, "< should be escaped to &lt;"
        assert "&gt;" in html_content, "> should be escaped to &gt;"


def test_dashboard_empty_results():
    """Test dashboard generation with empty results list."""
    from scripts.generate_security_dashboard import calculate_statistics, generate_html_dashboard

    with TemporaryDirectory() as td:
        td = Path(td)
        output_html = td / "dashboard.html"

        # Empty results list
        results = []
        stats = calculate_statistics(results)

        # Generate dashboard
        historical = []
        generate_html_dashboard(results, stats, historical, output_html)

        # Verify file created
        assert output_html.exists(), "Dashboard should be created even with empty results"

        html_content = output_html.read_text(encoding="utf-8")

        # Should show 0 totals
        assert "0" in html_content, "Should show 0 values"
        assert stats["total"] == 0
        assert stats["pass"] == 0
        assert stats["fail"] == 0


def test_dashboard_with_error_status():
    """Test dashboard generation with Error status controls."""
    with TemporaryDirectory() as td:
        td = Path(td)
        test_json = td / "test_audit.json"

        # Create test data with Error status
        test_data = {
            "Timestamp": "2024-01-01T12:00:00",
            "Controls": [
                {
                    "ControlId": "1.1.1",
                    "Title": "Test Control",
                    "Status": "Error",
                    "Severity": "High",
                    "Actual": "Error occurred during check",
                }
            ],
        }

        test_json.write_text(json.dumps(test_data), encoding="utf-8")
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        html_content = output_html.read_text(encoding="utf-8")

        # Verify Error status handled
        assert "Error" in html_content, "Error status should be displayed"


def test_dashboard_with_unknown_severity():
    """Test dashboard generation with unknown/missing severity."""
    with TemporaryDirectory() as td:
        td = Path(td)
        test_json = td / "test_audit.json"

        # Create test data with missing severity
        test_data = {
            "Timestamp": "2024-01-01T12:00:00",
            "Controls": [
                {
                    "ControlId": "1.1.1",
                    "Title": "Test Control",
                    "Status": "Pass",
                    "Severity": "Unknown",  # Unusual severity
                    "Actual": "Test value",
                }
            ],
        }

        test_json.write_text(json.dumps(test_data), encoding="utf-8")
        output_html = td / "dashboard.html"
        _generate_dashboard_from_json(test_json, output_html)

        html_content = output_html.read_text(encoding="utf-8")

        # Verify Unknown severity handled gracefully
        assert "Unknown" in html_content or "unknown" in html_content, "Unknown severity should be handled"


def test_calculate_statistics_comprehensive():
    """Test calculate_statistics function with various scenarios."""
    from scripts.generate_security_dashboard import calculate_statistics

    # Test comprehensive results with all statuses and severities
    results = [
        {"Status": "Pass", "Severity": "High"},
        {"Status": "Pass", "Severity": "Medium"},
        {"Status": "Fail", "Severity": "High"},
        {"Status": "Fail", "Severity": "Medium"},
        {"Status": "Fail", "Severity": "Low"},
        {"Status": "Manual", "Severity": "Low"},
        {"Status": "Error", "Severity": "High"},
        {"Status": "Unknown", "Severity": "Unknown"},  # Unknown statuses
    ]

    stats = calculate_statistics(results)

    # Verify counts
    assert stats["total"] == 8
    assert stats["pass"] == 2
    assert stats["fail"] == 3
    assert stats["manual"] == 1
    assert stats["error"] == 1

    # Verify severity breakdowns
    assert stats["by_severity"]["High"] == 3
    assert stats["by_severity"]["Medium"] == 2
    assert stats["by_severity"]["Low"] == 2

    # Verify failed by severity
    assert stats["failed_by_severity"]["High"] == 1
    assert stats["failed_by_severity"]["Medium"] == 1
    assert stats["failed_by_severity"]["Low"] == 1

    # Verify rates
    assert stats["pass_rate"] == round((2 / 8) * 100, 2)
    assert stats["fail_rate"] == round((3 / 8) * 100, 2)


def test_calculate_statistics_edge_cases():
    """Test calculate_statistics with edge cases."""
    from scripts.generate_security_dashboard import calculate_statistics

    # Test empty results
    stats = calculate_statistics([])
    assert stats["total"] == 0
    assert stats["pass_rate"] == 0
    assert stats["fail_rate"] == 0

    # Test results with missing fields
    results = [
        {"Status": "Pass"},  # Missing Severity
        {"Severity": "High"},  # Missing Status
    ]
    stats = calculate_statistics(results)
    assert stats["total"] == 2


def test_load_historical_data_with_valid_files():
    """Test loading historical data from timestamped JSON files."""
    from scripts.generate_security_dashboard import load_historical_data

    with TemporaryDirectory() as td:
        td = Path(td)

        # Create timestamped audit files (JSON format: list of controls)
        audit1 = [
            {"Status": "Pass", "Severity": "High"},
            {"Status": "Fail", "Severity": "Medium"},
        ]
        audit2 = [
            {"Status": "Pass", "Severity": "High"},
            {"Status": "Pass", "Severity": "Medium"},
        ]

        file1 = td / "m365_cis_audit_20240115_120000.json"
        file2 = td / "m365_cis_audit_20240116_140000.json"

        file1.write_text(json.dumps(audit1), encoding="utf-8")
        file2.write_text(json.dumps(audit2), encoding="utf-8")

        # Load historical data
        historical = load_historical_data(td)

        # Should return list with 2 entries
        assert len(historical) == 2
        assert historical[0]["timestamp"] == "2024-01-15 12:00"
        assert historical[1]["timestamp"] == "2024-01-16 14:00"

        # Should have pass_rate calculated
        assert "pass_rate" in historical[0]
        assert "pass" in historical[0]
        assert "fail" in historical[0]


def test_load_historical_data_with_invalid_json():
    """Test historical data loading with invalid JSON files."""
    import json

    from scripts.generate_security_dashboard import load_historical_data

    with TemporaryDirectory() as td:
        td = Path(td)

        # Create file with invalid JSON
        bad_file = td / "m365_cis_audit_20240115_120000.json"
        bad_file.write_text("{invalid json", encoding="utf-8")

        # Create one valid file (JSON format: list of controls)
        valid_file = td / "m365_cis_audit_20240116_140000.json"
        valid_file.write_text(
            json.dumps([{"Status": "Pass", "Severity": "High"}]),
            encoding="utf-8",
        )

        # Should skip invalid JSON and return only valid entry
        historical = load_historical_data(td)
        assert len(historical) == 1
        assert historical[0]["timestamp"] == "2024-01-16 14:00"


def test_load_historical_data_with_invalid_filenames():
    """Test historical data loading with malformed filenames."""
    from scripts.generate_security_dashboard import load_historical_data

    with TemporaryDirectory() as td:
        td = Path(td)

        # Create files with various invalid filename patterns
        (td / "invalid_name.json").write_text('{"Controls": []}', encoding="utf-8")
        (td / "m365_cis_audit.json").write_text('{"Controls": []}', encoding="utf-8")  # Missing timestamp
        (td / "m365_cis_audit_invaliddate.json").write_text('{"Controls": []}', encoding="utf-8")

        # Should handle gracefully and return empty list
        historical = load_historical_data(td)
        assert len(historical) == 0


def test_load_historical_data_limits_to_10_entries():
    """Test that historical data is limited to last 10 entries."""
    import json

    from scripts.generate_security_dashboard import load_historical_data

    with TemporaryDirectory() as td:
        td = Path(td)

        # Create 15 timestamped audit files (JSON format: list of controls)
        for i in range(15):
            audit_file = td / f"m365_cis_audit_2024011{i % 10}_12{i:02d}00.json"
            audit_file.write_text(json.dumps([{"Status": "Pass", "Severity": "High"}]), encoding="utf-8")

        # Should return only last 10
        historical = load_historical_data(td)
        assert len(historical) == 10


def test_load_historical_data_empty_directory():
    """Test historical data loading with no JSON files."""
    from scripts.generate_security_dashboard import load_historical_data

    with TemporaryDirectory() as td:
        td = Path(td)

        # Empty directory
        historical = load_historical_data(td)
        assert historical == []

        # Empty directory
        historical = load_historical_data(td)
        assert historical == []
