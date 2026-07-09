
import httpx
from .normalize import parse_date

SENATE_URL = (
    "https://raw.githubusercontent.com/timothycarambat/"
    "senate-stock-watcher-data/master/aggregate/all_transactions.json"
)
# House feed: historically on S3; currently 403.
HOUSE_URL = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

class StockWatcherSource:
    name = "StockWatcher"

    def __init__(self, limit = 800, timeout = 30.0):
        self.limit = limit
        self.timeout = timeout

    def fetch(self):
        records: list[dict] = []
        records.extend(self.try_fetch(SENATE_URL))
        records.extend(self.try_fetch(HOUSE_URL))

        # Newest first, then cap. Records with unparseable dates sort last.
        records.sort(key=lambda r: parse_date(r.get("transaction_date")) or _MIN_DATE, reverse=True)
        return records[: self.limit] if self.limit else records


    def try_fetch(self, URL):
        try:
            resp = httpx.get(URL, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []
        except (httpx.HTTPError, ValueError):
            print("Couldn't get values from ", {URL})
            return []

from datetime import date as _date 

_MIN_DATE = _date.min