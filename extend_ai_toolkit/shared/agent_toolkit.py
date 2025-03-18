import os
from typing import List, Generic, Type

from pydantic import PrivateAttr

from .api import ExtendAPI
from .configuration import Configuration
from .enums import Agent
from .interfaces import ToolType, AgentToolType
from .tools import Tool, tools


class ExtendAgentToolkit(Generic[ToolType, AgentToolType]):
    _tools: List[ToolType] = PrivateAttr(default=[])

    def __init__(
            self,
            tool_class: Type[AgentToolType],
            agent: Agent,
            api_key: str,
            api_secret: str,
            configuration: Configuration
    ):
        super().__init__()

        self.tool_class = tool_class

        host = os.getenv("API_HOST")
        if host is None:
            raise ValueError("API_HOST environment variable must be set")
        version = os.getenv("API_VERSION")
        if version is None:
            raise ValueError("API_VERSION environment variable must be set")

        extend_api = ExtendAPI(
            host=host,
            version=version,
            api_key=api_key,
            api_secret=api_secret
        )

        self._tools = [
            self.tool_for_agent(extend_api, tool)
            for tool in configuration.allowed_tools(tools)
        ]

    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ToolType:
        instance: AgentToolType = self.tool_class(api, tool)
        return instance.build_tool()

    def get_tools(self) -> List[ToolType]:
        return self._tools
