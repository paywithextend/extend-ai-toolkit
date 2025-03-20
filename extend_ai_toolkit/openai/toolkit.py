from agents import FunctionTool

from extend_ai_toolkit.shared import (
    Agent,
    AgentToolkit,
    Configuration,
    ExtendAPI,
    Tool
)
from .extend_tool import ExtendTool


class ExtendOpenAIToolkit(AgentToolkit[FunctionTool]):

    def __init__(
            self, api_key: str, api_secret: str, configuration: Configuration = Configuration.all_tools()
    ):
        super().__init__(
            agent=Agent.OPENAI,
            api_key=api_key,
            api_secret=api_secret,
            configuration=configuration
        )

    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> FunctionTool:
        return ExtendTool(api, tool)
