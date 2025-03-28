# test_configuration.py

from dataclasses import dataclass
from typing import List

import pytest

from extend_ai_toolkit.shared import (
    Configuration,
    Product,
    Actions,
    Scope,
)


# Dummy implementations for testing:
class ToolScope:
    """
    Represents a scope requirement for a tool.
    """

    def __init__(self, product_type: Product, actions: Actions):
        self.type = product_type
        self.actions = actions


@dataclass
class Tool:
    """
    A dummy Tool for testing. It has a name and a list of required scopes.
    """
    name: str
    required_scope: List[ToolScope]


# Test that the classmethod all_tools creates a configuration with the expected defaults.
def test_all_tools_configuration():
    config = Configuration.all_tools(org_id="test_org_id")
    assert config.scope is not None
    assert config.org_id == "test_org_id"
    assert len(config.scope) == 4
    # Check that each default scope is set as expected.
    for pp in config.scope:
        if pp.type == Product.CREDIT_CARDS:
            assert pp.actions.get("read") is True
        elif pp.type == Product.VIRTUAL_CARDS:
            assert pp.actions.get("read") is True
            assert pp.actions.get("create") is True
            assert pp.actions.get("update") is True
        elif pp.type == Product.TRANSACTIONS:
            assert pp.actions.get("read") is True
        elif pp.type == Product.EXPENSE_CATEGORIES:
            assert pp.actions.get("read") is True
            assert pp.actions.get("create") is True
            assert pp.actions.get("update") is True
        else:
            raise ValueError(f"Unexpected product type in configuration: {pp.type}")


# Test is_tool_in_scope returns True when tool requirements match configuration.
def test_is_tool_in_scope_success():
    config = Configuration.all_tools()
    # Create a tool that requires credit_cards.read scope.
    tool_perm = ToolScope(
        product_type=Product.CREDIT_CARDS,
        actions=Actions(read=True)
    )
    tool = Tool(name="Tool1", required_scope=[tool_perm])
    # Assuming the default configuration for CREDIT_CARDS has read True.
    assert config.is_tool_in_scope(tool) is True


def test_is_tool_in_scope_with_limited_scope_success():
    config = Configuration(scope=[Scope(Product.VIRTUAL_CARDS, actions=Actions(create=True))])
    # Create a tool that requires virtual_cards.create scope.
    tool_perm = ToolScope(
        product_type=Product.VIRTUAL_CARDS,
        actions=Actions(create=True)
    )
    tool = Tool(name="Tool1", required_scope=[tool_perm])
    assert config.is_tool_in_scope(tool) is True


# Test is_tool_in_scope returns False when a required scope is missing.
def test_is_tool_in_scope_failure_missing_scope_action():
    config = Configuration.all_tools()
    # For TRANSACTIONS, the default configuration allows read.
    # Here we require a 'create' action which is not allowed.
    tool_perm = ToolScope(
        product_type=Product.TRANSACTIONS,
        actions=Actions(create=True)
    )
    tool = Tool(name="Tool2", required_scope=[tool_perm])
    assert config.is_tool_in_scope(tool) is False


# Test allowed_tools returns only the tools that meet the scope requirements.
def test_allowed_tools():
    config = Configuration.all_tools()
    # Tool1 meets its requirement (credit_cards with read True)
    tool1 = Tool(
        name="Tool1",
        required_scope=[
            ToolScope(
                product_type=Product.CREDIT_CARDS,
                actions=Actions(read=True)
            )
        ]
    )
    # Tool2 does not meet its requirement (transactions with create True, but not allowed)
    tool2 = Tool(
        name="Tool2",
        required_scope=[
            ToolScope(
                product_type=Product.TRANSACTIONS,
                actions=Actions(create=True)
            )
        ]
    )
    # Tool3 has multiple requirements and should pass if all are met.
    tool3 = Tool(
        name="Tool3",
        required_scope=[
            ToolScope(
                product_type=Product.CREDIT_CARDS,
                actions=Actions(read=True)
            ),
            ToolScope(
                product_type=Product.VIRTUAL_CARDS,
                actions=Actions(update=True)
            )
        ]
    )
    # Tool4 for expense categories; requires read access.
    tool4 = Tool(
        name="Tool4",
        required_scope=[
            ToolScope(
                product_type=Product.EXPENSE_CATEGORIES,
                actions=Actions(read=True)
            )
        ]
    )

    # Get allowed tools from configuration.
    allowed = config.allowed_tools([tool1, tool2, tool3, tool4])
    allowed_names = [tool.name for tool in allowed]

    # Tool1, Tool3, and Tool4 should be allowed; Tool2 should not.
    assert "Tool1" in allowed_names
    assert "Tool3" in allowed_names
    assert "Tool4" in allowed_names
    assert "Tool2" not in allowed_names


if __name__ == "__main__":
    pytest.main()
