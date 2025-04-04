from typing import Dict, Optional, List

from pydantic import BaseModel, Field


class GetVirtualCards(BaseModel):
    """Schema for the `get_virtual_cards` operation."""
    page: int = Field(
        0,
        description="Pagination page number, default is 0."
    )
    per_page: int = Field(
        10,
        description="Number of items per page, default is 10."
    )
    status: Optional[str] = Field(
        None,
        description="Filter virtual cards by status. Options: ACTIVE, CANCELLED, PENDING, EXPIRED, CLOSED, CONSUMED."
    )
    recipient: Optional[str] = Field(
        None,
        description="Filter virtual cards by recipient identifier."
    )
    search_term: Optional[str] = Field(
        None,
        description="Search term to filter virtual cards."
    )
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort by: 'createdAt', 'updatedAt', 'balanceCents', 'displayName', 'type', or 'status'."
    )
    sort_direction: Optional[str] = Field(
        None,
        description="Sort direction, ASC or DESC."
    )


class GetVirtualCardDetail(BaseModel):
    """Schema for the `get_virtual_card_detail` operation."""
    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card."
    )


class CreateVirtualCard(BaseModel):
    """Schema for the `create_virtual_card` operation."""
    credit_card_id: str = Field(
        ...,
        description="ID of the credit card to use."
    )
    display_name: str = Field(
        ...,
        description="Display name for the virtual card."
    )
    amount_dollars: float = Field(
        ...,
        description="Amount to load on the card in dollars."
    )
    recipient_email: Optional[str] = Field(
        None,
        description="Optional email address of the recipient."
    )
    cardholder_email: Optional[str] = Field(
        None,
        description="Optional email address of the cardholder."
    )
    valid_from: Optional[str] = Field(
        None,
        description="Optional start date (YYYY-MM-DD)."
    )
    valid_to: Optional[str] = Field(
        None,
        description="Optional end date (YYYY-MM-DD)."
    )
    notes: Optional[str] = Field(
        None,
        description="Optional notes for the card."
    )
    is_recurring: bool = Field(
        False,
        description="Set to True to create a recurring card."
    )
    period: Optional[str] = Field(
        None,
        description="Recurrence period (DAILY, WEEKLY, MONTHLY, or YEARLY)."
    )
    interval: Optional[int] = Field(
        None,
        description="Number of periods between recurrences."
    )
    terminator: Optional[str] = Field(
        None,
        description="Recurrence terminator (NONE, COUNT, DATE, or COUNT_OR_DATE)."
    )
    count: Optional[int] = Field(
        None,
        description="Number of times to recur for a COUNT terminator."
    )
    until: Optional[str] = Field(
        None,
        description="End date for recurrence (for DATE terminator)."
    )
    by_week_day: Optional[int] = Field(
        None,
        description="Day of week for WEEKLY recurrence (0-6, Monday to Sunday)."
    )
    by_month_day: Optional[int] = Field(
        None,
        description="Day of month for MONTHLY recurrence (1-31)."
    )
    by_year_day: Optional[int] = Field(
        None,
        description="Day of year for YEARLY recurrence (1-365)."
    )


class UpdateVirtualCard(BaseModel):
    """Schema for the `update_virtual_card` operation."""
    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card to update."
    )
    display_name: str = Field(
        ...,
        description="New display name for the virtual card."
    )
    balance_dollars: float = Field(
        ...,
        description="New balance for the card in dollars."
    )
    valid_to: Optional[str] = Field(
        None,
        description="New end date (YYYY-MM-DD)."
    )
    notes: Optional[str] = Field(
        None,
        description="New notes for the virtual card."
    )


class CloseVirtualCard(BaseModel):
    """Schema for the `close_virtual_card` operation."""
    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card to close."
    )


class CancelVirtualCard(BaseModel):
    """Schema for the `cancel_virtual_card` operation."""
    virtual_card_id: str = Field(
        ...,
        description="The ID of the virtual card to cancel."
    )


