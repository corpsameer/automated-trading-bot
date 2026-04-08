# Telegram + CoinDCX Automation (Bootstrap + MySQL Storage)

Minimal Python project foundation for a personal automation workflow that will later support:

- Telegram signal capture
- signal parsing
- trade decision processing
- simulated trade tracking with CoinDCX market movement
- live CoinDCX trade execution
- position monitoring
- reporting/analysis integration

> Current status: **storage foundation ready with MySQL**. Telegram/CoinDCX business logic is intentionally not implemented yet.

## Project structure

```text
.
├── init_db.py
├── listener.py
├── process_signals.py
├── decide_trades.py
├── simulate_trades.py
├── execute_live_trades.py
├── monitor_positions.py
├── capture_prices.py
├── constants.py
├── README.md
├── .env.example
├── requirements.txt
├── __init__.py
├── db/
│   ├── __init__.py
│   ├── mysql.py
│   └── schema.py
├── clients/
│   ├── __init__.py
│   ├── telegram_client.py
│   ├── coindcx_client.py
│   └── storage_client.py
├── parsers/
│   ├── __init__.py
│   └── signal_parser.py
├── services/
│   ├── __init__.py
│   ├── decision_engine.py
│   ├── risk_manager.py
│   ├── simulator.py
│   ├── position_monitor.py
│   └── price_tracker.py
└── utils/
    ├── __init__.py
    ├── logger.py
    ├── helpers.py
    └── time_utils.py
```

## Modes

`APP_MODE` supports exactly three values:

- `capture` - for message capture and data ingestion flows
- `simulated` - for paper/simulated trade flow
- `live` - for real trade execution flow

If `APP_MODE` is anything else, startup fails with a clear error.

## MySQL requirement

This project now uses **MySQL only** as the storage backend.

Required local setup:

1. MySQL server running locally/remotely.
2. User credentials in `.env` with permission to create database/schema.

Required DB config keys:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_CHARSET` (`utf8mb4`)

## Setup

### 1) Create your local environment file

```bash
cp .env.example .env
```

### 2) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3) Initialize MySQL schema

```bash
python init_db.py
```

This command:

- creates the configured database if missing
- creates all required tables and indexes
- seeds default `system_settings`

## Verify schema in MySQL

```sql
USE telegram_coindcx_automation;
SHOW TABLES;
SELECT * FROM system_settings;
```

## Optional quick storage check from Python

```python
from datetime import datetime
from clients.storage_client import StorageClient

store = StorageClient()
channel_id = store.create_channel("Demo Channel", "demo_channel")
raw_id = store.save_raw_message(
    channel_id=channel_id,
    telegram_message_id="msg-1",
    message_text="BTC long 60000-60500",
    message_time=datetime.utcnow(),
)
print(channel_id, raw_id)
print(store.get_pending_raw_messages(limit=10))
```

## Run scripts manually

Each script currently boots config + logging and prints a startup message.

```bash
python listener.py
python process_signals.py
python decide_trades.py
python simulate_trades.py
python execute_live_trades.py
python monitor_positions.py
python capture_prices.py
```
