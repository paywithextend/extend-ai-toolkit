# openai_client.py
import os
from typing import List, Dict, Any, Tuple, Optional

from openai import AsyncOpenAI

from extend_ai_toolkit.modelcontextprotocol.client import ChatClient


class OpenAIChatClient(ChatClient):
    """Implementation of ChatClient for OpenAI's API"""

    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def generate_completion(
            self,
            messages: List[Dict[str, Any]],
            functions: List[Dict[str, Any]],
            max_tokens: int
    ) -> Tuple[Optional[str], Optional[Dict]]:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=messages,
            functions=functions
        )

        choice = response.choices[0]

        # Check if the assistant wants to call a function
        if choice.finish_reason == "function_call":
            func_call = choice.message.function_call
            function_call_info = {
                "name": func_call.name,
                "arguments": func_call.arguments
            }
            return None, function_call_info
        else:
            # No function call; return the assistant's message directly
            return choice.message.content, None

    async def generate_with_tool_result(
            self,
            messages: List[Dict[str, Any]],
            max_tokens: int
    ) -> str:
        follow_up = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=messages,
        )

        return follow_up.choices[0].message.content
