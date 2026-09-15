"""Generate Sprint 5 capital-allocation summaries and pattern changes."""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    allocation = pd.read_csv(ROOT / "output" / "capital_allocation.csv")
    allocation = allocation.sort_values(["company_id", "year"])
    latest = allocation.groupby("company_id").tail(1)
    latest["pattern_label"].value_counts().rename_axis("pattern_label").reset_index(name="company_count").to_csv(ROOT / "output" / "capital_allocation_distribution.csv", index=False)
    allocation["previous_pattern"] = allocation.groupby("company_id").pattern_label.shift(1)
    changes = allocation[(allocation.previous_pattern.notna()) & (allocation.previous_pattern != allocation.pattern_label)][["company_id", "year", "previous_pattern", "pattern_label"]]
    changes.to_csv(ROOT / "output" / "pattern_changes.csv", index=False)
    return len(changes)


if __name__ == "__main__": print(f"pattern_changes={main()}")