class GetTransactions(BaseModel):
    """Schema for the `get_transactions` operation."""
    page: int = Field(
        0,
        description="Pagination page number, default is 0."
    )
    per_page: int = Field(
        50,
        description="Number of transactions per page, default is 50."
    )
    from_date: Optional[str] = Field(
        None,
        description="Start date to filter transactions (YYYY-MM-DD)."
    )
    to_date: Optional[str] = Field(
        None,
        description="End date to filter transactions (YYYY-MM-DD)."
    )
    status: Optional[str] = Field(
        None,
        description="Filter transactions by status (e.g., PENDING, CLEARED, DECLINED, etc.)."
    )
    virtual_card_id: Optional[str] = Field(
        None,
        description="Filter transactions by a specific virtual card ID."
    )
    min_amount_cents: Optional[int] = Field(
        None,
        description="Minimum transaction amount in cents."
    )
    max_amount_cents: Optional[int] = Field(
        None,
        description="Maximum transaction amount in cents."
    )
    search_term: Optional[str] = Field(
        None,
        description="Filter transactions by search term."
    )
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort transactions by."
    )


class GetTransactionDetail(BaseModel):
    """Schema for the `get_transaction_detail` operation."""
    transaction_id: str = Field(
        ...,
        description="The ID of the transaction to retrieve details for."
    )


class ProposeTransactionExpenseData(BaseModel):
    """Schema for the `propose_transaction_expense_data` operation."""
    transaction_id: str = Field(
        ...,
        description="The unique identifier of the transaction."
    )
    data: Dict = Field(
        ...,
        description=(
            "A dictionary representing the expense details to propose. "
            "Expected format: {'expenseDetails': [{'categoryId': str, 'labelId': str}]}."
        )
    )


class ProposeTransactionExpenseDataResponse(BaseModel):
    """Response schema for the `propose_transaction_expense_data` operation."""
    status: str = Field(
        default="pending_confirmation",
        description="Status of the expense data proposal."
    )
    transaction_id: str = Field(
        ...,
        description="The unique identifier of the transaction."
    )
    confirmation_token: str = Field(
        ...,
        description="The unique token required to confirm this expense data update."
    )
    expires_at: str = Field(
        ...,
        description="ISO-8601 timestamp when this proposal expires."
    )
    proposed_categories: List[Dict] = Field(
        ...,
        description="List of proposed expense categories and labels."
    )


class ConfirmTransactionExpenseData(BaseModel):
    """Schema for the `confirm_transaction_expense_data` operation."""
    confirmation_token: str = Field(
        ...,
        description="The unique token from the proposal step that was shared with the user."
    )


class UpdateTransactionExpenseData(BaseModel):
    """Schema for the `update_transaction_expense_data` operation."""
    transaction_id: str = Field(
        ...,
        description="The unique identifier of the transaction."
    )
    user_confirmed_data_values: bool = Field(
        ...,
        description="Indicates whether or not the user has confirmed the specific values used in the data argument."
    )
    data: Dict = Field(
        ...,
        description=(
            "A dictionary representing the expense details to update. "
            "Expected format: {'expenseDetails': [{'categoryId': str, 'labelId': str}]}."
        )
    )


class GetCreditCards(BaseModel):
    """Schema for the `get_credit_cards` operation."""
    page: int = Field(
        0,
        description="Pagination page number, default is 0."
    )
    per_page: int = Field(
        10,
        description="Number of credit cards per page, default is 10."
    )
    status: Optional[str] = Field(
        None,
        description="Filter credit cards by status."
    )
    search_term: Optional[str] = Field(
        None,
        description="Search term to filter credit cards."
    )
    sort_direction: Optional[str] = Field(
        None,
        description="Sort direction, ASC or DESC."
    )


