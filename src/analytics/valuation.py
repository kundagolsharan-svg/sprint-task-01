"""Market-multiple valuation summary and flags."""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def build_valuation(db_path: Path = ROOT / "nifty100.db") -> pd.DataFrame:
    with sqlite3.connect(db_path) as db:
        market = pd.read_sql_query("SELECT * FROM market_cap", db)
        market = market.sort_values("year").groupby("company_id", as_index=False).tail(1)
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios", db)
        ratios = ratios[ratios.year != "TTM"].sort_values("year").groupby("company_id", as_index=False).tail(1)
        companies = pd.read_sql_query("SELECT company_id, company_name FROM companies", db)
        sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", db)
    cashflow = pd.read_sql_query("SELECT company_id, year, operating_activity, investing_activity FROM cashflow", sqlite3.connect(db_path))
    cashflow = cashflow[cashflow.year != "TTM"].sort_values("year").groupby("company_id", as_index=False).tail(1)
    result = market.merge(companies, on="company_id", how="left").merge(sectors, on="company_id", how="left").merge(cashflow, on="company_id", how="left")
    result["fcf_yield_pct"] = (result["operating_activity"].fillna(0) + result["investing_activity"].fillna(0)) / result["market_cap_crore"].replace(0, pd.NA) * 100
    result["5yr_median_PE"] = result.groupby("broad_sector")["pe_ratio"].transform("median")
    result["PE_vs_sector_median_pct"] = (result["pe_ratio"] / result["5yr_median_PE"].replace(0, pd.NA) - 1) * 100
    result["flag"] = result.apply(lambda row: "Caution" if row.pe_ratio > row["5yr_median_PE"] * 1.5 else "Discount" if row.pe_ratio < row["5yr_median_PE"] * .7 else "Fair", axis=1)
    columns = ["company_id", "company_name", "broad_sector", "pe_ratio", "pb_ratio", "ev_ebitda", "fcf_yield_pct", "5yr_median_PE", "PE_vs_sector_median_pct", "flag"]
    result = result[columns].rename(columns={"broad_sector": "sector", "pe_ratio": "P/E", "pb_ratio": "P/B", "ev_ebitda": "EV/EBITDA"})
    result = result.fillna({"P/E": 0, "P/B": 0, "EV/EBITDA": 0, "fcf_yield_pct": 0, "5yr_median_PE": 0, "PE_vs_sector_median_pct": 0})
    return result.sort_values("company_id").reset_index(drop=True)


def generate_valuation_outputs(db_path: Path = ROOT / "nifty100.db") -> pd.DataFrame:
    result = build_valuation(db_path)
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    result.to_excel(output / "valuation_summary.xlsx", index=False)
    result[result["flag"].isin(["Caution", "Discount"])].to_csv(output / "valuation_flags.csv", index=False)
    with sqlite3.connect(db_path) as db:
        result.to_sql("valuation_summary", db, if_exists="replace", index=False)
    return result


if __name__ == "__main__":
    print(generate_valuation_outputs().shape)
