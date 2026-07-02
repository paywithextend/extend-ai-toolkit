import inspect
import io
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Sequence, Union

from extend import ExtendClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pending_selections = {}


def _clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in params.items() if value is not None}


def _api_client_for(extend: ExtendClient) -> Any:
    api_client = getattr(extend, "_api_client", None)
    if api_client is None:
        raise AttributeError("Extend client does not expose a raw API client")
    return api_client


async def _raw_get(
        extend: ExtendClient,
        path: str,
        params: Optional[Dict[str, Any]] = None,
) -> Dict:
    return await _api_client_for(extend).get(path, _clean_params(params or {}))


async def _raw_post(
        extend: ExtendClient,
        path: str,
        data: Optional[Dict[str, Any]] = None,
) -> Dict:
    return await _api_client_for(extend).post(path, _clean_params(data or {}))


def _filter_graph_data(data: Any, include_graph_data: bool) -> Any:
    if include_graph_data:
        return data
    if isinstance(data, dict):
        graph_keys = {
            "graphData",
            "graph_data",
            "chartData",
            "chart_data",
            "series",
            "dataPoints",
            "data_points",
            "timeSeriesData",
            "time_series_data",
            "timeSeries",
            "time_series",
        }
        return {
            key: _filter_graph_data(value, include_graph_data)
            for key, value in data.items()
            if key not in graph_keys
        }
    if isinstance(data, list):
        return [_filter_graph_data(item, include_graph_data) for item in data]
    return data


# =========================
# Virtual Card Functions
# =========================

