"""Core Extend tool catalog and execution helpers.

This module is intentionally framework-neutral. It exposes structured tool
metadata and raw tool execution without requiring LangChain, MCP, OpenAI Agents,
or CrewAI adapter dependencies.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Callable

from .shared import functions
from .shared.configuration import Configuration
from .shared.enums import ExtendAPITools
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


_RAW_FUNCTIONS: dict[ExtendAPITools, Callable[..., Any]] = {
    ExtendAPITools.GET_VIRTUAL_CARDS: functions.get_virtual_cards,
    ExtendAPITools.GET_VIRTUAL_CARD_DETAIL: functions.get_virtual_card_detail,
    ExtendAPITools.CANCEL_VIRTUAL_CARD: functions.cancel_virtual_card,
    ExtendAPITools.CLOSE_VIRTUAL_CARD: functions.close_virtual_card,
    ExtendAPITools.GET_CREDIT_CARDS: functions.get_credit_cards,
    ExtendAPITools.GET_CREDIT_CARD_DETAIL: functions.get_credit_card_detail,
    ExtendAPITools.GET_TRANSACTIONS: functions.get_transactions,
    ExtendAPITools.COUNT_TRANSACTIONS: functions.count_transactions,
    ExtendAPITools.GET_TRANSACTION_DETAIL: functions.get_transaction_detail,
    ExtendAPITools.UPDATE_TRANSACTION_EXPENSE_DATA: (
        functions.update_transaction_expense_data
    ),
    ExtendAPITools.GET_EXPENSE_CATEGORIES: functions.get_expense_categories,
    ExtendAPITools.GET_EXPENSE_CATEGORY: functions.get_expense_category,
    ExtendAPITools.GET_EXPENSE_CATEGORY_LABELS: functions.get_expense_category_labels,
    ExtendAPITools.GET_EXPENSE_CATEGORY_LABEL: functions.get_expense_category_label,
    ExtendAPITools.CREATE_EXPENSE_CATEGORY: functions.create_expense_category,
    ExtendAPITools.CREATE_EXPENSE_CATEGORY_LABEL: (
        functions.create_expense_category_label
    ),
    ExtendAPITools.UPDATE_EXPENSE_CATEGORY: functions.update_expense_category,
    ExtendAPITools.UPDATE_EXPENSE_CATEGORY_LABEL: (
        functions.update_expense_category_label
    ),
    ExtendAPITools.GET_ORGANIZATIONS: functions.get_organizations,
    ExtendAPITools.GET_ORGANIZATION_MEMBERS: functions.get_organization_members,
    ExtendAPITools.GET_USER_DETAILS: functions.get_user_details,
    ExtendAPITools.GET_EXPENSE_POLICY: functions.get_expense_policy,
    ExtendAPITools.PROPOSE_EXPENSE_CATEGORY_LABEL: (
        functions.propose_transaction_expense_data
    ),
    ExtendAPITools.CONFIRM_EXPENSE_CATEGORY_LABEL: (
        functions.confirm_transaction_expense_data
    ),
    ExtendAPITools.CREATE_RECEIPT_ATTACHMENT: functions.create_receipt_attachment,
    ExtendAPITools.AUTOMATCH_RECEIPTS: functions.automatch_receipts,
    ExtendAPITools.GET_AUTOMATCH_STATUS: functions.get_automatch_status,
    ExtendAPITools.SEND_RECEIPT_REMINDER: functions.send_receipt_reminder,
}


def list_tool_specs(
    configuration: Configuration | None = None,
    *,
    catalog: Sequence[Tool] | None = None,
) -> list[ToolSpec]:
    """Return framework-neutral tool metadata for the configured tools."""
    selected_catalog = list(tools if catalog is None else catalog)
    selected_tools = (
        selected_catalog
        if configuration is None
        else configuration.allowed_tools(selected_catalog)
    )
    return [_tool_spec(tool) for tool in selected_tools]


async def execute_tool(
    extend: Any,
    tool_name: str,
    arguments: Mapping[str, Any] | None = None,
    *,
    catalog: Sequence[Tool] | None = None,
) -> Any:
    """Validate and execute a raw Extend tool, returning structured API data."""
    tool = _tool_by_name(tool_name, tools if catalog is None else catalog)
    if tool is None:
        raise ValueError(f"Unknown Extend tool: {tool_name}")
    function = _RAW_FUNCTIONS.get(tool.method)
    if function is None:
        raise ValueError(f"Extend tool has no executor: {tool_name}")

    validated_arguments = _validate_arguments(tool, arguments or {})
    return await function(extend=extend, **validated_arguments)


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
        side_effect_class=_side_effect_class(actions),
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


def _side_effect_class(actions: Sequence[str]) -> str:
    if any(action in {"create", "update", "delete"} for action in actions):
        return "external_write"
    return "read_only"


def _schema_for(tool: Tool) -> dict[str, Any]:
    schema_model = tool.args_schema
    if hasattr(schema_model, "model_json_schema"):
        return schema_model.model_json_schema()
    return schema_model.schema()


def _validate_arguments(tool: Tool, arguments: Mapping[str, Any]) -> dict[str, Any]:
    validated = tool.args_schema(**dict(arguments))
    if hasattr(validated, "model_dump"):
        return validated.model_dump(exclude_none=True)
    return validated.dict(exclude_none=True)
