from typing import Literal, Optional, cast

from pydantic.v1 import BaseModel
from typing_extensions import TypedDict

from .tools import Tool

Object = Literal[
    "credit_cards",
    "virtual_cards",
    "transactions",
]


class Permission(TypedDict, total=False):
    create: Optional[bool]
    update: Optional[bool]
    read: Optional[bool]


class Actions(TypedDict, total=False):
    credit_cards: Optional[Permission]
    virtual_cards: Optional[Permission]
    transactions: Optional[Permission]


class Context(TypedDict, total=False):
    org_id: Optional[str]


class Configuration(BaseModel):
    """
    Configuration for tools and permissions.

    Attributes:
        actions: A dictionary mapping tools to a dictionary of permission flags.
        context: Additional context for the configuration.
    """
    actions: Optional[Actions] = None
    context: Optional[Context] = None

    def is_tool_allowed(self, tool) -> bool:
        """
        Check if the provided tool is allowed based on configured actions and permissions.

        """
        if not self.actions:
            return False

        for resource, permissions in tool.actions.items():
            if resource not in self.actions:
                return False
            for permission in permissions:
                actions = cast(dict, self.actions) if self.actions is not None else {}
                if not actions.get(resource, {}).get(permission, False):
                    return False
        return True

    def allowed_tools(self, tools) -> list[Tool]:
        """
        Return which tools are allowed based on configured actions and permissions.

        """
        return [tool for tool in tools if self.is_tool_allowed(tool)]

    @classmethod
    def allTools(cls) -> "Configuration":
        """
        Create a Configuration instance that allows all tools.        .
        """
        actions: Actions = {
            "credit_cards": {
                "read": True,
                "create": True,
                "update": True,
            },
            "virtual_cards": {
                "read": True,
                "create": True,
                "update": True,
            },
            "transactions": {
                "read": True,
                "update": True,
            },
        }
        return cls(actions=actions)
