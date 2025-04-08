from typing import Any
from langchain_core.tools import BaseTool
from pydantic import Field
from extend_ai_toolkit.shared import ExtendAPI, Tool


class ExtendTool(BaseTool):
    """Tool for interacting with Extend API."""
    
    extend_api: ExtendAPI = Field(description="The Extend API client")
    method: str = Field(description="The method to call on the Extend API")

    def __init__(
            self,
            extend_api: ExtendAPI,
            tool: Tool,
    ):
        super().__init__(
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
            extend_api=extend_api,
            method=tool.method.value
        )

    async def _arun(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> str:
        return await self.extend_api.run(self.method, *args, **kwargs)

    def _run(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> str:
        raise NotImplementedError("ExtendTool only supports async operations")
