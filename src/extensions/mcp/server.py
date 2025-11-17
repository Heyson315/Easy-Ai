#!/usr/bin/env python3
"""
M365 Security Toolkit MCP Server

Custom Model Context Protocol server that integrates AI assistants with
your M365 Security Toolkit, enabling intelligent automation and analysis.

This server provides AI assistants with tools to:
- Execute M365 CIS security audits
- Analyze SharePoint permissions
- Monitor security alerts
- Generate compliance reports
- Automate remediation workflows

Usage:
    python m365_security_server.py

Environment Variables:
    M365_TENANT_ID     - Microsoft 365 Tenant ID
    M365_CLIENT_ID     - Application Client ID
    M365_CLIENT_SECRET - Application Client Secret
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# MCP imports
try:
    from mcp import McpError, Server
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Microsoft Graph imports
try:
    from azure.identity import ClientSecretCredential
    from microsoft.graph import GraphServiceClient
except ImportError:
    print("Warning: Microsoft Graph SDK not installed. Some features may be limited.", file=sys.stderr)


class M365SecurityMCPServer:
    """Custom MCP Server for M365 Security Toolkit integration"""

    def __init__(self):
        self.server = Server("m365-security-toolkit")
        self.graph_client = None
        self.toolkit_path = Path(__file__).parent.parent.parent  # Go up to share report root
        self.setup_logging()
        self.setup_tools()

    def setup_logging(self):
        """Configure logging for the MCP server"""
        log_dir = Path.home() / ".aitk" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_dir / "m365_mcp_server.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("M365 Security MCP Server initializing...")

    def setup_tools(self):
        """Register all available M365 security tools"""

        @self.server.tool("run_security_audit")
        async def run_security_audit(
            timestamped: bool = True, spo_admin_url: Optional[str] = None, skip_purview: bool = False
        ) -> str:
            """
            Execute comprehensive M365 CIS security audit

            Args:
                timestamped: Whether to timestamp the audit results
                spo_admin_url: SharePoint Online admin URL (optional)
                skip_purview: Whether to skip Purview compliance checks

            Returns:
                Audit results summary and file location
            """
            try:
                self.logger.info("Starting M365 CIS security audit...")

                # Build PowerShell command
                script_path = self.toolkit_path / "scripts" / "powershell" / "Invoke-M365CISAudit.ps1"
                cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]

                if timestamped:
                    cmd.append("-Timestamped")
                if spo_admin_url:
                    cmd.extend(["-SPOAdminUrl", spo_admin_url])
                if skip_purview:
                    cmd.append("-SkipPurview")

                # Execute audit
                result = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(self.toolkit_path)
                )

                stdout, stderr = await result.communicate()

                if result.returncode == 0:
                    # Parse results
                    output_file = self.toolkit_path / "output" / "reports" / "security" / "m365_cis_audit.json"
                    if output_file.exists():
                        audit_data = json.loads(output_file.read_text())

                        # Generate summary
                        total_controls = len(audit_data.get("results", []))
                        passed_controls = sum(1 for r in audit_data.get("results", []) if r.get("Status") == "Pass")
                        compliance_percentage = (passed_controls / total_controls * 100) if total_controls > 0 else 0

                        summary = f"""✅ M365 CIS Security Audit Complete!

📊 **Results Summary:**
• Total Controls Tested: {total_controls}
• Controls Passed: {passed_controls}
• Compliance Percentage: {compliance_percentage:.1f}%
• Audit File: {output_file}

