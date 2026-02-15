import logging
import os
import sys


def configure_logging(level: str | int | None = None) -> None:
    """Configure root logger for the application.

    This sets a simple console handler and a sensible default format.
    Calling multiple times will reset existing handlers to avoid duplicates.
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    # Allow either numeric or textual level
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

    root = logging.getLogger()
    # Remove existing handlers to avoid duplicate logs when reloaded
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
