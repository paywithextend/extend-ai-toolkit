from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extend_ai_toolkit import ExecutionPolicy, execute_tool, list_tool_specs
from extend_ai_toolkit.shared import Configuration


def test_stable_metadata_and_empty_catalog():
    policy = ExecutionPolicy.from_configuration(Configuration.all_tools())
    specs = {tool.name: tool for tool in list_tool_specs(policy=policy)}
    assert specs["get_transactions"].ref == "extend.transactions.get_transactions.v1"
    assert specs["get_transactions"].actions == ("read",)
    assert specs["update_transaction_expense_data"].actions == ("read", "update")
    assert list_tool_specs(catalog=[]) == []

async def test_raw_result_and_unknown_catalog():
    response = {"virtualCards": [{"id": "v", "currency": "CAD"}]}
    client = SimpleNamespace(virtual_cards=SimpleNamespace(get_virtual_cards=AsyncMock(return_value=response)))
    assert await execute_tool(client, "get_virtual_cards") == response
    for name, catalog in [("missing", None), ("get_virtual_cards", [])]:
        with pytest.raises(ValueError):
            await execute_tool(client, name, catalog=catalog)
