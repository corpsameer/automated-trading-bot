"""Entry script for process signals workflow."""

from __future__ import annotations

from constants import APP_MODE
from utils.logger import get_logger


def main() -> None:
    """Bootstrap and start the process signals workflow."""
    logger = get_logger(__name__)
    logger.info("Starting process_signals.py in mode='%s'", APP_MODE)


if __name__ == "__main__":
    main()
