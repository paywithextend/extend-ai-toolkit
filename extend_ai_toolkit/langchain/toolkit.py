"""langchain registration through the shared host policy."""

from extend_ai_toolkit.shared import AgentToolkit, ExtendAPI, Tool

from .extend_tool import ExtendTool


class ExtendLangChainToolkit(AgentToolkit[ExtendTool]):
    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> ExtendTool:
        return ExtendTool(api, tool)
