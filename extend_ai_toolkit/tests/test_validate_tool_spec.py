# test_validate_tool_spec.py

import pytest

from extend_ai_toolkit.shared import validate_tool_spec, Product, Permissions


def test_validate_tool_spec_valid():
    # Valid input: "virtual_cards.read"
    product, permission = validate_tool_spec("virtual_cards.read")
    assert product == Product.VIRTUAL_CARDS
    assert permission == "read"

    # Another valid input: "credit_cards.create"
    product, permission = validate_tool_spec("credit_cards.create")
    assert product == Product.CREDIT_CARDS
    assert permission == "create"


def test_validate_tool_spec_invalid_format():
    # Missing dot should raise a ValueError.
    with pytest.raises(ValueError) as exc_info:
        validate_tool_spec("invalidformat")
    assert "must be in the format 'product.permission'" in str(exc_info.value)


def test_validate_tool_spec_invalid_product():
    # Invalid product should raise a ValueError.
    with pytest.raises(ValueError) as exc_info:
        validate_tool_spec("nonexistent.read")
    # Check if error message mentions valid products.
    assert "Invalid product" in str(exc_info.value)


def test_validate_tool_spec_invalid_permission():
    # Invalid permission should raise a ValueError.
    with pytest.raises(ValueError) as exc_info:
        validate_tool_spec("credit_cards.invalid")
    # Check if error message mentions valid permissions.
    valid_permissions = list(Permissions.__annotations__.keys())
    assert "Invalid permission" in str(exc_info.value)
    for perm in valid_permissions:
        assert perm in str(exc_info.value) or str(valid_permissions) in str(exc_info.value)
