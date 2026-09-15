"""Cached read-only database access for the dashboard."""

from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "nifty100.db"


def _query(sql, params=()):
    with sqlite3.connect(DB_PATH) as db:
        return pd.read_sql_query(sql, db, params=params)


@st.cache_data(ttl=600)
def get_companies():
    return _query("SELECT * FROM companies ORDER BY company_name")


@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    clauses, params = [], []
    if ticker:
        clauses.append("company_id = ?"); params.append(ticker)
    if year:
        clauses.append("year = ?"); params.append(str(year))
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return _query("SELECT * FROM financial_ratios" + where + " ORDER BY year", params)


@st.cache_data(ttl=600)
def get_pl(ticker):
    return _query("SELECT * FROM profitandloss WHERE company_id = ? ORDER BY year", (ticker,))


@st.cache_data(ttl=600)
def get_bs(ticker):
    return _query("SELECT * FROM balancesheet WHERE company_id = ? ORDER BY year", (ticker,))


@st.cache_data(ttl=600)
def get_cf(ticker):
    return _query("SELECT * FROM cashflow WHERE company_id = ? ORDER BY year", (ticker,))


@st.cache_data(ttl=600)
def get_sectors():
    return _query("SELECT * FROM sectors ORDER BY broad_sector, company_id")


@st.cache_data(ttl=600)
def get_peers(group_name):
    with sqlite3.connect(DB_PATH) as db:
        membership = pd.read_sql_query("SELECT * FROM peer_percentiles WHERE peer_group_name = ?", db, params=(group_name,))
    return membership


@st.cache_data(ttl=600)
def get_valuation(ticker=None):
    clauses, params = [], []
    if ticker:
        clauses.append("company_id = ?"); params.append(ticker)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return _query("SELECT * FROM valuation_summary" + where, params)


@st.cache_data(ttl=600)
def get_market_cap():
    return _query("SELECT * FROM market_cap")


@st.cache_data(ttl=600)
def get_documents(ticker):
    return _query("SELECT * FROM documents WHERE company_id = ? ORDER BY year DESC", (ticker,))


@st.cache_data(ttl=600)
def get_pros_cons(ticker):
    return _query("SELECT * FROM prosandcons WHERE company_id = ?", (ticker,))


@st.cache_data(ttl=600)
def get_capital_allocation():
    return pd.read_csv(ROOT / "output" / "capital_allocation.csv")
