#!/usr/bin/env python3
"""
Security Dashboard Generator
Creates interactive HTML dashboards from M365 CIS audit results
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

DEFAULT_INPUT = "output/reports/security/m365_cis_audit.json"
DEFAULT_OUTPUT = "output/reports/security/dashboard.html"

def load_audit_data(json_path: Path) -> dict:
    """Load audit data from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        print(f"✅ Loaded audit data from {json_path}")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_path}: {e}")
        sys.exit(1)

def generate_dashboard_html(data: dict, output_path: Path):
    """Generate interactive HTML dashboard"""
    try:
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Basic HTML dashboard template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>M365 Security Dashboard</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #0078d4; color: white; padding: 20px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }}
        .status-pass {{ color: #107c10; font-weight: bold; }}
        .status-fail {{ color: #d13438; font-weight: bold; }}
        .timestamp {{ color: #666; font-style: italic; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔐 M365 Security Dashboard</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="card">
            <h3>📊 Audit Summary</h3>
            <p>Total Controls: {len(data) if isinstance(data, list) else 'N/A'}</p>
            <p>Status: <span class="status-pass">Dashboard Generated</span></p>
        </div>
        
        <div class="card">
            <h3>🎯 Quick Stats</h3>
            <p>Data Type: {type(data).__name__}</p>
            <p>Source: M365 CIS Audit</p>
        </div>
    </div>
    
    <div class="card">
        <h3>📋 Audit Data</h3>
        <pre style="background: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto;">
{json.dumps(data, indent=2)[:1000]}{'...' if len(str(data)) > 1000 else ''}
        </pre>
    </div>
    
    <div class="card">
        <h3>🔗 Next Steps</h3>
        <ul>
            <li>Review security control status</li>
            <li>Address any failed controls</li>
            <li>Schedule regular audits</li>
            <li>Update security policies</li>
        </ul>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard generated: {output_path}")
        
    except Exception as e:
        print(f"❌ Failed to generate dashboard: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate interactive HTML security dashboard")
    parser.add_argument("--input", default=DEFAULT_INPUT, help=f"Input JSON file (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Output HTML file (default: {DEFAULT_OUTPUT})")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    print("📊 Security Dashboard Generator")
    print("=" * 40)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Load and convert data
    data = load_audit_data(input_path)
    generate_dashboard_html(data, output_path)
    
    print("🎉 Dashboard generation completed!")

if __name__ == "__main__":
    main()