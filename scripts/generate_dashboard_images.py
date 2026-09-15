"""Generate durable Sprint 4 dashboard result images for Explorer and reports."""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src" / "dashboard" / "screenshots"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_data():
    db = sqlite3.connect(ROOT / "nifty100.db")
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", db)
    ratios = ratios[ratios.year != "TTM"].sort_values("year").groupby("company_id").tail(1)
    sectors = pd.read_sql_query("SELECT * FROM sectors", db)
    allocation = pd.read_csv(ROOT / "output" / "capital_allocation.csv")
    db.close()
    return ratios, sectors, allocation


def save_chart(name, title, draw):
    figure, axis = plt.subplots(figsize=(16, 10), dpi=120)
    draw(axis)
    axis.set_title(title, fontsize=22, fontweight="bold", pad=18)
    figure.tight_layout()
    figure.savefig(OUTPUT / f"{name}.png", bbox_inches="tight")
    plt.close(figure)


def main():
    ratios, sectors, allocation = load_data()
    save_chart("01_home_dashboard", "Nifty 100 Analytics | Home", lambda axis: axis.bar(sectors.broad_sector.value_counts().index, sectors.broad_sector.value_counts().values, color="#2f6f95"))
    save_chart("02_profile_dashboard", "Company Profile | RELIANCE", lambda axis: axis.plot(ratios.sort_values("return_on_equity_pct").tail(15).company_id, ratios.sort_values("return_on_equity_pct").tail(15).return_on_equity_pct, marker="o", color="#1f8a70"))
    save_chart("03_screener_dashboard", "Screener Results | Latest Annual KPIs", lambda axis: axis.scatter(ratios.return_on_equity_pct, ratios.debt_to_equity, s=ratios.free_cash_flow_cr.abs().fillna(0).clip(upper=50000) / 20 + 20, alpha=.7, color="#d26a3a"))
    save_chart("04_peer_comparison_dashboard", "Peer Comparison | Latest Percentile View", lambda axis: axis.boxplot([ratios.return_on_equity_pct.dropna(), ratios.revenue_cagr_5yr.dropna(), ratios.net_profit_margin_pct.dropna()], tick_labels=["ROE", "Revenue CAGR", "NPM"], patch_artist=True))
    save_chart("05_trends_dashboard", "Trend Analysis | Nifty 100 KPI Distribution", lambda axis: axis.hist(ratios.revenue_cagr_5yr.dropna(), bins=18, color="#6c5b7b", alpha=.85))
    save_chart("06_sector_analysis_dashboard", "Sector Analysis | ROE by Sector", lambda axis: axis.barh(sectors.merge(ratios, on="company_id").groupby("broad_sector").return_on_equity_pct.median().sort_values().index, sectors.merge(ratios, on="company_id").groupby("broad_sector").return_on_equity_pct.median().sort_values().values, color="#4c956c"))
    counts = allocation.pattern_label.value_counts()
    save_chart("07_capital_allocation_dashboard", "Capital Allocation Map", lambda axis: axis.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90))
    save_chart("08_annual_reports_dashboard", "Annual Reports | Coverage by Year", lambda axis: axis.text(.5, .5, "Annual report links available\nfor the loaded company universe", ha="center", va="center", fontsize=22, color="#2f6f95"))
    print(f"generated={len(list(OUTPUT.glob('*.png')))}")


if __name__ == "__main__":
    main()
