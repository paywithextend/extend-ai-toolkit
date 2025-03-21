VENV_NAME ?= venv
PIP ?= pip
PYTHON ?= python3.11
ENV ?= stage

venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: requirements.txt
	@test -d $(VENV_NAME) || $(PYTHON) -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/python -m pip install -r requirements.txt
	@touch $(VENV_NAME)/bin/activate

test: venv
	$(VENV_NAME)/bin/python -m unittest discover tests

build: set-config venv
	cp LICENSE LICENSE.bak
	$(VENV_NAME)/bin/python -m build
	rm LICENSE.bak

set-config:
ifeq ($(ENV), stage)
	@cp extend_ai_toolkit/config/config_stage.py extend_ai_toolkit/config/config.py
	@echo "Using STAGING configuration"
else ifeq ($(ENV), prod)
	@cp extend_ai_toolkit/config/config_prod.py extend_ai_toolkit/config/config.py
	@echo "Using PRODUCTION configuration"
else
	@echo "Invalid ENV value. Use 'stage' or 'prod'."
	@exit 1
endif