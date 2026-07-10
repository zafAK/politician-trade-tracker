"""Shared test fixtures.

Each test gets a fresh in-memory SQLite database (StaticPool so the whole test shares one
connection). `seeded_session` runs the real ingestion pipeline over the bundled fixture, so
tests exercise the same normalize -> upsert path the app uses — not hand-built rows.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (register mappers)
from app.db import Base
from app.ingest.fixture import FixtureSource
from app.ingest.sync import run_sync


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def seeded_session(session: Session) -> Session:
    run_sync(session, FixtureSource())
    return session
