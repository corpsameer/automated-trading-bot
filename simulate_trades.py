"""Entry script for simulate trades workflow."""

from __future__ import annotations

from constants import APP_MODE
from utils.logger import get_logger


def main() -> None:
    """Bootstrap and start the simulate trades workflow."""
    logger = get_logger(__name__)
    logger.info("Starting simulate_trades.py in mode='%s'", APP_MODE)


if __name__ == "__main__":
    main()
