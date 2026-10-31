from .__version__ import __version__ as _version
from .core import ToolSpec, execute_tool, list_tool_specs

__version__ = _version

__all__ = [
    "ToolSpec",
    "execute_tool",
    "list_tool_specs",
    "ExtendLangChainToolkit",
    "ExtendMCPServer",
    "ExtendOpenAIToolkit",
    "Options",
    "validate_options",
]


def __getattr__(name):
    if name == "ExtendLangChainToolkit":
        from .langchain import ExtendLangChainToolkit

        return ExtendLangChainToolkit
    if name in {"ExtendMCPServer", "Options", "validate_options"}:
        from .modelcontextprotocol import ExtendMCPServer, Options, validate_options

        return {
            "ExtendMCPServer": ExtendMCPServer,
            "Options": Options,
            "validate_options": validate_options,
        }[name]
    if name == "ExtendOpenAIToolkit":
        from .openai import ExtendOpenAIToolkit

        return ExtendOpenAIToolkit
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
