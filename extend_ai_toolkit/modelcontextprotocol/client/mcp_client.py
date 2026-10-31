"""Reference client for bounded Extend conversations over local stdio MCP."""

import argparse
import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ...shared.tools import tools as catalog

_EFFECTS = {tool.name: tool.side_effect_class for tool in catalog}
_SCHEMAS = {tool.name: tool.args_schema for tool in catalog}


class MCPClient:
    def __init__(self, llm_client, *, max_tokens=1000, max_rounds=8, max_calls=32):
        if not 1 <= max_rounds <= 32 or not 1 <= max_calls <= 128:
            raise ValueError("Conversation limits are out of range")
        self.llm_client = llm_client
        self.max_tokens = max_tokens
        self.max_rounds = max_rounds
        self.max_calls = max_calls
        self.session = None
        self.messages = []
        self._attempted_writes = set()
        self._seen_call_ids = set()
        self._busy = asyncio.Lock()

    @asynccontextmanager
    async def connect(self, parameters: StdioServerParameters):
        if not isinstance(parameters, StdioServerParameters):
            raise ValueError(
                "Use StdioServerParameters; unauthenticated remote URLs are unsupported"
            )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                try:
                    yield self
                finally:
                    self.session = None
                    await self.llm_client.aclose()

    async def list_available_tools(self):
        if self.session is None:
            raise RuntimeError("Connect before requesting tools")
        listed = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            }
            for tool in listed.tools
            if tool.name in _EFFECTS
        ]

    async def _call(self, call, allowed):
        if call.name not in allowed:
            return call, json.dumps({"error": "tool_not_available"}), True
        try:
            canonical = _SCHEMAS[call.name].model_validate(call.arguments).model_dump(exclude_none=True)
        except ValueError:
            return call, json.dumps({"error": "invalid_arguments"}), True
        if _EFFECTS[call.name] != "read_only":
            fingerprint = json.dumps([call.name, canonical], sort_keys=True, allow_nan=False)
            if fingerprint in self._attempted_writes:
                return (
                    call,
                    json.dumps(
                        {"error": "write_already_attempted", "action": "reconcile_before_retry"}
                    ),
                    True,
                )
            # Record before dispatch: a timeout/cancellation can leave a committed mutation.
            self._attempted_writes.add(fingerprint)
        try:
            result = await self.session.call_tool(call.name, call.arguments)
            structured = result.structured_content
            content = (
                json.dumps(structured)
                if structured is not None
                else "\n".join(
                    item.text for item in result.content if getattr(item, "type", None) == "text"
                )
            )
            return call, content, bool(result.is_error)
        except asyncio.CancelledError:
            raise
        except Exception:
            return (
                call,
                json.dumps(
                    {
                        "error": "tool_transport_failed",
                        "action": "reconcile_write_outcome_before_retry",
                    }
                ),
                True,
            )

    async def process_query(self, query):
        async with self._busy:
            definitions = await self.list_available_tools()
            allowed = {tool["name"] for tool in definitions}
            self.messages.append({"role": "user", "content": query})
            calls_used = 0
            seen_ids = self._seen_call_ids
            for _ in range(self.max_rounds):
                turn = await self.llm_client.complete(self.messages, definitions, self.max_tokens)
                if any(not call.id or call.id in seen_ids for call in turn.calls) or len(
                    {c.id for c in turn.calls}
                ) != len(turn.calls):
                    raise ValueError("Provider returned duplicate or missing tool call IDs")
                calls_used += len(turn.calls)
                if calls_used > self.max_calls:
                    raise RuntimeError(
                        "Tool call limit reached; no calls from this round were executed"
                    )
                seen_ids.update(call.id for call in turn.calls)
                self.messages.append(turn.message)
                if not turn.calls:
                    return turn.text
                results = []
                # Parallelize consecutive reads only; preserve all mutation ordering.
                batch = []

                async def flush_reads():
                    if batch:
                        results.extend(
                            await asyncio.gather(*(self._call(call, allowed) for call in batch))
                        )
                        batch.clear()

                try:
                    for call in turn.calls:
                        if _EFFECTS.get(call.name) == "read_only":
                            batch.append(call)
                        else:
                            await flush_reads()
                            results.append(await self._call(call, allowed))
                    await flush_reads()
                except asyncio.CancelledError:
                    completed = {call.id for call, _, _ in results}
                    results.extend(
                        (
                            call,
                            json.dumps({"error": "cancelled", "action": "reconcile_write_outcome"}),
                            True,
                        )
                        for call in turn.calls
                        if call.id not in completed
                    )
                    self.messages.extend(self.llm_client.result_messages(results))
                    raise
                self.messages.extend(self.llm_client.result_messages(results))
            raise RuntimeError("Conversation round limit reached; writes will not be retried")


async def main():
    parser = argparse.ArgumentParser(description="Reference local Extend MCP terminal client")
    parser.add_argument("--provider", choices=("openai", "anthropic"), default="openai")
    parser.add_argument("--model", required=True)
    parser.add_argument("--environment", choices=("stage", "prod"), required=True)
    args = parser.parse_args()
    if args.provider == "openai":
        from .openai_chat_client import OpenAIChatClient

        provider = OpenAIChatClient(args.model)
    else:
        from .anthropic_chat_client import AnthropicChatClient

        provider = AnthropicChatClient(args.model)
    client = MCPClient(provider)
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "extend_ai_toolkit.modelcontextprotocol.main",
            "--environment=" + args.environment,
        ],
        env={
            name: os.environ[name]
            for name in ("EXTEND_API_KEY", "EXTEND_API_SECRET")
            if name in os.environ
        },
    )
    async with client.connect(parameters):
        while True:
            query = await asyncio.to_thread(input, "You: ")
            if query.strip().lower() in {"quit", "exit"}:
                break
            try:
                print(await client.process_query(query))
            except Exception:
                print(
                    "Request failed or reached its limit. Reconcile any pending write before retrying."
                )


if __name__ == "__main__":
    asyncio.run(main())
