"""Provider-native conversation fixtures with no paid model or live financial calls."""

import asyncio
import copy
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extend_ai_toolkit.modelcontextprotocol.client.chat_client import AssistantTurn, ToolCall
from extend_ai_toolkit.modelcontextprotocol.client.mcp_client import MCPClient


class Block(SimpleNamespace):
    def model_dump(self, **kwargs):
        return {key: value for key, value in vars(self).items() if value is not None}


class Session:
    def __init__(self):
        self.calls = []
        self.active_reads = 0
        self.parallel_reads = 0

    async def list_tools(self):
        return SimpleNamespace(
            tools=[
                SimpleNamespace(name=name, description=name, input_schema={"type": "object"})
                for name in [
                    "get_organizations",
                    "get_user_details",
                    "create_receipt_attachment",
                    "automatch_receipts",
                    "get_automatch_status",
                    "close_virtual_card",
                ]
            ]
        )

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if name.startswith("get_"):
            self.active_reads += 1
            self.parallel_reads = max(self.parallel_reads, self.active_reads)
            await asyncio.sleep(0.01)
            self.active_reads -= 1
        value = {"id": "ra"} if name == "create_receipt_attachment" else {"id": "job"}
        if name == "get_automatch_status":
            value["tasks"] = [{"status": "SUCCESS"}]
        return SimpleNamespace(structured_content=value, content=[], is_error=False)


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
async def test_native_multi_tool_receipt_conversation_and_retained_state(provider):
    requests = []
    rounds = [
        [("read1", "get_organizations", {}), ("read2", "get_user_details", {"user_id": "u"})],
        [("upload", "create_receipt_attachment", {"file_path": "safe.pdf"})],
        [("match", "automatch_receipts", {"receipt_attachment_ids": ["ra"]})],
        [("poll", "get_automatch_status", {"job_id": "job"})],
        [],
        [],
    ]

    async def create(**kwargs):
        requests.append(copy.deepcopy(kwargs))
        calls = rounds.pop(0)
        if provider == "openai":
            tool_calls = [
                SimpleNamespace(
                    id=id, function=SimpleNamespace(name=name, arguments=json.dumps(args))
                )
                for id, name, args in calls
            ]
            message = SimpleNamespace(content=None if calls else "done", tool_calls=tool_calls)
            message.model_dump = lambda **opts: {
                "role": "assistant",
                "content": message.content,
                **(
                    {
                        "tool_calls": [
                            {
                                "id": id,
                                "type": "function",
                                "function": {"name": name, "arguments": json.dumps(args)},
                            }
                            for id, name, args in calls
                        ]
                    }
                    if calls
                    else {}
                ),
            }
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])
        blocks = [
            Block(type="tool_use", id=id, name=name, input=args) for id, name, args in calls
        ] or [Block(type="text", text="done")]
        return SimpleNamespace(content=blocks)

    if provider == "openai":
        from extend_ai_toolkit.modelcontextprotocol.client.openai_chat_client import (
            OpenAIChatClient,
        )

        llm = OpenAIChatClient(
            client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        )
    else:
        from extend_ai_toolkit.modelcontextprotocol.client.anthropic_chat_client import (
            AnthropicChatClient,
        )

        llm = AnthropicChatClient(client=SimpleNamespace(messages=SimpleNamespace(create=create)))
    client = MCPClient(llm)
    client.session = Session()
    assert await client.process_query("Match my synthetic receipt") == "done"
    assert client.session.parallel_reads == 2
    assert [name for name, args in client.session.calls] == [
        "get_organizations",
        "get_user_details",
        "create_receipt_attachment",
        "automatch_receipts",
        "get_automatch_status",
    ]
    assert await client.process_query("What happened?") == "done"
    assert requests[-1]["messages"][0]["content"] == "Match my synthetic receipt"
    if provider == "openai":
        messages = requests[1]["messages"]
        assert [m["tool_call_id"] for m in messages if m["role"] == "tool"] == ["read1", "read2"]
        assert requests[0]["store"] is False
        assert all("tools" in request for request in requests)
    else:
        results = requests[1]["messages"][-1]["content"]
        assert [block["tool_use_id"] for block in results] == ["read1", "read2"]
        assert all(block["type"] == "tool_result" for block in results)
        assert requests[1]["messages"][-2]["content"][0]["id"] == "read1"


