from typing import Any

from langchain_core.tools import BaseTool

from extend_ai_toolkit.shared import (
    AgentToolInterface,
    ExtendAPI,
    Tool
)


class LangChainTool(AgentToolInterface["LangChainTool._Tool"]):
    _tool: Tool
    _extend_api: ExtendAPI

    class _Tool(BaseTool):
        def __init__(
                self,
                extend_api: ExtendAPI,
                tool: Tool,
        ):
            self.extend_api = extend_api
            self.method = tool.method.value
            self.name = tool.name
            self.description = tool.description
            self.args_schema = tool.args_schema or None

        async def _run(
                self,
                *args: Any,
                **kwargs: Any,
        ) -> str:
            return await self.extend_api.run(self.method, *args, **kwargs)

    def __init__(
            self,
            extend_api: ExtendAPI,
            tool: Tool,
    ):
        self._tool = tool
        self._extend_api = extend_api

    def build_tool(self) -> _Tool:
        return LangChainTool._Tool(
            extend_api=self._extend_api,
            tool=self._tool
        )
