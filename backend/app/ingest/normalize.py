from datetime import date, datetime
import re

import hashlib

class SkipRecord(Exception):
    """Raised when a raw record can't be normalized (missing essentials)."""


def parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(raw: str | None) -> tuple[int | None, int | None]:
    """"$1,001 - $15,000" -> (1001, 15000). Single values -> (v, v). Unknown -> (None, None)."""
    if not raw:
        return None, None
    nums = [int(n.replace(",", "")) for n in re.findall(r"[\d,]+", raw)]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return min(nums), max(nums)

def normalize_type(raw: str | None) -> str:
    if not raw:
        return "exchange"
    text = raw.strip().lower()
    if text.startswith(("purchase", "buy")):
        return "buy"
    if text.startswith(("sale", "sell")):
        return "sell"
    if text.startswith("exchange"):
        return "exchange"
    return "exchange"

def compute_hash(name, ticker, tdate, amount):
    key = "|".join([name, ticker or "", tdate or "", amount or ""])
    return hashlib.sha256(key.encode()).hexdigest()

def normalize(raw, source) -> dict:
    name = raw.get("representative") or raw.get("senator") or raw.get("name")
    if not name:
        raise SkipRecord("No member name")

    ticker = (raw.get("ticker") or "").strip().upper()
    if ticker in {"--", "N/A", "NONE", ""}:
        raise SkipRecord("No usable ticker")

    amount_min, amount_max = parse_amount(raw.get("amount"))
    if amount_min is None or amount_max is None:
        raise SkipRecord("No usable amount")

    if raw.get("chamber"):
        chamber = raw["chamber"]
    else:
        if raw.get("senator"):
            chamber = "senate"  
        else: 
            chamber = "house"
    

    return {
         "politician": {
            "name": name.strip(),
            "chamber": chamber,
            "party": raw.get("party"),
        },
        "trade": {
            "ticker": ticker,
            "asset_description": raw.get("asset_description"),
            "transaction_type": normalize_type(raw.get("type")),
            "transaction_date": parse_date(raw.get("transaction_date")),
            "min_amount": amount_min,
            "max_amount": amount_max,
            "raw_hash": compute_hash(
                name.strip(),
                ticker,
                raw.get("transaction_date", ""),
                raw.get("amount", ""),
            ),
            "source": source,
        },
    }

