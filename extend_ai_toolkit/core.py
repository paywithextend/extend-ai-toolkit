"""Core Extend tool catalog and execution helpers.

This module is intentionally framework-neutral. It exposes structured tool
metadata and raw tool execution without requiring LangChain, MCP or OpenAI Agents
adapter dependencies.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .policy import ExecutionPolicy, ToolPermissionError
from .receipts import snapshot_receipt
from .shared import functions
from .shared.tools import Tool, tools

_ACTION_ORDER = ("read", "create", "update", "delete")
_TOOL_REF_PREFIX = "extend"
_TOOL_REF_VERSION = "v1"


@dataclass(frozen=True)
class ToolSpec:
    """Framework-neutral metadata for an Extend API tool."""

    name: str
    ref: str
    description: str
    input_schema: dict[str, Any]
    required_scopes: tuple[dict[str, Any], ...]
    product: str
    products: tuple[str, ...]
    actions: tuple[str, ...]
    side_effect_class: str


def _catalog(catalog):
    # A caller catalog only narrows names; its schemas/effect claims are never trusted.
    if catalog is None:
        return list(tools)
    names = {tool.name for tool in catalog}
    if names - {tool.name for tool in tools}:
        raise ValueError("Unknown catalog tool")
    return [tool for tool in tools if tool.name in names]


def list_tool_specs(configuration=None, *, catalog=None, policy=None) -> list[ToolSpec]:
    """Discover exactly the tools permitted by a host policy and optional scope filter."""
    policy = policy if policy is not None else ExecutionPolicy.read_only()
    if configuration is not None:
        policy = policy.restrict(configuration)
    return [_tool_spec(tool) for tool in _catalog(catalog) if tool.name in policy.allowed_tools]


async def execute_tool(
    extend: Any,
    tool_name: str,
    arguments: Mapping[str, Any] | None = None,
    *,
    catalog=None,
    policy: ExecutionPolicy | None = None,
) -> Any:
    """Validate, authorize and execute one invocation without model-granted authority."""
    tool = _tool_by_name(tool_name, _catalog(catalog))
    if tool is None:
        raise ValueError("Unknown Extend tool")
    policy = policy if policy is not None else ExecutionPolicy.read_only()
    if tool.name not in policy.allowed_tools:
        raise ToolPermissionError("Tool is not permitted by the host allowlist")
    validated = _validate_arguments(tool, copy.deepcopy(dict(arguments or {})))
    if tool.side_effect_class == "file_upload":
        if not policy.actor_id or policy.approve is None:
            raise ToolPermissionError("Host approval is required before reading receipt files")
        snapshot = snapshot_receipt(policy, validated["file_path"])
        try:
            proposal = {
                **validated,
                "file_sha256": snapshot.sha256,
                "file_size": snapshot.size,
                "content_type": snapshot.content_type,
            }
            await policy.authorize(tool.name, tool.side_effect_class, proposal)
            data = (
                {"transactionId": validated["transaction_id"]}
                if validated.get("transaction_id")
                else {}
            )
            return await extend.api_client.post_multipart(
                "/receiptattachments",
                data=data,
                files={"file": (snapshot.filename, snapshot.file, snapshot.content_type)},
            )
        finally:
            snapshot.close()
    await policy.authorize(tool.name, tool.side_effect_class, validated)
    return await getattr(functions, tool.name)(extend=extend, **validated)


def _tool_by_name(tool_name: str, catalog: Sequence[Tool]) -> Tool | None:
    for tool in catalog:
        if tool.name == tool_name or tool.method.value == tool_name:
            return tool
    return None


def _tool_spec(tool: Tool) -> ToolSpec:
    required_scopes = tuple(_scope_payload(scope) for scope in tool.required_scope)
    products = tuple(scope["product"] for scope in required_scopes)
    actions = _combined_actions(required_scopes)
    product = products[0] if products else ""
    return ToolSpec(
        name=tool.name,
        ref=_tool_ref(tool),
        description=tool.description,
        input_schema=_schema_for(tool),
        required_scopes=required_scopes,
        product=product,
        products=products,
        actions=actions,
        side_effect_class=tool.side_effect_class,
    )


def _tool_ref(tool: Tool) -> str:
    product = tool.required_scope[0].type.value if tool.required_scope else "general"
    return f"{_TOOL_REF_PREFIX}.{product}.{tool.name}.{_TOOL_REF_VERSION}"


def _scope_payload(scope: Any) -> dict[str, Any]:
    return {
        "product": scope.type.value,
        "actions": _enabled_actions(scope.actions),
    }


def _enabled_actions(actions: Mapping[str, Any]) -> tuple[str, ...]:
    enabled = {
        str(getattr(action, "value", action))
        for action, is_required in actions.items()
        if is_required
    }
    ordered = [action for action in _ACTION_ORDER if action in enabled]
    ordered.extend(sorted(enabled.difference(ordered)))
    return tuple(ordered)


def _combined_actions(required_scopes: Sequence[dict[str, Any]]) -> tuple[str, ...]:
    enabled: set[str] = set()
    for scope in required_scopes:
        enabled.update(scope["actions"])
    ordered = [action for action in _ACTION_ORDER if action in enabled]
    ordered.extend(sorted(enabled.difference(ordered)))
    return tuple(ordered)


def _schema_for(tool: Tool) -> dict[str, Any]:
    return tool.args_schema.model_json_schema()


def _validate_arguments(tool: Tool, arguments: Mapping[str, Any]) -> dict[str, Any]:
    return tool.args_schema.model_validate(arguments).model_dump(exclude_none=True)
