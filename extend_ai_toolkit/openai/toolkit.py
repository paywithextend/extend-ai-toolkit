"""openai registration through the shared host policy."""

from agents import FunctionTool

from extend_ai_toolkit.shared import AgentToolkit, ExtendAPI, Tool

from .extend_tool import ExtendTool


class ExtendOpenAIToolkit(AgentToolkit[FunctionTool]):
    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> FunctionTool:
        return ExtendTool(api, tool)
