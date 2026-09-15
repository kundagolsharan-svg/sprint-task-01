load:
	python -m src.etl.loader
validate:
	python -m src.etl.validator
test:
	python -m pytest
report: load validate
	python scripts/generate_completion_report.py
ratios: load
	python -m src.analytics.engine
sprint2: load ratios
	python scripts/sprint2_checks.py
sprint3: load ratios
	python -m src.screener.engine
	python -m src.analytics.peer
	python scripts/sprint3_checks.py
report3:
	python scripts/generate_sprint3_report.py
sprint4: load ratios
	python -m src.analytics.valuation
	python -m src.screener.engine
	python -m src.analytics.peer
	python scripts/sprint4_checks.py
report4:
	python scripts/generate_sprint4_report.py
sprint5: load ratios
	python -m src.nlp.parser
	python -m src.nlp.pros_cons_generator
	python -m src.analytics.cashflow_intelligence
	python scripts/sprint5_outputs.py
	python -m src.reports.tearsheet
	python -m src.reports.sector_report
	python -m src.reports.portfolio
	python scripts/sprint5_checks.py
report5:
	python scripts/generate_sprint5_report.py
dashboard: report
api: report
clean:
	python -c "from pathlib import Path; [p.unlink() for p in [Path('nifty100.db'), Path('output/load_audit.csv'), Path('output/validation_failures.csv')] if p.exists()]"