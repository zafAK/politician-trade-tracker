from __future__ import annotations

import json
from datetime import date

from sqlalchemy.orm import Session

from .. import repository
from ..llm.provider import ToolSpec

# --- Handlers ------------------------------------------------------------------

def _trade_dict(t) -> dict:
    return {
        "politician": t.politician.name if t.politician else None,
        "ticker": t.ticker,
        "asset": t.asset_description,
        "type": t.transaction_type,
        "date": t.transaction_date.isoformat() if t.transaction_date else None,
        "min_amount": t.min_amount,
        "max_amount": t.max_amount,
    }


def search_trades(
    session: Session,
    politician: str | None = None,
    ticker: str | None = None,
    transaction_type: str | None = None,
    start: str | None = None,
    end: str | None = None,
    limit: int = 20,
) -> dict:
    rows, total = repository.list_trades(
        session,
        politician=politician,
        ticker=ticker,
        transaction_type=transaction_type,
        start=date.fromisoformat(start) if start else None,
        end=date.fromisoformat(end) if end else None,
        limit=min(limit, 50),
    )
    return {"total_matches": total, "returned": len(rows), "trades": [_trade_dict(t) for t in rows]}


def top_traders_of_ticker(session: Session, ticker: str, limit: int = 10) -> dict:
    pairs = repository.top_traders_of_ticker(session, ticker, limit=limit)
    return {
        "ticker": ticker.upper(),
        "traders": [{"politician": name, "trade_count": n} for name, n in pairs],
    }


def top_tickers(session: Session, limit: int = 10) -> dict:
    pairs = repository.top_tickers(session, limit=limit)
    return {"top_tickers": [{"ticker": t, "trade_count": n} for t, n in pairs]}


def ticker_summary(session: Session, ticker: str) -> dict:
    rows, total = repository.list_trades(session, ticker=ticker, limit=50)
    buys = sum(1 for r in rows if r.transaction_type == "buy")
    sells = sum(1 for r in rows if r.transaction_type == "sell")
    traders = repository.top_traders_of_ticker(session, ticker, limit=5)
    return {
        "ticker": ticker.upper(),
        "total_trades": total,
        "buys": buys,
        "sells": sells,
        "top_traders": [{"politician": n, "trade_count": c} for n, c in traders],
        "recent": [_trade_dict(t) for t in rows[:5]],
    }


def politician_summary(session: Session, name: str) -> dict:
    rows, total = repository.list_trades(session, politician=name, limit=50)
    if not rows:
        return {"politician": name, "total_trades": 0, "note": "No trades found for that name."}
    tickers: dict[str, int] = {}
    for r in rows:
        if r.ticker:
            tickers[r.ticker] = tickers.get(r.ticker, 0) + 1
    top = sorted(tickers.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "politician": rows[0].politician.name,
        "total_trades": total,
        "buys": sum(1 for r in rows if r.transaction_type == "buy"),
        "sells": sum(1 for r in rows if r.transaction_type == "sell"),
        "most_traded_tickers": [{"ticker": t, "trade_count": c} for t, c in top],
        "recent": [_trade_dict(t) for t in rows[:5]],
    }


def recent_trades(session: Session, limit: int = 10) -> dict:
    rows, _ = repository.list_trades(session, limit=limit)
    return {"trades": [_trade_dict(t) for t in rows]}


# --- Registry ------------------------------------------------------------------

_HANDLERS = {
    "search_trades": search_trades,
    "top_traders_of_ticker": top_traders_of_ticker,
    "top_tickers": top_tickers,
    "ticker_summary": ticker_summary,
    "politician_summary": politician_summary,
    "recent_trades": recent_trades,
}

TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="search_trades",
        description=(
            "Search individual trade disclosures with optional filters. Use for questions about "
            "specific trades, or combinations like 'sells of TSLA in 2024'."
        ),
        parameters={
            "type": "object",
            "properties": {
                "politician": {"type": "string", "description": "Full or partial member name"},
                "ticker": {"type": "string", "description": "Stock ticker, e.g. NVDA"},
                "transaction_type": {"type": "string", "enum": ["buy", "sell", "exchange"]},
                "start": {"type": "string", "description": "ISO date lower bound (YYYY-MM-DD)"},
                "end": {"type": "string", "description": "ISO date upper bound (YYYY-MM-DD)"},
                "limit": {"type": ["integer", "string"], "description": "Max rows (<=50)"},
            },
        },
    ),
    ToolSpec(
        name="top_traders_of_ticker",
        description="Rank the members who traded a given ticker most, by number of trades.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "limit": {"type": ["integer", "string"]},
            },
            "required": ["ticker"],
        },
    ),
    ToolSpec(
        name="top_tickers",
        description="The most-traded tickers overall, by number of disclosed trades.",
        parameters={
            "type": "object",
            "properties": {"limit": {"type": ["integer", "string"]}},
        },
    ),
    ToolSpec(
        name="ticker_summary",
        description="A summary for one ticker: total trades, buys vs sells, and top traders.",
        parameters={
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    ),
    ToolSpec(
        name="politician_summary",
        description="A summary for one member: trade count, buys vs sells, most-traded tickers.",
        parameters={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    ),
    ToolSpec(
        name="recent_trades",
        description="The most recent disclosed trades across everyone. Good for 'what's new'.",
        parameters={
            "type": "object",
            "properties": {"limit": {"type": ["integer", "string"]}},
        },
    ),
]


# Args that must be ints. Smaller models often emit them as strings ("limit": "10"), so we
# advertise them as integer-or-string in the schema (to pass provider-side validation) and
# coerce back to int here before the handler runs.
_INT_ARGS = {"limit"}


def _coerce_args(arguments: dict) -> dict:
    coerced = {}
    for key, value in arguments.items():
        if key in _INT_ARGS and isinstance(value, str) and value.lstrip("+-").isdigit():
            coerced[key] = int(value)
        else:
            coerced[key] = value
    return coerced


def dispatch(session: Session, name: str, arguments: dict) -> str:
    """Run a tool by name and return a JSON string for the transcript."""
    handler = _HANDLERS.get(name)
    if handler is None:
        return json.dumps({"error": f"unknown tool '{name}'"})
    try:
        result = handler(session, **_coerce_args(arguments))
    except TypeError as exc:  # bad/missing args from the model
        return json.dumps({"error": f"invalid arguments for {name}: {exc}"})
    except Exception as exc:  # noqa: BLE001 — surface as data, don't crash the loop
        return json.dumps({"error": f"{name} failed: {exc}"})
    return json.dumps(result, default=str)