🎯 **Next Steps:**
• Review detailed results in the audit file
• Address any failed controls
• Generate remediation plan if needed"""

                        self.logger.info(f"Audit completed successfully. Compliance: {compliance_percentage:.1f}%")
                        return summary
                    else:
                        raise McpError("Audit completed but output file not found")
                else:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    raise McpError(f"Audit failed: {error_msg}")

            except Exception as e:
                self.logger.error(f"Security audit failed: {str(e)}")
                raise McpError(f"Security audit failed: {str(e)}")

        @self.server.tool("analyze_sharepoint_permissions")
        async def analyze_sharepoint_permissions(input_file: str, generate_excel: bool = True) -> str:
            """
            Analyze SharePoint permissions from CSV export

            Args:
                input_file: Path to SharePoint permissions CSV file
                generate_excel: Whether to generate Excel report

            Returns:
                Analysis summary and report location
            """
            try:
                self.logger.info(f"Analyzing SharePoint permissions from {input_file}")

                # First clean the CSV
                clean_script = self.toolkit_path / "scripts" / "clean_csv.py"
                cleaned_file = self.toolkit_path / "data" / "processed" / "sharepoint_permissions_clean.csv"

                cmd = [sys.executable, str(clean_script), "--input", input_file, "--output", str(cleaned_file)]

                result = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await result.communicate()

                if result.returncode != 0:
                    raise McpError(f"CSV cleaning failed: {stderr.decode()}")

                # Generate analysis report
                if generate_excel:
                    output_file = (
                        self.toolkit_path / "output" / "reports" / "business" / "sharepoint_permissions_report.xlsx"
                    )

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
                        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(self.toolkit_path)
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
                        raise McpError(f"Report generation failed: {stderr.decode()}")
                else:
                    return f"""✅ SharePoint Permissions Analysis Complete!

📊 **Analysis Results:**
• Input File: {input_file}
• Cleaned Data: {cleaned_file}

🔍 **CSV cleaning completed successfully.**
📁 Use generate_excel=True for detailed Excel report."""

            except Exception as e:
                self.logger.error(f"SharePoint analysis failed: {str(e)}")
                raise McpError(f"SharePoint analysis failed: {str(e)}")

        @self.server.tool("get_security_dashboard")
        async def get_security_dashboard(include_historical: bool = True, output_format: str = "html") -> str:
            """
            Generate interactive security dashboard

            Args:
                include_historical: Whether to include historical trend data
                output_format: Output format ("html" or "json")

            Returns:
                Dashboard location and summary
            """
            try:
                self.logger.info("Generating security dashboard...")

                script_path = self.toolkit_path / "scripts" / "generate_security_dashboard.py"
                output_file = self.toolkit_path / "output" / "reports" / "security" / f"dashboard.{output_format}"

                cmd = [sys.executable, str(script_path), "--output", str(output_file)]

                if include_historical:
                    cmd.append("--include-historical")

                result = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await result.communicate()

                if result.returncode == 0:
                    return f"""🎯 Security Dashboard Generated!

📊 **Dashboard Features:**
• Real-time security metrics
• Compliance trending
• Risk assessment summaries
• Interactive charts and filters

🌐 **Access Dashboard:**
• File: {output_file}
• Format: {output_format.upper()}

💡 **Next Actions:**
• Open dashboard in web browser
• Review security trends
• Identify areas for improvement"""
                else:
                    raise McpError(f"Dashboard generation failed: {stderr.decode()}")

            except Exception as e:
                self.logger.error(f"Dashboard generation failed: {str(e)}")
                raise McpError(f"Dashboard generation failed: {str(e)}")

        @self.server.tool("remediate_security_issues")
        async def remediate_security_issues(preview_only: bool = True, force_apply: bool = False) -> str:
            """
            Apply automated security remediations

            Args:
                preview_only: Whether to only preview changes (safe mode)
                force_apply: Whether to force apply changes (use with caution)

            Returns:
                Remediation summary and actions taken
            """
            try:
                self.logger.info(f"Starting security remediation (preview_only={preview_only})")

                script_path = self.toolkit_path / "scripts" / "powershell" / "PostRemediateM365CIS.ps1"
                cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]

                if preview_only:
                    cmd.append("-WhatIf")
                elif force_apply:
                    cmd.append("-Force")

                result = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(self.toolkit_path)
                )

                stdout, stderr = await result.communicate()

                if result.returncode == 0:
                    output = stdout.decode()
                    mode = "Preview" if preview_only else "Applied"

                    return f"""🛠️ Security Remediation {mode}!

📋 **Remediation Summary:**
{output}

⚠️ **Important Notes:**
• {'Preview mode - no changes applied' if preview_only else 'Changes have been applied to your M365 tenant'}
• Review all actions before applying in production
• Test changes in non-production environment first

