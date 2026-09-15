import sqlite3

import pytest

from src.etl.loader import load_database


@pytest.fixture(scope="module")
def loaded_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("etl") / "nifty100.db"
    load_database(db_path=path)
    return path


@pytest.mark.parametrize("table, expected", [
    ("companies", 92),
    ("profitandloss", 1164),
    ("balancesheet", 1058),
    ("cashflow", 1056),
    ("analysis", 4),
    ("documents", 1456),
    ("prosandcons", 4),
    ("sectors", 92),
    ("stock_prices", 5520),
    ("financial_ratios", 1041),
    ("market_cap", 552),
    ("peer_groups", 248),
])
def test_loaded_row_counts(loaded_db, table, expected):
    with sqlite3.connect(loaded_db) as db:
        assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == expected


def test_loaded_database_has_no_foreign_key_errors(loaded_db):
    with sqlite3.connect(loaded_db) as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_loader_is_repeatable(loaded_db):
    load_database(db_path=loaded_db)
    with sqlite3.connect(loaded_db) as db:
        assert db.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 92