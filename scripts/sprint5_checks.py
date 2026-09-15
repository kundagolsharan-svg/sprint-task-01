"""Verify Sprint 5 NLP, cash-flow, and PDF report exit criteria."""

import csv
import glob
import sqlite3
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]


def main():
    pros = list(csv.DictReader((ROOT / "output" / "pros_cons_generated.csv").open(encoding="utf-8")))
    companies = {row[0] for row in sqlite3.connect(ROOT / "nifty100.db").execute("SELECT company_id FROM companies")}
    pros_ids = {row["company_id"] for row in pros if row["type"] == "pro"}
    cons_ids = {row["company_id"] for row in pros if row["type"] == "con"}
    intelligence = openpyxl.load_workbook(ROOT / "output" / "cashflow_intelligence.xlsx", read_only=True)
    tearsheets = glob.glob(str(ROOT / "reports" / "tearsheets" / "*_tearsheet.pdf"))
    sectors = glob.glob(str(ROOT / "reports" / "sector" / "*_report.pdf"))
    checks = {
        "pros_for_all_companies": companies <= pros_ids,
        "cons_for_all_companies": companies <= cons_ids,
        "intelligence_rows_92": intelligence.active.max_row - 1 == 92,
        "tearsheets_92": len(tearsheets) == 92,
        "tearsheets_30kb": all(Path(path).stat().st_size >= 30_000 for path in tearsheets),
        "sector_reports_11": len(sectors) == 11,
        "portfolio_pdf": (ROOT / "reports" / "portfolio" / "portfolio_summary.pdf").exists(),
        "distress_alerts": (ROOT / "output" / "distress_alerts.csv").exists(),
        "parsed_analysis": (ROOT / "output" / "analysis_parsed.csv").exists(),
        "pattern_changes": (ROOT / "output" / "pattern_changes.csv").exists(),
    }
    for name, passed in checks.items(): print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print("tearsheets=", len(tearsheets), "sector_reports=", len(sectors))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__": raise SystemExit(main())
