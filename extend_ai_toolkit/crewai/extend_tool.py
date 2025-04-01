from typing import Any
import asyncio
from crewai.tools import BaseTool
from pydantic import Field, ConfigDict
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
            method=tool.method.value
        )

    async def _arun(self, **kwargs: Any) -> str:
        """Run the tool asynchronously."""
        return await self.extend_api.run(self.method, **kwargs)

    def _run(self, **kwargs: Any) -> str:
        """Run the tool synchronously by creating an event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._arun(**kwargs))
        finally:
            loop.close()
