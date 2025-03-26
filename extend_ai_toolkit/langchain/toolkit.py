from extend_ai_toolkit.shared import (
    AgentToolkit,
    Configuration,
    ExtendAPI,
    Tool
)
from .extend_tool import ExtendTool


class ExtendLangChainToolkit(AgentToolkit[ExtendTool]):

    def __init__(
            self,
            org_id: str,
            api_key: str,
            api_secret: str,
            configuration: Configuration = Configuration.all_tools()
    ):
        configuration.org_id = org_id

        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            configuration=configuration
        )

    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ExtendTool:
        return ExtendTool(api, tool)
