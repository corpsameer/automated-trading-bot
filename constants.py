"""Application configuration constants loaded from the local .env file."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


ALLOWED_APP_MODES = {"capture", "simulated", "live"}


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file into environment variables."""
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _get_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {name}: {raw!r}") from exc


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid float for {name}: {raw!r}") from exc


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean for {name}: {raw!r}")


_load_env_file(ENV_FILE)

APP_NAME = _get_str("APP_NAME", "telegram_coindcx_automation")
APP_ENV = _get_str("APP_ENV", "local")
APP_MODE = _get_str("APP_MODE", "capture")
LOG_LEVEL = _get_str("LOG_LEVEL", "INFO")

if APP_MODE not in ALLOWED_APP_MODES:
    raise ValueError(
        f"Invalid APP_MODE={APP_MODE!r}. Allowed values: {sorted(ALLOWED_APP_MODES)}"
    )

DB_HOST = _get_str("DB_HOST", "127.0.0.1")
DB_PORT = _get_int("DB_PORT", 3306)
DB_NAME = _get_str("DB_NAME", "telegram_coindcx_automation")
DB_USER = _get_str("DB_USER", "root")
DB_PASSWORD = _get_str("DB_PASSWORD", "")
DB_CHARSET = _get_str("DB_CHARSET", "utf8mb4")

if DB_CHARSET.lower() != "utf8mb4":
    raise ValueError("DB_CHARSET must be utf8mb4 for consistent Unicode storage.")

for required_name in ("DB_HOST", "DB_NAME", "DB_USER"):
    if not globals()[required_name]:
        raise ValueError(f"{required_name} is required. Please update your .env file.")

TELEGRAM_API_ID = _get_str("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = _get_str("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE = _get_str("TELEGRAM_PHONE", "")
TELEGRAM_SESSION_NAME = _get_str("TELEGRAM_SESSION_NAME", "telegram_coindcx_session")

COINDCX_API_KEY = _get_str("COINDCX_API_KEY", "")
COINDCX_API_SECRET = _get_str("COINDCX_API_SECRET", "")
COINDCX_BASE_URL = _get_str("COINDCX_BASE_URL", "https://api.coindcx.com")

DEFAULT_SIGNAL_MAX_AGE_SECONDS = _get_int("DEFAULT_SIGNAL_MAX_AGE_SECONDS", 60)
DEFAULT_MAX_OPEN_TRADES = _get_int("DEFAULT_MAX_OPEN_TRADES", 1)
DEFAULT_MAX_LEVERAGE = _get_int("DEFAULT_MAX_LEVERAGE", 5)
DEFAULT_RISK_PER_TRADE = _get_float("DEFAULT_RISK_PER_TRADE", 100.0)
KILL_SWITCH_ENABLED = _get_bool("KILL_SWITCH_ENABLED", True)
