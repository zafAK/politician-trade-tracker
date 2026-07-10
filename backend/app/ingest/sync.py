from sqlalchemy.orm import Session

from .. import repository
from ..config import settings
from ..db import SessionLocal, init_db
from .fixture import FixtureSource
from .normalize import SkipRecord, normalize
from .source import TradeSource


def get_source(name: str | None = None) -> TradeSource:
    name = name or settings.tradesource
    if name == "stock_watcher":
        from .stock_watcher import StockWatcherSource

        return StockWatcherSource()
    return FixtureSource()


def run_sync(session: Session, source: TradeSource | None = None) -> dict:
    source = source or get_source()
    raw_records = source.fetch()

    inserted = 0
    skipped = 0
    seen_hashes: set[str] = set()  # guards against exact-duplicate rows within one feed
    for raw in raw_records:
        try:
            norm = normalize(raw, source.name)
        except SkipRecord:
            skipped += 1
            continue

        # Two identical rows in the same fetch would both pass the DB check, dedupe them here, before touching the DB.
        raw_hash = norm["trade"]["raw_hash"]
        if raw_hash in seen_hashes:
            skipped += 1
            continue
        seen_hashes.add(raw_hash)

        politician = repository.get_or_create_politician(session, **norm["politician"])
        was_new = repository.upsert_trade(
            session, politician_id=politician.id, **norm["trade"]
        )
        inserted += int(was_new)

    session.commit()
    total_trades, _ = repository.counts(session)
    return {
        "source": source.name,
        "inserted": inserted,
        "updated": len(raw_records) - inserted - skipped,
        "skipped": skipped,
        "total_in_db": total_trades,
    }


def main() -> None:
    init_db()
    session = SessionLocal()
    try:
        result = run_sync(session)
        print(
            f"[sync] source={result['source']} inserted={result['inserted']} "
            f"updated={result['updated']} skipped={result['skipped']} "
            f"total_in_db={result['total_in_db']}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()