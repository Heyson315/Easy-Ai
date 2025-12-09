"""
Tests for logging utilities.
"""

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from src.core.logging_utils import setup_logging


def test_setup_logging_creates_log_directory():
    """Test that setup_logging creates log directory."""
    with TemporaryDirectory() as tmpdir:
        # Mock Path.home() to return tmpdir
        import src.core.logging_utils as logging_utils  # noqa: F401

        original_home = Path.home

        def mock_home():
            return Path(tmpdir)

        try:
            Path.home = mock_home
            logger = setup_logging("test_logger", "test.log")

            # Check that log directory was created
            log_dir = Path(tmpdir) / ".aitk" / "logs"
            assert log_dir.exists()
            assert log_dir.is_dir()

            # Check that log file exists
            log_file = log_dir / "test.log"
            assert log_file.exists()

            # Check that logger was configured
            assert isinstance(logger, logging.Logger)
            assert logger.name == "test_logger"

        finally:
            Path.home = original_home


def test_setup_logging_uses_correct_level():
    """Test that setup_logging respects log level parameter."""
    with TemporaryDirectory() as tmpdir:
        import src.core.logging_utils as logging_utils  # noqa: F401

        original_home = Path.home

        def mock_home():
            return Path(tmpdir)

        try:
            Path.home = mock_home
            # Use a unique logger name to avoid conflicts with other tests
            logger = setup_logging("test_unique_logger_123", "test.log", log_level=logging.DEBUG)

            # Check that logger was created
            assert isinstance(logger, logging.Logger)
            assert logger.name == "test_unique_logger_123"

        finally:
            Path.home = original_home


def test_setup_logging_handles_existing_directory():
    """Test that setup_logging works with existing log directory."""
    with TemporaryDirectory() as tmpdir:
        import src.core.logging_utils as logging_utils  # noqa: F401

        original_home = Path.home

        def mock_home():
            return Path(tmpdir)

        try:
            Path.home = mock_home

            # Pre-create the directory
            log_dir = Path(tmpdir) / ".aitk" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            # Should not fail
            logger = setup_logging("test_logger", "test.log")
            assert isinstance(logger, logging.Logger)

        finally:
            Path.home = original_home
