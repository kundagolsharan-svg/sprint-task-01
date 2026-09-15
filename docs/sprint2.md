# Sprint 2 Ratio Engine

Run the complete Sprint 2 workflow with:

```powershell
python -m src.etl.loader
python -m src.analytics.engine
python scripts/sprint2_checks.py
python -m pytest -q
```

The engine computes profitability, leverage, efficiency, CAGR, cash-flow, and capital-allocation KPIs for every canonical P&L period. It writes `output/capital_allocation.csv` and `output/ratio_edge_cases.log`, and replaces the source-shaped `financial_ratios` table with the computed 44-column KPI table.

The screener check uses the latest non-TTM annual row per company, avoiding duplicate historical matches.