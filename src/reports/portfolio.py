"""Generate an alphabetical portfolio summary PDF."""

import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[2]


def generate(db_path=ROOT / "nifty100.db"):
    with sqlite3.connect(db_path) as db:
        companies = pd.read_sql_query("SELECT company_id, company_name FROM companies ORDER BY company_id", db)
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios", db)
    ratios = ratios[ratios.year != "TTM"].sort_values("year").groupby("company_id").tail(1).set_index("company_id")
    path = ROOT / "reports" / "portfolio" / "portfolio_summary.pdf"
    styles = getSampleStyleSheet(); story = []
    for index, company in companies.iterrows():
        row = ratios.loc[company.company_id] if company.company_id in ratios.index else None
        story.append(Paragraph(f"{company.company_name} ({company.company_id})", styles["Title"]))
        if row is not None:
            text = f"ROE: {row.return_on_equity_pct:.2f} | ROCE: {row.return_on_capital_employed_pct:.2f} | NPM: {row.net_profit_margin_pct:.2f} | D/E: {row.debt_to_equity:.2f} | Revenue CAGR: {row.revenue_cagr_5yr:.2f} | FCF: {row.free_cash_flow_cr:.2f}"
        else:
            text = "No latest-year ratio data available."
        story += [Spacer(1, 20), Paragraph(text, styles["BodyText"])]
        if index < len(companies) - 1: story.append(PageBreak())
    SimpleDocTemplate(str(path), pagesize=A4).build(story)
    return path


if __name__ == "__main__": print(generate())
