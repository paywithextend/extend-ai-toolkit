"""Cross-package regressions using the real SDK and MCP protocol models."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from extend import ExtendClient
from extend.auth import BasicAuth
from pydantic import ValidationError

from extend_ai_toolkit import execute_tool
from extend_ai_toolkit.shared.functions import get_transactions


@pytest.mark.parametrize("entrypoint", ["tool", "function"])
async def test_default_transactions_use_first_sdk_page(entrypoint):
    requests = []
    response = {"report": {"transactions": [], "page": 1, "perPage": 50, "count": 0}}

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json=response)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        async with ExtendClient(
            BasicAuth("synthetic", "synthetic-secret"), environment="stage", http_client=transport
        ) as sdk:
            result = (await execute_tool(sdk, "get_transactions", {})
                      if entrypoint == "tool" else await get_transactions(sdk))
    assert result["report"] == response["report"]
    assert len(requests) == 1
    assert requests[0].url.path == "/reports/transactions/v2"
    assert requests[0].url.params["page"] == "1"


@pytest.mark.parametrize("page", [0, -1])
async def test_invalid_transaction_page_rejected_before_sdk(page):
    sdk = SimpleNamespace(transactions=SimpleNamespace(get_transactions=AsyncMock()))
    with pytest.raises(ValidationError):
        await execute_tool(sdk, "get_transactions", {"page": page})
    sdk.transactions.get_transactions.assert_not_called()


async def test_terminal_lists_and_queries_real_mcp_models():
    types = pytest.importorskip("mcp.types")
    from extend_ai_toolkit.modelcontextprotocol.client.mcp_client import MCPClient

    schema = {"type": "object", "properties": {"page": {"type": "integer", "minimum": 1}}}
    result = types.ListToolsResult(tools=[types.Tool(
        name="get_transactions", description="List transactions", input_schema=schema
    )])
    from extend_ai_toolkit.modelcontextprotocol.client.chat_client import AssistantTurn

    provider = SimpleNamespace(complete=AsyncMock(return_value=AssistantTurn(
        {"role": "assistant", "content": "Ready"}, text="Ready"
    )))
    client = MCPClient(provider)
    client.session = SimpleNamespace(list_tools=AsyncMock(return_value=result))
    assert await client.list_available_tools() == [{
        "name": "get_transactions", "description": "List transactions", "parameters": schema
    }]
    assert await client.process_query("List transactions") == "Ready"
    provider.complete.assert_awaited_once()
    assert provider.complete.await_args.args[1] == [{
        "name": "get_transactions", "description": "List transactions", "parameters": schema
    }]
