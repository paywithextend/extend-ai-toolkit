from .anthropic_chat_client import AnthropicChatClient
from .chat_client import ChatClient
from .openai_chat_client import OpenAIChatClient

__all__ = [
    "AnthropicChatClient",
    "ChatClient",
    "MCPClient",
    "OpenAIChatClient",
]


def __getattr__(name):
    if name == "MCPClient":
        from .mcp_client import MCPClient
        return MCPClient
    raise AttributeError(f"module {__name__} has no attribute {name}")
