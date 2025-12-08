"""
Tests for the performance profiling utilities.
"""

import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from src.core.profiler import memory_profile, profile_function, profile_script


class TestProfiler:
    """Tests for the profiling functions."""

    def test_profile_function_decorator(self, capsys):
        """Test the @profile_function decorator captures and prints execution time."""

        @profile_function
        def dummy_function():
            time.sleep(0.01)
            return "done"

        result = dummy_function()
        captured = capsys.readouterr()

        assert result == "done"
        assert "dummy_function took" in captured.out
        assert "s" in captured.out

    def test_profile_script_prints_to_console(self, capsys):
        """Test that profile_script prints cProfile stats to the console."""

        def script_to_profile():
            sum(i for i in range(1000))

        profile_script(script_to_profile)
        captured = capsys.readouterr()

        assert "ncalls" in captured.out
        assert "tottime" in captured.out
        assert "cumtime" in captured.out
        assert "script_to_profile" in captured.out

    def test_profile_script_saves_to_file(self):
        """Test that profile_script saves detailed stats to a file."""
        with TemporaryDirectory() as td:
            output_file = Path(td) / "profile_stats.txt"

            def script_to_profile():
                time.sleep(0.01)

            profile_script(script_to_profile, output_file=str(output_file))

            assert output_file.exists()
            content = output_file.read_text()
            assert "ncalls" in content
            assert "tottime" in content
            assert "script_to_profile" in content

    def test_memory_profile_decorator_with_library(self):
        """Test the @memory_profile decorator when memory_profiler is installed."""
        # Mock the memory_profiler library
        mock_mem_profile = MagicMock(side_effect=lambda f: f)
        sys.modules["memory_profiler"] = MagicMock(profile=mock_mem_profile)

        @memory_profile
        def dummy_mem_function():
            return [1] * 100

        dummy_mem_function()
        mock_mem_profile.assert_called_once()

        # Cleanup the mock
        del sys.modules["memory_profiler"]

    def test_memory_profile_decorator_without_library(self, capsys):
        """Test that @memory_profile handles ImportError gracefully."""
        # Ensure memory_profiler is not in sys.modules
        if "memory_profiler" in sys.modules:
            del sys.modules["memory_profiler"]

        @memory_profile
        def dummy_mem_function():
            return "unprofiled"

        result = dummy_mem_function()
        captured = capsys.readouterr()

        assert result == "unprofiled"
        assert "memory-profiler not installed" in captured.out

    def test_profile_function_preserves_signature(self):
        """Test that the decorator preserves the original function's signature."""

        @profile_function
        def function_with_args(a: int, b: str = "default") -> str:
            """A docstring."""
            return f"{a}-{b}"

        assert function_with_args.__name__ == "function_with_args"
        assert function_with_args.__doc__ == "A docstring."

        result = function_with_args(1, b="custom")
        assert result == "1-custom"


if __name__ == "__main__":
    pytest.main()
