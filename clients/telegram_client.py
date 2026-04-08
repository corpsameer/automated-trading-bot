"""Telegram client scaffold for future signal capture integration."""

from __future__ import annotations


class TelegramClient:
    """Client skeleton responsible for Telegram connectivity and message fetching."""

    def __init__(self, session_name: str) -> None:
        self.session_name = session_name

    def connect(self) -> None:
        """Connect to Telegram (placeholder)."""
        raise NotImplementedError("Telegram connect logic is not implemented yet.")

    def fetch_messages(self) -> list[dict]:
        """Fetch new Telegram messages (placeholder)."""
        raise NotImplementedError("Telegram fetch logic is not implemented yet.")
