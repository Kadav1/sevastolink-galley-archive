"""
Logging configuration for the Galley API.

Sets up two handlers:
- stdout  — for Docker / uvicorn log capture
- rotating file — at data/logs/galley-api.log (5 MB, keep 3 files)

Log format (grep-friendly, one line per record):
    2026-03-30T14:50:21Z INFO  src.main Galley API starting — initialising database

Log level is controlled by LOG_LEVEL in .env (default: INFO).
"""

import logging
import logging.handlers
import sys
from pathlib import Path


_FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(levelname)-5s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
_FORMATTER.converter = __import__("time").gmtime  # UTC timestamps


def configure_logging(log_level: str, logs_dir: Path) -> None:
    """
    Configure root logger.  Call once at startup before any other imports
    that use the logging module.

    :param log_level: e.g. "INFO", "DEBUG", "WARNING"
    :param logs_dir:  directory where rotating log files are written
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Stdout handler (always on — Docker/uvicorn captures this)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(_FORMATTER)

    # Rotating file handler (5 MB per file, keep 3 backups)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "galley-api.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(_FORMATTER)

    root = logging.getLogger()
    root.setLevel(level)
    # Remove any handlers added by basicConfig or uvicorn before we run
    root.handlers.clear()
    root.addHandler(stdout_handler)
    root.addHandler(file_handler)

    # Quiet noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
