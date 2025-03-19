from typing import Any

from extend_ai_toolkit.shared import (
    ExtendAPI,
    Tool
)


class ExtendTool:
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
