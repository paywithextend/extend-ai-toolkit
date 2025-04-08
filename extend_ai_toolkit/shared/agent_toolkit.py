from abc import abstractmethod
from typing import List, Generic

from pydantic import PrivateAttr

from .api import ExtendAPI
from .configuration import Configuration
from .enums import Agent
from .interfaces import ToolType
from .tools import Tool, tools


class AgentToolkit(Generic[ToolType]):
    _tools: List[ToolType] = PrivateAttr(default=[])
    agent: Agent

    def __init__(
            self,
            extend_api: ExtendAPI,
            configuration: Configuration,
    ):
        super().__init__()

        self._tools = [
            self.tool_for_agent(extend_api, tool)
            for tool in configuration.allowed_tools(tools)
        ]

    @classmethod
    def default_instance(cls, api_key: str, api_secret: str, configuration: Configuration) -> "AgentToolkit":
        return cls(
            extend_api=ExtendAPI.default_instance(api_key, api_secret),
            configuration=configuration
        )
    
    @abstractmethod
    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ToolType:
        raise NotImplementedError("Subclasses must implement tool_for_agent()")

    def get_tools(self) -> List[ToolType]:
        return self._tools
