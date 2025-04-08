import pytest

from extend_ai_toolkit.shared import validate_tool_spec, Product, Actions


def test_validate_tool_spec_valid():
    # Valid input: "virtual_cards.read"
    product, action = validate_tool_spec("virtual_cards.read")
    assert product == Product.VIRTUAL_CARDS
    assert action == "read"

    # Another valid input: "credit_cards.create"
    product, action = validate_tool_spec("credit_cards.create")
    assert product == Product.CREDIT_CARDS
    assert action == "create"

    # Additional valid input: "expense_categories.read"
    product, action = validate_tool_spec("expense_categories.read")
    assert product == Product.EXPENSE_CATEGORIES
    assert action == "read"


def test_validate_tool_spec_invalid_format():
    # Missing dot should raise a ValueError.
    with pytest.raises(ValueError) as exc_info:
        validate_tool_spec("invalidformat")
    assert "must be in the format 'product.action'" in str(exc_info.value)


def test_validate_tool_spec_invalid_product():
    # Invalid product should raise a ValueError.
    with pytest.raises(ValueError) as exc_info:
        validate_tool_spec("nonexistent.read")
    # Check if error message mentions valid products.
    assert "Invalid product" in str(exc_info.value)


def test_validate_tool_spec_invalid_actions():
    # Invalid action should raise a ValueError.
    with pytest.raises(ValueError) as exc_info:
        validate_tool_spec("credit_cards.invalid")
    # Check if error message mentions valid action.
    valid_actions = list(Actions.__annotations__.keys())
    assert "Invalid action" in str(exc_info.value)
    for perm in valid_actions:
        assert perm in str(exc_info.value) or str(valid_actions) in str(exc_info.value)
