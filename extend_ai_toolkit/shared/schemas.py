from typing import Dict, List, Optional, Union

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
    status: Optional[Union[List[str], str]] = Field(
        None,
        description="Filter transactions by status (e.g., PENDING, CLEARED, DECLINED, etc.)."
    )
    receipt_statuses: Optional[List[str]] = Field(
        None,
        description="Filter transactions by receipt statuses."
    )
    expense_category_statuses: Optional[List[str]] = Field(
        None,
        description="Filter transactions by expense category status, such as Attached or Missing."
    )
    missing_expense_categories: Optional[bool] = Field(
        None,
        description="Filter transactions missing expense categorizations."
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
    receipt_missing: Optional[bool] = Field(
        None,
        description="Filter transactions by whether they are missing a receipt."
    )
    search_term: Optional[str] = Field(
        None,
        description="Filter transactions by search term."
    )
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort by, with optional direction. Use 'recipientName', 'merchantName', 'amount', 'date' for ASC. Use '-recipientName', '-merchantName', '-amount', '-date' for DESC."
    )    


class CountTransactions(BaseModel):
    """Schema for the `count_transactions` operation."""
    from_date: Optional[str] = Field(
        None,
        description="Start date to filter transactions (YYYY-MM-DD)."
    )
    to_date: Optional[str] = Field(
        None,
        description="End date to filter transactions (YYYY-MM-DD)."
    )
    status: Optional[List[str]] = Field(
        None,
        description="Filter transactions by one or more statuses."
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
    expense_category_statuses: Optional[List[str]] = Field(
        None,
        description="Filter transactions by expense category status, such as Attached or Missing."
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
    type: Optional[str] = Field(
        None,
        description="Filter credit cards by type, such as SOURCE or DELEGATE."
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


class GetExpenseCategoryLabel(BaseModel):
    """Schema for the `get_expense_category_label` operation."""
    category_id: str = Field(
        ...,
        description="The ID of the expense category."
    )
    label_id: str = Field(
        ...,
        description="The ID of the expense category label."
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


class GetOrganizations(BaseModel):
    """Schema for the `get_organizations` operation."""


class GetOrganizationMembers(BaseModel):
    """Schema for the `get_organization_members` operation."""
    organization_id: str = Field(
        ...,
        description="The organization ID to retrieve members for."
    )
    page: Optional[int] = Field(
        None,
        description="Page number for pagination."
    )
    count: Optional[int] = Field(
        None,
        description="Number of members per page."
    )
    search: Optional[str] = Field(
        None,
        description="Search term to filter members by name or email."
    )
    organization_role: Optional[str] = Field(
        None,
        description="Filter to a single organization role."
    )
    organization_roles: Optional[List[str]] = Field(
        None,
        description="Filter to multiple organization roles."
    )
    show_deactivated_users: Optional[bool] = Field(
        True,
        description="Whether to include deactivated users."
    )
    render_metrics: Optional[bool] = Field(
        False,
        description="Whether to include activity metrics."
    )


class GetUserDetails(BaseModel):
    """Schema for the `get_user_details` operation."""
    user_id: str = Field(
        ...,
        description="The user ID to retrieve."
    )


class GetExpensePolicy(BaseModel):
    """Schema for the `get_expense_policy` operation."""
    organization_id: str = Field(
        ...,
        description="The organization ID whose expense policy should be retrieved."
    )


class CreateReceiptAttachmentSchema(BaseModel):
    """Schema for the `create_receipt_attachment` operation."""
    file_path: str = Field(
        ...,
        description="File path for the receipt attachment to be uploaded via multipart form data."
    )
    transaction_id: Optional[str] = Field(
        ...,
        description="The optional unique identifier of the transaction to attach the receipt to."
    )


class AutomatchReceiptsSchema(BaseModel):
    """Schema for the `automatch_receipts` operation."""
    receipt_attachment_ids: List[str] = Field(
        ...,
        description="A list of receipt attachment IDs to be automatched."
    )


class GetAutomatchStatusSchema(BaseModel):
    """Schema for the `get_automatch_status` operation."""
    job_id: str = Field(
        ...,
        description="The unique identifier of the automatch job whose status is to be retrieved."
    )


class SendReceiptReminderSchema(BaseModel):
    """Schema for the `send_receipt_reminder` operation."""
    transaction_id: str = Field(
        ...,
        description="The unique identifier of the transaction to send a receipt reminder for."
    )
