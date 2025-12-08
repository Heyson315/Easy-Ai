#!/usr/bin/env python3
"""
Manual XSS Vulnerability Test
Test if the current dashboard generator is vulnerable to XSS attacks
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

# Create malicious test data
malicious_results = [
    {
        "ControlId": "<script>alert('XSS1')</script>",
        "Title": "<img src=x onerror=alert('XSS2')>",
        "Severity": "High\"><script>alert('XSS3')</script>",
        "Status": "Fail' onload='alert('XSS4')",
        "Actual": "<svg/onload=alert('XSS5')>",
        "Expected": "Safe value",
        "Evidence": "Test",
        "Reference": "https://example.com",
        "Timestamp": "2025-12-03T00:00:00Z",
    }
]

print("🔍 Testing XSS Vulnerability in Dashboard Generator...\n")

with TemporaryDirectory() as td:
    td = Path(td)

    # Create test JSON
    json_file = td / "test_audit.json"
    json_file.write_text(json.dumps(malicious_results), encoding="utf-8")

    # Generate dashboard
    output_html = td / "test_dashboard.html"

    print(f"📄 Input JSON: {json_file}")
    print(f"📄 Output HTML: {output_html}\n")

    # Import and run generator
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from generate_security_dashboard import calculate_statistics, generate_html_dashboard, load_audit_results

    try:
        # Load and process data
        results = load_audit_results(json_file)
        stats = calculate_statistics(results)

        # Generate dashboard
        generate_html_dashboard(results, stats, [], output_html)

        # Read generated HTML
        html_content = output_html.read_text(encoding="utf-8")

        # Check for vulnerabilities
        print("🔎 Vulnerability Check:")
        print("=" * 60)

        vulnerabilities = []

        if "<script>alert('XSS1')</script>" in html_content:
            vulnerabilities.append("❌ VULNERABLE: Script in ControlId not escaped")
        else:
            print("✅ ControlId: Scripts are escaped")

        if "<img src=x onerror=alert('XSS2')>" in html_content:
            vulnerabilities.append("❌ VULNERABLE: Image tag in Title not escaped")
        else:
            print("✅ Title: Image tags are escaped")

        if "<svg/onload=alert('XSS5')>" in html_content:
            vulnerabilities.append("❌ VULNERABLE: SVG tag in Actual not escaped")
        else:
            print("✅ Actual: SVG tags are escaped")

        # Check if escaped versions exist
        if "&lt;script&gt;" in html_content:
            print("✅ HTML entities found - escaping is working")
        else:
            vulnerabilities.append("⚠️  WARNING: No HTML entities found")

        print("=" * 60)

        if vulnerabilities:
            print("\n🚨 SECURITY ISSUES FOUND:")
            for vuln in vulnerabilities:
                print(f"   {vuln}")
            print("\n💡 PR #87 fixes these issues by adding html.escape()")
        else:
            print("\n✅ No XSS vulnerabilities detected!")
            print("   The code properly escapes user input")

        # Show snippet of generated HTML
        print(f"\n📋 Generated HTML snippet (first 1000 chars):")
        print("-" * 60)
        print(html_content[:1000])
        print("...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

print("\n✅ Test complete!")
