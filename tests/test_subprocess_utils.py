"""
Tests for subprocess utilities.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.core.subprocess_utils import run_python_module, run_python_script


@pytest.mark.asyncio
async def test_run_python_script_success():
    """Test running a simple Python script."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        script = tmpdir / "test_script.py"
        script.write_text('print("Hello, World!")')

        returncode, stdout, stderr = await run_python_script(script)

        assert returncode == 0
        assert "Hello, World!" in stdout
        assert stderr == ""


@pytest.mark.asyncio
async def test_run_python_script_with_args():
    """Test running a Python script with arguments."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        script = tmpdir / "test_script.py"
        script.write_text(
            """
import sys
print(f"Args: {' '.join(sys.argv[1:])}")
"""
        )

        returncode, stdout, stderr = await run_python_script(script, args=["arg1", "arg2"])

        assert returncode == 0
        assert "Args: arg1 arg2" in stdout


@pytest.mark.asyncio
async def test_run_python_script_error():
    """Test running a Python script that raises an error."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        script = tmpdir / "test_script.py"
        script.write_text('raise ValueError("Test error")')

        returncode, stdout, stderr = await run_python_script(script)

        assert returncode != 0
        assert "ValueError: Test error" in stderr


@pytest.mark.asyncio
async def test_run_python_module():
    """Test running a Python module."""
    # Use a built-in module for testing
    returncode, stdout, stderr = await run_python_module("json.tool", args=["--help"])

    assert returncode == 0
    assert "usage" in stdout.lower()


@pytest.mark.asyncio
async def test_run_python_script_with_cwd():
    """Test running a Python script with a working directory."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        script = tmpdir / "test_script.py"
        script.write_text(
            """
import os
print(f"CWD: {os.getcwd()}")
"""
        )

        returncode, stdout, stderr = await run_python_script(script, cwd=tmpdir)

        assert returncode == 0
        assert str(tmpdir) in stdout
