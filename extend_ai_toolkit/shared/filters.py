"""Explicit mappings to the transaction report request contract."""

import re
from datetime import date

TRANSACTION_STATUSES = {
    "PENDING",
    "CLEARED",
    "DECLINED",
    "NO_MATCH",
    "AVS_PASS",
    "AVS_FAIL",
    "AUTH_REVERSAL",
}
SORT_FIELDS = {
    prefix + name
    for prefix in ("", "-")
    for name in ("recipientName", "merchantName", "virtualCard", "vcnReference", "amount", "date")
}


def _statuses(values, valid, title=False):
    if values is None:
        return None
    values = [values] if isinstance(values, str) else list(values)
    if not values:
        raise ValueError("Empty status filters are ambiguous")
    normalized = [value.title() if title else value.upper() for value in values]
    if set(normalized) - valid:
        raise ValueError("Unsupported filter status")
    return list(dict.fromkeys(normalized))


def transaction_query(
    *,
    from_date=None,
    to_date=None,
    status=None,
    statuses=None,
    receipt_statuses=None,
    expense_category_statuses=None,
    missing_expense_categories=None,
    virtual_card_id=None,
    min_amount_cents=None,
    max_amount_cents=None,
    receipt_missing=None,
    search_term=None,
    sort_field=None,
):
    if status is not None and statuses is not None:
        raise ValueError("Choose status or statuses, not both")
    for value in (from_date, to_date):
        if value is not None:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError("Dates must use YYYY-MM-DD")
            date.fromisoformat(value)
    if from_date and to_date and from_date > to_date:
        raise ValueError("from_date must not exceed to_date")
    if (
        min_amount_cents is not None
        and max_amount_cents is not None
        and min_amount_cents > max_amount_cents
    ):
        raise ValueError("Minimum amount must not exceed maximum")
    if sort_field is not None and sort_field not in SORT_FIELDS:
        raise ValueError("Unsupported transaction sort")
    if receipt_missing is not None and receipt_statuses is not None:
        raise ValueError("Choose receipt_missing or receipt_statuses")
    if missing_expense_categories is not None and expense_category_statuses is not None:
        raise ValueError("Choose missing_expense_categories or expense_category_statuses")
    if receipt_missing is not None:
        receipt_statuses = ["Missing" if receipt_missing else "Attached"]
    if missing_expense_categories is not None:
        expense_category_statuses = ["Missing" if missing_expense_categories else "Attached"]
    values = {
        "since": from_date,
        "until": to_date,
        "dateType": "Transaction",
        "status": _statuses(status if status is not None else statuses, TRANSACTION_STATUSES),
        "receiptStatus": _statuses(receipt_statuses, {"Missing", "Attached"}, title=True),
        "expenseCategoryStatuses": _statuses(
            expense_category_statuses, {"Missing", "Attached"}, title=True
        ),
        "virtualCardId": virtual_card_id,
        "minClearingBillingCents": min_amount_cents,
        "maxClearingBillingCents": max_amount_cents,
        "search": search_term,
        "sort": sort_field,
    }
    return {key: value for key, value in values.items() if value is not None}
