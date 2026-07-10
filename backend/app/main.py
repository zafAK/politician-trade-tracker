from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine, init_db, get_session
from app.ingest.stock_watcher import StockWatcherSource
from app.ingest.normalize import normalize, SkipRecord



# print(normalize({'transaction_date': '12/02/2020', 'owner': 'N/A', 'ticker': 'AAPL', 'asset_description': 'This filing was disclosed via scanned PDF. Use link in ptr_link column to view the PDF.', 'asset_type': 'PDF Disclosed Filing', 'type': 'N/A', 'amount': '$10,000 - $50,000', 'comment': '', 'senator': 'Richard Blumenthal', 'ptr_link': 'https://efdsearch.senate.gov/search/view/paper/2a123633-1454-49ff-8c3b-c4028372a119/'},
#           "fixture"))