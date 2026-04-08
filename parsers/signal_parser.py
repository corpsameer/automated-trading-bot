"""Signal parser scaffold for turning raw messages into structured signal data."""

from __future__ import annotations


class SignalParser:
    """Parse raw incoming text into normalized signal objects.

    Future expected input:
    - Raw message string (or message payload)

    Future expected output:
    - Dictionary containing symbol, side, entry, stop-loss, targets, and metadata
    """

    def parse(self, raw_message: str) -> dict:
        """Parse a raw signal message into a structured dictionary (placeholder)."""
        raise NotImplementedError("Signal parsing logic is not implemented yet.")
