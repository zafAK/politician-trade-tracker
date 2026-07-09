from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine, init_db
from app.ingest.stock_watcher import StockWatcherSource


init_db()

src = StockWatcherSource(limit = 5)
records = src.fetch()
print("got: ", len(records))
print(records[0])