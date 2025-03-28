import logging
from typing import Optional, Dict

from extend import ExtendClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        display_name: Optional[str] = None,
        balance_dollars: Optional[float] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        notes: Optional[str] = None
) -> Dict:
    """
    Update a virtual card

    Args:
        virtual_card_id: ID of the virtual card to update
        display_name: New name for the virtual card
        balance_dollars: New balance for the card in dollars
        valid_from: New start date (YYYY-MM-DD)
        valid_to: New end date (YYYY-MM-DD)
        notes: New notes for the card

    """
    try:
        balance_cents = int(balance_dollars * 100)
        response = await extend.virtual_cards.update_virtual_card(
            card_id=virtual_card_id,
            balance_cents=balance_cents,
            notes=notes,
            display_name=display_name,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        return response

    except Exception as e:
        logger.error("Error creating virtual card: %s", e)
        raise Exception("Error creating virtual card")


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
