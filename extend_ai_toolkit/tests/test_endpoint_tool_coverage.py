import pytest

from extend_ai_toolkit.core import execute_tool, list_tool_specs
from extend_ai_toolkit.shared import Configuration


def test_catalog_exposes_current_service_endpoint_tools():
    tool_names = {spec.name for spec in list_tool_specs()}

    assert {
        "count_transactions",
        "get_expense_category_label",
        "get_organizations",
        "get_organization_members",
        "get_user_details",
        "get_expense_policy",
    }.issubset(tool_names)

    assert {
        "trigger_async_predict_expense_data_for_transactions",
        "get_current_user",
        "get_spend_by_expense_category",
        "get_spend_by_merchant_category",
        "get_spend_over_time_by_expense",
        "get_spend_over_time_by_merchant",
        "get_spend_vs_prior_period",
    }.isdisjoint(tool_names)


def test_new_endpoint_families_are_available_through_scopes():
    scoped_names = {
        spec.name
        for spec in list_tool_specs(
            Configuration.from_tool_str(
                ",".join(
                    [
                        "transactions.read",
                        "transactions.update",
                        "expense_categories.read",
                        "organizations.read",
                        "users.read",
                        "expense_policies.read",
                    ]
                )
            )
        )
    }

    assert "count_transactions" in scoped_names
    assert "get_expense_policy" in scoped_names
    assert "get_user_details" in scoped_names


def test_transaction_and_card_schemas_cover_current_filter_shapes():
    specs = {spec.name: spec for spec in list_tool_specs()}

    transaction_properties = specs["get_transactions"].input_schema["properties"]
    assert "receipt_statuses" in transaction_properties
    assert "expense_category_statuses" in transaction_properties
    assert "missing_expense_categories" in transaction_properties

    status_items = transaction_properties["status"]["anyOf"][0]["items"]
    assert status_items["type"] == "string"

    credit_card_properties = specs["get_credit_cards"].input_schema["properties"]
    assert "type" in credit_card_properties


@pytest.mark.asyncio
async def test_execute_tool_supports_raw_get_endpoints_missing_from_sdk_resources():
    class APIClient:
        def __init__(self):
            self.calls = []

        async def get(self, url, params=None):
            self.calls.append(("get", url, params))
            return {"user": {"id": "u_123"}}

    class Extend:
        def __init__(self):
            self._api_client = APIClient()

    extend = Extend()

    result = await execute_tool(extend, "get_user_details", {"user_id": "u_123"})

    assert result == {"user": {"id": "u_123"}}
    assert extend._api_client.calls == [("get", "/users/u_123", {})]
