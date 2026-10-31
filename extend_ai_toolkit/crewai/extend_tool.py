from typing import Any

from crewai.tools import BaseTool
from pydantic import ConfigDict, Field

from extend_ai_toolkit.shared import ExtendAPI, Tool


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
