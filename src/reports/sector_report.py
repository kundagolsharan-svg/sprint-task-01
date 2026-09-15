"""Generate one-page PDF summaries for each sector."""

import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[2]


def generate_sector_reports(db_path=ROOT / "nifty100.db"):
    output = ROOT / "reports" / "sector"; output.mkdir(parents=True, exist_ok=True)
    for old_report in output.glob("*_report.pdf"):
        old_report.unlink()
    with sqlite3.connect(db_path) as db:
        sectors = pd.read_sql_query("SELECT * FROM sectors", db)
        peer_members = pd.read_sql_query("SELECT DISTINCT peer_group_name, company_id FROM peer_percentiles", db)
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios", db)
        ratios = ratios[ratios.year != "TTM"].sort_values("year").groupby("company_id").tail(1)
    styles = getSampleStyleSheet()
    groups = [(sector, members) for sector, members in sectors.groupby("broad_sector")]
    if len(groups) < 11:
        groups = [(group, members.merge(sectors[["company_id"]], on="company_id", how="inner")) for group, members in peer_members.groupby("peer_group_name")]
    for sector, members in groups:
        data = members.merge(ratios, on="company_id", how="left")
        path = output / f"{sector.replace(' ', '_')}_report.pdf"
        story = [Paragraph(f"{sector} Sector Report", styles["Title"]), Spacer(1, 10)]
        table_data = [["Company", "ROE", "ROCE", "NPM", "D/E", "Revenue CAGR"]]
        table_data += [[str(row.company_id), f"{row.return_on_equity_pct:.2f}", f"{row.return_on_capital_employed_pct:.2f}", f"{row.net_profit_margin_pct:.2f}", f"{row.debt_to_equity:.2f}", f"{row.revenue_cagr_5yr:.2f}"] for row in data.itertuples()]
        table = Table(table_data, repeatRows=1, colWidths=[35, 55, 55, 55, 45, 70])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe8f4")), ("GRID", (0, 0), (-1, -1), .3, colors.grey)]))
        story.append(table)
        SimpleDocTemplate(str(path), pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24).build(story)
    return len(list(output.glob("*_report.pdf")))


if __name__ == "__main__": print(f"sector_reports={generate_sector_reports()}")
