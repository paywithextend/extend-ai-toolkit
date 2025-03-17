import os
from typing import List
from typing import Optional

from pydantic import PrivateAttr

from extend_ai_toolkit.shared import Configuration
from extend_ai_toolkit.shared import tools
from extend_ai_toolkit.shared.api import ExtendAPI
from .tool import ExtendTool


class ExtendLangChainToolkit:
    _tools: List = PrivateAttr(default=[])

    def __init__(
            self, api_key: str, api_secret: str, configuration: Optional[Configuration] = None
    ):
        super().__init__()

        host = os.getenv("API_HOST")
        if host is None:
            raise ValueError("API_HOST environment variable must be set")
        version = os.getenv("API_VERSION")
        if version is None:
            raise ValueError("API_VERSION environment variable must be set")

        extend_api = ExtendAPI(
            host=host,
            version=version,
            api_key=api_key,
            api_secret=api_secret
        )

        self._tools = [
            ExtendTool(
                name=tool.name,
                description=tool.description,
                method=tool.method.value,
                extend_api=extend_api,
                args_schema=tool.args_schema or None,
            )
            for tool in (configuration.allowed_tools(tools) if configuration else tools)
        ]

    def get_tools(self) -> List:
        return self._tools
