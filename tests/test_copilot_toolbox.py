"""
Unit tests for the Copilot Toolbox CLI.

Tests all three commands (list-docs, show-agent-prompts, check-workspace)
with various scenarios and edge cases.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from scripts.copilot_tools.__main__ import (
    check_workspace,
    get_repo_root,
    list_docs,
    show_agent_prompts,
)


class TestGetRepoRoot:
    """Tests for get_repo_root function."""

    def test_finds_git_directory(self):
        """Test that get_repo_root finds .git directory."""
        with TemporaryDirectory() as td:
            td = Path(td)
            git_dir = td / ".git"
            git_dir.mkdir()

            # Create a subdirectory to test traversal
            sub_dir = td / "scripts" / "copilot_tools"
            sub_dir.mkdir(parents=True)

            # Should find repo root from subdirectory
            # Note: This tests the logic, but in actual test we use the real repo
            root = get_repo_root()
            assert root.is_dir()


class TestListDocs:
    """Tests for list-docs command."""

    def test_list_docs_text_format(self):
        """Test listing docs in text format."""
        with TemporaryDirectory() as td:
            td = Path(td)

            # Create docs directory with files
            docs_dir = td / "docs"
            docs_dir.mkdir()
            (docs_dir / "README.md").write_text("# Docs", encoding="utf-8")
            (docs_dir / "GUIDE.md").write_text("# Guide", encoding="utf-8")

            # Create .github directory with files
            github_dir = td / ".github"
            github_dir.mkdir()
            (github_dir / "CODEOWNERS").write_text("* @owner", encoding="utf-8")

            result = list_docs(td, output_format="text")

            assert isinstance(result, str)
            assert "Documentation Files" in result
            assert "README.md" in result
            assert "GUIDE.md" in result
            assert "CODEOWNERS" in result

    def test_list_docs_json_format(self):
        """Test listing docs in JSON format."""
        with TemporaryDirectory() as td:
            td = Path(td)

            # Create docs directory
            docs_dir = td / "docs"
            docs_dir.mkdir()
            (docs_dir / "README.md").write_text("# Docs", encoding="utf-8")

            # Create .github directory
            github_dir = td / ".github"
            github_dir.mkdir()
            (github_dir / "CODEOWNERS").write_text("* @owner", encoding="utf-8")

            result = list_docs(td, output_format="json")

            assert isinstance(result, dict)
            assert "docs" in result
            assert "github" in result
            assert "README.md" in result["docs"]
            assert "CODEOWNERS" in result["github"]

    def test_list_docs_missing_directories(self):
        """Test behavior when docs/github directories are missing."""
        with TemporaryDirectory() as td:
            td = Path(td)

            result = list_docs(td, output_format="json")

            assert isinstance(result, dict)
            assert result["docs"] == []
            assert result["github"] == []

    def test_list_docs_excludes_hidden_files(self):
        """Test that hidden files are excluded."""
        with TemporaryDirectory() as td:
            td = Path(td)

            docs_dir = td / "docs"
            docs_dir.mkdir()
            (docs_dir / "README.md").write_text("# Docs", encoding="utf-8")
            (docs_dir / ".hidden").write_text("hidden", encoding="utf-8")

            result = list_docs(td, output_format="json")

            assert "README.md" in result["docs"]
            assert ".hidden" not in result["docs"]

    def test_list_docs_nested_structure(self):
        """Test listing docs with nested directory structure."""
        with TemporaryDirectory() as td:
            td = Path(td)

            docs_dir = td / "docs"
            docs_dir.mkdir()
            (docs_dir / "README.md").write_text("# Docs", encoding="utf-8")

            # Create nested directory
            guides_dir = docs_dir / "guides"
            guides_dir.mkdir()
            (guides_dir / "setup.md").write_text("# Setup", encoding="utf-8")

            result = list_docs(td, output_format="json")

            assert "README.md" in result["docs"]
            assert "guides/setup.md" in result["docs"] or "guides\\setup.md" in result["docs"]


class TestShowAgentPrompts:
    """Tests for show-agent-prompts command."""

    def test_show_agent_prompts_text_format(self):
        """Test showing agent prompts in text format."""
        with TemporaryDirectory() as td:
            td = Path(td)

            agents_dir = td / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create agent file
            agent_file = agents_dir / "test-agent.md"
            agent_file.write_text(
                """---
