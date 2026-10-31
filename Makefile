PYTHON ?= python
lint:
	$(PYTHON) -m ruff check extend_ai_toolkit tools --exclude 'extend_ai_toolkit/tests/test_*'
	$(PYTHON) -m ruff check extend_ai_toolkit/tests/test_security.py extend_ai_toolkit/tests/test_adapter_security.py extend_ai_toolkit/tests/test_core.py extend_ai_toolkit/tests/test_configuration.py extend_ai_toolkit/tests/test_validate_tool_spec.py extend_ai_toolkit/tests/test_packaging.py

test:
	$(PYTHON) -m pytest -q extend_ai_toolkit/tests/test_security.py extend_ai_toolkit/tests/test_adapter_security.py extend_ai_toolkit/tests/test_core.py extend_ai_toolkit/tests/test_configuration.py extend_ai_toolkit/tests/test_validate_tool_spec.py extend_ai_toolkit/tests/test_packaging.py

build:
	$(PYTHON) -m build
