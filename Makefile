PYTHON ?= python
lint:
	$(PYTHON) -m ruff check extend_ai_toolkit tools --exclude 'extend_ai_toolkit/tests/test_*'
	$(PYTHON) -m ruff check extend_ai_toolkit/tests/test_security.py extend_ai_toolkit/tests/test_adapter_security.py

test:
	$(PYTHON) -m pytest -q extend_ai_toolkit/tests/test_security.py extend_ai_toolkit/tests/test_adapter_security.py

build:
	$(PYTHON) -m build
