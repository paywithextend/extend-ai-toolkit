"""Framework adapters delegate to the same host-policy-checked executor."""

import json

from extend import ExtendClient

from ..policy import ExecutionPolicy
from .auth import Authorization, create_client_with_auth, create_extend_client
from .configuration import Configuration


class ExtendAPI:
    def __init__(self, extend: ExtendClient, *, policy: ExecutionPolicy | None = None):
        self.extend = extend
        self.policy = policy if policy is not None else ExecutionPolicy.read_only()

    @classmethod
    def from_auth(
        cls,
        auth: Authorization,
        *,
        environment: str | None = None,
        policy: ExecutionPolicy | None = None,
    ):
        return cls(create_client_with_auth(auth, environment=environment), policy=policy)

    @classmethod
    def default_instance(
        cls,
        api_key: str,
        api_secret: str,
        *,
        environment: str | None = None,
        policy: ExecutionPolicy | None = None,
    ):
        return cls(
            create_extend_client(api_key, api_secret, environment=environment), policy=policy
        )

    def restricted_to(self, configuration: Configuration):
        return type(self)(self.extend, policy=self.policy.restrict(configuration))

    async def execute(self, tool: str, arguments: dict | None = None):
        from ..core import execute_tool

        return await execute_tool(self.extend, tool, arguments, policy=self.policy)

    async def run(self, tool: str, **kwargs) -> str:
        return json.dumps(await self.execute(tool, kwargs), ensure_ascii=False, allow_nan=False)

    async def aclose(self):
        await self.extend.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.aclose()
