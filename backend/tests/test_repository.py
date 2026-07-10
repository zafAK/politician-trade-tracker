"""Repository tests — the shared query layer the API and the agent both depend on."""

from __future__ import annotations

from app import repository
from app.ingest.fixture import FixtureSource
from app.ingest.sync import run_sync


def test_seed_counts(seeded_session):
    total_trades, total_politicians = repository.counts(seeded_session)
    assert total_trades == 15
    assert total_politicians == 6


def test_sync_is_idempotent(session):
    first = run_sync(session, FixtureSource())
    second = run_sync(session, FixtureSource())
    assert first["inserted"] == 15
    assert second["inserted"] == 0  # nothing new on re-run
    assert repository.counts(session)[0] == 15


def test_top_tickers_ordering(seeded_session):
    top = repository.top_tickers(seeded_session, limit=3)
    assert top[0] == ("NVDA", 5)
    tickers = [t for t, _ in top]
    assert tickers == sorted(tickers, key=lambda t: dict(top)[t], reverse=True)


def test_filter_by_ticker(seeded_session):
    rows, total = repository.list_trades(seeded_session, ticker="NVDA")
    assert total == 5
    assert all(r.ticker == "NVDA" for r in rows)


def test_filter_by_politician_partial_match(seeded_session):
    rows, total = repository.list_trades(seeded_session, politician="pelosi")
    assert total == 3
    assert all("Pelosi" in r.politician.name for r in rows)


def test_filter_by_type(seeded_session):
    _, buys = repository.list_trades(seeded_session, transaction_type="buy")
    _, sells = repository.list_trades(seeded_session, transaction_type="sell")
    assert buys + sells == 15


def test_top_traders_of_ticker(seeded_session):
    traders = dict(repository.top_traders_of_ticker(seeded_session, "NVDA"))
    assert traders["Nancy Pelosi"] == 2


def test_pagination(seeded_session):
    page1, total = repository.list_trades(seeded_session, limit=10, offset=0)
    page2, _ = repository.list_trades(seeded_session, limit=10, offset=10)
    assert total == 15
    assert len(page1) == 10
    assert len(page2) == 5
    ids = {t.id for t in page1} | {t.id for t in page2}
    assert len(ids) == 15  # no overlap between pages
