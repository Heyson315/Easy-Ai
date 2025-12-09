#!/usr/bin/env python3
"""
Copilot Toolbox - CLI for discovering repo assets and workspace health checks.

This module provides three commands:
  - list-docs: List documentation files in docs/ and .github/
  - show-agent-prompts: Display summaries of .github/agents/*.md files
  - check-workspace: Verify key files exist and report health status

Security: Never prints secrets, uses environment variables only for non-sensitive toggles.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Union

# Configure logging - structured and secure (no env values exposed)
LOG_LEVEL = os.environ.get("COPILOT_TOOLBOX_VERBOSE", "").lower()
logging.basicConfig(
    level=logging.DEBUG if LOG_LEVEL == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def get_repo_root() -> Path:
    """
    Get the repository root directory.

    Returns:
        Path: Absolute path to repository root.
    """
    # Navigate up from this script to find repo root
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    # If no .git found, assume current working directory
    return Path.cwd()


def list_docs(repo_root: Path, output_format: str = "text") -> Union[str, Dict]:
    """
    List documentation files in docs/ and .github/.

    Args:
        repo_root: Path to repository root
        output_format: Output format ('text' or 'json')

    Returns:
        Formatted string or dictionary with file listings
    """
    logger.debug(f"Listing docs in {repo_root}")

    docs_dir = repo_root / "docs"
    github_dir = repo_root / ".github"

    result: Dict[str, List[str]] = {"docs": [], "github": []}

    # List docs/ directory
    if docs_dir.exists() and docs_dir.is_dir():
        result["docs"] = sorted([
            str(f.relative_to(docs_dir))
            for f in docs_dir.rglob("*")
            if f.is_file() and not f.name.startswith(".")
        ])
        logger.debug(f"Found {len(result['docs'])} files in docs/")
    else:
        logger.warning(f"docs/ directory not found at {docs_dir}")

    # List .github/ directory (excluding workflows subdirectory for brevity)
    if github_dir.exists() and github_dir.is_dir():
        result["github"] = sorted([
            str(f.relative_to(github_dir))
            for f in github_dir.rglob("*")
            if f.is_file()
            and not f.name.startswith(".")
            and "workflows" not in f.parts  # Exclude workflows for cleaner output
        ])
        logger.debug(f"Found {len(result['github'])} files in .github/")
    else:
        logger.warning(f".github/ directory not found at {github_dir}")

    if output_format == "json":
        return result

    # Format as text
    output = []
    output.append("=== Documentation Files ===\n")

    if result["docs"]:
        output.append(f"docs/ ({len(result['docs'])} files):")
        for doc in result["docs"]:
            output.append(f"  - {doc}")
    else:
        output.append("docs/: No files found")

    output.append("")

    if result["github"]:
        output.append(f".github/ ({len(result['github'])} files, excluding workflows/):")
        for gh_file in result["github"]:
            output.append(f"  - {gh_file}")
    else:
        output.append(".github/: No files found")

    return "\n".join(output)


def show_agent_prompts(repo_root: Path, output_format: str = "text") -> Union[str, Dict]:
    """
    Display summaries of .github/agents/*.md files.

    Args:
        repo_root: Path to repository root
        output_format: Output format ('text' or 'json')

    Returns:
        Formatted string or dictionary with agent prompt summaries
    """
    logger.debug(f"Reading agent prompts from {repo_root}")

    agents_dir = repo_root / ".github" / "agents"
    result: Dict[str, Dict[str, str]] = {}

    if not agents_dir.exists() or not agents_dir.is_dir():
        logger.warning(f"Agents directory not found at {agents_dir}")
        if output_format == "json":
            return {"agents": {}, "count": 0}
        return "No agent prompts found (.github/agents/ directory does not exist)"

    # Read all .md files in agents directory
    agent_files = sorted(agents_dir.glob("*.md"))
    logger.debug(f"Found {len(agent_files)} agent files")

    for agent_file in agent_files:
        try:
            content = agent_file.read_text(encoding="utf-8")
            # Extract first non-empty line as summary (after frontmatter if present)
            lines = [line.strip() for line in content.split("\n") if line.strip()]

            # Skip YAML frontmatter if present
            start_idx = 0
            if lines and lines[0] == "---":
                # Find closing ---
                for i in range(1, len(lines)):
                    if lines[i] == "---":
                        start_idx = i + 1
                        break

            # Get first meaningful line as summary
            summary = ""
            for line in lines[start_idx:]:
                if line and not line.startswith("#"):
                    summary = line[:150]  # Limit to 150 chars
                    break
                elif line.startswith("# "):
                    summary = line[2:].strip()[:150]
                    break

            if not summary and lines[start_idx:]:
                summary = lines[start_idx][:150]

            result[agent_file.name] = {
                "file": str(agent_file.relative_to(repo_root)),
                "summary": summary or "No description available",
                "lines": len(content.split("\n")),
            }
        except Exception as e:
            logger.error(f"Error reading {agent_file.name}: {e}")
            result[agent_file.name] = {
                "file": str(agent_file.relative_to(repo_root)),
                "summary": f"Error reading file: {str(e)}",
                "lines": 0,
            }

    if output_format == "json":
        return {"agents": result, "count": len(result)}

    # Format as text
    output = []
    output.append("=== Agent Prompts ===\n")

    if result:
        output.append(f"Found {len(result)} agent prompt(s):\n")
        for agent_name, info in result.items():
            output.append(f"📄 {agent_name}")
            output.append(f"   Path: {info['file']}")
            output.append(f"   Summary: {info['summary']}")
            output.append(f"   Lines: {info['lines']}")
            output.append("")
    else:
        output.append("No agent prompts found in .github/agents/")

    return "\n".join(output)


def check_workspace(repo_root: Path, output_format: str = "text") -> Union[str, Dict]:
    """
    Verify key files exist and report workspace health status.

    Args:
        repo_root: Path to repository root
        output_format: Output format ('text' or 'json')

    Returns:
        Formatted string or dictionary with workspace health report
    """
    logger.debug(f"Checking workspace health for {repo_root}")

    # Define critical files and directories to check
    checks = {
        "README.md": repo_root / "README.md",
        "docs/": repo_root / "docs",
        ".github/workflows/": repo_root / ".github" / "workflows",
        "requirements.txt": repo_root / "requirements.txt",
        ".gitignore": repo_root / ".gitignore",
        "pyproject.toml": repo_root / "pyproject.toml",
    }

    results = {}
    for name, path in checks.items():
        exists = path.exists()
        results[name] = {
            "exists": exists,
            "path": str(path.relative_to(repo_root)),
            "type": "directory" if path.is_dir() else "file" if exists else "unknown",
        }

    # Count workflow files
    workflows_dir = repo_root / ".github" / "workflows"
    workflow_count = 0
    if workflows_dir.exists():
        workflow_count = len(list(workflows_dir.glob("*.yml"))) + len(list(workflows_dir.glob("*.yaml")))
        results[".github/workflows/"]["workflow_count"] = workflow_count

    # Count docs
    docs_dir = repo_root / "docs"
    docs_count = 0
    if docs_dir.exists():
        docs_count = len([f for f in docs_dir.rglob("*") if f.is_file()])
        results["docs/"]["file_count"] = docs_count

    # Calculate health score
    total_checks = len(checks)
    passed_checks = sum(1 for r in results.values() if r["exists"])
    health_score = (passed_checks / total_checks) * 100

    summary = {
        "health_score": health_score,
        "passed": passed_checks,
        "total": total_checks,
        "checks": results,
    }

    if output_format == "json":
        return summary

    # Format as text
    output = []
    output.append("=== Workspace Health Check ===\n")
    output.append(f"Health Score: {health_score:.1f}% ({passed_checks}/{total_checks} checks passed)\n")

    for name, result in results.items():
        status = "✅" if result["exists"] else "❌"
        output.append(f"{status} {name}")

        if name == ".github/workflows/" and result["exists"]:
            output.append(f"   └─ {workflow_count} workflow file(s)")
        elif name == "docs/" and result["exists"]:
            output.append(f"   └─ {docs_count} documentation file(s)")

    output.append("")

    if health_score == 100:
        output.append("✨ Workspace is healthy! All critical files are present.")
    elif health_score >= 75:
        output.append("⚠️  Workspace is mostly healthy, but some files are missing.")
    else:
        output.append("🚨 Workspace needs attention! Critical files are missing.")

    return "\n".join(output)


def main() -> int:
    """
    Main entry point for the Copilot Toolbox CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Copilot Toolbox - Discover repo assets and run workspace health checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.copilot_tools list-docs
  python -m scripts.copilot_tools show-agent-prompts --format json
  python -m scripts.copilot_tools check-workspace
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-docs command
    list_parser = subparsers.add_parser("list-docs", help="List documentation files")
    list_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    # show-agent-prompts command
    show_parser = subparsers.add_parser("show-agent-prompts", help="Display agent prompt summaries")
    show_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    # check-workspace command
    check_parser = subparsers.add_parser("check-workspace", help="Verify workspace health")
    check_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        repo_root = get_repo_root()
        logger.debug(f"Repository root: {repo_root}")

        result: Union[str, Dict]
        if args.command == "list-docs":
            result = list_docs(repo_root, args.format)
        elif args.command == "show-agent-prompts":
            result = show_agent_prompts(repo_root, args.format)
        elif args.command == "check-workspace":
            result = check_workspace(repo_root, args.format)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1

        # Output result
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)

        return 0

    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
