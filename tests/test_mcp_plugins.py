"""
Tests for the M365 MCP Server plugin architecture.

These tests verify:
- Plugin discovery from the plugins directory
- Dynamic plugin loading
- Plugin management tools (list_available_toolsets, load_toolset)
"""

import sys
import os
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest


# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Skip MCP tests if MCP is not properly installed
try:
    from mcp import McpError
    from mcp.server import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP SDK not available")


if MCP_AVAILABLE:
    from src.mcp.m365_mcp_server import M365MCPServer, PluginInfo


class TestPluginInfo:
    """Tests for the PluginInfo class."""

    def test_plugin_info_creation(self):
        """Test PluginInfo initialization."""
        plugin = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="A test plugin",
            entry_point="tools:register_tools",
            path=Path("/tmp/test_plugin"),
        )

        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "A test plugin"
        assert plugin.entry_point == "tools:register_tools"
        assert plugin.loaded is False

    def test_plugin_info_to_dict_unloaded(self):
        """Test PluginInfo.to_dict() for unloaded plugin."""
        plugin = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="A test plugin",
            entry_point="tools:register_tools",
            path=Path("/tmp/test_plugin"),
        )

        result = plugin.to_dict()

        assert result["name"] == "test_plugin"
        assert result["version"] == "1.0.0"
        assert result["description"] == "A test plugin"
        assert result["status"] == "unloaded"

    def test_plugin_info_to_dict_loaded(self):
        """Test PluginInfo.to_dict() for loaded plugin."""
        plugin = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="A test plugin",
            entry_point="tools:register_tools",
            path=Path("/tmp/test_plugin"),
        )
        plugin.loaded = True

        result = plugin.to_dict()

        assert result["status"] == "loaded"


class TestM365MCPServerPluginDiscovery:
    """Tests for plugin discovery functionality."""

    def test_discover_plugins_finds_valid_plugin(self):
        """Test that plugin discovery finds plugins with valid manifests."""
        with TemporaryDirectory() as tmpdir:
            # Create a test plugin directory structure
            plugins_dir = Path(tmpdir) / "plugins"
            test_plugin_dir = plugins_dir / "test_plugin"
            test_plugin_dir.mkdir(parents=True)

            # Create a valid plugin.json
            manifest = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "A test plugin",
                "entry_point": "tools:register_tools",
            }
            (test_plugin_dir / "plugin.json").write_text(json.dumps(manifest))

            # Create a mock server instance and patch paths
            with patch.object(M365MCPServer, "__init__", lambda self: None):
                server = M365MCPServer()
                server.server = MagicMock()
                server.logger = MagicMock()
                server.plugins_path = plugins_dir
                server._discovered_plugins = {}
                server._loaded_plugins = set()

                server._discover_plugins()

                assert "test_plugin" in server._discovered_plugins
                plugin = server._discovered_plugins["test_plugin"]
                assert plugin.version == "1.0.0"
                assert plugin.description == "A test plugin"

    def test_discover_plugins_skips_invalid_json(self):
        """Test that plugin discovery skips plugins with invalid JSON manifests."""
        with TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            test_plugin_dir = plugins_dir / "invalid_plugin"
            test_plugin_dir.mkdir(parents=True)

            # Create an invalid plugin.json
            (test_plugin_dir / "plugin.json").write_text("invalid json {")

            with patch.object(M365MCPServer, "__init__", lambda self: None):
                server = M365MCPServer()
                server.server = MagicMock()
                server.logger = MagicMock()
                server.plugins_path = plugins_dir
                server._discovered_plugins = {}
                server._loaded_plugins = set()

                server._discover_plugins()

                # Plugin should not be discovered due to invalid JSON
                assert "invalid_plugin" not in server._discovered_plugins

    def test_discover_plugins_skips_missing_manifest(self):
        """Test that plugin discovery skips directories without manifest."""
        with TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            test_plugin_dir = plugins_dir / "no_manifest_plugin"
            test_plugin_dir.mkdir(parents=True)

            # No plugin.json created

            with patch.object(M365MCPServer, "__init__", lambda self: None):
                server = M365MCPServer()
                server.server = MagicMock()
                server.logger = MagicMock()
                server.plugins_path = plugins_dir
                server._discovered_plugins = {}
                server._loaded_plugins = set()

                server._discover_plugins()

                assert "no_manifest_plugin" not in server._discovered_plugins

    def test_discover_plugins_skips_pycache(self):
        """Test that plugin discovery skips __pycache__ directories."""
        with TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            pycache_dir = plugins_dir / "__pycache__"
            pycache_dir.mkdir(parents=True)

            with patch.object(M365MCPServer, "__init__", lambda self: None):
                server = M365MCPServer()
                server.server = MagicMock()
                server.logger = MagicMock()
                server.plugins_path = plugins_dir
                server._discovered_plugins = {}
                server._loaded_plugins = set()

                server._discover_plugins()

                assert "__pycache__" not in server._discovered_plugins


