"""Optional providers are imported only when selected."""

from .chat_client import ChatClient

__all__ = ["ChatClient", "MCPClient", "OpenAIChatClient", "AnthropicChatClient"]


def __getattr__(name):
    if name == "MCPClient":
        from .mcp_client import MCPClient

        return MCPClient
    if name == "OpenAIChatClient":
        from .openai_chat_client import OpenAIChatClient

        return OpenAIChatClient
    if name == "AnthropicChatClient":
        from .anthropic_chat_client import AnthropicChatClient

        return AnthropicChatClient
    raise AttributeError(name)
