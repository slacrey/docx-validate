VENV_PYTHON := .venv/bin/python

.PHONY: venv install test run clean

venv: $(VENV_PYTHON)

$(VENV_PYTHON):
	python3 -m venv .venv

install: venv
	$(VENV_PYTHON) -m pip install -e '.[dev]'

test: install
	PYTHONPATH=src $(VENV_PYTHON) -m pytest -q

run:
	bash scripts/dev.sh

clean:
	rm -rf .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
