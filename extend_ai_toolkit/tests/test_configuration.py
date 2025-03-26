# test_configuration.py

from dataclasses import dataclass
from typing import List

import pytest

from extend_ai_toolkit.shared import (
    Configuration,
    Product,
    Permissions,
)


# Dummy implementations for testing:
class ToolPermission:
    """
    Represents a permission requirement for a tool.
    """

    def __init__(self, type: Product, permissions: Permissions):
        self.type = type
        self.permissions = permissions


@dataclass
class Tool:
    """
    A dummy Tool for testing. It has a name and a list of required permissions.
    """
    name: str
    required_permissions: List[ToolPermission]


# Test that the classmethod all_tools creates a configuration with the expected defaults.
def test_all_tools_configuration():
    config = Configuration.all_tools(org_id="test_org_id")
    # Expecting three product permissions.
    assert config.product_permissions is not None
    assert config.org_id is "test_org_id"
    assert len(config.product_permissions) == 3
    # Check that each default permission is set as expected.
    for pp in config.product_permissions:
        if pp.type == Product.CREDIT_CARDS:
            assert pp.permissions.get("read") is True
        elif pp.type == Product.VIRTUAL_CARDS:
            assert pp.permissions.get("read") is True
            assert pp.permissions.get("create") is True
            assert pp.permissions.get("update") is True
        elif pp.type == Product.TRANSACTIONS:
            assert pp.permissions.get("read") is True


# Test is_tool_permissible returns True when tool requirements match configuration
def test_is_tool_permissible_success():
    config = Configuration.all_tools()
    # Create a tool that requires credit_cards permission with read allowed.
    tool_perm = ToolPermission(
        type=Product.CREDIT_CARDS,
        permissions=Permissions(read=True)
    )
    tool = Tool(name="Tool1", required_permissions=[tool_perm])
    # Assuming the default configuration for CREDIT_CARDS has read True.
    assert config.is_tool_permissible(tool) is True


# Test is_tool_permissible returns False when a required permission is missing.
def test_is_tool_permissible_failure_missing_permission():
    config = Configuration.all_tools()
    # For TRANSACTIONS, the default configuration allows read and update.
    # Here we require a 'create' permission which is not allowed.
    tool_perm = ToolPermission(
        type=Product.TRANSACTIONS,
        permissions=Permissions(create=True)
    )
    tool = Tool(name="Tool2", required_permissions=[tool_perm])
    assert config.is_tool_permissible(tool) is False


# Test allowed_tools returns only the tools that meet the permission requirements.
def test_allowed_tools():
    config = Configuration.all_tools()
    # Tool1 meets its requirement (credit_cards with create True)
    tool1 = Tool(
        name="Tool1",
        required_permissions=[
            ToolPermission(type=Product.CREDIT_CARDS, permissions=Permissions(read=True))
        ]
    )
    # Tool2 does not meet its requirement (transactions with create True, but not allowed)
    tool2 = Tool(
        name="Tool2",
        required_permissions=[
            ToolPermission(type=Product.TRANSACTIONS, permissions=Permissions(create=True))
        ]
    )
    # Tool3 has multiple requirements and should pass if all are met.
    tool3 = Tool(
        name="Tool3",
        required_permissions=[
            ToolPermission(type=Product.CREDIT_CARDS, permissions=Permissions(read=True)),
            ToolPermission(type=Product.VIRTUAL_CARDS, permissions=Permissions(update=True))
        ]
    )

    # Get allowed tools from configuration.
    allowed = config.allowed_tools([tool1, tool2, tool3])
    allowed_names = [tool.name for tool in allowed]

    # Tool1 and Tool3 should be allowed, Tool2 should not.
    assert "Tool1" in allowed_names
    assert "Tool3" in allowed_names
    assert "Tool2" not in allowed_names


if __name__ == "__main__":
    pytest.main()
