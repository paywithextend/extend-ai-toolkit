from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from extend_ai_toolkit.shared.api import ExtendAPI


class ExtendTool(BaseTool):
    """Tool for interacting with the Extend API."""

    extend_api: ExtendAPI
    method: str
    name: str = ""
    description: str = ""
    args_schema: Optional[Type[BaseModel]] = None

    async def _run(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> str:
        return await self.extend_api.run(self.method, *args, **kwargs)
