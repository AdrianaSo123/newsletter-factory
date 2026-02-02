.PHONY: help setup test test-fast

VENV := .venv
PY := $(VENV)/bin/python

help:
	@echo "Targets:"
	@echo "  make setup     - create venv + install deps"
	@echo "  make test      - run full pytest suite"
	@echo "  make test-fast - run pytest (quiet)"

setup:
	./scripts/setup_venv.sh

test:
	$(PY) -m pytest

test-fast:
	$(PY) -m pytest -q
