"""
Unit tests for Copilot Tools Toolbox.

Tests all core functions (list_docs, show_agent_prompts, check_workspace)
using pytest and temporary directories for isolation.

Design:
- Deterministic: No network calls, no system dependencies
- Flexible: Assert types and structure, not exact counts
- Isolated: Each test uses TemporaryDirectory
- Comprehensive: Cover success cases, edge cases, and error conditions
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from scripts.copilot_tools import list_docs, show_agent_prompts, check_workspace


class TestListDocs:
    """Tests for list_docs() function."""

    def test_list_docs_basic(self):
        """Test basic documentation discovery."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create test documentation structure
            (root / 'docs').mkdir()
            (root / 'docs' / 'README.md').write_text('# Documentation', encoding='utf-8')
            (root / 'docs' / 'guide.rst').write_text('Guide content', encoding='utf-8')
            (root / 'CHANGELOG.md').write_text('# Changelog', encoding='utf-8')

            result = list_docs(root)

            # Assert structure
            assert isinstance(result, dict)
            assert 'docs' in result
            assert 'count' in result
            assert 'directories' in result

            # Assert types
            assert isinstance(result['docs'], list)
            assert isinstance(result['count'], int)
            assert isinstance(result['directories'], list)

            # Assert content
            assert result['count'] == 3
            assert any(doc['name'] == 'README.md' for doc in result['docs'])
            assert any(doc['name'] == 'CHANGELOG.md' for doc in result['docs'])

            # Assert doc structure
            for doc in result['docs']:
                assert 'name' in doc
                assert 'path' in doc
                assert 'type' in doc
                assert 'size_bytes' in doc
                assert isinstance(doc['size_bytes'], int)
                assert doc['size_bytes'] > 0

    def test_list_docs_empty_repo(self):
        """Test with empty repository (no docs)."""
        with TemporaryDirectory() as td:
            root = Path(td)

            result = list_docs(root)

            assert result['count'] == 0
            assert result['docs'] == []
            assert isinstance(result['directories'], list)

    def test_list_docs_nested_structure(self):
        """Test with nested documentation structure."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create nested structure
            (root / 'docs' / 'api').mkdir(parents=True)
            (root / 'docs' / 'api' / 'reference.md').write_text('API ref', encoding='utf-8')
            (root / 'docs' / 'guides').mkdir(parents=True)
            (root / 'docs' / 'guides' / 'tutorial.md').write_text('Tutorial', encoding='utf-8')

            result = list_docs(root)

            assert result['count'] == 2
            assert any('api' in doc['path'] for doc in result['docs'])
            assert any('guides' in doc['path'] for doc in result['docs'])

    def test_list_docs_github_directory(self):
        """Test discovery in .github directory."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / '.github').mkdir()
            (root / '.github' / 'CONTRIBUTING.md').write_text('# Contributing', encoding='utf-8')

            result = list_docs(root)

            assert result['count'] >= 1
            assert any(doc['name'] == 'CONTRIBUTING.md' for doc in result['docs'])

    def test_list_docs_skips_sensitive_files(self):
        """Test that sensitive files are skipped."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create sensitive files that should be skipped
            (root / '.env').write_text('SECRET=value', encoding='utf-8')
            (root / '.env.local').write_text('SECRET=value', encoding='utf-8')
            (root / 'README.md').write_text('# Safe file', encoding='utf-8')

            result = list_docs(root)

            # Should only find README.md
            assert result['count'] == 1
            assert result['docs'][0]['name'] == 'README.md'

            # Should not include .env files
            assert not any('.env' in doc['name'] for doc in result['docs'])

    def test_list_docs_multiple_types(self):
        """Test discovery of different documentation types."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / 'docs').mkdir()
            (root / 'docs' / 'doc1.md').write_text('Markdown', encoding='utf-8')
            (root / 'docs' / 'doc2.rst').write_text('ReStructuredText', encoding='utf-8')
            (root / 'docs' / 'doc3.txt').write_text('Plain text', encoding='utf-8')
            (root / 'docs' / 'doc4.adoc').write_text('AsciiDoc', encoding='utf-8')

            result = list_docs(root)

            assert result['count'] == 4

            # Check types are properly identified
            types = {doc['type'] for doc in result['docs']}
            assert 'MD' in types
            assert 'RST' in types
            assert 'TXT' in types
            assert 'ADOC' in types


