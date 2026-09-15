"""Initial critical and warning data-quality checks."""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate(db_path: Path = ROOT / "nifty100.db") -> list[dict[str, str]]:
    db = sqlite3.connect(db_path)
    checks = [
        ("DQ-01", "CRITICAL", "companies", "company_id IS NULL"),
        ("DQ-02", "CRITICAL", "profitandloss", "company_id IS NULL OR year IS NULL"),
        ("DQ-04", "WARNING", "balancesheet", "total_assets != 0 AND ABS(total_assets-total_liabilities)/ABS(total_assets) >= 0.01"),
        ("DQ-05", "WARNING", "profitandloss", "sales > 0 AND ABS(operating_profit/sales*100-opm_percentage) > 1"),
        ("DQ-06", "WARNING", "profitandloss", "sales IS NOT NULL AND sales <= 0"),
        ("DQ-07", "WARNING", "cashflow", "net_cash_flow IS NOT NULL AND net_cash_flow != operating_activity + investing_activity + financing_activity"),
        ("DQ-08", "WARNING", "profitandloss", "tax_percentage < 0 OR tax_percentage > 100"),
        ("DQ-09", "WARNING", "profitandloss", "dividend_payout < 0 OR dividend_payout > 100"),
        ("DQ-10", "WARNING", "documents", "annual_report IS NOT NULL AND annual_report NOT LIKE 'http%'"),
        ("DQ-11", "WARNING", "profitandloss", "eps IS NOT NULL AND sales > 0 AND eps < 0 AND net_profit > 0"),
        ("DQ-12", "WARNING", "balancesheet", "total_assets IS NOT NULL AND total_liabilities IS NOT NULL AND total_assets < 0"),
        ("DQ-13", "WARNING", "profitandloss", "year IS NULL OR year = ''"),
        ("DQ-14", "WARNING", "stock_prices", "date IS NULL OR date = ''"),
        ("DQ-15", "WARNING", "stock_prices", "close_price IS NOT NULL AND close_price <= 0"),
        ("DQ-16", "WARNING", "companies", "company_name IS NULL OR TRIM(company_name) = ''"),
    ]
    failures = []
    for rule, severity, table, condition in checks:
        period = "year" if table not in {"companies", "stock_prices"} else ("date" if table == "stock_prices" else "NULL")
        for company_id, period_value in db.execute(f"SELECT company_id, {period} FROM {table} WHERE {condition}"):
            failures.append({"rule": rule, "severity": severity, "table": table, "company_id": str(company_id), "year": str(period_value or ""), "message": condition})
    for table in ("profitandloss", "balancesheet", "cashflow", "analysis", "documents", "prosandcons", "sectors", "stock_prices", "financial_ratios", "market_cap", "peer_groups"):
        for company_id, period_value in db.execute(f"SELECT company_id, NULL FROM {table} WHERE company_id NOT IN (SELECT company_id FROM companies)"):
            failures.append({"rule": "DQ-03", "severity": "CRITICAL", "table": table, "company_id": str(company_id), "year": "", "message": "company_id NOT IN companies"})
    db.close()
    with (ROOT / "output" / "validation_failures.csv").open("w", newline="", encoding="utf-8") as report:
        writer = csv.DictWriter(report, fieldnames=["rule", "severity", "table", "company_id", "year", "message"])
        writer.writeheader(); writer.writerows(failures)
    return failures


if __name__ == "__main__":
    print(f"validation failures: {len(validate())}")