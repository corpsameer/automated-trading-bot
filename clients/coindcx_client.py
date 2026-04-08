"""CoinDCX client scaffold for future market and order operations."""

from __future__ import annotations


class CoinDCXClient:
    """Client skeleton for CoinDCX pricing and trade execution methods."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_price(self, symbol: str) -> float:
        """Get market price for a symbol (placeholder)."""
        raise NotImplementedError("CoinDCX price retrieval is not implemented yet.")

    def place_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Place an order on CoinDCX (placeholder)."""
        raise NotImplementedError("CoinDCX order placement is not implemented yet.")
