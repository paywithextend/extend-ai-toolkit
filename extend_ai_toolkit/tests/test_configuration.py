# test_configuration.py

from dataclasses import dataclass
from typing import List

import pytest

from extend_ai_toolkit.shared import (
    Configuration,
    Product,
    Actions, 
    tools,
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
    config = Configuration.all_tools()
    assert config.scope is not None

    # Build a mapping of product -> set of expected actions from tools
    expected_scopes = {}

    for tool in tools:
        for scope in tool.required_scope:
            product = scope.type
            if product not in expected_scopes:
                expected_scopes[product] = set()
            expected_scopes[product].update({k for k, v in scope.actions.items() if v})

    # Validate the number of configured scopes
    assert len(config.scope) == len(expected_scopes)

    # Validate each product and its actions are in the config
    for pp in config.scope:
        expected_actions = expected_scopes.get(pp.type)
        assert expected_actions is not None, f"Unexpected product in config: {pp.type}"
        for action in expected_actions:
            assert pp.actions.get(action) is True, f"{pp.type}.{action} should be True"


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
    # Tool3 for expense categories; requires read access.
    tool3 = Tool(
        name="Tool3",
        required_scope=[
            ToolScope(
                product_type=Product.EXPENSE_CATEGORIES,
                actions=Actions(read=True)
            )
        ]
    )

    # Get allowed tools from configuration.
    allowed = config.allowed_tools([tool1, tool2, tool3])
    allowed_names = [tool.name for tool in allowed]

    # Tool1 and Tool3 should be allowed; Tool2 should not.
    assert "Tool1" in allowed_names
    assert "Tool3" in allowed_names
    assert "Tool2" not in allowed_names


if __name__ == "__main__":
    pytest.main()
