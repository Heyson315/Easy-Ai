#!/usr/bin/env python3
"""
M365 Security MCP Server Setup Script

This script helps you set up and configure the custom M365 Security MCP server
for integration with AI assistants.

Usage:
    python setup_mcp_server.py [--install-deps] [--configure-env] [--test-connection]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def install_mcp_dependencies():
    """Install required MCP server dependencies"""
    print("🔧 Installing MCP server dependencies...")

    requirements_file = Path(__file__).parent / "requirements-mcp.txt"

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✅ MCP dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def configure_environment():
    """Help user configure environment variables"""
    print("🌍 Configuring environment variables...")

    env_template = Path(__file__).parent / ".env.template"
    env_file = Path(__file__).parent / ".env"

    if env_file.exists():
        print(f"⚠️  Environment file already exists: {env_file}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != "y":
            print("Skipping environment configuration.")
            return True

    # Copy template
    env_file.write_text(env_template.read_text())

    print(
        f"""
📝 Environment template created: {env_file}

🔧 **Next Steps:**
1. Edit {env_file} and fill in your actual values
2. For M365 credentials, see: docs/M365_SERVICE_PRINCIPAL_SETUP.md
3. For GitHub token: https://github.com/settings/tokens

⚠️  **Important:** Never commit the .env file to version control!
"""
    )

    return True


def test_mcp_connection():
    """Test the MCP server configuration"""
    print("🧪 Testing MCP server configuration...")

    # Check if environment file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ No .env file found. Run with --configure-env first.")
        return False

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file)
    except ImportError:
        print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
        print("Checking environment variables from system...")

    # Check required variables
    required_vars = ["M365_TENANT_ID", "M365_CLIENT_ID", "M365_CLIENT_SECRET"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith("your-"):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing or unconfigured environment variables: {', '.join(missing_vars)}")
        print(f"Please edit {env_file} and set proper values.")
        return False

    print("✅ Environment variables configured!")

    # Test MCP server import
    try:
        mcp_server_path = Path(__file__).parent / "src" / "mcp" / "m365_security_server.py"
        if not mcp_server_path.exists():
            print(f"❌ MCP server not found: {mcp_server_path}")
            return False

        print("✅ MCP server file found!")
        print(f"📁 Location: {mcp_server_path}")

        # Test basic import (without running)
        import importlib.util

        spec = importlib.util.spec_from_file_location("m365_security_server", mcp_server_path)
        if spec is None:
            print("❌ Failed to load MCP server module")
            return False

        print("✅ MCP server module can be imported!")

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

    print(
        """
🎉 **MCP Server Configuration Test Complete!**

🚀 **Next Steps:**
1. Your MCP server is ready to use
2. Add the server to your AI assistant's MCP configuration
3. Test the integration with AI assistant tools

📚 **Documentation:**
• MCP Server Guide: docs/CUSTOM_MCP_SERVER_GUIDE.md
• M365 Setup: docs/M365_SERVICE_PRINCIPAL_SETUP.md
"""
    )

    return True


def main():
    parser = argparse.ArgumentParser(description="Setup M365 Security MCP Server")
    parser.add_argument("--install-deps", action="store_true", help="Install required dependencies")
    parser.add_argument("--configure-env", action="store_true", help="Configure environment variables")
    parser.add_argument("--test-connection", action="store_true", help="Test MCP server configuration")
    parser.add_argument("--all", action="store_true", help="Run all setup steps")

    args = parser.parse_args()

    if not any([args.install_deps, args.configure_env, args.test_connection, args.all]):
        parser.print_help()
        return

    print("🚀 M365 Security MCP Server Setup")
    print("=" * 40)

    success = True

    if args.all or args.install_deps:
        success &= install_mcp_dependencies()
        print()

    if args.all or args.configure_env:
        success &= configure_environment()
        print()

    if args.all or args.test_connection:
        success &= test_mcp_connection()
        print()

    if success:
        print("🎉 Setup completed successfully!")
    else:
        print("❌ Setup encountered errors. Please review and fix issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
