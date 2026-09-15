"""Verify Sprint 2 ratio-engine exit criteria."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sqlite3.connect(ROOT / "nifty100.db") as db:
        count = db.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
        columns = [row[1] for row in db.execute("PRAGMA table_info(financial_ratios)")]
        null_only = [column for column in columns if column not in {"company_id", "year"} and db.execute(f"SELECT COUNT(*) FROM financial_ratios WHERE [{column}] IS NOT NULL").fetchone()[0] == 0]
        screener = db.execute("""
            SELECT COUNT(*) FROM financial_ratios r
            WHERE r.year = (
                SELECT MAX(r2.year) FROM financial_ratios r2
                WHERE r2.company_id = r.company_id AND r2.year <> 'TTM'
            ) AND r.return_on_equity_pct > 15 AND r.debt_to_equity < 1
        """).fetchone()[0]
    checks = {"ratio_rows": count >= 1100, "required_kpis": len(columns) >= 14, "zero_null_only_columns": not null_only, "edge_log": (ROOT / "output" / "ratio_edge_cases.log").exists(), "capital_allocation": (ROOT / "output" / "capital_allocation.csv").exists(), "screener_15_to_50": 15 <= screener <= 50}
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    if null_only:
        print("null_only=", ",".join(null_only))
    print("screener_companies=", screener)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
