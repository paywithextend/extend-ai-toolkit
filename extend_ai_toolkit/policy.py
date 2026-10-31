"""Host-owned execution policy. Model arguments cannot grant permissions or approval."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .shared.configuration import Configuration


class ToolPermissionError(PermissionError):
    """The host has not authorized this tool invocation."""


@dataclass(frozen=True)
class ApprovalRequest:
    """Immutable, one-invocation proposal delivered only to the trusted host."""

    invocation_id: str
    actor_id: str
    tool_name: str
    effect: str
    arguments_json: str
    payload_sha256: str


ApprovalHandler = Callable[[ApprovalRequest], Awaitable[bool]]


@dataclass(frozen=True)
class ExecutionPolicy:
    """Immutable allowlist and optional host approval integration.

    The host authenticates actor_id and owns the handler. Never populate these
    fields from model arguments. Handlers run for every write; decisions are not
    stored or reused. A model confirmation tool is not an approval handler.
    """

    allowed_tools: frozenset[str]
    actor_id: str | None = None
    approve: ApprovalHandler | None = None
    receipt_root: Path | None = None
    max_receipt_bytes: int = 20 * 1024 * 1024
    approval_timeout: float = 120

    def __post_init__(self):
        object.__setattr__(self, "allowed_tools", frozenset(self.allowed_tools))
        if self.receipt_root is not None:
            object.__setattr__(self, "receipt_root", Path(self.receipt_root).resolve(strict=True))
        if (
            isinstance(self.max_receipt_bytes, bool)
            or not isinstance(self.max_receipt_bytes, int)
            or not 0 < self.max_receipt_bytes <= 100 * 1024 * 1024
        ):
            raise ValueError("max_receipt_bytes must be between 1 and 100 MiB")
        if not math.isfinite(self.approval_timeout) or not 0 < self.approval_timeout <= 600:
            raise ValueError("approval_timeout must be between 0 and 600 seconds")

    @classmethod
    def from_configuration(cls, configuration: Configuration, **host_options) -> ExecutionPolicy:
        from .shared.tools import tools

        return cls(
            frozenset(tool.name for tool in configuration.allowed_tools(tools)), **host_options
        )

    @classmethod
    def read_only(cls) -> ExecutionPolicy:
        from .shared.configuration import Configuration

        return cls.from_configuration(Configuration.read_only())

    def restrict(self, configuration: Configuration) -> ExecutionPolicy:
        allowed = self.from_configuration(configuration).allowed_tools
        return replace(self, allowed_tools=self.allowed_tools & allowed)

    async def authorize(self, tool_name: str, effect: str, arguments: dict[str, Any]) -> None:
        if tool_name not in self.allowed_tools:
            raise ToolPermissionError("Tool is not permitted by the host allowlist")
        if effect == "read_only":
            return
        if effect not in {"external_write", "destructive", "external_send", "file_upload"}:
            raise ToolPermissionError("Unclassified tool effect")
        if not self.actor_id or self.approve is None:
            raise ToolPermissionError(
                "A trusted actor and host approval handler are required for writes"
            )
        payload = json.dumps(arguments, sort_keys=True, separators=(",", ":"), allow_nan=False)
        request = ApprovalRequest(
            invocation_id=uuid.uuid4().hex,
            actor_id=self.actor_id,
            tool_name=tool_name,
            effect=effect,
            arguments_json=payload,
            payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),
        )
        try:
            async with asyncio.timeout(self.approval_timeout):
                approved = await self.approve(request)
        except TimeoutError as exc:
            raise ToolPermissionError("Host approval expired") from exc
        if approved is not True:
            raise ToolPermissionError("Host did not approve this invocation")
