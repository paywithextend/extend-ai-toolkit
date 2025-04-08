from typing import Optional

from agents import FunctionTool

from extend_ai_toolkit.shared import (
    AgentToolkit,
    Configuration,
    ExtendAPI,
    Tool
)
from .extend_tool import ExtendTool


class ExtendOpenAIToolkit(AgentToolkit[FunctionTool]):

    def __init__(
            self,
            extend_api: ExtendAPI,
            configuration: Optional[Configuration]
    ):
        super().__init__(
            extend_api=extend_api,
            configuration=configuration or Configuration.all_tools()
        )

    @classmethod
    def default_instance(cls, api_key: str, api_secret: str, configuration: Configuration) -> "ExtendOpenAIToolkit":
        return cls(
            extend_api=ExtendAPI.default_instance(api_key, api_secret),
            configuration=configuration
        )

    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> FunctionTool:
        return ExtendTool(api, tool)
