# Politician Trades Tracker

Track and explore stock trades disclosed by US politicians. A FastAPI + SQLite backend ingests
and normalizes trade disclosures, and a React + Vite dashboard lets you filter them and ask
questions about them in plain English through a small tool-calling agent.

- **Backend** — FastAPI, SQLAlchemy, SQLite
- **Frontend** — React 19, TypeScript, Vite
- **Chat agent** — pluggable LLM provider (a built-in mock, or Groq)

The app runs with **no configuration and no API keys**. On first startup it creates the database
and seeds it with bundled sample data, and the chat panel answers using the mock provider.

## Requirements

- Python 3.11+
- Node.js 20.19+ (or 22+)

## Setup

Clone the repo:

```bash
git clone https://github.com/zafAK/politician-trade-tracker.git
cd politician-trade-tracker
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is now on **http://localhost:8000**, with interactive docs at
**http://localhost:8000/docs**.

On startup the app creates `backend/trades.db` and, if the database is empty, seeds it from
`data/fixtures/trades.sample.json` (15 trades across 6 politicians). There is no migration step.

Verify it came up:

```bash
curl http://localhost:8000/health
# {"status":"ok","tradesource":"fixture"}
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The dashboard is now on **http://localhost:5173**. It talks to `http://localhost:8000` by
default, which the backend already allows via CORS — so with both servers running, you're done.

To point the frontend at a different API host, set `VITE_API_URL` in `frontend/.env.local`:

```bash
VITE_API_URL=http://localhost:8000
```

## Configuration

All backend settings are optional. To change any of them, copy the example file and edit it:

```bash
cd backend
cp .env.example .env
```

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./trades.db` | Any SQLAlchemy URL. For Postgres: `postgresql+psycopg://user:pass@localhost:5432/trades` |
| `TRADESOURCE` | `fixture` | `fixture` (bundled sample data) or `stock_watcher` (live feed) |
| `LLM_PROVIDER` | `mock` | `mock` (no key needed) or `groq` |
| `GROQ_API_KEY` | _unset_ | Required only when `LLM_PROVIDER=groq`. Free key at [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | |

`.env` is gitignored — keep real keys out of version control.

### Using the real LLM

Set `LLM_PROVIDER=groq` and `GROQ_API_KEY=<your key>`, then restart the backend. If the key is
missing, the app logs a warning and silently falls back to the mock provider rather than failing.

### Using live trade data

The default `fixture` source is bundled sample data. Setting `TRADESOURCE=stock_watcher` pulls
real disclosures from the public Senate Stock Watcher feed (capped at the 800 most recent).

You can also pull live data on demand without changing any config, by passing the source to the
sync endpoint:

```bash
curl -X POST "http://localhost:8000/admin/sync?source=stock_watcher"
# {"source":"StockWatcher","inserted":800,"updated":0,"total_in_db":815}
```

Syncs are idempotent: each trade is hashed, so re-running only inserts genuinely new rows. Note
that the House feed is currently returning 403 upstream; the source logs the failure and
continues with Senate data alone.

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness check and active trade source |
| `GET` | `/trades` | Trades, filtered and paginated |
| `GET` | `/tickers` | Distinct tickers, for autocomplete |
| `GET` | `/politicians` | All politicians |
| `GET` | `/politicians/{id}` | One politician |
| `GET` | `/stats` | Totals, last sync time, top tickers |
| `POST` | `/chat` | Ask a question about the trade data |
| `POST` | `/admin/sync` | Trigger an ingest; optional `?source=` |

`/trades` accepts `politician`, `ticker`, `transaction_type` (`buy`/`sell`/`exchange`), `start`,
`end`, `limit` (1–200, default 50), and `offset`:

```bash
curl "http://localhost:8000/trades?ticker=NVDA&transaction_type=buy&limit=5"
```

Asking the agent a question:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What did Ron Wyden buy?","history":[]}'
```

The response includes both the answer and a `tool_calls` trace showing which tools the agent
called and with what arguments.

## Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

## Project layout

```
backend/
  app/
    main.py          # FastAPI app, CORS, startup seeding
    config.py        # Settings (env-driven)
    db.py            # Engine, session, table creation
    models.py        # Politician and Trade ORM models
    schemas.py       # Pydantic request/response models
    repository.py    # Queries and upserts
    routers/         # trades, admin, chat endpoints
    ingest/          # Sources (fixture, stock_watcher), normalize, sync
    agent/           # Tool-calling chat agent
    llm/             # Provider interface, mock and Groq implementations
  data/fixtures/     # Bundled sample trades
  tests/
frontend/
  src/
    api/             # Typed API client — the only place that talks to the backend
    components/      # Filters, StatCards, TradesTable, ChatPanel
    pages/           # Dashboard
```

## Data model

A **Politician** has a name, chamber, and party. A **Trade** belongs to a politician and records
the ticker, transaction type, date, and the disclosed amount as a `min_amount`/`max_amount` range
(disclosures give brackets, not exact figures). Each trade carries a `raw_hash` for deduplication
and a `source` marking where it came from. `owner` and `asset_type` are Senate-only fields and
stay null for House rows.