class TestM365MCPServerPluginLoading:
    """Tests for plugin loading functionality."""

    def test_load_plugin_not_found(self):
        """Test loading a plugin that doesn't exist."""
        with patch.object(M365MCPServer, "__init__", lambda self: None):
            server = M365MCPServer()
            server.server = MagicMock()
            server.logger = MagicMock()
            server._discovered_plugins = {}
            server._loaded_plugins = set()

            # Import McpError for testing
            from mcp import McpError

            with pytest.raises(McpError) as exc_info:
                server._load_plugin("nonexistent_plugin")

            assert "Plugin not found" in str(exc_info.value)

    def test_load_plugin_already_loaded(self):
        """Test loading a plugin that's already loaded."""
        with patch.object(M365MCPServer, "__init__", lambda self: None):
            server = M365MCPServer()
            server.server = MagicMock()
            server.logger = MagicMock()
            server._discovered_plugins = {
                "test_plugin": PluginInfo(
                    name="test_plugin",
                    version="1.0.0",
                    description="Test",
                    entry_point="tools:register_tools",
                    path=Path("/tmp"),
                )
            }
            server._loaded_plugins = {"test_plugin"}

            result = server._load_plugin("test_plugin")

            assert "already loaded" in result

    def test_load_plugin_invalid_entry_point(self):
        """Test loading a plugin with invalid entry point format."""
        with patch.object(M365MCPServer, "__init__", lambda self: None):
            server = M365MCPServer()
            server.server = MagicMock()
            server.logger = MagicMock()
            server._discovered_plugins = {
                "test_plugin": PluginInfo(
                    name="test_plugin",
                    version="1.0.0",
                    description="Test",
                    entry_point="invalid_entry_point",  # Missing colon
                    path=Path("/tmp"),
                )
            }
            server._loaded_plugins = set()

            from mcp import McpError

            with pytest.raises(McpError) as exc_info:
                server._load_plugin("test_plugin")

            assert "Invalid entry_point format" in str(exc_info.value)


class TestM365MCPServerIntegration:
    """Integration tests for the M365 MCP Server."""

    def test_get_discovered_plugins(self):
        """Test getting discovered plugins as dictionaries."""
        with patch.object(M365MCPServer, "__init__", lambda self: None):
            server = M365MCPServer()
            server._discovered_plugins = {
                "plugin1": PluginInfo(
                    name="plugin1",
                    version="1.0.0",
                    description="First plugin",
                    entry_point="tools:register_tools",
                    path=Path("/tmp"),
                ),
                "plugin2": PluginInfo(
                    name="plugin2",
                    version="2.0.0",
                    description="Second plugin",
                    entry_point="tools:register_tools",
                    path=Path("/tmp"),
                ),
            }

            result = server.get_discovered_plugins()

            assert len(result) == 2
            names = [p["name"] for p in result]
            assert "plugin1" in names
            assert "plugin2" in names


class TestRealPluginDiscovery:
    """Tests that verify real plugin discovery in the repository."""

    def test_sharepoint_tools_plugin_exists(self):
        """Test that the sharepoint_tools plugin is discoverable."""
        # Get the path to the actual plugins directory
        repo_root = Path(__file__).parent.parent
        plugins_path = repo_root / "src" / "mcp" / "plugins"

        assert plugins_path.exists(), "Plugins directory should exist"

        sharepoint_plugin = plugins_path / "sharepoint_tools"
        assert sharepoint_plugin.exists(), "sharepoint_tools plugin directory should exist"

        manifest = sharepoint_plugin / "plugin.json"
        assert manifest.exists(), "plugin.json should exist"

        # Verify manifest content
        manifest_data = json.loads(manifest.read_text())
        assert manifest_data["name"] == "sharepoint_tools"
        assert manifest_data["version"] == "1.0.0"
        assert "description" in manifest_data
        assert "entry_point" in manifest_data

    def test_sharepoint_tools_has_tools_module(self):
        """Test that the sharepoint_tools plugin has a tools.py module."""
        repo_root = Path(__file__).parent.parent
        tools_file = repo_root / "src" / "mcp" / "plugins" / "sharepoint_tools" / "tools.py"

        assert tools_file.exists(), "tools.py should exist"

        # Verify it can be imported
        from src.mcp.plugins.sharepoint_tools.tools import register_tools

        assert callable(register_tools), "register_tools should be callable"
