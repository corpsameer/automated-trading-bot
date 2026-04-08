# Telegram + CoinDCX Automation (Bootstrap)

Minimal Python project foundation for a personal automation workflow that will later support:

- Telegram signal capture
- signal parsing
- trade decision processing
- simulated trade tracking with CoinDCX market movement
- live CoinDCX trade execution
- position monitoring
- future reporting/analysis integration

> Current status: **bootstrap only**. Business logic is intentionally not implemented yet.

## Project structure

```text
.
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

## Setup

### 1) Create your local environment file

```bash
cp .env.example .env
```

### 2) Install dependencies

```bash
python -m pip install -r requirements.txt
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

## Notes

- Configuration is loaded from `.env` at repository root via a lightweight built-in loader in `constants.py`.
- `STORAGE_BACKEND` defaults to `local`, with placeholders left for future API/DB-backed storage.
- All clients/services/parsers are scaffolds only.
