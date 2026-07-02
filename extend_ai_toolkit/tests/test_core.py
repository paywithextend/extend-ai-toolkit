from dataclasses import dataclass

import pytest

from extend_ai_toolkit.core import execute_tool, list_tool_specs
from extend_ai_toolkit.shared import Configuration


def test_list_tool_specs_returns_stable_structured_metadata():
    specs = list_tool_specs(
        Configuration.from_tool_str("transactions.read,transactions.update")
    )
    by_name = {spec.name: spec for spec in specs}

    assert set(by_name) >= {"get_transactions", "update_transaction_expense_data"}

    transactions = by_name["get_transactions"]
    assert transactions.ref == "extend.transactions.get_transactions.v1"
    assert transactions.product == "transactions"
    assert transactions.actions == ("read",)
    assert transactions.side_effect_class == "read_only"
    assert transactions.required_scopes == (
        {"product": "transactions", "actions": ("read",)},
    )
    assert "properties" in transactions.input_schema

    update = by_name["update_transaction_expense_data"]
    assert update.ref == "extend.transactions.update_transaction_expense_data.v1"
    assert update.product == "transactions"
    assert update.actions == ("read", "update")
    assert update.side_effect_class == "external_write"
    assert update.required_scopes == (
        {"product": "transactions", "actions": ("read", "update")},
    )


def test_list_tool_specs_allows_empty_custom_catalog():
    assert list_tool_specs(catalog=[]) == []


@pytest.mark.asyncio
async def test_execute_tool_validates_arguments_and_returns_raw_structured_data():
    @dataclass
    class Transactions:
        async def get_transactions(
            self,
            page=None,
            per_page=None,
            from_date=None,
            to_date=None,
            status=None,
            virtual_card_id=None,
            min_amount_cents=None,
            max_amount_cents=None,
            search_term=None,
            sort_field=None,
        ):
            return {
                "report": {"transactions": [{"id": "txn_123"}]},
                "kwargs": {
                    "page": page,
                    "per_page": per_page,
                    "from_date": from_date,
                    "to_date": to_date,
                    "status": status,
                    "virtual_card_id": virtual_card_id,
                    "min_amount_cents": min_amount_cents,
                    "max_amount_cents": max_amount_cents,
                    "search_term": search_term,
                    "sort_field": sort_field,
                },
            }

    @dataclass
    class Extend:
        transactions: Transactions

    result = await execute_tool(
        Extend(Transactions()),
        "get_transactions",
        {"page": 1, "per_page": 10, "status": "cleared"},
    )

    assert result == {
        "report": {"transactions": [{"id": "txn_123"}]},
        "kwargs": {
            "page": 1,
            "per_page": 10,
            "from_date": None,
            "to_date": None,
            "status": "CLEARED",
            "virtual_card_id": None,
            "min_amount_cents": None,
            "max_amount_cents": None,
            "search_term": None,
            "sort_field": None,
        },
    }


@pytest.mark.asyncio
async def test_execute_tool_rejects_unknown_tool_names():
    with pytest.raises(ValueError, match="Unknown Extend tool"):
        await execute_tool(object(), "missing_tool", {})


@pytest.mark.asyncio
async def test_execute_tool_allows_empty_custom_catalog():
    with pytest.raises(ValueError, match="Unknown Extend tool"):
        await execute_tool(object(), "get_transactions", {}, catalog=[])
