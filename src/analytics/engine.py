"""Populate financial_ratios and Sprint 2 cash-flow outputs."""

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

from .cagr import cagr
from .cashflow_kpis import capital_allocation_pattern, capex_intensity, cfo_quality, fcf_conversion, free_cash_flow
from .ratios import asset_turnover, debt_to_equity, high_leverage_flag, interest_coverage, interest_coverage_label, interest_warning, net_debt, net_profit_margin, opm_cross_check, operating_profit_margin, return_on_assets, return_on_capital_employed, return_on_equity

ROOT = Path(__file__).resolve().parents[2]
RATIO_COLUMNS = [
    "company_id", "year", "net_profit_margin_pct", "operating_profit_margin_pct", "return_on_equity_pct", "return_on_capital_employed_pct", "return_on_assets_pct", "debt_to_equity", "high_leverage_flag", "interest_coverage", "icr_label", "icr_warning_flag", "net_debt_cr", "asset_turnover", "free_cash_flow_cr", "cfo_quality_ratio", "cfo_quality_label", "capex_intensity_pct", "capex_intensity_label", "fcf_conversion_pct", "earnings_per_share", "book_value_per_share", "dividend_payout_ratio_pct", "total_debt_cr", "cash_from_operations_cr", "revenue_cagr_3yr", "revenue_cagr_3yr_flag", "revenue_cagr_5yr", "revenue_cagr_5yr_flag", "revenue_cagr_10yr", "revenue_cagr_10yr_flag", "pat_cagr_3yr", "pat_cagr_3yr_flag", "pat_cagr_5yr", "pat_cagr_5yr_flag", "pat_cagr_10yr", "pat_cagr_10yr_flag", "eps_cagr_3yr", "eps_cagr_3yr_flag", "eps_cagr_5yr", "eps_cagr_5yr_flag", "eps_cagr_10yr", "eps_cagr_10yr_flag", "composite_quality_score"
]


def _number(value):
    return None if value is None else float(value)


