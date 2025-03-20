from typing import Optional, List

from pydantic.v1 import BaseModel

from .enums import Product, Action
from .models import ProductPermissions, Permissions
from .tools import Tool
from .utils import pop_first

VALID_PRODUCT_PERMISSIONS = [
    'virtual_cards.create',
    'virtual_cards.update',
    'virtual_cards.read',
    'credit_cards.read',
    'transactions.read',
]


class Configuration(BaseModel):
    product_permissions: Optional[List[ProductPermissions]] = None

    def add_permission(self, permission):
        if not self.product_permissions:
            self.product_permissions = []
        self.product_permissions.append(permission)

    def allowed_tools(self, tools) -> list[Tool]:
        return [tool for tool in tools if self.is_tool_permissible(tool)]

    def is_tool_permissible(self, tool: Tool) -> bool:
        if not self.product_permissions:
            return False

        for tool_permission in tool.required_permissions:
            configured_permission = next(
                filter(lambda x: x.type == tool_permission.type, self.product_permissions),
                None
            )
            if configured_permission is None:
                return False
            for permission in tool_permission.permissions.keys():
                if not configured_permission.permissions.get(permission, False):
                    return False
        return True

    @classmethod
    def all_tools(cls) -> "Configuration":
        product_permissions: List[ProductPermissions] = []
        for tool in VALID_PRODUCT_PERMISSIONS:
            product_str, action_str = tool.split(".")
            prod_permission: ProductPermissions = pop_first(
                product_permissions,
                lambda x: x.type.value == product_str,
                default=None
            )
            if prod_permission:
                action = Action(action_str)
                prod_permission.permissions[action.value] = True
                product_permissions.append(prod_permission)
            else:
                prod_permission = ProductPermissions.from_str(product_str, action_str)
                product_permissions.append(prod_permission)

        return cls(product_permissions=product_permissions)

    @classmethod
    def from_tool_str(cls, tools: str) -> "Configuration":
        configuration = cls(product_permissions=[])
        tool_specs = tools.split(",") if tools else []

        if "all" in tools:
            configuration = Configuration.all_tools()
        else:
            validated_tools = []
            for tool_spec in tool_specs:
                validated_tools.append(validate_tool_spec(tool_spec))

            for product, action_str in validated_tools:
                product_permission = ProductPermissions(product, Permissions(**{action_str: True}))
                configuration.add_permission(product_permission)
        return configuration


def validate_tool_spec(tool_spec: str) -> tuple[Product, str]:
    try:
        product_str, permission = tool_spec.split(".")
    except ValueError:
        raise ValueError(f"Tool spec '{tool_spec}' must be in the format 'product.permission'")

    try:
        product = Product(product_str)
    except ValueError:
        raise ValueError(f"Invalid product: '{product_str}'. Valid products are: {[p.value for p in Product]}")

    valid_permissions = Permissions.__annotations__.keys()
    if permission not in valid_permissions:
        raise ValueError(f"Invalid permission: '{permission}'. Valid permissions are: {list(valid_permissions)}")

    return product, permission
