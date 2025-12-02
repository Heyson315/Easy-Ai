#!/usr/bin/env python3
"""
M365 Security Toolkit MCP Server with Plugin Architecture

Custom Model Context Protocol server that integrates AI assistants with
your M365 Security Toolkit, enabling intelligent automation and analysis.

This server supports a plugin-based architecture for on-demand tool loading,
making the system more modular, performant, and scalable.

Key Features:
- Dynamic plugin discovery from src/mcp/plugins/
- On-demand plugin loading via load_toolset tool
- Built-in plugin management tools (list_available_toolsets, load_toolset)
- Integration with existing M365 security toolkit functionality

Usage:
    python -m src.mcp.m365_mcp_server

Environment Variables:
    M365_TENANT_ID     - Microsoft 365 Tenant ID
    M365_CLIENT_ID     - Application Client ID
    M365_CLIENT_SECRET - Application Client Secret
"""

import asyncio
import importlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# MCP imports
try:
    from mcp import ErrorData, McpError
    from mcp.server import FastMCP
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


def create_mcp_error(message: str, code: int = -32603) -> McpError:
    """Helper to create MCP errors with proper ErrorData format."""
    return McpError(ErrorData(code=code, message=message))


class PluginInfo:
    """Information about a discovered plugin."""

    def __init__(self, name: str, version: str, description: str, entry_point: str, path: Path):
        self.name = name
        self.version = version
        self.description = description
        self.entry_point = entry_point
        self.path = path
        self.loaded = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": "loaded" if self.loaded else "unloaded",
        }


