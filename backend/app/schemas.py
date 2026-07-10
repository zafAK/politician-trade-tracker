from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PoliticianOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    chamber: str
    party: str | None = None


class TradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    politician_id: int
    politician_name: str | None = None
    ticker: str | None = None
    asset_description: str | None = None
    transaction_type: str
    transaction_date: date | None = None
    min_amount: int | None = None
    max_amount: int | None = None
    source: str | None = None
    synced_at: datetime | None = None


class TradePage(BaseModel):
    """'Showing X of N'."""

    items: list[TradeOut]
    total: int
    limit: int
    offset: int

class TickerCount(BaseModel):
    ticker: str
    trade_count: int

class StatsOut(BaseModel):
    total_trades: int
    total_politicians: int
    last_synced_at: datetime | None = None
    top_tickers: list[TickerCount]

class SyncResult(BaseModel):
    source: str
    inserted: int
    updated: int
    total_in_db: int