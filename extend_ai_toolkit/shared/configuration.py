"""Validated host capability configuration (not model-supplied authority)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import Product
from .models import Scope

if TYPE_CHECKING:
    from .tools import Tool

VALID_SCOPES = [
    "virtual_cards.read",
    "virtual_cards.update",
    "credit_cards.read",
    "transactions.read",
    "transactions.update",
    "expense_categories.read",
    "expense_categories.create",
    "expense_categories.update",
    "receipt_attachments.read",
    "receipt_attachments.create",
    "receipt_attachments.send",
    "organizations.read",
    "users.read",
    "expense_policies.read",
]


class Configuration(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    scope: list[Scope] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scopes(self):
        for scope in self.scope:
            for action, enabled in scope.actions.items():
                if type(enabled) is not bool or f"{scope.type.value}.{action}" not in VALID_SCOPES:
                    raise ValueError("Invalid scope action")
        return self

    def add_scope(self, scope):
        self.scope = type(self)(scope=[*self.scope, scope]).scope

    def allowed_tools(self, tools) -> list[Tool]:
        return [tool for tool in tools if self.is_tool_in_scope(tool)]

    def is_tool_in_scope(self, tool: Tool) -> bool:
        for required in tool.required_scope:
            actions = {
                action
                for scope in self.scope
                if scope.type == required.type
                for action, enabled in scope.actions.items()
                if enabled is True
            }
            if any(
                enabled and action not in actions for action, enabled in required.actions.items()
            ):
                return False
        return bool(tool.required_scope)

    @classmethod
    def all_tools(cls):
        return cls.from_tool_str(",".join(VALID_SCOPES))

    @classmethod
    def read_only(cls):
        return cls.from_tool_str(",".join(s for s in VALID_SCOPES if s.endswith(".read")))

    @classmethod
    def from_tool_str(cls, tools: str):
        if not isinstance(tools, str):
            raise ValueError("Scopes must be a comma-separated string")
        if tools == "":
            return cls()
        specs = [token.strip() for token in tools.split(",")]
        if specs == ["all"]:
            specs = VALID_SCOPES
        scopes = {}
        for spec in specs:
            product, action = validate_tool_spec(spec)
            scopes.setdefault(product, {})[action] = True
        return cls(scope=[Scope(product, actions) for product, actions in scopes.items()])


def validate_tool_spec(tool_spec: str) -> tuple[Product, str]:
    if tool_spec not in VALID_SCOPES:
        raise ValueError("Unknown or malformed capability; expected a supported product.action")
    product, action = tool_spec.split(".")
    return Product(product), action