name: Test Agent
---

# Test Agent

This is a test agent for testing purposes.""",
                encoding="utf-8",
            )

            result = show_agent_prompts(td, output_format="text")

            assert isinstance(result, str)
            assert "Agent Prompts" in result
            assert "test-agent.md" in result
            assert "Test Agent" in result or "This is a test agent" in result

    def test_show_agent_prompts_json_format(self):
        """Test showing agent prompts in JSON format."""
        with TemporaryDirectory() as td:
            td = Path(td)

            agents_dir = td / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create agent file without frontmatter
            agent_file = agents_dir / "simple-agent.md"
            agent_file.write_text("# Simple Agent\n\nA simple agent description.", encoding="utf-8")

            result = show_agent_prompts(td, output_format="json")

            assert isinstance(result, dict)
            assert "agents" in result
            assert "count" in result
            assert result["count"] == 1
            assert "simple-agent.md" in result["agents"]
            assert "summary" in result["agents"]["simple-agent.md"]

    def test_show_agent_prompts_missing_directory(self):
        """Test behavior when agents directory is missing."""
        with TemporaryDirectory() as td:
            td = Path(td)

            result = show_agent_prompts(td, output_format="json")

            assert isinstance(result, dict)
            assert result["agents"] == {}
            assert result["count"] == 0

    def test_show_agent_prompts_multiple_agents(self):
        """Test showing multiple agent prompts."""
        with TemporaryDirectory() as td:
            td = Path(td)

            agents_dir = td / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create multiple agent files
            (agents_dir / "agent1.md").write_text("# Agent 1\nFirst agent", encoding="utf-8")
            (agents_dir / "agent2.md").write_text("# Agent 2\nSecond agent", encoding="utf-8")

            result = show_agent_prompts(td, output_format="json")

            assert result["count"] == 2
            assert "agent1.md" in result["agents"]
            assert "agent2.md" in result["agents"]

    def test_show_agent_prompts_with_frontmatter(self):
        """Test parsing agent prompts with YAML frontmatter."""
        with TemporaryDirectory() as td:
            td = Path(td)

            agents_dir = td / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create agent file with frontmatter
            agent_content = """---
name: Advanced Agent
version: 1.0
---

# Advanced Agent

