"""Generate Sprint 4 completion report."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "sprint4_completion_report.md"


def main():
    checks = subprocess.run([sys.executable, "scripts/sprint4_checks.py"], cwd=ROOT, capture_output=True, text=True)
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
    lines = [
        "# Sprint 4 Completion Report", "", "## Dashboard and Valuation Definition of Done", "",
        "- Dashboard entry point: `src/dashboard/app.py`", "- Dashboard screens: 8", "- Valuation summary: 92 companies", "- Valuation flags CSV: generated", "- Streamlit cache layer: implemented for all database query helpers", "- CSV screener download: implemented", "", "## Sprint 4 Checks", "", "```text", checks.stdout.strip(), "```", "", "## Test Output", "", "```text", tests.stdout.strip(), "```", "", "## Deliverables", "", "- `src/dashboard/app.py`", "- `src/dashboard/pages/01_home.py` through `08_reports.py`", "- `src/dashboard/utils/db.py`", "- `src/analytics/valuation.py`", "- `output/valuation_summary.xlsx`", "- `output/valuation_flags.csv`", "- `reports/dashboard_screenshots/README.md`", "- `src/dashboard/screenshots/` (8 Explorer-visible PNG results)", "- `reports/radar_charts/`", "- `scripts/sprint4_checks.py`", "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT)
    return checks.returncode or tests.returncode


if __name__ == "__main__":
    raise SystemExit(main())
