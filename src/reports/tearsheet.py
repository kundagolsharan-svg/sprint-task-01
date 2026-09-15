"""Generate two-page company tearsheets with ReportLab."""

import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, PageBreak, Spacer, Table, TableStyle, Image

ROOT = Path(__file__).resolve().parents[2]


def _page(canvas, document):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#142b4a"))
    canvas.rect(0, A4[1] - 18 * mm, A4[0], 18 * mm, fill=1, stroke=0)
    canvas.restoreState()


def generate_tearsheet(company_id, db_path=ROOT / "nifty100.db", output_dir=ROOT / "reports" / "tearsheets"):
    output_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        company = pd.read_sql_query("SELECT * FROM companies WHERE company_id = ?", db, params=(company_id,)).iloc[0]
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year", db, params=(company_id,))
        pl = pd.read_sql_query("SELECT * FROM profitandloss WHERE company_id = ? ORDER BY year", db, params=(company_id,))
        bs = pd.read_sql_query("SELECT * FROM balancesheet WHERE company_id = ? ORDER BY year", db, params=(company_id,))
        cf = pd.read_sql_query("SELECT * FROM cashflow WHERE company_id = ? ORDER BY year", db, params=(company_id,))
    path = output_dir / f"{company_id}_tearsheet.pdf"
    styles = getSampleStyleSheet(); styles["BodyText"].fontSize = 8; styles["BodyText"].leading = 10
    document = BaseDocTemplate(str(path), pagesize=A4, rightMargin=12 * mm, leftMargin=12 * mm, topMargin=24 * mm, bottomMargin=12 * mm)
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="normal")
    document.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=_page)])
    story = [Paragraph(f"<font color='#142b4a'><b>{company['company_name']} ({company_id})</b></font>", styles["Title"]), Spacer(1, 6 * mm)]
    latest = ratios[ratios.year != "TTM"].tail(1)
    kpi_fields = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct", "debt_to_equity", "revenue_cagr_5yr", "free_cash_flow_cr"]
    kpi_data = [[field.replace("_", " ").title(), "N/A" if latest.empty or pd.isna(latest.iloc[0].get(field)) else f"{latest.iloc[0][field]:.2f}"] for field in kpi_fields]
    table = Table(kpi_data, colWidths=[70 * mm, 45 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eaf1f8")), ("GRID", (0, 0), (-1, -1), .4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story += [table, Spacer(1, 5 * mm), Paragraph("Revenue and Net Profit History", styles["Heading2"])]
    chart = Table([["Year", "Sales", "Net Profit"]] + [[str(row.year), f"{row.sales:.1f}", f"{row.net_profit:.1f}"] for row in pl.tail(10).itertuples()], colWidths=[35 * mm, 50 * mm, 50 * mm], repeatRows=1)
    chart.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe8f4")), ("GRID", (0, 0), (-1, -1), .3, colors.grey)]))
    chart_figure, chart_axis = plt.subplots(figsize=(8, 3.2), dpi=150)
    chart_axis.plot(pl.tail(10).year.astype(str), pl.tail(10).sales, marker="o", label="Revenue")
    chart_axis.plot(pl.tail(10).year.astype(str), pl.tail(10).net_profit, marker="o", label="Net Profit")
    chart_axis.legend(); chart_axis.grid(alpha=.25); chart_axis.tick_params(axis="x", rotation=45); chart_figure.tight_layout()
    chart_buffer = BytesIO(); chart_figure.savefig(chart_buffer, format="png"); plt.close(chart_figure); chart_buffer.seek(0)
    story += [chart, Spacer(1, 4 * mm), Image(chart_buffer, width=175 * mm, height=65 * mm), PageBreak(), Paragraph("Balance Sheet and Cash Flow", styles["Heading2"])]
    bs_table = Table([["Year", "Equity", "Borrowings", "Assets"]] + [[str(row.year), f"{row.equity_capital:.1f}", f"{row.borrowings:.1f}", f"{row.total_assets:.1f}"] for row in bs.tail(10).itertuples()], colWidths=[30 * mm, 45 * mm, 45 * mm, 45 * mm], repeatRows=1)
    bs_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe8f4")), ("GRID", (0, 0), (-1, -1), .3, colors.grey)]))
    bs_figure, bs_axis = plt.subplots(figsize=(8, 3.2), dpi=150)
    bs_axis.bar(bs.tail(10).year.astype(str), bs.tail(10).equity_capital.fillna(0), label="Equity")
    bs_axis.bar(bs.tail(10).year.astype(str), bs.tail(10).borrowings.fillna(0), bottom=bs.tail(10).equity_capital.fillna(0), label="Borrowings")
    bs_axis.legend(); bs_axis.tick_params(axis="x", rotation=45); bs_axis.grid(axis="y", alpha=.25); bs_figure.tight_layout()
    bs_buffer = BytesIO(); bs_figure.savefig(bs_buffer, format="png"); plt.close(bs_figure); bs_buffer.seek(0)
    story += [bs_table, Spacer(1, 4 * mm), Image(bs_buffer, width=175 * mm, height=65 * mm), Spacer(1, 5 * mm), Paragraph("Latest Cash Flow", styles["Heading2"])]
    if not cf.empty:
        row = cf.tail(1).iloc[0]
        story.append(Paragraph(f"CFO: {row.operating_activity} | CFI: {row.investing_activity} | CFF: {row.financing_activity} | Net cash flow: {row.net_cash_flow}", styles["BodyText"]))
    story += [Spacer(1, 5 * mm), Paragraph("Pros and Cons", styles["Heading2"]), Paragraph("Pros: Financial KPIs and cash-flow signals are available in the analytics outputs.", styles["BodyText"]), Paragraph("Cons: Source data contains some periods with incomplete financial coverage.", styles["BodyText"]), Paragraph("Capital allocation: See output/capital_allocation.csv for the year-level classification.", styles["BodyText"])]
    document.build(story)
    return path


def generate_all(db_path=ROOT / "nifty100.db"):
    with sqlite3.connect(db_path) as db:
        companies = db.execute("SELECT company_id FROM companies ORDER BY company_id").fetchall()
    skipped = []
    for (company_id,) in companies:
        with sqlite3.connect(db_path) as db:
            count = db.execute("SELECT COUNT(*) FROM profitandloss WHERE company_id = ? AND year <> 'TTM'", (company_id,)).fetchone()[0]
        if count < 3:
            skipped.append((company_id, "fewer than 3 annual periods; generated with available data"))
        generate_tearsheet(company_id, db_path)
    pd.DataFrame(skipped, columns=["company_id", "reason"]).to_csv(ROOT / "output" / "skipped_tearsheets.csv", index=False)
    return len(companies)


if __name__ == "__main__":
    print(f"tearsheets={generate_all()}")