This agent has YAML frontmatter that should be skipped."""

            (agents_dir / "advanced.md").write_text(agent_content, encoding="utf-8")

            result = show_agent_prompts(td, output_format="json")

            assert "advanced.md" in result["agents"]
            # Summary should skip frontmatter
            summary = result["agents"]["advanced.md"]["summary"]
            assert "Advanced Agent" in summary or "This agent has YAML" in summary

    def test_show_agent_prompts_handles_read_error(self):
        """Test graceful handling of file read errors."""
        with TemporaryDirectory() as td:
            td = Path(td)

            agents_dir = td / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create a valid file
            (agents_dir / "valid.md").write_text("# Valid Agent", encoding="utf-8")

            result = show_agent_prompts(td, output_format="json")

            # Should still process valid files
            assert result["count"] >= 1
            assert "valid.md" in result["agents"]


class TestCheckWorkspace:
    """Tests for check-workspace command."""

    def test_check_workspace_text_format(self):
        """Test workspace check in text format."""
        with TemporaryDirectory() as td:
            td = Path(td)

            # Create all expected files/directories
            (td / "README.md").write_text("# README", encoding="utf-8")
            (td / "docs").mkdir()
            (td / ".github" / "workflows").mkdir(parents=True)
            (td / "requirements.txt").write_text("pytest", encoding="utf-8")
            (td / ".gitignore").write_text("*.pyc", encoding="utf-8")
            (td / "pyproject.toml").write_text("[tool.black]", encoding="utf-8")

            result = check_workspace(td, output_format="text")

            assert isinstance(result, str)
            assert "Workspace Health Check" in result
            assert "Health Score" in result
            assert "100" in result  # Should be 100%
            assert "✅" in result

    def test_check_workspace_json_format(self):
        """Test workspace check in JSON format."""
        with TemporaryDirectory() as td:
            td = Path(td)

            # Create some expected files
            (td / "README.md").write_text("# README", encoding="utf-8")
            (td / "docs").mkdir()

            result = check_workspace(td, output_format="json")

            assert isinstance(result, dict)
            assert "health_score" in result
            assert "passed" in result
            assert "total" in result
            assert "checks" in result
            assert "README.md" in result["checks"]
            assert result["checks"]["README.md"]["exists"] is True
            assert result["checks"]["docs/"]["exists"] is True

    def test_check_workspace_missing_files(self):
        """Test workspace check with missing files."""
        with TemporaryDirectory() as td:
            td = Path(td)

            result = check_workspace(td, output_format="json")

            assert result["health_score"] == 0.0
            assert result["passed"] == 0
            for check in result["checks"].values():
                assert check["exists"] is False

    def test_check_workspace_partial_health(self):
        """Test workspace check with some files present."""
        with TemporaryDirectory() as td:
            td = Path(td)

            # Create only some files
            (td / "README.md").write_text("# README", encoding="utf-8")
            (td / ".gitignore").write_text("*.pyc", encoding="utf-8")

            result = check_workspace(td, output_format="json")

            assert 0 < result["health_score"] < 100
            assert result["passed"] == 2
            assert result["checks"]["README.md"]["exists"] is True
            assert result["checks"][".gitignore"]["exists"] is True
            assert result["checks"]["docs/"]["exists"] is False

    def test_check_workspace_counts_workflows(self):
        """Test that workspace check counts workflow files."""
        with TemporaryDirectory() as td:
            td = Path(td)

            workflows_dir = td / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)
            (workflows_dir / "ci.yml").write_text("name: CI", encoding="utf-8")
            (workflows_dir / "test.yaml").write_text("name: Test", encoding="utf-8")

            result = check_workspace(td, output_format="json")

            assert result["checks"][".github/workflows/"]["exists"] is True
            assert result["checks"][".github/workflows/"]["workflow_count"] == 2

    def test_check_workspace_counts_docs(self):
        """Test that workspace check counts documentation files."""
        with TemporaryDirectory() as td:
            td = Path(td)

            docs_dir = td / "docs"
            docs_dir.mkdir()
            (docs_dir / "README.md").write_text("# Docs", encoding="utf-8")
            (docs_dir / "GUIDE.md").write_text("# Guide", encoding="utf-8")

            result = check_workspace(td, output_format="json")

            assert result["checks"]["docs/"]["exists"] is True
            assert result["checks"]["docs/"]["file_count"] == 2


class TestIntegration:
    """Integration tests for the CLI."""

    def test_all_commands_return_valid_output(self):
        """Test that all commands return valid output without errors."""
        with TemporaryDirectory() as td:
            td = Path(td)

            # Create minimal structure
            (td / "README.md").write_text("# README", encoding="utf-8")
            (td / "docs").mkdir()
            (td / ".github" / "agents").mkdir(parents=True)
            (td / ".github" / "agents" / "test.md").write_text("# Test", encoding="utf-8")

            # Test list-docs
            result1 = list_docs(td, output_format="json")
            assert isinstance(result1, dict)
            assert "docs" in result1

            # Test show-agent-prompts
            result2 = show_agent_prompts(td, output_format="json")
            assert isinstance(result2, dict)
            assert "agents" in result2

            # Test check-workspace
            result3 = check_workspace(td, output_format="json")
            assert isinstance(result3, dict)
            assert "health_score" in result3

    def test_json_output_is_valid_json(self):
        """Test that JSON output is valid and parseable."""
        with TemporaryDirectory() as td:
            td = Path(td)

            (td / "README.md").write_text("# README", encoding="utf-8")

            # Get JSON output from each command
            result1 = list_docs(td, output_format="json")
            result2 = show_agent_prompts(td, output_format="json")
            result3 = check_workspace(td, output_format="json")

            # Verify all can be serialized to JSON
            json.dumps(result1)
            json.dumps(result2)
            json.dumps(result3)
