"""Rule-based pros and cons generator with confidence scores."""

import csv
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def generate(db_path: Path = ROOT / "nifty100.db") -> int:
    db = sqlite3.connect(db_path)
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", db)
    ratios = ratios[ratios.year != "TTM"].sort_values("year")
    latest = ratios.groupby("company_id", as_index=False).tail(1).set_index("company_id")
    companies = pd.read_sql_query("SELECT company_id FROM companies", db)
    sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", db).set_index("company_id")
    rows = []
    for company_id in companies.company_id:
        item = latest.loc[company_id] if company_id in latest.index else pd.Series(dtype=float)
        sector = sectors.loc[company_id, "broad_sector"] if company_id in sectors.index else ""
        def value(field):
            result = item.get(field)
            if result is None or pd.isna(result): return None
            if field in {"icr_label"}: return str(result)
            return float(result)
        pros = [
            ("P01", value("return_on_equity_pct") is not None and value("return_on_equity_pct") > 20, "Consistently high return on equity above 20% demonstrates exceptional capital efficiency", 85),
            ("P03", value("debt_to_equity") == 0, "Debt-free balance sheet provides financial flexibility and eliminates interest burden", 90),
            ("P04", value("revenue_cagr_5yr") is not None and value("revenue_cagr_5yr") > 15, "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum", 82),
            ("P05", value("operating_profit_margin_pct") is not None and value("operating_profit_margin_pct") > 25, "Operating profit margin above 25% indicates strong pricing power and cost discipline", 80),
            ("P06", value("pat_cagr_5yr") is not None and value("pat_cagr_5yr") > 20, "Net profit compounding at above 20% over 5 years creates significant shareholder value", 82),
            ("P07", (value("interest_coverage") or 0) > 10 or value("icr_label") == "Debt Free", "Very high interest coverage ratio reflects negligible financial stress from debt servicing", 78),
            ("P08", value("dividend_payout_ratio_pct") is not None and value("dividend_payout_ratio_pct") > 2 and (value("free_cash_flow_cr") or 0) > 0, "Consistent dividend yield backed by positive free cash flow", 74),
            ("P09", value("eps_cagr_5yr") is not None and value("eps_cagr_5yr") > 15, "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding", 80),
            ("P11", value("revenue_cagr_5yr") is not None and value("pat_cagr_5yr") is not None and value("revenue_cagr_5yr") < value("pat_cagr_5yr"), "Profit growth ahead of revenue growth shows improving operating leverage and scale benefits", 72),
        ]
        cons = [
            ("C01", value("debt_to_equity") is not None and value("debt_to_equity") > 2 and sector != "Financials", f"Debt-to-equity ratio of {value('debt_to_equity'):.2f} is elevated for a non-financial company and warrants monitoring", 88),
            ("C04", value("net_profit_margin_pct") is not None and value("net_profit_margin_pct") < 0, "Company reported a net loss in the most recent financial year", 92),
            ("C06", value("interest_coverage") is not None and value("interest_coverage") < 1.5, "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations", 88),
            ("C07", value("dividend_payout_ratio_pct") is not None and value("dividend_payout_ratio_pct") > 100, "Dividend payout ratio above 100% may be unsustainable", 82),
            ("C10", value("return_on_capital_employed_pct") is not None and value("return_on_capital_employed_pct") < 10, "Return on capital employed below 10% suggests insufficient returns on invested capital", 76),
            ("C12", value("revenue_cagr_5yr") is not None and value("revenue_cagr_5yr") < 5, "Revenue growing at below 5% over 5 years suggests limited business momentum", 72),
        ]
        selected_pros = [row for row in pros if row[1] and row[3] > 60]
        selected_cons = [row for row in cons if row[1] and row[3] > 60]
        if not selected_pros: selected_pros = [("P00", True, "Established operating history and diversified business platform", 61)]
        if not selected_cons: selected_cons = [("C00", True, "Continued monitoring of financial and operating performance is warranted", 61)]
        rows.extend((company_id, "pro", rule, text, confidence) for rule, _, text, confidence in selected_pros)
        rows.extend((company_id, "con", rule, text, confidence) for rule, _, text, confidence in selected_cons)
    with (ROOT / "output" / "pros_cons_generated.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file); writer.writerow(["company_id", "type", "rule_id", "text", "confidence_pct"]); writer.writerows(rows)
    db.close()
    return len(rows)


if __name__ == "__main__":
    print(f"pros_cons_rows={generate()}")
