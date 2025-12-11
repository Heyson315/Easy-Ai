"""
Copilot Tools Toolbox CLI - Command-line interface for repository exploration.

This module provides a simple CLI for accessing copilot toolbox functions.
All outputs are JSON-formatted for easy consumption by AI agents and automation tools.

Usage:
    python -m scripts.copilot_tools list-docs [--root PATH]
    python -m scripts.copilot_tools show-prompts [--root PATH]
    python -m scripts.copilot_tools check-workspace [--root PATH]

Examples:
    # List all documentation files
    python -m scripts.copilot_tools list-docs

    # Show agent configuration files
    python -m scripts.copilot_tools show-prompts

    # Run workspace health check
    python -m scripts.copilot_tools check-workspace

    # Specify custom repository root
    python -m scripts.copilot_tools list-docs --root /path/to/repo
"""

import argparse
import json
import sys
from pathlib import Path

from scripts.copilot_tools import list_docs, show_agent_prompts, check_workspace


def find_repo_root() -> Path:
    """
    Find the repository root by looking for .git directory.

    Returns:
        Path to repository root

    Raises:
        RuntimeError: If repository root cannot be found
    """
    current = Path.cwd()

    # Check current directory and parents
    for parent in [current] + list(current.parents):
        if (parent / '.git').exists():
            return parent

    # If no .git found, use current directory
    return current


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        prog='copilot_tools',
        description='Copilot Tools Toolbox - Helper utilities for AI agents and contributors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list-docs
  %(prog)s show-prompts
  %(prog)s check-workspace
  %(prog)s list-docs --root /path/to/repo --pretty
        """
    )

    parser.add_argument(
        'command',
        choices=['list-docs', 'show-prompts', 'check-workspace'],
        help='Command to execute'
    )

    parser.add_argument(
        '--root',
        type=Path,
        default=None,
        help='Repository root path (default: auto-detect from .git)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output for human readability'
    )

    args = parser.parse_args()

    # Determine repository root
    try:
        root = args.root.resolve() if args.root else find_repo_root()

        if not root.exists():
            print(json.dumps({
                'error': 'Repository root does not exist',
                'path': str(root)
            }), file=sys.stderr)
            return 1

    except Exception as e:
        print(json.dumps({
            'error': 'Failed to determine repository root',
            'message': str(e)
        }), file=sys.stderr)
        return 1

    # Execute command
    try:
        if args.command == 'list-docs':
            result = list_docs(root)
        elif args.command == 'show-prompts':
            result = show_agent_prompts(root)
        elif args.command == 'check-workspace':
            result = check_workspace(root)
        else:
            # Should not happen due to argparse choices
            print(json.dumps({
                'error': f'Unknown command: {args.command}'
            }), file=sys.stderr)
            return 1

        # Output result as JSON
        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent))
        return 0

    except Exception as e:
        print(json.dumps({
            'error': f'Command failed: {args.command}',
            'message': str(e),
            'type': type(e).__name__
        }), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
