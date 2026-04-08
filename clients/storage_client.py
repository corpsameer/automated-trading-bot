"""MySQL-backed storage client for automation entities."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable

from db.mysql import get_connection, transaction


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _serialize_json(data: Any | None) -> str | None:
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False)


class StorageClient:
    """Direct MySQL storage client with simple CRUD methods."""

    def create_channel(
        self,
        channel_name: str,
        channel_identifier: str,
        is_active: bool = True,
        allowed_for_live: bool = False,
    ) -> int:
        now = _utcnow_naive()
        sql = """
            INSERT INTO telegram_channels (
                channel_name, channel_identifier, is_active, allowed_for_live, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                channel_name = VALUES(channel_name),
                is_active = VALUES(is_active),
                allowed_for_live = VALUES(allowed_for_live),
                updated_at = VALUES(updated_at),
                id = LAST_INSERT_ID(id)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        channel_name,
                        channel_identifier,
                        int(is_active),
                        int(allowed_for_live),
                        now,
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def get_active_channels(self) -> list[dict[str, Any]]:
        sql = "SELECT * FROM telegram_channels WHERE is_active = 1 ORDER BY id ASC"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return list(cursor.fetchall())

    def get_channel_by_identifier(self, channel_identifier: str) -> dict[str, Any] | None:
        sql = "SELECT * FROM telegram_channels WHERE channel_identifier = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (channel_identifier,))
                return cursor.fetchone()

    def save_raw_message(
        self,
        channel_id: int,
        telegram_message_id: str,
        message_text: str,
        message_time: datetime,
        received_at: datetime | None = None,
        edited_at: datetime | None = None,
        raw_payload: dict[str, Any] | str | None = None,
        parse_status: str = "pending",
    ) -> int:
        now = _utcnow_naive()
        received = received_at or now
        sql = """
            INSERT INTO telegram_messages_raw (
                channel_id, telegram_message_id, message_text, message_time, received_at,
                edited_at, raw_payload_json, parse_status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                message_text = VALUES(message_text),
                message_time = VALUES(message_time),
                received_at = VALUES(received_at),
                edited_at = VALUES(edited_at),
                raw_payload_json = VALUES(raw_payload_json),
                parse_status = VALUES(parse_status),
                updated_at = VALUES(updated_at),
                id = LAST_INSERT_ID(id)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        channel_id,
                        telegram_message_id,
                        message_text,
                        message_time,
                        received,
                        edited_at,
                        _serialize_json(raw_payload),
                        parse_status,
                        now,
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def get_pending_raw_messages(self, limit: int = 100) -> list[dict[str, Any]]:
        sql = """
            SELECT * FROM telegram_messages_raw
            WHERE parse_status = 'pending'
            ORDER BY message_time ASC
            LIMIT %s
        """
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (limit,))
                return list(cursor.fetchall())

    def mark_raw_message_parse_status(self, raw_message_id: int, parse_status: str) -> None:
        sql = "UPDATE telegram_messages_raw SET parse_status = %s, updated_at = %s WHERE id = %s"
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(sql, (parse_status, _utcnow_naive(), raw_message_id))

    def save_parsed_signal(
        self,
        raw_message_id: int,
        channel_id: int,
        parser_status: str,
        symbol: str | None = None,
        market_type: str | None = None,
        side: str | None = None,
        entry_min: Any | None = None,
        entry_max: Any | None = None,
        stop_loss: Any | None = None,
        target_1: Any | None = None,
        target_2: Any | None = None,
        target_3: Any | None = None,
        leverage: Any | None = None,
        signal_type: str | None = None,
        signal_time: datetime | None = None,
        parser_error: str | None = None,
        parsed_payload: dict[str, Any] | str | None = None,
    ) -> int:
        now = _utcnow_naive()
        sql = """
            INSERT INTO parsed_signals (
                raw_message_id, channel_id, symbol, market_type, side,
                entry_min, entry_max, stop_loss, target_1, target_2, target_3,
                leverage, signal_type, signal_time, parser_status, parser_error,
                parsed_json, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                channel_id = VALUES(channel_id),
                symbol = VALUES(symbol),
                market_type = VALUES(market_type),
                side = VALUES(side),
                entry_min = VALUES(entry_min),
                entry_max = VALUES(entry_max),
                stop_loss = VALUES(stop_loss),
                target_1 = VALUES(target_1),
                target_2 = VALUES(target_2),
                target_3 = VALUES(target_3),
                leverage = VALUES(leverage),
                signal_type = VALUES(signal_type),
                signal_time = VALUES(signal_time),
                parser_status = VALUES(parser_status),
                parser_error = VALUES(parser_error),
                parsed_json = VALUES(parsed_json),
                updated_at = VALUES(updated_at),
                id = LAST_INSERT_ID(id)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        raw_message_id,
                        channel_id,
                        symbol,
                        market_type,
                        side,
                        entry_min,
                        entry_max,
                        stop_loss,
                        target_1,
                        target_2,
                        target_3,
                        leverage,
                        signal_type,
                        signal_time,
                        parser_status,
                        parser_error,
                        _serialize_json(parsed_payload),
                        now,
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def get_pending_parsed_signals(self, limit: int = 100) -> list[dict[str, Any]]:
        sql = """
            SELECT * FROM parsed_signals
            WHERE parser_status = 'pending'
            ORDER BY id ASC
            LIMIT %s
        """
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (limit,))
                return list(cursor.fetchall())

    def save_trade_decision(
        self,
        parsed_signal_id: int,
        system_mode: str,
        decision: str,
        decided_at: datetime,
        reason: str | None = None,
        market_price_at_decision: Any | None = None,
        price_deviation_pct: Any | None = None,
        risk_amount: Any | None = None,
        leverage_used: Any | None = None,
        capital_allocated: Any | None = None,
        qty: Any | None = None,
        decision_payload: dict[str, Any] | str | None = None,
    ) -> int:
        now = _utcnow_naive()
        sql = """
            INSERT INTO trade_decisions (
                parsed_signal_id, system_mode, decision, reason,
                market_price_at_decision, price_deviation_pct, risk_amount, leverage_used,
                capital_allocated, qty, decided_at, decision_json, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                system_mode = VALUES(system_mode),
                decision = VALUES(decision),
                reason = VALUES(reason),
                market_price_at_decision = VALUES(market_price_at_decision),
                price_deviation_pct = VALUES(price_deviation_pct),
                risk_amount = VALUES(risk_amount),
                leverage_used = VALUES(leverage_used),
                capital_allocated = VALUES(capital_allocated),
                qty = VALUES(qty),
                decided_at = VALUES(decided_at),
                decision_json = VALUES(decision_json),
                updated_at = VALUES(updated_at),
                id = LAST_INSERT_ID(id)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        parsed_signal_id,
                        system_mode,
                        decision,
                        reason,
                        market_price_at_decision,
                        price_deviation_pct,
                        risk_amount,
                        leverage_used,
                        capital_allocated,
                        qty,
                        decided_at,
                        _serialize_json(decision_payload),
                        now,
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def get_trade_decision_by_parsed_signal_id(
        self, parsed_signal_id: int
    ) -> dict[str, Any] | None:
        sql = "SELECT * FROM trade_decisions WHERE parsed_signal_id = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (parsed_signal_id,))
                return cursor.fetchone()

    def create_position(
        self,
        trade_decision_id: int,
        mode: str,
        symbol: str,
        side: str,
        status: str,
        entry_type: str | None = None,
        planned_entry_min: Any | None = None,
        planned_entry_max: Any | None = None,
        actual_entry_price: Any | None = None,
        actual_entry_time: datetime | None = None,
        qty: Any | None = None,
        leverage: Any | None = None,
        stop_loss: Any | None = None,
        target_1: Any | None = None,
        target_2: Any | None = None,
        target_3: Any | None = None,
    ) -> int:
        now = _utcnow_naive()
        sql = """
            INSERT INTO positions (
                trade_decision_id, mode, symbol, side, entry_type,
                planned_entry_min, planned_entry_max, actual_entry_price, actual_entry_time,
                qty, leverage, stop_loss, target_1, target_2, target_3,
                status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        trade_decision_id,
                        mode,
                        symbol,
                        side,
                        entry_type,
                        planned_entry_min,
                        planned_entry_max,
                        actual_entry_price,
                        actual_entry_time,
                        qty,
                        leverage,
                        stop_loss,
                        target_1,
                        target_2,
                        target_3,
                        status,
                        now,
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def get_open_positions(self, limit: int = 100) -> list[dict[str, Any]]:
        sql = """
            SELECT * FROM positions
            WHERE status IN ('open', 'active', 'pending_entry')
            ORDER BY id ASC
            LIMIT %s
        """
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (limit,))
                return list(cursor.fetchall())

    def update_position_status(
        self,
        position_id: int,
        status: str,
        exit_price: Any | None = None,
        exit_time: datetime | None = None,
        exit_reason: str | None = None,
        realized_pnl: Any | None = None,
        realized_pnl_pct: Any | None = None,
    ) -> None:
        sql = """
            UPDATE positions
            SET status = %s,
                exit_price = %s,
                exit_time = %s,
                exit_reason = %s,
                realized_pnl = %s,
                realized_pnl_pct = %s,
                updated_at = %s
            WHERE id = %s
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        status,
                        exit_price,
                        exit_time,
                        exit_reason,
                        realized_pnl,
                        realized_pnl_pct,
                        _utcnow_naive(),
                        position_id,
                    ),
                )

    def save_price_snapshot(
        self,
        symbol: str,
        source: str,
        snapshot_time: datetime,
        snapshot_type: str,
        position_id: int | None = None,
        price: Any | None = None,
        mark_price: Any | None = None,
        high_price: Any | None = None,
        low_price: Any | None = None,
        open_price: Any | None = None,
        close_price: Any | None = None,
        volume: Any | None = None,
        raw_payload: dict[str, Any] | str | None = None,
    ) -> int:
        now = _utcnow_naive()
        sql = """
            INSERT INTO price_snapshots (
                position_id, symbol, source, price, mark_price, high_price, low_price,
                open_price, close_price, volume, snapshot_time, snapshot_type,
                raw_payload_json, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        position_id,
                        symbol,
                        source,
                        price,
                        mark_price,
                        high_price,
                        low_price,
                        open_price,
                        close_price,
                        volume,
                        snapshot_time,
                        snapshot_type,
                        _serialize_json(raw_payload),
                        now,
                    ),
                )
                return int(cursor.lastrowid)

    def save_price_snapshots_bulk(self, snapshots: Iterable[dict[str, Any]]) -> int:
        rows = list(snapshots)
        if not rows:
            return 0

        now = _utcnow_naive()
        sql = """
            INSERT INTO price_snapshots (
                position_id, symbol, source, price, mark_price, high_price, low_price,
                open_price, close_price, volume, snapshot_time, snapshot_type,
                raw_payload_json, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = [
            (
                row.get("position_id"),
                row["symbol"],
                row["source"],
                row.get("price"),
                row.get("mark_price"),
                row.get("high_price"),
                row.get("low_price"),
                row.get("open_price"),
                row.get("close_price"),
                row.get("volume"),
                row["snapshot_time"],
                row["snapshot_type"],
                _serialize_json(row.get("raw_payload")),
                now,
            )
            for row in rows
        ]

        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.executemany(sql, values)
        return len(values)

    def save_execution_log(
        self,
        log_type: str,
        message: str,
        position_id: int | None = None,
        trade_decision_id: int | None = None,
        payload: dict[str, Any] | str | None = None,
    ) -> int:
        sql = """
            INSERT INTO execution_logs (
                position_id, trade_decision_id, log_type, message, payload_json, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        position_id,
                        trade_decision_id,
                        log_type,
                        message,
                        _serialize_json(payload),
                        _utcnow_naive(),
                    ),
                )
                return int(cursor.lastrowid)

    def get_setting(self, setting_key: str) -> str | None:
        sql = "SELECT setting_value FROM system_settings WHERE setting_key = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (setting_key,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return row["setting_value"]

    def set_setting(self, setting_key: str, setting_value: str) -> None:
        now = _utcnow_naive()
        sql = """
            INSERT INTO system_settings (setting_key, setting_value, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                setting_value = VALUES(setting_value),
                updated_at = VALUES(updated_at)
        """
        with get_connection() as conn, transaction(conn):
            with conn.cursor() as cursor:
                cursor.execute(sql, (setting_key, setting_value, now, now))

    def get_all_settings(self) -> list[dict[str, Any]]:
        sql = "SELECT * FROM system_settings ORDER BY setting_key ASC"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return list(cursor.fetchall())
