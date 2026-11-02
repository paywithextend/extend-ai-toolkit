"""OpenAI chat tool-call messages with provider-issued call IDs."""

import json

from openai import AsyncOpenAI

from .chat_client import AssistantTurn, ChatClient, ToolCall


class OpenAIChatClient(ChatClient):
    def __init__(self, model_name="gpt-4.1", *, client=None):
        self.model_name = model_name
        self.client = client if client is not None else AsyncOpenAI()
        self._owns_client = client is None

    async def complete(self, messages, tools, max_tokens):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=[{"type": "function", "function": tool} for tool in tools],
            max_completion_tokens=max_tokens,
            store=False,
        )
        message = response.choices[0].message
        calls = tuple(
            ToolCall(call.id, call.function.name, json.loads(call.function.arguments))
            for call in (message.tool_calls or [])
        )
        if any(not isinstance(call.arguments, dict) for call in calls):
            raise ValueError("Tool arguments must be JSON objects")
        return AssistantTurn(message.model_dump(exclude_none=True), calls, message.content or "")

    def result_messages(self, results):
        return [
            {"role": "tool", "tool_call_id": call.id, "content": content}
            for call, content, failed in results
        ]

    async def aclose(self):
        if self._owns_client:
            await self.client.close()
