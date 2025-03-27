from typing import Optional, List

from pydantic.v1 import BaseModel

from .enums import Product, Action
from .models import Scope, Actions
from .tools import Tool
from .utils import pop_first

VALID_SCOPES = [
    'virtual_cards.create',
    'virtual_cards.update',
    'virtual_cards.read',
    'credit_cards.read',
    'transactions.read',
]


class Configuration(BaseModel):
    scope: Optional[List[Scope]] = None
    org_id: Optional[str]

    def add_scope(self, scope):
        if not self.scope:
            self.scope = []
        self.scope.append(scope)

    def allowed_tools(self, tools) -> list[Tool]:
        return [tool for tool in tools if self.is_tool_in_scope(tool)]

    def is_tool_in_scope(self, tool: Tool) -> bool:
        if not self.scope:
            return False

        for tool_scope in tool.required_scope:
            configured_scope = next(
                filter(lambda x: x.type == tool_scope.type, self.scope),
                None
            )
            if configured_scope is None:
                return False
            for action in tool_scope.actions.keys():
                if not configured_scope.actions.get(action, False):
                    return False
        return True

    @classmethod
    def all_tools(cls, org_id: str = None) -> "Configuration":
        scopes: List[Scope] = []
        for tool in VALID_SCOPES:
            product_str, action_str = tool.split(".")
            scope: Scope = pop_first(
                scopes,
                lambda x: x.type.value == product_str,
                default=None
            )
            if scope:
                action = Action(action_str)
                scope.actions[action.value] = True
                scopes.append(scope)
            else:
                scope = Scope.from_str(product_str, action_str)
                scopes.append(scope)

        return cls(scope=scopes, org_id=org_id)

    @classmethod
    def from_tool_str(cls, tools: str, org_id: str) -> "Configuration":
        configuration = cls(scope=[])
        tool_specs = tools.split(",") if tools else []

        if "all" in tools:
            configuration = Configuration.all_tools()
        else:
            validated_tools = []
            for tool_spec in tool_specs:
                validated_tools.append(validate_tool_spec(tool_spec))

            for product, action_str in validated_tools:
                scope = Scope(product, Actions(**{action_str: True}))
                configuration.add_scope(scope)
        configuration.org_id = org_id
        return configuration


def validate_tool_spec(tool_spec: str) -> tuple[Product, str]:
    try:
        product_str, action = tool_spec.split(".")
    except ValueError:
        raise ValueError(f"Tool spec '{tool_spec}' must be in the format 'product.action'")

    try:
        product = Product(product_str)
    except ValueError:
        raise ValueError(f"Invalid product: '{product_str}'. Valid products are: {[p.value for p in Product]}")

    valid_actions = Actions.__annotations__.keys()
    if action not in valid_actions:
        raise ValueError(f"Invalid action: '{action}'. Valid actions are: {list(valid_actions)}")

    return product, action
