from extend_ai_toolkit.shared import (
    Agent,
    AgentToolkit,
    Configuration,
    ExtendAPI,
    Tool
)
from .extend_tool import ExtendTool


class ExtendLangChainToolkit(AgentToolkit[ExtendTool]):

    def __init__(
            self, api_key: str, api_secret: str, configuration: Configuration = Configuration.allTools()
    ):
        super().__init__(
            agent=Agent.LANGCHAIN,
            api_key=api_key,
            api_secret=api_secret,
            configuration=configuration
        )

        def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ExtendTool:
            return ExtendTool(api, tool)
