"""Parse analysis text fields into structured percentage observations."""

import csv
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%", re.IGNORECASE)
FIELDS = ("compounded_sales_growth", "compounded_profit_growth", "stock_price_cagr", "roe")


def parse_analysis(db_path: Path = ROOT / "nifty100.db") -> int:
    with sqlite3.connect(db_path) as db:
        rows = db.execute("SELECT company_id, compounded_sales_growth, compounded_profit_growth, stock_price_cagr, roe FROM analysis").fetchall()
    parsed, failures = [], []
    for row in rows:
        company_id = row[0]
        for metric, text in zip(FIELDS, row[1:]):
            match = PATTERN.search(str(text or ""))
            if match:
                parsed.append((company_id, metric, int(match.group(1)), float(match.group(2))))
            else:
                failures.append((company_id, metric, text or "", "pattern did not match"))
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    with (output / "analysis_parsed.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file); writer.writerow(["company_id", "metric_type", "period_years", "value_pct"]); writer.writerows(parsed)
    with (output / "parse_failures.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file); writer.writerow(["company_id", "metric_type", "raw_text", "reason"]); writer.writerows(failures)
    return len(parsed)


if __name__ == "__main__":
    print(f"parsed_rows={parse_analysis()}")
