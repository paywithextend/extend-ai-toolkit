import json
import os
from typing import List, Dict, Any, Tuple, Optional

from anthropic import AsyncAnthropic

from .chat_client import ChatClient


class AnthropicChatClient(ChatClient):
    """Implementation of ChatClient for Anthropic API"""

    def __init__(
            self,
            model_name="claude-3-7-sonnet-20250219",
            system_prompt="You are a helpful assistant."):
        self.model_name = model_name
        self.client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.system_prompt = system_prompt

    async def generate_completion(
            self,
            messages: List[Dict[str, Any]],
            functions: List[Dict[str, Any]],
            max_tokens: int
    ) -> Tuple[Optional[str], Optional[Dict]]:
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = self._convert_messages(messages)

        # Convert OpenAI-style functions to Anthropic tools
        tools = self._convert_functions_to_tools(functions)

        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=anthropic_messages,
            tools=tools,
            system=self.system_prompt
        )

        # Process all content blocks and prioritize tool_use if present
        text_content = []
        tool_use_info = None

        if response.content and len(response.content) > 0:
            for content_block in response.content:
                if content_block.type == "tool_use":
                    # Get tool use data
                    name = getattr(content_block, "name", None)
                    input_data = getattr(content_block, "input", {})

                    # Convert input data to JSON string
                    try:
                        input_json = json.dumps(input_data)
                    except TypeError:
                        # Fallback for non-JSON-serializable objects
                        if hasattr(input_data, "__dict__"):
                            input_dict = input_data.__dict__
                        else:
                            input_dict = {"data": str(input_data)}
                        input_json = json.dumps(input_dict)

                    tool_use_info = {
                        "name": name if name else "unknown_tool",
                        "arguments": input_json
                    }
                elif content_block.type == "text":
                    text_content.append(str(content_block.text))

        # Combine all text content
        combined_text = "\n".join(text_content) if text_content else None

        # Prioritize tool_use if present
        if tool_use_info:
            return combined_text, tool_use_info
        else:
            return combined_text, None

    async def generate_with_tool_result(
            self,
            messages: List[Dict[str, Any]],
            max_tokens: int) -> str:
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = self._convert_messages(messages)

        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=anthropic_messages,
            system=self.system_prompt
        )

        if response.content and len(response.content) > 0:
            text_blocks = []

            for content_block in response.content:
                if content_block.type == "text":
                    text_blocks.append(str(content_block.text))

            return "\n".join(text_blocks) if text_blocks else ""

        return ""

    def _convert_messages(self, openai_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI message format to Anthropic format"""
        anthropic_messages = []
        tool_use_ids = {}  # Map to store tool use IDs
        tool_use_count = 0

        for i, msg in enumerate(openai_messages):
            if msg["role"] == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": msg["content"]
                })
            elif msg["role"] == "assistant":
                # Handle potential function calls in assistant messages
                if msg.get("function_call"):
                    # Create a unique ID for this tool use
                    tool_use_id = f"tool_{tool_use_count}"
                    tool_use_count += 1

                    # Store the mapping for future tool results
                    tool_use_ids[len(anthropic_messages)] = tool_use_id

                    try:
                        input_data = json.loads(msg["function_call"]["arguments"])
                    except json.JSONDecodeError:
                        input_data = {}

                    anthropic_messages.append({
                        "role": "assistant",
                        "content": [{
                            "type": "tool_use",
                            "id": tool_use_id,
                            "name": msg["function_call"]["name"],
                            "input": input_data
                        }]
                    })
                else:
                    anthropic_messages.append({
                        "role": "assistant",
                        "content": msg["content"]
                    })
            elif msg["role"] == "function":
                # Convert function messages to tool responses
                # Find the corresponding tool use ID if available
                # Default to a generated ID if not found
                tool_use_id = tool_use_ids.get(len(anthropic_messages) - 1, f"tool_{tool_use_count}")
                tool_use_count += 1

                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,  # Using tool_use_id as required by Anthropic API
                        "content": msg["content"]
                    }]
                })

        return anthropic_messages

    def _convert_functions_to_tools(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI function definitions to Anthropic tool format"""
        tools = []

        for func in functions:
            tools.append({
                "name": func["name"],
                "description": func.get("description", ""),
                "input_schema": func["parameters"]
            })

        return tools
