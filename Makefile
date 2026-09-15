load:
	python -m src.etl.loader
validate:
	python -m src.etl.validator
test:
	python -m pytest
report: load validate
	python scripts/generate_completion_report.py
ratios: load
dashboard: report
api: report
clean:
	python -c "from pathlib import Path; [p.unlink() for p in [Path('nifty100.db'), Path('output/load_audit.csv'), Path('output/validation_failures.csv')] if p.exists()]"