from typing import Any

from crewai.tools import BaseTool
from crewai.tools.structured_tool import CrewStructuredTool
from pydantic import ConfigDict, Field

from extend_ai_toolkit.shared import ExtendAPI, Tool


class AsyncExtendStructuredTool(CrewStructuredTool):
    """Never create a new event loop around the pooled Extend client."""

    def invoke(self, *args, **kwargs):
        raise NotImplementedError("Use ainvoke for Extend tools")


class ExtendCrewAITool(BaseTool):
    """Tool for interacting with the Extend API in CrewAI."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    extend_api: ExtendAPI = Field(description="The Extend API client")
    method: str = Field(description="The method to call on the Extend API")

    def __init__(self, api: ExtendAPI, tool: Tool):
        super().__init__(
            name=tool.method.value,
            description=tool.description,
            args_schema=tool.args_schema,
            extend_api=api,
            method=tool.method.value,
        )

    async def _arun(self, **kwargs: Any) -> str:
        """Run the tool asynchronously."""
        return await self.extend_api.run(self.method, **kwargs)

    def _run(self, **kwargs: Any) -> str:
        """Require the asynchronous API so the pooled SDK keeps one event loop."""
        raise NotImplementedError("Use CrewAI asynchronous tool execution")

    def to_structured_tool(self):
        tool = AsyncExtendStructuredTool(
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
            func=self._arun,
            result_schema=self.result_schema,
            result_as_answer=self.result_as_answer,
            max_usage_count=self.max_usage_count,
            current_usage_count=self.current_usage_count,
            cache_function=self.cache_function,
            tool_failure_policy=self.tool_failure_policy,
        )
        tool._original_tool = self
        return tool