async def get_virtual_cards(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 10,
        status: Optional[str] = None,
        recipient: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """Get list of virtual cards

    Args:
        page (int): The page number for pagination. Defaults to 0.
        per_page (int): The number of virtual cards to return per page. Defaults to 10.
        status (Optional[str]): Filter cards by status (e.g., "ACTIVE", "CANCELLED", "PENDING", "EXPIRED", "CLOSED", "CONSUMED")
        recipient (Optional[str], optional): A filter by recipient identifier. Defaults to None.
        search_term (Optional[str], optional): A term to search virtual cards by. Defaults to None.
        sort_field (Optional[str]): Field to sort by "createdAt", "updatedAt", "balanceCents", "displayName", "type", or "status"
        sort_direction (Optional[str]): Direction to sort (ASC or DESC)
    """
    try:
        response = await extend.virtual_cards.get_virtual_cards(
            page=page,
            per_page=per_page,
            status=status.upper() if status else None,
            recipient=recipient,
            search_term=search_term,
            sort_field=sort_field,
            sort_direction=sort_direction
        )
        return response

    except Exception as e:
        logger.error("Error getting virtual cards: %s", e)
        raise Exception("Error getting virtual cards: %s", e)


async def get_virtual_card_detail(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Get details of a specific virtual card"""
    try:
        response = await extend.virtual_cards.get_virtual_card_detail(virtual_card_id)
        return response

    except Exception as e:
        logger.error("Error getting virtual card detail: %s", e)
        raise Exception(e)


async def close_virtual_card(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Close a specific virtual card"""
    try:
        response = await extend.virtual_cards.close_virtual_card(virtual_card_id)
        return response

    except Exception as e:
        logger.error("Error closing virtual card: %s", e)
        raise Exception("Error closing virtual card")


async def cancel_virtual_card(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Cancel a specific virtual card"""
    try:
        response = await extend.virtual_cards.cancel_virtual_card(virtual_card_id)
        return response

    except Exception as e:
        logger.error("Error canceling virtual card: %s", e)
        raise Exception("Error canceling virtual card")


# =========================
# Transaction Functions
# =========================

async def get_transactions(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 50,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        status: Optional[str] = None,
        statuses: Optional[Sequence[str]] = None,
        receipt_statuses: Optional[Sequence[str]] = None,
        expense_category_statuses: Optional[Sequence[str]] = None,
        missing_expense_categories: Optional[bool] = None,
        virtual_card_id: Optional[str] = None,
        min_amount_cents: Optional[int] = None,
        max_amount_cents: Optional[int] = None,
        receipt_missing: Optional[bool] = None,
        search_term: Optional[str] = None,
        sort_field: Optional[str] = None,
) -> Dict:
    """
    Get a list of recent transactions

    Args:
        page (int): pagination page number,
        per_page (int): number of transactions per page,
        from_date (Optional[str]): Start date (YYYY-MM-DD)
        to_date (Optional[str]): End date (YYYY-MM-DD)
        status (Optional[str]): Filter transactions by status (e.g., "PENDING", "CLEARED", "DECLINED")
        statuses (Optional[Sequence[str]]): Provide multiple status filters (2.0+)
        receipt_statuses (Optional[Sequence[str]]): Filter by receipt statuses when supported
        expense_category_statuses (Optional[Sequence[str]]): Filter by expense category statuses when supported
        missing_expense_categories (Optional[bool]): Filter transactions missing expense categorizations (2.0+)
        virtual_card_id (Optional[str]): Filter by specific virtual card
        min_amount_cents (Optional[int]): Minimum amount in cents
        max_amount_cents (Optional[int]): Maximum amount in cents
        receipt_missing (Optional[bool]): Filter transactions by whether they are missing a receipt
        search_term (Optional[str]): Filter transactions by search term (e.g., "Subscription")
        sort_field (Optional[str]): Field to sort by, with optional direction
                                    Use "recipientName", "merchantName", "amount", "date" for ASC
                                    Use "-recipientName", "-merchantName", "-amount", "-date" for DESC        

    """
    try:
        transaction_method = extend.transactions.get_transactions
        parameters = inspect.signature(transaction_method).parameters

        def _normalize(values: Optional[Union[Sequence[str], str]]) -> Optional[List[str]]:
            if values is None:
                return None
            if isinstance(values, str):
                iterable = [values]
            else:
                iterable = list(values)

            normalized = [value.upper() for value in iterable if value]
            return normalized or None

        normalized_statuses = _normalize(statuses)
        if normalized_statuses is None:
            normalized_statuses = _normalize(status)

        normalized_receipt_statuses = _normalize(receipt_statuses)
        normalized_expense_category_statuses = _normalize(expense_category_statuses)

        call_kwargs: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "from_date": from_date,
            "to_date": to_date,
            "virtual_card_id": virtual_card_id,
            "min_amount_cents": min_amount_cents,
            "max_amount_cents": max_amount_cents,
            "search_term": search_term,
            "sort_field": sort_field,
        }

        if normalized_statuses:
            if "statuses" in parameters:
                call_kwargs["statuses"] = normalized_statuses
            elif "status" in parameters:
                if len(normalized_statuses) > 1:
                    raise ValueError("Multiple statuses require paywithextend>=2.0.0. Current version only supports a single status parameter.")
                call_kwargs["status"] = normalized_statuses[0]

        if normalized_receipt_statuses and "receipt_statuses" in parameters:
            call_kwargs["receipt_statuses"] = normalized_receipt_statuses

        if normalized_expense_category_statuses and "expense_category_statuses" in parameters:
            call_kwargs["expense_category_statuses"] = normalized_expense_category_statuses

        if missing_expense_categories is not None and "missing_expense_categories" in parameters:
            call_kwargs["missing_expense_categories"] = missing_expense_categories

        if receipt_missing is not None and "receipt_missing" in parameters:
            call_kwargs["receipt_missing"] = receipt_missing

        supported_param_names = set(parameters.keys())
        filtered_kwargs = {
            key: value
            for key, value in call_kwargs.items()
            if key in supported_param_names and value is not None
        }

        response = await transaction_method(**filtered_kwargs)
        return response

    except Exception as e:
        logger.error("Error getting transactions: %s", e)
        raise Exception("Error getting transactions")


async def count_transactions(
        extend: ExtendClient,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        status: Optional[Sequence[str]] = None,
        virtual_card_id: Optional[str] = None,
        min_amount_cents: Optional[int] = None,
        max_amount_cents: Optional[int] = None,
        search_term: Optional[str] = None,
        expense_category_statuses: Optional[Sequence[str]] = None,
) -> Dict:
    """Count transactions matching report filters."""
    try:
        count_method = getattr(extend.transactions, "count_transactions", None)
        normalized_statuses = [value.upper() for value in status] if status else None
        normalized_expense_statuses = (
            [value.upper()[0] + value.lower()[1:] for value in expense_category_statuses]
            if expense_category_statuses
            else None
        )
        if count_method is not None:
            return await count_method(
                from_date=from_date,
                to_date=to_date,
                status=normalized_statuses,
                virtual_card_id=virtual_card_id,
                min_amount_cents=min_amount_cents,
                max_amount_cents=max_amount_cents,
                search_term=search_term,
                expense_category_statuses=normalized_expense_statuses,
            )

        return await _raw_get(
            extend,
            "/reports/transactions/count",
            {
                "since": from_date,
                "until": to_date,
                "statuses": normalized_statuses,
                "virtualCardId": virtual_card_id,
                "minClearingBillingCents": min_amount_cents,
                "maxClearingBillingCents": max_amount_cents,
                "search": search_term,
                "expenseCategoryStatuses": normalized_expense_statuses,
                "dateType": "Transaction",
            },
        )
    except Exception as e:
        logger.error("Error counting transactions: %s", e)
        raise Exception("Error counting transactions")


async def get_transaction_detail(extend: ExtendClient, transaction_id: str) -> Dict:
    """Get a transaction detail"""
    try:
        response = await extend.transactions.get_transaction(transaction_id)
        return response

    except Exception as e:
        logger.error("Error getting transaction detail: %s", e)
        raise Exception("Error getting transaction detail")


# =========================
# Credit Card Functions
# =========================

async def get_credit_cards(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 10,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """Get a list of credit cards"""
    try:
        credit_card_method = extend.credit_cards.get_credit_cards
        parameters = inspect.signature(credit_card_method).parameters
        if type is not None and "type" not in parameters:
            return await _raw_get(
                extend,
                "/creditcards",
                {
                    "page": page,
                    "count": per_page,
                    "statuses": status.upper() if status else None,
                    "types": type.upper(),
                    "search": search_term,
                    "sortDirection": sort_direction,
                },
            )

        call_kwargs = {
            "page": page,
            "per_page": per_page,
            "status": status.upper() if status else None,
            "type": type.upper() if type else None,
            "search_term": search_term,
            "sort_direction": sort_direction,
        }
        response = await credit_card_method(
            **{
                key: value
                for key, value in call_kwargs.items()
                if key in parameters
            }
        )
        return response

    except Exception as e:
        logger.error("Error getting credit cards: %s", e)
        raise Exception("Error getting credit cards")


async def get_credit_card_detail(extend: ExtendClient, credit_card_id: str) -> Dict:
    """Get details of a specific credit card"""
    try:
        response = await extend.virtual_cards.get_credit_card_detail(credit_card_id)
        return response

    except Exception as e:
        logger.error("Error getting credit card details: %s", e)
        raise Exception(e)


# =========================
# Expense Data Functions
# =========================

async def get_expense_categories(
        extend: ExtendClient,
        active: Optional[bool] = None,
        required: Optional[bool] = None,
        search: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """
    Get a list of expense categories.
    """
    try:
        response = await extend.expense_data.get_expense_categories(
            active=active,
            required=required,
            search=search,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )
        return response

    except Exception as e:
        logger.error("Error getting expense categories: %s", e)
        raise Exception("Error getting expense categories: %s", e)


async def get_expense_category(extend: ExtendClient, category_id: str) -> Dict:
    """
    Get detailed information about a specific expense category.
    """
    try:
        response = await extend.expense_data.get_expense_category(category_id)
        return response

    except Exception as e:
        logger.error("Error getting expense category: %s", e)
        raise Exception("Error getting expense category: %s", e)


async def get_expense_category_labels(
        extend: ExtendClient,
        category_id: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """
    Get a paginated list of expense category labels.
    """
    try:
        response = await extend.expense_data.get_expense_category_labels(
            category_id=category_id,
            page=page,
            per_page=per_page,
            active=active,
            search=search,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )
        return response

    except Exception as e:
        logger.error("Error getting expense category labels: %s", e)
        raise Exception("Error getting expense category labels: %s", e)


async def get_expense_category_label(
        extend: ExtendClient,
        category_id: str,
        label_id: str,
) -> Dict:
    """Get detailed information about a specific expense category label."""
    try:
        label_method = getattr(extend.expense_data, "get_expense_category_label", None)
        if label_method is not None:
            return await label_method(category_id=category_id, label_id=label_id)
        return await _raw_get(
            extend,
            f"/expensedata/categories/{category_id}/labels/{label_id}",
        )
    except Exception as e:
        logger.error("Error getting expense category label: %s", e)
        raise Exception("Error getting expense category label: %s", e)


async def create_expense_category(
        extend: ExtendClient,
        name: str,
        code: str,
        required: bool,
        active: Optional[bool] = None,
        free_text_allowed: Optional[bool] = None,
) -> Dict:
    """
    Create an expense category.
    """
    try:
        response = await extend.expense_data.create_expense_category(
            name=name,
            code=code,
            required=required,
            active=active,
            free_text_allowed=free_text_allowed,
        )
        return response

    except Exception as e:
        logger.error("Error creating expense category: %s", e)
        raise Exception("Error creating expense category: %s", e)


async def create_expense_category_label(
        extend: ExtendClient,
        category_id: str,
        name: str,
        code: str,
        active: bool = True
) -> Dict:
    """
    Create an expense category label.
    """
    try:
        response = await extend.expense_data.create_expense_category_label(
            category_id=category_id,
            name=name,
            code=code,
            active=active
        )
        return response

    except Exception as e:
        logger.error("Error creating expense category label: %s", e)
        raise Exception("Error creating expense category label: %s", e)


async def update_expense_category(
        extend: ExtendClient,
        category_id: str,
        name: Optional[str] = None,
        active: Optional[bool] = None,
        required: Optional[bool] = None,
        free_text_allowed: Optional[bool] = None,
) -> Dict:
    """
    Update an expense category.
    """
    try:
        response = await extend.expense_data.update_expense_category(
            category_id=category_id,
            name=name,
            active=active,
            required=required,
            free_text_allowed=free_text_allowed,
        )
        return response

    except Exception as e:
        logger.error("Error updating expense category: %s", e)
        raise Exception("Error updating expense category: %s", e)


async def update_expense_category_label(
        extend: ExtendClient,
        category_id: str,
        label_id: str,
        name: Optional[str] = None,
        active: Optional[bool] = None,
) -> Dict:
    """
    Update an expense category label.
    """
    try:
        response = await extend.expense_data.update_expense_category_label(
            category_id=category_id,
            label_id=label_id,
            name=name,
            active=active,
        )
        return response

    except Exception as e:
        logger.error("Error updating expense category label: %s", e)
        raise Exception("Error updating expense category label: %s", e)


async def propose_transaction_expense_data(
        extend: ExtendClient,
        transaction_id: str,
        data: Dict
) -> Dict:
    """
    Propose expense data changes for a transaction without applying them.

    Args:
        extend: The Extend client instance
        transaction_id: The unique identifier of the transaction
        data: A dictionary representing the expense data to update

    Returns:
        Dict: A confirmation request with token and expiration
    """
    # Fetch transaction to ensure it exists
    await extend.transactions.get_transaction(transaction_id)

    # Generate a unique confirmation token
    confirmation_token = str(uuid.uuid4())

    # Set expiration time (10 minutes from now)
    expiration_time = datetime.now() + timedelta(minutes=10)

    # Store the pending selection with its metadata
    pending_selections[confirmation_token] = {
        "transaction_id": transaction_id,
        "data": data,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiration_time.isoformat(),
        "status": "pending"
    }

    # Return the confirmation request
    return {
        "status": "pending_confirmation",
        "transaction_id": transaction_id,
        "confirmation_token": confirmation_token,
        "expires_at": expiration_time.isoformat(),
        "proposed_categories": [
            {"categoryId": category.get("categoryId", "Unknown"),
             "labelId": category.get("labelId", "None")}
            for category in data.get("expenseDetails", [])
        ]
    }


async def confirm_transaction_expense_data(
        extend: ExtendClient,
        confirmation_token: str
) -> Dict:
    """
    Confirm and apply previously proposed expense data changes.

    Args:
        extend: The Extend client instance
        confirmation_token: The unique token from the proposal step

    Returns:
        Dict: The updated transaction details
    """
    # Check if token exists
    if confirmation_token not in pending_selections:
        raise Exception("Invalid confirmation token")

    # Get the pending selection
    selection = pending_selections[confirmation_token]

    # Check if expired
    if datetime.now() > datetime.fromisoformat(selection["expires_at"]):
        # Clean up expired token
        del pending_selections[confirmation_token]
        raise Exception("Confirmation token has expired")

    # Apply the expense data update
    response = await extend.transactions.update_transaction_expense_data(
        selection["transaction_id"],
        selection["data"]
    )

    # Mark as confirmed and clean up
    selection["status"] = "confirmed"
    selection["confirmed_at"] = datetime.now().isoformat()

    # In a real implementation, you might want to keep the record for auditing
    # but for simplicity, we'll delete it here
    del pending_selections[confirmation_token]

    return response


async def update_transaction_expense_data(
        extend: ExtendClient,
        transaction_id: str,
        user_confirmed_data_values: bool,
        data: Dict
) -> Dict:
    """
    Internal function to update the expense data for a specific transaction.
    This should not be exposed directly to external callers.

    Args:
        extend: The Extend client instance
        transaction_id: The unique identifier of the transaction
        user_confirmed_data_values: Only true if the user has confirmed the specific values in the data argument
        data: A dictionary representing the expense data to update

    Returns:
        Dict: A dictionary containing the updated transaction details
    """
    try:
        if not user_confirmed_data_values:
            raise Exception("User has not confirmed the expense category or label values")
        response = await extend.transactions.update_transaction_expense_data(transaction_id, data)
        return response
    except Exception as e:
        raise Exception(f"Error updating transaction expense data: {str(e)}")


# =========================
# Automation Functions
# =========================

async def trigger_async_predict_expense_data_for_transactions(
        extend: ExtendClient,
        transaction_ids: List[str],
) -> Dict:
    """Trigger async expense-data prediction for transactions."""
    try:
        automation = getattr(extend, "automation", None)
        trigger = (
            getattr(
                automation,
                "trigger_async_predict_expense_data_for_transactions",
                None,
            )
            if automation is not None
            else None
        )
        if trigger is not None:
            return await trigger(transaction_ids=transaction_ids)
        return await _raw_post(
            extend,
            "/automations/transactions/enrichment",
            {"transactionIds": transaction_ids},
        )
    except Exception as e:
        logger.error("Error triggering expense-data prediction: %s", e)
        raise Exception("Error triggering expense-data prediction")


# =========================
# Organization And User Functions
# =========================

async def get_organizations(extend: ExtendClient) -> Dict:
    """Get organizations available to the current user."""
    try:
        organizations = getattr(extend, "organizations", None)
        if organizations is not None and hasattr(organizations, "list"):
            return await organizations.list()
        return await _raw_get(extend, "/organizations/")
    except Exception as e:
        logger.error("Error getting organizations: %s", e)
        raise Exception("Error getting organizations")


async def get_organization_members(
        extend: ExtendClient,
        organization_id: str,
        page: Optional[int] = None,
        count: Optional[int] = None,
        search: Optional[str] = None,
        organization_role: Optional[str] = None,
        organization_roles: Optional[List[str]] = None,
        show_deactivated_users: Optional[bool] = True,
        render_metrics: Optional[bool] = False,
) -> Dict:
    """Get members for an organization."""
    try:
        organizations = getattr(extend, "organizations", None)
        if organizations is not None and hasattr(organizations, "get_members"):
            return await organizations.get_members(
                organization_id=organization_id,
                page=page,
                count=count,
                search=search,
                organization_role=organization_role,
                organization_roles=organization_roles,
                show_deactivated_users=show_deactivated_users,
                render_metrics=render_metrics,
            )
        return await _raw_get(
            extend,
            f"/organizations/{organization_id}/members",
            {
                "page": page,
                "count": count,
                "search": search,
                "organizationRole": organization_role,
                "organizationRoles": organization_roles,
                "showDeactivatedUsers": show_deactivated_users,
                "renderMetrics": render_metrics,
            },
        )
    except Exception as e:
        logger.error("Error getting organization members: %s", e)
        raise Exception("Error getting organization members")


async def get_user_details(extend: ExtendClient, user_id: str) -> Dict:
    """Get a user's profile details."""
    try:
        users = getattr(extend, "users", None)
        if users is not None and hasattr(users, "get_user"):
            return await users.get_user(user_id=user_id)
        return await _raw_get(extend, f"/users/{user_id}")
    except Exception as e:
        logger.error("Error getting user details: %s", e)
        raise Exception("Error getting user details")


async def get_current_user(extend: ExtendClient) -> Dict:
    """Get the authenticated user's profile."""
    try:
        users = getattr(extend, "users", None)
        if users is not None and hasattr(users, "get_me"):
            return await users.get_me()
        return await _raw_get(extend, "/users/me")
    except Exception as e:
        logger.error("Error getting current user: %s", e)
        raise Exception("Error getting current user")


async def get_expense_policy(extend: ExtendClient, organization_id: str) -> Dict:
    """Get raw expense policy text for an organization."""
    try:
        expense_policy = getattr(extend, "expense_policy", None)
        if expense_policy is not None and hasattr(expense_policy, "get_expense_policy"):
            return await expense_policy.get_expense_policy(organization_id=organization_id)
        return await _raw_get(
            extend,
            f"/organizations/{organization_id}/expensepolicy/rawtext",
        )
    except Exception as e:
        logger.error("Error getting expense policy: %s", e)
        raise Exception("Error getting expense policy")


# =========================
# Insights Functions
# =========================

def _insights_params(
        *,
        since: Optional[str] = None,
        until: Optional[str] = None,
        expense_category_id: Optional[str] = None,
        expense_label_id: Optional[str] = None,
        merchant_category: Optional[str] = None,
        credit_card_id: Optional[List[str]] = None,
        virtual_card_id: Optional[List[str]] = None,
        recipient_id: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
        comparison_type: Optional[str] = None,
        interval: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "since": since,
        "until": until,
        "expenseCategoryId": expense_category_id,
        "expenseLabelId": expense_label_id,
        "merchantCategory": merchant_category,
        "creditCardId": credit_card_id,
        "virtualCardId": virtual_card_id,
        "recipientId": recipient_id,
        "departments": departments,
        "comparisonType": comparison_type,
        "interval": interval,
    }


async def _call_insights(
        extend: ExtendClient,
        method_name: str,
        path: str,
        include_graph_data: bool,
        **params: Any,
) -> Dict:
    insights = getattr(extend, "insights", None)
    method = getattr(insights, method_name, None) if insights is not None else None
    if method is not None:
        result = await method(include_graph_data=include_graph_data, **params)
    else:
        result = await _raw_get(
            extend,
            f"/clickhouse/insights/{path}",
            _insights_params(**params),
        )
    return _filter_graph_data(result, include_graph_data)


async def get_spend_by_expense_category(
        extend: ExtendClient,
        since: Optional[str] = None,
        until: Optional[str] = None,
        expense_category_id: Optional[str] = None,
        expense_label_id: Optional[str] = None,
        merchant_category: Optional[str] = None,
        credit_card_id: Optional[List[str]] = None,
        virtual_card_id: Optional[List[str]] = None,
        recipient_id: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
        include_graph_data: bool = True,
) -> Dict:
    return await _call_insights(
        extend,
        "get_spend_by_expense_category_label",
        "spendbyexpensecategorylabel",
        include_graph_data,
        since=since,
        until=until,
        expense_category_id=expense_category_id,
        expense_label_id=expense_label_id,
        merchant_category=merchant_category,
        credit_card_id=credit_card_id,
        virtual_card_id=virtual_card_id,
        recipient_id=recipient_id,
        departments=departments,
    )


async def get_spend_by_merchant_category(
        extend: ExtendClient,
        since: Optional[str] = None,
        until: Optional[str] = None,
        expense_category_id: Optional[str] = None,
        expense_label_id: Optional[str] = None,
        merchant_category: Optional[str] = None,
        credit_card_id: Optional[List[str]] = None,
        virtual_card_id: Optional[List[str]] = None,
        recipient_id: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
        include_graph_data: bool = True,
) -> Dict:
    return await _call_insights(
        extend,
        "get_spend_by_merchant_category",
        "spendbymerchantcategory",
        include_graph_data,
        since=since,
        until=until,
        expense_category_id=expense_category_id,
        expense_label_id=expense_label_id,
        merchant_category=merchant_category,
        credit_card_id=credit_card_id,
        virtual_card_id=virtual_card_id,
        recipient_id=recipient_id,
        departments=departments,
    )


async def get_spend_over_time_by_expense(
        extend: ExtendClient,
        since: Optional[str] = None,
        until: Optional[str] = None,
        expense_category_id: Optional[str] = None,
        expense_label_id: Optional[str] = None,
        merchant_category: Optional[str] = None,
        credit_card_id: Optional[List[str]] = None,
        virtual_card_id: Optional[List[str]] = None,
        recipient_id: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
        comparison_type: str = "MOM",
        interval: str = "DAY",
        include_graph_data: bool = True,
) -> Dict:
    return await _call_insights(
        extend,
        "get_spend_over_time_for_expense_category_label",
        "spendovertimeexpensecategorylabel",
        include_graph_data,
        since=since,
        until=until,
        expense_category_id=expense_category_id,
        expense_label_id=expense_label_id,
        merchant_category=merchant_category,
        credit_card_id=credit_card_id,
        virtual_card_id=virtual_card_id,
        recipient_id=recipient_id,
        departments=departments,
        comparison_type=comparison_type,
        interval=interval,
    )


async def get_spend_over_time_by_merchant(
        extend: ExtendClient,
        since: Optional[str] = None,
        until: Optional[str] = None,
        expense_category_id: Optional[str] = None,
        expense_label_id: Optional[str] = None,
        merchant_category: Optional[str] = None,
        credit_card_id: Optional[List[str]] = None,
        virtual_card_id: Optional[List[str]] = None,
        recipient_id: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
        comparison_type: str = "MOM",
        interval: str = "DAY",
        include_graph_data: bool = True,
) -> Dict:
    return await _call_insights(
        extend,
        "get_spend_over_time_for_merchant_category",
        "spendovertimemerchantcategory",
        include_graph_data,
        since=since,
        until=until,
        expense_category_id=expense_category_id,
        expense_label_id=expense_label_id,
        merchant_category=merchant_category,
        credit_card_id=credit_card_id,
        virtual_card_id=virtual_card_id,
        recipient_id=recipient_id,
        departments=departments,
        comparison_type=comparison_type,
        interval=interval,
    )


async def get_spend_vs_prior_period(
        extend: ExtendClient,
        since: Optional[str] = None,
        until: Optional[str] = None,
        expense_category_id: Optional[str] = None,
        expense_label_id: Optional[str] = None,
        merchant_category: Optional[str] = None,
        credit_card_id: Optional[List[str]] = None,
        virtual_card_id: Optional[List[str]] = None,
        recipient_id: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
        comparison_type: str = "MOM",
        include_graph_data: bool = True,
) -> Dict:
    return await _call_insights(
        extend,
        "get_spend_vs_prior_period",
        "spendvspriorperiod",
        include_graph_data,
        since=since,
        until=until,
        expense_category_id=expense_category_id,
        expense_label_id=expense_label_id,
        merchant_category=merchant_category,
        credit_card_id=credit_card_id,
        virtual_card_id=virtual_card_id,
        recipient_id=recipient_id,
        departments=departments,
        comparison_type=comparison_type,
    )


# =========================
# Receipt Attachment Functions
# =========================

async def create_receipt_attachment(
        extend: ExtendClient,
        transaction_id: str,
        file_path: str,
) -> Dict:
    """
    Create a receipt attachment by uploading a file via multipart form data.

    Args:
        extend: The Extend client instance
        transaction_id (str): The unique identifier of the transaction to attach the receipt to.
        file_path (str): A file path for the receipt image.

    Returns:
        Dict: A dictionary representing the receipt attachment details, including:
                - id: Unique identifier of the receipt attachment.
                - transactionId: The associated transaction ID.
                - contentType: The MIME type of the uploaded file.
                - urls: A dictionary with URLs for the original image, main image, and thumbnail.
                - createdAt: Timestamp when the receipt attachment was created.
                - uploadType: A string describing the type of upload (e.g., "TRANSACTION", "VIRTUAL_CARD").
    """
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_obj = io.BytesIO(file_content)

            # Get the filename and determine the MIME type
            filename = os.path.basename(file_path)
            mime_type = None

            # Set the MIME type based on file extension
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                mime_type = 'image/jpeg'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif filename.lower().endswith('.bmp'):
                mime_type = 'image/bmp'
            elif filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                mime_type = 'image/tiff'
            elif filename.lower().endswith('.heic'):
                mime_type = 'image/heic'
            elif filename.lower().endswith('.pdf'):
                mime_type = 'application/pdf'
            else:
                raise ValueError(f"Unsupported file type: {filename}")

            file_obj = io.BytesIO(file_content)
            file_obj.name = filename
            file_obj.content_type = mime_type

            response = await extend.receipt_attachments.create_receipt_attachment(
                transaction_id=transaction_id,
                file=file_obj
            )
            return response


    except Exception as e:
        logger.error("Error creating receipt attachment: %s", e)
        raise Exception("Error creating receipt attachment: %s", e)


# =========================
# Receipt Capture Functions
# =========================

async def automatch_receipts(
        extend: ExtendClient,
        receipt_attachment_ids: List[str],
) -> Dict:
    """
    Initiates an asynchronous bulk receipt automatch job.

    This method triggers an asynchronous job on the server that processes the provided receipt attachment IDs.
    The operation is non-blocking: it immediately returns a job ID and preliminary details,
    while the matching process is performed in the background.

    Args:
        receipt_attachment_ids (List[str]): A list of receipt attachment IDs to be automatched.

    Returns:
        Dict: A dictionary representing the Bulk Receipt Automatch Response.
    """
    try:
        response = await extend.receipt_capture.automatch_receipts(
            receipt_attachment_ids=receipt_attachment_ids
        )
        return response
    except Exception as e:
        logger.error("Error initiating receipt automatch: %s", e)
        raise Exception("Error initiating receipt automatch: %s", e)


async def get_automatch_status(
        extend: ExtendClient,
        job_id: str,
) -> Dict:
    """
    Retrieves the status of a bulk receipt capture automatch job.

    Args:
        job_id (str): The ID of the automatch job whose status is to be retrieved.

    Returns:
        Dict: A dictionary representing the current Bulk Receipt Automatch Response.
    """
    try:
        response = await extend.receipt_capture.get_automatch_status(job_id=job_id)
        return response
    except Exception as e:
        logger.error("Error getting automatch status: %s", e)
        raise Exception("Error getting automatch status: %s", e)


async def send_receipt_reminder(
        extend: ExtendClient,
        transaction_id: str,
) -> Dict:
    """
    Send a transaction-specific receipt reminder.

    Args:
        extend: The Extend client instance
        transaction_id (str): The unique identifier of the transaction.

    Returns:
        Dict: Response from the API indicating the reminder was sent successfully.
    """
    try:
        response = await extend.transactions.send_receipt_reminder(transaction_id)
        return response
    except Exception as e:
        logger.error("Error sending receipt reminder: %s", e)
        raise Exception(f"Error sending receipt reminder: {e}") from e


# Optional: Cleanup function to remove expired selections
async def cleanup_pending_selections():
    """Remove all expired selection tokens"""
    now = datetime.now()
    expired_tokens = [
        token for token, selection in pending_selections.items()
        if now > datetime.fromisoformat(selection["expires_at"])
    ]

    for token in expired_tokens:
        del pending_selections[token]
