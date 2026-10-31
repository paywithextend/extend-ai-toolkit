"""Real optional-adapter registration; no constructor mocks or external API calls."""

import importlib.metadata
import importlib.util
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extend_ai_toolkit import ExecutionPolicy
from extend_ai_toolkit.policy import ToolPermissionError
from extend_ai_toolkit.shared import Configuration, ExtendAPI

ADAPTERS = [
    ("langchain_core", "extend_ai_toolkit.langchain", "ExtendLangChainToolkit"),
    ("agents", "extend_ai_toolkit.openai", "ExtendOpenAIToolkit"),
    ("crewai", "extend_ai_toolkit.crewai", "ExtendCrewAIToolkit"),
]


@pytest.mark.parametrize("dependency,module,class_name", ADAPTERS)
async def test_real_adapter_registration_and_invocation(dependency, module, class_name):
    if importlib.util.find_spec(dependency) is None:
        pytest.skip(f"{dependency} extra is not installed")
    if dependency == "agents" and importlib.metadata.version("openai").split(".")[0] != "3":
        pytest.skip("OpenAI Agents extra is tested separately from CrewAI")
    cls = getattr(importlib.import_module(module), class_name)
    client = SimpleNamespace(
        virtual_cards=SimpleNamespace(close_virtual_card=AsyncMock(return_value={})),
        aclose=AsyncMock(),
    )
    api = ExtendAPI(client, policy=ExecutionPolicy.from_configuration(Configuration.all_tools()))
    toolkit = cls(api)
    assert len(toolkit.get_tools()) == 26
    assert len(cls(ExtendAPI(client)).get_tools()) == 16
    close = next(t for t in toolkit.get_tools() if t.name == "close_virtual_card")
    with pytest.raises(ToolPermissionError):
        if dependency == "agents":
            await close.on_invoke_tool(None, json.dumps({"virtual_card_id": "v"}))
        else:
            await close._arun(virtual_card_id="v")
    client.virtual_cards.close_virtual_card.assert_not_called()
    await toolkit.aclose()


async def test_mcp_real_catalog_strictness_and_transport():
    pytest.importorskip("mcp")
    if importlib.metadata.version("mcp").split(".")[0] != "2":
        pytest.skip("CrewAI owns MCP 1.x internally; the toolkit MCP extra is tested separately")
    from extend_ai_toolkit.modelcontextprotocol.server import ExtendMCPServer
    from extend_ai_toolkit.shared.tools import tools

    client = SimpleNamespace(aclose=AsyncMock())
    server = ExtendMCPServer(
        ExtendAPI(client, policy=ExecutionPolicy.from_configuration(Configuration.all_tools()))
    )
    listed = await server.list_tools()
    assert {tool.name for tool in listed} == {tool.name for tool in tools}
    for advertised in listed:
        source = next(t for t in tools if t.name == advertised.name)
        assert advertised.input_schema == source.args_schema.model_json_schema()
    assert (await server.call_tool("get_transactions", {"receipt_missing": "false"})).is_error
    assert (await server.call_tool("send_receipt_reminder", {"transaction_id": "t"})).is_error
    with pytest.raises(ValueError):
        server.run(transport="sse")
    with pytest.raises(ValueError):
        server.streamable_http_app()


async def test_stdio_initialization_and_list():
    pytest.importorskip("mcp")
    if importlib.metadata.version("mcp").split(".")[0] != "2":
        pytest.skip("CrewAI owns MCP 1.x internally; the toolkit MCP extra is tested separately")
    import os
    import sys

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "extend_ai_toolkit.modelcontextprotocol.main", "--environment=stage"],
        env={**os.environ, "EXTEND_API_KEY": "synthetic", "EXTEND_API_SECRET": "synthetic"},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            assert len(listed.tools) == 16
            result = await session.call_tool("close_virtual_card", {"virtual_card_id": "v"})
            assert result.is_error

@pytest.mark.parametrize("provider,module", [("openai", "openai_chat_client"), ("anthropic", "anthropic_chat_client")])
def test_terminal_provider_imports_without_the_other_provider(provider, module):
    if importlib.util.find_spec(provider) is None or importlib.util.find_spec("mcp") is None:
        pytest.skip("Selected terminal extra is not installed")
    if importlib.metadata.version("mcp").split(".")[0] != "2":
        pytest.skip("CrewAI internal MCP is not the terminal extra")
    importlib.import_module("extend_ai_toolkit.modelcontextprotocol.client.mcp_client")
    importlib.import_module("extend_ai_toolkit.modelcontextprotocol.client." + module)
