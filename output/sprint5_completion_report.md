# Sprint 5 Completion Report

## Intelligence, NLP, and PDF Reports

- Pros/cons generated for all 92 companies
- Analysis parser output generated
- Cash-flow intelligence rows: **92**
- Company tearsheets: **92**
- Sector reports: **11**
- Portfolio summary PDF: generated
- Distress alerts: generated
- Capital-allocation distribution and pattern changes: generated

## Sprint 5 Checks

```text
pros_for_all_companies: PASS
cons_for_all_companies: PASS
intelligence_rows_92: PASS
tearsheets_92: PASS
tearsheets_30kb: PASS
sector_reports_11: PASS
portfolio_pdf: PASS
distress_alerts: PASS
parsed_analysis: PASS
pattern_changes: PASS
tearsheets= 92 sector_reports= 11
```

## Regression Tests

```text
........................................................................ [ 90%]
........                                                                 [100%]
```

## Deliverables

- `output/pros_cons_generated.csv`
- `output/analysis_parsed.csv`
- `output/cashflow_intelligence.xlsx`
- `output/distress_alerts.csv`
- `output/capital_allocation_distribution.csv`
- `output/pattern_changes.csv`
- `reports/tearsheets/`
- `reports/sector/`
- `reports/portfolio/portfolio_summary.pdf`
- `src/nlp/parser.py`
- `src/nlp/pros_cons_generator.py`
- `src/analytics/cashflow_intelligence.py`
- `src/reports/tearsheet.py`
- `src/reports/sector_report.py`
