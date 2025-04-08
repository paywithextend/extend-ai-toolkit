VENV_NAME ?= venv
PIP ?= pip
PYTHON ?= python3.12
ENV ?= stage

venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: pyproject.toml
	@test -d $(VENV_NAME) || $(PYTHON) -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/python -m pip install -e ".[dev]"
	@touch $(VENV_NAME)/bin/activate

test: venv
	$(VENV_NAME)/bin/pytest tests

build: venv
	cp LICENSE LICENSE.bak
	$(VENV_NAME)/bin/python -m build
	rm LICENSE.bak
