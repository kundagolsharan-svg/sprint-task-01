"""Check the executable Sprint 1 Definition of Done criteria."""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    database = ROOT / "nifty100.db"
    failures = list(csv.DictReader((ROOT / "output" / "validation_failures.csv").open(encoding="utf-8")))
    with sqlite3.connect(database) as connection:
        checks = {
            "companies": connection.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 92,
            "foreign_key_check": connection.execute("PRAGMA foreign_key_check").fetchall() == [],
            "critical_dq": not any(row["severity"] == "CRITICAL" for row in failures),
            "stock_prices": connection.execute("SELECT COUNT(*) FROM stock_prices").fetchone()[0] == 5520,
        }
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())