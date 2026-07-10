from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import repository
from ..db import get_session
from ..schemas import (
    PoliticianOut,
    StatsOut,
    TickerCount,
    TradeOut,
    TradePage,
)

router = APIRouter(tags=["trades"])


def _to_trade_out(trade) -> TradeOut:
    return TradeOut(
        id=trade.id,
        politician_id=trade.politician_id,
        politician_name=trade.politician.name if trade.politician else None,
        ticker=trade.ticker,
        asset_description=trade.asset_description,
        transaction_type=trade.transaction_type,
        transaction_date=trade.transaction_date,
        min_amount=trade.min_amount,
        max_amount=trade.max_amount,
        source=trade.source,
        synced_at=trade.synced_at,
    )


@router.get("/trades", response_model=TradePage)
def get_trades(
    politician: str | None = None,
    ticker: str | None = None,
    transaction_type: str | None = Query(None, pattern="^(buy|sell|exchange)$"),
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> TradePage:
    rows, total = repository.list_trades(
        session,
        politician=politician,
        ticker=ticker,
        transaction_type=transaction_type,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return TradePage(
        items=[_to_trade_out(t) for t in rows], total=total, limit=limit, offset=offset
    )


@router.get("/tickers", response_model=list[str])
def get_tickers(session: Session = Depends(get_session)) -> list[str]:
    """All distinct tickers, for the search-field autocomplete."""
    return repository.distinct_tickers(session)


@router.get("/politicians", response_model=list[PoliticianOut])
def get_politicians(session: Session = Depends(get_session)) -> list[PoliticianOut]:
    return [PoliticianOut.model_validate(p) for p in repository.list_politicians(session)]


@router.get("/politicians/{politician_id}", response_model=PoliticianOut)
def get_politician(politician_id: int, session: Session = Depends(get_session)) -> PoliticianOut:
    p = repository.get_politician(session, politician_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Politician not found")
    return PoliticianOut.model_validate(p)


@router.get("/stats", response_model=StatsOut)
def get_stats(session: Session = Depends(get_session)) -> StatsOut:
    total_trades, total_politicians = repository.counts(session)
    return StatsOut(
        total_trades=total_trades,
        total_politicians=total_politicians,
        last_synced_at=repository.last_synced_at(session),
        top_tickers=[
            TickerCount(ticker=t, trade_count=n) for t, n in repository.top_tickers(session)
        ],
    )
