"""
MCP Plugins Package

This package contains self-contained toolsets (plugins) that can be loaded
dynamically by the MCP server.

Each plugin is a subdirectory containing:
    - plugin.json: Manifest file with name, version, description, entry_point
    - tools.py: Python module with a register_tools(server) function
"""

__all__ = []
