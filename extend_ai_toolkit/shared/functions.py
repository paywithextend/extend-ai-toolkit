import logging
from typing import Optional, Dict

from extend import ExtendClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =========================
# Virtual Card Functions
# =========================

async def get_virtual_cards(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 10,
        status: Optional[str] = None,
        recipient: Optional[str] = None,
        search_term: Optional[str] = None
) -> Dict:
    """Get list of virtual cards"""
    try:
        response = await extend.virtual_cards.get_virtual_cards(
            page=page,
            per_page=per_page,
            status=status,
            recipient=recipient,
            search_term=search_term
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


async def create_virtual_card(
        extend: ExtendClient,
        credit_card_id: str,
        display_name: str,
        amount_dollars: float,
        recipient_email: Optional[str] = None,
        cardholder_email: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        notes: Optional[str] = None,
        is_recurring: bool = False,
        # Recurrence parameters
        period: Optional[str] = None,
        interval: Optional[int] = None,
        terminator: Optional[str] = None,
        count: Optional[int] = None,
        until: Optional[str] = None,
        by_week_day: Optional[int] = None,
        by_month_day: Optional[int] = None,
        by_year_day: Optional[int] = None
) -> Dict:
    """
    Create a virtual card

    Args:
        credit_card_id: ID of the credit card to use (get this from list_credit_cards)
        display_name: Name for the virtual card
        amount_dollars: Amount to load on the card in dollars
        recipient_email: Optional email address of recipient
        cardholder_email: Optional email address of cardholder
        valid_from: Optional start date (YYYY-MM-DD)
        valid_to: Optional end date (YYYY-MM-DD)
        notes: Optional notes for the card
        is_recurring: Set to True to create a recurring card
        period: DAILY, WEEKLY, MONTHLY, or YEARLY
        interval: Number of periods between recurrences
        terminator: NONE, COUNT, DATE, or COUNT_OR_DATE
        count: Number of times to recur (for COUNT terminator)
        until: End date for recurrence (for DATE terminator)
        by_week_day: Day of week (0-6, Monday to Sunday) for WEEKLY recurrence
        by_month_day: Day of month (1-31) for MONTHLY recurrence
        by_year_day: Day of year (1-365) for YEARLY recurrence

    """
    try:
        balance_cents = int(amount_dollars * 100)

        response = await extend.virtual_cards.create_virtual_card(
            credit_card_id=credit_card_id,
            display_name=display_name,
            balance_cents=balance_cents,
            notes=notes,
            recurs=is_recurring,
            recurrence={
                "balance_cents": balance_cents,
                "period": period,
                "interval": interval,
                "terminator": terminator,
                "count": count,
                "until": until,
                "by_week_day": by_week_day,
                "by_month_day": by_month_day,
                "by_year_day": by_year_day
            },
            recipient=recipient_email,
            cardholder=cardholder_email,
            valid_to=valid_to,
        )
        return response

    except Exception as e:
        logger.error("Error creating virtual card: %s", e)
        raise Exception("Error creating virtual card")


async def update_virtual_card(
        extend: ExtendClient,
        virtual_card_id: str,
        display_name: str,
        balance_dollars: float,
        valid_to: Optional[str] = None,
        notes: Optional[str] = None
) -> Dict:
    """
    Update a virtual card

    Args:
        virtual_card_id: ID of the virtual card to update
        display_name: New existing name for the virtual card
        balance_dollars: New or existing balance for the card in dollars
        valid_to: New end date (YYYY-MM-DD)
        notes: New notes for the card

    """
    try:
        balance_cents = int(balance_dollars * 100)
        response = await extend.virtual_cards.update_virtual_card(
            card_id=virtual_card_id,
            balance_cents=balance_cents,
            display_name=display_name,
            notes=notes,
            valid_to=valid_to,
        )
        return response

    except Exception as e:
        logger.error("Error updating virtual card: %s", e)
        raise Exception("Error updating virtual card")


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
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        virtual_card_id: Optional[str] = None,
        min_amount_cents: Optional[int] = None,
        max_amount_cents: Optional[int] = None
) -> Dict:
    """
    Get a list of recent transactions

    Args:
        page (int): pagination page number,
        per_page (int): number of transactions per page,
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        virtual_card_id (str): Filter by specific virtual card
        min_amount_cents (int): Minimum amount in cents
        max_amount_cents (int): Maximum amount in cents

    """
    try:
        response = await extend.transactions.get_transactions(
            page,
            per_page,
            start_date,
            end_date,
            virtual_card_id,
            min_amount_cents,
            max_amount_cents
        )
        return response

    except Exception as e:
        logger.error("Error getting transactions: %s", e)
        raise Exception("Error getting transactions")


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
        search_term: Optional[str] = None,
) -> Dict:
    """Get a list of credit cards"""
    try:
        response = await extend.credit_cards.get_credit_cards(
            page=page,
            per_page=per_page,
            status=status
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
