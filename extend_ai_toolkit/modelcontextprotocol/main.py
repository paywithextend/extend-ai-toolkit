"""Start the local read-only MCP server without import-time side effects."""

import sys

from ..policy import ExecutionPolicy
from ..shared.configuration import Configuration
from .options import Options
from .server import ExtendMCPServer


def build_server(args=None):
    options = Options.from_args(sys.argv[1:] if args is None else args)
    configuration = Configuration.from_tool_str(options.tools)
    requested = ExecutionPolicy.from_configuration(configuration)
    if requested.allowed_tools - ExecutionPolicy.read_only().allowed_tools:
        raise ValueError(
            "CLI hosts are read-only. Embed ExtendMCPServer with a trusted host approval handler for writes."
        )
    return ExtendMCPServer.default_instance(
        options.api_key, options.api_secret, configuration, environment=options.environment
    )


if __name__ == "__main__":
    build_server().run()
