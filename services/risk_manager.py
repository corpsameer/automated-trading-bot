"""Risk manager scaffold for future risk controls and limits."""

from __future__ import annotations


class RiskManager:
    """Apply position and leverage constraints before execution (future implementation)."""

    def validate(self, trade_decision: dict) -> bool:
        """Validate a trade decision against risk constraints (placeholder)."""
        raise NotImplementedError("Risk validation logic is not implemented yet.")
