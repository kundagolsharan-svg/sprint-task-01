"""Load the supplied Nifty 100 Excel exports into SQLite."""

import csv
import sqlite3
from pathlib import Path

import pandas as pd

from .normaliser import clean_frame, normalize_ticker, normalize_year

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    "companies": "1788501606103-7177b6c2-companies.xlsx", "profitandloss": "1788501607124-aad40f4f-profitandloss.xlsx",
    "balancesheet": "1788501604829-ac8c0874-balancesheet.xlsx", "cashflow": "1788501605758-8e951681-cashflow.xlsx",
    "analysis": "1788501604303-57986a9b-analysis.xlsx", "documents": "1788501606362-ba899c04-documents.xlsx",
    "prosandcons": "1788501607452-d6bbe55b-prosandcons.xlsx", "sectors": "1788501621129-8684701e-sectors.xlsx",
    "stock_prices": "1788501621395-a51977cd-stock_prices.xlsx", "financial_ratios": "1788501620089-fb3ae469-financial_ratios.xlsx",
    "market_cap": "1788501620397-69ae3e7f-market_cap.xlsx", "peer_groups": "1788501620796-5060f580-peer_groups.xlsx",
}
DERIVED_TABLES = {"financial_ratios", "peer_groups"}


def read_source(path: Path) -> pd.DataFrame:
    return clean_frame(pd.read_excel(path))


def load_database(source_dir: Path = ROOT, db_path: Path = ROOT / "nifty100.db") -> dict[str, int]:
    input_dir = source_dir
    if not all((input_dir / filename).exists() for filename in SOURCES.values()):
        test_input_dir = source_dir / "tests" / "etl"
        if all((test_input_dir / filename).exists() for filename in SOURCES.values()):
            input_dir = test_input_dir
    missing_sources = [filename for filename in SOURCES.values() if not (input_dir / filename).exists()]
    if missing_sources:
        raise FileNotFoundError(
            "Missing Excel source files: " + ", ".join(missing_sources)
        )
    db_path.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "output").mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript("""
        DROP TABLE IF EXISTS financial_ratios; DROP TABLE IF EXISTS peer_groups;
        DROP TABLE IF EXISTS market_cap;
        DROP TABLE IF EXISTS stock_prices; DROP TABLE IF EXISTS sectors;
        DROP TABLE IF EXISTS prosandcons; DROP TABLE IF EXISTS documents;
        DROP TABLE IF EXISTS analysis; DROP TABLE IF EXISTS cashflow;
        DROP TABLE IF EXISTS balancesheet; DROP TABLE IF EXISTS profitandloss;
        DROP TABLE IF EXISTS companies;
    """)
    connection.executescript((ROOT / "db" / "schema.sql").read_text())
    audit: dict[str, tuple[int, int]] = {}
    try:
        companies = read_source(input_dir / SOURCES["companies"]).rename(columns={"id": "company_id"})
        companies["company_id"] = companies["company_id"].map(normalize_ticker)
        company_ids = set(companies["company_id"].dropna())
        for table, filename in SOURCES.items():
            if table == "peer_groups":
                continue
            frame = read_source(input_dir / filename)
            source_rows = len(frame)
            if table == "companies":
                frame = frame.rename(columns={"id": "company_id"})
            if "company_id" in frame:
                frame["company_id"] = frame["company_id"].map(normalize_ticker)
            if "year" in frame:
                frame["year"] = frame["year"].map(normalize_year)
            if table == "stock_prices":
                frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
            for column in frame.columns:
                if column not in {"company_id", "year", "date", "annual_report", "pros", "cons", "company_logo", "company_name", "chart_link", "about_company", "website", "nse_profile", "bse_profile", "broad_sector", "sub_sector", "market_cap_category", "compounded_sales_growth", "compounded_profit_growth", "stock_price_cagr", "roe"}:
                    frame[column] = pd.to_numeric(frame[column], errors="coerce")
            frame = frame.drop(columns=["id"], errors="ignore").dropna(subset=["company_id"])
            if table != "companies" and "company_id" in frame:
                frame = frame[frame["company_id"].isin(company_ids)]
            key = [column for column in ("company_id", "year", "date") if column in frame]
            if key:
                frame = frame.drop_duplicates(key, keep="last")
            frame.to_sql(table, connection, if_exists="append", index=False)
            audit[table] = (len(frame), source_rows - len(frame))
        audit["financial_ratios"] = (audit["financial_ratios"][0], audit["financial_ratios"][1])
        peer_groups = read_source(input_dir / SOURCES["peer_groups"])
        peer_groups = peer_groups.drop(columns=["id", "is_benchmark"], errors="ignore")
        peer_groups = peer_groups.merge(peer_groups[["peer_group_name", "company_id"]], on="peer_group_name", suffixes=("", "_peer"))
        peer_groups = peer_groups[peer_groups["company_id"] != peer_groups["company_id_peer"]]
        peer_groups = peer_groups.rename(columns={"company_id": "company_id", "company_id_peer": "peer_company_id"})[["company_id", "peer_company_id"]].drop_duplicates()
        peer_groups.to_sql("peer_groups", connection, if_exists="append", index=False)
        audit["peer_groups"] = (len(peer_groups), 0)
        connection.commit()
    finally:
        with (ROOT / "output" / "load_audit.csv").open("w", newline="", encoding="utf-8") as report:
            writer = csv.writer(report)
            writer.writerow(["table", "rows", "rejected_rows", "critical_rejections"])
            writer.writerows((table, rows, rejected, 0) for table, (rows, rejected) in audit.items())
        connection.close()
    return audit


if __name__ == "__main__":
    print(load_database())