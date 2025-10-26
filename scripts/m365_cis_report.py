#!/usr/bin/env python3
"""
M365 CIS Report Generator
Converts CIS audit JSON results to Excel reports
"""

import argparse
import json
import sys
from pathlib import Path
import pandas as pd

DEFAULT_INPUT = "output/reports/security/m365_cis_audit.json"
DEFAULT_OUTPUT = "output/reports/security/m365_cis_report.xlsx"

def load_cis_data(json_path: Path) -> dict:
    """Load CIS audit data from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        print(f"✅ Loaded CIS audit data from {json_path}")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_path}: {e}")
        sys.exit(1)

def convert_to_excel(data: dict, output_path: Path):
    """Convert CIS data to Excel format"""
    try:
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to DataFrame (basic implementation)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'results' in data:
            df = pd.DataFrame(data['results'])
        else:
            df = pd.DataFrame([data])
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CIS_Audit_Results', index=False)
        
        print(f"✅ Excel report generated: {output_path}")
        
    except Exception as e:
        print(f"❌ Failed to generate Excel report: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert M365 CIS audit JSON to Excel report")
    parser.add_argument("--input", default=DEFAULT_INPUT, help=f"Input JSON file (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Output Excel file (default: {DEFAULT_OUTPUT})")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    print("🔐 M365 CIS Report Generator")
    print("=" * 40)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Load and convert data
    data = load_cis_data(input_path)
    convert_to_excel(data, output_path)
    
    print("🎉 Report generation completed!")

if __name__ == "__main__":
    main()