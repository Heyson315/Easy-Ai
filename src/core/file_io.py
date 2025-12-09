"""
Shared file I/O utilities for M365 Security Toolkit.

Provides consistent file handling with:
- UTF-8 BOM handling for PowerShell-generated files
- Standardized error handling and messaging
- Common path operations
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, List

# Standard column ordering for CIS audit data
CIS_AUDIT_COLUMNS = [
    "ControlId",
    "Title",
    "Severity",
    "Expected",
    "Actual",
    "Status",
    "Evidence",
    "Reference",
    "Timestamp",
]


def load_json_with_bom(json_path: Path, exit_on_error: bool = True) -> Any:
    """
    Load JSON file with UTF-8 BOM handling for PowerShell-generated files.

    Args:
        json_path: Path to the JSON file
        exit_on_error: If True, print error and call sys.exit(1) on failure.
                       If False, raise the original exception.

    Returns:
        Parsed JSON data (dict or list)

    Raises:
        json.JSONDecodeError: If JSON is invalid (when exit_on_error=False)
        FileNotFoundError: If file doesn't exist (when exit_on_error=False)
        PermissionError: If file can't be read (when exit_on_error=False)
    """
    json_path = Path(json_path)

    if not json_path.exists():
        if exit_on_error:
            print(f"ERROR: Input file not found: {json_path}", file=sys.stderr)
            sys.exit(1)
        raise FileNotFoundError(f"Input file not found: {json_path}")

    try:
        # Use utf-8-sig to handle UTF-8 BOM from PowerShell's UTF8 encoding
        return json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        if exit_on_error:
            print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
            sys.exit(1)
        raise
    except (PermissionError, UnicodeDecodeError) as e:
        if exit_on_error:
            print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
            sys.exit(1)
        raise


def normalize_audit_data(data: Any) -> List[dict]:
    """
    Normalize audit data to a list of dictionaries, ensuring all standard
    columns are present.

    Handles both single object and array formats from audit JSON files.

    Args:
        data: Parsed JSON data (can be dict or list)

    Returns:
        List of audit result dictionaries with all standard columns.
    """
    if not data:
        return []

    results = [data] if isinstance(data, dict) else data

    normalized_results = []
    for audit_item in results:
        normalized_item = {column_name: "" for column_name in CIS_AUDIT_COLUMNS}
        normalized_item.update(audit_item)
        normalized_results.append(normalized_item)

    return normalized_results


def ensure_parent_dir(path: Path) -> Path:
    """
    Ensure the parent directory of a path exists.

    Args:
        path: File path whose parent directory should exist

    Returns:
        The original path (for method chaining)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
