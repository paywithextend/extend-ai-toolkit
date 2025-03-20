import os
import sys

import uvicorn
from colorama import Fore
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from extend_ai_toolkit.modelcontextprotocol import ExtendMCPServer, Options
from extend_ai_toolkit.shared import Configuration
from extend_ai_toolkit.shared.configuration import VALID_PRODUCT_PERMISSIONS

load_dotenv()


def create_starlette_app(sse_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await sse_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def build_server():
    options = Options.from_args((sys.argv[1:]), VALID_PRODUCT_PERMISSIONS)
    selected_tools = options.tools
    configuration = Configuration.from_tool_str(selected_tools)

    return ExtendMCPServer(
        api_key=options.api_key,
        api_secret=options.api_secret,
        configuration=configuration
    )


server = build_server()


def handle_error(error):
    sys.stderr.write(f"\n{Fore.RED}   {str(error)}\n")


if __name__ == "__main__":
    try:
        mcp_server = server._mcp_server

        import argparse

        # parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
        # parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
        # parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
        # args = parser.parse_args()
        host = os.environ.get("MCP_HOST")
        port = os.environ.get("MCP_PORT")

        # Bind SSE request handling to MCP server
        starlette_app = create_starlette_app(mcp_server, debug=True)

        uvicorn.run(starlette_app, host=host, port=int(port))
    except Exception as e:
        handle_error(e)
