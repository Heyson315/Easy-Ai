"""
MCP Server Extension for M365 Security Toolkit

This extension provides Model Context Protocol (MCP) server functionality,
enabling AI assistants to interact with the M365 security toolkit.

Usage:
    python -m src.extensions.mcp.server

Or:
    python src/extensions/mcp/server.py

For setup and configuration:
    python src/extensions/mcp/setup.py --help
"""

from .server import M365SecurityMCPServer

__all__ = ["M365SecurityMCPServer"]
