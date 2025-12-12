"""
Copilot Tools Toolbox - Helper utilities for AI agents and contributors.

This module provides secure, standardized functions to help Copilot and other AI agents
discover repository assets, surface agent prompts, and run workspace health checks.

Design Principles:
- Security first: Never expose secrets, use structured logging
- Standard library only: No external dependencies for core functionality
- Deterministic: Predictable outputs for testing and automation
- Agent-friendly: JSON-serializable outputs for programmatic use

Functions:
    list_docs: Discover documentation files in the repository
    show_agent_prompts: Surface AI agent configuration files
    check_workspace: Run basic health checks on the workspace

Usage:
    from scripts.copilot_tools import list_docs, show_agent_prompts, check_workspace

    # Discover docs
    docs = list_docs(repo_root)

    # Show agent prompts
    prompts = show_agent_prompts(repo_root)

    # Run health check
    health = check_workspace(repo_root)
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Configure logging to be secure (no sensitive data)
logger = logging.getLogger(__name__)


def _is_safe_path(path: Path, root: Path) -> bool:
    """
    Check if a path is safe to read (within repo, not a sensitive file).

    Args:
        path: Path to check
        root: Repository root path

    Returns:
        True if path is safe to read, False otherwise
    """
    try:
        # Resolve to absolute path and check if within root
        abs_path = path.resolve()
        abs_root = root.resolve()

        # Must be within repository
        if not str(abs_path).startswith(str(abs_root)):
            return False

        # Skip sensitive files/directories
        sensitive_patterns = {'.env', '.git', '__pycache__', '.venv', 'venv',
                              'node_modules', '.pytest_cache', '.mypy_cache'}

        for part in abs_path.parts:
            if part in sensitive_patterns or part.startswith('.env'):
                return False

        return True
    except (OSError, RuntimeError):
        return False


def list_docs(root: Path) -> Dict[str, Any]:
    """
    Discover documentation files in the repository.

    Scans common documentation directories (docs/, root *.md files) and
    returns structured information about available documentation.

    Args:
        root: Repository root path

    Returns:
        Dictionary with:
            - docs: List of doc files with paths and types
            - count: Total count of documentation files
            - directories: List of documentation directories found

    Example:
        >>> docs = list_docs(Path('/path/to/repo'))
        >>> print(f"Found {docs['count']} documentation files")
        >>> for doc in docs['docs']:
        ...     print(f"  - {doc['name']}: {doc['path']}")
    """
    root = Path(root).resolve()

    docs_list: List[Dict[str, str]] = []
    doc_dirs = set()

    # Common documentation locations
    search_paths = [
        root / 'docs',
        root / '.github',
        root,  # Root level markdown files
    ]

    # Documentation file patterns
    doc_extensions = {'.md', '.rst', '.txt', '.adoc'}

    for search_path in search_paths:
        if not search_path.exists() or not _is_safe_path(search_path, root):
            continue

        try:
            # For root, only check direct children
            if search_path == root:
                files = [f for f in search_path.iterdir() if f.is_file()]
            else:
                # For subdirectories, search recursively
                files = list(search_path.rglob('*'))

            for file_path in files:
                if not file_path.is_file() or not _is_safe_path(file_path, root):
                    continue

                if file_path.suffix.lower() in doc_extensions:
                    relative_path = file_path.relative_to(root)
                    doc_dirs.add(str(relative_path.parent))

                    docs_list.append({
                        'name': file_path.name,
                        'path': str(relative_path),
                        'type': file_path.suffix.lstrip('.').upper(),
                        'size_bytes': file_path.stat().st_size,
                    })

        except (OSError, PermissionError) as e:
            logger.warning(f"Could not read path {search_path}: {e}")
            continue

    # Sort by path for consistent output
    docs_list.sort(key=lambda x: x['path'])

    return {
        'docs': docs_list,
        'count': len(docs_list),
        'directories': sorted(list(doc_dirs)),
    }


def show_agent_prompts(root: Path) -> Dict[str, Any]:
    """
    Surface AI agent configuration and prompt files.

    Discovers copilot instructions, agent configs, and AI-related
    documentation that helps agents understand the repository context.

    Args:
        root: Repository root path

    Returns:
        Dictionary with:
            - prompts: List of agent prompt files with metadata
            - count: Total count of agent-related files
            - locations: Common locations where agent files are found

    Example:
        >>> prompts = show_agent_prompts(Path('/path/to/repo'))
        >>> for prompt in prompts['prompts']:
        ...     print(f"Agent file: {prompt['path']}")
    """
    root = Path(root).resolve()

    prompts_list: List[Dict[str, str]] = []
    locations = set()
    seen_paths = set()  # Track seen files to avoid duplicates

    # Agent-related file patterns
    agent_patterns = [
        'copilot-instructions',
        'copilot_instructions',
        'ai-instructions',
        'agent-config',
        'agent_config',
        '.copilot',
        '.ai',
    ]

    # Common agent file locations
    search_paths = [
        root / '.github',
        root / 'docs',
        root,  # Root level files only
    ]

    for search_path in search_paths:
        if not search_path.exists() or not _is_safe_path(search_path, root):
            continue

        try:
            # For root, only check direct children
            if search_path == root:
                files = [f for f in search_path.iterdir() if f.is_file()]
            else:
                # For subdirectories, search recursively
                files = [f for f in search_path.rglob('*') if f.is_file()]

            for file_path in files:
                if not _is_safe_path(file_path, root):
                    continue

                relative_path = file_path.relative_to(root)

                # Skip if already seen
                if str(relative_path) in seen_paths:
                    continue

                # Check if filename matches agent patterns
                name_lower = file_path.name.lower()
                is_agent_file = any(pattern in name_lower for pattern in agent_patterns)

                # Also check for AI/agent related markdown files
                if file_path.suffix.lower() == '.md' and not is_agent_file:
                    try:
                        content_preview = file_path.read_text(encoding='utf-8', errors='ignore')[:200].lower()
                        if any(keyword in content_preview for keyword in ['copilot', 'ai agent', 'agent:', 'prompt']):
                            is_agent_file = True
                    except (OSError, UnicodeDecodeError):
                        pass

                if is_agent_file:
                    seen_paths.add(str(relative_path))
                    locations.add(str(relative_path.parent))

                    prompts_list.append({
                        'name': file_path.name,
                        'path': str(relative_path),
                        'type': 'Agent Configuration' if 'config' in name_lower else 'Agent Instructions',
                        'size_bytes': file_path.stat().st_size,
                    })

        except (OSError, PermissionError) as e:
            logger.warning(f"Could not read path {search_path}: {e}")
            continue

    # Sort by path for consistent output
    prompts_list.sort(key=lambda x: x['path'])

    return {
        'prompts': prompts_list,
        'count': len(prompts_list),
        'locations': sorted(list(locations)),
    }


def check_workspace(root: Path) -> Dict[str, Any]:
    """
    Run basic health checks on the workspace.

    Performs lightweight, deterministic checks to help agents and contributors
    understand the state of the workspace before taking actions.

    Checks include:
    - Repository structure (key directories exist)
    - Python environment (requirements files present)
    - Git status (is this a git repository)
    - Configuration files (common config files exist)

    Args:
        root: Repository root path

    Returns:
        Dictionary with:
            - status: Overall status ('healthy', 'warning', 'error')
            - checks: List of individual check results
            - summary: Human-readable summary message
            - recommendations: List of recommended actions (if any)

    Example:
        >>> health = check_workspace(Path('/path/to/repo'))
        >>> if health['status'] == 'healthy':
        ...     print("Workspace is ready!")
        >>> else:
        ...     print("Issues found:", health['recommendations'])
    """
    root = Path(root).resolve()

    checks: List[Dict[str, Any]] = []
    recommendations: List[str] = []

    # Check 1: Git repository
    git_dir = root / '.git'
    git_check = {
        'name': 'Git Repository',
        'status': 'pass' if git_dir.exists() else 'fail',
        'message': 'Valid git repository' if git_dir.exists() else 'Not a git repository',
    }
    checks.append(git_check)

    if not git_dir.exists():
        recommendations.append('Initialize git repository: git init')

    # Check 2: Python requirements files
    req_files = ['requirements.txt', 'requirements-dev.txt', 'requirements-extensions.txt']
    found_reqs = [f for f in req_files if (root / f).exists()]

    req_check = {
        'name': 'Python Requirements',
        'status': 'pass' if found_reqs else 'warning',
        'message': f"Found {len(found_reqs)} requirements file(s): {', '.join(found_reqs)}" if found_reqs
                   else 'No requirements files found',
        'details': found_reqs,
    }
    checks.append(req_check)

    if not found_reqs:
        recommendations.append('Create requirements.txt for Python dependencies')

    # Check 3: Key directories
    key_dirs = ['scripts', 'tests', 'docs', 'src', '.github']
    found_dirs = [d for d in key_dirs if (root / d).exists() and (root / d).is_dir()]

    dir_check = {
        'name': 'Repository Structure',
        'status': 'pass' if len(found_dirs) >= 3 else 'warning',
        'message': f"Found {len(found_dirs)}/{len(key_dirs)} key directories",
        'details': found_dirs,
    }
    checks.append(dir_check)

    # Check 4: Python environment
    venv_paths = ['.venv', 'venv', '.env']
    has_venv = any((root / vp).exists() for vp in venv_paths)

    python_check = {
        'name': 'Python Environment',
        'status': 'pass' if has_venv else 'info',
        'message': 'Virtual environment detected' if has_venv else 'No virtual environment detected',
    }
    checks.append(python_check)

    if not has_venv and found_reqs:
        recommendations.append('Consider creating a virtual environment: python -m venv .venv')

    # Check 5: Configuration files
    config_files = ['pyproject.toml', 'setup.py', 'setup.cfg', '.flake8', '.bandit']
    found_configs = [cf for cf in config_files if (root / cf).exists()]

    config_check = {
        'name': 'Configuration Files',
        'status': 'pass' if found_configs else 'info',
        'message': f"Found {len(found_configs)} config file(s): {', '.join(found_configs)}" if found_configs
                   else 'No configuration files found',
        'details': found_configs,
    }
    checks.append(config_check)

    # Check 6: CI/CD workflows
    workflows_dir = root / '.github' / 'workflows'
    workflow_files = []
    if workflows_dir.exists():
        workflow_files = [f.name for f in workflows_dir.glob('*.yml') if f.is_file()]

    ci_check = {
        'name': 'CI/CD Workflows',
        'status': 'pass' if workflow_files else 'info',
        'message': f"Found {len(workflow_files)} workflow(s)" if workflow_files else 'No CI/CD workflows found',
        'details': workflow_files[:5],  # Limit to first 5
    }
    checks.append(ci_check)

    # Determine overall status
    failed_checks = [c for c in checks if c['status'] == 'fail']
    warning_checks = [c for c in checks if c['status'] == 'warning']

    if failed_checks:
        overall_status = 'error'
        summary = f"{len(failed_checks)} critical issue(s) found"
    elif warning_checks:
        overall_status = 'warning'
        summary = f"{len(warning_checks)} warning(s) found"
    else:
        overall_status = 'healthy'
        summary = "Workspace appears healthy"

    # Get environment info (safely, no secrets)
    verbose = os.environ.get('COPILOT_TOOLBOX_VERBOSE', 'false').lower() == 'true'

    result = {
        'status': overall_status,
        'summary': summary,
        'checks': checks,
        'recommendations': recommendations,
    }

    if verbose:
        # Safely check if cwd is relative to root (compatible with Python 3.8+)
        cwd = Path.cwd()
        try:
            cwd_relative = str(cwd.relative_to(root))
        except ValueError:
            # Not relative to root
            cwd_relative = str(cwd)

        result['verbose'] = {
            'python_version': sys.version.split()[0],
            'platform': sys.platform,
            'cwd': cwd_relative,
        }

    return result


# Module metadata
__version__ = '1.0.0'
__all__ = ['list_docs', 'show_agent_prompts', 'check_workspace']
