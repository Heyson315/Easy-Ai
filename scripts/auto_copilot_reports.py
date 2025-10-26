#!/usr/bin/env python3
"""
Auto-Copilot Report Generator
Creates Copilot-optimized reports automatically from M365 audit data
"""

import argparse
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import subprocess
import sys

def create_copilot_excel_template(data: dict, output_path: Path):
    """Create Excel template with Copilot-friendly structure"""
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Quick Stats (for instant Copilot analysis)
        if isinstance(data, list):
            df = pd.DataFrame(data)
            
            # Create summary statistics
            quick_stats = {
                'Metric': [
                    'Total Security Controls',
                    'Controls Passed', 
                    'Controls Failed',
                    'High Risk Issues',
                    'Compliance Percentage',
                    'Last Assessment Date',
                    'Next Review Due'
                ],
                'Value': [
                    len(df),
                    len(df[df.get('Status', '') == 'Pass']) if 'Status' in df.columns else 0,
                    len(df[df.get('Status', '') == 'Fail']) if 'Status' in df.columns else 0,
                    len(df[df.get('Severity', '') == 'High']) if 'Severity' in df.columns else 0,
                    f"{(len(df[df.get('Status', '') == 'Pass']) / len(df) * 100):.1f}%" if len(df) > 0 and 'Status' in df.columns else '0%',
                    datetime.now().strftime('%Y-%m-%d'),
                    (datetime.now().replace(month=datetime.now().month + 1) if datetime.now().month < 12 else datetime.now().replace(year=datetime.now().year + 1, month=1)).strftime('%Y-%m-%d')
                ],
                'Copilot_Prompt': [
                    'Ask: "How many security controls do we have?"',
                    'Ask: "What\'s our pass rate?"',
                    'Ask: "Show me all failed controls"',
                    'Ask: "What are our highest risks?"',
                    'Ask: "Are we compliant?"',
                    'Ask: "When was our last assessment?"',
                    'Ask: "When is our next review?"'
                ]
            }
            quick_df = pd.DataFrame(quick_stats)
            quick_df.to_excel(writer, sheet_name='Quick_Stats', index=False)
            
            # Sheet 2: Detailed data with Copilot instructions
            df_with_instructions = df.copy()
            
            # Add a column with suggested Copilot queries
            if not df_with_instructions.empty:
                df_with_instructions['Suggested_Copilot_Query'] = [
                    f"Tell me more about {row.get('ControlId', 'this control')} and how to fix it" 
                    if row.get('Status') == 'Fail' 
                    else f"Explain why {row.get('ControlId', 'this control')} is important"
                    for _, row in df_with_instructions.iterrows()
                ]
            
            df_with_instructions.to_excel(writer, sheet_name='Detailed_Data', index=False)
            
            # Sheet 3: Action items formatted for Copilot task creation
            if 'Status' in df.columns:
                failed_controls = df[df['Status'] == 'Fail'].copy()
                if not failed_controls.empty:
                    tasks = pd.DataFrame({
                        'Task_ID': [f"SEC-{i+1:03d}" for i in range(len(failed_controls))],
                        'Priority': [
                            'P1 - Critical' if sev == 'High' 
                            else 'P2 - Important' if sev == 'Medium' 
                            else 'P3 - Standard' 
                            for sev in failed_controls.get('Severity', ['Medium'] * len(failed_controls))
                        ],
                        'Control_ID': failed_controls.get('ControlId', failed_controls.index),
                        'Task_Title': [f"Remediate: {title}" for title in failed_controls.get('Title', ['Security Control'] * len(failed_controls))],
                        'Description': failed_controls.get('Evidence', 'No details provided'),
                        'Assigned_To': ['Security Team'] * len(failed_controls),
                        'Due_Date': [(datetime.now().replace(day=min(datetime.now().day + 30, 28)).strftime('%Y-%m-%d'))] * len(failed_controls),
                        'Status': ['Not Started'] * len(failed_controls),
                        'Copilot_Action': [
                            f"Ask Copilot: 'Create a project plan for fixing {control_id}'"
                            for control_id in failed_controls.get('ControlId', ['control'] * len(failed_controls))
                        ]
                    })
                    tasks.to_excel(writer, sheet_name='Action_Items', index=False)

