.PHONY: setup data demo demo-llm test eval eval-llm holdout audit app clean

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

# make eval BATCH=dev LABEL=r1_baseline -- rules only, no key needed, seconds
eval:
	$(PY) -m ledgerloop.run --batch $(BATCH) --no-llm $(if $(LABEL),--label $(LABEL),)

# The full four-stage number. Needs a key in .env; first run costs real tokens,
# reruns are served from .cache/llm and cost nothing.
eval-llm:
	$(PY) -m ledgerloop.run --batch $(BATCH) $(if $(LABEL),--label $(LABEL),)

demo-llm:
	$(PY) -m ledgerloop.run --batch dev --no-report

# The one-shot. batch_holdout is never read during development; this is the
# only command that touches it, and it needs the flag to say so out loud.
holdout:
	$(PY) -m ledgerloop.run --batch holdout --allow-holdout --label final

# Inspect the append-only trail: what was decided, and what was reconsidered.
audit:
	@$(PY) -c "from ledgerloop.audit import AuditLog; \
	log = AuditLog('audit.db'); \
	runs = log.runs(); \
	print('runs:'); \
	[print(f\"  {r['run_id']:<28} {r['batch']:<8} {r['n_txns']:>4} txns\") for r in runs[:8]]; \
	rid = runs[0]['run_id'] if runs else None; \
	print(); print('latest:', log.summary(rid)) if rid else None"

app:
	uv run streamlit run app.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
