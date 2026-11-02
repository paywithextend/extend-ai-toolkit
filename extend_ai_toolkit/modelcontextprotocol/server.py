"""Local stdio MCP adapter using the authoritative shared catalog."""

import json
from contextlib import asynccontextmanager

from mcp.server import MCPServer
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from mcp.types import Tool as MCPTool

from ..__version__ import __version__
from ..errors import error_payload
from ..shared.api import ExtendAPI
from ..shared.tools import tools


class ExtendMCPServer(MCPServer):
    def __init__(self, extend_api: ExtendAPI, configuration=None):
        self.api = (
            extend_api.restricted_to(configuration) if configuration is not None else extend_api
        )

        @asynccontextmanager
        async def lifespan(server):
            try:
                yield {}
            finally:
                await self.api.aclose()

        super().__init__(name="Extend", version=__version__, lifespan=lifespan)
        self._catalog = tuple(tool for tool in tools if tool.name in self.api.policy.allowed_tools)

    async def list_tools(self):
        return [
            MCPTool(
                name=tool.name,
                description=tool.description,
                input_schema=tool.args_schema.model_json_schema(),
                annotations=ToolAnnotations(
                    readOnlyHint=tool.side_effect_class == "read_only",
                    destructiveHint=tool.side_effect_class == "destructive",
                    idempotentHint=tool.side_effect_class == "read_only",
                    openWorldHint=True,
                ),
            )
            for tool in self._catalog
        ]

    async def call_tool(self, name, arguments, context=None):
        # Validate the original JSON before any framework coercion or defaulting.
        try:
            result = await self.api.execute(name, arguments)
        except Exception as exc:
            effect = next(
                (tool.side_effect_class for tool in self._catalog if tool.name == name), "unknown"
            )
            error = error_payload(exc, mutation=effect != "read_only")
            return CallToolResult(
                is_error=True,
                content=[TextContent(type="text", text=json.dumps(error))],
                structured_content=error,
            )
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result))],
            structured_content=result if isinstance(result, dict) else {"result": result},
        )

    @classmethod
    def from_auth(cls, auth, configuration=None, **host_options):
        return cls(ExtendAPI.from_auth(auth, **host_options), configuration)

    @classmethod
    def default_instance(cls, api_key, api_secret, configuration=None, **host_options):
        return cls(ExtendAPI.default_instance(api_key, api_secret, **host_options), configuration)

    def run(self, transport="stdio", **kwargs):
        if transport != "stdio" or kwargs:
            raise ValueError(
                "Only local stdio is supported; remote hosting requires a separate authenticated service"
            )
        return super().run(transport="stdio")

    async def run_sse_async(self, *args, **kwargs):
        raise ValueError("SSE hosting is disabled; use stdio")

    async def run_streamable_http_async(self, *args, **kwargs):
        raise ValueError("Remote HTTP hosting is not supported")

    def sse_app(self, *args, **kwargs):
        raise ValueError("SSE hosting is disabled; use stdio")

    def streamable_http_app(self, *args, **kwargs):
        raise ValueError("Remote HTTP hosting is not supported")
