from typing import Optional

from pydantic import BaseModel, Field


class GetVirtualCards(BaseModel):
    """Schema for the `get_virtual_cards` operation."""

    page: int = Field(
        0,
        description="Pagination page number, default is 0.",
    )
    per_page: int = Field(
        10,
        description="Number of items per page, default is 10.",
    )
    status: Optional[str] = Field(
        None,
        description="Filter virtual cards by status. Options: ACTIVE, INACTIVE, CANCELLED, CLOSED.",
    )
    recipient: Optional[str] = Field(
        None,
        description="Filter virtual cards by recipient identifier.",
    )
    search_term: Optional[str] = Field(
        None,
        description="Search term to filter virtual cards.",
    )


class GetVirtualCardDetail(BaseModel):
    """Schema for the `get_virtual_card_detail` operation."""

    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card.",
    )


class CreateVirtualCard(BaseModel):
    """Schema for the `create_virtual_card` operation."""

    credit_card_id: str = Field(
        ...,
        description="ID of the credit card to use.",
    )
    display_name: str = Field(
        ...,
        description="Display name for the virtual card.",
    )
    amount_dollars: float = Field(
        ...,
        description="Amount to load on the card in dollars.",
    )
    recipient_email: Optional[str] = Field(
        None,
        description="Optional email address of the recipient.",
    )
    valid_from: Optional[str] = Field(
        None,
        description="Optional start date (YYYY-MM-DD).",
    )
    valid_to: Optional[str] = Field(
        None,
        description="Optional end date (YYYY-MM-DD).",
    )
    notes: Optional[str] = Field(
        None,
        description="Optional notes for the card.",
    )
    is_recurring: bool = Field(
        False,
        description="Set to True to create a recurring card.",
    )
    period: Optional[str] = Field(
        None,
        description="Recurrence period (DAILY, WEEKLY, MONTHLY, or YEARLY).",
    )
    interval: Optional[int] = Field(
        None,
        description="Number of periods between recurrences.",
    )
    terminator: Optional[str] = Field(
        None,
        description="Recurrence terminator (NONE, COUNT, DATE, or COUNT_OR_DATE).",
    )
    count: Optional[int] = Field(
        None,
        description="Number of times to recur for a COUNT terminator.",
    )
    until: Optional[str] = Field(
        None,
        description="End date for recurrence (for DATE terminator).",
    )
    by_week_day: Optional[int] = Field(
        None,
        description="Day of week for WEEKLY recurrence (0-6, Monday to Sunday).",
    )
    by_month_day: Optional[int] = Field(
        None,
        description="Day of month for MONTHLY recurrence (1-31).",
    )
    by_year_day: Optional[int] = Field(
        None,
        description="Day of year for YEARLY recurrence (1-365).",
    )


class UpdateVirtualCard(BaseModel):
    """Schema for the `update_virtual_card` operation."""

    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card to update.",
    )
    display_name: Optional[str] = Field(
        None,
        description="New display name for the virtual card.",
    )
    balance_dollars: Optional[float] = Field(
        None,
        description="New balance for the card in dollars.",
    )
    valid_from: Optional[str] = Field(
        None,
        description="New start date (YYYY-MM-DD).",
    )
    valid_to: Optional[str] = Field(
        None,
        description="New end date (YYYY-MM-DD).",
    )
    notes: Optional[str] = Field(
        None,
        description="New notes for the virtual card.",
    )


class CloseVirtualCard(BaseModel):
    """Schema for the `close_virtual_card` operation."""

    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card to close.",
    )


class CancelVirtualCard(BaseModel):
    """Schema for the `cancel_virtual_card` operation."""

    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card to cancel.",
    )


class GetTransactions(BaseModel):
    """Schema for the `get_transactions` operation."""

    page: int = Field(
        0,
        description="Pagination page number, default is 0.",
    )
    per_page: int = Field(
        50,
        description="Number of transactions per page, default is 50.",
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date to filter transactions (YYYY-MM-DD).",
    )
    end_date: Optional[str] = Field(
        None,
        description="End date to filter transactions (YYYY-MM-DD).",
    )
    virtual_card_id: Optional[str] = Field(
        None,
        description="Filter transactions by a specific virtual card ID.",
    )
    min_amount_cents: Optional[int] = Field(
        None,
        description="Minimum transaction amount in cents.",
    )
    max_amount_cents: Optional[int] = Field(
        None,
        description="Maximum transaction amount in cents.",
    )


class GetTransactionDetail(BaseModel):
    """Schema for the `get_transaction_detail` operation."""

    transaction_id: str = Field(
        ...,
        description="The ID of the transaction to retrieve details for.",
    )


class GetCreditCards(BaseModel):
    """Schema for the `get_credit_cards` operation."""

    page: int = Field(
        0,
        description="Pagination page number, default is 0.",
    )
    per_page: int = Field(
        10,
        description="Number of credit cards per page, default is 10.",
    )