def create_copilot_powerpoint_content(data: dict, output_path: Path):
    """Create PowerPoint content outline for Copilot"""
    
    content = f"""# M365 Security Presentation Outline for Copilot

## Slide Structure (Ask Copilot to create these slides)

### Slide 1: Title Slide
**Copilot Prompt**: "Create a professional title slide for M365 Security Assessment Report dated {datetime.now().strftime('%B %Y')}"

### Slide 2: Executive Summary
**Copilot Prompt**: "Create an executive summary slide with these key metrics:"
"""
    
    if isinstance(data, list):
        df = pd.DataFrame(data)
        total = len(df)
        passed = len(df[df.get('Status', '') == 'Pass']) if 'Status' in df.columns else 0
        failed = len(df[df.get('Status', '') == 'Fail']) if 'Status' in df.columns else 0
        
        content += f"""
- Total Controls: {total}
- Compliance Rate: {(passed/total*100):.1f}%
- Critical Issues: {len(df[df.get('Severity', '') == 'High']) if 'Severity' in df.columns else 0}
- Status: {"Compliant" if failed == 0 else "Needs Attention"}

### Slide 3: Security Posture Overview
**Copilot Prompt**: "Create a visual dashboard showing our security status with charts for pass/fail rates and risk levels"

### Slide 4: Key Findings
**Copilot Prompt**: "Create a slide highlighting the most important security findings:"
"""
        
        if 'Status' in df.columns and failed > 0:
            failed_controls = df[df['Status'] == 'Fail']
            high_risk = failed_controls[failed_controls.get('Severity', '') == 'High']
            
            if not high_risk.empty:
                content += "\n**High Priority Issues:**\n"
                for _, control in high_risk.head(3).iterrows():
                    content += f"- {control.get('ControlId', 'Unknown')}: {control.get('Title', 'No title')}\n"
        
        content += """
### Slide 5: Action Plan
**Copilot Prompt**: "Create an action plan slide with timeline and ownership for security remediation"

### Slide 6: Next Steps
**Copilot Prompt**: "Create a next steps slide with specific deliverables and timelines"

## Additional Copilot Commands for Enhancement

1. **Visual Enhancement**: "Add professional security-themed icons and colors to these slides"
2. **Chart Creation**: "Create charts showing security trends and compliance metrics"
3. **Risk Matrix**: "Design a risk matrix showing security issues by impact and likelihood"
4. **Timeline**: "Create a remediation timeline showing priority and dependencies"

## Speaker Notes Prompts

Ask Copilot to "Generate speaker notes for each slide that include":
- Key talking points
- Supporting data
- Anticipated questions
- Transition statements

## Custom Requests

- "Make this presentation suitable for executive audience"
- "Add technical details for IT team review"
- "Create a version focused on compliance requirements"
- "Design slides for board presentation"
"""
    
    output_path.write_text(content, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Generate Copilot-optimized reports from M365 audit data")
    parser.add_argument("--input", required=True, help="Input JSON audit file")
    parser.add_argument("--output-dir", default="output/copilot-reports", help="Output directory for Copilot-ready files")
    
    args = parser.parse_args()
    
    # Load audit data
    with open(args.input, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🤖 Auto-Copilot Report Generator")
    print("=" * 50)
    print(f"Processing: {args.input}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Generate Excel template
    excel_file = output_dir / f"copilot_security_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
    create_copilot_excel_template(data, excel_file)
    print(f"✅ Excel template created: {excel_file}")
    
    # Generate PowerPoint outline
    ppt_file = output_dir / f"copilot_presentation_outline_{datetime.now().strftime('%Y%m%d')}.md"
    create_copilot_powerpoint_content(data, ppt_file)
    print(f"✅ PowerPoint outline created: {ppt_file}")
    
    # Generate Word document content using the existing formatter
    try:
        word_file = output_dir / f"copilot_security_report_{datetime.now().strftime('%Y%m%d')}.md"
        subprocess.run([
            sys.executable, "scripts/copilot_formatter.py",
            "--input", args.input,
            "--word-output", str(word_file)
        ], check=True, capture_output=True)
        print(f"✅ Word content created: {word_file}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Word content generation failed: {e}")
    
    print()
    print("🚀 Next Steps with Copilot:")
    print("1. Open the Excel file and ask: 'Analyze this security data'")
    print("2. In PowerPoint, use the outline to ask: 'Create slides from this content'")
    print("3. In Word, paste the markdown and ask: 'Format this as a professional report'")
    print("4. In Teams, share findings and ask: 'Summarize for leadership team'")
    print()
    print("💡 Pro Tip: Start each Copilot session with context:")
    print("   'I'm reviewing our M365 security audit. [your question]'")

if __name__ == "__main__":
    main()