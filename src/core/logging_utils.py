"""
Shared logging utilities for M365 Security Toolkit.

Provides consistent logging configuration across all MCP servers and scripts.
"""

import inspect
import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    logger_name: Optional[str] = None,
    log_filename: str = "m365_toolkit.log",
    log_level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure logging with consistent format and handlers.

    Creates log directory at ~/.aitk/logs/ if it doesn't exist.

    Args:
        logger_name: Name for the logger (default: caller's module name)
        log_filename: Name of log file in ~/.aitk/logs/
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    log_dir = Path.home() / ".aitk" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / log_filename),
            logging.StreamHandler(),
        ],
    )

    # Use caller's module name if not specified
    if logger_name is None:
        frame = inspect.currentframe()
        caller_frame = frame.f_back if frame else None
        logger_name = caller_frame.f_globals.get("__name__", "root") if caller_frame else "root"

    return logging.getLogger(logger_name)