class GetCreditCardDetail(BaseModel):
    """Schema for the `get_credit_card_detail` operation."""
    credit_card_id: str = Field(
        ...,
        description="The ID of the credit card to retrieve details for."
    )


class GetExpenseCategories(BaseModel):
    """Schema for the `get_expense_categories` operation."""
    active: Optional[bool] = Field(
        None,
        description="Filter categories by active status."
    )
    required: Optional[bool] = Field(
        None,
        description="Filter categories by required status."
    )
    search: Optional[str] = Field(
        None,
        description="Search term to filter categories."
    )
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort the categories by."
    )
    sort_direction: Optional[str] = Field(
        None,
        description="Direction to sort the categories (ASC or DESC)."
    )


class GetExpenseCategory(BaseModel):
    """Schema for the `get_expense_category` operation."""
    category_id: str = Field(
        ...,
        description="The ID of the expense category."
    )


class GetExpenseCategoryLabels(BaseModel):
    """Schema for the `get_expense_category_labels` operation."""
    category_id: str = Field(
        ...,
        description="The ID of the expense category."
    )
    page: Optional[int] = Field(
        0,
        description="Pagination page number, default is 0."
    )
    per_page: Optional[int] = Field(
        10,
        description="Number of labels per page, default is 10."
    )
    active: Optional[bool] = Field(
        None,
        description="Filter labels by active status."
    )
    search: Optional[str] = Field(
        None,
        description="Search term to filter labels."
    )
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort labels by."
    )
    sort_direction: Optional[str] = Field(
        None,
        description="Direction to sort the labels (ASC or DESC)."
    )


class CreateExpenseCategory(BaseModel):
    """Schema for the `create_expense_category` operation."""
    name: str = Field(
        ...,
        description="The name of the expense category."
    )
    code: str = Field(
        ...,
        description="A unique code for the expense category."
    )
    required: bool = Field(
        ...,
        description="Indicates whether the expense category is required."
    )
    active: Optional[bool] = Field(
        None,
        description="The active status of the category."
    )
    free_text_allowed: Optional[bool] = Field(
        None,
        description="Indicates if free text is allowed."
    )


class CreateExpenseCategoryLabel(BaseModel):
    """Schema for the `create_expense_category_label` operation."""
    category_id: str = Field(
        ...,
        description="The ID of the expense category."
    )
    name: str = Field(
        ...,
        description="The name of the expense category label."
    )
    code: str = Field(
        ...,
        description="A unique code for the expense category label."
    )
    active: bool = Field(
        True,
        description="The active status of the label (defaults to True)."
    )


class UpdateExpenseCategory(BaseModel):
    """Schema for the `update_expense_category` operation."""
    category_id: str = Field(
        ...,
        description="The ID of the expense category to update."
    )
    name: Optional[str] = Field(
        None,
        description="The new name for the expense category."
    )
    active: Optional[bool] = Field(
        None,
        description="The updated active status."
    )
    required: Optional[bool] = Field(
        None,
        description="The updated required status."
    )
    free_text_allowed: Optional[bool] = Field(
        None,
        description="Indicates if free text is allowed."
    )


class UpdateExpenseCategoryLabel(BaseModel):
    """Schema for the `update_expense_category_label` operation."""
    category_id: str = Field(
        ...,
        description="The ID of the expense category."
    )
    label_id: str = Field(
        ...,
        description="The ID of the expense category label to update."
    )
    name: Optional[str] = Field(
        None,
        description="The new name for the label."
    )
    active: Optional[bool] = Field(
        None,
        description="The updated active status of the label."
    )


class CreateReceiptAttachmentSchema(BaseModel):
    """Schema for the `create_receipt_attachment` operation."""
    transaction_id: str = Field(
        ...,
        description="The unique identifier of the transaction to attach the receipt to."
    )
    file_path: str = Field(
        ...,
        description="File path for the receipt attachment to be uploaded via multipart form data."
    )
