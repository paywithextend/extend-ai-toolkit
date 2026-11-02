import pytest

from extend_ai_toolkit.shared import Product, validate_tool_spec


@pytest.mark.parametrize("scope,product,action", [
    ("virtual_cards.read", Product.VIRTUAL_CARDS, "read"),
    ("expense_categories.create", Product.EXPENSE_CATEGORIES, "create"),
    ("receipt_attachments.send", Product.RECEIPT_ATTACHMENTS, "send")])
def test_supported_capabilities(scope, product, action):
    assert validate_tool_spec(scope) == (product, action)

@pytest.mark.parametrize("scope", ["credit_cards.create", "invalidformat", "nonexistent.read", "credit_cards.invalid"])
def test_unsupported_capabilities(scope):
    with pytest.raises(ValueError):
        validate_tool_spec(scope)
