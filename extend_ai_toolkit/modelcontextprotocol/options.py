"""Explicit local server configuration with read-only defaults."""

import argparse
import os

from ..shared.configuration import VALID_SCOPES, Configuration


def validate_options(cls):
    return cls


class Options:
    def __init__(self, tools=None, api_key=None, api_secret=None, environment=None):
        self.tools = (
            tools if tools is not None else ",".join(s for s in VALID_SCOPES if s.endswith(".read"))
        )
        Configuration.from_tool_str(self.tools)
        self.api_key = api_key or os.environ.get("EXTEND_API_KEY")
        self.api_secret = api_secret or os.environ.get("EXTEND_API_SECRET")
        self.environment = environment or os.environ.get("ENV")
        if not self.api_key or not self.api_secret:
            raise ValueError("Set EXTEND_API_KEY and EXTEND_API_SECRET")
        if self.environment not in {"stage", "prod"}:
            raise ValueError("Select --environment=stage or --environment=prod explicitly")

    @staticmethod
    def from_args(args, valid_tools=None):
        parser = argparse.ArgumentParser(description="Extend local read-only MCP server")
        parser.add_argument("--tools")
        parser.add_argument("--environment", choices=("stage", "prod"))
        # Credentials belong in the environment, not process arguments/history.
        return Options(**vars(parser.parse_args(args)))
