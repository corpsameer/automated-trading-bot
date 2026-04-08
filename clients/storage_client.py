"""Storage client scaffold for local and future external persistence layers."""

from __future__ import annotations


class StorageClient:
    """Client skeleton for persistence of captured and processed automation data."""

    def __init__(self, backend: str) -> None:
        self.backend = backend

    def save_raw_message(self, message: dict) -> None:
        """Persist a captured raw message (placeholder)."""
        raise NotImplementedError("Raw message storage is not implemented yet.")

    def save_parsed_signal(self, signal: dict) -> None:
        """Persist a parsed signal (placeholder)."""
        raise NotImplementedError("Parsed signal storage is not implemented yet.")

    def save_trade_decision(self, decision: dict) -> None:
        """Persist a trade decision record (placeholder)."""
        raise NotImplementedError("Trade decision storage is not implemented yet.")
