"""Shared adapter registration and lifecycle."""

from abc import abstractmethod
from typing import Generic

from .api import ExtendAPI
from .configuration import Configuration
from .interfaces import ToolType
from .tools import Tool, tools


class AgentToolkit(Generic[ToolType]):
    def __init__(self, extend_api: ExtendAPI, configuration: Configuration | None = None):
        self.api = (
            extend_api.restricted_to(configuration) if configuration is not None else extend_api
        )
        self._tools = [
            self.tool_for_agent(self.api, tool)
            for tool in tools
            if tool.name in self.api.policy.allowed_tools
        ]

    @classmethod
    def from_auth(cls, auth, configuration=None, **host_options):
        return cls(ExtendAPI.from_auth(auth, **host_options), configuration)

    @classmethod
    def default_instance(cls, api_key, api_secret, configuration=None, **host_options):
        return cls(ExtendAPI.default_instance(api_key, api_secret, **host_options), configuration)

    @abstractmethod
    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ToolType:
        raise NotImplementedError

    def get_tools(self) -> list[ToolType]:
        return list(self._tools)

    async def aclose(self):
        await self.api.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.aclose()
