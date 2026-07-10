from sqlalchemy import func, select
from sqlalchemy.orm import Session

from datetime import date, datetime

from .models import Politician, Trade


def get_or_create_politician(
        session,
        name,
        chamber,
        party) -> Politician:
    p = session.scalar(select(Politician).where(Politician.name == name))
    if p is None:
        p = Politician(name = name, chamber=chamber, party=party)
        session.add(p)
        session.flush()
    return p
    

def upsert_trade(session, **fields):
    record = session.scalar(select(Trade).where(Trade.raw_hash == fields["raw_hash"]))
    if record is not None:
        return False
    session.add(Trade(**fields))
    return True


# --- Reads ----------------------------------------

def list_trades(
    session: Session,
    politician: str | None = None,
    ticker: str | None = None,
    transaction_type: str | None = None,
    start: date | None = None,
    end: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Trade], int]:
    stmt = select(Trade).join(Politician)
    if politician:
        stmt = stmt.where(Politician.name.ilike(f"%{politician}%"))
    if ticker:
        stmt = stmt.where(Trade.ticker.ilike(ticker))
    if transaction_type:
        stmt = stmt.where(Trade.transaction_type == transaction_type)
    if start:
        stmt = stmt.where(Trade.transaction_date >= start)
    if end:
        stmt = stmt.where(Trade.transaction_date <= end)

    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        session.scalars(
            stmt.order_by(Trade.transaction_date.desc().nulls_last(), Trade.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return rows, total


def get_politician(session: Session, politician_id: int) -> Politician | None:
    return session.get(Politician, politician_id)


def list_politicians(session: Session) -> list[Politician]:
    return list(session.scalars(select(Politician).order_by(Politician.name)))


def top_tickers(session: Session, limit: int = 10) -> list[tuple[str, int]]:
    stmt = (
        select(Trade.ticker, func.count().label("n"))
        .where(Trade.ticker.is_not(None))
        .group_by(Trade.ticker)
        .order_by(func.count().desc())
        .limit(limit)
    )
    return [(t, n) for t, n in session.execute(stmt).all()]


def distinct_tickers(session: Session) -> list[str]:
    stmt = (
        select(Trade.ticker)
        .where(Trade.ticker.is_not(None))
        .distinct()
        .order_by(Trade.ticker)
    )
    return list(session.scalars(stmt))


def top_traders_of_ticker(session: Session, ticker: str, limit: int = 10) -> list[tuple[str, int]]:
    stmt = (
        select(Politician.name, func.count().label("n"))
        .join(Trade, Trade.politician_id == Politician.id)
        .where(Trade.ticker.ilike(ticker))
        .group_by(Politician.name)
        .order_by(func.count().desc())
        .limit(limit)
    )
    return [(name, n) for name, n in session.execute(stmt).all()]


def counts(session: Session) -> tuple[int, int]:
    total_trades = session.scalar(select(func.count()).select_from(Trade)) or 0
    total_politicians = session.scalar(select(func.count()).select_from(Politician)) or 0
    return total_trades, total_politicians


def last_synced_at(session: Session) -> datetime | None:
    return session.scalar(select(func.max(Trade.synced_at)))