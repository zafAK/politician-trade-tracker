"""Normalization is where the messy real-world data gets tamed, so it earns close tests."""
from datetime import date

from app.ingest.normalize import (
    compute_hash,
    normalize,
    normalize_type,
    parse_amount,
    parse_date,
)


def test_parse_amount_range():
    assert parse_amount("$1,001 - $15,000") == (1001, 15000)
    assert parse_amount("$1,000,001 - $5,000,000") == (1000001, 5000000)


def test_parse_amount_edge_cases():
    assert parse_amount(None) == (None, None)
    assert parse_amount("--") == (None, None)
    assert parse_amount("$50,000") == (50000, 50000)


def test_parse_date_formats():
    assert parse_date("2024-01-12") == date(2024, 1, 12)
    assert parse_date("01/12/2024") == date(2024, 1, 12)
    assert parse_date(None) is None
    assert parse_date("garbage") is None


def test_normalize_type_variants():
    # House spellings
    assert normalize_type("purchase") == "buy"
    assert normalize_type("sale_partial") == "sell"
    assert normalize_type("sale_full") == "sell"
    # Senate spellings
    assert normalize_type("Purchase") == "buy"
    assert normalize_type("Sale (Full)") == "sell"
    assert normalize_type("Sale (Partial)") == "sell"
    assert normalize_type("Exchange") == "exchange"
    assert normalize_type(None) == "exchange"

def test_hash_is_stable_for_identical_records():
    args = ("Jane Doe", "AAPL", "2024-01-01", "$1,001 - $15,000")
    assert compute_hash(*args) == compute_hash(*args)


def test_normalize_house_record():
    raw = {
        "chamber": "house",
        "representative": "Nancy Pelosi",
        "ticker": "nvda",
        "asset_description": "NVIDIA Corporation",
        "type": "purchase",
        "transaction_date": "2024-01-12",
        "amount": "$1,000,001 - $5,000,000",
    }
    out = normalize(raw, "fixture")
    assert out["politician"]["name"] == "Nancy Pelosi"
    assert out["politician"]["chamber"] == "house"
    assert out["trade"]["ticker"] == "NVDA"  # upper-cased
    assert out["trade"]["transaction_type"] == "buy"
    assert out["trade"]["min_amount"] == 1000001


def test_normalize_senate_record_infers_chamber():
    raw = {
        "senator": "Ron L Wyden",
        "ticker": "BYND", 
        "asset_description": "Some Bond",
        "type": "Sale (Full)",
        "transaction_date": "11/10/2020",
        "amount": "$50,001 - $100,000",
    }
    out = normalize(raw, "stock_watcher")
    assert out["politician"]["chamber"] == "senate"
    assert out["trade"]["ticker"] == "BYND"
    assert out["trade"]["transaction_type"] == "sell"
