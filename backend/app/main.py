from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db, SessionLocal
from .repository import counts
from .ingest.sync import run_sync
from .ingest.fixture import FixtureSource

from .routers import admin, trades, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup so a fresh clone works with no migration step.
    init_db()
    with SessionLocal() as session:
        totalCounts, _ = counts(session)
        if totalCounts == 0:
            run_sync(session=session, source=FixtureSource())
         
    yield


app = FastAPI(title="Politician Trades Tracker", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trades.router)
app.include_router(admin.router)
app.include_router(chat.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "tradesource": settings.tradesource}