def _year(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _cagr_for(history, year, years):
    cutoff = _year(year)
    usable = [(item_year, value) for item_year, value in history if item_year != "TTM" and (cutoff is None or _year(item_year) is None or _year(item_year) <= cutoff)]
    usable = sorted(usable, key=lambda item: (_year(item[0]) is None, _year(item[0]) or 0))
    if len(usable) <= years:
        return None, "INSUFFICIENT"
    return cagr(usable[-years - 1][1], usable[-1][1], years)


def populate_ratios(db_path: Path = ROOT / "nifty100.db") -> int:
    db = sqlite3.connect(db_path)
    db.execute("DROP TABLE IF EXISTS financial_ratios")
    definitions = ", ".join(f"{column} {'TEXT' if column.endswith('_flag') or column in {'company_id', 'year', 'icr_label', 'cfo_quality_label', 'capex_intensity_label'} else 'INTEGER' if column.endswith('_flag') else 'REAL'}" for column in RATIO_COLUMNS)
    db.execute(f"CREATE TABLE financial_ratios ({definitions}, PRIMARY KEY(company_id, year), FOREIGN KEY(company_id) REFERENCES companies(company_id))")
    pl_rows = db.execute("SELECT company_id, year, sales, operating_profit, opm_percentage, other_income, interest, net_profit, eps, dividend_payout FROM profitandloss ORDER BY company_id, year").fetchall()
    histories = defaultdict(lambda: {"sales": [], "net_profit": [], "eps": []})
    for company_id, year, sales, operating_profit, opm, other_income, interest, net_profit, eps, dividend in pl_rows:
        histories[company_id]["sales"].append((year, sales))
        histories[company_id]["net_profit"].append((year, net_profit))
        histories[company_id]["eps"].append((year, eps))
    query = """SELECT p.company_id,p.year,p.sales,p.operating_profit,p.opm_percentage,p.other_income,p.interest,p.net_profit,p.eps,p.dividend_payout,b.equity_capital,b.reserves,b.borrowings,b.investments,b.total_assets,c.operating_activity,c.investing_activity,c.financing_activity,s.broad_sector FROM profitandloss p LEFT JOIN balancesheet b USING(company_id,year) LEFT JOIN cashflow c USING(company_id,year) LEFT JOIN sectors s USING(company_id) ORDER BY p.company_id,p.year"""
    edge_cases = []
    company_reference = {company_id: (roce, roe) for company_id, roce, roe in db.execute("SELECT company_id, roce_percentage, roe_percentage FROM companies")}
    cfo_history = defaultdict(list)
    for company_id, cfo, pat in db.execute("SELECT c.company_id, c.operating_activity, p.net_profit FROM cashflow c LEFT JOIN profitandloss p USING(company_id, year)"):
        if cfo is not None and pat not in (None, 0):
            cfo_history[company_id].append(cfo / pat)
    output_rows = []
    for row in db.execute(query):
        company_id, year, sales, op_profit, source_opm, other_income, interest, net_profit, eps, dividend, equity, reserves, borrowings, investments, assets, cfo, cfi, cff, sector = row
        ebit = (op_profit or 0) + (other_income or 0)
        fcf = free_cash_flow(cfo, cfi)
        average_cfo_ratio = sum(cfo_history[company_id][-5:]) / len(cfo_history[company_id][-5:]) if cfo_history[company_id] else None
        cfo_ratio, cfo_label = cfo_quality(average_cfo_ratio, 1)
        capex_pct, capex_label = capex_intensity(cfi, sales)
        roe = return_on_equity(net_profit or 0, equity, reserves)
        roce = return_on_capital_employed(ebit, equity, reserves, borrowings)
        opm = operating_profit_margin(op_profit, sales)
        if opm_cross_check(opm, source_opm):
            edge_cases.append(f"{company_id},{year}: OPM mismatch; category=data source issue; computed={opm}; source={source_opm}")
        cagr_values = []
        for field in ("sales", "net_profit", "eps"):
            for window in (3, 5, 10):
                cagr_values.extend(_cagr_for(histories[company_id][field], year, window))
        score = sum(value is not None for value in (net_profit_margin(net_profit, sales), roe, roce, asset_turnover(sales, assets), cfo_ratio))
        output_rows.append((company_id, year, net_profit_margin(net_profit, sales), opm, roe, roce, return_on_assets(net_profit, assets), debt_to_equity(borrowings or 0, equity, reserves), int(high_leverage_flag(debt_to_equity(borrowings or 0, equity, reserves), sector)), interest_coverage(op_profit, other_income, interest), interest_coverage_label(interest_coverage(op_profit, other_income, interest)), int(interest_warning(interest_coverage(op_profit, other_income, interest))), net_debt(borrowings, investments), asset_turnover(sales, assets), fcf, cfo_ratio, cfo_label, capex_pct, capex_label, fcf_conversion(fcf, op_profit), eps, (equity or 0) + (reserves or 0), dividend, borrowings, cfo, *cagr_values, score))
        reference_roce, reference_roe = company_reference.get(company_id, (None, None))
        if roce is not None and reference_roce is not None and abs(roce - reference_roce) > 5:
            edge_cases.append(f"{company_id},{year}: ROCE differs from source by >5%; category=version difference; computed={roce}; source={reference_roce}")
        if roe is not None and reference_roe is not None and abs(roe - reference_roe) > 5:
            edge_cases.append(f"{company_id},{year}: ROE differs from source by >5%; category=data source issue; computed={roe}; source={reference_roe}")
    placeholders = ",".join("?" for _ in RATIO_COLUMNS)
    db.executemany(f"INSERT INTO financial_ratios VALUES ({placeholders})", output_rows)
    db.commit()
    (ROOT / "output").mkdir(exist_ok=True)
    with (ROOT / "output" / "ratio_edge_cases.log").open("w", encoding="utf-8") as log:
        log.write("\n".join(edge_cases) if edge_cases else "No ratio edge cases detected.")
    capital_rows = []
    for company_id, year, cfo, cfi, cff, net_profit in db.execute("SELECT c.company_id,c.year,c.operating_activity,c.investing_activity,c.financing_activity,p.net_profit FROM cashflow c LEFT JOIN profitandloss p USING(company_id,year)"):
        ratio = None if cfo is None or not net_profit else cfo / net_profit
        capital_rows.append((company_id, year, "+" if (cfo or 0) >= 0 else "-", "+" if (cfi or 0) >= 0 else "-", "+" if (cff or 0) >= 0 else "-", capital_allocation_pattern(cfo, cfi, cff, ratio)))
    with (ROOT / "output" / "capital_allocation.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"])
        writer.writerows(capital_rows)
    db.close()
    return len(output_rows)


if __name__ == "__main__":
    print(f"financial_ratios rows: {populate_ratios()}")
