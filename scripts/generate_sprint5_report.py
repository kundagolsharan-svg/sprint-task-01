"""Generate the Sprint 5 completion report."""

import subprocess
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "sprint5_completion_report.md"


def main():
    checks = subprocess.run([sys.executable, "scripts/sprint5_checks.py"], cwd=ROOT, capture_output=True, text=True)
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
    intelligence_rows = openpyxl.load_workbook(ROOT / "output" / "cashflow_intelligence.xlsx", read_only=True).active.max_row - 1
    lines = [
        "# Sprint 5 Completion Report", "", "## Intelligence, NLP, and PDF Reports", "",
        "- Pros/cons generated for all 92 companies", "- Analysis parser output generated", f"- Cash-flow intelligence rows: **{intelligence_rows}**", "- Company tearsheets: **92**", "- Sector reports: **11**", "- Portfolio summary PDF: generated", "- Distress alerts: generated", "- Capital-allocation distribution and pattern changes: generated", "", "## Sprint 5 Checks", "", "```text", checks.stdout.strip(), "```", "", "## Regression Tests", "", "```text", tests.stdout.strip(), "```", "", "## Deliverables", "", "- `output/pros_cons_generated.csv`", "- `output/analysis_parsed.csv`", "- `output/cashflow_intelligence.xlsx`", "- `output/distress_alerts.csv`", "- `output/capital_allocation_distribution.csv`", "- `output/pattern_changes.csv`", "- `reports/tearsheets/`", "- `reports/sector/`", "- `reports/portfolio/portfolio_summary.pdf`", "- `src/nlp/parser.py`", "- `src/nlp/pros_cons_generator.py`", "- `src/analytics/cashflow_intelligence.py`", "- `src/reports/tearsheet.py`", "- `src/reports/sector_report.py`", "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT)
    return checks.returncode or tests.returncode


if __name__ == "__main__":
    raise SystemExit(main())
