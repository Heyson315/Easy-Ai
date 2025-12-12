#!/usr/bin/env python3
"""
Demo: Test qwe Integration with Easy-Ai MCP Server

This script demonstrates how the qwe website communicates with
the Easy-Ai MCP server by making the same API calls.

Usage:
    python scripts/test_qwe_integration.py
"""

import requests
import json
from datetime import datetime

def test_endpoint(name, url):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Status: {response.status_code} OK")
            data = response.json()
            print(f"\n📄 Response Data:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: MCP server not running")
        print(f"   Start server with: python scripts/demo_mcp_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run integration tests"""
    print("\n" + "="*60)
    print("🔗 qwe + Easy-Ai Integration Demo")
    print("="*60)
    print()
    print("This simulates the API calls that the qwe website makes")
    print("to the Easy-Ai MCP server.")
    print()
    
    base_url = "http://localhost:8080"
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Security Dashboard", f"{base_url}/api/security/dashboard"),
        ("Active Alerts", f"{base_url}/api/security/alerts"),
        ("Compliance Status", f"{base_url}/api/security/compliance"),
        ("SharePoint Analysis", f"{base_url}/api/security/sharepoint"),
    ]
    
    results = []
    for name, url in tests:
        success = test_endpoint(name, url)
        results.append((name, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working!")
        print("\nNext steps:")
        print("1. Build qwe project in Visual Studio")
        print("2. Run qwe website")
        print("3. Navigate to: /Admin/Security/Dashboard")
    else:
        print("\n⚠️  Some tests failed. Check if MCP server is running:")
        print("   python scripts/demo_mcp_server.py")


if __name__ == "__main__":
    main()
