"""
Shared subprocess execution utilities for M365 Security Toolkit.

Provides consistent subprocess patterns for running scripts across MCP servers.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple


async def run_python_script(
    script_path: Path,
    args: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
) -> Tuple[Optional[int], str, str]:
    """
    Execute a Python script as a subprocess.

    Args:
        script_path: Path to the Python script
        args: Optional list of command-line arguments
        cwd: Optional working directory

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    result = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd) if cwd else None,
    )

    stdout, stderr = await result.communicate()
    return result.returncode, stdout.decode(), stderr.decode()


async def run_python_module(
    module_name: str,
    args: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
) -> Tuple[Optional[int], str, str]:
    """
    Execute a Python module as a subprocess using -m flag.

    Args:
        module_name: Name of the Python module (e.g., "src.integrations.sharepoint_connector")
        args: Optional list of command-line arguments
        cwd: Optional working directory

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    cmd = [sys.executable, "-m", module_name]
    if args:
        cmd.extend(args)

    result = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd) if cwd else None,
    )

    stdout, stderr = await result.communicate()
    return result.returncode, stdout.decode(), stderr.decode()


async def run_powershell_script(
    script_path: Path,
    args: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
    use_pwsh: Optional[bool] = None,
) -> Tuple[Optional[int], str, str]:
    """
    Execute a PowerShell script as a subprocess.

    Args:
        script_path: Path to the PowerShell script
        args: Optional list of command-line arguments
        cwd: Optional working directory
        use_pwsh: If None, auto-detect (pwsh on non-Windows, powershell.exe on Windows).
                  If True, use pwsh. If False, use powershell.exe.

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if use_pwsh is None:
        use_pwsh = os.name != "nt"

    pwsh = "pwsh" if use_pwsh else "powershell.exe"
    cmd = [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]

    if args:
        cmd.extend(args)

    result = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd) if cwd else None,
    )

    stdout, stderr = await result.communicate()
    return result.returncode, stdout.decode(), stderr.decode()
