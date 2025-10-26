#!/usr/bin/env python3
"""
Copilot Data Formatter
Prepares M365 Security Toolkit data for optimal Copilot consumption
"""

import argparse
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def format_for_copilot_excel(data: dict, output_path: Path):
    """Format audit data for Excel Copilot optimization"""
    
    # Create multiple sheets optimized for different Copilot tasks
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # 1. Executive Summary Sheet (for Copilot executive reports)
        if isinstance(data, list):
            df = pd.DataFrame(data)
            summary_data = {
                'Metric': ['Total Controls', 'Passed', 'Failed', 'Manual Review', 'High Risk', 'Medium Risk', 'Low Risk'],
                'Count': [
                    len(df),
                    len(df[df.get('Status', '') == 'Pass']) if 'Status' in df.columns else 0,
                    len(df[df.get('Status', '') == 'Fail']) if 'Status' in df.columns else 0,
                    len(df[df.get('Status', '') == 'Manual']) if 'Status' in df.columns else 0,
                    len(df[df.get('Severity', '') == 'High']) if 'Severity' in df.columns else 0,
                    len(df[df.get('Severity', '') == 'Medium']) if 'Severity' in df.columns else 0,
                    len(df[df.get('Severity', '') == 'Low']) if 'Severity' in df.columns else 0,
                ],
                'Percentage': [
                    '100%',
                    f"{(len(df[df.get('Status', '') == 'Pass']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Status' in df.columns else '0%',
                    f"{(len(df[df.get('Status', '') == 'Fail']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Status' in df.columns else '0%',
                    f"{(len(df[df.get('Status', '') == 'Manual']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Status' in df.columns else '0%',
                    f"{(len(df[df.get('Severity', '') == 'High']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Severity' in df.columns else '0%',
                    f"{(len(df[df.get('Severity', '') == 'Medium']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Severity' in df.columns else '0%',
                    f"{(len(df[df.get('Severity', '') == 'Low']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Severity' in df.columns else '0%',
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # 2. Detailed Results (for Copilot analysis)
            df.to_excel(writer, sheet_name='Detailed_Results', index=False)
            
            # 3. Action Items (for Copilot task generation)
            if 'Status' in df.columns:
                failed_controls = df[df['Status'] == 'Fail'].copy()
                if not failed_controls.empty:
                    action_items = pd.DataFrame({
                        'Priority': ['High' if sev == 'High' else 'Medium' if sev == 'Medium' else 'Low' 
                                   for sev in failed_controls.get('Severity', ['Medium'] * len(failed_controls))],
                        'Control_ID': failed_controls.get('ControlId', failed_controls.index),
                        'Issue': failed_controls.get('Title', 'No title'),
                        'Current_State': failed_controls.get('Actual', 'Unknown'),
                        'Required_Action': ['Review and remediate ' + title for title in failed_controls.get('Title', ['control'] * len(failed_controls))],
                        'Owner': ['Security Team'] * len(failed_controls),
                        'Due_Date': [(datetime.now().strftime('%Y-%m-%d'))] * len(failed_controls)
                    })
                    action_items.to_excel(writer, sheet_name='Action_Items', index=False)

def format_for_copilot_word(data: dict, output_path: Path):
    """Create Word-friendly markdown for Copilot document generation"""
    
    content = f"""# M365 Security Audit Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report provides a comprehensive analysis of Microsoft 365 security controls based on CIS benchmarks.

### Key Findings
"""
    
    if isinstance(data, list):
        df = pd.DataFrame(data)
        total = len(df)
        passed = len(df[df.get('Status', '') == 'Pass']) if 'Status' in df.columns else 0
        failed = len(df[df.get('Status', '') == 'Fail']) if 'Status' in df.columns else 0
        
        content += f"""
- **Total Controls Evaluated**: {total}
- **Passed Controls**: {passed} ({(passed/total*100):.1f}%)
- **Failed Controls**: {failed} ({(failed/total*100):.1f}%)
- **Overall Compliance Score**: {(passed/total*100):.1f}%

## Security Posture Analysis

### Controls Status Distribution
"""
        
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            for status, count in status_counts.items():
                content += f"- **{status}**: {count} controls\n"
        
        content += "\n### Risk Level Breakdown\n"
        if 'Severity' in df.columns:
            severity_counts = df['Severity'].value_counts()
            for severity, count in severity_counts.items():
                content += f"- **{severity} Risk**: {count} controls\n"
        
        # Add failed controls as action items
        if 'Status' in df.columns:
            failed_controls = df[df['Status'] == 'Fail']
            if not failed_controls.empty:
                content += "\n## Immediate Action Required\n\n"
                for _, control in failed_controls.iterrows():
                    content += f"### {control.get('ControlId', 'Unknown')}: {control.get('Title', 'No title')}\n"
                    content += f"- **Current State**: {control.get('Actual', 'Unknown')}\n"
                    content += f"- **Expected State**: {control.get('Expected', 'Not specified')}\n"
                    content += f"- **Risk Level**: {control.get('Severity', 'Unknown')}\n"
                    content += f"- **Evidence**: {control.get('Evidence', 'No evidence provided')}\n\n"
    
    content += """
## Recommendations

### Short-term Actions (0-30 days)
1. Address all High-risk failed controls
2. Review and update security policies
3. Implement missing MFA requirements

### Medium-term Actions (1-3 months)
1. Remediate Medium-risk controls
2. Enhance monitoring and alerting
3. Conduct user security training

### Long-term Actions (3-6 months)
1. Implement automated compliance monitoring
2. Regular security assessments
3. Continuous improvement program

## Appendix
- Generated by M365 Security Toolkit
- Based on CIS Microsoft 365 Foundations Benchmark
- For technical details, refer to the detailed Excel report
"""
    
    output_path.write_text(content, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Format M365 audit data for Copilot optimization")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--excel-output", help="Output Excel file for Copilot analysis")
    parser.add_argument("--word-output", help="Output Markdown file for Copilot documents")
    
    args = parser.parse_args()
    
    # Load data
    with open(args.input, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    print("🤖 Copilot Data Formatter")
    print("=" * 40)
    
    if args.excel_output:
        excel_path = Path(args.excel_output)
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        format_for_copilot_excel(data, excel_path)
        print(f"✅ Excel file optimized for Copilot: {excel_path}")
    
    if args.word_output:
        word_path = Path(args.word_output)
        word_path.parent.mkdir(parents=True, exist_ok=True)
        format_for_copilot_word(data, word_path)
        print(f"✅ Markdown file optimized for Copilot: {word_path}")
    
    print("\n💡 Copilot Usage Tips:")
    print("1. In Excel: Ask 'Analyze this security data and create a pivot table'")
    print("2. In Word: Ask 'Create an executive summary of this security report'")
    print("3. In PowerPoint: Ask 'Create slides from this security analysis'")
    print("4. In Teams: Ask 'Summarize our security findings for the leadership team'")

if __name__ == "__main__":
    main()