"""Centralized logging configuration for StashStats."""

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


def setup_logging(
    log_level: str | None = None,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Configure root logger with console and rotating file handlers.

    Args:
        log_level: Logging level name (DEBUG, INFO, WARNING, ERROR).
        log_file: File path for output log file.

    Returns:
        Configured root logger.
    """
    resolved_level_name = (
        log_level
        or os.getenv("LOG_LEVEL")
        or ("DEBUG" if os.getenv("APP_DEBUG", "true").lower() in ("true", "1", "t", "yes") else "INFO")
    )
    level = getattr(logging, resolved_level_name.upper(), logging.INFO)

    resolved_log_file = log_file or os.getenv("LOG_FILE", "logs/stashstats.log")
    log_path = Path(resolved_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers on reload
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        file_handler = RotatingFileHandler(
            str(log_path),
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    if not any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
        for h in root_logger.handlers
    ):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        root_logger.addHandler(stream_handler)

    return root_logger
