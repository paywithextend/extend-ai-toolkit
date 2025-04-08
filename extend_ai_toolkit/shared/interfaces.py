from typing import Protocol

from typing_extensions import TypeVar

from .api import ExtendAPI
from .tools import Tool

ToolType = TypeVar("ToolType", covariant=True)
AgentToolType = TypeVar("AgentToolType", bound="AgentToolInterface[ToolType]")


class AgentToolInterface(Protocol[ToolType]):
    def __init__(self, extend_api: ExtendAPI, tool: Tool) -> None:
        ...

    def build_tool(self) -> ToolType:
        ...
