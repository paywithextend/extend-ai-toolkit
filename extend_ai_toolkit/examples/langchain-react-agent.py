"""Asynchronous langchain adapter read example; --fixture makes no network requests."""

import argparse
import asyncio
import json
import os

import httpx
from extend import ExtendClient
from extend.auth import BasicAuth

from extend_ai_toolkit.langchain import ExtendLangChainToolkit
from extend_ai_toolkit.shared import ExtendAPI


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--environment", choices=("stage", "prod"))
    args = parser.parse_args()
    if not args.fixture and args.environment is None:
        parser.error("Choose --environment explicitly")
    transport = (
        httpx.MockTransport(
            lambda request: httpx.Response(
                200, json={"virtualCards": [], "pagination": {"page": 0}}
            )
        )
        if args.fixture
        else None
    )
    async with httpx.AsyncClient(transport=transport, trust_env=False) as http:
        async with ExtendClient(
            auth=BasicAuth(
                "synthetic" if args.fixture else os.environ["EXTEND_API_KEY"],
                "synthetic" if args.fixture else os.environ["EXTEND_API_SECRET"],
            ),
            environment="stage" if args.fixture else args.environment,
            http_client=http,
        ) as sdk:
            toolkit = ExtendLangChainToolkit(ExtendAPI(sdk))
            tool = next(tool for tool in toolkit.get_tools() if tool.name == "get_virtual_cards")
            result = await tool.ainvoke({})
            print(json.dumps(json.loads(result), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
