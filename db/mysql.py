"""Lightweight MySQL connection helpers using PyMySQL."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterator

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from constants import DB_CHARSET, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def get_db_config(include_database: bool = True) -> Dict[str, Any]:
    """Return validated MySQL config for PyMySQL."""
    required_values = {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_USER": DB_USER,
        "DB_CHARSET": DB_CHARSET,
    }
    if include_database:
        required_values["DB_NAME"] = DB_NAME

    missing = [name for name, value in required_values.items() if value in (None, "")]
    if missing:
        raise ValueError(
            f"Missing required DB config: {', '.join(missing)}. "
            "Please update your .env file."
        )

    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME if include_database else None,
        "charset": DB_CHARSET,
        "cursorclass": DictCursor,
        "autocommit": False,
    }


def get_connection(include_database: bool = True) -> Connection:
    """Open a new MySQL connection."""
    config = get_db_config(include_database=include_database)
    if not include_database:
        config.pop("database", None)
    return pymysql.connect(**config)


@contextmanager
def transaction(connection: Connection) -> Iterator[None]:
    """Context manager for transaction-safe write operations."""
    try:
        yield
        connection.commit()
    except Exception:
        connection.rollback()
        raise