class FakeProvider:
    def __init__(self, turns):
        self.turns = iter(turns)

    async def complete(self, *args):
        return next(self.turns)

    def result_messages(self, results):
        return [
            {"role": "tool", "tool_call_id": call.id, "content": content}
            for call, content, failed in results
        ]

    async def aclose(self):
        pass


def turn(id="a", name="close_virtual_card", arguments=None):
    return AssistantTurn(
        {"role": "assistant", "content": "call"},
        (ToolCall(id, name, arguments if arguments is not None else {"virtual_card_id": "vc"}),),
    )


async def test_uncertain_write_is_not_replayed_even_with_a_new_call_id():
    client = MCPClient(
        FakeProvider(
            [
                turn("a"),
                turn("b"),
                AssistantTurn({"role": "assistant", "content": "done"}, text="done"),
            ]
        )
    )
    session = Session()
    session.call_tool = AsyncMock(side_effect=TimeoutError())
    client.session = session
    assert await client.process_query("Close card") == "done"
    assert session.call_tool.await_count == 1
    assert "write_already_attempted" in client.messages[-2]["content"]


async def test_round_and_call_limits():
    client = MCPClient(FakeProvider([turn("a", "get_organizations", {})]), max_rounds=1)
    client.session = Session()
    with pytest.raises(RuntimeError, match="round limit"):
        await client.process_query("Read")
    assert len(client.session.calls) == 1
    calls = (
        ToolCall("a", "close_virtual_card", {"virtual_card_id": "v"}),
        ToolCall("b", "close_virtual_card", {"virtual_card_id": "w"}),
    )
    client = MCPClient(FakeProvider([AssistantTurn({"role": "assistant"}, calls)]), max_calls=1)
    client.session = Session()
    with pytest.raises(RuntimeError, match="call limit"):
        await client.process_query("Close")
    assert client.session.calls == []


async def test_duplicate_call_ids_reject_entire_round():
    call = ToolCall("duplicate", "close_virtual_card", {"virtual_card_id": "v"})
    client = MCPClient(FakeProvider([AssistantTurn({"role": "assistant"}, (call, call))]))
    client.session = Session()
    with pytest.raises(ValueError, match="duplicate"):
        await client.process_query("Close")
    assert client.session.calls == []


async def test_cancelled_write_keeps_reconciliation_ledger():
    client = MCPClient(
        FakeProvider(
            [
                turn("a"),
                turn("b"),
                AssistantTurn({"role": "assistant", "content": "done"}, text="done"),
            ]
        )
    )
    session = Session()
    started = asyncio.Event()

    async def slow(*args):
        started.set()
        await asyncio.sleep(30)

    session.call_tool = AsyncMock(side_effect=slow)
    client.session = session
    task = asyncio.create_task(client.process_query("Close"))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert await client.process_query("Retry") == "done"
    assert session.call_tool.await_count == 1


async def test_provider_closes_when_mcp_initialization_fails(monkeypatch):
    from contextlib import asynccontextmanager

    from mcp import StdioServerParameters

    from extend_ai_toolkit.modelcontextprotocol.client import mcp_client

    provider = SimpleNamespace(aclose=AsyncMock())
    session = SimpleNamespace(initialize=AsyncMock(side_effect=RuntimeError("handshake failed")))

    @asynccontextmanager
    async def streams(*args):
        yield (object(), object())

    @asynccontextmanager
    async def session_context(*args):
        yield session

    monkeypatch.setattr(mcp_client, "stdio_client", streams)
    monkeypatch.setattr(mcp_client, "ClientSession", session_context)
    client = MCPClient(provider)
    with pytest.raises(RuntimeError, match="handshake failed"):
        async with client.connect(StdioServerParameters(command="synthetic")):
            pytest.fail("A failed handshake must not yield a client")
    provider.aclose.assert_awaited_once()
    assert client.session is None


@pytest.mark.parametrize("option", ["max_rounds", "max_calls"])
@pytest.mark.parametrize("value", [1.5, True, "2"])
def test_conversation_limits_require_integers(option, value):
    with pytest.raises(ValueError):
        MCPClient(SimpleNamespace(), **{option: value})