🎯 **Next Steps:**
• {'Run with force_apply=True to apply changes' if preview_only else 'Monitor for any unexpected impacts'}
• Document changes for compliance audit trail"""
                else:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    raise McpError(f"Remediation failed: {error_msg}")

            except Exception as e:
                self.logger.error(f"Security remediation failed: {str(e)}")
                raise McpError(f"Security remediation failed: {str(e)}")

        @self.server.tool("get_compliance_status")
        async def get_compliance_status() -> str:
            """
            Get current M365 compliance status summary

            Returns:
                Compliance status overview
            """
            try:
                # Check for latest audit results
                audit_dir = self.toolkit_path / "output" / "reports" / "security"
                audit_files = list(audit_dir.glob("m365_cis_audit*.json"))

                if not audit_files:
                    return """⚠️ No Recent Audit Data Found

🔍 **Recommendation:**
Run a security audit first to get compliance status:
• Use the 'run_security_audit' tool
• This will generate current compliance metrics
• Results will be available for status reporting"""

                # Get most recent audit file
                latest_audit = max(audit_files, key=lambda f: f.stat().st_mtime)
                audit_data = json.loads(latest_audit.read_text())

                # Calculate compliance metrics
                results = audit_data.get("results", [])
                total_controls = len(results)
                passed_controls = sum(1 for r in results if r.get("Status") == "Pass")
                failed_controls = sum(1 for r in results if r.get("Status") == "Fail")
                manual_controls = sum(1 for r in results if r.get("Status") == "Manual")

                compliance_percentage = (passed_controls / total_controls * 100) if total_controls > 0 else 0

                # Generate status report
                audit_date = audit_data.get("timestamp", "Unknown")

                return f"""📊 M365 Compliance Status Report

🕒 **Last Audit:** {audit_date}

📈 **Compliance Metrics:**
• Overall Compliance: {compliance_percentage:.1f}%
• Controls Passed: {passed_controls}/{total_controls}
• Controls Failed: {failed_controls}
• Manual Review Required: {manual_controls}

🎯 **Compliance Health:**
{self._get_compliance_health_indicator(compliance_percentage)}

📋 **Critical Areas:**
{self._get_critical_areas(results)}

🔄 **Recommendations:**
• {'Excellent compliance posture!' if compliance_percentage >= 90 else 'Address failed controls to improve compliance'}
• Schedule regular audits for continuous monitoring
• Document remediation efforts for audit trail"""

            except Exception as e:
                self.logger.error(f"Compliance status check failed: {str(e)}")
                raise McpError(f"Compliance status check failed: {str(e)}")

    def _get_compliance_health_indicator(self, percentage: float) -> str:
        """Get health indicator based on compliance percentage"""
        if percentage >= 95:
            return "🟢 Excellent (95%+)"
        elif percentage >= 85:
            return "🟡 Good (85-94%)"
        elif percentage >= 70:
            return "🟠 Needs Attention (70-84%)"
        else:
            return "🔴 Critical (Below 70%)"

    def _get_critical_areas(self, results: List[Dict]) -> str:
        """Identify critical areas that need attention"""
        failed_results = [r for r in results if r.get("Status") == "Fail"]

        if not failed_results:
            return "• No critical issues identified"

        # Group by severity
        critical_issues = []
        for result in failed_results[:5]:  # Top 5 issues
            title = result.get("Title", "Unknown Control")
            severity = result.get("Severity", "Medium")
            critical_issues.append(f"• {title} (Severity: {severity})")

        return "\n".join(critical_issues)

    async def authenticate_graph(self) -> bool:
        """Authenticate with Microsoft Graph API"""
        try:
            tenant_id = os.getenv("M365_TENANT_ID")
            client_id = os.getenv("M365_CLIENT_ID")
            client_secret = os.getenv("M365_CLIENT_SECRET")

            if not all([tenant_id, client_id, client_secret]):
                self.logger.warning("M365 credentials not configured. Graph API features will be limited.")
                return False

            credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

            self.graph_client = GraphServiceClient(credential)
            self.logger.info("Microsoft Graph authentication successful")
            return True

        except Exception as e:
            self.logger.error(f"Graph authentication failed: {str(e)}")
            return False

    async def start(self):
        """Start the MCP server"""
        self.logger.info("Starting M365 Security MCP Server...")

        # Attempt Graph authentication
        await self.authenticate_graph()

        # Start the server
        await self.server.start()
        self.logger.info("M365 Security MCP Server started successfully!")


async def main():
    """Main entry point"""
    server = M365SecurityMCPServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
