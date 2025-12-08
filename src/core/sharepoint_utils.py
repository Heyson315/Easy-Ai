"""
Shared SharePoint analysis utilities for M365 Security Toolkit MCP servers.

Provides reusable functions for SharePoint permissions analysis that can be
called from multiple MCP server implementations.
"""

from pathlib import Path
from typing import Tuple

from src.core.subprocess_utils import run_python_module, run_python_script


async def analyze_sharepoint_permissions(
    input_file: str,
    toolkit_path: Path,
    generate_excel: bool = True,
) -> Tuple[bool, str]:
    """
    Analyze SharePoint permissions from CSV export.

    This is a shared implementation that can be used by multiple MCP servers
    to avoid code duplication.

    Args:
        input_file: Path to SharePoint permissions CSV file
        toolkit_path: Path to the toolkit root directory
        generate_excel: Whether to generate Excel report

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Step 1: Clean the CSV
        clean_script = toolkit_path / "scripts" / "clean_csv.py"
        cleaned_file = toolkit_path / "data" / "processed" / "sharepoint_permissions_clean.csv"

        returncode, stdout, stderr = await run_python_script(
            clean_script,
            args=["--input", input_file, "--output", str(cleaned_file)],
        )

        if returncode != 0:
            return False, f"CSV cleaning failed: {stderr}"

        # Step 2: Generate analysis report (if requested)
        if generate_excel:
            output_file = toolkit_path / "output" / "reports" / "business" / "sharepoint_permissions_report.xlsx"

            returncode, stdout, stderr = await run_python_module(
                "src.integrations.sharepoint_connector",
                args=["--input", str(cleaned_file), "--output", str(output_file)],
                cwd=toolkit_path,
            )

            if returncode == 0:
                return (
                    True,
                    f"""✅ SharePoint Permissions Analysis Complete!

📊 **Analysis Results:**
• Input File: {input_file}
• Cleaned Data: {cleaned_file}
• Excel Report: {output_file}

🔍 **Analysis includes:**
• Permission summaries by site
• User access patterns
• External sharing risks
• Recommendations for optimization

📁 Open the Excel report for detailed insights!""",
                )

            return False, f"Report generation failed: {stderr}"

        return (
            True,
            f"""✅ SharePoint Permissions Analysis Complete!

📊 **Analysis Results:**
• Input File: {input_file}
• Cleaned Data: {cleaned_file}

🔍 **CSV cleaning completed successfully.**
📁 Use generate_excel=True for detailed Excel report.""",
            )

    except Exception as e:
        return False, f"SharePoint analysis failed: {str(e)}"
