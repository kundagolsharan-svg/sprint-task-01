"""Generate company-level cash-flow intelligence outputs."""

import sqlite3
from pathlib import Path

import pandas as pd

from .cashflow_kpis import capex_intensity, capital_allocation_pattern, cfo_quality, fcf_conversion, free_cash_flow

ROOT = Path(__file__).resolve().parents[2]


def generate(db_path: Path = ROOT / "nifty100.db") -> int:
    db = sqlite3.connect(db_path)
    cf = pd.read_sql_query("SELECT * FROM cashflow", db); cf = cf[cf.year != "TTM"].sort_values(["company_id", "year"])
    pl = pd.read_sql_query("SELECT company_id,year,sales,operating_profit,net_profit FROM profitandloss", db); pl = pl[pl.year != "TTM"]
    bs = pd.read_sql_query("SELECT company_id,year,borrowings FROM balancesheet", db); bs = bs[bs.year != "TTM"]
    sectors = pd.read_sql_query("SELECT company_id,broad_sector FROM sectors", db)
    companies = pd.read_sql_query("SELECT company_id FROM companies", db)
    latest = companies.merge(cf.groupby("company_id").tail(1), on="company_id", how="left").merge(pl, on=["company_id", "year"], how="left").merge(bs, on=["company_id", "year"], how="left").merge(sectors, on="company_id", how="left")
    rows, distress = [], []
    for _, item in latest.iterrows():
        history = cf[cf.company_id == item.company_id].merge(pl, on=["company_id", "year"], how="left")
        ratios = history.loc[history.net_profit.notna() & (history.net_profit != 0), "operating_activity"] / history.loc[history.net_profit.notna() & (history.net_profit != 0), "net_profit"]
        cfo_ratio = ratios.tail(5).mean() if len(ratios) else None
        score, label = cfo_quality(cfo_ratio, 1)
        capex, capex_label = capex_intensity(item.investing_activity, item.sales)
        fcf = free_cash_flow(item.operating_activity, item.investing_activity)
        fcf_values = history.operating_activity.fillna(0) + history.investing_activity.fillna(0)
        fcf_cagr = None
        if len(fcf_values) >= 6 and fcf_values.iloc[-6] > 0 and fcf_values.iloc[-1] > 0:
            fcf_cagr = ((fcf_values.iloc[-1] / fcf_values.iloc[-6]) ** .2 - 1) * 100
        distress_flag = (item.operating_activity or 0) < 0 and (item.financing_activity or 0) > 0
        prior_debt = bs[(bs.company_id == item.company_id) & (bs.year < item.year)].sort_values("year").tail(1).borrowings
        deleveraging = (item.financing_activity or 0) < 0 and not prior_debt.empty and item.borrowings < prior_debt.iloc[0]
        pattern = capital_allocation_pattern(item.operating_activity, item.investing_activity, item.financing_activity, cfo_ratio)
        rows.append((item.company_id, item.broad_sector, score, label, capex, capex_label, fcf_cagr, fcf_conversion(fcf, item.operating_profit), int(distress_flag), int(deleveraging), pattern))
        if distress_flag: distress.append((item.company_id, item.broad_sector, item.operating_activity, item.financing_activity, item.net_profit))
    output = ROOT / "output"; output.mkdir(exist_ok=True)
    columns = ["company_id", "sector", "cfo_quality_score", "cfo_quality_label", "capex_intensity_pct", "capex_label", "fcf_cagr_5yr", "fcf_conversion_pct", "distress_flag", "deleveraging_flag", "capital_allocation_label"]
    result = pd.DataFrame(rows, columns=columns); result.to_excel(output / "cashflow_intelligence.xlsx", index=False)
    pd.DataFrame(distress, columns=["company_id", "sector", "cfo_value", "cff_value", "latest_net_profit"]).to_csv(output / "distress_alerts.csv", index=False)
    db.close(); return len(result)


if __name__ == "__main__": print(f"cashflow_intelligence_rows={generate()}")