class TestShowAgentPrompts:
    """Tests for show_agent_prompts() function."""

    def test_show_agent_prompts_basic(self):
        """Test basic agent prompt discovery."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create agent configuration files
            (root / '.github').mkdir()
            (root / '.github' / 'copilot-instructions.md').write_text(
                '# Copilot Instructions\nAgent guidance here',
                encoding='utf-8'
            )

            result = show_agent_prompts(root)

            # Assert structure
            assert isinstance(result, dict)
            assert 'prompts' in result
            assert 'count' in result
            assert 'locations' in result

            # Assert types
            assert isinstance(result['prompts'], list)
            assert isinstance(result['count'], int)
            assert isinstance(result['locations'], list)

            # Assert content
            assert result['count'] >= 1
            assert any('copilot-instructions' in p['name'] for p in result['prompts'])

    def test_show_agent_prompts_empty_repo(self):
        """Test with no agent configuration files."""
        with TemporaryDirectory() as td:
            root = Path(td)

            result = show_agent_prompts(root)

            assert result['count'] == 0
            assert result['prompts'] == []
            assert isinstance(result['locations'], list)

    def test_show_agent_prompts_multiple_patterns(self):
        """Test discovery of various agent file patterns."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / '.github').mkdir()
            (root / '.github' / 'copilot-instructions.md').write_text('Copilot', encoding='utf-8')
            (root / '.github' / 'ai-instructions.md').write_text('AI', encoding='utf-8')
            (root / '.github' / 'agent-config.json').write_text('{}', encoding='utf-8')

            result = show_agent_prompts(root)

            # Should find at least 3 files (may find more due to content detection)
            assert result['count'] >= 3
            assert any('copilot' in p['name'].lower() for p in result['prompts'])
            assert any('ai' in p['name'].lower() for p in result['prompts'])
            assert any('agent' in p['name'].lower() for p in result['prompts'])

    def test_show_agent_prompts_content_detection(self):
        """Test content-based detection of agent files."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / 'docs').mkdir()
            # File with agent-related content but generic name
            (root / 'docs' / 'DEVELOPMENT.md').write_text(
                '# Development Guide\n\n## Copilot Setup\n\nInstructions for AI agents...',
                encoding='utf-8'
            )

            result = show_agent_prompts(root)

            # Should detect based on content
            assert result['count'] >= 1
            assert any('DEVELOPMENT.md' in p['name'] for p in result['prompts'])

    def test_show_agent_prompts_structure(self):
        """Test prompt file structure."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / '.github').mkdir()
            (root / '.github' / 'copilot-instructions.md').write_text('Instructions', encoding='utf-8')

            result = show_agent_prompts(root)

            for prompt in result['prompts']:
                assert 'name' in prompt
                assert 'path' in prompt
                assert 'type' in prompt
                assert 'size_bytes' in prompt
                assert isinstance(prompt['size_bytes'], int)


class TestCheckWorkspace:
    """Tests for check_workspace() function."""

    def test_check_workspace_basic(self):
        """Test basic workspace health check."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create minimal valid workspace
            (root / '.git').mkdir()
            (root / 'requirements.txt').write_text('pytest\n', encoding='utf-8')
            (root / 'scripts').mkdir()
            (root / 'tests').mkdir()

            result = check_workspace(root)

            # Assert structure
            assert isinstance(result, dict)
            assert 'status' in result
            assert 'summary' in result
            assert 'checks' in result
            assert 'recommendations' in result

            # Assert types
            assert isinstance(result['checks'], list)
            assert isinstance(result['recommendations'], list)
            assert result['status'] in ['healthy', 'warning', 'error']

            # Assert checks structure
            for check in result['checks']:
                assert 'name' in check
                assert 'status' in check
                assert 'message' in check
                assert check['status'] in ['pass', 'fail', 'warning', 'info']

    def test_check_workspace_empty_directory(self):
        """Test with completely empty directory."""
        with TemporaryDirectory() as td:
            root = Path(td)

            result = check_workspace(root)

            # Should have status but likely warnings/errors
            assert 'status' in result
            assert result['status'] in ['warning', 'error']
            assert len(result['recommendations']) > 0

    def test_check_workspace_git_check(self):
        """Test git repository check."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Without .git
            result1 = check_workspace(root)
            git_check1 = next(c for c in result1['checks'] if c['name'] == 'Git Repository')
            assert git_check1['status'] == 'fail'

            # With .git
            (root / '.git').mkdir()
            result2 = check_workspace(root)
            git_check2 = next(c for c in result2['checks'] if c['name'] == 'Git Repository')
            assert git_check2['status'] == 'pass'

    def test_check_workspace_python_requirements(self):
        """Test Python requirements file check."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Without requirements
            result1 = check_workspace(root)
            req_check1 = next(c for c in result1['checks'] if c['name'] == 'Python Requirements')
            assert req_check1['status'] in ['warning', 'fail']

            # With requirements.txt
            (root / 'requirements.txt').write_text('pytest', encoding='utf-8')
            result2 = check_workspace(root)
            req_check2 = next(c for c in result2['checks'] if c['name'] == 'Python Requirements')
            assert req_check2['status'] == 'pass'
            assert 'requirements.txt' in req_check2['details']

    def test_check_workspace_directory_structure(self):
        """Test repository directory structure check."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create some key directories
            (root / 'scripts').mkdir()
            (root / 'tests').mkdir()
            (root / 'docs').mkdir()

            result = check_workspace(root)

            dir_check = next(c for c in result['checks'] if c['name'] == 'Repository Structure')
            assert 'details' in dir_check
            assert 'scripts' in dir_check['details']
            assert 'tests' in dir_check['details']
            assert 'docs' in dir_check['details']

    def test_check_workspace_recommendations(self):
        """Test that recommendations are provided when needed."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Empty directory should generate recommendations
            result = check_workspace(root)

            assert len(result['recommendations']) > 0
            # Should recommend git init
            assert any('git' in rec.lower() for rec in result['recommendations'])

    def test_check_workspace_ci_workflows(self):
        """Test CI/CD workflow detection."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create workflow files
            workflows_dir = root / '.github' / 'workflows'
            workflows_dir.mkdir(parents=True)
            (workflows_dir / 'ci.yml').write_text('name: CI\non: push', encoding='utf-8')
            (workflows_dir / 'test.yml').write_text('name: Test\non: pull_request', encoding='utf-8')

            result = check_workspace(root)

            ci_check = next(c for c in result['checks'] if c['name'] == 'CI/CD Workflows')
            assert ci_check['status'] == 'pass'
            assert 'ci.yml' in ci_check['details']


