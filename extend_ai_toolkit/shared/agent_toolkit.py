import os
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

    def __init__(
            self,
            agent: Agent,
            api_key: str,
            api_secret: str,
            configuration: Configuration
    ):
        super().__init__()

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

    @abstractmethod
    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ToolType:
        raise NotImplementedError("Subclasses must implement tool_for_agent()")

    def get_tools(self) -> List[ToolType]:
        return self._tools
