.PHONY: setup data demo test eval app clean

BATCH ?= dev

# fixed seeds: `make data` is idempotent, and manifest.json records the seed
DEV_SEED     ?= 42
STRESS_SEED  ?= 7
HOLDOUT_SEED ?= 1337

PY := uv run python

setup:
	uv sync

data:
	$(PY) -m ledgerloop.generate --invoices 500 --seed $(DEV_SEED)     --out data/batch_dev
	$(PY) -m ledgerloop.generate --invoices 500 --seed $(STRESS_SEED)  --out data/batch_stress --profile stress
	$(PY) -m ledgerloop.generate --invoices 500 --seed $(HOLDOUT_SEED) --out data/batch_holdout

demo:
	$(PY) -m ledgerloop.run --batch dev --no-llm --no-report

test:
	uv run pytest -q

# make eval BATCH=dev LABEL=r1_baseline
eval:
	$(PY) -m ledgerloop.run --batch $(BATCH) --no-llm $(if $(LABEL),--label $(LABEL),)

app:
	uv run streamlit run app.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