class M365MCPServer:
    """
    Custom MCP Server for M365 Security Toolkit with Plugin Architecture

    This server provides AI assistants with tools to manage and load plugins
    dynamically, enabling modular security analysis and automation.
    """

    def __init__(self):
        self.server = FastMCP("m365-security-toolkit")
        self.toolkit_path = Path(__file__).parent.parent.parent  # Go up to share report root
        self.plugins_path = Path(__file__).parent / "plugins"
        self._discovered_plugins: Dict[str, PluginInfo] = {}
        self._loaded_plugins: Set[str] = set()
        self.setup_logging()
        self._discover_plugins()
        self._setup_management_tools()

    def setup_logging(self) -> None:
        """Configure logging for the MCP server."""
        log_dir = Path.home() / ".aitk" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_dir / "m365_mcp_server.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("M365 MCP Server initializing...")

    def _discover_plugins(self) -> None:
        """
        Scan the plugins directory and populate the list of available plugins.

        Each plugin must have a plugin.json manifest file with:
        - name: Plugin name
        - version: Plugin version
        - description: Plugin description
        - entry_point: Module and function to call (e.g., "tools:register_tools")
        """
        self.logger.info(f"Discovering plugins from {self.plugins_path}")

        if not self.plugins_path.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_path}")
            return

        for plugin_dir in self.plugins_path.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Skip __pycache__ and other internal directories
            if plugin_dir.name.startswith("__"):
                continue

            manifest_file = plugin_dir / "plugin.json"
            if not manifest_file.exists():
                self.logger.warning(f"Plugin manifest not found for {plugin_dir.name}")
                continue

            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                plugin_info = PluginInfo(
                    name=manifest.get("name", plugin_dir.name),
                    version=manifest.get("version", "0.0.0"),
                    description=manifest.get("description", "No description"),
                    entry_point=manifest.get("entry_point", "tools:register_tools"),
                    path=plugin_dir,
                )
                self._discovered_plugins[plugin_info.name] = plugin_info
                self.logger.info(f"Discovered plugin: {plugin_info.name} v{plugin_info.version}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in plugin manifest for {plugin_dir.name}: {e}")
            except (PermissionError, IOError) as e:
                self.logger.error(f"Cannot read plugin manifest for {plugin_dir.name}: {e}")

        self.logger.info(f"Discovered {len(self._discovered_plugins)} plugins")

    def _load_plugin(self, plugin_name: str) -> str:
        """
        Dynamically load a plugin by name.

        Args:
            plugin_name: The name of the plugin to load

        Returns:
            Success or error message

        Raises:
            McpError: If plugin loading fails
        """
        # Check if plugin exists
        if plugin_name not in self._discovered_plugins:
            raise create_mcp_error(
                f"Plugin not found: {plugin_name}. Use list_available_toolsets to see available plugins."
            )

        plugin = self._discovered_plugins[plugin_name]

        # Check if already loaded
        if plugin_name in self._loaded_plugins:
            return f"Plugin '{plugin_name}' is already loaded."

        # Parse entry point (format: "module:function")
        entry_parts = plugin.entry_point.split(":")
        if len(entry_parts) != 2:
            raise create_mcp_error(f"Invalid entry_point format for {plugin_name}: {plugin.entry_point}")

        module_name, function_name = entry_parts

        try:
            # Build the full module path
            # Format: src.mcp.plugins.<plugin_name>.<module_name>
            full_module_path = f"src.mcp.plugins.{plugin_name}.{module_name}"

            # Import the module dynamically
            module = importlib.import_module(full_module_path)

            # Get the register function
            register_func = getattr(module, function_name, None)
            if register_func is None:
                raise create_mcp_error(f"Function '{function_name}' not found in module '{full_module_path}'")

            # Call the register function with server and toolkit_path
            register_func(self.server, self.toolkit_path)

            # Mark as loaded
            self._loaded_plugins.add(plugin_name)
            plugin.loaded = True

            self.logger.info(f"Loaded plugin: {plugin_name}")
            return f"Successfully loaded plugin '{plugin_name}' v{plugin.version}"

        except ModuleNotFoundError as e:
            raise create_mcp_error(f"Module not found for plugin {plugin_name}: {e}")
        except AttributeError as e:
            raise create_mcp_error(f"Entry point function not found for {plugin_name}: {e}")
        except Exception as e:
            raise create_mcp_error(f"Failed to load plugin {plugin_name}: {e}")

    def _setup_management_tools(self) -> None:
        """Register the built-in plugin management tools."""

        @self.server.tool("list_available_toolsets")
        async def list_available_toolsets() -> str:
            """
            List all available plugins (toolsets) and their current status.

            Returns:
                A formatted list of all discovered plugins with their
                name, version, description, and loaded/unloaded status.
            """
            if not self._discovered_plugins:
                return """📦 No Plugins Found

The plugins directory appears to be empty.

📁 **Plugin Directory:** src/mcp/plugins/

💡 **To create a plugin:**
1. Create a subdirectory in the plugins folder
2. Add a plugin.json manifest file
3. Add a tools.py with a register_tools(server) function

See documentation for more details."""

            # Build formatted response
            lines = ["📦 **Available Toolsets (Plugins)**\n"]

            for plugin in self._discovered_plugins.values():
                status_emoji = "✅" if plugin.loaded else "⏳"
                status_text = "Loaded" if plugin.loaded else "Available"
                lines.append(f"{status_emoji} **{plugin.name}** v{plugin.version} [{status_text}]")
                lines.append(f"   {plugin.description}\n")

            lines.append("---")
            lines.append(f"📊 Total plugins: {len(self._discovered_plugins)}")
            lines.append(f"✅ Loaded: {len(self._loaded_plugins)}")
            lines.append(f"⏳ Available: {len(self._discovered_plugins) - len(self._loaded_plugins)}")
            lines.append("\n💡 Use `load_toolset` to load a plugin and access its tools.")

            return "\n".join(lines)

        @self.server.tool("load_toolset")
        async def load_toolset(plugin_name: str) -> str:
            """
            Load a plugin (toolset) dynamically to make its tools available.

            Args:
                plugin_name: The name of the plugin to load (from list_available_toolsets)

            Returns:
                Success message with plugin details, or error if loading fails.
            """
            try:
                result = self._load_plugin(plugin_name)
                plugin = self._discovered_plugins[plugin_name]
                return f"""✅ {result}

📦 **Plugin Details:**
• Name: {plugin.name}
• Version: {plugin.version}
• Description: {plugin.description}

🛠️ **Tools Now Available:**
The plugin's tools are now registered and ready to use.
Call the plugin's specific tools as needed.

💡 Use `list_available_toolsets` to see all loaded plugins."""
            except McpError as e:
                return f"❌ Failed to load plugin: {str(e)}"
            except Exception as e:
                return f"❌ Unexpected error loading plugin: {str(e)}"

    def get_discovered_plugins(self) -> List[Dict[str, Any]]:
        """
        Get a list of all discovered plugins as dictionaries.

        Returns:
            List of plugin information dictionaries
        """
        return [p.to_dict() for p in self._discovered_plugins.values()]

    async def start(self) -> None:
        """Start the MCP server."""
        self.logger.info("Starting M365 MCP Server...")
        self.logger.info(f"Toolkit path: {self.toolkit_path}")
        self.logger.info(f"Plugins path: {self.plugins_path}")
        self.logger.info(f"Discovered {len(self._discovered_plugins)} plugins")

        # Start the server via stdio (standard MCP transport)
        await self.server.run_stdio_async()
        self.logger.info("M365 MCP Server started successfully!")


async def main():
    """Main entry point."""
    server = M365MCPServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
