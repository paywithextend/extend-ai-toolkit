PYTHON ?= python
FOCUSED_TESTS = extend_ai_toolkit/tests/test_security.py extend_ai_toolkit/tests/test_adapter_security.py extend_ai_toolkit/tests/test_core.py extend_ai_toolkit/tests/test_configuration.py extend_ai_toolkit/tests/test_validate_tool_spec.py extend_ai_toolkit/tests/test_packaging.py extend_ai_toolkit/tests/test_contracts.py extend_ai_toolkit/tests/test_client_workflows.py extend_ai_toolkit/tests/test_review_regressions.py extend_ai_toolkit/tests/test_release_files.py

lint:
	$(PYTHON) -m ruff check extend_ai_toolkit tools --exclude 'extend_ai_toolkit/tests/test_*'
	$(PYTHON) -m ruff check $(FOCUSED_TESTS)

test:
	$(PYTHON) -m pytest -q $(FOCUSED_TESTS)

build:
	$(PYTHON) -m build

docs:
	$(PYTHON) tools/generate_capabilities.py
