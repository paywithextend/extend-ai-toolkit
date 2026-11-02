from typing import Dict, List, Optional

from extend import ExtendClient


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
    response = await extend.virtual_cards.get_virtual_cards(
        page=page,
        per_page=per_page,
        status=status.upper() if status else None,
        recipient=recipient,
        search_term=search_term,
        sort_field=sort_field,
        sort_direction=sort_direction,
    )
    return response


async def get_virtual_card_detail(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Get details of a specific virtual card"""
    response = await extend.virtual_cards.get_virtual_card_detail(virtual_card_id)
    return response


async def close_virtual_card(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Close a specific virtual card"""
    response = await extend.virtual_cards.close_virtual_card(virtual_card_id)
    return response


async def cancel_virtual_card(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Cancel a specific virtual card"""
    response = await extend.virtual_cards.cancel_virtual_card(virtual_card_id)
    return response


async def get_transactions(
    extend: ExtendClient, page: int = 1, per_page: int = 50, **filters
) -> Dict:
    """Get one report page. Full-page totals are sentinel values, not exact counts."""
    response = await extend.transactions.get_transactions(page=page, per_page=per_page, **filters)
    report = response.get("report", {})
    rows = report.get("transactions", [])
    actual_page = report.get("page", page)
    actual_size = report.get("perPage", per_page)
    full = len(rows) >= actual_size
    return {
        **response,
        "paginationInfo": {
            "page": actual_page,
            "perPage": actual_size,
            "countExact": not full and (actual_page == 1 or bool(rows)),
            "mayHaveMore": full,
            "nextPage": actual_page + 1 if full else None,
        },
    }


async def count_transactions(extend: ExtendClient, **filters) -> Dict:
    """Request an exact count explicitly, using the same filters as report listing."""
    return await extend.transactions.count_transactions(**filters)


async def get_transaction_detail(extend: ExtendClient, transaction_id: str) -> Dict:
    """Get a transaction detail"""
    response = await extend.transactions.get_transaction(transaction_id)
    return response


async def get_credit_cards(
    extend: ExtendClient,
    page: int = 0,
    per_page: int = 10,
    status: str | None = None,
    type: str | None = None,
    search_term: str | None = None,
    sort_direction: str | None = None,
) -> Dict:
    """List credit cards with the backend's singular type parameter."""
    return await extend.credit_cards.get_credit_cards(
        page=page,
        per_page=per_page,
        status=status,
        type=type,
        search_term=search_term,
        sort_direction=sort_direction,
    )


async def get_credit_card_detail(extend: ExtendClient, credit_card_id: str) -> Dict:
    return await extend.credit_cards.get_credit_card_detail(credit_card_id)


async def get_expense_categories(
    extend: ExtendClient,
    active: Optional[bool] = None,
    required: Optional[bool] = None,
    search: Optional[str] = None,
    sort_field: Optional[str] = None,
    sort_direction: Optional[str] = None,
    transaction_id: Optional[str] = None,
    required_for_transactions: Optional[bool] = None,
    required_for_virtual_cards: Optional[bool] = None,
) -> Dict:
    """
    Get a list of expense categories.
    """
    response = await extend.expense_data.get_expense_categories(
        active=active,
        required=required,
        search=search,
        sort_field=sort_field,
        sort_direction=sort_direction,
        transaction_id=transaction_id,
        required_for_transactions=required_for_transactions,
        required_for_virtual_cards=required_for_virtual_cards,
    )
    return response


async def get_expense_category(extend: ExtendClient, category_id: str) -> Dict:
    """
    Get detailed information about a specific expense category.
    """
    response = await extend.expense_data.get_expense_category(category_id)
    return response


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


async def get_expense_category_label(extend: ExtendClient, category_id: str, label_id: str) -> Dict:
    return await extend.expense_data.get_expense_category_label(category_id, label_id)


async def create_expense_category(
    extend: ExtendClient,
    name: str,
    code: str,
    required: bool,
    active: Optional[bool] = None,
    free_text_allowed: Optional[bool] = None,
    required_for_transactions: Optional[bool] = None,
    required_for_virtual_cards: Optional[bool] = None,
) -> Dict:
    """
    Create an expense category.
    """
    response = await extend.expense_data.create_expense_category(
        name=name,
        code=code,
        required=required,
        active=active,
        free_text_allowed=free_text_allowed,
        required_for_transactions=required_for_transactions,
        required_for_virtual_cards=required_for_virtual_cards,
    )
    return response


async def create_expense_category_label(
    extend: ExtendClient, category_id: str, name: str, code: str, active: bool = True
) -> Dict:
    """
    Create an expense category label.
    """
    response = await extend.expense_data.create_expense_category_label(
        category_id=category_id, name=name, code=code, active=active
    )
    return response


async def update_expense_category(
    extend: ExtendClient,
    category_id: str,
    name: Optional[str] = None,
    active: Optional[bool] = None,
    required: Optional[bool] = None,
    free_text_allowed: Optional[bool] = None,
    required_for_transactions: Optional[bool] = None,
    required_for_virtual_cards: Optional[bool] = None,
) -> Dict:
    """
    Update an expense category.
    """
    response = await extend.expense_data.update_expense_category(
        category_id=category_id,
        name=name,
        active=active,
        required=required,
        free_text_allowed=free_text_allowed,
        required_for_transactions=required_for_transactions,
        required_for_virtual_cards=required_for_virtual_cards,
    )
    return response


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
    response = await extend.expense_data.update_expense_category_label(
        category_id=category_id, label_id=label_id, name=name, active=active
    )
    return response


async def update_transaction_expense_data(
    extend: ExtendClient, transaction_id: str, data: Dict
) -> Dict:
    """Apply data after the shared executor obtains host approval."""
    return await extend.transactions.update_transaction_expense_data(transaction_id, data)


async def get_organizations(extend: ExtendClient) -> Dict:
    return await extend.organizations.get_organizations()


async def get_organization_members(
    extend: ExtendClient,
    organization_id: str,
    page: int = 0,
    count: int = 50,
    search: str | None = None,
    organization_role: str | None = None,
    organization_roles: list[str] | None = None,
    show_deactivated_users: bool = True,
    render_metrics: bool = False,
) -> Dict:
    return await extend.organizations.get_organization_members(
        organization_id,
        page=page,
        count=count,
        search=search,
        organization_role=organization_role,
        organization_roles=organization_roles,
        show_deactivated_users=show_deactivated_users,
        render_metrics=render_metrics,
    )


async def get_user_details(extend: ExtendClient, user_id: str) -> Dict:
    return await extend.users.get_user_details(user_id)


async def get_expense_policy(extend: ExtendClient, organization_id: str) -> Dict:
    """Return policy file/compile metadata; signed URLs are not fetched."""
    return await extend.organizations.get_expense_policy(organization_id)


async def create_receipt_attachment(
    extend: ExtendClient, transaction_id: str, file_path: str
) -> Dict:
    """File access is available only through the policy-checked core executor."""
    raise PermissionError("Use execute_tool with a host receipt policy")


async def automatch_receipts(extend: ExtendClient, receipt_attachment_ids: List[str]) -> Dict:
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
    response = await extend.receipt_capture.automatch_receipts(
        receipt_attachment_ids=receipt_attachment_ids
    )
    return response


async def get_automatch_status(extend: ExtendClient, job_id: str) -> Dict:
    """
    Retrieves the status of a bulk receipt capture automatch job.

    Args:
        job_id (str): The ID of the automatch job whose status is to be retrieved.

    Returns:
        Dict: A dictionary representing the current Bulk Receipt Automatch Response.
    """
    response = await extend.receipt_capture.get_automatch_status(job_id=job_id)
    return response


async def send_receipt_reminder(extend: ExtendClient, transaction_id: str) -> Dict:
    """
    Send a transaction-specific receipt reminder.

    Args:
        extend: The Extend client instance
        transaction_id (str): The unique identifier of the transaction.

    Returns:
        Dict: Response from the API indicating the reminder was sent successfully.
    """
    response = await extend.transactions.send_receipt_reminder(transaction_id)
    return response
