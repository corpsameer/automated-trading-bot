"""Database creation and schema initialization for MySQL."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from pymysql.connections import Connection

from constants import (
    APP_MODE,
    DB_CHARSET,
    DB_NAME,
    DEFAULT_MAX_LEVERAGE,
    DEFAULT_MAX_OPEN_TRADES,
    DEFAULT_RISK_PER_TRADE,
    DEFAULT_SIGNAL_MAX_AGE_SECONDS,
    KILL_SWITCH_ENABLED,
)
from db.mysql import transaction


def utcnow_naive() -> datetime:
    """Return UTC time as naive datetime for DATETIME columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_database_if_not_exists(connection: Connection) -> None:
    """Create configured database if it does not already exist."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            f"CHARACTER SET {DB_CHARSET} COLLATE {DB_CHARSET}_unicode_ci"
        )
    connection.commit()


def initialize_schema(connection: Connection) -> None:
    """Create all schema objects and seed default system settings."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS telegram_channels (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            channel_name VARCHAR(255) NOT NULL,
            channel_identifier VARCHAR(255) NOT NULL UNIQUE,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            allowed_for_live TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS telegram_messages_raw (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            channel_id BIGINT UNSIGNED NOT NULL,
            telegram_message_id VARCHAR(255) NOT NULL,
            message_text LONGTEXT NOT NULL,
            message_time DATETIME NOT NULL,
            received_at DATETIME NOT NULL,
            edited_at DATETIME NULL,
            raw_payload_json LONGTEXT NULL,
            parse_status VARCHAR(50) NOT NULL DEFAULT 'pending',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            UNIQUE KEY uq_channel_message (channel_id, telegram_message_id),
            KEY idx_telegram_messages_channel_time (channel_id, message_time),
            KEY idx_telegram_messages_parse_status (parse_status),
            CONSTRAINT fk_tmr_channel
                FOREIGN KEY (channel_id) REFERENCES telegram_channels(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS parsed_signals (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            raw_message_id BIGINT UNSIGNED NOT NULL UNIQUE,
            channel_id BIGINT UNSIGNED NOT NULL,
            symbol VARCHAR(100) NULL,
            market_type VARCHAR(50) NULL,
            side VARCHAR(20) NULL,
            entry_min DECIMAL(20,8) NULL,
            entry_max DECIMAL(20,8) NULL,
            stop_loss DECIMAL(20,8) NULL,
            target_1 DECIMAL(20,8) NULL,
            target_2 DECIMAL(20,8) NULL,
            target_3 DECIMAL(20,8) NULL,
            leverage DECIMAL(10,2) NULL,
            signal_type VARCHAR(50) NULL,
            signal_time DATETIME NULL,
            parser_status VARCHAR(50) NOT NULL,
            parser_error TEXT NULL,
            parsed_json LONGTEXT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            KEY idx_parsed_signals_parser_status (parser_status),
            KEY idx_parsed_signals_symbol (symbol),
            CONSTRAINT fk_ps_raw_message
                FOREIGN KEY (raw_message_id) REFERENCES telegram_messages_raw(id),
            CONSTRAINT fk_ps_channel
                FOREIGN KEY (channel_id) REFERENCES telegram_channels(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS trade_decisions (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            parsed_signal_id BIGINT UNSIGNED NOT NULL UNIQUE,
            system_mode VARCHAR(20) NOT NULL,
            decision VARCHAR(50) NOT NULL,
            reason TEXT NULL,
            market_price_at_decision DECIMAL(20,8) NULL,
            price_deviation_pct DECIMAL(10,4) NULL,
            risk_amount DECIMAL(20,8) NULL,
            leverage_used DECIMAL(10,2) NULL,
            capital_allocated DECIMAL(20,8) NULL,
            qty DECIMAL(20,8) NULL,
            decided_at DATETIME NOT NULL,
            decision_json LONGTEXT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            KEY idx_trade_decisions_decision (decision),
            KEY idx_trade_decisions_system_mode (system_mode),
            CONSTRAINT fk_td_parsed_signal
                FOREIGN KEY (parsed_signal_id) REFERENCES parsed_signals(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS positions (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            trade_decision_id BIGINT UNSIGNED NOT NULL,
            mode VARCHAR(20) NOT NULL,
            symbol VARCHAR(100) NOT NULL,
            side VARCHAR(20) NOT NULL,
            entry_type VARCHAR(50) NULL,
            planned_entry_min DECIMAL(20,8) NULL,
            planned_entry_max DECIMAL(20,8) NULL,
            actual_entry_price DECIMAL(20,8) NULL,
            actual_entry_time DATETIME NULL,
            qty DECIMAL(20,8) NULL,
            leverage DECIMAL(10,2) NULL,
            stop_loss DECIMAL(20,8) NULL,
            target_1 DECIMAL(20,8) NULL,
            target_2 DECIMAL(20,8) NULL,
            target_3 DECIMAL(20,8) NULL,
            status VARCHAR(50) NOT NULL,
            exit_price DECIMAL(20,8) NULL,
            exit_time DATETIME NULL,
            exit_reason VARCHAR(100) NULL,
            realized_pnl DECIMAL(20,8) NULL,
            realized_pnl_pct DECIMAL(10,4) NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            KEY idx_positions_status (status),
            KEY idx_positions_symbol (symbol),
            CONSTRAINT fk_positions_trade_decision
                FOREIGN KEY (trade_decision_id) REFERENCES trade_decisions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            trade_decision_id BIGINT UNSIGNED NOT NULL,
            position_id BIGINT UNSIGNED NULL,
            order_mode VARCHAR(20) NOT NULL,
            exchange_order_id VARCHAR(255) NULL,
            symbol VARCHAR(100) NOT NULL,
            side VARCHAR(20) NOT NULL,
            order_type VARCHAR(50) NOT NULL,
            price DECIMAL(20,8) NULL,
            trigger_price DECIMAL(20,8) NULL,
            qty DECIMAL(20,8) NULL,
            status VARCHAR(50) NOT NULL,
            response_json LONGTEXT NULL,
            placed_at DATETIME NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            CONSTRAINT fk_orders_trade_decision
                FOREIGN KEY (trade_decision_id) REFERENCES trade_decisions(id),
            CONSTRAINT fk_orders_position
                FOREIGN KEY (position_id) REFERENCES positions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            position_id BIGINT UNSIGNED NULL,
            symbol VARCHAR(100) NOT NULL,
            source VARCHAR(50) NOT NULL,
            price DECIMAL(20,8) NULL,
            mark_price DECIMAL(20,8) NULL,
            high_price DECIMAL(20,8) NULL,
            low_price DECIMAL(20,8) NULL,
            open_price DECIMAL(20,8) NULL,
            close_price DECIMAL(20,8) NULL,
            volume DECIMAL(30,8) NULL,
            snapshot_time DATETIME NOT NULL,
            snapshot_type VARCHAR(50) NOT NULL,
            raw_payload_json LONGTEXT NULL,
            created_at DATETIME NOT NULL,
            KEY idx_price_snapshots_symbol_time (symbol, snapshot_time),
            CONSTRAINT fk_price_snapshots_position
                FOREIGN KEY (position_id) REFERENCES positions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS execution_logs (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            position_id BIGINT UNSIGNED NULL,
            trade_decision_id BIGINT UNSIGNED NULL,
            log_type VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            payload_json LONGTEXT NULL,
            created_at DATETIME NOT NULL,
            KEY idx_execution_logs_created_at (created_at),
            CONSTRAINT fk_execution_logs_position
                FOREIGN KEY (position_id) REFERENCES positions(id),
            CONSTRAINT fk_execution_logs_trade_decision
                FOREIGN KEY (trade_decision_id) REFERENCES trade_decisions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(191) NOT NULL UNIQUE,
            setting_value TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            KEY idx_system_settings_setting_key (setting_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS trade_analysis_metrics (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            position_id BIGINT UNSIGNED NOT NULL UNIQUE,
            mfe DECIMAL(20,8) NULL,
            mae DECIMAL(20,8) NULL,
            time_to_entry_seconds INT NULL,
            time_to_exit_seconds INT NULL,
            max_profit_pct DECIMAL(10,4) NULL,
            max_drawdown_pct DECIMAL(10,4) NULL,
            entry_validity_status VARCHAR(50) NULL,
            analysis_json LONGTEXT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            CONSTRAINT fk_trade_analysis_metrics_position
                FOREIGN KEY (position_id) REFERENCES positions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
    ]

    with transaction(connection):
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)

        seed_default_system_settings(connection)


def seed_default_system_settings(connection: Connection) -> None:
    """Seed default settings if keys do not exist."""
    now = utcnow_naive()
    defaults: Dict[str, str] = {
        "app_mode": APP_MODE,
        "kill_switch_enabled": str(KILL_SWITCH_ENABLED).lower(),
        "default_signal_max_age_seconds": str(DEFAULT_SIGNAL_MAX_AGE_SECONDS),
        "default_max_open_trades": str(DEFAULT_MAX_OPEN_TRADES),
        "default_max_leverage": str(DEFAULT_MAX_LEVERAGE),
        "default_risk_per_trade": str(DEFAULT_RISK_PER_TRADE),
    }

    insert_sql = """
        INSERT INTO system_settings (setting_key, setting_value, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            setting_key = setting_key
    """
    with connection.cursor() as cursor:
        for key, value in defaults.items():
            cursor.execute(insert_sql, (key, value, now, now))
