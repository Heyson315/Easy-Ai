"""
SharePoint Tools Plugin

Provides tools for analyzing SharePoint Online sites and permissions.
This plugin is loaded dynamically by the MCP server.
"""

import asyncio
import sys
from pathlib import Path


def register_tools(server, toolkit_path: Path = None) -> None:
    """
    Register SharePoint tools with the MCP server.

    Args:
        server: The MCP Server instance to register tools with
        toolkit_path: Path to the toolkit root directory (optional)
    """
    if toolkit_path is None:
        # Default to repository root
        toolkit_path = Path(__file__).parent.parent.parent.parent.parent

    @server.tool("analyze_sharepoint_permissions")
    async def analyze_sharepoint_permissions(input_file: str, generate_excel: bool = True) -> str:
        """
        Analyze SharePoint permissions from CSV export.

        Args:
            input_file: Path to SharePoint permissions CSV file
            generate_excel: Whether to generate Excel report

        Returns:
            Analysis summary and report location
        """
        try:
            # First clean the CSV
            clean_script = toolkit_path / "scripts" / "clean_csv.py"
            cleaned_file = toolkit_path / "data" / "processed" / "sharepoint_permissions_clean.csv"

            cmd = [sys.executable, str(clean_script), "--input", input_file, "--output", str(cleaned_file)]

            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                raise Exception(f"CSV cleaning failed: {stderr.decode()}")

            # Generate analysis report
            if generate_excel:
                output_file = toolkit_path / "output" / "reports" / "business" / "sharepoint_permissions_report.xlsx"

                cmd = [
                    sys.executable,
                    "-m",
                    "src.integrations.sharepoint_connector",
                    "--input",
                    str(cleaned_file),
                    "--output",
                    str(output_file),
                ]

                result = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(toolkit_path)
                )

                stdout, stderr = await result.communicate()

                if result.returncode == 0:
                    return f"""✅ SharePoint Permissions Analysis Complete!

📊 **Analysis Results:**
• Input File: {input_file}
• Cleaned Data: {cleaned_file}
• Excel Report: {output_file}

🔍 **Analysis includes:**
• Permission summaries by site
• User access patterns
• External sharing risks
• Recommendations for optimization

📁 Open the Excel report for detailed insights!"""
                else:
                    raise Exception(f"Report generation failed: {stderr.decode()}")
            else:
                return f"""✅ SharePoint Permissions Analysis Complete!

📊 **Analysis Results:**
• Input File: {input_file}
• Cleaned Data: {cleaned_file}

🔍 **CSV cleaning completed successfully.**
📁 Use generate_excel=True for detailed Excel report."""

        except Exception as e:
            raise Exception(f"SharePoint analysis failed: {str(e)}")

    @server.tool("get_sharepoint_site_info")
    async def get_sharepoint_site_info(site_url: str) -> str:
        """
        Get information about a SharePoint site.

        Args:
            site_url: The URL of the SharePoint site to analyze

        Returns:
            Site information summary
        """
        # This is a placeholder for future Graph API integration
        return f"""📊 SharePoint Site Information

🌐 **Site URL:** {site_url}

⚠️ **Note:** This feature requires Microsoft Graph API authentication.
Configure your credentials in the .env file:
• M365_TENANT_ID
• M365_CLIENT_ID
• M365_CLIENT_SECRET

💡 **Alternative:**
Export site permissions using SharePoint admin center
and use the 'analyze_sharepoint_permissions' tool."""