class TestCLIIntegration:
    """Integration tests for CLI interface."""

    def test_cli_module_import(self):
        """Test that CLI module can be imported."""
        from scripts.copilot_tools import __main__ as cli_module

        assert hasattr(cli_module, 'main')
        assert callable(cli_module.main)

    def test_cli_find_repo_root(self):
        """Test repo root detection function."""
        from scripts.copilot_tools.__main__ import find_repo_root

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / '.git').mkdir()

            # Change to temp directory with proper cleanup
            import os
            original_cwd = os.getcwd()
            detected_root = None
            try:
                os.chdir(root)
                detected_root = find_repo_root()
            finally:
                os.chdir(original_cwd)

            # Assert outside the try/finally block
            assert detected_root is not None
            assert detected_root == root


class TestSecurityFeatures:
    """Tests for security features."""

    def test_no_secret_exposure_in_paths(self):
        """Test that .env files are not exposed."""
        with TemporaryDirectory() as td:
            root = Path(td)

            # Create sensitive files
            (root / '.env').write_text('SECRET_KEY=sensitive', encoding='utf-8')
            (root / '.env.local').write_text('API_KEY=secret', encoding='utf-8')

            # Test list_docs
            docs_result = list_docs(root)
            assert not any('.env' in doc['path'] for doc in docs_result['docs'])

            # Test show_agent_prompts
            prompts_result = show_agent_prompts(root)
            assert not any('.env' in prompt['path'] for prompt in prompts_result['prompts'])

    def test_safe_path_checking(self):
        """Test that paths outside repository are rejected."""
        from scripts.copilot_tools import _is_safe_path

        with TemporaryDirectory() as td:
            root = Path(td)

            # Safe paths
            assert _is_safe_path(root / 'docs' / 'README.md', root)
            assert _is_safe_path(root / 'scripts' / 'tool.py', root)

            # Unsafe paths (sensitive directories)
            assert not _is_safe_path(root / '.env', root)
            assert not _is_safe_path(root / '.git' / 'config', root)
            assert not _is_safe_path(root / '__pycache__' / 'module.pyc', root)
            assert not _is_safe_path(root / '.venv' / 'lib', root)


class TestOutputFormats:
    """Tests for output format consistency."""

    def test_json_serializable_outputs(self):
        """Test that all outputs are JSON-serializable."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / '.git').mkdir()
            (root / 'README.md').write_text('# Project', encoding='utf-8')

            # Test each function
            docs_result = list_docs(root)
            prompts_result = show_agent_prompts(root)
            workspace_result = check_workspace(root)

            # All should be JSON-serializable
            assert json.dumps(docs_result)
            assert json.dumps(prompts_result)
            assert json.dumps(workspace_result)

    def test_consistent_output_structure(self):
        """Test that outputs have consistent structure."""
        with TemporaryDirectory() as td:
            root = Path(td)

            (root / 'README.md').write_text('# Test', encoding='utf-8')

            # Test multiple times to ensure consistency
            result1 = list_docs(root)
            result2 = list_docs(root)

            assert result1.keys() == result2.keys()
            assert result1 == result2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
