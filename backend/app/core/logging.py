"""
Logging configuration.

Sets up Python's built-in logging module with a consistent format
across the whole application. Called once at startup from main.py.
"""

import logging
import sys

from app.core.config import get_settings


def configure_logging() -> None:
    """
    Configure root logging for the application.

    Log level is controlled by the LOG_LEVEL environment variable
    (see core/config.py), so verbosity can be changed per-environment
    without touching code.
    """
    settings = get_settings()

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    logger = logging.getLogger(__name__)
    logger.info("Logging configured (level=%s, env=%s)", settings.LOG_LEVEL, settings.ENV)
